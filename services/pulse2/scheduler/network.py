# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
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

# My functions
from pulse2.scheduler.config import SchedulerConfig
from pulse2.network import IPResolve

class SchedulerNetUtils :

    @classmethod
    def prepare_target(cls, target):
        """
        Convert the scheduler target format to common format.

        @param target: target info
        @type target: dict

        @return: target common format
        @rtype: tuple
        """
        hostname = target["shortname"]
        fqdn = target["fqdn"]
        ips = target["ips"]
        macs = target["macs"]
        if "netmasks" in target :
            netmasks = target["netmasks"]

        i = 0
        ifaces = []
        for ip in ips :
            iface = {}
            iface["ip"] = ip
            if i < len(macs) :
                iface["mac"] = macs[i]
            if i < len(netmasks) :
                iface["netmask"] = netmasks[i]
            ifaces.append(iface)
            i += 1

        return (hostname, fqdn, ifaces)

    @classmethod
    def get_ip_resolve(cls):
        resolve_order = SchedulerConfig().resolv_order
        networks = SchedulerConfig().preferred_network
        netbios_path = SchedulerConfig().netbios_path
        
        ip_resolve = IPResolve(resolve_order,
                               networks,
                               netbios_path=netbios_path)
        return ip_resolve


def chooseClientIP(msc_target):
    """
        Attempt to guess how to reach our client

        Available informations:
        - FQDN
        - IP adresses, in order of interrest

        Expected target struct:
        {
            'uuid': ,
            'fqdn': ,
            'shortname': ,
            'ips': [],
            'macs': [],
            'netmasks': [],
        }

        Probes:
        - FQDN resolution
        - Netbios resolution
        - Host resolution
        - IP check
    """
    target = SchedulerNetUtils.prepare_target(msc_target)
    ip_resolve = SchedulerNetUtils.get_ip_resolve()
    ip = ip_resolve.get_from_target(target)
 
    return ip

