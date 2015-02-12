# -*- test-case-name: pulse2.cm.tests.control -*-
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


import logging
import os
import time
import psutil
from datetime import datetime

from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.defer import succeed, fail
from twisted.internet.task import deferLater
from twisted.web.client import getPage
from twisted.internet.protocol import ProcessProtocol
from twisted.internet.error import ProcessDone

from mmc.client.async import Proxy

class MethodNotFound(Exception):
    def __repr__(self):
        return "Method %s not found" % repr(self.message)


class Endpoint(object):
    """
    Defines a base frame for objects which process the incoming requests.

    All methods to be call must be declared in an inherited class,
    otherwise the exception MethodNotFound will be throwed.

    Each endpoint defines a prefix. This parameter helps to resolve
    the name of method which will be called. That avoids the mistakes
    when a same method name is already defined in another endpoint.
    """
    prefix = None
    config = None

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger()
        self._mmc_proxy_init()


    def _mmc_proxy_init(self):
        """Starts the cleint mmc proxy for remote calls """
        proto = "https" if self.config.mmc.enablessl else "http"
        url = "%s://%s:%d/XMLRPC" % (proto,
                                     self.config.mmc.host,
                                     self.config.mmc.port,
                                     )
        self.mmc_proxy = Proxy(url,
                               self.config.mmc.user,
                               self.config.mmc.passwd,
                               )


    def call_method(self, name, *args):
        """
        Calls a method defined in an inherited class

        @param method: method name
        @type method: str

        @param args: arguments
        @type args: list
        """
        if hasattr(self, name):
            method = getattr(self, name)
            return method(*args)
        else:
            raise MethodNotFound(name)


    def _get_machine_uuid(self, hostname, macs):
        """
        A remote call to get UUID of machine.

        @param hostname: hostname of machine
        @type hostname: str

        @param macs: list of active MAC addresses of machine
        @type macs: list

        @return: UUID of machine
        @rtype: Deferred
        """
        d = self.mmc_proxy.callRemote("base.ldapAuth",
                                      self.config.mmc.ldap_user,
                                      self.config.mmc.ldap_passwd,
                                      )
        @d.addCallback
        def cb(result):
            if result:
                method = "base.getComputerByHostnameAndMacs"
                return self.mmc_proxy.callRemote(method, hostname, macs)

        @d.addErrback
        def eb(failure):
            self.logger.error("MMC LDAP auth failed: %s" % str(failure))
            return failure

        return d



class AgentsInstallMap(object):
    """Common attributes containing the install commands of agents by platform."""

    windows = ["##wget## ##server##/downloads/win32/pulse2-win32-agents-pack-silent.exe",
               "##tmp## pulse2-win32-agents-pack-silent.exe"]
    debian = ["wget -O - ##server##/downloads/pulse2-agents.gpg.key | apt-key add -",
              "echo 'deb ##server##/downloads/debian common main' >> /etc/apt/sources.list",
              "apt-get update -y",
              "apt-get install -y pulse2-agents-installer"
              ]
    debian_server = ["wget -O - ##server##/downloads/pulse2-agents.gpg.key | apt-key add -",
              "echo 'deb ##server##/downloads/debian common main' >> /etc/apt/sources.list",
              "apt-get update -y",
              "apt-get install -y pulse2-agents-installer-nordp"
              ]
    redhat = ["yum-config-manager --add-repo ##server##/downloads/rpm/pulse2-agents.repo",
              "yum install -y pulse2-agents-installer",
              ]
    redhat_server = ["yum-config-manager --add-repo ##server##/downloads/rpm/pulse2-agents.repo",
              "yum install -y pulse2-agents-installer-nordp",
              ]
    osx = ["##wget##  ##server##/downloads/mac/Pulse2AgentsInstaller.tar",
           "tar xvf Pulse2AgentsInstaller.tar",
           "/usr/bin/installer -pkg Pulse2AgentsInstaller.tar -target /",
           ]

class VPNInstallMap(object):
    windows = ["##wget## ##server##/downloads/vpn/softether/softether-silent-install.exe",
               "##tmp## softether-silent-install.exe /S ##args##"]

    posix = ["##wget## ##server##/downloads/vpn/vpn-service-install.sh",
             "##wget## ##server##/downloads/vpn/vpn-client-set.sh",
             "##wget## ##server##/downloads/vpn/vpn-variables.in",
            ]


