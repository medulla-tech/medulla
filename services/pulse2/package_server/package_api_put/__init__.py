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
import os
from pulse2.package_server.package_api_get import PackageApiGet
from pulse2.package_server.types import Package
from pulse2.package_server.common import Common
from pulse2.package_server.config import P2PServerCP

class PackageApiPut(PackageApiGet):
    type = 'PackageApiPut'
    
    def __init__(self, mp, name = '', tmp_input_dir = ''):
        PackageApiGet.__init__(self, mp, name)
        self.tmp_input_dir = tmp_input_dir
        self.config = P2PServerCP()

    def xmlrpc_getTemporaryFiles(self):
        ret = []
        if os.path.exists(self.tmp_input_dir):
            for f in os.listdir(self.tmp_input_dir):
                ret.append([f, os.path.isdir(f)])
        return ret

    def xmlrpc_associatePackages(self, pid, fs):
        files = []
        ret = True

        for f in fs:
            if not os.path.exists(os.path.join(self.tmp_input_dir, f)):
                ret = False
            else:
                files.append(os.path.join(self.tmp_input_dir, f))
        if not ret:
            return [False, 'Some files are missing']
                
        ret = Common().associateFiles(self.mp, pid, files)
        Common().dontgivepkgs[pid] = self.config.package_mirror_target
        return [True]
    
    def xmlrpc_putPackageDetail(self, package):
        pa = Package()
        pa.fromH(package)
        if Common().dontgivepkgs.has_key(pa.id) and len(Common().dontgivepkgs[pa.id]) > 0:
            return (False, "This package is curently locked")

        ret = Common().editPackage(package['id'], pa)
        if not ret: return False

        ret = Common().writePackageTo(package['id'], self.mp)
        ret, confdir = ret
        if not ret: return False

        ret = Common().associatePackage2mp(package['id'], self.mp)
        if not ret: return False

        return (True, package['id'], confdir)

    def xmlrpc_dropPackage(self, pid):
        ret = Common().dropPackage(pid, self.mp)
        if not ret: return False

        ret = Common().desassociatePackage2mp(pid, self.mp)
        if not ret: return False

        return pid

    def xmlrpc_putPackageLabel(self, pid, label):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_putPackageVersion(self, pid, version):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_putPackageSize(self, pid, size):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_putPackageInstallInit(self, pid, cmd):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_putPackagePreCommand(self, pid, cmd):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_putPackageCommand(self, pid, cmd):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_putPackagePostCommandSuccess(self, pid, cmd):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_putPackagePostCommandFailure(self, pid, cmd):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_putPackageFiles(self, pid, a_files):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

    def xmlrpc_addPackageFile(self, pid, file):
        self.logger.warn("(%s) %s : call to an unimplemented method"%(self.type, self.name))

