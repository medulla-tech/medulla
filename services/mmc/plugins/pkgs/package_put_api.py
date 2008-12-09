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
from mmc.support.uuid import uuid1

class PackagePutA:
    def __init__(self, server, port = None, mountpoint = None, proto = 'http', login = ''):
        self.logger = logging.getLogger()
        if type(server) == dict:
            mountpoint = server['mountpoint']
            port = server['port']
            proto = server['protocol']
            bind = server['server']
            if server.has_key('username') and server.has_key('password') and server['username'] != '':
                login = "%s:%s@" % (server['username'], server['password'])

        self.server_addr = '%s://%s%s:%s%s' % (proto, login, bind, str(port), mountpoint)
        self.logger.debug('PackagePutA will connect to %s' % (self.server_addr))

        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")
        if self.config.upaa_verifypeer:
            self.ppaserver = XmlrpcSslProxy(self.server_addr)
            self.sslctx = makeSSLContext(self.config.upaa_verifypeer, self.config.upaa_cacert, self.config.upaa_localcert, False)
            self.ppaserver.setSSLClientContext(self.sslctx)
        else:
            self.ppaserver = Proxy(self.server_addr)
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args = '', value = []):
        self.logger.warn("PackagePutA:%s %s has failed: %s" % (funcname, str(args), error))
        return value

    def getTemporaryFiles(self):
        if self.initialized_failed:
            return []
        d = self.ppaserver.callRemote("getTemporaryFiles")
        d.addErrback(self.onError, "getTemporaryFiles")
        return d

    def associatePackages(self, pid, files, level = 0):
        if self.initialized_failed:
            return []
        d = self.ppaserver.callRemote("associatePackages", pid, files, level)
        d.addErrback(self.onError, "associatePackages", [pid, files, level])
        return d

    def putPackageDetail(self, package, need_assign = True):
        if self.initialized_failed:
            return -1
        if package.has_key('mode') and package['mode'] == 'creation' and package['id'] == '':
            package['id'] = str(uuid1())
        d = self.ppaserver.callRemote("putPackageDetail", package, need_assign)
        d.addErrback(self.onError, "putPackageDetail", package, -1)
        return d

    def dropPackage(self, pid):
        if self.initialized_failed:
            return -1
        d = self.ppaserver.callRemote("dropPackage", pid)
        d.addErrback(self.onError, "dropPackage", pid, -1)
        return d

    def getRsyncStatus(self, pid):
        if self.initialized_failed:
            return -1
        d = self.ppaserver.callRemote("getRsyncStatus", pid)
        d.addErrback(self.onError, "getRsyncStatus", pid, -1)
        return d
