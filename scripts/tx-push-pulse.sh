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

modules="dyngroup glpi imaging inventory msc pkgs pulse2 backuppc support guacamole"

for mod in $modules
do
	cd $SCRIPT_PROJECT/../web/modules/$mod/locale/
	tx push -r pulse-1.${mod} -s -t
	#-f --no-interactive
done
