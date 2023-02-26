# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Dyngroup implementation of the profile manager interface
"""

from pulse2.managers.profile import ComputerProfileI
from mmc.plugins.dyngroup.database import DyngroupDatabase

class DyngroupProfile(ComputerProfileI):
    def getProfileByNameImagingServer(self, name, is_uuid):
        return DyngroupDatabase().getProfileByNameImagingServer(name, is_uuid)

    def getProfileByUUID(self, uuid):
        return DyngroupDatabase().getProfileByUUID(uuid)

    def getProfileImagingServerUUID(self, uuid):
        return DyngroupDatabase().getProfileImagingServer(uuid)

    def getComputersProfile(self, uuid):
        return DyngroupDatabase().getComputersProfile(uuid)

    def getProfileContent(self, uuid):
        return DyngroupDatabase().getProfileContent(uuid)

    def addComputersToProfile(self, ctx, computers_UUID, profile_UUID):
        return DyngroupDatabase().addmembers_to_group(ctx, profile_UUID, computers_UUID)

    def delComputersFromProfile(self, computers_UUID, profile_UUID):
        pass

    def getForbiddenComputersUUID(self):
        pass

    # TODO need to be completed
