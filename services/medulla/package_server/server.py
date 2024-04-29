# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import twisted.web.server

import logging

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http  # pyflakes.ignore


class P2PHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the MMC
    agent is in DEBUG mode, and to log connection errors.
    """

    def connectionMade(self):
        logger = logging.getLogger()
        logger.debug("Connection from %s" % (self.transport.getPeer().host,))
        http.HTTPChannel.connectionMade(self)

    def connectionLost(self, reason):
        if not reason.check(twisted.internet.error.ConnectionDone) and not reason.check(
            twisted.internet.error.ConnectionLost
        ):
            logger = logging.getLogger()
            logger.error(reason)
        http.HTTPChannel.connectionLost(self, reason)


class P2PSite(twisted.web.server.Site):
    protocol = P2PHTTPChannel
