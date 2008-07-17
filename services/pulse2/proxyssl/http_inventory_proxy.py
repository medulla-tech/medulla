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
import re
import socket
import sys
import time
import signal

import BaseHTTPServer
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from httplib import HTTPSConnection

from pulse2.proxyssl.utilities import Singleton
from pulse2.proxyssl.threads import LaunchInv, ServerInv
from pulse2.proxyssl.config import Pulse2InventoryProxyConfig
if os.name == 'nt':
    from _winreg import *

class HttpInventoryProxySingleton(Singleton):
    count_call = 0
    want_quit = False
    def initialise(self, config):
        self.config = config

    def halt(self):
        self.want_quit = True

    def check_flag(self):
        if self.config.flag_type == 'reg':
            try:
                key = OpenKey(HKEY_LOCAL_MACHINE, self.config.flag[0])
                (hk_do_inv,typeval) = QueryValueEx(key, self.config.flag[1])
                return hk_do_inv == 'yes'
            except WindowsError, e:
                return False
        else:
            return False

class HttpInventoryProxy(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, *args):
        self.logger = logging.getLogger()
        self.config = Pulse2InventoryProxyConfig()
        self.singleton = HttpInventoryProxySingleton()
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)

    def log_message(self, format, *args):
        self.logger.info(format % args)

    def send(self, data):
        if self.config.enablessl:
            h = HTTPSConnection(self.config.server, self.config.port)
            h.key_file = self.config.key_file
            h.cert_file = self.config.cert_file
        else:
            h = HTTPConnection(self.config.server, self.config.port)
        try:
            h.request('POST', self.config.path, data, {'content-type':'application/x-compress'})
        except socket.error, e:
            if e.args == (111, 'Connection refused'):
                print "Connection refused"
            else:
                print e.args
            sys.exit(-1)
                
        return h.getresponse()

    def do_POST(self):
        content = self.rfile.read(int(self.headers['Content-Length']))
        cont = [content, self.headers['Content-Type']]
        resp = self.send(content)
        self.send_response(resp.status)
        self.end_headers()
        self.wfile.write(resp.read())
        if not self.config.pooling:
            self.singleton.count_call += 1
            if self.singleton.count_call > 1:
                self.singleton.halt()

