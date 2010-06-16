#
# (c) 2010 Mandriva, http://www.mandriva.com/
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
Imaging implementation of the pulse2 interface
It only implement the write methods!
"""

from pulse2.managers.pulse import Pulse2I
from pulse2.database.imaging import ImagingDatabase

class ImagingPulse2Manager(Pulse2I):
    def getPackageServerEntityByPackageServer(self, ps_uuid):
        raise Exception("I won't do that!")

    def getPackageServerEntityByEntity(self, e_uuid):
        raise Exception("I won't do that!")

    def getPackageServerEntityByEntities(self, e_uuids):
        raise Exception("I won't do that!")

    def getPackageServerEntity(self, ps_uuid, e_uuid):
        raise Exception("I won't do that!")

    def putPackageServerEntity(self, ps_uuid, e_uuid):
        ims = ImagingDatabase().getImagingServerByPackageServerUUID(ps_uuid)
        entity = ImagingDatabase().getEntityByUUID(e_uuid)
        ImagingDatabase().updateImagingServer(ims[0].getUUID(), {'fk_entity':entity.id})

