#
# (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
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
import ldap
import logging
import os
import os.path
import time
import re
import struct

from lmc.plugins.base import ldapUserGroupControl, LogView
from lmc.support.config import *
from lmc.support import lmctools
import lmc

INI = "/etc/lmc/plugins/network.ini"

VERSION = "1.1.3"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION


def activate():
    config = NetworkConfig("network")
    logger = logging.getLogger()

    if config.disabled:
        logger.warning("Plugin network: disabled by configuration.")
        return False

    try:
        ldapObj = ldapUserGroupControl()
    except ldap.INVALID_CREDENTIALS:
        logger.error("Can't bind to LDAP: invalid credentials.")
        return False

    # Test if the Samba LDAP schema is available in the directory
    try:
         schema = ldapObj.getSchema("dhcpServer")
         if len(schema) <= 0:
             logger.error("DHCP schema is not included in LDAP directory");
             return False
    except:
        logger.exception("invalid schema")
        return False

    d = Dhcp()
    try:
        d.addServiceConfig("DHCP config")
    except ldap.ALREADY_EXISTS:
        pass

##     d = Dns()
##     d.addZone("linboxe.com", "172.16.73")
##     d.addSOA("linboxe.com")
##     rec = {
##         "nameserver" : "sarge.linboxe.com.",
##         "emailaddr" :  "admin.linboxe.com.",
##         "serial" : "20070306",
##         "refresh" : "2D",
##         "retry" : "15M",
##         "expiry" : "2W",
##         "minimum" : "1H",
##         }
##     d.setSOARecord("linboxe.com", rec)
##     d.addRecordA("sarge", "172.16.73.129", "linboxe.com")
##     d.setNSRecord("linboxe.com", "sarge.linboxe.com.")
##     print d.getZones()
##     hostname = socket.gethostname()
##     d.addServer(hostname)
##     d.setServicePrimaryServer("DHCP config", hostname)
##     #d.setServiceConfigOption("default-lease-time", 600)
##     print d.getServiceConfigOption()
##     #d.setServiceConfigOption("max-lease-time", 7200)
##     print d.getServiceConfig()

##     d.addSubnet("10.0.0.0", 24)
##     d.setSubnetOption("10.0.0.0", "domain-name-servers", "10.200.0.2")
##     d.addPool("10.0.0.0", "Pool 1", "10.0.0.1 10.0.0.25")
##     d.setPoolOption("Pool 1", "pool-option", "pool-value")
##     d.addGroup("10.0.0.0", "Group 1")
##     d.setGroupOption("Group 1", "group-option", "group-value")
##     d.addHostToSubnet("10.0.0.0", "boulet1")
##     d.addHostToGroup("Group 1", "boulet2")
    #d.delPool("Pool 1")
    #d.delSubnet("10.0.0.0")
##     d.setServiceConfigStatement("ddns-update-style", "ad-hoc")
##     d.addSubnet("192.168.0.0", 24)
##     d.setSubnetOption("192.168.0.0", "subnet-mask", "255.255.255.0")
##     d.setSubnetOption("192.168.0.0", "routers", "192.168.0.2")
##     d.setSubnetOption("192.168.0.0", "domain-name", '"domain.org"')
##     d.setSubnetOption("192.168.0.0", "domain-name-servers", "192.168.0.2")
##     d.setSubnetStatement("192.168.0.0", "filename",  '"/tftpboot/revoboot/bin/revoboot.pxe"')
##     d.addPool("192.168.0.0", "Default pool", "192.168.0.240 192.168.0.253")
##     d.setPoolStatement("Default pool", "max-lease-time" , "1800")
##     d.setPoolStatement("Default pool", "allow", "unknown clients")
    return True

def addZoneWithSubnet(zonename, network, netmask, reverse = False, description = None, nameserver = None, nameserverip = None):
    Dns().addZone(zonename, network, netmask, reverse, description, nameserver, nameserverip)
    d = Dhcp()
    d.addSubnet(network, netmask, zonename)
    d.setSubnetOption(network, "domain-name", '"' + zonename +'"')
    if nameserverip: d.setSubnetOption(network, "domain-name-servers", nameserverip)

# DNS exported call

def getZones(f):
    return Dns().getZones(f)

def addZone(zonename, network = None, netmask = None, reverse = False, description = None, nameserver = None, nameserverip = None):
    return Dns().addZone(zonename, network, netmask, reverse, description, nameserver, nameserverip)

