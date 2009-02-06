# -*- coding: utf-8; -*-
#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id: xmlrpc.py 307 2009-02-06 09:09:43Z nrueff $
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

import logging # to log stuff

import twisted.web.server
import twisted.internet.error
import twisted.web.xmlrpc
from twisted.internet import ssl, reactor

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http

import pulse2.utils

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

