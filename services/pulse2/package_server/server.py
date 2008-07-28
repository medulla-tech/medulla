import xmlrpclib

import twisted.web.xmlrpc
import twisted.web.server

import twisted.internet.defer
import twisted.internet.reactor
import twisted.internet.ssl

import logging

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http

class P2PHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the MMC
    agent is in DEBUG mode, and to log connection errors.
    """
    
    def connectionMade(self):
        logger = logging.getLogger()
        logger.debug("Connection from %s" % (self.transport.getHost().host,))
        http.HTTPChannel.connectionMade(self)

    def connectionLost(self, reason):
        if not reason.check(twisted.internet.error.ConnectionDone):
            logger = logging.getLogger()
            logger.error(reason)
        http.HTTPChannel.connectionLost(self, reason)        

class P2PSite(twisted.web.server.Site):
    protocol = P2PHTTPChannel

def makeSSLContext(verifypeer, cacert, localcert, log = True):
    """
    Make the SSL context for the server, according to the parameters

    @returns: a SSL context
    @rtype: twisted.internet.ssl.ContextFactory
    """
    logger = logging.getLogger()    
    if verifypeer:
        logger.debug(localcert)
        fd = open(localcert)
        localCertificate = twisted.internet.ssl.PrivateCertificate.loadPEM(fd.read())
        fd.close()
        fd = open(cacert)
        caCertificate = twisted.internet.ssl.Certificate.loadPEM(fd.read())
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
        ctx = twisted.internet.ssl.DefaultOpenSSLContextFactory(localcert, cacert)
    return ctx
