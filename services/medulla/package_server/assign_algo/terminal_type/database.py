# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from medulla.database.inventory import Inventory
from sqlalchemy.orm import create_session

NB_DB_CONN_TRY = 2


class PluginInventoryAADatabase(Inventory):
    def getMachineType(self, uuid):
        session = create_session()
        ret = self.__getMachineType(uuid, session)
        session.close()
        return ret

    def getMachinesType(self, uuids):
        session = create_session()
        ret = []
        for uuid in uuids:
            ret.append(self.__getMachineType(uuid, session))
        session.close()
        return ret

    def __getMachineType(self, uuid, session):
        query = session.query(self.klass["Registry"])
        query = query.select_from(
            self.table["Registry"]
            .join(self.table["hasRegistry"])
            .join(self.table["nomRegistryPath"])
            .join(self.machine)
            .join(self.inventory)
        )
        query = (
            query.filter(self.inventory.c.Last == 1)
            .filter(self.machine.c.id == fromUUID(uuid))
            .filter(self.table["nomRegistryPath"].c.Path == "terminalType")
            .first()
        )
        if query is None:
            return None
        return query.Value

    def buildPopulateCacheQuery(self):
        session = create_session()
        result = (
            session.query(self.klass["Registry"])
            .add_column(self.machine.c.Name)
            .add_column(self.machine.c.id)
            .add_column(self.table["hasRegistry"].c.inventory.label("inventoryid"))
            .add_column(self.inventory.c.Date)
        )
        selectfrom = (
            self.machine.outerjoin(self.table["hasRegistry"])
            .join(self.inventory)
            .join(self.table["Registry"])
            .join(self.table["nomRegistryPath"])
        )
        result = result.select_from(selectfrom).filter(self.inventory.c.Last == 1)
        result = result.filter(self.table["nomRegistryPath"].c.Path == "terminalType")
        return result


def toUUID(
    id,
):  # TODO : change this method to get a value from somewhere in the db, depending on a config param
    return "UUID%s" % (str(id))


def fromUUID(uuid):
    return int(uuid.replace("UUID", ""))
