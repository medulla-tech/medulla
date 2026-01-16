# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
from mmc.support.config import PluginConfig
from pulse2.database.security.config import SecurityDatabaseConfig

class SecurityConfig(PluginConfig, SecurityDatabaseConfig):
    """
    Security plugin configuration.

    Reads from /etc/mmc/plugins/security.ini with optional override
    from /etc/mmc/plugins/security.ini.local
    """

    def __init__(self, name='security', conffile=None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            SecurityDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)
        # Logging
        self.log_level = 'INFO'
        # CVE Central connection
        self.cve_central_url = ''
        self.cve_central_server_id = ''
        self.cve_central_keyAES32 = ''

    def readConf(self):
        PluginConfig.readConf(self)
        SecurityDatabaseConfig.setup(self, self.conffile)

        # [main] section
        self.disable = self.getboolean("main", "disable")
        self.tempdir = self.safe_get("main", "tempdir", "/tmp/mmc-security")
        self.log_level = self.safe_get("main", "log_level", "INFO").upper()

        # [cve_central] section
        if self.has_section("cve_central"):
            self.cve_central_url = self.safe_get("cve_central", "url", "")
            self.cve_central_server_id = self.safe_get("cve_central", "server_id", "")
            self.cve_central_keyAES32 = self.safe_get("cve_central", "keyAES32", "")

    def safe_get(self, section, option, default=''):
        """Get config value with fallback to default"""
        try:
            return self.get(section, option)
        except:
            return default

    def check(self):
        pass

    def is_cve_central_configured(self):
        """Check if CVE Central is properly configured"""
        return bool(self.cve_central_url and
                    self.cve_central_server_id and
                    self.cve_central_keyAES32)

    @staticmethod
    def activate():
        SecurityConfig("security")
        return True
