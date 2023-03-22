# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

""" Network utils module """

import socket
import struct
import fcntl
import logging
import inspect
import os
import subprocess

from pulse2.utils import isdigit, get_default_ip, get_default_netif

log = logging.getLogger()

# All possibles values of subnet mask
# (To get a bit value, use index of them)
SUBNET_BITS = (0, 128, 192, 224, 240, 248, 252, 254, 255)

class NetUtils :
    """ Common network utils """

    @classmethod
    def get_netmask(cls):
        """
        Getting the server's netmask

        @return: netmask
        @rtype: str
        """
        SIOCGIFNETMASK = 0x891b

        iface = get_default_netif()

        n_sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        netmask = fcntl.ioctl(n_sck, SIOCGIFNETMASK, struct.pack('256s', iface))[20:24]

        return socket.inet_ntoa(netmask)

    @classmethod
    def on_same_network(cls, ip, network, netmask):
        """
        Test if IP address can be found in network.

        @param ip: tested IP adddress
        @type ip: string

        @param network: address of network
        @type network: string

        @param netmask: netmask of network
        @type netmask: string

        @return: True if IP address are in the same network.
        @rtype: bool
        """
        if not cls.check_netmask(network, netmask):
            log.warn("network %s is not matching to netmask %s !" % (network, netmask))

        ip_num = struct.unpack('>L',socket.inet_aton(ip))[0]

        cidr = cls.netmask_to_cidr(netmask)
        netmask_of_network = struct.unpack('>L',socket.inet_aton(network))[0]

        masked = ip_num & (4294967295<<(32-int(cidr)))

        return masked == netmask_of_network

    @classmethod
    def check_netmask(cls, network, netmask):
        """
        Test if defined netmask of network is correct.

        @param network: address of network
        @type network: string

        @param netmask: netmask of network
        @type netmask: string

        @return: True if IP address are in the same network.
        @rtype: bool
        """

        cidr = cls.netmask_to_cidr(netmask)
        netmask_of_network = struct.unpack('>L',socket.inet_aton(network))[0]

        return netmask_of_network == netmask_of_network & (4294967295<<(32-int(cidr)))


    @classmethod
    def netmask_to_cidr(cls, netmask):
        """
        Converting decimal dotted subnet mask to CIDR format

        i.e.: 255.255.255.0 -> 24

        @param netmask: netmask on dotted decimal format
        @type netmask: str

        @return: number of bits (CIDR)
        @rtype: int
        """
        dec_bytes = [int(n) for n in netmask.split(".")]

        count = 0
        for byte in dec_bytes :
            while byte != 0:
                if byte % 2 == 1:
                    count += 1
                byte = byte / 2

        return count


    @classmethod
    def has_enough_info(cls, iface):
        """
        Test if interface has enough informations for resolving methods.

        @param iface: networking parameters of interface
        @type iface: dict

        @return: True if enough info
        @rtype: bool
        """
        key = "ip"

        if key not in iface :
            return False
        if not iface[key] or len(iface[key].strip()) == 0 :
            return False
        return True

    @classmethod
    def is_ipv4_format(cls, candidate):
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

    @classmethod
    def netmask_validate(cls, netmask):
        """
        Check of netmask format

        @param netmask: checked netmask
        @type netmask: str

        @return: True if netmask is valid
        @rtype: bool
        """
        if not NetUtils.is_ipv4_format(netmask) :
            return False
        for element in netmask.split("."):
            if not isdigit(element):
                return False
            if int(element) not in SUBNET_BITS :
                return False
        return True

    @classmethod
    def ipv4_to_dec(cls, address):
        """
        Converts a IPv4 address string to list of integers.

        i.e. '192.168.12.206' --> [192, 168, 12, 206]

        @param address: address to extract
        @type address: string

        @return: ip address in list of integers
        @rtype: list
        """
        return [int(a) for a in address.split(".")]

    @classmethod
    def is_port_free(cls, port, host="127.0.0.1"):
        """
        Check if port on host is free.

        @param port: checked port
        @type port: int

        @param host: checked host
        @type host: str

        @return: True if port is free
        @rtype: bool
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            s.shutdown(2)
            s.close()
            return False
        except :
            return True


class NetworkDetect :
    """ Detecting of the network/broadcast addresses """

    def __init__(self, ip, netmask):
        """
        @param ip: IP address of any computer on checked network
        @type ip: str

        @param netmask: netmask of checked network
        @type netmask: str
        """

        if NetUtils.is_ipv4_format(ip) :
            self.ip = ip
        else :
            raise Exception("Invalid format of IP address")

        if NetUtils.netmask_validate(netmask) :
            self.netmask = netmask
        else :
            raise Exception("Invalid format of netmask")

        self.subnets = self.get_subnets(netmask)

    @classmethod
    def get_subnets(cls, netmask):
        """
        For each bit returns number of subnets and number of elements.

        @param netmask: netmask to extract
        @type netmask: str

        @return: number of subnets and last bit value for each bit
        @rtype: list
        """

        TOTAL_BITS = 8

        for element in NetUtils.ipv4_to_dec(netmask) :

            n_bits = SUBNET_BITS.index(element)
            m_bits = TOTAL_BITS - n_bits

            nbr_subnets = 2 ** m_bits
            last_bit_value = 2 ** n_bits

            yield (nbr_subnets, last_bit_value)


    @classmethod
    def get_valid_range(cls, nbr, last_bit, value):
        """
        Get the valid range according to checked value

        @param nbr: number of subnets
        @type nbr: int

        @param last_bit: value of last bit of subnet
        @type last_bit: int

        @param value: checked value
        @type value: int

        @return: valid range to get network/broadcast addresses
        @rtype: tuple
        """

        if nbr == 256 :
            return (0, 255)

        start = 0
        end = 0

        for attempt in range(0, nbr) :

            end = attempt * last_bit - 1

            if value in range(start, end) :
                return (start, end)
            start = attempt * last_bit

        return (value, value)


    def get_ranges(self):
        """
        Apply the netmask rules on checked IP address.
        @return: range of all possibles IP adresses on format:
                 (min, max), (min, max), (min, max), (min, max)
        @rtype: generator
        """
        ip_dec = NetUtils.ipv4_to_dec(self.ip)
        ip_mask =  NetUtils.ipv4_to_dec(self.netmask)
        for i in range(len(ip_dec)):
            val=ip_dec[i]&ip_mask[i]
            yield val

    @property
    def network(self):
        """
        @return: calculated IPv4 network address
        @rtype: str
        """
        decimals = [ str(r) for r in self.get_ranges() ]
        return ".".join(decimals)

    @property
    def broadcast(self):
        """
        @return: calculated IPv4 broadcast address
        @rtype: str
        """
        decimals = [ str(r) for r in self.get_ranges() ]
        return ".".join(decimals)


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
        hostname, fqdn, ifaces = target
        last_ip = last_netmask = None

        for iface in ifaces :
            if NetUtils.has_enough_info(iface) :
                iface_ip = iface["ip"]
                if not NetUtils.is_ipv4_format(iface_ip):
                    log.debug("Interface %s not matching to IPv4 format, skiping" % iface_ip)
                    continue
                for pref_ip, pref_netmask in self.networks :

                    log.debug("Comparing host '%s'(%s) with my preferred network (%s/%s)" %
                            (hostname, iface_ip, pref_ip, pref_netmask))

                    if NetUtils.on_same_network(iface_ip, pref_ip, pref_netmask) :

                        return iface_ip

                    last_ip = pref_ip
                    last_netmask = pref_netmask

        if not last_ip and not last_netmask :
            log.debug("Not enough info to check host='%s'" % hostname)
        else :
            log.debug("No match host='%s'with preferred network(%s/%s)" %
                     (hostname, last_ip, last_netmask))


        return None


class ChoosePerShortname (ResolvingCallable):

    name = "shortname"

    hosts_path = "/usr/bin/getent"

    def validate(self):
        if not os.path.exists(self.hosts_path):
            log.warn("Command '%s' not found, omitting '%s' method." % (self.hosts_path, self.name))
            return False
        else :
            return True


    def __call__(self, target):
        """
        Request to "hosts" database using the shortname as key.

        @param target: container having complete networking info.
        @type target: list

        @return: IP address of reachable interface
        @rtype: string

        """
        hostname, fqdn, ifaces = target

        cmd = "%s hosts %s" % (self.hosts_path, hostname)

        out = self.run_command(cmd)
        # <example of a positive response> :
        # 192.168.127.3   <hostname>
        # if negative, response empty
        if out :
            if len(out.split()) > 1 :
                ip = out.split()[0] # 1st place is ip
                if NetUtils.is_ipv4_format(ip) :
                    return ip

        return None

class ChoosePerFQDN (ResolvingCallable):

    name = "fqdn"

    hosts_path = "/usr/bin/getent"

    def validate(self):
        if not os.path.exists(self.hosts_path):
            log.warn("Command '%s' not found, omitting '%s' method." % (self.hosts_path, self.name))
            return False
        else :
            return True


    def __call__(self, target):
        """
        Request to "hosts" database using the fqdn as key.

        @param target: container having complete networking info.
        @type target: list

        @return: IP address of reachable interface
        @rtype: string

        """
        hostname, fqdn, ifaces = target

        cmd = "%s hosts %s" % (self.hosts_path, fqdn)

        out = self.run_command(cmd)
        # <example of a positive response> :
        # 192.168.127.3   <hostname>
        # if negative, response empty
        if out :
            if len(out.split()) > 1 :
                ip = out.split()[0] # 1st place is ip
                if NetUtils.is_ipv4_format(ip) :
                    return ip

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
        hostname, fqdn, ifaces = target
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
        hostname, fqdn, ifaces = target

        cmd = "%s '%s'" % (self.netbios_path, hostname)

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

                if NetUtils.is_ipv4_format(ip) :
                    return ip

        return None


class IPResolversContainer :
    """
    Registering of all resolvers to get a correct network interface
    of a client machine.
    """
    resolvers = []
    networks = []

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
        self.resolvers = []
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
        if not (isinstance(target, tuple) or isinstance(target, list)):
            log.warn("Invalid target format: Tuple or list required, not %s" % type(target))
            return False

        if len(target) != 3 :
            log.warn("Invalid target format: Invalid length.")
            return False

        hostname, fqdn, ifaces = target

        if not isinstance(ifaces, list) :
            log.warn("Invalid target format: List required, not %s" % type(ifaces))
            return False

        for iface in ifaces :
            for key, value in iface.items():
                if not isinstance(value, str) :
                    log.warn("Invalid interface format, section '%s' (hostname='%s')" % (key, hostname))
                    return False
        return True


    def get_from_target(self, target) :
        """
        Final getting of valid IP address.

        @param target: container having complete networking info.
        @type target: list

        Target structure :
          (hostname, fqdn, interfaces)
             interfaces = [iface1, iface2,..., ifacen]
               iface = {"ip":, "mac":, "netmask":, "gateway":,}
        """
        if not self._validate_target(target):
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

class PreferredNetworkParser :

    def __init__(self, default_ip, default_netmask):
        if not default_ip :
            default_ip = get_default_ip()
        if not default_netmask :
            default_netmask = NetUtils.get_netmask()

        net_detect = NetworkDetect(default_ip, default_netmask)
        network_address = net_detect.network
        self.default_network = [(network_address, default_netmask)]

    def get_default(self):
        return self.default_network

    @classmethod
    def check_str_format(cls, value):
        networks = value.split()
        for ip_slash_mask in networks :
            if not "/" in ip_slash_mask :
                return False
            elif len(ip_slash_mask.split("/")) != 2 :
                return False
        return True

    def parse(self, value):
        if not self.check_str_format(value) :
            log.warning("Preferred network not set, using default value: %s/%s" % self.default_network[0])
            return self.default_network
        else :
            network = []
            for ip_slash_mask in value.split() :
                ip, mask = ip_slash_mask.split("/")
                net_detect = NetworkDetect(ip, mask)
                if ip != net_detect.network :
                    log.warn("Incorrect network address '%s' for netmask '%s', correcting to: '%s'" %
                            (ip, mask, net_detect.network))
                    network.append((net_detect.network, mask))
                else :
                    network.append((ip, mask))
            return network
