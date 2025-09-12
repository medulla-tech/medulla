# -*- coding: utf-8; -*-
from mmc.support.config import PluginConfig
from pulse2.database.security.config import SecurityDatabaseConfig

class SecurityConfig(PluginConfig, SecurityDatabaseConfig):
    def __init__(self, name='security', conffile=None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            SecurityDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)

    def readConf(self):
        PluginConfig.readConf(self)
        SecurityDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")

    def check(self):
        pass

    @staticmethod
    def activate():
        SecurityConfig("security")
        return True
