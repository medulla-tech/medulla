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
Contains location related classes and methods.
"""

import logging
from pulse2.managers.location import ComputerLocationI
from pulse2.database.inventory import Inventory

class InventoryLocation(ComputerLocationI):
    def init(self, config):
        self.logger = logging.getLogger()
        self.config = config
        return Inventory().activate(config)

    def getUserProfile(self, userid):
        return Inventory().getUserProfile(userid)

    def getUserLocations(self, userid):
        return map(lambda l: convertLocations(l), Inventory().getUserLocations(userid, with_level = True))

    def doesUserHaveAccessToMachine(self, userid, machine_uuid):
        return Inventory().doesUserHaveAccessToMachine(userid, machine_uuid)

    def doesUserHaveAccessToMachines(self, userid, machine_uuid, all = True):
        return Inventory().doesUserHaveAccessToMachines(userid, machine_uuid, all)

    def displayLocalisationBar(self):
        return True

    def getLocationsCount(self):
        return Inventory().getLocationsCount()

    def getUsersInSameLocations(self, userid):
        return Inventory().getUsersInSameLocations(userid)

    def getMachinesLocations(self, machine_uuids):
        return Inventory().getComputersLocations(machine_uuids)

    def getLocationsFromPathString(self, location_path):
        return Inventory().getLocationsFromPathString(location_path)

    def getLocationParentPath(self, loc_uuid):
        return Inventory().getLocationParentPath(loc_uuid)


def convertLocations(hloc):
    location = hloc[0]
    level = hloc[1]
    ret = {
        'name': location.Label,
        'uuid': 'UUID' + str(location.id),
        'level': level
        }
    # Tag the root entity to easily recognize it
    if location.id == 1:
        ret['isrootentity'] = True
    return ret
