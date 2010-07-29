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

"""
Configuration class for the inventory MMC agent plugin.
"""

from pulse2.database.inventory.config import InventoryDatabaseConfig
from mmc.plugins.inventory.utilities import getInventoryParts
from mmc.support import mmctools

class InventoryConfig(InventoryDatabaseConfig):
    disable = True
    expert_mode = {}
    graph = {}
    software_filter = []

    def init(self, name = 'inventory', conffile = None):
        self.dbsection = "inventory"
        self.name = name
        if not conffile: self.conffile = mmctools.getConfigFile(name)
        else: self.conffile = conffile

        InventoryDatabaseConfig.setup(self, self.conffile)
        self.setup(self.conffile)

    def setup(self, conf_file):
        self.disable = self.cp.getboolean("main", "disable")
        for i in getInventoryParts():
            try:
                self.graph[i] = self.cp.get("graph", i).split('|')
            except:
                self.graph[i] = []
            try:
                self.expert_mode[i] = self.cp.get("expert_mode", i).split('|')
            except:
                self.expert_mode[i] = []

    def getSoftwareFilter(self):
        self.software_filter = self.cp.get("main", "software_filter").split(',')
        return self.software_filter
