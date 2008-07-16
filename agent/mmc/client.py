# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Set of classes to connect to a MMC server, and do XML-RPC requests.

Example:

def cb(result):
    print result
    reactor.stop()

proxy = MMCProxy("https://127.0.0.1:7080/XMLRPC", "mmc", "s3cr3t")
proxy.callRemote("base.ldapAuth", "root", "passpass").addCallbacks(cb)
reactor.run()
"""

import xmlrpclib
import logging

from twisted.web.xmlrpc import Proxy, QueryProtocol, payloadTemplate

try:
    from twisted.web.xmlrpc import QueryFactory
except ImportError:
    from twisted.web.xmlrpc import _QueryFactory
    QueryFactory = _QueryFactory 
from twisted.internet import reactor, defer, ssl

def makeSSLContext(verifypeer, cacert, localcert, log = True):
    """
    Make the SSL context for the server, according to the parameters

    @returns: a SSL context
    @rtype: twisted.internet.ssl.ContextFactory
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
            logger.debug("MMC agent certificate: %s" % localcert)
            logger.debug(localCertificate.inspect())
    else:
        if log:
            logger.warning("SSL enabled, but peer verification is disabled.")
        ctx = ssl.DefaultOpenSSLContextFactory(localcert, cacert)
    return ctx

class MMCQueryProtocol(QueryProtocol):

    def connectionMade(self):
        self.sendCommand('POST', self.factory.path)
        self.sendHeader('User-Agent', 'Twisted/XMLRPClib')
        self.sendHeader('Host', self.factory.host)
        self.sendHeader('Content-type', 'text/xml')
        self.sendHeader('Content-length', str(len(self.factory.payload)))
        if self.factory.user:
            auth = '%s:%s' % (self.factory.user, self.factory.password)
            auth = auth.encode('base64').strip()
            self.sendHeader('Authorization', 'Basic %s' % (auth,))
        if self.factory.session:
            # Put MMC session cookie
            self.sendHeader('Cookie', self.factory.session)
        self.endHeaders()
        self.transport.write(self.factory.payload)

    def lineReceived(self, line):
        QueryProtocol.lineReceived(self, line)
        if line:
            if line.startswith("Set-Cookie: "):
                value = line.split()[1]
                self.factory.session = value

class MMCQueryFactory(QueryFactory):

    protocol = MMCQueryProtocol

    def __init__(self, path, host, method, user=None, password=None, *args):
        self.path, self.host = path, host
        self.user, self.password = user, password
        self.method = method
        self.payload = payloadTemplate % (method, xmlrpclib.dumps(args))
        self.deferred = defer.Deferred()
        if method == "base.ldapAuth":
            self.deferred.addCallback(self.getSession)

    def getSession(self, value):
        self.parent.session = self.session
        return value
                   
class MMCProxy(Proxy):

    def __init__(self, url, user=None, password=None):
        Proxy.__init__(self, url, user, password)
        self.session = None
        self.SSLClientContext = None

    def setSSLClientContext(self, SSLClientContext):
        self.SSLClientContext = SSLClientContext

    def callRemote(self, method, *args):
        factory = MMCQueryFactory(self.path, self.host, method, self.user,
            self.password, *args)
        factory.parent = self
        factory.session = self.session
        if self.secure:
            from twisted.internet import ssl
            if not self.SSLClientContext:
                self.SSLClientContext = ssl.ClientContextFactory()
            reactor.connectSSL(self.host, self.port or 443,
                               factory, self.SSLClientContext)
        else:
            reactor.connectTCP(self.host, self.port or 80, factory)
        return factory.deferred

class XmlrpcSslProxy(Proxy):

    def __init__(self, url, user=None, password=None):
        Proxy.__init__(self, url, user, password)
        self.SSLClientContext = None

    def setSSLClientContext(self, SSLClientContext):
        self.SSLClientContext = SSLClientContext

    def callRemote(self, method, *args):
        factory = self.queryFactory(
            self.path, self.host, method, self.user,
            self.password, self.allowNone, args)
        if self.secure:
            if not self.SSLClientContext:
                self.SSLClientContext = ssl.ClientContextFactory()
            reactor.connectSSL(self.host, self.port or 443,
                               factory, self.SSLClientContext)
        else:
            reactor.connectTCP(self.host, self.port or 80, factory)
        return factory.deferred
    
