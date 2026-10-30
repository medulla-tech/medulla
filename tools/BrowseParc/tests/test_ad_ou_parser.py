#!/usr/bin/env python3
"""Verifie le parser des unites d'organisation (et des conteneurs) du script.

ps_json_parse_ous() vit dans medulla-deploy-agent.sh : il recoit la reponse
JSON du serveur Active Directory et la transforme en une ligne par noeud.
C'est lui qui decide quelles branches meritent d'apparaitre, il est donc teste
avec des reponses simulees - aucun annuaire n'est necessaire.

Run:  python3 test_ad_ou_parser.py
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "server", "medulla-deploy-agent.sh")

FAILURES = []
CHECKS = [0]


def check(label, condition, detail=""):
    CHECKS[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s%s" % (label, (" -> %s" % detail) if detail else ""))
        FAILURES.append(label)


def extract_parser():
    """Le code python embarque dans ps_json_parse_ous()."""
    source = open(SCRIPT, encoding="utf-8").read()
    start = source.index("ps_json_parse_ous() {")
    body = source[start:]
    py = body.index("python3 -c '") + len("python3 -c '")
    end = body.index("\n'\n", py)
    code = body[py:end]
    return code.replace("'\"'\"'", "'")


def parse(code, payload):
    proc = subprocess.run([sys.executable, "-c", code], input=payload,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          universal_newlines=True)
    rows = []
    for line in proc.stdout.strip().splitlines():
        if not line:
            continue
        columns = line.split("\t")
        if columns[0] == "__ERROR__":
            rows.append({"error": columns[1] if len(columns) > 1 else ""})
            continue
        while len(columns) < 7:
            columns.append("")
        rows.append({
            "name": columns[0], "dn": columns[1], "canonical": columns[2],
            "kind": columns[3], "machines": int(columns[4] or 0),
            "total": int(columns[5] or 0), "parent": columns[6],
        })
    return rows


ANSWER = """{"ok":true,"items":[
{"Name":"medulla","DistinguishedName":"DC=medulla,DC=lan","CanonicalName":"medulla.lan","Kind":"domain","Direct":1,"Total":9},
{"Name":"Servers","DistinguishedName":"OU=Servers,DC=medulla,DC=lan","CanonicalName":"medulla.lan/Servers","Kind":"ou","Direct":3,"Total":5},
{"Name":"DMZ","DistinguishedName":"OU=DMZ,OU=Servers,DC=medulla,DC=lan","CanonicalName":"medulla.lan/Servers/DMZ","Kind":"ou","Direct":2,"Total":2},
{"Name":"Postes","DistinguishedName":"OU=Postes,DC=medulla,DC=lan","CanonicalName":"medulla.lan/Postes","Kind":"ou","Direct":2,"Total":2},
{"Name":"Vide","DistinguishedName":"OU=Vide,DC=medulla,DC=lan","CanonicalName":"medulla.lan/Vide","Kind":"ou","Direct":0,"Total":0},
{"Name":"Computers","DistinguishedName":"CN=Computers,DC=medulla,DC=lan","CanonicalName":"medulla.lan/Computers","Kind":"container","Direct":2,"Total":2},
{"Name":"Users","DistinguishedName":"CN=Users,DC=medulla,DC=lan","CanonicalName":"medulla.lan/Users","Kind":"container","Direct":0,"Total":0}
]}"""


def main():
    code = extract_parser()

    print("\n1. Un noeud par element, dans l'ordre de l'annuaire")
    rows = parse(code, ANSWER)
    names = [r.get("name") for r in rows if not r.get("error")]
    check("les erreurs ne polluent pas la liste", not any(r.get("error") for r in rows))
    check("le domaine est present", "medulla" in names, names)
    check("les OU sont presentes", "Servers" in names and "Postes" in names, names)
    check("le conteneur CN=Computers est present", "Computers" in names, names)

    print("\n2. Seules les branches contenant des machines sont gardees")
    check("OU vide ecartee", "Vide" not in names, names)
    check("conteneur vide ecarte", "Users" not in names, names)

    print("\n3. Hierarchie")
    by = {r.get("name"): r for r in rows if not r.get("error")}
    check("le domaine est la racine", by["medulla"]["parent"] == "DC=lan",
          by["medulla"]["parent"])
    check("une OU est rattachee au domaine",
          by["Servers"]["parent"] == "DC=medulla,DC=lan", by["Servers"]["parent"])
    check("une sous-OU est rattachee a son parent",
          by["DMZ"]["parent"] == "OU=Servers,DC=medulla,DC=lan", by["DMZ"]["parent"])
    check("le conteneur est rattache au domaine",
          by["Computers"]["parent"] == "DC=medulla,DC=lan", by["Computers"]["parent"])

    print("\n4. Comptages")
    check("machines directes de Servers", by["Servers"]["machines"] == 3,
          by["Servers"]["machines"])
    check("total de Servers inclut la sous-OU", by["Servers"]["total"] == 5,
          by["Servers"]["total"])
    check("total du domaine", by["medulla"]["total"] == 9, by["medulla"]["total"])
    check("comptage du conteneur", by["Computers"]["total"] == 2,
          by["Computers"]["total"])

    print("\n5. Type de noeud")
    check("le domaine est type domain", by["medulla"]["kind"] == "domain",
          by["medulla"]["kind"])
    check("une OU est typee ou", by["Servers"]["kind"] == "ou", by["Servers"]["kind"])
    check("CN=Computers est type conteneur", by["Computers"]["kind"] == "container",
          by["Computers"]["kind"])
    check("un type absent retombe sur ou",
          parse(code, '{"ok":true,"items":[{"Name":"X","DistinguishedName":"OU=X,DC=medulla,DC=lan","Total":1}]}'
                )[0]["kind"] == "ou")

    print("\n6. Reponses degradees")
    rows = parse(code, '{"ok":false,"error":"Authentication failed"}')
    check("erreur de l'annuaire remontee",
          rows and rows[0].get("error") == "Authentication failed", rows)
    rows = parse(code, "pwsh: command not found")
    check("reponse illisible signalee",
          rows and "No JSON answer" in rows[0].get("error", ""), rows)
    rows = parse(code, "\x1b[?1h\x1b[?1l" + ANSWER + "\x1b[?1h")
    # 5 noeuds gardes : le domaine, trois OU et CN=Computers.
    check("sequences terminal ignorees", len(rows) == 5, len(rows))

    print("\n=====================================")
    total = CHECKS[0]
    if FAILURES:
        print("%d verifications, %d echec(s)" % (total, len(FAILURES)))
        print("Echecs: %s" % ", ".join(FAILURES))
        return 1
    print("%d verifications, 0 echec(s)" % total)
    print("TOUS LES TESTS PASSENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
