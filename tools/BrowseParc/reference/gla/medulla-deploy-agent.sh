#!/bin/bash

# Needs the following packages:
# powershell # From https://github.com/PowerShell/PowerShell/releases/download/v7.3.6/powershell_7.3.6-1.deb_amd64.deb
# https://learn.microsoft.com/en-us/powershell/scripting/install/install-debian?view=powershell-7.3#installation-via-direct-download
# gss-ntlmssp
# Powershell remoting must be enabled. cf https://theitbros.com/run-powershell-script-on-remote-computer/
# WSMan must be installed:
#    pwsh -Command "Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted"
#    pwsh -Command 'Install-Module -Name PSWSMan'
#    pwsh -Command 'Install-WSMan'

# Parameters
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
WINRM_PORT='5985'
DBHOST=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbhost 2> /dev/null || echo localhost)
DBPORT=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbport 2> /dev/null || echo 3306)
DBUSER=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbuser 2> /dev/null || echo mmc)
DBPASS=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbpasswd)

display_usage() {
    echo -e "${RED}Usage: $0 --target=<target_cidr | target_fqdn> | --server=<ad_server_name> [--port=<winrm_or_ssh_port>] [--namefilter=<filter_on_hostname>] [--domain=<user_domain>] [--username=<remote_username>] [--password=<remote_password>] [--sshkey=<path_to_ssh_key>] [--ou=<ad_ou>] [--force] [--reinstall]"
    echo -e "${NC}"
    echo "Example using network discovery and winrm:"
    echo "  $0 --target=10.10.0.0/24 --namefilter=win --username=vagrant --password=vagrant"
    echo "Example using Active Directory and winrm:"
    echo "  $0 --server=10.10.0.100 --namefilter=win --ou=OU=grp1,DC=MEDULLA,DC=int --domain=MEDULLA --username=Administrator --password=P@ssw0rd"
    echo "Example using network discovery and ssh:"
    echo "  $0 --target=10.10.0.0/24 --namefilter=win --port=22 --username=pulseuser --sshkey=/root/.ssh/id_rsa"
    echo "Examples for an individual machine:"
    echo "  $0 --target=10.10.0.94/32 --username=vagrant --password=vagrant"
    echo "  $0 --target=host.siveo.net --username=pulseuser --sshkey=/root/.ssh/id_rsa"
    echo "Example for a linux machine:"
    echo "  $0 --target=10.10.0.94/32 --port=22 --username=root --sshkey=/root/.ssh/id_rsa"
}

check_arguments() {
    if [[ $# -lt 1 ]]; then
        display_usage
        exit 1
    fi
    for i in "$@"; do
        case $i in
            --target=*)
                CIDR_REGEX='(((25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?))(\/([8-9]|[1-2][0-9]|3[0-2]))([^0-9.]|$)'
                TARGET="${i#*=}"
                if host "$TARGET" >/dev/null 2>&1; then
                    echo -e "${GREEN}Running with FQDN $TARGET"
                    FQDN=1
                elif [[ $TARGET =~ $REGEX ]]; then
                    echo -e "${GREEN}Running with CIDR $TARGET"
                else
                    echo -e "${RED}$TARGET is not a valid CIDR or FQDN"
                    display_usage
                    exit 1
                fi
                shift
                ;;
            --server=*)
                SERVER="${i#*=}"
                echo -e "${GREEN}Querying Active Directory $SERVER"
                shift
                ;;
            --namefilter=*)
                FILTER="${i#*=}"
                echo -e "${GREEN}Filtering on hostname: *$FILTER*"
                shift
                ;;
            --port=*)
                PORT="${i#*=}"
                shift
                ;;
            --username=*)
                USERNAME="${i#*=}"
                shift
                ;;
            --password=*)
                PASSWORD="${i#*=}"
                shift
                ;;
            --sshkey=*)
                SSHKEY="${i#*=}"
                shift
                ;;
            --domain=*)
                DOMAIN="${i#*=}"
                shift
                ;;
            --ou=*)
                OU="${i#*=}"
                echo -e "${GREEN}Filtering on ou: *$OU*"
                shift
                ;;
            --force*)
                FORCE=1
                shift
                ;;
            --reinstall*)
                REINSTALL=1
                shift
                ;;
            --debug*)
                DEBUG=1
                shift
                ;;
            *)
                # unknown option
                display_usage
                ;;
        esac
    done
    if [ -z ${PORT+x} ]; then
        PORT=${WINRM_PORT}
    fi
    # Ask for username and password if not given in the command
    if [[ -z $SSHKEY ]]; then
        # Check if a user name and password is given
        if [[ -z $USERNAME || -z $PASSWORD ]]; then
            echo "Please provide a domain account for accessing the machines and/or the Active Directory."
            read -r -p "Username: " USERNAME
            read -p "Password: " PASSWORD
            # Cater for inclusion of domain in username eg. MEDULLA\Administrateur
            USERNAME=$(echo ${USERNAME} | sed 's~\\~\\\\~g')
        fi
    else
        # Ony check if a username is given
        if [[ -z $USERNAME ]]; then
            echo "Please provide a domain account for accessing the machines and/or the Active Directory."
            read -r -p "Username: " USERNAME
        fi
    fi
}

