#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BrowseParc installer / updater for a Medulla MMC server.

This script runs ON the Medulla server (as root). The companion
deploy_browseparc.sh copies the staging tree and calls it.

    patch_remote.py install  --stage /root/browseparc-stage
    patch_remote.py rollback [--backup /root/browseparc-backup-YYYYmmdd-HHMMSS]
    patch_remote.py verify

install records the backup it took in STATE_FILE; rollback without --backup
restores that one (the staging tree is not needed). verify exits non-zero as
soon as one check fails.

Everything is idempotent: the PHP/python files are patched between explicit
markers, so running install twice does not duplicate anything.
"""

import argparse
import configparser
import glob
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

MMC_WEB = "/usr/share/mmc"
ADMIN_MODULE = os.path.join(MMC_WEB, "modules", "admin")
INFO_PACKAGE = os.path.join(ADMIN_MODULE, "infoPackage.inc.php")
LOCAL_SIDEBAR = os.path.join(ADMIN_MODULE, "admin", "localSidebar.php")
PLUGIN_DIR = "/usr/lib/python3/dist-packages/mmc/plugins/admin"
PLUGIN_INIT = os.path.join(PLUGIN_DIR, "__init__.py")
# Languages shipped with the page: the file locale/browseparc_<short>.po is
# merged into the matching Medulla locale, exactly like the other admin strings.
LANGUAGES = {"en": "en_US", "fr": "fr_FR", "es": "es_ES"}
ADMIN_MO = os.path.join(ADMIN_MODULE, "locale", "fr_FR", "LC_MESSAGES", "admin.mo")
# Small state kept between runs: the last backup taken (so rollback works
# without the staging tree) and the python module version the running
# mmc-agent was last restarted with.
STATE_FILE = "/root/.browseparc-state.json"
BACKUP_PREFIX = "/root/browseparc-backup-"


def admin_mo(locale):
    return os.path.join(ADMIN_MODULE, "locale", locale, "LC_MESSAGES", "admin.mo")


def all_admin_mo():
    """Every admin.mo of the Medulla web module (fr_FR, es_ES, ...), plus the
    known ones, so that each catalogue we may rewrite is backed up."""
    found = glob.glob(os.path.join(ADMIN_MODULE, "locale", "*", "LC_MESSAGES", "admin.mo"))
    found.extend(admin_mo(locale) for locale in LANGUAGES.values())
    return sorted(set(found))
DEPLOY_SCRIPT = "/usr/sbin/medulla-deploy-agent.sh"
SMB_HELPER = "/usr/sbin/medulla-deploy-agent-smb.py"

MARK_INFO = "// --- BrowseParc (Parcourir mon parc) ---"
MARK_SIDEBAR = "// --- BrowseParc (Parcourir mon parc) ---"
MARK_PYTHON = "# --- BrowseParc (Parcourir mon parc) ---"

INFO_BLOCK = """
// --- BrowseParc (Parcourir mon parc) ---
$page = new Page("browseparc", _T("Browse my fleet", "admin"));
$page->setFile("modules/admin/admin/browseparc.php");
$submod->addPage($page);

$page = new Page("browseparcAjax", _T("Browse my fleet", "admin"));
$page->setFile("modules/admin/admin/browseparcAjax.php");
$page->setOptions(array("AJAX" => true, "visible" => false));
$submod->addPage($page);
// --- end BrowseParc ---
"""

SIDEBAR_BLOCK = """
// --- BrowseParc (Parcourir mon parc) ---
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Browse my fleet", "admin"), "admin", "admin", "browseparc")
);
// --- end BrowseParc ---
"""

PYTHON_BLOCK = """
# --- BrowseParc (Parcourir mon parc) ---
# Fleet discovery and agent deployment helpers exposed to the web interface.
# Kept in a dedicated module so the plugin file itself barely changes.
try:
    from mmc.plugins.admin.browseparc import *  # noqa: F401,F403
except Exception as _browseparc_error:  # pragma: no cover
    import logging as _browseparc_logging
    _browseparc_logging.getLogger().error(
        "browseparc: cannot load the module: %s", _browseparc_error)
