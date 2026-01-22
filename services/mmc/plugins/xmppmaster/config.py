# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.support.config import PluginConfig  # , ConfigException
from pulse2.database.xmppmaster.config import XmppMasterDatabaseConfig
import platform
from mmc.plugins.xmppmaster.master.lib import utils
import logging
from mmc.plugins.xmppmaster.master.lib.utils import ipfromdns
import os
import configparser

logger = logging.getLogger()


class xmppMasterConfig(PluginConfig, XmppMasterDatabaseConfig):
    def __init__(self, name="xmppmaster", conffile=None, backend="database"):
        if not hasattr(self, "initdone"):
            logger.info(f"[xmppMasterConfig] Initialisation avec backend={backend}")
            # Initialiser avec backend database (lit depuis variables d'environnement)
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table="xmpp_conf")
            logger.info(f"[xmppMasterConfig] ✅ Configuration chargée depuis la BDD")
            XmppMasterDatabaseConfig.__init__(self)
            self.initdone = True

    def loadparametersplugins(self, namefile):
        Config = configparser.ConfigParser()
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
        # Appeler setup() pour initialiser la connexion à la base xmppmaster
        if self.backend == "ini":
            XmppMasterDatabaseConfig.setup(self, self.conffile)
        else:
            if self.has_option("database", "dbdriver"):
                self.dbdriver = self.get("database", "dbdriver")
            if self.has_option("database", "dbhost"):
                self.dbhost = self.get("database", "dbhost")
            if self.has_option("database", "dbport"):
                self.dbport = self.getint("database", "dbport")
            if self.has_option("database", "dbname"):
                self.dbname = self.get("database", "dbname")
            if self.has_option("database", "dbuser"):
                self.dbuser = self.get("database", "dbuser")
            if self.has_option("database", "dbpasswd"):
                self.dbpasswd = self.getpassword("database", "dbpasswd")
            if self.has_option("database", "dbdebug"):
                self.dbdebug = self.get("database", "dbdebug")
            if self.has_option("database", "dbpoolrecycle"):
                self.dbpoolrecycle = self.getint("database", "dbpoolrecycle")
            if self.has_option("database", "dbpoolsize"):
                self.dbpoolsize = self.getint("database", "dbpoolsize")
            if self.has_option("database", "dbpooltimeout"):
                self.dbpooltimeout = self.getint("database", "dbpooltimeout")


        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")

        self.Port = self.get("connection", "port")
        self.Server = ipfromdns(self.get("connection", "server"))
        self.passwordconnection = self.get("connection", "password")
        self.debugmode = self.get("global", "log_level")
        #########chatroom############

        self.jidchatroommaster = "master@%s" % self.get("chatroom", "server")
        self.jidchatroomlog = "log@%s" % self.get("chatroom", "server")
        self.jidchatroomcommand = "command@%s" % self.get("chatroom", "server")
        self.passwordconnexionmuc = self.get("chatroom", "password")

        #######configuration browserfile#######
        self.defaultdir = os.path.join("/", "var", "lib", "pulse2", "file-transfer")
        self.rootfilesystem = os.path.join("/", "var", "lib", "pulse2", "file-transfer")
        if self.has_option("browserfile", "defaultdir"):
            self.defaultdir = self.get("browserfile", "defaultdir")
        if self.has_option("bowserfile", "rootfilesystem"):
            self.rootfilesystem = self.get("browserfile", "rootfilesystem")

        # This will be used to configure the machine table from GLPI
        # the reg_key_ to show are defined  reg_key_1 reg_key_2
        # regarding the reg_key_1 et reg_key_2 defined in the inventory section
        self.summary = ["cn", "description", "os", "type", "user", "entity"]
        if self.has_option("computer_list", "summary"):
            self.summary = self.get("computer_list", "summary").split(" ")

        # This is used to order by name asc the xmpp machines list
        self.ordered = 0
        if self.has_option("computer_list", "ordered"):
            self.ordered = self.getint("computer_list", "ordered")

        ## Registry keys that need to be pushed in an inventory
        ## Format: reg_key_x = path_to_key|key_label_shown_in_mmc
        ## eg.:
        ## reg_key_1 = HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA|LUAEnabled
        ## reg_key_2 = HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\ProductName|WindowsVersion
        ## max_key_index = 2

        ##reg_key_1 = HKEY_CURRENT_USER\Software\test\dede|dede
        # reg_key_1 = HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA|LUAEnabled
        # reg_key_2 = HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\ProductName|ProductName
        # max_key_index=2

        self.max_key_index = 50
        if self.has_option("inventory", "max_key_index"):
            self.max_key_index = self.getint("inventory", "max_key_index")
        # create mutex
        self.arraykeys = []
        for index_key in range(1, self.max_key_index + 1):
            if self.has_option("inventory", "reg_key_%s" % index_key):
                self.arraykeys.append(self.get("inventory", "reg_key_%s" % index_key))

        self.max_key_index = len(self.arraykeys)

        self.centralizedmultiplesharing = True
        if self.has_option("pkgs", "centralizedmultiplesharing"):
            self.centralizedmultiplesharing = self.getboolean(
                "pkgs", "centralizedmultiplesharing"
            )

        self.movepackage = False
        if self.has_option("pkgs", "movepackage"):
            self.movepackage = self.getboolean("pkgs", "movepackage")

        ###################Chatroom for dynamic configuration of agents#######################
        # Dynamic configuration information
        self.confjidchatroom = "%s@%s" % (
            self.get("configuration_server", "confmuc_chatroom"),
            self.get("chatroom", "server"),
        )
        self.confpasswordmuc = self.get("configuration_server", "confmuc_password")
        ########chat#############
        # The jidagent must be the smallest value in the list of mac addresses
        self.chatserver = self.get("chat", "domain")
        # plus petite mac adress
        self.jidagent = "%s@%s/%s" % (
            utils.name_jid(),
            self.get("chat", "domain"),
            platform.node(),
        )

        try:
            # Interval for installing new plugins on clients (in seconds)
            self.remote_update_plugin_interval = self.getint(
                "global", "remote_update_plugin_interval"
            )
        except Exception:
            self.remote_update_plugin_interval = 60
        # deployment support for master
        try:
            self.Booltaskdeploy = self.getboolean("global", "taskdeploy")
        except Exception:
            self.Booltaskdeploy = True
        # manage session
        try:
            self.Boolsessionwork = self.getboolean("global", "sessionwork")
        except Exception:
            self.Boolsessionwork = True
        # Enable memory leaks checks and define interval (in seconds)
        try:
            self.memory_leak_check = self.getboolean("global", "memory_leak_check")
        except Exception:
            self.memory_leak_check = False
        try:
            self.memory_leak_interval = self.getint("global", "memory_leak_interval")
        except Exception:
            self.memory_leak_interval = 15

        try:
            self.reload_plugins_base_interval = self.getint(
                "global", "reload_plugins_base_interval"
            )
        except Exception:
            self.reload_plugins_base_interval = 900
        try:
            # Interval between two scans for checking for new deployments (in seconds)
            self.deployment_scan_interval = self.getint(
                "global", "deployment_scan_interval"
            )
        except Exception:
            self.deployment_scan_interval = 30
        try:
            self.deployment_end_timeout = self.getint(
                "global", "deployment_end_timeout"
            )
        except Exception:
            self.deployment_end_timeout = 300
        try:
            self.session_check_interval = self.getint(
                "global", "session_check_interval"
            )
        except Exception:
            self.session_check_interval = 15

        try:
            self.wol_interval = self.getint("global", "wol_interval")
        except Exception:
            self.wol_interval = 60
        try:
            self.jidagentsiveo = "%s@%s" % (
                self.get("global", "allow_order"),
                self.get("chat", "domain"),
            )
        except:
            self.jidagentsiveo = "%s@%s" % ("agentsiveo", self.get("chat", "domain"))
        self.ordreallagent = self.getboolean("global", "inter_agent")
        self.showinfomaster = self.getboolean("master", "showinfo")
        self.showplugins = self.getboolean("master", "showplugins")
        self.blacklisted_mac_addresses = []
        if self.has_option("master", "blacklisted_mac_addresses"):
            blacklisted_mac_addresses = self.get("master", "blacklisted_mac_addresses")
        else:
            blacklisted_mac_addresses = "00:00:00:00:00:00"
        blacklisted_mac_addresses = (
            blacklisted_mac_addresses.lower().replace(":", "").replace(" ", "")
        )
        blacklisted_mac_addresses_list = [
            x.strip() for x in blacklisted_mac_addresses.split(",")
        ]
        for t in blacklisted_mac_addresses_list:
            if len(t) == 12:
                macadrs = (
                    t[0:2]
                    + ":"
                    + t[2:4]
                    + ":"
                    + t[4:6]
                    + ":"
                    + t[6:8]
                    + ":"
                    + t[8:10]
                    + ":"
                    + t[10:12]
                )
                self.blacklisted_mac_addresses.append(macadrs)
            else:
                logger.warning(
                    "the mac address in blacklisted_mac_addresses parameter is bad format for value %s"
                    % t
                )
        if "00:00:00:00:00:00" not in self.blacklisted_mac_addresses:
            self.blacklisted_mac_addresses.insert(0, "00:00:00:00:00:00")
        self.blacklisted_mac_addresses = list(set(self.blacklisted_mac_addresses))
        ###################time execcution plugin ####################
        # write execution time in fichier /tmp/Execution_time_plugin.txt
        #
        if self.has_option("global", "executiontimeplugins"):
            self.executiontimeplugins = self.getboolean(
                "global", "executiontimeplugins"
            )
        else:
            self.executiontimeplugins = False
        #################default connection ###################
        ### Connection server parameters if no relay server is available ####
        self.defaultrelayserverip = ipfromdns(self.get("defaultconnection", "serverip"))
        if self.defaultrelayserverip == "localhost":
            logging.getLogger().error(
                'parameter section "defaultconnection" serverip must not be localhost'
            )
        if self.defaultrelayserverip == "127.0.0.1":
            logging.getLogger().error(
                'parameter section "defaultconnection" serverip must not be 127.0.0.1'
            )
        self.defaultrelayserverport = self.get("defaultconnection", "port")
        self.defaultrelayserverbaseurlguacamole = self.get(
            "defaultconnection", "guacamole_baseurl"
        )
        self.jidagent = "%s@%s/%s" % ("master", self.chatserver, "MASTER")
        self.NickName = "MASTER"

        if self.has_option("global", "diragentbase"):
            self.diragentbase = self.get("global", "diragentbase")
        else:
            self.diragentbase = "/var/lib/pulse2/xmpp_baseremoteagent/"
        if self.has_option("global", "autoupdate"):
            self.autoupdate = self.getboolean("global", "autoupdate")
        else:
            self.autoupdate = True
        if self.has_option("global", "autoupdatebyrelay"):
            self.autoupdatebyrelay = self.getboolean("global", "autoupdatebyrelay")
        else:
            self.autoupdatebyrelay = True
        self.pluginliststart = ""
        if self.has_option("plugins", "pluginliststart"):
            self.pluginliststart = self.get("plugins", "pluginliststart")
        self.pluginliststart = [
            x.strip() for x in self.pluginliststart.split(",") if x.strip() != ""
        ]
        self.dirplugins = self.get("plugins", "dirplugins")
        self.dirschedulerplugins = self.get("plugins", "dirschedulerplugins")
        self.information = {}
        self.PlatformSystem = platform.platform()
        self.information["platform"] = self.PlatformSystem
        self.OperatingSystem = platform.system()
        self.information["os"] = self.OperatingSystem
        self.UnameSystem = platform.uname()
        self.information["uname"] = self.UnameSystem
        self.HostNameSystem = platform.node()
        self.information["hostname"] = self.HostNameSystem
        self.OsReleaseNumber = platform.release()
        self.information["osrelease"] = self.OsReleaseNumber
        self.DetailedVersion = platform.version()
        self.information["version"] = self.DetailedVersion
        self.HardwareType = platform.machine()
        self.information["hardtype"] = self.HardwareType
        self.ProcessorIdentifier = platform.processor()
        self.information["processor"] = self.ProcessorIdentifier
        self.Architecture = platform.architecture()
        self.information["archi"] = self.Architecture

        if self.has_option("plugins", "pluginlist"):
            pluginlist = self.get("plugins", "pluginlist").split(",")
            pluginlist = [x.strip() for x in pluginlist]

            for z in pluginlist:
                namefile = "%s.ini" % os.path.join("/", "etc", "mmc", "plugins", z)
                logging.getLogger().debug("load parameter File plugin %s" % namefile)
                if os.path.isfile(namefile):
                    liststuple = self.loadparametersplugins(namefile)
                    for keyparameter, valueparameter in liststuple:
                        setattr(self, keyparameter, valueparameter)
                else:
                    logging.getLogger().error(
                        "Parameter File Plugin %s : missing" % namefile
                    )
        if self.has_option("syncthing", "announce_server"):
            self.announce_server = self.get("syncthing", "announce_server")
        else:
            self.announce_server = "default"

    def check(self):
        """
        Check the values set in the configuration file.
        Must be implemented by the subclass. ConfigException is raised
        with a corresponding error string if a check fails.
        """
        # if not self.confOption: raise ConfigException("Conf error")
        pass

    def activate():
        # Get module config from "/etc/mmc/plugins/module_name.ini"
        xmppMasterConfig("xmppmaster")
        return True
