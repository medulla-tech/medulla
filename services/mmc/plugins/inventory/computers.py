
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
Inventory implementation of the Computer Interface
Used by the ComputerManager
"""

from mmc.plugins.base import ComputerI
from mmc.plugins.inventory.config import InventoryConfig
from pulse2.database.inventory import Inventory
from pulse2.managers.imaging import ComputerImagingManager
import pulse2.utils
import logging

class InventoryComputers(ComputerI):
    def __init__(self, conffile = None):
        self.logger = logging.getLogger()
        self.config = InventoryConfig()
        self.inventory = Inventory()

    def getComputer(self, ctx, filt = None):
        ret = self.inventory.getMachinesOnly(ctx, filt)

        if type(ret) == list and len(ret) == 1:
            return ret[0].toDN(ctx, True)
        else:
            return {}

    def getMachineMac(self, ctx, filt): # TODO : need to sort!
        """
        @return: dict of computer with their MAC addresses
                 {'UUID1', ['MAC1', 'MAC2'], 'UUID2': ['MAC1']}
        """
        machines = self.inventory.getMachineNetwork(ctx, filt)
        ret = {}
        for m in machines:
            ret[m[2]] = []
            for net in m[1]:
                ret[m[2]].append(net['MACAddress'])
        return ret

    def getMachineIp(self, ctx, filt): # TODO : need to sort!
        machines = self.inventory.getMachineNetwork(ctx, filt)
        ret = []
        for m in machines:
            ret.append(map(lambda i: i['IP'], m[1]))
        if len(ret) == 1:
            return ret[0]
        return ret

    def getMachineHostname(self, ctx, filt = None):
        machines = self.inventory.getMachinesOnly(ctx, filt)
        ret = []
        for m in machines:
            ret.append(m.toH())
        if len(ret) == 1:
            return ret[0]
        return ret

    def getComputersNetwork(self, ctx, filt):
        computers = self.inventory.getMachinesNetworkSorted(ctx, filt)
        ret = []
        for item in computers:
            tmp = [False, {'cn' : [item[0]], 'objectUUID':[item[2]]}]
            if not len(item[1]):
                tmp[1]['ipHostNumber'] = ''
                tmp[1]['macAddress'] = ''
                tmp[1]['subnetMask'] = ''
                tmp[1]['networkUuids'] = ''
            else:
                tmp[1]['ipHostNumber'] = item[1]['IP']
                tmp[1]['macAddress'] = item[1]['MACAddress']
                tmp[1]['subnetMask'] = item[1]['SubnetMask']
                tmp[1]['networkUuids'] = item[1]['networkUuids']
            ret.append(tmp)
        return ret

    def getComputersList(self, ctx, filt = None):
        return self.getRestrictedComputersList(ctx, 0, -1, filt)

    def __restrictLocationsOnImagingServerOrEntity(self, filt, ctx):
        if filt.has_key('imaging_server') and filt['imaging_server'] != '':
            entity_uuid = ComputerImagingManager().getImagingServerEntityUUID(filt['imaging_server'])
            if entity_uuid != None:
                filt['location'] = entity_uuid
            else:
                self.logger.warn("can't get the entity that correspond to the imaging server %s"%(filt['imaging_server']))
                return [False]

        if filt.has_key('entity_uuid') and filt['entity_uuid'] != '':
            grep_entity = None
            for l in ctx.locations:
                if l.uuid == filt['entity_uuid']:
                    grep_entity = l
            if grep_entity != None:
                filt['location'] = [grep_entity]
            else:
                self.logger.warn("the user '%s' try to filter on an entity he shouldn't access '%s'"%(ctx.userid, filt['entity_uuid']))
                return [False]
        return [True, filt]

    def getRestrictedComputersListLen(self, ctx, filt = {}):
        if filt == '':
            filt = {}

        filt = self.__restrictLocationsOnImagingServerOrEntity(filt, ctx)
        if not filt[0]: return 0
        filt = filt[1]

        return self.inventory.countMachinesOnly(ctx, filt)

    def getRestrictedComputersList(self, ctx, min = 0, max = -1, filt = {}, advanced = True, justId = False, toH = False):
        if filt == '':
            filt = {}

        filt = self.__restrictLocationsOnImagingServerOrEntity(filt, ctx)
        if not filt[0]: return {}
        filt = filt[1]

        filt['min'] = min
        filt['max'] = max
        if justId:
            return map(lambda m:m.uuid(), self.inventory.getMachinesOnly(ctx, filt))
        elif toH:
            return map(lambda m:m.toH(), self.inventory.getMachinesOnly(ctx, filt))
        else:
            if filt.has_key('get'):
                return map(lambda m:m.toCustom(filt['get']), self.inventory.getMachinesOnly(ctx, filt))
            else:
                return self.inventory.getComputersOptimized(ctx, filt)

    def getTotalComputerCount(self):
        return self.inventory.getTotalComputerCount()

    def getComputerCount(self, ctx, filt = None):
        return self.getRestrictedComputersListLen(ctx, filt)

    def canAddComputer(self):
        return self.inventory.canAddMachine()

    def canAssociateComputer2Location(self):
        return True

    def addComputer(self, ctx, params):
        name = params["computername"]
        comment = params["computerdescription"].encode("utf-8")
        ip = params['computerip']
        mac = params['computermac']
        net = params['computernet']
        location = None
        if params.has_key('location_uuid'):
            location = params['location_uuid']
        ret = self.inventory.addMachine(name, ip, mac, net, comment, location)
        return ret

    def neededParamsAddComputer(self):
        return [
            ['computerip', 'string', 'Computer\'s IP address'],
            ['computermac', 'string', 'Computer\'s MAC address'],
            ['computernet', 'string', 'Computer\'s netmask address']
        ]

    def checkComputerName(self, name):
        return pulse2.utils.checkComputerName(name)

    def isComputerNameAvailable(self, ctx, locationUUID, name):
        return self.inventory.isComputerNameAvailable(ctx, locationUUID, name)

    def canDelComputer(self):
        return True

    def delComputer(self, ctx, uuid, backup):
        return self.inventory.delMachine(uuid)

    def editComputerName(self, uuid, name):
        """
        Edit the computer name

        @param ctx: the context
        @type: currentContext

        @param uuid: the machine uuid
        @type: str

        @param name: new computer name
        @type: str

        @returns: True if the name changed
        @type: bool

        """
        return self.inventory.editMachineName(uuid, name)

    def getComputerByMac(self, mac):
        ret = self.inventory.getMachinesBy(None, 'Network', 'MACAddress', mac, False)
        if type(ret) == list:
            if len(ret) != 0:
                return ret[0]
            else:
                return None
        return ret

    def getComputersListHeaders(self, ctx):
        """
        Computers list header is just hostname as Computer Name and Description as Description
        """
        return self.config.display