class PackagesEndpoint(Endpoint):
    """
    Treats the first-run queries to install needed agent packs.

    Served responses allows to download necessary agents from Pulse server
    or from public mirrors if a dependency is defined in package.
    """

    prefix = "packages"

    commands = AgentsInstallMap()
    vpn_install = VPNInstallMap()

    def _parse_request(self, request):
        """
        Resolves the platform of machine.

        @param request: package query
        @type request: dict

        @return: list of install commands
        @rtype: list
        """
        if "vpnclient" in request["name"]:
            if request["system"] in ["Linux", "Darwin"]:
                return self.vpn_install.posix
            else:
                return self.vpn_install.windows

        # TODO - recognize by SW name request["name"] in ->
        # "Mandriva OpenSSH Agent", "pulse2-agents-installer",
        # "pulse2-agents-installer-nordp", "org.pulse2-agents-installer"
        system = request["system"]

        if system == "Windows":
            return self.commands.windows
        elif system == "Linux":
            distro = request["distro"]
            xserver = request["xserver"]
            if distro.lower() in ["debian", "ubuntu", "mint"]:
                if xserver:
                    return self.commands.debian
                else:
                    return self.commands.debian_server
            elif distro.lower() in ["redhat", "centos", "fedora"]:
                if xserver:
                    return self.commands.redhat
                else:
                    return self.commands.redhat_server

    def get_package(self, request, from_ip=None):
        commands = self._parse_request(request)

        d = Deferred()

        d.callback(commands)
        return d

class FusionFormatter(object):

    template = """<?xml version='1.0' encoding='utf-8'?>
<REQUEST>
    <DEVICEID>{deviceid}</DEVICEID>
    <QUERY>INVENTORY</QUERY>
    <TAG>root</TAG>
    <CONTENT>
        <ACCESSLOG>
            <LOGDATE>{timestamp}</LOGDATE>
        </ACCESSLOG>
        <HARDWARE>
            <NAME>{hostname}</NAME>
            <OSNAME>{osname}</OSNAME>
            <OSVERSION>{osversion}</OSVERSION>
        </HARDWARE>
        {networks}
    </CONTENT>
</REQUEST>
"""
    network_template = """<NETWORKS>
            <IPADDRESS>{ipaddr}</IPADDRESS>
            <IPMASK>{ipmask}</IPMASK>
            <MACADDR>{macaddr}</MACADDR>
            <STATUS>{state}</STATUS>
            <TYPE>Ethernet</TYPE>
            <DESCRIPTION>{name}</DESCRIPTION>
        </NETWORKS>"""

    def get_networks(self, inv_networks):

        networks = []
        for name, ip, mac, netmask in inv_networks:
            if mac is None and ip is None:
                continue
            if ip.startswith("127."):
                # excluding the loopback
                continue
            state = "Up"
            if mac is None:
                mac = ""
            if ip is None:
                ip = ""
            if isinstance(ip, tuple) and len(ip) > 0:
                ip = ip[0]
            network = self.network_template.format(name=name,
                                                   ipaddr=ip,
                                                   ipmask=netmask,
                                                   macaddr=mac,
                                                   state=state)
            networks.append(network)

        return "\n".join(networks)

    def get(self, inventory):
        hostname, system, osversion, networks = inventory
        timestamp = time.time()

        now_datetime = datetime.fromtimestamp(timestamp)
        device_format = "%Y-%m-%d-%H-%M-%S"
        device_timestamp = now_datetime.strftime(device_format)
        logdate_format = "%Y-%m-%d %H:%M:%S"
        logdate_timestamp = now_datetime.strftime(logdate_format)

        device_id = "%s-%s" % (hostname, device_timestamp)
        return self.template.format(deviceid=device_id,
                                    timestamp=logdate_timestamp,
                                    hostname=hostname,
                                    osname=system,
                                    osversion=osversion,
                                    networks=self.get_networks(networks),
                                    ) #.encode("utf-8")



