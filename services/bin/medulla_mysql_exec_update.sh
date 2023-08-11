#!/bin/bash
#
# (c) 20118 Siveo, http://www.siveo.net
#
# This file is part of Pulse 2
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# file : /usr/sbin/medulla_mysql_exec_update.sh

function defaultvalus(){
    user=mmc
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
    baseupdate="/var/lib/pulse2/base_update_package"
    partage="winupdates"
    logfile="/var/log/mmc/medulla-mariadb-synchro-update-package.log"
    fileconf="/etc/mmc/plugins/xmppmaster.ini"
    # Récupérer le nom du programme (nom du script en cours d'exécution)
    # nom_programme="${0##*/}"
    nom_programme=$(basename "$prog")
    }

function  check_and_exit_if_running() {
    local parametre_cible="$1"
    local nom_programme="move-update-package.py"

    if ps aux | grep -v grep | grep "$nom_programme.*$parametre_cible" >/dev/null 2>&1; then
        echo "Une instance de $nom_programme avec le paramètre $parametre_cible est déjà en cours d'exécution."
        exit 1
    fi
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
        log_message "L'UUID est conforme. $uuid"
    else
        log_message "L'UUID n'est pas conforme. $uuid"
        exit 1
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

function Get_parameter_file_section() {
  # $1 conffile
  # $2 section
  conffile=$1
  conffilelocal=$1".local"
  eval "$(crudini --get --format=sh $conffile $2)"
  if [ -f "$conffilelocal" ]; then
    eval "$(crudini --get --format=sh $conffilelocal $2)"
fi
}

# Fonction pour vérifier et quitter le programme si une instance est déjà en cours d'exécution
function check_and_exit_if_running() {
    local parametre_cible="$1"

    if ps aux | grep -v grep | grep "$nom_programme.*$parametre_cible" >/dev/null 2>&1; then
        log_message "Une instance de $nom_programme avec le paramètre $parametre_cible est déjà en cours d'exécution."
        exit 1
    fi
}

defaultvalus
clear
# pas 2 instance de programme avec le meme uuid
check_and_exit_if_running $1

if [[ $# -ne 2 ]]
then
    uuidval=$(uuid)
    log_message "il doit y avoir 2 parametres"
    log_message "argument obligatoire 'uuid' suivi de l'action ['s' | 'S' | 'c' | 'C']"
    log_message "exemple "
    log_message "$pythonexec $prog $uuidval C"
    exit -1
fi
uuid_length="${#1}"
if [[ ${uuid_length} -ne 36 ]]
then
    echo "uuid non valable uuid doit avoir la forme suivante :" $(uuid)
    exit -1
fi

# option posible
# if [ "${#2}" != '1' ] ||  ! ([ "$2" == "s" ] || [ "$2" == "S" ] || [ "$2" == "c" ] ||  [ "$2" == "C" ])
# option permise
if [ "${#2}" != '1' ] ||  ! ([ "$2" == "s" ] || [ "$2" == "c" ] )
then
    log_message "commande non valable"
    log_message "option c ou s"
    log_message "eg : "
    log_message "$pythonexec $prog $option -c"
    log_message "or"
    log_message "$pythonexec $prog $option -s"
    exit -1
fi

if [ "`which crudini`" != "" ]
then
    Get_parameter_file_section $fileconf global
    if [ $log_level == "DEBUG" ]
    then
        debug=true
        quiet=true
    fi
    # cherche parameter
    Get_parameter_file_section $fileconf database
    user=$dbuser
    port=$dbport
    hostname=$dbhost
    password=$dbpasswd
fi

if [ $debug ]; then option+=" -d"; fi
if [ $quiet ]; then option+=" -q"; fi
option+=" -P$port"
option+=" -H$hostname"
option+=" -u$user"
option+=" -U$1"
option+=" -$2"
option+=" -o$baseupdate"
option+=" -M$partage"
option+=" -l$logfile"

if [ $debug ]; then
    launchdebug="$pythonexec $prog $option -pXXXXX"
    echo $launchdebug >> $logfile
fi

option+=" -p$password"
log_message $pythonexec $prog $option

# nohup $pythonexec $prog $option >> "$logfile" 2>> "$logfile" &
#     nohup : Cela indique au système de ne pas envoyer le signal SIGHUP (signal de raccrochage) au processus lorsque le terminal est fermé. Cela permet au processus de continuer à s'exécuter en arrière-plan.
#  & : Cela indique au shell de lancer le processus en arrière-plan. le script present rend la main imediatement
nohup $pythonexec $prog $option >> "$logfile" 2>&1 &
