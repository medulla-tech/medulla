# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from mmc.support.config import PluginConfig


class DashboardConfig(PluginConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        try:
            self.disabled_panels = self.get("main", "disabled_panels").split()
        except:
            self.disabled_panels = []
