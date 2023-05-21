# SPDX-FileCopyrightText: 2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Pulse2 implementation of the pulse2 interface
"""

from pulse2.managers.pulse import Pulse2I
from pulse2.database.pulse import Pulse2Database


class Pulse2Pulse2Manager(Pulse2I):
    def getPackageServerEntityByPackageServer(self, ps_uuid):
        ret = Pulse2Database().getPackageServerEntityByPackageServer(ps_uuid)
        return ret.toH()

    def getPackageServerEntityByEntity(self, e_uuid):
        ret = Pulse2Database().getPackageServerEntityByEntity(e_uuid)
        return ret.toH()

    def getPackageServerEntityByEntities(self, e_uuids):
        ret = Pulse2Database().getPackageServerEntityByEntities(e_uuids)
        for uuid in ret:
            ret[uuid] = [x.toH() for x in ret[uuid]]
        return ret

    def getPackageServerEntity(self, ps_uuid, e_uuid):
        ret = Pulse2Database().getPackageServerEntity(ps_uuid, e_uuid)
        return ret.toH()

    def putPackageServerEntity(self, ps_uuid, e_uuid):
        print("pulse2 > putPackageServerEntity")
        ret = Pulse2Database().putPackageServerEntity(ps_uuid, e_uuid)
        return ret.toH()

    def delPackageServerEntity(self, e_uuid):
        ret = Pulse2Database().delPackageServerEntity(e_uuid)
        return ret
