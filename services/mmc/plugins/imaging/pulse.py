# SPDX-FileCopyrightText: 2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
