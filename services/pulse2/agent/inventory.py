# -*- test-case-name: pulse2.msc.client.tests.inventory -*-
# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""Checking of needed installed software."""

import os
import socket
import struct
import platform
import logging
from tempfile import NamedTemporaryFile

SYSTEM = platform.system().upper()

if SYSTEM == "WINDOWS":

    from _winreg import ConnectRegistry             #pyflakes.ignore
    from _winreg import OpenKey, CloseKey, EnumKey  #pyflakes.ignore
    from _winreg import HKEY_LOCAL_MACHINE          #pyflakes.ignore
    from win32com.client import Dispatch            #pyflakes.ignore

else:
    import fcntl

from subprocess import Popen, PIPE

from pexceptions import SoftwareCheckError
from ptypes import Component



class WindowsRegistry:
    """Common methods querying the Windows registry"""

    @classmethod
    def get_missing(cls, path, required):
        """
        Checks required entries from the Windows registry.

        @param path: registry path to list of installed software
        @type path: str

        @param required: list of entries to check
        @type required: list

        @return: list of missing entries
        @rtype: list
        """
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        logging.getLogger().debug("Registry: %s " % repr(reg))
        key = OpenKey(reg, path)

        missing = required
        i = 0
        while True:
            try:
                folder = EnumKey(key, i)
                if folder in missing:
                    missing.remove(folder)
                i += 1
            except WindowsError: #pyflakes.ignore
                break
        CloseKey(key)
        return missing

class WMIQueryManager:
    def __init__(self):

        objWMIService = Dispatch("WbemScripting.SWbemLocator")
        self.service = objWMIService.ConnectServer("localhost","root/cimv2")

    def get(self, klass, columns):
        query = self.service.ExecQuery("Select * from %s" % klass)

        for q in query:
            line = []
            for column in columns:
                if hasattr(q, column):
                    line.append(getattr(q, column))
                else:
                    # TODO - log someone
                    line.append(None)
            yield line

class InventoryChecker(Component):

    __component_name__ = "inventory_checker"

    def check_missing(self):
        """
        Looks for missing software to install.

        Related to operating system, this method checks if required
        software is installed or not.

        @return: list of missing entries
        @rtype: generator
        """

        if SYSTEM == "WINDOWS":
            path = self.config.inventory.windows_reg_path
            software_required = self.config.inventory.windows_software_required

            reg_query = WindowsRegistry.get_missing(path, software_required)

            for name in reg_query:
                yield name


        elif SYSTEM == "LINUX":

            distname, version, id = platform.linux_distribution()

            if distname in ("debian", "ubuntu", "mint"):

                software_required = self.config.inventory.debian_software_required
                base_command = "/usr/bin/dpkg -l"

            elif distname in ("redhat", "fedora", "centos"):
                software_required = self.config.inventory.redhat_software_required
                base_command = "/usr/bin/rpm -qa"

            for name in self.posix_shell_query(base_command, software_required):
                yield name

        elif SYSTEM == "DARWIN":
            software_required = self.config.inventory.osx_software_required
            base_command = "/usr/sbin/pkgutil --pkgs"

            for name in self.posix_shell_query(base_command, software_required):
                yield name



    def posix_shell_query(self, base_command, software_required):
        """
        Executes a command filtering required software.

        The query command is formed like this:
        base_command | grep 'software1\|software2\|software3'

        @param base_command: command which lists all installed software
        @type base_command: str

        @param required: list of entries to check
        @type required: list

        @return: list of missing entries
        @rtype: generator
        """

        if len(software_required) > 1:
            filter_exp = "\|".join(software_required)
        else:
            filter_exp = software_required[0]

        # To avoid quote related errors during the parsing,
        # whole command is stored in a temporary file
        # and executed as parameter
        stf = NamedTemporaryFile(mode="w", delete=False)

        cmd_bash =  "%s | grep '%s'" % (base_command, filter_exp)
        stf.write(cmd_bash)
        stf.close()

        command = ["bash", stf.name]
        print ("Inventory check cmd: %s" % repr(command))

        process = Popen(command,
                        stdout=PIPE,
                        stderr=PIPE,
                        close_fds=True,
                       )
        out, err = process.communicate()
        returncode = process.returncode
        if returncode == 0:
            print ("Inventory check out: %s" % repr(out))
            for name in software_required:
                if name not in out:
                    yield name
        else:
            self.logger.warn("Inventory check errcode: %s" % repr(returncode))
            self.logger.warn("Inventory check nok: %s" % repr(out))
            self.logger.warn("Inventory check failed: %s" % repr(err))
            raise SoftwareCheckError(repr(err))

        os.unlink(stf.name)


class MinimalInventory(object):

    def get_network(self):
        raise NotImplementedError

    def get_osname(self):
        system = platform.system()
        if system.upper() == "WINDOWS":
            return "Microsoft %s" % system
        else:
            return system



    def get(self):
        network = [n for n in self.get_network()]
        hostname = platform.node()
        system = self.get_osname()
        version = platform.version()

        return (hostname, system, version, network)


class PosixMinimalInventory(MinimalInventory):

    def get_ip_netmask(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                          0x8915,
                                          struct.pack('256s', ifname[:15])
                                          )[20:24]
                              )
        netmask = socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                               0x891b,
                                               struct.pack('256s',ifname)
                                               )[20:24]
                                   )
        macinfo = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        mac = ''.join(['%02x:' % ord(char) for char in macinfo[18:24]])[:-1]

        return ip, mac, netmask

    def get_interfaces(self):
        if os.path.exists("/proc/net/dev"):
            lines = []
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()

            for line in lines:
                if ":" in line:
                    yield line[:line.index(":")].strip()


    def get_network(self):
        for ifname in self.get_interfaces():
            ip, mac, netmask = self.get_ip_netmask(ifname)
            if ip.startswith("127."):
                continue
            yield ifname, ip, mac, netmask

    def get_hostname(self):
        return platform.node()

class WindowsMinimalInventory(MinimalInventory):
    def get_network(self):
        wqm = WMIQueryManager()
        info = wqm.get("Win32_NetworkAdapterConfiguration",
                       ["Caption",
                        "IPEnabled",
                        "IPAddress",
                        "MACAddress",
                        "IPSubnet"]
                       )
        for ifname, enabled, ip, mac, netmask in info:
            if enabled and len(ip)>0 and len(netmask)>0 :
                if ip[0].startswith("127."):
                    continue
                yield ifname, ip[0], mac, netmask[0]

def get_minimal_inventory():
    if SYSTEM == "WINDOWS":
        inv = WindowsMinimalInventory()
    elif SYSTEM in ("LINUX","DARWIN"):
        inv = PosixMinimalInventory()
    else:
        raise OSError
    return inv.get()


print get_minimal_inventory()



