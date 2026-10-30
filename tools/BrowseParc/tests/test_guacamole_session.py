#!/usr/bin/env python3
"""Test de browse_parc_session : creation, mise a jour et URL Guacamole.

Le module est importe directement depuis un chemin de test : aucun redemarrage
de l'agent n'est necessaire pour ce test. Par defaut c'est server/python/browseparc.py
de ce depot ; un autre chemin peut etre passe en premier argument.
"""
import atexit
import importlib.util
import json
import os
import sys

DEFAULT_MODULE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "..", "server", "python", "browseparc.py")
MODULE = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(DEFAULT_MODULE)

spec = importlib.util.spec_from_file_location("browseparc_test", MODULE)
browseparc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(browseparc)

PASS = [0]
FAIL = [0]
# Noms des connexions creees par CE test : seules celles-la sont supprimees.
CREATED = set()


def cleanup():
    """Supprime les connexions creees par le test (et rien d'autre)."""
    removed = 0
    if not CREATED:
        return removed
    settings = browseparc._guacamole_settings()
    token = browseparc._guacamole_token(settings)
    path = "/api/session/data/mysql/connections"
    status, body = browseparc._guacamole_call(settings, "GET", path, token=token)
    for cid, conn in json.loads(body).items():
        if conn.get("name") in CREATED:
            browseparc._guacamole_call(settings, "DELETE", "%s/%s" % (path, cid), token=token)
            removed += 1
    CREATED.clear()
    return removed


# Execute aussi en cas d'echec ou d'exception au milieu du test.
atexit.register(cleanup)


def check(label, condition, detail=""):
    if condition:
        PASS[0] += 1
        print("  ok   %s" % label)
    else:
        FAIL[0] += 1
        print("  FAIL %s %s" % (label, detail))


TARGET = "127.0.0.1"           # cible locale : la sonde RDP doit joindre un vrai service
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
RDP_PORT, RDP_STOP = fake_rdp_server(1)

print("\n1. Configuration Guacamole")
settings = browseparc._guacamole_settings()
check("URL de base lue", settings["template"].startswith("https://"), settings["template"])
check("identifiants web lus", bool(settings["username"]) and bool(settings["password"]))
check("endpoint API local", settings["api"].startswith("https://127.0.0.1/"), settings["api"])
import base64 as _b64
attendu = _b64.b64encode(b"3843" + b"\x00c\x00mysql").decode()
check("encodage de l'identifiant client", browseparc._guacamole_cux_id(3843) == attendu,
      "%s != %s" % (browseparc._guacamole_cux_id(3843), attendu))
print("     options RDP du relais : %s" % json.dumps(browseparc._guacamole_parameters("rdp")))

print("\n2. Refus des entrees invalides")
check("protocole inconnu refuse",
      browseparc.browse_parc_session({"protocol": "telnet", "target": TARGET}).get("ok") is False)
check("machine invalide refusee",
      browseparc.browse_parc_session({"protocol": "rdp", "target": "$(id)"}).get("ok") is False)
check("port invalide refuse",
      browseparc.browse_parc_session({"protocol": "rdp", "target": TARGET,
                                      "port": "99999"}).get("ok") is False)
check("identifiants trop longs refuses",
      browseparc.browse_parc_session({"protocol": "rdp", "target": TARGET,
                                      "username": "a" * 200}).get("ok") is False)

print("\n3. Creation d'une session RDP")
result = browseparc.browse_parc_session({
    "protocol": "rdp", "target": TARGET, "port": RDP_PORT,
    "username": "testuser", "password": "testpass"})
check("session creee", result.get("ok") is True, result)
if result.get("ok"):
    CREATED.add(result["connection"])
if not result.get("ok"):
    print("\n%d ok, %d echec(s)" % (PASS[0], FAIL[0]))
    raise SystemExit(1)
check("nom de connexion conventionnel", result["connection"] == "RDP_%s" % TARGET, result)
check("action = created", result["action"] == "created", result)
check("URL Guacamole exploitable",
      result["url"].startswith("https://") and "#/client/" in result["url"]
      and "@@CUX_ID@@" not in result["url"], result["url"])
check("identifiant de connexion present", str(result["connection_id"]).isdigit(), result)

print("\n4. Mise a jour de la meme connexion")
again = browseparc.browse_parc_session({
    "protocol": "rdp", "target": TARGET, "port": RDP_PORT,
    "username": "testuser", "password": "anotherpass"})
check("deuxieme appel ok", again.get("ok") is True, again)
check("action = updated", again.get("action") == "updated", again)
check("meme identifiant de connexion",
      again["connection_id"] == result["connection_id"], again)

print("\n5. Protocoles Linux")
token = browseparc._guacamole_token(browseparc._guacamole_settings())
for protocol, port in (("ssh", 22),):
    session = browseparc.browse_parc_session({
        "protocol": protocol, "target": TARGET, "port": port,
        "username": "root", "password": "secret"})
    check("session %s creee" % protocol, session.get("ok") is True, session)
    if session.get("ok"):
        CREATED.add(session["connection"])
        check("nom %s_<hote>" % protocol.upper(),
              session["connection"] == "%s_%s" % (protocol.upper(), TARGET), session)
        settings_check = browseparc._guacamole_call(
            browseparc._guacamole_settings(), "GET",
            "/api/session/data/mysql/connections", token=browseparc._guacamole_token(
                browseparc._guacamole_settings()))
        connections = json.loads(settings_check[1])
        match = [(cid, c) for cid, c in connections.items()
                 if c.get("name") == session["connection"]]
        check("connexion %s presente dans Guacamole" % protocol, len(match) == 1, match)
        if match:
            # Les parametres se lisent sur un endpoint dedie.
            _st, _body = browseparc._guacamole_call(
                browseparc._guacamole_settings(), "GET",
                "/api/session/data/mysql/connections/%s/parameters" % match[0][0], token=token)
            params = json.loads(_body) if _st == 200 else {}
            check("hote enregistre", params.get("hostname") == TARGET, params)
            check("port enregistre", str(params.get("port")) == str(port), params)
            check("identifiants enregistres",
                  params.get("username") == "root" and params.get("password") == "secret", params)

print("\n6. Nettoyage")
removed = cleanup()
check("connexions de test supprimees", removed >= 2, removed)
RDP_STOP.set()

print("\n=====================================")
print("%d verifications OK, %d echec(s)" % (PASS[0], FAIL[0]))
sys.exit(1 if FAIL[0] else 0)
