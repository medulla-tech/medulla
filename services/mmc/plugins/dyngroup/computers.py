# (c) 2008 Mandriva, http://www.mandriva.com/
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
from mmc.plugins.dyngroup.database import DyngroupDatabase
import logging

class DyngroupComputers(ComputerI):
    # don't know how to do something else than delComputer.
    def __init__(self, conffile = None):
        self.logger = logging.getLogger()
        self.dyngroup = DyngroupDatabase()

    def getComputer(self, ctx, filt = None):
        return {}

    def getMachineMac(self, ctx, filt): # TODO : need to sort!
        return None

    def getMachineIp(self, ctx, filt): # TODO : need to sort!
        return None

    def getComputersNetwork(self, ctx, filt):
        return None

    def getComputersList(self, ctx, filt = None):
        return []

    def getRestrictedComputersListLen(self, ctx, filt = {}):
        return 0

    def getRestrictedComputersList(self, ctx, min = 0, max = -1, filt = {}, advanced = True, justId = False, toH = False):
        return []

    def getComputerCount(self, ctx, filt = None):
        return 0

    def canAddComputer(self):
        return False

    def canAssociateComputer2Location(self):
        return False
        
    def addComputer(self, ctx, params):
        return -1
    
    def neededParamsAddComputer(self):
        return []

    def canDelComputer(self):
        return True

    def delComputer(self, ctx, uuid, backup):
        return self.dyngroup.delMachine(uuid)

    def getComputersListHeaders(self, ctx):
        return []


