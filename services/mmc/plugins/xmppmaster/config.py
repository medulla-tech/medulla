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

from mmc.support.config import PluginConfig  # , ConfigException
from pulse2.database.xmppmaster.config import XmppMasterDatabaseConfig
import platform
from mmc.plugins.xmppmaster.master.lib import utils
import logging
from mmc.plugins.xmppmaster.master.lib.utils import ipfromdns
import os
import ConfigParser

logger = logging.getLogger()

class xmppMasterConfig(PluginConfig, XmppMasterDatabaseConfig):

    def __init__(self, name='xmppmaster', conffile=None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            XmppMasterDatabaseConfig.__init__(self)
            self.initdone = True

    def loadparametersplugins(self, namefile):
        Config = ConfigParser.ConfigParser()
        Config.optionxform = str
        Config.read(namefile)
        return Config.items("parameters")

    def setDefault(self):
        """
        Set default for the module if a parameter is missing from the
        configuration file.
        This function is called in the class constructor, so what you
        set here will be overwritten by the readConf method.
        """
        PluginConfig.setDefault(self)
        self.showinfomaster = False
        self.showplugins = False
        self.debugmode = "NOTSET"
        self.ordreallagent = False

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

        self.Port = self.get('connection', 'port')
        self.Server = ipfromdns(self.get('connection', 'server'))
        self.passwordconnection = self.get('connection', 'password')
        self.debugmode = self.get('global', 'log_level')
        #########chatroom############

        self.jidchatroommaster = "master@%s" % self.get('chatroom', 'server')
        self.jidchatroomlog = "log@%s" % self.get('chatroom', 'server')
        self.jidchatroomcommand = "command@%s" % self.get('chatroom', 'server')
        self.passwordconnexionmuc = self.get('chatroom', 'password')

        #######configuration browserfile#######
        self.defaultdir = os.path.join("/", "var", "lib", "pulse2", "file-transfer")
        self.rootfilesystem = os.path.join("/", "var", "lib", "pulse2", "file-transfer")
        if self.has_option("browserfile", "defaultdir"):
            self.defaultdir = self.get('browserfile', 'defaultdir')
        if self.has_option("bowserfile", "rootfilesystem"):
            self.rootfilesystem = self.get('browserfile', 'rootfilesystem')

        ###################Chatroom for dynamic configuration of agents#######################
        # Dynamic configuration information
        self.confjidchatroom = "%s@%s" % (
            self.get('configuration_server', 'confmuc_chatroom'), self.get('chatroom', 'server'))
        self.confpasswordmuc = self.get('configuration_server', 'confmuc_password')
        ########chat#############
        # The jidagent must be the smallest value in the list of mac addresses
        self.chatserver = self.get('chat', 'domain')
        # plus petite mac adress
        self.jidagent = "%s@%s/%s" % (utils.name_jid(), self.get('chat', 'domain'), platform.node())

        try:
            # Interval for installing new plugins on clients (in seconds)
            self.remote_update_plugin_interval = self.getint('global', 'remote_update_plugin_interval')
        except Exception:
            self.remote_update_plugin_interval = 60
        # Enable memory leaks checks and define interval (in seconds)
        try:
            self.memory_leak_check = self.getboolean('global', 'memory_leak_check')
        except Exception:
            self.memory_leak_check = False
        try:
            self.memory_leak_interval = self.getint('global', 'memory_leak_interval')
        except Exception:
            self.memory_leak_interval = 15

        try:
            self.reload_plugins_base_interval = self.getint('global', 'reload_plugins_base_interval')
        except Exception:
            self.reload_plugins_base_interval = 900
        try:
            # Interval between two scans for checking for new deployments (in seconds)
            self.deployment_scan_interval = self.getint('global', 'deployment_scan_interval')
        except Exception:
            self.deployment_scan_interval = 30
        try:
            self.deployment_end_timeout = self.getint('global', 'deployment_end_timeout')
        except Exception:
            self.deployment_end_timeout = 300
        try:
            self.session_check_interval = self.getint('global', 'session_check_interval')
        except Exception:
            self.session_check_interval = 15

        try:
            self.wol_interval = self.getint('global', 'wol_interval')
        except Exception:
            self.wol_interval = 60
        try:
            self.jidagentsiveo = "%s@%s" % (
                self.get('global', 'allow_order'), self.get('chat', 'domain'))
        except:
            self.jidagentsiveo = "%s@%s" % ("agentsiveo", self.get('chat', 'domain'))
        self.ordreallagent = self.getboolean('global', 'inter_agent')
        self.showinfomaster = self.getboolean('master', 'showinfo')
        self.showplugins = self.getboolean('master', 'showplugins')
        self.blacklisted_mac_addresses= []
        if self.has_option("master", "blacklisted_mac_addresses"):
            blacklisted_mac_addresses = self.get('master', 'blacklisted_mac_addresses')
        else:
            blacklisted_mac_addresses = "00:00:00:00:00:00"
        blacklisted_mac_addresses = blacklisted_mac_addresses.lower().replace(":","").replace(" ","")
        blacklisted_mac_addresses_list = [x.strip() for x in blacklisted_mac_addresses.split(',')]
        for t in blacklisted_mac_addresses_list:
            if len(t) == 12:
                macadrs = t[0:2]+":"+t[2:4]+":"+t[4:6]+":"+t[6:8]+":"+t[8:10]+":"+t[10:12]
                self.blacklisted_mac_addresses.append(macadrs)
            else:
                logger.warning("the mac address in blacklisted_mac_addresses parameter is bad format for value %s"%t )
        if "00:00:00:00:00:00" not in self.blacklisted_mac_addresses:
            self.blacklisted_mac_addresses.insert(0,"00:00:00:00:00:00")
        self.blacklisted_mac_addresses=list(set(self.blacklisted_mac_addresses))
        ###################time execcution plugin ####################
        # write execution time in fichier /tmp/Execution_time_plugin.txt
        #
        if self.has_option("global", "executiontimeplugins"):
            self.executiontimeplugins = self.getboolean('global', 'executiontimeplugins')
        else:
            self.executiontimeplugins = False
        #################default connection ###################
        ### Connection server parameters if no relay server is available ####
        self.defaultrelayserverip = ipfromdns(self.get('defaultconnection', 'serverip'))
        if self.defaultrelayserverip == "localhost":
            logging.getLogger().error('parameter section "defaultconnection" serverip must not be localhost')
        if self.defaultrelayserverip == "127.0.0.1":
            logging.getLogger().error('parameter section "defaultconnection" serverip must not be 127.0.0.1')
        self.defaultrelayserverport = self.get('defaultconnection', 'port')
        self.defaultrelayserverbaseurlguacamole = self.get('defaultconnection', 'guacamole_baseurl')
        self.jidagent = "%s@%s/%s" % ("master", self.chatserver, "MASTER")
        self.NickName = "MASTER"

        if self.has_option("global", "diragentbase"):
            self.diragentbase = self.get('global', 'diragentbase')
        else:
            self.diragentbase = "/var/lib/pulse2/xmpp_baseremoteagent/"
        if self.has_option("global", "autoupdate"):
            self.autoupdate = self.getboolean('global', 'autoupdate')
        else:
            self.autoupdate = True
        if self.has_option("global", "autoupdatebyrelay"):
            self.autoupdatebyrelay = self.getboolean('global', 'autoupdatebyrelay')
        else:
            self.autoupdatebyrelay = False
        self.dirplugins = self.get('plugins', 'dirplugins')
        self.dirschedulerplugins = self.get('plugins', 'dirschedulerplugins')
        self.information = {}
        self.PlatformSystem = platform.platform()
        self.information['platform'] = self.PlatformSystem
        self.OperatingSystem = platform.system()
        self.information['os'] = self.OperatingSystem
        self.UnameSystem = platform.uname()
        self.information['uname'] = self.UnameSystem
        self.HostNameSystem = platform.node()
        self.information['hostname'] = self.HostNameSystem
        self.OsReleaseNumber = platform.release()
        self.information['osrelease'] = self.OsReleaseNumber
        self.DetailedVersion = platform.version()
        self.information['version'] = self.DetailedVersion
        self.HardwareType = platform.machine()
        self.information['hardtype'] = self.HardwareType
        self.ProcessorIdentifier = platform.processor()
        self.information['processor'] = self.ProcessorIdentifier
        self.Architecture = platform.architecture()
        self.information['archi'] = self.Architecture

        if self.has_option("plugins", "pluginlist"):
            pluginlist = self.get('plugins', 'pluginlist').split(",")
            pluginlist = [x.strip() for x in pluginlist]

            for z in pluginlist:
                namefile = "%s.ini" % os.path.join("/", "etc", "mmc", "plugins", z)
                logging.getLogger().debug('load parameter File plugin %s' % namefile)
                if os.path.isfile(namefile):
                    liststuple = self.loadparametersplugins(namefile)
                    for keyparameter, valueparameter in liststuple:
                        setattr(self, keyparameter, valueparameter)
                else:
                    logging.getLogger().error("Parameter File Plugin %s : missing" % namefile)
        if self.has_option("syncthing", "announce_server"):
            self.announce_server = self.get('syncthing', 'announce_server')
        else:
            self.announce_server = "default"

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
