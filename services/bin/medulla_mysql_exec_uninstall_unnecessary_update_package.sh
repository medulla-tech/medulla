#!/bin/bash
#
# (c) 20118 Siveo, http://www.siveo.net
#
# This file is part of Medulla 2
#
# Medulla 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Medulla 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Medulla 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# file :  /usr/sbin/medulla_mysql_exec_uninstall_unnecessary_update_package.sh
# ce programme deinsctalle les packages qui ne sont plus en gray list ou white list.
# ces paquages sont considérés comme plus utile
# Il sont en attente en base fichier dans directory  /var/lib/medulla/base_update_package

defaultvalus(){
    user=root
    port=3306
    hostname=lacalhost
    password=siveo
    debug=false
    quiet=false
    option=""
    date=$(date '+%d-%m-%Y %H:%M:%S')
    BASEDIR=$(dirname "$0")
    BASENAME=$(basename "$0")
    prog="/usr/sbin/medulla-mariadb-move-update-package.py"
    pythonexec=$(which python3)
    baseupdate="/var/lib/medulla/base_update_package"
    partage="winupdates"
    logfile="/var/log/mmc/medulla_mysql_exec_uninstall_unnecessary_update_package.log"
    fileconf="/etc/mmc/plugins/xmppmaster.ini"
    }

function log_message() {
    message="$1"
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    message_with_date="$timestamp - $message"
    echo "$message_with_date" >> "$logfile"
}

function is_valid_uuid() {
    uuid="$1"
    uuid_pattern='^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'

    if [[ "$uuid" =~ $uuid_pattern ]]; then
        log_message "L'UUID est conforme."
    else
        log_message "L'UUID n'est pas conforme."
    fi
}


function create_directory() {
    directory_path="$1"

    if [ ! -d "$directory_path" ]; then
        # Créer le répertoire s'il n'existe pas
        mkdir -p "$directory_path"
        if [ $? -eq 0 ]; then
            log_message "Le répertoire a été créé avec succès."
        else
            log_message "Erreur lors de la création du répertoire."
            exit 1
        fi
    fi
}

Get_parameter_file_section() {
  # $1 conffile
  # $2 section
  conffile=$1
  conffilelocal=$1".local"
  eval "$(crudini --get --format=sh $conffile $2)"
  if [ -f "$conffilelocal" ]; then
    eval "$(crudini --get --format=sh $conffilelocal $2)"
fi
}

defaultvalus

if [ "`which crudini`" != "" ]
then
    Get_parameter_file_section $fileconf global
    # cherche parameter
    Get_parameter_file_section $fileconf database
    user=$dbuser
    port=$dbport
    hostname=$dbhost
    password=$dbpasswd
fi

query="SELECT pkgs.packages.uuid AS uuid FROM pkgs.packages WHERE pkgs.packages.pkgs_share_id = (SELECT pkgs.pkgs_shares.id FROM pkgs.pkgs_shares WHERE pkgs.pkgs_shares.name = '$partage') AND pkgs.packages.uuid NOT IN (SELECT DISTINCT xmppmaster.up_gray_list.updateid FROM xmppmaster.up_gray_list UNION SELECT xmppmaster.up_white_list.updateid FROM xmppmaster.up_white_list);"
log_message "query : $query"
# Exécuter la requête en utilisant la commande mysql
result=$(echo "$query" | mysql -u "$user" -h "$hostname" -p"$password" -N)
# Itération sur les résultats en utilisant une boucle for
IFS=$'\n' # Définit le séparateur de champs pour inclure uniquement les sauts de ligne
for t in $result; do
    log_message "deinstalle package : $t"
    log_message "$pythonexec $prog -u$user -P$port -H$hostname -p$password -U $t -s'"
    # Faites ici ce que vous souhaitez avec chaque élément $t
    $pythonexec $prog -u"$user"  -P$port -H"$hostname" -p"$password" -U $t -s
done
