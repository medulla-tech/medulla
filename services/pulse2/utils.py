# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Some common utility methods used by Pulse 2 components.

Some words about MAC Addresses : Pulse 2 recognizes 4 formats, without
consideration of case.

The following formats can be used :
 - IEEE 802.3 'Unix'        :
    + grouped by two,
    + separator is ":",
    + example 12:34:56:78:90:ab
 - IEEE 802.3 'Microsoft'   :
    + grouped by two,
    + separator is "-",
    + example 12-34-56-78-90-ab
 - EUI-64 'Cisco'           :
    + grouped by four,
    + separator is '.',
    + example 1234.5678.90ab
  - Short                   :
    + no group,
    + no separator,
    + example 1234.5678.90ab
However a Pulse 2 stored MAC Address is always following the IEEE 802.3
'Unix' convention, with capital letters : 12:34:56:78:90:AB

"""
import socket, struct
import fcntl

# to build Pulse2ConfigParser on top of ConfigParser()
from ConfigParser import ConfigParser

# some imports to convert stuff in xmlrpcCleanup()
import datetime
import re
import os
from time import struct_time, gmtime, strftime
import inspect
import posixpath
import psutil
import logging

# python 2.3 fallback for set() in xmlrpcleanup
try:
    set
except NameError:
    from sets import Set as set

try:
    import mx.DateTime as mxDateTime
except ImportError:
    mxDateTime = None # pyflakes.ignore

import uuid

from mmc.site import mmcconfdir

class Singleton(object):
    """
    Duplicate from the Singleton() class from the MMC Project,
    to remove unwanted dependencies
    """

    def __new__(cls, *args):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


class Pulse2ConfigParser(ConfigParser):
    """
        Duplicate from the MMCConfigParser() class from the MMC Project,
        to remove unwanted dependancies
    """

    def __init__(self):
        ConfigParser.__init__(self)

    def getpassword(self, section, option):
        """
        Like get, but interpret the value as a obfuscated password if a
        password scheme is specified.

        For example: passwd = {base64}bWFuL2RyaXZhMjAwOA==
        """
        value = self.get(section, option)
        m = re.search('^{(\w+)}(.+)$', value)
        if m:
            scheme = m.group(1)
            obfuscated = m.group(2)
            ret = obfuscated.decode(scheme)
        else:
            ret = value
        return ret


def xmlrpcCleanup(data):
    """
        Duplicate from mmc.support.mmctools.xmlrpcCleanup()
        to remove unwanted dependancies
    """
    if type(data) == dict:
        ret = {}
        for key in data.keys():
            # array keys must be string
            ret[str(key)] = xmlrpcCleanup(data[key])
    elif type(data) == list:
        ret = []
        for item in data:
            ret.append(xmlrpcCleanup(item))
    elif type(data) == set:
        ret = []
        for item in data:
            ret.append(xmlrpcCleanup(item))
    elif type(data) == datetime.date:
        ret = tuple(data.timetuple())
    elif type(data) == datetime.datetime:
        ret = tuple(data.timetuple())
    elif mxDateTime and type(data) == mxDateTime.DateTimeType:
        ret = data.tuple()
    elif type(data) == struct_time:
        ret = tuple(data)
    elif data == None:
        ret = False
    elif type(data) == tuple:
        ret = map(lambda x: xmlrpcCleanup(x), data)
    elif type(data) == long:
        ret = str(data)
    else:
        ret = data
    return ret


def unique(s):
    """
    Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        u = None # move on to the next method

    if u != None:
        return u.keys()
    del u

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        t = None # move on to the next method

    if t != None:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]
    else:
        del t

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u


def same_network(ip1, ip2, netmask):
    try:
        ip1 = map(lambda x: int(x), ip1.split('.'))
        ip2 = map(lambda x: int(x), ip2.split('.'))
        netmask = map(lambda x: int(x), netmask.split('.'))
        for i in range(4):
            if ip1[i].__and__(netmask[i]) != ip2[i].__and__(netmask[i]):
                return False
    except ValueError:
        return False
    return True


def onlyAddNew(obj, value):
    if type(value) == list:
        for i in value:
            try:
                obj.index(i)
            except:
                obj.append(i)
    else:
        try:
            obj.index(value)
        except:
            obj.append(value)
    return obj


def getConfigFile(module, path = mmcconfdir + "/plugins/"):
    """Return the path of the default config file for a plugin"""
    return os.path.join(path, module) + ".ini"


