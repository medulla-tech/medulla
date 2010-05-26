# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Contains classes to read MMC agent plugin configuration files.
"""

import mmctools

import ldap
import re
from ConfigParser import ConfigParser, NoOptionError, NoSectionError


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
        match = re.search('^{(\w+)}(.+)$', value)
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

    def __init__(self, name, conffile = None):
        MMCConfigParser.__init__(self)
        self.name = name
        self.userDefault = {}
        self.hooks = {}
        if not conffile:
            self.conffile = mmctools.getConfigFile(name)
        else: self.conffile = conffile
        self.setDefault()
        fid = file(self.conffile, "r")
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
