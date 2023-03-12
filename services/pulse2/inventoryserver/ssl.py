#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import socket
import logging
from socketserver import BaseServer
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from OpenSSL import SSL
from twisted.internet import ssl
from socketserver import ThreadingMixIn


def makeSSLContext(verifypeer, cacert, localcert, cb, log=True):
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
        ctx = makeSSLContext(
            config.verifypeer, config.cacert, config.localcert, self.sslReject
        )
        self.socket = SSL.Connection(
            ctx, socket.socket(self.address_family, self.socket_type)
        )
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
