from mmc.support.config import PluginConfig, ConfigException
from pulse2.database.monitoring.config import MonitoringDatabaseConfig

class MonitoringConfig(PluginConfig, MonitoringDatabaseConfig):

    def __init__(self, name = 'monitoring', conffile = None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
	    MonitoringDatabaseConfig.__init__(self)
            self.initdone = True


    def setDefault(self):
        """
        Set good default for the module if a parameter is missing the
        configuration file.
        This function is called in the class constructor, so what you
        set here will be overwritten by the readConf method.
        """
        PluginConfig.setDefault(self)
        #self.confOption = "option1"
        # ...

    def readConf(self):
        """
        Read the configuration file using the ConfigParser API.
        The PluginConfig.readConf reads the "disable" option of the
        "main" section.
        """
        PluginConfig.readConf(self)
	MonitoringDatabaseConfig.setup(self, self.conffile)

        try:
            self.monitoring_uri = self.get("webservices", "monitoring_url")
        except:
            self.monitoring_uri = "" # http://localhost/zabbix/api_jsonrpc.php

        try:
            self.monitoring_username = self.get("webservices", "monitoring_username")
        except:
            self.monitoring_username = "" # Admin

        try:
            self.monitoring_password = self.get("webservices", "monitoring_password")
        except:
            self.monitoring_password = "" # zabbix



        #self.confOption = self.get("sectionname", "optionname")
        # ...

    def check(self):
        """
        Check the values set in the configuration file.
        Must be implemented by the subclass. ConfigException is raised
        with a corresponding error string if a check fails.
        """
        if not self.confOption: raise ConfigException("Conf error")

    def activate():
        # Get module config from "/etc/mmc/plugins/module_name.ini"
        MonitoringConfig("monitoring")
        
        return True
