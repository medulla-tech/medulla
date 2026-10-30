"""Minimal stand-in for impacket.smbconnection: the "C$" share is a directory
named by FAKE_SMB_DIR, the behaviour is selected by FAKE_SMB_MODE."""
import os

MODE = lambda: os.environ.get("FAKE_SMB_MODE", "")
ROOT = lambda: os.environ["FAKE_SMB_DIR"]


class SessionError(Exception):
    pass


def _name(path):
    return os.path.join(ROOT(), path.replace("\\", "/").split("/")[-1])


class SMBConnection(object):
    def __init__(self, remote, name, sess_port=445, timeout=60):
        with open(os.path.join(ROOT(), "_calls"), "a") as handle:
            handle.write("connect %s port=%s\n" % (remote, sess_port))
        if MODE() == "refused":
            raise ConnectionRefusedError(111, "Connection refused")

    def login(self, user, password, domain=""):
        with open(os.path.join(ROOT(), "_calls"), "a") as handle:
            handle.write("login user=%s domain=%s password=%s\n" % (user, domain, "yes" if password else "no"))
        if MODE() == "logon_failure":
            raise SessionError("SMB SessionError: STATUS_LOGON_FAILURE(The attempted logon is invalid.)")

    def putFile(self, share, path, callback):
        if MODE() == "access_denied":
            raise SessionError("SMB SessionError: STATUS_ACCESS_DENIED({Access Denied} A process has requested access to an object)")
        if MODE() == "no_admin_share":
            raise SessionError("SMB SessionError: STATUS_BAD_NETWORK_NAME({Network Name Not Found})")
        data = b""
        while True:
            block = callback(4096)
            if not block:
                break
            data += block
        with open(_name(path), "wb") as handle:
            handle.write(data)

    def getFile(self, share, path, callback):
        target = _name(path)
        if not os.path.exists(target):
            raise SessionError("SMB SessionError: STATUS_OBJECT_NAME_NOT_FOUND(The object name is not found.)")
        with open(target, "rb") as handle:
            callback(handle.read())

    def deleteFile(self, share, path):
        target = _name(path)
        if os.path.exists(target):
            os.remove(target)
            with open(os.path.join(ROOT(), "_calls"), "a") as handle:
                handle.write("delete %s\n" % os.path.basename(target))

    def logoff(self):
        pass
