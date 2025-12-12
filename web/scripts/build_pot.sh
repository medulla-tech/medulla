#!/bin/bash

# build_pot.sh – Génère les fichiers .pot pour tous les modules Medulla
# Doit être lancé depuis le dossier web/
#
# Usage:
#   bash scripts/build_pot.sh           # Tous les modules
#   bash scripts/build_pot.sh admin     # Un seul module
#   bash scripts/build_pot.sh mobile    # Un seul module

set -e

[ ! -d modules ] && echo "Ce script doit être lancé depuis le dossier web/" && exit 1

all_modules=(
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
  mastering
  medulla_server
  mobile
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

# Si un paramètre est passé, on ne traite que ce module
if [[ -n "$1" ]]; then
  # Vérifier que le module existe dans la liste
  module_found=false
  for m in "${all_modules[@]}"; do
    if [[ "$m" == "$1" ]]; then
      module_found=true
      break
    fi
  done

  if [[ "$module_found" == false ]]; then
    echo "❌ Module '$1' non reconnu."
    echo "Modules disponibles: ${all_modules[*]}"
    exit 1
  fi

  modules=("$1")
  echo "📦 Extraction pour le module: $1"
else
  modules=("${all_modules[@]}")
  echo "📦 Extraction pour tous les modules (${#modules[@]})"
fi

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

  # Compter les strings extraites
  count=$(grep -c "^msgid " "$pot" 2>/dev/null || echo "0")
  echo "  ✅ $module: $count strings"
done

# Optional: cleaning of charsets in .Po if necessary
[ -x scripts/fix_po_charset.sh ] && sh scripts/fix_po_charset.sh

echo ""
echo "✅ Extraction terminée."
