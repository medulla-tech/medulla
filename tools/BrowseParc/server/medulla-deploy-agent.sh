#!/bin/bash

# Medulla agent deployment helper.
#
# Two usages:
#   1. Historical interactive usage (discovery + install, prompts for credentials)
#   2. Non interactive usage driven by the MMC web interface ("Parcourir mon parc")
#      with --json / --state-file so the UI can follow the job progress.
#
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
# Colours are only emitted on a terminal. When the output is redirected (the web
# interface stores it in a log file), the escape sequences would be written to
# the file: ESC is valid UTF-8 but ILLEGAL in XML 1.0, which breaks the XML-RPC
# answer the interface reads back.
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    NC=''
fi
WINRM_PORT='5985'
DBHOST=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbhost 2> /dev/null || echo localhost)
DBPORT=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbport 2> /dev/null || echo 3306)
DBUSER=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbuser 2> /dev/null || echo mmc)
DBPASS=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbpasswd)

# Non interactive / JSON state (used by the web UI)
DISCOVER_MODE=0
LIST_OUS=0
JSON_MODE=0
NONINTERACTIVE=0
STATE_FILE=""
STATE_FD=""
TARGETS_ARG=""
PASSWORD_ENV=""
SKIP_PS_SETUP=0
UUID_LOOKUP=0
CHECK_PREREQ=0
PS_SETUP=0
INSTALL_TIMEOUT=""
SMB_HELPER="${SMB_HELPER:-/usr/sbin/medulla-deploy-agent-smb.py}"
# Agent to deploy: by default the generic Medulla one (install-agent.ps1 on
# Windows). The web interface can select an entity specific agent instead
# (Admin > Entities > Download agent).
AGENT_LIN_PATH="/var/lib/pulse2/clients/lin/Medulla-Agent-linux-MINIMAL-latest.sh"
AGENT_WIN_URL=""
AGENT_WIN_REFERER=""
AGENT_WIN_INSECURE=0
AGENT_LIN_EXPLICIT=0
AGENT_LIN_URL=""
AGENT_LIN_REFERER=""
# macOS packages (.pkg, one per architecture). A directory: the right file is
# chosen on the machine from `uname -m`.
AGENT_MAC_DIR="/var/lib/pulse2/clients/mac"
# Per machine installation logs (<state dir>/logs/<machine>.log). Empty when
# there is no state file: the steps then only go to stderr.
LOG_DIR=""
# Ports scanned during a discovery. They carry the remote control services the
# web interface offers for a discovered machine.
DISCOVER_PORTS="22,445,3389,5985"
# Hosts nmap keeps in flight during a scan. The original value (512) makes nmap
# warn ("highly aggressive --min-hostgroup") and can hide slow machines without
# making a /24 any faster: 64 is measured to give the same result in the same
# time. Raise it explicitly only for very large networks.
MIN_HOSTGROUP=64
# pwsh looks for user scoped modules under $HOME/.local/share/powershell/Modules.
# The mmc-agent is started by systemd WITHOUT HOME, so PSWSMan looked missing and
# every Active Directory operation failed from the web interface while working
# from a shell. HOME is therefore always provided to pwsh.
PWSH_HOME="${BP_PWSH_HOME:-/root}"
# Optional per machine information sent by the web interface:
# [{"target":"pc1","os":"Debian 12","ports":[22],"method":"ssh"}, ...]
TARGET_INFO_JSON=""
declare -A T_METHOD=() T_TPORTS=() T_TOS=()
declare -A M_NAME=() M_IP=() M_SRC=() M_OU=() M_OS=() M_INSTALLED=() M_PORTS=() M_SERVICES=()
MACH_LIST=()

display_usage() {
    echo -e "${RED}Usage: $0 --target=<target_cidr | target_fqdn> | --server=<ad_server_name> [--port=<winrm_or_ssh_port>] [--namefilter=<filter_on_hostname>] [--domain=<user_domain>] [--username=<remote_username>] [--password=<remote_password>] [--sshkey=<path_to_ssh_key>] [--ou=<ad_ou>] [--force] [--reinstall]"
    echo -e "${NC}"
    echo "Example using network discovery and winrm:"
    echo "  $0 --target=10.10.0.0/24 --namefilter=win --username=vagrant --password=vagrant"
    echo "Example using Active Directory and winrm:"
    echo "  $0 --server=10.10.0.100 --namefilter=win --ou=OU=grp1,DC=MEDULLA,DC=int --domain=MEDULLA --username=Administrator --password=P@ssw0rd"
    echo "Example using network discovery and ssh:"
    echo "  $0 --target=10.10.0.0/24 --namefilter=win --port=22 --username=pulseuser --sshkey=/root/.ssh/id_rsa"
    echo "  $0 --target=10.0.0.0/16 --discover --min-hostgroup=256   # grand reseau uniquement"
    echo "Examples for an individual machine:"
    echo "  $0 --target=10.10.0.94/32 --username=vagrant --password=vagrant"
    echo "  $0 --target=host.siveo.net --username=pulseuser --sshkey=/root/.ssh/id_rsa"
    echo "Example for a linux machine:"
    echo "  $0 --target=10.10.0.94/32 --port=22 --username=root --sshkey=/root/.ssh/id_rsa"
    echo ""
    echo "Non interactive options (used by the web interface):"
    echo "  --discover                 only list the machines, never install"
    echo "  --list-ous                 list the Active Directory organizational units as JSON"
    echo "  --targets=a,b,c            install on an explicit machine list (skips discovery)"
    echo "  --json                     emit machine readable JSON"
    echo "  --state-file=<path>        append JSON line progress events to <path>"
    echo "  --password-env=<VAR>       read the password from the environment variable VAR"
    echo "  --non-interactive          never prompt, exit on missing arguments"
    echo "  --skip-ps-setup            do not (re)install the Powershell WSMan prerequisites"
    echo "  --timeout=<seconds>        timeout applied to each remote command"
    echo "  --agent-mac=<dir>          directory holding the macOS .pkg agents (one per architecture)"
}

# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

json_str() {
    # Encode a string as a JSON string. Every control character is escaped
    # (\u00XX) and invalid UTF-8 is dropped so the document always stays valid.
    # Byte semantics (C locale) so that ${s:i:1} walks the bytes.
    local LC_ALL=C
    local s="${1-}" out="" c h i
    if [[ $s != *[![:print:]]* ]]; then
        # Fast path: printable ASCII only.
        s=${s//\\/\\\\}
        s=${s//\"/\\\"}
        printf '"%s"' "$s"
        return 0
    fi
    if command -v iconv >/dev/null 2>&1; then
        # The sentinel keeps trailing newlines through the command substitution.
        s=$(printf '%sx' "$s" | iconv -c -f UTF-8 -t UTF-8 2>/dev/null)
        s=${s%x}
    fi
    for ((i = 0; i < ${#s}; i++)); do
        c="${s:i:1}"
        case "$c" in
            '"') out+='\"' ;;
            '\') out+='\\' ;;
            $'\n') out+='\n' ;;
            $'\r') ;;
            $'\t') out+='\t' ;;
            [[:cntrl:]])
                printf -v h '\\u%04x' "'$c"
                out+="$h"
                ;;
            *) out+="$c" ;;
        esac
    done
    printf '"%s"' "$out"
}

json_bool() {
    if [ "${1-}" = "1" ] || [ "${1-}" = "true" ]; then printf 'true'; else printf 'false'; fi
}

info() {
    # Human readable progress. In JSON mode it must not pollute stdout, which
    # only carries the machine readable answer.
    if [ "$JSON_MODE" = "1" ]; then
        echo -e "$@" >&2
    else
        echo -e "$@"
    fi
}

state_event() {
    # Append one JSON event line to the state file (atomic under flock).
    [ -z "$STATE_FILE" ] && return 0
    if [ -n "$STATE_FD" ]; then
        flock -x "$STATE_FD" 2>/dev/null
        printf '%s\n' "$1" >&"$STATE_FD"
        flock -u "$STATE_FD" 2>/dev/null
    else
        printf '%s\n' "$1" >> "$STATE_FILE"
    fi
}

service_of_port() {
    # Port -> remote control service name understood by the web interface.
    case "${1-}" in
        22) printf 'ssh' ;;
        445) printf 'smb' ;;
        3389) printf 'rdp' ;;
        5985) printf 'winrm' ;;
        *) printf '' ;;
    esac
}

services_json() {
    # JSON array of the services found on a machine, from its open ports.
    local t="${1-}" port first=1 out=""
    local IFS=','
    for port in ${M_PORTS[$t]:-}; do
        [ -z "$port" ] && continue
        if [ "$first" = "0" ]; then out="$out,"; fi
        first=0
        out="$out$(json_str "$(service_of_port "$port")")"
    done
    printf '[%s]' "$out"
}

ports_json() {
    local t="${1-}" port first=1 out=""
    local IFS=','
    for port in ${M_PORTS[$t]:-}; do
        [ -z "$port" ] && continue
        if [ "$first" = "0" ]; then out="$out,"; fi
        first=0
        out="$out$port"
    done
    printf '[%s]' "$out"
}

machine_json() {
    local t="${1-}"
    printf '{"target":%s,"name":%s,"ip":%s,"source":%s,"ou":%s,"os":%s,"installed":%s,"ports":%s,"services":%s}' \
        "$(json_str "$t")" \
        "$(json_str "${M_NAME[$t]:-$t}")" \
        "$(json_str "${M_IP[$t]:-}")" \
        "$(json_str "${M_SRC[$t]:-}")" \
        "$(json_str "${M_OU[$t]:-}")" \
        "$(json_str "${M_OS[$t]:-}")" \
        "$(json_bool "${M_INSTALLED[$t]:-0}")" \
        "$(ports_json "$t")" \
        "$(services_json "$t")"
}

json_error() {
    # Record a fatal error and leave with a JSON (or plain) message.
    local msg="${1-}"
    if [ "$JSON_MODE" = "1" ]; then
        state_event "{\"event\":\"error\",\"message\":$(json_str "$msg")}"
        printf '{"status":"error","message":%s,"machines":[]}\n' "$(json_str "$msg")"
    else
        echo -e "${RED}${msg}${NC}"
    fi
    exit 1
}

add_machine() {
    # add_machine <target> [ip] [name] [source] [ou] [os]
    local target="${1-}"
    [ -z "$target" ] && return 0
    if [ -z "${M_NAME[$target]+x}" ]; then
        MACH_LIST+=("$target")
    fi
    M_NAME[$target]="${3:-$target}"
    if [ -n "${2-}" ]; then M_IP[$target]="$2"; fi
    M_SRC[$target]="${4:-}"
    if [ -n "${5-}" ]; then M_OU[$target]="$5"; fi
    if [ -n "${6-}" ]; then M_OS[$target]="$6"; fi
    if [ -n "${7-}" ]; then M_PORTS[$target]="$7"; fi
    M_INSTALLED[$target]=0
}

dig_ipv4() {
    # First IPv4 address of a name ("dig +short" may also print CNAMEs or
    # error lines). Short timeout: a dead resolver must not stall a /24 scan.
    local name="${1-}"
    [ -z "$name" ] && return 0
    case "$name" in -*) return 0 ;; esac
    dig +short +time=2 +tries=1 "$name" 2>/dev/null \
        | grep -E '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' | head -n1
}

dig_ptr() {
    # Reverse name of an IP, without the trailing dot ("" when unknown).
    local ip="${1-}"
    [ -z "$ip" ] && return 0
    case "$ip" in -*) return 0 ;; esac
    dig +short +time=2 +tries=1 -x "$ip" 2>/dev/null \
        | grep -E '^[A-Za-z0-9_.-]+$' | head -n1 | sed 's/\.$//'
}

