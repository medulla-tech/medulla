#!/usr/bin/env python3
"""Fake medulla-deploy-agent.sh used by the unit tests.

It speaks exactly the same command line contract as the real script so the
Python backend can be exercised without touching a live server.
"""
import json
import os
import sys
import time


def arg_values(argv, name):
    values = []
    for item in argv:
        if item.startswith(name + "="):
            values.append(item[len(name) + 1:])
    return values


def main():
    argv = sys.argv[1:]
    state_file = (arg_values(argv, "--state-file") or [""])[0]
    targets = (arg_values(argv, "--targets") or [""])[0]
    target = (arg_values(argv, "--target") or [""])[0]

    def emit(event):
        if state_file:
            with open(state_file, "a") as handle:
                handle.write(json.dumps(event) + "\n")

    if "--check-prereq" in argv:
        print(json.dumps({"status": "ok", "prerequisites": {
            "pwsh": True, "wsman": True, "nmap": True,
            "python3": True, "mysql": True, "dig": True}}))
        return 0

    if "--uuid-lookup" in argv:
        emit({"event": "start", "mode": "uuid-lookup"})
        machines = {}
        for line in sys.stdin.read().splitlines():
            host = line.strip()
            if not host:
                continue
            known = host.startswith("known")
            info = {
                "hostname": host if known else "",
                "uuid": ("UUID-" + host.upper()) if known else "",
                "jid": (host + "@relay") if known else "",
                "known": known,
            }
            machines[host] = info
            event = {"event": "machine_uuid", "host": host}
            event.update(info)
            emit(event)
        emit({"event": "end", "status": "ok"})
        print(json.dumps({"status": "ok", "mode": "uuid-lookup", "machines": machines}))
        return 0

    if "--ps-setup" in argv:
        print(json.dumps({"status": "ok", "wsman": True}))
        return 0

    if "--list-ous" in argv:
        emit({"event": "start", "mode": "list-ous"})
        for name, dn in (("Users", "OU=Users,DC=test,DC=lan"),
                         ("Computers", "OU=Computers,DC=test,DC=lan")):
            emit({"event": "ou", "name": name, "dn": dn, "canonical": "test.lan/" + name})
        emit({"event": "end", "status": "ok"})
        print(json.dumps({"status": "ok", "ous": [
            {"name": "Users", "dn": "OU=Users,DC=test,DC=lan", "canonical": "test.lan/Users"},
            {"name": "Computers", "dn": "OU=Computers,DC=test,DC=lan", "canonical": "test.lan/Computers"}]}))
        return 0

    if "--discover" in argv:
        if target == "10.0.0.0/24":
            machines = [
                {"target": "pc1.test.lan", "name": "pc1.test.lan", "ip": "10.0.0.1",
                 "source": "network", "ou": "", "os": "", "installed": False,
                 "ports": [3389, 5985], "services": ["rdp", "winrm"]},
                {"target": "pc2.test.lan", "name": "pc2.test.lan", "ip": "10.0.0.2",
                 "source": "network", "ou": "", "os": "", "installed": True,
                 "ports": [22, 3389], "services": ["ssh", "rdp"]},
            ]
        else:
            machines = []
        # Prove the password travelled through the environment and not argv
        sys.stderr.write("password-in-env=%s\n" % bool(os.environ.get("BROWSE_PARC_PASSWORD")))
        emit({"event": "start", "mode": "discover", "total": len(machines)})
        for machine in machines:
            emit({"event": "machine", "machine": machine})
        emit({"event": "end", "status": "ok", "total": len(machines)})
        print(json.dumps({"status": "ok", "mode": "discover",
                          "total": len(machines), "machines": machines}))
        return 0

    # install
    if targets:
        hosts = [item for item in targets.split(",") if item]
    else:
        hosts = []
    if target == "slow" or "slow" in hosts:
        # Used to test the cancellation of a running job.
        time.sleep(30)
    emit({"event": "start", "mode": "install", "total": len(hosts)})
    results = []
    for index, host in enumerate(hosts):
        time.sleep(0.05)
        ok = not host.startswith("ko")
        item = {"target": host, "name": host, "status": "ok" if ok else "ko"}
        if not ok:
            item.update({"transport": "ssh", "system": "linux", "step": "connect",
                         "code": "auth_failed", "reason": "Permission denied (publickey)"})
        results.append(item)
        if state_file:
            logdir = os.path.join(os.path.dirname(state_file), "logs")
            os.makedirs(logdir, exist_ok=True)
            with open(os.path.join(logdir, host + ".log"), "w") as handle:
                handle.write("2026-01-01 10:00:00 [connect] %s\n" % ("ok" if ok else "fail - auth_failed"))
        emit({"event": "step", "target": host, "step": "connect",
              "status": "ok" if ok else "fail", "detail": "", "ts": 0})
        emit({"event": "progress", "done": index + 1, "total": len(hosts),
              "target": host, "ok": ok})
    ko = len([item for item in results if item["status"] == "ko"])
    emit({"event": "end", "status": "ok", "ok": len(results) - ko, "ko": ko,
          "total": len(results), "results": results})
    print(json.dumps({"status": "ok", "mode": "install", "total": len(results),
                      "ok": len(results) - ko, "ko": ko, "results": results}))
    return 1 if ko else 0


if __name__ == "__main__":
    sys.exit(main())
