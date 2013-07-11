#!/usr/bin/python 
# -*- coding: utf-8; -*-
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
Common methods called from PXE with response processing.

This module is replacing a part of old LRS imaging server and its set of hooks.
Processing and functionnality of major part of functions is preserved,
only functions using temporary text files to exchange longer strings 
are optimized to direct communication by variables.
"""

import logging

from twisted.internet import reactor, task
from twisted.internet.defer import succeed
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import implements

from pulse2.package_server.config import P2PServerCP as PackageServerConfig
from pulse2.package_server.imaging.pxe.parser import PXEMethodParser, assign
from pulse2.imaging.bootinventory import BootInventory


class InventorySender(object):
    """ POST request to inventory-server """

    implements(IBodyProducer)

    def __init__(self, inventory):
        self.body = inventory
        self.length = len(self.body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)


class PXEImagingApi (PXEMethodParser):
    """ 
    A frame to recognize the method definitions to build.

    Names and argumets of methods will be extracted and validated
    before calling them by PXEMethodParser.

    Rules to recognize instance methods as "RPC-like callables" :

    - decorated with <@assign> decorator having related argument to identify
    - all the arguments of that methods must be declared into 
      ArgumentContainer class as properties (with the same name)
    - don't forget to initialize PXEMethodParser instance.
    """
    api = None

    def set_api(self, api):
        self.api = api

    def __init__(self, config):
        PXEMethodParser.__init__(self)

    # argument of decorator @assign is identifying each method
    # which can be executed.
    # this argument is ord value of first byte of packet

    # ------------------------ computer register ------------------------------

    @assign(0xAD)
    def computerRegister(self, mac, hostname, ip_address, password=None):
        """ 
        Machine inscription by PXE imaging client.

        If the GLPI backend is used, a minimal inventory is sended to glpiproxy
        two seconds before the inscription by imaging backend.

        @param mac: MAC address
        @type mac: str

        @param hostname: hostname of inventoried machine
        @type hostname: str
 
        @param ip_address: machine IP address 
        @type ip_address: str
        
        """

        if PackageServerConfig().imaging_api["glpi_mode"] :

            d = task.deferLater(reactor, 0, self.glpi_register, mac, hostname, ip_address)
            d.addCallback(self._computerRegister, hostname, mac, 2)
            d.addErrback(self._ebRegisterError)

            return d

        else :

            return self._computerRegister(None, hostname, mac)


    def _computerRegister(self, result, hostname, mac, delay=0):
        """
        Machine inscription by imaging backend.

        @param result: used only if called as callback
        @type result: bool

        @param mac: MAC address
        @type mac: str

        @param hostname: hostname of inventoried machine
        @type hostname: str
 
        @param ip_address: machine IP address 
        @type ip_address: str
        """
 
        d = task.deferLater(reactor, delay, self.api.computerRegister, hostname, mac)
        d.addCallback(self._cbRegisterOk)
        d.addErrback(self._ebRegisterError)

        return d


    def _cbRegisterOk (self, result):
        return "OK"
    def _ebRegisterError (self, failure):
        return "KO"


    def glpi_register(self, mac, hostname, ip_address):
        """
        Computer register sending a minimal inventory

        @param mac: MAC address
        @type mac: str

        @param hostname: hostname of inventoried machine
        @type hostname: str
 
        @param ip_address: machine IP address 
        @type ip_address: str
        
        """
        boot_inv = BootInventory()
        boot_inv.macaddr_info = mac
        boot_inv.ipaddr_info = {'ip': ip_address, 'port': 0}

        inventory = boot_inv.dumpOCS(hostname, "root")

        return self.send_inventory(inventory, hostname)

       

    #  ------------------------ process inventory ---------------------------
    @assign(0xAA)
    def injectInventory(self, mac, inventory):
        """
        Minimal inventory received from PXE.

        @param mac: MAC address
        @type mac: str

        @param inventory: inventory from PXE
        @type inventory: str

        @rtype: deferred
        """
        inventory = inventory.replace("Mc", "MAC Address")
        inventory = [i.strip() for i in inventory.split("\n")]
        parsed_inventory = BootInventory(inventory).dump()
        parsed_inventory["macaddr"] = mac

        # 1st step - inject inventory trough imaging (only disk info)
        d = self.api.injectInventory(mac, parsed_inventory)

        # 2nd step - send inventory by HTTP POST to inventory server
        d.addCallback(self._injectedInventoryOk, mac, inventory)
        d.addErrback(self._injectedInventoryError)

        return d

    def _injectedInventoryError(self, failure):
        """ Inject inventory failed """
        logging.getLogger().warn("PXE Proxy: inject inventory failed: %s" % str(failure))

    def _injectedInventoryOk (self, result, mac, inventory):
        """ 
        Result parsing callback after inventory inject.

        If inventory inject trough imaging is successfull,
        following computer info is needed to send our inventory
        to inventory server.

        @param result: inject inventory result
        @type result: list

        @param mac: MAC address
        @type mac: str

        @param inventory: inventory from PXE
        @type inventory: str
        """

        if isinstance(result, list) and len(result) > 0 \
                and isinstance(result[0], str) and result[0] == 'PULSE2_ERR':
            logging.getLogger().error("PXE Proxy: Error code = %d when inject inventory" % (result[1]))
            return None
        else:
            logging.getLogger().debug("PXE Proxy: Hardware inventory injected successfully into imaging")

            # need the hostname and entity to send this inventory
            d = self.api.getComputerByMac(mac)

            d.addCallback(self._injectedInventorySend, mac, inventory)
            d.addErrback(self._injectedInventoryErrorGetComputer)

    def _injectedInventoryErrorGetComputer(self, failure):
        """ An error occured while getting the hostname """

        logging.getLogger().warn("PXE Proxy: inject inventory - get hostname failed: %s" % str(failure))


    def _injectedInventorySend (self, computer, mac, inventory):
        """
        Inventory sending by HTTP POST to inventory server.

        @param computer: ComputerManager container
        @type computer: dist

        @param mac: MAC address
        @type mac: str

        @param inventory: inventory from PXE
        @type inventory: str

        """
        if not isinstance(computer, dict) :
            logging.getLogger().info("PXE Proxy: computer not resolved, inventory sending don't be processed")
            return
         
        inventory = BootInventory(inventory)
        inventory.macaddr_info = mac

        hostname = computer['shortname']
        entity = computer['entity']

        inventory = inventory.dumpOCS(hostname, entity)

        self.send_inventory(inventory, hostname)


    def send_inventory(self, inventory, hostname):
        """
        Sending the inventory on FusionInventory (XML) format.

        @param inventory: inventory to send
        @type inventory: str

        @param hostname: hostname of inventoried machine
        @type hostname: str
        """

        try:

            if PackageServerConfig().imaging_api["inventory_enablessl"]:
                protocol = "https"
            else : 
                protocol = "http"

            url = "%s://%s:%d/" % (protocol,
                                   PackageServerConfig().imaging_api["inventory_host"], 
                                   PackageServerConfig().imaging_api["inventory_port"])

            # POST the inventory to the inventory server
            logging.getLogger().debug("PXE Proxy: inventory will be sent to url: %s" % url)

            agent = Agent(reactor)
            d = agent.request('POST',
                              url,  
                              Headers({
                                'Content-Type': ['application/x-www-form-urlencoded'],
                                'Content-Length': [str(len(inventory))],
                                'User-Agent': ['Pulse2 Imaging server inventory hook']
                              }),
                              InventorySender(inventory),
                             )
            @d.addCallback
            def _cb (result):
                if result :
                    logging.getLogger().info("PXE Proxy: inventory of %s sent successfully" % hostname)
                return result

            return d

        except Exception, e:
            logging.getLogger().warn("PXE Proxy: Inventory send failed: %s" % str(e))
 

    # ----------------------- backup -------------------------------

    @assign(0xEC)
    def computerCreateImageDirectory(self, mac):
        """
        Creating the directory to stock the downloaded backup.

        @param mac: MAC address
        @type mac: str

        @rtype: deferred
        """
        d = self.api.computerCreateImageDirectory(mac)

        @d.addCallback
        def _cb(result):
            logging.getLogger().debug("PXE Proxy: create image directory result: %s" % str(result))
            return result

        @d.addErrback
        def _eb(failure):
            logging.getLogger().warn("PXE Proxy: create image directory failed: %s" % str(failure))
            return failure 
               
        return d

    @assign(0xED)
    def imageDone(self, mac, imageUUID):
        """ 
        Called when backup process is terminated.

        @param mac: MAC address
        @type mac: str

        @param imageUUID: UUID of image
        @typr imageUUID: str

        @rtype: deferred
 
        """
        d = self.api.imageDone(mac, imageUUID)

        @d.addCallback
        def _cb (result):
            if result :
                logging.getLogger().debug("PXE Proxy: Backup process terminated")
                return "ACK"

        @d.addErrback
        def _eb (failure):
            logging.getLogger().warn("PXE Proxy: Backup process failed: %s" % str(failure))
            return "ERROR"

        return d
        
    @assign(0xCD)
    def computerChangeDefaultMenuItem(self):
        """ 
        Menu item change

        @return: ACK to confirm a correct reception, otherwise ERROR
        @rtype: str
        """
        d= self.api.computerChangeDefaultMenuItem()

        @d.addCallback
        def _cb (result):
            return "ACK"

        @d.addErrback
        def _eb (failure):
            return "ERROR"

        return d

    @assign(0x4C)
    def logClientAction(self, mac, level, phase, message):
        """ 
        Imaging client logs sended to mmc.

        This logs will be displayed on imaging log tab of computer.

        @param mac: MAC address
        @type mac: str

        @param level: logging message level
        @type level: int

        @param phase: step of imaging workflow
        @type phase: str
 
        @param message: displayed message
        @type message: str

        @return: ACK to confirm a correct reception, otherwise ERROR
        @rtype: str
        """

        level += 1 # (different offset on imaging client)

        d = self.api.logClientAction(mac, level, phase, repr(message))

        @d.addCallback
        def _cb(result):
            return "ACK"

        @d.addErrback
        def _eb(failure):
            logging.getLogger().warn("PXE Proxy: logging action failed: %s" % str(failure))
            return "ERROR"

        return d

    @assign(0x1B)
    def getComputerUUID(self, mac):
        """
        Returns computer's UUID if exists. Used for backup processing.

        @param mac: MAC address
        @type mac: str

        @return: computer's UUID if exists, otherwise None
        @rtype: str
        """
        d = self.api.getComputerByMac(mac)

        @d.addCallback
        def cb(result):
            if isinstance(result, dict):
                if "uuid" in result :
                    return result["uuid"]
        @d.addErrback
        def _eb(failure):
            logging.getLogger().warn("PXE Proxy: computer's UUID get failed: %s" % str(failure))

        return d
 
    @assign(0x1A)
    def getComputerHostname(self, mac): 
        """
        Returns computer'hostname if exists. 
        Used for menu title and backup processing.

        @param mac: MAC address
        @type mac: str

        @return: computer's hostname if exists, otherwise None
        @rtype: str
        """
        d = self.api.getComputerByMac(mac)

        @d.addCallback
        def _cb(result):
            if isinstance(result, dict):
                if "shortname" in result :
                    return result["shortname"]

        @d.addErrback
        def _eb(failure):
            logging.getLogger().warn("PXE Proxy: computer's hostname get failed: %s" % str(failure))

        return d

    @assign(0x54)
    def imagingServerStatus(self, mac):
        """
        Returns the percentage of remaining size from the part where the images are stored.

        @param mac: MAC address
        @type mac: str

        @return: a percentage, or -1 if it fails
        @rtype: int
        """
        d = self.api.imagingServerStatus(mac)

        @d.addErrback
        def _eb(failure):
            logging.getLogger().warn("PXE Proxy: server status get failed: %s" % str(failure))

        return d
 
