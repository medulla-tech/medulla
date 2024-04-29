# SPDX-FileCopyrightText: 2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Imaging implementation of the medulla interface
It only implement the write methods!
"""

from medulla.managers.medulla import Medulla2I
from medulla.database.imaging import ImagingDatabase


class ImagingMedulla2Manager(Medulla2I):
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
        ImagingDatabase().updateImagingServer(
            ims[0].getUUID(), {"fk_entity": entity.id}
        )
