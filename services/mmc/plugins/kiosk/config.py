# -*- coding: utf-8; -*-
#
# (c) 2018 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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


# file : mmc/plugins/kiosk/config.py

from mmc.support.config import PluginConfig
from pulse2.database.kiosk.config import KioskDatabaseConfig


class KioskConfig(PluginConfig,KioskDatabaseConfig):
    """ This class is called by the __init__ of the kiosk module. """
    def __init__(self, name = 'kiosk', conffile = None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            KioskDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        """
        Set good default for the module if a parameter is missing the
        configuration file.
        This function is called in the class constructor, so what you
        set here will be overwritten by the readConf method.
        """
        PluginConfig.setDefault(self)
        #self.confOption = "option1"
        # ...

    def readConf(self):
        """
        Read the configuration file using the ConfigParser API.
        The PluginConfig.readConf reads the "disable" option of the
        "main" section.
        """
        PluginConfig.readConf(self)
        KioskDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
        # ...

    def check(self):
        """
        Check the values set in the configuration file.
        Must be implemented by the subclass. ConfigException is raised
        with a corresponding error string if a check fails.
        """
        #if not self.confOption: raise ConfigException("Conf error")
        pass

    @staticmethod
    def activate():
        # Get module config from "/etc/mmc/plugins/kiosk.ini"
        KioskConfig("kiosk")
        return True
