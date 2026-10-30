#!/usr/bin/env python3
"""Mesure le temps de browse_parc_agents et de ses etapes."""
import sys
import time

sys.path.insert(0, "/usr/lib/python3/dist-packages")
import mmc.plugins.admin as admin          # noqa: E402

print("--- browse_parc_agents() :")
began = time.time()
try:
    result = admin.browse_parc_agents()
    print("    duree = %.3fs, ok=%s, %d agent(s)" % (
        time.time() - began, result.get("ok"), len(result.get("agents") or [])))
except Exception as exc:
    print("    ECHEC apres %.3fs : %s" % (time.time() - began, exc))

print("--- _organisation_names() seule :")
began = time.time()
try:
    names = admin.browseparc._organisation_names()
    print("    duree = %.3fs, %d nom(s) : %s" % (time.time() - began, len(names), names))
except Exception as exc:
    print("    ECHEC apres %.3fs : %s" % (time.time() - began, exc))

print("--- _list_agents() seule :")
began = time.time()
try:
    agents = admin.browseparc._list_agents()
    print("    duree = %.3fs, %d agent(s)" % (time.time() - began, len(agents)))
except Exception as exc:
    print("    ECHEC apres %.3fs : %s" % (time.time() - began, exc))
