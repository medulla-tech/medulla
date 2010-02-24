
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: computers.py 37 2008-04-15 13:21:32Z oroussy $
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
        machines = self.inventory.getMachineNetwork(ctx, filt)
        ret = []
        for m in machines:
            ret.append(map(lambda i: i['MACAddress'], m[1]))
        if len(ret) == 1:
            return ret[0]
        return ret

    def getMachineIp(self, ctx, filt): # TODO : need to sort!
        machines = self.inventory.getMachineNetwork(ctx, filt)
        ret = []
        for m in machines:
            ret.append(map(lambda i: i['IP'], m[1]))
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
            else:
                tmp[1]['ipHostNumber'] = item[1]['IP']
                tmp[1]['macAddress'] = item[1]['MACAddress']
                tmp[1]['subnetMask'] = item[1]['SubnetMask']
            ret.append(tmp)
        return ret

    def getComputersList(self, ctx, filt = None):
        return self.getRestrictedComputersList(ctx, 0, -1, filt)

    def getRestrictedComputersListLen(self, ctx, filt = {}):
        if filt == '':
            filt = {}
        return self.inventory.countMachinesOnly(ctx, filt)

    def getRestrictedComputersList(self, ctx, min = 0, max = -1, filt = {}, advanced = True, justId = False, toH = False):
        if filt == '':
            filt = {}
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

    def getComputerCount(self, ctx, filt = None):
        return self.getRestrictedComputersListLen(ctx, filt)

    def canAddComputer(self):
        return True

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
            ['computerip', 'string', 'computer\'s ip address'],
            ['computermac', 'string', 'computer\'s mac address'],
            ['computernet', 'string', 'computer\'s network adress']
        ]

    def canDelComputer(self):
        return True

    def delComputer(self, ctx, uuid):
        return self.inventory.delMachine(uuid)

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


