#!/bin/bash
# (c) 2026 Medulla, http://www.medulla-tech.io
#
# This file is part of MMC, http://www.medulla-tech.io
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; If not, see <http://www.gnu.org/licenses/>.

# file : /usr/sbin/update_medulla.sh

DISCLAIMER="""

############################################################################

AVERTISSEMENT : SAUVEGARDE REQUISE AVANT MISE À JOUR

Avant d'exécuter ce script de mise à jour, il vous appartient de :

✓ Créer une sauvegarde complète de vos données
✓ Effectuer un snapshot du système (si applicable)
✓ Sauvegarder les fichiers de configuration
✓ Vérifier que vous disposez d'un point de restauration fonctionnel

- Cette mise à jour modifiera le système de manière irréversible
- En cas d'échec, une restauration sera nécessaire
- Aucun retour en arrière automatique n'est disponible

############################################################################

"""

DL_URL=https://dl.medulla-tech.io/up/update_medulla.sh
DBHOST=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbhost 2> /dev/null || echo localhost)
DBPORT=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbport 2> /dev/null || echo 3306)
DBUSER=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbuser 2> /dev/null || echo mmc)
DBPASS=$(crudini --get /etc/mmc/plugins/xmppmaster.ini.local database dbpasswd)

IP_ADDRESS=$(hostname -I | awk '{print $1}')
INTERNAL_FQDN=$(hostname -f)
PUBLIC_IP=$(crudini --get /etc/pulse-xmpp-agent/relayconf.ini.local connection server 2> /dev/null || echo "" )
if [[ "${PUBLIC_IP}" == "${IP_ADDRESS}" ]]; then
    PUBLIC_IP=""
fi

accept_disclaimer() {
    echo "${DISCLAIMER}"
    read -p "Acceptez-vous ces termes? (y/n) "
    if [[ $REPLY != "y" && $REPLY != "Y" && $REPLY != "o" && $REPLY != "O" ]]; then
        echo "Aborting."
        exit 1
    fi
    touch /var/lib/mmc/.accepted_medulla_update_disclaimer
}

write_to_log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> /var/log/medulla_update.log
}

