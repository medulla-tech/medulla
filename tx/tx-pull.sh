#!/bin/bash

which tx > /dev/null
if [ $? -ne 0 ]; then
    echo "Install the Transifex client CLI (https://github.com/transifex/cli/releases)"
    exit 1
fi

[ ! -z "$1" ] && lang="-l $1" && shift 1
args=$@

modules=(
  admin
  backuppc
  base
  dashboard
  dyngroup
  glpi
  guacamole
  imaging
  inventory
  kiosk
  medulla_server
  msc
  pkgs
  ppolicy
  report
  services
  support
  updates
  urbackup
  xmppmaster
)

TOKEN_API=""

for mod in "${modules[@]}"
do
    tx --token "$TOKEN_API" pull -r medulla.$mod -a -f $lang $args || echo "Resource $mod not found, we continue"

    if [ -d "web/modules/$mod/locale/fr/LC_MESSAGES" ]; then
        mkdir -p "web/modules/$mod/locale/fr_FR/LC_MESSAGES"
        cp -fv web/modules/$mod/locale/fr/LC_MESSAGES/* web/modules/$mod/locale/fr_FR/LC_MESSAGES/

        if [ -f "web/modules/$mod/locale/fr_FR/LC_MESSAGES/$mod.po" ]; then
            sed -i '' 's/Language: fr\\n/Language: fr_FR\\n/' "web/modules/$mod/locale/fr_FR/LC_MESSAGES/$mod.po"
        fi
    fi
done