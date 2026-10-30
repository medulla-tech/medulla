import os
import re

MSRPC_UUID_SCMR = "367ABB81-9844-35F1-AD32-98F038001003"
SERVICE_DEMAND_START = 3
ROOT = lambda: os.environ["FAKE_SMB_DIR"]


def _log(text):
    with open(os.path.join(ROOT(), "_calls"), "a") as handle:
        handle.write(text + "\n")


def hROpenSCManagerW(dce):
    return {"lpScHandle": "manager"}


def hRCreateServiceW(dce, manager, name, display, lpBinaryPathName="", dwStartType=0):
    _log("service-create %s" % lpBinaryPathName.rstrip("\x00"))
    return {"lpServiceHandle": lpBinaryPathName.rstrip("\x00")}


def hRStartServiceW(dce, service):
    mode = os.environ.get("FAKE_SMB_MODE", "")
    if mode == "start_denied":
        raise Exception("DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied")
    ident = re.search(r"bp-([0-9a-f]+)\.cmd", service).group(1)
    base = os.path.join(ROOT(), "bp-%s" % ident)
    if mode != "never":
        with open(base + ".out", "w") as handle:
            handle.write(os.environ.get("FAKE_SMB_OUT", "BPSTEP:download\r\nBPSTEP:install\r\n"))
        with open(base + ".rc", "w") as handle:
            handle.write("%s \r\n" % os.environ.get("FAKE_SMB_RC", "0"))
        script = open(base + ".ps1", "rb").read()
        with open(os.path.join(ROOT(), "_script"), "wb") as handle:
            handle.write(script)
    raise Exception("SCMR SessionError: code: 0x41d - ERROR_SERVICE_REQUEST_TIMEOUT - The service did not respond to the start or control request in a timely fashion.")


def hRDeleteService(dce, service):
    _log("service-delete")


def hRCloseServiceHandle(dce, handle):
    pass
