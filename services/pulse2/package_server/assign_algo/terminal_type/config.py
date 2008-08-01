#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: __init__.py 3 2008-03-03 14:35:11Z cdelfosse $
#
# This file is part of MMC.
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

from pulse2.package_server.utilities import Singleton
from mmc.support.config import PluginConfig
import logging
import sys
import re

if sys.platform != "win32":
    import pwd
    import grp
    import string
    # MMC
    from mmc.support.config import MMCConfigParser

class PluginInventoryAAConfig(Singleton):
    dbdriver = "mysql"
    dbhost = "localhost"
    dbname = "inventory"
    dbuser = "mmc"
    dbpasswd = "mmc"
    dbpoolrecycle = None
    dbport = None
    dbsslenable = False
    dbsslca = ''
    dbsslcert = ''
    dbsslkey = ''
    type2url = {}

    def setup(self, config_file):
        # Load configuration file
        if sys.platform != "win32":
            self.cp = MMCConfigParser()
        else:   
            self.cp = ConfigParser.ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option("main", "dbdriver"):
            self.dbdriver = self.cp.get("main", "dbdriver")
        if self.cp.has_option("main", "dbhost"):
            self.dbhost = self.cp.get("main", "dbhost")
        if self.cp.has_option("main", "dbname"):
            self.dbname = self.cp.get("main", "dbname")
        if self.cp.has_option("main", "dbuser"):
            self.dbuser = self.cp.get("main", "dbuser")
        if self.cp.has_option("main", "dbpasswd"):
            self.dbpasswd = self.cp.getpassword("main", "dbpasswd")
        if self.cp.has_option("main", "dbpoolrecycle"):
            self.dbpoolrecycle = self.cp.getint("main", "dbpoolrecycle")

        if self.cp.has_option("main", "dbport"):
            self.dbport = self.cp.getint("main", "dbport")

        if self.cp.has_option("main", "dbsslenable"):
            self.dbsslenable = self.cp.getboolean("main", "dbsslenable")
            if self.dbsslenable:
                self.dbsslca = self.cp.get("main", "dbsslca")
                self.dbsslcert = self.cp.get("main", "dbsslcert")
                self.dbsslkey = self.cp.get("main", "dbsslkey")

        for section in self.cp.sections():
            if re.compile('^associations:[0-9]+$').match(section):
                if not self.cp.has_option(section, 'terminal_types'):
                    continue
                if not self.cp.has_option(section, 'mirror'):
                    continue
                if not self.cp.has_option(section, 'kind'):
                    continue
                
                types = self.cp.get(section, 'terminal_types').split('||')
                url = self.cp.get(section, 'mirror')
                kind = self.cp.get(section, 'kind')
                for type in types:
                    if not self.type2url.has_key(type):
                        self.type2url[type] = {}
                    if not self.type2url[type].has_key(kind):
                        self.type2url[type][kind] = []
                    self.type2url[type][kind].append(url)
        if len(self.type2url.keys()) == 0:
            raise Exception("Please put some associations in your config file")
                    
