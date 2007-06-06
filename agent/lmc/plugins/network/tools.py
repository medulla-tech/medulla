#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of LMC.
#
# LMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import socket
import struct

def dottedQuadToNum(ip):
    """Convert decimal dotted quad string to long integer"""
    return socket.ntohl(struct.unpack('L', socket.inet_aton(ip))[0])

def numToDottedQuad(n):
    """Convert long int to dotted quad string"""
    return socket.inet_ntoa(struct.pack('L', socket.htonl(n)))

def makeMask(n):
    """Return a mask of n bits as a long integer"""
    return 0xffffffff << (32 - n)

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
