#!/bin/bash

# Script to prepare the translation environment with Transifex Cli (Go)
# To be launched at the project root

SCRIPT_DIR=$(pwd)

which tx > /dev/null
if [ $? -ne 0 ]; then
  echo "Install the new Customer Transifex CLI (https://github.com/transifex/cli/releases)"
  exit 1
fi

#InitTransifexLocalSiBesoin
test -d .tx || tx init

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

# Generation of .pot (translation sources)
cd "$SCRIPT_DIR/web"
bash scripts/build_pot.sh
cd "$SCRIPT_DIR"

TX_CONFIG=".tx/config"

echo "[main]" > "$TX_CONFIG"
echo "host = https://app.transifex.com" >> "$TX_CONFIG"
echo "" >> "$TX_CONFIG"

for mod in "${modules[@]}"
do
  echo "[o:medulla:p:medulla:r:$mod]" >> "$TX_CONFIG"
  echo "file_filter = web/modules/$mod/locale/<lang>/LC_MESSAGES/$mod.po" >> "$TX_CONFIG"
  echo "source_file = web/modules/$mod/locale/$mod.pot" >> "$TX_CONFIG"
  echo "source_lang = en" >> "$TX_CONFIG"
  echo "type = PO" >> "$TX_CONFIG"
  echo "" >> "$TX_CONFIG"
done

echo "Modules configurés :"
for mod in "${modules[@]}"; do
  echo "- medulla.$mod"
done
echo ""
echo "Voir la doc officielle : https://developers.transifex.com/docs/cli"