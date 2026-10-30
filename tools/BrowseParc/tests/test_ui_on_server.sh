#!/bin/bash
#
# Automated checks of the "Parcourir mon parc" feature, run ON the Medulla
# server.
#
#   test_ui_on_server.sh <staging_dir>
#
# Environment (defaults match the original test server):
#   BP_TEST_HOST  Windows / domain controller host used for the AD check  (172.16.12.141)
#   BP_SSH_KEY    SSH private key given to --sshkey                       (/root/.ssh/id_rsa)
#   BP_BASE       web base URL used for static assets                     (http://127.0.0.1/mmc)
#   BP_BASE_TLS   TLS web base URL used by the php-fpm gettext probe      (https://127.0.0.1/mmc)
#
# The page and its AJAX endpoint are rendered with a minimal MMC bootstrap
# (bp_render_test.php) instead of a browser session: on an instance whose web
# login goes through OIDC/GLPI there is no way to obtain an MMC agent RPC
# session from a script, and every page including MMC's own fails the same way
# without it. The bootstrap only needs what the page really uses.
#
set -u

STAGE="${1:-/root/browseparc-stage}"
WEBROOT="/usr/share/mmc"
# Private scratch directory: nothing predictable in /tmp.
TMPD="$(mktemp -d "${TMPDIR:-/tmp}/bp-ui-test.XXXXXX")" || { echo "mktemp failed"; exit 1; }
HELPER="$TMPD/bp_render_test.php"
PROBE=""
cleanup() {
    [ -n "$PROBE" ] && rm -f "$PROBE"
    rm -rf "$TMPD"
}
trap cleanup EXIT
trap 'exit 130' INT TERM
TEST_HOST="${BP_TEST_HOST:-172.16.12.141}"
SSH_KEY="${BP_SSH_KEY:-/root/.ssh/id_rsa}"
# The web SAPI (php-fpm) runs with short_open_tag=On, the CLI defaults to Off.
PHP="php -d short_open_tag=1"
BASE="${BP_BASE:-http://127.0.0.1/mmc}"
BASE_TLS="${BP_BASE_TLS:-https://127.0.0.1/mmc}"
PASS=0
FAIL=0

ok()   { PASS=$((PASS + 1)); echo "  ok   $*"; }
ko()   { FAIL=$((FAIL + 1)); echo "  FAIL $*"; }
# check <label> <grep-exit-code> [detail]
check(){ if [ "$2" = "0" ]; then ok "$1"; else ko "$1 ${3:-}"; fi; }
# refute <label> <grep-exit-code> [detail]  (passes when the pattern is absent)
refute(){ if [ "$2" != "0" ]; then ok "$1"; else ko "$1 ${3:-}"; fi; }

HERE="$(cd "$(dirname "$0")" && pwd)"
RENDER_SRC="$HERE/bp_render_test.php"
[ -f "$RENDER_SRC" ] || RENDER_SRC="$STAGE/bp_render_test.php"
cp "$RENDER_SRC" "$HELPER" || { echo "cannot install $HELPER (from $RENDER_SRC)"; exit 1; }

