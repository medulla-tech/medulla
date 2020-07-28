# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

import logging

from mmc.support.mmctools import SingletonN
from mmc.plugins.dashboard.config import DashboardConfig

logger = logging.getLogger()


class DashboardManager(object):
    __metaclass__ = SingletonN

    def __init__(self):
        self.config = DashboardConfig("dashboard")
        self.panel = {}

    def register_panel(self, panel):
        if not panel.id in self.config.disabled_panels:
            logger.debug("Registering panel %s" % panel)
            self.panel[panel.id] = panel
        else:
            logger.info("Panel %s disabled by configuration" % panel)

    def get_panels(self):
        return [ name for name, panel in self.panel.items() ]

    def get_panel_infos(self, panel):
        if panel in self.panel:
            return self.panel[panel].serialize()
        else:
            return False

    def get_panels_infos(self):
        infos = {}
        for name, panel in self.panel.items():
            infos[name] = panel.serialize()
        return infos