add_single_target() {
    # Register a single machine given as an IP or a FQDN, resolving the
    # reverse / forward DNS so the UI can display something meaningful.
    local host="${1-}"
    local ip="" ptr=""
    if [[ "$host" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        ip="$host"
        ptr=$(dig_ptr "$ip")
        add_machine "$ip" "$ip" "${ptr:-$ip}" "explicit" "" ""
    else
        ip=$(dig_ipv4 "$host")
        add_machine "$host" "$ip" "$host" "explicit" "" ""
    fi
}

# ---------------------------------------------------------------------------
# PowerShell helpers
# ---------------------------------------------------------------------------

ps_run() {
    # Run the powershell script read on stdin. Credentials are passed through
    # the environment so that the password never appears in the process
    # command line (argv is world readable through ps).
    # $1 = remote target (optional), $2 = "with-timeout" to apply INSTALL_TIMEOUT
    # $3 = WinRM port for this machine (defaults to the port from the form)
    local target="${1-}"
    local use_timeout="${2-}"
    local winrm_port="${3-${PORT-}}"
    local ps_script
    ps_script=$(cat)
    # PowerShell reads "-Command -" LINE BY LINE: a multi-line block (try/catch,
    # scriptblock...) is never executed. The blocks below are written with
    # explicit ";" separators, and newlines are folded away here so that stdin
    # always carries a single line.
    ps_script=$(printf '%s' "$ps_script" | tr '\n' ' ')

    # Always "1" or "0": the target tests it explicitly, a non empty "0" string
    # would be truthy in PowerShell.
    local insecure=0
    [ "${AGENT_WIN_INSECURE-0}" = "1" ] && insecure=1

    # --foreground: timeout stays in our process group, so the signal sent to
    # the group by the web backend on cancellation also reaches pwsh.
    if [ "$use_timeout" = "with-timeout" ] && [ -n "$INSTALL_TIMEOUT" ]; then
        HOME="${PWSH_HOME}" BP_USERNAME="${USERNAME-}" BP_PASSWORD="${PASSWORD-}" BP_DOMAIN="${DOMAIN-}" \
        BP_SERVER="${SERVER-}" BP_TARGET="$target" BP_FILTER="${FILTER-}" BP_OU="${OU-}" \
        BP_PORT="${winrm_port}" BP_AGENT_URL="${AGENT_WIN_URL-}" BP_AGENT_REFERER="${AGENT_WIN_REFERER-}" \
        BP_AGENT_INSECURE="$insecure" \
            timeout --foreground --signal=TERM "$INSTALL_TIMEOUT" pwsh -NoProfile -NonInteractive -Command - <<<"$ps_script" 2>&1
    else
        HOME="${PWSH_HOME}" BP_USERNAME="${USERNAME-}" BP_PASSWORD="${PASSWORD-}" BP_DOMAIN="${DOMAIN-}" \
        BP_SERVER="${SERVER-}" BP_TARGET="$target" BP_FILTER="${FILTER-}" BP_OU="${OU-}" \
        BP_PORT="${winrm_port}" BP_AGENT_URL="${AGENT_WIN_URL-}" BP_AGENT_REFERER="${AGENT_WIN_REFERER-}" \
        BP_AGENT_INSECURE="$insecure" \
            pwsh -NoProfile -NonInteractive -Command - <<<"$ps_script" 2>&1
    fi
}

ps_json_parse_machines() {
    # Convert the JSON produced by Get-ADComputer into TAB separated lines:
    # name <TAB> ip <TAB> os <TAB> distinguishedName
    # On error, print "__ERROR__" <TAB> message.
    python3 -c '
import json, re, sys

raw = sys.stdin.read()
# pwsh emits terminal escape sequences even with -NonInteractive
raw = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", raw)
start = raw.find("{")
if start < 0:
    start = raw.find("[")
if start is None or start < 0:
    print("__ERROR__\tNo JSON answer from the Active Directory server")
    sys.exit(0)
try:
    data = json.loads(raw[start:])
except Exception as exc:
    print("__ERROR__\tUnreadable answer from the Active Directory server: %s" % exc)
    sys.exit(0)

if isinstance(data, dict) and "ok" in data:
    if not data.get("ok"):
        print("__ERROR__\t%s" % (data.get("error") or "Active Directory query failed"))
        sys.exit(0)
    data = data.get("items") or []
if isinstance(data, dict):
    data = [data]

def first(value):
    if isinstance(value, list):
        return (value[0] if value else "") or ""
    return value or ""

for item in data:
    if not isinstance(item, dict):
        continue
    name = first(item.get("Name")).strip()
    ip = first(item.get("IPv4Address")).strip()
    osys = first(item.get("OperatingSystem")).strip()
    dn = first(item.get("DistinguishedName")).strip()
    if name:
        print("\t".join([name, ip, osys, dn]))
'
}

ps_json_parse_ous() {
    # name <TAB> dn <TAB> canonicalName <TAB> kind <TAB> machines <TAB> total <TAB> parent
    #
    # Only the branches that really hold computers are printed: "total" counts
    # the whole subtree, so an organizational unit with machines anywhere below
    # keeps its place in the tree, and empty ones disappear.
    # On error, print "__ERROR__" <TAB> message.
    python3 -c '
import json, re, sys

raw = sys.stdin.read()
# pwsh emits terminal escape sequences even with -NonInteractive
raw = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", raw)
start = raw.find("{")
if start < 0:
    start = raw.find("[")
if start is None or start < 0:
    print("__ERROR__\tNo JSON answer from the Active Directory server")
    sys.exit(0)
try:
    data = json.loads(raw[start:])
except Exception as exc:
    print("__ERROR__\tUnreadable answer from the Active Directory server: %s" % exc)
    sys.exit(0)

if isinstance(data, dict) and "ok" in data:
    if not data.get("ok"):
        print("__ERROR__\t%s" % (data.get("error") or "Active Directory query failed"))
        sys.exit(0)
    data = data.get("items") or []
if isinstance(data, dict):
    data = [data]

def first(value):
    if isinstance(value, list):
        return (value[0] if value else "") or ""
    return value or ""

def number(value):
    if isinstance(value, list):
        value = value[0] if value else 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


SEPARATOR = re.compile(r"(?<!\\),")


for item in data:
    if not isinstance(item, dict):
        continue
    name = first(item.get("Name")).strip()
    dn = first(item.get("DistinguishedName")).strip()
    cn = first(item.get("CanonicalName")).strip()
    kind = (first(item.get("Kind")).strip() or "ou").lower()
    machines = number(item.get("Direct"))
    total = number(item.get("Total"))
    parts = SEPARATOR.split(dn, 1)
    parent = parts[1] if len(parts) > 1 else ""
    # The domain itself is always kept, even when it holds no computer.
    if not parent and not name:
        continue
    if parent and total <= 0:
        continue
    print("\t".join([name, dn, cn, kind, str(machines), str(total), parent]))
'
}

check_prerequisites() {
    # Machine readable prerequisite report for the web interface.
    local have_pwsh=false have_wsman=false have_nmap=false have_python=false have_mysql=false have_dig=false
    command -v pwsh >/dev/null 2>&1 && have_pwsh=true
    command -v nmap >/dev/null 2>&1 && have_nmap=true
    command -v python3 >/dev/null 2>&1 && have_python=true
    command -v mysql >/dev/null 2>&1 && have_mysql=true
    command -v dig >/dev/null 2>&1 && have_dig=true
    if [ "$have_pwsh" = "true" ]; then
        wsman_available && have_wsman=true
    fi
    printf '{"status":"ok","prerequisites":{"pwsh":%s,"wsman":%s,"nmap":%s,"python3":%s,"mysql":%s,"dig":%s}}\n' \
        "$have_pwsh" "$have_wsman" "$have_nmap" "$have_python" "$have_mysql" "$have_dig"
    exit 0
}

# Query the xmppmaster database ($1 = SQL). The password goes through an
# anonymous option file: never in argv (visible in ps), and --defaults-file also
# bypasses /root/.my.cnf, whose password would override MYSQL_PWD.
xmpp_mysql() {
    local pass="${DBPASS//\\/\\\\}"
    pass="${pass//\"/\\\"}"
    mysql --defaults-file=<(printf '[client]\nhost=%s\nport=%s\nuser=%s\npassword="%s"\n' \
        "$DBHOST" "$DBPORT" "$DBUSER" "$pass") -Ns xmppmaster -e "$1" 2>/dev/null
}

uuid_lookup() {
    # Read hostnames on stdin and print "hostname<TAB>resolved hostname<TAB>uuid<TAB>jid"
    # for every machine already known by the Medulla server.
    local host sql found resolved uuid jid known first=1
    state_event "{\"event\":\"start\",\"mode\":\"uuid-lookup\",\"ts\":$(date +%s)}"
    printf '{"status":"ok","mode":"uuid-lookup","machines":{'
    while IFS= read -r host; do
        host="$(echo "$host" | xargs)"
        [ -z "$host" ] && continue
        host="${host//\'/}"
        resolved=""
        uuid=""
        jid=""
        if [[ "$host" =~ ^[A-Za-z0-9._-]+$ ]]; then
            sql="SELECT hostname, uuid_inventorymachine, jid FROM machines WHERE hostname='${host%%.*}' OR hostname LIKE '${host%%.*}.%' LIMIT 1"
            found=$(xmpp_mysql "$sql" | head -n1)
            if [ -n "$found" ]; then
                resolved=$(printf '%s' "$found" | cut -f1)
                uuid=$(printf '%s' "$found" | cut -f2)
                jid=$(printf '%s' "$found" | cut -f3)
            fi
        fi
        known=false
        if [ -n "$uuid" ] || [ -n "$jid" ]; then known=true; fi
        state_event "{\"event\":\"machine_uuid\",\"host\":$(json_str "$host"),\"hostname\":$(json_str "$resolved"),\"uuid\":$(json_str "$uuid"),\"jid\":$(json_str "$jid"),\"known\":${known}}"
        if [ "$first" = "0" ]; then printf ','; fi
        first=0
        printf '%s:{"hostname":%s,"uuid":%s,"jid":%s,"known":%s}' \
            "$(json_str "$host")" "$(json_str "$resolved")" "$(json_str "$uuid")" "$(json_str "$jid")" "$known"
    done
    printf '}}\n'
    state_event "{\"event\":\"end\",\"status\":\"ok\"}"
    exit 0
}

# ---------------------------------------------------------------------------
# Inventory helper
# ---------------------------------------------------------------------------

is_installed() {
    # $1 = machine name, fqdn or ip ; returns 0 when the machine already
    # declared itself to the Medulla server.
    local target="${1-}"
    [ -z "$target" ] && return 1
    command -v mysql >/dev/null 2>&1 || return 1
    # The values come from the web interface: only a strict character set is
    # ever put in a query (same gate as uuid_lookup, plus ":" for IPv6).
    # Anything else is simply reported as "not installed".
    [[ "$target" =~ ^[A-Za-z0-9._:-]+$ ]] || return 1
    local host="${target%%.*}"
    local ip=""
    if [[ "$target" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        ip="$target"
        host=$(dig_ptr "$ip")
        host="${host%%.*}"
    fi
    [[ -z "$host" || "$host" =~ ^[A-Za-z0-9._:-]+$ ]] || return 1
    local sql="SELECT hostname FROM machines WHERE hostname='${host}'"
    if [ -n "$ip" ]; then
        sql="$sql OR ip_xmpp='${ip}'"
    fi
    local found
    found=$(xmpp_mysql "$sql")
    [ -n "$found" ]
}

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

validate_target() {
    # --target is either an IPv4 address / CIDR or a host name. It ends up as an
    # nmap / dig argument: refuse anything else, and anything starting with '-'.
    local target="${1-}"
    local cidr_regex='^((25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])(/([0-9]|[1-2][0-9]|3[0-2]))?$'
    local host_regex='^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$'
    local min_prefix="${BP_MIN_CIDR_PREFIX:-16}"
    local prefix
    if ! [[ "$min_prefix" =~ ^[0-9]{1,2}$ ]] || [ "$((10#$min_prefix))" -lt 8 ] || [ "$((10#$min_prefix))" -gt 32 ]; then
        min_prefix=16
    fi
    min_prefix=$((10#$min_prefix))
    if [[ "$target" == -* ]]; then
        info "${RED}$target is not a valid CIDR or FQDN"
        display_usage
        exit 1
    elif [[ "$target" =~ $cidr_regex ]]; then
        if [[ "$target" == */* ]]; then
            prefix="${target#*/}"
            if [ "$((10#$prefix))" -lt "$min_prefix" ]; then
                info "${RED}$target is too large: the smallest prefix allowed is /$min_prefix"
                exit 1
            fi
            info "${GREEN}Running with CIDR $target"
        else
            # A plain address is a single machine.
            info "${GREEN}Running with IP $target"
            FQDN=1
        fi
    elif [[ "$target" =~ $host_regex ]] && host "$target" >/dev/null 2>&1; then
        info "${GREEN}Running with FQDN $target"
        FQDN=1
    else
        info "${RED}$target is not a valid CIDR or FQDN"
        display_usage
        exit 1
    fi
}

check_arguments() {
    if [[ $# -lt 1 ]]; then
        display_usage
        exit 1
    fi
    # First pass: the output mode must be known before any parsing message is
    # emitted, options are not necessarily given in a friendly order.
    local pre
    for pre in "$@"; do
        case $pre in
            --json) JSON_MODE=1 ;;
            --non-interactive) NONINTERACTIVE=1 ;;
        esac
    done
    for i in "$@"; do
        case $i in
            --target=*)
                TARGET="${i#*=}"
                validate_target "$TARGET"
                ;;
            --server=*)
                SERVER="${i#*=}"
                info "${GREEN}Querying Active Directory $SERVER"
                ;;
            --namefilter=*)
                FILTER="${i#*=}"
                info "${GREEN}Filtering on hostname: *$FILTER*"
                ;;
            --port=*)
                PORT="${i#*=}"
                ;;
            --username=*)
                USERNAME="${i#*=}"
                ;;
            --password=*)
                PASSWORD="${i#*=}"
                ;;
            --sshkey=*)
                SSHKEY="${i#*=}"
                ;;
            --domain=*)
                DOMAIN="${i#*=}"
                ;;
            --ou=*)
                OU="${i#*=}"
                info "${GREEN}Filtering on ou: *$OU*"
                ;;
            --force*)
                FORCE=1
                ;;
            --reinstall*)
                REINSTALL=1
                ;;
            --debug*)
                DEBUG=1
                ;;
            --discover)
                DISCOVER_MODE=1
                ;;
            --list-ous)
                LIST_OUS=1
                ;;
            --json)
                JSON_MODE=1
                ;;
            --non-interactive)
                NONINTERACTIVE=1
                ;;
            --skip-ps-setup)
                SKIP_PS_SETUP=1
                ;;
            --ps-setup)
                PS_SETUP=1
                ;;
            --uuid-lookup)
                UUID_LOOKUP=1
                ;;
            --check-prereq)
                CHECK_PREREQ=1
                ;;
            --target-info=*)
                TARGET_INFO_JSON="${i#*=}"
                ;;
            --min-hostgroup=*)
                MIN_HOSTGROUP="${i#*=}"
                ;;
            --discover-ports=*)
                DISCOVER_PORTS="${i#*=}"
                ;;
            --agent-lin=*)
                AGENT_LIN_PATH="${i#*=}"
                AGENT_LIN_EXPLICIT=1
                ;;
            --agent-mac=*)
                AGENT_MAC_DIR="${i#*=}"
                ;;
            --agent-lin-url=*)
                AGENT_LIN_URL="${i#*=}"
                ;;
            --agent-lin-referer=*)
                AGENT_LIN_REFERER="${i#*=}"
                ;;
            --agent-win-url=*)
                AGENT_WIN_URL="${i#*=}"
                ;;
            --agent-win-referer=*)
                AGENT_WIN_REFERER="${i#*=}"
                ;;
            --agent-win-insecure)
                AGENT_WIN_INSECURE=1
                ;;
            --state-file=*)
                STATE_FILE="${i#*=}"
                ;;
            --targets=*)
                TARGETS_ARG="${i#*=}"
                ;;
            --password-env=*)
                PASSWORD_ENV="${i#*=}"
                ;;
            --timeout=*)
                INSTALL_TIMEOUT="${i#*=}"
                ;;
            *)
                # unknown option
                printf 'Unknown option: %s\n' "$i" >&2
                display_usage >&2
                exit 2
                ;;
        esac
    done
    if [ -z ${PORT+x} ]; then
        PORT=${WINRM_PORT}
    fi
    parse_target_info

    # Password from an environment variable: keeps the secret out of argv.
    if [ -n "$PASSWORD_ENV" ]; then
        if ! [[ "$PASSWORD_ENV" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
            json_error "Invalid environment variable name for --password-env"
        fi
        if [ -z "${!PASSWORD_ENV-}" ]; then
            json_error "Environment variable $PASSWORD_ENV is empty"
        fi
        PASSWORD="${!PASSWORD_ENV}"
    fi

    # --targets forces the machine list, no discovery at all.
    if [ -n "$TARGETS_ARG" ]; then
        local t
        local IFS=','
        for t in $TARGETS_ARG; do
            t="$(echo "$t" | xargs)"
            [ -z "$t" ] && continue
            add_machine "$t" "" "$t" "explicit" "" ""
        done
    fi

    # Every search and every installation needs an account; only the checks that
    # never touch a machine are exempt. A plain network sweep used to run without
    # credentials: it now follows the same rule as Active Directory, so a search
    # always leaves something usable for the installation that follows.
    local need_creds=1
    local ad_mode=0
    # A server is only given to reach Active Directory (discovery or OU listing).
    if [ -n "${SERVER-}" ]; then
        ad_mode=1
    fi
    if [ "$UUID_LOOKUP" = "1" ] \
       || [ "$CHECK_PREREQ" = "1" ] \
       || [ "$PS_SETUP" = "1" ]; then
        need_creds=0
    fi

    # An SSH key stands in for the login/password pair. Active Directory needs a
    # real domain account, where an SSH key is of no use.
    if [ "$need_creds" = "1" ] && [ "$ad_mode" = "1" ] \
       && { [ -z "${USERNAME-}" ] || [ -z "${PASSWORD-}" ]; }; then
        if [ "$NONINTERACTIVE" = "1" ]; then
            json_error "Please provide a domain account for accessing the machines and/or the Active Directory."
        fi
        echo "Please provide a domain account for accessing the machines and/or the Active Directory."
        read -r -p "Username: " USERNAME
        read -r -s -p "Password: " PASSWORD
        echo
        # Cater for inclusion of domain in username eg. MEDULLA\Administrateur
        USERNAME=$(echo ${USERNAME} | sed 's~\\~\\\\~g')
    elif [ "$need_creds" = "1" ] && [ -z "${SSHKEY-}" ]; then
        # Check if a user name and password is given
        if [ -z "${USERNAME-}" ] || [ -z "${PASSWORD-}" ]; then
            if [ "$NONINTERACTIVE" = "1" ]; then
                json_error "Please provide a login and a password (or an SSH key) to search the machines."
            fi
            echo "Please provide a login and a password (or an SSH key) to search the machines."
            read -r -p "Username: " USERNAME
            read -r -s -p "Password: " PASSWORD
            echo
            # Cater for inclusion of domain in username eg. MEDULLA\Administrateur
            USERNAME=$(echo ${USERNAME} | sed 's~\\~\\\\~g')
        fi
    else
        # An SSH key is given: only a user name is still needed.
        if [ "$need_creds" = "1" ] && [ -z "${USERNAME-}" ]; then
            if [ "$NONINTERACTIVE" = "1" ]; then
                json_error "Please provide a user name for the ssh connection."
            fi
            echo "Please provide a user name for the ssh connection."
            read -r -p "Username: " USERNAME
        fi
    fi

    export USERNAME PASSWORD
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

check_ps_available() {
    if ! command -v pwsh >/dev/null 2>&1; then
        json_error "PowerShell (pwsh) is not installed on this server."
    fi
}

wsman_available() {
    # The PSWSMan module provides the WSMan client used by Invoke-Command
    # -ComputerName (WinRM remoting) and by the Active Directory cmdlets.
    local out ps_script
    # Hard timeout: pwsh can hang while probing the module path, and this
    # function is used by web driven code paths.
    ps_script='if (Get-Module -ListAvailable -Name PSWSMan | Select-Object -First 1) { "OK" } else { "MISSING" }'
    out=$(HOME="${PWSH_HOME}" BP_USERNAME="${USERNAME-}" BP_PASSWORD="${PASSWORD-}" \
          timeout 25 pwsh -NoProfile -NonInteractive -Command - <<<"$ps_script" 2>/dev/null \
          | tr -d '\r' | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g')
    [[ "$out" == *OK* ]]
}

require_wsman() {
    # $1 = what the caller wanted to do, for the error message
    if ! wsman_available; then
        json_error "The PowerShell WSMan client (PSWSMan) is missing on the Medulla server: $1 is not possible. Run the PowerShell prerequisites from the web interface (or: $0 --ps-setup) and try again."
    fi
}

run_ps_setup() {
    # Install the Powershell remote execution prerequisites, machine readable.
    local step
    state_event "{\"event\":\"start\",\"mode\":\"ps-setup\",\"ts\":$(date +%s)}"
    if ! check_ps_available 2>/dev/null; then :; fi
    # -Scope AllUsers: the module lands in /usr/local/share/powershell/Modules,
    # found by every process whatever its HOME.
    for step in "Register-PSRepository -Default" "Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted" "Install-Module -Name PSWSMan -Force -AllowClobber -Scope AllUsers" "Install-WSMan"; do
        info "Running: pwsh -Command \"$step\""
        if ! HOME="${PWSH_HOME}" pwsh -NoProfile -NonInteractive -Command "$step" >/dev/null 2>&1; then
            info "${RED}Failed: $step${NC}"
        fi
    done
    if wsman_available; then
        printf '{"status":"ok","wsman":true}\n'
        state_event "{\"event\":\"end\",\"status\":\"ok\",\"wsman\":true}"
    else
        printf '{"status":"error","wsman":false,"message":"The PSWSMan module is still unavailable after the setup."}\n'
        state_event "{\"event\":\"end\",\"status\":\"error\",\"wsman\":false}"
        exit 1
    fi
    exit 0
}

# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

get_machines_list_nmap() {
    # Scan the local network and record every host with the wanted port open.
    local IP MACH PTR OUT RC MATCHES
    if [ -n "${DEBUG-}" ]; then
        info "${GREEN}Running nmap -T4 -Pn --max-rtt-timeout 200ms --initial-rtt-timeout 150ms --min-hostgroup ${MIN_HOSTGROUP} -n --open -p ${DISCOVER_PORTS} -oG - -- ${TARGET} | grep \"/open\""
    fi
    if ! command -v nmap >/dev/null 2>&1; then
        json_error "nmap is not installed on the Medulla server."
    fi
    # Not a process substitution: a failing nmap must not look like an empty
    # network. stderr is kept in OUT to explain the failure.
    OUT=$(nmap -T4 -Pn --max-rtt-timeout 200ms --initial-rtt-timeout 150ms --min-hostgroup "${MIN_HOSTGROUP}" -n --open -p "${DISCOVER_PORTS}" -oG - -- "${TARGET}" 2>&1)
    RC=$?
    if [ "$RC" -ne 0 ]; then
        json_error "nmap failed (exit code $RC): $(printf '%s' "$OUT" | tr '\n' ' ' | tr -s ' ' | cut -c1-300)"
    fi
    MATCHES=$(printf '%s\n' "$OUT" | grep '^Host: .*/open/' || true)
    local LINE PORTS
    while IFS= read -r LINE; do
        [ -z "$LINE" ] && continue
        IP=$(printf '%s' "$LINE" | awk '{ print $2 }')
        # "22/open/tcp//ssh///, 5985/open/tcp//wsman///" -> "22,5985"
        PORTS=$(printf '%s' "$LINE" | grep -oE '[0-9]+/open' | cut -d/ -f1 | sort -n -u | paste -sd, -)
        [ -z "$IP" ] && continue
        PTR=$(dig_ptr "${IP}")
        MACH=${PTR:-$IP}
        if [ -n "${FILTER-}" ]; then
            # Case insensitive name filter.
            if [[ "${MACH,,}" != *"${FILTER,,}"* ]]; then
                continue
            fi
        fi
        add_machine "$MACH" "$IP" "$MACH" "network" "" "" "$PORTS"
    done <<< "$MATCHES"
}

get_machines_list_ad() {
    # Query Active Directory and record the computers with their IP and OU.
    local PS OUT line name ip osys dn err=""
    PS='$ErrorActionPreference = "Stop";
try {
    $pw = ConvertTo-SecureString -AsPlainText -Force -String $env:BP_PASSWORD;
    $cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $env:BP_USERNAME,$pw;
    $items = Invoke-Command -ComputerName $env:BP_SERVER -Authentication Negotiate -Credential $cred -ScriptBlock {
        param($ou, $filterName);
        Import-Module ActiveDirectory;
        $params = @{ Properties = @("IPv4Address","OperatingSystem"); ErrorAction = "Stop" };
        if ($filterName) { $params["LDAPFilter"] = "(name=*$filterName*)" } else { $params["Filter"] = "*" };
        if ($ou) { $params["SearchBase"] = $ou };
        Get-ADComputer @params | Select-Object Name, IPv4Address, OperatingSystem, DistinguishedName
    } -ArgumentList $env:BP_OU, $env:BP_FILTER;
    @{ ok = $true; items = @($items) } | ConvertTo-Json -Compress -Depth 5
} catch {
    @{ ok = $false; error = $_.Exception.Message } | ConvertTo-Json -Compress -Depth 5
}'
    OUT=$(ps_run "" <<<"$PS")
    if [ -z "$OUT" ]; then
        json_error "No answer from the Active Directory server ${SERVER}."
    fi
    # Fields are re-separated with US (0x1f), a non blanks IFS character: with a
    # TAB, "read" would merge consecutive separators and an empty IPv4Address
    # would shift the following fields.
    while IFS=$'\037' read -r name ip osys dn; do
        [ -z "$name" ] && continue
        if [ "$name" = "__ERROR__" ]; then
            err="$ip"
            continue
        fi
        if [ -n "${FILTER-}" ]; then
            if [[ "${name,,}" != *"${FILTER,,}"* ]]; then
                continue
            fi
        fi
        add_machine "$name" "$ip" "$name" "ad" "$dn" "$osys"
    done < <(printf '%s' "$OUT" | ps_json_parse_machines | tr '\t' '\037')
    scan_services_ad
    if [ -n "$err" ]; then
        json_error "Active Directory query failed: $err"
    fi
}

list_ad_ous() {
    # List the Active Directory organizational units (JSON output).
    local PS OUT name dn cn first=1 err=""
    # The domain, its organizational units and their computers are fetched as a
    # whole: asking the directory per unit would be far slower. Each unit is
    # then given the number of computers it holds directly and in its subtree.
    # (No '#' comment inside PS: ps_run folds the block onto a single line and a
    # comment would swallow the rest of the script.)
    PS='$ErrorActionPreference = "Stop";
try {
    $pw = ConvertTo-SecureString -AsPlainText -Force -String $env:BP_PASSWORD;
    $cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $env:BP_USERNAME,$pw;
    $items = Invoke-Command -ComputerName $env:BP_SERVER -Authentication Negotiate -Credential $cred -ScriptBlock {
        Import-Module ActiveDirectory;
        $domain = Get-ADDomain;
        $domainDN = $domain.DistinguishedName;
        $ous = @(Get-ADOrganizationalUnit -Filter * -Properties CanonicalName |
                 Select-Object Name, DistinguishedName, CanonicalName);
        $computers = @(Get-ADComputer -Filter * -Properties DistinguishedName |
                       Select-Object -ExpandProperty DistinguishedName);
        $containers = @(Get-ADObject -SearchBase $domainDN -SearchScope OneLevel -Filter "objectClass -eq ""container""" -Properties CanonicalName |
                        Select-Object Name, DistinguishedName, CanonicalName);
        $direct = @{};
        $total = @{};
        foreach ($dn in $computers) {
            $parts = $dn -split "(?<!\\),";
            if ($parts.Count -lt 2) { continue }
            for ($i = 1; $i -lt $parts.Count; $i++) {
                $ancestor = ($parts[$i..($parts.Count - 1)] -join ",");
                if ($i -eq 1) { $direct[$ancestor] = 1 + [int]$direct[$ancestor] }
                $total[$ancestor] = 1 + [int]$total[$ancestor]
            }
        }
        $items = @();
        $items += [pscustomobject]@{
            Name = $domain.Name; DistinguishedName = $domainDN;
            CanonicalName = $domain.DNSRoot; Kind = "domain";
            Direct = [int]$direct[$domainDN]; Total = [int]$total[$domainDN] };
        foreach ($ou in $ous) {
            $items += [pscustomobject]@{
                Name = $ou.Name; DistinguishedName = $ou.DistinguishedName;
                CanonicalName = $ou.CanonicalName; Kind = "ou";
                Direct = [int]$direct[$ou.DistinguishedName];
                Total = [int]$total[$ou.DistinguishedName] };
        }
        foreach ($container in $containers) {
            $containerTotal = [int]$total[$container.DistinguishedName];
            if ($containerTotal -le 0) { continue }
            $items += [pscustomobject]@{
                Name = $container.Name; DistinguishedName = $container.DistinguishedName;
                CanonicalName = $container.CanonicalName; Kind = "container";
                Direct = [int]$direct[$container.DistinguishedName];
                Total = $containerTotal };
        }
        $items
    };
    @{ ok = $true; items = @($items) } | ConvertTo-Json -Compress -Depth 5
} catch {
    @{ ok = $false; error = $_.Exception.Message } | ConvertTo-Json -Compress -Depth 5
}'
    if ! command -v python3 >/dev/null 2>&1; then
        json_error "python3 is required to list the organizational units."
    fi
    OUT=$(ps_run "" <<<"$PS")

    state_event "{\"event\":\"start\",\"mode\":\"list-ous\",\"ts\":$(date +%s)}"
    local body=""
    while IFS=$'\037' read -r name dn cn kind machines total parent; do
        [ -z "$dn" ] && continue
        if [ "$name" = "__ERROR__" ]; then
            err="$dn"
            continue
        fi
        machines="${machines:-0}"
        total="${total:-0}"
        if [ "$first" = "0" ]; then body="$body,"; fi
        first=0
        entry="{\"name\":$(json_str "$name"),\"dn\":$(json_str "$dn"),\"canonical\":$(json_str "$cn"),\"kind\":$(json_str "$kind"),\"machines\":$machines,\"total\":$total,\"parent\":$(json_str "$parent")}"
        body="$body$entry"
        state_event "{\"event\":\"ou\",$entry}"
    done < <(printf '%s' "$OUT" | ps_json_parse_ous | tr '\t' '\037')
    if [ -n "$err" ]; then
        json_error "Active Directory query failed: $err"
    fi
    printf '{"status":"ok","ous":[%s]}\n' "$body"
    state_event "{\"event\":\"end\",\"status\":\"ok\"}"
    exit 0
}

scan_explicit_services() {
    # Machines registered without any port (single target, --targets list) were
    # never scanned: the OS detection and the remote control buttons need their
    # services too, so scan them in a single nmap pass.
    local targets=() entry ip line ports
    for entry in "${MACH_LIST[@]}"; do
        [ -n "${M_PORTS[$entry]:-}" ] && continue
        if [ -z "${M_IP[$entry]:-}" ]; then
            M_IP[$entry]=$(dig_ipv4 "$entry")
        fi
        ip="${M_IP[$entry]:-}"
        [ -z "$ip" ] && continue
        targets+=("$ip")
    done
    [ ${#targets[@]} -eq 0 ] && return 0
    if [ -n "${DEBUG-}" ]; then
        info "${GREEN}Scanning the services of ${#targets[@]} machine(s) given explicitly"
    fi
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        ip=$(printf '%s' "$line" | awk '{ print $2 }')
        ports=$(printf '%s' "$line" | grep -oE '[0-9]+/open' | cut -d/ -f1 | sort -n -u | paste -sd, -)
        for entry in "${MACH_LIST[@]}"; do
            if [ "${M_IP[$entry]:-}" = "$ip" ]; then
                M_PORTS[$entry]="$ports"
            fi
        done
    done < <(nmap -T4 -Pn -n --open -p "${DISCOVER_PORTS}" "${targets[@]}" -oG - 2>/dev/null | grep "/open")
}

parse_target_info() {
    # Fill the per machine transport tables from --target-info. TABs are turned
    # into US (0x1f) so that "read" keeps empty fields (a TAB IFS merges them).
    [ -z "$TARGET_INFO_JSON" ] && return 0
    local line target method ports osys
    while IFS=$'\037' read -r target method ports osys; do
        [ -z "$target" ] && continue
        T_METHOD[$target]="$method"
        T_TPORTS[$target]="$ports"
        T_TOS[$target]="$osys"
    done < <(printf '%s' "$TARGET_INFO_JSON" | python3 -c '
import json, sys
try:
    data = json.loads(sys.stdin.read())
except Exception:
    sys.exit(0)
if not isinstance(data, list):
    sys.exit(0)
for item in data:
    if not isinstance(item, dict):
        continue
    target = str(item.get("target") or "").replace("\t", " ")
    method = str(item.get("method") or "")
    ports = ",".join(str(p) for p in (item.get("ports") or []) if isinstance(p, int))
    osys = str(item.get("os") or "").replace("\t", " ")
    print("%s\t%s\t%s\t%s" % (target, method, ports, osys))
' 2>/dev/null | tr '\t' '\037')
}

choose_transport() {
    # winrm | ssh | smb | "" (unknown: keep the historical target probe).
    # smb (Windows without WinRM nor SSH) is only chosen explicitly or when SMB
    # is the only remote administration port found.
    local mach="${1-}"
    local method="${T_METHOD[$mach]:-}"
    local ports="${T_TPORTS[$mach]:-}"
    local has22=0 has5985=0 has445=0
    case ",$ports," in *,22,*) has22=1;; esac
    case ",$ports," in *,5985,*) has5985=1;; esac
    case ",$ports," in *,445,*) has445=1;; esac
    case "$method" in
        winrm|ssh|smb) printf '%s' "$method"; return 0;;
    esac
    if [ "$has5985" = "1" ] && [ "$has22" = "0" ]; then printf 'winrm'; return 0; fi
    if [ "$has22" = "1" ] && [ "$has5985" = "0" ]; then printf 'ssh'; return 0; fi
    if [ "$has445" = "1" ] && [ "$has22" = "0" ] && [ "$has5985" = "0" ]; then printf 'smb'; return 0; fi
    printf ''
}

port_for_transport() {
    # The port follows the transport: 22 for ssh, 5985 for winrm, 445 for smb. The web form
    # always sends --port (5985 by default), so 22 / 5985 / 445 carry no information
    # and could pick the wrong service on a machine exposing both. Only a port
    # which is neither of the two is a deliberate override (e.g. ssh on 2222).
    local mach="${1-}" transport="${2-}"
    case "${PORT-}" in
        22|5985|445|'') ;;
        *) printf '%s' "$PORT"; return 0 ;;
    esac
    case "$transport" in
        winrm) printf '5985' ;;
        smb) printf '445' ;;
        *) printf '22' ;;
    esac
}

