import logging
from mmc.support.config import PluginConfig
from ConfigParser import NoOptionError

class DGConfig(PluginConfig):
    dyngroup_activate = True
    defaultModule = ''
    
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
        self.disable = self.getboolean("main", "disable")
        self.dynamicEnable = self.getboolean("main", "dynamic_enable")
        if self.has_option('main', 'default_module'):
            self.defaultModule = self.get('main', 'default_module')
        try:
            self.dbport = self.getint("database", "dbport")
        except NoOptionError:
            # We will use the default db driver port
            self.dbport = None
        if self.has_option("database", "dbpoolrecycle"):
            self.dbpoolrecycle = self.getint("database", "dbpoolrecycle")

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

        if self.has_section("querymanager"):
            if self.has_option("querymanager", "activate"):
                self.dyngroup_activate = self.getboolean("querymanager", "activate")

    def setDefault(self):
        """
        Set default values
        """
        PluginConfig.setDefault(self)
        self.dbsslenable = False
        self.dbpoolrecycle = 60

