#!/usr/bin/env python3
"""Reproduit le polling de statut pendant qu'un job tourne.

Pendant toute la duree du job, on interroge browse_parc_status comme le fait le
navigateur, puis on serialise le resultat EXACTEMENT comme l'agent
(sanitize_for_xmlrpc + xmlrpc.client.dumps). Toute anomalie est signalee.
"""
import sys
import time
import xmlrpc.client

sys.path.insert(0, "/usr/lib/python3/dist-packages")
import mmc.plugins.admin as admin          # noqa: E402
from mmc.agent import sanitize_for_xmlrpc  # noqa: E402

start = admin.browse_parc_start({
    "action": "discover", "mode": "network", "target": "172.16.12.128/28",
    "port": 5985, "ps_setup": False})
job = start.get("job")
print("--- job = %s (%s)" % (job, start.get("ok")))
if not job:
    print("--- demarrage impossible : %s" % start)
    sys.exit(1)

failures = []
polls = 0
offset = 0
began = time.time()
while time.time() - began < 25:
    polls += 1
    try:
        result = admin.browse_parc_status(job, offset)
    except Exception as exc:
        failures.append(("exception appel", type(exc).__name__, str(exc)[:200]))
        break
    if not isinstance(result, dict):
        failures.append(("resultat non dict", type(result).__name__, repr(result)[:200]))
        break
    try:
        payload = sanitize_for_xmlrpc(result)
        body = xmlrpc.client.dumps((payload,), methodresponse=True, allow_none=True)
    except Exception as exc:
        failures.append(("exception serialisation", type(exc).__name__, str(exc)[:300]))
        break

    lines = result.get("log") or []
    offset += len(lines)
    status = result.get("status")
    if status in ("done", "error", "cancelled"):
        print("--- job termine (%s) apres %d polls, %d octets" % (status, polls, len(body)))
        break
    time.sleep(0.4)

print("--- %d interrogations" % polls)
if failures:
    print("--- ECHECS :")
    for item in failures:
        print("     %s : %s : %s" % item)
    sys.exit(1)
print("--- aucun echec de serialisation")
