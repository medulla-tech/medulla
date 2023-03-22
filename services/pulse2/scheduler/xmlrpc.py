# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
import logging

import twisted.web.server
import twisted.internet.error
import twisted.web.xmlrpc

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http # pyflakes.ignore

from pulse2.scheduler.config import SchedulerConfig
from pulse2.xmlrpc import Pulse2XMLRPCProxy

class SchedulerHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the
    scheduler is in DEBUG mode, and to log connection errors.
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

class SchedulerSite(twisted.web.server.Site):
    protocol = SchedulerHTTPChannel


def getProxy(url):
    """
    Return a suitable SchedulerProxy object to communicate with launchers
    """
    verifypeer = SchedulerConfig().verifypeer
    cacert = SchedulerConfig().cacert
    localcert = SchedulerConfig().localcert

    return Pulse2XMLRPCProxy(url,
                             verifypeer=verifypeer,
                             cacert=cacert,
                             localcert=localcert
                             )
