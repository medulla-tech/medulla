#!/usr/bin/env python3
"""Journal des taches d'installation et installation macOS (medulla-deploy-agent.sh).

Les fonctions du script sont extraites et executees avec un faux `ssh` place
dans le PATH : aucune machine reelle n'est contactee. Necessite bash >= 4
(tableaux associatifs), comme le script lui-meme : ignore sinon.

    python3 tests/test_install_logging.py
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = next((p for p in (os.path.join(HERE, "..", "server", "medulla-deploy-agent.sh"),
                           os.path.join(HERE, "..", "medulla-deploy-agent.sh"))
               if os.path.exists(p)), os.path.join(HERE, "..", "server", "medulla-deploy-agent.sh"))
FAILURES = []
CHECKS = [0]

FUNCTIONS = ("json_str", "json_bool", "state_event", "clean_text", "machine_log_path",
             "mlog", "mlog_raw", "classify_failure", "install_info", "inst_ok", "inst_fail",
             "last_marker", "log_markers", "timed", "mac_pick_package",
             "install_agent_ssh_mac", "install_agent", "choose_transport",
             "port_for_transport", "build_win_agent_ps", "ps_run", "install_agent_smb",
             "smb_fallback_possible", "safe_url", "manual_install_command")

FAKE_SSH = r'''#!/bin/bash
cmd="${@: -1}"
echo "$cmd" >> "$FAKE_LOG"
case "$cmd" in
    "exit 0")
        case "$FAKE_CONNECT" in
            refused) echo "ssh: connect to host pc1 port 22: Connection refused" >&2; exit 255;;
            auth) echo "root@pc1: Permission denied (publickey)." >&2; exit 255;;
            dns) echo "ssh: Could not resolve hostname pc1: Name or service not known" >&2; exit 255;;
        esac
        exit 0;;
    "uname -s") [ -n "$FAKE_UNAME" ] && echo "$FAKE_UNAME" && exit 0; exit 127;;
    "uname -m") echo "$FAKE_ARCH"; exit 0;;
    wmic*) [ "$FAKE_UNAME" = "" ] && [ "$FAKE_WINDOWS" = "1" ] && exit 0; exit 1;;
    ver) [ "$FAKE_WINDOWS" = "1" ] && echo "Microsoft Windows [Version 10]" && exit 0; exit 1;;
    "bash -s") cat > /dev/null; echo "$FAKE_LINUX_OUT"; exit "${FAKE_LINUX_RC:-0}";;
    PowerShell*) cat > /dev/null; echo "$FAKE_PS_OUT"; exit "${FAKE_PS_RC:-0}";;
    *mktemp*) cat > /dev/null; echo "/tmp/medulla-agent.AbCdEf"; exit "${FAKE_COPY_RC:-0}";;
    d=*) echo "$FAKE_INSTALL_OUT"; exit "${FAKE_INSTALL_RC:-0}";;
esac
exit 99
'''


FAKE_PWSH = r'''#!/bin/bash
cat > /dev/null
echo "$FAKE_PWSH_OUT"
exit "${FAKE_PWSH_RC:-0}"
'''

FAKE_SMB = r'''#!/usr/bin/env python3
import os, sys
with open(os.environ["FAKE_SMB_LOG"], "a") as handle:
    handle.write("argv=%s user=%s target=%s pw=%s domain=%s stdin=%s\n" % (
        " ".join(sys.argv[1:]), os.environ.get("BP_USERNAME"), os.environ.get("BP_TARGET"),
        "set" if os.environ.get("BP_PASSWORD") else "unset", os.environ.get("BP_DOMAIN"),
        len(sys.stdin.read())))
sys.stderr.write(os.environ.get("FAKE_SMB_ERR", ""))
sys.stdout.write(os.environ.get("FAKE_SMB_OUT", ""))
sys.exit(int(os.environ.get("FAKE_SMB_RC", "0")))
'''


def check(label, condition, detail=""):
    CHECKS[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s %s" % (label, detail))
        FAILURES.append(label)


def bash_ok():
    try:
        out = subprocess.run(["bash", "-c", "echo ${BASH_VERSINFO[0]}"], stdout=subprocess.PIPE).stdout
        return int(out.strip() or 0) >= 4
    except (OSError, ValueError):
        return False


def run_install(work, env, machine="pc1", extra=""):
    """Runs install_agent for one machine; returns (rc, log, info, events, stderr)."""
    state = os.path.join(work, "events.jsonl")
    open(state, "w").close()
    for name in ("logs",):
        shutil.rmtree(os.path.join(work, name), ignore_errors=True)
    os.makedirs(os.path.join(work, "logs"))
    info_file = os.path.join(work, "info")
    if os.path.exists(info_file):
        os.remove(info_file)
    prog = r'''
SCRIPT="$1"
eval "$(for f in %s; do sed -n "/^$f() {/,/^}$/p" "$SCRIPT"; done)"
RED=''; GREEN=''; NC=''; JSON_MODE=1
STATE_FILE="$STATE"; STATE_FD=""; LOG_DIR="$WORK/logs"
USERNAME=root; PORT=22; SSHKEY=""; INSTALL_TIMEOUT=""
AGENT_WIN_URL=""; AGENT_WIN_REFERER=""; AGENT_WIN_INSECURE=0
AGENT_LIN_URL=""; AGENT_LIN_REFERER=""; AGENT_LIN_PATH="$WORK/agent.sh"; AGENT_MAC_DIR="$WORK/mac"
SMB_HELPER="$WORK/smb_helper.py"; PWSH_HOME="$WORK"; DOMAIN=""; PASSWORD="${PASSWORD-}"
declare -A T_METHOD=() T_TPORTS=() T_TOS=()
T_METHOD[pc1]=ssh
%s
BP_INFO_FILE="$WORK/info" install_agent pc1 >/dev/null
echo "RC=$?" >&2
''' % (" ".join(FUNCTIONS), extra)
    full_env = dict(os.environ)
    full_env.update(env)
    full_env.update({"STATE": state, "WORK": work,
                     "PATH": os.path.join(work, "bin") + os.pathsep + os.environ["PATH"]})
    proc = subprocess.run(["bash", "-c", prog, "bash", SCRIPT], env=full_env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = proc.stderr.decode("utf-8", "replace")
    rc = int([l for l in err.splitlines() if l.startswith("RC=")][-1][3:])
    log_path = os.path.join(work, "logs", "%s.log" % machine)
    log = open(log_path).read() if os.path.exists(log_path) else ""
    info = {}
    if os.path.exists(info_file):
        info = json.loads("{" + open(info_file).read() + "}")
    events = [json.loads(line) for line in open(state) if line.strip()]
    return rc, log, info, events, err


def main():
    if not bash_ok():
        print("bash < 4 : tests du script d'installation ignores (a lancer sur le serveur)")
        return 0
    work = tempfile.mkdtemp(prefix="bp-install-test-")
    os.makedirs(os.path.join(work, "bin"))
    os.makedirs(os.path.join(work, "mac"))
    ssh = os.path.join(work, "bin", "ssh")
    open(ssh, "w").write(FAKE_SSH)
    os.chmod(ssh, os.stat(ssh).st_mode | stat.S_IEXEC)
    open(os.path.join(work, "agent.sh"), "w").write("#!/bin/bash\n")
    open(os.path.join(work, "smb_helper.py"), "w").write(FAKE_SMB)
    pwsh = os.path.join(work, "bin", "pwsh")
    open(pwsh, "w").write(FAKE_PWSH)
    os.chmod(pwsh, os.stat(pwsh).st_mode | stat.S_IEXEC)
    open(os.path.join(work, "mac", "Medulla-Agent-mac-arm64-5.6.5-abc.pkg"), "wb").write(b"pkg")
    log_file = os.path.join(work, "ssh.log")
    base = {"FAKE_LOG": log_file, "FAKE_CONNECT": "", "FAKE_UNAME": "", "FAKE_ARCH": "",
            "FAKE_WINDOWS": "", "FAKE_LINUX_RC": "0", "FAKE_LINUX_OUT": "",
            "FAKE_INSTALL_RC": "0", "FAKE_INSTALL_OUT": "", "FAKE_COPY_RC": "0",
            "FAKE_SMB_LOG": os.path.join(work, "smb.log"), "FAKE_SMB_RC": "0", "FAKE_SMB_OUT": "",
            "FAKE_SMB_ERR": "", "FAKE_PWSH_OUT": "", "FAKE_PWSH_RC": "0"}

    def env(**kw):
        merged = dict(base)
        merged.update(kw)
        return merged

    try:
        print("\n1. Linux : chaque tache est journalisee")
        rc, log, info, events, err = run_install(work, env(FAKE_UNAME="Linux"))
        check("installation reussie", rc == 0, err)
        for step in ("[transport]", "[connect] start", "[connect] ok", "[detect] ok - linux",
                     "[install] start", "[done] ok"):
            check("journal: %s" % step, step in log, log)
        check("resultat: code ok", info.get("code") == "ok" and info.get("system") == "linux", info)
        check("evenements step emis", any(e.get("event") == "step" and e.get("step") == "install"
                                          for e in events), events)
        check("les etapes vont aussi dans le journal de la tache (stderr)", "pc1: [install] start" in err, err)

        print("\n2. Echecs de connexion : etape et cause")
        for mode, code in (("refused", "connection_refused"), ("auth", "auth_failed"),
                           ("dns", "dns_failed")):
            rc, log, info, events, err = run_install(work, env(FAKE_CONNECT=mode, FAKE_UNAME="Linux"))
            check("%s: echec" % mode, rc != 0)
            check("%s: etape connect" % mode, info.get("step") == "connect", info)
            check("%s: code %s" % (mode, code), info.get("code") == code, info)
            check("%s: message distant conserve" % mode, len(info.get("reason", "")) > 5, info)
            check("%s: journal contient l'echec" % mode, "[connect] fail" in log, log)

        print("\n3. Linux : l'installeur echoue")
        rc, log, info, events, err = run_install(
            work, env(FAKE_UNAME="Linux", FAKE_LINUX_RC="3", FAKE_LINUX_OUT="dpkg: error processing package"))
        check("etape install", info.get("step") == "install" and info.get("code") == "installer_failed", info)
        check("sortie complete dans le journal", "dpkg: error processing package" in log, log)
        check("code de sortie conserve", rc == 3, rc)

        print("\n4. macOS")
        rc, log, info, events, err = run_install(work, env(FAKE_UNAME="Darwin", FAKE_ARCH="arm64"))
        check("macOS: installation reussie", rc == 0, err)
        check("macOS: systeme reconnu", info.get("system") == "macos", info)
        for step in ("[prepare] ok - package Medulla-Agent-mac-arm64-5.6.5-abc.pkg", "[transfer] ok",
                     "[install] ok", "[done] ok"):
            check("macOS journal: %s" % step, step in log, log)
        calls = open(log_file).read()
        check("macOS: installer(8) appele", "/usr/sbin/installer -pkg" in calls, calls)
        check("macOS: sudo sans mot de passe", "sudo -n /usr/sbin/installer" in calls, calls)
        check("macOS: nettoyage du dossier temporaire", "rm -rf" in calls, calls)

        rc, log, info, events, err = run_install(work, env(FAKE_UNAME="Darwin", FAKE_ARCH="x86_64"))
        check("macOS sans paquet pour l'architecture: echec", rc != 0)
        check("macOS: etape prepare / code no_package",
              info.get("step") == "prepare" and info.get("code") == "no_package", info)
        check("macOS: l'architecture est citee", "x86_64" in info.get("reason", ""), info)

        rc, log, info, events, err = run_install(
            work, env(FAKE_UNAME="Darwin", FAKE_ARCH="arm64", FAKE_INSTALL_RC="1",
                      FAKE_INSTALL_OUT="sudo: a password is required"))
        check("macOS sans sudo: code sudo_required", info.get("code") == "sudo_required", info)
        check("macOS sans sudo: etape install", info.get("step") == "install", info)

        rc, log, info, events, err = run_install(
            work, env(FAKE_UNAME="Darwin", FAKE_ARCH="arm64", FAKE_COPY_RC="1"))
        check("macOS: echec de copie = etape transfer", info.get("step") == "transfer", info)

        print("\n5. Windows detecte via SSH")
        rc, log, info, events, err = run_install(
            work, env(FAKE_WINDOWS="1", FAKE_PS_OUT="BPSTEP:download", FAKE_PS_RC="1"),
            extra='AGENT_WIN_URL="https://x/a.exe"')
        check("windows: systeme reconnu", info.get("system") == "windows", info)
        check("windows: l'etape atteinte vient du marqueur", info.get("step") == "download"
              and info.get("code") == "download_failed", info)
        rc, log, info, events, err = run_install(work, env())
        check("systeme non identifiable: echec explicite", info.get("step") == "detect", info)

        print("\n6. Classification")
        cases = (
            ("ssh", "connect", 255, "Permission denied (publickey).", "auth_failed"),
            ("winrm", "connect", 1, "Access is denied", "auth_failed"),
            ("winrm", "connect", 1, "WinRM cannot process the request", "winrm_unreachable"),
            ("winrm", "connect", 1, "OpenError: [10.0.0.1] Connecting to remote server failed with the following error message : Authorization failed", "auth_failed"),
            ("winrm", "connect", 1, "Connecting to remote server failed with the following error message : MI_RESULT_FAILED", "winrm_unreachable"),
            ("winrm", "download", 1, "Invoke-WebRequest : Unable to connect to the remote server", "download_failed"),
            ("winrm", "install", 1, "Installer exit code 1603", "installer_failed"),
            ("ssh", "install", 124, "", "timeout"),
            ("ssh", "install", 1, "No space left on device", "disk_full"),
            ("ssh", "connect", 255, "ssh: connect to host x port 22: No route to host", "unreachable"),
            ("ssh", "install", 1, "sudo: command not found", "installer_failed"),
        )
        prog = 'eval "$(for f in clean_text classify_failure; do sed -n "/^$f() {/,/^}$/p" "$1"; done)"; INSTALL_TIMEOUT=60; classify_failure "$2" "$3" "$4" "$5"; echo "$FAIL_STEP|$FAIL_CODE"'
        for transport, step, rc_value, text, code in cases:
            out = subprocess.run(["bash", "-c", prog, "bash", SCRIPT, transport, step, str(rc_value), text],
                                 stdout=subprocess.PIPE).stdout.decode().strip()
            check("%s -> %s" % (text[:40] or "timeout", code), out.endswith("|" + code), out)

        print("\n6 bis. Classification SMB")
        for text, code in (("smb: connect failed: SMB SessionError: STATUS_LOGON_FAILURE(The attempted logon is invalid.)", "auth_failed"),
                           ("smb: transfer failed: SMB SessionError: STATUS_ACCESS_DENIED(Access Denied)", "admin_required"),
                           ("smb: start failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied", "admin_required"),
                           ("smb: transfer failed: STATUS_BAD_NETWORK_NAME(Network Name Not Found)", "smb_unavailable"),
                           ("smb: impacket is not installed (Debian: apt install python3-impacket)", "smb_client_missing"),
                           ("smb: connect failed: [Errno 111] Connection refused", "connection_refused"),
                           ("smb: connect failed: timed out", "unreachable")):
            out = subprocess.run(["bash", "-c", prog, "bash", SCRIPT, "smb", "connect", "10", text],
                                 stdout=subprocess.PIPE).stdout.decode().strip()
            check("smb %s -> %s" % (text[11:45], code), out.endswith("|" + code), out)

        print("\n6 ter. Windows via SMB (sans WinRM)")
        smb = 'T_METHOD[pc1]=smb; T_TPORTS[pc1]=445; AGENT_WIN_URL="https://x/a.exe"; PASSWORD="S3cretValue"; USERNAME=admin'
        open(os.path.join(work, "smb.log"), "w").close()
        rc, log, info, events, err = run_install(
            work, env(FAKE_SMB_OUT="BPSTEP:download\nBPSTEP:install\n"), extra=smb)
        check("smb: installation reussie", rc == 0, err)
        check("smb: transport et systeme", info.get("transport") == "smb" and info.get("system") == "windows", info)
        for step in ("[transport] ok - smb on port 445", "[connect] ok", "[download] ok", "[install] ok", "[done] ok"):
            check("smb journal: %s" % step, step in log, log)
        helper_log = open(os.path.join(work, "smb.log")).read()
        check("smb: port 445 et delai en argument", "argv=--port 445" in helper_log, helper_log)
        check("smb: identifiants par l'environnement", "user=admin target=pc1 pw=set" in helper_log, helper_log)
        check("smb: le mot de passe n'est pas dans les arguments", "S3cretValue" not in helper_log)
        check("smb: le script est envoye sur l'entree standard", "stdin=0" not in helper_log, helper_log)
        blob = log + err + json.dumps(events) + json.dumps(info)
        check("smb: mot de passe absent des journaux", "S3cretValue" not in blob)

        rc, log, info, events, err = run_install(
            work, env(FAKE_SMB_RC="10", FAKE_SMB_ERR="smb: connect failed: SMB SessionError: STATUS_LOGON_FAILURE(The attempted logon is invalid.)"),
            extra=smb)
        check("smb: echec d'authentification", info.get("step") == "connect" and info.get("code") == "auth_failed", info)
        check("smb: le message distant est conserve", "STATUS_LOGON_FAILURE" in info.get("reason", ""), info)
        rc, log, info, events, err = run_install(
            work, env(FAKE_SMB_RC="11", FAKE_SMB_ERR="smb: transfer failed: SMB SessionError: STATUS_ACCESS_DENIED(Access Denied)"),
            extra=smb)
        check("smb: droits insuffisants", info.get("step") == "transfer" and info.get("code") == "admin_required", info)
        rc, log, info, events, err = run_install(
            work, env(FAKE_SMB_RC="13", FAKE_SMB_ERR="smb: impacket is not installed (Debian: apt install python3-impacket)"),
            extra=smb)
        check("smb: client absent", info.get("step") == "connect" and info.get("code") == "smb_client_missing", info)
        rc, log, info, events, err = run_install(
            work, env(FAKE_SMB_RC="1", FAKE_SMB_OUT="BPSTEP:download\nInvoke-WebRequest : Unable to connect to the remote server\n"),
            extra=smb)
        check("smb: l'etape atteinte vient du marqueur",
              info.get("step") == "download" and info.get("code") == "download_failed", info)
        check("smb: connexion marquee reussie avant l'echec", "[connect] ok" in log, log)
        rc, log, info, events, err = run_install(work, env(FAKE_SMB_RC="124", FAKE_SMB_ERR="smb: timed out after 60s"), extra=smb + "; INSTALL_TIMEOUT=60")
        check("smb: delai depasse", info.get("code") == "timeout", info)
        rc, log, info, events, err = run_install(work, env(), extra=smb + '; SMB_HELPER="$WORK/absent.py"')
        check("smb: helper absent = client manquant", info.get("code") == "smb_client_missing", info)

        print("\n6 quater. Choix du transport")
        for method, ports, expected in (("", "445", "smb"), ("", "445,3389", "smb"), ("", "5985,445", "winrm"),
                                        ("", "22,445", "ssh"), ("smb", "", "smb"), ("", "3389", ""),
                                        ("winrm", "445", "winrm")):
            prog_t = ('eval "$(for f in choose_transport; do sed -n "/^$f() {/,/^}$/p" "$1"; done)";'
                      ' declare -A T_METHOD=() T_TPORTS=(); T_METHOD[m]="$2"; T_TPORTS[m]="$3"; choose_transport m')
            out = subprocess.run(["bash", "-c", prog_t, "bash", SCRIPT, method, ports, ""],
                                 stdout=subprocess.PIPE).stdout.decode().strip()
            check("transport %s ports [%s] -> %s" % (method or "auto", ports, expected or "inconnu"), out == expected, out)
        for transport, expected in (("smb", "445"), ("winrm", "5985"), ("ssh", "22")):
            out = subprocess.run(["bash", "-c", 'eval "$(sed -n "/^port_for_transport() {/,/^}$/p" "$1")"; PORT=5985; port_for_transport m "$2"',
                                  "bash", SCRIPT, transport], stdout=subprocess.PIPE).stdout.decode().strip()
            check("port du transport %s" % transport, out == expected, out)

        print("\n6 quinquies. WinRM injoignable : repli sur SMB")
        winrm = 'T_METHOD[pc1]=winrm; T_TPORTS[pc1]="5985,445"; AGENT_WIN_URL="https://x/a.exe"'
        rc, log, info, events, err = run_install(
            work, env(FAKE_PWSH_RC="1", FAKE_PWSH_OUT="OpenError: Connecting to remote server failed with the following error message : MI_RESULT_FAILED",
                      FAKE_SMB_OUT="BPSTEP:download\nBPSTEP:install\n"), extra=winrm)
        check("repli: installation reussie par SMB", rc == 0 and info.get("transport") == "smb", (rc, info, err))
        check("repli: l'echec WinRM est journalise", "winrm: winrm_unreachable, trying smb" in log, log)
        rc, log, info, events, err = run_install(
            work, env(FAKE_PWSH_RC="1", FAKE_PWSH_OUT="Connecting to remote server failed with the following error message : Authorization failed"),
            extra=winrm)
        check("pas de repli quand les identifiants sont refuses", info.get("transport") == "winrm" and info.get("code") == "auth_failed", info)
        rc, log, info, events, err = run_install(
            work, env(FAKE_PWSH_RC="1", FAKE_PWSH_OUT="MI_RESULT_FAILED"),
            extra='T_METHOD[pc1]=winrm; T_TPORTS[pc1]="5985"; AGENT_WIN_URL="https://x/a.exe"')
        check("pas de repli sans port 445", info.get("transport") == "winrm", info)
        rc, log, info, events, err = run_install(
            work, env(FAKE_PWSH_RC="1", FAKE_PWSH_OUT="BPSTEP:download\nInvoke-WebRequest failed", FAKE_SMB_OUT="BPSTEP:download\n"), extra=winrm)
        check("pas de repli quand WinRM a deja execute le script (marqueur)", info.get("transport") == "winrm", info)

        print("\n6 sexies. Installation manuelle proposee quand SSH echoue")
        url = 'AGENT_LIN_URL="https://med.example/medulla_agent/abc/Medulla-Agent-linux-MINIMAL-latest.sh"; AGENT_LIN_REFERER="https://med.example/"'
        rc, log, info, events, err = run_install(work, env(FAKE_CONNECT="refused", FAKE_UNAME="Linux"), extra=url)
        expected = ("curl -fsSk -e 'https://med.example/' "
                    "'https://med.example/medulla_agent/abc/Medulla-Agent-linux-MINIMAL-latest.sh' | sudo bash")
        check("ssh refuse: commande manuelle fournie", info.get("manual") == expected, info)
        check("la commande figure dans le journal de la machine", expected in log, log)
        rc, log, info, events, err = run_install(work, env(FAKE_CONNECT="auth", FAKE_UNAME="Linux"),
                                                 extra='AGENT_LIN_URL="https://med.example/downloads/lin/a.sh"')
        check("sans referer: curl simple",
              info.get("manual") == "curl -fsSk 'https://med.example/downloads/lin/a.sh' | sudo bash", info)
        rc, log, info, events, err = run_install(work, env(FAKE_CONNECT="refused", FAKE_UNAME="Linux"))
        check("sans URL connue: pas de commande", "manual" not in info, info)
        rc, log, info, events, err = run_install(
            work, env(FAKE_UNAME="Linux", FAKE_LINUX_RC="3", FAKE_LINUX_OUT="dpkg: error"), extra=url)
        check("echec de l'installeur: pas de commande", "manual" not in info, info)
        rc, log, info, events, err = run_install(
            work, env(FAKE_UNAME="Linux", FAKE_LINUX_RC="1", FAKE_LINUX_OUT="sudo: a password is required"), extra=url)
        check("sudo requis: commande fournie", "sudo bash" in info.get("manual", ""), info)
        rc, log, info, events, err = run_install(work, env(FAKE_WINDOWS="1", FAKE_PS_OUT="BPSTEP:download", FAKE_PS_RC="1"),
                                                 extra=url + '; AGENT_WIN_URL="https://x/a.exe"')
        check("Windows: pas de commande Linux", "manual" not in info, info)
        rc, log, info, events, err = run_install(work, env(FAKE_UNAME="Darwin", FAKE_ARCH="arm64", FAKE_INSTALL_RC="1",
                                                           FAKE_INSTALL_OUT="sudo: a password is required"), extra=url)
        check("macOS: pas de commande Linux", "manual" not in info, info)
        for value, good in (("https://a.b/x/y.sh", True), ("http://a/b?c=d", True), ("https://a/x y", False),
                            ("https://a/x'y", False), ("https://a/$(id)", False), ("ftp://a/b", False),
                            ("https://a/x;id", False), ("https://a/`id`", False), ("https://a/x|y", False)):
            res = subprocess.run(["bash", "-c", 'eval "$(sed -n "/^safe_url() {/,/^}$/p" "$1")"; safe_url "$2"',
                                  "bash", SCRIPT, value]).returncode
            check("URL %s %s" % (value, "acceptee" if good else "refusee"), (res == 0) == good, res)

        print("\n7. Le mot de passe ne figure jamais dans les journaux")
        rc, log, info, events, err = run_install(
            work, env(FAKE_UNAME="Linux", PASSWORD="S3cretValue"),
            extra='PASSWORD="S3cretValue"')
        blob = log + err + json.dumps(events) + json.dumps(info)
        check("mot de passe absent", "S3cretValue" not in blob)
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
