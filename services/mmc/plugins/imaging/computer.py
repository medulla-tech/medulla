# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Imaging implementation of the Computer Interface
Used by the ComputerManager
It's only used for the computer deletion
"""


from mmc.plugins.base import ComputerI
from mmc.plugins.imaging.functions import computersUnregister
import pulse2.utils
import logging

class InventoryComputers(ComputerI):
    def __init__(self, conffile = None):
        self.logger = logging.getLogger()

    def canDelComputer(self):
        return True

    def checkComputerName(self, name):
        return pulse2.utils.checkComputerName(name)

    def delComputer(self, ctx, uuid, backup):
        return computersUnregister([uuid], backup)
