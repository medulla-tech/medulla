# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.support.config import PluginConfig
from medulla.database.backuppc.config import BackuppcDatabaseConfig


class BackuppcConfig(PluginConfig, BackuppcDatabaseConfig):
    def __init__(self, name="backuppc", conffile=None):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile)
            BackuppcDatabaseConfig.__init__(self)
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
        BackuppcDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
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
        # Get module config from "/etc/mmc/plugins/module_name.ini"
        BackuppcConfig("backuppc")
        return True
