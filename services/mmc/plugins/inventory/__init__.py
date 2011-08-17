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


"""
Pulse 2 MMC agent inventory plugin
"""

# Helpers
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.support.mmctools import xmlrpcCleanup
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.base.provisioning import ProvisioningManager
from pulse2.managers.location import ComputerLocationManager

import logging

from mmc.plugins.inventory.config import InventoryConfig
from pulse2.database.inventory import Inventory
from mmc.plugins.inventory.computers import InventoryComputers
from mmc.plugins.inventory.provisioning import InventoryProvisioner
from mmc.plugins.inventory.locations import InventoryLocation
from mmc.plugins.inventory.tables_def import PossibleQueries

from pulse2.version import getVersion, getRevision

APIVERSION = "0:0:0"

def getApiVersion(): return APIVERSION

def activate():
    logger = logging.getLogger()
    config = InventoryConfig()
    config.init("inventory")
    logger.debug("Inventory %s"%str(config.disable))
    if config.disable:
        logger.warning("Plugin inventory: disabled by configuration.")
        return False

    # When this module is used by the MMC agent, the global inventory variable is shared.
    # This means an Inventory instance is not created each time a XML-RPC call is done.
    if not InventoryLocation().init(config): # does Inventory().activate() (which does the Inventory().db_check())
        return False

    logger.info("Plugin inventory: Inventory database version is %d" % Inventory().dbversion)

    ComputerManager().register("inventory", InventoryComputers)
    ProvisioningManager().register('inventory', InventoryProvisioner)
    ComputerLocationManager().register('inventory', InventoryLocation)

    PossibleQueries().init(config)
    return True


class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.locations = Inventory().getUserLocations(s.userid)
        s.locationsid = map(lambda e: e.id, s.locations)
        return s

class RpcProxy(RpcProxyI):
    def countLastMachineInventoryPart(self, part, params):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().countLastMachineInventoryPart(ctx, part, params))

    def getLastMachineInventoryPart(self, part, params):
        ctx = self.currentContext
#        uuid = name # TODO : get uuid from name, or something like that...
#        ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid)
        return xmlrpcCleanup(Inventory().getLastMachineInventoryPart(ctx, part, params))

    def getLastMachineInventoryFull(self, params):
        ctx = self.currentContext
#        if not ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
#            return False
        return xmlrpcCleanup(Inventory().getLastMachineInventoryFull(ctx, params))

    def getMachineInventoryFull(self, params):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getComputerInventoryFull(ctx, params))

    def getMachineInventoryHistory(self, params):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getComputerInventoryHistory(ctx, params))

    def countMachineInventoryHistory(self, params):
        ctx = self.currentContext
        return Inventory().countComputerInventoryHistory(ctx, params)

    def getMachineInventoryDiff(self, params):
        ctx = self.currentContext
        # Use xmlrpcCleanup to clean all None values
        return xmlrpcCleanup(Inventory().getComputerInventoryDiff(ctx, params))

    def getAllMachinesInventoryColumn(self, part, column, pattern = {}):
        ctx = self.currentContext
        ret = self.getLastMachineInventoryPart(part, pattern)
        # TODO : m.uuid doesn't exists and should do that in just one call
        retour = []
        for machine in ret:
            name = machine[0]
            uuid = machine[2]
#            if not ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
#                continue
            invents = []
            for invent in machine[1]:
                invents.append(invent[column])
            retour.append([name, invents])
        return xmlrpcCleanup(retour)

    #############
    def getMachines(self, pattern = None):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getMachines(ctx, pattern))

    def inventoryExists(self, uuid):
        ctx = self.currentContext
        if uuid == '':
            return False
#        if not ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
#            return False
        return xmlrpcCleanup(Inventory().inventoryExists(ctx, uuid))

    def getInventoryEM(self, col):
        conf = InventoryConfig()
        return conf.expert_mode[col]

    def getInventoryGraph(self, col):
        conf = InventoryConfig()
        return conf.graph[col]

    def getMachinesBy(self, table, field, value):
        ctx = self.currentContext
        return xmlrpcCleanup(map(lambda m: ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, m[0]), Inventory().getMachinesBy(ctx, table, field, value)))

    def getMachinesByDict(self, table, params):
        ctx = self.currentContext
        return xmlrpcCleanup(map(lambda m: ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, m[0]), Inventory().getMachinesByDict(ctx, table, params)))

    def getValues(self, table, field):
        return Inventory().getValues(table, field)

    def getValuesWhere(self, table, field1, value1, field2):
        return Inventory().getValuesWhere(table, field1, value1, field2)

    def getValueFuzzyWhere(self, table, field1, value1, field2, fuzzy_value):
        return Inventory().getValueFuzzyWhere(table, field1, value1, field2, fuzzy_value)

    def getValuesFuzzy(self, table, field, fuzzy_value):
        return Inventory().getValuesFuzzy(table, field, fuzzy_value)


def getValues(table, field):
    return Inventory().getValues(table, field)

def getValuesWhere(table, field1, value1, field2):
    return Inventory().getValuesWhere(table, field1, value1, field2)

def getValuesFuzzy(table, field, fuzzy_value):
    return Inventory().getValuesFuzzy(table, field, fuzzy_value)

def getValueFuzzyWhere(table, field1, value1, field2, fuzzy_value):
    return Inventory().getValueFuzzyWhere(table, field1, value1, field2, fuzzy_value)

def getMachinesBy(table, field, value):
    # TODO : ctx is missing....
    ctx = None
    return Inventory().getMachinesBy(ctx, table, field, value)

def getInventoryHistory(days, only_new, pattern, max, min):
    # Use xmlrpcCleanup to clean the date values
    return xmlrpcCleanup(Inventory().getInventoryHistory(days, only_new, pattern, max, min))

def countInventoryHistory(days, only_new, pattern):
    return Inventory().countInventoryHistory(days, only_new, pattern)

def getTypeOfAttribute(klass, attr):
    return Inventory().getTypeOfAttribute(klass, attr)

