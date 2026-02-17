# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.support.config import PluginConfig
from pulse2.database.mobile.config import MobileDatabaseConfig

class MobileConfig(PluginConfig, MobileDatabaseConfig):
    def __init__(self, name='mobile', conffile=None, backend='database'):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile, backend=backend, db_table='mobile_conf')
            MobileDatabaseConfig.__init__(self)
            self.initdone = True

    def setDefault(self):
        PluginConfig.setDefault(self)

    def readConf(self):
        """
        Read the module configuration (from DB backend or INI file).
        """
        PluginConfig.readConf(self)
        if self.backend == 'database':
            # read DB settings from admin DB backend
            self._load_db_settings_from_backend()
        elif self.conffile and self.backend == 'ini':
            # read DB settings from INI file
            MobileDatabaseConfig.setup(self, self.conffile)

        self.disable = self.getboolean('main', 'disable')
        self.tempdir = self.get('main', 'tempdir')

        self.hmdm_url = self.get('hmdm', 'url') if self.has_option('hmdm', 'url') else None
        self.hmdm_login = self.get('hmdm', 'login') if self.has_option('hmdm', 'login') else None
        self.hmdm_password = self.get('hmdm', 'password') if self.has_option('hmdm', 'password') else None

    def check(self):
        pass

    @staticmethod
    def activate():
        # Initialize config using database backend by default
        MobileConfig('mobile', None, 'database')
        return True
