# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
from mmc.support.config import PluginConfig
from pulse2.database.store.config import StoreDatabaseConfig

class StoreConfig(PluginConfig, StoreDatabaseConfig):
    def __init__(self, name='store', conffile=None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            StoreDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)

    def readConf(self):
        PluginConfig.readConf(self)
        StoreDatabaseConfig.setup(self, self.conffile)
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.get("main", "tempdir")
        # Packages directory path
        self.packages_path = self.get("main", "packages_path") if self.has_option("main", "packages_path") else "/var/lib/pulse2/packages"
        # Store API (catalog, subscriptions, packages - all in one)
        self.store_api_url = self.get("store_api", "url") if self.has_option("store_api", "url") else None
        self.store_api_token = self.get("store_api", "api_token") if self.has_option("store_api", "api_token") else None
        self.store_api_timeout = self.getint("store_api", "timeout") if self.has_option("store_api", "timeout") else 15
        self.store_api_skip_ssl = self.getboolean("store_api", "skip_ssl_verify") if self.has_option("store_api", "skip_ssl_verify") else False
        self.client_uuid = self.get("store_api", "client_uuid") if self.has_option("store_api", "client_uuid") else None
        self.lang = self.get("store_api", "lang") if self.has_option("store_api", "lang") else "multi"
        # Script to regenerate packages in Medulla database
        self.generate_package_script = self.get("main", "generate_package_script") if self.has_option("main", "generate_package_script") else "/usr/sbin/pulse2-generation_package.py"

    def check(self):
        pass

    @staticmethod
    def activate():
        StoreConfig("store")
        return True
