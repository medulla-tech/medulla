#!/usr/bin/env python3
"""Valide la creation d'une connexion Guacamole via l'API REST (test jetable)."""
import base64
import configparser
import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request

XMPP_INI = ["/etc/mmc/plugins/xmppmaster.ini", "/etc/mmc/plugins/xmppmaster.ini.local"]
CTX = ssl._create_unverified_context()
BASE = "https://127.0.0.1/guacamole"
TEST_NAME = "RDP_bp-selftest"


def read_conf():
    """Le .local doit ecraser le fichier de base, comme le fait MMC."""
    value = None
    for path in XMPP_INI:
        if not os.path.isfile(path):
            continue
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(path)
        for section in parser.sections():
            if parser.has_option(section, "guacamole_baseurl"):
                value = parser.get(section, "guacamole_baseurl")
    return value


def call(method, path, token=None, data=None, content_type="application/json"):
    url = BASE + path
    body = None
    headers = {}
    if data is not None:
        body = data.encode() if isinstance(data, str) else data
        headers["Content-Type"] = content_type
    if token:
        headers["Guacamole-Token"] = token
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15, context=CTX) as response:
            return response.status, response.read().decode("utf-8", "replace"), dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace"), dict(exc.headers)


url_template = read_conf()
print("--- guacamole_baseurl :", url_template)
# Les identifiants sont dans le fragment : ...#/client/@@CUX_ID@@?username=..&password=..
query = url_template.split("?", 1)[1] if "?" in url_template else ""
creds = urllib.parse.parse_qs(query)
user, password = creds["username"][0], creds["password"][0]
print("--- compte guacamole :", user)
path = urllib.parse.urlparse(url_template).path.rstrip("/")
BASE = "https://127.0.0.1" + path
print("--- base API :", BASE)

status, body, _ = call("POST", "/api/tokens",
                       data=urllib.parse.urlencode({"username": user, "password": password}),
                       content_type="application/x-www-form-urlencoded")
print("--- token :", status)
if status != 200:
    print(body[:300])
    raise SystemExit(1)
token = json.loads(body)["authToken"]
data_source = json.loads(body).get("dataSource", "mysql")

# menage d'un eventuel reste de test precedent
status, body, _ = call("GET", "/api/session/data/%s/connections" % data_source, token=token)
connections = json.loads(body) if status == 200 else {}
for identifier, conn in connections.items():
    if conn.get("name") == TEST_NAME:
        call("DELETE", "/api/session/data/%s/connections/%s" % (data_source, identifier), token=token)
        print("--- ancien test supprime")

payload = json.dumps({
    "parentIdentifier": "ROOT",
    "name": TEST_NAME,
    "protocol": "rdp",
    "parameters": {"hostname": "192.0.2.10", "port": "3389",
                   "username": "testuser", "password": "testpass",
                   "ignore-cert": "true"},
    "attributes": {},
})
status, body, headers = call("POST", "/api/session/data/%s/connections" % data_source,
                             token=token, data=payload)
print("--- creation :", status)
if status not in (200, 201):
    print(body[:300])
    raise SystemExit(1)

status, body, _ = call("GET", "/api/session/data/%s/connections" % data_source, token=token)
connections = json.loads(body)
found = [(cid, c) for cid, c in connections.items() if c.get("name") == TEST_NAME]
print("--- connexion retrouvee :", found[0][0] if found else "AUCUNE")
if found:
    cid = found[0][0]
    cux = base64.b64encode(("%s" % cid).encode() + b"\x00c\x00mysql").decode()
    print("--- URL de prise en main :")
    print("   ", url_template.replace("@@CUX_ID@@", cux))
    status, _, _ = call("DELETE", "/api/session/data/%s/connections/%s" % (data_source, cid), token=token)
    print("--- nettoyage :", status)
