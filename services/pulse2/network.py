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

""" Network utils module """

import socket
import struct
import fcntl
import logging
import inspect
import os
import subprocess

from pulse2.utils import isdigit, isMACAddress

log = logging.getLogger()

class NetUtils :
    """ Common network utils """

    @classmethod
    def get_netmask_and_gateway(cls):
        """
        Getting the server's netmask & gateway 

        @return: netmask and gateway 
        @rtype: tuple
        """
        SIOCGIFNETMASK = 0x891b

        filename = "/proc/net/route"

        route = []
        try :
            r_file = open(filename, "r") 

            for line in r_file.readlines():
                r_fields = line.strip().split()
                if r_fields[1] != '00000000' or not int(r_fields[3], 16) & 2:
                    continue
                route.append(r_fields)

            r_file.close()

        except IOError :

            log.warn("Cannot read file '%s'" % filename)
            log.warn("Ignore to get the netmask and gateway")

            return False, False


        iface = route[0][0]

        n_sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        netmask = fcntl.ioctl(n_sck, SIOCGIFNETMASK, struct.pack('256s', iface))[20:24]
        gateway = struct.pack("<L", int(route[0][2], 16))

        return socket.inet_ntoa(netmask), socket.inet_ntoa(gateway)

    @classmethod
    def on_same_network(cls, ip1, ip2):
        """
        Test of those IP addresses on the same network.

        @param ip1: first IP adddress
        @type ip1: string

        @param ip2: second IP adddress
        @type ip2: string

        @return: True if this two IP addresses are in the same network.
        @rtype: bool      
        """
        ip_list1 = ip1.split(".")
        ip_list2 = ip2.split(".")

        assert len(ip_list1) == len(ip_list2)

        for i in range(3):
            if ip_list1[i] != ip_list2[i] :
                return False

        return True


    @classmethod
    def has_enough_info(cls, iface):
        """
        Test if interface has enough informations for resolving methods.

        @param iface: networking parameters of interface
        @type iface: dict

        @return: True if enough info
        @rtype: bool
        """
        for key in ["ip", "mac", "netmask"] :
            # if one of required key is missing
            if key not in iface :
                return False
            # if empty
            if not iface[key] or len(iface[key].strip()) == 0 :
                return False
        return True

    @classmethod
    def is_ip4_address(cls, candidate):
        """
        Validating the IPv4 address format.

        @param candidate: candidate string to validate
        @str candidate: str

        @return: True if correct IPv4 format 
        @rtype: bool
        """
        if "." in candidate :
            if len(candidate.split(".")) == 4 :
                for num in candidate.split(".") :
                    if not isdigit(num) :
                        return False
                return True
        return False
                



