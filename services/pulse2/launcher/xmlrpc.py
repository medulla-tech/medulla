# -*- coding: utf-8; -*-
#
# (c) 2008 Mandriva, http://www.mandriva.com/
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

import logging

import twisted.internet.reactor
import twisted.web.server
import twisted.internet.error
import twisted.web.xmlrpc

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http # pyflakes.ignore

from pulse2.launcher.config import LauncherConfig
from pulse2.xmlrpc import Pulse2XMLRPCProxy

class LauncherHTTPChannel(http.HTTPChannel):
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

class LauncherSite(twisted.web.server.Site):
    protocol = LauncherHTTPChannel


def getProxy(url):
    """
    Return a suitable LauncherProxy object to communicate with scheduler
    """
    verifypeer = LauncherConfig().launchers[LauncherConfig().name]['verifypeer']
    return Pulse2XMLRPCProxy(url, verifypeer=verifypeer)

