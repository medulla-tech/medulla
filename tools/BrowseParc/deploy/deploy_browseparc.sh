#!/bin/bash
#
# Deploy the "Parcourir mon parc" feature on a Medulla server.
#
#   ./deploy_browseparc.sh deploy   [host] [--no-restart|--force-restart]
#   ./deploy_browseparc.sh verify   [host]   check an existing installation
#   ./deploy_browseparc.sh rollback [host] [backup_dir]
#   ./deploy_browseparc.sh status   [host]   what is deployed right now
#
# host defaults to gla (an ssh alias). Everything is backed up under
# /root/browseparc-backup-<timestamp> on the server before being replaced;
# rollback (without backup_dir) restores the last one, no staging tree needed.
# deploy/verify/status exit non-zero when a check fails.
#
set -euo pipefail

ACTION="${1:-}"
shift || true
RESTART_FLAG=""
POSITIONAL=()
for arg in "$@"; do
    case "$arg" in
        --no-restart)    RESTART_FLAG="--no-restart" ;;
        --force-restart) RESTART_FLAG="--force-restart" ;;
        *)               POSITIONAL+=("$arg") ;;
    esac
done
HOST="${POSITIONAL[0]:-gla}"
BACKUP_DIR="${POSITIONAL[1]:-}"

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STAGE_REMOTE="/root/browseparc-stage"
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'

usage() {
    sed -n '3,13p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
}

log()  { echo -e "${BLUE}==>${NC} $*"; }
ok()   { echo -e "${GREEN}ok${NC}  $*"; }
fail() { echo -e "${RED}ko${NC}  $*" >&2; exit 1; }

check_sources() {
    local missing=0
    for f in server/medulla-deploy-agent.sh \
             server/medulla-deploy-agent-smb.py \
             server/python/browseparc.py \
             web/browseparc.php \
             web/browseparcAjax.php \
             web/browseparc_common.php \
             web/browseparc.js \
             web/browseparc.css \
             locale/browseparc_en.po \
             locale/browseparc_fr.po \
             locale/browseparc_es.po \
             deploy/patch_remote.py; do
        if [ ! -f "$SRC_DIR/$f" ]; then
            echo "  missing: $f" >&2
            missing=1
        fi
    done
    [ "$missing" = "0" ] || fail "incomplete source tree in $SRC_DIR"
}

build_stage() {
    local stage="$1"
    rm -rf "$stage"
    mkdir -p "$stage/web" "$stage/locale"
    cp "$SRC_DIR/server/medulla-deploy-agent.sh" "$stage/medulla-deploy-agent.sh"
    cp "$SRC_DIR/server/medulla-deploy-agent-smb.py" "$stage/medulla-deploy-agent-smb.py"
    cp "$SRC_DIR/server/python/browseparc.py"    "$stage/browseparc.py"
    cp "$SRC_DIR/web/browseparc.php"             "$stage/web/"
    cp "$SRC_DIR/web/browseparcAjax.php"         "$stage/web/"
    cp "$SRC_DIR/web/browseparc_common.php"      "$stage/web/"
    cp "$SRC_DIR/web/browseparc.js"              "$stage/web/"
    cp "$SRC_DIR/web/browseparc.css"             "$stage/web/"
    cp "$SRC_DIR/locale/browseparc_en.po"        "$stage/locale/"
    cp "$SRC_DIR/locale/browseparc_fr.po"        "$stage/locale/"
    cp "$SRC_DIR/locale/browseparc_es.po"        "$stage/locale/"
    cp "$SRC_DIR/deploy/patch_remote.py"         "$stage/"
    # test helpers, used by the automated checks on the server
    mkdir -p "$stage/tests"
    cp "$SRC_DIR/tests/"*.py "$stage/tests/" 2>/dev/null || true
    [ -d "$SRC_DIR/tests/fake_impacket" ] && cp -R "$SRC_DIR/tests/fake_impacket" "$stage/tests/"
    cp "$SRC_DIR/tests/bp_render_test.php" "$stage/tests/" 2>/dev/null || true
    cp "$SRC_DIR/tests/test_ui_on_server.sh" "$stage/tests/" 2>/dev/null || true
    chmod +x "$stage/tests/test_ui_on_server.sh" 2>/dev/null || true
    # diagnostique : sondes guacd / RDP / XMLRPC utilisees en cas d'incident
    mkdir -p "$stage/tools"
    cp "$SRC_DIR/tools/"*.py "$stage/tools/" 2>/dev/null || true
}

remote() { ssh -o BatchMode=yes "$HOST" "$@"; }

# Run patch_remote.py on the server straight from stdin: works whether or not
# the staging tree is still there.
remote_patch() { remote "python3 - $*" < "$SRC_DIR/deploy/patch_remote.py"; }

