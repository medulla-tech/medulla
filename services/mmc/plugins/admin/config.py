# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

from mmc.support.config import PluginConfig
from pulse2.database.admin.config import AdminDatabaseConfig


class AdminConfig(PluginConfig, AdminDatabaseConfig):
    def __init__(self, name="admin", conffile=None):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile)
            AdminDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)
        # self.confOption = "option1"
        # ...

    def readConf(self):
        PluginConfig.readConf(self)
        AdminDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
        # ...

    def check(self):
        # if not self.confOption: raise ConfigException("Conf error")
        pass

    @staticmethod
    def activate():
        # Get module config from "/etc/mmc/plugins/admin.ini"
        AdminConfig("admin")
        return True
