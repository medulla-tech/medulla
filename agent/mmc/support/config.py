# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Contains classes to read MMC agent plugin configuration files.
"""

from . import mmctools

import ldap
import re
from pulse2.database.admin import AdminDatabase
from os.path import isfile
from configparser import ConfigParser, NoOptionError, NoSectionError, InterpolationError
import logging

logger = logging.getLogger()


class ConfigException(Exception):
    """
    Exception raised when there is a configuration error.
    """

    pass


class MMCConfigParser(ConfigParser):
    """
    Class to read and parse a MMC agent plugin configuration file.
    """

    def __init__(self):
        ConfigParser.__init__(self)

    def get(self, section, option, **kwargs):
        try:
            value = ConfigParser.get(self, section, option, **kwargs)
        except InterpolationError as exc:
            kwargs["raw"] = True
            value = ConfigParser.get(self, section, option, **kwargs)
            if "%(baseDN)s" not in value:
                raise InterpolationError
            from mmc.plugins.base import BasePluginConfig

            config = PluginConfigFactory.new(BasePluginConfig, "base")
            value = value.replace("%(baseDN)s", config.baseDN)
        return value

    def safe_get(self, section, option, default=None):
        """
        Returns a default value if the option does not exist
        """
        try:
            return self.get(section, option)
        except (NoOptionError, NoSectionError):
            return default

    def getdn(self, section, option):
        """
        Like get, but interpret the value as a LDAP DN, and sanitize it by
        removing the extra spaces.

        If the value is not a valid DN, a ldap.LDAPError exception will be
        raised.
        """
        return ",".join(ldap.explode_dn(self.get(section, option)))

    def getpassword(self, section, option):
        """
        Like get, but interpret the value as a obfuscated password if a
        password scheme is specified.

        For example: passwd = {base64}bWFuL2RyaXZhMjAwOA==
        """
        value = self.get(section, option)
        if not (match := re.search("^{(\w+)}(.+)$", value)):
            return value
        scheme = match[1]
        obfuscated = match[2]
        return obfuscated.decode(scheme)


class PluginConfig(MMCConfigParser):
    """
    Class to hold a MMC agent plugin configuration
    """

    USERDEFAULT = "userdefault"
    HOOKS = "hooks"
    SERVICE = "service"

    def __init__(self, name, conffile=None, backend="ini", db_table=None):
        """
        Args:
            name: Plugin name
            conffile: Path to config file (optional)
            backend: "ini" (default) or "database"
            db_table: DB table name (e.g., 'xmpp_conf') if backend="database"
        """
        MMCConfigParser.__init__(self)
        self.name = name
        self.userDefault = {}
        self.hooks = {}
        self.service = {}
        self.backend = backend
        
        if backend == "database":
            if not db_table:
                raise ConfigException(f"db_table required when using database backend for {name}")
            self.db_table = db_table
            self.conffile = None  # No file when reading from DB
            self._admin_db = AdminDatabase()
            if hasattr(self._admin_db, "activate"):
                self._admin_db.activate(self)
            logger.info(f"[PluginConfig] Backend database activé pour {name} (table: {db_table})")
        else:
            # Classic INI mode
            self.conffile = mmctools.getConfigFile(name) if not conffile else conffile
            self.setDefault()
            fid = open(self.conffile, "r")
            self.readfp(fid, self.conffile)
            if isfile(f"{self.conffile}.local"):
                fid = open(f"{self.conffile}.local", "r")
                self.readfp(fid, self.conffile)
            logger.info(f"[PluginConfig] Backend ini file activé pour {name} ({self.conffile})")
        
        self.setDefault()
        self.readConf()

    def get(self, section, option, **kwargs):
        """Override get to route to the appropriate backend"""
        if self.backend == "database":
            value = self._admin_db.get_config_value(self.db_table, section, option)
            if value is None:
                raise NoOptionError(option, section)
            return value
        else:
            return MMCConfigParser.get(self, section, option, **kwargs)

    def has_option(self, section, option):
        """Override has_option to route to the appropriate backend"""
        if self.backend == "database":
            return self._admin_db.get_config_value(self.db_table, section, option) is not None
        else:
            return ConfigParser.has_option(self, section, option)

    def has_section(self, section):
        """Override has_section to route to the appropriate backend"""
        if self.backend == "database":
            return self._admin_db.has_config_section(self.db_table, section)
        else:
            return ConfigParser.has_section(self, section)

    def options(self, section):
        """Override options to route to the appropriate backend"""
        if self.backend == "database":
            return self._admin_db.get_config_options(self.db_table, section)
        else:
            return ConfigParser.options(self, section)

    def sections(self):
        """Return list of sections.

        For `database` backend, build the section list from the stored
        configuration rows. This keeps compatibility with code that uses
        `self.cp.sections()`.
        """
        if self.backend == "database":
            return self._admin_db.get_config_sections(self.db_table)
        else:
            return ConfigParser.sections(self)

    def readConf(self):
        """Read the configuration file"""
        try:
            self.disabled = self.getboolean("main", "disable")
        except (NoSectionError, NoOptionError):
            pass
        if self.has_section(self.USERDEFAULT):
            for option in self.options(self.USERDEFAULT):
                self.userDefault[option] = self.get(self.USERDEFAULT, option)
        if self.has_section(self.HOOKS):
            for option in self.options(self.HOOKS):
                self.hooks[f"{self.name}.{option}"] = self.get(self.HOOKS, option)
        if self.has_section(self.SERVICE):
            for option in self.options(self.SERVICE):
                self.service[option] = self.get(self.SERVICE, option)

    def setDefault(self):
        """Set reasonable default"""
        self.disabled = True

    def _load_db_settings_from_backend(self):
        """
        Load standard database-related settings from the configured backend.
        When `backend == 'database'`, PluginConfig routes get/has_option/has_section
        to the admin database, so this method works the same way as
        DatabaseConfig.setup but using the dynamic backend.
        """
        # Only act when backend is database and dbsection is defined
        if self.backend != "database":
            return
        if not hasattr(self, "dbsection"):
            return

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

        Must be implemented by the subclass.
        ConfigException is raised with a corresponding error string if a check
        fails.
        """
        pass


class PluginConfigFactory(object):
    """
    For each plugin, we need to have only ONE config instance.
    This is useful, for example so that the Admin-Configuration plugin
    can change the config at run time, and every classes using the a PluginConfig will get the new values without restarting.
    So, every PluginConfig (or a derivated) instance should be created this way
    """

    instances = {}

    @staticmethod
    def new(cls, name, *args, **kwargs):
        """
        If no instance of a class (with this name) has not already
        been created, create it and keep it in the dict.
        If one already exist, just return it.
        """
        if name not in PluginConfigFactory.instances:
            PluginConfigFactory.instances[name] = cls(name, *args, **kwargs)
        return PluginConfigFactory.instances[name]

    @staticmethod
    def get(name):
        """
        Returns the PluginConfig instance that was
        created with this name.
        If it doesn't exist, raise an error because that should never
        happen.
        """
        return PluginConfigFactory.instances.get(name)