fingerprint_os() {
    # Identify the operating system of every discovered machine.
    #
    # The SSH banner and the WinRM HTTP header name the real system ("Debian 12",
    # "Windows"), which is far more useful than guessing from the open ports. The
    # probes run in parallel: a /24 costs a couple of seconds.
    local entry ip ports payload
    local -a lines=()
    for entry in "${MACH_LIST[@]}"; do
        ip="${M_IP[$entry]:-}"
        [ -z "$ip" ] && continue
        # Real tab: a literal backslash-t would not match the Python parser.
        lines+=("$ip"$'\t'"${M_PORTS[$entry]:-}")
    done
    [ ${#lines[@]} -eq 0 ] && return 0

    if [ -n "${DEBUG-}" ]; then
        info "${GREEN}Identifying the operating system of ${#lines[@]} machine(s)"
    fi

    payload=$(printf '%s\n' "${lines[@]}" | python3 -c '
import concurrent.futures
import re
import socket
import sys


def ssh_banner(ip, timeout=2.0):
    """First line sent by an SSH server, e.g. SSH-2.0-OpenSSH_9.2p1 Debian-..."""
    try:
        with socket.create_connection((ip, 22), timeout=timeout) as sock:
            sock.settimeout(timeout)
            data = sock.recv(256)
        return data.decode("utf-8", "replace").strip()
    except OSError:
        return ""


def winrm_server(ip, timeout=2.0):
    """HTTP Server header of the WinRM listener (Windows only)."""
    try:
        with socket.create_connection((ip, 5985), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.send(b"GET /wsman HTTP/1.1\r\nHost: " + ip.encode()
                      + b"\r\nConnection: close\r\n\r\n")
            data = sock.recv(1024)
        match = re.search(rb"^Server:\s*(.+)$", data, re.M | re.I)
        return match.group(1).decode("utf-8", "replace").strip() if match else ""
    except OSError:
        return ""


def classify_ssh(banner):
    """Turn an SSH banner into an operating system name."""
    if not banner.startswith("SSH-"):
        return ""
    if "OpenSSH_for_Windows" in banner:
        return "Windows"
    match = re.search(r"deb(\d+)", banner)
    if match:
        return "Debian %s" % match.group(1)
    for name in ("Ubuntu", "CentOS", "Rocky", "AlmaLinux", "Alpine", "Fedora",
                 "Raspbian", "FreeBSD", "OpenBSD", "NetBSD"):
        if name in banner:
            return name
    match = re.search(r"(?:^|[^a-z])el(\d+)", banner)
    if match:
        return "RHEL/CentOS %s" % match.group(1)
    if "OpenSSH" in banner:
        return "Linux/Unix"
    return ""


def guess_from_ports(ports):
    """Last resort when nothing answers: only the open ports are left."""
    if 5985 in ports or 3389 in ports:
        return "Windows (assumed)"
    if 22 in ports:
        return "Linux/Unix (assumed)"
    return "Unknown"


def identify(line):
    ip, _, raw = line.partition("\t")
    if not ip:
        return None
    ports = []
    for item in raw.split(","):
        item = item.strip()
        if item.isdigit():
            ports.append(int(item))

    found = ""
    if 22 in ports:
        found = classify_ssh(ssh_banner(ip))
    if not found and 5985 in ports:
        server = winrm_server(ip)
        if "microsoft" in server.lower():
            found = "Windows"
    if not found:
        found = guess_from_ports(ports)
    return "%s\t%s" % (ip, found)


rows = [line for line in sys.stdin.read().splitlines() if line.strip()]
with concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
    for result in pool.map(identify, rows):
        if result:
            print(result)
' 2>/dev/null)

    [ -z "$payload" ] && return 0
    while IFS=$'\t' read -r ip osys; do
        [ -z "$ip" ] && continue
        for entry in "${MACH_LIST[@]}"; do
            if [ "${M_IP[$entry]:-}" = "$ip" ] && [ -z "${M_OS[$entry]:-}" ]; then
                M_OS[$entry]="$osys"
            fi
        done
    done <<< "$payload"
}

scan_services_ad() {
    # Active Directory gives the machines but not their services: scan the
    # discovered addresses for the remote control ports in a single pass.
    local targets=() entry ip ports line
    for entry in "${MACH_LIST[@]}"; do
        ip="${M_IP[$entry]:-}"
        [ -n "$ip" ] && targets+=("$ip")
    done
    [ ${#targets[@]} -eq 0 ] && return 0
    if [ -n "${DEBUG-}" ]; then
        info "${GREEN}Running nmap -p ${DISCOVER_PORTS} on ${#targets[@]} address(es)"
    fi
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        ip=$(printf '%s' "$line" | awk '{ print $2 }')
        ports=$(printf '%s' "$line" | grep -oE '[0-9]+/open' | cut -d/ -f1 | sort -n -u | paste -sd, -)
        for entry in "${MACH_LIST[@]}"; do
            if [ "${M_IP[$entry]:-}" = "$ip" ]; then
                M_PORTS[$entry]="$ports"
            fi
        done
    done < <(nmap -T4 -Pn -n --open -p "${DISCOVER_PORTS}" "${targets[@]}" -oG - 2>/dev/null | grep "/open")
}

remove_installed() {
    # Drop the machines which already declared themselves to Medulla.
    local MACH i
    local kept=()
    for i in "${!MACH_LIST[@]}"; do
        MACH="${MACH_LIST[$i]}"
        if is_installed "$MACH"; then
            M_INSTALLED[$MACH]=1
        else
            kept+=("$MACH")
        fi
    done
    MACH_LIST=("${kept[@]}")
}

mark_installed_machines() {
    # In discovery mode every machine stays in the list, we only flag it.
    local MACH
    for MACH in "${MACH_LIST[@]}"; do
        if is_installed "$MACH"; then
            M_INSTALLED[$MACH]=1
        else
            M_INSTALLED[$MACH]=0
        fi
    done
}

confirm_list() {
    echo -e "${NC}"
    echo "Are you sure you want to install Medulla agent on the following machines:"
    for MACH in "${MACH_LIST[@]}"; do
        echo "- ${MACH}"
    done
    read -p "Install Medulla agent? (y/N) " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
}

list_machines() {
    info "${GREEN}Medulla agent will be installed on the following machines:"
    for MACH in "${MACH_LIST[@]}"; do
        info "- ${MACH}"
    done
}

# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------

build_win_agent_ps() {
    # PowerShell (single line, see ps_run) that makes the target download the
    # chosen agent and run it silently, exactly like Medulla's own
    # install-agent.ps1 does. $1 = url, $2 = optional Referer header,
    # $3 = 1 to skip the certificate check (self signed HTTPS).
    # A non zero installer exit code becomes the exit code of the whole script.
    local url="${1-}"
    local referer="${2-}"
    local insecure="${3-0}"
    local tls="" skip=""
    if [ "$insecure" = "1" ]; then
        tls='[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true };'
        skip='if ((Get-Command Invoke-WebRequest).Parameters.ContainsKey("SkipCertificateCheck")) { $iwr["SkipCertificateCheck"] = $true };'
    fi
    printf '$ErrorActionPreference = "Stop"; $ProgressPreference = "SilentlyContinue"; $out = "C:\\Windows\\Temp\\medulla-setup.exe"; %s $headers = @{}; if ("%s") { $headers["Referer"] = "%s" }; $iwr = @{ Uri = "%s"; OutFile = $out; Headers = $headers; UseBasicParsing = $true }; %s Write-Output ("BPSTEP" + ":download"); Invoke-WebRequest @iwr; Write-Output ("BPSTEP" + ":install"); $proc = Start-Process -FilePath $out -ArgumentList "/S" -NoNewWindow -Wait -PassThru; if ($proc.ExitCode -ne 0) { exit $proc.ExitCode }' \
        "$tls" "$referer" "$referer" "$url" "$skip"
}

safe_url() {
    # http(s) URL without space, quote or shell metacharacter.
    case "${1-}" in
        http://*|https://*) ;;
        *) return 1 ;;
    esac
    case "${1-}" in
        *[[:space:]\'\"\\\$\`\;\&\|\<\>\(\)\{\}\*\!]*) return 1 ;;
    esac
    return 0
}

check_agent_selection() {
    # Refuse une selection d'agent inutilisable avant de lancer le moindre job.
    if [ -n "$AGENT_WIN_URL" ] && ! [[ "$AGENT_WIN_URL" =~ ^https?:// ]]; then
        json_error "Invalid agent URL: $AGENT_WIN_URL"
    fi
    # Both end up inside a command shown to the user.
    if [ -n "$AGENT_LIN_URL" ] && ! safe_url "$AGENT_LIN_URL"; then
        json_error "Invalid Linux agent URL: $AGENT_LIN_URL"
    fi
    if [ -n "$AGENT_LIN_REFERER" ] && ! safe_url "$AGENT_LIN_REFERER"; then
        json_error "Invalid Linux agent referer: $AGENT_LIN_REFERER"
    fi
    if [ "$AGENT_LIN_EXPLICIT" = "1" ] && [ ! -f "$AGENT_LIN_PATH" ]; then
        json_error "Linux agent not found: $AGENT_LIN_PATH"
    fi
}

report_failure() {
    # Keep the remote error in the job log (stderr), without the terminal noise.
    local machine="${1-}"
    local message="${2-}"
    message=$(printf '%s' "$message" | tr -d '\r' \
        | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g' \
        | tr '\n' ' ' | tr -s ' ' | cut -c1-500)
    [ -z "$message" ] && return 0
    echo -e "$machine: ${message}" >&2
}

clean_text() {
    # One line, no escape sequence, at most $2 characters (default 500).
    printf '%s' "${1-}" | tr -d '\r' \
        | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g' \
        | tr '\n' ' ' | tr -s ' ' | cut -c1-"${2-500}"
}

machine_log_path() {
    [ -z "$LOG_DIR" ] && return 1
    printf '%s/%s.log' "$LOG_DIR" "$(printf '%s' "${1-}" | tr -c 'A-Za-z0-9._-' '_' | cut -c1-120)"
}

mlog() {
    # One task of an installation: $1 machine, $2 step, $3 status
    # (start|ok|fail|info), $4 optional detail. Goes to the machine log file, to
    # the job log (stderr) and to the state file (step event).
    local mach="${1-}" step="${2-}" st="${3-}" detail
    detail=$(clean_text "${4-}" 500)
    local file
    if file=$(machine_log_path "$mach"); then
        printf '%s [%s] %s%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$step" "$st" "${detail:+ - $detail}" >> "$file"
    fi
    echo "$mach: [$step] $st${detail:+ - $detail}" >&2
    state_event "{\"event\":\"step\",\"target\":$(json_str "$mach"),\"step\":$(json_str "$step"),\"status\":$(json_str "$st"),\"detail\":$(json_str "$detail"),\"ts\":$(date +%s)}"
}

mlog_raw() {
    # Full output of a remote command, kept in the machine log only (the job log
    # shows the short version). $1 machine, $2 label, $3 output.
    local file
    file=$(machine_log_path "${1-}") || return 0
    {
        printf '%s [%s] output:\n' "$(date '+%Y-%m-%d %H:%M:%S')" "${2-}"
        printf '%s' "${3-}" | tr -d '\r' | sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g' | head -c 20000
        printf '\n'
    } >> "$file"
}

classify_failure() {
    # $1 transport, $2 step, $3 exit code, $4 output. Sets FAIL_STEP, FAIL_CODE
    # (stable identifier, translated by the web interface) and FAIL_REASON (the
    # remote message, shortened).
    local transport="${1-}" step="${2-}" rc="${3-1}" out="${4-}" low
    low=$(printf '%s' "$out" | tr '[:upper:]' '[:lower:]')
    FAIL_STEP="$step"
    FAIL_CODE="unknown"
    FAIL_REASON=$(clean_text "$out" 300)

    case "$low" in
        *"permission denied"*|*"authentication failed"*|*"too many authentication failures"*)
            FAIL_CODE="auth_failed" ;;
        *"access is denied"*|*"logon failure"*|*"user name or password is incorrect"*|*"unauthorized"*|*"authorization failed"*)
            FAIL_CODE="auth_failed" ;;
        *"could not resolve"*|*"name or service not known"*|*"no such host"*|*"nodename nor servname"*|*"cannot resolve"*)
            FAIL_CODE="dns_failed" ;;
        *"connection refused"*)
            FAIL_CODE="connection_refused" ;;
        *"no route to host"*|*"network is unreachable"*|*"connection timed out"*|*"operation timed out"*|*"connection reset"*|*"connection closed"*|*"kex_exchange_identification"*)
            FAIL_CODE="unreachable" ;;
        *"a password is required"*|*"a terminal is required"*|*"not in the sudoers"*)
            FAIL_CODE="sudo_required" ;;
        *"host key verification failed"*)
            FAIL_CODE="host_key" ;;
        *"winrm cannot process"*|*"cannot connect to"*|*"the client cannot connect"*|*"wsman"*|*"mi_result_failed"*)
            FAIL_CODE="winrm_unreachable" ;;
        *"no space left"*)
            FAIL_CODE="disk_full" ;;
    esac
    case "$low" in
        *"impacket is not installed"*)
            FAIL_CODE="smb_client_missing" ;;
        *"status_logon_failure"*|*"status_wrong_password"*|*"status_account_"*|*"status_password_"*|*"status_no_logon_servers"*|*"status_trusted_domain_failure"*)
            FAIL_CODE="auth_failed" ;;
        *"access_denied"*)
            FAIL_CODE="admin_required" ;;
        *"status_bad_network_name"*|*"status_not_supported"*|*"status_object_path_not_found"*)
            FAIL_CODE="smb_unavailable" ;;
    esac
    if [ "$FAIL_CODE" = "unknown" ]; then
        case "$step" in
            download) FAIL_CODE="download_failed" ;;
            install)  FAIL_CODE="installer_failed" ;;
            transfer) FAIL_CODE="transfer_failed" ;;
            connect)  FAIL_CODE="unreachable" ;;
        esac
    fi
    # What the target could not fetch is a download problem whatever the message.
    if [ "$step" = "download" ]; then
        FAIL_CODE="download_failed"
    fi
    if [ "$rc" = "124" ] || [ "$rc" = "143" ]; then
        FAIL_CODE="timeout"
        [ -z "$FAIL_REASON" ] && FAIL_REASON="Timed out after ${INSTALL_TIMEOUT:-?}s"
    fi
    if [ -z "$FAIL_REASON" ]; then
        FAIL_REASON="Exit code $rc"
    fi
}

