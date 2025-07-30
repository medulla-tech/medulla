#!/bin/bash

# build_pot.sh – Génère les fichiers .pot pour tous les modules Medulla
# Doit être lancé depuis le dossier web/

set -e

[ ! -d modules ] && echo "Ce script doit être lancé depuis le dossier web/" && exit 1

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

for module in "${modules[@]}"; do
  pot="modules/$module/locale/$module.pot"
  fpath="modules/$module"
  keyword="_T"

  # Special case for the "Base" module
  if [[ "$module" == "base" ]]; then
    fpath="."
    keyword="_"
  fi

  mkdir -p "$(dirname "$pot")"
  rm -f "$pot"
  touch "$pot"

find "$fpath" -iname "*.php" -exec xgettext \
  --from-code=UTF-8 \
  --language=PHP \
  --keyword="$keyword" \
  --output="$pot" \
  --join-existing \
  {} +

done

# Optional: cleaning of charsets in .Po if necessary
[ -x scripts/fix_po_charset.sh ] && sh scripts/fix_po_charset.sh

echo "Tous les fichiers .pot ont été générés."