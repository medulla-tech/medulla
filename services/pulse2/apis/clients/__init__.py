# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Class to manage api calls and errors
"""

import logging

from twisted.internet import reactor
import twisted.web.xmlrpc
import pulse2.xmlrpc
from pulse2.apis.consts import PULSE2_ERR_404, PULSE2_ERR_CONN_REF, PULSE2_ERR_UNKNOWN
import exceptions

class Pulse2Api(twisted.web.xmlrpc.Proxy):

    name = "pulse2API"

    def __init__(self, credentials, url, verifypeer = False, cacert = None, localcert = None):
        """
        @param credentials: XML-RPC HTTP BASIC credentials = login:password
        @type credentials: str
        """
        url = str(url)
        twisted.web.xmlrpc.Proxy.__init__(self, url, None, None)
        self.SSLClientContext = None
        self.logger = logging.getLogger()
        if verifypeer :
            pulse2.xmlrpc.OpenSSLContext().setup(localcert, cacert, verifypeer)
            self.SSLClientContext = pulse2.xmlrpc.OpenSSLContext().getContext()
        self.logger.debug('%s will connect to %s' % (self.name, url))
        self.server_addr = url
        self.credentials = credentials
        # FIXME: still needed ?
        self.initialized_failed = False

    def callRemote(self, method, *args):
        if pulse2.xmlrpc.isTwistedEnoughForCert():
            factory = self.queryFactory(self.path, self.host, method, self.user, self.password, self.allowNone, args)
            d = factory.deferred
            if self.secure:
                from twisted.internet import ssl
                if not self.SSLClientContext:
                    self.SSLClientContext = ssl.ClientContextFactory()
                reactor.connectSSL(self.host, self.port or 443, factory, self.SSLClientContext)
            else:
                reactor.connectTCP(self.host, self.port or 80, factory)
            return d
        else:
            # cont support certif
            return twisted.web.xmlrpc.Proxy.callRemote(self, method, *args)

    def onError(self, error, funcname, args, default_return = []):
        self.logger.warn("%s: %s %s has failed: %s" % (self.name, funcname, args, error))
        return default_return

    def onErrorRaise(self, error, funcname, args, default_return = []):
        """
        To use as a deferred error back

        @returns: a list containing error informations
        @rtype: list
        """
        if error.type == twisted.internet.error.ConnectionRefusedError:
            self.logger.error("%s %s has failed: connection refused" % (funcname, args))
            ret = ['PULSE2_ERR', PULSE2_ERR_CONN_REF,
                   self.server_addr, default_return]
        elif error.type == exceptions.ValueError:
            self.logger.error("%s %s has failed: the mountpoint don't exists" % (funcname, args))
            ret = ['PULSE2_ERR', PULSE2_ERR_404,
                   self.server_addr, default_return]
        else:
            self.logger.error("%s %s has failed: %s" % (funcname, args, error))
            ret = ['PULSE2_ERR', PULSE2_ERR_UNKNOWN,
                   self.server_addr, default_return]
        return ret

