#!/bin/bash

# This script maps PO and POT files to transifex ressources
# on https://transifex.mandriva.com

SCRIPT_PROJECT=`pwd`

which tx > /dev/null
if [ $? -ne 0 ]; then
	echo "Install the transifex client v0.4 (pip install transifex-client==0.4)"
	exit 1
fi

test -d .tx || tx init --host=https://fr.transifex.com/

args=$@

modules="dyngroup glpi imaging inventory kiosk msc pkgs pulse2 backuppc support guacamole base ppolicy services dashboard report xmppmaster updates urbackup"

for mod in $modules
do
    if [ "$mod" == "dashboard" ]; then
        cd $SCRIPT_PROJECT/../web/modules/$mod/locale/
        tx push -r pulse-1.p${mod} -s -t
    else
	    cd $SCRIPT_PROJECT/../web/modules/$mod/locale/
	    tx push -r pulse-1.${mod} -s -t
	    #-f --no-interactive
    fi
done
