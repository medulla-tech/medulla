# -*- coding: utf-8; -*-
from mmc.support.config import PluginConfig
from pulse2.database.mobile.config import MobileDatabaseConfig

class MobileConfig(PluginConfig, MobileDatabaseConfig):
    def __init__(self, name='mobile', conffile=None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            MobileDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)

    def readConf(self):
        PluginConfig.readConf(self)
        MobileDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")

    def check(self):
        pass

    @staticmethod
    def activate():
        MobileConfig("mobile")
        return True
