# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id: mirror_api.py 689 2009-02-06 15:18:43Z oroussy $
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

import logging

import mmc.plugins.msc
import pulse2.apis.clients.mirror

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.
class Mirror(pulse2.apis.clients.mirror_api.Mirror):
    def __init__(self, url = None):
        self.logger = logging.getLogger()
        credit = ''
        if url:
            self.server_addr = url
            # TODO check if that's a possibility... credit will always be empty...
            pulse2.apis.clients.mirror_api.Mirror.__init__(self, credit, url)
        else:
            self.config = mmc.plugins.msc.MscConfig()

            if self.config.ma_enablessl:
                self.server_addr = 'https://'
            else:
                self.server_addr = 'http://'

            if self.config.ma_username != '':
                self.server_addr += self.config.ma_username
                credit = self.config.ma_username
                if self.config.ma_password != '':
                    self.server_addr += ":"+self.config.ma_password
                    credit += ":"+self.config.ma_password
                self.server_addr += "@"

            self.server_addr += self.config.ma_server+':'+str(self.config.ma_port) + self.config.ma_mountpoint

            if self.config.ma_verifypeer:
                pulse2.apis.clients.mirror_api.Mirror.__init__(self, credit, self.server_addr, self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert)
            else:
                pulse2.apis.clients.mirror_api.Mirror.__init__(self, credit, self.server_addr)