# --- end BrowseParc ---
"""

# staging relative path -> (destination, mode)
FILES = [
    ("medulla-deploy-agent.sh", DEPLOY_SCRIPT, 0o755),
    ("medulla-deploy-agent-smb.py", SMB_HELPER, 0o755),
    ("browseparc.py", os.path.join(PLUGIN_DIR, "browseparc.py"), 0o644),
    ("web/browseparc.php", os.path.join(ADMIN_MODULE, "admin", "browseparc.php"), 0o644),
    ("web/browseparcAjax.php", os.path.join(ADMIN_MODULE, "admin", "browseparcAjax.php"), 0o644),
    ("web/browseparc_common.php", os.path.join(ADMIN_MODULE, "admin", "browseparc_common.php"), 0o644),
    ("web/browseparc.js", os.path.join(ADMIN_MODULE, "graph", "js", "browseparc.js"), 0o644),
    ("web/browseparc.css", os.path.join(ADMIN_MODULE, "graph", "css", "browseparc.css"), 0o644),
]

PATCHED_FILES = [INFO_PACKAGE, LOCAL_SIDEBAR, PLUGIN_INIT]

ACL_FEATURE_KEY = "admin_fleet_discovery"


def run(cmd, check=True):
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as exc:  # command not installed
        if check:
            raise RuntimeError("cannot run %s: %s" % (" ".join(cmd), exc))
        return 127, str(exc)
    output = proc.stdout.decode("utf-8", "replace")
    if check and proc.returncode != 0:
        raise RuntimeError("command failed (%s): %s\n%s" % (proc.returncode, " ".join(cmd), output))
    return proc.returncode, output


def file_sha(path):
    """SHA-256 of a file, or None when it does not exist."""
    try:
        with open(path, "rb") as handle:
            return hashlib.sha256(handle.read()).hexdigest()
    except OSError:
        return None


def read_file(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def apply_meta(tmp, destination, mode=None, uid=None, gid=None):
    """Give the temporary file the mode/owner of the file it replaces.

    An explicit mode (or uid/gid) wins; otherwise the existing destination's
    are kept, so patching a root:www-data 0640 file does not turn it into a
    root:root 0644 one.
    """
    try:
        current = os.stat(destination)
    except OSError:
        current = None
    if current is not None:
        if mode is None:
            mode = stat.S_IMODE(current.st_mode)
        if uid is None:
            uid, gid = current.st_uid, current.st_gid
    if uid is not None and gid is not None:
        try:
            os.chown(tmp, uid, gid)
        except (OSError, AttributeError):
            pass  # not root (tests) or unsupported platform
    if mode is not None:
        os.chmod(tmp, mode)  # after chown, which may clear special bits


def write_file(path, text, mode=None):
    """Atomic write: a concurrent request must never read a truncated file."""
    tmp = "%s.bp-tmp-%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    apply_meta(tmp, path, mode)
    os.replace(tmp, path)


def copy_file_atomic(source, destination, mode=None, uid=None, gid=None):
    """Same for a binary copy: os.replace keeps readers on the old inode."""
    tmp = "%s.bp-tmp-%d" % (destination, os.getpid())
    shutil.copyfile(source, tmp)
    apply_meta(tmp, destination, mode, uid, gid)
    os.replace(tmp, destination)


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(**values):
    state = load_state()
    state.update(values)
    write_file(STATE_FILE, json.dumps(state, indent=2), 0o600)


# ---------------------------------------------------------------------------
# Database configuration (admin plugin)
# ---------------------------------------------------------------------------

def database_config():
    conf = {}
    base = "/etc/mmc/plugins/admin.ini"
    local = "/etc/mmc/plugins/admin.ini.local"
    for path in (base, local):
        if not os.path.isfile(path):
            continue
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read(path)
        except configparser.Error as exc:
            raise RuntimeError("cannot read %s: %s" % (path, exc))
        if parser.has_section("database"):
            for key in ("dbhost", "dbport", "dbuser", "dbpasswd", "dbname"):
                if parser.has_option("database", key):
                    conf[key] = parser.get("database", key)
    conf.setdefault("dbhost", "localhost")
    conf.setdefault("dbuser", "mmc")
    conf.setdefault("dbpasswd", "")
    conf.setdefault("dbname", "admin")
    return conf


def mysql_option(value):
    """Quote a value for a MySQL option file (passwords may hold # ; \\ or ")."""
    value = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return '"%s"' % value


def mysql_run(sql, database=None):
    conf = database_config()
    handle, defaults = tempfile.mkstemp(prefix="browseparc-mysql-")
    os.close(handle)
    os.chmod(defaults, 0o600)
    try:
        with open(defaults, "w", encoding="utf-8") as config:
            config.write("[client]\n")
            config.write("host=%s\n" % mysql_option(conf["dbhost"]))
            if conf.get("dbport"):
                config.write("port=%s\n" % mysql_option(conf["dbport"]))
            config.write("user=%s\n" % mysql_option(conf["dbuser"]))
            config.write("password=%s\n" % mysql_option(conf["dbpasswd"]))
        cmd = ["mysql", "--defaults-file=%s" % defaults]
        if database:
            cmd.append(database)
        proc = subprocess.run(cmd, input=sql.encode("utf-8"),
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.returncode, proc.stdout.decode("utf-8", "replace")
    finally:
        if os.path.exists(defaults):
            os.remove(defaults)


def apply_acl():
    """Register the ACL feature the page relies on.

    The table gained a NOT NULL ``install_types`` column in Medulla 5.6.5: it is
    detected rather than assumed, so the same deployment works on 5.5.x and on
    5.6.x. The feature works whatever the installation type, hence both values.
    """
    conf = database_config()
    columns = ["feature_key", "label", "description", "category",
               "superadmin_only", "acl_entry", "access_type"]
    values = ["'%s'" % ACL_FEATURE_KEY,
              "'Decouverte et deploiement de l''agent (parc)'",
              "'Parcourir mon parc : decouverte reseau / Active Directory et "
              "installation de l''agent'",
              "'admin'", "0", "'admin#admin#browseparc'", "'rw'"]

    code, output = mysql_run(
        "SHOW COLUMNS FROM acl_feature_definitions LIKE 'install_types';", conf["dbname"])
    if code == 0 and "install_types" in output:
        columns.append("install_types")
        values.append("'onpremise,saas'")

    # One transaction: a failing INSERT must not leave the feature deleted (the
    # mysql client stops at the first error and closes the session, which rolls
    # the transaction back).
    sql = (
        "START TRANSACTION;\n"
        "DELETE FROM acl_feature_definitions WHERE feature_key = '%s';\n"
        "INSERT INTO acl_feature_definitions (%s) VALUES (%s);\n"
        "COMMIT;\n"
        % (ACL_FEATURE_KEY, ", ".join(columns), ", ".join(values))
    )
    code, output = mysql_run(sql, conf["dbname"])
    if code != 0:
        raise RuntimeError("cannot write the ACL entries: %s" % output)
    return output.strip()


def remove_acl():
    conf = database_config()
    sql = "DELETE FROM acl_feature_definitions WHERE feature_key = '%s';\n" % ACL_FEATURE_KEY
    mysql_run(sql, conf["dbname"])


# ---------------------------------------------------------------------------
# Backup / restore
# ---------------------------------------------------------------------------

def backup(backup_dir, targets):
    os.makedirs(backup_dir, mode=0o700, exist_ok=True)
    manifest = {}
    for index, path in enumerate(targets):
        entry = {"path": path, "existed": os.path.exists(path)}
        if entry["existed"]:
            info = os.stat(path)
            entry.update(mode=stat.S_IMODE(info.st_mode), uid=info.st_uid, gid=info.st_gid)
            name = "%02d-%s" % (index, os.path.basename(path))
            shutil.copy2(path, os.path.join(backup_dir, name))
            entry["backup"] = name
        manifest[path] = entry
    with open(os.path.join(backup_dir, "manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    return manifest


# ---------------------------------------------------------------------------
# Text patches
# ---------------------------------------------------------------------------

def patch_info_package():
    text = read_file(INFO_PACKAGE)
    if MARK_INFO in text:
        return "already patched"
    anchor = "$mod->addSubmod($submod);"
    if anchor not in text:
        raise RuntimeError("cannot find the anchor %r in %s" % (anchor, INFO_PACKAGE))
    text = text.replace(anchor, INFO_BLOCK + "\n" + anchor, 1)
    write_file(INFO_PACKAGE, text)
    return "patched"


def patch_local_sidebar():
    text = read_file(LOCAL_SIDEBAR)
    if MARK_SIDEBAR in text:
        return "already patched"
    if not text.endswith("\n"):
        text += "\n"
    write_file(LOCAL_SIDEBAR, text + SIDEBAR_BLOCK)
    return "patched"


def patch_plugin_init():
    text = read_file(PLUGIN_INIT)
    if MARK_PYTHON in text:
        return "already patched"
    if not text.endswith("\n"):
        text += "\n"
    write_file(PLUGIN_INIT, text + PYTHON_BLOCK)
    return "patched"


# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------

def count_entries(path):
    code, output = run(["msgunfmt", path], check=False)
    return len([line for line in output.splitlines() if line.startswith("msgid ")])


def php_fpm_units():
    """php-fpm units present on this host (whatever the PHP version)."""
    code, output = run(["/bin/systemctl", "list-units", "php*-fpm.service",
                        "--no-legend", "--plain", "--no-pager"], check=False)
    units = []
    if code == 0:
        for line in output.splitlines():
            fields = line.split()
            if fields and fields[0].endswith(".service"):
                units.append(fields[0][:-len(".service")])
    return units


def reload_php_fpm():
    """Make a changed catalogue visible.

    PHP keeps the gettext catalogues in memory, per php-fpm worker: once a
    worker has loaded admin.mo it keeps serving it, so a freshly merged
    translation is invisible until the workers are recycled. A graceful reload
    lets every worker finish its current request first.
    """
    reloaded = []
    for unit in php_fpm_units():
        code, output = run(["/bin/systemctl", "reload", unit], check=False)
        if code == 0:
            reloaded.append(unit)
    if reloaded:
        return "%s reloaded (catalogues gettext rechargees)" % ", ".join(reloaded)
    # discovery found nothing usable: well known unit names
    for unit in ("php8.2-fpm", "php8.1-fpm", "php8.0-fpm", "php-fpm"):
        code, output = run(["/bin/systemctl", "reload", unit], check=False)
        if code == 0:
            return "%s reloaded (catalogues gettext rechargees)" % unit
    return "ATTENTION: php-fpm non recharge, les traductions peuvent rester en cache"


def strip_po_header(text):
    """Remove the header entry (msgid "") of a .po file.

    The project fragments carry their own header; it must not replace the
    header (charset, plural forms...) of the Medulla catalogue they are merged
    into.
    """
    blocks = re.split(r"\n[ \t]*\n", text)
    kept = []
    for block in blocks:
        lines = block.split("\n")
        is_header = any(
            line == 'msgid ""' and index + 1 < len(lines) and lines[index + 1].startswith("msgstr")
            for index, line in enumerate(lines))
        if not is_header:
            kept.append(block)
    return "\n\n".join(kept).strip("\n") + "\n"


def po_header(text):
    """The header entry (msgid "") of a .po file, or "" when there is none."""
    for block in re.split(r"\n[ \t]*\n", text):
        lines = block.split("\n")
        if any(line == 'msgid ""' and index + 1 < len(lines)
               and lines[index + 1].startswith("msgstr")
               for index, line in enumerate(lines)):
            return block.strip("\n") + "\n"
    return ""


def msgcat_command(fragment, existing, merged):
    """msgcat --use-first keeps the FIRST file's msgstr on a conflict: the
    project fragment goes first so that updated translations win, while the
    msgids it does not define stay as Medulla has them."""
    return ["msgcat", "--use-first", fragment, existing, "-o", merged]


def install_translations(stage):
    """Merge every available language into the matching Medulla catalogue.

    Always returns (report, changed): report is a human readable string,
    changed is True when at least one catalogue really differs, which is what
    requires a php-fpm reload.
    """
    for tool in ("msgunfmt", "msgcat", "msgfmt"):
        if not shutil.which(tool):
            return "%s is missing, translations skipped" % tool, False

    reports = []
    changed = False
    for short, locale in sorted(LANGUAGES.items()):
        fragment = os.path.join(stage, "locale", "browseparc_%s.po" % short)
        if not os.path.isfile(fragment):
            continue
        target = admin_mo(locale)
        if not os.path.isfile(target):
            if short == "en":
                reports.append("%s: English is the source language, nothing to merge" % locale)
            else:
                reports.append("%s: no admin.mo, skipped" % locale)
            continue

        before = count_entries(target)
        workdir = tempfile.mkdtemp(prefix="browseparc-i18n-")
        try:
            existing = os.path.join(workdir, "existing.po")
            run(["msgunfmt", target, "-o", existing])
            fragment_body = os.path.join(workdir, "fragment.po")
            # msgcat wants a header (charset) in every input: give the fragment
            # the header of the Medulla catalogue it is merged into.
            write_file(fragment_body,
                       po_header(read_file(existing)) + "\n" +
                       strip_po_header(read_file(fragment)))
            merged = os.path.join(workdir, "merged.po")
            run(msgcat_command(fragment_body, existing, merged))
            new_mo = os.path.join(workdir, "admin.mo")
            run(["msgfmt", "--check-format", "-o", new_mo, merged])
            after = count_entries(new_mo)
            if after < before:
                raise RuntimeError(
                    "the merged %s translation would lose entries (%d -> %d), aborting"
                    % (locale, before, after))
            # Atomic replace: glibc gettext mmaps this file, an in-place rewrite
            # would crash the php-fpm workers reading it concurrently.
            if file_sha(new_mo) != file_sha(target):
                changed = True
            copy_file_atomic(new_mo, target)
            reports.append("%s: %d entries (%d before)" % (locale, after, before))
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    return ("; ".join(reports) or "no translation file in the staging area"), changed


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def restart_services():
    messages = []
    code, output = run(["/bin/systemctl", "restart", "mmc-agent"], check=False)
    messages.append("mmc-agent restart: %s" % ("ok" if code == 0 else output.strip()))
    time.sleep(2)
    code, output = run(["/bin/systemctl", "is-active", "mmc-agent"], check=False)
    messages.append("mmc-agent: %s" % output.strip())
    if code != 0 or output.strip() != "active":
        raise RuntimeError("the mmc-agent is not running after the restart: %s" % output.strip())
    run(["/bin/systemctl", "reload", "apache2"], check=False)
    return messages


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def python_signature(paths):
    return dict((path, file_sha(path)) for path in paths)


def install(stage, restart=None):
    """Install / update. On any failure after the backup, everything is rolled
    back and a RuntimeError is raised (the exit code is then non-zero)."""
    report = {}
    for relative, destination, _ in FILES:
        source = os.path.join(stage, relative)
        if not os.path.isfile(source):
            raise RuntimeError("missing file in the staging area: %s" % source)

    # The php-fpm pool has very few workers (pm.max_children = 5 on the test
    # server) and the mmc-agent warms its plugins up lazily right after a
    # restart, which blocks its Twisted reactor: restarting it during working
    # hours makes the console answer 503. It is therefore only restarted when
    # the python plugin really changed.
    watched = [os.path.join(PLUGIN_DIR, "browseparc.py"), PLUGIN_INIT]
    before = python_signature(watched)

    backup_dir = "%s%s" % (BACKUP_PREFIX, time.strftime("%Y%m%d-%H%M%S"))
    targets = [destination for _, destination, _ in FILES] + PATCHED_FILES + all_admin_mo()
    manifest = backup(backup_dir, sorted(set(targets)))
    # Recorded at once so that rollback finds it even without the staging tree.
    save_state(last_backup=backup_dir)
    report["backup"] = backup_dir

    try:
        for relative, destination, mode in FILES:
            source = os.path.join(stage, relative)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            copy_file_atomic(source, destination, mode)
            report[destination] = "installed"

        report["infoPackage"] = patch_info_package()
        report["localSidebar"] = patch_local_sidebar()
        report["plugin"] = patch_plugin_init()
        report["acl"] = "updated"
        apply_acl()
        translations, catalogues_changed = install_translations(stage)
        report["translations"] = translations
        # A catalogue that changed is invisible until the php-fpm workers
        # recycle their in-memory copy.
        fpm_message = reload_php_fpm() if catalogues_changed else None

        after = python_signature(watched)
        # Changed now, or never loaded by the running agent (a previous run may
        # have installed the files and failed before the restart: the content
        # is then identical to the installed one but the agent still runs the
        # old code).
        python_changed = (before != after
                          or load_state().get("agent_signature") != after)
        report["python_changed"] = python_changed
        if restart is None:
            restart = python_changed
        if restart:
            report["services"] = restart_services()
            save_state(agent_signature=after)
        else:
            run(["/bin/systemctl", "reload", "apache2"], check=False)
            code, output = run(["/bin/systemctl", "is-active", "mmc-agent"], check=False)
            if output.strip() != "active":
                report["services"] = restart_services()
                save_state(agent_signature=after)
            else:
                report["services"] = [
                    "mmc-agent laisse en service (module python inchange) : aucun gel",
                    "mmc-agent: active",
                ]
        if fpm_message:
            report.setdefault("services", []).append(fpm_message)
        report["verify"] = verify()
        report["failures"] = verify_failures(report["verify"])
        report["backup_dir"] = backup_dir
        with open(os.path.join(backup_dir, "manifest.json"), "w", encoding="utf-8") as handle:
            json.dump({"files": manifest, "report": report}, handle, indent=2)
    except Exception as exc:
        try:
            rollback(backup_dir)
            outcome = "everything was rolled back from %s" % backup_dir
        except Exception as rollback_exc:
            outcome = "ROLLBACK FAILED too (%s), backup kept in %s" % (rollback_exc, backup_dir)
        raise RuntimeError("install failed: %s; %s" % (exc, outcome))
    return report


def latest_backup():
    """The backup recorded by the last install, else the newest one on disk."""
    recorded = load_state().get("last_backup")
    if recorded and os.path.isdir(recorded):
        return recorded
    found = sorted(glob.glob(BACKUP_PREFIX + "*/manifest.json"))
    return os.path.dirname(found[-1]) if found else None


def rollback(backup_dir=None):
    """Restore the files saved by an install (all of them: PHP, python, the
    deploy script, every admin.mo), remove those that did not exist before,
    unregister the ACL entry and restart the services."""
    backup_dir = backup_dir or latest_backup()
    if not backup_dir:
        raise RuntimeError("no backup found (%s*)" % BACKUP_PREFIX)
    manifest_path = os.path.join(backup_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        raise RuntimeError("no manifest in %s" % backup_dir)
    with open(manifest_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    manifest = payload.get("files", payload)
    report = {"backup": backup_dir}
    for path, entry in manifest.items():
        if entry.get("existed"):
            copy_file_atomic(os.path.join(backup_dir, entry["backup"]), path,
                             entry.get("mode"), entry.get("uid"), entry.get("gid"))
            report[path] = "restored"
        elif os.path.exists(path):
            os.remove(path)
            report[path] = "removed"
        else:
            report[path] = "nothing to do"
    try:
        remove_acl()
        report["acl"] = "removed"
    except Exception as exc:
        report["acl"] = "warning: %s" % exc
    # The restored catalogues must replace the ones php-fpm keeps in memory.
    report["php-fpm"] = reload_php_fpm()
    # The files are back to what they were: the agent must reload them.
    save_state(agent_signature=None)
    report["services"] = restart_services()
    return report


GOOD_VALUES = ("ok", "patched", "syntax ok", "active", "yes", "EXPOSED")


def verify_failures(checks):
    """Names of the checks that did not pass ("skipped ..." is not a failure)."""
    return sorted(key for key, value in checks.items()
                  if value not in GOOD_VALUES and not str(value).startswith("skipped"))


def verify():
    checks = {}
    for relative, destination, mode in FILES:
        checks["%s (present)" % destination] = "ok" if os.path.isfile(destination) else "MISSING"

    for path, marker in ((INFO_PACKAGE, MARK_INFO), (LOCAL_SIDEBAR, MARK_SIDEBAR),
                         (PLUGIN_INIT, MARK_PYTHON)):
        try:
            patched = marker in read_file(path)
        except OSError:
            patched = False
        checks["%s (patch)" % path] = "patched" if patched else "NOT PATCHED"

    # PHP syntax
    for name in ("browseparc.php", "browseparcAjax.php", "browseparc_common.php"):
        path = os.path.join(ADMIN_MODULE, "admin", name)
        code, output = run(["php", "-l", path], check=False)
        if code == 127:
            checks["%s (syntax)" % path] = "skipped (php CLI not found)"
        else:
            checks["%s (syntax)" % path] = "syntax ok" if code == 0 else "SYNTAX ERROR: %s" % output.strip()

    # Python syntax
    for path in (os.path.join(PLUGIN_DIR, "browseparc.py"), PLUGIN_INIT):
        code, output = run(["python3", "-c",
                            "compile(open(%r).read(), %r, 'exec')" % (path, path)], check=False)
        checks["%s (syntax)" % path] = "syntax ok" if code == 0 else "SYNTAX ERROR: %s" % output.strip()

    # The plugin namespace must expose every XMLRPC method of the module.
    probe = (
        "import sys; sys.path.insert(0, '/usr/lib/python3/dist-packages');"
        "import mmc.plugins.admin as admin;"
        "import mmc.plugins.admin.browseparc as bp;"
        "missing = [n for n in bp.__all__ if not hasattr(admin, n)];"
        "print('EXPOSED' if bp.__all__ and not missing else 'NOT EXPOSED: ' + ', '.join(missing))"
    )
    code, output = run(["python3", "-c", probe], check=False)
    checks["xmlrpc namespace"] = output.strip().splitlines()[-1] if output.strip() else "unknown"

    code, output = run(["/bin/systemctl", "is-active", "mmc-agent"], check=False)
    checks["mmc-agent"] = output.strip() or "unknown"

    script_ok = os.access(DEPLOY_SCRIPT, os.X_OK)
    checks["deploy script executable"] = "yes" if script_ok else "NO"

    code, output = run(["python3", SMB_HELPER, "--check"], check=False)
    checks["smb install (impacket)"] = "yes" if code == 0 else "skipped (optional: apt install python3-impacket)"

    return checks


def main():
    parser = argparse.ArgumentParser(description="BrowseParc Medulla installer")
    sub = parser.add_subparsers(dest="command", required=True)
    install_parser = sub.add_parser("install")
    install_parser.add_argument("--stage", required=True)
    install_parser.add_argument("--force-restart", action="store_true",
                                help="redemarrer mmc-agent meme si le module python est inchange")
    install_parser.add_argument("--no-restart", action="store_true",
                                help="ne jamais redemarrer mmc-agent")
    rollback_parser = sub.add_parser("rollback")
    rollback_parser.add_argument("--backup", default=None,
                                 help="dossier de sauvegarde (defaut : la derniere sauvegarde)")
    sub.add_parser("verify")
    args = parser.parse_args()

    try:
        if args.command == "install":
            restart = None
            if args.force_restart:
                restart = True
            elif args.no_restart:
                restart = False
            result = install(args.stage, restart=restart)
            failures = result.get("failures", [])
        elif args.command == "rollback":
            result = rollback(args.backup)
            failures = []
        else:
            result = verify()
            failures = verify_failures(result)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    if failures:
        print(json.dumps({"ok": False,
                          "error": "verification failed: %s" % ", ".join(failures),
                          "result": result}, indent=2))
        return 1
    print(json.dumps({"ok": True, "result": result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
