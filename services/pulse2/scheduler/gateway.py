# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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
"""
A input gateway of sheduler receiving the responses to async_* actions 
from scheduler-proxy which forwards the requests from all attached launchers 
and mmc-agent.

+-------------+  
| launcher_01 |---+
+-------------+   |  
    ....          |
    ....         <scheduler_host>:8000       unix socket    
+-------------+   |       +-----------------+         +---------+-----------+
| launcher_nn |---+------>| scheduler-proxy |-------->| gateway | scheduler |
+-------------+   |       +-----------------+         +---------+-----------+ 
------------+     |                                    
| MMC agent |-----+    
+-----------+          
"""


import logging

from twisted.internet.protocol import Factory
from twisted.internet.defer import Deferred

from pulse2.utils import xmlrpcCleanup
from pulse2.scheduler.network import chooseClientIP
from pulse2.scheduler.control import MscDispatcher
from pulse2.scheduler.health import getHealth
from pulse2.scheduler.utils import UnixProtocol
from pulse2.scheduler.dlp import DownloadQuery

class SchedulerGateway(UnixProtocol):
    """
    Provides incomming requests from scheduler-proxy trough the unix socket.
    """

    def __init__(self):
        self.dlq = DownloadQuery()

    def _nok(self):
        """A negative deferred response"""
        d = Deferred()
        @d.addCallback
        def cb(reslut):
            return False
        d.callback(True)
        return d

    def ping_client(self, uuid, fqdn, shortname, ips, macs, netmasks):
        client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs,
            'netmasks': netmasks
        })
        if client : 
            return MscDispatcher().launchers_provider.ping_client(client)
        else :
            return self._nok()

    def probe_client(self, uuid, fqdn, shortname, ips, macs, netmasks):
        client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs,
            'netmasks': netmasks
        })
 
        if client :
            return MscDispatcher().launchers_provider.probe_client(client)
        else :
            return self._nok()

       

    def ping_and_probe_client(self, uuid, fqdn, shortname, ips, macs, netmasks):
        client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs,
            'netmasks': netmasks
        })
        
        if client :
            return MscDispatcher().launchers_provider.ping_and_probe_client(client)
        else :
            return self._nok()


    def download_file(self, uuid, fqdn, shortname, ips, macs, netmasks, path, bwlimit):
        return MscDispatcher().launchers_provider.download_file(uuid, fqdn, shortname, ips, macs, netmasks, path, bwlimit)

    def tcp_sproxy(self, uuid, fqdn, shortname, ips, macs, netmasks, requestor_ip, requested_port):
        return MscDispatcher().launchers_provider.establish_proxy(uuid, fqdn, shortname, ips, macs, netmasks, requestor_ip, requested_port)


    def start_all_commands(self):
        return MscDispatcher().start_commands()

    def start_these_commands(self, ids):
        return MscDispatcher().start_commands(ids)


    def start_command(self, id):
        return MscDispatcher().start_commands([id])

    def start_commands(self, ids):
        return MscDispatcher().start_commands(ids)

    def stop_command(self, id):
        return MscDispatcher().stop_commands([id])
 
    def stop_commands(self, ids):
        return MscDispatcher().stop_commands(ids)
 
    ### XMLRPC functions used from a launcher ###
    def tell_i_am_alive(self, launcher):
        logging.getLogger().info("Launcher %s tells us it is alive" % launcher)
        return True



    def completed_quick_action(self, launcher, (exitcode, stdout, stderr), id, from_dlp=False):
        return MscDispatcher().run_proxymethod(launcher, 
                                              id, 
                                              "completed_quick_action", 
                                              (exitcode, stdout, stderr),
                                              from_dlp
                                              )
    def completed_push(self, launcher, (exitcode, stdout, stderr), id, from_dlp=False):
        return MscDispatcher().run_proxymethod(launcher, 
                                              id, 
                                              "completed_push", 
                                              (exitcode, stdout, stderr),
                                              from_dlp
                                              )
    def completed_pull(self, launcher, (exitcode, stdout, stderr), id, from_dlp=False):
        return MscDispatcher().run_proxymethod(launcher, 
                                              id, 
                                              "completed_pull", 
                                              (exitcode, stdout, stderr),
                                              from_dlp
                                              )
    def completed_execution(self, launcher, (exitcode, stdout, stderr), id, from_dlp=False):
        return MscDispatcher().run_proxymethod(launcher, 
                                              id, 
                                              "completed_execution", 
                                              (exitcode, stdout, stderr),
                                              from_dlp
                                              )
    def completed_deletion(self, launcher, (exitcode, stdout, stderr), id, from_dlp=False):
        return MscDispatcher().run_proxymethod(launcher, 
                                              id, 
                                              "completed_deletion", 
                                              (exitcode, stdout, stderr),
                                              from_dlp
                                              )
    def completed_inventory(self, launcher, (exitcode, stdout, stderr), id, from_dlp=False):
        return MscDispatcher().run_proxymethod(launcher, 
                                              id, 
                                              "completed_inventory", 
                                              (exitcode, stdout, stderr),
                                              from_dlp
                                              )
    def completed_reboot(self, launcher, (exitcode, stdout, stderr), id, from_dlp=False):
        return MscDispatcher().run_proxymethod(launcher, 
                                              id, 
                                              "completed_reboot", 
                                              (exitcode, stdout, stderr),
                                              from_dlp
                                              )
    def completed_halt(self, launcher, (exitcode, stdout, stderr), id, from_dlp=False):
        return MscDispatcher().run_proxymethod(launcher, 
                                              id, 
                                              "completed_halt", 
                                              (exitcode, stdout, stderr),
                                              from_dlp
                                              )
    def get_health(self):
        return getHealth()

    def choose_client_ip(self, interfaces):
        return chooseClientIP(interfaces)

    ### Download Provider methods ###
    def _get_dlp_method(self, phase):
        methods = {"upload": "pull_completed_pull",
                   "execute": "pull_completed_execution",
                   "delete": "pull_completed_deletion",
                   "inventory": "pull_completed_inventory",
                   "reboot": "pull_completed_reboot",
                   "halt": "pull_completed_halt",
                  }
        return methods[phase]

    def get_available_commands(self, uuid):
        return self.dlq.get_available_commands(uuid)

    def machine_has_commands(self, uuid):
        return self.dlq.machine_has_commands(uuid)

    def pull_target_awake(self, hostname, macs):
        return self.dlq.pull_target_awake(hostname, macs)
    
    def completed_step(self, id, phase, stdout, stderr, exitcode):
        method = self._get_dlp_method(phase)
        return xmlrpcCleanup(MscDispatcher().run_proxymethod("dlp", 
                                               id, 
                                               method, 
                                               (exitcode, stdout, stderr),
                                               True
                                               ))
        
    def verify_target(self, id, hostname, mac):
        """
        @param id: commands_on_host id 
        @type id: int

        @param hostname: hostname of computer
        @type hostname: str

        @param mac: MAC address of computer
        @type mac: str

        @return: True if at least one dowload disponible
        @rtype: bool
        """
        return self.dlq.verify_target(id, hostname, mac)
 
class SchedulerGatewayFactory(Factory):
    protocol = SchedulerGateway


