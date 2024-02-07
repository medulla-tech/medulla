# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# file mmc/plugins/greenit/config.py

from mmc.support.config import PluginConfig
from pulse2.database.greenit.config import GreenitDatabaseConfig


class GreenitConfig(PluginConfig, GreenitDatabaseConfig):
    """This class is called by the __init__ of the Greenit module."""

    def __init__(self, name="greenit", conffile=None):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile)
            GreenitDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        """
        Set good default for the module if a parameter is missing the
        configuration file.
        This function is called in the class constructor, so what you
        set here will be overwritten by the readConf method.
        """
        PluginConfig.setDefault(self)
        # self.confOption = "option1"
        # ...

    def readConf(self):
        """
        Read the configuration file using the ConfigParser API.
        The PluginConfig.readConf reads the "disable" option of the
        "main" section.
        """
        PluginConfig.readConf(self)
        GreenitDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        # ...


    def check(self):
        """
        Check the values set in the configuration file.
        Must be implemented by the subclass. ConfigException is raised
        with a corresponding error string if a check fails.
        """
        # if not self.confOption: raise ConfigException("Conf error")
        pass

    @staticmethod
    def activate():
        # Get module config from "/etc/mmc/plugins/greenit.ini"
        GreenitConfig("greenit")

        if config.disable:
            logger.warning("Plugin greenit: disabled by configuration.")
            return False

        return True
