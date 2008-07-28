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
import os
import re
import socket
import sys
import time
import signal
import OpenSSL
import urlparse

from pulse2.proxyssl.utilities import Singleton
from pulse2.proxyssl.config import Pulse2InventoryProxyConfig

from twisted.internet import ssl, reactor
from twisted.web import proxy, server, http
from twisted.web.server import NOT_DONE_YET


if os.name == 'nt':
    from _winreg import *


def makeSSLContext(verifypeer, cacert, localcert, log = False):
    """
    Make the SSL context for the server, according to the parameters

    @returns: a SSL context
    """
    logger = logging.getLogger()
    if verifypeer:
        fd = open(localcert)
        localCertificate = ssl.PrivateCertificate.loadPEM(fd.read())
        fd.close()
        fd = open(cacert)
        caCertificate = ssl.Certificate.loadPEM(fd.read())
        fd.close()
        ctx = localCertificate.options(caCertificate)
        ctx.verify = True
        ctx.verifyDepth = 9
        ctx.requireCertification = True
        ctx.verifyOnce = True
        ctx.enableSingleUseKeys = True
        ctx.enableSessions = True
        ctx.fixBrokenPeers = False
        if log:
            logger.debug("CA certificate informations: %s" % cacert)
            logger.debug(caCertificate.inspect())
            logger.debug("Inventory server certificate: %s" % localcert)
            logger.debug(localCertificate.inspect())
        return ctx
    else:
        if log:
            logger.warning("SSL enabled, but peer verification is disabled.")
        ctx = ssl.DefaultOpenSSLContextFactory(localcert, cacert)
    return ctx


class MyProxyRequest(proxy.ProxyRequest):

    """
    Proxy that handle a outgoing HTTP or HTTPS connection.
    For HTTPS. create a SSL context according to the configuration file.
    """

    config = Pulse2InventoryProxyConfig()
    ports = {'http' : config.port, 'https' : config.port }
    protocols = {'http': proxy.ProxyClientFactory, 'https': proxy.ProxyClientFactory}

    def process(self):
        self.uri = "%s:%d%s" % (self.config.server, self.config.port, self.uri)
        if self.config.enablessl:
            self.uri = "https://" + self.uri
        else:
            self.uri = "http://" + self.uri
        parsed = urlparse.urlparse(self.uri)
        protocol = parsed[0]
        host = parsed[1]
        port = self.ports[protocol]
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        rest = urlparse.urlunparse(('', '') + parsed[2:])
        if not rest:
            rest = rest + '/'
        class_ = self.protocols[protocol]
        headers = self.getAllHeaders().copy()
        if 'host' not in headers:
            headers['host'] = host
        self.content.seek(0, 0)
        s = self.content.read()
        clientFactory = class_(self.method, rest, self.clientproto, headers,
                               s, self)
        if self.config.enablessl:
            try:
                ctx = makeSSLContext(self.config.verifypeer, self.config.cert_file, self.config.key_file)
                self.reactor.connectSSL(host, port, clientFactory, ctx)
            except Exception, e:
                logging.getLogger().error(str(e))
                raise
        else:
            self.reactor.connectTCP(host, port, clientFactory)
        return NOT_DONE_YET

class MyProxy(proxy.Proxy):
    requestFactory = MyProxyRequest


class HttpInventoryProxySingleton(Singleton):
    count_call = 0
    want_quit = False
    def initialise(self, config):
        self.config = config
        self.logger = logging.getLogger()

    def halt(self):
        self.want_quit = True

    def check_flag(self):
        if self.config.flag_type == 'reg':
            self.logger.debug("Checking for flag in registry")
            try:
                key = OpenKey(HKEY_LOCAL_MACHINE, self.config.flag[0])
                hk_do_inv, typeval  = QueryValueEx(key, self.config.flag[1])
                return hk_do_inv == 'yes'
            except WindowsError, e:
                self.logger.debug(str(e))
                return False
        else:
            return False

    def clean_flag(self):
        self.logger.debug("Setting registry key to 'no'")
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, self.config.flag[0], 0, KEY_SET_VALUE)
            SetValue(key, self.config.flag[1], REG_SZ, "no")
            CloseKey(key)
            self.logger.debug("Registry key value set")
        except Exception, e:
            self.logger.error("Can't change registry key value: %s", str(e))
            
        
