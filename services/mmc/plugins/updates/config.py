# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

from mmc.support.config import PluginConfig
from pulse2.database.updates.config import UpdatesDatabaseConfig


class UpdatesConfig(PluginConfig, UpdatesDatabaseConfig):
    def __init__(self, name="updates", conffile=None):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile)
            UpdatesDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)
        # self.confOption = "option1"
        # ...

    def readConf(self):
        PluginConfig.readConf(self)
        UpdatesDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
        # ...

    def check(self):
        # if not self.confOption: raise ConfigException("Conf error")
        pass

    @staticmethod
    def activate():
        # Get module config from "/etc/mmc/plugins/updates.ini"
        UpdatesConfig("updates")
        return True
