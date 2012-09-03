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
import os
import time
import exceptions
from base64 import b64decode
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
        self.logger.debug("xmlrpc_getTemporaryFiles")
        ret = []
        if os.path.exists(self.tmp_input_dir):
            for f in os.listdir(self.tmp_input_dir):
                ret.append([f, os.path.isdir(os.path.join(self.tmp_input_dir,f))])
        return ret

    def xmlrpc_pushPackage(self, filename, random_dir, filebinary):
        if not os.path.exists(self.tmp_input_dir):
            return False
        filepath = os.path.join(self.tmp_input_dir, random_dir)
        os.mkdir(filepath)
        f = open(os.path.join(filepath, filename), 'w')
        f.write(b64decode(filebinary))
        f.close()

        return True

    def xmlrpc_associatePackages(self, pid, fs, level = 0):
        files = []
        ret = True

        for f in fs:
            if not os.path.exists(os.path.join(self.tmp_input_dir, f)):
                ret = False
            else:
                files.append(os.path.join(self.tmp_input_dir, f))
        if not ret:
            return [False, 'Some files are missing']
                
        try:
            ret_assoc = Common().associateFiles(self.mp, pid, files, level)
        except exceptions.OSError, e:
           return [False, str(e)]

        if not self.config.package_detect_activate:
            # Run the detectNewPackages stuff to register our new package
            # FIXME: the next line force the new package to be detected
            del Common().packages[pid]
            for i in range(10):
                ret = Common().detectNewPackages()
                if ret: break
                time.sleep(1)
        errors = []
        if ret_assoc[1] & 1:
            errors.append('Some files failed to be erased')
        # COULD ADD SOME MORE FLAGS
            
        ret_assoc[1] = errors
        return ret_assoc

    def xmlrpc_putPackageDetail(self, package, need_assign = True):
        self.logger.debug("xmlrpc_putPackageDetail")
        pa = Package()
        pa.fromH(package)
        if Common().dontgivepkgs.has_key(pa.id) and len(Common().dontgivepkgs[pa.id]) > 0:
            return (False, "This package is curently locked")

        ret = Common().editPackage(package['id'], pa, need_assign)
        if not ret: return False
        
        # Create conf.xml file in package
        ret = Common().writePackageTo(package['id'], self.mp)
        ret, confdir = ret
        if not ret: return False

        ret = Common().associatePackage2mp(package['id'], self.mp)
        if not ret: return False

        if not P2PServerCP().package_detect_activate:
            del Common().inEdition[package['id']]

        return (True, package['id'], confdir, pa.toH())

    def xmlrpc_dropPackage(self, pid):
        ret = Common().dropPackage(pid, self.mp)
        if not ret: return False

        ret = Common().desassociatePackage2mp(pid, self.mp)
        if not ret: return False

        return pid

    def xmlrpc_getRsyncStatus(self, pid):
        return Common().getRsyncStatus(pid, self.mp)

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

