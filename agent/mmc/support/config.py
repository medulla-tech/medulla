# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Contains classes to read MMC agent plugin configuration files.
"""

from . import mmctools

import ldap
import re
from os.path import isfile
from configparser import ConfigParser, NoOptionError, NoSectionError, InterpolationError


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
            if "%(baseDN)s" in value:
                from mmc.plugins.base import BasePluginConfig

                config = PluginConfigFactory.new(BasePluginConfig, "base")
                value = value.replace("%(baseDN)s", config.baseDN)
            else:
                raise InterpolationError
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
        match = re.search("^{(\w+)}(.+)$", value)
        if match:
            scheme = match.group(1)
            obfuscated = match.group(2)
            ret = obfuscated.decode(scheme)
        else:
            ret = value
        return ret


class PluginConfig(MMCConfigParser):
    """
    Class to hold a MMC agent plugin configuration
    """

    USERDEFAULT = "userdefault"
    HOOKS = "hooks"
    SERVICE = "service"

    def __init__(self, name, conffile=None):
        MMCConfigParser.__init__(self)
        self.name = name
        self.userDefault = {}
        self.hooks = {}
        self.service = {}
        if not conffile:
            self.conffile = mmctools.getConfigFile(name)
        else:
            self.conffile = conffile
        self.setDefault()
        fid = open(self.conffile, "r")
        self.readfp(fid, self.conffile)
        if isfile(self.conffile + ".local"):
            fid = open(self.conffile + ".local", "r")
            self.readfp(fid, self.conffile)
        self.readConf()

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
                self.hooks[self.name + "." + option] = self.get(self.HOOKS, option)
        if self.has_section(self.SERVICE):
            for option in self.options(self.SERVICE):
                self.service[option] = self.get(self.SERVICE, option)

    def setDefault(self):
        """Set reasonable default"""
        self.disabled = True

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
        if not name in PluginConfigFactory.instances:
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
