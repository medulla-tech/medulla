# SPDX-FileCopyrightText: 2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Medulla2 implementation of the medulla interface
"""

from medulla.managers.medulla import Medulla2I
from medulla.database.medulla import Medulla2Database


class Medulla2Medulla2Manager(Medulla2I):
    def getPackageServerEntityByPackageServer(self, ps_uuid):
        ret = Medulla2Database().getPackageServerEntityByPackageServer(ps_uuid)
        return ret.toH()

    def getPackageServerEntityByEntity(self, e_uuid):
        ret = Medulla2Database().getPackageServerEntityByEntity(e_uuid)
        return ret.toH()

    def getPackageServerEntityByEntities(self, e_uuids):
        ret = Medulla2Database().getPackageServerEntityByEntities(e_uuids)
        for uuid in ret:
            ret[uuid] = [x.toH() for x in ret[uuid]]
        return ret

    def getPackageServerEntity(self, ps_uuid, e_uuid):
        ret = Medulla2Database().getPackageServerEntity(ps_uuid, e_uuid)
        return ret.toH()

    def putPackageServerEntity(self, ps_uuid, e_uuid):
        print("medulla > putPackageServerEntity")
        ret = Medulla2Database().putPackageServerEntity(ps_uuid, e_uuid)
        return ret.toH()

    def delPackageServerEntity(self, e_uuid):
        ret = Medulla2Database().delPackageServerEntity(e_uuid)
        return ret
