import logging
from mmc.support.config import PluginConfig
from ConfigParser import NoOptionError

class DGConfig(PluginConfig):
    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)
        self.dbdriver = self.get("database", "dbdriver")
        self.dbuser = self.get("database", "dbuser")
        self.dbpasswd = self.get("database", "dbpasswd")
        self.dbhost = self.get("database", "dbhost")
        self.dbname = self.get("database", "dbname")
        self.disable = self.get("main", "disable")
        self.dynamicEnable = (str(self.get("main", "dynamic_enable")) == '1')
        try:
            self.dbport = self.getint("database", "dbport")
        except NoOptionError:
            # We will use the default db driver port
            self.dbport = None

        try:
            self.dbdebug = logging._levelNames[self.get("msc", "dbdebug")]
        except:
            self.dbdebug = logging.DEBUG


    def setDefault(self):
        """
        Set default values
        """
        PluginConfig.setDefault(self)


