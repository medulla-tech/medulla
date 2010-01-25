# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
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

import re
import sre_constants

def dottedQuadToNum(ip):
    """Convert decimal dotted quad string to long integer"""
    bytes = ip.split('.')
    if len(bytes) > 4:
        raise ValueError, "IPv4 Address with more than 4 bytes"
    bytes += ['0'] * (4 - len(bytes))
    bytes = [long(x) for x in bytes]
    for x in bytes:
        if x > 255 or x < 0:
            raise ValueError, "%r: single byte must be 0 <= byte < 256" % (ip)
    return ((bytes[0] << 24) + (bytes[1] << 16) + (bytes[2] << 8) + bytes[3])

def ipInRange(ipAddress, beginRange, endRange):
    """
    Return True if IP is between begin and end
    """
    ip = dottedQuadToNum(ipAddress)
    begin = dottedQuadToNum(beginRange)
    end = dottedQuadToNum(endRange)
    return (begin <= ip) and (ip <= end)

def processIPListFromConfig(iplist):
    """
    Parse and check a list of IP addresses or network range

    @returns: a list with the cleaned up addresses or range
    @rtype: list
    """
    ret  = []
    for ip in iplist.split(","):
        ip = ip.strip()
        if "/" in ip:
            begin, end = ip.split("/")
            try:
                if not (dottedQuadToNum(begin) <= dottedQuadToNum(end)):
                    raise ValueError
                ret.append((begin,end))
            except ValueError:
                pass            
        else:
            try:
                dottedQuadToNum(ip)
                ret.append(ip)
            except ValueError:
                pass
    return ret

def rfc2780Filter(ips):
    """
    Filter non RFC 2780 IP addresses (not in IPV4 unicast space).
    
    @param ips: a list of IP addresses
    @type ips: list

    @returns: valid IP addresses
    @rtype: list
    """
    ret = []
    for ip in ips:
        try:
            if ipInRange(ip, "0.0.0.0", "0.255.255.255") or ipInRange(ip, "127.0.0.0", "127.255.255.255"):
                continue
            if ipInRange(ip, "0.0.0.0", "223.255.255.255"):
                ret.append(ip)
        except ValueError:
            # A given IP address is malformed
            pass
    return ret

def rfc1918Filter(ips):
    """
    Filter non RFC 1918 IP addresses (not a valid private address)
    
    @param ips: a list of IP addresses
    @type ips: list

    @returns: valid IP addresses
    @rtype: list
    """
    ret = []
    for ip in ips:
        try:
            if ipInRange(ip, "10.0.0.0", "10.255.255.255") or ipInRange(ip, "172.16.0.0", "172.31.255.255") or ipInRange(ip, "192.168.0.0", "192.168.255.255"):
                ret.append(ip)
        except ValueError:
            # A given IP address is malformed
            pass
    return ret

def excludeFilter(ips, exclude):
    """
    Filter IP addresses according to an exclude list

    @param ips: list of IP addresses
    @type ips: list

    @param exclude: IP addresses exclude list
    @type exclude: str

    @returns: filtered IP addresses list
    @rtype: list
    """
    exclude = processIPListFromConfig(exclude)
    ret = []
    for ip in ips:
        filtered = False
        for ex in exclude:
            if ip == ex:
                # This IP is filtered
                filtered = True
                break
            elif type(ex) == tuple:
                if ipInRange(ip, ex[0], ex[1]):
                    # This IP is filtered
                    filtered = True
                    break         
        if not filtered:
            ret.append(ip)
    return ret
        
def mergeWithIncludeFilter(ips, filteredips, include):
    """
    @param ips: list of IP addresses
    @type ips: list

    @param ips: list of filtered IP addresses
    @type ips: list

    @param include: IP addresses exclude list
    @type include: str

    @returns: merge of the filtered IP addresses list and the accepted IP addresses
    @rtype: list
    """
    include = processIPListFromConfig(include)
    ret = filteredips
    for ip in ips:
        for inc in include:
            if ip == inc and ip not in ret:
                ret.append(ip)
                break
            elif type(inc) == tuple:
                if ipInRange(ip, inc[0], inc[1]) and ip not in ret:
                    ret.append(ip)
                    break
    return ret

def isFqdn(hostname):
    """
    @param hostname: computer host name
    @type hostname: str

    @returns: True if the hostname is a valid FQDN
    @rtype: bool
    """
    # _ is accepted in the host name part of the FQDN because some AD managed
    # DNS zones may have some host with _ in their name (they are accepted
    # in NT4 netbios name).
    ret = False
    if re.compile("^([a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]\.){1,10}[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$").search(hostname):
        ret = True
    return ret

def isValidHostname(hostname):
    """
    @param hostname: computer host name
    @type hostname: str

    @returns: True if the hostname is a valid host name
    @rtype: bool
    """
    ret = False
    if isFqdn(hostname) or re.compile("^[a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]$").search(hostname):
        ret = True
    return ret

def checkWithRegexps(string, regexps):
    """
    Check if a string is matching a regexp from a list of regexps
    
    @param hostname: string to check
    @type hostname: str

    @param regexps: space separated regexps
    @type regexps: str

    @returns: True if the string is matching at least one regexp
    @rtype: boolean
    """
    ret = False
    for regexp in regexps.split():
        # Add ^ and $ to the regexp
        if not regexp.startswith("^"):
            regexp = "^" + regexp
        if not regexp.endswith("$"):
            regexp = regexp + "$"
        try:
            if re.compile(regexp).search(string):
                ret = True
                break
        except sre_constants.error:
            # The regexp is malformed, ignore it
            pass
    return ret

def macAddressesFilter(macs, regexps):
    """
    Filter a list of MAC addresses, removing those that are matching at least
    on regexp in a list of regexps.
    """
    ret = macs[:]
    for mac in macs:
        if checkWithRegexps(mac, regexps):
            ret.remove(mac)
            continue
    return ret
