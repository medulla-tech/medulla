# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
from mmc.plugins.base import ComputerI
from mmc.plugins.dyngroup.database import DyngroupDatabase
import logging


class DyngroupComputers(ComputerI):
    # don't know how to do something else than delComputer.
    def __init__(self, conffile=None):
        self.logger = logging.getLogger()
        self.dyngroup = DyngroupDatabase()

    def getComputer(self, ctx, filt=None):
        return {}

    def getMachineMac(self, ctx, filt):  # TODO : need to sort!
        return None

    def getMachineIp(self, ctx, filt):  # TODO : need to sort!
        return None

    def getComputersNetwork(self, ctx, filt):
        return None

    def getComputersList(self, ctx, filt=None):
        return []

    def getRestrictedComputersListLen(self, ctx, filt={}):
        # Mutable dict filt used as default argument to a method or function
        return 0

    def getRestrictedComputersList(
        self, ctx, min=0, max=-1, filt={}, advanced=True, justId=False, toH=False
    ):
        # Mutable dict filt used as default argument to a method or function
        return []

    def getComputerCount(self, ctx, filt=None):
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
