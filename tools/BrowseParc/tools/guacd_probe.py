#!/usr/bin/env python3
"""Interroge guacd directement pour connaitre l'erreur exacte d'une connexion.

Pilote le demon guacd (127.0.0.1:4822) avec le protocole Guacamole, en reprenant
les parametres de la connexion enregistree, et affiche la reponse : 'ready' ou
'error' avec le message de FreeRDP.

Usage : guacd_probe.py <nom_connexion> [cle=valeur ...]
"""
import json
import os
import socket
import ssl
import time
import sys
import urllib.parse
import urllib.request

GUACD_HOST, GUACD_PORT = "127.0.0.1", 4822
XMPP_INI = ["/etc/mmc/plugins/xmppmaster.ini", "/etc/mmc/plugins/xmppmaster.ini.local"]


def guacamole_api(path, token=None, method="GET", payload=None):
    base = "https://127.0.0.1/guacamole"
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Guacamole-Token"] = token
    request = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(request, timeout=20, context=context) as response:
        return json.loads(response.read().decode())


def settings():
    import configparser
    template = None
    for path in XMPP_INI:
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(path)
        for section in parser.sections():
            if parser.has_option(section, "guacamole_baseurl"):
                template = parser.get(section, "guacamole_baseurl")
    creds = urllib.parse.parse_qs(template.split("?", 1)[1])
    return creds["username"][0], creds["password"][0]


def instruction(*parts):
    out = []
    for part in parts:
        part = str(part)
        out.append("%d.%s" % (len(part.encode()), part))
    return ",".join(out) + ";"


class _Decoder:
    """Decodeur d'instructions du protocole Guacamole."""

    def __init__(self, sock):
        self.sock = sock
        self.buffer = b""

    def next_instruction(self):
        while b";" not in self.buffer:
            try:
                chunk = self.sock.recv(65536)
            except socket.timeout:
                return None
            if not chunk:
                return None
            self.buffer += chunk
        raw, self.buffer = self.buffer.split(b";", 1)
        parts = []
        pos = 0
        while pos < len(raw):
            try:
                dot = raw.index(b".", pos)
                length = int(raw[pos:dot])
            except (ValueError, IndexError):
                return parts or None
            parts.append(raw[dot + 1:dot + 1 + length].decode("utf-8", "replace"))
            pos = dot + 1 + length + 1
        return parts or None


