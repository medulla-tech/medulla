# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from mmc.support import mmctools
from mmc.support.config import PluginConfig
from pulse2.database.dyngroup.config import DyngroupDatabaseConfig


class DGConfig(DyngroupDatabaseConfig):
    dyngroup_activate = True
    defaultModule = ""
    maxElementsForStaticList = 2000
    profilesEnable = True
    check_db_enable = False
    check_db_interval = 300

    def init(self, name, conffile=None):
        self.name = name
        if not conffile:
            self.conffile = mmctools.getConfigFile(name)
        else:
            self.conffile = conffile

        DyngroupDatabaseConfig.setup(self, self.conffile)
        self.setup(self.conffile)

    def setup(self, conf_file):
        """
        Read the module configuration
        """
        self.disable = self.cp.getboolean("main", "disable")
        self.dynamicEnable = self.cp.getboolean("main", "dynamic_enable")
        if self.cp.has_option("main", "profiles_enable"):
            self.profilesEnable = self.cp.getboolean("main", "profiles_enable")
        if self.cp.has_option("main", "default_module"):
            self.defaultModule = self.cp.get("main", "default_module")

        if self.cp.has_option("main", "max_elements_for_static_list"):
            self.maxElementsForStaticList = self.cp.get(
                "main", "max_elements_for_static_list"
            )

        if self.cp.has_section("querymanager"):
            if self.cp.has_option("querymanager", "activate"):
                self.dyngroup_activate = self.cp.getboolean("querymanager", "activate")

        if self.cp.has_option("main", "check_db_enable"):
            self.check_db_enable = self.cp.getboolean("main", "check_db_enable")
        if self.cp.has_option("main", "check_db_interval"):
            self.check_db_interval = self.cp.getint("main", "check_db_interval")

    def setDefault(self):
        """
        Set default values
        """
        PluginConfig.setDefault(self)
        self.dbsslenable = False
        self.dbpoolrecycle = 60
        self.dbpoolsize = 5
