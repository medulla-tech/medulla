
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

from mmc.plugins.base import ComputerI
from mmc.plugins.inventory.config import InventoryConfig
from mmc.plugins.inventory.database import Inventory
import logging
import exceptions

class InventoryComputers(ComputerI):
    def __init__(self, conffile = None):
        self.logger = logging.getLogger()
        self.config = InventoryConfig("inventory")
        self.inventory = Inventory()

    def getComputer(self, ctx, filt = None):
        #try:
            return self.inventory.getMachinesOnly(filt)[0].toDN(True)
        #except:
        #    return False

    def getMachineMac(self, ctx, filt):
        return map(lambda n: n['MACAddress'], self.inventory.getMachineNetwork(filt))

    def getMachineIp(self, ctx, filt):
        return map(lambda n: n['IP'], self.inventory.getMachineNetwork(filt))

    def getComputersList(self, ctx, filt = None):
        return self.getRestrictedComputersList(ctx, 0, -1, filt)

    def getRestrictedComputersListLen(self, ctx, filt = None):
        return len(self.getRestrictedComputersList(ctx, 0, -1, filt))

    def getRestrictedComputersList(self, ctx, min = 0, max = -1, filt = None, advanced = True):
        return map(lambda m: m.toDN(), self.inventory.getMachinesOnly(filt))

    def getComputerCount(self, ctx, filt = None):
        return self.getRestrictedComputersListLen(ctx, filt)

    def canAddComputer(self):
        return True
        
    def addComputer(self, ctx, params):
        name = params["computername"]
        comment = params["computerdescription"].encode("utf-8")
        ip = params['computerip']
        mac = params['computermac']
        return self.inventory.addMachine(name, ip, mac, comment)
    
    def neededParamsAddComputer(self):
        return [
            ['computerip', 'string', 'computer\'s ip address'],
            ['computermac', 'string', 'computer\'s mac address']
        ]

    def canDelComputer(self):
        return True

    def delComputer(self, ctx, uuid):
        return self.inventory.delMachine(uuid)


