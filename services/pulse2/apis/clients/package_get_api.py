#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id: package_api.py 713 2009-02-27 14:06:11Z oroussy $
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
This module define the package_api_get API
It provides methods to acces to package informations.
"""

from pulse2.apis.clients import Pulse2Api
import twisted.internet.defer

class PackageGetA(Pulse2Api):
    def __init__(self, *attr):
        self.name = "PackageGetApi"
        Pulse2Api.__init__(self, *attr)
    
    def getAllPackages(self, mirror = None):
        try:
            d = self.callRemote("getAllPackages", mirror)
            d.addErrback(self.onError, "getAllPackages", mirror, [{'label':'A', 'version':'0', 'ERR':'PULSE2ERROR_GETALLPACKAGE', 'mirror':self.server_addr.replace(self.credentials, '')}])
            return d
        except Exception, e:
            self.logger.error("getAllPackages %s"%(str(e)))
            return [{'label':'A', 'version':'0', 'ERR':'PULSE2ERROR_GETALLPACKAGE', 'mirror':self.server_addr.replace(self.credentials, '')}]

    def getAllPendingPackages(self, mirror = None):
        try:
            d = self.callRemote("getAllPendingPackages", mirror)
            d.addErrback(self.onError, "getAllPendingPackages", mirror)
            return d
        except Exception, e:
            self.logger.error("getAllPendingPackages %s"%(str(e)))
            return []

    # FIXME ! __convertDoReboot* shouldn't be needed

    def __convertDoRebootList(self, pkgs):
        ret = []
        for pkg in pkgs:
            ret.append(self.__convertDoReboot(pkg))
        return ret
            
    def __convertDoReboot(self, pkg):
        if pkg:
            try:
                do_reboot = pkg['reboot']
                if do_reboot == '' or do_reboot == '0' or do_reboot == 0 or do_reboot == u'0' or do_reboot == 'false' or do_reboot == u'false' or do_reboot == False or do_reboot == 'disable' or do_reboot == u'disable' or do_reboot == 'off' or do_reboot == u'off':
                    pkg['do_reboot'] = 'disable'
                elif do_reboot == '1' or do_reboot == 1 or do_reboot == u'1' or do_reboot == 'true' or do_reboot == u'true' or do_reboot == True or do_reboot == 'enable' or do_reboot == u'enable' or do_reboot == 'on' or do_reboot == u'on':
                    pkg['do_reboot'] = 'enable'
                else:
                    self.logger.warning("Dont know option '%s' for do_reboot, will use 'disable'"%(do_reboot))
                del pkg['reboot']
            except KeyError:
                pkg['do_reboot'] = 'disable'
        return pkg

    def getPackageDetail(self, pid):
        d = self.callRemote("getPackageDetail", pid)
        d.addCallback(self.__convertDoReboot)
        d.addErrback(self.onError, "getPackageDetail", pid, False)
        return d

    def getPackagesDetail(self, pids):
        d = self.callRemote("getPackagesDetail", pids)
        d.addCallback(self.__convertDoRebootList)
        d.addErrback(self.onErrorGetPackageDetailCall, pids, False)
        return d
 
    def treatMultipleGetPackageDetailCall(self, results):
        ret = []
        for i in results:
            ret.append(i[1])
        return ret

    def onErrorGetPackageDetailCall(self, error, pids, value = []):
        # when the package server is old, this one call function does not exists
        # so we call several time the existing function
        self.logger.warn("one of your package server does not support getPackagesDetail, you should update it.")
        ds = []
        for pid in pids:
            d = self.callRemote("getPackageDetail", pid)
            d.addCallback(self.__convertDoReboot)
            d.addErrback(self.onError, "getPackageDetail", pid, False)
            ds.append(d)
        dl = twisted.internet.defer.DeferredList(ds)
        dl.addCallback(self.treatMultipleGetPackageDetailCall)
        return dl

    def getPackageLabel(self, pid):
        d = self.callRemote("getPackageLabel", pid)
        d.addErrback(self.onError, "getPackageLabel", pid, False)
        return d

    def _erGetLocalPackagePath(self):
        return self.config.repopath

    def getLocalPackagePath(self, pid):
        d = self.callRemote("getLocalPackagePath", pid)
        d.addErrback(self._erGetLocalPackagePath)
        return d

    def getLocalPackagesPath(self, pids):
        d = self.callRemote("getLocalPackagesPath", pids)
        d.addErrback(self.onError, "getLocalPackagesPath", pids, False)
        return d

    def getPackageVersion(self, pid):
        d = self.callRemote("getPackageVersion", pid)
        d.addErrback(self.onError, "getPackageVersion", pid, False)
        return d


    def getPackageSize(self, pid):
        d = self.callRemote("getPackageSize", pid)
        d.addErrback(self.onError, "getPackageSize", pid, 0)
        return d

    def getPackageInstallInit(self, pid):
        d = self.callRemote("getPackageInstallInit", pid)
        d.addErrback(self.onError, "getPackageInstallInit", pid, False)
        return d

    def getPackagePreCommand(self, pid):
        d = self.callRemote("getPackagePreCommand", pid)
        d.addErrback(self.onError, "getPackagePreCommand", pid, False)
        return d

    def getPackageCommand(self, pid):
        d = self.callRemote("getPackageCommand", pid)
        d.addErrback(self.onError, "getPackageCommand", pid, False)
        return d

    def getPackagePostCommandSuccess(self, pid):
        d = self.callRemote("getPackagePostCommandSuccess", pid)
        d.addErrback(self.onError, "getPackagePostCommandSuccess", pid, False)
        return d

    def getPackagePostCommandFailure(self, pid):
        d = self.callRemote("getPackagePostCommandFailure", pid)
        d.addErrback(self.onError, "getPackagePostCommandFailure", pid, False)
        return d

    def getPackageHasToReboot(self, pid):
        d = self.callRemote("getPackageHasToReboot", pid)
        d.addErrback(self.onError, "getPackageHasToReboot", pid, False)
        return d

    def getPackageFiles(self, pid):
        d = self.callRemote("getPackageFiles", pid)
        d.addErrback(self.onError, "getPackageFiles", pid)
        return d

    def getFileChecksum(self, file):
        d = self.callRemote("getFileChecksum", file)
        d.addErrback(self.onError, "getFileChecksum", file, False)
        return d

    def getPackagesIds(self, label):
        d = self.callRemote("getPackagesIds", label)
        d.addErrback(self.onError, "getPackagesIds", label)
        return d

    def getPackageId(self, label, version):
        d = self.callRemote("getPackageId", label, version)
        d.addErrback(self.onError, "getPackageId", (label, version), False)
        return d

    def isAvailable(self, pid, mirror):
        d = self.callRemote("isAvailable", pid, mirror)
        d.addErrback(self.onError, "getPackageId", (pid, mirror), False)
        return d