check_ps_setup() {
    # Make sure WSMan is installed
    pwsh -Command "Register-PSRepository -Default"
    pwsh -Command "Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted"
    pwsh -Command "Install-Module -Name PSWSMan"
    pwsh -Command "Install-WSMan"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Remote execution support is not properly setup. Please check PowerShell installation and WSMan setup."
        exit 1
    fi
}

get_machines_list_nmap() {
    MACH_LIST=()

    # Scan local network and list machines for user confirmation
    if [ ! -z ${DEBUG+x} ]; then
        echo -e "${GREEN}Running nmap -T4 -Pn --max-rtt-timeout 200ms --initial-rtt-timeout 150ms --min-hostgroup 512 -n --open -p ${PORT} ${TARGET} -oG - | grep \"/open\" | awk '{ print \$2 }'"
    fi
    IPS=$(nmap -T4 -Pn --max-rtt-timeout 200ms --initial-rtt-timeout 150ms --min-hostgroup 512 -n --open -p ${PORT} ${TARGET} -oG - | grep "/open" | awk '{ print $2 }')

    for IP in ${IPS}; do
        MACH=$(dig +short -x ${IP} | sed 's/\.$//' || echo ${IP})
        if [ -z ${FILTER+x} ]; then
            MACH_LIST+=("${MACH}")
        else
            if [[ "$MACH" == *"$FILTER"* ]]; then
                MACH_LIST+=("${MACH}")
            fi
        fi
    done
}