def delZone(zone):
    return Dns().delZone(zone)

def zoneExists(zone):
    return Dns().zoneExists(zone)

def getAllZonesNetworkAddresses():
    return Dns().getAllZonesNetworkAddresses()

def getZoneNetworkAddress(zone):
    return Dns().getZoneNetworkAddress(zone)

def getZoneObjectsCount(zone):
    return Dns().getZoneObjectsCount(zone)

def getZoneObjects(zone, filt):
    return Dns().getZoneObjects(zone, filt)

def addRecordA(hostname, ip, zone):
    return Dns().addRecordA(hostname, ip, zone)

def delRecord(hostname, zone):
    return Dns().delRecord(hostname, zone)

def getSOARecord(zone):
    return Dns().getSOARecord(zone)

def setNSRecord(zone, nameserver):
    Dns().setNSRecord(zone, nameserver)

def setZoneDescription(zone, description):
    Dns().setZoneDescription(zone, description)

# DHCP exported call

def addSubnet(network, netmask, name):
    Dhcp().addSubnet(network, netmask, name)

def delSubnet(network):
    Dhcp().delSubnet(network)

def getSubnet(subnet):
    return Dhcp().getSubnet(subnet)

def getSubnets(f):
    return Dhcp().getSubnets(f)

def setSubnetOption(subnet, option, value = None):
    Dhcp().setSubnetOption(subnet, option, value)
    
def setSubnetStatement(subnet, option, value = None):
    Dhcp().setSubnetStatement(subnet, option, value)

def setSubnetDescription(subnet, description):
    Dhcp().setSubnetDescription(subnet, description)

def setSubnetNetmask(subnet, netmask):
    Dhcp().setSubnetNetmask(subnet, netmask)

def getSubnetHosts(network, filter):
    return Dhcp().getSubnetHosts(network, filter)

def getSubnetHostsCount(zone):
    return Dhcp().getSubnetHostsCount(zone)

def addPool(subnet, poolname, start, end):
    Dhcp().addPool(subnet, poolname, start, end)

def delPool(poolname):
    Dhcp().delPool(poolname)

def getPool(poolname):
    return Dhcp().getPool(poolname)

def setPoolRange(poolname, start, end):
    Dhcp().setPoolRange(poolname, start, end)

def addHostToSubnet(subnet, hostname):
    Dhcp().addHostToSubnet(subnet, hostname)

def delHost(hostname):
    Dhcp().delHost(hostname)

def setHostOption(host, option, value = None):
    Dhcp().setHostOption(host, option, value)

def setHostStatement(host, option, value = None):
    Dhcp().setHostStatement(host, option, value)

def setHostHWAddress(host, address):
    Dhcp().setHostHWAddress(host, address)

def getHostHWAddress(host, address):
    Dhcp().getHostHWAddress(host, address)

def getHost(host):
    return Dhcp().getHost(host)

# Log

def getDhcpLog(filter = ''):
    return DhcpLogView().getLog(filter)

def getDnsLog(filter = ''):
    return DnsLogView().getLog(filter)

# Service management

def dhcpService(command):
    return DhcpService().command(command)

def dnsService(command):
    return DnsService().command(command)

