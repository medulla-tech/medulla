#!/usr/bin/env python3
"""Installation sans WinRM : helper SMB (medulla-deploy-agent-smb.py).

impacket est remplace par tests/fake_impacket (un dossier tient lieu de C$) :
aucune machine reelle n'est contactee.

    python3 tests/test_smb_helper.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HELPER = next((p for p in (os.path.join(HERE, "..", "server", "medulla-deploy-agent-smb.py"),
                           os.path.join(HERE, "..", "medulla-deploy-agent-smb.py"))
               if os.path.exists(p)), None)
FAKE = os.path.join(HERE, "fake_impacket")
FAILURES = []
CHECKS = [0]


def check(label, condition, detail=""):
    CHECKS[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s %s" % (label, detail))
        FAILURES.append(label)


def run(work, mode="", stdin="Write-Output hello", args=(), pythonpath=FAKE, **extra):
    share = os.path.join(work, "share")
    shutil.rmtree(share, ignore_errors=True)
    os.makedirs(share)
    env = dict(os.environ)
    env.update({"PYTHONPATH": pythonpath, "FAKE_SMB_DIR": share, "FAKE_SMB_MODE": mode,
                "BP_SMB_POLL": "0.1", "BP_USERNAME": "admin", "BP_PASSWORD": "S3cretValue",
                "BP_DOMAIN": "", "BP_TARGET": "pc1"})
    env.update(extra)
    proc = subprocess.run([sys.executable, HELPER] + list(args), input=stdin.encode(), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    calls_file = os.path.join(share, "_calls")
    calls = open(calls_file).read() if os.path.exists(calls_file) else ""
    return proc.returncode, proc.stdout.decode(), proc.stderr.decode(), calls, share


def main():
    if HELPER is None:
        print("helper introuvable")
        return 1
    work = tempfile.mkdtemp(prefix="bp-smb-test-")
    try:
        print("\n1. Execution reussie")
        rc, out, err, calls, share = run(work, args=["--timeout", "10"])
        check("code 0", rc == 0, err)
        check("la sortie du script est restituee", "BPSTEP:download" in out and "BPSTEP:install" in out, out)
        script = open(os.path.join(share, "_script"), "rb").read()
        check("le script est copie (UTF-8 avec BOM)", script.startswith(b"\xef\xbb\xbf") and b"Write-Output hello" in script)
        check("service cree avec un lanceur detache",
              'service-create cmd.exe /Q /c start "" /b C:\\Windows\\Temp\\bp-' in calls, calls)
        check("service supprime", "service-delete" in calls, calls)
        left = [n for n in os.listdir(share) if n.startswith("bp-")]
        check("fichiers distants nettoyes", left == [], left)
        check("port SMB transmis", "port=445" in calls, calls)
        check("mot de passe absent des sorties", "S3cretValue" not in out + err + calls)

        print("\n2. Code de sortie du script")
        rc, out, err, calls, share = run(work, FAKE_SMB_RC="3", FAKE_SMB_OUT="BPSTEP:download\nBPSTEP:install\nboom\n")
        check("code du script conserve", rc == 3, (rc, err))
        check("sortie conservee", "boom" in out, out)

        print("\n3. Echecs, avec leur cause")
        rc, out, err, calls, share = run(work, "logon_failure")
        check("authentification refusee: 10", rc == 10, rc)
        check("authentification: cause lisible", "smb: connect failed" in err and "STATUS_LOGON_FAILURE" in err, err)
        check("authentification: mot de passe absent", "S3cretValue" not in err)
        rc, out, err, calls, share = run(work, "refused")
        check("connexion refusee: 10", rc == 10 and "Connection refused" in err, (rc, err))
        rc, out, err, calls, share = run(work, "access_denied")
        check("acces refuse a C$: 11", rc == 11 and "smb: transfer failed" in err and "ACCESS_DENIED" in err, (rc, err))
        rc, out, err, calls, share = run(work, "no_admin_share")
        check("C$ absent: 11", rc == 11 and "BAD_NETWORK_NAME" in err, (rc, err))
        rc, out, err, calls, share = run(work, "start_denied")
        check("service refuse: 12", rc == 12 and "smb: start failed" in err, (rc, err))
        check("service supprime meme apres echec", "service-delete" in calls, calls)
        check("fichiers nettoyes apres echec", [n for n in os.listdir(share) if n.startswith("bp-")] == [])
        rc, out, err, calls, share = run(work, "never", args=["--timeout", "1"])
        check("delai depasse: 124", rc == 124 and "timed out" in err, (rc, err))
        check("delai depasse: fichiers nettoyes", [n for n in os.listdir(share) if n.startswith("bp-")] == [])
        rc, out, err, calls, share = run(work, stdin="")
        check("script vide refuse", rc == 11, (rc, err))

        print("\n4. Compte")
        rc, out, err, calls, share = run(work, BP_USERNAME="CORP\\jdoe")
        check("DOMAINE\\compte decoupe", "login user=jdoe domain=CORP" in calls, calls)
        rc, out, err, calls, share = run(work, BP_USERNAME="jdoe@corp.local")
        check("compte@domaine conserve", "login user=jdoe@corp.local domain=" in calls, calls)
        rc, out, err, calls, share = run(work, BP_USERNAME="admin", BP_DOMAIN="LAB")
        check("domaine fourni a part", "login user=admin domain=LAB" in calls, calls)

        print("\n5. impacket absent")
        broken = os.path.join(work, "broken")
        os.makedirs(os.path.join(broken, "impacket"))
        open(os.path.join(broken, "impacket", "__init__.py"), "w").write("raise ImportError('no impacket')\n")
        rc, out, err, calls, share = run(work, pythonpath=broken)
        check("code 13 et message d'installation", rc == 13 and "impacket is not installed" in err
              and "python3-impacket" in err, (rc, err))
        rc, out, err, calls, share = run(work, pythonpath=broken, args=["--check"])
        check("--check sans impacket: 13", rc == 13, rc)
        rc, out, err, calls, share = run(work, args=["--check"])
        check("--check avec impacket: 0", rc == 0, (rc, err))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print("\n=====================================")
    print("%d verifications, %d echec(s)" % (CHECKS[0], len(FAILURES)))
    if FAILURES:
        print("Echecs: %s" % ", ".join(FAILURES))
        return 1
    print("TOUS LES TESTS PASSENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