install_info() {
    # Result details of this machine for install_sweep (read through the file
    # named by BP_INFO_FILE). Written once, as JSON members without braces.
    [ -z "${BP_INFO_FILE-}" ] && return 0
    printf '%s' "${1-}" > "$BP_INFO_FILE"
}

inst_ok() {
    # $1 machine, $2 transport, $3 system (windows|linux|macos|"")
    mlog "$1" done ok "installed over ${2}"
    install_info "\"transport\":$(json_str "$2"),\"system\":$(json_str "${3-}"),\"step\":\"done\",\"code\":\"ok\",\"reason\":\"\""
    echo -e "${GREEN}$1: Execution successful"
    return 0
}

manual_install_command() {
    # One line to type on a Linux machine we could not reach over SSH. $1 =
    # transport, $2 = system ("" when unknown yet), $3 = failure code.
    [ "${1-}" = "ssh" ] && [ -n "$AGENT_LIN_URL" ] || return 0
    case "${2-}" in ""|linux) ;; *) return 0;; esac
    case "${3-}" in
        auth_failed|connection_refused|unreachable|host_key|sudo_required|timeout) ;;
        *) return 0;;
    esac
    if [ -n "$AGENT_LIN_REFERER" ]; then
        printf "curl -fsSk -e '%s' '%s' | sudo bash" "$AGENT_LIN_REFERER" "$AGENT_LIN_URL"
    else
        printf "curl -fsSk '%s' | sudo bash" "$AGENT_LIN_URL"
    fi
}

