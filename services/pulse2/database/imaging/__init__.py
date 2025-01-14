# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Database class for imaging
"""

import logging
import time
import datetime

from pulse2.utils import isUUID
from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from pulse2.database.imaging.types import P2ISS, P2IT, P2IM, P2IIK, P2ERR, P2ILL
from mmc.database import database_helper
from mmc.database.utilities import toUUID, fromUUID

from sqlalchemy import (
    create_engine,
    ForeignKey,
    Integer,
    MetaData,
    Table,
    Column,
    and_,
    or_,
    desc,
    func,
    distinct,
    Text,
    UniqueConstraint,
    ForeignKeyConstraint,
    not_,
)
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.sql.expression import alias as sa_exp_alias
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.automap import automap_base


# THAT REQUIRE TO BE IN A MMC SCOPE, NOT IN A PULSE2 ONE
from pulse2.managers.profile import ComputerProfileManager
from pulse2.managers.location import ComputerLocationManager


def cmp(a, b):
    return (a > b) - (a < b)


class ImagingException(Exception):
    pass


class NoImagingServerError(ImagingException):
    pass


class ImagingDatabase(DyngroupDatabaseHelper):
    """
    Class to query the Pulse2 imaging database.

    DyngroupDatabaseHelper is a Singleton, so is ImagingDatabase
    """

    def db_check(self):
        self.my_name = "imaging"
        self.configfile = "imaging.ini"
        return DyngroupDatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        DyngroupDatabaseHelper.init(self)
        if self.is_activated:
            self.logger.info("ImagingDatabase don't need activation")
            return None
        self.logger.info("ImagingDatabase is activating")
        self.config = config
        db_path = self.makeConnectionPath()
        self.db = create_engine(
            db_path,
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
            convert_unicode=True,
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
            return False
        self.metadata.create_all()
        self.r_nomenclatures = {}
        self.nomenclatures = {
            "ImagingLogState": ImagingLogState,
            "TargetType": TargetType,
            "SynchroState": SynchroState,
            "Language": Language,
            "ImageState": ImageState,
        }
        self.fk_nomenclatures = {
            "ImagingLog": {
                "fk_imaging_log_state": "ImagingLogState",
            },
            "Target": {"type": "TargetType"},
            "Menu": {"fk_synchrostate": "SynchroState"},
            "ImagingServer": {"fk_language": "Language"},
            "Image": {"fk_state": "ImageState"},
        }
        self.__loadNomenclatureTables()
        self.loadDefaults()
        self.loadLanguage()
        self.loadImagingServerLanguage()
        self.is_activated = True
        self.dbversion = self.getImagingDatabaseVersion()
        self.logger.debug("ImagingDatabase finish activation")
        return self.db_check()

    def loadDefaults(self):
        self.default_params = {
            "default_name": self.config.web_def_default_menu_name,
            "timeout": self.config.web_def_default_timeout,
            "hidden_menu": self.config.web_def_default_hidden_menu,
            "background_uri": self.config.web_def_default_background_uri,
            "message": self.config.web_def_default_message,
        }

    def loadLanguage(self):
        session = create_session()
        self.languages = {}
        self.r_languages = {}
        for i in session.query(Language).all():
            self.languages[i.id] = i.label
            self.r_languages[i.label] = i.id
        session.close()

    def loadImagingServerLanguage(self):
        session = create_session()
        self.imagingServer_lang = {}
        self.imagingServer_entity = {}
        for i in (
            session.query(ImagingServer)
            .add_entity(Entity)
            .select_from(
                self.imaging_server.join(
                    self.entity, self.entity.c.id == self.imaging_server.c.fk_entity
                )
            )
            .all()
        ):
            self.imagingServer_lang[id2uuid(i[0].id)] = i[0].fk_language
            # the true one! self.imagingServer_entity[id2uuid(i[0].id)] = i[1].uuid
            # the working one in our context :
            self.imagingServer_entity[i[1].uuid] = id2uuid(i[0].id)

        session.close()

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the imaging database
        """
        self.version = Table("version", self.metadata, autoload=True)

        self.initTables()
        mapper(BootService, self.boot_service)
        mapper(BootServiceInMenu, self.boot_service_in_menu)
        mapper(BootServiceOnImagingServer, self.boot_service_on_imaging_server)
        mapper(
            ComputerDisk,
            self.computer_disk,
            properties={
                "partitions": relation(ComputerPartition, cascade="all,delete-orphan")
            },
        )
        mapper(ComputerPartition, self.computer_partition)
        mapper(Entity, self.entity)
        mapper(Image, self.image)
        mapper(ImageState, self.image_state)
        mapper(ImageInMenu, self.image_in_menu)
        mapper(ImageOnImagingServer, self.image_on_imaging_server)
        mapper(ImagingServer, self.imaging_server)
        mapper(Internationalization, self.internationalization)
        mapper(Language, self.language)
        mapper(ImagingLog, self.imaging_log)
        mapper(ImagingLogState, self.imaging_log_state)
        mapper(MasteredOn, self.mastered_on)
        # , properties = { 'default_item':relation(MenuItem), 'default_item_WOL':relation(MenuItem) } )
        mapper(Menu, self.menu)
        # , properties = { 'menu' : relation(Menu) })
        mapper(MenuItem, self.menu_item)
        mapper(Partition, self.partition)
        mapper(PostInstallScript, self.post_install_script)
        mapper(PostInstallScriptInImage, self.post_install_script_in_image)
        mapper(
            PostInstallScriptOnImagingServer, self.post_install_script_on_imaging_server
        )
        mapper(SynchroState, self.synchro_state)
        mapper(
            Target,
            self.target,
            properties={"disks": relation(ComputerDisk, cascade="all,delete-orphan")},
        )
        mapper(TargetType, self.target_type)
        mapper(User, self.user)
        mapper(Multicast, self.multicast)

    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """
        self.boot_service = Table("BootService", self.metadata, autoload=True)

        self.entity = Table("Entity", self.metadata, autoload=True)

        self.language = Table("Language", self.metadata, autoload=True)

        self.imaging_log_state = Table("ImagingLogState", self.metadata, autoload=True)

        self.synchro_state = Table("SynchroState", self.metadata, autoload=True)

        self.post_install_script = Table(
            "PostInstallScript", self.metadata, autoload=True
        )

        self.target_type = Table("TargetType", self.metadata, autoload=True)

        self.user = Table("User", self.metadata, autoload=True)

        self.image = Table(
            "Image",
            self.metadata,
            Column("fk_creator", Integer, ForeignKey("User.id")),
            Column("fk_state", Integer, ForeignKey("ImageState.id")),
            autoload=True,
        )

        self.image_state = Table("ImageState", self.metadata, autoload=True)

        self.imaging_server = Table(
            "ImagingServer",
            self.metadata,
            Column("fk_entity", Integer, ForeignKey("Entity.id")),
            Column("fk_default_menu", Integer, ForeignKey("Menu.id")),
            Column("fk_language", Integer, ForeignKey("Language.id")),
            autoload=True,
        )

        self.internationalization = Table(
            "Internationalization",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("label", Text, nullable=False),
            Column("fk_language", Integer, nullable=False),
            UniqueConstraint(
                "id", "fk_language", name="uq_id_fk_language"
            ),  # contrainte unique
            extend_existing=True,  # étendre la définition existante de la table
        )

        self.menu = Table(
            "Menu",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("default_name", Text, nullable=False),
            Column(
                "fk_name", Integer, ForeignKey("Internationalization.id"), nullable=True
            ),
            Column("timeout", Integer),
            Column("mtftp_restore_timeout", Integer, default=10, nullable=False),
            Column("background_uri", Text, default=""),
            Column("message", Text, default="", nullable=False),
            Column("ethercard", Integer, default=0, nullable=False),
            Column("bootcli", Integer, default=0, nullable=False),
            Column("disklesscli", Integer, default=0, nullable=False),
            Column("dont_check_disk_size", Integer, default=0, nullable=False),
            Column("hidden_menu", Integer, default=0, nullable=False),
            Column("custom_menu", Integer, default=0, nullable=False),
            Column("debug", Integer, default=0, nullable=False),
            Column("update_nt_boot", Integer, default=0, nullable=False),
            Column(
                "fk_default_item", Integer, ForeignKey("MenuItem.id"), nullable=True
            ),
            Column(
                "fk_default_item_WOL", Integer, ForeignKey("MenuItem.id"), nullable=True
            ),
            Column("fk_protocol", Integer, ForeignKey("Protocol.id"), default=1),
            Column(
                "fk_synchrostate", Integer, ForeignKey("SynchroState.id"), default=1
            ),
            UniqueConstraint("id", "fk_name", name="unique_menu"),
            extend_existing=True,
        )

        self.menu_item = Table(
            "MenuItem",
            self.metadata,
            Column("fk_menu", Integer, ForeignKey("Menu.id")),
            autoload=True,
            extend_existing=True,
        )

        self.partition = Table(
            "Partitions",
            self.metadata,
            Column("fk_image", Integer, ForeignKey("Image.id")),
            autoload=True,
        )

        self.boot_service_in_menu = Table(
            "BootServiceInMenu",
            self.metadata,
            Column(
                "fk_bootservice",
                Integer,
                ForeignKey("BootService.id"),
                primary_key=True,
            ),
            Column("fk_menuitem", Integer, ForeignKey("MenuItem.id"), primary_key=True),
            autoload=True,
        )

        self.boot_service_on_imaging_server = Table(
            "BootServiceOnImagingServer",
            self.metadata,
            Column(
                "fk_boot_service",
                Integer,
                ForeignKey("BootService.id"),
                primary_key=True,
            ),
            # Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            # cant declare it implicit as a FK else it make circular
            # dependencies
            Column("fk_imaging_server", Integer, primary_key=True),
            autoload=True,
        )

        self.image_in_menu = Table(
            "ImageInMenu",
            self.metadata,
            Column("fk_image", Integer, ForeignKey("Image.id"), primary_key=True),
            Column("fk_menuitem", Integer, ForeignKey("MenuItem.id"), primary_key=True),
            autoload=True,
        )

        self.image_on_imaging_server = Table(
            "ImageOnImagingServer",
            self.metadata,
            Column("fk_image", Integer, ForeignKey("Image.id"), primary_key=True),
            Column(
                "fk_imaging_server",
                Integer,
                ForeignKey("ImagingServer.id"),
                primary_key=True,
            ),
            autoload=True,
        )

        self.target = Table(
            "Target",
            self.metadata,
            Column("fk_entity", Integer, ForeignKey("Entity.id")),
            Column("fk_menu", Integer, ForeignKey("Menu.id")),
            autoload=True,
        )

        self.computer_disk = Table("ComputerDisk", self.metadata, autoload=True)

        self.computer_partition = Table(
            "ComputerPartition", self.metadata, autoload=True
        )

        self.imaging_log = Table(
            "ImagingLog",
            self.metadata,
            Column("fk_imaging_log_state", Integer, ForeignKey("ImagingLogState.id")),
            Column("fk_target", Integer, ForeignKey("Target.id")),
            autoload=True,
        )

        self.mastered_on = Table(
            "MasteredOn",
            self.metadata,
            Column("fk_image", Integer, ForeignKey("Image.id"), primary_key=True),
            Column(
                "fk_imaging_log", Integer, ForeignKey("ImagingLog.id"), primary_key=True
            ),
            autoload=True,
        )

        self.post_install_script_in_image = Table(
            "PostInstallScriptInImage",
            self.metadata,
            Column("fk_image", Integer, ForeignKey("Image.id"), primary_key=True),
            Column(
                "fk_post_install_script",
                Integer,
                ForeignKey("PostInstallScript.id"),
                primary_key=True,
            ),
            autoload=True,
        )

        self.post_install_script_on_imaging_server = Table(
            "PostInstallScriptOnImagingServer",
            self.metadata,
            # Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            # circular deps
            Column("fk_imaging_server", Integer, primary_key=True),
            Column(
                "fk_post_install_script",
                Integer,
                ForeignKey("PostInstallScript.id"),
                primary_key=True,
            ),
            autoload=True,
        )

        self.multicast = Table(
            "Multicast",
            self.metadata,
            Column("location", Text),
            Column("target_uuid", Text, nullable=False),
            Column("image_uuid", Text, nullable=False),
            Column("image_name", Text, nullable=False),
            autoload=True,
        )

    def __loadNomenclatureTables(self):
        session = create_session()
        for i in self.nomenclatures:
            n = session.query(self.nomenclatures[i]).all()
            self.nomenclatures[i] = {}
            self.r_nomenclatures[i] = {}
            for j in n:
                self.nomenclatures[i][j.id] = j.label
                self.r_nomenclatures[i][j.label] = j.id
        session.close()

    def completeNomenclatureLabel(self, objs):
        if not isinstance(objs, list) and not isinstance(objs, tuple):
            objs = [objs]
        if len(objs) == 0:
            return
        className = str(objs[0].__class__).split("'")[1].split(".")[-1]
        nomenclatures = []
        if className in self.fk_nomenclatures:
            for i in self.fk_nomenclatures[className]:
                nomenclatures.append(
                    [
                        i,
                        i.replace("fk_", ""),
                        self.nomenclatures[self.fk_nomenclatures[className][i]],
                    ]
                )
            for obj in objs:
                for fk, field, value in nomenclatures:
                    fk_val = getattr(obj, fk)
                    if fk == field:
                        field = "%s_value" % field
                    if fk_val in value:
                        setattr(obj, field, value[fk_val])
                    else:
                        self.logger.warn(
                            "nomenclature is missing for %s field %s (value = %s)"
                            % (str(obj), field, str(fk_val))
                        )
                        setattr(
                            obj,
                            field,
                            "%s:nomenclature does not exists."
                            % (P2ERR.ERR_MISSING_NOMENCLATURE),
                        )

    def completeTarget(self, objs):
        """
        take a list of dict with a fk_target element and add them the target dict that correspond
        """
        ids = {}
        for i in objs:
            ids[i["fk_target"]] = None
        ids = list(ids.keys())
        targets = self.getTargetsById(ids)
        id_target = {}
        for t in targets:
            t = t.toH()
            id_target[t["id"]] = t
        for i in objs:
            i["target"] = id_target[i["fk_target"]]

    def getImagingDatabaseVersion(self):
        """
        Return the imaging database version.
        We don't use this information for now, but if we can get it this means the database connection is working.

        @rtype: int
        """
        return self.version.select().execute().fetchone()[0]

    def getAllKnownLanguages(self):
        session = create_session()
        l = session.query(Language).all()
        session.close()
        return l

    ###########################################################

    def getAllRegisteredComputers(self):
        session = create_session()
        ret = (
            session.query(Target.uuid)
            .filter(Target.type.in_([P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE]))
            .all()
        )
        session.close()
        return [m[0] for m in ret]

    def getRegisteredComputersForEntity(self, loc_uuid):
        session = create_session()
        ret = (
            session.query(Target.uuid)
            .select_from(
                self.target.join(
                    self.entity, self.target.c.fk_entity == self.entity.c.id
                )
            )
            .filter(
                and_(
                    self.entity.c.uuid == loc_uuid,
                    self.target.c.type.in_([P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE]),
                )
            )
            .all()
        )
        session.close()
        return [m[0] for m in ret]

    def getTargetsEntity(self, uuids):
        session = create_session()
        e = (
            session.query(Entity)
            .add_entity(Target)
            .select_from(
                self.entity.join(
                    self.target, self.target.c.fk_entity == self.entity.c.id
                )
            )
            .filter(self.target.c.uuid.in_(uuids))
            .all()
        )
        session.close()
        return e

    def getAllLocation(self):
        session = create_session()
        query = session.query(ImagingServer).all()
        session.close()
        return [m for m in query]

    def getTargetPackageServer(self, target_id):
        session = create_session()
        # Run the following query: SELECT ImagingServer.url from ImagingServer
        # INNER JOIN Target ON Target.fk_entity = ImagingServer.fk_entity WHERE
        # Target.uuid=target_id;
        query = (
            session.query(ImagingServer)
            .select_from(
                self.imaging_server.join(
                    self.target,
                    self.target.c.fk_entity == self.imaging_server.c.fk_entity,
                )
            )
            .filter(self.target.c.uuid == target_id)
        )
        query = query.all()
        session.close()
        return [m for m in query]

    def getImagingServerInfo(self, location_uuid):
        q = self.getImagingServerByEntityUUID(location_uuid)
        if not q:
            return None
        if isinstance(q, list):
            return q[0]
        else:
            return q

    def getTargetsById(self, ids):
        session = create_session()
        n = session.query(Target).filter(self.target.c.id.in_(ids)).all()
        session.close()
        return n

    def getTargetsByUUID(self, ids, session=None):
        need_to_close_session = False
        if session is None:
            need_to_close_session = True
            session = create_session()
        n = session.query(Target).filter(self.target.c.uuid.in_(ids)).all()
        if need_to_close_session:
            session.close()
        return n

    def __mergeTargetInImagingLog(self, imaging_log_list):
        ret = []
        for imaging_log, target in imaging_log_list:
            setattr(imaging_log, "target", target)
            ret.append(imaging_log)
        return ret

    def __getTargetsMenuQuery(self, session):
        return (
            session.query(Menu)
            .add_column(self.internationalization.c.label)
            .select_from(
                self.menu.join(self.target, self.target.c.fk_menu == self.menu.c.id)
                .join(
                    self.imaging_server,
                    self.target.c.fk_entity == self.imaging_server.c.fk_entity,
                )
                .outerjoin(
                    self.internationalization,
                    and_(
                        self.internationalization.c.id == self.menu.c.fk_name,
                        self.internationalization.c.fk_language
                        == self.imaging_server.c.fk_language,
                    ),
                )
            )
        )

    def getTargetsMenuTID(self, target_id):
        session = create_session()
        q = self.__getTargetsMenuQuery(session)
        # there should always be only one!
        q = q.filter(self.target.c.id == target_id).first()
        session.close()
        if q is None:
            return q
        if q[1] is not None and q[1] != "NOTTRANSLATED":
            q[0].default_name = q[1]
        return q[0]

    def getTargetsMenuTUUID(self, target_id, session=None):
        need_to_close_session = False
        if session is None:
            need_to_close_session = True
            session = create_session()
        q = self.__getTargetsMenuQuery(session)
        # there should always be only one!
        q = q.filter(self.target.c.uuid == target_id).first()
        if need_to_close_session:
            session.close()
        if q is None:
            return q
        if q[1] is not None and q[1] != "NOTTRANSLATED":
            q[0].default_name = q[1]
        return q[0]

    def getDefaultSuscribeMenu(self, location, session=None):
        need_to_close_session = False
        if session is None:
            need_to_close_session = True
            session = create_session()
        lang = self.__getLocLanguage(session, location.uuid)
        q = (
            session.query(Menu)
            .add_column(self.internationalization.c.label)
            .select_from(
                self.menu.outerjoin(
                    self.internationalization,
                    and_(
                        self.internationalization.c.id == self.menu.c.fk_name,
                        self.internationalization.c.fk_language == lang,
                    ),
                )
            )
            .filter(self.menu.c.id == 2)
            .first()
        )
        if need_to_close_session:
            session.close()
        if q is None:
            return q
        if q[1] is not None and q[1] != "NOTTRANSLATED":
            q[0].default_name = q[1]
        return q[0]

    def getEntitiesImagingServer(self, entities_uuid, is_associated):
        session = create_session()
        q = session.query(ImagingServer).add_column(self.entity.c.uuid)
        q = q.select_from(
            self.imaging_server.join(
                self.entity, self.entity.c.id == self.imaging_server.c.fk_entity
            )
        )
        filt = self.entity.c.uuid.in_(entities_uuid)
        if is_associated:
            filt = and_(filt, self.imaging_server.c.associated == 1)
        q = q.filter(filt).all()
        session.close()
        return q

    def getEntityDefaultMenu(self, loc_id, session=None):
        """
        Given an entity <loc_id>, returns its default menu (more precisely, its imaging server default menu)

        FIXME: this code doesn't handle the case when imaging_server.is_recursive
        is True

        @param loc_id the entity UUID
        @param session (optional) a SQL session to use
        """
        need_to_close_session = False
        if session is None:
            need_to_close_session = True
            session = create_session()
        imaging_server = self.getImagingServerByEntityUUID(loc_id, session)
        if isinstance(imaging_server, list) and len(imaging_server) == 0:
            raise NoImagingServerError()

        j = (
            self.menu.join(self.imaging_server)
            .join(self.entity)
            .outerjoin(
                self.internationalization,
                and_(
                    self.internationalization.c.id == self.menu.c.fk_name,
                    self.internationalization.c.fk_language
                    == self.imaging_server.c.fk_language,
                ),
            )
        )
        q = (
            session.query(Menu)
            .add_column(self.internationalization.c.label)
            .select_from(j)
        )
        q = q.filter(self.imaging_server.c.id == imaging_server.id)
        q = q.filter(self.imaging_server.c.associated == 1)
        q = q.first()
        if need_to_close_session:
            session.close()

        if q is None:
            return None

        if q[1] is not None and q[1] != "NOTTRANSLATED":
            q[0].default_name = q[1]

        return q[0]

    def getTargetMenu(self, uuid, _type, session=None):
        need_to_close_session = False
        if session is None:
            need_to_close_session = True
            session = create_session()
        q = (
            session.query(Menu)
            .add_column(self.internationalization.c.label)
            .select_from(
                self.menu.join(self.target, self.target.c.fk_menu == self.menu.c.id)
                .join(
                    self.imaging_server,
                    self.imaging_server.c.fk_entity == self.target.c.fk_entity,
                )
                .outerjoin(
                    self.internationalization,
                    and_(
                        self.internationalization.c.id == self.menu.c.fk_name,
                        self.internationalization.c.fk_language
                        == self.imaging_server.c.fk_language,
                    ),
                )
            )
            .filter(and_(self.target.c.uuid == uuid, self.target.c.type == _type))
            .first()
        )  # there should always be only one!
        if need_to_close_session:
            session.close()
        if q is None:
            return q
        if q[1] is not None and q[1] != "NOTTRANSLATED":
            q[0].default_name = q[1]
        return q[0]

    def __mergeMenuItemInBootService(self, list_of_bs, list_of_both):
        ret = []
        temporary = {}
        for bs, mi in list_of_both:
            if mi is not None:
                temporary[bs.id] = mi
        # used_bs_id = ID of BootService if this BootService is used
        for bs, bs_id, used_bs_id, name_i18n, desc_i18n in list_of_bs:
            if name_i18n is not None:
                setattr(bs, "default_name", name_i18n.label)
            if desc_i18n is not None:
                setattr(bs, "default_desc", desc_i18n.label)
            if bs_id in temporary:
                mi = temporary[bs_id]
                if name_i18n is not None:
                    setattr(mi, "default_name", name_i18n.label)
                if desc_i18n is not None:
                    setattr(mi, "default_desc", desc_i18n.label)
                setattr(bs, "menu_item", mi)
            setattr(bs, "used_bs_id", used_bs_id)
            ret.append(bs)
        return ret

    def __mergeBootServiceInMenuItem(self, my_list):
        ret = []
        for mi, bs, menu, bsois, name_i18n, desc_i18n in my_list:
            if bs is not None:
                setattr(mi, "boot_service", bs)
            setattr(mi, "is_local", (bsois is not None))
            if menu is not None:
                setattr(mi, "default", (menu.fk_default_item == mi.id))
                setattr(mi, "default_WOL", (menu.fk_default_item_WOL == mi.id))
            if name_i18n is not None:
                setattr(mi, "name", name_i18n.label)
                setattr(bs, "default_name", name_i18n.label)
            if desc_i18n is not None:
                setattr(mi, "desc", desc_i18n.label)
                setattr(bs, "default_desc", desc_i18n.label)
            ret.append(mi)
        return ret

    def __mergeMenuItemInImage(self, list_of_im, list_of_both, list_of_target=[]):
        ret = []
        temporary = {}
        for im, mi in list_of_both:
            if mi is not None:
                temporary[im.id] = mi
        targets = {}
        for t, mo in list_of_target:
            targets[mo.fk_image] = t.uuid
        for im, im_id in list_of_im:
            if im_id in temporary:
                setattr(im, "menu_item", temporary[im_id])
            if len(list_of_target) != 0 and im.id in targets:
                setattr(im, "mastered_on_target_uuid", targets[im.id])
            ret.append(im)
        return ret

    def __mergeBootServiceOrImageInMenuItem(self, mis):
        """warning this one does not work on a list but on a tuple of 3 elements (mi, bs, im)"""
        (menuitem, bootservice, image, menu, name_bs_i18n, desc_bs_i18n) = mis
        if bootservice is not None:
            if name_bs_i18n is not None:
                setattr(bootservice, "default_name", name_bs_i18n.label)
            if desc_bs_i18n is not None:
                setattr(bootservice, "default_desc", desc_bs_i18n.label)
            setattr(menuitem, "boot_service", bootservice)
        if image is not None:
            setattr(menuitem, "image", image)
        if menu is not None:
            setattr(menuitem, "default", (menu.fk_default_item == menuitem.id))
            setattr(menuitem, "default_WOL", (menu.fk_default_item_WOL == menuitem.id))

        return menuitem

    def __mergeImageInMenuItem(self, my_list):
        ret = []
        for mi, im, menu in my_list:
            if im is not None:
                setattr(mi, "image", im)
            if menu is not None:
                setattr(mi, "default", (menu.fk_default_item == mi.id))
                setattr(mi, "default_WOL", (menu.fk_default_item_WOL == mi.id))
            ret.append(mi)
        return ret

    def __getMenusImagingServer(self, session, menu_id):
        """
        Get stuff pointing to menu menu_id
        """
        j = self.imaging_server.outerjoin(self.entity).outerjoin(self.target)
        f = or_(
            self.imaging_server.c.fk_default_menu == menu_id,
            self.target.c.fk_menu == menu_id,
        )
        imaging_server = session.query(ImagingServer).select_from(j).filter(f).first()
        if imaging_server:
            return imaging_server
        else:
            self.logger.error("cant find any imaging_server for menu '%s'" % (menu_id))
            return None

    # TODO implement the start/end with a union between q1 and q2
    def getMenuContent(
        self,
        menu_id,
        _type=P2IM.ALL,
        start=0,
        end=-1,
        filter="",
        session=None,
        loc_id=None,
    ):
        session_need_close = False
        if session is None:
            session = create_session()
            session_need_close = True

        mi_ids = (
            session.query(MenuItem)
            .add_column(self.menu_item.c.id)
            .select_from(
                self.menu_item.join(
                    self.menu, self.menu_item.c.fk_menu == self.menu.c.id
                )
            )
        )
        if filter != "":
            mi_ids = mi_ids.filter(
                and_(
                    self.menu.c.id == menu_id,
                    self.menu_item.c.desc.like("%" + filter + "%"),
                )
            )
        else:
            mi_ids = mi_ids.filter(self.menu.c.id == menu_id)
        mi_ids = mi_ids.order_by(self.menu_item.c.order)
        if end != -1:
            mi_ids = mi_ids.offset(int(start)).limit(int(end) - int(start))
        else:
            mi_ids = mi_ids.all()
        mi_ids = [x[1] for x in mi_ids]

        if loc_id is not None:
            imaging_server = self.getImagingServerByEntityUUID(loc_id, session)
        else:
            imaging_server = self.__getMenusImagingServer(session, menu_id)
        is_id = 0
        lang = 1
        if imaging_server:
            is_id = imaging_server.id
            lang = imaging_server.fk_language
        elif loc_id is not None and menu_id == 2:  # this is the suscribe menu
            lang = self.__getLocLanguage(session, loc_id)

        q = []
        if _type == P2IM.ALL or _type == P2IM.BOOTSERVICE:
            # we don't need the i18n trick for the menu name here
            I18n1 = sa_exp_alias(self.internationalization)
            I18n2 = sa_exp_alias(self.internationalization)
            q1 = session.query(MenuItem)
            q1 = (
                q1.add_entity(BootService)
                .add_entity(Menu)
                .add_entity(BootServiceOnImagingServer)
                .add_entity(Internationalization, alias=I18n1)
                .add_entity(Internationalization, alias=I18n2)
            )
            q1 = q1.select_from(
                self.menu_item.join(self.boot_service_in_menu)
                .join(self.boot_service)
                .join(
                    self.menu, self.menu_item.c.fk_menu == self.menu.c.id
                )  # ID 1 of Internationalization table is "NOTTRANSLATED"
                # Do not display it, display english text instead
                .outerjoin(
                    I18n1,
                    and_(
                        self.boot_service.c.fk_name == I18n1.c.id,
                        I18n1.c.fk_language == lang,
                        I18n1.c.id != 1,
                    ),
                )
                .outerjoin(
                    I18n2,
                    and_(
                        self.boot_service.c.fk_desc == I18n2.c.id,
                        I18n2.c.fk_language == lang,
                        I18n2.c.id != 1,
                    ),
                )
                .outerjoin(self.boot_service_on_imaging_server)
            )
            q1 = q1.filter(
                and_(
                    self.menu_item.c.id.in_(mi_ids),
                    or_(
                        self.boot_service_on_imaging_server.c.fk_boot_service == None,
                        self.boot_service_on_imaging_server.c.fk_imaging_server
                        == is_id,
                    ),
                )
            )
            q1 = q1.order_by(self.menu_item.c.order).all()
            q1 = self.__mergeBootServiceInMenuItem(q1)
            q.extend(q1)
        if _type == P2IM.ALL or _type == P2IM.IMAGE:
            # we don't need the i18n trick for the menu name here
            q2 = (
                session.query(MenuItem)
                .add_entity(Image)
                .add_entity(Menu)
                .select_from(
                    self.menu_item.join(self.image_in_menu)
                    .join(self.image)
                    .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id)
                )
            )
            q2 = (
                q2.filter(self.menu_item.c.id.in_(mi_ids))
                .order_by(self.menu_item.c.order)
                .all()
            )
            q2 = self.__mergeImageInMenuItem(q2)
            q.extend(q2)
        if session_need_close:
            session.close()
        # q.sort(lambda x, y: cmp(x.order, y.order))
        return q

    def getLastMenuItemOrder(self, menu_id):
        session = create_session()
        # q = session.query(MenuItem).filter(self.menu_item.c.fk_menu == menu_id).max(self.menu_item.c.order)
        q = session.query(func.max(self.menu_item.c.order)).filter(
            self.menu_item.c.fk_menu == menu_id
        )
        ret = q.first()
        session.close()
        if ret is None:
            return -1
        return ret[0]

    def countMenuContentFast(self, menu_id):  # get P2IM.ALL and empty filter
        session = create_session()
        q = session.query(MenuItem).filter(self.menu_item.c.fk_menu == menu_id).count()
        session.close()
        return q

    def countMenuContent(self, menu_id, _type=P2IM.ALL, filter=""):
        if _type == P2IM.ALL and filter == "":
            return self.countMenuContentFast(menu_id)

        session = create_session()
        q = 0
        if _type == P2IM.ALL or _type == P2IM.BOOTSERVICE:
            q1 = (
                session.query(MenuItem)
                .add_entity(BootService)
                .select_from(
                    self.menu_item.join(self.boot_service_in_menu).join(
                        self.boot_service
                    )
                )
            )
            q1 = q1.filter(
                and_(
                    self.menu_item.c.fk_menu == menu_id,
                    self.boot_service.c.default_desc.like("%" + filter + "%"),
                )
            ).count()
            q += q1
        if _type == P2IM.ALL or _type == P2IM.IMAGE:
            q2 = (
                session.query(MenuItem)
                .add_entity(Image)
                .select_from(self.menu_item.join(self.image_in_menu).join(self.image))
            )
            q2 = q2.filter(
                and_(
                    self.menu_item.c.fk_menu == menu_id,
                    self.boot_service.c.default_desc.like("%" + filter + "%"),
                )
            ).count()
            q += q2
        session.close()
        return q

    ###########################################################
    def getEntityUrl(self, location_uuid):
        q = self.getImagingServerByEntityUUID(location_uuid)
        if not q:
            return None
        if isinstance(q, list):
            return q[0].url
        else:
            return q.url

    def __ImagingLogs4Location(self, session, location_uuid, filter):
        n = (
            session.query(ImagingLog)
            .add_entity(Target)
            .select_from(self.imaging_log.join(self.target).join(self.entity))
            .filter(self.entity.c.uuid == location_uuid)
        )
        if filter != "":
            n = n.filter(
                or_(
                    self.imaging_log.c.detail.like("%" + filter + "%"),
                    self.target.c.name.like("%" + filter + "%"),
                )
            )
        return n

    def getImagingLogs4Location(self, location_uuid, start, end, filter):
        session = create_session()
        n = self.__ImagingLogs4Location(session, location_uuid, filter)
        n = n.order_by(desc(self.imaging_log.c.timestamp))
        if end != -1:
            n = n.offset(int(start)).limit(int(end) - int(start))
        else:
            n = n.all()
        session.close()
        n = self.__mergeTargetInImagingLog(n)
        return n

    def countImagingLogs4Location(self, location_uuid, filter):
        session = create_session()
        n = self.__ImagingLogs4Location(session, location_uuid, filter)
        n = n.count()
        session.close()
        return n

    #####################
    def __ImagingLogsOnTargetByIdAndType(self, session, target_id, _type, filter):
        q = (
            session.query(ImagingLog)
            .add_entity(Target)
            .select_from(self.imaging_log.join(self.target))
        )
        if _type in [P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE]:
            q = q.filter(self.target.c.type == _type).filter(
                self.target.c.uuid == target_id
            )
        elif _type == P2IT.PROFILE:
            # Need to get all computers UUID of the profile
            uuids = [
                c.uuid for c in ComputerProfileManager().getProfileContent(target_id)
            ]
            q = q.filter(self.target.c.type == P2IT.COMPUTER_IN_PROFILE).filter(
                self.target.c.uuid.in_(uuids)
            )
        else:
            self.logger.error("type %s does not exists!" % _type)
            # to be sure we don't get anything, this is an error case!
            q = q.filter(self.target.c.type == 0)
        if filter != "":
            q = q.filter(
                or_(
                    self.imaging_log.c.detail.like("%" + filter + "%"),
                    self.target.c.name.like("%" + filter + "%"),
                )
            )
        return q

    def getImagingLogsOnTargetByIdAndType(self, target_id, _type, start, end, filter):
        session = create_session()
        q = self.__ImagingLogsOnTargetByIdAndType(session, target_id, _type, filter)
        q = q.order_by(desc(self.imaging_log.c.timestamp))
        if end != -1:
            q = q.offset(int(start)).limit(int(end) - int(start))
        else:
            q = q.all()
        session.close()
        q = self.__mergeTargetInImagingLog(q)
        return q

    def countImagingLogsOnTargetByIdAndType(self, target_id, _type, filter):
        session = create_session()
        q = self.__ImagingLogsOnTargetByIdAndType(session, target_id, _type, filter)
        q = q.count()
        session.close()
        return q

    ######################
    def getTargetLanguage(self, session, target_uuid):
        ims = session.query(ImagingServer).select_from(
            self.imaging_server.join(
                self.target, self.target.c.fk_entity == self.imaging_server.c.fk_entity
            )
        )
        ims = ims.filter(self.target.c.uuid == target_uuid).first()
        lang = ims.fk_language
        return lang

    def getLocLanguage(self, loc_id):
        session = create_session()
        ret = self.__getLocLanguage(session, loc_id)
        session.close()
        return ret

    def __getLocLanguage(self, session, loc_id):
        lang = 1
        if loc_id in self.imagingServer_entity:
            if loc_id not in self.imagingServer_lang:
                ims = (
                    session.query(ImagingServer)
                    .select_from(
                        self.imaging_server.join(
                            self.entity,
                            self.entity.c.id == self.imaging_server.c.fk_entity,
                        )
                    )
                    .filter(self.entity.c.uuid == loc_id)
                    .first()
                )
                self.imagingServer_lang[loc_id] = ims.fk_language
        else:
            q = (
                session.query(ImagingServer)
                .add_entity(Entity)
                .select_from(
                    self.imaging_server.join(
                        self.entity, self.entity.c.id == self.imaging_server.c.fk_entity
                    )
                )
                .filter(self.entity.c.uuid == loc_id)
                .first()
            )
            if q is not None:
                ims, en = q
                # the true one! self.imagingServer_entity[id2uuid(ims.id)] = en.uuid
                # the working one in our context :
                self.imagingServer_entity[en.uuid] = id2uuid(ims.id)
                self.imagingServer_lang[self.imagingServer_entity[loc_id]] = (
                    ims.fk_language
                )
            else:
                return 1  # default to english
        if loc_id in self.imagingServer_lang:
            lang = self.imagingServer_lang[loc_id]
        return lang

    def __PossibleBootServices(self, session, target_uuid, filter, count=False):
        """
        Return Possible Boot Services
        If count variable is set to True, this function return number of Boot Services
        """

        lang = self.getTargetLanguage(session, target_uuid)

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        # If count is set to True, Using of func.count()
        q = (
            count
            and session.query(func.count(distinct(self.boot_service.c.id)), BootService)
            or session.query(BootService)
        )

        q = (
            q.add_column(self.boot_service.c.id)
            .add_column(self.boot_service_in_menu.c.fk_bootservice)
            .add_entity(Internationalization, alias=I18n1)
            .add_entity(Internationalization, alias=I18n2)
        )
        q = q.select_from(
            self.boot_service.outerjoin(
                self.boot_service_on_imaging_server,
                self.boot_service.c.id
                == self.boot_service_on_imaging_server.c.fk_boot_service,
            )
            .outerjoin(
                self.imaging_server,
                self.imaging_server.c.id
                == self.boot_service_on_imaging_server.c.fk_imaging_server,
            )
            .outerjoin(
                self.boot_service_in_menu,
                self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            )  # ID 1 of Internationalization table is "NOTTRANSLATED"
            # Do not display it, display english text instead
            .outerjoin(
                I18n1,
                and_(
                    self.boot_service.c.fk_name == I18n1.c.id,
                    I18n1.c.fk_language == lang,
                    I18n1.c.id != 1,
                ),
            )
            .outerjoin(
                I18n2,
                and_(
                    self.boot_service.c.fk_desc == I18n2.c.id,
                    I18n2.c.fk_language == lang,
                    I18n2.c.id != 1,
                ),
            )
            .outerjoin(self.entity)
            .outerjoin(self.target)
        )
        q = q.filter(
            or_(
                self.target.c.uuid == target_uuid,
                self.boot_service_on_imaging_server.c.fk_boot_service == None,
            )
        )
        if filter != "":
            q = q.filter(
                or_(
                    self.boot_service.c.default_desc.like("%" + filter + "%"),
                    self.boot_service.c.value.like("%" + filter + "%"),
                )
            )

        # If count is set to True, Count...
        if count:
            q = q.scalar()

        return q

    def __EntityBootServices(self, session, loc_id, filter, count=False):
        """
        Return Entity Boot Services
        If count variable is set to True, this function return number of Boot Services
        """

        lang = self.__getLocLanguage(session, loc_id)

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        # If count is set to True, Using of func.count()
        q = (
            count
            and session.query(func.count(distinct(self.boot_service.c.id)), BootService)
            or session.query(BootService)
        )

        q = (
            q.add_column(self.boot_service.c.id)
            .add_column(self.boot_service_in_menu.c.fk_bootservice)
            .add_entity(Internationalization, alias=I18n1)
            .add_entity(Internationalization, alias=I18n2)
        )
        q = q.select_from(
            self.boot_service.outerjoin(
                self.boot_service_on_imaging_server,
                self.boot_service.c.id
                == self.boot_service_on_imaging_server.c.fk_boot_service,
            )
            .outerjoin(
                self.imaging_server,
                self.imaging_server.c.id
                == self.boot_service_on_imaging_server.c.fk_imaging_server,
            )
            .outerjoin(
                self.boot_service_in_menu,
                self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            )  # ID 1 of Internationalization table is "NOTTRANSLATED"
            # Do not display it, display english text instead
            .outerjoin(
                I18n1,
                and_(
                    self.boot_service.c.fk_name == I18n1.c.id,
                    I18n1.c.fk_language == lang,
                    I18n1.c.id != 1,
                ),
            )
            .outerjoin(
                I18n2,
                and_(
                    self.boot_service.c.fk_desc == I18n2.c.id,
                    I18n2.c.fk_language == lang,
                    I18n2.c.id != 1,
                ),
            )
            .outerjoin(self.entity)
        )
        q = q.filter(
            or_(
                self.entity.c.uuid == loc_id,
                self.boot_service_on_imaging_server.c.fk_boot_service == None,
            )
        )
        if filter != "":
            q = q.filter(
                or_(
                    self.boot_service.c.default_desc.like("%" + filter + "%"),
                    self.boot_service.c.value.like("%" + filter + "%"),
                )
            )

        # If count is set to True, Count...
        if count:
            q = q.scalar()

        return q

    def createBootServiceFromPostInstall(self, script_id):
        session = create_session()

        # Check if Boot service already exists
        if (
            session.query(PostInstallScript)
            .filter(
                and_(
                    self.post_install_script.c.id == uuid2id(script_id),
                    self.post_install_script.c.fk_boot_service != None,
                )
            )
            .first()
        ):
            session.logger.warn("A boot service with this name already exists")
            session.close()
            return False

        # Get PostInstallScript according to script_id
        pis = (
            session.query(PostInstallScript)
            .filter(self.post_install_script.c.id == uuid2id(script_id))
            .first()
        )

        bs = BootService()
        bs.default_name = pis.default_name
        bs.default_desc = pis.default_desc
        bs.fk_name = pis.fk_name
        bs.fk_desc = pis.fk_desc

        # bs.value cannot by null, we need script_name based on bs.id who doesn't still exist
        # so fill with a dummy value
        bs.value = "Dummy"

        session.add(bs)
        session.flush()

        # We give bs id to script_name
        script_name = toUUID(bs.id) + ".sh"

        # Update PostInstallScript and associate it with New BootService
        # Created
        pis.fk_boot_service = bs.id

        # We have script_name, so give correct value for bs.value
        bs.value = (
            "kernel ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL## ##PULSE2_KERNEL_OPTS## davos_action=RUN_BOOTSERVICE ##PULSE2_DAVOS_OPTS## bootservice_script=%s \ninitrd ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_INITRD##"
        ) % script_name

        session.flush()

        session.close()

        return [
            script_name,
            pis.value,
            {
                "name": bs.default_name,
                "desc": bs.default_desc,
                "value": bs.value,
            },
        ]

    def __PossibleBootServiceAndMenuItem(self, session, bs_ids, menu_id):
        q = session.query(BootService).add_entity(MenuItem)
        q = q.filter(
            and_(
                self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
                self.menu_item.c.fk_menu == menu_id,
                self.boot_service.c.id.in_(bs_ids),
            )
        ).all()
        return q

    def getPossibleBootServices(self, target_uuid, start, end, filter):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid)
        q1 = self.__PossibleBootServices(session, target_uuid, filter)
        q1 = q1.group_by(self.boot_service.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end) - int(start))
        else:
            q1 = q1.all()
        bs_ids = [bs[1] for bs in q1]
        q2 = self.__PossibleBootServiceAndMenuItem(session, bs_ids, menu.id)
        profile = ComputerProfileManager().getComputersProfile(target_uuid)
        if profile is not None:
            # this should be the profile uuid!
            menu_root = self.getTargetsMenuTUUID(profile.id)
            q3 = self.__PossibleBootServiceAndMenuItem(session, bs_ids, menu_root.id)
            q4 = []
            already = []
            for bs, mi in q3:
                setattr(mi, "read_only", True)
                q4.append([bs, mi])
                already.append(bs.id)
            for bs, mi in q2:
                if bs.id not in already:
                    q4.append([bs, mi])
            q2 = q4

        session.close()

        q = self.__mergeMenuItemInBootService(q1, q2)
        return q

    def getEntityBootServices(self, loc_id, start, end, filter):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id)
        q1 = self.__EntityBootServices(session, loc_id, filter)
        q1 = q1.group_by(self.boot_service.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end) - int(start))
        else:
            q1 = q1.all()
        bs_ids = [bs[1] for bs in q1]
        q2 = self.__PossibleBootServiceAndMenuItem(session, bs_ids, menu.id)
        session.close()

        q = self.__mergeMenuItemInBootService(q1, q2)
        return q

    def countPossibleBootServices(self, target_uuid, filter):
        session = create_session()

        # With last param of self.__PossibleBootServices set to True,
        # we get number of PossibleBootServices
        q = self.__PossibleBootServices(session, target_uuid, filter, True)
        session.close()
        return q

    def countEntityBootServices(self, loc_id, filter):
        session = create_session()

        # With last param of self.__EntityBootServices set to True,
        # we get number of EntityBootServices
        q = self.__EntityBootServices(session, loc_id, filter, True)
        session.close()
        return q

    def __createNewMenuItem(self, session, menu_id, params):
        mi = MenuItem()
        params["order"] = self.getLastMenuItemOrder(menu_id) + 1
        mi = self.__fillMenuItem(session, mi, menu_id, params)
        return mi

    def __fillMenuItem(self, session, mi, menu_id, params):
        if "hidden" in params:
            mi.hidden = params["hidden"]
        else:
            mi.hidden = True
        if "hidden_WOL" in params:
            mi.hidden_WOL = params["hidden_WOL"]
        else:
            mi.hidden_WOL = True
        if "order" in params:
            mi.order = params["order"]
        mi.fk_menu = menu_id
        session.add(mi)
        return mi

    def __addMenuDefaults(self, session, menu, mi, params):
        is_menu_modified = False
        # if 'default' in params and params['default']:
        if "default" in params and params["default"]:
            is_menu_modified = True
            menu.fk_default_item = mi.id
        # if 'default_WOL' in params and params['default_WOL']:
        if (
            "default_WOL" in params
            and "default_WOL" in params
            and params["default_WOL"]
        ):
            is_menu_modified = True
            menu.fk_default_item_WOL = mi.id
        if is_menu_modified:
            session.add(menu)
        return menu

    def __editMenuDefaults(self, session, menu, mi, params):
        is_menu_modified = False
        if type(menu) in (int, int):
            menu = session.query(Menu).filter(self.menu.c.id == menu).first()
        if menu.fk_default_item != mi.id and params["default"]:
            is_menu_modified = True
            menu.fk_default_item = mi.id
        if menu.fk_default_item == mi.id and not params["default"]:
            is_menu_modified = True
            menu.fk_default_item = None

        if menu.fk_default_item_WOL != mi.id and params["default_WOL"]:
            is_menu_modified = True
            menu.fk_default_item_WOL = mi.id
        if menu.fk_default_item_WOL == mi.id and not params["default_WOL"]:
            is_menu_modified = True
            menu.fk_default_item_WOL = None

        if is_menu_modified:
            session.add(menu)
        return menu

    def __sortMenuItems(self, menu_id, session):
        """
        Executed when a item is deleted to have a correct order
        of remaining items.

        @param menu_id: computers menu id
        @type menu_id: int

        @param session: SqlAlchemy session
        @type: object
        """
        items = session.query(MenuItem).select_from(self.menu_item)
        items = items.filter(self.menu_item.c.fk_menu == menu_id)
        items = items.order_by(self.menu_item.c.order).all()

        new_order = 0

        for item in items:
            item.order = new_order
            new_order += 1
            session.flush()

    def getDefaultMenuItemOrder(self, id):
        session = create_session()
        mis = session.query(MenuItem).select_from(self.menu_item)
        mis = mis.filter(self.menu_item.c.id == id)
        return mis.all()

    def __computerChangeDefaultMenuItem(self, session, menu, mis, item_number):
        mi = mis[item_number]
        params = {"default": True}
        self.__addMenuDefaults(session, menu, mi, params)
        return mi.id

    def getProfileComputersDefaultMenuItem(self, profile_uuid, session):
        uuids = [
            c.uuid for c in ComputerProfileManager().getProfileContent(profile_uuid)
        ]

        q = session.query(Target).add_entity(Menu)
        q = q.select_from(
            self.target.join(self.menu, self.target.c.fk_menu == self.menu.c.id)
        )
        q = q.filter(self.target.c.uuid.in_(uuids)).all()

        return q

    def profileChangeDefaultMenuItem(
        self, imaging_server_uuid, profile_uuid, item_number, session=None
    ):
        session_need_close = False
        if session is None:
            session = create_session()
            session_need_close = True

        menu = self.getTargetsMenuTUUID(profile_uuid, session)
        mis = session.query(MenuItem).select_from(
            self.menu_item.join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
        )
        mis = (
            mis.filter(self.menu.c.id == menu.id).order_by(self.menu_item.c.order).all()
        )

        self.__computerChangeDefaultMenuItem(session, menu, mis, item_number)

        if session_need_close:
            session.close()
        return True

    def computerChangeDefaultMenuItem(
        self, imaging_server_uuid, computer_uuid, item_number
    ):
        session = create_session()

        profile = ComputerProfileManager().getComputersProfile(computer_uuid)
        menu = self.getTargetsMenuTUUID(computer_uuid, session)
        if profile is not None:
            # this should be the profile uuid!
            menu_root = self.getTargetsMenuTUUID(profile.id, session)
            mis = session.query(MenuItem).select_from(
                self.menu_item.join(
                    self.menu, self.menu.c.id == self.menu_item.c.fk_menu
                )
            )
            mis = (
                mis.filter(self.menu.c.id == menu_root.id)
                .order_by(self.menu_item.c.order)
                .all()
            )
            root_len = len(mis)
            mi_id = None
            if root_len > item_number:
                mi_id = self.__computerChangeDefaultMenuItem(
                    session, menu, mis, item_number
                )
            else:
                mis = session.query(MenuItem).select_from(
                    self.menu_item.join(
                        self.menu, self.menu.c.id == self.menu_item.c.fk_menu
                    )
                )
                mis = (
                    mis.filter(self.menu.c.id == menu.id)
                    .order_by(self.menu_item.c.order)
                    .all()
                )
                if len(mis) > item_number:
                    mi_id = self.__computerChangeDefaultMenuItem(
                        session, menu, mis, item_number - root_len
                    )
                else:
                    session.close()
                    raise Exception("can't get that element of the menu")
            computers = self.getProfileComputersDefaultMenuItem(
                profile.getUUID(), session
            )
            any_not_back_to_first = False
            for computer, m in computers:
                if m.fk_default_item != mi_id:
                    any_not_back_to_first = True

            if not any_not_back_to_first:
                self.profileChangeDefaultMenuItem(
                    imaging_server_uuid, profile.getUUID(), item_number
                )

        else:
            mis = session.query(MenuItem).select_from(
                self.menu_item.join(
                    self.menu, self.menu.c.id == self.menu_item.c.fk_menu
                )
            )
            mis = (
                mis.filter(self.menu.c.id == menu.id)
                .order_by(self.menu_item.c.order)
                .all()
            )
            if len(mis) > item_number:
                self.__computerChangeDefaultMenuItem(session, menu, mis, item_number)
            else:
                session.close()
                raise Exception("can't get that element of the menu")
        session.flush()
        session.close()
        return True

    def __addBootServiceInMenu(self, session, mi_id, bs_uuid):
        bsim = BootServiceInMenu()
        bsim.fk_menuitem = mi_id
        bsim.fk_bootservice = uuid2id(bs_uuid)
        session.add(bsim)
        session.flush()
        return bsim

    def __addImageInMenu(self, session, mi_id, im_uuid):
        imim = ImageInMenu()
        imim.fk_menuitem = mi_id
        imim.fk_image = uuid2id(im_uuid)
        session.add(imim)
        session.flush()
        return imim

    def __addService(self, session, bs_uuid, menu, params):
        if menu is None:
            raise "%s:Please create menu before trying to put a bootservice" % (
                P2ERR.ERR_TARGET_HAS_NO_MENU
            )

        mi = self.__createNewMenuItem(session, menu.id, params)
        session.flush()

        self.__addMenuDefaults(session, menu, mi, params)
        self.__addBootServiceInMenu(session, mi.id, bs_uuid)

        self.__sortMenuItems(menu.id, session)
        session.close()
        return None

    def addServiceToTarget(self, bs_uuid, target_uuid, params):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid, session)
        ret = self.__addService(session, bs_uuid, menu, params)
        session.close()
        return ret

    def addServiceToEntity(self, bs_uuid, loc_id, params):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id, session)
        ret = self.__addService(session, bs_uuid, menu, params)
        session.close()
        return ret

    def __getServiceMenuItem(self, session, bs_uuid, target_uuid):
        mi = session.query(MenuItem).select_from(
            self.menu_item.join(
                self.boot_service_in_menu,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
            .join(
                self.boot_service,
                self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            )
            .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id)
            .join(self.target, self.target.c.fk_menu == self.menu.c.id)
        )
        mi = mi.filter(
            and_(
                self.boot_service.c.id == uuid2id(bs_uuid),
                self.target.c.uuid == target_uuid,
            )
        ).first()
        return mi

    def __editService(self, session, bs_uuid, menu, mi, params):
        if menu is None:
            raise "%s:Please create menu before trying to put a bootservice" % (
                P2ERR.ERR_TARGET_HAS_NO_MENU
            )

        mi = self.__fillMenuItem(session, mi, menu.id, params)
        session.flush()

        self.__editMenuDefaults(session, menu, mi, params)

        session.flush()
        return None

    def editServiceToTarget(self, bs_uuid, target_uuid, target_type, params):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid, session)
        mi = self.__getServiceMenuItem(session, bs_uuid, target_uuid)
        if target_type == P2IT.PROFILE:
            for computer in ComputerProfileManager().getProfileContent(target_uuid):
                cmenu = self.getTargetsMenuTUUID(computer.uuid, session)
                self.__editService(session, bs_uuid, cmenu, mi, params)

        ret = self.__editService(session, bs_uuid, menu, mi, params)
        session.close()
        return ret

    def removeService(self, bs_uuid, loc_id, params):
        session = create_session()

        # Update PostInstallScript table and remove fk link to BootService
        # table
        pis = (
            session.query(PostInstallScript)
            .filter(self.post_install_script.c.fk_boot_service == uuid2id(bs_uuid))
            .first()
        )
        # pis can be None if pis was deleted
        if pis:
            pis.fk_boot_service = None
            session.flush()

        bs = (
            session.query(BootService)
            .filter(self.boot_service.c.id == uuid2id(bs_uuid))
            .first()
        )
        session.delete(bs)
        session.flush()

        session.close()
        return [
            toUUID(bs.id),
            {
                "name": bs.default_name,
                "desc": bs.default_desc,
                "value": bs.value,
            },
        ]

    def __getMenuItemByUUID(self, session, mi_uuid):
        return (
            session.query(MenuItem)
            .filter(self.menu_item.c.id == uuid2id(mi_uuid))
            .first()
        )

    def editServiceToEntity(self, mi_uuid, loc_id, params):
        session = create_session()
        if self.isLocalBootService(mi_uuid, session):
            # we can change the title/desc/...
            bs = session.query(BootService).select_form(
                self.boot_service.join(self.boot_service_in_menu)
            )
            bs = bs.filter(
                self.boot_service_in_menu.c.fk_menuitem == uuid2id(mi_uuid)
            ).first()
            if bs.default_name != params["default_name"]:
                bs.default_name = params["default_name"]
                bs.fk_name = 1
                session.add(bs)
        mi = self.__getMenuItemByUUID(session, mi_uuid)
        if mi is None:
            raise "%s:This MenuItem does not exists" % (P2ERR.ERR_UNEXISTING_MENUITEM)
        self.__fillMenuItem(session, mi, mi.fk_menu, params)
        # TODO : what do we do with ret ?
        session.flush()
        self.__editMenuDefaults(session, mi.fk_menu, mi, params)
        session.flush()
        session.close()
        return None

    def __getFirstMenuItem(self, session, menu_id, exclude=None):
        mi = session.query(MenuItem).filter(self.menu_item.c.fk_menu == menu_id)
        if exclude is not None:
            mi = mi.filter(self.menu_item.c.id != exclude)
        mi = mi.order_by(self.menu_item.c.order)
        return mi.first()

    def delServiceToTarget(self, bs_uuid, target_uuid):
        session = create_session()
        mi = session.query(MenuItem).select_from(
            self.menu_item.join(
                self.boot_service_in_menu,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
            .join(
                self.boot_service,
                self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            )
            .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id)
            .join(self.target, self.menu.c.id == self.target.c.fk_menu)
        )
        mi = mi.filter(
            and_(
                self.boot_service.c.id == uuid2id(bs_uuid),
                self.target.c.uuid == target_uuid,
            )
        ).first()
        bsim = session.query(BootServiceInMenu).select_from(
            self.boot_service_in_menu.join(
                self.menu_item,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
            .join(
                self.boot_service,
                self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            )
            .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id)
            .join(self.target, self.menu.c.id == self.target.c.fk_menu)
        )
        bsim = bsim.filter(
            and_(
                self.boot_service.c.id == uuid2id(bs_uuid),
                self.target.c.uuid == target_uuid,
            )
        ).first()
        # if mi is the fk_default_item or the fk_default_item_WOL, we need to
        # change that
        menu = session.query(Menu).filter(self.menu.c.id == mi.fk_menu).first()
        menu_id = menu.id
        need_to_save_menu = False
        first_mi = None
        if menu.fk_default_item == mi.id:
            need_to_save_menu = True
            if first_mi is None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi is None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item = first_mi.id
        if menu.fk_default_item_WOL == mi.id:
            need_to_save_menu = True
            if first_mi is None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi is None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item_WOL = first_mi.id
        if need_to_save_menu:
            session.add(menu)
            session.flush()
        session.delete(bsim)
        session.flush()
        session.delete(mi)
        session.flush()

        self.__sortMenuItems(menu_id, session)
        session.close()
        return [True]

    def delServiceToEntity(self, bs_uuid, loc_id):
        # FIXME : fk_default_menu has moved
        # FIXME : explicit joins, check why !
        session = create_session()
        mi = session.query(MenuItem).select_from(
            self.menu_item.join(
                self.boot_service_in_menu,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
            .join(
                self.boot_service,
                self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            )
            .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id)
            .join(
                self.imaging_server,
                self.imaging_server.c.fk_default_menu == self.menu.c.id,
            )
            .join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity)
        )
        mi = mi.filter(
            and_(
                self.boot_service.c.id == uuid2id(bs_uuid), self.entity.c.uuid == loc_id
            )
        ).first()
        bsim = session.query(BootServiceInMenu).select_from(
            self.boot_service_in_menu.join(
                self.menu_item,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
            .join(
                self.boot_service,
                self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            )
            .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id)
            .join(
                self.imaging_server,
                self.imaging_server.c.fk_default_menu == self.menu.c.id,
            )
            .join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity)
        )
        bsim = bsim.filter(
            and_(
                self.boot_service.c.id == uuid2id(bs_uuid), self.entity.c.uuid == loc_id
            )
        ).first()
        # if mi is the fk_default_item or the fk_default_item_WOL, we need to
        # change that
        menu = session.query(Menu).filter(self.menu.c.id == mi.fk_menu).first()
        need_to_save_menu = False
        first_mi = None
        if menu.fk_default_item == mi.id:
            need_to_save_menu = True
            if first_mi is None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi is None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item = first_mi.id
        if menu.fk_default_item_WOL == mi.id:
            need_to_save_menu = True
            if first_mi is None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi is None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item_WOL = first_mi.id
        if need_to_save_menu:
            session.add(menu)
            session.flush()

        session.delete(bsim)
        session.flush()
        session.delete(mi)
        session.flush()

        session.close()
        return [True]

    def getMenuItemByUUID(self, mi_uuid, session=None):
        session_need_close = False
        if session is None:
            session_need_close = True
            session = create_session()
        ims = (
            session.query(ImagingServer)
            .select_from(
                self.menu_item.outerjoin(
                    self.target, self.target.c.fk_menu == self.menu_item.c.fk_menu
                ).outerjoin(
                    self.imaging_server,
                    or_(
                        self.target.c.fk_entity == self.imaging_server.c.fk_entity,
                        self.imaging_server.c.fk_default_menu
                        == self.menu_item.c.fk_menu,
                    ),
                )
            )
            .filter(self.menu_item.c.id == uuid2id(mi_uuid))
            .first()
        )
        lang = ims.fk_language
        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        # we don't need the i18n trick for the menu name here
        mi = (
            session.query(MenuItem)
            .add_entity(BootService)
            .add_entity(Image)
            .add_entity(Menu)
        )
        mi = mi.add_entity(Internationalization, alias=I18n1).add_entity(
            Internationalization, alias=I18n2
        )
        mi = mi.select_from(
            self.menu_item.join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
            .outerjoin(self.boot_service_in_menu)
            .outerjoin(self.boot_service)
            .outerjoin(
                I18n1,
                and_(
                    self.boot_service.c.fk_name == I18n1.c.id,
                    I18n1.c.fk_language == lang,
                ),
            )
            .outerjoin(
                I18n2,
                and_(
                    self.boot_service.c.fk_desc == I18n2.c.id,
                    I18n2.c.fk_language == lang,
                ),
            )
            .outerjoin(self.image_in_menu)
            .outerjoin(self.image)
        )
        mi = mi.filter(self.menu_item.c.id == uuid2id(mi_uuid)).first()
        mi = self.__mergeBootServiceOrImageInMenuItem(mi)
        if hasattr(mi, "boot_service"):
            local = self.isLocalBootService(mi_uuid, session)
            setattr(mi.boot_service, "is_local", local)
        if session_need_close:
            session.close()
        return mi

    ######################
    def __PossibleImages(self, session, target_uuid, is_master, filt=""):
        q = session.query(Image).add_column(self.image.c.id)
        q = q.select_from(
            self.image.join(self.image_state)
            .join(self.image_on_imaging_server)
            .join(self.imaging_server)
            .join(self.entity)
            .join(self.target, self.target.c.fk_entity == self.entity.c.id)
            .join(self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id)
            .join(
                self.imaging_log,
                self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log,
            )
        )
        # , or_(self.image.c.is_master == True, and_(self.image.c.is_master == False, )))
        q = q.filter(self.target.c.uuid == target_uuid)
        if filt != "":
            q = q.filter(
                or_(
                    self.image.c.desc.like("%%%s%%" % filt),
                    self.image.c.name.like("%%%s%%" % filt),
                )
            )
        if is_master == P2IIK.IS_MASTER_ONLY:
            q = q.filter(self.image.c.is_master)
        elif is_master == P2IIK.IS_IMAGE_ONLY:
            q = q.filter(
                and_(
                    self.image.c.is_master == False,
                    self.target.c.id == self.imaging_log.c.fk_target,
                )
            )
        elif is_master == P2IIK.IS_BOTH:
            pass
        return q

    def __EntityImages(self, session, loc_id, filt):
        q = session.query(Image).add_column(self.image.c.id)
        q = q.select_from(
            self.image.join(self.image_on_imaging_server)
            .join(self.imaging_server)
            .join(self.entity)
        )
        q = q.filter(
            and_(
                self.entity.c.uuid == loc_id,
                self.image.c.is_master,
                or_(
                    self.image.c.name.like("%" + filt + "%"),
                    self.image.c.desc.like("%" + filt + "%"),
                ),
            )
        )
        return q

    def __PossibleImageAndMenuItem(self, session, bs_ids, menu_id):
        q = session.query(Image).add_entity(MenuItem)
        q = q.filter(
            and_(
                self.image_in_menu.c.fk_image == self.image.c.id,
                self.image_in_menu.c.fk_menuitem == self.menu_item.c.id,
                self.menu_item.c.fk_menu == menu_id,
                self.image.c.id.in_(bs_ids),
            )
        ).all()
        return q

    def getPossibleImagesOrMaster(
        self, target_uuid, target_type, is_master, start, end, filt
    ):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid)
        q1 = self.__PossibleImages(session, target_uuid, is_master, filt)
        q1 = q1.group_by(self.image.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end) - int(start))
        else:
            q1 = q1.all()
        bs_ids = [bs[1] for bs in q1]
        q2 = self.__PossibleImageAndMenuItem(session, bs_ids, menu.id)

        im_ids = [im[0].id for im in q1]
        q3 = (
            session.query(Target)
            .add_entity(MasteredOn)
            .select_from(self.target.join(self.imaging_log).join(self.mastered_on))
            .filter(self.mastered_on.c.fk_image.in_(im_ids))
            .all()
        )
        session.close()

        q = self.__mergeMenuItemInImage(q1, q2, q3)

        if is_master == P2IIK.IS_MASTER_ONLY and target_type == P2IT.COMPUTER:
            profile = ComputerProfileManager().getComputersProfile(target_uuid)
            if profile is not None:
                puuid = profile.id
                menu = self.getTargetsMenuTUUID(puuid)
                q1 = self.__PossibleImages(session, puuid, is_master, filt)
                q1 = q1.group_by(self.image.c.id)
                q1 = q1.all()
                bs_ids = [bs[1] for bs in q1]
                q2 = self.__PossibleImageAndMenuItem(session, bs_ids, menu.id)

                in_profile = {}
                for im, mi in q2:
                    if mi is not None:
                        in_profile[im.id] = mi

                ret = []
                for i in q:
                    if i.id in in_profile:
                        setattr(i, "read_only", True)
                        setattr(i, "menu_item", in_profile[i.id])
                    ret.append(i)
                q = ret
        return q

    def canRemoveFromMenu(self, image_uuid):
        session = create_session()
        mis = session.query(MenuItem).select_from(
            self.menu_item.join(
                self.image_in_menu,
                self.menu_item.c.id == self.image_in_menu.c.fk_menuitem,
            )
            .join(self.image, self.image.c.id == self.image_in_menu.c.fk_image)
            .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
            .join(self.target, self.target.c.fk_menu == self.menu.c.id)
        )
        mis = (
            mis.filter(
                and_(
                    self.image.c.id == uuid2id(image_uuid),
                    self.target.c.type.in_([P2IT.COMPUTER, P2IT.PROFILE]),
                )
            )
            .group_by(self.menu_item.c.id)
            .all()
        )

        for mi in mis:
            menu = session.query(Menu).filter(self.menu.c.id == mi.fk_menu).first()
            first_mi = None
            if menu.fk_default_item == mi.id:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi is None:
                    session.close()
                    return False
            if menu.fk_default_item_WOL == mi.id:
                if first_mi is None:
                    first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi is None:
                    session.close()
                    return False
        session.close()
        return True

    def imagingServerImageDelete(self, image_uuid):
        session = create_session()

        image_id = uuid2id(image_uuid)

        il = ImagingLog()
        il.timestamp = datetime.datetime.fromtimestamp(time.mktime(time.localtime()))
        il.fk_imaging_log_level = P2ILL.LOG_INFO
        il.detail = "Image %s has been removed from Imaging Server by %s" % (
            image_uuid,
            "",
        )
        il.fk_imaging_log_state = 8

        q = (
            session.query(MasteredOn)
            .add_entity(ImageOnImagingServer)
            .add_entity(Image)
            .add_column(self.imaging_log.c.fk_target)
            .select_from(
                self.mastered_on.join(
                    self.image, self.mastered_on.c.fk_image == self.image.c.id
                )
                .join(
                    self.image_on_imaging_server,
                    self.image_on_imaging_server.c.fk_image == self.image.c.id,
                )
                .join(
                    self.imaging_log,
                    self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log,
                )
            )
            .filter(self.image.c.id == image_id)
            .first()
        )

        mo, iois, image, target_id = q
        il.fk_target = target_id

        # delete PostInstallScriptInImage if exists
        session.query(PostInstallScriptInImage).filter(
            self.post_install_script_in_image.c.fk_image == image_id
        ).delete()
        session.flush()

        # TODO!
        # delete ImageInMenu and MenuItem if exists for all targets and put the
        # synchro state flag to TODO
        q = session.query(ImageInMenu).add_entity(MenuItem).add_entity(Target)
        q = (
            q.select_from(
                self.menu_item.join(
                    self.image_in_menu,
                    self.menu_item.c.id == self.image_in_menu.c.fk_menuitem,
                )
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
                .join(self.target, self.target.c.fk_menu == self.menu.c.id)
            )
            .filter(self.image_in_menu.c.fk_image == image_id)
            .all()
        )
        targets = {P2IT.COMPUTER: [], P2IT.PROFILE: []}
        for iim, mi, target in q:
            targets[target.type].append(target.uuid)
            session.delete(iim)
            session.flush()
            session.delete(mi)
            session.flush()

        for i in (P2IT.COMPUTER, P2IT.PROFILE):
            if len(targets[i]) > 0:
                self.changeTargetsSynchroState(targets[i], i, P2ISS.TODO)

        session.add(il)
        session.delete(mo)
        session.flush()
        session.delete(iois)
        session.flush()
        session.delete(image)
        session.flush()

        return True

    #        mo = session.query(MasteredOn).filter(self.mastered_on.c.fk_image == image_id).first()
    #        iois = session.query(ImageOnImagingServer).filter(self.image_on_imaging_server.c.fk_image == image_id).first()
    #        image = session.query(Image).filter(self.image.c.id == image_id).first()

    def countPossibleImagesOrMaster(self, target_uuid, _type, filt):
        session = create_session()
        q = self.__PossibleImages(session, target_uuid, _type, filt)
        q = q.count()
        session.close()
        return q

    def getPossibleImages(self, target_uuid, target_type, start, end, filt):
        return self.getPossibleImagesOrMaster(
            target_uuid, target_type, P2IIK.IS_IMAGE_ONLY, start, end, filt
        )

    def getPossibleMasters(self, target_uuid, target_type, start, end, filt):
        return self.getPossibleImagesOrMaster(
            target_uuid, target_type, P2IIK.IS_MASTER_ONLY, start, end, filt
        )

    def getComputerWithImageInEntity(self, uuidimagingServer):
        session = create_session()
        q = session.query(
            self.target.c.uuid.label("Computer"),
            self.target.c.name.label("ComputerName"),
            self.image.c.name.label("Nameimage"),
            self.image.c.is_master.label("masterimage"),
            self.imaging_server.c.name.label("nameimagingserver"),
            self.entity.c.uuid.label("uuidentity"),
        )
        q = q.select_from(
            self.image.join(
                self.image_state, self.image_state.c.id == self.image.c.fk_state
            )
            .join(
                self.image_on_imaging_server,
                self.image_on_imaging_server.c.fk_image == self.image.c.id,
            )
            .join(
                self.imaging_server,
                self.imaging_server.c.id
                == self.image_on_imaging_server.c.fk_imaging_server,
            )
            .join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity)
            .join(self.target, self.target.c.fk_entity == self.entity.c.id)
            .join(self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id)
            .join(
                self.imaging_log,
                self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log,
            )
        )
        q = q.filter(
            and_(
                self.entity.c.uuid == uuidimagingServer,
                self.target.c.id == self.imaging_log.c.fk_target,
            )
        )
        q = q.order_by(self.image.c.is_master)
        print(q)
        q = q.all()
        q1 = [
            [
                z.Computer,
                z.ComputerName,
                z.Nameimage,
                z.masterimage,
                z.nameimagingserver,
                z.uuidentity,
            ]
            for z in q
        ]
        return q1

    def getEntityMasters(self, loc_id, start, end, filt):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id)
        if menu is None:
            raise "%s:Entity does not have a default menu" % (
                P2ERR.ERR_ENTITY_HAS_NO_DEFAULT_MENU
            )
        q1 = self.__EntityImages(session, loc_id, filt)
        q1 = q1.group_by(self.image.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end) - int(start))
        else:
            q1 = q1.all()
        bs_ids = [bs[1] for bs in q1]
        q2 = self.__PossibleImageAndMenuItem(session, bs_ids, menu.id)
        session.close()

        q = self.__mergeMenuItemInImage(q1, q2)
        return q

    def getEntityMastersByUUID(self, loc_id, uuids):
        session = create_session()
        ret = {}
        q1 = self.__EntityImages(session, loc_id, "")
        q1 = q1.filter(self.image.c.id.in_([uuid2id(u) for u in uuids])).all()

        q2 = (
            session.query(PostInstallScript)
            .add_column(self.post_install_script_in_image.c.fk_image)
            .add_column(self.post_install_script_in_image.c.order)
        )
        q2 = q2.select_from(
            self.post_install_script.join(self.post_install_script_in_image)
        )
        q2 = q2.filter(
            self.post_install_script_in_image.c.fk_image.in_(
                [uuid2id(u) for u in uuids]
            )
        ).all()
        session.close()

        im_pis = {}
        for pis, im_id, order in q2:
            if im_id not in im_pis:
                # if not im_id in im_pis:
                im_pis[im_id] = {}
            pis = pis.toH()
            pis["order"] = order
            im_pis[im_id][order] = pis

        for im_id in im_pis:
            h_pis = im_pis[im_id]
            orders = sorted(h_pis.keys())
            a_pis = []
            for i in orders:
                a_pis.append(h_pis[i])
            im_pis[im_id] = a_pis

        for im, im_id in q1:
            ret[id2uuid(im_id)] = im.toH()
            if im_id in im_pis:
                ret[id2uuid(im_id)]["post_install_scripts"] = im_pis[im_id]
        return ret

    def countPossibleImages(self, target_uuid, filter):
        return self.countPossibleImagesOrMaster(
            target_uuid, P2IIK.IS_IMAGE_ONLY, filter
        )

    def countPossibleMasters(self, target_uuid, filter):
        return self.countPossibleImagesOrMaster(
            target_uuid, P2IIK.IS_MASTER_ONLY, filter
        )

    def countEntityMasters(self, loc_id, filter):
        session = create_session()
        q = self.__EntityImages(session, loc_id, filter)
        q = q.count()
        session.close()
        return q

    def __delImage(self, session, menu_item_id):
        """
        Queries to remove an image from default boot menu
        """
        s_menu_item = (
            session.query(MenuItem).filter(self.menu_item.c.id == menu_item_id).first()
        )
        s_image_in_menu = (
            session.query(ImageInMenu)
            .filter(self.image_in_menu.c.fk_menuitem == menu_item_id)
            .first()
        )
        session.delete(s_image_in_menu)
        session.flush()
        session.delete(s_menu_item)
        session.flush()
        return True

    def __addImage(self, session, item_uuid, menu, params):
        if menu is None:
            raise "%s:Please create menu before trying to put an image" % (
                P2ERR.ERR_TARGET_HAS_NO_MENU
            )
        # if 'name' in params and not 'default_name' in params:
        if "name" in params and "default_name" not in params:
            params["default_name"] = params["name"]
        mi = self.__createNewMenuItem(session, menu.id, params)
        session.flush()

        self.__addMenuDefaults(session, menu, mi, params)
        self.__addImageInMenu(session, mi.id, item_uuid)

        self.__sortMenuItems(menu.id, session)
        session.close()
        return None

    def addImageToTarget(self, item_uuid, target_uuid, params):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid, session)
        ret = self.__addImage(session, item_uuid, menu, params)
        session.close()
        return ret

    def registerImage(self, imaging_server_uuid, computer_uuid, params):
        """
        Registers an image into the database, and link it to a package server
        and to a computer.

        @return: True on success, else will raise an exception
        @rtype: bool
        """

        session = create_session()
        # check no image with the same uuid exists
        c = session.query(Image).filter(self.image.c.uuid == params["uuid"]).count()
        if c != 0:
            self.logger.warn(
                "an image with the same UUID already exists (%s)" % (params["uuid"])
            )
            raise "%s:An image with the same UUID already exists! (%s)" % (
                P2ERR.ERR_IMAGE_ALREADY_EXISTS,
                params["uuid"],
            )

        # create the image item
        image = Image()
        image.name = params["name"]
        image.desc = params["desc"]
        image.path = params["path"]
        image.uuid = params["uuid"]
        image.checksum = params["checksum"]
        image.size = params["size"]

        if isinstance(params["creation_date"], list):
            params["creation_date"] = tuple(params["creation_date"])

        image.creation_date = datetime.datetime.fromtimestamp(
            time.mktime(params["creation_date"])
        )
        image.fk_creator = 1  # TOBEDONE image['']
        image.is_master = params["is_master"]

        if params["state"] in self.r_nomenclatures["ImageState"]:
            image.fk_state = self.r_nomenclatures["ImageState"][params["state"]]
        elif params["state"] in self.nomenclatures["ImageState"]:
            image.fk_state = params["state"]
        else:  # this state is unknown!
            self.logger.warn("don't know that imaging log state %s" % (params["state"]))
            image.fk_state = 1  # the UNKNOWN entry

        session.add(image)
        session.flush()

        # fill the imaging_log
        #   there is way to much fields!
        imaging_log = ImagingLog()
        imaging_log.timestamp = datetime.datetime.fromtimestamp(
            time.mktime(params["creation_date"])
        )
        imaging_log.detail = params["desc"]
        imaging_log.fk_imaging_log_level = P2ILL.LOG_INFO
        imaging_log.fk_imaging_log_state = 1  # done
        target = (
            session.query(Target).filter(self.target.c.uuid == computer_uuid).first()
        )
        imaging_log.fk_target = target.id
        session.add(imaging_log)
        session.flush()

        # Mastered on
        mastered_on = MasteredOn()
        mastered_on.fk_image = image.id
        mastered_on.fk_imaging_log = imaging_log.id
        session.add(mastered_on)

        # link the image to the imaging_server
        ims = (
            session.query(ImagingServer)
            .filter(self.imaging_server.c.packageserver_uuid == imaging_server_uuid)
            .first()
        )
        ioims = ImageOnImagingServer()
        ioims.fk_image = image.id
        ioims.fk_imaging_server = ims.id
        session.add(ioims)

        # link the image to the machine
        # DONT PUT IN THE MENU BY DEFAULT
        # self.addImageToTarget(id2uuid(image.id), computer_uuid, params)
        session.flush()
        session.close()
        return True

    def logClientAction(self, loc_uuid, item_uuid, log):
        session = create_session()
        imaging_log = ImagingLog()
        imaging_log.timestamp = datetime.datetime.fromtimestamp(
            time.mktime(time.localtime())
        )
        imaging_log.detail = log["detail"]
        imaging_log.fk_imaging_log_level = log["level"]
        # if log['state'] in self.r_nomenclatures['ImagingLogState']:
        if log["state"] in self.r_nomenclatures["ImagingLogState"]:
            imaging_log.fk_imaging_log_state = self.r_nomenclatures["ImagingLogState"][
                log["state"]
            ]
            # elif log['state'] in self.nomenclatures['ImagingLogState']:
        elif log["state"] in self.nomenclatures["ImagingLogState"]:
            imaging_log.fk_imaging_log_state = log["state"]
        else:  # this state is unknown!
            self.logger.warn("don't know that imaging log state %s" % (log["state"]))
            imaging_log.fk_imaging_log_state = 1  # the UNKNOWN entry

        target = session.query(Target).filter(self.target.c.uuid == item_uuid).first()
        imaging_log.fk_target = target.id
        session.add(imaging_log)
        session.flush()
        session.close()
        return True

    def delImageToEntity(self, menu_item_id):
        """
        Queries to remove an image from default boot menu
        """
        session = create_session()
        ret = self.__delImage(session, menu_item_id)
        session.close()
        return ret

    def addImageToEntity(self, item_uuid, loc_id, params):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id, session)
        ret = self.__addImage(session, item_uuid, menu, params)
        session.close()
        return ret

    def __editImage(self, session, item_uuid, menu, mi, params):
        if menu is None:
            raise "%s:Please create menu before trying to put an image" % (
                P2ERR.ERR_TARGET_HAS_NO_MENU
            )

        mi = self.__fillMenuItem(session, mi, menu.id, params)
        session.flush()

        self.__editMenuDefaults(session, menu, mi, params)

        session.flush()
        return None

    def __getImageMenuItem(self, session, item_uuid, target_uuid):
        mi = session.query(MenuItem).select_from(
            self.menu_item.join(
                self.image_in_menu,
                self.image_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
            .join(self.image, self.image_in_menu.c.fk_image == self.image.c.id)
            .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id)
            .join(self.target, self.menu.c.id == self.target.c.fk_menu)
        )
        mi = mi.filter(
            and_(
                self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid
            )
        ).first()
        return mi

    def __getImageMenuItem4Entity(self, session, item_uuid, loc_id):
        """
        given an item ID and an entity ID, get I don't now what
        TODO : don't see what has to be done here ...
        """
        j = (
            self.menu_item.join(self.image_in_menu)
            .join(self.image)
            .join(self.menu)
            .join(self.imaging_server)
        )
        f = and_(
            self.menu_item.c.id == uuid2id(item_uuid),
            self.menu.c.id == self.imaging_server.c.fk_default_menu,
            self.entity.c.uuid == loc_id,
        )
        mi = session.query(MenuItem).select_from(j)
        mi = mi.filter(f)
        mi = mi.first()
        return mi

    def editImageToTarget(self, item_uuid, target_uuid, target_type, params):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid, session)
        mi = self.__getImageMenuItem(session, item_uuid, target_uuid)
        if target_type == P2IT.PROFILE:
            for computer in ComputerProfileManager().getProfileContent(target_uuid):
                cmenu = self.getTargetsMenuTUUID(computer.uuid, session)
                self.__editImage(session, item_uuid, cmenu, mi, params)

        ret = self.__editImage(session, item_uuid, menu, mi, params)
        session.close()
        return ret

    def editImageToEntity(self, item_uuid, loc_id, params):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id, session)
        mi = self.__getImageMenuItem4Entity(session, item_uuid, loc_id)
        ret = self.__editImage(session, item_uuid, menu, mi, params)
        session.close()
        return ret

    def __queryImageInMenu(self, session):
        return (
            session.query(Image)
            .add_entity(Target)
            .select_from(
                self.image.join(
                    self.image_in_menu, self.image.c.id == self.image_in_menu.c.fk_image
                )
                .join(
                    self.menu_item,
                    self.menu_item.c.id == self.image_in_menu.c.fk_menuitem,
                )
                .join(self.target, self.target.c.fk_menu == self.menu_item.c.fk_menu)
            )
        )

    def __queryImageInImagingServerMenu(self, session):
        return (
            session.query(Image)
            .add_entity(ImagingServer)
            .add_entity(Entity)
            .select_from(
                self.image.join(
                    self.image_in_menu, self.image.c.id == self.image_in_menu.c.fk_image
                )
                .join(
                    self.menu_item,
                    self.menu_item.c.id == self.image_in_menu.c.fk_menuitem,
                )
                .join(
                    self.imaging_server,
                    self.imaging_server.c.fk_default_menu == self.menu_item.c.fk_menu,
                )
                .join(self.entity, self.imaging_server.c.fk_entity == self.entity.c.id)
            )
        )

    def isImageInMenu(self, item_uuid, target_uuid=None, target_type=None):
        session = create_session()
        q = self.__queryImageInMenu(session)
        if target_uuid is not None:
            q = q.filter(
                and_(
                    self.target.c.uuid == target_uuid,
                    self.target.c.type == target_type,
                    self.image.c.id == uuid2id(item_uuid),
                )
            )
        else:
            q = q.filter(self.image.c.id == uuid2id(item_uuid))
        q = q.count()
        return q > 0

    def areImagesUsed(self, images):
        session = create_session()
        ret = {}
        for item_uuid, target_uuid, target_type in images:
            # check in targets
            q = self.__queryImageInMenu(session)
            q = q.filter(self.image.c.id == uuid2id(item_uuid)).all()
            ret1 = []
            for im, target in q:
                target = target.toH()
                ret1.append([target["uuid"], target["type"], target["name"]])

            # check in imaging server (they can also have a reference in the
            # boot menu)
            q = self.__queryImageInImagingServerMenu(session)
            if target_uuid is not None and target_type == -1:
                q = q.filter(
                    and_(
                        self.image.c.id == uuid2id(item_uuid),
                        self.imaging_server.c.id != uuid2id(target_uuid),
                    )
                ).all()
            else:
                q = q.filter(self.image.c.id == uuid2id(item_uuid)).all()
            for im, ims, entity in q:
                ims = ims.toH()
                entity = entity.toH()
                ret1.append([entity["uuid"], -1, ims["name"]])
            ret[item_uuid] = ret1
        return ret

    def isServiceUsed(self, bs_uuid):
        session = create_session()
        # Check in Targets
        q = session.query(Target)
        q = q.select_from(
            self.target.outerjoin(self.menu, self.menu.c.id == self.target.c.fk_menu)
            .outerjoin(self.menu_item, self.menu_item.c.fk_menu == self.menu.c.id)
            .outerjoin(
                self.boot_service_in_menu,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
        )
        q = q.filter(
            self.boot_service_in_menu.c.fk_bootservice == uuid2id(bs_uuid)
        ).all()

        ret = []
        for target in q:
            target = target.toH()
            ret.append(
                {
                    "uuid": target["imaging_uuid"],
                    "type": target["type"],
                    "name": target["name"],
                }
            )

        # Check in imaging server
        q = session.query(ImagingServer)
        q = q.select_from(
            self.imaging_server.outerjoin(
                self.menu, self.menu.c.id == self.imaging_server.c.fk_default_menu
            )
            .outerjoin(self.menu_item, self.menu_item.c.fk_menu == self.menu.c.id)
            .outerjoin(
                self.boot_service_in_menu,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
        )
        q = q.filter(
            self.boot_service_in_menu.c.fk_bootservice == uuid2id(bs_uuid)
        ).all()

        for target in q:
            target = target.toH()
            ret.append(
                {
                    "uuid": target["imaging_uuid"],
                    "type": -1,
                    "name": target["name"],
                }
            )

        session.close()
        return ret

    def __editImage__grepAndStartOrderAtZero(self, post_install_scripts):
        ret = {}
        inverted = {}
        for pisid in post_install_scripts:
            if post_install_scripts[pisid] != "None":
                inverted[post_install_scripts[pisid]] = pisid
        i = 0
        my_keys = sorted(inverted.keys())
        for order in my_keys:
            ret[inverted[order]] = i
            i += 1
        return ret

    def editImage(self, item_uuid, params):
        session = create_session()
        im = session.query(Image).filter(self.image.c.id == uuid2id(item_uuid)).first()
        if im is None:
            raise "%s:Cant find the image you are trying to edit." % (P2ERR.ERR_DEFAULT)
        need_to_be_save = False
        for p in ("name", "desc", "is_master", "size"):
            if p in params and params[p] != getattr(im, p):
                need_to_be_save = True
                setattr(im, p, params[p])
        if "state" in params:
            if params["state"] in self.r_nomenclatures["ImageState"]:
                im.fk_state = self.r_nomenclatures["ImageState"][params["state"]]
            elif params["state"] in self.nomenclatures["ImageState"]:
                im.fk_state = params["state"]
            else:  # this state is unknown!
                self.logger.warn(
                    "don't know that imaging log state %s" % (params["state"])
                )
                im.fk_state = 1  # the UNKNOWN entry

        if "is_master" in params:
            if (
                params["is_master"]
                and "post_install_scripts" in params
                or not params["is_master"]
            ):
                pisiis = (
                    session.query(PostInstallScriptInImage)
                    .filter(
                        self.post_install_script_in_image.c.fk_image
                        == uuid2id(item_uuid)
                    )
                    .all()
                )
                for p in pisiis:
                    session.delete(p)
                session.flush()

            if params["is_master"] and "post_install_scripts" in params:
                post_install_scripts = self.__editImage__grepAndStartOrderAtZero(
                    params["post_install_scripts"]
                )
                for pis in post_install_scripts:
                    pisii = PostInstallScriptInImage()
                    pisii.fk_image = uuid2id(item_uuid)
                    pisii.fk_post_install_script = uuid2id(pis)
                    pisii.order = post_install_scripts[pis]
                    session.add(pisii)

        if need_to_be_save:
            session.add(im)
        session.flush()
        session.close()
        return im.id

    def delImageToTarget(self, item_uuid, target_uuid):
        session = create_session()
        mi = session.query(MenuItem).select_from(
            self.menu_item.join(
                self.image_in_menu,
                self.menu_item.c.id == self.image_in_menu.c.fk_menuitem,
            )
            .join(self.image, self.image.c.id == self.image_in_menu.c.fk_image)
            .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
            .join(self.target, self.target.c.fk_menu == self.menu.c.id)
        )
        mi = mi.filter(
            and_(
                self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid
            )
        ).first()
        iim = session.query(ImageInMenu).select_from(
            self.image_in_menu.join(
                self.menu_item, self.menu_item.c.id == self.image_in_menu.c.fk_menuitem
            )
            .join(self.image, self.image.c.id == self.image_in_menu.c.fk_image)
            .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
            .join(self.target, self.target.c.fk_menu == self.menu.c.id)
        )
        iim = iim.filter(
            and_(
                self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid
            )
        ).first()

        menu = session.query(Menu).filter(self.menu.c.id == mi.fk_menu).first()
        menu_id = menu.id
        need_to_save_menu = False
        first_mi = None
        if menu.fk_default_item == mi.id:
            need_to_save_menu = True
            if first_mi is None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi is None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item = first_mi.id
        if menu.fk_default_item_WOL == mi.id:
            need_to_save_menu = True
            if first_mi is None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi is None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item_WOL = first_mi.id
        if need_to_save_menu:
            session.add(menu)
            session.flush()

        session.delete(iim)
        session.flush()
        session.delete(mi)
        # TODO when it's not a master and the computer is the only one, what
        # should we do with the image?
        session.flush()
        self.__sortMenuItems(menu_id, session)
        session.close()
        return None

    def unregisterTargets(self, targets_uuid):
        """
        Unregister targets from DB
        @return list of uuid image directories to delete from imaging server
        """
        session = create_session()
        if not isinstance(targets_uuid, list):
            targets_uuid = [targets_uuid]

        for target_uuid in targets_uuid:
            self.logger.info("Going to unregister target %s from imaging" % target_uuid)
            mis = session.query(MenuItem).select_from(
                self.menu_item.join(
                    self.menu, self.menu.c.id == self.menu_item.c.fk_menu
                ).join(self.target, self.target.c.fk_menu == self.menu.c.id)
            )
            mis = mis.filter(self.target.c.uuid == target_uuid).all()
            mis_id = [mi.id for mi in mis]

            iims = session.query(ImageInMenu).select_from(
                self.image_in_menu.join(
                    self.menu_item,
                    self.menu_item.c.id == self.image_in_menu.c.fk_menuitem,
                )
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
                .join(self.target, self.target.c.fk_menu == self.menu.c.id)
            )
            iims = iims.filter(
                and_(self.menu_item.c.id.in_(mis_id), self.target.c.uuid == target_uuid)
            ).all()

            bsims = session.query(BootServiceInMenu).select_from(
                self.boot_service_in_menu.join(
                    self.menu_item,
                    self.menu_item.c.id == self.boot_service_in_menu.c.fk_menuitem,
                )
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
                .join(self.target, self.target.c.fk_menu == self.menu.c.id)
            )
            bsims = bsims.filter(
                and_(self.menu_item.c.id.in_(mis_id), self.target.c.uuid == target_uuid)
            ).all()

            # TODO : get all i18n to remove orphans!

            for iim in iims:
                self.logger.debug(
                    "Remove ImageInMenu %s %s"
                    % (str(iim.fk_menuitem), str(iim.fk_image))
                )
                session.delete(iim)

            for bsim in bsims:
                self.logger.debug(
                    "Remove BootServiceInMenu %s %s"
                    % (str(bsim.fk_menuitem), str(bsim.fk_bootservice))
                )
                session.delete(bsim)

            session.flush()

            menu = (
                session.query(Menu)
                .select_from(
                    self.menu.join(self.target, self.target.c.fk_menu == self.menu.c.id)
                )
                .filter(self.target.c.uuid == target_uuid)
                .first()
            )

            self.logger.debug("Changing type and menu for Target %s" % str(target_uuid))
            deleted_uuid = "DELETED %s" % target_uuid
            count = (
                session.query(Target).filter(self.target.c.uuid == deleted_uuid).count()
            )
            index = 0
            while count != 0:
                index += 1
                deleted_uuid = "DELETED %s %s" % (str(index), target_uuid)
                count = (
                    session.query(Target)
                    .filter(self.target.c.uuid == deleted_uuid)
                    .count()
                )

            target = (
                session.query(Target).filter(self.target.c.uuid == target_uuid).first()
            )
            target.fk_menu = 1  # we put it to the default 1 menu because we need it to be on something
            target.type = P2IT.DELETED_COMPUTER
            target.uuid = deleted_uuid
            session.add(target)
            session.flush()

            menu.fk_default_item = 1
            menu.fk_default_item_WOL = 1
            session.add(menu)
            session.flush()

            for mi in mis:
                self.logger.debug("Remove MenuItem %s" % (str(mi.id)))
                session.delete(mi)
            session.flush()

            session.delete(menu)
            session.flush()

            images = (
                session.query(Image)
                .add_entity(ImagingLog)
                .add_entity(MasteredOn)
                .select_from(
                    self.image.join(
                        self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id
                    )
                    .join(
                        self.imaging_log,
                        self.mastered_on.c.fk_imaging_log == self.imaging_log.c.id,
                    )
                    .join(self.target, self.imaging_log.c.fk_target == self.target.c.id)
                )
            )
            images = images.filter(
                and_(
                    self.target.c.uuid == deleted_uuid,
                    or_(
                        self.image.c.is_master == 0,
                    ),
                )
            ).all()

            images_id = [m[0].id for m in images]

            if images_id:
                post_install_script_in_image = (
                    session.query(PostInstallScriptInImage)
                    .filter(self.post_install_script_in_image.c.fk_image.in_(images_id))
                    .all()
                )

                image_on_imaging_server = (
                    session.query(ImageOnImagingServer)
                    .filter(self.image_on_imaging_server.c.fk_image.in_(images_id))
                    .all()
                )

                for pisim in post_install_script_in_image:
                    self.logger.debug(
                        "Remove post_install_script_in_image %s %s"
                        % (str(pisim.fk_image), str(pisim.fk_post_install_script))
                    )
                    session.delete(pisim)

                for iois in image_on_imaging_server:
                    self.logger.debug(
                        "Remove image_on_imaging_server %s %s"
                        % (str(iois.fk_image), str(iois.fk_imaging_server))
                    )
                    session.delete(iois)

            to_delete = []

            # result is the list of uuid image directories to delete
            result = []
            for image, imaging_log, mastered_on in images:
                result.append(image.uuid)
                self.logger.debug(
                    "Remove mastered on %s %s"
                    % (str(mastered_on.fk_image), str(mastered_on.fk_imaging_log))
                )
                session.delete(mastered_on)
                self.logger.debug("Remove Image %s" % (str(image.id)))
                to_delete.append(image)
                self.logger.debug("Remove imaging log %s" % (str(imaging_log.id)))
                to_delete.append(imaging_log)
            session.flush()

            for item in to_delete:
                session.delete(item)
            session.flush()

        session.close()
        return result

    ######################

    def __TargetImagesQuery(self, session, target_uuid, _type, filter):
        q = session.query(Image).add_entity(MenuItem)
        q = q.select_from(
            self.image.join(self.image_on_imaging_server)
            .join(self.imaging_server)
            .join(self.entity)
            .join(self.target)
            .join(self.image_in_menu)
            .join(self.menu_item)
        )
        q = q.filter(
            and_(
                self.target.c.uuid == target_uuid,
                or_(
                    self.image.c.desc.like("%" + filter + "%"),
                    self.image.c.name.like("%" + filter + "%"),
                ),
            )
        )
        return q

    def __TargetImagesNoMaster(self, session, target_uuid, _type, filter):
        q = self.__TargetImagesQuery(session, target_uuid, _type, filter)
        q.filter(self.image.c.is_master == False)
        return q

    def __TargetImagesIsMaster(self, session, target_uuid, _type, filter):
        q = self.__TargetImagesQuery(session, target_uuid, _type, filter)
        q.filter(self.image.c.is_master)
        return q

    ##
    def __ImagesInEntityQuery(self, session, entity_uuid, filter):
        q = session.query(Image).add_entity(MenuItem)
        q = q.select_from(
            self.image.join(self.image_on_imaging_server)
            .join(self.imaging_server)
            .join(self.entity)
            .outerjoin(self.image_in_menu)
            .outerjoin(self.menu_item)
        )
        q = q.filter(
            and_(
                self.entity.c.uuid == entity_uuid,
                or_(
                    self.image.c.desc.like("%" + filter + "%"),
                    self.image.c.name.like("%" + filter + "%"),
                ),
            )
        )
        return q

    def __ImagesInEntityNoMaster(self, session, target_uuid, _type, filter):
        q = self.__ImagesInEntityQuery(session, target_uuid, _type, filter)
        q.filter(self.image.c.is_master == False)
        return q

    def __ImagesInEntityIsMaster(self, session, target_uuid, _type, filt):
        q = self.__ImagesInEntityQuery(session, target_uuid, _type, filt)
        q.filter(self.image.c.is_master == False)
        return q

    def getTargetOwnImages(self, target_uuid, target_type):
        session = create_session()
        if target_type == P2IT.ALL_COMPUTERS:
            filt1 = and_(
                self.target.c.uuid == target_uuid,
                self.target.c.type.in_([P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE]),
            )
        else:
            filt1 = and_(
                self.target.c.uuid == target_uuid, self.target.c.type == target_type
            )

        q = (
            session.query(Image)
            .select_from(
                self.image.join(
                    self.mastered_on, self.image.c.id == self.mastered_on.c.fk_image
                )
                .join(
                    self.imaging_log,
                    self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log,
                )
                .join(self.target, self.target.c.id == self.imaging_log.c.fk_target)
            )
            .filter(filt1)
            .all()
        )

        session.close()
        return q

    def getTargetImages(self, target_uuid, target_type, start=0, end=-1, filt=""):
        session = create_session()
        if target_type == P2IT.ALL_COMPUTERS:
            filt1 = and_(
                self.target.c.uuid == target_uuid,
                self.target.c.type.in_([P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE]),
            )
        else:
            filt1 = and_(
                self.target.c.uuid == target_uuid, self.target.c.type == target_type
            )

        q1 = (
            session.query(Image)
            .add_entity(MenuItem)
            .select_from(
                self.image.outerjoin(
                    self.image_in_menu, self.image_in_menu.c.fk_image == self.image.c.id
                )
                .outerjoin(
                    self.menu_item,
                    self.image_in_menu.c.fk_menuitem == self.menu_item.c.id,
                )
                .join(self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id)
                .join(
                    self.imaging_log,
                    self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log,
                )
                .join(self.target, self.target.c.id == self.imaging_log.c.fk_target)
            )
            .filter(filt1)
            .all()
        )
        images_ids = [r[0].id for r in q1]

        ims = (
            session.query(ImagingServer)
            .select_from(
                self.imaging_server.join(
                    self.target,
                    self.target.c.fk_entity == self.imaging_server.c.fk_entity,
                )
            )
            .filter(filt1)
            .first()
        )
        lang = ims.fk_language

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q2 = (
            session.query(PostInstallScript)
            .add_column(self.post_install_script_in_image.c.order)
            .add_entity(Internationalization, alias=I18n1)
            .add_entity(Internationalization, alias=I18n2)
            .add_column(self.image.c.id)
            .select_from(
                self.image.join(
                    self.post_install_script_in_image,
                    self.post_install_script_in_image.c.fk_image == self.image.c.id,
                )
                .join(
                    self.post_install_script,
                    self.post_install_script_in_image.c.fk_post_install_script
                    == self.post_install_script.c.id,
                )
                .outerjoin(
                    I18n1,
                    and_(
                        self.post_install_script.c.fk_name == I18n1.c.id,
                        I18n1.c.fk_language == lang,
                    ),
                )
                .outerjoin(
                    I18n2,
                    and_(
                        self.post_install_script.c.fk_desc == I18n2.c.id,
                        I18n2.c.fk_language == lang,
                    ),
                )
            )
            .filter(self.image.c.id.in_(images_ids))
            .all()
        )
        q2 = self.__mergePostInstallScriptI18n(q2)
        h_pis_by_imageid = {}
        for pis in q2:
            # if not pis.image_id in h_pis_by_imageid:
            if pis.image_id not in h_pis_by_imageid:
                h_pis_by_imageid[pis.image_id] = []
            h_pis_by_imageid[pis.image_id].append(pis)

        ret = {}
        for im, mi in q1:
            q = self.__mergeMenuItemInImage([(im, im.id)], [[im, mi]])
            q = q[0]
            if im.id in h_pis_by_imageid:
                setattr(q, "post_install_scripts", h_pis_by_imageid[im.id])
            ret[mi.order] = q

        ret1 = []
        if end != -1:
            for i in range(start, end):
                if i in ret:
                    ret1.append(ret[i])
        else:
            ret1 = ret

        return ret1

    def countTargetImages(self, target_uuid, target_type, filter):
        session = create_session()
        q1 = (
            session.query(Image)
            .select_from(
                self.image.join(
                    self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id
                )
                .join(
                    self.imaging_log,
                    self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log,
                )
                .join(self.target, self.target.c.id == self.imaging_log.c.fk_target)
            )
            .filter(
                and_(
                    self.target.c.uuid == target_uuid, self.target.c.type == target_type
                )
            )
            .count()
        )
        return q1

    def __mergePostInstallScriptI18n(self, postinstallscript_list):
        ret = []
        for (
            postinstallscript,
            order,
            name_i18n,
            desc_i18n,
            im_id,
        ) in postinstallscript_list:
            if name_i18n is not None:
                setattr(postinstallscript, "default_name", name_i18n.label)
            if desc_i18n is not None:
                setattr(postinstallscript, "default_desc", desc_i18n.label)
            setattr(postinstallscript, "image_id", im_id)
            setattr(postinstallscript, "order", order)
            ret.append(postinstallscript)
        return ret

    def getTargetImage(self, uuid, target_type, image_uuid):
        session = create_session()
        q1 = (
            session.query(Image)
            .add_entity(MenuItem)
            .select_from(
                self.image.outerjoin(
                    self.image_in_menu, self.image_in_menu.c.fk_image == self.image.c.id
                )
                .outerjoin(
                    self.menu_item,
                    self.image_in_menu.c.fk_menuitem == self.menu_item.c.id,
                )
                .join(self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id)
                .join(
                    self.imaging_log,
                    self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log,
                )
                .join(self.target, self.target.c.id == self.imaging_log.c.fk_target)
            )
            .filter(
                and_(
                    self.image.c.id == uuid2id(image_uuid),
                    self.target.c.uuid == uuid,
                    self.target.c.type == target_type,
                )
            )
            .first()
        )
        if q1 is None:
            raise Exception("cant get the image %s for target %s" % (image_uuid, uuid))

        ims = (
            session.query(ImagingServer)
            .select_from(
                self.imaging_server.join(
                    self.target,
                    self.target.c.fk_entity == self.imaging_server.c.fk_entity,
                )
            )
            .filter(and_(self.target.c.uuid == uuid, self.target.c.type == target_type))
            .first()
        )
        lang = ims.fk_language

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q2 = (
            session.query(PostInstallScript)
            .add_column(self.post_install_script_in_image.c.order)
            .add_entity(Internationalization, alias=I18n1)
            .add_entity(Internationalization, alias=I18n2)
            .add_column(self.image.c.id)
            .select_from(
                self.image.join(
                    self.post_install_script_in_image,
                    self.post_install_script_in_image.c.fk_image == self.image.c.id,
                )
                .join(
                    self.post_install_script,
                    self.post_install_script_in_image.c.fk_post_install_script
                    == self.post_install_script.c.id,
                )
                .outerjoin(
                    I18n1,
                    and_(
                        self.post_install_script.c.fk_name == I18n1.c.id,
                        I18n1.c.fk_language == lang,
                    ),
                )
                .outerjoin(
                    I18n2,
                    and_(
                        self.post_install_script.c.fk_desc == I18n2.c.id,
                        I18n2.c.fk_language == lang,
                    ),
                )
            )
            .filter(self.image.c.id == uuid2id(image_uuid))
            .all()
        )
        q2 = self.__mergePostInstallScriptI18n(q2)
        im, mi = q1
        q = self.__mergeMenuItemInImage([(im, im.id)], [q1])
        q = q[0]
        setattr(q, "post_install_scripts", q2)
        return q

    ######################
    def getBootServicesOnTargetById(self, target_id, start, end, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu is None:
            return []
        menu_items = self.getMenuContent(menu.id, P2IM.BOOTSERVICE, start, end, filter)
        return menu_items

    def countBootServicesOnTargetById(self, target_id, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu is None:
            return 0
        count_items = self.countMenuContent(menu.id, P2IM.BOOTSERVICE, filter)
        return count_items

    def isLocalBootService(self, mi_uuid, session=None):
        """
        Check if MenuItem mi is a local boot service owned by an imaging
        server, or a global boot service.
        """
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()

        mi = session.query(MenuItem).add_entity(Entity)
        mi = mi.select_from(
            self.menu_item.join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu)
            .outerjoin(self.target)
            .outerjoin(
                self.imaging_server,
                self.imaging_server.c.fk_default_menu == self.menu.c.id,
            )
            .outerjoin(
                self.entity,
                or_(
                    self.entity.c.id == self.target.c.fk_entity,
                    self.entity.c.id == self.imaging_server.c.fk_entity,
                ),
            )
        )
        mi = mi.filter(
            and_(self.menu_item.c.id == uuid2id(mi_uuid), self.entity.c.id != None)
        ).first()
        loc_id = mi[1].uuid

        q = session.query(BootService).add_entity(BootServiceOnImagingServer)
        q = q.select_from(
            self.boot_service.join(self.boot_service_in_menu)
            .join(self.menu_item)
            .outerjoin(
                self.boot_service_on_imaging_server,
                self.boot_service.c.id
                == self.boot_service_on_imaging_server.c.fk_boot_service,
            )
            .outerjoin(
                self.imaging_server,
                self.imaging_server.c.id
                == self.boot_service_on_imaging_server.c.fk_imaging_server,
            )
            .outerjoin(self.entity)
        )
        q = q.filter(
            or_(
                self.boot_service_on_imaging_server.c.fk_boot_service == None,
                self.entity.c.uuid == loc_id,
            )
        )
        q = q.filter(self.menu_item.c.id == uuid2id(mi_uuid))
        q = q.first()

        ret = q[1] is not None

        if session_need_to_close:
            session.close()
        return ret

    ######################
    def getBootMenu(self, target_id, _type, start, end, filter):
        menu_items = []
        if _type == P2IT.COMPUTER:
            profile = ComputerProfileManager().getComputersProfile(target_id)
            if profile is not None:
                # this should be the profile uuid!
                menu_root = self.getTargetsMenuTUUID(profile.id)
                menu_items = self.getMenuContent(
                    menu_root.id, P2IM.ALL, start, end, filter
                )

        menu = self.getTargetsMenuTUUID(target_id)

        if menu is None:
            return menu_items

        root_len = len(menu_items)
        for i in range(0, len(menu_items)):
            setattr(menu_items[i], "read_only", True)

        menu_items1 = self.getMenuContent(menu.id, P2IM.ALL, start, end, filter)

        if menu_items == []:
            return menu_items1
        # need to merge menu_items and menu_items1
        for mi in menu_items1:
            mi.order += root_len
            menu_items.append(mi)
        for i in range(0, len(menu_items)):
            if menu_items[i].id == menu.fk_default_item:
                menu_items[i].default = True
            else:
                menu_items[i].default = False
            if menu_items[i].id == menu.fk_default_item_WOL:
                menu_items[i].default_WOL = True
            else:
                menu_items[i].default_WOL = False

        return menu_items

    def countBootMenu(self, target_id, _type, filter):
        count_items = 0
        if _type == P2IT.COMPUTER:
            profile = ComputerProfileManager().getComputersProfile(target_id)
            if profile is not None:
                # this should be the profile uuid!
                menu_root = self.getTargetsMenuTUUID(profile.id)
                count_items = self.countMenuContent(menu_root.id, P2IM.ALL, filter)

        menu = self.getTargetsMenuTUUID(target_id)

        if menu is None:
            return count_items

        count_items += self.countMenuContent(menu.id, P2IM.ALL, filter)
        return count_items

    def getEntityBootMenu(self, loc_id, start, end, filter):
        menu = self.getEntityDefaultMenu(loc_id)
        if menu is None:
            return []
        menu_items = self.getMenuContent(menu.id, P2IM.ALL, start, end, filter)
        return menu_items

    def countEntityBootMenu(self, loc_id, filter):
        menu = self.getEntityDefaultMenu(loc_id)
        if menu is None:
            return 0
        count_items = self.countMenuContent(menu.id, P2IM.ALL, filter)
        return count_items

    ######################
    def __moveItemInMenu(self, menu, mi_uuid, reverse=False):
        session = create_session()
        mis = self.getMenuContent(menu.id, P2IM.ALL, 0, -1, "", session)
        # if reverse:
        #     mis.sort(lambda x, y: cmp(y.order, x.order))
        move = False
        mod_mi = [None, None]
        for mi in mis:
            if move:
                move = False
                mod_mi[1] = mi
            if str(mi.id) == str(uuid2id(mi_uuid)):
                move = True
                mod_mi[0] = mi
        if mod_mi[0] is not None and mod_mi[1] is not None:
            ord = mod_mi[0].order
            mod_mi[0].order = mod_mi[1].order
            mod_mi[1].order = ord
            session.add(mod_mi[0])
            session.add(mod_mi[1])
            session.flush()
            session.close()
        else:
            session.close()
            return False
        return True

    def moveItemUpInMenu(self, target_uuid, mi_uuid):
        menu = self.getTargetsMenuTUUID(target_uuid)
        ret = self.__moveItemInMenu(menu, mi_uuid, True)
        return ret

    def moveItemUpInMenu4Location(self, loc_id, mi_uuid):
        menu = self.getEntityDefaultMenu(loc_id)
        ret = self.__moveItemInMenu(menu, mi_uuid, True)
        return ret

    def moveItemDownInMenu(self, target_uuid, mi_uuid):
        menu = self.getTargetsMenuTUUID(target_uuid)
        ret = self.__moveItemInMenu(menu, mi_uuid)
        return ret

    def moveItemDownInMenu4Location(self, loc_id, mi_uuid):
        menu = self.getEntityDefaultMenu(loc_id)
        ret = self.__moveItemInMenu(menu, mi_uuid)
        return ret

    ##################################
    # ImagingServer
    def getEntityStatus(self, location):
        session = create_session()
        q = (
            session.query(Target)
            .add_entity(Image)
            .select_from(
                self.target.join(
                    self.imaging_server,
                    self.target.c.fk_entity == self.imaging_server.c.fk_entity,
                )
                .join(self.entity, self.entity.c.id == self.target.c.fk_entity)
                .outerjoin(
                    self.imaging_log, self.imaging_log.c.fk_target == self.target.c.id
                )
                .outerjoin(
                    self.mastered_on,
                    self.mastered_on.c.fk_imaging_log == self.imaging_log.c.id,
                )
                .outerjoin(self.image, self.mastered_on.c.fk_image == self.image.c.id)
            )
            .filter(
                and_(
                    self.entity.c.uuid == location,
                    self.target.c.type.in_([P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE]),
                )
            )
        )
        q = q.group_by().all()
        im_total = set()
        im_rescue = set()
        for t, i in q:
            # Targets set
            im_total.add(t)
            if i is not None and not i.is_master:
                # Targets set with a rescue image
                im_rescue.add(t)

        im_master = (
            session.query(Image)
            .select_from(
                self.image.join(
                    self.image_on_imaging_server,
                    self.image_on_imaging_server.c.fk_image == self.image.c.id,
                )
                .join(
                    self.imaging_server,
                    self.image_on_imaging_server.c.fk_imaging_server
                    == self.imaging_server.c.id,
                )
                .join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity)
            )
            .filter(and_(self.entity.c.uuid == location, self.image.c.is_master == 1))
            .count()
        )

        return {"total": len(im_total), "rescue": len(im_rescue), "master": im_master}

    def countImagingServerByPackageServerUUID(self, uuid):
        session = create_session()
        q = (
            session.query(ImagingServer)
            .filter(self.imaging_server.c.packageserver_uuid == uuid)
            .count()
        )
        session.close()
        return q

    def getImageAndImagingServer(self, uuid, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        q = (
            session.query(Image)
            .add_entity(ImagingServer)
            .select_from(
                self.imaging_server.join(self.image_on_imaging_server).join(self.image)
            )
            .filter(self.image.c.id == uuid2id(uuid))
            .first()
        )

        if session_need_to_close:
            session.close()
        return q

    def getImageImagingServer(self, uuid, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        q = (
            session.query(ImagingServer)
            .select_from(
                self.imaging_server.join(self.image_on_imaging_server).join(self.image)
            )
            .filter(self.image.c.id == uuid2id(uuid))
            .first()
        )

        if session_need_to_close:
            session.close()
        return q

    def getImagingServerByUUID(self, uuid, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        q = (
            session.query(ImagingServer)
            .filter(self.imaging_server.c.id == uuid2id(uuid))
            .first()
        )
        if session_need_to_close:
            session.close()
        return q

    def getLinkedEntityByEntityUUID(self, uuid, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        q = (
            session.query(Entity)
            .select_from(self.imaging_server.join(self.entity))
            .filter(self.entity.c.uuid == uuid)
            .first()
        )
        if q is None:
            parent_path = ComputerLocationManager().getLocationParentPath(uuid)
            q = (
                session.query(Entity)
                .add_column(self.entity.c.uuid)
                .select_from(self.imaging_server.join(self.entity))
                .filter(
                    and_(
                        self.entity.c.uuid.in_(parent_path),
                        self.imaging_server.c.is_recursive == 1,
                        self.imaging_server.c.associated == 1,
                    )
                )
                .all()
            )
            h_temp = {}
            for entity, en_uuid in q:
                h_temp[en_uuid] = entity
            for en_uuid in parent_path:
                if en_uuid in h_temp:
                    q = h_temp[en_uuid]
                    continue
        if session_need_to_close:
            session.close()
        return q

    def getImagingServerByEntityUUID(self, uuid, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        q = (
            session.query(ImagingServer)
            .select_from(self.imaging_server.join(self.entity))
            .filter(self.entity.c.uuid == uuid)
            .first()
        )
        if q is None:
            parent_path = ComputerLocationManager().getLocationParentPath(uuid)
            q = (
                session.query(ImagingServer)
                .add_column(self.entity.c.uuid)
                .select_from(self.imaging_server.join(self.entity))
                .filter(
                    and_(
                        self.entity.c.uuid.in_(parent_path),
                        self.imaging_server.c.is_recursive == 1,
                        self.imaging_server.c.associated == 1,
                    )
                )
                .all()
            )
            h_temp = {}
            for imaging_server, en_uuid in q:
                h_temp[en_uuid] = imaging_server
            for en_uuid in parent_path:
                if en_uuid in h_temp:
                    q = h_temp[en_uuid]
                    continue
        if session_need_to_close:
            session.close()
        return q

    def getImagingServerByPackageServerUUID(self, uuid, with_entity=False):
        session = create_session()
        q = session.query(ImagingServer)
        if with_entity:
            q = q.add_entity(Entity).select_from(self.imaging_server.join(self.entity))
        q = q.filter(self.imaging_server.c.packageserver_uuid == uuid).all()
        session.close()
        return q

    def registerImagingServer(self, name, url, uuid):
        session = create_session()
        ims = ImagingServer()
        ims.name = name
        ims.url = url
        ims.fk_entity = 1  # the 'root' entity
        ims.packageserver_uuid = uuid
        # the default "subscribe" menu, which is shown when an unknown client
        # boots
        ims.fk_default_menu = 1
        ims.associated = 0  # we are registered, but not yet associated
        ims.fk_language = 1  # default on English
        self.imagingServer_lang[uuid] = 1
        session.add(ims)
        session.flush()
        session.close()
        return ims.id

    def updateImagingServer(self, uuid, params={}):
        session = create_session()
        ims = self.getImagingServerByUUID(uuid, session)
        need_to_be_save = False
        for param in params:
            if hasattr(ims, param):
                if getattr(ims, param) != params[param]:
                    setattr(ims, param, params[param])
                    need_to_be_save = True
            else:
                self.logger.debug(
                    "trying to update something that don't exists in ImagingServer"
                )
        if need_to_be_save:
            session.add(ims)
            session.flush()
        session.close()
        return True

    def getEntityByUUID(self, loc_id, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        ret = session.query(Entity).filter(self.entity.c.uuid == loc_id).first()
        if session_need_to_close:
            session.close()
        return ret

    def getMenusByID(self, menus_id, session):
        q = session.query(Menu).filter(self.menu.c.id.in_(menus_id)).all()
        return q

    def getMenuByUUID(self, menu_uuid, session=None):
        # dont need the i18n trick here, we just want to modify some menu
        # internals
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        q = session.query(Menu).filter(self.menu.c.id == uuid2id(menu_uuid)).first()
        if session_need_to_close:
            session.close()
        return q

    def modifyMenus(self, menus_id, params):
        session = create_session()
        menus = self.getMenusByID(menus_id, session)
        for m in menus:
            for p in [
                "default_name",
                "hidden_menu",
                "timeout",
                "background_uri",
                "message",
                "default_item",
                "default_item_WOL",
            ]:
                if p in params:
                    setattr(m, p, params[p])
        session.flush()
        session.close()
        return True

    def __modifyMenu(self, menu_uuid, params, session=None):
        """
        Modify menu in database according to params dict content
        """
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        menu = self.getMenuByUUID(menu_uuid, session)
        need_to_be_save = False
        # FIXME: could be factorized
        if "default_name" in params and menu.default_name != params["default_name"]:
            need_to_be_save = True
            menu.default_name = params["default_name"]
            menu.fk_name = 1
        if "timeout" in params and menu.timeout != params["timeout"]:
            need_to_be_save = True
            menu.timeout = params["timeout"]
        if "hidden_menu" in params and menu.hidden_menu != params["hidden_menu"]:
            need_to_be_save = True
            menu.hidden_menu = params["hidden_menu"]

        for option in [
            "hidden_menu",
            "bootcli",
            "dont_check_disk_size",
            "update_nt_boot",
            "disklesscli",
        ]:
            if option in params and params[option]:
                params[option] = 1
            else:
                params[option] = 0
            if getattr(menu, option) != params[option]:
                need_to_be_save = True
                setattr(menu, option, params[option])
        if (
            "background_uri" in params
            and menu.background_uri != params["background_uri"]
        ):
            need_to_be_save = True
            menu.background_uri = params["background_uri"]
        if "message" in params and menu.message != params["message"]:
            need_to_be_save = True
            menu.message = params["message"]
        if need_to_be_save:
            session.add(menu)
        if session_need_to_close:
            session.flush()
            session.close()
        return menu

    def modifyMenu(self, menu_uuid, params):
        self.__modifyMenu(menu_uuid, params)
        return True

    def __getDefaultMenu(self, session, lang=1):
        ret = (
            session.query(Menu)
            .add_column(self.internationalization.c.label)
            .select_from(
                self.menu.outerjoin(
                    self.internationalization,
                    and_(
                        self.internationalization.c.id == self.menu.c.fk_name,
                        self.internationalization.c.fk_language == lang,
                    ),
                )
            )
            .filter(self.menu.c.id == 1)
            .first()
        )
        if ret[1] is not None and ret[1] != "NOTTRANSLATED":
            ret[0].default_name = ret[1]
        return ret[0]

    def __getDefaultMenuItem(self, session, menu_id=1):
        default_item = (
            session.query(MenuItem)
            .filter(
                and_(
                    self.menu.c.id == menu_id,
                    self.menu.c.fk_default_item == self.menu_item.c.id,
                )
            )
            .first()
        )
        default_item_WOL = (
            session.query(MenuItem)
            .filter(
                and_(
                    self.menu.c.id == menu_id,
                    self.menu.c.fk_default_item_WOL == self.menu_item.c.id,
                )
            )
            .first()
        )
        return [default_item, default_item_WOL]

    def __getDefaultMenuMenuItems(self, session):
        return self.__getMenuItemsInMenu(session, 1)

    def __getMenuItemsInMenu(self, session, menu_id):
        return (
            session.query(MenuItem)
            .add_entity(BootServiceInMenu)
            .add_entity(ImageInMenu)
            .select_from(
                self.menu_item.outerjoin(self.boot_service_in_menu).outerjoin(
                    self.image_in_menu
                )
            )
            .filter(self.menu_item.c.fk_menu == menu_id)
            .all()
        )

    def __duplicateDefaultMenuItem(self, session, loc_id=None, p_id=None):
        # warning ! can't be an image !
        default_list = []
        if p_id is not None:
            # get the profile menu
            menu = self.getTargetMenu(p_id, P2IT.PROFILE, session)
            default_list = self.__getMenuItemsInMenu(session, menu.id)
            mi = self.__getDefaultMenuItem(session, menu.id)
        elif loc_id is not None:
            # get the entity menu
            menu = self.getEntityDefaultMenu(loc_id, session)
            default_list = self.__getMenuItemsInMenu(session, menu.id)
            mi = self.__getDefaultMenuItem(session, menu.id)
        else:
            # get the default menu
            default_list = self.__getDefaultMenuMenuItems(session)
            mi = self.__getDefaultMenuItem(session)
        ret = []
        mi_out = [0, 0]
        for default_menu_item, default_bsim, default_iim in default_list:
            menu_item = MenuItem()
            menu_item.order = default_menu_item.order
            menu_item.hidden = default_menu_item.hidden
            menu_item.hidden_WOL = default_menu_item.hidden_WOL
            menu_item.fk_menu = (
                1  # default Menu, need to be change as soon as we have the menu id!
            )
            session.add(menu_item)
            ret.append(menu_item)
            session.flush()
            for counter, elem in enumerate(mi):
                # Duplication of menu items will fail if no default bootmenu is set
                # for WOL or normal boot, so raise an exception if this is not
                # the case
                if elem is None:
                    raise Exception(
                        "No default bootmenu entry has been selected for %s"
                        % (counter and "WOL" or "normal boot")
                    )
            if mi[0].id == default_menu_item.id:
                mi_out[0] = menu_item.id
            if mi[1].id == default_menu_item.id:
                mi_out[1] = menu_item.id
            if default_bsim is not None:
                bsim = BootServiceInMenu()
                bsim.fk_menuitem = menu_item.id
                bsim.fk_bootservice = default_bsim.fk_bootservice
                session.add(bsim)
            if default_iim is not None:
                iim = ImageInMenu()
                iim.fk_menuitem = menu_item.id
                iim.fk_image = default_iim.fk_image
                session.add(iim)
        session.flush()
        return [ret, mi_out]

    def __duplicateDefaultMenu(self, session, loc_id):
        lang = self.__getLocLanguage(session, loc_id)
        default_menu = self.__getDefaultMenu(session, lang)
        return self.__duplicateMenu(session, default_menu)

    def __duplicateMenu(self, session, default_menu, loc_id=None, p_id=None, sub=False):
        menu = Menu()
        menu.default_name = default_menu.default_name
        menu.fk_name = default_menu.fk_name
        menu.timeout = default_menu.timeout
        menu.hidden_menu = default_menu.hidden_menu
        menu.background_uri = default_menu.background_uri
        menu.message = default_menu.message
        menu.ethercard = default_menu.ethercard
        menu.bootcli = default_menu.bootcli
        menu.disklesscli = default_menu.disklesscli
        menu.dont_check_disk_size = default_menu.dont_check_disk_size
        if sub:
            menu_items = []
            menu.fk_default_item = default_menu.fk_default_item
            menu.fk_default_item_WOL = default_menu.fk_default_item_WOL
        elif p_id is not None:
            menu_items = []
            menu.fk_default_item = None
            menu.fk_default_item_WOL = None
        else:
            menu_items, mi = self.__duplicateDefaultMenuItem(session, loc_id, p_id)
            menu.fk_default_item = mi[0]
            menu.fk_default_item_WOL = mi[1]
        menu.fk_synchrostate = 1
        session.add(menu)
        session.flush()
        for menu_item in menu_items:
            menu_item.fk_menu = menu.id
            session.add(menu_item)
        return menu

    def __createMenu(self, session, params):
        menu = Menu()
        menu.default_name = params["default_name"]
        menu.timeout = params["timeout"]
        menu.hidden_menu = params["hidden_menu"]
        menu.background_uri = params["background_uri"]
        menu.message = params["message"]
        menu.fk_default_item = 0
        menu.fk_default_item_WOL = 0
        menu.fk_synchrostate = 1
        menu.fk_name = 1
        session.add(menu)
        return menu

    def __createEntity(self, session, loc_id, loc_name):
        e = Entity()
        e.name = loc_name
        e.uuid = loc_id
        session.add(e)
        return e

    def getImagingServerEntity(self, imaging_server_uuid):
        """
        Get the entity linked to that imaging server, or None if the imaging
        server doesn't exist in database or has not been associated to an
        entity.
        """
        session = create_session()
        entity = (
            session.query(Entity)
            .select_from(
                self.entity.join(
                    self.imaging_server,
                    self.imaging_server.c.fk_entity == self.entity.c.id,
                )
            )
            .filter(
                and_(
                    or_(
                        self.imaging_server.c.id
                        == imaging_server_uuid.replace("UUID", ""),
                        self.imaging_server.c.packageserver_uuid == imaging_server_uuid,
                    ),
                    self.imaging_server.c.associated == True,
                )
            )
            .first()
        )
        if entity == None:
            entity = (
                session.query(Entity)
                .select_from(
                    self.entity.join(
                        self.imaging_server,
                        self.imaging_server.c.fk_entity == self.entity.c.id,
                    )
                )
                .filter(
                    and_(
                        self.entity.c.uuid == imaging_server_uuid,
                        self.imaging_server.c.associated == True,
                    )
                )
                .first()
            )
        session.close()
        return entity

    def linkImagingServerToEntity(self, is_uuid, loc_id, loc_name):
        """
        Attach the entity loc_id, name loc_name, to the imaging server is_uuid
        """
        session = create_session()

        # checks if IS already exists
        imaging_server = self.getImagingServerByUUID(is_uuid, session)
        if imaging_server is None:
            raise Exception(
                "%s : No server exists with that uuid (%s)"
                % (P2ERR.ERR_IMAGING_SERVER_DONT_EXISTS, is_uuid)
            )

        # checks if entity is not already linked somewhere else
        potential_imaging_server_id = self.__getLinkedImagingServerForEntity(
            session, loc_id
        )
        if potential_imaging_server_id:
            raise Exception(
                "%s : This entity is already linked to the Imaging Server %s"
                % (P2ERR.ERR_ENTITY_ALREADY_EXISTS, potential_imaging_server_id)
            )

        location = self.getEntityByUUID(loc_id, session)
        if location is None:  # entity do not yet exists in database, let's create it !
            location = self.__createEntity(session, loc_id, loc_name)
            session.flush()

        # create default imaging server menu
        menu = self.__duplicateDefaultMenu(session, loc_id)
        session.flush()

        imaging_server.fk_entity = location.id
        imaging_server.fk_default_menu = menu.id
        imaging_server.associated = 1
        session.add(imaging_server)
        session.flush()

        session.close()
        return True

    def unlinkImagingServerToEntity(self, is_uuid):
        """
        Inverse method to linkImagingServerToEntity.

        @param is_uuid: Imaging server UUID
        @type is_uuid: str

        @return: True if success
        @rtype: bool
        """
        session = create_session()

        # checks if IS already exists
        imaging_server = self.getImagingServerByUUID(is_uuid, session)
        if imaging_server is None:
            raise Exception(
                "%s : No server exists with that uuid (%s)"
                % (P2ERR.ERR_IMAGING_SERVER_DONT_EXISTS, is_uuid)
            )

        imaging_server.associated = 0
        imaging_server.fk_entity = 1
        imaging_server.fk_default_menu = 1
        session.add(imaging_server)
        session.flush()

        session.close()
        return True

    def getListImagingServerAssociated(self):
        """
        method return list imaging server associated
        @return: @return: list of imaging server associated
        @rtype: list
        """
        session = create_session()
        q = session.query(ImagingServer).filter(self.imaging_server.c.associated == 1)
        q = q.all()
        session.close()
        return q

    def __getLinkedImagingServerForEntity(self, session, loc_id):
        """
        If this entity is linked to an imaging server, returns it's uuid, if not (or if the entity do not exists), return None
        """
        q = (
            session.query(ImagingServer)
            .select_from(self.imaging_server.join(self.entity))
            .filter(self.imaging_server.c.associated == 1)
            .filter(self.entity.c.uuid == loc_id)
            .first()
        )
        if q:
            return q.name
        return None

    def __AllNonLinkedImagingServer(self, session, filter):
        q = session.query(ImagingServer).filter(self.imaging_server.c.associated == 0)
        if filter and filter != "":
            q = q.filter(
                or_(
                    self.imaging_server.c.name.like("%" + filter + "%"),
                    self.imaging_server.c.url.like("%" + filter + "%"),
                    self.imaging_server.c.uuid.like("%" + filter + "%"),
                )
            )
        return q

    def getAllNonLinkedImagingServer(self, start, end, filter):
        session = create_session()
        q = self.__AllNonLinkedImagingServer(session, filter)
        if end != -1:
            q = q.offset(int(start)).limit(int(end) - int(start))
        else:
            q = q.all()
        session.close()
        return q

    def countAllNonLinkedImagingServer(self, filter):
        session = create_session()
        q = self.__AllNonLinkedImagingServer(session, filter)
        q = q.count()
        session.close()
        return q

    def doesLocationHasImagingServer(self, loc_id):
        session = create_session()
        q = (
            session.query(ImagingServer)
            .select_from(self.imaging_server.join(self.entity))
            .filter(self.imaging_server.c.associated == 1)
            .filter(self.entity.c.uuid == loc_id)
            .count()
        )
        return q != 0

    def checkLanguage(self, location, language):
        session = create_session()
        imaging_server = self.getImagingServerByEntityUUID(location, session)
        lang = (
            session.query(Language)
            .filter(self.language.c.id == uuid2id(language))
            .first()
        )
        if imaging_server.fk_language != lang.id:
            imaging_server.fk_language = lang.id
            session.add(imaging_server)
            session.flush()
        session.close()
        self.imagingServer_lang[location] = lang.id
        return True

    # REGISTRATION
    def setTargetRegisteredInPackageServer(self, uuid, target_type):
        session = create_session()

        if target_type == P2IT.ALL_COMPUTERS:
            filt = self.target.c.type.in_([P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE])
        else:
            filt = and_(self.target.c.type == target_type)
        if not isinstance(uuid, list):
            uuid = [uuid]
        if len(uuid) == 0:
            self.logger.debug(
                "setTargetRegisteredInPackageServer couldn't get target for %s"
                % (str(uuid))
            )
            session.close()
            return True
        q = session.query(Target).filter(and_(self.target.c.uuid.in_(uuid), filt)).all()
        for t in q:
            t.is_registered_in_package_server = 1
            session.add(t)
        session.flush()
        session.close()
        return True

    def isTargetRegisterInPackageServer(self, uuid, target_type, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()

        ret = False
        if target_type == P2IT.ALL_COMPUTERS:
            filt = self.target.c.type.in_([P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE])
        else:
            filt = and_(self.target.c.type == target_type)

        if isinstance(uuid, list):
            ret = {}
            q = (
                session.query(Target)
                .filter(and_(self.target.c.uuid.in_(uuid), filt))
                .all()
            )
            for target in q:
                ret[target.uuid] = target.is_registered_in_package_server == 1
            for l_uuid in uuid:
                # if not l_uuid in ret:
                if l_uuid not in ret:
                    ret[l_uuid] = False
        else:
            q = (
                session.query(Target)
                .filter(and_(self.target.c.uuid == uuid, filt))
                .first()
            )
            if q is not None:
                ret = ret.is_registered_in_package_server == 1
            else:
                ret = False

        if session_need_to_close:
            session.close()
        return ret

    def isTargetRegister(self, uuid, target_type, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()

        if target_type == P2IT.ALL_COMPUTERS:
            filt = self.target.c.type.in_([P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE])
        else:
            filt = and_(self.target.c.type == target_type)
        ret = False
        if isinstance(uuid, list):
            ret = {}
            q = (
                session.query(Target)
                .filter(and_(self.target.c.uuid.in_(uuid), filt))
                .all()
            )
            for target in q:
                ret[target.uuid] = True
            for l_uuid in uuid:
                # if not l_uuid in ret:
                if l_uuid not in ret:
                    ret[l_uuid] = False
        else:
            q = (
                session.query(Target)
                .filter(and_(self.target.c.uuid == uuid, filt))
                .first()
            )
            ret = q is not None

        if session_need_to_close:
            session.close()
        return ret

    def __createTarget(self, session, uuid, name, _type, entity_id, menu_id, params):
        target = Target()
        target.uuid = uuid
        target.name = name
        target.type = _type
        if "choose_network" in params:
            target.nic_uuid = params["choose_network"]
        if "choose_network_profile" in params:
            # Get nic_uuid only for computers
            # type 2 => profile type
            if target.type != 2:
                target.nic_uuid = params["choose_network_profile"][uuid]
        if "nic_uuid" in params:
            target.nic_uuid = params["nic_uuid"]
        if "target_opt_kernel" in params:
            target.kernel_parameters = params["target_opt_kernel"]
        else:
            target.kernel_parameters = self.config.web_def_kernel_parameters
        if "target_opt_image" in params:
            target.image_parameters = params["target_opt_image"]
        else:
            target.image_parameters = self.config.web_def_image_parameters
        target.exclude_parameters = ""  # Always empty when creating a target
        if "target_opt_raw_mode" in params and params["target_opt_raw_mode"]:
            target.raw_mode = 1
        target.fk_entity = entity_id
        target.fk_menu = menu_id
        session.add(target)
        return target

    def getTargetNICuuid(self, uuid, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()

        filt = None
        if isinstance(uuid, list):
            filt = self.target.c.uuid.in_(uuid)
        else:
            filt = self.target.c.uuid == uuid
        ret = session.query(Target).filter(filt).all()

        if session_need_to_close:
            session.close()
        return [x.nic_uuid for x in ret]

    # SYNCHRO
    def getTargetsThatNeedSynchroInEntity(self, loc_id, target_type, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()

        if target_type == P2IT.ALL_COMPUTERS:
            filter_type = self.target.c.type.in_(
                [P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE]
            )
        else:
            filter_type = and_(self.target.c.type == target_type)

        q = session.query(Target).add_entity(SynchroState)
        q = q.select_from(
            self.target.join(self.menu).join(
                self.entity, self.target.c.fk_entity == self.entity.c.id
            )
        )
        q = (
            q.filter(
                and_(
                    self.entity.c.uuid == loc_id,
                    self.menu.c.fk_synchrostate.in_([P2ISS.TODO, P2ISS.INIT_ERROR]),
                    filter_type,
                )
            )
            .group_by(self.target.c.id)
            .all()
        )

        if session_need_to_close:
            session.close()
        return q

    def getComputersThatNeedSynchroInEntity(self, loc_id, session=None):
        return self.getTargetsThatNeedSynchroInEntity(loc_id, P2IT.COMPUTER, session)

    def getProfilesThatNeedSynchroInEntity(self, loc_id, session=None):
        return self.getTargetsThatNeedSynchroInEntity(loc_id, P2IT.PROFILE, session)

    def getComputersInProfileThatNeedSynchroInEntity(self, loc_id, session=None):
        return self.getTargetsThatNeedSynchroInEntity(
            loc_id, P2IT.COMPUTER_IN_PROFILE, session
        )

    def getComputersSynchroStates(self, uuids, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()

        q = session.query(Target).add_entity(SynchroState)
        q = q.select_from(self.target.join(self.menu).join(self.synchro_state))
        q = q.filter(self.target.c.uuid.in_(uuids)).all()

        if session_need_to_close:
            session.close()
        return q

    def getTargetsByCustomMenuInEntity(self, loc_id, custom_menu, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()

        q = session.query(Target.uuid)
        q = q.select_from(
            self.target.join(self.menu).join(
                self.entity, self.target.c.fk_entity == self.entity.c.id
            )
        )
        q = (
            q.filter(
                and_(
                    self.entity.c.uuid == loc_id,
                    self.menu.c.custom_menu == custom_menu,
                    self.target.c.type == P2IT.COMPUTER,
                )
            )
            .group_by(self.target.c.id)
            .all()
        )

        if session_need_to_close:
            session.close()
        return [z[0] for z in q]

    def getCustomMenuCount(self, location):
        session = create_session()
        ret = (
            session.query(func.count(Menu.id))
            .select_from(
                self.menu.join(
                    self.target, self.target.c.fk_menu == self.menu.c.id
                ).join(self.entity, self.target.c.fk_entity == self.entity.c.id)
            )
            .filter(and_(Menu.custom_menu == 1, self.entity.c.uuid == location))
        )
        return ret.scalar()

    def getCustomMenuCountdashboard(self, location):
        session = create_session()
        ret = session.query(func.count(distinct(self.target.c.uuid))).filter(
            and_(
                self.target.c.fk_entity == fromUUID(location),
                self.target.c.is_registered_in_package_server == 1,
                self.target.c.type.in_([1, 3]),
            )
        )
        return ret.scalar()

    def getCustomMenubylocation(self, location):
        session = create_session()
        ret = (
            session.query(
                self.target.c.uuid, self.target.c.name, self.target.c.nic_uuid
            )
            .select_from(
                self.target.join(
                    self.menu, self.menu.c.id == self.target.c.fk_menu
                ).join(self.entity, self.target.c.fk_entity == self.entity.c.id)
            )
            .filter(and_(Menu.custom_menu == 1, self.entity.c.uuid == location))
        )

        q = ret.distinct().all()
        q1 = []
        for z in q:
            a = []
            a.append(z.uuid)
            a.append(z.name)
            if z.nic_uuid is None:
                a.append("")
            else:
                a.append(z.nic_uuid)
            q1.append(a)
        # q1 =  [[z.uuid, z.name,z.nic_uuid] for z in q]
        return q1

    def getMenubylocation(self, location):
        session = create_session()
        ret = (
            session.query(self.target.c.uuid)
            .select_from(
                self.target.join(
                    self.menu, self.menu.c.id == self.target.c.fk_menu
                ).join(self.entity, self.target.c.fk_entity == self.entity.c.id)
            )
            .filter(
                and_(
                    not_(self.target.c.uuid.contains("DELETED")),
                    self.entity.c.uuid == location,
                )
            )
            .distinct()
            .all()
        )

        result = []
        for element in ret:
            result.append(element.uuid)
        session.close()
        return result

    def __getSynchroStates(self, uuids, target_type, session):
        q = session.query(SynchroState).add_entity(Menu)
        q = q.select_from(
            self.synchro_state.join(self.menu).join(
                self.target, self.menu.c.id == self.target.c.fk_menu
            )
        )
        if target_type == P2IT.ALL_COMPUTERS:
            q = q.filter(
                and_(
                    self.target.c.uuid.in_(uuids),
                    self.target.c.type.in_((P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE)),
                )
            ).all()
        else:
            q = q.filter(
                and_(self.target.c.uuid.in_(uuids), self.target.c.type == target_type)
            ).all()
        return q

    def getTargetsSynchroState(self, uuids, target_type):
        session = create_session()
        q = self.__getSynchroStates(uuids, target_type, session)
        session.close()
        if q:
            return [x[0] for x in q]
        return None

    def getTargetsCustomMenuFlag(self, uuids, target_type):
        session = create_session()
        q = self.__getSynchroStates(uuids, target_type, session)
        session.close()
        if q:
            try:
                return q[0][1].custom_menu
            except BaseException:
                return None
        return None

    def setComputerCustomMenuFlag(self, uuids, value):
        session = create_session()
        q = self.__getSynchroStates(uuids, P2IT.ALL_COMPUTERS, session)
        if q:
            q[0][1].custom_menu = value
        session.flush()
        session.close()
        return True

    def getLocationSynchroState(self, uuid):
        """
        Attempt to see if a location uuid needs to be synced, or not

        @param uuid the Entity uuid
        """

        session = create_session()

        # check if the entity menu as to be synced, by looking at its imaging
        # server menu status
        j = (
            self.synchro_state.join(self.menu)
            .join(self.imaging_server)
            .join(self.entity)
        )
        f = and_(self.entity.c.uuid == uuid, self.imaging_server.c.associated == 1)
        q2 = session.query(SynchroState)
        q2 = q2.select_from(j)
        q2 = q2.filter(f)
        q2 = q2.first()

        ret = []

        ret.append(
            {
                "id": q2.id,
                "label": q2.label,
                "item": "",
            }  # no item : this is the location menu
        )

        # same, this time by target (we check the state of the content of this
        # entity)
        q1 = session.query(SynchroState).add_entity(Target)
        j = self.synchro_state.join(self.menu).join(self.target).join(self.entity)
        f = and_(
            self.entity.c.uuid == uuid,
            self.target.c.type.in_(
                [P2IT.COMPUTER, P2IT.PROFILE, P2IT.COMPUTER_IN_PROFILE]
            ),
        )
        q1 = q1.select_from(j)
        q1 = q1.filter(f)
        q1 = q1.all()

        for q, target in q1:
            self.logger.debug(
                "getLocationSynchroState target %s is in state %s"
                % (target.uuid, q.label)
            )

            ret.append({"id": q.id, "label": q.label, "item": target.uuid})

        session.close()
        return ret

    def __sha512_crypt_password(self, password):
        if not password:
            return ""
        import crypt

        passphrase = "$6$DzmCpUs3$"
        return crypt.crypt(password, passphrase)

    def getPXELogin(self, location_uuid):
        session = create_session()
        login = (
            session.query(Entity.pxe_login)
            .filter(Entity.uuid == location_uuid)
            .scalar()
        )
        session.close()
        return login

    def getPXEPasswordHash(self, location_uuid):
        session = create_session()
        password = (
            session.query(Entity.pxe_password)
            .filter(Entity.uuid == location_uuid)
            .scalar()
        )
        session.close()
        return password

    def setLocationPXEParams(self, uuid, params):
        session = create_session()
        try:
            location = session.query(Entity).filter(Entity.uuid == uuid).one()
            if "pxe_login" in params:
                location.pxe_login = params["pxe_login"]
            if "pxe_password" in params:
                # location.pxe_password = self.__sha512_crypt_password(params['pxe_password'])
                location.pxe_password = params["pxe_password"]
            if "pxe_keymap" in params:
                location.pxe_keymap = params["pxe_keymap"]
            elif "language" in params:
                keymap = (
                    session.query(Language.keymap)
                    .filter(Language.id == int(params["language"].replace("UUID", "")))
                    .scalar()
                )
                location.pxe_keymap = keymap
            session.flush()
            session.close()
            return True
        except Exception as e:
            logging.getLogger().error(str(e))
            session.close()
            return False

    def getClonezillaSaverParams(self, location_uuid):
        session = create_session()
        saver_params = (
            session.query(Entity.clonezilla_saver_params)
            .filter(Entity.uuid == location_uuid)
            .scalar()
        )
        session.close()
        return saver_params

    def getClonezillaRestorerParams(self, location_uuid):
        session = create_session()
        restorer_params = (
            session.query(Entity.clonezilla_restorer_params)
            .filter(Entity.uuid == location_uuid)
            .scalar()
        )
        session.close()
        return restorer_params

    def setLocationClonezillaParams(self, uuid, params):
        session = create_session()
        try:
            location = session.query(Entity).filter(Entity.uuid == uuid).one()
            if "clonezilla_saver_params" in params:
                location.clonezilla_saver_params = params["clonezilla_saver_params"]
            if "clonezilla_restorer_params" in params:
                location.clonezilla_restorer_params = params[
                    "clonezilla_restorer_params"
                ]
            session.flush()
            session.close()
            return True
        except Exception as e:
            logging.getLogger().error(str(e))
            session.close()
            return False

    def setLocationSynchroState(self, uuid, state):
        self.logger.debug(">>> setLocationSynchroState %s %s" % (uuid, str(state)))
        session = create_session()
        q2 = session.query(SynchroState).add_entity(Menu)
        q2 = q2.select_from(
            self.synchro_state.join(self.menu)
            .join(self.imaging_server)
            .join(self.entity)
        )
        q2 = q2.filter(
            and_(self.entity.c.uuid == uuid, self.imaging_server.c.associated == 1)
        ).first()

        if q2:
            synchro_state, menu = q2
            menu.fk_synchrostate = state
            session.add(menu)
        else:
            logging.getLogger().warn(
                "Imaging.setLocationSynchroState : failed to set synchro_state"
            )

        session.flush()
        session.close()
        return True

    def changeTargetsSynchroState(self, uuids, target_type, state):
        session = create_session()
        synchro_states = self.__getSynchroStates(uuids, target_type, session)
        for synchro_state, menu in synchro_states:
            menu.fk_synchrostate = state
            session.add(menu)
        session.flush()
        session.close()
        return True

    # MENUS
    def delProfileMenuTarget(self, uuids):
        session = create_session()
        targets = session.query(Target).add_entity(Menu)
        targets = targets.select_from(
            self.target.join(self.menu, self.target.c.fk_menu == self.menu.c.id)
        )
        targets = targets.filter(
            and_(
                self.target.c.uuid.in_(uuids),
                self.target.c.type == P2IT.COMPUTER_IN_PROFILE,
            )
        ).all()
        for t, m in targets:
            session.delete(t)
            session.delete(m)
        session.flush()
        session.close()
        return True

    def delProfileComputerMenuItem(self, uuids):
        session = create_session()

        mis = (
            session.query(MenuItem)
            .add_entity(BootServiceInMenu)
            .add_entity(ImageInMenu)
        )
        mis = mis.select_from(
            self.menu_item.join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id)
            .join(self.target, self.target.c.fk_menu == self.menu.c.id)
            .outerjoin(
                self.boot_service_in_menu,
                self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
            .outerjoin(
                self.image_in_menu,
                self.image_in_menu.c.fk_menuitem == self.menu_item.c.id,
            )
        )
        mis = mis.filter(
            and_(
                self.target.c.uuid.in_(uuids),
                self.target.c.type == P2IT.COMPUTER_IN_PROFILE,
            )
        ).all()

        for mi, bsim, iim in mis:
            if bsim is not None:
                session.delete(bsim)
            if iim is not None:
                session.delete(iim)
            session.delete(mi)

        session.flush()
        session.close()
        return True

    def switchMenusToDefault(self, uuids):
        """
        Menus of deleted computers from profile wil be switched
        to default entity menu.

        @param uuids: list of UUIDs of removed computers
        @type uuids: list
        """
        session = create_session()

        menus = []
        for uuid in uuids:
            location = ComputerLocationManager().getMachinesLocations([uuid])
            location_id = location[uuid]["uuid"]
            menu = self.getEntityDefaultMenu(location_id, session)
            mis = self.__getDefaultMenuItem(session, menu.id)
            target = self.getTargetsByUUID([uuid])
            target_name = ""
            if type(target) is list and len(target) > 0:
                target_name = target[0].name
            else:
                target_name = target.name
            params = menu.toH()
            params["target_name"] = target_name
            menus.append((uuid, params, mis))

        self.unregisterTargets(uuids)

        for uuid, params, items in menus:
            self.setMyMenuTarget(uuid, params, P2IT.COMPUTER)

        return True

    def __getAllProfileMenuItem(self, profile_UUID, session):
        return self.__getAllMenuItem(
            session,
            and_(
                self.target.c.uuid == profile_UUID, self.target.c.type == P2IT.PROFILE
            ),
        )

    def __getAllComputersMenuItem(self, computers_UUID, session):
        return self.__getAllMenuItem(
            session,
            and_(
                self.target.c.uuid.in_(computers_UUID),
                self.target.c.type.in_([P2IT.COMPUTER_IN_PROFILE, P2IT.COMPUTER]),
            ),
        )

    def __getAllMenuItem(self, session, filt):
        ret = (
            session.query(MenuItem)
            .add_entity(Target)
            .add_entity(BootServiceInMenu)
            .add_entity(ImageInMenu)
            .select_from(
                self.menu_item.join(
                    self.menu, self.menu_item.c.fk_menu == self.menu.c.id
                )
                .join(self.target, self.target.c.fk_menu == self.menu.c.id)
                .outerjoin(
                    self.boot_service_in_menu,
                    self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
                )
                .outerjoin(
                    self.image_in_menu,
                    self.image_in_menu.c.fk_menuitem == self.menu_item.c.id,
                )
            )
            .filter(filt)
            .all()
        )
        return ret

    def __copyMenuInto(self, menu_from, menu_into, session):
        for i in (
            "default_name",
            "timeout",
            "background_uri",
            "message",
            "ethercard",
            "bootcli",
            "disklesscli",
            "dont_check_disk_size",
            "hidden_menu",
            "debug",
            "update_nt_boot",
        ):
            try:
                setattr(menu_into, i, getattr(menu_from, i))
            except:
                continue
        session.add(menu_into)

    def __copyMenuItemInto(self, mi_from, mi_into, session):
        for i in ("order", "hidden", "hidden_WOL"):
            setattr(mi_into, i, getattr(mi_from, i))
        session.add(mi_into)

    def delComputersFromProfile(self, profile_UUID, computers):
        # we put the profile's mi before the computer's mi
        session = create_session()
        computers_UUID = [c["uuid"] for c in list(computers.values())]
        # copy the profile part of the menu in their own menu
        pmenu = self.getTargetMenu(profile_UUID, P2IT.PROFILE, session)
        pmis = self.__getAllProfileMenuItem(profile_UUID, session)

        pnb_element = len(pmis)
        mis = self.__getAllComputersMenuItem(computers_UUID, session)

        h_tid2target = {}
        for target, tuuid in (
            session.query(Target)
            .add_column(self.target.c.uuid)
            .filter(self.target.c.uuid.in_(computers_UUID))
            .all()
        ):
            try:
                h_tid2target[tuuid] = target
            except:
                pass

        for mi, target, bsim, iim in mis:
            mi.order += pnb_element
            session.add(mi)

        session.flush()

        a_bsim = []
        a_iim = []
        a_target2default_item = []
        a_target2default_item_WOL = []
        for tuuid in computers_UUID:
            if tuuid not in h_tid2target:
                continue
            target = h_tid2target[tuuid]

            # put the parameter of the profile's menu in the computer menu
            menu = self.getTargetMenu(tuuid, P2IT.COMPUTER_IN_PROFILE, session)
            self.__copyMenuInto(pmenu, menu, session)

            # change the computer type, it's no longer a computer_in_profile
            target.type = P2IT.COMPUTER
            session.add(target)

            for mi, target, bsim, iim in pmis:
                # duplicate menu_item
                new_mi = MenuItem()
                new_mi.fk_menu = menu.id
                self.__copyMenuItemInto(mi, new_mi, session)

                # create a bsim if it's a bsim
                if bsim is not None:
                    a_bsim.append([new_mi, bsim])

                # create a iim if it's a iim
                if iim is not None:
                    a_iim.append([new_mi, iim])

                if mi.id == pmenu.fk_default_item:
                    a_target2default_item.append([menu, new_mi])

                if mi.id == pmenu.fk_default_item_WOL:
                    a_target2default_item_WOL.append([menu, new_mi])

        session.flush()

        for menu, mi in a_target2default_item:
            menu.fk_default_item = mi.id
            session.add(menu)

        for menu, mi in a_target2default_item_WOL:
            menu.fk_default_item_WOL = mi.id
            session.add(menu)

        for mi, bsim in a_bsim:
            new_bsim = BootServiceInMenu()
            new_bsim.fk_menuitem = mi.id
            new_bsim.fk_bootservice = bsim.fk_bootservice
            session.add(new_bsim)

        for mi, iim in a_iim:
            new_iim = ImageInMenu()
            new_iim.fk_menuitem = mi.id
            new_iim.fk_image = iim.fk_image
            session.add(new_iim)

        session.flush()
        session.close()

        return True

    def delProfile(self, profile_UUID):
        session = create_session()
        # remove all the possible menuitem that only depend on this profile
        pmis = self.__getAllProfileMenuItem(profile_UUID, session)
        profile, menu = (
            session.query(Target)
            .add_entity(Menu)
            .select_from(
                self.target.join(self.menu, self.target.c.fk_menu == self.menu.c.id)
            )
            .filter(
                and_(
                    self.target.c.uuid == profile_UUID,
                    self.target.c.type == P2IT.PROFILE,
                )
            )
            .one()
        )

        menu.fk_default_item = None
        menu.fk_default_item_WOL = None
        session.add(menu)
        session.flush()
        mi_list = []
        for mi, target, bsim, iim in pmis:
            mi_list.append(mi.id)
            if bsim != None:
                session.delete(bsim)
            if iim is not None:
                session.delete(iim)
        session.flush()

        menus_refs = (
            session.query(Menu)
            .filter(
                or_(Menu.fk_default_item.in_(mi_list)),
                Menu.fk_default_item_WOL.in_(mi_list),
            )
            .all()
        )
        menus_ids = []
        for menu in menus_refs:
            menus_ids.append(menu.id)
            menu.fk_default_item = None
            menu.fk_default_item_WOL = None
        session.flush()

        for mi, target, bsim, iim in pmis:
            session.delete(mi)
        session.flush()

        session.delete(profile)
        session.flush()

        session.delete(menu)
        session.query(Target).filter(Target.fk_menu == menu.id).delete()
        session.flush()
        session.close()
        return True

    def setProfileMenuTarget(self, uuids, profile_uuid, params):
        session = create_session()
        menu = self.getTargetMenu(profile_uuid, P2IT.PROFILE, session)
        cache_location_id = {}
        locations = ComputerLocationManager().getMachinesLocations(uuids)

        hostnames = {}
        if "hostnames" in params:
            params["hostnames"]

        registered = self.isTargetRegister(uuids, P2IT.COMPUTER_IN_PROFILE, session)
        for uuid in uuids:
            # if not (uuid in registered and registered[uuid]):
            if not (uuid in registered and registered[uuid]):
                loc_id = 0
                location_id = locations[uuid]["uuid"]
                # if not location_id in cache_location_id:
                if location_id not in cache_location_id:
                    loc = (
                        session.query(Entity)
                        .filter(self.entity.c.uuid == location_id)
                        .first()
                    )
                    cache_location_id[location_id] = loc.id
                loc_id = cache_location_id[location_id]
                target_name = ""
                if uuid in hostnames:
                    target_name = hostnames[uuid]
                target = self.__createTarget(
                    session,
                    uuid,
                    target_name,
                    P2IT.COMPUTER_IN_PROFILE,
                    loc_id,
                    menu.id,
                    params,
                )
            else:
                target = self.getTargetsByUUID([uuid], session)
                target = target[0]
                target.kernel_parameters = params["target_opt_kernel"]
                target.image_parameters = params["target_opt_image"]
                session.add(target)
        session.flush()
        session.close()
        return [True]

    def putComputersInProfile(self, profile_UUID, computers):
        session = create_session()
        menu = self.getTargetMenu(profile_UUID, P2IT.PROFILE, session)
        imaging_server = ComputerProfileManager().getProfileImagingServerUUID(
            profile_UUID
        )
        entity = self.getImagingServerEntity(imaging_server)
        location_id = entity.uuid
        loc = session.query(Entity).filter(self.entity.c.uuid == location_id).first()

        for computer in list(computers.values()):
            m = self.__duplicateMenu(session, menu, location_id, profile_UUID, True)
            self.__createTarget(
                session,
                computer["uuid"],
                computer["hostname"],
                P2IT.COMPUTER_IN_PROFILE,
                loc.id,
                m.id,
                {},
            )

        session.flush()
        session.close()

        return True

    def setMyMenuTarget(self, uuid, params, _type):
        session = create_session()
        menu = self.getTargetMenu(uuid, _type, session)
        location_id = None
        p_id = None

        if not menu:
            if _type == P2IT.COMPUTER:
                profile = ComputerProfileManager().getComputersProfile(uuid)
                default_menu = None
                if profile:
                    default_menu = self.getTargetMenu(profile.id, P2IT.PROFILE, session)
                if default_menu is None or not profile:
                    location = ComputerLocationManager().getMachinesLocations([uuid])
                    location_id = location[uuid]["uuid"]
                    default_menu = self.getEntityDefaultMenu(location_id, session)
                else:
                    p_id = profile.id
                    location_id = None
            elif _type == P2IT.PROFILE:
                imaging_server = ComputerProfileManager().getProfileImagingServerUUID(
                    uuid
                )
                if not imaging_server:
                    raise "%s:Can't get this profile's imaging_server%s" % (
                        P2ERR.ERR_DEFAULT,
                        uuid,
                    )
                entity = self.getImagingServerEntity(imaging_server)
                if entity is None:
                    raise "%s:Can't get the entity associated to this imaging server %s" % (
                        P2ERR.ERR_DEFAULT,
                        imaging_server.id,
                    )
                location_id = entity.uuid
                default_menu = self.getEntityDefaultMenu(location_id, session)
            else:
                raise "%s:Don't know that type of target : %s" % (
                    P2ERR.ERR_DEFAULT,
                    _type,
                )
            menu = self.__duplicateMenu(session, default_menu, location_id, p_id)
            menu = self.__modifyMenu(id2uuid(menu.id), params, session)
            session.flush()
        else:
            menu = self.__modifyMenu(id2uuid(menu.id), params, session)

        target = None
        if not self.isTargetRegister(uuid, _type, session):
            if location_id is None:
                location = ComputerLocationManager().getMachinesLocations([uuid])
                location_id = location[uuid]["uuid"]
            loc = self.getLinkedEntityByEntityUUID(location_id)
            target = self.__createTarget(
                session, uuid, params["target_name"], _type, loc.id, menu.id, params
            )
            # TODO : what do we do with target ?
            if _type == P2IT.PROFILE:
                # need to create the targets for all the computers inside the profile
                # and then create them an "empty" menu
                # (ie : a menu with only the default_item* part)

                for computer in ComputerProfileManager().getProfileContent(uuid):
                    m = self.__duplicateMenu(session, menu, location_id, uuid, True)
                    self.__createTarget(
                        session,
                        computer.uuid,
                        computer.name,
                        P2IT.COMPUTER_IN_PROFILE,
                        loc.id,
                        m.id,
                        params,
                    )

                session.flush()
        else:
            target = self.getTargetsByUUID([uuid], session)
            target = target[0]
            target.kernel_parameters = params["target_opt_kernel"]
            target.image_parameters = params["target_opt_image"]
            target.exclude_parameters = self._getExcludeString(
                target, params["target_opt_parts"]
            )
            if "target_opt_raw_mode" in params and params["target_opt_raw_mode"]:
                target.raw_mode = 1
            else:
                target.raw_mode = 0
            session.add(target)

        session.flush()
        session.close()
        return [True, target]

    def getProfileLocation(self, uuid):
        """get Location of given Profile"""
        session = create_session()
        q = session.query(Entity)
        q = q.join(Target).filter(Target.uuid == uuid)
        q = q.first()
        session.close()
        if q is None:
            return None
        return q.uuid

    def getMyMenuTarget(self, uuid, type):
        session = create_session()
        muuid = False
        orig_target = None
        if type == P2IT.COMPUTER:
            # if registered, get the computer menu and finish
            if self.isTargetRegister(uuid, type, session):
                target = self.getTargetsByUUID([uuid])
                whose = [uuid, type, target[0].toH()]
                menu = self.getTargetMenu(uuid, type, session)
                session.close()
                return [whose, menu]
            # else get the profile id
            else:
                profile = ComputerProfileManager().getComputersProfile(uuid)
                muuid = uuid
                if profile:
                    orig_target = self.getTargetsByUUID([uuid])
                    uuid = profile.id  # WARNING we must pass in UUIDs!

        # if profile is registered, get the profile menu and finish
        if uuid and self.isTargetRegister(uuid, P2IT.PROFILE, session):
            target = self.getTargetsByUUID([uuid])
            whose = [uuid, P2IT.PROFILE, target[0].toH()]
            if orig_target is not None:
                whose.append(orig_target[0].toH())
            menu = self.getTargetMenu(uuid, P2IT.PROFILE, session)
        # else get the entity menu
        else:
            whose = False
            if muuid:
                location = ComputerLocationManager().getMachinesLocations([muuid])
                loc_id = location[muuid]["uuid"]
            else:
                imaging_server = ComputerProfileManager().getProfileImagingServerUUID(
                    uuid
                )
                entity = self.getImagingServerEntity(imaging_server)
                loc_id = entity.uuid

            menu = self.getEntityDefaultMenu(loc_id, session)
        if menu is None:
            menu = False

        session.close()
        return [whose, menu]

    # POST INSTALL SCRIPT
    def isLocalPostInstallScripts(self, pis_uuid, session=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()

        q = session.query(PostInstallScript).add_entity(
            PostInstallScriptOnImagingServer
        )
        q = q.select_from(
            self.post_install_script.outerjoin(
                self.post_install_script_on_imaging_server,
                self.post_install_script_on_imaging_server.c.fk_post_install_script
                == self.post_install_script.c.id,
            )
            .outerjoin(
                self.imaging_server,
                self.post_install_script_on_imaging_server.c.fk_imaging_server
                == self.imaging_server.c.id,
            )
            .outerjoin(self.entity)
        )
        q = q.filter(
            or_(
                self.post_install_script_on_imaging_server.c.fk_post_install_script
                == None,
                self.entity.c.uuid == pis_uuid,
            )
        )
        q = q.filter(self.post_install_script.c.id == uuid2id(pis_uuid))
        q = q.first()

        ret = q[1] is not None

        if session_need_to_close:
            session.close()
        return ret

    def __AllPostInstallScripts(self, session, location, filter, is_count=False):
        # PostInstallScripts are not specific to an Entity
        lang = self.__getLocLanguage(session, location)
        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q = session.query(PostInstallScript)
        if not is_count:
            q = (
                q.add_entity(PostInstallScriptOnImagingServer)
                .add_entity(Internationalization, alias=I18n1)
                .add_entity(Internationalization, alias=I18n2)
            )
            q = q.select_from(
                self.post_install_script.outerjoin(
                    self.post_install_script_on_imaging_server,
                    self.post_install_script_on_imaging_server.c.fk_post_install_script
                    == self.post_install_script.c.id,
                )
                .outerjoin(
                    self.imaging_server,
                    self.post_install_script_on_imaging_server.c.fk_imaging_server
                    == self.imaging_server.c.id,
                )
                .outerjoin(
                    I18n1,
                    and_(
                        self.post_install_script.c.fk_name == I18n1.c.id,
                        I18n1.c.fk_language == lang,
                    ),
                )
                .outerjoin(
                    I18n2,
                    and_(
                        self.post_install_script.c.fk_desc == I18n2.c.id,
                        I18n2.c.fk_language == lang,
                    ),
                )
                .outerjoin(self.entity)
            )
            q = q.filter(
                or_(
                    self.post_install_script_on_imaging_server.c.fk_post_install_script
                    == None,
                    self.entity.c.uuid == location,
                )
            )
        q = q.filter(
            or_(
                self.post_install_script.c.default_name.like("%" + filter + "%"),
                self.post_install_script.c.default_desc.like("%" + filter + "%"),
            )
        )
        return q

    def __mergePostInstallScriptOnImagingServerInPostInstallScript(
        self, postinstallscript_list
    ):
        ret = []
        for (
            postinstallscript,
            postinstallscript_on_imagingserver,
            name_i18n,
            desc_i18n,
        ) in postinstallscript_list:
            if name_i18n is not None and name_i18n.label != "NOTTRANSLATED":
                #    setattr(postinstallscript, 'name', name_i18n.label)
                setattr(postinstallscript, "default_name", name_i18n.label)
            if desc_i18n is not None and desc_i18n.label != "NOTTRANSLATED":
                #    setattr(postinstallscript, 'desc', desc_i18n.label)
                setattr(postinstallscript, "default_desc", desc_i18n.label)
            setattr(
                postinstallscript,
                "is_local",
                (postinstallscript_on_imagingserver is not None),
            )
            ret.append(postinstallscript)
        return ret

    def getAllTargetPostInstallScript(self, target_uuid, start, end, filter):
        session = create_session()
        loc = (
            session.query(Entity)
            .select_from(self.entity.join(self.target))
            .filter(self.target.c.uuid == target_uuid)
            .first()
        )
        session.close()
        location = id2uuid(loc.id)
        return self.getAllPostInstallScripts(location, start, end, filter)

    def countAllTargetPostInstallScript(self, target_uuid, filter):
        session = create_session()
        loc = (
            session.query(Entity)
            .select_from(self.entity.join(self.target))
            .filter(self.target.c.uuid == target_uuid)
            .first()
        )
        session.close()
        location = id2uuid(loc.id)
        return self.countAllPostInstallScripts(location, filter)

    def getAllPostInstallScripts(self, location, start, end, filter):
        session = create_session()
        q = self.__AllPostInstallScripts(session, location, filter)
        if end != -1:
            q = q.offset(int(start)).limit(int(end) - int(start))
        else:
            q = q.all()
        session.close()
        q = self.__mergePostInstallScriptOnImagingServerInPostInstallScript(q)
        return q

    def countAllPostInstallScripts(self, location, filter):
        session = create_session()
        q = self.__AllPostInstallScripts(session, location, filter, True)
        q = q.count()
        session.close()
        return q

    def getComputersWithThisPostInstallScript(self, pis_uuid):
        """
        For each master who have this postinstall script, get one computer UUID
        Used to update Postinstall script

        @param pis_uuid: Postinstall script UUID
        @type pis_uuid: str

        @return: list of Computer UUID
        @rtype: list
        """
        session = create_session()
        query = session.query(PostInstallScriptInImage).filter(
            PostInstallScriptInImage.fk_post_install_script == fromUUID(pis_uuid)
        )
        session.close()

        ret = []
        for pis in query:
            master_uuid = toUUID(pis.fk_image)
            used = self.areImagesUsed([[master_uuid, "", ""]])
            if len(used[master_uuid]) > 0:
                if (
                    used[master_uuid][0][1] != -1
                ):  # Master is attached to default boot menu
                    ret.append(used[master_uuid][0][0])
        return ret

    def getPostInstallScript(self, pis_uuid, session=None, location_id=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        lang = 1
        if location_id is not None:
            lang = self.__getLocLanguage(session, location_id)
        else:
            pass
            # this is used internally to delete or edit a PIS
            # which mean that the day we manage to edit i18n labels, we have to
            # work here
        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q = (
            session.query(PostInstallScript)
            .add_entity(PostInstallScriptOnImagingServer)
            .add_entity(Internationalization, alias=I18n1)
            .add_entity(Internationalization, alias=I18n2)
        )
        q = q.select_from(
            self.post_install_script.outerjoin(
                self.post_install_script_on_imaging_server
            )
            .outerjoin(
                I18n1,
                and_(
                    self.post_install_script.c.fk_name == I18n1.c.id,
                    I18n1.c.fk_language == lang,
                ),
            )
            .outerjoin(
                I18n2,
                and_(
                    self.post_install_script.c.fk_desc == I18n2.c.id,
                    I18n2.c.fk_language == lang,
                ),
            )
        )
        q = q.filter(self.post_install_script.c.id == uuid2id(pis_uuid)).first()
        q = self.__mergePostInstallScriptOnImagingServerInPostInstallScript([q])

        if session_need_to_close:
            session.close()
        return q[0]

    def delPostInstallScript(self, pis_uuid):
        session = create_session()
        # delete the post install script
        pis = self.getPostInstallScript(pis_uuid, session)
        if not pis.is_local:
            return False
        # have to remove the post install script on imaging server if it exists
        pisois = (
            session.query(PostInstallScriptOnImagingServer)
            .filter(
                self.post_install_script_on_imaging_server.c.fk_post_install_script
                == uuid2id(pis_uuid)
            )
            .first()
        )
        if pisois is None:
            # we have a local pis and no pisois !
            return False
        session.delete(pisois)
        session.flush()
        session.delete(pis)
        session.flush()
        session.close
        return True

    def getImagesPostInstallScript(self, ims, session=None, location_id=None):
        session_need_to_close = False
        if session is None:
            session_need_to_close = True
            session = create_session()
        lang = 1
        if location_id is not None:
            lang = self.__getLocLanguage(session, location_id)

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q = (
            session.query(PostInstallScript)
            .add_entity(Image)
            .add_entity(Internationalization, alias=I18n1)
            .add_entity(Internationalization, alias=I18n2)
            .add_column(self.post_install_script_in_image.c.order)
        )
        q = q.select_from(
            self.post_install_script.join(self.post_install_script_in_image)
            .join(self.image)
            .outerjoin(
                I18n1,
                and_(
                    self.post_install_script.c.fk_name == I18n1.c.id,
                    I18n1.c.fk_language == lang,
                ),
            )
            .outerjoin(
                I18n2,
                and_(
                    self.post_install_script.c.fk_desc == I18n2.c.id,
                    I18n2.c.fk_language == lang,
                ),
            )
        )
        q = q.filter(self.image.c.id.in_(ims))
        q = q.order_by(self.image.c.id, self.post_install_script_in_image.c.order)
        q = q.all()

        if session_need_to_close:
            session.close()
        return q

    def editPostInstallScript(self, pis_uuid, params):
        session = create_session()
        pis = self.getPostInstallScript(pis_uuid, session)
        need_to_be_save = False
        if pis.default_name != params["default_name"]:
            need_to_be_save = True
            pis.default_name = params["default_name"]
            pis.fk_name = 1
        if pis.default_desc != params["default_desc"]:
            need_to_be_save = True
            pis.default_desc = params["default_desc"]
            pis.fk_desc = 1
        if pis.value != params["value"]:
            need_to_be_save = True
            pis.value = params["value"]

        if need_to_be_save:
            session.add(pis)
            session.flush()
        session.close()
        return True

    def addPostInstallScript(self, loc_id, params):
        session = create_session()
        pis = PostInstallScript()
        pis.default_name = params["default_name"]
        pis.fk_name = 1
        pis.default_desc = params["default_desc"]
        pis.fk_desc = 1
        pis.value = params["value"]
        session.add(pis)
        session.flush()
        # link it to the location because it's a local script
        imaging_server = self.getImagingServerByEntityUUID(loc_id, session)
        pisois = PostInstallScriptOnImagingServer()
        pisois.fk_post_install_script = pis.id
        pisois.fk_imaging_server = imaging_server.id
        session.add(pisois)
        session.flush()
        session.close()
        return True

    def getLocationImagingServerByServerUUID(self, imaging_server_uuid):
        session = create_session()
        ims, entity = (
            session.query(ImagingServer, Entity)
            .join(Entity, Entity.id == ImagingServer.fk_entity)
            .filter(self.imaging_server.c.packageserver_uuid == imaging_server_uuid)
            .first()
        )
        LocationServer = entity.uuid
        LocationId = entity.id
        session.close()
        return LocationId, LocationServer

    # Computer basic inventory stuff
    def injectInventory(self, imaging_server_uuid, computer_uuid, inventory):
        """
        Inject a computer inventory into the dabatase.
        For now only the ComputerDisk and ComputerPartition tables are used.
        """

        if not isUUID(imaging_server_uuid):
            raise TypeError("Bad imaging server UUID: %s" % imaging_server_uuid)
        if not isUUID(computer_uuid):
            raise TypeError("Bad computer UUID: %s" % computer_uuid)
        session = create_session()
        session.begin()

        locationId, locationServerImaging = self.getLocationImagingServerByServerUUID(imaging_server_uuid)
        target = None
        session.query(Target).filter_by(uuid=computer_uuid).update(
            {"uuid": "DELETED UUID%s" % computer_uuid}
        )
        if not locationServerImaging.startswith("UUID"):
            locationServerImaging = "UUID%s" % locationServerImaging
        menu = self.getEntityDefaultMenu(locationServerImaging)
        new_menu = self.__duplicateMenu(
            session, menu, locationServerImaging, None, False
        )
        target = Target()
        target.fk_menu = new_menu.id
        target.is_registered_in_package_server = 1
        new_menu.fk_synchrostate = 1
        target.name = inventory["shortname"]
        target.uuid = computer_uuid
        target.type = 1
        target.fk_entity = locationId

        try:
            # Then push a new inventory
            if "disk" in inventory:
                for disknum in inventory["disk"]:
                    disk_info = inventory["disk"][disknum]
                    cd = ComputerDisk()
                    cd.num = int(disknum)
                    cd.cyl = int(disk_info["C"])
                    cd.head = int(disk_info["H"])
                    cd.sector = int(disk_info["S"])
                    cd.capacity = int(disk_info["size"])
                    for partnum in disk_info["parts"]:
                        part = disk_info["parts"][partnum]
                        cp = ComputerPartition()
                        cp.num = int(partnum)
                        cp.type = part["type"]
                        cp.length = int(part["length"])
                        cp.start = int(part["start"])
                        cd.partitions.append(cp)
                        target.disks.append(cd)

            self.logger.debug(
                "Attribution location %s for computer  %s"
                % (target.fk_entity, target.name)
            )
            session.add(target)
            session.commit()
        # except InvalidRequestError as e:
        except Exception as e:
            session.rollback()
            self.logger.warn(
                "Can't get the computer %s, we can't inject an inventory. This happen when the computer exists in the backend but is not declared in the imaging."
                % (computer_uuid)
            )
            return [
                False,
                "Can't get the computer %s, we can't inject an inventory. This happen when the computer exists in the backend but is not declared in the imaging."
                % (computer_uuid),
            ]
        session.close()
        return [True, True]

    def getPartitionsToBackupRestore(self, computer_uuid):
        """
        @return: the computer disks and parts inventory, and flags them as
        excluded according to Target.exclude_parameters value
        @rtype: dict
        """
        if not isUUID(computer_uuid):
            raise TypeError("Bad computer UUID: %s" % computer_uuid)
        session = create_session()
        try:
            target = session.query(Target).filter_by(uuid=computer_uuid).one()
        except InvalidRequestError:
            return []
        excluded = target.exclude_parameters
        if not excluded:
            excluded = ""
        excluded = excluded.split()
        ret = {}
        for disk in target.disks:
            disknum = str(disk.num)
            ret[disknum] = {}
            if disknum + ":0" in excluded:
                ret[disknum]["exclude"] = True
            for partition in disk.partitions:
                partnum = str(partition.num)
                ret[disknum][partnum] = partition.toH()
                if disknum + ":" + str(partition.num + 1) in excluded:
                    ret[disknum][partnum]["exclude"] = True
        session.close()
        return ret

    def _getExcludeString(self, target, enabled):
        """
        @param enabled: list of [disk, part] couples to enable
        @type enabled: list

        @returns: string to set in the Target.exclude_parameters
        @rtype: str
        """
        excluded = []
        for disk in target.disks:
            disknum = disk.num + 1
            if [disknum, 0] in enabled:
                # This disk is enabled
                for partition in disk.partitions:
                    partnum = partition.num + 1
                    if not [disknum, partnum] in enabled:
                        excluded.append(str(disknum - 1) + ":" + str(partnum))
            else:
                # Disk completely disabled
                excluded.append(str(disknum - 1) + ":0")
        return " ".join(excluded)

    def getForbiddenComputersUUID(self, profile_UUID=None):
        """
        @returns: return all the computers that already have an imaging menu
        @rtype: list
        """
        session = create_session()
        targets = session.query(Target).select_from(
            self.target.join(self.menu, self.target.c.fk_menu == self.menu.c.id)
        )
        if profile_UUID is None:
            targets = targets.filter(self.target.c.type == P2IT.COMPUTER).all()
        else:
            computers = ComputerProfileManager().getProfileContent(profile_UUID)
            if computers:
                computers = [c.uuid for c in computers]
                targets = targets.filter(
                    and_(
                        self.target.c.type == P2IT.COMPUTER,
                        not self.target.c.uuid.in_(computers),
                    )
                )
            else:
                targets = targets.filter(self.target.c.type == P2IT.COMPUTER).all()
        session.close()
        ret = [t.uuid for t in targets]
        return ret

    def areForbiddebComputers(self, computers_UUID):
        """
        @returns: return all the computers from the computer_UUID list that already have an imaging menu
        @rtype: list
        """
        session = create_session()
        targets = (
            session.query(Target)
            .select_from(
                self.target.join(self.menu, self.target.c.fk_menu == self.menu.c.id)
            )
            .filter(
                and_(
                    self.target.c.uuid.in_(computers_UUID),
                    self.target.c.type == P2IT.COMPUTER,
                )
            )
            .all()
        )
        session.close()
        ret = [t.uuid for t in targets]
        return ret

    def getImageIDFromImageUUID(self, image_uuid):
        session = create_session()
        img = session.query(Image).filter(self.image.c.uuid == image_uuid).first()
        session.close()
        if img:
            return img.id
        return None

    def getImageUUIDFromImageUUID(self, image_uuid):
        return id2uuid(self.getImageIDFromImageUUID(image_uuid))

    def add_multicast(self, parameters):
        session = create_session()

        multicast = Multicast()
        multicast.location = parameters["location"]
        multicast.target_uuid = parameters["target_uuid"]
        multicast.image_uuid = parameters["uuidmaster"]
        multicast.image_name = parameters["itemlabel"]

        session.add(multicast)
        session.flush()
        session.close()

    def remove_multicast(self, parameters):

        session = create_session()

        session.query(Multicast).filter(
            and_(
                Multicast.image_uuid == parameters["uuidmaster"],
                Multicast.target_uuid == parameters["target_uuid"],
            )
        ).delete()

        session.flush()
        session.close()

    def set_diskless_infos(self, location, config):
        session = create_session()
        entity = session.query(Entity).filter(Entity.uuid == location).one()

        if entity is not None:
            ims = (
                session.query(ImagingServer)
                .filter(ImagingServer.fk_entity == entity.id)
                .update(
                    {
                        "diskless_dir": config["diskless_dir"],
                        "diskless_kernel": config["diskless_kernel"],
                        "inventories_dir": config["inventories_dir"],
                        "pxe_time_reboot": config["pxe_time_reboot"],
                        "diskless_initrd": config["diskless_initrd"],
                        "tools_dir": config["tools_dir"],
                        "davos_opts": config["davos_opts"],
                        "template_name": config["template_name"],
                        "increment": config["increment"],
                        "digit": config["digit"],
                    }
                )
            )

        session.flush()
        session.close()


def id2uuid(id):
    return "UUID%d" % id


def uuid2id(uuid):
    return uuid.replace("UUID", "")


###########################################################
class DBObject(database_helper.DBObject):
    def toH(self, level=0):
        ImagingDatabase().completeNomenclatureLabel(self)
        ret = database_helper.DBObject.toH(self, level)
        if hasattr(self, "id"):
            ret["imaging_uuid"] = self.getUUID()
        return ret


class BootService(DBObject):
    # used_bs_id = ID of BootService if this BootService is used
    to_be_exported = [
        "id",
        "value",
        "default_desc",
        "uri",
        "is_local",
        "default_name",
        "used_bs_id",
    ]
    need_iteration = ["menu_item"]
    i18n = ["fk_name", "fk_desc"]


class BootServiceInMenu(DBObject):
    pass


class BootServiceOnImagingServer(DBObject):
    pass


class ComputerDisk(DBObject):
    to_be_exported = ["num"]


class ComputerPartition(DBObject):
    to_be_exported = ["num", "type", "length"]


class Entity(DBObject):
    to_be_exported = ["id", "name", "uuid"]


class Image(DBObject):
    to_be_exported = [
        "id",
        "path",
        "checksum",
        "size",
        "desc",
        "is_master",
        "creation_date",
        "fk_creator",
        "name",
        "is_local",
        "uuid",
        "mastered_on_target_uuid",
        "read_only",
        "fk_state",
    ]
    need_iteration = ["menu_item", "post_install_scripts"]


class ImageState(DBObject):
    to_be_exported = ["id", "label"]


class ImageInMenu(DBObject):
    pass


class ImagingLog(DBObject):
    to_be_exported = [
        "id",
        "timestamp",
        "completeness",
        "detail",
        "fk_imaging_log_state",
        "fk_imaging_log_level",
        "fk_target",
        "imaging_log_state",
        "imaging_log_level",
    ]
    need_iteration = ["target"]


class ImagingLogState(DBObject):
    to_be_exported = ["id", "label"]


class ImageOnImagingServer(DBObject):
    pass


class ImagingServer(DBObject):
    to_be_exported = [
        "id",
        "name",
        "url",
        "packageserver_uuid",
        "is_recursive",
        "fk_entity",
        "fk_default_menu",
        "fk_language",
        "language",
        "diskless_dir",
        "diskless_kernel",
        "inventories_dir",
        "pxe_time_reboot",
        "diskless_initrd",
        "tools_dir",
        "davos_opts",
        "template_name",
        "increment",
        "digit",
    ]


class Internationalization(DBObject):
    to_be_exported = ["id", "label", "fk_language"]


class Language(DBObject):
    to_be_exported = ["id", "label"]


class MasteredOn(DBObject):
    to_be_exported = ["fk_image", "image", "fk_imaging_log", "imaging_log"]


class Menu(DBObject):
    to_be_exported = [
        "id",
        "default_name",
        "fk_name",
        "timeout",
        "background_uri",
        "message",
        "ethercard",
        "bootcli",
        "disklesscli",
        "dont_check_disk_size",
        "hidden_menu",
        "debug",
        "update_nt_boot",
        "fk_default_item",
        "fk_default_item_WOL",
        "synchrostate",
    ]
    i18n = ["fk_name"]


class MenuItem(DBObject):
    to_be_exported = [
        "id",
        "default_name",
        "order",
        "hidden",
        "hidden_WOL",
        "fk_menu",
        "fk_name",
        "default",
        "default_WOL",
        "desc",
        "read_only",
    ]
    need_iteration = ["boot_service", "image"]


class Partition(DBObject):
    to_be_exported = ["id", "filesystem", "size", "fk_image"]


class PostInstallScript(DBObject):
    to_be_exported = [
        "id",
        "default_name",
        "value",
        "default_desc",
        "is_local",
        "order",
        "fk_boot_service",
    ]
    i18n = ["fk_name", "fk_desc"]


class PostInstallScriptInImage(DBObject):
    to_be_exported = ["order"]


class PostInstallScriptOnImagingServer(DBObject):
    pass


class SynchroState(DBObject):
    to_be_exported = ["id", "label"]


class Target(DBObject):
    # nic_uuid is not necessary outside of the imaging DB
    to_be_exported = [
        "id",
        "name",
        "uuid",
        "type",
        "fk_entity",
        "fk_menu",
        "kernel_parameters",
        "image_parameters",
        "exclude_parameters",
        "is_registered_in_package_server",
        "raw_mode",
    ]


class TargetType(DBObject):
    to_be_exported = ["id", "label"]


class User(DBObject):
    to_be_exported = ["id", "login"]


class Multicast(DBObject):
    to_be_exported = ["id", "location", "target_uuid", "image_uuid", "image_name"]
