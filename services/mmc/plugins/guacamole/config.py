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
        #self.disable = self.getboolean("main", "disable")
        #self.tempdir = self.get("main", "tempdir")

        #self.Port= self.get('connection', 'port')
        #self.Server= self.get('connection', 'server')
        #self.passwordconnection=self.get('connection', 'password')

        ##########salon############

        #self.jidsalonmaster="master@%s"%self.get('salon', 'server')
        #self.jidsalonlog="log@%s"%self.get('salon', 'server')
        #self.jidsaloncommand="command@%s"%self.get('salon', 'server')
        #self.passwordconnexionmuc=self.get('salon', 'password')
        #########chat#############
        ## le jidagent doit être la plus petite valeur de la liste des macs.
        #self.chatserver=self.get('chat', 'server')
        ## plus petite mac adress
        #self.jidagent="%s@%s/%s"%(utils.name_jid(),self.get('chat', 'server'),platform.node())
        #self.jidagentsiveo = "%s@%s"%(self.get('global', 'ordre'),self.get('chat', 'server'))
        #self.ordreallagent = self.getboolean('global', 'inter_agent')
        #self.showinfomaster = self.getboolean('master', 'showinfo')
        #self.showplugins = self.getboolean('master', 'showplugins')

        ##self.inventory = self.get('inventorypulse', 'inventory')

        #self.jidagent="%s@%s/%s"%("master",self.chatserver,"MASTER")
        #self.NickName="MASTER"

        #self.dirplugins = self.get('plugins', 'dirplugins')
        #self.information={}
        #self.PlateformSystem=platform.platform()
        #self.information['plateform']=self.PlateformSystem
        #self.OperatingSystem=platform.system()
        #self.information['os']=self.OperatingSystem
        #self.UnameSystem = platform.uname()
        #self.information['uname']=self.UnameSystem
        #self.HostNameSystem =platform.node()
        #self.information['hostname']=self.HostNameSystem
        #self.OsReleaseNumber=platform.release()
        #self.information['osrelease']=self.OsReleaseNumber
        #self.DetailedVersion=platform.version()
        #self.information['version']=self.DetailedVersion
        #self.HardwareType=platform.machine()
        #self.information['hardtype']=self.HardwareType
        #self.ProcessorIdentifier=platform.processor()
        #self.information['processor']=self.ProcessorIdentifier
        #self.Architecture=platform.architecture()
        #self.information['archi']=self.Architecture

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
