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

defaultvalus(){
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
clear

if [[ $# -ne 2 ]]
then
    uuidval=$(uuid)
    echo "il doit y avoir 2 parametres"
    echo "argument obligatoire 'uuid' suivi de l'action ['s' | 'S' | 'c' | 'C']"
    echo "exemple "
    echo "$pythonexec $prog $uuidval C"
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
    echo "commande non valable"
    echo "option c ou s"
    echo "eg : "
    echo "$pythonexec $prog $option -c"
    echo "or"
    echo "$pythonexec $prog $option -s"
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
$pythonexec $prog $option
