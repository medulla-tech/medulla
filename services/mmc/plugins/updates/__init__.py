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

# File : mmc/plugins/updates/__init__.py

from pulse2.version import getVersion, getRevision # pyflakes.ignore
# Au cas où on souhaite appeler des configs d'autres modules
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.updates.config import UpdatesConfig

# import pour la database
from pulse2.database.updates import UpdatesDatabase

from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
import logging

VERSION = "1.0.0"
APIVERSION = "1:0:0"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################

def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = UpdatesConfig("updates")

    if config.disable:
        logger.warning("Plugin updates: disabled by configuration.")
        return False

    if not UpdatesDatabase().activate(config):
        logger.warning("Plugin updates: an error occurred during the database initialization")
        return False
    return True

def tests():
    return UpdatesDatabase().tests()

def test_xmppmaster():
    return UpdatesDatabase().test_xmppmaster()

def get_grey_list(start, end, filter=""):
    return UpdatesDatabase().get_grey_list(start, end, filter)

def get_white_list(start, end, filter=""):
    return UpdatesDatabase().get_white_list(start, end, filter)

def get_black_list(start, end, filter=""):
    return UpdatesDatabase().get_black_list(start, end, filter)

def get_family_list(start, end, filter=""):
    return UpdatesDatabase().get_family_list(start, end, filter)

def approve_update(updateid):
    return UpdatesDatabase().approve_update(updateid)

def grey_update(updateid, enabled=0):
    return UpdatesDatabase().grey_update(updateid, enabled)

def exclude_update(updateid):
    return UpdatesDatabase().exclude_update(updateid)

def get_count_machine_as_not_upd(updateid):
    return UpdatesDatabase().get_count_machine_as_not_upd(updateid)

def delete_rule(id):
     return UpdatesDatabase().delete_rule(id)

def white_unlist_update(updateid):
    return UpdatesDatabase().white_unlist_update(updateid)

def get_machine_with_update(kb):
    return Glpi().get_machine_with_update(kb)
