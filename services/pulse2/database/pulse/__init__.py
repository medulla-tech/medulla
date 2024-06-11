# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Pulse2 database handler
"""

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Text
from sqlalchemy.orm import create_session, mapper
from sqlalchemy.sql import and_
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.automap import automap_base


# PULSE2 modules
# from mmc.database.database_helper import DBObject
from mmc.database import database_helper
from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper

# Imported last
import logging


class Pulse2Database(DyngroupDatabaseHelper):
    """
    Singleton Class to query the pulse2 database.

    """

    is_activated = False

    def db_check(self):
        self.my_name = "pulse2"
        self.configfile = "medulla_server.ini"
        return DyngroupDatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("Pulse2 database is connecting")
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
        )
        self.metadata = MetaData(self.db)

        Base = automap_base()
        Base.prepare(self.db, reflect=True)

        # Only federated tables (beginning by local_) are automatically mapped
        # If needed, excludes tables from this list
        exclude_table = []
        # Dynamically add attributes to the object for each mapped class
        for table_name, mapped_class in Base.classes.items():
            if table_name in exclude_table:
                continue
            if table_name.startswith("local"):
                setattr(self, table_name.capitalize(), mapped_class)

        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.session = create_session()
        self.is_activated = True
        self.logger.debug(
            "Pulse2 database connected (version:%s)"
            % (self.version.select().execute().fetchone()[0])
        )
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the pulse2 database
        """

        # entity/package server association
        self.packageServerEntity = Table(
            "PackageServerEntity",
            self.metadata,
            Column("entity_uuid", Text, primary_key=True),
            Column("package_server_uuid", Text, primary_key=True),
            autoload=True,
        )
        mapper(PackageServerEntity, self.packageServerEntity)

        # version
        self.version = Table("Version", self.metadata, autoload=True)

    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError as e:
                self.logger.error(e)
            except Exception as e:
                self.logger.error(e)
            if ret:
                break
        if not ret:
            raise "Database connection error"
        return ret

    ####################################
    # entity/package server

    def getPackageServerEntityByPackageServer(self, ps_uuid):
        """
        @param ps_uuid: the package server uuid
        @type ps_uuid: str

        @returns: the PackageServerEntity that correspond to the given ps_uuid
        @rtype: the PackageServerEntity object
        """
        session = create_session()
        ret = (
            session.query(PackageServerEntity)
            .filter(self.packageServerEntity.c.package_server_uuid == ps_uuid)
            .one()
        )
        session.close()
        return ret

    def getPackageServerEntityByEntity(self, e_uuid):
        """
        @param e_uuid: the entity uuid
        @type e_uuid: str

        @returns: the PackageServerEntities that correspond to the given e_uuid
        @rtype: a list of PackageServerEntity object
        """
        session = create_session()
        ret = (
            session.query(PackageServerEntity)
            .filter(self.packageServerEntity.c.entity_uuid == e_uuid)
            .all()
        )
        session.close()
        return ret

    def getPackageServerEntityByEntities(self, e_uuids):
        session = create_session()
        ret1 = (
            session.query(PackageServerEntity)
            .add_column(self.packageServerEntity.c.entity_uuid)
            .filter(self.packageServerEntity.c.entity_uuid.in_(e_uuids))
            .all()
        )
        session.close()
        ret = {}
        for pes, e_uuid in ret1:
            if e_uuid not in ret:
                ret[e_uuid] = []
            ret[e_uuid].append(pes)
        return ret

    def getPackageServerEntity(self, ps_uuid, e_uuid):
        """
        @param ps_uuid: the package server uuid
        @type ps_uuid: str

        @param e_uuid: the entity uuid
        @type e_uuid: str

        @returns: the PackageServerEntity that correspond to the given ps_uuid and e_uuid
        @rtype: the PackageServerEntity object
        """
        session = create_session()
        ret = (
            session.query(PackageServerEntity)
            .filter(
                and_(
                    self.packageServerEntity.c.package_server_uuid == ps_uuid,
                    self.packageServerEntity.c.entity_uuid == e_uuid,
                )
            )
            .one()
        )
        session.close()
        return ret

    def putPackageServerEntity(self, ps_uuid, e_uuid):
        """
        @param ps_uuid: the package server uuid
        @type ps_uuid: str

        @param e_uuid: the entity uuid
        @type e_uuid: str

        @returns: the PackageServerEntity that correspond to the given ps_uuid and e_uuid
        @rtype: the PackageServerEntity object
        """
        session = create_session()
        pse = PackageServerEntity()
        pse.package_server_uuid = ps_uuid
        pse.entity_uuid = e_uuid
        session.add(pse)
        session.flush()
        session.close()
        return pse

    def delPackageServerEntity(self, e_uuid):
        """
        @param e_uuid: the entity uuid
        @type e_uuid: str

        @return: True if success
        @rtype: bool
        """
        session = create_session()
        pse = (
            session.query(PackageServerEntity)
            .filter(self.packageServerEntity.c.entity_uuid == e_uuid)
            .all()
        )
        if pse and len(pse) == 1:
            session.delete(pse[0])
        else:
            session.close()
            return False

        session.flush()
        session.close()
        return True

    ################################
    # MEMBERS


def id2uuid(id):
    return "UUID%s" % (str(id))


def uuid2id(uuid):
    return uuid.replace("UUID", "")


##########################################################################


class PackageServerEntity(database_helper.DBObject):
    to_be_exported = ["entity_uuid", "package_server_uuid"]
