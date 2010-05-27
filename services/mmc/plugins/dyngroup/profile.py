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
Dyngroup implementation of the profile manager interface
"""

from pulse2.managers.profile import ComputerProfileI
from mmc.plugins.dyngroup.database import DyngroupDatabase

class DyngroupProfile(ComputerProfileI):
    def getProfileByUUID(self, uuid):
        return DyngroupDatabase().getProfileByUUID(uuid)

    def getProfileImagingServerUUID(self, uuid):
        return DyngroupDatabase().getProfileImagingServer(uuid)

    def getComputersProfile(self, uuid):
        return DyngroupDatabase().getComputersProfile(uuid)

    def getProfileContent(self, uuid):
        return DyngroupDatabase().getProfileContent(uuid)

    def addComputersToProfile(self, computers_UUID, profile_UUID):
        pass

    def delComputersFromProfile(self, computers_UUID, profile_UUID):
        pass

    def getForbiddenComputersUUID(self):
        pass

    # TODO need to be completed
