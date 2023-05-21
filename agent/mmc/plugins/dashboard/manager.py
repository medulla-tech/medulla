# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

from mmc.support.mmctools import SingletonN
from mmc.plugins.dashboard.config import DashboardConfig

logger = logging.getLogger()


class DashboardManager(object, metaclass=SingletonN):
    def __init__(self):
        self.config = DashboardConfig("dashboard")
        self.panel = {}

    def register_panel(self, panel):
        if panel.id not in self.config.disabled_panels:
            logger.debug(f"Registering panel {panel}")
            self.panel[panel.id] = panel
        else:
            logger.info(f"Panel {panel} disabled by configuration")

    def get_panels(self):
        return [name for name, panel in list(self.panel.items())]

    def get_panel_infos(self, panel):
        return self.panel[panel].serialize() if panel in self.panel else False

    def get_panels_infos(self):
        return {name: panel.serialize() for name, panel in list(self.panel.items())}
