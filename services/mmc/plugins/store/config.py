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
        # Client UUID for subscriptions
        self.client_uuid = self.get("client", "uuid") if self.has_option("client", "uuid") else None
        # Kestra webhook configuration (single section, global enabled flag)
        self.kestra_enabled = self.getboolean("kestra", "enabled") if self.has_option("kestra", "enabled") else False
        self.kestra_ai_webhook_url = self.get("kestra", "ai_webhook_url") if self.has_option("kestra", "ai_webhook_url") else None
        self.kestra_sync_webhook_url = self.get("kestra", "sync_webhook_url") if self.has_option("kestra", "sync_webhook_url") else None
        self.kestra_skip_ssl_verify = self.getboolean("kestra", "skip_ssl_verify") if self.has_option("kestra", "skip_ssl_verify") else False

    def check(self):
        pass

    @staticmethod
    def activate():
        StoreConfig("store")
        return True
