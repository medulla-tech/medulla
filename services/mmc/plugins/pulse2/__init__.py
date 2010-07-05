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

"""
Pulse2 mmc-agent plugin
give a central access to the Managers that can be needed by pulse2 modules
"""

# SqlAlchemy
from sqlalchemy.exceptions import SQLError
import sqlalchemy.orm.query

import logging
from mmc.support.config import PluginConfig
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext, xmlrpcCleanup
from mmc.agent import PluginManager
from pulse2.managers.group import ComputerGroupManager
from pulse2.managers.location import ComputerLocationManager
from pulse2.managers.imaging import ComputerImagingManager
from pulse2.database.pulse.config import Pulse2DatabaseConfig
from pulse2.database.pulse import Pulse2Database
from pulse2.managers.pulse import Pulse2Manager
from mmc.plugins.pulse2.pulse import Pulse2Pulse2Manager

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
    if not Pulse2Database().activate(config):
        logger.warning("Plugin pulse2: an error occurred during the database initialization")
        return False

    Pulse2Manager().register('pulse2', Pulse2Pulse2Manager)
    updateQueryClass()
    return True

def activate_2():
    config = Pulse2Config("pulse2")
    try:
        ComputerLocationManager().select(config.location)
    except Exception, e:
        logging.getLogger().error(e)
        return False
    return True

def updateQueryClass():
    """
    Our fix for SQLAlchemy behaviour with MySQL
    Sometimes we lost the connection to the MySQL Server, even on a local
    server.
    """
    q = sqlalchemy.orm.query.Query
    for m in ['first', 'count', 'all', '__iter__']:
        setattr(q, '_old_'+m, getattr(q, m))
        setattr(q, m, create_method(m))

def create_method(m):
    def method(self, already_in_loop = False):
        NB_DB_CONN_TRY = 2
        NORESULT = "__noresult__"
        ret = NORESULT
        try:
            old_m = getattr(self, '_old_'+m)
            ret = old_m()
        except SQLError, e:
            reconnect = False
            if e.orig.args[0] == 2013 and not already_in_loop: # Lost connection to MySQL server during query error
                logging.getLogger().warn("SQLError Lost connection")
                reconnect = True
            elif e.orig.args[0] == 2006 and not already_in_loop: # MySQL server has gone away
                logging.getLogger().warn("SQLError MySQL server has gone away")
                reconnect = True
            if reconnect:
                for i in range(0, NB_DB_CONN_TRY):
                    logging.getLogger().warn("Trying to recover the connection (try #%d on %d)" % (i + 1, NB_DB_CONN_TRY + 1))
                    new_m = getattr(self, m)
                    try:
                        ret = new_m(True)
                        break
                    except Exception, e:
                        # Try again
                        continue
            if ret != NORESULT:
                return ret
            raise e
        return ret
    return method

class Pulse2Config(PluginConfig, Pulse2DatabaseConfig):
    location = None
    def __init__(self, name = 'pulse2', conffile = None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            Pulse2DatabaseConfig.__init__(self)
            self.initdone = True

    def readConf(self):
        """
        Read the module configuration
        """
        PluginConfig.readConf(self)
        self.disable = self.getboolean("main", "disable")
        Pulse2DatabaseConfig.setup(self, self.conffile)

        if self.has_option("main", "location"):
            self.location = self.get("main", "location")

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s


class RpcProxy(RpcProxyI):
    # groups
    def isdyn_group(self, gid):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerGroupManager().isdyn_group(ctx, gid))

    def isrequest_group(self, gid):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerGroupManager().isrequest_group(ctx, gid))

    def requestresult_group(self, gid, min, max, filter):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerGroupManager().requestresult_group(ctx, gid, min, max, filter))

    def result_group(self, gid, min, max, filter):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerGroupManager().result_group(ctx, gid, min, max, filter))

    # Locations
    def getUserLocations(self):
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerLocationManager().getUserLocations(ctx.userid))

    # Profiles
    def isImagingInProfilePossible(self):
        """
        tell if the profiles can access imaging

        @returns: True if the profiles can access imaging
        @rtype: boolean
        """
        return ComputerImagingManager().isImagingInProfilePossible()

    def areProfilesPossible(self):
        """
        profiles are possible only if the imaging plugin is enable
        """
        # maybe we can add something in the configuration of dyngroup to say if we want or not profiles
        return PluginManager().isEnabled("imaging")

    def getAllImagingServersForProfiles(self, associated = False):
        """
        get all the imaging server that this user can access
        """
        ctx = self.currentContext
        return ComputerImagingManager().getAllImagingServers(ctx.userid, associated)


def displayLocalisationBar():
    return xmlrpcCleanup(ComputerLocationManager().displayLocalisationBar())
