#!/usr/bin/env python3
"""Runs a PowerShell script on a Windows machine over SMB (port 445), no WinRM.

Used by medulla-deploy-agent.sh when a machine exposes SMB but neither WinRM nor
SSH. Needs the "impacket" library (Debian: apt install python3-impacket).

Credentials only come from the environment, never from the command line:
    BP_USERNAME, BP_PASSWORD, BP_DOMAIN (optional), BP_TARGET
The PowerShell script is read on the standard input.

How it works (the same mechanism as Sysinternals PsExec, administrator rights
are required on the target):
  1. log on over SMB and copy the script and a small launcher to C$\\Windows\\Temp
  2. create a one shot service through the service control manager (\\pipe\\svcctl)
     which starts the launcher detached from the service (the SCM would stop a
     long installation after 30 seconds)
  3. poll the result file written by the launcher until it appears
  4. print the output of the script, remove every file, exit with its exit code

Exit codes: the exit code of the script, or
    10 logon / connection failed     11 file transfer failed
    12 could not start the service   13 impacket is not installed
    124 timeout
The standard error tells why ("smb: <phase> failed: <message>").
"""
import argparse
import io
import os
import sys
import time
import uuid

EXIT_CONNECT = 10
EXIT_TRANSFER = 11
EXIT_LAUNCH = 12
EXIT_MISSING = 13
EXIT_TIMEOUT = 124

REMOTE_DIR = "Windows\\Temp"
REMOTE_DIR_ABS = "C:\\Windows\\Temp"
DEFAULT_TIMEOUT = 1800
POLL_SECONDS = float(os.environ.get("BP_SMB_POLL", "2"))


def fail(phase, error, code):
    text = " ".join(str(error).split()) or error.__class__.__name__
    sys.stderr.write("smb: %s failed: %s\n" % (phase, text))
    sys.stderr.flush()
    return code


def load_impacket():
    try:
        from impacket.smbconnection import SMBConnection
        from impacket.dcerpc.v5 import transport, scmr
    except ImportError:
        return None
    return SMBConnection, transport, scmr


def split_user(username, domain):
    # DOMAIN\user -> (DOMAIN, user). user@domain.tld is kept as is: the server
    # resolves it itself.
    if "\\" in username and not domain:
        domain, username = username.split("\\", 1)
    return username, domain


def launcher(ident):
    base = "%s\\bp-%s" % (REMOTE_DIR_ABS, ident)
    return ("@echo off\r\n"
            'powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%(b)s.ps1" > "%(b)s.out" 2>&1\r\n'
            'echo %%ERRORLEVEL%%> "%(b)s.rc.tmp"\r\n'
            'move /y "%(b)s.rc.tmp" "%(b)s.rc" > nul\r\n') % {"b": base}


def put(smb, name, data):
    smb.putFile("C$", "%s\\%s" % (REMOTE_DIR, name), io.BytesIO(data).read)


def get(smb, name):
    chunks = []
    smb.getFile("C$", "%s\\%s" % (REMOTE_DIR, name), chunks.append)
    return b"".join(chunks)


def missing(error):
    text = str(error).upper()
    return "NOT_FOUND" in text or "NO_SUCH_FILE" in text or "PATH_NOT_FOUND" in text


def remove(smb, ident):
    for suffix in (".ps1", ".cmd", ".out", ".rc", ".rc.tmp"):
        try:
            smb.deleteFile("C$", "%s\\bp-%s%s" % (REMOTE_DIR, ident, suffix))
        except Exception:
            pass