class NetworkConfig(PluginConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        # DHCP conf
        self.dhcpDN = self.get("dhcp", "dn")
        self.dhcpPidFile = self.get("dhcp", "pidfile")
        self.dhcpInit = self.get("dhcp", "init")
        self.dhcpLogFile = self.get("dhcp", "logfile")
        # DNS conf
        self.dnsDN = self.get("dns", "dn")        
        self.dnsPidFile = self.get("dns", "pidfile")
        self.dnsInit = self.get("dns", "init")
        self.dnsLogFile = self.get("dns", "logfile")

    def setDefault(self):
        PluginConfig.setDefault(self)
        self.bindRootPath = "/etc/bind/"
        self.bindLdap = os.path.join(self.bindRootPath, "named.conf.ldap")
        self.bindLdapDir = os.path.join(self.bindRootPath, "named.ldap")
        self.bindUser = "bind"

class Dns(ldapUserGroupControl):

    def __init__(self, conffile = None, conffilebase = None):
        lmc.plugins.base.ldapUserGroupControl.__init__(self, conffilebase)
        self.configDns = NetworkConfig("network", conffile)
        self.reverseMarkup = "Reverse:"
        self.reversePrefix = ".in-addr.arpa"
        self.templateZone = """
// Auto generated by LMC agent - edit at your own risk !
zone "%(zone)s" {
    type master;
    database "ldap ldap://%(ldapurl)s????!bindname=%(admin)s,!x-bindpw=%(passwd)s 172800";
    notify yes;
};
"""

    def reverseZone(self, network):
        ret = network.split(".")
        ret.reverse()
        return ".".join(ret) + self.reversePrefix

    def getZoneNetworkAddress(self, zone):
        """
        Return the network address of a zone thanks to its reverse
        """
        rev = self.getReverseZone(zone)
        ret = None
        if rev: ret = self.translateReverse(rev)
        return ret

    def getAllZonesNetworkAddresses(self):
        """
        Return all the network addresses that are configured in the DNS.
        We only use the reverse zone to get them
        """
        ret = []
        for result in self.getZones(self.reversePrefix, True):
            ret.append(self.translateReverse(result[1]["zoneName"][0]))
        return ret
        
    def getReverseZone(self, name):
        """
        Return the name of the reverse zone of a zone
        """
        zones = self.getZones(name)
        ret = None
        if zones:
            try:
                txts = zones[0][1]["tXTRecord"]
            except KeyError:
                txts = []
            rev = None
            for txt in txts:
                if txt.startswith(self.reverseMarkup):
                    rev = txt.replace(self.reverseMarkup, "").strip()
                    break
            ret = rev
        return ret

    def getZoneObjects(self, name, filt = None):
        """
        Return the objects defined in a zone
        """
        if filt:
            filt = "*" + filt.strip() + "*"
        else:
            filt = "*"
        search = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=%s))" % (name, filt), None)
        ret = []
        for result in search:
            relative = result[1]["relativeDomainName"][0]
            # Don't count these entries
            if relative != "@" and relative != name:
                ret.append(result)
        return ret

    def getZoneObjectsCount(self, name):
        """
        Return the number of objects defined in a zone
        """
        search = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s))" % (name), ["relativeDomainName"])
        count = 0
        for result in search:
            relative = result[1]["relativeDomainName"][0]
            # Don't count these entries
            if relative != "@" and relative != name:
                count = count + 1
        return count

    def getZone(self, zoneName):
        return self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=%s))" % (zoneName, zoneName), None)        
        
    def getZones(self, filt = "", reverse = False):
        """
        Return all available DNS zones. Reverse zones are returned only if reverse = True
        """
        filt = filt.strip()
        if not filt: filt = "*"
        else: filt = "*" + filt + "*"
        search = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=%s))" % (filt, filt), None)
        ret = []
        for result in search:
            if result[1]["zoneName"] == result[1]["relativeDomainName"]:
                if self.reversePrefix in result[1]["zoneName"][0]:
                    # Reverse zone
                    if reverse: ret.append(result)
                else: ret.append(result)
        return ret

    def zoneExists(self, zone):
        """
        Return true if the given zone exists
        """
        return len(self.getZones(zone)) > 0

    def addZone(self, name, network = None, netmask = None, reverse = False, description = None, nameserver = "ns", nameserverip = None):
        """
        @param name: the zone name
        @param network: the network address defined in this zone (needed to build the reverse zone)
        @param netmask: the netmask address (needed to build the reverse zone)
        """
        if reverse:
            if network == None or netmask == None:
                raise "Won't create reverse zone as asked, missing network or netmask"
            netmask = int(netmask)
            # Build network address start according to netmask
            elements = network.split(".")
            if netmask == 8:
                network = elements[0]
            elif netmask == 16:
                network = ".".join(elements[0:2])
            elif netmask == 24:
                network = ".".join(elements[0:3])
            else:
                raise "Won't create reverse zone as asked, netmask is not 8, 16 or 24"

        f = open(os.path.join(self.configDns.bindLdapDir, name), "w")
        d = {
            "zone" : name,
            "ldapurl" : self.ldapHost + "/" + self.configDns.dnsDN,
            "admin": self.config.get("ldap", "rootName").replace(",", "%2c").replace(" ", ""),
            "passwd" : self.config.get("ldap", "password")
            }    
        f.write(self.templateZone % d)
        if reverse:
            d["zone"] = network
            f.write(self.templateZone % d)
        f.close()
        os.chmod(os.path.join(self.configDns.bindLdapDir, name), 0640)

        f = open(self.configDns.bindLdap, "r")
        found = False
        toadd = 'include "' + os.path.join(self.configDns.bindLdapDir, name) + '";\n'
        for line in f:
            if line == toadd:
                found = True
                break
        f.close()
        if not found:
            f = open(self.configDns.bindLdap, "a")
            f.write(toadd)
            f.close()

        # Create the needed zones object in LDAP
        if reverse:
            reverseZone = self.reverseZone(network)
            self.addDnsZone(reverseZone)
        else:
            reverseZone = None
        self.addDnsZone(name, description, reverseZone)
        
        # Fill SOA
        self.addSOA(name)
        ns = nameserver + "." + name + "."
        rec = {
            "nameserver" : ns,
            "emailaddr" :  "admin." + name + ".",
            "serial" : self.computeSerial(),
            "refresh" : "2D",
            "retry" : "15M",
            "expiry" : "2W",
            "minimum" : "1H",
            }
        self.setSOARecord(name, rec)
        self.setNSRecord(name, ns)

        if nameserverip:
            # Add a A record for the primary nameserver
            self.addRecordA(nameserver, nameserverip, name)

    def delZone(self, zone):
        """
        Delete a DNS zone with its reverse zone
        
        @param name: the zone name to delete     
        """
        revzone = self.getReverseZone(zone)
        self.delRecursiveEntry("ou=" + zone + "," + self.configDns.dnsDN)
        if revzone: self.delRecursiveEntry("ou=" + revzone + "," + self.configDns.dnsDN)
        os.unlink(os.path.join(self.configDns.bindLdapDir, zone))
        newcontent = []
        f = open(self.configDns.bindLdap, "r")
        for line in f:
            if not "/" + zone + '";' in line:
                newcontent.append(line)
        f.close()
        f = open(self.configDns.bindLdap, "w+")
        for line in newcontent:
            f.write(line)
        f.close()
        
    def addDnsZone(self, zoneName, description = None, container = None):
        """
        Add a dNSZone object in the LDAP.
        """
        if not container: container = zoneName
        # Create the container of this zone and its reverses if it does not exist
        try:
            self.addOu(container, self.configDns.dnsDN)
        except ldap.ALREADY_EXISTS:
            pass
        # Create the ou defining this zone and that will contain all records
        self.addOu(zoneName, "ou=" + container + "," + self.configDns.dnsDN)
        dn = "zoneName=" + zoneName + "," + "ou=" + zoneName + "," + "ou=" + container + "," + self.configDns.dnsDN
        entry = {
            "zoneName" : zoneName,
            "objectClass" : ["top", "dNSZone"],
            "relativeDomainName" : zoneName,
            }
        if description: entry["tXTRecord"] = [description]
        attributes = [ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)

    def addSOA(self, zoneName, container = None, dnsClass = "IN"):
        if not container: container = zoneName
        dn = "relativeDomainName=@," + "ou=" + zoneName + "," + "ou=" + container + "," + self.configDns.dnsDN
        entry = {
            "zoneName" : zoneName,
            "objectClass" : ["top", "dNSZone"],
            "relativeDomainName" : "@",
            "dnsClass" : dnsClass
            }
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)        

    def setSOARecord(self, zoneName, record):
        soa = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=@))" % zoneName, None)
        if soa:
            soaDN = soa[0][0]
            s = "%(nameserver)s %(emailaddr)s %(serial)s %(refresh)s %(retry)s %(expiry)s %(minimum)s" % record
            self.l.modify_s(soaDN, [(ldap.MOD_REPLACE, "sOARecord", [s])])

    def setNSRecord(self, zoneName, nameserver):
        soa = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=@))" % zoneName, None)
        if soa:
            soaDN = soa[0][0]
            self.l.modify_s(soaDN, [(ldap.MOD_REPLACE, "nSRecord", [nameserver])])
        # Also sync SOA record if there is one
        soaRecord = self.getSOARecord(zoneName)
        if soaRecord:
            soaRecord["nameserver"] = nameserver
            self.setSOARecord(zoneName, soaRecord)

    def setZoneDescription(self, zoneName, description):
        zone = self.getZone(zoneName)
        if zone:
            zoneDN = zone[0][0]
            self.l.modify_s(zoneDN, [(ldap.MOD_REPLACE, "tXTRecord", [description])])

    def getSOARecord(self, zoneName):
        """
        Return the content of the SOA record of a zone

        @rtype: dict
        """
        ret = {}
        soa = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=@))" % zoneName, ["soaRecord"])
        if soa:
            try:
                ret["nameserver"], ret["emailaddr"], ret["serial"], ret["refresh"], ret["retry"], ret["expiry"], ret["minimum"] = soa[0][1]["sOARecord"][0].split()
            except KeyError:
                pass
        return ret            

    def searchReverseZone(self, ip):
        """
        Search a convenient reverse zone for a IP
        """
        elements = ip.split(".")
        elements.pop()
        elements.reverse()
        while elements:
            rev = ".".join(elements) + self.reversePrefix
            ret = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s))" % rev, None)
            if ret:
                elements.reverse()
                # Return the reverse zone name and how the IPs are beginning in this zone
                return rev, ".".join(elements)
            elements.pop(0)
        return None

    def addRecordA(self, hostname, ip, zone, dnsClass = "IN"):
        """
        Add an entry for a zone and its reverse zone
        """
        revZone = self.getReverseZone(zone)
        #revZone, ipStart = self.searchReverseZone(ip)
        dn = "relativeDomainName=" + hostname + "," + "ou=" + zone + "," + self.configDns.dnsDN
        entry = {
            "relativeDomainName" : hostname,
            "objectClass" : ["top", "dNSZone"],
            "zoneName" : zone,
            "dNSClass" : dnsClass,
            "aRecord" : ip,
        }
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)

        if revZone:
            # Add host to corresponding reverse zone if there is one
            ipStart = self.translateReverse(revZone)
            ipLast = ip.replace(ipStart, "")
            elements = ipLast.split(".")
            elements.reverse()
            relative = ".".join(elements)
            dn = "relativeDomainName=" + relative + "," + "ou=" + revZone + "," + self.configDns.dnsDN
            entry = {
                "relativeDomainName" : relative,
                "objectClass" : ["top", "dNSZone"],
                "zoneName" : revZone,
                "dNSClass" : dnsClass,
                "pTRRecord" : hostname + "." + zone + ".",
            }
            attributes=[ (k,v) for k,v in entry.items() ]
            self.l.add_s(dn, attributes)

    def delRecord(self, hostname, zone):
        """
        Remove a host from a zone.
        Remove it from the reverse zone too.
        """
        revzone = self.getReverseZone(zone)
        host = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s)(relativeDomainName=%s))" % (zone, hostname), None)
        revhost = self.l.search_s(self.configDns.dnsDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dNSZone)(zoneName=%s)(pTRRecord=%s))" % (revzone, hostname + "." + zone + "."), None)
        if host: self.l.delete_s(host[0][0])
        if revhost: self.l.delete_s(revhost[0][0])

    def computeSerial(self, oldSerial = None):
        return int(time.time())

    def translateReverse(self, revZone):
        revZone = revZone.replace(self.reversePrefix, "")
        elements = revZone.split(".")
        elements.reverse()
        return ".".join(elements)
        

