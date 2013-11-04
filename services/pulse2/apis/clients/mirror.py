# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id: mirror_api.py 689 2009-02-06 15:18:43Z oroussy $
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

from pulse2.apis.clients import Pulse2Api

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.
class Mirror(Pulse2Api):

    errorback = None

    def __init__(self, base_mirror, fb_mirror=None):
        self.name = "Mirror"
        credentials, mirror = self.extractCredentials(base_mirror)
        if fb_mirror :
            Pulse2Api.__init__(self, credentials, fb_mirror)
        else :
            Pulse2Api.__init__(self, credentials, mirror)


    def extractCredentials(self, mirror):
        if not '@' in mirror:
            return ('', mirror)
        mirror = mirror.replace('http://', '')
        credentials, mirror = mirror.split("@")
        return (credentials, 'http://%s'%mirror)

    def convertMachineIntoH(self, machine):
        if type(machine) != dict:
            machine = {'uuid':machine}
        return machine

    def isAvailable(self, pid):
        """ Is my package (identified by pid) available ? """
        d = self.callRemote("isAvailable", pid)
        if self.errorback :
            d.addErrback(self.errorback)
        else :
            d.addErrback(self.onErrorRaise, "Mirror:isAvailable", pid)
        return d

    def getFileURI(self, fid):
        """ convert from a fid (File ID) to a file URI """
        d = self.callRemote("getFileURI", fid)
        if self.errorback :
            d.addErrback(self.errorback)
        else :
            d.addErrback(self.onErrorRaise, "Mirror:getFileURI", fid)
        return d

    def getFilesURI(self, fids):
        """ convert from a list of fids (File ID) to a list of files URI """
        d = self.callRemote("getFilesURI", fids)
        if self.errorback :
            d.addErrback(self.errorback)
        else :
            d.addErrback(self.onErrorRaise, "Mirror:getFilesURI", fids)
        return d
