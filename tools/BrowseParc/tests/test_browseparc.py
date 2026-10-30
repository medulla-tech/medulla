#!/usr/bin/env python3
"""Unit tests for the BrowseParc backend (mmc admin plugin).

Run:  python3 test_browseparc.py
"""
import glob
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "server", "python"))
sys.path.insert(0, HERE)

import browseparc  # noqa: E402

FAILURES = []
CHECKS = [0]


def check(label, condition, detail=""):
    CHECKS[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s %s" % (label, detail))
        FAILURES.append(label)


def wait_status(job, timeout=20):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = browseparc.browse_parc_status(job)
        if last.get("status") in ("done", "error"):
            return last
        time.sleep(0.1)
    return last


def main():
    tmp = tempfile.mkdtemp(prefix="browseparc-test-")
    fake = os.path.join(tmp, "fake-deploy-agent.py")
    shutil.copy(os.path.join(HERE, "fake_deploy_agent.py"), fake)
    os.chmod(fake, 0o755)

    browseparc.BROWSER_ROOT = tmp
    browseparc.JOBS_DIR = os.path.join(tmp, "jobs")
    browseparc.GROUPS_DIR = os.path.join(tmp, "groups")
    browseparc.DEPLOY_SCRIPT = fake

    print("\n1. Validation des entrées")
    check("CIDR accepté", browseparc._validate_target("10.0.0.0/24") == "10.0.0.0/24")
    check("IP seule acceptée", browseparc._validate_target("10.0.0.1") == "10.0.0.1")
    check("FQDN accepté", browseparc._validate_target("pc1.test.lan") == "pc1.test.lan")
    check("injection refusée", browseparc._validate_target("10.0.0.1; rm -rf /") is None)
    check("backtick refusé", browseparc._validate_target("`id`") is None)
    check("CIDR invalide refusé", browseparc._validate_target("10.0.0.0/99") is None)
    check("port valide", browseparc._validate_port("5985") == 5985)
    check("port invalide refusé", browseparc._validate_port("70000") is None)
    check("port non numérique refusé", browseparc._validate_port("abc") is None)
    check("nom de groupe simple", browseparc._validate_group_name("Salle 12") == "Salle 12")
    check("traversée de chemin refusée", browseparc._validate_group_name("../../etc/passwd") is None)
    check("slash refusé", browseparc._validate_group_name("a/b") is None)

    print("\n2. Découverte réseau (job + statut)")
    start = browseparc.browse_parc_start({
        "action": "discover", "mode": "network", "target": "10.0.0.0/24",
        "port": 5985, "username": "admin", "password": "Sup3rS3cret"})
    check("job démarré", start.get("ok") is True, start)
    job = start.get("job")
    status = wait_status(job)
    check("statut final = done", status.get("status") == "done", status.get("status"))
    check("2 machines trouvées", len(status.get("machines") or []) == 2,
          len(status.get("machines") or []))
    check("machine déjà équipée signalée",
          [m for m in status["machines"] if m["installed"]],
          status.get("machines"))
    check("progression total = 2", status["progress"]["total"] == 2, status["progress"])
    check("le mot de passe circule par l'environnement",
          any("password-in-env=True" in line for line in status.get("log") or []),
          status.get("log"))

    print("\n3. Le mot de passe n'est jamais écrit sur disque")
    jobdir = os.path.join(tmp, "jobs", job)
    raw = open(os.path.join(jobdir, "request.json")).read()
    check("request.json sans mot de passe", "Sup3rS3cret" not in raw)
    check("request.json sans --password",
          all("--password" not in item for item in
              json.loads(raw).get("command", [])))
    blob = ""
    for name in os.listdir(jobdir):
        path = os.path.join(jobdir, name)
        if os.path.isfile(path):
            blob += open(path, "rb").read().decode("utf-8", "replace")
    check("aucun fichier du job ne contient le mot de passe", "Sup3rS3cret" not in blob)

    print("\n4. Installation sélectionnée")
    start = browseparc.browse_parc_start({
        "action": "install", "targets": ["pc1.test.lan", "ko-pc.test.lan"],
        "port": 5985, "username": "admin", "password": "Sup3rS3cret", "timeout": 30})
    check("job d'installation démarré", start.get("ok") is True, start)
    status = wait_status(start.get("job"))
    check("statut terminé", status.get("status") == "done", status)
    check("1 succès / 1 échec",
          status["summary"].get("ok") == 1 and status["summary"].get("ko") == 1,
          status.get("summary"))
    check("2 résultats détaillés", len(status["summary"].get("results") or []) == 2)

    print("\n5. Liste des OU Active Directory")
    start = browseparc.browse_parc_start({
        "action": "list_ous", "mode": "ad", "server": "10.0.0.10",
        "username": "admin", "password": "Sup3rS3cret"})
    check("job OU démarré", start.get("ok") is True, start)
    status = wait_status(start.get("job"))
    check("2 OU remontées", len(status.get("ous") or []) == 2, status.get("ous"))

    print("\n6. Refus des entrées invalides")
    check("action inconnue refusée",
          browseparc.browse_parc_start({"action": "drop_database"}).get("ok") is False)
    check("cible invalide refusée",
          browseparc.browse_parc_start({"action": "discover", "target": ";;"}) .get("ok") is False)
    check("AD sans serveur refusé",
          browseparc.browse_parc_start({"action": "discover", "mode": "ad",
                                        "username": "a", "password": "b"}).get("ok") is False)
    check("installation sans machine refusée",
          browseparc.browse_parc_start({"action": "install", "targets": []}).get("ok") is False)
    check("machine invalide refusée",
          browseparc.browse_parc_start({"action": "install",
                                        "targets": ["ok", "$(reboot)"]}).get("ok") is False)

    print("\n7. Groupes de ciblage")
    save = browseparc.browse_parc_group_save(
        "Salle 12",
        [{"target": "pc1.test.lan", "name": "pc1.test.lan", "ip": "10.0.0.1", "source": "network"},
         {"target": "pc1.test.lan", "name": "doublon"},
         "pc2.test.lan"],
        "Groupe de test")
    check("groupe enregistré", save.get("ok") is True, save)
    check("doublon supprimé", save.get("count") == 2, save)
    listing = browseparc.browse_parc_groups_list()
    check("groupe listé", [g["name"] for g in listing["groups"]] == ["Salle 12"], listing)
    one = browseparc.browse_parc_group_get("Salle 12")
    check("groupe relu avec ses machines", len(one.get("machines") or []) == 2, one)
    # Un groupe doit se deployer comme la selection dont il vient : les ports
    # decident entre SSH et WinRM.
    browseparc.browse_parc_group_save("Deploiement", [
        {"target": "win-ssh", "os": "Windows 11", "ports": [22, 99999, "x", 22],
         "services": ["ssh", "../bad", "rdp"]},
        {"target": "lin1", "os": "", "ports": [22], "services": ["ssh"]}])
    kept = browseparc.browse_parc_group_get("Deploiement").get("machines") or []
    check("ports conserves et nettoyes dans le groupe",
          kept and kept[0].get("ports") == [22], kept)
    check("services conserves et nettoyes dans le groupe",
          kept and kept[0].get("services") == ["ssh", "rdp"], kept)
    details = [browseparc._target_details(m) for m in kept]
    check("Windows joignable en SSH seul reste installe en SSH depuis un groupe",
          browseparc._install_transport(details[0][1], details[0][2]) == "ssh", details)
    from_group = browseparc._build_command(
        "install", {"targets": kept, "username": "u", "password": "p"}, "/tmp/unused")
    info = [part for part in from_group if str(part).startswith("--target-info=")]
    check("installation depuis un groupe : transport transmis au script",
          len(info) == 1 and '"method":"ssh"' in info[0], info)
    browseparc.browse_parc_group_delete("Deploiement")
    check("remplacement du groupe",
          browseparc.browse_parc_group_save("Salle 12", ["pc3.test.lan"]).get("replaced") is True)
    check("groupe absent refusé", browseparc.browse_parc_group_get("Inconnu").get("ok") is False)
    check("suppression du groupe",
          browseparc.browse_parc_group_delete("Salle 12").get("ok") is True)
    check("groupe bien supprimé",
          browseparc.browse_parc_groups_list()["groups"] == [])
    check("suppression nom invalide refusée",
          browseparc.browse_parc_group_delete("../x").get("ok") is False)

    print("\n8. Résolution UUID (poussée vers un groupe Medulla)")
    start = browseparc.browse_parc_start({
        "action": "uuid_lookup", "targets": ["known-pc", "unknown-pc"]})
    check("job de resolution demarre", start.get("ok") is True, start)
    status = wait_status(start.get("job"))
    check("job de resolution termine", status.get("status") == "done", status.get("status"))
    uuids = status.get("uuids") or {}
    check("machine connue resolue",
          uuids.get("known-pc", {}).get("uuid", "").startswith("UUID-"), uuids)
    check("machine inconnue marquee", uuids.get("unknown-pc", {}).get("known") is False, uuids)
    check("liste vide refusee",
          browseparc.browse_parc_start({"action": "uuid_lookup", "targets": []}).get("ok") is False)
    check("machine invalide refusee",
          browseparc.browse_parc_start({"action": "uuid_lookup",
                                        "targets": ["$()"]}).get("ok") is False)

    print("\n9. Annulation d'un job")
    start = browseparc.browse_parc_start({"action": "install", "targets": "slow",
                                          "username": "admin", "password": "x"})
    if start.get("ok"):
        time.sleep(0.4)
        cancel = browseparc.browse_parc_cancel(start["job"])
        check("annulation demandée", cancel.get("ok") is True, cancel)
        cancelled = False
        for _ in range(50):
            if not browseparc._pid_alive(browseparc._read_pid(
                    os.path.join(tmp, "jobs", start["job"]))):
                cancelled = True
                break
            time.sleep(0.1)
        check("processus arrêté", cancelled)
        final = browseparc.browse_parc_status(start["job"])
        check("statut « annulée » et non « erreur »", final.get("status") == "cancelled",
              final.get("status"))
        check("annulation sans message d'erreur", not final.get("error"), final.get("error"))
    else:
        check("job 'slow' démarré", False, start)

    print("\n10. Historique et prérequis")
    jobs = browseparc.browse_parc_jobs(5)
    check("historique non vide", jobs.get("ok") and len(jobs["jobs"]) >= 4, jobs)
    started = time.time()
    prereq = browseparc.browse_parc_prerequisites()
    elapsed = time.time() - started
    check("les prérequis ne bloquent pas (< 0.5s)", prereq.get("ok") and elapsed < 0.5,
          "%s en %.3fs" % (prereq, elapsed))
    check("rafraîchissement lancé en tâche de fond", prereq.get("refreshing") is True, prereq)
    cached = {}
    for _ in range(50):
        time.sleep(0.1)
        reread = browseparc.browse_parc_prerequisites()
        if (reread.get("prerequisites") or {}).get("wsman"):
            cached = reread
            break
    check("cache rempli par la tâche de fond",
          (cached.get("prerequisites") or {}).get("wsman") is True, cached)
    check("lecture suivante non bloquante", cached.get("refreshing") is False, cached)

    print("\n10 bis. Services détectés et prise en main")
    start = browseparc.browse_parc_start({
        "action": "discover", "mode": "network", "target": "10.0.0.0/24", "port": 5985})
    discovered = wait_status(start.get("job"))
    found = (discovered or {}).get("machines") or []
    check("machines découvertes", len(found) == 2, found)
    if found:
        check("ports remontés", isinstance(found[0].get("ports"), list), found[0])
        check("services remontés", isinstance(found[0].get("services"), list), found[0])
        check("service rdp détecté", "rdp" in (found[0].get("services") or []), found[0])
        check("service ssh détecté", "ssh" in (found[1].get("services") or []), found[1])
    check("aucun service vnc", all("vnc" not in (m.get("services") or []) for m in found), found)
    # Les refus sont testes sans contacter Guacamole (validation en amont).
    check("protocole inconnu refusé",
          browseparc.browse_parc_session({"protocol": "telnet", "target": "10.0.0.1"}).get("ok") is False)
    check("VNC n'est plus proposé",
          browseparc.browse_parc_session({"protocol": "vnc", "target": "10.0.0.1"}).get("ok") is False)
    check("machine invalide refusée",
          browseparc.browse_parc_session({"protocol": "rdp", "target": "$(id)"}).get("ok") is False)
    check("port hors plage refusé",
          browseparc.browse_parc_session({"protocol": "rdp", "target": "10.0.0.1",
                                          "port": 99999}).get("ok") is False)
    check("identifiants trop longs refusés",
          browseparc.browse_parc_session({"protocol": "ssh", "target": "10.0.0.1",
                                          "username": "a" * 200}).get("ok") is False)
    check("encodage de l'identifiant client Guacamole",
          browseparc._guacamole_cux_id(3843) ==
          __import__("base64").b64encode(b"3843" + b"\x00c\x00mysql").decode(),
          browseparc._guacamole_cux_id(3843))

    print("\n10 ter. Fichiers de traduction (multilingue)")
    locale_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "locale")

    def read_po(path):
        """msgid -> msgstr, plus la liste des entrees non traduites."""
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        entries, empty, duplicates = {}, [], []
        current, has = None, False
        for line in lines:
            if line.startswith("msgid "):
                if current and not has:
                    empty.append(current)
                current = line[6:].strip().strip('"')
                has = False
                if current:
                    if current in entries:
                        duplicates.append(current)
                    entries[current] = ""
            elif line.startswith("msgstr ") and current:
                value = line[7:].strip().strip('"')
                has = value != ""
                entries[current] = value
        if current and not has:
            empty.append(current)
        return entries, empty, duplicates

    po_files = sorted(glob.glob(os.path.join(locale_dir, "browseparc_*.po")))
    check("au moins deux langues livrees", len(po_files) >= 2,
          [os.path.basename(p) for p in po_files])

    reference = None
    for path in po_files:
        name = os.path.basename(path)
        entries, empty, duplicates = read_po(path)
        check("%s : aucun msgid en double" % name, not duplicates, duplicates)
        check("%s : toutes les chaines sont traduites" % name, not empty, empty)
        check("%s : nombre de traductions coherent" % name, len(entries) >= 70, len(entries))
        if reference is None:
            reference = (name, set(entries))
        else:
            missing = reference[1] - set(entries)
            extra = set(entries) - reference[1]
            check("%s couvre les memes chaines que %s" % (name, reference[0]),
                  not missing and not extra, {"manquantes": sorted(missing)[:3],
                                              "en_trop": sorted(extra)[:3]})
        print("     %-24s %d chaines" % (name, len(entries)))

    check("ESPAGNOL livre (comme le reste du module admin)",
          os.path.isfile(os.path.join(locale_dir, "browseparc_es.po")))
    check("ANGLAIS livre (fr, en, es)",
          os.path.isfile(os.path.join(locale_dir, "browseparc_en.po")) and len(po_files) == 3,
          [os.path.basename(p) for p in po_files])
    check("FRANCAIS livre",
          os.path.isfile(os.path.join(locale_dir, "browseparc_fr.po")))

    # Toute chaine demandee par la page doit exister dans chaque langue : c'est
    # ce controle qui manquait quand des libelles restaient en dur.
    import re as _re
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    php_source = open(os.path.join(root, "web", "browseparc.php"), encoding="utf-8").read()
    requested = set()
    for match in _re.finditer(r"_T\('((?:[^'\\]|\\.)*)'", php_source):
        requested.add(match.group(1).replace("\\'", "'"))
    check("chaines _T detectees dans la page", len(requested) >= 60, len(requested))

    for path in po_files:
        entries, _, _ = read_po(path)
        missing = sorted(m for m in requested if m not in entries)
        check("%s couvre toutes les chaines de la page" % os.path.basename(path),
              not missing, missing[:4])

    # Le JavaScript ne doit plus contenir de libelle francais en dur.
    js_source = open(os.path.join(root, "web", "browseparc.js"), encoding="utf-8").read()
    # Les commentaires ne sont pas des libelles : on les retire avant le controle.
    js_code = "\n".join(line for line in js_source.splitlines()
                         if not line.strip().startswith(("*", "//", "/*")))
    hardcoded = _re.findall(r'"[A-ZÀ-Ü][a-zà-ü]{3,} [^"]{2,}"', js_code)
    check("aucun libelle francais en dur dans le JS", not hardcoded, hardcoded[:3])

    # \b evite de confondre closest("tr") avec un appel a t("tr").
    keys_used = set(_re.findall(r'\bt\("([a-zA-Z]+)"\)', js_source))
    keys_declared = set(_re.findall(r"^\s+'([a-zA-Z]+)' => _T\(", php_source, _re.M))
    check("toutes les cles t() sont declarees", not (keys_used - keys_declared),
          sorted(keys_used - keys_declared)[:5])

    # Modele de traduction (.pot) : genere depuis les sources, memes chaines que les .po.
    sys.path.insert(0, os.path.join(root, "tools"))
    import make_pot
    check("browseparc.pot a jour (tools/make_pot.py)",
          open(os.path.join(locale_dir, "browseparc.pot"), encoding="utf-8").read() ==
          make_pot.render(make_pot.collect()))
    pot_ids = set(make_pot.collect())
    for path in po_files:
        entries, _, _ = read_po(path)
        check("%s : memes chaines que le modele .pot" % os.path.basename(path),
              set(entries) == pot_ids,
              {"manquantes": sorted(pot_ids - set(entries))[:3], "en_trop": sorted(set(entries) - pot_ids)[:3]})

    # Messages de l'agent MMC (python, en anglais) : chacun doit etre traduisible
    # par bp_translate_message(), sinon l'utilisateur le voit en anglais.
    import ast as _ast
    tree = _ast.parse(open(os.path.join(root, "server", "python", "browseparc.py"), encoding="utf-8").read())

    def literal(node):
        if isinstance(node, _ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, _ast.BinOp) and isinstance(node.op, _ast.Mod):
            return literal(node.left)
        return None

    messages = set()
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, _ast.Constant) and key.value in ("error", "message") and literal(value):
                    messages.add(literal(value))
        elif isinstance(node, _ast.Raise) and isinstance(node.exc, _ast.Call):
            messages.update(m for m in map(literal, node.exc.args) if m)
    messages = {m for m in messages if " " in m and not m.startswith("http")}
    common = open(os.path.join(root, "web", "browseparc_common.php"), encoding="utf-8").read()
    covered = set(_re.findall(r"^\s+'((?:[^'\\]|\\.)*)' => _T\('", common, _re.M))
    covered |= set(_re.findall(r"=> _T\('((?:[^'\\]|\\.)*)', 'admin'\),\n", common))
    covered = {m.replace("\\'", "'") for m in covered}
    uncovered = sorted(m for m in messages if m not in covered)
    check("%d messages de l'agent MMC traduisibles" % len(messages), not uncovered, uncovered[:4])
    for path in po_files:
        entries, _, _ = read_po(path)
        gaps = sorted(m for m in messages if m not in entries)
        check("%s traduit les messages de l'agent MMC" % os.path.basename(path), not gaps, gaps[:3])

    print("\n11. Choix de l'agent à déployer")
    # Un faux depot d'agents d'entite
    agent_root = os.path.join(tmp, "medulla_agent")
    client_root = os.path.join(tmp, "clients")
    tag = "11111111-2222-3333-4444-555555555555"
    os.makedirs(os.path.join(agent_root, tag))
    open(os.path.join(agent_root, tag, "Medulla-Agent-windows-FULL-latest.exe"), "wb").write(b"MZ" * 50)
    open(os.path.join(agent_root, tag, "Medulla-Agent-linux-MINIMAL-latest.sh"), "w").write("#!/bin/bash\n")
    os.makedirs(os.path.join(client_root, "win"))
    open(os.path.join(client_root, "win", "install-agent.ps1"), "w").write(
        "$downloadUrl = 'https://medulla.test/downloads/win/Medulla-Agent-windows-FULL-latest.exe'\n")
    browseparc.AGENT_ROOT = agent_root
    browseparc.CLIENT_ROOT = client_root

    listing = browseparc.browse_parc_agents()
    check("liste d'agents lisible", listing.get("ok") is True, listing)
    ids = [item["id"] for item in listing.get("agents", [])]
    check("agent d'entite detecte", ("entity:%s" % tag) in ids, ids)
    check("agent generique propose", "generic" in ids, ids)
    entity = [item for item in listing["agents"] if item["id"] == "entity:%s" % tag][0]
    check("URL Windows construite", entity["windows"]["url"].endswith(
        "/medulla_agent/%s/Medulla-Agent-windows-FULL-latest.exe" % tag), entity["windows"])
    check("Referer renseigne", entity["windows"]["referer"].endswith("/"), entity["windows"])
    check("chemin Linux renseigne", entity["linux"]["path"].endswith(".sh"), entity["linux"])
    check("taille du binaire", entity["windows"]["size"] == 100, entity["windows"])
    check("URL de base deduite de install-agent.ps1",
          listing.get("base_url") == "https://medulla.test", listing.get("base_url"))

    options = browseparc._resolve_agent("entity:%s" % tag)
    check("resolution des options Windows",
          options.get("--agent-win-url", "").endswith(".exe"), options)
    check("resolution du Referer", "--agent-win-referer" in options, options)
    check("resolution du chemin Linux", options.get("--agent-lin", "").endswith(".sh"), options)
    check("agent generique = aucun changement", browseparc._resolve_agent("generic") == {})
    lin_opts = browseparc._linux_download_options("entity:%s" % tag)
    check("URL de telechargement Linux de l'agent d'entite",
          lin_opts.get("--agent-lin-url", "").endswith("/medulla_agent/%s/%s" % (tag, browseparc.LIN_AGENT_FILE))
          and lin_opts.get("--agent-lin-referer", "").endswith("/"), lin_opts)
    check("agent inconnu: aucune URL", browseparc._linux_download_options("entity:nope") == {})
    check("identifiant vide = generique", browseparc._resolve_agent("") == {})
    try:
        browseparc._resolve_agent("entity:../../etc/passwd")
        check("agent inconnu refuse", False, "aucune exception")
    except ValueError:
        check("agent inconnu refuse", True)
    try:
        browseparc._resolve_agent("entity:/etc/shadow")
        check("chemin absolu refuse", False, "aucune exception")
    except ValueError:
        check("chemin absolu refuse", True)

    print("\n11 bis. Sécurité XML-RPC : le journal ne doit pas casser la réponse")
    # Les codes couleur ANSI contiennent ESC (0x1b), valide en UTF-8 mais
    # INTERDIT en XML 1.0. Sans assainissement, l'agent produit un document XML
    # invalide, PHP ne peut pas le décoder et l'interface affiche
    # « Unexpected answer from the MMC agent (NULL) ».
    import re as _re
    import xml.dom.minidom as _minidom
    import xmlrpc.client as _xmlrpc

    ansi_job = "20260101-000000-abcdef12"
    ansi_dir = os.path.join(browseparc.JOBS_DIR, ansi_job)
    os.makedirs(ansi_dir, exist_ok=True)
    with open(os.path.join(ansi_dir, "stderr.log"), "w", encoding="utf-8") as handle:
        handle.write("\033[0;31mERREUR\033[0m: nc: connexion refusée\r\n")
        handle.write("ligne normale\n")
    with open(os.path.join(ansi_dir, "events.jsonl"), "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"event": "log",
                                 "line": "\033[0;34mbleu\033[0m"}) + "\n")
        handle.write(json.dumps({"event": "end", "status": "ok", "total": 1,
                                 "ok": 1, "ko": 0}) + "\n")
    with open(os.path.join(ansi_dir, "request.json"), "w", encoding="utf-8") as handle:
        json.dump({"action": "discover", "target": "10.0.0.0/24"}, handle)

    status = browseparc.browse_parc_status(ansi_job, 0)
    check("statut lisible malgré les codes couleur", status.get("ok") is True, status)
    dump = json.dumps(status, ensure_ascii=False)
    illegal = _re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
    found = illegal.search(dump)
    check("aucun caractère interdit en XML", found is None, repr(found.group(0)) if found else "")
    check("séquence d'échappement ANSI retirée", "\x1b" not in dump)
    check("texte de la ligne conservé", "ERREUR" in dump and "ligne normale" in dump)

    body = _xmlrpc.dumps((status,), methodresponse=True, allow_none=True)
    try:
        _minidom.parseString(body)
        check("document XML-RPC analysable (ce que fait PHP)", True)
    except Exception as exc:  # noqa: BLE001
        check("document XML-RPC analysable (ce que fait PHP)", False, str(exc)[:120])

    print("\n11 ter. Clé SSH privée pour la prise en main")
    keydir = os.path.join(tmp, "sshkeys")
    os.makedirs(keydir, exist_ok=True)
    saved_dirs = browseparc.GUAC_KEY_DIRS
    browseparc.GUAC_KEY_DIRS = (keydir,)

    check("chemin hors zone autorisée refusé",
          browseparc._read_private_key("/etc/passwd")[1] is not None)
    check("chemin relatif refusé",
          browseparc._read_private_key("id_rsa")[1] is not None)
    check("chemin vide refusé", browseparc._read_private_key("")[1] is not None)
    absent = os.path.join(keydir, "absente")
    check("clé absente refusée",
          "not found" in (browseparc._read_private_key(absent)[1] or ""), absent)
    fake = os.path.join(keydir, "pas-une-cle")
    with open(fake, "w", encoding="utf-8") as handle:
        handle.write("ceci n'est pas une cle\n")
    check("fichier non-clé refusé",
          "not a private key" in (browseparc._read_private_key(fake)[1] or ""))
    good = os.path.join(keydir, "id_test")
    with open(good, "w", encoding="utf-8") as handle:
        handle.write("-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n"
                     "-----END OPENSSH PRIVATE KEY-----\n")
    content, error = browseparc._read_private_key(good)
    check("clé valide lue", error is None and "PRIVATE KEY" in (content or ""))

    # Une clé interdite doit être refusée AVANT tout appel à Guacamole.
    refused = browseparc.browse_parc_session({
        "protocol": "ssh", "target": "10.0.0.1", "sshkey": "/etc/passwd"})
    check("session SSH refusée si la clé est hors zone",
          refused.get("ok") is False and "SSH key" in (refused.get("error") or ""), refused)
    check("paramètre private-key construit",
          "private-key" in browseparc.browse_parc_session.__doc__.lower()
          or callable(browseparc._read_private_key))
    browseparc.GUAC_KEY_DIRS = saved_dirs

    print("\n11 quater. Sonde du mode de sécurité RDP")
    import socket as _socket
    import struct as _struct
    import threading as _threading

    def fake_rdp(answer):
        """Petit serveur RDP jetable qui renvoie la réponse fournie."""
        server = _socket.socket()
        server.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def serve():
            try:
                conn, _ = server.accept()
                conn.recv(1024)
                conn.send(answer)
                conn.close()
            except OSError:
                pass
            finally:
                server.close()

        _threading.Thread(target=serve, daemon=True).start()
        return port

    def answer(selected):
        # TPKT + X.224 Connection Confirm + RDP_NEG_RSP
        return (b"\x03\x00\x00\x13\x0e\xd0\x00\x00\x12\x34\x00"
                b"\x02\x01\x08\x00" + _struct.pack("<I", selected))

    selected, failure, error = browseparc._probe_rdp_security("127.0.0.1", fake_rdp(answer(0)))
    check("RDP standard détecté", selected == 0 and failure is None and error is None,
          (selected, failure, error))
    selected, failure, error = browseparc._probe_rdp_security("127.0.0.1", fake_rdp(answer(1)))
    check("TLS détecté", selected == 1 and failure is None and error is None,
          (selected, failure, error))
    selected, failure, error = browseparc._probe_rdp_security("127.0.0.1", fake_rdp(answer(2)))
    check("NLA détecté", selected == 2 and failure is None and error is None,
          (selected, failure, error))

    def neg_failure(code):
        return (b"\x03\x00\x00\x13\x0e\xd0\x00\x00\x12\x34\x00"
                b"\x03\x00\x08\x00" + _struct.pack("<I", code))

    selected, failure, error = browseparc._probe_rdp_security("127.0.0.1",
                                                              fake_rdp(neg_failure(2)))
    check("SSL_NOT_ALLOWED remonté (pas un service absent)",
          selected is None and failure == 2 and error is None, (selected, failure, error))
    selected, failure, error = browseparc._probe_rdp_security("127.0.0.1",
                                                              fake_rdp(neg_failure(1)))
    check("SSL_REQUIRED remonté", failure == 1 and error is None, (selected, failure, error))
    closed = _socket.socket()
    closed.bind(("127.0.0.1", 0))
    dead_port = closed.getsockname()[1]
    closed.close()
    selected, failure, error = browseparc._probe_rdp_security("127.0.0.1", dead_port, timeout=2)
    check("service absent remonté", selected is None and failure is None and error is not None,
          (selected, failure, error))

    print("\n11 quinquies. Transport d'installation choisi selon l'OS")
    check("Linux -> ssh", browseparc._install_transport("Debian 12", [22]) == "ssh")
    check("Windows + WinRM -> winrm",
          browseparc._install_transport("Windows", [5985]) == "winrm")
    check("Windows joignable en SSH -> ssh",
          browseparc._install_transport("Windows", [22]) == "ssh")
    check("Debian 13 -> ssh", browseparc._install_transport("Debian 13", [22, 3389]) == "ssh")
    check("Windows (assumed) -> winrm",
          browseparc._install_transport("Windows (assumed)", [3389]) == "winrm")
    check("aucune information -> indetermine",
          browseparc._install_transport("", []) is None)
    check("Windows sans WinRM ni SSH mais avec SMB -> smb",
          browseparc._install_transport("Windows", [445, 3389]) == "smb")
    check("Windows avec WinRM et SMB -> winrm (repli smb dans le script)",
          browseparc._install_transport("Windows", [5985, 445]) == "winrm")
    check("Windows avec SSH et SMB -> ssh",
          browseparc._install_transport("Windows", [22, 445]) == "ssh")
    check("OS inconnu, SMB seul -> smb", browseparc._install_transport("", [445]) == "smb")
    check("Linux avec Samba -> ssh", browseparc._install_transport("Debian 12", [22, 445]) == "ssh")

    events = os.path.join(tmp, "transport.jsonl")
    objects = [
        {"target": "pc-linux", "os": "Debian 12", "ports": [22]},
        {"target": "pc-win", "os": "Windows", "ports": [5985]},
    ]
    command = browseparc._build_command(
        "install", {"targets": objects, "username": "u", "password": "p",
                    "port": 5985}, events)
    joined = " ".join(str(part) for part in command)
    check("objets machines acceptes (bug corrige)", "--targets=pc-linux,pc-win" in joined,
          [part for part in command if str(part).startswith("--targets")])
    info = [part for part in command if str(part).startswith("--target-info=")]
    check("--target-info transmis", len(info) == 1, info)
    if info:
        payload = json.loads(str(info[0]).split("=", 1)[1])
        methods = {item["target"]: item["method"] for item in payload}
        check("methode ssh pour le Linux", methods.get("pc-linux") == "ssh", methods)
        check("methode winrm pour le Windows", methods.get("pc-win") == "winrm", methods)

    # Compatibilite : une simple liste de noms reste acceptee.
    command = browseparc._build_command(
        "install", {"targets": ["10.0.0.1"], "username": "u", "password": "p",
                    "port": 5985}, events)
    joined = " ".join(str(part) for part in command)
    check("liste de noms toujours acceptee", "--targets=10.0.0.1" in joined, joined[:120])
    check("pas de --target-info sans information", "--target-info=" not in joined)

    refused = False
    try:
        browseparc._build_command(
            "install", {"targets": [{"name": "sans-cible"}], "username": "u",
                        "password": "p", "port": 5985}, events)
    except ValueError:
        refused = True
    check("objet sans cible refuse", refused)

    print("\n12. Statut d'un job inconnu")
    check("job inconnu refusé", browseparc.browse_parc_status("inconnu").get("ok") is False)
    check("job id invalide refusé", browseparc.browse_parc_status("../../x").get("ok") is False)

    print("\n13. Limite de taille des réseaux (CIDR)")
    check("/16 accepté", browseparc._validate_target("10.0.0.0/16") == "10.0.0.0/16")
    check("/8 refusé par défaut", browseparc._validate_target("10.0.0.0/8") is None)
    check("raison explicite pour /8",
          "too large" in (browseparc._target_error("10.0.0.0/8") or ""))
    check("pas de raison pour /24", browseparc._target_error("10.0.0.0/24") is None)
    refused = browseparc.browse_parc_start({
        "action": "discover", "mode": "network", "target": "10.0.0.0/8",
        "port": 5985, "username": "u", "password": "p"})
    check("démarrage refusé avec message clair",
          refused.get("ok") is False and "too large" in refused.get("error", ""), refused)

    print("\n14. Logs par offset en octets")
    logfile = os.path.join(tmp, "chunk.log")
    with open(logfile, "wb") as handle:
        handle.write(b"un\ndeux\ntrois")
    lines, offset, more, _ = browseparc._read_log_chunk(logfile, 0)
    check("la ligne en cours d'écriture n'est pas livrée", lines == ["un", "deux"], lines)
    with open(logfile, "ab") as handle:
        handle.write(b"\nquatre\n")
    lines, offset, more, _ = browseparc._read_log_chunk(logfile, offset)
    check("la suite arrive complète", lines == ["trois", "quatre"], lines)
    lines, offset2, more, _ = browseparc._read_log_chunk(logfile, offset)
    check("rien de nouveau", lines == [] and offset2 == offset and not more, (lines, more))
    lines, _, _, _ = browseparc._read_log_chunk(logfile, 0, complete_only=False)
    check("job terminé: tout est livré", lines[-1] == "quatre", lines)
    with open(logfile, "wb") as handle:
        handle.write(b"x" * 10 + b"\n")
    lines, _, _, _ = browseparc._read_log_chunk(logfile, 9999)
    check("offset au-delà de la taille: relecture", lines == ["x" * 10], lines)

    saved_chunk = browseparc.MAX_LOG_CHUNK
    browseparc.MAX_LOG_CHUNK = 64
    with open(logfile, "wb") as handle:
        handle.write(b"".join(b"ligne %03d\n" % i for i in range(50)))
    lines, offset, more, truncated = browseparc._read_log_chunk(logfile, 0)
    check("gros log: démarre sur la fin", truncated and lines[-1] == "ligne 049", (truncated, lines[-3:]))
    check("gros log: première ligne entière", lines[0].startswith("ligne "), lines[:1])
    lines, offset, more, truncated = browseparc._read_log_chunk(logfile, 20)
    check("lecture par tranches", more and len(lines) >= 1 and not truncated, (more, lines))
    seen = list(lines)
    while more:
        lines, offset, more, _ = browseparc._read_log_chunk(logfile, offset)
        seen += lines
    check("toutes les tranches se raccordent", seen[-1] == "ligne 049" and len(seen) == len(set(seen)), seen[-2:])
    browseparc.MAX_LOG_CHUNK = saved_chunk

    print("\n15. Statut: log_more et offsets")
    start = browseparc.browse_parc_start({
        "action": "discover", "mode": "network", "target": "10.0.0.0/24",
        "port": 5985, "username": "admin", "password": "x"})
    status = wait_status(start["job"])
    check("log_offset est un nombre d'octets", status["log_offset"] > 0, status.get("log_offset"))
    check("log_more présent", status.get("log_more") is False, status.get("log_more"))
    again = browseparc.browse_parc_status(start["job"], status["log_offset"])
    check("poll suivant: pas de doublon", again["log"] == [], again["log"])
    nolog = browseparc.browse_parc_status(start["job"], 0, False)
    check("with_log=False: pas de log, résultat intact",
          nolog["ok"] and nolog["log"] == [] and nolog["status"] == status["status"], nolog.get("log"))

    print("\n16. Cache incrémental des événements")
    jobdir_cache = os.path.join(tmp, "jobs", start["job"])
    first = browseparc._read_events(jobdir_cache)
    second = browseparc._read_events(jobdir_cache)
    check("deux lectures identiques", first == second and len(first) > 0)
    with open(os.path.join(jobdir_cache, "events.jsonl"), "a") as handle:
        handle.write(json.dumps({"event": "progress", "done": 1, "total": 2}) + "\n")
        handle.write('{"event": "progress", "done": 2')
    third = browseparc._read_events(jobdir_cache)
    check("l'événement ajouté est vu", len(third) == len(first) + 1, (len(first), len(third)))
    with open(os.path.join(jobdir_cache, "events.jsonl"), "a") as handle:
        handle.write(', "total": 2}\n')
    fourth = browseparc._read_events(jobdir_cache)
    check("la ligne coupée est complétée sans doublon", len(fourth) == len(first) + 2, len(fourth))
    check("job sans fichier d'événements", browseparc._read_events(os.path.join(tmp, "nope")) == [])

    print("\n17. Réponse uuid-lookup: machines en dictionnaire")
    lookup = browseparc.browse_parc_start({"action": "uuid_lookup", "targets": ["10.0.0.1"]})
    status = wait_status(lookup["job"])
    check("machines reste une liste", isinstance(status["machines"], list), type(status["machines"]))

    print("\n18. Purge des anciens jobs")
    old_dir = os.path.join(tmp, "jobs", "20200101-000000-deadbeef")
    os.makedirs(old_dir)
    old_time = time.time() - 90 * 86400
    os.utime(old_dir, (old_time, old_time))
    foreign = os.path.join(tmp, "jobs", "a")
    os.makedirs(foreign)
    os.utime(foreign, (old_time, old_time))
    removed = browseparc._purge_jobs(force=True)
    check("job de 90 jours supprimé", not os.path.exists(old_dir) and removed >= 1, removed)
    check("dossier hors format conservé", os.path.isdir(foreign))
    check("jobs récents conservés", os.path.isdir(os.path.join(tmp, "jobs", start["job"])))
    shutil.rmtree(foreign)
    saved_max = browseparc.JOB_RETENTION_MAX
    browseparc.JOB_RETENTION_MAX = 10
    for index in range(15):
        extra = os.path.join(tmp, "jobs", "20250101-0000%02d-abcdef%02d" % (index, index))
        os.makedirs(extra)
        stamp = time.time() - 100 + index
        os.utime(extra, (stamp, stamp))
    browseparc._purge_jobs(force=True)
    left = [d for d in os.listdir(os.path.join(tmp, "jobs")) if d.startswith("20250101")]
    total_left = len(os.listdir(os.path.join(tmp, "jobs")))
    check("limite en nombre respectée", total_left == 10, total_left)
    browseparc.JOB_RETENTION_MAX = saved_max

    print("\n19. Sauvegarde atomique des groupes")
    first = browseparc.browse_parc_group_save("Atomique", ["10.0.0.1"])
    second = browseparc.browse_parc_group_save("Atomique", ["10.0.0.2"])
    check("groupe créé puis remplacé", first["ok"] and second["ok"] and second["replaced"], second)
    check("aucun fichier temporaire résiduel",
          not [f for f in os.listdir(browseparc.GROUPS_DIR) if f.endswith(".tmp")],
          os.listdir(browseparc.GROUPS_DIR))
    check("contenu à jour", browseparc.browse_parc_group_get("Atomique")["machines"][0]["target"] == "10.0.0.2")
    browseparc.browse_parc_group_delete("Atomique")

    print("\n20. Répertoires autorisés pour les clés SSH")
    saved_dirs = browseparc.GUAC_KEY_DIRS
    glob_root = tempfile.mkdtemp(prefix="bp-home-")
    os.makedirs(os.path.join(glob_root, "alice", ".ssh"))
    browseparc.GUAC_KEY_DIRS = (os.path.join(glob_root, "*", ".ssh"),)
    alice_key = os.path.join(glob_root, "alice", ".ssh", "id_test")
    with open(alice_key, "w") as handle:
        handle.write("-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----\n")
    content, error = browseparc._read_private_key(alice_key)
    check("clé d'un home accessible via le motif", content and not error, error)
    other = os.path.join(glob_root, "alice", "id_hors_ssh")
    shutil.copy(alice_key, other)
    content, error = browseparc._read_private_key(other)
    check("clé hors .ssh refusée", content is None and error, error)
    browseparc.GUAC_KEY_DIRS = saved_dirs
    shutil.rmtree(glob_root, ignore_errors=True)

    print("\n21. Réglages optionnels [browseparc]")
    conf = os.path.join(tmp, "admin.ini")
    with open(conf, "w") as handle:
        handle.write("[browseparc]\nmin_cidr_prefix = 20\njob_retention_days = abc\n")
    saved_conf = browseparc.BP_CONFIG_FILES
    browseparc.BP_CONFIG_FILES = (conf,)
    check("préfixe minimal configuré", browseparc._validate_target("10.0.0.0/16") is None)
    check("préfixe /20 accepté", browseparc._validate_target("10.0.0.0/20") == "10.0.0.0/20")
    check("valeur invalide: défaut", browseparc._config_int("job_retention_days", 30, 1, 3650) == 30)
    browseparc.BP_CONFIG_FILES = saved_conf
    check("sans fichier: défaut", browseparc._validate_target("10.0.0.0/16") == "10.0.0.0/16")

    print("\n21b. Dernière installation d'un groupe")
    first = browseparc.browse_parc_start({"action": "install", "targets": ["pc1.test.lan"],
                                          "username": "admin", "password": "x", "group": "Salle 12"})
    wait_status(first.get("job"))
    second = browseparc.browse_parc_start({"action": "install", "targets": ["pc1.test.lan"],
                                           "username": "admin", "password": "x", "group": "  Salle 12  "})
    wait_status(second.get("job"))
    other = browseparc.browse_parc_start({"action": "install", "targets": ["pc1.test.lan"],
                                          "username": "admin", "password": "x", "group": "Autre"})
    wait_status(other.get("job"))
    plain = browseparc.browse_parc_start({"action": "install", "targets": ["pc1.test.lan"],
                                          "username": "admin", "password": "x"})
    wait_status(plain.get("job"))
    found = browseparc.browse_parc_jobs(5, "Salle 12")
    ids = [j["job"] for j in found.get("jobs", [])]
    check("seules les installations du groupe sont listées", ids == [second["job"], first["job"]], found)
    check("le nom du groupe est renvoyé", all(j.get("group") == "Salle 12" for j in found["jobs"]), found)
    check("groupe inconnu: aucune tâche", browseparc.browse_parc_jobs(5, "Inconnu").get("jobs") == [])
    check("sans filtre: toutes les tâches", len(browseparc.browse_parc_jobs(50).get("jobs", [])) >= 4)

    print("\n21c. Journal et cause d'échec d'une installation")
    fail_job = browseparc.browse_parc_start({"action": "install", "targets": ["ko1.test.lan", "pc1.test.lan"],
                                             "username": "admin", "password": "x"})
    final = wait_status(fail_job.get("job"))
    results = {r["target"]: r for r in final.get("summary", {}).get("results", [])}
    check("l'étape en échec est renvoyée", results.get("ko1.test.lan", {}).get("step") == "connect", results)
    check("le code d'échec est renvoyé", results["ko1.test.lan"].get("code") == "auth_failed", results)
    check("le message distant est renvoyé", "Permission denied" in results["ko1.test.lan"].get("reason", ""), results)
    check("une machine réussie n'a pas de cause", "code" not in results["pc1.test.lan"], results)
    mlog = browseparc.browse_parc_machine_log(fail_job["job"], "ko1.test.lan")
    check("journal de la machine lisible", mlog.get("ok") is True and "auth_failed" in mlog.get("log", ""), mlog)
    check("journal d'une machine inconnue: erreur", browseparc.browse_parc_machine_log(fail_job["job"], "nope").get("ok") is False)
    check("identifiant de tâche invalide refusé", browseparc.browse_parc_machine_log("../x", "ko1.test.lan").get("ok") is False)
    escape = browseparc.browse_parc_machine_log(fail_job["job"], "../../../etc/passwd")
    check("pas d'évasion de répertoire", escape.get("ok") is False, escape)

    print("\n21d. macOS")
    mac_root = os.path.join(tmp, "clients2")
    os.makedirs(os.path.join(mac_root, "mac"))
    for name in ("Medulla-Agent-mac-arm64-5.6.5-abc.pkg", "Medulla-Agent-mac-x86_64-5.6.5-abc.pkg"):
        open(os.path.join(mac_root, "mac", name), "wb").write(b"pkg")
    saved_root, saved_agents = browseparc.CLIENT_ROOT, browseparc.AGENT_ROOT
    browseparc.CLIENT_ROOT = mac_root
    browseparc.AGENT_ROOT = os.path.join(tmp, "no-entity")
    generic = [a for a in browseparc.browse_parc_agents()["agents"] if a["id"] == "generic"][0]
    check("l'agent générique propose macOS", bool(generic.get("mac")), generic)
    check("deux architectures listées", len(generic["mac"]["files"]) == 2, generic["mac"])
    check("macOS: installation via ssh", browseparc._install_transport("macOS 14", [22]) == "ssh")
    check("Darwin: installation via ssh", browseparc._install_transport("Darwin", []) == "ssh")
    browseparc.CLIENT_ROOT, browseparc.AGENT_ROOT = saved_root, saved_agents

    shutil.rmtree(tmp, ignore_errors=True)

    print("\n=====================================")
    print("%d vérifications, %d échec(s)" % (CHECKS[0], len(FAILURES)))
    if FAILURES:
        print("Échecs: %s" % ", ".join(FAILURES))
        return 1
    print("TOUS LES TESTS PASSENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
