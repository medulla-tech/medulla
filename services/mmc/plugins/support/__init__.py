# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2014 Mandriva, http://www.mandriva.com
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

""" Product manager plugin base """

import logging

from pulse2.version import getVersion, getRevision # pyflakes.ignore

from mmc.plugins.dashboard.manager import DashboardManager
from mmc.plugins.support.config import SupportConfig
from mmc.plugins.support.panel import RemoteSupportPanel
from mmc.plugins.support.process import TunnelBuilder

APIVERSION = "0:1:0"
NAME = "support"

def getApiVersion(): return APIVERSION


def activate():
    config = SupportConfig(NAME)
    if config.disabled:
        logging.getLogger().warning("Plugin Support: disabled by configuration.")
        return False

    DM = DashboardManager()
    DM.register_panel(RemoteSupportPanel("remotesupport"))
    return True


config = SupportConfig(NAME)
builder = TunnelBuilder(config)

def open():
    return builder.open()

def close():
    return builder.close()

def established():
    return builder.established

def get_port():
    return builder.port





