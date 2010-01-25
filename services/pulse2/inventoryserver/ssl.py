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


import socket
import logging
from SocketServer import BaseServer
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from OpenSSL import SSL
from twisted.internet import ssl
from SocketServer import ThreadingMixIn


def makeSSLContext(verifypeer, cacert, localcert, cb, log = True):
    """
    Make the SSL context for the server, according to the parameters

    @returns: a SSL context
    """
    logger = logging.getLogger()    
    if verifypeer:
        # I use twisted certificate loading function, else our CA and our
        # private key don't match, I didn't find out why
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
        return ctx.getContext()
    else:
        if log:
            logger.warning("SSL enabled, but peer verification is disabled.")
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_privatekey_file(localcert)
        ctx.use_certificate_file(cacert)
    return ctx

class SecureHTTPServer(HTTPServer):

    def __init__(self, server_address, HandlerClass, config):
        BaseServer.__init__(self, server_address, HandlerClass)
        ctx = makeSSLContext(config.verifypeer, config.cacert, config.localcert, self.sslReject)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
        self.server_bind()
        self.server_activate()

    def sslReject(self, conn, x509, errnum, errdepth, retcode):
        logger = logging.getLogger()
        logger.warning("SSL reject !")
        request, client_address = self.get_request()
        self.close_request(request)

class SecureHTTPRequestHandler(SimpleHTTPRequestHandler):
    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

class SecureThreadedHTTPServer(ThreadingMixIn, SecureHTTPServer):
    """Handle requests in a separate thread."""
    