inst_fail() {
    # $1 machine, $2 transport, $3 system, $4 step, $5 rc, $6 output
    local mach="${1-}" rc="${5-1}" manual
    classify_failure "$2" "$4" "$rc" "${6-}"
    mlog_raw "$mach" "$4" "${6-}"
    mlog "$mach" "$FAIL_STEP" fail "${FAIL_CODE}: ${FAIL_REASON}"
    manual=$(manual_install_command "$2" "${3-}" "$FAIL_CODE")
    [ -n "$manual" ] && mlog_raw "$mach" "manual installation, to type on the machine" "$manual"
    install_info "\"transport\":$(json_str "$2"),\"system\":$(json_str "${3-}"),\"step\":$(json_str "$FAIL_STEP"),\"code\":$(json_str "$FAIL_CODE"),\"reason\":$(json_str "$FAIL_REASON")${manual:+,\"manual\":$(json_str "$manual")}"
    echo -e "${RED}$mach: Execution failed"
    [ "$rc" = "0" ] && rc=1
    return "$rc"
}

last_marker() {
    # Last "BPSTEP:<name>" printed by the remote PowerShell (empty when none).
    printf '%s' "${1-}" | tr -d '\r' | grep -o 'BPSTEP:[a-z]*' | tail -1 | cut -d: -f2
}