def start_service(smb, target, ident, transport, scmr):
    rpc = transport.DCERPCTransportFactory("ncacn_np:%s[\\pipe\\svcctl]" % target)
    rpc.set_smb_connection(smb)
    dce = rpc.get_dce_rpc()
    dce.connect()
    dce.bind(scmr.MSRPC_UUID_SCMR)
    name = "bp%s" % ident[:8]
    manager = scmr.hROpenSCManagerW(dce)["lpScHandle"]
    command = 'cmd.exe /Q /c start "" /b %s\\bp-%s.cmd' % (REMOTE_DIR_ABS, ident)
    service = scmr.hRCreateServiceW(dce, manager, name + "\x00", name + "\x00",
                                    lpBinaryPathName=command + "\x00",
                                    dwStartType=scmr.SERVICE_DEMAND_START)["lpServiceHandle"]
    try:
        try:
            scmr.hRStartServiceW(dce, service)
        except Exception as error:
            # cmd.exe is not a real service: the SCM reports 1053 (it did not
            # answer) once the launcher has been started, which is expected.
            if "1053" not in str(error) and "SERVICE_REQUEST_TIMEOUT" not in str(error).upper():
                raise
    finally:
        try:
            scmr.hRDeleteService(dce, service)
        except Exception:
            pass
        try:
            scmr.hRCloseServiceHandle(dce, service)
            scmr.hRCloseServiceHandle(dce, manager)
        except Exception:
            pass


def decode(data):
    for encoding in ("utf-8", "cp850"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", "replace")


def run(args, script):
    modules = load_impacket()
    if modules is None:
        sys.stderr.write("smb: impacket is not installed (Debian: apt install python3-impacket)\n")
        return EXIT_MISSING
    SMBConnection, transport, scmr = modules

    target = os.environ.get("BP_TARGET", "")
    username, domain = split_user(os.environ.get("BP_USERNAME", ""), os.environ.get("BP_DOMAIN", ""))
    password = os.environ.get("BP_PASSWORD", "")
    ident = uuid.uuid4().hex[:12]

    try:
        smb = SMBConnection(target, target, sess_port=args.port, timeout=15)
        smb.login(username, password, domain)
    except Exception as error:
        return fail("connect", error, EXIT_CONNECT)
    sys.stderr.write("smb: logged on %s\n" % target)

    try:
        try:
            put(smb, "bp-%s.ps1" % ident, b"\xef\xbb\xbf" + script.encode("utf-8"))
            put(smb, "bp-%s.cmd" % ident, launcher(ident).encode("ascii"))
        except Exception as error:
            return fail("transfer", error, EXIT_TRANSFER)
        sys.stderr.write("smb: script copied\n")

        try:
            start_service(smb, target, ident, transport, scmr)
        except Exception as error:
            return fail("start", error, EXIT_LAUNCH)
        sys.stderr.write("smb: script started\n")

        deadline = time.time() + args.timeout
        code = None
        while time.time() < deadline:
            time.sleep(POLL_SECONDS)
            try:
                code = int(decode(get(smb, "bp-%s.rc" % ident)).strip() or 1)
                break
            except Exception as error:
                if not missing(error) and "SHARING_VIOLATION" not in str(error).upper():
                    return fail("wait", error, EXIT_LAUNCH)
        try:
            sys.stdout.write(decode(get(smb, "bp-%s.out" % ident)))
        except Exception:
            pass
        sys.stdout.flush()
        if code is None:
            sys.stderr.write("smb: timed out after %ds\n" % args.timeout)
            return EXIT_TIMEOUT
        return code
    finally:
        remove(smb, ident)
        try:
            smb.logoff()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description="Run a PowerShell script over SMB")
    parser.add_argument("--port", type=int, default=445)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--check", action="store_true", help="only tell whether impacket is available")
    args = parser.parse_args()
    if args.timeout <= 0:
        args.timeout = DEFAULT_TIMEOUT
    if args.check:
        if load_impacket() is None:
            sys.stderr.write("smb: impacket is not installed\n")
            return EXIT_MISSING
        return 0
    script = sys.stdin.read()
    if not script.strip():
        return fail("input", "no PowerShell script on stdin", EXIT_TRANSFER)
    return run(args, script)


if __name__ == "__main__":
    sys.exit(main())
