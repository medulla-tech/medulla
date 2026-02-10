# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
from mmc.support.config import PluginConfig
from pulse2.database.kiosk.config import KioskDatabaseConfig


class KioskConfig(PluginConfig, KioskDatabaseConfig):
    """This class is called by the __init__ of the kiosk module."""

    def __init__(self, name="kiosk", conffile=None, backend="database"):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table="kiosk_conf")
            KioskDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        """
        Set good default for the module if a parameter is missing the
        configuration file.
        This function is called in the class constructor, so what you
        set here will be overwritten by the readConf method.
        """
        PluginConfig.setDefault(self)
        # self.confOption = "option1"
        # ...

    def readConf(self):
        """
        Read the configuration file using the ConfigParser API.
        The PluginConfig.readConf reads the "disable" option of the
        "main" section.
        """
        PluginConfig.readConf(self)
        if self.backend == "database":
            self._load_db_settings_from_backend()
        elif self.conffile and self.backend == "ini":
            KioskDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
        self.use_external_ldap = False
        if self.has_option("provider", "use_external_ldap"):
            self.use_external_ldap = self.getboolean("provider", "use_external_ldap")

        self.enable_acknowledgements = False
        if self.has_option("display", "enable_acknowledgements"):
            self.enable_acknowledgements = self.getboolean(
                "display", "enable_acknowledgements"
            )
        # ...

    def _load_db_settings_from_backend(self):
        if not self.has_section(self.dbsection):
            return

        if self.has_option(self.dbsection, "dbdriver"):
            self.dbdriver = self.get(self.dbsection, "dbdriver")
        if self.has_option(self.dbsection, "dbhost"):
            self.dbhost = self.get(self.dbsection, "dbhost")
        if self.has_option(self.dbsection, "dbport"):
            self.dbport = self.getint(self.dbsection, "dbport")
        if self.has_option(self.dbsection, "dbname"):
            self.dbname = self.get(self.dbsection, "dbname")
        if self.has_option(self.dbsection, "dbuser"):
            self.dbuser = self.get(self.dbsection, "dbuser")
        if self.has_option(self.dbsection, "dbpasswd"):
            self.dbpasswd = self.getpassword(self.dbsection, "dbpasswd")

        if self.has_option(self.dbsection, "dbdebug"):
            self.dbdebug = self.get(self.dbsection, "dbdebug")
        if self.has_option(self.dbsection, "dbpoolrecycle"):
            self.dbpoolrecycle = self.getint(self.dbsection, "dbpoolrecycle")
        if self.has_option(self.dbsection, "dbpoolsize"):
            self.dbpoolsize = self.getint(self.dbsection, "dbpoolsize")
        if self.has_option(self.dbsection, "dbpooltimeout"):
            self.dbpooltimeout = self.getint(self.dbsection, "dbpooltimeout")

        if self.has_option(self.dbsection, "dbsslenable"):
            self.dbsslenable = self.getboolean(self.dbsection, "dbsslenable")
            if self.dbsslenable:
                if self.has_option(self.dbsection, "dbsslca"):
                    self.dbsslca = self.get(self.dbsection, "dbsslca")
                if self.has_option(self.dbsection, "dbsslcert"):
                    self.dbsslcert = self.get(self.dbsection, "dbsslcert")
                if self.has_option(self.dbsection, "dbsslkey"):
                    self.dbsslkey = self.get(self.dbsection, "dbsslkey")

    def check(self):
        """
        Check the values set in the configuration file.
        Must be implemented by the subclass. ConfigException is raised
        with a corresponding error string if a check fails.
        """
        # if not self.confOption: raise ConfigException("Conf error")
        pass

    @staticmethod
    def activate():
        KioskConfig("kiosk", None, "database")
        return True
