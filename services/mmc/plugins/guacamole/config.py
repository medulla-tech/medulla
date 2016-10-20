# -*- coding: utf-8 -*-

from mmc.support.config import PluginConfig


class guacamoleConfig(PluginConfig):

    def __init__(self, name = 'guacamole', conffile = None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            self.initdone = True

    def setDefault(self):
        """
        Set good default for the module if a parameter is missing the
        configuration file.
        This function is called in the class constructor, so what you
        set here will be overwritten by the readConf method.
        """
        PluginConfig.setDefault(self)


    def readConf(self):
        """
        Read the configuration file using the ConfigParser API.
        The PluginConfig.readConf reads the "disable" option of the
        "main" section.
        """
        PluginConfig.readConf(self)
        self.disable = self.getboolean("main", "disable")

    def check(self):
        """
        Check the values set in the configuration file.
        Must be implemented by the subclass. ConfigException is raised
        with a corresponding error string if a check fails.
        """
        #if not self.confOption: raise ConfigException("Conf error")
        pass

    def activate():
        # Get module config from "/etc/mmc/plugins/module_name.ini"
        guacamoleConfig("guacamole")
        return True
