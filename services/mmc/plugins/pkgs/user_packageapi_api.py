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

import re
import dircache
import os
import logging

import xmlrpclib
from twisted.web.xmlrpc import Proxy

from mmc.support.mmctools import Singleton
import mmc.plugins.pkgs.config

from mmc.client import XmlrpcSslProxy, makeSSLContext

class UserPackageApiApi(Singleton):
    def __init__(self):
        self.logger = logging.getLogger()
        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")

        if self.config.upaa_enablessl:
            self.server_addr = 'https://'
        else:
            self.server_addr = 'http://'

        if self.config.upaa_username != '':
            self.server_addr += self.config.upaa_username
            if self.config.upaa_password != '':
                self.server_addr += ":"+self.config.upaa_password
            self.server_addr += "@"

        self.server_addr += self.config.upaa_server+':'+str(self.config.upaa_port) + self.config.upaa_mountpoint
        self.logger.debug('UserPackageApiApi will connect to %s' % (self.server_addr))

        if self.config.upaa_verifypeer:
            self.upaaserver = XmlrpcSslProxy(self.server_addr)
            self.sslctx = makeSSLContext(self.config.upaa_verifypeer, self.config.upaa_cacert, self.config.upaa_localcert, False)
            self.upaaserver.setSSLClientContext(self.sslctx)
        else:
            self.upaaserver = Proxy(self.server_addr)
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args):
        self.logger.warn("%s %s has failed: %s" % (funcname, args, error))
        return []

    def getUserPackageApi(self, user):
        if self.initialized_failed:
            return {}
        d = self.upaaserver.callRemote("getUserPackageApi", {"name":user, "uuid":user})
        d.addErrback(self.onError, "UserPackageApiApi:getUserPackageApi", {"name":user, "uuid":user})
        return d