# Print the JSON report of patch_remote.py ($1 = file); exit status 1 when it
# says the operation failed.
print_report() {
    python3 - "$1" <<'PY'
import json, sys
try:
    payload = json.load(open(sys.argv[1]))
except Exception as exc:
    print("cannot read the report: %s" % exc); sys.exit(1)
result = payload.get("result") or {}
if not payload.get("ok"):
    print("FAILED: %s" % payload.get("error"))
if isinstance(result, dict) and "backup_dir" in result:
    print("backup      : %s" % result.get("backup_dir"))
    print("translations: %s" % result.get("translations"))
    for line in result.get("services", []):
        print("service     : %s" % line)
checks = result.get("verify", result) if isinstance(result, dict) else {}
if isinstance(checks, dict) and checks and "backup_dir" not in checks:
    print("verification:")
    for key, value in sorted(checks.items()):
        print("  %-60s %s" % (key.split("/")[-1], value))
sys.exit(0 if payload.get("ok") else 1)
PY
}

case "$ACTION" in
    deploy)
        check_sources
        STAGE_LOCAL="$(mktemp -d "${TMPDIR:-/tmp}/browseparc-stage.XXXXXX")"
        REPORT="$(mktemp "${TMPDIR:-/tmp}/browseparc-report.XXXXXX")"
        trap 'rm -rf "$STAGE_LOCAL" "$REPORT"' EXIT
        log "building the staging tree"
        build_stage "$STAGE_LOCAL"

        log "copying to $HOST:$STAGE_REMOTE"
        remote "rm -rf '$STAGE_REMOTE' && mkdir -p '$STAGE_REMOTE'"
        scp -q -o BatchMode=yes -r "$STAGE_LOCAL"/. "$HOST:$STAGE_REMOTE/"

        log "installing (backup, patches, ACL, translations, services)"
        # patch_remote.py prints its JSON report even when it fails (exit 1):
        # keep the status instead of letting tee hide it.
        if remote "python3 '$STAGE_REMOTE/patch_remote.py' install --stage '$STAGE_REMOTE' ${RESTART_FLAG:-}" > "$REPORT"; then
            INSTALL_RC=0
        else
            INSTALL_RC=$?
        fi

        echo
        log "report"
        if print_report "$REPORT"; then REPORT_RC=0; else REPORT_RC=$?; fi
        echo
        if [ "$INSTALL_RC" -ne 0 ] || [ "$REPORT_RC" -ne 0 ]; then
            BACKUP_USED="$(sed -n 's/.*"backup_dir": "\([^"]*\)".*/\1/p' "$REPORT" | head -n1)"
            echo -e "${RED}The files stay installed on $HOST.${NC} To go back to the previous version:" >&2
            echo "  ./deploy_browseparc.sh rollback $HOST${BACKUP_USED:+   # restores $BACKUP_USED}" >&2
            fail "deployment failed on $HOST (details above)"
        fi
        ok "deployed on $HOST - open the Admin tab, menu 'Parcourir mon parc'"
        ;;

    verify)
        log "verifying the installation on $HOST"
        REPORT="$(mktemp "${TMPDIR:-/tmp}/browseparc-report.XXXXXX")"
        trap 'rm -f "$REPORT"' EXIT
        if remote_patch verify > "$REPORT"; then VERIFY_RC=0; else VERIFY_RC=$?; fi
        print_report "$REPORT" || VERIFY_RC=1
        if [ "$VERIFY_RC" -ne 0 ]; then
            echo "  to go back to the last backup: ./deploy_browseparc.sh rollback $HOST" >&2
            fail "verification failed"
        fi
        ok "installation verified on $HOST"
        ;;

    rollback)
        log "rolling back on $HOST"
        ROLLBACK_ARGS="rollback"
        if [ -n "$BACKUP_DIR" ]; then
            log "using backup $BACKUP_DIR"
            ROLLBACK_ARGS="rollback --backup '$BACKUP_DIR'"
        else
            log "using the last backup recorded on the server"
        fi
        REPORT="$(mktemp "${TMPDIR:-/tmp}/browseparc-report.XXXXXX")"
        trap 'rm -f "$REPORT"' EXIT
        if remote_patch "$ROLLBACK_ARGS" > "$REPORT"; then RB_RC=0; else RB_RC=$?; fi
        cat "$REPORT"
        [ "$RB_RC" -eq 0 ] || fail "rollback failed"
        ok "rolled back"
        ;;

    status)
        REPORT="$(mktemp "${TMPDIR:-/tmp}/browseparc-report.XXXXXX")"
        trap 'rm -f "$REPORT"' EXIT
        if remote_patch verify > "$REPORT"; then ST_RC=0; else ST_RC=$?; fi
        print_report "$REPORT" || ST_RC=1
        exit "$ST_RC"
        ;;

    *)
        usage
        ;;
esac
