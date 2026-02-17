# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.support.config import PluginConfig
from pulse2.database.urbackup.config import UrbackupDatabaseConfig


class UrbackupConfig(PluginConfig, UrbackupDatabaseConfig):
    def __init__(self, name="urbackup", conffile=None, backend="database"):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table="urbackup_conf")
            UrbackupDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)

    def readConf(self):
        """
        Read the configuration for urbackup from  the configuration files.
        The configuration file is stored in /etc/mmc/plugins/urbackup.ini
        """
        PluginConfig.readConf(self)
        if self.backend == "database":
            self._load_db_settings_from_backend()
        elif self.conffile and self.backend == "ini":
            UrbackupDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
        # ...
        self.urbackup_url = self.get("urbackup", "url")
        self.urbackup_username = self.get("urbackup", "username")
        self.urbackup_password = self.get("urbackup", "password")

    def check(self):
        """
        Does nothing yet
        IMPLEMENT ME
        """
        pass

    @staticmethod
    def activate():
        """
        It looks in the configuration file /etc/mmc/plugins/urbackup.ini
        If disable is set to 0 the plugin is enabled.
        """
        # Get module config from "/etc/mmc/plugins/urbackup.ini"
        UrbackupConfig("urbackup", None, "database")
        return True
