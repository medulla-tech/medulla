#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 22 2008-06-16 07:43:42Z cdelfosse $
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
import os
import sys
import signal

from pulse2.proxyssl.config import Pulse2InventoryProxyConfig
from pulse2.proxyssl.threads import LaunchInv, ServerInv
from pulse2.proxyssl.http_inventory_proxy import HttpInventoryProxySingleton, HttpInventoryProxy

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
    HttpInventoryProxySingleton().initialise(config)

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    launchinv = LaunchInv(config)
    launchinv.setDaemon(True)

    serverinv = ServerInv(config)
    serverinv.setDaemon(True)

    serverinv.start()
    launchinv.start()

    launchinv.join()
    serverinv.join()

