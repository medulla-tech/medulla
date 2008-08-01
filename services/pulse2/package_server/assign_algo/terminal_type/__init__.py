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
    Pulse2 PackageServer
"""

import random
from pulse2.package_server.types import Mirror, Machine
from pulse2.package_server.mirror_api.assign_algo import AssignAlgo
from pulse2.package_server.assign_algo.terminal_type.database import PluginInventoryAADatabase
from pulse2.package_server.assign_algo.terminal_type.config import PluginInventoryAAConfig

class UserAssignAlgo(AssignAlgo):
    name = 'terminal_type'
    assign = {}

    def __init__(self):
        AssignAlgo.__init__(self)
        self.config = PluginInventoryAAConfig()
        self.config.setup("/etc/mmc/pulse2/pserver/plugin_terminal_type.ini")
        self.database = PluginInventoryAADatabase()
        self.database.activate(self.config)
        
    def __getMachineType(self, m):
        return self.database.getMachineType(m['uuid'])
    
    def getMachineMirror(self, m):
        if not self.assign.has_key(m['uuid']):
            self.assign[m['uuid']] = {}
        if not self.assign[m['uuid']].has_key('getMirror'):
            type = self.__getMachineType(m)
            self.assign[m['uuid']]['getMirror'] = []
            for u in self.config.type2url[type]['mirror']:
                self.assign[m['uuid']]['getMirror'].append(self.url2mirrors[u])
        return self.assign[m['uuid']]['getMirror']
        
    def getMachineMirrorFallback(self, m):
        if not self.assign.has_key(m['uuid']):
            self.assign[m['uuid']] = {}
        if not self.assign[m['uuid']].has_key('getFallbackMirror'):
            type = self.__getMachineType(m)
            self.assign[m['uuid']]['getFallbackMirror'] = []
            for u in self.config.type2url[type]['mirror']:
                self.assign[m['uuid']]['getFallbackMirror'].append(self.url2mirrors_fallback[u])
        return self.assign[m['uuid']]['getFallbackMirror']

    def getMachinePackageApi(self, m):
        if not self.assign.has_key(m['uuid']):
            self.assign[m['uuid']] = {}
        if not self.assign[m['uuid']].has_key('getMachinePackageApi'):
            type = self.__getMachineType(m)
            self.assign[m['uuid']]['getMachinePackageApi'] = []
            for u in self.config.type2url[type]['package_api']:
                self.assign[m['uuid']]['getMachinePackageApi'].append(self.url2package_apis[u])
        return self.assign[m['uuid']]['getMachinePackageApi']

