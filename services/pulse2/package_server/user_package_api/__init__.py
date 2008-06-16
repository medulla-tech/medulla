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
from pulse2.package_server.types import Mirror, Machine, User

class UserPackageApi(twisted.web.xmlrpc.XMLRPC):
    type = 'UserPackageApi'
    def __init__(self, services = {}, name = ''):
        twisted.web.xmlrpc.XMLRPC.__init__(self)
        self.logger = logging.getLogger()
        self.name = name
        self.mirrors = {}
        self.assign = {}

        try:
            for service in services:
                if not self.mirrors.has_key(service['type']):
                    self.mirrors[service['type']] = []
                if service['server'] == '':
                    service['server'] = 'localhost'
                self.mirrors[service['type']].append(Mirror(service['proto'], service['server'], service['port'], service['mp']))
            self.logger.debug("(%s) %s api user/packageApi server initialised"%(self.type, self.name))
        except Exception, e:
            self.logger.error("(%s) %s api user/packageApi server can't initialize correctly"%(self.type, self.name))
            raise e

    def xmlrpc_getServerDetails(self):
        ret = []
        if self.mirrors.has_key('package_api_put'):
            ret = map(lambda m: m.toH(), self.mirrors['package_api_put'])
        return ret

    def xmlrpc_getUserPackageApi(self, u):
        user = User().from_h(u)
        if not self.assign.has_key(user.uuid):
            self.assign[user.uuid] = map(lambda x: x.toH(), self.mirrors['package_api_put'])
#            {
#                'READ'=>@mirrors['package_api_put'],
#                'WRITE'=>@mirrors['package_api_put'],
#                'DEL'=>@mirrors['package_api_put']
#            }
        return self.assign[user.uuid]


