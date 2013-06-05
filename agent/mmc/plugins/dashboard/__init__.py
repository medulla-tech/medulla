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

"""
MMC Dashboard
"""

import logging

from mmc.plugins.dashboard.manager import DashboardManager
from mmc.plugins.dashboard.config import DashboardConfig
from mmc.plugins.dashboard.panel import GeneralPanel, SpacePanel, ShortcutsPanel

VERSION = "3.1.0"
APIVERSION = "0:1:0"
REVISION = ""

logger = logging.getLogger()

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    config = DashboardConfig("dashboard")
    if config.disabled:
        logger.warning("Plugin dashboard: disabled by configuration.")
        return False
    DM = DashboardManager()
    DM.register_panel(GeneralPanel("general"))
    DM.register_panel(SpacePanel("space"))
    DM.register_panel(ShortcutsPanel("shortcuts"))
    return True


# XML-RPC methods
def get_panels():
    return DashboardManager().get_panels()

def get_panel_infos(panel):
    return DashboardManager().get_panel_infos(panel)

def get_panels_infos():
    return DashboardManager().get_panels_infos()
