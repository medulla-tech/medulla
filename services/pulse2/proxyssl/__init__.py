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
