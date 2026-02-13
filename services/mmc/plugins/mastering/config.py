# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

# file : mmc/plugins/mastering/config.py

from mmc.support.config import PluginConfig
from pulse2.database.mastering.config import MasteringDatabaseConfig

class MasteringConfig(PluginConfig,MasteringDatabaseConfig):
    def __init__(self, name = 'mastering', conffile = None, backend = "database"):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile, backend = backend, db_table = "mastering_conf")
            MasteringDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)
        #self.confOption = "option1"
        # ...

    def readConf(self):
        PluginConfig.readConf(self)
        if self.backend == "database":
            self._load_db_settings_from_backend()
        elif self.backend == "ini" and self.conffile:
            MasteringDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
        
        self.master_path = ""
        if self.has_option("master", "path"):
            self.master_path = self.get("master", "path")

        # ...

    def check(self):
        #if not self.confOption: raise ConfigException("Conf error")
        pass

    @staticmethod
    def activate():
        # Get module config from "/etc/mmc/plugins/mastering.ini"
        MasteringConfig("mastering", None, "database")
        return True


