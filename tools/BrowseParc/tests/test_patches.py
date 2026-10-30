#!/usr/bin/env python3
"""Unit tests for the in-place patches done by deploy/patch_remote.py.

The reference files are the ones actually deployed on the target server
(reference/gla/), so the anchors are validated against the real code.
The install / rollback / translation logic is exercised on temporary
directories, with the system commands (msgcat, systemctl, mysql...) faked.
"""
import os
import shutil
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "deploy"))

import patch_remote  # noqa: E402

REFERENCE = os.path.join(HERE, "..", "reference", "gla")
FAILURES = []
CHECKS = [0]

# Every XMLRPC method the plugin glue (browseparc.__all__) must expose.
EXPECTED_METHODS = (
    "browse_parc_start", "browse_parc_status", "browse_parc_cancel",
    "browse_parc_jobs", "browse_parc_prerequisites", "browse_parc_groups_list",
    "browse_parc_group_get", "browse_parc_group_save", "browse_parc_group_delete",
    "browse_parc_agents", "browse_parc_session", "browse_parc_machine_log",
)


def check(label, condition, detail=""):
    CHECKS[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s %s" % (label, detail))
        FAILURES.append(label)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


# --- fakes for the translation tests -----------------------------------------
# A fake ".mo" is simply the .po text: enough to exercise the merge logic
# without the gettext tools (not installed on a development machine).

def po_blocks(text):
    blocks = {}
    for block in text.strip("\n").split("\n\n"):
        for line in block.split("\n"):
            if line.startswith("msgid "):
                blocks.setdefault(line, block)
                break
    return blocks


def fake_run(cmd, check=True):
    tool = cmd[0]
    if tool == "msgunfmt":
        text = read(cmd[1])
        if "-o" in cmd:
            write(cmd[cmd.index("-o") + 1], text)
            return 0, ""
        return 0, text
    if tool == "msgcat":
        assert cmd[1] == "--use-first"
        merged = {}
        for source in cmd[2:cmd.index("-o")]:
            for key, block in po_blocks(read(source)).items():
                merged.setdefault(key, block)  # --use-first: the first file wins
        write(cmd[cmd.index("-o") + 1], "\n\n".join(merged.values()) + "\n")
        return 0, ""
    if tool == "msgfmt":
        shutil.copyfile(cmd[-1], cmd[cmd.index("-o") + 1])
        return 0, ""
    raise AssertionError("unexpected command %r" % (cmd,))


EXISTING_PO = (
    'msgid ""\nmsgstr ""\n"Project-Id-Version: medulla\\n"\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
    'msgid "Browse my fleet"\nmsgstr "ANCIEN TEXTE"\n\n'
    'msgid "Other string"\nmsgstr "Autre chaine"\n'
)
FRAGMENT_PO = (
    '# fragment header comment\nmsgid ""\nmsgstr ""\n"Project-Id-Version: browseparc\\n"\n'
    '"Language: fr_FR\\n"\n\n'
    'msgid "Browse my fleet"\nmsgstr "NOUVEAU TEXTE"\n\n'
    'msgid "Brand new key"\nmsgstr "Cle nouvelle"\n'
)


def main():
    workdir = tempfile.mkdtemp(prefix="browseparc-patch-")
    info_package = os.path.join(workdir, "infoPackage.inc.php")
    sidebar = os.path.join(workdir, "localSidebar.php")
    plugin_init = os.path.join(workdir, "__init__.py")

    shutil.copy(os.path.join(REFERENCE, "infoPackage.inc.php"), info_package)
    shutil.copy(os.path.join(REFERENCE, "localSidebar.php"), sidebar)
    shutil.copy(os.path.join(REFERENCE, "admin_plugin__init__.py"), plugin_init)

    patch_remote.INFO_PACKAGE = info_package
    patch_remote.LOCAL_SIDEBAR = sidebar
    patch_remote.PLUGIN_INIT = plugin_init

    print("\n1. Patch de infoPackage.inc.php")
    original = open(info_package).read()
    check("ancre unique avant patch", original.count("$mod->addSubmod($submod);") == 1)
    result = patch_remote.patch_info_package()
    check("patch appliqué", result == "patched", result)
    text = open(info_package).read()
    check("marqueur présent", patch_remote.MARK_INFO in text)
    check("page browseparc déclarée", '"browseparc"' in text)
    check("page ajax déclarée", '"browseparcAjax"' in text)
    check("option AJAX posée", 'array("AJAX" => true, "visible" => false)' in text)
    check("addSubmod toujours unique", text.count("$mod->addSubmod($submod);") == 1)
    check("idempotent", patch_remote.patch_info_package() == "already patched")
    check("pas de doublon de page", text.count('"browseparc"') == 1, text.count('"browseparc"'))

    print("\n2. Patch de localSidebar.php")
    result = patch_remote.patch_local_sidebar()
    check("patch appliqué", result == "patched", result)
    text = open(sidebar).read()
    check("marqueur présent", patch_remote.MARK_SIDEBAR in text)
    check("entrée de menu ajoutée", '"admin", "admin", "browseparc"' in text)
    check("idempotent", patch_remote.patch_local_sidebar() == "already patched")

    print("\n3. Patch du plugin python")
    result = patch_remote.patch_plugin_init()
    check("patch appliqué", result == "patched", result)
    text = open(plugin_init).read()
    check("marqueur présent", patch_remote.MARK_PYTHON in text)
    check("import ajouté", "from mmc.plugins.admin.browseparc import *" in text)
    check("idempotent", patch_remote.patch_plugin_init() == "already patched")
    try:
        compile(text, plugin_init, "exec")
        compiled = True
        detail = ""
    except SyntaxError as exc:
        compiled = False
        detail = str(exc)
    check("le fichier patché compile", compiled, detail)

    print("\n4. Le bloc d'import protège le démarrage de l'agent")
    check("import protégé par try/except", "except Exception as _browseparc_error" in text)
    check("erreur journalisée", "_browseparc_logging" in text)

    print("\n5. Le module browseparc expose bien l'API attendue")
    module = os.path.join(HERE, "..", "server", "python", "browseparc.py")
    namespace = {}
    exec(compile(open(module).read(), module, "exec"), namespace)
    exported = namespace.get("__all__", [])
    for name in EXPECTED_METHODS:
        check("exposé: %s" % name, name in exported)
        check("appelable: %s" % name, callable(namespace.get(name)))
    check("exactement %d méthodes exposées" % len(EXPECTED_METHODS),
          sorted(exported) == sorted(EXPECTED_METHODS),
          sorted(set(exported) ^ set(EXPECTED_METHODS)))
    check("__all__ cohérent", all(callable(namespace.get(n)) for n in exported))

    print("\n6. Le script de déploiement embarque les bons fichiers")
    deploy = open(os.path.join(HERE, "..", "deploy", "deploy_browseparc.sh")).read()
    for item in ("browseparc_es.po", "browseparcAjax.php", "browseparc_common.php",
                 "browseparc.js", "browseparc.css", "browseparc_fr.po", "patch_remote.py"):
        check("staging contient %s" % item, item in deploy)
    check("--force-restart accepté", "--force-restart" in deploy)
    check("--no-restart accepté", "--no-restart" in deploy)
    check("rapport dans un fichier mktemp", "/tmp/browseparc-deploy-report.json" not in deploy)

    print("\n7. Fusion des traductions : le texte du projet l'emporte")
    original_run, original_which = patch_remote.run, patch_remote.shutil.which
    original_module = patch_remote.ADMIN_MODULE
    try:
        patch_remote.ADMIN_MODULE = os.path.join(workdir, "mmc", "modules", "admin")
        patch_remote.run = fake_run
        patch_remote.shutil.which = lambda tool: "/usr/bin/%s" % tool
        fr_mo = patch_remote.admin_mo("fr_FR")
        write(fr_mo, EXISTING_PO)
        stage = os.path.join(workdir, "stage")
        write(os.path.join(stage, "locale", "browseparc_fr.po"), FRAGMENT_PO)

        check("l'en-tête du fragment est retiré",
              "browseparc" not in patch_remote.strip_po_header(FRAGMENT_PO)
              and "Cle nouvelle" in patch_remote.strip_po_header(FRAGMENT_PO))
        check("un msgid multi-ligne n'est pas pris pour l'en-tête",
              "Multi" in patch_remote.strip_po_header('msgid ""\n"Multi"\nmsgstr "x"\n'))
        header = patch_remote.po_header(EXISTING_PO)
        check("l'en-tête du catalogue existant est récupéré (charset exigé par msgcat)",
              "charset" in header.lower() and header.startswith("msgid"), header[:60])
        check("po_header: rien si pas d'en-tête", patch_remote.po_header('msgid "a"\nmsgstr "b"\n') == "")
        cmd = patch_remote.msgcat_command("frag.po", "old.po", "out.po")
        check("msgcat: le fragment du projet est listé AVANT l'existant",
              cmd.index("frag.po") < cmd.index("old.po") and "--use-first" in cmd, cmd)

        outcome = patch_remote.install_translations(stage)
        check("install_translations renvoie (rapport, changed)",
              isinstance(outcome, tuple) and len(outcome) == 2
              and isinstance(outcome[0], str) and isinstance(outcome[1], bool), outcome)
        merged = read(fr_mo)
        check("la traduction mise à jour est celle du projet",
              'msgstr "NOUVEAU TEXTE"' in merged and "ANCIEN TEXTE" not in merged)
        check("un msgid nouveau est ajouté", 'msgstr "Cle nouvelle"' in merged)
        check("un msgid absent du projet reste inchangé", 'msgstr "Autre chaine"' in merged)
        check("l'en-tête de Medulla est conservé",
              "charset=UTF-8" in merged and "Project-Id-Version: medulla" in merged
              and "Project-Id-Version: browseparc" not in merged)
        check("catalogue modifié => changed", outcome[1] is True)
        again = patch_remote.install_translations(stage)
        check("second passage: plus de changement", again[1] is False, again)

        patch_remote.shutil.which = lambda tool: None
        missing = patch_remote.install_translations(stage)
        check("outils absents: même type de retour (rapport, False)",
              isinstance(missing, tuple) and len(missing) == 2 and missing[1] is False, missing)
    finally:
        patch_remote.run, patch_remote.shutil.which = original_run, original_which
        patch_remote.ADMIN_MODULE = original_module

    print("\n8. Sauvegarde et rollback de tous les admin.mo, modes conservés")
    originals = dict((name, getattr(patch_remote, name)) for name in (
        "ADMIN_MODULE", "STATE_FILE", "BACKUP_PREFIX", "remove_acl",
        "reload_php_fpm", "restart_services"))
    try:
        patch_remote.ADMIN_MODULE = os.path.join(workdir, "mmc2", "modules", "admin")
        patch_remote.STATE_FILE = os.path.join(workdir, "state.json")
        patch_remote.BACKUP_PREFIX = os.path.join(workdir, "backup-")
        patch_remote.remove_acl = lambda: None
        patch_remote.reload_php_fpm = lambda: "reloaded"
        patch_remote.restart_services = lambda: ["restarted"]

        mo_fr, mo_es = patch_remote.admin_mo("fr_FR"), patch_remote.admin_mo("es_ES")
        mo_de = patch_remote.admin_mo("de_DE")  # a language the script does not ship
        for path in (mo_fr, mo_es, mo_de):
            write(path, "original %s" % path)
        check("tous les admin.mo sont sauvegardés",
              set([mo_fr, mo_es, mo_de]) <= set(patch_remote.all_admin_mo()))
        existing = os.path.join(workdir, "dest", "existing.php")
        created = os.path.join(workdir, "dest", "created.php")
        write(existing, "original php")
        os.chmod(existing, 0o640)

        backup_dir = patch_remote.BACKUP_PREFIX + "20240101-000000"
        patch_remote.backup(backup_dir, sorted(patch_remote.all_admin_mo() + [existing, created]))
        for path in (mo_fr, mo_es, mo_de, existing):
            write(path, "CHANGED")
        os.chmod(existing, 0o600)
        write(created, "new file")
        patch_remote.save_state(last_backup=backup_dir)
        check("latest_backup lit l'état enregistré", patch_remote.latest_backup() == backup_dir)

        report = patch_remote.rollback()  # no argument, no staging tree
        check("rollback sans --backup rend un rapport", isinstance(report, dict), report)
        check("fr_FR restauré", read(mo_fr) == "original %s" % mo_fr)
        check("es_ES restauré", read(mo_es) == "original %s" % mo_es)
        check("autre langue restaurée", read(mo_de) == "original %s" % mo_de)
        check("fichier restauré", read(existing) == "original php")
        check("mode d'origine restauré",
              stat.S_IMODE(os.stat(existing).st_mode) == 0o640,
              oct(stat.S_IMODE(os.stat(existing).st_mode)))
        check("fichier créé par l'installation supprimé", not os.path.exists(created))
        check("write_file conserve le mode existant",
              (patch_remote.write_file(existing, "x"),
               stat.S_IMODE(os.stat(existing).st_mode))[1] == 0o640)
    finally:
        for name, value in originals.items():
            setattr(patch_remote, name, value)

    print("\n9. install : l'échec d'une étape déclenche le rollback")
    names = ("FILES", "PATCHED_FILES", "PLUGIN_DIR", "ADMIN_MODULE", "STATE_FILE",
             "BACKUP_PREFIX", "apply_acl", "remove_acl", "install_translations",
             "reload_php_fpm", "restart_services", "verify", "INFO_PACKAGE",
             "LOCAL_SIDEBAR", "PLUGIN_INIT", "run")
    originals = dict((name, getattr(patch_remote, name)) for name in names)
    try:
        root = os.path.join(workdir, "inst")
        stage = os.path.join(root, "stage")
        dest = os.path.join(root, "dest")
        patch_remote.PLUGIN_DIR = os.path.join(dest, "plugin")
        patch_remote.ADMIN_MODULE = os.path.join(dest, "admin")
        patch_remote.STATE_FILE = os.path.join(root, "state.json")
        patch_remote.BACKUP_PREFIX = os.path.join(root, "backup-")
        patch_remote.FILES = [("a.txt", os.path.join(dest, "a.txt"), 0o644)]
        write(os.path.join(stage, "a.txt"), "new a")
        write(os.path.join(dest, "a.txt"), "old a")
        php_info = os.path.join(dest, "infoPackage.inc.php")
        write(php_info, "<?php\n$mod->addSubmod($submod);\n")
        patch_remote.INFO_PACKAGE = php_info
        patch_remote.LOCAL_SIDEBAR = os.path.join(dest, "localSidebar.php")
        patch_remote.PLUGIN_INIT = os.path.join(dest, "plugin", "__init__.py")
        write(patch_remote.LOCAL_SIDEBAR, "<?php\n")
        write(patch_remote.PLUGIN_INIT, "# plugin\n")
        patch_remote.PATCHED_FILES = [php_info, patch_remote.LOCAL_SIDEBAR, patch_remote.PLUGIN_INIT]
        patch_remote.remove_acl = lambda: None
        patch_remote.reload_php_fpm = lambda: "reloaded"
        restarts = []
        patch_remote.restart_services = lambda: restarts.append(1) or ["restarted"]
        patch_remote.verify = lambda: {"mmc-agent": "active"}
        # never touch the real systemctl: every command "succeeds", agent active
        patch_remote.run = lambda cmd, check=True: (0, "active\n")
        def failing_acl():
            raise RuntimeError("mysql is down")
        patch_remote.apply_acl = failing_acl
        patch_remote.install_translations = lambda stage: ("no translation", False)

        raised = None
        try:
            patch_remote.install(stage, restart=False)
        except RuntimeError as exc:
            raised = str(exc)
        check("une étape en échec lève une erreur (code de sortie non nul)",
              raised is not None and "mysql is down" in raised and "rolled back" in raised, raised)
        check("fichier restauré après l'échec", read(os.path.join(dest, "a.txt")) == "old a")
        check("infoPackage restauré après l'échec", "BrowseParc" not in read(php_info))
        check("l'agent est redémarré par le rollback", len(restarts) == 1, restarts)

        patch_remote.apply_acl = lambda: ""
        restarts[:] = []
        result = patch_remote.install(stage, restart=False)
        check("installation réussie: fichier installé", read(os.path.join(dest, "a.txt")) == "new a")
        check("installation réussie: pas d'échec de vérification", result["failures"] == [], result)
        check("--no-restart respecté", restarts == [], restarts)
        restarts[:] = []
        patch_remote.install(stage, restart=True)
        check("--force-restart redémarre l'agent", len(restarts) == 1, restarts)
    finally:
        for name, value in originals.items():
            setattr(patch_remote, name, value)

    print("\n10. ACL transactionnelle, vérification et citation MySQL")
    original_mysql, original_conf = patch_remote.mysql_run, patch_remote.database_config
    sent = []

    def fake_mysql(sql, database=None):
        sent.append(sql)
        return 0, ""
    try:
        patch_remote.mysql_run = fake_mysql
        patch_remote.database_config = lambda: {"dbname": "admin"}
        patch_remote.apply_acl()
        sql = sent[-1]
        check("ACL: DELETE et INSERT dans une seule transaction",
              sql.startswith("START TRANSACTION;") and sql.rstrip().endswith("COMMIT;")
              and sql.index("DELETE") < sql.index("INSERT") < sql.index("COMMIT"), sql)
    finally:
        patch_remote.mysql_run, patch_remote.database_config = original_mysql, original_conf
    check("mot de passe cité pour le fichier d'options MySQL",
          patch_remote.mysql_option('p#ss"w\\d') == '"p#ss\\"w\\\\d"',
          patch_remote.mysql_option('p#ss"w\\d'))
    check("verify_failures: tout est ok", patch_remote.verify_failures(
        {"a": "ok", "b": "patched", "c": "syntax ok", "d": "active", "e": "skipped (php CLI not found)"}) == [])
    check("verify_failures: signale les échecs", patch_remote.verify_failures(
        {"a": "MISSING", "b": "active", "c": "NOT PATCHED", "d": "inactive"}) == ["a", "c", "d"])

    shutil.rmtree(workdir, ignore_errors=True)

    print("\n=====================================")
    print("%d vérifications, %d échec(s)" % (CHECKS[0], len(FAILURES)))
    if FAILURES:
        print("Échecs: %s" % ", ".join(FAILURES))
        return 1
    print("TOUS LES TESTS PASSENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
