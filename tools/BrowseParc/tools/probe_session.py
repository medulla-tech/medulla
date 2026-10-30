#!/usr/bin/env python3
"""Ouvre une vraie session XMLRPC et appelle browse_parc_* comme le fait le web.

But : voir la reponse BRUTE de l'agent (marshalling XMLRPC) pour les methodes
browse_parc_*, et mesurer la taille exacte des charges.
"""
import base64
import http.client
import ssl
import sys

HOST = "127.0.0.1"
PORT = 7080
BASIC = base64.b64encode(b"mmc:s3cr3t").decode()


def request(body, cookie=None):
    context = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection(HOST, PORT, context=context, timeout=60)
    headers = {
        "Content-Type": "text/xml",
        "Authorization": "Basic " + BASIC,
    }
    if cookie:
        headers["Cookie"] = cookie
    conn.request("POST", "/", body=body, headers=headers)
    response = conn.getresponse()
    payload = response.read().decode("utf-8", "replace")
    set_cookie = response.getheader("Set-Cookie") or ""
    conn.close()
    return response.status, payload, set_cookie


def call(method, params=None, cookie=None):
    import xmlrpc.client
    body = xmlrpc.client.dumps(tuple(params or ()), methodname=method, allow_none=True)
    return request(body, cookie)


print("=== 1. base.ldapAuth (creation de session)")
status, body, cookie = call("base.ldapAuth", ["mmc", "s3cr3t"])
print("    HTTP %s, cookie=%s" % (status, cookie[:60] if cookie else "(aucun)"))
print("    reponse : %s" % body.strip()[:300])

session = cookie.split(";")[0] if cookie else ""
if not session and "session" in body.lower():
    # L'agent renvoie parfois le cookie dans une entete specifique
    print("    (pas de cookie exploitable)")

print("\n=== 2. admin.browse_parc_agents AVEC la session")
status, body, _ = call("admin.browse_parc_agents", [], session)
print("    HTTP %s, %d octets" % (status, len(body)))
print("    reponse : %s" % body.strip()[:400])

print("\n=== 3. admin.browse_parc_groups_list AVEC la session")
status, body, _ = call("admin.browse_parc_groups_list", [], session)
print("    HTTP %s, %d octets" % (status, len(body)))
print("    reponse : %s" % body.strip()[:400])

print("\n=== 4. admin.browse_parc_start (discover invalide, doit refuser proprement)")
status, body, _ = call("admin.browse_parc_start", [{"action": "discover"}], session)
print("    HTTP %s, %d octets" % (status, len(body)))
print("    reponse : %s" % body.strip()[:400])

sys.exit(0)
