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

import ldap
from mmc.plugins.base import ldapUserGroupControl, LogView
from tools import *
from mmc.support.mmctools import ServiceManager
import mmc.plugins.network

class Dhcp(ldapUserGroupControl):

    def __init__(self, conffile = None, conffilebase = None):
        ldapUserGroupControl.__init__(self, conffilebase)
        self.configDhcp = mmc.plugins.network.NetworkConfig("network", conffile)

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
        if value:
            tmp = option + " " + str(value)
            options.append(tmp.strip())
        if not options:
            try:
                self.l.modify_s(dn, [(ldap.MOD_DELETE, "dhcpStatements", None)])
            except ldap.NO_SUCH_ATTRIBUTE:
                pass
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
            if description:
                self.l.modify_s(subnetDN, [(ldap.MOD_REPLACE, "dhcpComments", description)])
            else:
                self.l.modify_s(subnetDN, [(ldap.MOD_DELETE, "dhcpComments", None)])

    def setSubnetNetmask(self, subnet, netmask):
        subnets = self.getSubnet(subnet)
        if subnets:
            subnetDN = subnets[0][0]
            self.l.modify_s(subnetDN, [(ldap.MOD_REPLACE, "dhcpNetMask", netmask)])

    def setSubnetAuthoritative(self, subnet, flag = True):
        """
        Set the subnet as authoritative or 'not authoritative'

        @param subnet: the network address of the subnet
        @type subnet: str

        @param flag: whether the subnet is authoritative or not
        @type flag: bool
        """
        subnets = self.getSubnet(subnet)
        if subnets:
            subnetDN = subnets[0][0]
            options = self.getObjectStatements(subnetDN)
            newoptions = []
            for option in options:
                if not option in ["authoritative", "not authoritative"]:
                    newoptions.append(option)
            if flag:
                newoptions.append("authoritative")
            else:
                newoptions.append("not authoritative")
            self.l.modify_s(subnetDN, [(ldap.MOD_REPLACE, "dhcpStatements", newoptions)])

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

    def getPoolRange(self, pool):
        """
        Return the IP range of a pool
        """
        ret = None
        pools = self.getPool(pool)        
        if pools:
            fields = pools[0][1]
            try:
                dhcpRange = fields["dhcpRange"][0]
            except KeyError:
                pass
            else:
                ret = dhcpRange.split()
        return ret
            
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

    def getHost(self, subnet, host = None):
        if not host: host = "*"
        subnetDN = self.getSubnet(subnet)[0][0]
        return self.l.search_s(subnetDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpHost)(cn=%s))" % host, None)

    def getHostOptions(self, subnet, host):
        try:
            ret = self.getHost(subnet, host)[0][1]["dhcpOption"]
        except KeyError:
            ret = []
        return ret

    def setHostOption(self, subnet, host, option, value = None):
        hosts = self.getHost(subnet, host)
        if hosts:
            hostDN = hosts[0][0]
            self.setObjectOption(hostDN, option, value)

    def setHostStatement(self, subnet, host, option, value):
        hosts = self.getHost(subnet, host)
        if hosts:
            hostDN = hosts[0][0]
            self.setObjectStatement(hostDN, option, value)

    def setHostHWAddress(self, subnet, host, address):
        hosts = self.getHost(subnet, host)
        if hosts:
            hostDN = hosts[0][0]
            self.l.modify_s(hostDN, [(ldap.MOD_REPLACE, "dhcpHWAddress", ["ethernet " + address])])

    def getHostHWAddress(self, subnet, host, address):
        try:
            ret = self.getHost(subnet, host)[0][1]["dhcpHWAddress"][0]
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

    def delHost(self, subnet, hostname):
        hosts = self.getHost(subnet, hostname)
        for host in hosts:
            if host[1]["cn"][0] == hostname:
                self.delRecursiveEntry(host[0])
                break

    def hostExistsInSubnet(self, subnet, hostname):
        subnets = self.getSubnet(subnet)
        ret = False
        if subnets:
            subnetDN = subnets[0][0]
            result = self.l.search_s(subnetDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpHost)(cn=%s))" % hostname, None)
            ret = len(result) > 0
        return ret

    def ipExistsInSubnet(self, subnet, ip):
        subnets = self.getSubnet(subnet)
        ret = False
        if subnets:
            subnetDN = subnets[0][0]
            result = self.l.search_s(subnetDN, ldap.SCOPE_SUBTREE, "(&(objectClass=dhcpHost)(dhcpStatements=fixed-address %s))" % ip, None)
            ret = len(result) > 0
        return ret

    def getSubnetFreeIp(self, subnet, startAt = None):
        """
        Return the first available IP address of a subnet.
        If startAt is given, start the search from this IP.

        IPs inside subnet dynamic pool range are never returned.

        If none available, return an empty string.

        @param subnet: subnet name in LDAP
        @type subnet: str

        @param startAt: IP to start search
        @type startAt: str
        """
        ret = ""
        subnetDN = self.getSubnet(subnet)
        network = subnetDN[0][1]["cn"][0]
        netmask = int(subnetDN[0][1]["dhcpNetMask"][0])
        poolRange = self.getPoolRange(subnet)
        if poolRange:
            rangeStart, rangeEnd = poolRange
        if startAt: ip = startAt
        else: ip = network
        ip = ipNext(network, netmask, ip)
        while ip:
            if not self.ipExistsInSubnet(subnet, ip):
                if poolRange:
                    if not ipInRange(ip, rangeStart, rangeEnd):
                        ret = ip
                        break
                else:
                    ret = ip
                    break
            ip = ipNext(network, netmask, ip)
        return ret

