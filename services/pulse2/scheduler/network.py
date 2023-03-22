# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

# My functions
from pulse2.scheduler.config import SchedulerConfig
from pulse2.network import IPResolve


def u_decode(text):
    """Normalize the text to str"""
    if isinstance(text, unicode):
        return text.encode("ascii", "ignore")
    else:
        return text

def u_list_decode(u_list):
    return [u_decode(a) for a in u_list]

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
        hostname = u_decode(target["shortname"])
        fqdn = u_decode(target["fqdn"])
        ips = u_list_decode(target["ips"])
        macs = u_list_decode(target["macs"])
        if "netmasks" in target :
            netmasks = u_list_decode(target["netmasks"])

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
