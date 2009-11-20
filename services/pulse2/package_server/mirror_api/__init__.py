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
    Pulse2 PackageServer Mirror/Computer link API
"""

import twisted.web.xmlrpc
import twisted.web.server
import logging
import random
from pulse2.package_server.types import Mirror, Machine
from pulse2.package_server.assign_algo import MMAssignAlgoManager
from pulse2.package_server.xmlrpc import MyXmlrpc

class MirrorApi(MyXmlrpc):
    type = 'MirrorApi'
    def __init__(self, services = {}, name = '', assign_algo = 'default'):
        MyXmlrpc.__init__(self)
        self.name = name
        self.mirrors = {}
        self.url2mirrors = {}
        self.assign = {}
        self.logger = logging.getLogger()
        try:
            for service in services:
                if service['type'] == 'package_api_get' or service['type'] == 'package_api_put':
                    type = 'package_api'
                else:
                    type = service['type']

                if not self.url2mirrors.has_key(type):
                    self.url2mirrors[type] = {}
                if not self.mirrors.has_key(type):
                    self.mirrors[type] = []
                if service['server'] == '':
                    service['server'] = 'localhost'
                self.mirrors[type].append(Mirror(service['proto'], service['server'], service['port'], service['mp']))
                if service.has_key('url'):
                    self.url2mirrors[type][service['url']] = self.mirrors[type][-1]
            self.logger.debug("(%s) %s api machine/mirror server initialised"%(self.type, self.name))
        except Exception, e:
            self.logger.error("(%s)%s api machine/mirror server can't initialize correctly"%(self.type, self.name))
            raise e

        if self.mirrors.has_key('mirror'):
            mirrors = self.mirrors['mirror']
        else:
            mirrors = []
        if self.mirrors.has_key('package_api'):
            package_api = self.mirrors['package_api']
        else:
            package_api = []

        if self.url2mirrors.has_key('mirror'):
            url2mirrors = self.url2mirrors['mirror']
        else:
            url2mirrors = []
        if self.url2mirrors.has_key('package_api'):
            url2package_api = self.url2mirrors['package_api']
        else:
            url2package_api = []

        # TODO find a clean way to affect another class
        self.assign_algo = MMAssignAlgoManager().getAlgo(assign_algo)
        self.assign_algo.init(mirrors, mirrors, package_api, url2mirrors, url2mirrors, url2package_api)

    def xmlrpc_getServerDetails(self):
        ret = {}
        if self.mirrors.has_key('package_api'):
            ret['package_api'] = map(lambda x: x.toH(), self.mirrors['package_api'])
        if self.mirrors.has_key('mirror'):
            ret['mirror'] = map(lambda x: x.toH(), self.mirrors['mirror'])
        return ret

    def xmlrpc_getMirror(self, m):
        return self.assign_algo.getMachineMirror(m)

    def xmlrpc_getMirrors(self, machines):
        ret = []
        for m in machines:
            ret.append(self.assign_algo.getMachineMirror(m))
        return ret

    def xmlrpc_getFallbackMirror(self, m):
        return self.assign_algo.getMachineMirrorFallback(m)

    def xmlrpc_getFallbackMirrors(self, machines):
        ret = []
        for m in machines:
            ret.append(self.assign_algo.getMachineMirrorFallback(m))
        return ret

    def xmlrpc_getApiPackage(self, m):
        return self.assign_algo.getMachinePackageApi(m)

    def xmlrpc_getApiPackages(self, machines):
        ret = []
        for m in machines:
            ret.append(self.assign_algo.getMachinePackageApi(m))
        return ret

