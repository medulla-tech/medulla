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
from mmc.plugins.base.output import XLSGenerator
from pulse2.managers.location import ComputerLocationManager

import logging

from mmc.plugins.inventory.config import InventoryConfig
from pulse2.database.inventory import Inventory
from mmc.plugins.inventory.computers import InventoryComputers
from mmc.plugins.inventory.provisioning import InventoryProvisioner
from mmc.plugins.inventory.locations import InventoryLocation
from mmc.plugins.inventory.tables_def import PossibleQueries

from pulse2.version import getVersion, getRevision # pyflakes.ignore

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

    # Register the panel to the DashboardManager
    try:
        from mmc.plugins.dashboard.manager import DashboardManager
        from mmc.plugins.inventory.panel import InventoryPanel
        DM = DashboardManager()
        DM.register_panel(InventoryPanel("inventory"))
    except ImportError:
        pass

    return True


class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.locations = Inventory().getUserLocations(s.userid)
        s.locationsid = map(lambda e: e.id, s.locations)
        return s

class RpcProxy(RpcProxyI):
    def getMachineByOwner(self, user):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getMachineByOwner(ctx, user))

    def getUUIDByMachineName(self, name):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getUUIDByMachineName(ctx, name))

    def countLastMachineInventoryPart(self, part, params):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().countLastMachineInventoryPart(ctx, part, params))

    def getLastMachineInventoryPart(self, part, params):
        ctx = self.currentContext
#        uuid = name # TODO : get uuid from name, or something like that...
#        ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid)
        return xmlrpcCleanup(Inventory().getLastMachineInventoryPart(ctx, part, params))

    def getLastMachineInventoryPart2(self, part, params):
        ctx = self.currentContext
#        uuid = name # TODO : get uuid from name, or something like that...
#        ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid)
        return xmlrpcCleanup(Inventory().getLastMachineInventoryPart2(ctx, part, params))

    def getReport(self,uuid,lang):
        xsl= XLSGenerator("/var/tmp/report-"+uuid+".xls",lang)
        xsl.get_summary_sheet(self.getLastMachineInventoryPart2('Summary', {"uuid":uuid}))
        xsl.get_hardware_sheet(self.getLastMachineInventoryPart2("Processors", {"uuid":uuid}),
                                self.getLastMachineInventoryPart2('Controllers', {"uuid":uuid}),
                                self.getLastMachineInventoryPart2('GraphicCards', {"uuid":uuid}),
                                self.getLastMachineInventoryPart2('SoundCards', {"uuid":uuid}))
        xsl.get_network_sheet(self.getLastMachineInventoryPart2('Network', {"uuid":uuid}))
        xsl.get_storage_sheet(self.getLastMachineInventoryPart2('Storage', {"uuid":uuid}))
        # TODO : adapt Inventory().getLastMachineInventoryPart2 to Software part
        #xsl.get_software_sheet(self.getLastMachineInventoryPart2('Software', {"uuid":uuid, "hide_win_updates":True}))
        xsl.save()
        return xmlrpcCleanup(xsl.path)

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

    def getMachineNumberByState(self):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getMachineNumberByState(ctx))

    def getMachineListByState(self, groupName):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getMachineListByState(ctx, groupName))

    def getMachineByHostnameAndMacs(self, hostname, macs):
        ctx = self.currentContext
        return xmlrpcCleanup(Inventory().getMachineByHostnameAndMacs(ctx, hostname, macs))

    def getAllMachinesInventoryColumn(self, part, column, pattern = {}):
        ret = self.getLastMachineInventoryPart(part, pattern)
        # TODO : m.uuid doesn't exists and should do that in just one call
        retour = []
        for machine in ret:
            name = machine[0]
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
    # TODO : ctx is missing....Inventory
    ctx = None
    return Inventory().getMachinesBy(ctx, table, field, value)

def getInventoryHistory(days, only_new, pattern, max, min):
    # Use xmlrpcCleanup to clean the date values
    return xmlrpcCleanup(Inventory().getInventoryHistory(days, only_new, pattern, max, min))

def countInventoryHistory(days, only_new, pattern):
    return Inventory().countInventoryHistory(days, only_new, pattern)

def getTypeOfAttribute(klass, attr):
    return Inventory().getTypeOfAttribute(klass, attr)

def getLicensesCount(vendor, software, version):
    ctx = SecurityContext()
    ctx.userid = "root"

    def replace_splat(param):
        if '*' in param:
            return param.replace('*', '%')
        return param

    def check_param(param):
        if param == '' or param == '*' or param == '%':
            return None
        return replace_splat(param)

    software = check_param(software)
    vendor = check_param(vendor)
    version = check_param(version)
    if software is None:
        software = '%'
    return xmlrpcCleanup(Inventory().getAllSoftwaresImproved(ctx,
                                                     software,
                                                     vendor=vendor,
                                                     version=version,
                                                     count=1))

def getLocationAll(params):
    return InventoryLocation().getLocationAll(params)

def updateEntities(id, name):
    return InventoryLocation().updateEntities(id, name)

def createLocation(name, parent_name):
    return InventoryLocation().createLocation(name, parent_name)

def deleteEntities(id, Label, parentId):
    return InventoryLocation().deleteEntities(id, Label, parentId)

def parse_file_rule(param):
    return InventoryLocation().parse_file_rule(param)

def moveEntityRuleDown(idrule):
    return InventoryLocation().moveEntityRuleDown(idrule)

def moveEntityRuleUp(idrule):
    return InventoryLocation().moveEntityRuleUp(idrule)

def operatorType():
    return InventoryLocation().operatorType()

def operatorTag(MappedObject):
    return InventoryLocation().operatorTag(MappedObject)

def operatorTagAll():
    return InventoryLocation().operatorTagAll()

def addEntityRule(ruleobj):
    return InventoryLocation().addEntityRule(ruleobj)

def deleteEntityRule(idrule):
    return InventoryLocation().deleteEntityRule(idrule)

def setLocationsForUser(username, attrs):
    return InventoryLocation().setLocationsForUser(username, attrs)

def getLocationsForUser(username):
    return InventoryLocation().getLocationsForUser(username)

def delUser(username):
    return InventoryLocation().delUser(username)
