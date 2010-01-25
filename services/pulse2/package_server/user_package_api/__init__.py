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
    Pulse2 PackageServer
"""

import twisted.web.xmlrpc
import logging
from pulse2.package_server.types import User, Mirror
from pulse2.package_server.assign_algo import UPAssignAlgoManager
from pulse2.package_server.xmlrpc import MyXmlrpc


class UserPackageApi(MyXmlrpc):
    type = 'UserPackageApi'
    def __init__(self, services = {}, name = '', assign_algo = 'default'):
        MyXmlrpc.__init__(self)
        self.logger = logging.getLogger()
        self.name = name
        package_api_put = []

        try:
            for service in services:
                if service['type'] == 'package_api_put':
                    if service['server'] == '':
                        service['server'] = 'localhost'
                    package_api_put.append(Mirror(service['proto'], service['server'], service['port'], service['mp']))
            self.logger.debug("(%s) %s api user/packageApi server initialised"%(self.type, self.name))
        except Exception, e:
            self.logger.error("(%s) %s api user/packageApi server can't initialize correctly"%(self.type, self.name))
            raise e

        self.assign_algo = UPAssignAlgoManager().getAlgo(assign_algo)
        self.assign_algo.init(package_api_put)

    def xmlrpc_getServerDetails(self):
        return map(lambda m: m.toH(), self.package_api_put)

    def xmlrpc_getUserPackageApi(self, u):
        return self.assign_algo.getUserPackageApi(u)

