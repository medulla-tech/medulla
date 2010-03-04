#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id: group.py 5110 2010-01-25 14:26:53Z jpbraun $
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

from pulse2.managers.profile import ComputerProfileI
from pulse2.database.imaging import ImagingDatabase
from pulse2.database.imaging.types import P2IT, P2ISS

class ImagingProfile(ComputerProfileI):
    def addComputersToProfile(self, computers_UUID, profile_UUID):
        ImagingDatabase().changeTargetsSynchroState([profile_UUID], P2IT.PROFILE, P2ISS.TODO)

    def delComputersFromProfile(self, computers_UUID, profile_UUID):
        ImagingDatabase().changeTargetsSynchroState([profile_UUID], P2IT.PROFILE, P2ISS.TODO)

