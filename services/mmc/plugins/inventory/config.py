# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
        try:
            self.software_filter = self.cp.get("main", "software_filter").split(',')
        except:
            pass
        return self.software_filter
