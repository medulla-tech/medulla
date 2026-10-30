#!/usr/bin/env python3
"""End to end backend checks, run ON the Medulla server.

It calls the very functions the MMC agent exposes (via the admin plugin
namespace, exactly like an XMLRPC call would) and drives the real
/usr/sbin/medulla-deploy-agent.sh script.

    python3 test_backend_on_server.py

Environment (defaults match the original test server):
    BP_TEST_NET   network scanned by the long discovery test  (172.16.12.0/24)
    BP_TEST_HOST  an unreachable-or-fake Windows host          (172.16.12.141)
    BP_ROOT       BrowseParc data directory of the server      (/var/lib/medulla/browseparc)
"""
import ipaddress
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/usr/lib/python3/dist-packages")

TEST_NET = os.environ.get("BP_TEST_NET", "172.16.12.0/24")
TEST_HOST = os.environ.get("BP_TEST_HOST", "172.16.12.141")
BP_ROOT = os.environ.get("BP_ROOT", "/var/lib/medulla/browseparc")
# Small ranges around TEST_HOST (172.16.12.140/30 and 172.16.12.136/29 by default).
TEST_NET_30 = str(ipaddress.ip_network("%s/30" % TEST_HOST, strict=False))
TEST_NET_29 = str(ipaddress.ip_network("%s/29" % TEST_HOST, strict=False))
# Every password sent by this test: none of them may be written to disk.
PASSWORD = "MotDePasseDeTest"
SENT_PASSWORDS = (PASSWORD, "Nope123", "bptest2")

PASS = [0]
FAIL = [0]
# Callables run at the end, whatever happens (created groups, connections,
# jobs, fake servers).
CLEANUPS = []


def check(label, condition, detail=""):
    if condition:
        PASS[0] += 1
        print("  ok   %s" % label)
    else:
        FAIL[0] += 1
        print("  FAIL %s %s" % (label, detail))


def wait_job(admin, job, timeout=180):
    deadline = time.time() + timeout
    status = None
    while time.time() < deadline:
        status = admin.browse_parc_status(job, 0)
        if not status.get("ok"):
            return status
        if status.get("status") in ("done", "error"):
            return status
        time.sleep(1)
    return status


def main():
    try:
        import mmc.plugins.admin as admin
    except Exception as exc:
        print("cannot import the admin plugin: %s" % exc)
        return 1
    try:
        return run_checks(admin)
    finally:
        for cleanup in reversed(CLEANUPS):
            try:
                cleanup()
            except Exception as exc:  # noqa: BLE001
                print("  cleanup failed: %s" % exc)


def delete_guacamole_connections(admin, name):
    """Delete the Guacamole connections called `name` (only that exact name)
    and return how many remain."""
    settings = admin.browseparc._guacamole_settings()
    token = admin.browseparc._guacamole_token(settings)
    path = "/api/session/data/mysql/connections"
    st, body = admin.browseparc._guacamole_call(settings, "GET", path, token=token)
    for cid, conn in json.loads(body).items():
        if conn.get("name") == name:
            admin.browseparc._guacamole_call(settings, "DELETE", "%s/%s" % (path, cid),
                                             token=token)
    st, body = admin.browseparc._guacamole_call(settings, "GET", path, token=token)
    return len([c for c in json.loads(body).values() if c.get("name") == name])


