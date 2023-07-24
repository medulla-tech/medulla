# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.apis.clients import Pulse2Api

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.


class MirrorApi(Pulse2Api):
    def __init__(self, *attr):
        self.name = "MirrorApi"
        Pulse2Api.__init__(self, *attr)

    def getMirror(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.callRemote("getMirror", machine)
        d.addErrback(self.onError, "MirrorApi:getMirror", machine)
        return d

    def getMirrors(self, machines):
        if self.initialized_failed:
            return []
        machines = [self.convertMachineIntoH(m) for m in machines]
        d = self.callRemote("getMirrors", machines)
        d.addErrback(self.onError, "MirrorApi:getMirrors", machines)
        return d

    def getFallbackMirror(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.callRemote("getFallbackMirror", machine)
        d.addErrback(self.onError, "MirrorApi:getFallbackMirror", machine)
        return d

    def getFallbackMirrors(self, machines):
        if self.initialized_failed:
            return []
        machines = [self.convertMachineIntoH(m) for m in machines]
        d = self.callRemote("getFallbackMirrors", machines)
        d.addErrback(self.onError, "MirrorApi:getFallbackMirrors", machines)
        return d

    def getApiPackage(self, machine):
        self.logger.debug(machine)
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.callRemote("getApiPackage", machine)
        d.addErrback(self.onError, "MirrorApi:getApiPackage", machine)
        return d

    def getApiPackages(self, machines):
        if self.initialized_failed:
            return []
        machines = [self.convertMachineIntoH(m) for m in machines]
        d = self.callRemote("getApiPackages", machines)
        d.addErrback(self.onError, "MirrorApi:getApiPackages", machines)
        return d

    def convertMachineIntoH(self, machine):
        if not isinstance(machine, dict):
            machine = {"uuid": machine}
        return machine