def drive_guacd(parameters, timeout=25):
    """Ouvre une session guacd et renvoie la premiere reponse significative."""
    sock = socket.create_connection((GUACD_HOST, GUACD_PORT), timeout=timeout)
    sock.settimeout(timeout)
    protocol = parameters.get("protocol", "rdp")
    handshake = (instruction("select", protocol)
                 + instruction("size", 1024, 768)
                 + instruction("audio", "audio/ogg")
                 + instruction("video")
                 + instruction("image", "image/png", "image/jpeg", "image/webp"))
    sock.send(handshake.encode())

    result = {"instructions": [], "error": None, "ready": False,
              "args": [], "sent": []}
    decoder = _Decoder(sock)
    try:
        # guacd annonce les arguments attendus par une instruction 'args'.
        while True:
            parts = decoder.next_instruction()
            if parts is None:
                return result
            result["instructions"].append(parts[0])
            if parts[0] == "args":
                result["args"] = parts[1:]
                break
            if parts[0] == "error":
                result["error"] = parts[1] if len(parts) > 1 else "(sans message)"
                return result

        # 'args' est la liste des parametres attendus, DANS L'ORDRE. Le premier
        # element est la version du protocole et doit etre renvoye tel quel ;
        # les suivants sont des noms de parametres, auxquels on repond par la
        # valeur correspondante (une par entree).
        names = result["args"]
        final = []
        for index, name in enumerate(names):
            if index == 0:
                final.append(name)
            else:
                final.append(str(parameters.get(name, "")))
        result["sent"] = [(name, final[index]) for index, name in enumerate(names)]
        sock.send(instruction("connect", *final).encode())

        while True:
            parts = decoder.next_instruction()
            if parts is None:
                return result
            result["instructions"].append(parts[0])
            if parts[0] == "error":
                result["error"] = parts[1] if len(parts) > 1 else "(sans message)"
                return result
            if parts[0] == "ready":
                # 'ready' ne signifie que "handshake accepte" : la vraie
                # connexion RDP peut encore echouer juste apres. On continue a
                # lire pour capter l'instruction 'error' eventuelle.
                result["ready"] = True
                result["painted"] = False
                result["closed"] = False
                # Une session n'est reellement stable que si guacd continue a
                # envoyer des instructions pendant toute la duree d'observation.
                span = float(os.environ.get("BP_GUACD_SPAN", "20"))
                began = time.time()
                sock.settimeout(span + 5)
                while time.time() - began < span:
                    following = decoder.next_instruction()
                    if following is None:
                        result["closed"] = True
                        break
                    result["instructions"].append(following[0])
                    if following[0] == "error":
                        result["error"] = (following[1] if len(following) > 1
                                           else "(sans message)")
                        return result
                    if following[0] in ("img", "blob", "sync", "png", "size", "cursor"):
                        result["painted"] = True
                    # 'end' termine un FLUX (image, presse-papier) : ce n'est
                    # pas la fin de la session. Seul 'disconnect' l'est.
                    if following[0] == "disconnect":
                        result["closed"] = True
                        return result
                result["alive_for"] = round(time.time() - began, 1)
                return result
            if parts[0] == "disconnect":
                return result
    except socket.timeout:
        result["error"] = result["error"] or "delai guacd depasse"
    finally:
        sock.close()
    return result


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "RDP_kno.medulla.lan"
    overrides = {}
    for extra in sys.argv[2:]:
        key, _, value = extra.partition("=")
        overrides[key] = value

    user, password = settings()
    # Le jeton s'obtient par formulaire.
    data = urllib.parse.urlencode({"username": user, "password": password}).encode()
    request = urllib.request.Request(
        "https://127.0.0.1/guacamole/api/tokens", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(request, timeout=20,
                               context=ssl._create_unverified_context()) as response:
        token = json.loads(response.read().decode())["authToken"]

    connections = guacamole_api("/api/session/data/mysql/connections", token=token)
    match = [(cid, c) for cid, c in connections.items() if c.get("name") == name]
    if not match:
        print("--- connexion introuvable : %s" % name)
        return 1
    connection_id, meta = match[0]
    stored = guacamole_api(
        "/api/session/data/mysql/connections/%s/parameters" % connection_id, token=token)

    parameters = dict(stored)
    parameters["width"] = "1024"
    parameters["height"] = "768"
    parameters["dpi"] = "96"
    parameters.update(overrides)

    print("--- connexion %s (id %s, protocole %s)" % (name, connection_id, meta.get("protocol")))
    shown = {k: ("*" * len(v) if "password" in k else v) for k, v in parameters.items()}
    print("--- parametres : %s" % json.dumps(shown, ensure_ascii=False))
    result = drive_guacd(parameters)
    print("--- instructions recues : %s" % ", ".join(result["instructions"]))
    if result.get("sent"):
        shown_sent = [(k, "*" * len(v) if "password" in k else v) for k, v in result["sent"]]
        print("--- arguments envoyes : %s" % json.dumps(dict(shown_sent), ensure_ascii=False))
    if result["ready"] and not result["error"]:
        if result.get("closed"):
            print("--- RESULTAT : session INTERROMPUE par le serveur (fermee)")
            return 3
        print("--- RESULTAT : session STABLE pendant %ss (affichage=%s)"
              % (result.get("alive_for"), result.get("painted")))
        return 0
    print("--- RESULTAT : echec -> %s" % (result["error"] or "aucune reponse utile"))
    return 2


if __name__ == "__main__":
    sys.exit(main())
