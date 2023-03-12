# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
MMC services plugin configuration
"""

from mmc.support.config import PluginConfig


class ServicesConfig(PluginConfig):
    def readConf(self):
        PluginConfig.readConf(self)
        self.journalctl_path = self.get("main", "journalctl_path")
        self.services = {}
        for plugin, services in self.items("plugins"):
            self.services[plugin] = services.split(",")
        try:
            self.blacklist = self.get("main", "blacklist").split(",")
        except:
            self.blacklist = []