def isdigit(i):
    if type(i) == int or type(i) == long:
        return True
    if (type(i) == str or type(i) == unicode) and re.search("^\d*$", i):
        return True
    return False


def grep(string, list):
    expr = re.compile(string)
    return filter(expr.search, list)


def grepv(string, list):
    expr = re.compile(string)
    return [item for item in list if not expr.search(item)]


def extractExceptionMessage(exception):
    message = ''
    if hasattr(exception, "value"):
        message = exception.value
    elif hasattr(exception, "__repr__"):
        message = repr(exception)
    elif hasattr(exception, "__str__"):
        message = str(exception)
    else:
        message = "unknown exception encountered"
    return message


def whoami():
    return inspect.stack()[1][3]


def whosdaddy():
    return inspect.stack()[2][3]


def printStack():
    stack = inspect.stack()
    a_stack = []
    for i in range(1, len(stack)-1):
        a_stack.append(stack[i][3])
    a_stack.reverse()
    return " > ".join(a_stack)


def isCiscoMacAddress(mac_addr):
    """
    Check that the given MAC adress is a cisco-formatted MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """
    if type(mac_addr) not in [str, unicode]:
        return False
    regex = '^([0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})$'
    return re.match(regex, mac_addr) != None


def isLinuxMacAddress(mac_addr):
    """
    Check that the given MAC adress is a linux-formatted MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """
    if type(mac_addr) not in [str, unicode]:
        return False
    regex = '^([0-9a-fA-F][0-9a-fA-F]:){5}([0-9a-fA-F][0-9a-fA-F])$'
    return re.match(regex, mac_addr) != None


def isWinMacAddress(mac_addr):
    """
    Check that the given MAC adress is a windows-formatted MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """
    if type(mac_addr) not in [str, unicode]:
        return False
    regex = '^([0-9a-fA-F][0-9a-fA-F]-){5}([0-9a-fA-F][0-9a-fA-F])$'
    return re.match(regex, mac_addr) != None


def isShortMacAddress(mac_addr):
    """
    Check that the given MAC adress is a short-formatted MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """
    if type(mac_addr) not in [str, unicode]:
        return False
    regex = '^(([0-9a-fA-F]){12})$'
    return re.match(regex, mac_addr) != None


def isMACAddress(mac_addr):
    """
    Check that the given MAC adress seems to be a MAC Address.

    @type mac_addr: str
    @param mac_addr: the mac addr to check
    @returns: returns True if the given MAC address is valid
    @rtype: bool
    """
    return isCiscoMacAddress(mac_addr) or isLinuxMacAddress(mac_addr) or isWinMacAddress(mac_addr) or isShortMacAddress(mac_addr)


def reduceMACAddress(mac):
    """
    @return: the MAC address in upper case without ':'
    """
    assert isMACAddress(mac)
    ret = mac.upper()
    ret = ret.replace(':', '')
    ret = ret.replace('-', '')
    ret = ret.replace('.', '')
    return ret


def normalizeMACAddress(mac):
    """
    @return: the MAC address normalized (see this module documentation)
    """
    assert isMACAddress(mac)
    return ':'.join(map(lambda (x, y): x + y, zip(reduceMACAddress(mac)[0:11:2], reduceMACAddress(mac)[1:12:2]))) # any questions ?


def macToNode(mac):
    """
    @return: the MAC address in the form of a 48-bits integer
    """
    assert isMACAddress(mac)
    try:
        return int(reduceMACAddress(mac), 16)
    except:
        return 0


def isUUID(value):
    """
    Check input validity for:
     - standard UUID like: 35f23420-4050-4734-b172-d458915ef17d
     - Pulse 2 fake UUID style: UUID<positive-int>

    @return: True if the parameter is a valid UUID
    @rtype: bool
    """
    if type(value) in [str, unicode] and value.startswith('UUID'):
        try:
            value = int(value[4:])
            ret = value > 0
        except ValueError:
            ret = False
    else:
        try:
            uuid.UUID(value)
            ret = True
        except (ValueError, AttributeError):
            ret = False
    return ret


def checkEntityName(entity_name):
    """
    @param: entity name
    @raise: TypeError: if the entity name is not valid
    @return: True
    """
    if entity_name and not re.match('^[a-zA-Z0-9]{3,64}$', entity_name):
        raise TypeError('Bad entity name: %s' % entity_name)

    return True

