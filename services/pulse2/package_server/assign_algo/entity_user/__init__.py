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
from pulse2.package_server.types import Mirror, Machine, User
from pulse2.package_server.assign_algo import MMAssignAlgo, UPAssignAlgo
from pulse2.package_server.assign_algo.entity_user.config import PluginInventoryUPAAConfig
from pulse2.package_server.assign_algo.entity_user.database import PluginInventoryUPAADatabase

class UPUserAssignAlgo(UPAssignAlgo):
    name = 'entity_user'
    assign = {}

    def init(self):
        UPAssignAlgo.init(self)
        self.config = PluginInventoryUPAAConfig()
        self.config.setup("/etc/mmc/pulse2/pserver/plugin_entity_user.ini")
        self.database = PluginInventoryUPAADatabase()
        self.database.activate(self.config)


    def getUserPackageApi(self, u):
        user = User().from_h(u)
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