get_machines_list_ad() {
    MACH_LIST=()

    if [ -z ${FILTER+x} ]; then
        ARGFILTER="-Filter *"
    else
        ARGFILTER="-LDAPFilter '(name=*${FILTER}*)'"
    fi

    if [ ! -z ${OU+x} ]; then
        ARGOU="-SearchBase '${OU}'"
    fi

    if [ ! -z ${DOMAIN+x} ]; then
        USERNAME="${DOMAIN}\\${USERNAME}"
    fi

    # Query AD and list machines for user confirmation
    if [ ! -z ${DEBUG+x} ]; then
        echo -e "${GREEN}Running pwsh -Command \"
\$pw = ConvertTo-SecureString -AsPlainText -Force -String ********
\$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList \"${USERNAME}\",\$pw
Invoke-Command -ComputerName ${SERVER} -Authentication Negotiate -Credential \$cred -ScriptBlock {
    Get-ADComputer ${ARGFILTER} ${ARGOU} -Properties IPv4Address | Format-Table -HideTableHeaders Name
}
\""
    fi
    MACH=$(pwsh -Command "
\$pw = ConvertTo-SecureString -AsPlainText -Force -String ${PASSWORD}
\$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList "${USERNAME}",\$pw
Invoke-Command -ComputerName ${SERVER} -Authentication Negotiate -Credential \$cred -ScriptBlock {
    Get-ADComputer ${ARGFILTER} ${ARGOU} -Properties IPv4Address | Format-Table -HideTableHeaders Name
}
")
    if [ $? -ne 0 ]; then
        echo -e "${RED}${MACH}"
        exit 1
    else
        MACH_LIST=($MACH)
    fi
}

remove_installed() {
    index=0
    for MACH in ${MACH_LIST[@]}; do
        if [[ $(mysql -Ns -h ${DBHOST} -P ${DBPORT} -u${DBUSER} -p${DBPASS} xmppmaster -e "SELECT hostname FROM machines WHERE hostname='${MACH%%.*}'") != '' ]]; then
            unset 'MACH_LIST[index]'
        fi
        ((index++))
    done
}

confirm_list() {
    echo -e "${NC}"
    echo "Are you sure you want to install Medulla agent on the following machines:"
    for MACH in ${MACH_LIST[@]}; do
        echo "- ${MACH}"
    done
    read -p "Install Medulla agent? (y/N) " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
}

list_machines() {
    echo -e "${GREEN}Medulla agent will be installed on the following machines:"
    for MACH in ${MACH_LIST[@]}; do
        echo "- ${MACH}"
    done
}

install_agent() {
    # Install agent on machine: $1 = machine name or ip
    echo -e "${GREEN}$1: Processing"
    if [[ $(timeout 1 bash -c cat < /dev/tcp/$1/${PORT}) == *"SSH"* || ! -z ${SSHKEY+x} ]]; then
        # Using SSH
        ssh ${USERNAME}@$1 -p ${PORT} -i ${SSHKEY} -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null 'wmic os get version /value' &> /dev/null
        if [ $? -eq 0 ]; then
            # Windows machine
            CMD="ssh ${USERNAME}@$1 -p ${PORT} -i ${SSHKEY} -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null 'PowerShell.exe -noprofile -' < /var/lib/pulse2/clients/win/install-agent.ps1"
        else
            # Linux machine
            CMD="ssh ${USERNAME}@$1 -p ${PORT} -i ${SSHKEY} -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null 'bash -s' < /var/lib/pulse2/clients/lin/Medulla-Agent-linux-MINIMAL-latest.sh"
        fi
        if [ ! -z ${DEBUG+x} ]; then
            echo -e "$1: Running ${CMD}"
            eval ${CMD}
        else
            eval ${CMD}&> /dev/null && echo -e "${GREEN}$1: Execution successful" || echo -e "${RED}$1: Execution failed"
        fi
    else
        # Using WINRM
        if [ ! -z ${DEBUG+x} ]; then
            echo -e "$1: Running pwsh -Command \"
\$pw = ConvertTo-SecureString -AsPlainText -Force -String ********
\$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList \"${USERNAME}\",\$pw
Invoke-Command -ComputerName $1 -Port ${PORT} -Authentication Negotiate -Credential \$cred -FilePath /var/lib/pulse2/clients/win/install-agent.ps1
}
\""
            pwsh -Command "
\$pw = ConvertTo-SecureString -AsPlainText -Force -String ${PASSWORD}
\$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList "${USERNAME}",\$pw
Invoke-Command -ComputerName $1 -Port ${PORT} -Authentication Negotiate -Credential \$cred -FilePath /var/lib/pulse2/clients/win/install-agent.ps1
"
        else
            pwsh -Command "
\$pw = ConvertTo-SecureString -AsPlainText -Force -String ${PASSWORD}
\$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList "${USERNAME}",\$pw
Invoke-Command -ComputerName $1 -Port ${PORT} -Authentication Negotiate -Credential \$cred -FilePath /var/lib/pulse2/clients/win/install-agent.ps1
"&> /dev/null && echo -e "${GREEN}$1: Execution successful" || echo -e "${RED}$1: Execution failed"
        fi
    fi
}


check_arguments "$@"
check_ps_setup
if [[ "$FQDN" == 1 ]]; then
    MACH_LIST=("${TARGET}")
elif [[ "$TARGET" == */32 ]]; then
    MACH_LIST=("${TARGET:0:-3}")
else
    if [ -z ${SERVER+x} ]; then
        get_machines_list_nmap
    else
        get_machines_list_ad
    fi
fi
if [ -z ${REINSTALL+x} ]; then
    remove_installed
fi
if [ ${#MACH_LIST[@]} -eq 0 ]; then
    echo -e "${NC}No machines to install Medulla Agent on"
    exit 0
else
    if [ -z ${FORCE+x} ]; then
        confirm_list
    else
        list_machines
    fi
    # Install agent on list of machines
    for MACH in ${MACH_LIST[@]}; do
        install_agent ${MACH} &
    done
fi
