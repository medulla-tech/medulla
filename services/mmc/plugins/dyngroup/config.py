#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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

import logging
from mmc.support.config import PluginConfig
from ConfigParser import NoOptionError

class DGConfig(PluginConfig):
    dyngroup_activate = True
    defaultModule = ''
    maxElementsForStaticList = 2000
    profilesEnable = False

    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)
        self.dbdriver = self.get("database", "dbdriver")
        self.dbuser = self.get("database", "dbuser")
        self.dbpasswd = self.getpassword("database", "dbpasswd")
        self.dbhost = self.get("database", "dbhost")
        self.dbname = self.get("database", "dbname")
        self.disable = self.getboolean("main", "disable")
        self.dynamicEnable = self.getboolean("main", "dynamic_enable")
        if self.has_option('main', 'profiles_enable'):
            self.profilesEnable = self.getboolean("main", 'profiles_enable')
        if self.has_option('main', 'default_module'):
            self.defaultModule = self.get('main', 'default_module')
        try:
            self.dbport = self.getint("database", "dbport")
        except NoOptionError:
            # We will use the default db driver port
            self.dbport = None
        if self.has_option("database", "dbpoolrecycle"):
            self.dbpoolrecycle = self.getint("database", "dbpoolrecycle")
        if self.has_option("database", "dbpoolsize"):
            self.dbpoolsize = self.getint("database", "dbpoolsize")

        if self.has_option("database", "dbsslenable"):
            self.dbsslenable = self.getboolean("database", "dbsslenable")
            if self.dbsslenable:
                self.dbsslca = self.get("database", "dbsslca")
                self.dbsslcert = self.get("database", "dbsslcert")
                self.dbsslkey = self.get("database", "dbsslkey")

        try:
            self.dbdebug = logging._levelNames[self.get("database", "dbdebug")]
        except:
            self.dbdebug = logging.ERROR

        if self.has_section("querymanager"):
            if self.has_option("querymanager", "activate"):
                self.dyngroup_activate = self.getboolean("querymanager", "activate")

        if self.has_option("main", "max_elements_for_static_list"):
            self.maxElementsForStaticList = self.get("main", "max_elements_for_static_list")

    def setDefault(self):
        """
        Set default values
        """
        PluginConfig.setDefault(self)
        self.dbsslenable = False
        self.dbpoolrecycle = 60
        self.dbpoolsize = 5