log_markers() {
    # Replays the remote PowerShell tasks as completed ones, up to the marker
    # reached ($2). $3 = "before": stop before it (the marker is the task that
    # failed).
    local mach="${1-}" upto="${2-}" mode="${3-}" step
    for step in download install; do
        if [ "$step" = "$upto" ] && [ "$mode" = "before" ]; then break; fi
        mlog "$mach" "$step" ok ""
        [ "$step" = "$upto" ] && break
    done
}

timed() {
    # Applies the installation timeout when one is requested.
    if [ -n "$INSTALL_TIMEOUT" ]; then
        timeout --foreground --signal=TERM "$INSTALL_TIMEOUT" "$@"
    else
        "$@"
    fi
}

mac_pick_package() {
    # $1 = value of `uname -m` on the machine. Prints the newest .pkg of that
    # architecture found in AGENT_MAC_DIR, nothing when there is none.
    local arch="${1-}" aliases pat f
    case "$arch" in
        arm64|aarch64) aliases="arm64 aarch64" ;;
        x86_64|amd64)  aliases="x86_64 x64 amd64 intel" ;;
        *)             aliases="$arch" ;;
    esac
    [ -d "$AGENT_MAC_DIR" ] || return 1
    for pat in $aliases; do
        f=$(ls -t "$AGENT_MAC_DIR"/Medulla-Agent-mac-"$pat"-*.pkg "$AGENT_MAC_DIR"/Medulla-Agent-mac-"$pat".pkg 2>/dev/null | head -1)
        [ -n "$f" ] && { printf '%s' "$f"; return 0; }
    done
    return 1
}

install_agent_ssh_mac() {
    # macOS over SSH: the .pkg of the right architecture is copied to a private
    # temporary directory, installed with installer(8), then removed. A non root
    # account needs a passwordless sudo (the password is never sent).
    local mach="${1-}" arch pkg out rc dir
    shift
    local -a SSH_ARGS=("$@")
    arch=$(ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$mach" 'uname -m' < /dev/null 2>/dev/null | tr -d '\r' | head -1)
    mlog "$mach" prepare start "architecture ${arch:-unknown}"
    if [ -z "$arch" ]; then
        inst_fail "$mach" ssh macos prepare 1 "Cannot read the architecture (uname -m)"
        return $?
    fi
    pkg=$(mac_pick_package "$arch")
    if [ -z "$pkg" ]; then
        mlog_raw "$mach" prepare "No macOS agent package for ${arch} in ${AGENT_MAC_DIR}"
        mlog "$mach" prepare fail "no_package: no macOS agent package for ${arch} in ${AGENT_MAC_DIR}"
        install_info "\"transport\":\"ssh\",\"system\":\"macos\",\"step\":\"prepare\",\"code\":\"no_package\",\"reason\":$(json_str "No macOS agent package for ${arch} in ${AGENT_MAC_DIR}")"
        echo -e "${RED}$mach: Execution failed"
        return 1
    fi
    mlog "$mach" prepare ok "package $(basename "$pkg")"

    mlog "$mach" transfer start "$(basename "$pkg")"
    out=$(timed ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$mach" 'd=$(mktemp -d /tmp/medulla-agent.XXXXXX) && cat > "$d/agent.pkg" && echo "$d"' < "$pkg" 2>&1)
    rc=$?
    dir=$(printf '%s' "$out" | tr -d '\r' | tail -1)
    if [ "$rc" != "0" ] || ! [[ "$dir" =~ ^/[A-Za-z0-9._/-]+$ ]]; then
        [ "$rc" = "0" ] && rc=1
        inst_fail "$mach" ssh macos transfer "$rc" "$out"
        return $?
    fi
    mlog "$mach" transfer ok "copied to ${dir}"

    mlog "$mach" install start "installer -pkg"
    out=$(timed ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$mach" "d='${dir}'; if [ \"\$(id -u)\" = 0 ]; then /usr/sbin/installer -pkg \"\$d/agent.pkg\" -target /; else sudo -n /usr/sbin/installer -pkg \"\$d/agent.pkg\" -target /; fi; rc=\$?; rm -rf \"\$d\"; exit \$rc" < /dev/null 2>&1)
    rc=$?
    if [ "$rc" != "0" ]; then
        inst_fail "$mach" ssh macos install "$rc" "$out"
        return $?
    fi
    mlog_raw "$mach" install "$out"
    mlog "$mach" install ok ""
    inst_ok "$mach" ssh macos
}

smb_fallback_possible() {
    # WinRM did not answer: the machine can still be reached over SMB when its
    # port 445 was seen open and the helper (with impacket) is installed.
    local ports="${T_TPORTS[${1-}]:-}"
    case ",$ports," in *,445,*) ;; *) return 1;; esac
    [ -f "$SMB_HELPER" ] && command -v python3 >/dev/null 2>&1
}

install_agent_smb() {
    # Windows over SMB (445) without WinRM: $1 = machine, $2 = port. The helper
    # copies the PowerShell script to C$ and runs it through a one shot service
    # (needs administrator rights). Credentials travel in the environment only.
    local MACH="${1-}" port="${2-445}" PS out rc marker step
    if [ ! -f "$SMB_HELPER" ]; then
        inst_fail "$MACH" smb windows connect 1 "smb: impacket is not installed (helper $SMB_HELPER not found)"
        return $?
    fi
    if [ -n "$AGENT_WIN_URL" ]; then
        PS=$(build_win_agent_ps "$AGENT_WIN_URL" "$AGENT_WIN_REFERER" "$AGENT_WIN_INSECURE")
    else
        PS=$(cat /var/lib/pulse2/clients/win/install-agent.ps1)
    fi
    if [ ! -z ${DEBUG-} ]; then
        echo -e "$MACH: Running $SMB_HELPER --port $port (script run through the admin share)"
    fi
    mlog "$MACH" connect start "smb ${USERNAME-?}@${MACH}:${port}"
    out=$(BP_USERNAME="${USERNAME-}" BP_PASSWORD="${PASSWORD-}" BP_DOMAIN="${DOMAIN-}" BP_TARGET="$MACH" \
        python3 "$SMB_HELPER" --port "$port" ${INSTALL_TIMEOUT:+--timeout "$INSTALL_TIMEOUT"} <<<"$PS" 2>&1)
    rc=$?
    marker=$(last_marker "$out")
    if [ "$rc" != "0" ]; then
        case "$out" in
            *"smb: connect failed"*|*"impacket is not installed"*) step=connect ;;
            *"smb: transfer failed"*|*"smb: input failed"*) step=transfer ;;
            *"smb: start failed"*|*"smb: wait failed"*) step=install ;;
            *) step="${marker:-install}" ;;
        esac
        case "$step" in
            transfer|install|download) mlog "$MACH" connect ok "" ;;
        esac
        if [ "$step" != "connect" ] && [ -n "$marker" ]; then
            log_markers "$MACH" "$marker" before
        fi
        inst_fail "$MACH" smb windows "$step" "$rc" "$out"
        return $?
    fi
    mlog "$MACH" connect ok ""
    mlog_raw "$MACH" install "$out"
    [ -n "$marker" ] && log_markers "$MACH" "$marker"
    inst_ok "$MACH" smb windows
    return $?
}

