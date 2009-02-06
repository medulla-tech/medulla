# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import re
import dircache
import os
import logging

from twisted.web.xmlrpc import Proxy

import mmc.plugins.msc

from mmc.client import XmlrpcSslProxy, makeSSLContext

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.
class MirrorApi:

    def __init__(self, url = None):
        self.logger = logging.getLogger()
        if url:
            self.server_addr = str(url)
            self.maserver = Proxy(self.server_addr)
        else:
            self.config = mmc.plugins.msc.MscConfig()

            if self.config.ma_enablessl:
                self.server_addr = 'https://'
            else:
                self.server_addr = 'http://'

            if self.config.ma_username != '':
                self.server_addr += self.config.ma_username
                if self.config.ma_password != '':
                    self.server_addr += ":"+self.config.ma_password
                self.server_addr += "@"

            self.server_addr += self.config.ma_server+':'+str(self.config.ma_port) + self.config.ma_mountpoint

            if self.config.ma_verifypeer:
                self.maserver = XmlrpcSslProxy(self.server_addr)
                self.sslctx = makeSSLContext(self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert, False)
                self.maserver.setSSLClientContext(self.sslctx)
            else:
                self.maserver = Proxy(self.server_addr)
        self.logger.debug('MirrorApi will connect to %s' % (self.server_addr))
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args):
        self.logger.warn("%s %s has failed: %s" % (funcname, args, error))
        return []

    def getMirror(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.maserver.callRemote("getMirror", machine)
        d.addErrback(self.onError, "MirrorApi:getMirror", machine)
        return d

    def getMirrors(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.maserver.callRemote("getMirrors", machines)
        d.addErrback(self.onError, "MirrorApi:getMirrors", machines)
        return d

    def getFallbackMirror(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.maserver.callRemote("getFallbackMirror", machine)
        d.addErrback(self.onError, "MirrorApi:getFallbackMirror", machine)
        return d

    def getFallbackMirrors(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.maserver.callRemote("getFallbackMirrors", machines)
        d.addErrback(self.onError, "MirrorApi:getFallbackMirrors", machines)
        return d

    def getApiPackage(self, machine):
        self.logger.debug(machine)
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.maserver.callRemote("getApiPackage", machine)
        d.addErrback(self.onError, "MirrorApi:getApiPackage", machine)
        return d

    def getApiPackages(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.maserver.callRemote("getApiPackages", machines)
        d.addErrback(self.onError, "MirrorApi:getApiPackages", machines)
        return d

    def convertMachineIntoH(self, machine):
        if type(machine) != dict:
            machine = {'uuid':machine}
        return machine

    def isAvailable(self, pid):
        """ Is my package (identified by pid) available ? """
        d = self.maserver.callRemote("isAvailable", pid)
        d.addErrback(self.onError, "MirrorApi:isAvailable", pid)
        return d

    def getFileURI(self, fid):
        """ convert from a fid (File ID) to a file URI """
        d = self.maserver.callRemote("getFileURI", fid)
        d.addErrback(self.onError, "MirrorApi:getFileURI", fid)
        return d

    def getFilesURI(self, fids):
        """ convert from a list of fids (File ID) to a list of files URI """
        d = self.maserver.callRemote("getFilesURI", fids)
        d.addErrback(self.onError, "MirrorApi:getFilesURI", fids)
        return d
