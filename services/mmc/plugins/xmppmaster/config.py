# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from mmc.support.config import PluginConfig #, ConfigException
from pulse2.database.xmppmaster.config import XmppMasterDatabaseConfig
import platform
from mmc.plugins.xmppmaster.master.lib import utils
import logging
class xmppMasterConfig(PluginConfig, XmppMasterDatabaseConfig):

    def __init__(self, name = 'xmppmaster', conffile = None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            XmppMasterDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        """
        Set good default for the module if a parameter is missing the
        configuration file.
        This function is called in the class constructor, so what you
        set here will be overwritten by the readConf method.
        """
        PluginConfig.setDefault(self)
        self.showinfomaster = False
        self.showplugins = False
        self.debugmode = "NOTSET"


    def readConf(self):
        """
        Read the configuration file using the ConfigParser API.
        The PluginConfig.readConf reads the "disable" option of the
        "main" section.
        """
        PluginConfig.readConf(self)
        XmppMasterDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")

        self.Port= self.get('connection', 'port')
        self.Server= self.get('connection', 'server')
        self.passwordconnection=self.get('connection', 'password')
        self.debugmode = self.get('global', 'debug')
        #########salon############

        self.jidsalonmaster="master@%s"%self.get('salon', 'server')
        self.jidsalonlog="log@%s"%self.get('salon', 'server')
        self.jidsaloncommand="command@%s"%self.get('salon', 'server')
        self.passwordconnexionmuc=self.get('salon', 'password')

        ###################SALON CONFIGURATION DYNAMIQUE AGENT#######################confjidsalon
        #information configuration dynamique
        self.confjidsalon = "%s@%s"%(self.get('configurationserver', 'confnamesalon'),self.get('salon', 'server'))
        self.confpasswordmuc = self.get('configurationserver', 'confpasswordmuc')
        ########chat#############
        # le jidagent doit etre la plus petite valeur de la liste des macs.
        self.chatserver=self.get('chat', 'server')
        # plus petite mac adress
        self.jidagent = "%s@%s/%s"%(utils.name_jid(),self.get('chat', 'server'),platform.node())
        self.jidagentsiveo = "%s@%s"%(self.get('global', 'ordre'),self.get('chat', 'server'))
        self.ordreallagent = self.getboolean('global', 'inter_agent')
        self.showinfomaster = self.getboolean('master', 'showinfo')
        self.showplugins = self.getboolean('master', 'showplugins')
        #################""default connection ###################""
        ### parameters conection server si pas server relais dispo ####

        self.defaultrelayserverip = self.get('defaultconnection', 'serverip')
        if self.defaultrelayserverip == "localhost":
            logging.getLogger().error('parameter section "defaultconnection" serverip not must localhost')
        if self.defaultrelayserverip == "127.0.0.1":
            logging.getLogger().error('parameter section "defaultconnection" serverip not must 127.0.0.1')
        self.defaultrelayserverport = self.get('defaultconnection', 'port')

        self.defaultrelayserverbaseurlguacamole=self.get('defaultconnection', 'baseurlguacamole')


        #self.inventory = self.get('inventorypulse', 'inventory')

        self.jidagent = "%s@%s/%s"%("master",self.chatserver,"MASTER")
        self.NickName = "MASTER"

        self.dirplugins = self.get('plugins', 'dirplugins')
        self.information={}
        self.PlateformSystem=platform.platform()
        self.information['plateform']=self.PlateformSystem
        self.OperatingSystem=platform.system()
        self.information['os']=self.OperatingSystem
        self.UnameSystem = platform.uname()
        self.information['uname']=self.UnameSystem
        self.HostNameSystem =platform.node()
        self.information['hostname']=self.HostNameSystem
        self.OsReleaseNumber=platform.release()
        self.information['osrelease']=self.OsReleaseNumber
        self.DetailedVersion=platform.version()
        self.information['version']=self.DetailedVersion
        self.HardwareType=platform.machine()
        self.information['hardtype']=self.HardwareType
        self.ProcessorIdentifier=platform.processor()
        self.information['processor']=self.ProcessorIdentifier
        self.Architecture=platform.architecture()
        self.information['archi']=self.Architecture

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
        xmppMasterConfig("xmppmaster")
        return True
