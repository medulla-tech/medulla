#!/usr/bin/python 
# -*- coding: utf-8; -*-
"""
"""
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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
Parsing of packets on custom format, incoming from imaging PXE client.

Each packet starts with 1 byte identifying a method to execute.
Rest of its content is integrating values of arguments, identified 
by normalized prefixes.

Output of this engine is method to execute with arguments.
"""
import inspect
import logging
from functools import wraps

from pulse2.utils import isMACAddress

LOG_ACTION = {0 : ("boot", "booted"), 
              1 : ("menu", "choosen menu entry"),
              2 : ("restoration", "restoration started"),
              3 : ("restoration", "restoration finished"),
              4 : ("backup", "backup started"),
              5 : ("backup", "backup finished"),
              6 : ("postinst", "postinstall started"),
              7 : ("postinst", "postinstall finished"),
              8 : ("error", "critical error"),
              }

class LOG_LEVEL (object):
    """Logging levels for ImagingLog"""
    EMERG = 1
    ALERT = 2
    CRIT = 3
    ERR = 4
    WARNING = 5
    NOTICE = 6
    INFO = 7
    DEBUG = 8

class LOG_STATE (object):
    """Logging states for ImagingLog"""
    BOOT = "boot"
    MENU = "menu"
    RESTO = "restoration"
    BACKUP = "backup"
    POSTINST = "postinst"
    ERROR = "error"
    DELETE = "delete"
    INVENTORY = "inventory"
    IDENTITY = "identity"


def assign(id):
    """
    Decorator to identify a method with first byte of packet.

    @param id: 1st byte identifying a method
    @type id: int

    @return: None when registering, otherwise decorated function
    @rtype: func
    """
    def wrapper(fnc):
        @wraps(fnc)
        def wrapped_fnc(self, *args, **kwargs):

            if self.register_only :
                # registering step called when RPC proxy created
                self.methods[id] = fnc
            else : 
                # already registered, function returned with normal behavior
                return fnc(self, *args, **kwargs)

        # flag to mark a function as RPC-like
        wrapped_fnc.is_proxy_fnc = True
        return wrapped_fnc

    return wrapper


class ArgumentContainer :
    """
    A container with input parser.

    When a packet incoming from PXE is containing related info, 
    (prefixes, markers, etc) an argument is created and accesible 
    as a property.
    If not, related property is None.
    """
    def __init__(self, packet):
        """
        @param packet: raw content of received packet
        @type packet: str
        """
        self.packet = packet

    # ================== PARSED ARGUMENTS ========================= #

    
    # ------- common arguments --------------- #
    MAC_FLAG = "Mc:"
    HOSTNAME_FLAG = "ID"
    IPADDR_FLAG = "IPADDR:"
    @property
    def mac(self):
        """ Common argument for all PXE methods """
        if self.MAC_FLAG in self.packet :
            start = self.packet.index(self.MAC_FLAG) + len(self.MAC_FLAG)

            if len(self.packet[start:]) >= 17 :
                mac = self.packet[start:start+17]
                if isMACAddress(mac) :
                    return mac

        return None

    # ------- computerRegister args ---------- #
    @property 
    def hostname(self):
        """ Argument for new machine registering (computerRegister)"""
        if self.HOSTNAME_FLAG in self.packet :
            packet = self.packet[len(self.HOSTNAME_FLAG)+1:]
            end = packet.index(":")
            return packet[:end]

        return None

    @property
    def ip_address(self):
        """ Special case for GLPI """
        if self.IPADDR_FLAG in self.packet :
            start = self.packet.index(self.IPADDR_FLAG) + len(self.IPADDR_FLAG)
            return self.packet[start:]

        return None


    # ---------- logAction args -------------- #

    @property
    def level(self):
        """ logAction argument """ 
        assert len(self.packet) > 1
        return int(self.packet[1])

    @property
    def phase(self):
        """ logAction argument """ 
        assert len(self.packet) > 1

        phase, message = LOG_ACTION[self.level]

        return phase

    @property
    def message(self):
        """ logAction argument """ 
        phase, message = LOG_ACTION[self.level]

        complement = None
        if self.level == 1 :
            complement = ord(self.packet[2])
        if self.level in [2,3,4,5] :
            if self.packet[2] == "-" :
                complement = self.packet[3:]
                if "\x00" in complement :
                    end = complement.index("\x00")
                    complement = complement[:end]
        if complement :
            return "%s: %s" % (message, complement)
        else :
            return message
    # --------- injectInventory args ----------- #
    @property
    def inventory(self):
        """ injectInventory argument """
         
        body = self.packet[1:]
        return body
    # example of PXE inventory :

    # M:26f,U:3f9b8
    # D:(hd0):CHS(1023,255,63)=16777216
    # P:0,t:83,s:2048,l:15986688
    # P:4,t:82,s:15990784,l:784384
    # S0:Bochs|Bochs|01/01/2007
    # S1:Bochs|Bochs|-|-|C28041465DFC34F864D2B04146CC7947
    # S3:Bochs|1
    # SM:256:9:DIMM 0:7:18756
    # S4:1
    # C:6,3,3,0,4,0,0,0,fd,ab,81,7,47,65,6e,75,69,6e,65,49,6e,74,65,6c
    # F:2593852
    # Mc:52:54:00:BB:00:95

    
    # ------------ imageDone args --------------- #
    @property
    def imageUUID(self):
        """imageDone argument"""
        if self.MAC_FLAG in self.packet :
            end = self.packet.index(self.MAC_FLAG)
            return self.packet[1:end].replace("\x00", "") # TODO

    @property
    def password(self):
        """ Client identification controlled by server"""
        if self.MAC_FLAG in self.packet :
            end = self.packet.index(self.MAC_FLAG)
            return self.packet[2:end].replace("\x00", "") 

    @property
    def num(self):
        """ Menu item number """
        if len(self.packet) > 1 :
            return ord(self.packet[1])
        else :
            return 0

    @property
    def pnum(self):
        """imagingServerStatus argument"""
        # packet format: T;P1000;10 Mc:52:54:00:61:1B:14
        try:
            if ";" in self.packet and self.packet.count(";") == 2:
                idx = self.packet.index(";") + 1
                return ord(self.packet[idx])
        except Exception, e:
            logging.getLogger().warn("An eror occured while parsing pnum argument: %s" % str(e))
            logging.getLogger().debug("Packet content: %s" % self.packet[1:])
            

    @property
    def bnum(self):
        """imagingServerStatus argument"""
        # packet format: T;P1000;10 Mc:52:54:00:61:1B:14
        try:
            if ";" in self.packet and self.packet.count(";") == 2:
                start_slice = self.packet.index(";") + 2
                packet_slice = self.packet[start_slice:]
                end = packet_slice.index(";")
                value = packet_slice[:end]
                try:
                    return int(value)
                except ValueError :
                    return None
        except Exception, e:
            logging.getLogger().warn("An eror occured while parsing pnum argument: %s" % str(e))
            logging.getLogger().debug("Packet content: %s" % self.packet[1:])
 
    @property
    def to(self):
        """imagingServerStatus argument"""
        # packet format: T;P1000;10 Mc:52:54:00:61:1B:14
        try:
            if ";" in self.packet and self.packet.count(";") == 2:
                start_slice = self.packet.index(";") + 2
                packet_slice = self.packet[start_slice:]
                start = packet_slice.index(";") + 1
                end = packet_slice.index(" " + self.MAC_FLAG)
                value = packet_slice[start:end]
                try:
                    return int(value)
                except ValueError :
                    return None
        except Exception, e:
            logging.getLogger().warn("An eror occured while parsing pnum argument: %s" % str(e))
            logging.getLogger().debug("Packet content: %s" % self.packet[1:])
 




class PXEMethodParser :
    """
    Extracting the methods and arguments from packet.

    All methods declared and decorated with @assign decorator
    are registered into methods dictionnary.
    Argument of @assign decorator is identifying a decorated
    method with a value of first byte of incoming packet 
    from PXE imaging client. 
    When a method is resolved, instance of ArgumentContainer
    extract the arguments and returns all as a method object.
    """

    # dictionnary containing all registered methods
    methods = {}

    # flag to indicate if decorated function should be registered
    # if True : method is only registered to methods dictionnary
    # if False : method is executed 
    register_only = False

    def __init__(self):
        self.register()

    def register(self):
        """Registering of decorated methods into methods dictionnary."""
        self.register_only = True
        for name in dir(self):
            fnc = getattr(self, name)
            
            if not callable(fnc) : continue
            if not hasattr(fnc, "is_proxy_fnc"): continue

            if fnc.is_proxy_fnc :
                args, vargs, kwds, defaults = inspect.getargspec(fnc)
                fnc(self,*args)
        self.register_only = False


    def get_method(self, packet):
        """
        Returns a method to execute.

        @param packet: packet recieved from imaging client
        @type packet: str

        @return: method to execute
        @rtype: func
        """
        marker = ord(packet[0])

        if not marker in self.methods :
            raise (KeyError, "Unrecognized method")

        method = self.methods[marker]
        if not (inspect.ismethod(method) or inspect.isfunction(method)):
            raise (TypeError, "Returned object isn't a method")

        arg_container = ArgumentContainer(packet)
        args = []
        for name in self.get_args(method):
            if hasattr(arg_container, name):
                value = getattr(arg_container, name)

                args.append(value)
        
        logging.getLogger().debug("PXE Proxy: executed method: (%s) %s" % (str(hex(marker)), method.__name__ ))
        return method, args

       
 
    def get_args(self, method):
        """
        Extract the names of arguments from method.

        @param method: method to extract
        @type method: func

        @return: list of names of arguments
        @rtype: list
        """
        args, vargs, kwds, defaults = inspect.getargspec(method)

        return [a for a in args if a != 'self']
     