install_agent() {
    # Install agent on machine: $1 = machine name or ip
    local MACH="${1-}"
    local CMD RESULT=1
    local TRANSPORT MACH_PORT
    local logfile
    if logfile=$(machine_log_path "$MACH"); then
        : > "$logfile"
    fi
    TRANSPORT=$(choose_transport "$MACH")
    if [ -z "$TRANSPORT" ]; then
        # Nothing is known about this machine: probe the target as before.
        if [[ $(timeout 1 bash -c cat < /dev/tcp/$1/${PORT}) == *"SSH"* || ! -z ${SSHKEY-} ]]; then
            TRANSPORT=ssh
        else
            TRANSPORT=winrm
        fi
    fi
    MACH_PORT=$(port_for_transport "$MACH" "$TRANSPORT")
    echo -e "${GREEN}$1: Processing"
    mlog "$MACH" transport ok "${TRANSPORT} on port ${MACH_PORT}, user ${USERNAME-?}"
    if [ -n "${DEBUG-}" ]; then
        echo -e "$1: transport ${TRANSPORT} on port ${MACH_PORT}"
    fi
    if [ "$TRANSPORT" = "smb" ]; then
        install_agent_smb "$MACH" "$MACH_PORT"
        return $?
    elif [ "$TRANSPORT" = "ssh" ]; then
        # Using SSH
        # One options array, every value quoted: nothing coming from the form can
        # turn into an ssh option ("--" ends the options before user@host).
        # Host keys are deliberately not checked (the machines of a fleet are
        # unknown to this server): that policy is unchanged.
        local -a SSH_ARGS=(-p "$MACH_PORT" -oBatchMode=yes -oConnectTimeout=10 -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null)
        if [ -n "${SSHKEY-}" ]; then
            SSH_ARGS+=(-i "$SSHKEY")
        fi
        local out osname="" system=""
        mlog "$MACH" connect start "ssh ${USERNAME}@${MACH}:${MACH_PORT}"
        out=$(ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$1" 'exit 0' < /dev/null 2>&1)
        RESULT=$?
        if [ "$RESULT" != "0" ]; then
            inst_fail "$MACH" ssh "" connect "$RESULT" "$out"
            return $?
        fi
        mlog "$MACH" connect ok ""

        # Operating system: uname answers on Linux and macOS, not on Windows.
        mlog "$MACH" detect start ""
        osname=$(ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$1" 'uname -s' < /dev/null 2>/dev/null | tr -d '\r' | head -1)
        case "$osname" in
            Darwin) system="macos" ;;
            "")
                if ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$1" 'wmic os get version /value' < /dev/null &> /dev/null \
                    || ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$1" 'ver' < /dev/null 2>/dev/null | grep -qi windows; then
                    system="windows"
                else
                    inst_fail "$MACH" ssh "" detect 1 "Cannot identify the operating system (uname, wmic and ver all failed)"
                    return $?
                fi
                ;;
            *) system="linux" ;;
        esac
        mlog "$MACH" detect ok "$system"

        if [ "$system" = "macos" ]; then
            install_agent_ssh_mac "$MACH" "${SSH_ARGS[@]}"
            return $?
        elif [ "$system" = "windows" ]; then
            # Windows machine
            if [ -n "$AGENT_WIN_URL" ]; then
                # Chosen agent: the target downloads it and runs it silently.
                local PS_INSTALL
                PS_INSTALL=$(build_win_agent_ps "$AGENT_WIN_URL" "$AGENT_WIN_REFERER" "$AGENT_WIN_INSECURE")
            else
                PS_INSTALL=$(cat /var/lib/pulse2/clients/win/install-agent.ps1)
            fi
            if [ ! -z ${DEBUG-} ]; then
                echo -e "$1: Running ssh ${SSH_ARGS[*]} -- ${USERNAME}@$1 'PowerShell.exe -noprofile -' <<< <agent>"
            fi
            mlog "$MACH" install start "PowerShell over ssh"
            local ssh_out
            ssh_out=$(timed ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$1" 'PowerShell.exe -noprofile -' <<<"$PS_INSTALL" 2>&1)
            RESULT=$?
            local marker
            marker=$(last_marker "$ssh_out")
            if [ "$RESULT" != "0" ]; then
                [ -n "$marker" ] && log_markers "$MACH" "$marker" before
                inst_fail "$MACH" ssh windows "${marker:-install}" "$RESULT" "$ssh_out"
                return $?
            fi
            mlog_raw "$MACH" install "$ssh_out"
            [ -n "$marker" ] && log_markers "$MACH" "$marker"
            inst_ok "$MACH" ssh windows
            return $?
        else
            # Linux machine
            if [ ! -f "$AGENT_LIN_PATH" ]; then
                inst_fail "$MACH" ssh linux prepare 1 "Linux agent not found: $AGENT_LIN_PATH"
                return $?
            fi
            if [ ! -z ${DEBUG-} ]; then
                echo -e "$1: Running bash -s < $AGENT_LIN_PATH"
            fi
            mlog "$MACH" install start "bash -s < $(basename "$AGENT_LIN_PATH")"
            local ssh_out
            ssh_out=$(timed ssh "${SSH_ARGS[@]}" -- "${USERNAME}@$1" 'bash -s' < "$AGENT_LIN_PATH" 2>&1)
            RESULT=$?
            if [ "$RESULT" != "0" ]; then
                inst_fail "$MACH" ssh linux install "$RESULT" "$ssh_out"
                return $?
            fi
            mlog_raw "$MACH" install "$ssh_out"
            inst_ok "$MACH" ssh linux
            return $?
        fi
    else
        # Using WINRM
        local PS
        if [ -n "$AGENT_WIN_URL" ]; then
            # Chosen agent: the scriptblock runs on the target, which downloads
            # the agent and installs it silently. The URL and the optional
            # Referer are passed as arguments (the remote has no BP_* env).
            # The BPSTEP markers tell which task was reached when it fails.
            PS='$ErrorActionPreference = "Stop";
$pw = ConvertTo-SecureString -AsPlainText -Force -String $env:BP_PASSWORD;
$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $env:BP_USERNAME,$pw;
Invoke-Command -ComputerName $env:BP_TARGET -Port $env:BP_PORT -Authentication Negotiate -Credential $cred -ScriptBlock {
    param($url, $referer, $insecure);
    $ProgressPreference = "SilentlyContinue";
    if ($insecure -eq "1") { [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true } };
    $out = "C:\Windows\Temp\medulla-setup.exe";
    $headers = @{};
    if ($referer) { $headers["Referer"] = $referer };
    $iwr = @{ Uri = $url; OutFile = $out; Headers = $headers; UseBasicParsing = $true };
    if ($insecure -eq "1") { if ((Get-Command Invoke-WebRequest).Parameters.ContainsKey("SkipCertificateCheck")) { $iwr["SkipCertificateCheck"] = $true } };
    Write-Output ("BPSTEP" + ":download");
    Invoke-WebRequest @iwr;
    Write-Output ("BPSTEP" + ":install");
    $proc = Start-Process -FilePath $out -ArgumentList "/S" -NoNewWindow -Wait -PassThru;
    if ($proc.ExitCode -ne 0) { throw ("Installer exit code " + $proc.ExitCode) }
} -ArgumentList $env:BP_AGENT_URL, $env:BP_AGENT_REFERER, $env:BP_AGENT_INSECURE'
        else
            PS='$ErrorActionPreference = "Stop";
$pw = ConvertTo-SecureString -AsPlainText -Force -String $env:BP_PASSWORD;
$cred = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $env:BP_USERNAME,$pw;
Invoke-Command -ComputerName $env:BP_TARGET -Port $env:BP_PORT -Authentication Negotiate -Credential $cred -FilePath /var/lib/pulse2/clients/win/install-agent.ps1'
        fi
        if [ ! -z ${DEBUG-} ]; then
            if [ -n "$AGENT_WIN_URL" ]; then
                echo -e "$1: Running Invoke-Command (download $AGENT_WIN_URL then /S)"
            else
                echo -e "$1: Running Invoke-Command -ComputerName $1 -Port ${PORT} -FilePath /var/lib/pulse2/clients/win/install-agent.ps1"
            fi
        fi
        mlog "$MACH" connect start "winrm ${USERNAME-?}@${MACH}:${MACH_PORT}"
        local win_out marker step
        win_out=$(ps_run "$MACH" with-timeout "$MACH_PORT" <<<"$PS" 2>&1)
        RESULT=$?
        marker=$(last_marker "$win_out")
        if [ "$RESULT" != "0" ]; then
            # No marker: the failure happened before the remote script ran
            # (connection, authentication) or the script has no marker.
            if [ -z "$marker" ] && smb_fallback_possible "$MACH"; then
                classify_failure winrm connect "$RESULT" "$win_out"
                case "$FAIL_CODE" in
                    winrm_unreachable|connection_refused|unreachable)
                        mlog_raw "$MACH" connect "$win_out"
                        mlog "$MACH" connect fail "winrm: ${FAIL_CODE}, trying smb on port 445"
                        install_agent_smb "$MACH" 445
                        return $?
                        ;;
                esac
            fi
            step="$marker"
            if [ -z "$step" ]; then
                if [ -n "$AGENT_WIN_URL" ]; then step="connect"; else step="install"; fi
            fi
            if [ "$step" != "connect" ] && [ -n "$marker" ]; then
                mlog "$MACH" connect ok ""
                log_markers "$MACH" "$marker" before
            fi
            inst_fail "$MACH" winrm windows "$step" "$RESULT" "$win_out"
            return $?
        fi
        mlog "$MACH" connect ok ""
        mlog_raw "$MACH" install "$win_out"
        [ -n "$marker" ] && log_markers "$MACH" "$marker"
        inst_ok "$MACH" winrm windows
        return $?
    fi
}

