# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

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
            ret2 = ImagingDatabase().changeTargetsSynchroState(
                [profile_UUID], P2IT.PROFILE, P2ISS.TODO
            )
            ret3 = ImagingDatabase().changeTargetsSynchroState(
                computers, P2IT.COMPUTER, P2ISS.TODO
            )

            computers_UUID = [c["uuid"] for c in list(computers.values())]

            def treatResult(result, ret):
                return result and ret

            d = synchroComputers(ctx, computers_UUID, P2IT.COMPUTER_IN_PROFILE)
            d.addCallback(treatResult, ret1 and ret2 and ret3)
            return d
        return True

    def delComputersFromProfile(self, computers_UUID, profile_UUID):
        # TODO need to remove the menu and the registering
        if ImagingDatabase().isTargetRegister(profile_UUID, P2IT.PROFILE):
            # put all the computers to their own menu

            ret1 = ImagingDatabase().delComputersFromProfile(
                profile_UUID, computers_UUID
            )
            ret2 = ImagingDatabase().changeTargetsSynchroState(
                [profile_UUID], P2IT.PROFILE, P2ISS.TODO
            )

            return ret1 and ret2
        return True

    def delProfile(self, profile_UUID):
        if ImagingDatabase().isTargetRegister(profile_UUID, P2IT.PROFILE):
            # TODO : put all the computers on their own menu
            computers_UUID = [
                c.uuid for c in ComputerProfileManager().getProfileContent(profile_UUID)
            ]
            computers = {}
            for uuid in computers_UUID:
                computers[uuid] = {"uuid": uuid}

            ret1 = (
                len(computers) > 0
                and ImagingDatabase().delComputersFromProfile(profile_UUID, computers)
                or True
            )
            ret2 = (
                len(computers) > 0
                and ImagingDatabase().changeTargetsSynchroState(
                    computers_UUID, P2IT.COMPUTER, P2ISS.TODO
                )
                or True
            )
            # delete the profile itself
            ret3 = ImagingDatabase().delProfile(profile_UUID)
            ret4 = (
                len(computers) > 0
                and ImagingDatabase().switchMenusToDefault(computers_UUID)
                or True
            )

            return ret1 and ret2 and ret3 and ret4
        return True

    def getForbiddenComputersUUID(self, profile_UUID=None):
        return ImagingDatabase().getForbiddenComputersUUID(profile_UUID)

    def areForbiddebComputers(self, computer_UUID):
        return ImagingDatabase().areForbiddebComputers(computer_UUID)
