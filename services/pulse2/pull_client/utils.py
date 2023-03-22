# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
import os
import socket
import platform
import copy
from subprocess import Popen, PIPE
from threading import Lock


class Singleton(object):
    """
    A thread safe Singleton implementation

    class A(Singleton):
        pass

    a = A.instance()
    """
    __singleton_lock = Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


def get_registry_value(key, subkey, value):
    """
    Utility function to retrieve values from the windows registery
    """
    import _winreg
    try:
        key = getattr(_winreg, key)
        handle = _winreg.OpenKey(key, subkey, 0, _winreg.KEY_READ | _winreg.KEY_WOW64_32KEY)
        (value, type) = _winreg.QueryValueEx(handle, value)
        return value
    except WindowsError:  # pyflakes.ignore
        return None


def get_packages_dir():
    if platform.system() == "Windows":
        openssh = os.path.join(get_registry_value("HKEY_LOCAL_MACHINE",
                                                  "SOFTWARE\Mandriva\OpenSSH",
                                                  "InstallPath"))
        openssh_tmp = os.path.join(openssh, "tmp")
        return str(openssh_tmp)
    else:
        return "/tmp"


def get_launcher_env():
    environ = copy.deepcopy(os.environ)
    if platform.system() == "Windows":
        openssh = get_registry_value("HKEY_LOCAL_MACHINE",
                                     "SOFTWARE\Mandriva\OpenSSH",
                                     "InstallPath")
        openssh_bin = os.path.join(openssh, "bin")

        # FusionInventory 2.3.X
        fusion_registry = get_registry_value("HKEY_LOCAL_MACHINE",
                                             "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\FusionInventory-Agent",
                                             "InstallLocation")
        if fusion_registry:
            if os.path.exists(fusion_registry):
                fusion_bin = os.path.join(fusion_registry, "perl", "bin")

        # FusionInventory 2.2.X
        if not fusion_registry:
            fusion_registry = get_registry_value("HKEY_LOCAL_MACHINE",
                                                "SOFTWARE\FusionInventory-Agent",
                                                "share-dir")
            if fusion_registry:
                if os.path.exists(fusion_registry):
                    fusion = os.path.dirname(fusion_registry)
                    fusion_bin = os.path.join(fusion, "perl", "bin")

        environ["OPENSSH_BIN_PATH"] = str(openssh_bin)
        environ["FUSION_BIN_PATH"] = str(fusion_bin)
        environ["PATH"] += str(os.pathsep + openssh_bin + os.pathsep + fusion_bin)
        environ["CYGWIN_HOME"] = str(openssh)
    else:
        environ["OPENSSH_BIN_PATH"] = "/usr/bin"
        environ["FUSION_BIN_PATH"] = "/usr/bin"
    return environ


def get_hostname():
    """
    Get current system hostname
    """
    return socket.gethostname()


def normalize(addr):
    """
    Normalize a MAC address to UNIX style
    """
    # Determine which delimiter style out input is using
    if "." in addr:
        delimiter = "."
    elif ":" in addr:
        delimiter = ":"
    elif "-" in addr:
        delimiter = "-"
    # Eliminate the delimiter
    m = addr.replace(delimiter, "")
    m = m.lower()
    # Normalize
    n = ":".join(["%s%s" % (m[i], m[i + 1]) for i in range(0, 12, 2)])
    return n


def get_mac_addresses():
    """
    Get list of mac addresses of the current system
    mac address are normalized to UNIX style
    """
    mac_addresses = []
    if platform.system() == "Windows":
        p = Popen("pulse2-ether-list.exe", stdout=PIPE, stderr=PIPE, env=get_launcher_env())
        stdout, stderr = p.communicate()
        for index, line in enumerate(stdout.split("\n")):
            # ignore header
            if index == 0:
                continue
            line = line.strip()
            if line:
                start, card, mac, ip, netmask, gateway, end = line.split("|||")
                mac_addresses.append(mac)

    return [normalize(mac) for mac in mac_addresses]
