# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

""" Tools for SSL connection
"""
from twisted.internet import ssl
import logging

log = logging.getLogger()


def makeSSLContext(verifypeer, cacert, localcert):
    """
    Make the SSL context for the server, according to the parameters

    @returns: a SSL context
    @rtype: twisted.internet.ssl.ContextFactory
    """
    if verifypeer:
        with open(localcert) as fd:
            localCertificate = ssl.PrivateCertificate.loadPEM(fd.read())
        with open(cacert) as fd:
            caCertificate = ssl.Certificate.loadPEM(fd.read())
        ctx = localCertificate.options(caCertificate)
        ctx.verify = True
        ctx.verifyDepth = 9
        ctx.requireCertification = True
        ctx.verifyOnce = True
        ctx.enableSingleUseKeys = True
        ctx.enableSessions = True
        ctx.fixBrokenPeers = False

        log.debug(f"CA certificate informations: {cacert}")
        log.debug(caCertificate.inspect())
        log.debug(f"MMC agent certificate: {localcert}")
        log.debug(localCertificate.inspect())
    else:
        log.warning("SSL enabled, but peer verification is disabled.")

        ctx = ssl.DefaultOpenSSLContextFactory(localcert, cacert)
    return ctx
