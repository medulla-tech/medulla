# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import socket
import struct
import glob
import os.path
from mmc.support.mmctools import shlaunch


# IP manipulation stuff

def dottedQuadToNum(ip):
    """Convert decimal dotted quad string to long integer"""
    return socket.ntohl(struct.unpack('=L', socket.inet_aton(ip))[0])

def numToDottedQuad(n):
    """Convert long int to dotted quad string"""
    return socket.inet_ntoa(struct.pack('=L', socket.htonl(n)))

def makeMask(n):
    """Return a mask of n bits as a long integer"""
    # ~0 is a 32 bits long with all bits set to 1
    # (using 0xffffffff doesn't work well with python > 2.3)
    return (~0) << (32 - n)

def ipInRange(ipAddress, beginRange, endRange):
    """
    Return True if IP is between begin and end
    """
    ip = dottedQuadToNum(ipAddress)
    begin = dottedQuadToNum(beginRange)
    end = dottedQuadToNum(endRange)
    return (begin <= ip) and (ip <= end)
    
def ipNext(network, netmask, startAt = None, boundaries = False):
    """
    Return the next IP address on a network range, or an empty string

    @param network: dotted quad IP representation
    @type network: str

    @param netmask: number of bits in netmask
    @type netmask: int

    @param startAt: IP from which to get the next IP
    @type startAt: str

    @param boundaries: flag telling whether the network address and the broadcast address are also returned
    @type boundaries: bool

    @return: an IP address in dotted quad representation, or an empty string
    @rtype: str
    """
    net = dottedQuadToNum(network)
    mask = makeMask(netmask)
    broadcast = net | (~mask)
    if startAt: current = dottedQuadToNum(startAt)
    else: current = net
    next = current + 1
    if boundaries:
        if not (net <= next and next <= broadcast):
            next = ""
    else:
        if not (net < next and next < broadcast):
            next = ""            
    if next: return numToDottedQuad(next)
    else: return ""


# Network related functions

def getAllNetworkInterfaces():
    """
    Get all network device interfaces using /proc.
    Linux only.
    
    @return: a list of ethernet interfaces
    @rtype: list
    """
    ret = []
    for f in glob.glob("/proc/sys/net/ipv4/conf/*"):
        device = os.path.basename(f)
        if device not in ["all", "default", "lo"]:
            ret.append(device)
    return ret

def detectNetworkInterfaceRate(device, cmd = "/usr/sbin/ethtool"):
    """
    Use ethtool to detect network device rate.
    We can use the given rate only if:
     - the link is up on the device (if the link is down, the device is on low
       speed mode, and this speed may change when the link is up again)
     - auto-negociation is on (else the speed information can't be really
       trusted)
    
    @return: interface rate in kbit/s, or None if the rate can't be detected
    @rtype: int
    """
    # Speed rate in Mbit/s => kbit/s 
    rates = { "10Mb/s": 10000, "100Mb/s": 100000, "1000Mb/s": 100000 }
    # Run ethtool
    data = shlaunch(cmd + " " + device)
    auto = False
    speed = None
    link = False
    for line in data:
        if "Auto-negotiation: on" in line: auto = True
        elif "Link detected: yes" in line: link = True
        elif "Speed: " in line:
            # Get the speed value, e.g. '10Mb/s'
            value = line.split()[1]
            try:
                speed = rates[value]
            except KeyError:
                pass

    if not (auto and link):
        speed = None
    return speed
