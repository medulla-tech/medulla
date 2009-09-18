# -*- coding: utf-8; -*-
#
# (c) 2008-2009 Mandriva, http://www.mandriva.com/
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

import logging # to log stuff

import twisted
from twisted.internet import ssl

import pulse2.utils

class OpenSSLContext(pulse2.utils.Singleton):
    """
    Singleton Class to hold OpenSSL stuff, preventing further reopening of client certs

    use pulse2.xmlrpc.OpenSSLContext().setup(localcert_path, cacert_path, verifypeer) to setup (first time usage)
    use pulse2.xmlrpc.OpenSSLContext().getContext() to get ctx

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

    def setup(self, localcert_path, cacert_path, verifypeer):
        """
        Just load the certs in verifypeer mode
        do nothing in standart mode
        """
        logger = logging.getLogger()

        self.localcert_path = localcert_path
        self.cacert_path = cacert_path
        self.verifypeer = verifypeer

        if self.verifypeer:
            fd = open(self.cacert_path)
            self.cacert_content = fd.read()
            fd.close()
            fd = open(self.localcert_path)
            self.localcert_content = fd.read()
            fd.close()

            logger.info("CA certificate: %s" % self.cacert_path)
            cacert = ssl.Certificate.loadPEM(self.cacert_content)
            logger.info(cacert.inspect())
            logger.info("My certificate: %s" % self.localcert_path)
            localcert = ssl.PrivateCertificate.loadPEM(self.localcert_content)
            logger.info(localcert.inspect())
            logger.info("SSL enabled, and peer verification is enabled.")
        else:
            logger.warning("SSL enabled, but peer verification is disabled.")

def __checkTwistedVersion(min):
    try:
        if twisted.version.major > min[0] or twisted.version.major == min[0] and twisted.version.minor > min[1]:
            return True
        return False
    except:
        return False

def isTwistedEnoughForLoginPass():
    min = (2, 3)
    return __checkTwistedVersion(min)
    
def isTwistedEnoughForCert():
    min = (2, 5)
    return __checkTwistedVersion(min)
