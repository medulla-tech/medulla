# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2008-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

import twisted
from twisted.internet import ssl
from twisted.internet import reactor
from twisted.web.xmlrpc import Proxy

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
            return ssl.DefaultOpenSSLContextFactory(
                self.localcert_path, self.cacert_path
            )

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


class Pulse2XMLRPCProxy(Proxy):
    def __init__(
        self,
        url,
        user=None,
        password=None,
        verifypeer=False,
        cacert=None,
        localcert=None,
    ):
        self._version_reminder()

        twisted.web.xmlrpc.Proxy.__init__(self, url, user, password)

        self.SSLClientContext = None

        if verifypeer:
            if cacert and localcert:
                OpenSSLContext().setup(localcert, cacert, verifypeer)
            self.SSLClientContext = OpenSSLContext().getContext()

    def _version_reminder(self):
        """
        Content of method callRemote was changed since 10.1.
        (last check for 17.5)

        Check please its content for each release of twisted and validate it
        increasing number version bellow...
        """
        if twisted.version.major < 10:
            logging.getLogger().warn(
                "Uncompatible Twisted version, must be greater than 10.1"
            )
            return False

        if twisted.version.major >= 17 and twisted.version.minor > 5:
            logging.getLogger().warn(
                "Uncompatible Twisted version, must be less than than 17.5"
            )
            return False

        return True

    def callRemote(self, method, *args):
        """
        Overrided only for giving the SSL context.

        Please check this method for each release of Twisted !!!
        """

        def cancel(ignored):
            factory.deferred = None
            connector.disconnect()

        factory = self.queryFactory(
            self.path,
            self.host,
            method,
            self.user,
            self.password,
            self.allowNone,
            args,
            cancel,
            self.useDateTime,
        )
        d = factory.deferred

        if self.secure:
            if not self.SSLClientContext:
                self.SSLClientContext = ssl.ClientContextFactory()
            connector = reactor.connectSSL(
                self.host,
                self.port or 443,
                factory,
                self.SSLClientContext,
            )
        else:
            connector = reactor.connectTCP(
                self.host,
                self.port or 80,
                factory,
            )
        return d


def __checkTwistedVersion(min):
    try:
        if (
            twisted.version.major > min[0]
            or twisted.version.major == min[0]
            and twisted.version.minor > min[1]
        ):
            return True
        return False
    except BaseException:
        return False


def isTwistedEnoughForLoginPass():
    min = (2, 3)
    return __checkTwistedVersion(min)


def isTwistedEnoughForCert():
    min = (2, 5)
    return __checkTwistedVersion(min)
