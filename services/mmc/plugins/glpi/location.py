#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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
Glpi implementation of the ComputerLocationI Interface
Provide functions to get all user profiles and user locations informations
"""

import logging
from pulse2.managers.location import ComputerLocationI
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.utilities import complete_ctx

class GlpiLocation(ComputerLocationI):
    def init(self, config):
        self.logger = logging.getLogger()
        self.config = config
        return Glpi().activate()

    def getUserProfile(self, userid):
        return Glpi().getUserProfile(userid)

    def getUserParentLocations(self, userid):
        return map(lambda l: l.toH(), Glpi().getUserParentLocations(userid))

    def getUserLocations(self, userid):
        return map(lambda l: l.toH(), Glpi().getUserLocations(userid))

    def doesUserHaveAccessToMachine(self, ctx, machine_uuid):
        if not hasattr(ctx, 'locations'):
            complete_ctx(ctx)
        return Glpi().doesUserHaveAccessToMachine(ctx, machine_uuid)

    def doesUserHaveAccessToMachines(self, ctx, machine_uuid, all = True):
        if not hasattr(ctx, 'locations'):
            complete_ctx(ctx)
        return Glpi().doesUserHaveAccessToMachines(ctx, machine_uuid, all)

    def displayLocalisationBar(self):
        return self.config.displayLocalisationBar

    def getLocationsCount(self):
        return Glpi().getLocationsCount()

    def getUsersInSameLocations(self, userid):
        return Glpi().getUsersInSameLocations(userid)

    def getMachinesLocations(self, machine_uuids):
        return Glpi().getMachinesLocations(machine_uuids)

    def getLocationsFromPathString(self, location_path):
        return Glpi().getLocationsFromPathString(location_path)

    def getLocationParentPath(self, loc_uuid):
        return Glpi().getLocationParentPath(loc_uuid)

