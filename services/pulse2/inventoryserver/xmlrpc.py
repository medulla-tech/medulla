# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

import twisted.web.server
import twisted.internet.error

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http  # pyflakes.ignore


class InventoryHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the
    launcher is in DEBUG mode, and to log connection errors.
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


class InventorySite(twisted.web.server.Site):
    protocol = InventoryHTTPChannel
