#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 30 2008-02-08 16:40:54Z nrueff $
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

"""
    Pulse2 Modules
"""
import twisted.web.html
import twisted.web.xmlrpc
import logging
from pulse2.package_server.common import Common

class PackageApiGet(twisted.web.xmlrpc.XMLRPC):
    type = 'PackageApiGet'
    def __init__(self, mp, name = ''):
        twisted.web.xmlrpc.XMLRPC.__init__(self)
        self.logger = logging.getLogger()
        self.name = name
        self.mp = mp
        if Common().getPackages(self.mp) == None:
            e = "(%s) %s : can't initialise at %s correctly"%(self.type, self.name, self.mp)
            self.logger.error(e)
            raise e
        self.logger.info("(%s) %s : initialised with packages : %s"%(self.type, self.name, str(Common().getPackages(self.mp).keys())))

    def xmlrpc_getServerDetails(self):
        return map(lambda x: Common().package(x).toH(), Common().getPackages(self.mp))

    def xmlrpc_getAllPackages(self, mirror = None):
        return map(lambda x: Common().package(x).toH(), Common().getPackages(self.mp))

    def xmlrpc_getAllPendingPackages(self, mirror = None):
        ret = Common().getPendingPackages(self.mp)
        return map(lambda x: ret[x].toH(), ret)

    def xmlrpc_getPackageDetail(self, pid):
        return Common().package(pid, self.mp).toH()

    def xmlrpc_getLocalPackagePath(self, pid):
        return Common().package(pid, self.mp).root

    def xmlrpc_getPackageLabel(self, pid):
        return Common().package(pid, self.mp).label

    def xmlrpc_getPackageVersion(self, pid):
        return Common().package(pid, self.mp).version

    def xmlrpc_getPackageSize(self, pid):
        return Common().package(pid, self.mp).size

    def xmlrpc_getPackageInstallInit(self, pid):
        return Common().package(pid, self.mp).initcmd.toH()

    def xmlrpc_getPackagePreCommand(self, pid):
        return Common().package(pid, self.mp).precmd.toH()

    def xmlrpc_getPackageCommand(self, pid):
        return Common().package(pid, self.mp).cmd.toH()

    def xmlrpc_getPackagePostCommandSuccess(self, pid):
        return Common().package(pid, self.mp).postcmd_ok.toH()

    def xmlrpc_getPackagePostCommandFailure(self, pid):
        return Common().package(pid, self.mp).postcmd_ko.toH()

    def xmlrpc_getPackageHasToReboot(self, pid):
        return Common().package(pid, self.mp).reboot

    def xmlrpc_getPackageFiles(self, pid): # TODO remove the internals
        return map(lambda x: x.toH(), Common().package(pid, self.mp).files.internals)

    def xmlrpc_getFileChecksum(self, file):
        return None

    def xmlrpc_getPackagesIds(self, label):
        return Common().reverse(self.mp)[label]

    def xmlrpc_getPackageId(self, label, version):
        return Common().reverse(self.mp)[label][version]

    def xmlrpc_isAvailable(self, pid, mirror):
        return True

