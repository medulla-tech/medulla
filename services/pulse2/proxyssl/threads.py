#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
            self.logger.debug(
                "Scheduling inventory in %s seconds" % self.config.polling_time
            )
            reactor.callLater(self.config.polling_time, self.run)

    def run(self):
        """
        Start an OCS inventory, and loop according to the configuration
        """
        if self.singleton.check_flag():
            self.logger.debug("Starting an inventory")
            d = utils.getProcessOutputAndValue(
                self.config.command_name, self.config.command_attr
            )
            d.addCallbacks(self.onSuccess, self.onError)
        else:
            self.logger.debug("Flag not set, not starting an inventory")
        self.maybeStartLoop()

    def onSuccess(self, result):
        self.logger.debug("Inventory done")

    def onError(self, reason):
        self.logger.error("Error while doing inventory: %s" % str(reason))
