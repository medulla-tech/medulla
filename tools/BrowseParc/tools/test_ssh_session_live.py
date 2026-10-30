#!/usr/bin/env python3
"""Valide la prise en main SSH sur une machine reelle, via mon backend + guacd.

Cree la connexion SSH_<hote> avec browse_parc_session (comme le fait le bouton
de l'interface), puis ouvre une session guacd avec ces parametres.
"""
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, "/usr/lib/python3/dist-packages")
import mmc.plugins.admin as admin  # noqa: E402

sys.path.insert(0, "/tmp")
import guacd_probe  # noqa: E402

HOST = sys.argv[1] if len(sys.argv) > 1 else "kno.medulla.lan"


def guac_token():
    user, password = guacd_probe.settings()
    data = urllib.parse.urlencode({"username": user, "password": password}).encode()
    request = urllib.request.Request(
        "https://127.0.0.1/guacamole/api/tokens", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(request, timeout=20,
                                context=ssl._create_unverified_context()) as response:
        return json.loads(response.read().decode())["authToken"]


# 1. Lire les identifiants deja utilises pour cette machine (connexion RDP).
token = guac_token()
connections = guacd_probe.guacamole_api("/api/session/data/mysql/connections", token=token)
username, password = None, None
for cid, meta in connections.items():
    if meta.get("name") == "RDP_%s" % HOST:
        stored = guacd_probe.guacamole_api(
            "/api/session/data/mysql/connections/%s/parameters" % cid, token=token)
        username = stored.get("username")
        password = stored.get("password")
print("--- identifiants repris de RDP_%s : utilisateur=%s, mot de passe=%s"
      % (HOST, username, "*" * len(password or "")))

# 2. Creer la connexion SSH avec le backend de l'application.
result = admin.browse_parc_session({
    "protocol": "ssh", "target": HOST, "port": 22,
    "username": username, "password": password})
print("--- browse_parc_session : ok=%s action=%s connexion=%s"
      % (result.get("ok"), result.get("action"), result.get("connection")))
if not result.get("ok"):
    print("    erreur : %s" % result.get("error"))
    sys.exit(1)

# 3. Tester la session reelle via guacd.
parameters = dict(guacd_probe.guacamole_api(
    "/api/session/data/mysql/connections/%s/parameters" % result["connection_id"],
    token=token))
parameters["width"] = "1024"
parameters["height"] = "768"
# Indispensable : le protocole n'est pas dans les parametres mais dans les
# metadonnees de la connexion.
parameters["protocol"] = "ssh"
os.environ.setdefault("BP_GUACD_SPAN", "12")
probe = guacd_probe.drive_guacd(parameters)
print("--- instructions recues : %s" % ", ".join(probe["instructions"]))
if probe["ready"] and not probe["error"] and not probe.get("closed"):
    print("--- RESULTAT : session SSH STABLE pendant %ss" % probe.get("alive_for"))
    sys.exit(0)
print("--- RESULTAT : echec -> %s" % (probe["error"] or "session fermee par le serveur"))
sys.exit(2)
