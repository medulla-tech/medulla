# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

from ConfigParser import NoOptionError, NoSectionError

from mmc.support.config import PluginConfig
from mmc.database.config import DatabaseConfig


class updateConfig(PluginConfig, DatabaseConfig):

    def __init__(self, name='update', conffile=None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            DatabaseConfig.__init__(self)
            self.initdone = True

    def readConf(self):
        PluginConfig.readConf(self)
        DatabaseConfig.setup(self, self.conffile)
        try:
            self.update_commands_cron = self.get(
                'main', 'update_commands_cron')
        except (NoOptionError, NoSectionError):
            self.update_commands_cron = '10 12 * * *'
        try:
            self.enable_update_commands = int(
                self.get('main', 'enable_update_commands'))
        except:
            self.enable_update_commands = 1