class InventoryServerEndpoint(Endpoint):

    prefix = "inventory"

    fusion_formatter = FusionFormatter()
    mmc_proxy = None


    def get_valid_mac(self, inventory, from_ip):
        hostname, system, osversion, networks = inventory

        for name, ip, mac, netmask in networks:
            if ip.startswith("127"):
                # exclude the loopack
                continue
            if ip == from_ip:
                return mac



    def process_inventory(self, inventory, from_ip):
        """
        Initial stage when an inventory of machine received.

        At first, we check if machine already exists in inventory.
        In this case, its UUID is immediatelly returned; if not,
        received inventory collection is transformed to fusion/OCS
        format and sent to inventory server.
        Because inscription of a new machine takes always few seconds,
        a lag defined in config allows to wait until our new machine
        is saved into the inventory database.
        After this delay, a new request to get UUID of this machine
        is repeated.

        @param inventory: inventory collection
        @type inventory: list

        @param from_ip: IP address of connected machine
        @param from_ip: str

        @return: UUID of machine or False if any fail occured
        @rtype: Deferred
        """

        hostname, system, osversion, networks = inventory
        macs = [mac for (name, ip, mac, mask) in networks]

        d = self._get_machine_uuid(hostname, macs)
        # UUID of machine
        d.addCallback(self.get_uuid_callback, hostname, macs, inventory)
        # IP address update for UUID (msc.target table)
        d.addCallback(self.update_target_ip, from_ip)
        @d.addErrback
        def eb_uuid(failure):
            self.logger.warn("Getting of UUID for machine '%s' failed: %s" % (hostname, str(failure)))
            return failure

        # Light Pull stage
        d.addCallback(self.check_pending_commands, hostname)
        d.addCallback(self.launch_pending_commands, hostname)
        d.addCallback(self.catch_results, hostname)
        @d.addErrback
        def eb_light_pull(failure):
            self.logger.warn("Pending commands launching for machine '%s' failed: %s" % (hostname, str(failure)))
            return failure

        return d

    def get_uuid_callback(self, uuid, hostname, macs, inventory):
        """
        Resolving of result of remote call to get UUID of machine.

        @param uuid: result of remote call (UUID if request successfull, otherwise False)
        @type uuid: str or bool

        @param hostname: hostname of machine
        @type hostname: str

        @param macs: list of active MAC addresses of machine
        @type macs: list

        @param inventory: inventory collection
        @type inventory: list

        @return: UUID of machine
        @rtype: Deferred
        """
        if uuid is not False and uuid is not None:
            self.logger.info("Machine %s has uuid=%s" % (hostname, str(uuid)))
            return succeed(uuid)
        else:
            d = self.send_inventory(inventory)
            @d.addCallback
            def try_to_get_uuid(result):
                """
                Tries to get UUID of machine after inventory injection

                @param result: True if sending succeed
                @type result: bool

                @return: UUID or None
                @rtype: Deferred
                """
                if result:
                    self.logger.info("Inventory of machine <%s> sent" % (hostname))

                    delay = self.config.inventory.inscription_lag
                    self.logger.info("Trying to get new UUID of %s after %d seconds" % (hostname, delay))

                    delayed = deferLater(reactor,
                                         delay,
                                         self._get_machine_uuid,
                                         hostname,
                                         macs,
                                         )
                    @delayed.addErrback
                    def eb(failure):
                        self.logger.warn("Getting of UUID for machine '%s' failed: %s" % (hostname, str(failure)))
                        return failure
                    return delayed
                else:
                    self.logger.warn("Inventory of machine <%s> sending failed" % (hostname))
                    return fail(None)
            return d



    def update_target_ip(self, uuid, ip):
        """
        Replacing of default IP address by an actual checked IP.

        @param uuid: UUID of machine
        @type uuid: str

        @param ip: Actual IP address
        @type ip: str

        @rtype: Deferred
        """
        if uuid != False and uuid is not None:

            d = self.mmc_proxy.callRemote("msc.update_target_ip", uuid, ip)
            @d.addCallback
            def cb(ignored):
                self.logger.info("New IP of target <%s>: %s" % (uuid, ip))
                return uuid
            @d.addErrback
            def eb(failure):
                self.logger.error("Update of target <%s> failed: %s" % (uuid, str(failure)))
                return failure
            return d

        else:
            return succeed(False)


    def check_pending_commands(self, uuid, hostname):
        """
        Checks if this active machine has something to launch.

        @param uuid: UUID of machine
        @type uuid: str

        @param hostname: hostname of machine
        @type hostname: str

        @return: list of ids of commands_on_host
        @rtype: list
        """

        self.logger.info("Looking for pending commands for machine <%s>" % (hostname))
        return self.mmc_proxy.callRemote("msc.checkLightPullCommands", uuid)


    def launch_pending_commands(self, cohs, hostname):
        """
        Starts all waiting commands.

        @param cohs :list of ids of commands_on_host
        @type cohs: list

        @param hostname: hostname of machine
        @type hostname: str

        @return: list of results
        @rtype: DeferredList
        """
        total = len(cohs)
        if total == 0:
            return DeferredList([succeed(True)])
        self.logger.info("%d deployments to start for machine <%s>" % (total, hostname))
        dl = []
        for coh in cohs:
            d = self.mmc_proxy.callRemote("msc.start_command_on_host", coh)
            dl.append(d)
        return DeferredList(dl)


    def catch_results(self, results, hostname):
        """
        Treats the results of looping call of all pending commands.

        @param results: list of results
        @type results: list

        @param hostname: hostname of machine
        @type hostname: str

        @return: True if all RPC calls have been correct
        @rtype: bool
        """
        try:
            iter(results)
        except TypeError:
            self.logger.warn("Launching of pending commands for <%s> failed: %s" % (hostname, results))
            return False
        # results format :
        # [(True, True), (True, True),...] if correct
        return all([a and b for a, b in results])



    def send_inventory(self, inventory):
        """
        Sends a minimal inventory to inventory server.

        @param inventory: minimal inventory of machine
        @type inventory: list

        @return:
        @rtype: Deferred
        """
        # transform to OCS/fusion format
        xml = self.fusion_formatter.get(inventory)

        self.logger.info("Inventory to send:\n %s" % (str(xml)))

        proto = "https" if self.config.inventory.enablessl else "http"
        url = "%s://%s:%d/" % (proto,
                               self.config.inventory.host,
                               self.config.inventory.port
                               )
        headers = {"User-Agent": "Pulse2 Connection Manager",
                   "Content-Type": "application/x-www-form-urlencoded",
                   "Content-Length" : str(len(xml)),
                   }

        # sending the inventory
        d = getPage(url, method="POST", postdata=xml, headers=headers)

        @d.addCallback
        def cb(reason):
            """
            Treats the result of sent inventory.

            @param reason: response from inventory server
            @type reason: str
            """
            from zlib import decompressobj
            decomp = decompressobj()
            response = decomp.decompress(reason)
            self.logger.debug("Forward result: %s" % (str(response)))
            return True

        @d.addErrback
        def eb(reason):
            self.logger.warn("Forward failed: %s" % (str(reason)))
            return False

        return d



