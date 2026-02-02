# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
MMC Dashboard
"""

import logging

from mmc.plugins.dashboard.manager import DashboardManager
from mmc.plugins.dashboard.config import DashboardConfig
from mmc.plugins.dashboard.panel import (
    GeneralPanel,
    SpacePanel,
    ShortcutsPanel,
    ProcessPanel,
    ComputersOnlinePanel,
    UpdatePanel,
    BackupPanel,
    SuccessRatePanel,
    DeploymentsLaunchedPanel,
    AgentsPanel,
    AlertsPanel,
)

VERSION = "5.4.6"
APIVERSION = "0:1:0"
REVISION = ""

logger = logging.getLogger()


def getVersion():
    return VERSION


def getApiVersion():
    return APIVERSION


def getRevision():
    return REVISION


def activate():
    config = DashboardConfig("dashboard")
    if config.disabled:
        logger.warning("Plugin dashboard: disabled by configuration.")
        return False
    DM = DashboardManager()
    DM.register_panel(GeneralPanel("general"))
    DM.register_panel(SpacePanel("space"))
    DM.register_panel(ShortcutsPanel("shortcuts"))
    DM.register_panel(ProcessPanel("process"))
    DM.register_panel(ComputersOnlinePanel("computersOnline"))
    DM.register_panel(BackupPanel("backup"))
    DM.register_panel(UpdatePanel("product_updates"))
    DM.register_panel(SuccessRatePanel("successRate"))
    DM.register_panel(DeploymentsLaunchedPanel("deploymentsLaunched"))
    DM.register_panel(AgentsPanel("agents"))
    DM.register_panel(AlertsPanel("alerts"))
    return True


# XML-RPC methods
def get_panels():
    return DashboardManager().get_panels()


def get_panel_infos(panel):
    return DashboardManager().get_panel_infos(panel)


def get_panels_infos():
    return DashboardManager().get_panels_infos()
