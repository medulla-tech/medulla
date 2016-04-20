# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Plugin to manage the interface with xmppmastr
"""
import logging
import os,sys
from mmc.plugins.xmppmaster.config import xmppMasterConfig

from pulse2.version import getVersion, getRevision # pyflakes.ignore
#from mmc.plugins.base import ComputerI
#from mmc.plugins.base.computers import ComputerManager

# Database
from pulse2.database.xmppmaster import XmppMasterDatabase

from  xmppmaster import *

VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################

def getApiVersion():
    return APIVERSION

def dede():
    logging.getLogger().info("test")



def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    logger = logging.getLogger()
    config = xmppMasterConfig("xmppmaster")
    if config.disable:
        logger.warning("Plugin xmppmaster: disabled by configuration.")
        return False
    if not XmppMasterDatabase().activate(config):
        logger.warning("Plugin XmppMaster: an error occurred during the database initialization")
        return False
    return True

# #############################################################
# xmppmaster MAIN FUNCTIONS [HTTP INTERFACE]
# #############################################################

def getPresenceuuid(uuid):
    return XmppMasterDatabase().getPresenceuuid(uuid)

def getGuacamoleRelaisServerMachineUuid(uuid):
    return XmppMasterDatabase().getGuacamoleRelaisServerMachineUuid(uuid)



