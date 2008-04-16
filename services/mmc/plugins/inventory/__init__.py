#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of MMC.
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

# Helpers
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.support.mmctools import Singleton, xmlrpcCleanup
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.pulse2.group import ComputerGroupManager

import logging
import datetime
import time

from mmc.plugins.inventory.config import InventoryExpertModeConfig, InventoryConfig
from mmc.plugins.inventory.database import Inventory
from mmc.plugins.inventory.utilities import unique

VERSION = "2.0.0"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    logger = logging.getLogger()
    config = InventoryConfig("inventory")
    logger.debug("Inventory %s"%str(config.disable))
    if config.disable:
        logger.warning("Plugin inventory: disabled by configuration.")
        return False
                                
    # When this module is used be the MMC agent, the global inventory variable is shared.
    # This means an Inventory instance is not created each time a XML-RPC call is done.
    Inventory().activate()
    if not Inventory().db_check():
        return False
        
    logger.info("Plugin inventory: Inventory database version is %d" % Inventory().dbversion)
    return True
            

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

class RpcProxy(RpcProxyI):
    def getLastMachineInventoryPart(self, part, name, pattern = None):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getLastMachineInventoryPart(part, name, pattern))
    
    def getAllMachinesInventoryColumn(self, part, column, pattern = None):
        ctx = self.currentContext
        ret = self.getAllMachinesInventoryPart(part, pattern)
        retour = []
        for machine in ret:
            name = machine[0]
            invents = []
            for invent in machine[1]:
                invents.append(invent[column])
            retour.append([name, invents])
        return xmlrpcCleanup(retour)
    
    def getMachines(self, pattern = None):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getMachines(pattern))
    
    def inventoryExists(self, name):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().inventoryExists(name))
    
    def getLastMachineInventoryFull(self, name):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getLastMachineInventoryFull(name))
    
    def getAllMachinesInventoryPart(self, part, pattern = None):
        ctx = self.currentContext
        machines = self.getMachines(pattern)
        result = []
        for machine in machines:
            result.append([machine[0], self.getLastMachineInventoryPart(part, machine[0])])
        return result
   
    def getInventoryEM(self, col):
        ctx = self.currentContext
        conf = InventoryExpertModeConfig("inventory", None)
        return conf.expert_mode[col]
    
    def getInventoryGraph(self, col):
        ctx = self.currentContext
        conf = InventoryExpertModeConfig("inventory", None)
        return conf.graph[col]
    
    def getMachinesBy(self, table, field, value):
        ctx = self.currentContext
        return Inventory().getMachinesBy(table, field, value)
    
    def getMachinesByDict(self, table, params):
        ctx = self.currentContext
        return Inventory().getMachinesByDict(table, params)
    
    def getValues(self, table, field):
        ctx = self.currentContext
        return Inventory().getValues(table, field)
    
    def getValuesWhere(self, table, field1, value1, field2):
        ctx = self.currentContext
        return Inventory().getValuesWhere(table, field1, value1, field2)
    

def getValues(table, field):
    return Inventory().getValues(table, field)
def getMachinesBy(table, field, value):
    return Inventory().getMachinesBy(table, field, value)
