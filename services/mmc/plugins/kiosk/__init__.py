# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
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

# File : mmc/plugins/kiosk/__init__.py

"""
Plugin to manage the interface with Kiosk
"""
import logging

from mmc.plugins.kiosk.config import KioskConfig
# from mmc.plugins.kiosk import kiosk
from pulse2.version import getVersion, getRevision # pyflakes.ignore
from mmc.plugins.base import ComputerI
from mmc.plugins.base.computers import ComputerManager

# Database
from pulse2.database.kiosk import KioskDatabase


VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################

def getApiVersion():
    return APIVERSION


def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    logger = logging.getLogger()
    config = KioskConfig("kiosk")

    # Registering KioskComputers in ComputerManager
    # ComputerManager().register('kiosk', KioskComputers)

    if config.disable:
        logger.warning("Plugin kiosk: disabled by configuration.")
        return False
    
    if not KioskDatabase().activate(config):
        logger.warning("Plugin kiosk: an error occurred during the database initialization")
        return False
    return True


def get_profiles_list():
    return KioskDatabase().get_profiles_list()


def get_profiles_name_list():
    return KioskDatabase().get_profiles_name_list()

def delete_profile(name):
    return KioskDatabase().delete_profile(name)