echo "=== 1. Rendu de la page (onglet Admin)"
$PHP "$HELPER" render > "$TMPD/bp-render.html" 2> "$TMPD/bp-render.err"
check "la page se rend sans erreur fatale" $?
grep -q 'id="browseParc"' "$TMPD/bp-render.html"; check "conteneur de page present" $?
grep -q 'id="browseparc"' "$TMPD/bp-render.html"; check "entree de menu dans la sidebar de l'onglet Admin" $?
grep -q 'action=browseparc"' "$TMPD/bp-render.html"; check "lien du menu vers la nouvelle page" $?
grep -q 'browseparc.js' "$TMPD/bp-render.html"; check "script client reference" $?
grep -q 'browseparc.css' "$TMPD/bp-render.html"; check "feuille de style referencee" $?
grep -q 'id="bpDiscover"' "$TMPD/bp-render.html"; check "bouton de decouverte" $?
grep -q 'id="bpInstall"' "$TMPD/bp-render.html"; check "bouton d'installation" $?
grep -q 'id="bpMachinesTable"' "$TMPD/bp-render.html"; check "table des machines" $?
grep -q 'id="bpGroupsTable"' "$TMPD/bp-render.html"; check "table des groupes" $?
grep -q 'id="bpOuTree"' "$TMPD/bp-render.html"; check "arbre des OU present" $?
grep -q 'id="bpOuSelection"' "$TMPD/bp-render.html"; check "rappel de la branche selectionnee" $?
grep -qF 'Listez les OU pour choisir une branche' "$TMPD/bp-render.html"; check "invite de l'arbre traduite" $?
# L'ancien selecteur plat a disparu au profit de l'arbre.
grep -q '<select id="bpOu"' "$TMPD/bp-render.html"; refute "plus de selecteur plat" $?
grep -q 'id="bpJobsTable"' "$TMPD/bp-render.html"; check "table des taches" $?
grep -q 'id="bpAgent"' "$TMPD/bp-render.html"; check "selecteur d'agent de deploiement" $?
grep -q 'id="bpAgentInsecure"' "$TMPD/bp-render.html"; check "option certificat auto-signe" $?
grep -q 'Prise en main' "$TMPD/bp-render.html"; check "colonne prise en main" $?
grep -q 'Méthode' "$TMPD/bp-render.html"; check "colonne methode d'installation" $?

# Les titres de section ne doivent plus etre numerotes.
grep -qE '>[[:space:]]*[0-9]+\. (Decouvrir|Machines|Groupes|Taches)' "$TMPD/bp-render.html"
refute "aucun titre de section numerote" $?
grep -q 'Découvrir le parc' "$TMPD/bp-render.html"; check "titre decouvrir sans numero" $?
grep -q 'Tâches récentes' "$TMPD/bp-render.html"; check "titre taches sans numero" $?
grep -qE 'browseparc\.js\?v=[0-9]+' "$TMPD/bp-render.html"; check "anti-cache sur le script client" $?
grep -qE 'browseparc\.css\?v=[0-9]+' "$TMPD/bp-render.html"; check "anti-cache sur la feuille de style" $?
grep -qiE 'Fatal error|Parse error|Uncaught' "$TMPD/bp-render.err"; refute "aucune erreur PHP pendant le rendu" $?
grep -qi 'browseparc' "$TMPD/bp-render.err"; refute "aucun avertissement lie a browseparc" $?

echo
echo "=== 2. Traduction francaise appliquee"
for label in "Parcourir mon parc" "Découvrir le parc" "Machines trouvées" "Groupes d'installation agent" \
             "Tâches récentes" "Unité d'organisation" "Identifiant" "Installer l'agent sur la sélection"; do
    grep -qF "$label" "$TMPD/bp-render.html"; check "libelle: $label" $?
done

echo
echo "=== 2 bis. Traduction espagnole (comme le reste du module admin)"
BP_LANG=es_ES $PHP "$HELPER" render > "$TMPD/bp-render-es.html" 2>/dev/null
for label in "Explorar mi parque" "Descubrir el parque" "Máquinas encontradas" "Grupos de instalación del agente" \
             "Tareas recientes" "Unidad organizativa" "Usuario"; do
    grep -qF "$label" "$TMPD/bp-render-es.html"; check "espagnol: $label" $?
done
rm -f "$TMPD/bp-render-es.html"