class Dhcp(ldapUserGroupControl):

    def __init__(self, conffile = None, conffilebase = None):
        lmc.plugins.base.ldapUserGroupControl.__init__(self, conffilebase)
        self.configDhcp = NetworkConfig("network", conffile)

    # DHCP options management (line with "options name value;")

    def getObjectOptions(self, dn):
        try:
            ret = self.l.search_s(dn, ldap.SCOPE_BASE, "(objectClass=dhcpOptions)", ["dhcpOption"])[0][1]["dhcpOption"]
        except KeyError:
            ret = []
        return ret

    def setObjectOption(self, dn, option, value):
        # If value == "", remove the option
        if not value.strip('"'): value = None
        options = self.getObjectOptions(dn)
        toremove = None
        for oldoption in options:
            optname, optvalue = oldoption.split(" ", 1)
            if option == optname:
                toremove = oldoption
        if toremove: options.remove(toremove)
        if value: options.append(option + " " + str(value))
        if not options:
            try:
                self.l.modify_s(dn, [(ldap.MOD_DELETE, "dhcpOption", None)])
            except ldap.NO_SUCH_ATTRIBUTE:
                pass
        else:
            self.l.modify_s(dn, [(ldap.MOD_REPLACE, "dhcpOption", options)])        

    # DHCP statements management (line with "name value;")

    def getObjectStatements(self, dn):
        try:
            ret = self.l.search_s(dn, ldap.SCOPE_BASE, "(objectClass=*)", ["dhcpStatements"])[0][1]["dhcpStatements"]
        except KeyError:
            ret = []
        return ret

    def setObjectStatement(self, dn, option, value):
        options = self.getObjectStatements(dn)
        toremove = None
        for oldoption in options:
            if option in oldoption:
                toremove = oldoption
        if toremove: options.remove(toremove)
        if value: options.append(option + " " + str(value))
        if not options:
            self.l.modify_s(dn, [(ldap.MOD_DELETE, "dhcpStatements", None)])
        else:
            self.l.modify_s(dn, [(ldap.MOD_REPLACE, "dhcpStatements", options)])

    # DHCP service config management

    def addServiceConfig(self, name):
        """
        Add a DHCP service config container entry in directory
        """
        dn = "cn=" + name + "," + self.configDhcp.dhcpDN
        entry = {
            "cn" : name,
            "dhcpPrimaryDN" : self.configDhcp.dhcpDN,
            "objectClass" : ["top", "dhcpService"]
            }
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)

    def getServiceConfig(self):
        """
        Return all available DHCP service config containers
        """
        return self.l.search_s(self.configDhcp.dhcpDN, ldap.SCOPE_SUBTREE, "(objectClass=dhcpService)", None)

    # DHCP server management

    def addServer(self, name, dhcpServiceDN = None):
        """
        Add a DHCP server in directory
        """
        if dhcpServiceDN: raise "NYI"
        else:
            dhcpServiceDN = self.getServiceConfig()[0][0]
        dn = "cn=" + name + "," + self.configDhcp.dhcpDN
        entry = {
            "cn" : name,
            "dhcpServiceDN" : dhcpServiceDN,
            "objectClass" : ["top", "dhcpServer"]
            }
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)

    def getServer(self):
        """
        Return all available DHCP server config containers
        """
        return self.l.search_s(self.configDhcp.dhcpDN, ldap.SCOPE_SUBTREE, "(objectClass=dhcpServer)", None)
        
    def setServicePrimaryServer(self, serviceName, serverName):
        serverDN = ""
        for server in self.getServer():
            if server[1]["cn"][0] == serverName:
                serverDN = server[0]
        serviceDN = ""
        for service in self.getServiceConfig():
            if service[1]["cn"][0] == serviceName:
                serviceDN = service[0]
        if serverDN and serviceDN:
            self.l.modify_s(serviceDN, [(ldap.MOD_REPLACE, "dhcpPrimaryDN", serverDN)])

    def getServiceConfigOption(self):
        try:
            ret = self.getServiceConfig()[0][1]["dhcpStatements"]
        except KeyError:
            ret = []
        return ret

    def setServiceConfigStatement(self, option, value):
        services = self.getServiceConfig()
        if services:
            serviceDN = services[0][0]
            self.setObjectStatement(serviceDN, option, value)

    # DHCP subnet management

    def getSubnets(self, filt = None):
        filt = filt.strip()
        if not filt: filt = "*"
        else: filt = "*" + filt + "*"
        return self.l.search_s(self.configDhcp.dhcpDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpSubnet)(cn=%s))" % filt, None)

    def getSubnet(self, subnet = None):
        if not subnet: subnet = "*"
        return self.l.search_s(self.configDhcp.dhcpDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpSubnet)(cn=%s))" % subnet, None)

    def getSubnetOptions(self, subnet):
        try:
            ret = self.getSubnet(subnet)[0][1]["dhcpOption"]
        except KeyError:
            ret = []
        return ret

    def setSubnetOption(self, subnet, option, value = None):
        subnets = self.getSubnet(subnet)
        if subnets:
            subnetDN = subnets[0][0]
            self.setObjectOption(subnetDN, option, value)

    def setSubnetStatement(self, subnet, option, value = None):
        subnets = self.getSubnet(subnet)
        if subnets:
            subnetDN = subnets[0][0]
            self.setObjectStatement(subnetDN, option, value)

    def setSubnetDescription(self, subnet, description):
        subnets = self.getSubnet(subnet)
        if subnets:
            subnetDN = subnets[0][0]
            self.l.modify_s(subnetDN, [(ldap.MOD_REPLACE, "dhcpComments", description)])

    def setSubnetNetmask(self, subnet, netmask):
        subnets = self.getSubnet(subnet)
        if subnets:
            subnetDN = subnets[0][0]
            self.l.modify_s(subnetDN, [(ldap.MOD_REPLACE, "dhcpNetMask", netmask)])

    def addSubnet(self, network, netmask, name = None):
        serviceDN = self.getServiceConfig()[0][0]
        if not name: name = network + "/" + str(netmask)
        dn = "cn=" + network + "," + serviceDN
        entry = {
            "cn" : network,
            "dhcpNetMask" : str(netmask),
            "dhcpComments" : name,
            "objectClass" : ["top", "dhcpSubnet", "dhcpOptions"]
            }
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)    

    def delSubnet(self, network):
        subnets = self.getSubnet()
        for subnet in subnets:
            if subnet[1]["cn"][0] == network:
                self.delRecursiveEntry(subnet[0])
                break

    def getSubnetHosts(self, network, filt = None):
        if filt:
            filt = "*" + filt.strip() + "*"
        else:
            filt = "*"
        subnets = self.getSubnet(network)
        ret = []
        if subnets:
            subnetDN = subnets[0][0]
            ret = self.l.search_s(subnetDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpHost)(|(cn=%(filt)s)(dhcpHWAddress=ethernet%(filt)s)(dhcpStatements=fixed-address%(filt)s)))" % {"filt" : filt}, None)
        return ret

    def getSubnetHostsCount(self, network):
        subnets = self.getSubnet(network)
        ret = []
        if subnets:
            subnetDN = subnets[0][0]
            ret = self.l.search_s(subnetDN, ldap.SCOPE_SUBTREE, "(objectClass=dhcpHost)", ["cn"])
        return len(ret)

    # DHCP pool management

    def getPool(self, pool = None):
        if not pool: pool = "*"
        return self.l.search_s(self.configDhcp.dhcpDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpPool)(cn=%s))" % pool, None)

    def getPoolOptions(self, pool):
        try:
            ret = self.getPool(pool)[0][1]["dhcpOption"]
        except KeyError:
            ret = []
        return ret

    def setPoolOption(self, pool, option, value = None):
        pools = self.getPool(pool)
        if pools:
            poolDN = pools[0][0]
            self.setObjectOption(poolDN, option, value)

    def setPoolStatement(self, pool, option, value = None):
        pools = self.getPool(pool)
        if pools:
            poolDN = pools[0][0]
            self.setObjectStatement(poolDN, option, value)

    def addPool(self, subnet, poolname, start, end):
        dhcprange = start + " " + end
        subnets = self.getSubnet(subnet)
        dn = "cn=" + poolname + "," + subnets[0][0]
        entry = {
            "cn" : poolname,
            "dhcpRange" : dhcprange,
            "objectClass" : ["top", "dhcpPool", "dhcpOptions"]
            }            
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)    
        
    def delPool(self, poolname):
        pools = self.getPool(poolname)
        for pool in pools:
            if pool[1]["cn"][0] == poolname:
                self.delRecursiveEntry(pool[0])
                break        

    def setPoolRange(self, pool, start, end):
        pools = self.getPool(pool)
        if pools:
            poolDN = pools[0][0]
            self.l.modify_s(poolDN, [(ldap.MOD_REPLACE, "dhcpRange", start + " " + end)])

    # DHCP group management

    def getGroup(self, group = None):
        if not group: group = "*"
        return self.l.search_s(self.configDhcp.dhcpDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpGroup)(cn=%s))" % group, None)

    def getGroupOptions(self, group):
        try:
            ret = self.getGroup(group)[0][1]["dhcpOption"]
        except KeyError:
            ret = []
        return ret

    def setGroupOption(self, group, option, value = None):
        groups = self.getGroup(group)
        if groups:
            groupDN = groups[0][0]
            self.setObjectOption(groupDN, option, value)

    def addGroup(self, subnet, groupname):
        subnets = self.getSubnet(subnet)
        dn = "cn=" + groupname + "," + subnets[0][0]
        entry = {
            "cn" : groupname,
            "objectClass" : ["top", "dhcpGroup", "dhcpOptions"]
            }            
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)    
        
    def delGroup(self, groupname):
        groups = self.getGroup(groupname)
        for group in groups:
            if group[1]["cn"][0] == groupname:
                self.delRecursiveEntry(group[0])
                break        

    # DHCP host management

    def getHost(self, host = None):
        if not host: host = "*"
        return self.l.search_s(self.configDhcp.dhcpDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpHost)(cn=%s))" % host, None)

    def getHostOptions(self, host):
        try:
            ret = self.getHost(host)[0][1]["dhcpOption"]
        except KeyError:
            ret = []
        return ret

    def setHostOption(self, host, option, value = None):
        hosts = self.getHost(host)
        if hosts:
            hostDN = hosts[0][0]
            self.setObjectOption(hostDN, option, value)

    def setHostStatement(self, host, option, value):
        hosts = self.getHost(host)
        if hosts:
            hostDN = hosts[0][0]
            self.setObjectStatement(hostDN, option, value)

    def setHostHWAddress(self, host, address):
        hosts = self.getHost(host)
        if hosts:
            hostDN = hosts[0][0]
            self.l.modify_s(hostDN, [(ldap.MOD_REPLACE, "dhcpHWAddress", ["ethernet " + address])])

    def getHostHWAddress(self, host, address):
        try:
            ret = self.getHost(host)[0][1]["dhcpHWAddress"][0]
            ret = ret.split()[1]
        except KeyError:
            ret = None
        return ret

    def addHostToSubnet(self, subnet, hostname):
        subnets = self.getSubnet(subnet)
        dn = "cn=" + hostname + "," + subnets[0][0]
        entry = {
            "cn" : hostname,
            "objectClass" : ["top", "dhcpHost", "dhcpOptions"]
            }            
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)    

    def addHostToGroup(self, groupname, hostname):
        groups = self.getGroup(groupname)
        dn = "cn=" + hostname + "," + groups[0][0]
        entry = {
            "cn" : hostname,
            "objectClass" : ["top", "dhcpHost", "dhcpOptions"]
            }            
        attributes=[ (k,v) for k,v in entry.items() ]
        self.l.add_s(dn, attributes)    

    def delHost(self, hostname):
        hosts = self.getHost(hostname)
        for host in hosts:
            if host[1]["cn"][0] == hostname:
                self.delRecursiveEntry(host[0])
                break

