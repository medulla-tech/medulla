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

"""
This module defined the scheduler API
It provides methods to know which scheduler to contact for a computer.
"""
import logging
from mmc.plugins.msc.config import MscConfig
from mmc.support.mmctools import Singleton
import pulse2.apis.clients.scheduler_api

class SchedulerApi(Singleton):
    initialized = False
    def __init__(self):
        if self.initialized: return
        self.logger = logging.getLogger()
        self.logger.debug("Going to initialize SchedulerApi")
        self.config = MscConfig()
        credentials = ''

        if self.config.sa_enable:
            if self.config.sa_enablessl:
                self.server_addr = 'https://'
            else:
                self.server_addr = 'http://'

            if self.config.sa_username != '':
                self.server_addr += self.config.sa_username
                credentials = self.config.sa_username
                if self.config.sa_password != '':
                    self.server_addr += ":"+self.config.sa_password
                    credentials += ":"+self.config.sa_password
                self.server_addr += "@"

            self.server_addr += self.config.sa_server+':'+str(self.config.sa_port) + self.config.sa_mountpoint
            self.logger.debug('SchedulerApi will connect to %s' % (self.server_addr))

            if self.config.sa_verifypeer:
                self.internal = pulse2.apis.clients.scheduler_api.SchedulerApi(MscConfig().default_scheduler, credentials, self.server_addr, self.config.sa_verifypeer, self.config.sa_cacert, self.config.sa_localcert)
            else:
                self.internal = pulse2.apis.clients.scheduler_api.SchedulerApi(MscConfig().default_scheduler, credentials, self.server_addr)
                
        for method in ('getScheduler', 'getSchedulers', 'getDefaultScheduler'):
            setattr(self, method, getattr(self.internal, method))

        self.internal.setConfig(self.config)
        self.initialized = True
 
