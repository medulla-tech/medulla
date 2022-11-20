#!/bin/bash

# This script maps PO and POT files to transifex ressources
# on https://www.transifex.com

SCRIPT_PROJECT=`pwd`

which tx > /dev/null
if [ $? -ne 0 ]; then
	echo "Install the transifex client v0.4 (pip install transifex-client==0.4)"
	exit 1
fi

test -d .tx || tx init --host=https://www.transifex.com

[ ! x$1 == x ] && lang="-l $1" && shift 1
args=$@

modules="base ppolicy services dashboard report xmppmaster dyngroup glpi imaging inventory kiosk msc pkgs pulse2 backuppc support guacamole updates urbackup"

for mod in $modules
do
    if [ "$mod" == "dashboard" ]; then
        cd $SCRIPT_PROJECT/../web/modules/$mod/locale/
        tx pull -a -f -r pulse-1.p${mod} ${lang} ${args}
        cp  -fv $SCRIPT_PROJECT/../web/modules/$mod/locale/fr/LC_MESSAGES/* $SCRIPT_PROJECT/../web/modules/$mod/locale/fr_FR/LC_MESSAGES
        sed -i 's/Language: fr\\n/Language: fr_FR\\n/' $SCRIPT_PROJECT/../web/modules/$mod/locale/fr_FR/LC_MESSAGES/$mod.po
    else
	cd $SCRIPT_PROJECT/../web/modules/$mod/locale/
	tx pull -a -f -r pulse-1.${mod} ${lang} ${args}
	cp  -fv $SCRIPT_PROJECT/../web/modules/$mod/locale/fr/LC_MESSAGES/* $SCRIPT_PROJECT/../web/modules/$mod/locale/fr_FR/LC_MESSAGES
        sed -i 's/Language: fr\\n/Language: fr_FR\\n/' $SCRIPT_PROJECT/../web/modules/$mod/locale/fr_FR/LC_MESSAGES/$mod.po
    fi
done

