#!/usr/bin/python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
    Pulse2 PackageServer
"""

import random
from pulse2.package_server.types import Machine, User
from pulse2.package_server.assign_algo import MMAssignAlgo, UPAssignAlgo

class MMUserAssignAlgo(MMAssignAlgo):
    name = 'default'
    assign = {}
    def getMachineMirror(self, m):
        machine = Machine().from_h(m)
        if not machine.uuid in self.assign:
            self.assign[machine.uuid] = {}
        #if not 'getMirror' in self.assign[machine.uuid]:
        if not self.assign[machine.uuid].has_key('getMirror'):
            self.assign[machine.uuid]['getMirror'] = self.mirrors[random.randint(0,len(self.mirrors)-1)].toH()
        return self.assign[machine.uuid]['getMirror']

    def getMachineMirrorFallback(self, m):
        machine = Machine().from_h(m)
        #if not machine.uuid in self.assign:
        if not self.assign.has_key(machine.uuid):
            self.assign[machine.uuid] = {}
        #if not 'getFallbackMirror' in self.assign[machine.uuid]:
        if not self.assign[machine.uuid].has_key('getFallbackMirror'):
            self.assign[machine.uuid]['getFallbackMirror'] = self.mirrors_fallback[random.randint(0,len(self.mirrors_fallback)-1)].toH()
        return self.assign[machine.uuid]['getFallbackMirror']

    def getMachinePackageApi(self, m):
        ret = []
        ret += map(lambda papi: papi.toH(), self.package_apis)
        return ret


class UPUserAssignAlgo(UPAssignAlgo):
    name = 'default'
    assign = {}

    def getUserPackageApi(self, u):
        user = User().from_h(u)
        #if not user.uuid in self.assign:
        if not self.assign.has_key(user.uuid):
            if self.package_api_put != None:
                self.assign[user.uuid] = self.package_api_put
            else:
                self.assign[user.uuid] = []
#            {
#                'READ'=>@mirrors['package_api_put'],
#                'WRITE'=>@mirrors['package_api_put'],
#                'DEL'=>@mirrors['package_api_put']
#            }
        return self.assign[user.uuid]
