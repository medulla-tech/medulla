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

import BaseHTTPServer
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import HTTPSConnection
import threading
from threading import Thread
import twisted.internet.utils

from pulse2.proxyssl.utilities import Singleton
from pulse2.proxyssl.config import Pulse2InventoryProxyConfig

class LaunchInv(Thread):
    def __init__(self, config):
        self.config = config
        Thread.__init__(self)

    def run(self):
        twisted.internet.utils.getProcessOutputAndValue(self.config.command_name, self.config.command_attr)

class ServerInv(Thread):
    
    def __init__(self, config):
        self.config = config
        Thread.__init__(self)

    def run(self):
        from pulse2.proxyssl.http_inventory_proxy import HttpInventoryProxy, HttpInventoryProxySingleton
        httpd = HTTPServer(('', self.config.local_port), HttpInventoryProxy)
        if self.config.pooling == True:
            httpd.serve_forever()
        else:
            while not HttpInventoryProxySingleton().want_quit:
                httpd.handle_request()