class ResolvingCallable :
    """ 
    An abstract class to implement a resolving callable.

    Inheriting this class ensure the creating a resolving method.
    This instance is identified by 'name' attribute and code placed 
    in __call__ method try to resolve a correct IP address.

    To pre-check of validity before the register a resolver
    use the 'validate' method which allows to prevent 
    an unauthorised execution.
    """

    name = None

    def __init__(self, networks, **kwargs):
        
        self.networks = networks

        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def validate(self):
        """ 
        Method to pre-check when the resolver is installed.

        Can be used to check the dependencies and prerequisites before
        the execution of resolving callable.

        @return: True if all the conditions are ok
        @rtype: bool
        """
        return True

    @classmethod
    def run_command(cls, cmd):
        """
        Execute a command in shell.

        @param cmd: command/expression to execute
        @type cmd: str

        @return: stdout of command
        @rtype: str
        """
        ps = subprocess.Popen(cmd, shell=True, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        try :
            out, err = ps.communicate()
        except Exception, e :
            log.error("While executing command: %s / Raised exception: %s" % (cmd, str(e)))

        if err :
            log.error("While executing command: %s / Received error mesage: %s" % (cmd, err))

        log.debug("Command executed (%s) result: %s" % (cmd, out))
        return out


    def __call__(self, target):
        raise NotImplementedError



class ChoosePerDNS (ResolvingCallable):

    name = "dns"

    def __call__(self, target):
        """ 
        Request passed on DNS server 

        @param target: container having complete networking info.
        @type target: list

        @return: IP address of reachable interface
        @rtype: string
        """
        hostname, ifaces = target
        ip = None
        try:
            ip = socket.gethostbyname(hostname)
        except Exception, exc:
            log.warn("Failed to get IP address by DNS request: %s" % str(exc))

        return ip

class ChoosePerIP (ResolvingCallable):

    name = "ip"

    def __call__(self, target):
        """ 
        Test when checked interface is on the same network

        @param target: container having complete networking info.
        @type target: list

        @return: IP address of reachable interface
        @rtype: string
 
        """
        hostname, ifaces = target

        for iface in ifaces :
            if NetUtils.has_enough_info(iface) :
                iface_ip = iface["ip"]
                iface_netmask = iface["netmask"]
                for pref_ip, pref_netmask in self.networks :
                    
                    log.debug("Comparing host '%s'(%s/%s) with my preferred network (%s/%s)" % 
                            (hostname, iface_ip, iface_netmask, pref_ip, pref_netmask))

                    if iface_netmask == pref_netmask and \
                    NetUtils.on_same_network(iface_ip, pref_ip) :

                        return iface_ip

        log.debug("No match host='%s'with preferred network(%s/%s)" % 
                   (hostname, pref_ip, pref_netmask))


        return None

class ChoosePerFQDN (ResolvingCallable):

    name = "fqdn"

    fqdn_path = "/usr/bin/host"

    def validate(self):
        if not os.path.exists(self.fqdn_path):
            log.warn("Command '%s' not found, omitting '%s' method." % (self.fqdn_path, self.name))
            return False
        else :
            return True


    def __call__(self, target):
        """ 
        Implemented for the backward compatibility with scheduler networking. 

        @param target: container having complete networking info.
        @type target: list

        @return: IP address of reachable interface
        @rtype: string
 
        """
        hostname, ifaces = target

        cmd = "%s -s 1 -t a %s 2>/dev/null 1>/dev/null" % (self.fqdn_path, hostname)

        out = self.run_command(cmd)

        if not out :
            return hostname
        else :
            return None

class ChoosePerHosts (ResolvingCallable):

    name = "hosts"

    hosts_path = "/usr/bin/getent"

    def validate(self):
        if not os.path.exists(self.hosts_path):
            log.warn("Command '%s' not found, omitting '%s' method." % (self.hosts_path, self.name))
            return False
        else :
            return True


    def __call__(self, target):
        """ 
        Implemented for the backward compatibility with scheduler networking. 

        @param target: container having complete networking info.
        @type target: list

        @return: IP address of reachable interface
        @rtype: string
 
        """
        hostname, ifaces = target

        cmd = "%s hosts %s 2>/dev/null 1>/dev/null" % (self.hosts_path, hostname)

        out = self.run_command(cmd)

        if not out :
            return hostname
        else :
            return None
               

class ChooseFirstComplete (ResolvingCallable) :

    name = "first"

    def __call__(self, target):
        """ 
        A "last chance" method. 
        Selected a first interface having enough networking info

        @param target: container having complete networking info.
        @type target: list

        @return: IP address of reachable interface
        @rtype: string
 
        """
        hostname, ifaces = target 
        for iface in ifaces :
            if NetUtils.has_enough_info(iface) :
                return iface["ip"]
        return None

class ChoosePerNMBLookup (ResolvingCallable) :

    name = "netbios"

    netbios_path = "/usr/bin/nmblookup"

    def validate(self):
        if not os.path.exists(self.netbios_path):
            log.warn("Samba utils seems not installed, omitting nmblookup method.")
            return False
        else :
            return True


    def __call__(self, target):
        """ 
        Samba based method - NetBIOS  

        @param target: container having complete networking info.
        @type target: list

        @return: IP address of reachable interface
        @rtype: string

        """
        hostname, ifaces = target 

        cmd = "%s -U server -R '%s'" % (self.netbios_path, hostname)

        out = self.run_command(cmd)
        # <example of a positive response> :
        # querying WORKSTATION_NAME on 192.168.1.255
        # 192.168.70.254 WORKSTATION_NAME<00>

        # <example of a negative response> :
        # querying WORKSTATION_NAME on 192.168.1.255
        # name_query failed to find name WORKSTATION_NAME

        # So, let's go to parse!
        if "\n" in out and len(out.split("\n")) > 1 :

            second_line = out.split("\n")[1]

            if not second_line.startswith("name_query") \
            and " " in second_line :

                ip = second_line.split(" ")[0]

                if NetUtils.is_ip4_address(ip) :
                    return ip

        return None
        
 
class IPResolversContainer :
    """ 
    Registering of all resolvers to get a correct network interface 
    of a client machine.
    """
    resolvers = []

    @classmethod
    def is_resolver(cls, candidate):
        """
        Test if candidate is a subclass of abstract frame 'ResolvingCallable'.

        @param candidate: candidate to check
        @type candidate: object

        @return: True if candidate is a resolver
        @rtype: bool
        """
        return inspect.isclass(candidate) and issubclass(candidate, ResolvingCallable)

    @classmethod
    def get_all_resolvers(cls):
        """ 
        Get of the all possibles resolvers in this module.

        return: list of resolvers
        rtype: list
        """
        return [r for r in globals().values() if cls.is_resolver(r)]
 
    def register_resolvers (self, resolve_order, resolvers=None, **kwargs) :
        """
        Registering of resolvers.

        @param resolve_order: list of resolver names to register
        @type resolve_order: list

        @param resolvers: resolvers to register
        @type resolvers: list

        kwargs parameters can be passed to resolvers from IPResolve constructor 
        to precize some parameters (typicaly command paths, etc.) 
        To prevent name conflicts, please use the name of resolver
        as a prefix, like 'dns_value', 'nmblookup_path', etc.
        """
        if not resolvers :
            resolvers = self.get_all_resolvers()
        else :
            # testing if all the externals resolvers are a ResolvingCallable subclass
            for i, candidate in enumerate(resolvers) :
                if not self.is_resolver(candidate) :
                    log.warn("Candidate %s isn't a resolver - ignoring" % str(candidate))
                    resolvers.pop(i)
            
        for name in resolve_order :
            
            for resolver_class in resolvers :
                resolver = resolver_class(self.networks, **kwargs)
                
                if name == resolver.name :
                    if resolver.validate():
                        self.resolvers.append(resolver)



class IPResolve (IPResolversContainer) :
    """
    Detecting a reachable network interface on local network 
    based on inventory info ("network" section).
    """

    def __init__(self, resolve_order, networks, **kwargs):
        """
        @param resolv_order: list of methods to apply
        @type resolv_order: list

        @param networks: list of preferred networks
        @type networks: list
        """
        self.resolve_order = resolve_order
        self.networks = networks

        self.register_resolvers(resolve_order, resolvers=None, **kwargs)

    def _validate_target (self, target):
        """ 
        Validating of target format 

        @param target: target container
        @type target: list

        @return: True if format is valid
        @rtype: bool
        """
        if not isinstance(target, tuple) or not isinstance(target, list):
            log.warn("Invalid target format.")
            return False

        if len(target) != 2 :
            log.warn("Invalid target format.")
            return False

        hostname, ifaces = target

        if not isinstance(ifaces, dict) :
            log.warn("Invalid target format.")
            return False

        for iface in ifaces :
            for key, value in iface.items():
                if not isinstance(value, str) :
                    log.warn("Invalid interface format, section '%s' (hostname='%s')" % (key, hostname))
                    return False
                if key == "mac" :
                    if not isMACAddress(value) :
                        log.warn("Invalid MAC address format : '%s' (hostname='%s')" % (value, hostname))
                        return False
        return True
 

    def get_from_target(self, target) :
        """
        Final getting of valid IP address.

        @param target: container having complete networking info.
        @type target: list

        Target structure :
          (hostname, interfaces)
             interfaces = [iface1, iface2,..., ifacen]
               iface = {"ip":, "mac":, "netmask":, "gateway":,}
        """
        if len(target) == 0 :
            log.error("Bad target format")
            return None

        for resolver in self.resolvers :    

            log.debug("Trying to apply '%s' method ..." % resolver.name)
            result = resolver(target)
            if result :
                log.info("IP address resolved by '%s' method : %s" % (resolver.name, result))
                return result 
            else :
                log.debug("No match, method '%s' ignored, trying the next one..." % resolver.name)
                continue

        return None