echo
echo "=== 2 ter. Traduction servie par php-fpm (cache gettext)"
# PHP garde les catalogues gettext en memoire dans les processus php-fpm : un
# catalogue fraichement fusionne reste invisible tant que les workers n'ont pas
# ete recycles. Un test en CLI ne peut pas le voir, d'ou cette sonde HTTP.
PROBE_NAME="bp_i18n_check_$$.php"
PROBE="$WEBROOT/$PROBE_NAME"
cat > "$PROBE" <<'PHPEOF'
<?php
bindtextdomain("admin", "/usr/share/mmc/modules/admin/locale");
textdomain("admin");
foreach (array("fr_FR.UTF-8" => "fr", "es_ES.UTF-8" => "es") as $loc => $tag) {
    setlocale(LC_ALL, $loc);
    putenv("LANG=$loc");
    putenv("LC_ALL=$loc");
    foreach (array("Browse my fleet", "Discover the fleet", "Machines found",
                   "Agent installation groups", "Recent jobs") as $s) {
        echo $tag, "|", $s, "|", gettext($s), "\n";
    }
}
PHPEOF
OUT=$(curl -sk -m 20 "$BASE_TLS/$PROBE_NAME" 2>/dev/null)
rm -f "$PROBE"; PROBE=""
if [ -z "$OUT" ]; then
    check "sonde php-fpm joignable" 1
else
    check "sonde php-fpm joignable" 0
    echo "$OUT" | grep -q "fr|Discover the fleet|Découvrir le parc"; check "php-fpm: titre fr" $?
    echo "$OUT" | grep -q "fr|Machines found|Machines trouvées"; check "php-fpm: section fr" $?
    echo "$OUT" | grep -q "es|Discover the fleet|Descubrir el parque"; check "php-fpm: titre es" $?
    echo "$OUT" | grep -q "es|Recent jobs|Tareas recientes"; check "php-fpm: section es" $?
fi

echo
echo "=== 3. Endpoint AJAX"
OUT=$($PHP "$HELPER" ajax_unknown 2>/dev/null)
echo "$OUT" | grep -q '"ok":false'; check "reponse JSON pour une commande inconnue" $?
echo "$OUT" | grep -q 'Commande inconnue'; check "message traduit" $?
echo "$OUT" | grep -qi '<html\|Fatal error'; refute "aucune page HTML d'erreur" $?

OUT=$($PHP "$HELPER" ajax_guard 2>/dev/null)
echo "$OUT" | grep -q 'Accès refusé'; check "ACL: utilisateur sans droit refuse" $?

OUT=$($PHP "$HELPER" ajax_guard_allowed 2>/dev/null)
echo "$OUT" | grep -q 'Commande inconnue'; check "ACL: utilisateur avec droit autorise" $?

OUT=$($PHP "$HELPER" ajax_csrf 2>/dev/null)
# Une reponse JSON est exigee : une redirection ferait recevoir la page de
# connexion au navigateur, qui ne pourrait pas la lire (« HTTP 200 »).
echo "$OUT" | grep -q '"expired":true'; check "CSRF: POST sans jeton rejete en JSON" $?
echo "$OUT" | grep -q 'session MMC a expir'; check "CSRF: message d'expiration explicite" $?
echo "$OUT" | grep -qi '<html\|Location:'; refute "CSRF: aucune redirection ni page HTML" $?

echo
echo "=== 3 bis. Messages de l'agent MMC traduits"
OUT=$(BP_LANG=en_US $PHP "$HELPER" translate 2>/dev/null)
echo "$OUT" | grep -q "^Unknown job|Unknown job\$"; check "en_US: message en anglais" $?
for LANGTAG in fr_FR es_ES; do
    OUT=$(BP_LANG=$LANGTAG $PHP "$HELPER" translate 2>/dev/null)
    case $LANGTAG in
        fr_FR) W1="Machine invalide"; W2="Tâche inconnue"; W3="Protocole non pris en charge : ssh2"; W4="impossible de open la connexion (HTTP 500)"; W5="préfixe /16" ;;
        es_ES) W1="Máquina no válida"; W2="Tarea desconocida"; W3="Protocolo no admitido: ssh2"; W4="no se puede open la conexión (HTTP 500)"; W5="prefijo /16" ;;
    esac
    echo "$OUT" | grep -q "^Invalid machine|$W1\$"; check "$LANGTAG: message simple" $?
    echo "$OUT" | grep -q "|$W2\$"; check "$LANGTAG: tache inconnue" $?
    echo "$OUT" | grep -q "|$W3\$"; check "$LANGTAG: message avec valeur" $?
    echo "$OUT" | grep -q "$W4"; check "$LANGTAG: message a deux valeurs" $?
    echo "$OUT" | grep -q "$W5"; check "$LANGTAG: nombre conserve" $?
    echo "$OUT" | grep -q "^Something nobody translated|Something nobody translated\$"; check "$LANGTAG: message inconnu inchange" $?