def run_checks(admin):
    print("\n1. Les methodes XMLRPC existent")
    for name in ("browse_parc_start", "browse_parc_status", "browse_parc_cancel",
                 "browse_parc_jobs", "browse_parc_prerequisites",
                 "browse_parc_groups_list", "browse_parc_group_get",
                 "browse_parc_group_save", "browse_parc_group_delete",
                 "browse_parc_agents", "browse_parc_session", "browse_parc_machine_log"):
        check("expose: %s" % name, hasattr(admin, name))

    print("\n2. Prerequis serveur (ne doit JAMAIS bloquer l'agent)")
    began = time.time()
    prereq = admin.browse_parc_prerequisites()
    elapsed = time.time() - began
    # L'agent Twisted execute les methodes dans le reacteur : un appel bloquant
    # gele toute la console MMC (c'est ce qui a provoque le 503).
    check("appel rendu immediatement (< 1s)", elapsed < 1.0, "%.3fs" % elapsed)
    check("rapport de prerequis lisible", prereq.get("ok") is True, prereq)
    print("     rendu en %.3fs, valeur en cache=%s, rafraichissement=%s"
          % (elapsed, prereq.get("cached"), prereq.get("refreshing")))
    for _ in range(40):
        time.sleep(1)
        again = admin.browse_parc_prerequisites()
        if (again.get("prerequisites") or {}).get("wsman") is not None:
            break
    print("     %s" % json.dumps((again or prereq).get("prerequisites", {})))

    print("\n3. Decouverte reseau reelle (machine locale)")
    start = admin.browse_parc_start({
        "action": "discover", "mode": "network", "target": "127.0.0.1/32",
        "port": 22, "namefilter": "",
        "username": "compte-de-test", "password": PASSWORD})
    check("job demarre", start.get("ok") is True, start)
    if not start.get("ok"):
        return 1
    job = start["job"]
    status = wait_job(admin, job, 120)
    check("job termine", status.get("status") == "done", status.get("status"))
    machines = status.get("machines") or []
    check("au moins une machine trouvee", len(machines) >= 1, machines)
    if machines:
        machine = machines[0]
        check("machine avec nom", bool(machine.get("name")), machine)
        check("machine avec adresse ip", bool(machine.get("ip")), machine)
        check("etat d'installation connu", "installed" in machine, machine)
    check("progression coherente",
          (status.get("progress") or {}).get("total") == len(machines),
          status.get("progress"))

    print("\n4. Mode decouverte sur une plage CIDR")
    start = admin.browse_parc_start({
        "action": "discover", "mode": "network", "target": TEST_NET_30,
        "port": 5985, "username": "compte-de-test", "password": PASSWORD})
    check("job CIDR demarre", start.get("ok") is True, start)
    if start.get("ok"):
        status = wait_job(admin, start["job"], 180)
        check("job CIDR termine", status.get("status") == "done", status.get("status"))
        print("     machines: %s" % ", ".join(
            "%s/%s" % (m.get("name"), m.get("ip")) for m in (status.get("machines") or [])))

    print("\n5. Refus des entrees dangereuses")
    check("injection shell refusee",
          admin.browse_parc_start({"action": "discover", "mode": "network",
                                   "target": "127.0.0.1; id"}).get("ok") is False)
    check("action inconnue refusee",
          admin.browse_parc_start({"action": "rm -rf"}).get("ok") is False)
    check("job inexistant refuse",
          admin.browse_parc_status("../../../etc/passwd").get("ok") is False)
    check("groupe avec traversee refuse",
          admin.browse_parc_group_delete("../../etc/passwd").get("ok") is False)

    print("\n6. Groupes de ciblage")
    save = admin.browse_parc_group_save(
        "Test automatique", [{"target": "127.0.0.1", "name": "localhost",
                              "ip": "127.0.0.1", "source": "explicit"}], "test")
    check("groupe enregistre", save.get("ok") is True, save)
    CLEANUPS.append(lambda: admin.browse_parc_group_delete("Test automatique"))
    listing = admin.browse_parc_groups_list()
    names = [g["name"] for g in listing.get("groups", [])]
    check("groupe visible dans la liste", "Test automatique" in names, names)
    one = admin.browse_parc_group_get("Test automatique")
    check("groupe relu", one.get("ok") is True and len(one.get("machines") or []) == 1, one)
    start = admin.browse_parc_start({"action": "uuid_lookup",
                                     "targets": ["gla-w11-1", "inconnu-xyz"]})
    check("job de resolution d'uuid demarre", start.get("ok") is True, start)
    if start.get("ok"):
        status = wait_job(admin, start["job"], 60)
        uuids = status.get("uuids") or {}
        check("machine connue resolue", bool(uuids.get("gla-w11-1", {}).get("known")), uuids)
        check("machine inconnue signalee",
              uuids.get("inconnu-xyz", {}).get("known") is False, uuids)
    check("groupe supprime", admin.browse_parc_group_delete("Test automatique").get("ok") is True)
    check("groupe bien supprime",
          "Test automatique" not in [g["name"] for g in
                                     admin.browse_parc_groups_list().get("groups", [])])

    print("\n7. Historique des jobs")
    jobs = admin.browse_parc_jobs(5)
    check("historique lisible", jobs.get("ok") is True and len(jobs.get("jobs", [])) >= 2, jobs)

    print("\n8. Etat reel des prerequis (hors cache) et echec d'installation")
    # Le cache a 5 minutes de duree de vie : on le rafraichit, puis on lit
    # l'etat directement dans le script pour decider de la suite.
    admin.browse_parc_prerequisites(force=True)
    for _ in range(30):
        time.sleep(1)
        fresh = admin.browse_parc_prerequisites()
        if fresh.get("checked_at") and not fresh.get("refreshing"):
            break
    check("le cache de prerequis a ete rafraichi", bool(fresh.get("checked_at")), fresh)
    raw = subprocess.check_output(
        ["/usr/sbin/medulla-deploy-agent.sh", "--check-prereq", "--json", "--non-interactive"],
        timeout=120).decode("utf-8", "replace")
    direct = json.loads(raw.strip().splitlines()[-1])
    wsman = bool(direct["prerequisites"].get("wsman"))
    print("     lecture directe : %s" % json.dumps(direct["prerequisites"]))

    if not wsman:
        start = admin.browse_parc_start({
            "action": "install", "targets": ["127.0.0.1"], "port": 5985,
            "username": "test", "password": "test", "timeout": 30})
        check("job d'installation demarre", start.get("ok") is True, start)
        if start.get("ok"):
            status = wait_job(admin, start["job"], 120)
            check("echec signale proprement", status.get("status") == "error", status.get("status"))
            check("message explicite sur WSMan",
                  "WSMan" in (status.get("error") or ""), status.get("error"))
    else:
        print("     client WSMan present : l'installation distante est possible")
        check("etat de prerequis coherent",
              (fresh.get("prerequisites") or {}).get("wsman") is True
              or fresh.get("refreshing") is True, fresh)

    print("\n8 bis. Agents deployables (agents des entites)")
    agents = admin.browse_parc_agents()
    check("liste d'agents lisible", agents.get("ok") is True, agents)
    listing = agents.get("agents") or []
    entities = [item for item in listing if item.get("kind") == "entity"]
    generic = [item for item in listing if item.get("kind") == "generic"]
    print("     %d agent(s) d'entite, %d generique(s), base=%s"
          % (len(entities), len(generic), agents.get("base_url")))
    for item in entities:
        systems = []
        if item.get("windows"):
            systems.append("windows")
        if item.get("linux"):
            systems.append("linux")
        print("       - %s [%s] %s" % (item.get("label"), "/".join(systems), item.get("date")))
    check("au moins un agent d'entite", len(entities) >= 1, listing)
    check("agent generique toujours propose", len(generic) == 1, listing)
    if entities:
        entity = entities[0]
        check("agent d'entite avec URL Windows",
              bool((entity.get("windows") or {}).get("url")), entity)
        check("agent d'entite avec chemin Linux",
              bool((entity.get("linux") or {}).get("path")), entity)
        check("URL d'agent sur le bon alias",
              "/medulla_agent/" in (entity.get("windows") or {}).get("url", ""), entity)
        start = admin.browse_parc_start({
            "action": "install", "targets": [TEST_HOST], "port": 5985,
            "username": "FAKE_NOBODY_XYZ", "password": "Nope123",
            "timeout": 60, "agent_id": entity["id"], "agent_insecure": True})
        check("installation avec agent d'entite demarree", start.get("ok") is True, start)
        if start.get("ok"):
            status = wait_job(admin, start["job"], 180)
            logs = " ".join(status.get("log") or [])
            check("pas d'erreur d'agent inconnu",
                  "Unknown agent" not in logs and "Unknown agent" not in (status.get("error") or ""),
                  logs[-200:])
    start = admin.browse_parc_start({
        "action": "install", "targets": ["127.0.0.1"], "port": 5985,
        "username": "a", "password": "b", "agent_id": "entity:../../etc/passwd"})
    check("agent inconnu refuse", start.get("ok") is False, start)

    print("\n8 ter. Prise en main Guacamole")
    def fake_rdp_server(selected=1):
        """Petit serveur RDP factice : repond a la negociation de securite.

        Le controle prealable de browse_parc_session exige un service RDP joignable,
        on ne peut donc plus tester avec une adresse non routable.
        """
        import socket
        import struct
        import threading

        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        server.listen(8)
        port = server.getsockname()[1]
        answer = (b"\x03\x00\x00\x13\x0e\xd0\x00\x00\x12\x34\x00"
                  b"\x02\x01\x08\x00" + struct.pack("<I", selected))
        stop = threading.Event()

        def serve():
            server.settimeout(0.5)
            while not stop.is_set():
                try:
                    conn, _ = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                try:
                    conn.recv(2048)
                    conn.send(answer)
                except OSError:
                    pass
                finally:
                    conn.close()
            server.close()

        threading.Thread(target=serve, daemon=True).start()
        return port, stop
    rdp_port, rdp_stop = fake_rdp_server(1)
    CLEANUPS.append(rdp_stop.set)
    CLEANUPS.append(lambda: delete_guacamole_connections(admin, "RDP_127.0.0.1"))
    session = admin.browse_parc_session({
        "protocol": "rdp", "target": "127.0.0.1", "port": rdp_port,
        "username": "bptest", "password": "bptest"})
    check("session Guacamole creee", session.get("ok") is True, session)
    if session.get("ok"):
        check("URL de client Guacamole",
              "#/client/" in session["url"] and "@@CUX_ID@@" not in session["url"], session["url"])
        check("nom de connexion conventionnel",
              session["connection"] == "RDP_127.0.0.1", session["connection"])
        again = admin.browse_parc_session({
            "protocol": "rdp", "target": "127.0.0.1", "port": rdp_port,
            "username": "bptest", "password": "bptest2"})
        check("session mise a jour", again.get("ok") is True and again.get("action") == "updated",
              again)
        # nettoyage (seule la connexion creee par ce test est supprimee)
        remaining = delete_guacamole_connections(admin, "RDP_127.0.0.1")
        check("connexion de test supprimee", remaining == 0, "%d restante(s)" % remaining)
        rdp_stop.set()
    check("protocole inconnu refuse",
          admin.browse_parc_session({"protocol": "telnet", "target": "192.0.2.77"}).get("ok") is False)
    check("machine invalide refusee",
          admin.browse_parc_session({"protocol": "rdp", "target": ";/etc"}).get("ok") is False)

    print("\n8 quater. Securite XML-RPC du journal (codes couleur ANSI)")
    import re as _re
    import xml.dom.minidom as _minidom
    import xmlrpc.client as _xmlrpc
    start = admin.browse_parc_start({
        "action": "discover", "mode": "network", "target": TEST_NET_29,
        "port": 5985, "username": "compte-de-test", "password": PASSWORD})
    check("job de controle demarre", start.get("ok") is True, start)
    if start.get("ok"):
        controle = wait_job(admin, start["job"], 120)
        dump = json.dumps(controle, ensure_ascii=False)
        illegal = _re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
        found = illegal.search(dump)
        check("aucun caractere interdit en XML dans le statut", found is None,
              repr(found.group(0)) if found else "")
        check("aucune sequence ANSI dans le statut", "\x1b" not in dump)
        body = _xmlrpc.dumps((controle,), methodresponse=True, allow_none=True)
        try:
            _minidom.parseString(body)
            check("document XML-RPC analysable par un parseur strict", True)
        except Exception as exc:  # noqa: BLE001
            check("document XML-RPC analysable par un parseur strict", False, str(exc)[:120])
        import os as _os
        err = _os.path.join(admin.browseparc.JOBS_DIR, start["job"], "stderr.log")
        raw = open(err, "rb").read() if _os.path.isfile(err) else b""
        check("le journal du job ne contient plus de code couleur", raw.count(27) == 0,
              "%d ESC" % raw.count(27))

    print("\n9. Le bloc PowerShell Active Directory s'execute vraiment")
    # Regression : "pwsh -Command -" lit son entree LIGNE PAR LIGNE, un bloc
    # multi-ligne n'etait donc jamais execute et ne renvoyait rien du tout.
    # Avec des identifiants invalides on doit obtenir une erreur exploitable.
    start = admin.browse_parc_start({
        "action": "list_ous", "mode": "ad", "server": TEST_HOST,
        "username": "FAKE_NOBODY_XYZ", "password": "Nope123"})
    check("job de listage des OU demarre", start.get("ok") is True, start)
    if start.get("ok"):
        status = wait_job(admin, start["job"], 120)
        err = status.get("error") or ""
        if prereq.get("prerequisites", {}).get("wsman"):
            check("reponse PowerShell exploitee (pas de reponse vide)",
                  "No JSON answer" not in err, err)
            check("erreur d'authentification remontee, pas un echec muet",
                  ("Authorization failed" in err) or ("Logon failure" in err)
                  or ("auth" in err.lower()), err)
        else:
            check("message explicite sur le client WSMan absent", "WSMan" in err, err)

    print("\n10. Le journal d'une installation en echec explique la cause")
    start = admin.browse_parc_start({
        "action": "install", "targets": [TEST_HOST], "port": 5985,
        "username": "FAKE_NOBODY_XYZ", "password": "Nope123", "timeout": 60})
    check("job d'installation demarre", start.get("ok") is True, start)
    if start.get("ok"):
        status = wait_job(admin, start["job"], 180)
        logs = " ".join(status.get("log") or [])
        check("l'echec est signale", (status.get("summary") or {}).get("ko") == 1,
              status.get("summary"))
        check("la cause remonte dans le journal",
              ("Authorization failed" in logs) or ("WSMan" in logs)
              or ("failed" in logs.lower()), logs[-200:])

    print("\n11. Une tache annulee est bien rapportee comme annulee")
    # Le tableau affichait "termine" apres une annulation : le bouton Annuler
    # semblait donc n'avoir rien fait, alors que la tache etait bien arretee.
    start = admin.browse_parc_start({
        "action": "discover", "mode": "network", "target": TEST_NET,
        "port": 5985, "timeout": 120,
        "username": "compte-de-test", "password": PASSWORD})
    check("job de decouverte demarre", start.get("ok") is True, start)
    if start.get("ok"):
        job = start["job"]
        CLEANUPS.append(lambda: admin.browse_parc_cancel(job))
        time.sleep(1)
        cancel = admin.browse_parc_cancel(job)
        check("annulation acceptee", cancel.get("ok") is True and cancel.get("cancelled") is True,
              cancel)
        entry = [j for j in (admin.browse_parc_jobs() or {}).get("jobs", []) if j.get("job") == job]
        check("la tache apparait dans la liste", bool(entry))
        if entry:
            check("l'etat est 'cancelled', pas 'finished'",
                  entry[0].get("state") == "cancelled", entry[0].get("state"))
        deadline = time.time() + 20
        while time.time() < deadline:
            status = admin.browse_parc_status(job, 0)
            if status.get("status") == "cancelled":
                break
            time.sleep(1)
        check("le statut detaille est 'cancelled'", status.get("status") == "cancelled",
              status.get("status"))
        # La tache doit vraiment s'arreter, pas seulement etre marquee.
        stopped = time.time() + 30
        while time.time() < stopped:
            if not os.path.exists("/proc/%d" % (start.get("pid") or 0)):
                break
            entry = [j for j in (admin.browse_parc_jobs() or {}).get("jobs", [])
                     if j.get("job") == job]
            if entry and entry[0].get("state") != "running":
                break
            time.sleep(1)
        check("la tache ne reste pas 'running'", not entry or entry[0].get("state") != "running",
              entry[0].get("state") if entry else None)

    print("\n12. Le mot de passe n'est jamais persiste")
    found = []
    for root, _dirs, files in os.walk(BP_ROOT):
        for name in files:
            path = os.path.join(root, name)
            try:
                with open(path, "rb") as handle:
                    content = handle.read()
                if any(p.encode("utf-8") in content for p in SENT_PASSWORDS):
                    found.append(path)
            except OSError:
                pass
    check("aucun fichier de job ne contient le mot de passe", not found, found)

    print("\n=====================================")
    print("%d verifications OK, %d echec(s)" % (PASS[0], FAIL[0]))
    return 1 if FAIL[0] else 0


if __name__ == "__main__":
    sys.exit(main())
