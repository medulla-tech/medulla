#!/usr/bin/env python3
"""Load / non blocking regression test, run ON the Medulla server.

Reproduces the failure scenario: a long running fleet job must not freeze the
MMC console. The mmc-agent is a Twisted application and, on this instance,
"multithreading" is disabled in /etc/mmc/agent/config.ini: any plugin method
that waits (subprocess, pwsh, mysql) blocks the whole console for every user,
which is what filled the 5 php-fpm workers and produced the 503.

    python3 test_load_on_server.py

Environment: BP_TEST_NET is the network scanned by the long job
(default 172.16.12.0/24).
"""
import os
import sys
import threading
import time
import urllib.request

sys.path.insert(0, "/usr/lib/python3/dist-packages")

PASS = [0]
FAIL = [0]
TEST_NET = os.environ.get("BP_TEST_NET", "172.16.12.0/24")
LATENCIES = []
LATENCIES_LOCK = threading.Lock()


def check(label, condition, detail=""):
    if condition:
        PASS[0] += 1
        print("  ok   %s" % label)
    else:
        FAIL[0] += 1
        print("  FAIL %s %s" % (label, detail))


def timed_get(url, timeout=30):
    began = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            response.read()
            code = response.status
    except Exception as exc:
        return None, time.time() - began, str(exc)
    return code, time.time() - began, ""


def main():
    import mmc.plugins.admin as admin

    print("\n1. Un appel de methode de la page ne bloque pas")
    began = time.time()
    prereq = admin.browse_parc_prerequisites()
    elapsed = time.time() - began
    check("browse_parc_prerequisites < 1s", elapsed < 1.0, "%.3fs" % elapsed)
    check("resultat exploitable", prereq.get("ok") is True, prereq)

    print("\n2. Un job long ne bloque pas la console")
    start = admin.browse_parc_start({
        "action": "discover", "mode": "network", "target": TEST_NET,
        "port": 22, "namefilter": "",
        "username": "compte-de-test", "password": "MotDePasseDeTest"})
    check("job long demarre", start.get("ok") is True, start)
    job = start.get("job")

    urls = [
        "http://127.0.0.1/mmc/index.php",
        "http://127.0.0.1/mmc/main.php?module=admin&submod=admin&action=browseparc",
        "http://127.0.0.1/mmc/main.php?module=admin&submod=admin&action=relaysList",
    ]

    codes = []
    print("     requetes HTTP pendant que le job tourne :")
    for index in range(12):
        for url in urls:
            code, latency, error = timed_get(url)
            codes.append((url.split("action=")[-1].split("&")[0], code, latency, error))
        admin.browse_parc_status(job, 0)
        admin.browse_parc_jobs(5)
        time.sleep(0.2)

    bad = [item for item in codes if item[1] != 200]
    slow = [item for item in codes if item[2] > 5.0]
    worst = max(item[2] for item in codes)
    print("     %d requetes HTTP, latence max %.3fs" % (len(codes), worst))
    check("aucune requete en echec (pas de 503)", not bad, bad[:3])
    check("aucune requete lente (> 5s)", not slow, [(i[0], round(i[2], 2)) for i in slow[:3]])
    check("latence max < 5s", worst < 5.0, "%.3fs" % worst)

    print("\n3. Les appels de statut restent rapides pendant le job")
    worst_call = 0.0
    for _ in range(10):
        began = time.time()
        status = admin.browse_parc_status(job, 0)
        worst_call = max(worst_call, time.time() - began)
        check_once = status.get("ok") is True
        if not check_once:
            break
        time.sleep(0.1)
    check("browse_parc_status < 1s", worst_call < 1.0, "%.3fs" % worst_call)

    print("\n4. Nettoyage")
    cancel = admin.browse_parc_cancel(job)
    check("job annule", cancel.get("ok") is True, cancel)
    time.sleep(1)
    final = admin.browse_parc_status(job, 0)
    print("     statut final: %s" % final.get("status"))

    print("\n=====================================")
    print("%d verifications OK, %d echec(s)" % (PASS[0], FAIL[0]))
    return 1 if FAIL[0] else 0


if __name__ == "__main__":
    sys.exit(main())