class VPNInstallEndpoint(Endpoint):
    prefix = "vpn_install"

    VPN_VARIALES_PATH = "/var/lib/pulse2/clients/vpn/vpn-variables"

    def _check_vpn_service(self):
        """ Returns True if VPN server running """
        process_name = "vpnserver"
        for p in psutil.process_iter():
            for arg in p.cmdline :
                if process_name in arg:
                    return True

        self.logger.warn("CM: Can't find VPN server service")
        return False



    def create_new_user(self, inventory, from_ip):

        if not self._check_vpn_service():
            return succeed(False)

        hostname, system, osversion, networks = inventory
        macs = [mac for (name, ip, mac, mask) in networks]

        d = self._get_machine_uuid(hostname, macs)
        @d.addCallback
        def get_uuid_callback(uuid):
            """
            Resolving of result of remote call to get UUID of machine.

            @param uuid: result of remote call (UUID if request successfull, otherwise False)
            @type uuid: str or bool

            @return: UUID of machine
            @rtype: Deferred
            """
            if uuid is not False and is not None:
                self.logger.info("VPN install: Machine %s has uuid=%s" % (hostname, str(uuid)))
                return succeed(uuid)
            else:
                return fail(None)

        @d.addCallback
        def create_user(uuid):
            """
            Creates a client account in VPN service.

            @param uuid: UUID of machine as username
            @type uuid: str
            """
            path = os.path.join(self.config.vpn.scripts_path,
                                "vpn-server-user-create.sh",
                                )
            password = self._password_generate()
            host, port = self.get_vpn_variables()

            protocol = ForkingProtocol("VPN installer")
            args = [path, uuid, password]
            reactor.spawnProcess(protocol,
                                 args[0],
                                 args,
                                 usePTY=True)

            return (host, port, uuid, password)


        @d.addErrback
        def get_uuid_errback(failure):
            self.logger.warn("VPN install: uuid get failed: %s" % (str(failure)))
            return False


        return d

    def _password_generate(self):
        length = 16
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        return "".join([chars[ord(c) % len(chars)] for c in os.urandom(length)])

    def get_vpn_variables(self):
        host = port = None
        with open(self.VPN_VARIALES_PATH, "r") as f:
            for line in f.readlines():
                if "VPN_SERVER_HOST" in line and "=" in line:
                    host = line.split("=")[1].strip()
                if "VPN_SERVER_PORT" in line and "=" in line:
                    port = line.split("=")[1].strip()
                if host and port:
                    return host, port

            self.logger.debug("%s: VPN VARIABLES: %s" % line)
        return host, port


class ForkingProtocol(ProcessProtocol):
    """ Protocol to fork a process"""

    def __init__(self, name, callback=None):
        """
        @param name: name or description (for logging only)
        @type name: str

        @param callback: function to call when forked process finished
        @type callback: func
        """
        ProcessProtocol()
        self.logger = logging.getLogger()

        self.name = name
        self.callback = callback


    def connectionMade(self):
        self.logger.debug("%s: Opening of process started" % self.name)


    def outReceived(self, data):
        self.logger.debug("%s: process data received: %s" % (self.name, data))
        ProcessProtocol.outReceived(self, data)

    def errReceived(self, reason):
        self.logger.warn("%s: process failed: %s" % (self.name, reason))
        self.transport.loseConnection()
        ProcessProtocol.errReceived(self, reason)

    def processEnded(self, reason):
        err = reason.trap(ProcessDone)
        if err==ProcessDone:
            self.logger.debug("%s: process successfully ended" % self.name)
        else:
            self.logger.warn("%s: closing failed: %s" % (self.name, reason))

        if self.callback:
            self.callback(reason)