class DhcpLeases:

    def __init__(self, conffile = None, conffilebase = None):
        self.config = mmc.plugins.network.NetworkConfig("network", conffile)
        self.leases = self.__parse()

    def __parse(self):
        COMMENT = "#"
        BEGIN = "lease"
        STARTS = "starts"
        ENDS = "ends"
        STATE = "binding state"
        HARDWARE = "hardware ethernet"
        HOSTNAME = "client-hostname"
        END = "}"
        leases = {}
        leasesFile = file(self.config.dhcpLeases)
        current = None
        for line in leasesFile:
            line = line.strip().strip(";")
            if line and not line.startswith(COMMENT):
                if line.startswith(BEGIN):
                    current = line.split()[1]
                    leases[current] = {}
                elif current:
                    if line.startswith(STATE):
                        leases[current]["state"] = line.split()[2]
                    elif line.startswith(HARDWARE):
                        leases[current]["hardware"] = line.split()[2]
                    elif line.startswith(HOSTNAME):
                        leases[current]["hostname"] = line.split()[1].strip('"')
                    else:
                        pass
        leasesFile.close()
        return leases

    def get(self):
        return self.leases


class DhcpService(ServiceManager):

    def __init__(self, conffile = None):
        self.config = mmc.plugins.network.NetworkConfig("network", conffile)
        ServiceManager.__init__(self, self.config.dhcpPidFile, self.config.dhcpInit)


class DhcpLogView(LogView):
    """
    Get DHCP service log content.
    """

    def __init__(self):
        config = mmc.plugins.network.NetworkConfig("network")
        self.logfile = config.dhcpLogFile
        self.maxElt= 200
        self.file = open(self.logfile, 'r')
        self.pattern = {
            "dhcpd-syslog1" : "^(?P<b>[A-z]{3}) *(?P<d>[0-9]+) (?P<H>[0-9]{2}):(?P<M>[0-9]{2}):(?P<S>[0-9]{2}) .* dhcpd: (?P<op>DHCP[A-Z]*) (?P<extra>.*)$",
            "dhcpd-syslog2" : "^(?P<b>[A-z]{3}) *(?P<d>[0-9]+) (?P<H>[0-9]{2}):(?P<M>[0-9]{2}):(?P<S>[0-9]{2}) .* dhcpd: (?P<extra>.*)$",
            }
