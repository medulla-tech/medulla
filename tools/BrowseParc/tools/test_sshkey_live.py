#!/usr/bin/env python3
"""Valide la prise en main SSH par CLE PRIVEE, de bout en bout.

Utilise une cle de test jetable ajoutee au compte 'support' de ce serveur, puis
retiree immediatement apres le test (restauration de authorized_keys).
"""
import json
import os
import shutil
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, "/usr/lib/python3/dist-packages")
sys.path.insert(0, "/tmp")
import mmc.plugins.admin as admin   # noqa: E402
import guacd_probe                  # noqa: E402

HOME = "/home/support"
SSH_DIR = os.path.join(HOME, ".ssh")
KEY = os.path.join(SSH_DIR, "bp_test_key")
AUTHORIZED = os.path.join(SSH_DIR, "authorized_keys")
BACKUP = AUTHORIZED + ".bp-backup"
TARGET = "gla.medulla.lan"


def guac_token():
    user, password = guacd_probe.settings()
    data = urllib.parse.urlencode({"username": user, "password": password}).encode()
    request = urllib.request.Request(
        "https://127.0.0.1/guacamole/api/tokens", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(request, timeout=20,
                               context=ssl._create_unverified_context()) as response:
        return json.loads(response.read().decode())["authToken"]


def cleanup(connection_name=None):
    # authorized_keys
    if os.path.isfile(BACKUP):
        shutil.move(BACKUP, AUTHORIZED)
        subprocess.run(["chown", "support:support", AUTHORIZED], check=False)
        print("--- authorized_keys restaure")
    for path in (KEY, KEY + ".pub"):
        if os.path.isfile(path):
            os.remove(path)
    if os.path.isfile(KEY):
        print("--- cle de test non supprimee !")
    # connexion Guacamole de test
    if connection_name:
        try:
            token = guac_token()
            connections = guacd_probe.guacamole_api(
                "/api/session/data/mysql/connections", token=token)
            for cid, meta in connections.items():
                if meta.get("name") == connection_name:
                    guacd_probe.guacamole_api(
                        "/api/session/data/mysql/connections/%s" % cid,
                        token=token, method="DELETE")
                    print("--- connexion %s supprimee" % connection_name)
        except Exception as exc:  # noqa: BLE001
            print("--- nettoyage Guacamole impossible : %s" % exc)


def main():
    connection_name = "SSH_%s" % TARGET
    created_key = False
    try:
        print("--- generation d'une cle de test")
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-N", "", "-q",
                        "-C", "browseparc-test", "-f", KEY], check=True)
        created_key = True
        subprocess.run(["chown", "-R", "support:support", SSH_DIR], check=False)

        if not os.path.isfile(AUTHORIZED):
            open(AUTHORIZED, "w").close()
        shutil.copy2(AUTHORIZED, BACKUP)
        with open(KEY + ".pub", encoding="utf-8") as handle:
            public = handle.read().strip()
        with open(AUTHORIZED, "a", encoding="utf-8") as handle:
            handle.write("\n# browseparc-test (temporaire)\n%s\n" % public)
        subprocess.run(["chmod", "600", AUTHORIZED], check=False)
        subprocess.run(["chown", "support:support", AUTHORIZED], check=False)
        print("--- cle publique ajoutee a %s" % AUTHORIZED)

        print("--- browse_parc_session avec la cle")
        result = admin.browse_parc_session({
            "protocol": "ssh", "target": TARGET, "port": 22,
            "username": "support", "sshkey": KEY})
        print("    ok=%s action=%s connexion=%s"
              % (result.get("ok"), result.get("action"), result.get("connection")))
        if not result.get("ok"):
            print("    erreur : %s" % result.get("error"))
            return 1

        token = guac_token()
        parameters = dict(guacd_probe.guacamole_api(
            "/api/session/data/mysql/connections/%s/parameters" % result["connection_id"],
            token=token))
        print("    parametres enregistres : %s"
              % json.dumps({k: ("*" * len(v) if "password" in k or "key" in k else v)
                            for k, v in parameters.items()}, ensure_ascii=False))
        if "private-key" not in parameters:
            print("    ECHEC : aucune cle privee enregistree")
            return 1
        print("    cle privee presente dans la connexion : OUI")

        parameters["protocol"] = "ssh"
        parameters["width"] = "1024"
        parameters["height"] = "768"
        os.environ["BP_GUACD_SPAN"] = "15"
        probe = guacd_probe.drive_guacd(parameters)
        print("--- instructions : %s" % ", ".join(probe["instructions"][:14]))
        if probe["ready"] and not probe["error"] and not probe.get("closed"):
            print("--- RESULTAT : session SSH par cle STABLE pendant %ss"
                  % probe.get("alive_for"))
            return 0
        print("--- RESULTAT : echec -> %s"
              % (probe["error"] or "session fermee par le serveur"))
        return 2
    finally:
        cleanup(connection_name if created_key else None)


if __name__ == "__main__":
    sys.exit(main())
