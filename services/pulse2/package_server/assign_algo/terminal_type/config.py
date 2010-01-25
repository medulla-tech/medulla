#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
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

import re
from pulse2.database.inventory.config import InventoryDatabaseConfigSkel

#if sys.platform != "win32":
#    import pwd
#    import grp
#    import string
#    # MMC
#    from mmc.support.config import MMCConfigParser

class PluginInventoryAAConfig(InventoryDatabaseConfigSkel):
    type2url = {}
    dbsection = 'main'

    def setup(self, config_file):
        InventoryDatabaseConfigSkel.setup(self, config_file)
                                
        ## Load configuration file
        #if sys.platform != "win32":
        #    self.cp = MMCConfigParser()
        #else:
        #    self.cp = ConfigParser.ConfigParser()
        #self.cp.read(config_file)

        for section in self.cp.sections():
            m = re.compile('^associations:(?P<index>[0-9]+)$').match(section)
            if m:
                index = m.group('index')
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
                        self.type2url[type][kind] = {}
                    self.type2url[type][kind][index] = url
        if len(self.type2url.keys()) == 0:
            raise Exception("Please put some associations in your config file")

        for type in self.type2url:
            for kind in self.type2url[type]:
                sorted = []
                keys = self.type2url[type][kind].keys()
                keys.sort()
                for index in keys:
                    sorted.append(self.type2url[type][kind][index])
                self.type2url[type][kind] = sorted

