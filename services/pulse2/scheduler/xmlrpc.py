# -*- coding: utf-8; -*-
#
# (c) 2008 Mandriva, http://www.mandriva.com/
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

import twisted.web.server
import twisted.internet.error
import twisted.web.xmlrpc
from twisted.internet import ssl, reactor

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http

from pulse2.scheduler.config import SchedulerConfig
import pulse2.utils

class SchedulerHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the
    scheduler is in DEBUG mode, and to log connection errors.
    """

    def connectionMade(self):
        logger = logging.getLogger()
        logger.debug("Connection from %s" % (self.transport.getPeer().host,))
        http.HTTPChannel.connectionMade(self)

    def connectionLost(self, reason):
        if not reason.check(twisted.internet.error.ConnectionDone):
            logger = logging.getLogger()
            logger.error(reason)
        http.HTTPChannel.connectionLost(self, reason)

class SchedulerSite(twisted.web.server.Site):
    protocol = SchedulerHTTPChannel

class OpenSSLContext(pulse2.utils.Singleton):
    """
    Singleton Class to hold OpenSSL stuff, preventing further reopening of client certs
    """
    ctx = None
    verifypeer = False
    cacert_path = None
    localcert_path = None
    cacert_content = None
    localcert_content = None

    def getContext(self):
        """
            Create an SSL context.
        """
        if self.verifypeer:
            localcert = ssl.PrivateCertificate.loadPEM(self.localcert_content)
            cacert = ssl.Certificate.loadPEM(self.cacert_content)
            ctx = localcert.options(cacert)
            ctx.verify = True
            ctx.verifyDepth = 9
            ctx.requireCertification = True
            ctx.verifyOnce = True
            ctx.enableSingleUseKeys = True
            ctx.enableSessions = True
            ctx.fixBrokenPeers = False
            return ctx
        else:
            return ssl.DefaultOpenSSLContextFactory(self.localcert_path, self.cacert_path)

    def setup(self, config):
        """
        Just load the certs in verifypeer mode
        do nothing in standart mode
        """
        logger = logging.getLogger()

        self.verifypeer = config.verifypeer
        self.cacert_path = config.cacert
        self.localcert_path = config.localcert

        if self.verifypeer:
            fd = open(self.cacert_path)
            self.cacert_content = fd.read()
            fd.close()
            fd = open(self.localcert_path)
            self.localcert_content = fd.read()
            fd.close()

            cacert = ssl.Certificate.loadPEM(self.cacert_content)
            logger.info("CA certificate: %s" % self.cacert_path)
            logger.info(cacert.inspect())
            localcert = ssl.PrivateCertificate.loadPEM(self.localcert_content)
            logger.info("My certificate: %s" % self.localcert_path)
            logger.info(localcert.inspect())
            logger.info("SSL enabled, and peer verification is enabled.")
        else:
            logger.warning("SSL enabled, but peer verification is disabled.")

def makeSSLContext(config, log = True):
    if log:
        OpenSSLContext().setup(config)
    return OpenSSLContext().getContext()


class SchedulerProxy(twisted.web.xmlrpc.Proxy):

    def __init__(self, url, user=None, password=None):
        twisted.web.xmlrpc.Proxy.__init__(self, url, user, password)
        self.SSLClientContext = None

    def setSSLClientContext(self, SSLClientContext):
        self.SSLClientContext = SSLClientContext

    def callRemote(self, method, *args):
        factory = self.queryFactory(
            self.path, self.host, method, self.user,
            self.password, self.allowNone, args)
        if self.secure:
            from twisted.internet import ssl
            if not self.SSLClientContext:
                self.SSLClientContext = ssl.ClientContextFactory()
            reactor.connectSSL(self.host, self.port or 443,
                               factory, self.SSLClientContext)
        else:
            reactor.connectTCP(self.host, self.port or 80, factory)
        return factory.deferred

def getProxy(url):
    """
    Return a suitable SchedulerProxy object to communicate with launchers
    """
    if url.startswith("http://"):
        ret = twisted.web.xmlrpc.Proxy(url)
    else:
        config = SchedulerConfig()
        if config.verifypeer:
            # We have to build the SSL context to include scheduler
            # certificates
            ctx = makeSSLContext(config, False)
            ret = SchedulerProxy(url)
            ret.setSSLClientContext(ctx)
        else:
            ret = twisted.web.xmlrpc.Proxy(url)
    return ret
