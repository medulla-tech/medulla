# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2
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

""" Test module for Pulse2 network utils """

import unittest
import subprocess
import logging

from pulse2.network import NetUtils, IPResolve

def myLogger ():
    """ Default logging instance """
    log = logging.getLogger()
    handler = logging.StreamHandler()
    log.addHandler(handler)
    return log

log = myLogger()

def get_my_network ():
    """ 
    Getting the networking info - directly from test machine

    Another way to get necesary networking infomations to compare getted 
    results of tested methods.

    @return: IP address, netmask and default gateway of testmachine
    @rtype: tuple
    
    """
    cmd_ip = "ifconfig $EXT_NIC | grep inet | cut -d : -f 2 | cut -d ' ' -f 1"
    cmd_nm = "ifconfig $EXT_NIC | grep Mask | cut -d : -f 4 | cut -d ' ' -f 1"
    
    ip = exec_cmd(cmd_ip,exclude="127.0.0.1")
    nm = exec_cmd(cmd_nm)

    return ip, nm

def get_my_gateway():
    import socket
    import struct

    with open("/proc/net/route") as f_route:
        for line in f_route:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

 
def exec_cmd(cmd, exclude=None):
    """
    Command execute and output parse 

    @param cmd: command line expression to execute
    @type cmd: str

    @param exclude: expression to exclude from output
    @type exclude: str

    @return: output from executed expression
    @rtype: str
    
    """
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = ps.communicate()

    ret = []
    for line in out :
        if not line :
            continue
        line = line.replace("\n", "")
        if exclude :
            if exclude in line :
                line = line.replace(exclude, "")
    
        ret.append(line)
    return ret[0]


class class01_NetUtils (unittest.TestCase) :
    """ Test class for common network utils """

    def setUp (self):
        """getting of local network settings"""
        self.my_ip, self.my_nm = get_my_network()  
        self.my_gw = get_my_gateway()
        

    def test01_get_netmask(self):
        """ test of getting of netmask """
        netmask, gateway = NetUtils.get_netmask_and_gateway()
        self.assertEqual(self.my_nm, netmask)

    def test02_get_gateway(self):
        """ test of getting of gateway """
        netmask, gateway = NetUtils.get_netmask_and_gateway()
        self.assertEqual(self.my_gw, gateway)

    def test03_on_same_network_true(self):
        """ test of co-existence in the same network"""
        ip1 = "10.1.22.5"
        ip2 = "10.1.22.211"
        result = NetUtils.on_same_network(ip1, ip2)
        self.assertEqual(result, True)

    def test04_on_same_network_false(self):
        """ test of co-existence in the same network"""
        ip1 = "10.1.20.5"
        ip2 = "10.1.41.2"
        result = NetUtils.on_same_network(ip1, ip2)
        self.assertEqual(result, False)

    def test05_has_enough_info_true(self):
        """ test of info complexity """
        iface_info = {"ip": "192.168.1.25", 
                      "mac": "00:55:47:f0:d4", 
                      "netmask": "255.255.255.0" , 
                      "gateway" : "192.168.1.1"}
        result = NetUtils.has_enough_info(iface_info)
        self.assertEqual(result, True)

    def test06_has_enough_info_false(self):
        """ test of info complexity """
        iface_info = {"ip": "192.168.1.25", 
                      "mac": None, 
                      "netmask": "255.255.255.0" , 
                      "gateway" : "192.168.1.1"}
        result = NetUtils.has_enough_info(iface_info)
        self.assertEqual(result, False)


class class02_IPresolve (unittest.TestCase):

    def test01_resolve_per_ip(self):
        """ 
        IP resolving method.
        
        Selecting of correct interface depends on prefered network of server.
        """

        my_ip = "192.168.1.100"
        my_mask = "255.255.255.0"

        resolve_order = ["ip"]

        estimated_ip = "192.168.1.25"

        iface1 = {"ip": estimated_ip, 
                  "mac": "00:55:47:f0:d4", 
                  "netmask": "255.255.255.0" , 
                  "gateway" : "192.168.1.1"}

        iface2 = {"ip": "127.0.0.1", 
                  "mac": "00:55:40:00:00", 
                  "netmask": "255.255.255.0" , 
                  "gateway" : "192.168.1.1"}

        iface3 = {"ip": "200.41.11.85", 
                  "mac": "41:45:40:f0:8f", 
                  "netmask": "255.255.0.0" , 
                  "gateway" : "192.168.1.1"}

        ifaces =  [iface1, iface2, iface3]

        target = ("WORKSTATION-2547", ifaces)

        ip_resolve = IPResolve(resolve_order, my_ip, my_mask)
        getted_ip = ip_resolve.get_from_target(target)

        self.assertEqual(estimated_ip, getted_ip)

    def test02_resolve_per_ip_with_default_detection(self):
        """ 
        IP resolving method.
        
        Selecting of correct interface depends on prefered network of server.
        IP address of tested machine exists on local network.
        """

        my_ip, my_mask = get_my_network()

        resolve_order = ["ip"]

        # modify the last number of IP address to 111 
        # e.g. 211.55.21.37 --> 211.55.21.111
        estimated_ip = ".".join(my_ip.split(".")[0:3] + ["111"])

        iface1 = {"ip": estimated_ip, 
                  "mac": "00:55:47:f0:d4", 
                  "netmask": "255.255.255.0" , 
                  "gateway" : "192.168.1.1"}

        iface2 = {"ip": "127.0.0.1", 
                  "mac": "00:55:40:00:00", 
                  "netmask": "255.255.255.0" , 
                  "gateway" : "192.168.1.1"}

        iface3 = {"ip": "200.41.11.85", 
                  "mac": "41:45:40:f0:8f", 
                  "netmask": "255.255.0.0" , 
                  "gateway" : "192.168.1.1"}

        ifaces =  [iface1, iface2, iface3]

        target = ("WORKSTATION-2547", ifaces)

        ip_resolve = IPResolve(resolve_order, my_ip, my_mask)
        getted_ip = ip_resolve.get_from_target(target)

        self.assertEqual(estimated_ip, getted_ip)

    def test03_resolve_first(self):
        """
        *Last chance method*

        Returns the first interface having enough networking info. 
        """

        resolve_order = ["first"]

        estimated_ip = "192.168.1.15" 
        iface1 = {"ip": estimated_ip, 
                  "mac": "00:55:47:f0:d4", 
                  "netmask": "255.255.255.0" , 
                  "gateway" : "192.168.1.1"}

        # omitting some informations 
        iface2 = {"ip": "127.0.0.1", 
                  "mac": "00:55:40:00:00", 
                  "netmask": "255.255.255.0"} 

        iface3 = {"ip": "200.41.11.85", 
                  "mac": "41:45:40:f0:8f"} 

        ifaces =  [iface1, iface2, iface3]

        target = ("WORKSTATION-2547", ifaces)

        ip_resolve = IPResolve(resolve_order)
        getted_ip = ip_resolve.get_from_target(target)

        self.assertEqual(estimated_ip, getted_ip)


if __name__ == '__main__' :
    unittest.main()


