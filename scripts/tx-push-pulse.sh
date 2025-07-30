#!/bin/bash

which tx > /dev/null
if [ $? -ne 0 ]; then
    echo "Install the Transifex client CLI (https://github.com/transifex/cli/releases)"
    exit 1
fi

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
    tx --token "$TOKEN_API" push --source --translation -r o:medulla:p:medulla:r:$mod
done