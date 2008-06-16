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

import twisted.web.xmlrpc
import twisted.web.server
import logging
import random
from pulse2.package_server.types import Mirror, Machine

class MirrorApi(twisted.web.xmlrpc.XMLRPC):
    type = 'MirrorApi'
    def __init__(self, services = {}, name = ''):
        twisted.web.xmlrpc.XMLRPC.__init__(self)
        self.name = name
        self.mirrors = {}
        self.assign = {}
        self.logger = logging.getLogger()
        try:
            for service in services:
                if not self.mirrors.has_key(service['type']):
                    self.mirrors[service['type']] = []
                if service['server'] == '':
                    service['server'] = 'localhost'
                self.mirrors[service['type']].append(Mirror(service['proto'], service['server'], service['port'], service['mp']))
            self.logger.debug("(%s)%s api machine/mirror server initialised"%(self.type, self.name))
        except Exception, e:
            self.logger.error("(%s)%s api machine/mirror server can't initialize correctly"%(self.type, self.name))
            raise e

    def xmlrpc_getServerDetails(self):
        ret = {}
        if self.mirrors.has_key('package_api_get'):
            ret['package_api_get'] = map(lambda x: x.toH(), self.mirrors['package_api_get']) 
        if self.mirrors.has_key('package_api_put'):
            ret['package_api_put'] = map(lambda x: x.toH(), self.mirrors['package_api_put']) 
        if self.mirrors.has_key('mirror'):
            ret['mirror'] = map(lambda x: x.toH(), self.mirrors['mirror']) 
        return ret

    def xmlrpc_getMirror(self, m):
        machine = Machine().from_h(m)
        if not self.assign.has_key(machine.uuid):
            self.assign[machine.uuid] = {}
        if not self.assign[machine.uuid].has_key('getMirror'):
            self.assign[machine.uuid]['getMirror'] = self.mirrors['mirror'][random.randint(0,len(self.mirrors['mirror'])-1)].toH()
        return self.assign[machine.uuid]['getMirror']
        
    def xmlrpc_getMirrors(self, machines):
        machines = map(lambda m: Machine().from_h(m), machines)
        ret = []
        for machine in machines:
            if not self.assign.has_key(machine.uuid):
                self.assign[machine.uuid] = {}
            if not self.assign[machine.uuid].has_key('getMirror'):
                self.assign[machine.uuid]['getMirror'] = self.mirrors['mirror'][random.randint(0,len(self.mirrors['mirror'])-1)].toH()
            ret.append(self.assign[machine.uuid]['getMirror'])
        return ret
        
    def xmlrpc_getFallbackMirror(self, m):
        machine = Machine().from_h(m)
        if not self.assign.has_key(machine.uuid):
            self.assign[machine.uuid] = {}
        if not self.assign[machine.uuid].has_key('getFallbackMirror'):
            self.assign[machine.uuid]['getFallbackMirror'] = self.mirrors['mirror'][random.randint(0,len(self.mirrors['mirror'])-1)].toH()
        return self.assign[machine.uuid]['getFallbackMirror']
        
    def xmlrpc_getFallbackMirrors(self, machines):
        machines = map(lambda m: Machine().from_h(m), machines)
        ret = []
        for machine in machines:
            if not self.assign.has_key(machine.uuid):
                self.assign[machine.uuid] = {}
            if not self.assign[machine.uuid].has_key('getFallbackMirror'):
                self.assign[machine.uuid]['getFallbackMirror'] = self.mirrors['mirror'][random.randint(0,len(self.mirrors['mirror'])-1)].toH()
            ret.append(self.assign[machine.uuid]['getFallbackMirror'])
        return ret

    def xmlrpc_getApiPackage(self, m):
        machine = Machine().from_h(m)
        ret = []
        if self.mirrors.has_key('package_api_get'):
            ret += map(lambda papi: papi.toH(), self.mirrors['package_api_get'])
        if self.mirrors.has_key('package_api_put'):
            ret += map(lambda papi: papi.toH(), self.mirrors['package_api_put'])
        return ret
        
    def xmlrpc_getApiPackages(self, machines):
        machines = map(lambda m: Machine().from_h(m), machines)
        ret = []
        for machine in machines:
            ret1 = []
            if self.mirrors.has_key('package_api_get'):
                ret1 += map(lambda papi: papi.toH(), self.mirrors['package_api_get'])
            if self.mirrors.has_key('package_api_put'):
                ret1 += map(lambda papi: papi.toH(), self.mirrors['package_api_put'])
            ret.append(ret1)
        return ret

