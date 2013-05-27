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

"""
This module define the package_api_put API
It provides methods to modify packages.
"""

from pulse2.apis.clients import Pulse2Api
from uuid import uuid1

class PackagePutA(Pulse2Api):
    def __init__(self, *attr):
        self.name = "PackagePutApi"
        Pulse2Api.__init__(self, *attr)

    def getTemporaryFiles(self):
        if self.initialized_failed:
            return []
        d = self.callRemote("getTemporaryFiles")
        d.addErrback(self.onError, "getTemporaryFiles")
        return d

    def getTemporaryFilesSuggestedCommand(self, tempdir):
        if self.initialized_failed:
            return -1
        d = self.callRemote("getTemporaryFilesSuggestedCommand", tempdir)
        d.addErrback(self.onError, "getTemporaryFilesSuggestedCommand", [tempdir])
        return d

    def associatePackages(self, pid, files, level = 0):
        if self.initialized_failed:
            return [False, "PackagePutA %s failed to initialize"%self.server_addr]
        d = self.callRemote("associatePackages", pid, files, level)
        d.addErrback(self.onError, "associatePackages", [pid, files, level])
        return d

    def pushPackage(self, random_dir, files, local_files):
        if self.initialized_failed:
            return -1
        d = self.callRemote("pushPackage", random_dir, files, local_files)
        d.addErrback(self.onError, "pushPackage", [random_dir, files, local_files], -1)
        return d

    def putPackageDetail(self, package, need_assign = True):
        if self.initialized_failed:
            return -1
        if package.has_key('mode') and package['mode'] == 'creation' and package['id'] == '':
            package['id'] = str(uuid1())
        d = self.callRemote("putPackageDetail", package, need_assign)
        d.addErrback(self.onError, "putPackageDetail", package, -1)
        return d

    def dropPackage(self, pid):
        if self.initialized_failed:
            return -1
        d = self.callRemote("dropPackage", pid)
        d.addErrback(self.onError, "dropPackage", pid, -1)
        return d

    def getRsyncStatus(self, pid):
        if self.initialized_failed:
            return -1
        d = self.callRemote("getRsyncStatus", pid)
        d.addErrback(self.onError, "getRsyncStatus", pid, -1)
        return d
