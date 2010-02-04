# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Module to connect to the Mirror API XMLRPC API.
This api provides methods to know which package or mirror API to connect 
to know package you can install on a computer.
"""

import logging
import mmc.plugins.msc
import pulse2.apis.clients.mirror_api
from mmc.support.mmctools import Singleton

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.
class MirrorApi(Singleton):
    initialized = False
    def __init__(self):
        if self.initialized: return
        self.logger = logging.getLogger()
        self.logger.debug("Going to initialize MirrorApi")
        self.config = mmc.plugins.msc.MscConfig()
        credentials = ''

        if self.config.ma_enablessl:
            self.server_addr = 'https://'
        else:
            self.server_addr = 'http://'

        if self.config.ma_username != '':
            self.server_addr += self.config.ma_username
            credentials = self.config.ma_username
            if self.config.ma_password != '':
                self.server_addr += ":"+self.config.ma_password
                credentials += ":"+self.config.ma_password
            self.server_addr += "@"

        self.server_addr += self.config.ma_server+':'+str(self.config.ma_port) + self.config.ma_mountpoint

        if self.config.ma_verifypeer:
            self.internal = pulse2.apis.clients.mirror_api.MirrorApi(credentials, self.server_addr, self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert)
        else:
            self.internal = pulse2.apis.clients.mirror_api.MirrorApi(credentials, self.server_addr)
        
        for method in ('getMirror', 'getMirrors', 'getFallbackMirror', 'getFallbackMirrors', 'getApiPackage', 'getApiPackages', ):
            setattr(self, method, getattr(self.internal, method))

        self.initialized = True
 
