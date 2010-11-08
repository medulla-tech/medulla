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
Imaging implementation of the profile manager interface
it only implement the client part
"""

from mmc.plugins.imaging.functions import synchroComputers
from pulse2.managers.profile import ComputerProfileI
from pulse2.database.imaging import ImagingDatabase
from pulse2.database.imaging.types import P2IT, P2ISS
from pulse2.managers.profile import ComputerProfileManager

class ImagingProfile(ComputerProfileI):
    def addComputersToProfile(self, ctx, computers, profile_UUID):
        # TODO need to put the menu and synchronize
        if ImagingDatabase().isTargetRegister(profile_UUID, P2IT.PROFILE):
            ret1 = ImagingDatabase().putComputersInProfile(profile_UUID, computers)
            ret2 = ImagingDatabase().changeTargetsSynchroState([profile_UUID], P2IT.PROFILE, P2ISS.TODO)
            ret3 = ImagingDatabase().changeTargetsSynchroState(computers, P2IT.COMPUTER, P2ISS.TODO)

            computers_UUID = map(lambda c:c['uuid'], computers.values())

            def treatResult(result, ret): return result and ret
            d = synchroComputers(ctx, computers_UUID, P2IT.COMPUTER_IN_PROFILE)
            d.addCallback(treatResult, ret1 and ret2 and ret3)
            return d
        return True

    def delComputersFromProfile(self, computers_UUID, profile_UUID):
        # TODO need to remove the menu and the registering
        if ImagingDatabase().isTargetRegister(profile_UUID, P2IT.PROFILE):
            # put all the computers to their own menu
            ret1 = ImagingDatabase().delComputersFromProfile(profile_UUID, computers_UUID)
            ret2 = ImagingDatabase().changeTargetsSynchroState([profile_UUID], P2IT.PROFILE, P2ISS.TODO)
            return ret1 and ret2
        return True

    def delProfile(self, profile_UUID):
        if ImagingDatabase().isTargetRegister(profile_UUID, P2IT.PROFILE):
            # TODO : put all the computers on their own menu
            computers_UUID = map(lambda c:c.uuid, ComputerProfileManager().getProfileContent(profile_UUID))
            computers = {}
            for uuid in computers_UUID:
                computers[uuid] = {'uuid':uuid}

            ret1 = ImagingDatabase().delComputersFromProfile(profile_UUID, computers)
            ret2 = ImagingDatabase().changeTargetsSynchroState(computers_UUID, P2IT.COMPUTER, P2ISS.TODO)
            # delete the profile itself
            ret3 = ImagingDatabase().delProfile(profile_UUID)

            return ret1 and ret2 and ret3
        return True

    def getForbiddenComputersUUID(self, profile_UUID = None):
        return ImagingDatabase().getForbiddenComputersUUID(profile_UUID)

    def areForbiddebComputers(self, computer_UUID):
        return ImagingDatabase().areForbiddebComputers(computer_UUID)
