#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

"""
    Pulse2 Modules
"""
import logging
import os
from pulse2.package_server.common import Common
from pulse2.package_server.xmlrpc import MyXmlrpc

class PackageApiGet(MyXmlrpc):
    type = 'PackageApiGet'
    def __init__(self, mp, name = ''):
        MyXmlrpc.__init__(self)
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
        r = []
        for x in ret:
            p = ret[x].toH()
            self.logger.debug(Common().newAssociation)
            self.logger.debug(Common().inEdition)
            if Common().newAssociation.has_key(p['id']) or Common().inEdition.has_key(p['id']):
                p['why'] = 'association'
            r.append(p)
        return r

    def xmlrpc_getPackagesDetail(self, pidlist):
        return map(lambda p: p.toH(), Common().packagelist(pidlist, self.mp))
    
    def xmlrpc_getPackageDetail(self, pid):
        try:
            ret = Common().package(pid, self.mp).toH()
        except KeyError:
            # We don't own this package
            ret = {}
        except Exception, e:
            # Another unknown error
            self.logger.exception(e)
            ret = {}
        return ret

    def xmlrpc_getLocalPackagesPath(self, pidlist):
        return map(lambda p: os.path.dirname(p.root), Common().packagelist(pidlist))
        
    def xmlrpc_getLocalPackagePath(self, pid):
        try:
            ret = os.path.dirname(Common().package(pid, self.mp).root)
        except KeyError:
            # We don't own this package
            ret = {}
        except Exception, e:
            # Another unknown error
            self.logger.exception(e)
            ret = {}
        return ret            

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

    def xmlrpc_getPackageQvendor(self, pid):
        return Common().package(pid, self.mp).Qvendor

    def xmlrpc_getPackageQsoftware(self, pid):
        return Common().package(pid, self.mp).Qsoftware

    def xmlrpc_getPackageQversion(self, pid):
        return Common().package(pid, self.mp).Qversion

    def xmlrpc_getPackageBoolcnd(self, pid):
        return Common().package(pid, self.mp).boolcnd

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

