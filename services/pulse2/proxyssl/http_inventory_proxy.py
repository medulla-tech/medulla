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
import sys
import urlparse

from pulse2.proxyssl.utilities import Singleton
from pulse2.proxyssl.config import Pulse2InventoryProxyConfig

from twisted.internet import ssl
from twisted.web import proxy
from twisted.web.server import NOT_DONE_YET

from zlib import *

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


class MyProxyClientFactory(proxy.ProxyClientFactory):

    def buildProtocol(self, addr):
        # Connection succeeded, we can clean the inventory flag if set
        if HttpInventoryProxySingleton().checked_flag:
            HttpInventoryProxySingleton().clean_flag()        
        return proxy.ProxyClientFactory.buildProtocol(self, addr)

    def clientConnectionFailed(self, connector, reason):
        logging.getLogger().error("Connection failed: " + str(reason))
        proxy.ProxyClientFactory.clientConnectionFailed(self, connector, reason)


class MyProxyRequest(proxy.ProxyRequest):

    """
    Proxy that handle a outgoing HTTP or HTTPS connection.
    For HTTPS. create a SSL context according to the configuration file.
    """

    config = Pulse2InventoryProxyConfig()
    ports = {'http' : config.port, 'https' : config.port }
    protocols = {'http': MyProxyClientFactory, 'https': MyProxyClientFactory}

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
        
        logger = logging.getLogger()
        
        logger.debug("\nOcs Report Received");
        
        # We will unzip the XML File and parsing it only if needed
        if self.config.getocsdebuglog or self.config.improve:
            # xml file unzip 
            try:
                decomp = decompressobj()
                sUnpack = decomp.decompress(s)
                if decomp.unused_data:
                    logger.warn("The zip content seems to be bad.")
                    logger.debug("The remaining bytes are : %s"%(decomp.unused_data))
            except Exception, e:
                logger.error("Failed during decompression.")
                logger.error(str(e))
                raise e
            
            # Get the query type
            try:
                query = re.search(r'<QUERY>([\w-]+)</QUERY>', sUnpack).group(1)
            except AttributeError, e:
                query = 'FAILS'
            
            # process on Inventory OCS XML file, 
            if query == 'INVENTORY' :
                try:
                    if sys.platform[0:3] == "win":                          #It's here because I need Pulse2InventoryProxyConfig be initialited before improve packtage be initialat
                        from improveWin import improveXML,getOcsDebugLog
                    elif sys.platform == "mac":
                        from improveMac import improveXML,getOcsDebugLog # pyflakes.ignore
                    else:
                        from improveUnix import improveXML,getOcsDebugLog # pyflakes.ignore
                    logger.debug("\tOcs Inventory Report Processing")
                    if self.config.getocsdebuglog:
                        # Add Ocs Log File
                        sUnpack = getOcsDebugLog(sUnpack)
                        logger.debug("\t\tOcs Debug Log add")
                    if self.config.improve:
                        # improving of xml file
                        sUnpack = improveXML(sUnpack)    
                        logger.debug("\t\tInformations add")
                except ImportError:
                    logger.error("OCS improving failed: no improving function found for "+sys.platform+" platform")
            
            logger.debug("\tOcs Report Terminated");
            logger.debug("\t\tuncompressed length: " + str(len(sUnpack)))
            
            # zip of xml file
            try:
                comp = compressobj()
                s = comp.compress(sUnpack) + comp.flush() # default to Z_FINISH
                logger.debug("\t\tcompressed length: " + str(len(s)))
            except Exception, e:
                logger.error("Failed during compression.")
                logger.error(str(e))
                raise e
            
            # update the new size of xml
            headers['content-length'] = len(s)
                    
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

    checked_flag = False

    def initialise(self, config):
        self.config = config
        self.logger = logging.getLogger()

    def check_flag(self):
        if self.config.flag_type == 'reg':
            self.logger.debug("Checking flag in registry %s %s" % (self.config.flag[0], self.config.flag[1]))
            try:
                key = OpenKey(HKEY_LOCAL_MACHINE, self.config.flag[0])
                hk_do_inv, typeval  = QueryValueEx(key, self.config.flag[1])
                ret = hk_do_inv == 'yes'
            except WindowsError, e:
                self.logger.debug(str(e))
                ret = False
            self.checked_flag = ret
        else:
            ret = False
        return ret

    def clean_flag(self):
        self.logger.debug("Setting registry key to 'no' %s %s" % (self.config.flag[0], self.config.flag[1]))
        self.checked_flag = False
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, self.config.flag[0], 0, KEY_SET_VALUE)
            SetValueEx(key, self.config.flag[1], 0, REG_SZ, "no")
            CloseKey(key)
            self.logger.debug("Registry key value set")
        except Exception, e:
            self.logger.error("Can't change registry key value: %s", str(e))
            
        
