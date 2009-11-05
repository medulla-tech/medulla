#
# (c) 2008 Mandriva, http://www.mandriva.com/
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

import logging
import mmc.plugins.pkgs.config
from mmc.support.mmctools import Singleton
import pulse2.apis.clients.user_packageapi_api

class UserPackageApiApi(Singleton):
    initialized = False
    def __init__(self):
        if self.initialized: return
        self.logger = logging.getLogger()
        self.logger.debug("Going to initialize UserPackageApiApi")
        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")
        credits = ''

        if self.config.upaa_enablessl:
            self.server_addr = 'https://'
        else:
            self.server_addr = 'http://'

        if self.config.upaa_username != '':
            self.server_addr += self.config.upaa_username
            credits += self.config.upaa_username
            if self.config.upaa_password != '':
                self.server_addr += ":"+self.config.upaa_password
                credits += ":"+self.config.upaa_password
            self.server_addr += "@"

        self.server_addr += self.config.upaa_server+':'+str(self.config.upaa_port) + self.config.upaa_mountpoint
        self.logger.debug('UserPackageApiApi will connect to %s' % (self.server_addr))

        if self.config.upaa_verifypeer:
            self.internal = pulse2.apis.clients.user_packageapi_api.UserPackageApiApi(credits, self.server_addr, self.config.upaa_verifypeer, self.config.upaa_cacert, self.config.upaa_localcert)
        else:
            self.internal = pulse2.apis.clients.user_packageapi_api.UserPackageApiApi(credits, self.server_addr)

        for method in ('getUserPackageApi', ):
            setattr(self, method, getattr(self.internal, method))
                    
        self.initialized = True

