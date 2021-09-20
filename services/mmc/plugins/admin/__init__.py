# -*- coding: utf-8; -*-
#
# (c) 2020 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# File : mmc/plugins/admin/__init__.py

from pulse2.version import getVersion, getRevision # pyflakes.ignore
# Au cas où on souhaite appeler des configs d'autres modules
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.admin.config import AdminConfig

# import pour la database
from pulse2.database.admin import AdminDatabase
import logging

VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################

def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = AdminConfig("admin")

    if config.disable:
        logger.warning("Plugin admin: disabled by configuration.")
        return False

    if not AdminDatabase().activate(config):
        logger.warning("Plugin admin: an error occurred during the database initialization")
        return False
    return True
