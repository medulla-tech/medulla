# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import re
from pulse2.database.inventory.config import InventoryDatabaseConfigSkel

# if sys.platform != "win32":
#    import pwd
#    import grp
#    import string
#    # MMC
#    from mmc.support.config import MMCConfigParser


class PluginInventoryAAConfig(InventoryDatabaseConfigSkel):
    type2url = {}
    dbsection = "main"

    def setup(self, config_file):
        InventoryDatabaseConfigSkel.setup(self, config_file)

        # Load configuration file
        # if sys.platform != "win32":
        #    self.cp = MMCConfigParser()
        # else:
        #    self.cp = ConfigParser.ConfigParser()
        # self.cp.read(config_file)

        for section in self.cp.sections():
            m = re.compile("^associations:(?P<index>[0-9]+)$").match(section)
            if m:
                index = m.group("index")
                if not self.cp.has_option(section, "terminal_types"):
                    continue
                if not self.cp.has_option(section, "mirror"):
                    continue
                if not self.cp.has_option(section, "kind"):
                    continue

                types = self.cp.get(section, "terminal_types").split("||")
                url = self.cp.get(section, "mirror")
                kind = self.cp.get(section, "kind")
                for type in types:
                    if type not in self.type2url:
                        self.type2url[type] = {}
                    if kind not in self.type2url[type]:
                        self.type2url[type][kind] = {}
                    self.type2url[type][kind][index] = url
        if len(list(self.type2url.keys())) == 0:
            raise Exception("Please put some associations in your config file")

        for type in self.type2url:
            for kind in self.type2url[type]:
                sorted = []
                keys = sorted(self.type2url[type][kind].keys())
                for index in keys:
                    sorted.append(self.type2url[type][kind][index])
                self.type2url[type][kind] = sorted