done

echo
echo "=== 4. Ressources statiques servies par Apache"
for asset in "modules/admin/graph/js/browseparc.js" "modules/admin/graph/css/browseparc.css"; do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 20 "$BASE/$asset")
    [ "$CODE" = "200" ]; check "HTTP 200 pour $asset" $? "(code $CODE)"
done

echo
echo "=== 5. Methodes XMLRPC exposees par le plugin admin"
python3 - <<'PY'
import sys
sys.path.insert(0, "/usr/lib/python3/dist-packages")
try:
    import mmc.plugins.admin as admin
except Exception as exc:
    print("  FAIL import du plugin admin: %s" % exc)
    sys.exit(1)
expected = ("browse_parc_start", "browse_parc_status", "browse_parc_cancel",
            "browse_parc_jobs", "browse_parc_prerequisites", "browse_parc_groups_list",
            "browse_parc_group_get", "browse_parc_group_save",
            "browse_parc_group_delete", "browse_parc_agents",
            "browse_parc_session")
missing = [name for name in expected if not hasattr(admin, name)]
if missing:
    print("  FAIL methodes absentes: %s" % ", ".join(missing))
    sys.exit(1)
print("  ok   %d methodes XMLRPC exposees" % len(expected))
PY
check "namespace du plugin complet" $?

echo
echo "=== 6. Script de deploiement"
/usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive 2>/dev/null \
    | python3 -c "
import json,sys
d = json.load(sys.stdin)
p = d['prerequisites']
print('  ok   prerequis:', ', '.join('%s=%s' % (k, v) for k, v in p.items()))
" 2>/dev/null
check "mode --check-prereq" $?

# Le mmc-agent est lance par systemd SANS HOME. PSWSMan etant installe dans le
# profil de root, pwsh ne le voyait plus : l'interface annoncait le module
# manquant alors qu'il etait present. Ce controle reproduit cet environnement.
OUT=$(env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin /usr/sbin/medulla-deploy-agent.sh \
      --check-prereq --json --non-interactive 2>/dev/null)
