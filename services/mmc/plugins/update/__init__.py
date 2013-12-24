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
Update plugin for the MMC agent
"""
import logging
import time
import os
from datetime import datetime
import xml.etree.ElementTree as ET

logger = logging.getLogger()

from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.core.tasks import TaskManager
from mmc.plugins.update.config import updateConfig
from mmc.plugins.update.database import updateDatabase

VERSION = "0.0.0"
APIVERSION = "0:1:0"
REVISION = ""

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION


def activate():
    config = updateConfig("update")
    if config.disabled:
        logger.warning("Plugin UpdateMgr: disabled by configuration.")
        return False
    if not updateDatabase().activate(config):
        logger.error("UpdateMgr database not activated")
        return False
    return True

def calldb(func, *args, **kw):
    return getattr(updateDatabase(), func).__call__(*args, **kw)

def get_os_classes(params):
    return updateDatabase().get_os_classes(params)

def get_update_types(params):
    return updateDatabase().get_update_types(params)

def get_updates(params):
    return updateDatabase().get_updates(params)

def set_update_status(update_id, status):
    return updateDatabase().set_update_status(update_id, status)