download_migration_script_and_restart() {
    # echo and write to log that we are downloading the migration script
    str="Checking for migration script updates..."
    echo "$str"
    write_to_log "$str"
    # check if md5sum of the current script matches the one on the server
    if [[ -f $0 ]]; then
        LOCAL_MD5=$(md5sum $0 | awk '{print $1}')
        REMOTE_MD5=$(curl -fsSL ${DL_URL}.md5)
        if [[ "${LOCAL_MD5}" == "${REMOTE_MD5}" ]]; then
            str="[v] Migration script is up to date. No download needed."
            echo "$str"
            write_to_log "$str"
            return
        fi
    fi
    curl -fsSL ${DL_URL} -o /tmp/update_medulla.sh
    # Check if download was successful
    if [[ $? -ne 0 ]]; then
        str="[x] Error downloading migration script. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    str="[v] Migration script downloaded successfully."
    echo "$str"
    write_to_log "$str"
    chmod +x /tmp/update_medulla.sh
    str="Restarting migration script with the latest version..."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

# --- Common functions for Medulla updates ---

setup_new_mmc_module() {
    module_name="$1"
    str="[=] Setting up new MMC module: $module_name"
    echo "$str"
    write_to_log "$str"
    # Make sure the module is installed
    apt -y install mmc-web-${module_name} python3-mmc-${module_name} &> /dev/null
    if [[ $? -ne 0 ]]; then
        str="[x] Error installing MMC module $module_name. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    # Copy /etc/mmc/plugins/kiosk.ini.local to /etc/mmc/plugins/<module_name>.ini.local if it does not exist
    if [[ ! -f /etc/mmc/plugins/${module_name}.ini.local ]]; then
        cp /etc/mmc/plugins/kiosk.ini.local /etc/mmc/plugins/${module_name}.ini.local
    fi
    # Create database for the module
    mysql --defaults-group-suffix=dbsetup -e "CREATE DATABASE IF NOT EXISTS ${module_name} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
    if [[ $? -ne 0 ]]; then
        str="[x] Error creating database for MMC module $module_name. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    # Import initial schema if version table does not exist in the database
    TABLE_EXISTS=$(mysql --defaults-group-suffix=dbsetup -sse "USE ${module_name}; SHOW TABLES LIKE 'version';")
    if [[ -z "${TABLE_EXISTS}" ]]; then
        mysql --defaults-group-suffix=dbsetup ${module_name} < /usr/share/doc/pulse2/contrib/${module_name}/sql/schema-001.sql
        if [[ $? -ne 0 ]]; then
            str="[x] Error importing database schema for MMC module $module_name. Aborting."
            echo "$str"
            write_to_log "$str"
            exit 1
        fi
    fi
    # Create db user and grant privileges
    mysql --defaults-group-suffix=dbsetup -e "GRANT ALL PRIVILEGES ON ${module_name}.* TO '${DBUSER}'@'localhost' IDENTIFIED BY '${DBPASS}'; FLUSH PRIVILEGES;"
    mysql --defaults-group-suffix=dbsetup -e "GRANT ALL PRIVILEGES ON ${module_name}.* TO '${DBUSER}'@'pulse' IDENTIFIED BY '${DBPASS}'; FLUSH PRIVILEGES;"
    if [[ "${DBHOST}" != "localhost" ]]; then
        mysql --defaults-group-suffix=dbsetup -e "GRANT ALL PRIVILEGES ON ${module_name}.* TO '${DBUSER}'@'${DBHOST}' IDENTIFIED BY '${DBPASS}'; FLUSH PRIVILEGES;"
    fi
    mysql --defaults-group-suffix=dbsetup -e "GRANT ALL PRIVILEGES ON ${module_name}.* TO '${DBUSER}'@'${IP_ADDRESS}' IDENTIFIED BY '${DBPASS}'; FLUSH PRIVILEGES;"
    mysql --defaults-group-suffix=dbsetup -e "GRANT ALL PRIVILEGES ON ${module_name}.* TO '${DBUSER}'@'${INTERNAL_FQDN}' IDENTIFIED BY '${DBPASS}'; FLUSH PRIVILEGES;"
    if [[ -n "${PUBLIC_IP}" ]]; then
        mysql --defaults-group-suffix=dbsetup -e "GRANT ALL PRIVILEGES ON ${module_name}.* TO '${DBUSER}'@'${PUBLIC_IP}' IDENTIFIED BY '${DBPASS}'; FLUSH PRIVILEGES;"
    fi
    # mmc-agent will be restarted in final_operations
    str="[v] MMC module $module_name setup completed successfully."
    echo "$str"
    write_to_log "$str"
}

check_medulla_version() {
    # Get current version from /var/lib/mmc/version
    CURRENT_VERSION=$(cat /var/lib/mmc/version 2> /dev/null)
    # If current version is empty, get the information from installed packages
    if [[ -z "${CURRENT_VERSION}" ]]; then
        CURRENT_VERSION=$(dpkg-query -W -f='${Version}' pulse2-common 2> /dev/null | cut -d'g' -f1)
        echo "${CURRENT_VERSION}" > /var/lib/mmc/version
    fi
    # Get available version from the repository
    AVAILABLE_VERSION=$(apt-cache policy pulse2-common | grep Candidat | awk '{print $2}' | cut -d'g' -f1)
}

update_repo_defs() {
    str="Updating repository definitions..."
    echo "$str"
    write_to_log "$str"
    apt update &> /dev/null
    if [[ $? -ne 0 ]]; then
        str="[x] Error updating repository definitions. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    str="[v] Repository definitions updated successfully."
    echo "$str"
    write_to_log "$str"
}

setup_apt_sources() {
    str="Setting up apt sources for Medulla..."
    echo "$str"
    write_to_log "$str"
    curl -fsSL https://apt.medulla-tech.io/stable.sources -o /etc/apt/sources.list.d/medulla.sources
    if [[ $? -ne 0 ]]; then
        str="[x] Error downloading apt sources file. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    str="[v] Apt sources for Medulla set up successfully."
    echo "$str"
    write_to_log "$str"
}

update_medulla() {
    str="[=] Updating Medulla packages to the latest version..."
    echo "$str"
    write_to_log "$str"
    DEBIAN_FRONTEND=noninteractive apt -o Dpkg::Options::="--force-confold" --force-yes -y upgrade &> /dev/null
    if [[ $? -ne 0 ]]; then
        str="[x] Error updating Medulla packages. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    str="[v] Medulla packages updated successfully."
    echo "$str"
    write_to_log "$str"
}

update_relays() {
    str="[=] Updating Medulla packages to the latest version on relay servers..."
    echo "$str"
    write_to_log "$str"
    SSH_OPTIONS='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'
    RELAYS=$(mysql --defaults-group-suffix=medulla xmppmaster -Bse "SELECT nameserver FROM relayserver WHERE jid NOT LIKE 'rspulse%@pulse/%';")
    for RELAY in ${RELAYS}; do
        str=" Updating relay server: ${RELAY} ..."
        echo "$str"
        write_to_log "$str"
        ssh ${SSH_OPTIONS} root@${RELAY} "apt update &> /dev/null"
        if [[ $? -ne 0 ]]; then
            str="[!] Error updating repository on relay server: ${RELAY}."
            echo "$str"
            write_to_log "$str"
        fi
        ssh ${SSH_OPTIONS} root@${RELAY} "DEBIAN_FRONTEND=noninteractive apt -o Dpkg::Options::='--force-confold' --force-yes -y upgrade &> /dev/null"
        if [[ $? -ne 0 ]]; then
            str="[!] Error updating relay server: ${RELAY}."
            echo "$str"
            write_to_log "$str"
        fi
        ssh ${SSH_OPTIONS} root@${RELAY} "/usr/sbin/restart-pulse-services &> /dev/null"
        if [[ $? -ne 0 ]]; then
            str="[!] Error restarting services on relay server: ${RELAY}."
            echo "$str"
            write_to_log "$str"
        fi
        str="[v] Relay server ${RELAY} updated successfully."
        echo "$str"
        write_to_log "$str"
    done
}

# --- End of common functions for Medulla updates ---


# --- Specific update functions for each version ---

update_521_to_530() {
    str="Applying Medulla config update from 5.2.1 to 5.3.0..."
    echo "$str"
    write_to_log "$str"
    update_medulla
    apt -y install pulse-agent-installers
    if [[ $? -ne 0 ]]; then
        str="[x] Error installing pulse-agent-installers package. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    apt -y install python3-mmc-pulse2
    if [[ $? -ne 0 ]]; then
        str="[x] Error installing python3-mmc-pulse2 package. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    echo "5.3.0" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.2.1 to 5.3.0 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

update_530_to_540() {
    str="Applying Medulla config update from 5.3.0 to 5.4.0..."
    echo "$str"
    write_to_log "$str"

    ## Configure saas_application for GLPI ITSM API
    str="[=] Configuring Medulla for GLPI ITSM API..."
    echo "$str"
    write_to_log "$str"
    # Insert APP token into saas_application
    GLPI_APPTOKEN=$(mysql --defaults-group-suffix=itsm glpi -Bse "SELECT app_token FROM glpi_apiclients WHERE name = 'MMC' LIMIT 1")
    if [[ -z "${GLPI_APPTOKEN}" ]]; then
        str="[=] Generating new GLPI API token for MMC application..."
        echo "$str"
        write_to_log "$str"
        apt -y install apg
        GLPI_APPTOKEN=$(apg -a 1 -M NCL -n 1 -x 40 -m 40)
        mysql --defaults-group-suffix=itsm glpi -Bse "INSERT INTO glpi_apiclients (is_recursive, name, is_active, app_token) VALUES (1, 'MMC', 1, '${GLPI_APPTOKEN}')"
        if [[ $? -ne 0 ]]; then
            str="[x] Error inserting MMC API client into GLPI database. Aborting."
            echo "$str"
            write_to_log "$str"
            exit 1
        fi
        str="[v] GLPI API token for MMC application generated successfully."
        echo "$str"
        write_to_log "$str"
    fi
    mysql --defaults-group-suffix=medulla admin -e "INSERT INTO saas_application (setting_name, setting_value, setting_description) VALUES ('glpi_mmc_app_token', '${GLPI_APPTOKEN}', 'MMC application token for ITSM API')"
    if [[ $? -ne 0 ]]; then
        str="[x] Error inserting GLPI MMC application token into Medulla database. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    # Insert URL and ITSM type into saas_application
    GLPI_URL=$(crudini --get /etc/mmc/plugins/glpi.ini.local webservices glpi_base_url)
    mysql --defaults-group-suffix=medulla admin -e "INSERT INTO saas_application (setting_name, setting_value, setting_description) VALUES ('glpi_url_base_api', '${GLPI_URL}', 'MMC application URL for ITSM API')"
    if [[ $? -ne 0 ]]; then
        str="[x] Error inserting GLPI URL into Medulla database. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    mysql --defaults-group-suffix=medulla admin -e "INSERT INTO saas_application (setting_name, setting_value, setting_description) VALUES ('type_api', 'glpi_rest', 'ITSM API type')"
    if [[ $? -ne 0 ]]; then
        str="[x] Error inserting ITSM API type into Medulla database. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    # Insert API token into saas_application
    GLPI_ROOTUSER=$(crudini --get /etc/mmc/plugins/glpi.ini.local webservices glpi_username)
    GLPI_ROOTUSER_APITOKEN=$(mysql --defaults-group-suffix=itsm glpi -Bse "SELECT api_token FROM glpi_users WHERE name = '${GLPI_ROOTUSER}' LIMIT 1")
    if [[ -z "${GLPI_ROOTUSER_APITOKEN}" ]]; then
        str="[=] Generating new GLPI API token for MMC..."
        echo "$str"
        write_to_log "$str"
        apt -y install apg
        GLPI_ROOTUSER_APITOKEN=$(apg -a 1 -M NCL -n 1 -x 40 -m 40)
        mysql --defaults-group-suffix=itsm glpi -e "UPDATE glpi_users SET api_token = '${GLPI_ROOTUSER_APITOKEN}' where name = '${GLPI_ROOTUSER}'"
        if [[ $? -ne 0 ]]; then
            str="[x] Error inserting root user API token into GLPI database. Aborting."
            echo "$str"
            write_to_log "$str"
            exit 1
        fi
        str="[v] GLPI API token for root user generated successfully."
        echo "$str"
        write_to_log "$str"
    fi
    mysql --defaults-group-suffix=medulla admin -e "INSERT INTO saas_application (setting_name, setting_value, setting_description) VALUES ('glpi_root_user_token', '${GLPI_ROOTUSER_APITOKEN}', 'MMC user token for ITSM API super-admin user')"
    if [[ $? -ne 0 ]]; then
        str="[x] Error inserting GLPI root user token into Medulla database. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    str="[v] Medulla configured for GLPI ITSM API successfully."
    echo "$str"
    write_to_log "$str"

    ## Configure OIDC
    URL_PROVIDER=$(crudini --get /etc/mmc/authproviders.ini.local OIDC urlProvider)
    if [[ -z "${URL_PROVIDER}" ]]; then
        str="[!] OIDC URL provider is not configured. Skipping OIDC configuration."
        echo "$str"
        write_to_log "$str"
        return
    else
        str="[=] Configuring OIDC provider in Medulla..."
        echo "$str"
        write_to_log "$str"
        CLIENT_ID=$(crudini --get /etc/mmc/authproviders.ini.local OIDC clientId)
        CLIENT_SECRET=$(crudini --get /etc/mmc/authproviders.ini.local OIDC clientSecret)
        mysql --defaults-group-suffix=medulla admin -e "INSERT INTO providers (client_name, name, url_provider, client_id, client_secret) values ('mmc', 'OIDC', '${URL_PROVIDER}', '${CLIENT_ID}', '${CLIENT_SECRET}')"
        if [[ $? -ne 0 ]]; then
            str="[x] Error inserting OIDC provider into Medulla database. Aborting."
            echo "$str"
            write_to_log "$str"
            exit 1
        fi
        str="[v] OIDC provider configured in Medulla successfully."
        echo "$str"
        write_to_log "$str"
    fi
    update_medulla
    update_relays
    echo "5.4.0" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.3.0 to 5.4.0 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

update_540_to_541() {
    str="Applying Medulla config update from 5.4.0 to 5.4.1..."
    echo "$str"
    write_to_log "$str"
    update_medulla
    update_relays
    echo "5.4.1" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.4.0 to 5.4.1 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

update_541_to_542() {
    str="Applying Medulla config update from 5.4.1 to 5.4.2..."
    echo "$str"
    write_to_log "$str"
    update_medulla
    update_relays
    echo "5.4.2" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.4.1 to 5.4.2 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

update_542_to_543() {
    str="Applying Medulla config update from 5.4.2 to 5.4.3..."
    echo "$str"
    write_to_log "$str"
    update_medulla
    update_relays
    echo "5.4.3" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.4.2 to 5.4.3 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

update_543_to_544() {
    str="Applying Medulla config update from 5.4.3 to 5.4.4..."
    echo "$str"
    write_to_log "$str"

    ## Update ACLs for ITSM profiles
    str="[=] Updating ACLs for ITSM profiles..."
    echo "$str"
    write_to_log "$str"
    sed -i 's/^profile_acl_Super-Admin.*$/profile_acl_Super-Admin = :inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#logview#index:base#logview#logsinventory:base#logview#logsbackup:base#logview#logsdeployment:base#logview#logsquickaction:base#logview#logsdownload:base#logview#logskiosk:base#logview#logspackaging:base#logview#logsremotedesktop:base#logview#logsimaging:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#relaysList:admin#admin#packageslist:admin#admin#reconfiguremachines:admin#admin#switchrelay:admin#admin#conffile:admin#admin#detailactions:admin#admin#qalaunched:admin#admin#qaresult:admin#admin#rules_tabs:admin#admin#rules:admin#admin#rulesDetail:admin#admin#moveRule:admin#admin#clustersList:admin#admin#editCluster:admin#admin#newCluster:admin#admin#deleteRelayRule:admin#admin#editRelayRule:admin#admin#moveRelayRule:admin#admin#ban:admin#admin#unban:admin#admin#entitiesManagement:admin#admin#editEntity:admin#admin#deleteEntity:admin#admin#listUsersofEntity:admin#admin#editUser:admin#admin#deleteUser:admin#admin#desactivateUser:admin#admin#downloadAgent:admin#admin#downloadAgentFile:admin#admin#manageproviders:admin#admin#editProvider:admin#admin#deleteProvider:dashboard#main#default:dashboard#main#computersOnline_dashboard:dashboard#main#space_dashboard:dashboard#main#general_dashboard:dashboard#main#backup_dashboard:dashboard#main#product_updates_dashboard:dashboard#main#alerts:dashboard#main#successRate:dashboard#main#agents:dashboard#main#deploymentsLaunched:glpi#glpi#glpi_dashboard:glpi#glpi#antivirus_dashboard:glpi#glpi#inventory_dashboard:glpi#glpi#os_repartition_dashboard:imaging#manage#systemImageManager:imaging#manage#sysprepView:imaging#manage#profilescript:imaging#manage#editProfilescript:imaging#manage#addProfilescript:imaging#manage#index:imaging#manage#master:imaging#manage#master_remove:imaging#manage#master_delete:imaging#manage#master_edit:imaging#manage#master_clone:imaging#manage#synchromaster:imaging#manage#master_add:imaging#manage#service:imaging#manage#service_edit:imaging#manage#service_del:imaging#manage#service_add:imaging#manage#service_remove:imaging#manage#service_show_used:imaging#manage#bootmenu:imaging#manage#bootmenu_up:imaging#manage#bootmenu_down:imaging#manage#bootmenu_edit:imaging#manage#postinstall:imaging#manage#postinstall_edit:imaging#manage#postinstall_duplicate:imaging#manage#postinstall_create_boot_service:imaging#manage#postinstall_redirect_to_boot_service:imaging#manage#postinstall_delete:imaging#manage#configuration:imaging#manage#save_configuration:imaging#manage#computersprofilecreator:imaging#manage#computersprofilecreatesubedit:imaging#manage#computersprofilecreatesubdel:imaging#manage#computersprofileedit:imaging#manage#computersprofilesubedit:imaging#manage#computersprofilesubdel:imaging#manage#list_profiles:imaging#manage#groupregister_target:imaging#manage#groupimgtabs:imaging#manage#groupbootmenu_remove:imaging#manage#display:imaging#manage#delete_group:imaging#manage#computersgroupedit:imaging#manage#edit_share:imaging#manage#groupmsctabs:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:medulla_server#update#viewProductUpdates:medulla_server#update#installProductUpdates:medulla_server#update#ajaxInstallProductUpdates:medulla_server#update#restartAllMedullaServices:medulla_server#update#regenerateAgent:pkgs#pkgs#rulesList:pkgs#pkgs#addRule:pkgs#pkgs#editRule:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:pkgs#pkgs#deleteBundle:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#ajaxMajorEntitiesList:updates#updates#ajaxMajorEntitiesListServ:updates#updates#updatesListWin:updates#updates#enableUpdate:updates#updates#disableUpdate:updates#updates#whitelistUpdate:updates#updates#blacklistUpdate:updates#updates#greylistUpdate:updates#updates#deleteRule:updates#updates#grayEnable:updates#updates#grayDisable:updates#updates#grayApprove:updates#updates#banUpdate:updates#updates#whiteUnlist:updates#updates#blackUnban:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:updates#updates#approve_rules:updates#updates#approve_products:urbackup#urbackup#index:urbackup#urbackup#list_backups:urbackup#urbackup#start_backup:urbackup#urbackup#checkMachine:urbackup#urbackup#create_group:urbackup#urbackup#add_member_togroup:urbackup#urbackup#add_member_togroup_aftercheck:urbackup#urbackup#edit_group_settings:urbackup#urbackup#list_computers_ongroup:urbackup#urbackup#result_search_file:urbackup#urbackup#restart_service:urbackup#urbackup#validate_edit_group:urbackup#urbackup#deleting_backup:urbackup#urbackup#deleting_group:urbackup#urbackup#deleting_client:urbackup#urbackup#all_files_backup:urbackup#urbackup#restore_file:urbackup#urbackup#download_file:urbackup#urbackup#usersgroups:urbackup#urbackup#logs:xmppmaster#xmppmaster#index:xmppmaster#xmppmaster#auditdeploy:xmppmaster#xmppmaster#auditpastdeploys:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditconvergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#filesmanagers:xmppmaster#xmppmaster#topology:xmppmaster#xmppmaster#alertsdetail:xmppmaster#xmppmaster#alerts:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#wakeonlan:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#switchrelay:xmppmaster#xmppmaster#reconfiguremachines:xmppmaster#xmppmaster#qalaunched:xmppmaster#xmppmaster#qaresult:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#monconfig:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs:updates#updates#MajorEntitiesList#tabwin:updates#updates#MajorEntitiesList#tabwinserv:admin#admin#rules_tabs#relayRules:admin#admin#rules_tabs#newRelayRule:imaging#manage#systemImageManager#unattended:imaging#manage#systemImageManager#sysprepList:imaging#manage#computersprofilecreator#tabdyn:imaging#manage#computersprofilecreator#tabsta:imaging#manage#computersprofilecreator#tabfromfile:imaging#manage#computersprofilecreatesubedit#tabdyn:imaging#manage#computersprofilecreatesubedit#tabsta:imaging#manage#computersprofilecreatesubedit#tabfromfile:imaging#manage#computersprofilecreatesubdel#tabdyn:imaging#manage#computersprofilecreatesubdel#tabsta:imaging#manage#computersprofilecreatesubdel#tabfromfile:imaging#manage#groupimgtabs#grouptabbootmenu:imaging#manage#groupimgtabs#grouptabimages:imaging#manage#groupimgtabs#grouptabservices:imaging#manage#groupimgtabs#grouptabimlogs:imaging#manage#groupimgtabs#grouptabconfigure:imaging#manage#groupmsctabs#grouptablaunch:imaging#manage#groupmsctabs#grouptabbundle:imaging#manage#groupmsctabs#grouptablogs:imaging#manage#groupmsctabs#grouptabhistory:xmppmaster#xmppmaster#alerts#notificationsTab:xmppmaster#xmppmaster#alerts#notificationsHistoryTab\//' /etc/mmc/plugins/glpi.ini.local
    if [[ $? -ne 0 ]]; then
        str="[x] Error updating ACLs for ITSM profiles. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    # Specific to SAAS, so only documented here.
    #sed -i 's/^profile_acl_Super-Admin.*$/profile_acl_Super-Admin = :inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#editEntity:admin#admin#deleteEntity:admin#admin#listUsersofEntity:admin#admin#editUser:admin#admin#deleteUser:admin#admin#desactivateUser:admin#admin#downloadAgent:admin#admin#downloadAgentFile:dashboard#main#default:dashboard#main#computersOnline_dashboard:dashboard#main#successRate:dashboard#main#agents:dashboard#main#deploymentsLaunched:glpi#glpi#glpi_dashboard:glpi#glpi#antivirus_dashboard:glpi#glpi#inventory_dashboard:glpi#glpi#os_repartition_dashboard:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#ajaxMajorEntitiesList:updates#updates#ajaxMajorEntitiesListServ:updates#updates#updatesListWin:updates#updates#enableUpdate:updates#updates#disableUpdate:updates#updates#whitelistUpdate:updates#updates#blacklistUpdate:updates#updates#greylistUpdate:updates#updates#deleteRule:updates#updates#grayEnable:updates#updates#grayDisable:updates#updates#grayApprove:updates#updates#banUpdate:updates#updates#whiteUnlist:updates#updates#blackUnban:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:updates#updates#approve_rules:updates#updates#approve_products:xmppmaster#xmppmaster#index:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs:updates#updates#MajorEntitiesList#tabwin:updates#updates#MajorEntitiesList#tabwinserv\//' /etc/mmc/plugins/glpi.ini.local
    #sed -i 's/^profile_acl_Admin.*$/profile_acl_Admin = :inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#listUsersofEntity:admin#admin#editUser:admin#admin#deleteUser:admin#admin#desactivateUser:admin#admin#downloadAgent:admin#admin#downloadAgentFile:dashboard#main#default:dashboard#main#computersOnline_dashboard:dashboard#main#successRate:dashboard#main#agents:dashboard#main#deploymentsLaunched:glpi#glpi#glpi_dashboard:glpi#glpi#antivirus_dashboard:glpi#glpi#inventory_dashboard:glpi#glpi#os_repartition_dashboard:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#ajaxMajorEntitiesList:updates#updates#ajaxMajorEntitiesListServ:updates#updates#updatesListWin:updates#updates#enableUpdate:updates#updates#disableUpdate:updates#updates#whitelistUpdate:updates#updates#blacklistUpdate:updates#updates#greylistUpdate:updates#updates#deleteRule:updates#updates#grayEnable:updates#updates#grayDisable:updates#updates#grayApprove:updates#updates#banUpdate:updates#updates#whiteUnlist:updates#updates#blackUnban:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:updates#updates#approve_rules:updates#updates#approve_products:xmppmaster#xmppmaster#index:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs:updates#updates#MajorEntitiesList#tabwin:updates#updates#MajorEntitiesList#tabwinserv\//' /etc/mmc/plugins/glpi.ini.local
    #sed -i 's/^profile_acl_Technician.*$/profile_acl_Technician = :inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#listUsersofEntity:admin#admin#downloadAgent:admin#admin#downloadAgentFile:dashboard#main#default:dashboard#main#computersOnline_dashboard:dashboard#main#successRate:dashboard#main#agents:dashboard#main#deploymentsLaunched:glpi#glpi#glpi_dashboard:glpi#glpi#antivirus_dashboard:glpi#glpi#inventory_dashboard:glpi#glpi#os_repartition_dashboard:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#ajaxMajorEntitiesList:updates#updates#ajaxMajorEntitiesListServ:updates#updates#updatesListWin:updates#updates#enableUpdate:updates#updates#disableUpdate:updates#updates#whitelistUpdate:updates#updates#blacklistUpdate:updates#updates#greylistUpdate:updates#updates#deleteRule:updates#updates#grayEnable:updates#updates#grayDisable:updates#updates#grayApprove:updates#updates#banUpdate:updates#updates#whiteUnlist:updates#updates#blackUnban:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:updates#updates#approve_rules:updates#updates#approve_products:xmppmaster#xmppmaster#index:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs:updates#updates#MajorEntitiesList#tabwin:updates#updates#MajorEntitiesList#tabwinserv\//' /etc/mmc/plugins/glpi.ini.local

    ## Update agents generation script
    str="[=] Updating agents generation script..."
    echo "$str"
    write_to_log "$str"
    curl -fsSL https://dl.medulla-tech.io/up/generate_medulla_agent.sh -o /usr/sbin/generate_medulla_agent.sh
    if [[ $? -ne 0 ]]; then
        str="[x] Error downloading agents generation script. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    update_medulla
    update_relays
    echo "5.4.4" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.4.3 to 5.4.4 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

update_544_to_545() {
    str="Applying Medulla config update from 5.4.4 to 5.4.5..."
    echo "$str"
    write_to_log "$str"
    # Specific to SAAS, so only documented here. ACLs for OIDC
    #sed -i 's/^profile_acl_Super-Admin.*$/profile_acl_Super-Admin = :inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#editEntity:admin#admin#deleteEntity:admin#admin#listUsersofEntity:admin#admin#editUser:admin#admin#deleteUser:admin#admin#desactivateUser:admin#admin#downloadAgent:admin#admin#downloadAgentFile:admin#admin#manageproviders:admin#admin#editProvider:admin#admin#deleteProvider:dashboard#main#default:dashboard#main#computersOnline_dashboard:dashboard#main#successRate:dashboard#main#agents:dashboard#main#deploymentsLaunched:glpi#glpi#glpi_dashboard:glpi#glpi#antivirus_dashboard:glpi#glpi#inventory_dashboard:glpi#glpi#os_repartition_dashboard:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#ajaxMajorEntitiesList:updates#updates#ajaxMajorEntitiesListServ:updates#updates#updatesListWin:updates#updates#enableUpdate:updates#updates#disableUpdate:updates#updates#whitelistUpdate:updates#updates#blacklistUpdate:updates#updates#greylistUpdate:updates#updates#deleteRule:updates#updates#grayEnable:updates#updates#grayDisable:updates#updates#grayApprove:updates#updates#banUpdate:updates#updates#whiteUnlist:updates#updates#blackUnban:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:updates#updates#approve_rules:updates#updates#approve_products:xmppmaster#xmppmaster#index:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs:updates#updates#MajorEntitiesList#tabwin:updates#updates#MajorEntitiesList#tabwinserv\//' /etc/mmc/plugins/glpi.ini.local
    update_medulla
    update_relays
    echo "5.4.5" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.4.4 to 5.4.5 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

update_545_to_546() {
    str="Applying Medulla config update from 5.4.5 to 5.4.6..."
    echo "$str"
    write_to_log "$str"
    update_medulla
    update_relays
    echo "5.4.6" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.4.5 to 5.4.6 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

update_546_to_550() {
    str="Applying Medulla config update from 5.4.6 to 5.5.0..."
    echo "$str"
    write_to_log "$str"
    update_medulla

    ## Make sure clientdbsetup section exists in /root/.my.cnf
    if ! grep -q "\[clientdbsetup\]" /root/.my.cnf; then
        mysqlpassword=$(crudini --get /root/.my.cnf client password)
        if [[ $? -ne 0 ]]; then
            str="[x] Error retrieving MySQL password from /root/.my.cnf. Aborting."
            echo "$str"
            write_to_log "$str"
            exit 1
        fi
        crudini --set /root/.my.cnf clientdbsetup host localhost
        crudini --set /root/.my.cnf clientdbsetup port 3306
        crudini --set /root/.my.cnf clientdbsetup user root
        crudini --set /root/.my.cnf clientdbsetup password "$mysqlpassword"
        if [[ $? -ne 0 ]]; then
            str="[x] Error adding clientdbsetup section to /root/.my.cnf. Aborting."
            echo "$str"
            write_to_log "$str"
            exit 1
        fi
        str="[v] clientdbsetup section added to /root/.my.cnf successfully."
        echo "$str"
        write_to_log "$str"
    fi

    ## Setup new MMC module: security
    setup_new_mmc_module "security"
    # Configure security module for CVE Central
    crudini --set /etc/mmc/plugins/security.ini.local cve_central url https://cve.medulla-tech.io
    if [[ $? -ne 0 ]]; then
        str="[x] Error configuring CVE Central URL in security module. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    crudini --set /etc/mmc/plugins/security.ini.local cve_central server_id $(crudini --get /etc/mmc/mmc.ini.local server_01 description)
    if [[ $? -ne 0 ]]; then
        str="[x] Error configuring CVE Central server_id in security module. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    crudini --set /etc/mmc/plugins/security.ini.local cve_central keyAES32 $(crudini --get /etc/mmc/plugins/xmppmaster.ini.local defaultconnection keyAES32)
    if [[ $? -ne 0 ]]; then
        str="[x] Error configuring CVE Central keyAES32 in security module. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    # Append the following string to /etc/mmc/plugins/glpi.ini.local profile_acl_Super-Admin and profile_acl_Admin parameters before the final / if not already present:
    # :security#security#index:security#security#softwareDetail:security#security#machines:security#security#machineDetail:security#security#entities:security#security#groups:security#security#groupDetail:security#security#allcves:security#security#cveDetail:security#security#ajaxAddExclusion:security#security#ajaxScanMachine:security#security#ajaxStartScanEntity:security#security#ajaxStartScanGroup:security#security#settings:security#security#ajaxResetDisplayFilters:security#security#settings:security#security#deployStoreUpdate
    # And profile_acl_Technician if not already present:
    # :security#security#index:security#security#softwareDetail:security#security#machines:security#security#machineDetail:security#security#entities:security#security#groups:security#security#groupDetail:security#security#allcves:security#security#cveDetail:security#security#ajaxAddExclusion:security#security#ajaxScanMachine:security#security#ajaxStartScanEntity:security#security#ajaxStartScanGroup:security#security#settings:security#security#ajaxResetDisplayFilters
    str="[=] Configuring ACLs for new Medulla MMC module 'security' in glpi.ini.local..."
    echo "$str"
    write_to_log "$str"
    for profile in Super-Admin Admin; do
        if ! grep -q "security#security#index" /etc/mmc/plugins/glpi.ini.local | grep -q "^profile_acl_$profile"; then
            sed -i "/^profile_acl_$profile/s|\(.*\)/$|\1:security#security#index:security#security#softwareDetail:security#security#machines:security#security#machineDetail:security#security#entities:security#security#groups:security#security#groupDetail:security#security#allcves:security#security#cveDetail:security#security#ajaxAddExclusion:security#security#ajaxScanMachine:security#security#ajaxStartScanEntity:security#security#ajaxStartScanGroup:security#security#settings:security#security#ajaxResetDisplayFilters:security#security#settings:security#security#deployStoreUpdate/|" /etc/mmc/plugins/glpi.ini.local
            if [[ $? -ne 0 ]]; then
                str="[x] Error updating ACLs for $profile profile in glpi.ini.local. Aborting."
                echo "$str"
                write_to_log "$str"
                exit 1
            fi
            str="[v] ACLs for $profile profile in glpi.ini.local updated successfully."
            echo "$str"
            write_to_log "$str"
        fi
    done
    for profile in Technician; do
        if ! grep -q "security#security#index" /etc/mmc/plugins/glpi.ini.local | grep -q "^profile_acl_$profile"; then
            sed -i "/^profile_acl_$profile/s|\(.*\)/$|\1:security#security#index:security#security#softwareDetail:security#security#machines:security#security#machineDetail:security#security#entities:security#security#groups:security#security#groupDetail:security#security#allcves:security#security#cveDetail:security#security#ajaxAddExclusion:security#security#ajaxScanMachine:security#security#ajaxStartScanEntity:security#security#ajaxStartScanGroup:security#security#settings:security#security#ajaxResetDisplayFilters/|" /etc/mmc/plugins/glpi.ini.local
            if [[ $? -ne 0 ]]; then
                str="[x] Error updating ACLs for $profile profile in glpi.ini.local. Aborting."
                echo "$str"
                write_to_log "$str"
                exit 1
            fi
            str="[v] ACLs for $profile profile in glpi.ini.local updated successfully."
            echo "$str"
            write_to_log "$str"
        fi
    done
    # mmc-agent will be restarted in final_operations
    str="[v] Medulla MMC module 'security' setup and configuration applied successfully."
    echo "$str"
    write_to_log "$str"

    # Setup anon stats exporter for Medulla
    str="[=] Setting up anon stats cron for Medulla..."
    echo "$str"
    write_to_log "$str"
    # Create /etc/cron.d/medulla-stats
    echo "0 4 * * * root /usr/sbin/medulla-stats.sh &> /dev/null" > /etc/cron.d/medulla-stats
    # Restart cron service to apply changes
    systemctl restart cron
    if [[ $? -ne 0 ]]; then
        str="[x] Error setting up anon statscron for Medulla. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    str="[v] Anon stats cron for Medulla set up successfully."
    echo "$str"
    write_to_log "$str"

    # Create cron job for checking for Medulla updates
    str="[=] Setting up cron job for checking for Medulla updates..."
    echo "$str"
    write_to_log "$str"
    # Create /etc/cron.d/check_medulla_updates
    echo "0 3 * * * root /usr/sbin/check_medulla_updates.sh 2>&1 | tee -a /tmp/check_medulla_updates.log" > /etc/cron.d/check_medulla_updates
    # Restart cron service to apply changes
    systemctl restart cron
    if [[ $? -ne 0 ]]; then
        str="[x] Error setting up cron job for checking for Medulla updates. Aborting."
        echo "$str"
        write_to_log "$str"
        exit 1
    fi
    str="[v] Cron job for checking for Medulla updates set up successfully."
    echo "$str"
    write_to_log "$str"

    update_relays
    echo "5.5.0" > /var/lib/mmc/version
    str="[v] Medulla config update from 5.4.6 to 5.5.0 applied successfully."
    echo "$str"
    write_to_log "$str"
    exec /tmp/update_medulla.sh "$@"
}

# --- End of specific update functions for each version ---



final_operations() {
    str="Performing final operations for Medulla migration..."
    echo "$str"
    write_to_log "$str"

    # Add any final operations needed for the migration here

    str="[v] Medulla migration completed successfully."
    echo "$str"
    write_to_log "$str"
    rm -f /var/lib/mmc/.accepted_medulla_update_disclaimer

    # Update database: mark update as done
    NEW_VERSION=$(cat /var/lib/mmc/version 2>/dev/null)
    mysql -u"${DBUSER}" -p"${DBPASS}" -h"${DBHOST:-localhost}" admin -e \
        "UPDATE medulla_update_availability SET update_available=0, current_version='${NEW_VERSION}', available_version=NULL, last_check=NOW(), last_check_status='success' WHERE id=1;" 2>/dev/null

    ## Restart services then generate agents (all in background, survives service restart)
    str="[=] Restarting Medulla services..."
    echo "$str"
    write_to_log "$str"

    nohup bash -c '
        /usr/sbin/restart-pulse-services &> /dev/null
        sleep 30
        /var/lib/pulse2/clients/generate-pulse-agent.sh &> /dev/null
        echo "$(date "+%Y-%m-%d %H:%M:%S") - [v] Agents generated successfully." >> /var/log/medulla_update.log
    ' &> /dev/null &
}


# --- Main script execution starts here ---

# Display disclaimer and get user acceptance if running interactively and .accepted_medulla_update_disclaimer not present
if [[ -t 0 ]] && [[ ! -f /var/lib/mmc/.accepted_medulla_update_disclaimer ]]; then
    accept_disclaimer
elif [[ -f /var/lib/mmc/.accepted_medulla_update_disclaimer ]]; then
    str="[i] Disclaimer already accepted. Proceeding with migration."
    echo "$str"
    write_to_log "$str"
else
    str="[i] Non-interactive mode detected. Proceeding without disclaimer acceptance."
    echo "$str"
    write_to_log "$str"
fi

# Download migration script and restart myself if needed
# If run with --noupdate option, skip this step
if [[ " $* " == *" --noupdate "* ]]; then
    str="[i] --noupdate option detected. Skipping download of latest version of migration script."
    echo "$str"
    write_to_log "$str"
else
    download_migration_script_and_restart
fi

# Setup apt sources for Medulla updates
setup_apt_sources
# Update repo definitions
update_repo_defs

check_medulla_version
# Perform updates based on current version
str="[i] Current Medulla version: $CURRENT_VERSION"
echo "$str"
write_to_log "$str"
case "$CURRENT_VERSION" in
    "5.2.1")
        if [[ "$AVAILABLE_VERSION" > "5.2.1" ]]; then
            update_521_to_530
        fi
        ;;
    "5.3.0")
        if [[ "$AVAILABLE_VERSION" > "5.3.0" ]]; then
            update_530_to_540
        fi
        ;;
    "5.4.0")
        if [[ "$AVAILABLE_VERSION" > "5.4.0" ]]; then
            update_540_to_541
        fi
        ;;
    "5.4.1")
        if [[ "$AVAILABLE_VERSION" > "5.4.1" ]]; then
            update_541_to_542
        fi
        ;;
    "5.4.2")
        if [[ "$AVAILABLE_VERSION" > "5.4.2" ]]; then
            update_542_to_543
        fi
        ;;
    "5.4.3")
        if [[ "$AVAILABLE_VERSION" > "5.4.3" ]]; then
            update_543_to_544
        fi
        ;;
    "5.4.4")
        if [[ "$AVAILABLE_VERSION" > "5.4.4" ]]; then
            update_544_to_545
        fi
        ;;
    "5.4.5")
        if [[ "$AVAILABLE_VERSION" > "5.4.5" ]]; then
            update_545_to_546
        fi
        ;;
    "5.4.6")
        if [[ "$AVAILABLE_VERSION" > "5.4.6" ]]; then
            update_546_to_550
        fi
        ;;
    *)
        str="Updating minor version if needed..."
        echo "$str"
        write_to_log "$str"
        update_medulla
        update_relays
        str="[!] Medulla is already at the latest version or an unsupported version is detected."
        echo "$str"
        write_to_log "$str"
        ;;
esac

# Call final operations
final_operations