class ServiceManager:
    """
    Class to know a service state, and start/stop/reload it
    """

    def __init__(self, pidfile, initfile):
        self.pidfile = pidfile
        self.initfile = initfile

    def isRunning(self):
        ret = False
        if os.path.exists(self.pidfile):
            f = open(self.pidfile)
            pid = f.read()
            f.close()
            ret = os.path.isdir(os.path.join("/proc", pid.strip()))
        return ret

    def start(self):
        lmctools.shLaunch(self.initfile + " start")

    def stop(self):
        lmctools.shLaunch(self.initfile + " stop")

    def restart(self):
        lmctools.shLaunch(self.initfile + " restart")

    def reLoad(self):
        lmctools.shLaunch(self.initfile + " reload")

    def command(self, command):
        ret = None
        if command == "status":
            ret = self.isRunning()
        elif command == "start":
            self.start()
        elif command == "stop":
            self.stop()
        elif command == "restart":
            self.restart()
        elif command == "reload":
            self.reLoad()
        return ret

class DhcpService(ServiceManager):

    def __init__(self, conffile = None):
        self.config = NetworkConfig("network", conffile)
        ServiceManager.__init__(self, self.config.dhcpPidFile, self.config.dhcpInit)

class DnsService(ServiceManager):

    def __init__(self, conffile = None):
        self.config = NetworkConfig("network", conffile)
        ServiceManager.__init__(self, self.config.dnsPidFile, self.config.dnsInit)

class DhcpLogView(LogView):
    """
    Get DHCP service log content.
    """

    def __init__(self):
        config = NetworkConfig("network")
        self.logfile = config.dhcpLogFile
        self.maxElt= 200
        self.file = open(self.logfile, 'r')
        self.pattern = {
            "dhcpd-syslog" : "^(?P<b>[A-z]{3}) *(?P<d>[0-9]+) (?P<H>[0-9]{2}):(?P<M>[0-9]{2}):(?P<S>[0-9]{2}) .* dhcpd: (?P<extra>.*)$",
            }

class DnsLogView(LogView):
    """
    Get DNS service log content.
    """

    def __init__(self):
        config = NetworkConfig("network")
        self.logfile = config.dnsLogFile
        self.maxElt= 200
        self.file = open(self.logfile, 'r')
        self.pattern = {
            "named-syslog" : "^(?P<b>[A-z]{3}) *(?P<d>[0-9]+) (?P<H>[0-9]{2}):(?P<M>[0-9]{2}):(?P<S>[0-9]{2}) .* named\[[0-9]+\]: (?P<extra>.*)$",
            }
