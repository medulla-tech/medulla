#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of MMC.
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

import logging
from ConfigParser import NoOptionError
from mmc.support.config import PluginConfig
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.pulse2.group import ComputerGroupManager
from mmc.plugins.pulse2.location import ComputerLocationManager

VERSION = "2.0.0"
APIVERSION = "0:0:0"
REVISION = int("$Rev$".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    config = Pulse2Config("pulse2")
    logger = logging.getLogger()
    if config.disable:
        logger.warning("Plugin pulse2: disabled by configuration.")
        return False
    
    return True


class Pulse2Config(PluginConfig):
    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)
        self.disable = (self.get("main", "disable") == 1)
        logging.getLogger().info(self.disable)


class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s


class RpcProxy(RpcProxyI):
    # groups
    def isdyn_group(self, gid):
        ctx = self.currentContext
        return ComputerGroupManager().isdyn_group(ctx, gid)
        
    def isrequest_group(self, gid):
        ctx = self.currentContext
        return ComputerGroupManager().isrequest_group(ctx, gid)
        
    def requestresult_group(self, gid, min, max, filter):
        ctx = self.currentContext
        return ComputerGroupManager().requestresult_group(ctx, gid, min, max, filter)
        
    def result_group(self, gid, min, max, filter):
        ctx = self.currentContext
        return ComputerGroupManager().result_group(ctx, gid, min, max, filter)

    # Locations
    def getUserLocations(self):
        ctx = self.currentContext
        return ComputerLocationManager().getUserLocations(ctx.userid)


def displayLocalisationBar():
    return False