install_sweep() {
    # Record (once) every installation whose result is available. $1 = 1 when
    # every child is over: a missing result file then means a crashed job.
    # Not standalone: it works on the variables of install_all (dynamic scope).
    local final="${1-0}" j rc status
    for j in "${!targets[@]}"; do
        [ -n "${collected[$j]:-}" ] && continue
        rc=""
        if [ -s "$RCDIR/$j.rc" ]; then
            rc=$(cat "$RCDIR/$j.rc")
        elif [ "$final" = "1" ]; then
            rc=1
        else
            continue
        fi
        collected[$j]=1
        done_count=$((done_count + 1))
        if [ "$rc" = "0" ]; then
            ok_count=$((ok_count + 1))
            status="ok"
        else
            ko_count=$((ko_count + 1))
            status="ko"
        fi
        local info=""
        [ -s "$RCDIR/$j.info" ] && info=$(cat "$RCDIR/$j.info")
        if [ -z "$info" ] && [ "$rc" != "0" ]; then
            info="\"step\":\"unknown\",\"code\":\"crashed\",\"reason\":\"The installation ended without reporting a result (exit code ${rc})\""
        fi
        RESULTS[$j]="{\"target\":$(json_str "${targets[$j]}"),\"name\":$(json_str "${M_NAME[${targets[$j]}]:-${targets[$j]}}"),\"status\":\"${status}\"${info:+,$info}}"
        state_event "{\"event\":\"progress\",\"done\":${done_count},\"total\":${total},\"target\":$(json_str "${targets[$j]}"),\"ok\":$(json_bool "$([ "$rc" = "0" ] && echo 1 || echo 0)")}"
    done
}

install_cancel() {
    # TERM / INT received while installing: stop the jobs we started, remove the
    # temporary directory and tell the web interface. Not standalone: it uses the
    # variables of install_all (dynamic scope).
    local code="${1-143}" p
    trap '' TERM INT
    for p in "${pids[@]}"; do
        # The job subshell first (its children are reparented once it is gone).
        if command -v pkill >/dev/null 2>&1; then pkill -TERM -P "$p" 2>/dev/null; fi
        kill -TERM "$p" 2>/dev/null
    done
    rm -rf "$RCDIR"
    state_event "{\"event\":\"end\",\"status\":\"cancelled\",\"ok\":${ok_count},\"ko\":${ko_count},\"total\":${total}}"
    exit "$code"
}

install_all() {
    # Launch the installations in parallel (bounded pool) and aggregate the
    # results.
    local MACH i
    local total=${#MACH_LIST[@]}
    local done_count=0 ok_count=0 ko_count=0
    local -a pids=() targets=() collected=()
    local -a RESULTS=()
    local RCDIR
    RCDIR=$(mktemp -d /tmp/bp-install.XXXXXX)
    local quiet=""
    [ "$JSON_MODE" = "1" ] && quiet="1"

    # At most BP_MAX_PARALLEL installations at a time (1..64, default 16): one
    # job per machine for a whole subnet would exhaust processes and memory (a
    # pwsh per WinRM job).
    local max_par="${BP_MAX_PARALLEL:-16}"
    if ! [[ "$max_par" =~ ^[0-9]{1,3}$ ]] || [ "$((10#$max_par))" -lt 1 ] || [ "$((10#$max_par))" -gt 64 ]; then
        max_par=16
    fi
    max_par=$((10#$max_par))
    local have_wait_n=0
    # "wait -n" needs bash >= 4.3, otherwise the oldest job is awaited.
    if (( BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 3) )); then
        have_wait_n=1
    fi
    local running=0 oldest=0

    trap 'install_cancel 143' TERM
    trap 'install_cancel 130' INT

    state_event "{\"event\":\"start\",\"mode\":\"install\",\"total\":${total},\"ts\":$(date +%s)}"

    for MACH in "${MACH_LIST[@]}"; do
        if [ "$running" -ge "$max_par" ]; then
            if [ "$have_wait_n" = "1" ]; then
                wait -n 2>/dev/null
            else
                wait "${pids[$oldest]}" 2>/dev/null
                oldest=$((oldest + 1))
            fi
            running=$((running - 1))
            install_sweep 0
        fi
        targets+=("$MACH")
        if [ "$quiet" = "1" ]; then
            # stdout is dropped, stderr is kept: the failure reason must reach
            # the job log shown in the web interface.
            ( BP_INFO_FILE="$RCDIR/$(( ${#targets[@]} - 1 )).info" install_agent "$MACH" >/dev/null; echo "$?" > "$RCDIR/$(( ${#targets[@]} - 1 )).rc" ) &
        else
            ( BP_INFO_FILE="$RCDIR/$(( ${#targets[@]} - 1 )).info" install_agent "$MACH"; echo "$?" > "$RCDIR/$(( ${#targets[@]} - 1 )).rc" ) &
        fi
        pids+=($!)
        running=$((running + 1))
    done

    # Every job is launched: wait for the remaining ones, collecting the
    # results as they come in.
    while [ "$running" -gt 0 ]; do
        if [ "$have_wait_n" = "1" ]; then
            wait -n 2>/dev/null
        else
            wait "${pids[$oldest]}" 2>/dev/null
            oldest=$((oldest + 1))
        fi
        running=$((running - 1))
        install_sweep 0
    done
    install_sweep 1
    trap - TERM INT
    rm -rf "$RCDIR"

    local joined="" r
    for i in "${!targets[@]}"; do
        r="${RESULTS[$i]}"
        [ -n "$joined" ] && joined="$joined,"
        joined="$joined$r"
    done

    state_event "{\"event\":\"end\",\"status\":\"ok\",\"ok\":${ok_count},\"ko\":${ko_count},\"total\":${total},\"results\":[${joined}]}"

    if [ "$JSON_MODE" = "1" ]; then
        printf '{"status":"ok","mode":"install","total":%d,"ok":%d,"ko":%d,"results":[%s]}\n' \
            "$total" "$ok_count" "$ko_count" "$joined"
    fi
    [ "$ko_count" -gt 0 ] && return 1
    return 0
}

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

emit_discovery_json() {
    local MACH first=1
    printf '{"status":"ok","mode":"discover","total":%d,"machines":[' "${#MACH_LIST[@]}"
    state_event "{\"event\":\"start\",\"mode\":\"discover\",\"total\":${#MACH_LIST[@]},\"ts\":$(date +%s)}"
    for MACH in "${MACH_LIST[@]}"; do
        if [ "$first" = "0" ]; then printf ','; fi
        first=0
        printf '%s' "$(machine_json "$MACH")"
        state_event "{\"event\":\"machine\",\"machine\":$(machine_json "$MACH")}"
    done
    printf ']}\n'
    state_event "{\"event\":\"end\",\"status\":\"ok\",\"total\":${#MACH_LIST[@]}}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

check_arguments "$@"

if [ -n "$STATE_FILE" ]; then
    mkdir -p "$(dirname "$STATE_FILE")" 2>/dev/null
    # Truncate any previous run, then keep the descriptor open for the events.
    : > "$STATE_FILE"
    exec {STATE_FD}>>"$STATE_FILE"
    LOG_DIR="$(dirname "$STATE_FILE")/logs"
    mkdir -p "$LOG_DIR" 2>/dev/null && chmod 700 "$LOG_DIR" 2>/dev/null || LOG_DIR=""
fi

if [ "$PS_SETUP" = "1" ]; then
    run_ps_setup
fi

if [ "$UUID_LOOKUP" = "1" ]; then
    uuid_lookup
fi

if [ "$CHECK_PREREQ" = "1" ]; then
    check_prerequisites
fi

# PowerShell (and its WSMan client) is only demanded when a WinRM or Active
# Directory path is really used: listing / discovering through AD, or installing
# without an SSH key. A network discovery (nmap) or an SSH only installation
# works without it.
NEED_PWSH=0
NEED_PWSH_WHY=""
if [ "$LIST_OUS" = "1" ] || [ -n "${SERVER-}" ]; then
    NEED_PWSH=1
    NEED_PWSH_WHY="listing the Active Directory objects"
elif [ "$DISCOVER_MODE" != "1" ] && [ -z "${SSHKEY-}" ] && [ "${PORT}" != "22" ]; then
    NEED_PWSH=1
    NEED_PWSH_WHY="installing the agent through WinRM"
fi

if [ "$NEED_PWSH" = "1" ]; then
    if [ "$SKIP_PS_SETUP" = "1" ]; then
        check_ps_available
    else
        check_ps_setup
    fi
    # The WSMan client library is mandatory for every remote Powershell operation.
    require_wsman "$NEED_PWSH_WHY"
fi

if [ "$LIST_OUS" = "1" ]; then
    if [ -z "${SERVER-}" ]; then
        json_error "--list-ous requires --server=<ad_server_name>"
    fi
    list_ad_ous
fi

# Announce the discovery right away: the scan itself can take a while and the
# web interface only knows the job mode from this event (the total is updated by
# the final one).
if [ "$DISCOVER_MODE" = "1" ]; then
    state_event "{\"event\":\"start\",\"mode\":\"discover\",\"total\":0,\"ts\":$(date +%s)}"
fi

if [[ "${FQDN-}" == 1 ]]; then
    add_single_target "${TARGET}"
elif [[ "${TARGET-}" == */32 ]]; then
    add_single_target "${TARGET:0:-3}"
elif [ -z "$TARGETS_ARG" ]; then
    if [ -z ${SERVER+x} ]; then
        get_machines_list_nmap
    else
        get_machines_list_ad
    fi
fi

# Services and operating system of the discovered machines. Installations skip
# this: they already know the port they use and must stay fast.
if [ "$DISCOVER_MODE" = "1" ]; then
    scan_explicit_services
    fingerprint_os
fi

mark_installed_machines

if [ "$DISCOVER_MODE" = "1" ]; then
    if [ ${#MACH_LIST[@]} -eq 0 ]; then
        if [ "$JSON_MODE" = "1" ]; then
            printf '{"status":"ok","mode":"discover","total":0,"machines":[]}\n'
            state_event "{\"event\":\"end\",\"status\":\"ok\",\"total\":0}"
        else
            echo -e "${NC}No machines found"
        fi
        exit 0
    fi
    if [ "$JSON_MODE" = "1" ]; then
        emit_discovery_json
    else
        list_machines
    fi
    exit 0
fi

# Agent selection is only meaningful when we are about to install something.
check_agent_selection

if [ -z ${REINSTALL+x} ]; then
    remove_installed
fi
if [ ${#MACH_LIST[@]} -eq 0 ]; then
    if [ "$JSON_MODE" = "1" ]; then
        printf '{"status":"ok","mode":"install","total":0,"ok":0,"ko":0,"results":[],"message":"No machines to install Medulla Agent on"}\n'
        state_event "{\"event\":\"end\",\"status\":\"ok\",\"total\":0}"
    else
        echo -e "${NC}No machines to install Medulla Agent on"
    fi
    exit 0
else
    if [ -z ${FORCE+x} ] && [ "$NONINTERACTIVE" != "1" ]; then
        confirm_list
    else
        list_machines
    fi
    install_all
    exit $?
fi
