#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
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
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import logging

from twisted.internet import utils, reactor
from pulse2.proxyssl.utilities import Singleton

class RunInventory(Singleton):

    """
    Little helper class that runs the inventory agent
    """

    def setup(self, config):
        self.config = config
        self.logger = logging.getLogger()
        from pulse2.proxyssl.http_inventory_proxy import HttpInventoryProxySingleton
        self.singleton = HttpInventoryProxySingleton()

    def maybeStartLoop(self):
        if self.config.polling:
            self.logger.debug("Scheduling inventory in %s seconds" % self.config.polling_time)
            reactor.callLater(self.config.polling_time, self.run)

    def run(self):
        """
        Start an OCS inventory, and loop according to the configuration
        """
        if self.singleton.check_flag():
            self.logger.debug("Starting an inventory")
            d = utils.getProcessOutputAndValue(self.config.command_name, self.config.command_attr)
            d.addCallbacks(self.onSuccess, self.onError)
        else:
            self.logger.debug("Flag not set, not starting an inventory")
        self.maybeStartLoop()

    def onSuccess(self, result):
        self.logger.debug("Inventory done")

    def onError(self, reason):
        self.logger.error("Error while doing inventory: %s" % str(reason))
