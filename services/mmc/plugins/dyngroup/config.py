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
        self.dbpasswd = self.getpassword("database", "dbpasswd")
        self.dbhost = self.get("database", "dbhost")
        self.dbname = self.get("database", "dbname")
        self.disable = self.get("main", "disable")
        self.dynamicEnable = self.getboolean("main", "dynamic_enable")
        try:
            self.dbport = self.getint("database", "dbport")
        except NoOptionError:
            # We will use the default db driver port
            self.dbport = None

        if self.has_option("database", "dbsslenable"):
            self.dbsslenable = self.getboolean("database", "dbsslenable")
            if self.dbsslenable:
                self.dbsslca = self.get("database", "dbsslca")
                self.dbsslcert = self.get("database", "dbsslcert")
                self.dbsslkey = self.get("database", "dbsslkey")

        try:
            self.dbdebug = logging._levelNames[self.get("database", "dbdebug")]
        except:
            self.dbdebug = logging.ERROR

    def setDefault(self):
        """
        Set default values
        """
        PluginConfig.setDefault(self)
        self.dbsslenable = False