def splitComputerPath(path):
    """
    Split the computer path according to this scheme:
     profile:/entity1/entity2/computerName

    @raise TypeError: if the computer path is not valid
    @returns: returns a tuple with (profile, entities, hostname, domain)
    @rtype: tuple
    """
    # Get profile
    m = re.match("^([a-zA-Z0-9-]*):(.*)$", path)
    if m:
        profile = m.group(1)
        tail = m.group(2)
    else:
        profile = ''
        tail = path

    # Split entity path and computer FQDN
    entities, fqdn = posixpath.split(tail)

    if entities and entities != '/':
        if not entities.startswith('/'):
            raise TypeError
        # Check entities
        for entity in entities.split('/'):
            checkEntityName(entity)
    else:
        entities = ''

    if '.' in fqdn:
        hostname, domain = fqdn.split('.', 1)
    else:
        hostname = fqdn
        domain = ''

    if domain and not re.match('^([a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]\.){0,10}[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]$', domain):
        raise TypeError('Bad domain: %s' % domain)

    if not re.match('^([a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9])$', hostname):
        raise TypeError('Bad hostname: %s' % hostname)


    return (profile, entities, hostname, domain)


def checkComputerName(name):
    """
    Check computer name for Pulse 2.
    It internally uses the splitComputerPath method.

    @param name: computer name to check
    @type name: str

    @returns: whether the computer name is valid or not
    @rtype: bool
    """
    ret = True
    try:
        if ':' in name or '/' in name:
            raise TypeError
        splitComputerPath(name)
    except TypeError:
        ret = False
    return ret


def rfc3339Time(ref = False):
    """
    Return a RFC 3339 string representing the time @ref
    """
    if not ref:
        ref = gmtime()
    return strftime('%Y-%m-%dT%H:%M:%SZ', ref)


def humanReadable(num, unit = "B", base = 1024):
    """
    port of my famous "human readable" formating function
    """

    assert type(num) in [float, int, long]
    assert type(unit) in [str]
    assert type(base) in [int]

    units = ["Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi"]

    ret = "%s" % num
    num = float(num)

    if num < base:
        ret = "%.0f %s" % (num, unit)
    else:
        for i in units:
            num /= base
            if num < base:
                ret = "%.1f %s%s" % (num, i, unit)
                break
    return ret

###
### Network interfaces related tools
###
def get_ip_address(ifname):
    """ TODO: IPv6
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname)
    )[20:24])

def get_default_netif():
    """ Read the default interface directly from /proc.
    """
    netif = None

    fh = open("/proc/net/route")
    try:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            netif = fields[0][:15]
            fh.close()
            break
    finally:
        fh.close()

    # 2nd possibility ->
    if not netif :
        cmd = "netstat -i"
        ps = os.popen(cmd, "r")
        out = ps.read()
        ps.close()

        # output on format :
        # Iface   MTU Met   RX-OK RX-ERR RX-DRP RX-OVR    TX-OK TX-ERR TX-DRP  TX-OVR Flg
        # eth0       1500 0     15985      0      0 0         13285      0      0       0 BMRU
        # lo        16436 0         0      0      0 0             0      0      0       0 LRU
        # so, we take 1st iface (16th element) to get our default interface

        netif = out.split()[15].strip()
 
    return netif



def get_default_ip():
    """ Return the IP of first netif with a default gateway
    """
    netif = get_default_netif()
    return get_ip_address(netif)


class HasSufficientMemory :
    """
    Can be used as a decorator to avoid executing the functions with high costs. 

    When usage of memory is less than mem_limit, this decorator returns 
    decorated function, otherwise neg_ret_value.

    Examples:
    --------- 
    @HasSufficientMemory(80)
    def called_function(arg1, arg2, ..)
        ...
        return True

    @HasSufficientMemory(60, "NOK")
    def called_function(arg1, arg2, ..)
        ...
        return "OK"
    """

    def __init__(self, mem_limit, neg_ret_value=False):
        """
        @param mem_limit: limit (in percent) of memory usage
        @type mem_limit: int

        @param neg_ret_value: returned value when memory usage is exceeded
        @type neg_ret_value: object
        """

        self.mem_limit = mem_limit
        self.neg_ret_value = neg_ret_value

    def __call__(self, fnc, *args):
        """
        @param fnc: decorated function
        @type fnc: function type

        @returns: decorated function or neg_ret_value
        """

        def wrapped (*args) :
            if psutil.virtual_memory().percent < self.mem_limit :
                 return fnc(*args)
            else :
                 logging.getLogger().warn("Not enough memory to run '%s'" % fnc.__name__)
                 return self.neg_ret_value

        return wrapped

