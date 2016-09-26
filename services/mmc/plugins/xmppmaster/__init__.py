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
from master.lib.utils import name_random
from  xmppmaster import *
from mmc.plugins.xmppmaster.master.agentmaster import simplecommandxmpp, simplecommandxmpp1, configurationxmpp,callxmppfunction 
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

def getGuacamoleRelayServerMachineUuid(uuid):
    return XmppMasterDatabase().getGuacamoleRelayServerMachineUuid(uuid)

def getListPresenceAgent():
    return ""
    #return XmppMasterDatabase().getListPresenceAgent()

def getListPresenceMachine():
    return XmppMasterDatabase().getListPresenceMachine()

##JFK
def getconfigurationxmpp():
    return configurationxmpp()
#JFK
def xmppapplicationdeployment(*args, **kwargs ):
    return callxmppfunction(*args, **kwargs )

def xmppcommand(cmd,machine):
    data = {
	"action": "shellcommand",
	"sessionid":name_random(8,"mcc_"),
	"data" : {'cmd' : cmd},
	"base64" :False
    }
    a=simplecommandxmpp1(machine, data , 4)
    d = a.t2.join()
    return a.result

def xmppscript(cmd,machine):
    data = {
	"action": "shellcommand",
	"sessionid":name_random(8,"mcc_"),
	"data" : {'cmd' : cmd},
	"base64" :False
    }
    a=simplecommandxmpp1(machine, data , 4)
    d = a.t2.join()
    return a.result