NO_HOME_WSMAN=$(echo "$OUT" | python3 -c "
import json, sys
print(json.load(sys.stdin)['prerequisites']['wsman'])
" 2>/dev/null)
[ "$NO_HOME_WSMAN" = "True" ]; check "PSWSMan detecte sans HOME (environnement du demon)" $? "wsman=$NO_HOME_WSMAN"

# Le parcours Active Directory ne doit plus s'arreter sur PSWSMan mais sur le
# compte manquant (preuve que le controle passe).
OUT=$(env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin /usr/sbin/medulla-deploy-agent.sh \
      --list-ous --server=$TEST_HOST --domain=MEDULLA --ou=DC=medulla,DC=lan \
      --json --non-interactive 2>/dev/null)
echo "$OUT" | grep -qi "PSWSMan is missing"; refute "AD: ne reclame plus PSWSMan" $?
echo "$OUT" | grep -qi "provide a domain account"; check "AD: demande le compte" $?

printf 'gla-w11-1\nmachine-inconnue-xyz\n' | /usr/sbin/medulla-deploy-agent.sh --uuid-lookup --json --non-interactive 2>/dev/null \
    | python3 -c "
import sys
lines = [l.split('\t') for l in sys.stdin.read().splitlines() if l.strip()]
known = [l for l in lines if len(l) > 2 and l[2]]
print('  ok   %d machine(s) connue(s) resolue(s) sur %d' % (len(known), len(lines)))
" 2>/dev/null
check "mode --uuid-lookup" $?

echo
echo "=== 7. Decouverte reseau reelle (boucle locale)"
# Toute recherche exige un compte : on en fournit un factice par variable
# d'environnement (le mot de passe ne doit jamais apparaitre en argument).
export BROWSE_PARC_PASSWORD="MotDePasseDeTest"
CREDS="--username=compte-de-test --password-env=BROWSE_PARC_PASSWORD"
OUT=$(/usr/sbin/medulla-deploy-agent.sh --target=127.0.0.1/32 --port=22 --discover --json \
      $CREDS --skip-ps-setup --non-interactive 2>/dev/null)
echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print('  ok   JSON valide, %d machine(s)' % d['total'])" 2>/dev/null
check "decouverte d'une machine locale" $?

# L'OS doit etre identifie : le serveur lui-meme tourne sous Debian et expose SSH.
echo "$OUT" | python3 -c "
import json, sys
machines = json.load(sys.stdin)['machines']
assert machines, 'aucune machine'
osys = machines[0].get('os') or ''
print('  ok   OS identifie : %s' % osys)
assert osys and osys != 'Unknown', 'OS non identifie : %r' % osys
" 2>/dev/null
check "l'OS de la machine locale est identifie" $?
echo "$OUT" | grep -q '"os":' ; check "le champ os est present dans le JSON" $?

# Le script d'origine demandait --min-hostgroup 512 : nmap avertit alors
# "highly aggressive --min-hostgroup" et peut masquer des machines lentes.
ERR=$(/usr/sbin/medulla-deploy-agent.sh --target=127.0.0.1/32 --discover --json \
      $CREDS --skip-ps-setup --non-interactive 2>&1 >/dev/null)
echo "$ERR" | grep -qi "aggressive"; refute "aucun avertissement nmap agressif" $?

# L'option reste disponible pour les tres grands reseaux.
OUT=$(/usr/sbin/medulla-deploy-agent.sh --target=127.0.0.1/32 --discover --json \
      $CREDS --min-hostgroup=256 --skip-ps-setup --non-interactive 2>/dev/null)
echo "$OUT" | grep -q '"total":1'; check "option --min-hostgroup acceptee" $?

echo
echo "=== 8. Toute recherche exige un compte"
OUT=$(env -u BROWSE_PARC_PASSWORD /usr/sbin/medulla-deploy-agent.sh --target=127.0.0.1/32 \
      --discover --json --skip-ps-setup --non-interactive 2>&1)
echo "$OUT" | grep -qi "login and a password"; check "decouverte reseau refusee sans compte" $?
OUT=$(/usr/sbin/medulla-deploy-agent.sh --target=127.0.0.1/32 --discover --json \
      --username=compte-de-test --skip-ps-setup --non-interactive 2>&1)
echo "$OUT" | grep -qi "login and a password"; check "refusee avec un identifiant sans mot de passe" $?
OUT=$(/usr/sbin/medulla-deploy-agent.sh --target=127.0.0.1/32 --discover --json \
      $CREDS --skip-ps-setup --non-interactive 2>/dev/null)
echo "$OUT" | grep -q '"total"'; check "acceptee avec un compte" $?
# Une cle SSH remplace le couple identifiant/mot de passe.
OUT=$(/usr/sbin/medulla-deploy-agent.sh --target=127.0.0.1/32 --discover --json \
      --username=compte-de-test --sshkey="$SSH_KEY" --skip-ps-setup --non-interactive 2>&1)
# Pas d'erreur d'identifiants ET une decouverte effectivement produite (le
# script est alle au bout) : une autre erreur ne doit pas faire passer le test.
echo "$OUT" | grep -qi "login and a password"; refute "la cle SSH remplace le mot de passe" $?
echo "$OUT" | grep -q '"total"'; check "la decouverte avec cle SSH produit un resultat" $?
# Les controles qui ne touchent aucune machine restent sans compte.
OUT=$(env -u BROWSE_PARC_PASSWORD /usr/sbin/medulla-deploy-agent.sh --check-prereq --json --non-interactive 2>/dev/null)
echo "$OUT" | grep -q '"status"'; check "--check-prereq reste sans compte" $?

echo
echo "====================================="
echo "$PASS verifications OK, $FAIL echec(s)"
[ "$FAIL" = "0" ] || exit 1
exit 0
