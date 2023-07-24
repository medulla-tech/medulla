# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


from pulse2.apis.clients import Pulse2Api

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.


class Mirror(Pulse2Api):
    def __init__(self, *attr):
        self.name = "Mirror"
        Pulse2Api.__init__(self, *attr)

    def convertMachineIntoH(self, machine):
        if not isinstance(machine, dict):
            machine = {"uuid": machine}
        return machine

    def isAvailable(self, pid):
        """Is my package (identified by pid) available ?"""
        d = self.callRemote("isAvailable", pid)
        d.addErrback(self.onErrorRaise, "Mirror:isAvailable", pid)
        return d

    def getFileURI(self, fid):
        """convert from a fid (File ID) to a file URI"""
        d = self.callRemote("getFileURI", fid)
        d.addErrback(self.onErrorRaise, "Mirror:getFileURI", fid)
        return d

    def getFilesURI(self, fids):
        """convert from a list of fids (File ID) to a list of files URI"""
        d = self.callRemote("getFilesURI", fids)
        d.addErrback(self.onErrorRaise, "Mirror:getFilesURI", fids)
        return d
