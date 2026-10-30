#!/usr/bin/env python3
"""Compare une session RDP utilisable et une cassee, pour definir un critere.

Ouvre une session guacd avec des identifiants factices (aucun secret reel) et
observe la sequence d'instructions et le message d'erreur eventuel.
"""
import os
import sys
import time

sys.path.insert(0, "/tmp")
import guacd_probe  # noqa: E402

CANDIDATS = [
    ("kno.medulla.lan", "xrdp casse (session RDP impossible)"),
    ("172.16.13.7", "serveur RDP utilisable"),
    ("172.16.13.61", "serveur RDP utilisable"),
]

for host, etat in CANDIDATS:
    parameters = {
        "protocol": "rdp",
        "hostname": host,
        "port": "3389",
        "username": "browseparc-probe",
        "password": "browseparc-probe",
        "security": "rdp",
        "ignore-cert": "true",
        "color-depth": "16",
        "width": "800",
        "height": "600",
    }
    os.environ["BP_GUACD_SPAN"] = "6"
    began = time.time()
    result = guacd_probe.drive_guacd(parameters)
    duree = time.time() - began
    instr = result["instructions"]
    affichage = any(i in ("img", "blob", "sync", "png", "cursor", "rect", "cfill")
                    for i in instr)
    print("--- %-18s (%s)" % (host, etat))
    print("    duree=%.1fs  affichage=%s  ferme=%s" % (duree, affichage, result.get("closed")))
    print("    instructions=%s" % ", ".join(instr[-8:]))
    print("    erreur=%r  (stable=%ss)" % (result["error"], result.get("alive_for")))
    print()
