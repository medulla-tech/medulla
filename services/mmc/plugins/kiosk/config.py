# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later
from mmc.support.config import PluginConfig
from pulse2.database.kiosk.config import KioskDatabaseConfig


class KioskConfig(PluginConfig, KioskDatabaseConfig):
    """This class is called by the __init__ of the kiosk module."""

    def __init__(self, name="kiosk", conffile=None):
        if not hasattr(self, "initdone"):
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
        # self.confOption = "option1"
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
        self.use_external_ldap = False
        if self.has_option("provider", "use_external_ldap"):
            self.use_external_ldap = self.getboolean("provider", "use_external_ldap")
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
        # Get module config from "/etc/mmc/plugins/kiosk.ini"
        KioskConfig("kiosk")
        return True
