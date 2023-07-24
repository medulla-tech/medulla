#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys

from twisted.internet import reactor
from twisted.web import http

from pulse2.proxyssl.config import Pulse2InventoryProxyConfig
from pulse2.proxyssl.http_inventory_proxy import MyProxy, HttpInventoryProxySingleton
from pulse2.proxyssl.threads import RunInventory


def handler(signum, frame):
    """
    SIGTERM handler
    """
    os.seteuid(0)
    os.setegid(0)
    try:
        os.unlink(Pulse2InventoryProxyConfig().pidfile)
    except OSError:
        pass

    sys.exit(0)


def initialize(config):
    singleton = HttpInventoryProxySingleton()
    singleton.initialise(config)
    f = http.HTTPFactory()
    f.protocol = MyProxy
    # Listen to incoming connection
    reactor.listenTCP(config.port, f)
    # Run the periodic inventory if configured
    if config.polling:
        r = RunInventory()
        r.setup(config)
        r.run()
