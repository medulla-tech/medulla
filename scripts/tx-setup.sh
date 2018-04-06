#!/bin/bash

# This script maps PO and POT files to transifex ressources
# on https://transifex.mandriva.com

SCRIPT_DIR=`pwd`

which tx > /dev/null
if [ $? -ne 0 ]; then
	echo "Install the transifex client v0.4 (pip install transifex-client==0.4)"
	exit 1
fi

test -d .tx || tx init --host=https://fr.transifex.com/

pulse_modules="dyngroup glpi imaging inventory msc pkgs pulse2 backuppc update support"

dir=`pwd`

cd $SCRIPT_DIR/../web
bash scripts/build_pot.sh
cd $dir

for mod in $pulse_modules
do
	tx set --execute --auto-local -r pulse.$mod -s en -f $SCRIPT_DIR/../web/modules/$mod/locale/$mod.pot "pulse/web/modules/$mod/locale/<lang>/LC_MESSAGES/$mod.po"
done

echo ""
echo "Setup complete. You can now push/pull translations from transifex for the following ressources:"
for mod in $pulse_modules; do echo "- pulse.$mod"; done

echo ""
echo "See help.transifex.net/features/client/index.html for details."
