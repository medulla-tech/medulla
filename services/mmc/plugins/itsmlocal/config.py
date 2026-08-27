# file : services/mmc/plugins/itsmlocal/config.py

"""Configuration for the itsmlocal MMC backend plugin."""

from mmc.plugins.base import PluginConfig
from pulse2.database.itsmlocal.config import ItsmlocalDatabaseConfig


class ItsmlocalConfig(PluginConfig, ItsmlocalDatabaseConfig):
    """Load itsmlocal settings from itsmlocal.ini and its local override."""

    def __init__(self, name="itsmlocal", conffile=None):
        PluginConfig.__init__(self, name, conffile)
        ItsmlocalDatabaseConfig.__init__(self)

    def readConf(self):
        """Read plugin and database settings."""
        PluginConfig.readConf(self)
        ItsmlocalDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable", fallback=True)
        self.tempdir = self.get("main", "tempdir", fallback="/tmp/mmc-itsmlocal")
