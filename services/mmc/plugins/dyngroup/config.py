# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.support import mmctools
from mmc.support.config import PluginConfig
from pulse2.database.dyngroup.config import DyngroupDatabaseConfig


class DGConfig(PluginConfig, DyngroupDatabaseConfig):
    dyngroup_activate = True
    defaultModule = ""
    maxElementsForStaticList = 500
    profilesEnable = True
    check_db_enable = False
    check_db_interval = 300

    def __init__(self, name, conffile=None, backend="ini"):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table="dyngroup_conf")
            DyngroupDatabaseConfig.__init__(self)
        
        if backend == "database":
            # read DB settings from admin DB backend
            self._load_db_settings_from_backend()
        elif conffile and backend == "ini":
            # read DB settings from INI file
            DyngroupDatabaseConfig.setup(self, self.conffile)
        self.setup(self.conffile)

    def setup(self, conf_file):
        """
        Read the module configuration
        """
        self.disable = self.getboolean("main", "disable")
        self.dynamicEnable = self.getboolean("main", "dynamic_enable")
        if self.has_option("main", "profiles_enable"):
            self.profilesEnable = self.getboolean("main", "profiles_enable")
        if self.has_option("main", "default_module"):
            self.defaultModule = self.get("main", "default_module")

        if self.has_option("main", "max_elements_for_static_list"):
            self.maxElementsForStaticList = self.get(
                "main", "max_elements_for_static_list"
            )

        if self.has_section("querymanager"):
            if self.has_option("querymanager", "activate"):
                self.dyngroup_activate = self.getboolean("querymanager", "activate")

        if self.has_option("main", "check_db_enable"):
            self.check_db_enable = self.getboolean("main", "check_db_enable")
        if self.has_option("main", "check_db_interval"):
            self.check_db_interval = self.getint("main", "check_db_interval")

    def setDefault(self):
        """
        Set default values
        """
        PluginConfig.setDefault(self)
        self.dbsslenable = False
        self.dbpoolrecycle = 60
        self.dbpoolsize = 5