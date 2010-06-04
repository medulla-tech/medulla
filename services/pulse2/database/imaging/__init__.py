# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
Database class for imaging
"""

import logging
import time
import datetime

from pulse2.utils import isUUID
from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from pulse2.database.imaging.types import P2ISS, P2IT, P2IM, P2IIK, P2ERR, P2ILL

from sqlalchemy import create_engine, ForeignKey, Integer, MetaData, Table, Column, and_, or_, desc
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.sql.expression import alias as sa_exp_alias

# THAT REQUIRE TO BE IN A MMC SCOPE, NOT IN A PULSE2 ONE
from pulse2.managers.profile import ComputerProfileManager
from pulse2.managers.location import ComputerLocationManager

DATABASEVERSION = 1


class ImagingDatabase(DyngroupDatabaseHelper):
    """
    Class to query the Pulse2 imaging database.

    DyngroupDatabaseHelper is a Singleton, so is ImagingDatabase
    """

    def db_check(self):
        self.my_name = "ImagingDatabase"
        self.configfile = "imaging.ini"
        return DyngroupDatabaseHelper.db_check(self, DATABASEVERSION)

    def activate(self, config):
        self.logger = logging.getLogger()
        DyngroupDatabaseHelper.init(self)
        if self.is_activated:
            self.logger.info("ImagingDatabase don't need activation")
            return None
        self.logger.info("ImagingDatabase is activating")
        self.config = config
        db_path = self.makeConnectionPath()
        if db_path.find('?') == -1:
            db_path = db_path + "?charset=utf8&use_unicode=0"
        else:
            db_path = db_path + "&charset=utf8&use_unicode=0"
        self.db = create_engine(db_path, pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize, convert_unicode=True)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            return False
        self.metadata.create_all()
        self.r_nomenclatures = {}
        self.nomenclatures = {
            'ImagingLogState': ImagingLogState,
            'ImagingLogLevel': ImagingLogLevel,
            'TargetType': TargetType,
            'Protocol': Protocol,
            'SynchroState': SynchroState,
            'Language': Language,
            'ImageState' : ImageState
        }
        self.fk_nomenclatures = {
            'ImagingLog': {
                'fk_imaging_log_state': 'ImagingLogState',
                'fk_imaging_log_level': 'ImagingLogLevel'
            },
            'Target': {
                'type': 'TargetType'
            },
            'Menu': {
                'fk_protocol': 'Protocol',
                'fk_synchrostate': 'SynchroState'
            },
            'ImagingServer': {
                'fk_language': 'Language'
            },
            'Image': {
                'fk_state': 'ImageState'
            },
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
            'default_name': self.config.web_def_default_menu_name,
            'timeout': self.config.web_def_default_timeout,
            'background_uri': self.config.web_def_default_background_uri,
            'message': self.config.web_def_default_message,
            'protocol': self.config.web_def_default_protocol
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
        for i in session.query(ImagingServer).add_entity(Entity).select_from(self.imaging_server.join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity)).all():
            self.imagingServer_lang[id2uuid(i[0].id)] = i[0].fk_language
            # the true one! self.imagingServer_entity[id2uuid(i[0].id)] = i[1].uuid
            # the working one in our context :
            self.imagingServer_entity[i[1].uuid] = id2uuid(i[0].id)

        session.close()

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the imaging database
        """
        self.version = Table("version", self.metadata, autoload = True)

        self.initTables()
        mapper(BootService, self.boot_service)
        mapper(BootServiceInMenu, self.boot_service_in_menu)
        mapper(BootServiceOnImagingServer, self.boot_service_on_imaging_server)
        mapper(ComputerDisk, self.computer_disk, properties = {
            'partitions' : relation(ComputerPartition,
                                    cascade="all,delete-orphan")
            })
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
        mapper(ImagingLogLevel, self.imaging_log_level)
        mapper(MasteredOn, self.mastered_on)
        mapper(Menu, self.menu) #, properties = { 'default_item':relation(MenuItem), 'default_item_WOL':relation(MenuItem) } )
        mapper(MenuItem, self.menu_item) #, properties = { 'menu' : relation(Menu) })
        mapper(Partition, self.partition)
        mapper(PostInstallScript, self.post_install_script)
        mapper(PostInstallScriptInImage, self.post_install_script_in_image)
        mapper(PostInstallScriptOnImagingServer, self.post_install_script_on_imaging_server)
        mapper(Protocol, self.protocol)
        mapper(SynchroState, self.synchro_state)
        mapper(Target, self.target, properties = {
            'disks' : relation(ComputerDisk,
                               cascade="all,delete-orphan")
            })
        mapper(TargetType, self.target_type)
        mapper(User, self.user)

    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """

        self.boot_service = Table(
            "BootService",
            self.metadata,
            autoload = True
        )

        self.entity = Table(
            "Entity",
            self.metadata,
            autoload = True
        )

        self.language = Table(
            "Language",
            self.metadata,
            autoload = True
        )

        self.imaging_log_state = Table(
            "ImagingLogState",
            self.metadata,
            autoload = True
        )

        self.imaging_log_level = Table(
            "ImagingLogLevel",
            self.metadata,
            autoload = True
        )

        self.synchro_state = Table(
            "SynchroState",
            self.metadata,
            autoload = True
        )

        self.post_install_script = Table(
            "PostInstallScript",
            self.metadata,
            autoload = True
        )

        self.protocol = Table(
            "Protocol",
            self.metadata,
            autoload = True
        )

        self.target_type = Table(
            "TargetType",
            self.metadata,
            autoload = True
        )

        self.user = Table(
            "User",
            self.metadata,
            autoload = True
        )

        self.image = Table(
            "Image",
            self.metadata,
            Column('fk_creator', Integer, ForeignKey('User.id')),
            Column('fk_state', Integer, ForeignKey('ImageState.id')),
            autoload = True
        )

        self.image_state = Table(
            "ImageState",
            self.metadata,
            autoload = True
        )

        self.imaging_server = Table(
            "ImagingServer",
            self.metadata,
            Column('fk_entity', Integer, ForeignKey('Entity.id')),
            Column('fk_default_menu', Integer, ForeignKey('Menu.id')),
            Column('fk_language', Integer, ForeignKey('Language.id')),
            autoload = True
        )

        self.internationalization = Table(
            "Internationalization",
            self.metadata,
            Column('id', Integer, primary_key=True),
            # Column('fk_language', Integer, ForeignKey('Language.id'), primary_key=True),
            Column('fk_language', Integer, primary_key=True),
            useexisting=True,
            autoload = True
        )

        self.menu = Table(
            "Menu",
            self.metadata,
            # cant put them for circular dependencies reasons, the join must be explicit
            # Column('fk_default_item', Integer, ForeignKey('MenuItem.id')),
            Column('fk_default_item', Integer),
            # Column('fk_default_item_WOL', Integer, ForeignKey('MenuItem.id')),
            Column('fk_default_item_WOL', Integer),
            Column('fk_protocol', Integer, ForeignKey('Protocol.id')),
            # fk_name is not an explicit FK, you need to choose the lang before being able to join
            Column('fk_synchrostate', Integer, ForeignKey('SynchroState.id')),
            useexisting=True,
            autoload = True
        )

        self.menu_item = Table(
            "MenuItem",
            self.metadata,
            Column('fk_menu', Integer, ForeignKey('Menu.id')),
            # fk_name is not an explicit FK, you need to choose the lang before being able to join
            useexisting=True,
            autoload = True
        )

        self.partition = Table(
            "Partition",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id')),
            useexisting=True,
            autoload = True
        )

        self.boot_service_in_menu = Table(
            "BootServiceInMenu",
            self.metadata,
            Column('fk_bootservice', Integer, ForeignKey('BootService.id'), primary_key=True),
            Column('fk_menuitem', Integer, ForeignKey('MenuItem.id'), primary_key=True),
            useexisting=True,
            autoload = True
        )

        self.boot_service_on_imaging_server = Table(
            "BootServiceOnImagingServer",
            self.metadata,
            Column('fk_boot_service', Integer, ForeignKey('BootService.id'), primary_key=True),
            # Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            # cant declare it implicit as a FK else it make circular dependencies
            Column('fk_imaging_server', Integer, primary_key=True),
            useexisting=True,
            autoload = True
        )

        self.image_in_menu = Table(
            "ImageInMenu",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_menuitem', Integer, ForeignKey('MenuItem.id'), primary_key=True),
            useexisting=True,
            autoload = True
        )

        self.image_on_imaging_server = Table(
            "ImageOnImagingServer",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            useexisting=True,
            autoload = True
        )

        self.target = Table(
            "Target",
            self.metadata,
            Column('fk_entity', Integer, ForeignKey('Entity.id')),
            Column('fk_menu', Integer, ForeignKey('Menu.id')),
            useexisting=True,
            autoload = True
        )

        self.computer_disk = Table(
            'ComputerDisk',
            self.metadata,
            autoload = True
        )

        self.computer_partition = Table(
            'ComputerPartition',
            self.metadata,
            autoload = True
        )

        self.imaging_log = Table(
            "ImagingLog",
            self.metadata,
            Column('fk_imaging_log_state', Integer, ForeignKey('ImagingLogState.id')),
            Column('fk_imaging_log_level', Integer, ForeignKey('ImagingLogLevel.id')),
            Column('fk_target', Integer, ForeignKey('Target.id')),
            useexisting=True,
            autoload = True
        )

        self.mastered_on = Table(
            "MasteredOn",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_imaging_log', Integer, ForeignKey('ImagingLog.id'), primary_key=True),
            useexisting=True,
            autoload = True
        )

        self.post_install_script_in_image = Table(
            "PostInstallScriptInImage",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_post_install_script', Integer, ForeignKey('PostInstallScript.id'), primary_key=True),
            useexisting=True,
            autoload = True
        )

        self.post_install_script_on_imaging_server = Table(
            "PostInstallScriptOnImagingServer",
            self.metadata,
            # Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            # circular deps
            Column('fk_imaging_server', Integer, primary_key=True),
            Column('fk_post_install_script', Integer, ForeignKey('PostInstallScript.id'), primary_key=True),
            useexisting=True,
            autoload = True
        )


#self.nomenclatures = {'ImagingLogState':ImagingLogState, 'TargetType':TargetType, 'Protocol':Protocol}
#self.fk_nomenclatures = {'ImagingLog':{'fk_imaging_log_state':'ImagingLogState'}, 'Target':{'type':'TargetType'}, 'Menu':{'fk_protocol':'Protocol'}}

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
        if type(objs) != list and type(objs) != tuple:
            objs = [objs]
        if len(objs) == 0:
            return
        className = str(objs[0].__class__).split("'")[1].split('.')[-1]
        nomenclatures = []
        if className in self.fk_nomenclatures:
            for i in self.fk_nomenclatures[className]:
                nomenclatures.append([i, i.replace('fk_', ''), self.nomenclatures[self.fk_nomenclatures[className][i]]])
            for obj in objs:
                for fk, field, value in nomenclatures:
                    fk_val = getattr(obj, fk)
                    if fk == field:
                        field = '%s_value' % field
                    if fk_val in value:
                        setattr(obj, field, value[fk_val])
                    else:
                        self.logger.warn("nomenclature is missing for %s field %s (value = %s)" % (str(obj), field, str(fk_val)))
                        setattr(obj, field, "%s:nomenclature does not exists." % (P2ERR.ERR_MISSING_NOMENCLATURE))

    def completeTarget(self, objs):
        """
        take a list of dict with a fk_target element and add them the target dict that correspond
        """
        ids = {}
        for i in objs:
            ids[i['fk_target']] = None
        ids = ids.keys()
        targets = self.getTargetsById(ids)
        id_target = {}
        for t in targets:
            t = t.toH()
            id_target[t['id']] = t
        for i in objs:
            i['target'] = id_target[i['fk_target']]

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
    def getTargetsEntity(self, uuids):
        session = create_session()
        e = session.query(Entity).add_entity(Target).select_from(self.entity.join(self.target, self.target.c.fk_entity == self.entity.c.id)).filter(self.target.c.uuid.in_(uuids)).all()
        session.close()
        return e

    def getTargetsById(self, ids):
        session = create_session()
        n = session.query(Target).filter(self.target.c.id.in_(ids)).all()
        session.close()
        return n

    def getTargetsByUUID(self, ids, session = None):
        need_to_close_session = False
        if session == None:
            need_to_close_session = True
            session = create_session()
        n = session.query(Target).filter(self.target.c.uuid.in_(ids)).all()
        if need_to_close_session:
            session.close()
        return n

    def __mergeTargetInImagingLog(self, imaging_log_list):
        ret = []
        for imaging_log, target in imaging_log_list:
            setattr(imaging_log, 'target', target)
            ret.append(imaging_log)
        return ret

    def __getTargetsMenuQuery(self, session):
        return session.query(Menu).add_column(self.internationalization.c.label).select_from(self.menu \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
                .join(self.imaging_server, self.target.c.fk_entity == self.imaging_server.c.fk_entity) \
                .outerjoin(self.internationalization, and_(self.internationalization.c.id == self.menu.c.fk_name, self.internationalization.c.fk_language == self.imaging_server.c.fk_language)) \
        )

    def getTargetsMenuTID(self, target_id):
        session = create_session()
        q = self.__getTargetsMenuQuery(session)
        q = q.filter(self.target.c.id == target_id).first() # there should always be only one!
        session.close()
        if q == None: return q
        if q[1] != None and q[1] != 'NOTTRANSLATED':
            q[0].default_name = q[1]
        return q[0]

    def getTargetsMenuTUUID(self, target_id, session = None):
        need_to_close_session = False
        if session == None:
            need_to_close_session = True
            session = create_session()
        q = self.__getTargetsMenuQuery(session)
        q = q.filter(self.target.c.uuid == target_id).first() # there should always be only one!
        if need_to_close_session:
            session.close()
        if q == None: return q
        if q[1] != None and q[1] != 'NOTTRANSLATED':
            q[0].default_name = q[1]
        return q[0]

    def getDefaultSuscribeMenu(self, location, session = None):
        need_to_close_session = False
        if session == None:
            need_to_close_session = True
            session = create_session()
        lang = self.__getLocLanguage(session, location.uuid)
        q = session.query(Menu).add_column(self.internationalization.c.label).select_from(self.menu \
                .outerjoin(self.internationalization, and_(self.internationalization.c.id == self.menu.c.fk_name, self.internationalization.c.fk_language == lang)) \
            ).filter(self.menu.c.id == 2).first()
        if need_to_close_session:
            session.close()
        if q == None: return q
        if q[1] != None and q[1] != 'NOTTRANSLATED':
            q[0].default_name = q[1]
        return q[0]

    def getEntitiesImagingServer(self, entities_uuid):
        session = create_session()
        q = session.query(ImagingServer).add_column(self.entity.c.uuid)
        q = q.select_from(self.imaging_server.join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity))
        q = q.filter(self.entity.c.uuid.in_(entities_uuid)).all()
        session.close()
        return q

    def getEntityDefaultMenu(self, loc_id, session = None):
        """
        Given an entity <loc_id>, returns its default menu (more precisely, its imaging server default menu)

        FIXME: this code doesn't handle the case when imaging_server.recursive
        is True

        @param loc_id the entity UUID
        @param session (optional) a SQL session to use
        """
        need_to_close_session = False
        if session == None:
            need_to_close_session = True
            session = create_session()
        j = self.menu.join(self.imaging_server).join(self.entity).outerjoin(self.internationalization, and_(self.internationalization.c.id == self.menu.c.fk_name, self.internationalization.c.fk_language == self.imaging_server.c.fk_language))
        q = session.query(Menu).add_column(self.internationalization.c.label).select_from(j)
        q = q.filter(self.entity.c.uuid == loc_id)
        q = q.filter(self.imaging_server.c.associated == 1)
        q = q.first()
        if need_to_close_session:
            session.close()
        if q == None: return q
        if q[1] != None and q[1] != 'NOTTRANSLATED':
            q[0].default_name = q[1]
        return q[0]

    def getTargetMenu(self, uuid, type, session = None):
        need_to_close_session = False
        if session == None:
            need_to_close_session = True
            session = create_session()
        q = session.query(Menu).add_column(self.internationalization.c.label).select_from(self.menu \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
                .join(self.imaging_server, self.imaging_server.c.fk_entity == self.target.c.fk_entity) \
                .outerjoin(self.internationalization, and_(self.internationalization.c.id == self.menu.c.fk_name, self.internationalization.c.fk_language == self.imaging_server.c.fk_language)) \
            ).filter(and_(self.target.c.uuid == uuid, self.target.c.type == type)).first() # there should always be only one!
        if need_to_close_session:
            session.close()
        if q == None: return q
        if q[1] != None and q[1] != 'NOTTRANSLATED':
            q[0].default_name = q[1]
        return q[0]

    def __mergeMenuItemInBootService(self, list_of_bs, list_of_both):
        ret = []
        temporary = {}
        for bs, mi in list_of_both:
            if mi != None:
                temporary[bs.id] = mi
        for bs, bs_id, name_i18n, desc_i18n in list_of_bs:
            if name_i18n != None:
                setattr(bs, 'default_name', name_i18n.label)
            if desc_i18n != None:
                setattr(bs, 'default_desc', desc_i18n.label)
            if temporary.has_key(bs_id):
                mi = temporary[bs_id]
                if name_i18n != None:
                    setattr(mi, 'default_name', name_i18n.label)
                if desc_i18n != None:
                    setattr(mi, 'default_desc', desc_i18n.label)
                setattr(bs, 'menu_item', mi)
            ret.append(bs)
        return ret

    def __mergeBootServiceInMenuItem(self, my_list):
        ret = []
        for mi, bs, menu, bsois, name_i18n, desc_i18n in my_list:
            if bs != None:
                setattr(mi, 'boot_service', bs)
            setattr(mi, 'is_local', (bsois != None))
            if menu != None:
                setattr(mi, 'default', (menu.fk_default_item == mi.id))
                setattr(mi, 'default_WOL', (menu.fk_default_item_WOL == mi.id))
            if name_i18n != None:
                setattr(mi, 'name', name_i18n.label)
                setattr(bs, 'default_name', name_i18n.label)
            if desc_i18n != None:
                setattr(mi, 'desc', desc_i18n.label)
                setattr(bs, 'default_desc', desc_i18n.label)
            ret.append(mi)
        return ret

    def __mergeMenuItemInImage(self, list_of_im, list_of_both, list_of_target = []):
        ret = []
        temporary = {}
        for im, mi in list_of_both:
            if mi != None:
                temporary[im.id] = mi
        targets = {}
        for t, mo in list_of_target:
            targets[mo.fk_image] = t.uuid
        for im, im_id in list_of_im:
            if temporary.has_key(im_id):
                setattr(im, 'menu_item', temporary[im_id])
            if len(list_of_target) != 0 and targets.has_key(im.id):
                setattr(im, 'mastered_on_target_uuid', targets[im.id])
            ret.append(im)
        return ret

    def __mergeBootServiceOrImageInMenuItem(self, mis):
        """ warning this one does not work on a list but on a tuple of 3 elements (mi, bs, im) """
        (menuitem, bootservice, image, menu, name_bs_i18n, desc_bs_i18n) = mis
        if bootservice != None:
            if name_bs_i18n != None:
                setattr(bootservice, 'default_name', name_bs_i18n.label)
            if desc_bs_i18n != None:
                setattr(bootservice, 'default_desc', desc_bs_i18n.label)
            setattr(menuitem, 'boot_service', bootservice)
        if image != None:
            setattr(menuitem, 'image', image)
        if menu != None:
            setattr(menuitem, 'default', (menu.fk_default_item == menuitem.id))
            setattr(menuitem, 'default_WOL', (menu.fk_default_item_WOL == menuitem.id))

        return menuitem

    def __mergeImageInMenuItem(self, my_list):
        ret = []
        for mi, im, menu in my_list:
            if im != None:
                setattr(mi, 'image', im)
            if menu != None:
                setattr(mi, 'default', (menu.fk_default_item == mi.id))
                setattr(mi, 'default_WOL', (menu.fk_default_item_WOL == mi.id))
            ret.append(mi)
        return ret

    def __getMenusImagingServer(self, session, menu_id):
        """
        Get stuff pointing to menu menu_id
        """
        j = self.imaging_server.outerjoin(self.entity).outerjoin(self.target)
        f = or_(self.imaging_server.c.fk_default_menu == menu_id, self.target.c.fk_menu == menu_id)
        imaging_server = session.query(ImagingServer).select_from(j).filter(f).first()
        if imaging_server:
            return imaging_server
        else:
            self.logger.error("cant find any imaging_server for menu '%s'" % (menu_id))
            return  None

    def getMenuContent(self, menu_id, type = P2IM.ALL, start = 0, end = -1, filter = '', session = None, loc_id = None):# TODO implement the start/end with a union between q1 and q2
        session_need_close = False
        if session == None:
            session = create_session()
            session_need_close = True

        mi_ids = session.query(MenuItem).add_column(self.menu_item.c.id).select_from(self.menu_item.join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id))
        if filter != '':
            mi_ids = mi_ids.filter(and_(self.menu.c.id == menu_id, self.menu_item.c.desc.like('%'+filter+'%')))
        else:
            mi_ids = mi_ids.filter(self.menu.c.id == menu_id)
        mi_ids = mi_ids.order_by(self.menu_item.c.order)
        if end != -1:
            mi_ids = mi_ids.offset(int(start)).limit(int(end)-int(start))
        else:
            mi_ids = mi_ids.all()
        mi_ids = map(lambda x:x[1], mi_ids)

        if loc_id != None:
            imaging_server = self.getImagingServerByEntityUUID(loc_id, session)
        else:
            imaging_server = self.__getMenusImagingServer(session, menu_id)
        is_id = 0
        lang = 1
        if imaging_server:
            is_id = imaging_server.id
            lang = imaging_server.fk_language
        elif loc_id != None and menu_id == 2: #this is the suscribe menu
            lang = self.__getLocLanguage(session, loc_id)

        q = []
        if type == P2IM.ALL or type == P2IM.BOOTSERVICE:
            # we don't need the i18n trick for the menu name here
            I18n1 = sa_exp_alias(self.internationalization)
            I18n2 = sa_exp_alias(self.internationalization)
            q1 = session.query(MenuItem)
            q1 = q1.add_entity(BootService).add_entity(Menu).add_entity(BootServiceOnImagingServer).add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2)
            q1 = q1.select_from(self.menu_item \
                    .join(self.boot_service_in_menu) \
                    .join(self.boot_service) \
                    .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                    .outerjoin(I18n1, and_(self.boot_service.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                    .outerjoin(I18n2, and_(self.boot_service.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
                    .outerjoin(self.boot_service_on_imaging_server) \
            )
            q1 = q1.filter(and_(self.menu_item.c.id.in_(mi_ids), or_(self.boot_service_on_imaging_server.c.fk_boot_service == None, self.boot_service_on_imaging_server.c.fk_imaging_server == is_id)))
            q1 = q1.order_by(self.menu_item.c.order).all()
            q1 = self.__mergeBootServiceInMenuItem(q1)
            q.extend(q1)
        if type == P2IM.ALL or type == P2IM.IMAGE:
            # we don't need the i18n trick for the menu name here
            q2 = session.query(MenuItem).add_entity(Image).add_entity(Menu).select_from(self.menu_item.join(self.image_in_menu).join(self.image).join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id))
            q2 = q2.filter(self.menu_item.c.id.in_(mi_ids)).order_by(self.menu_item.c.order).all()
            q2 = self.__mergeImageInMenuItem(q2)
            q.extend(q2)
        if session_need_close:
            session.close()
        q.sort(lambda x,y: cmp(x.order, y.order))
        return q

    def getLastMenuItemOrder(self, menu_id):
        session = create_session()
        q = session.query(MenuItem).filter(self.menu_item.c.fk_menu == menu_id).max(self.menu_item.c.order)
        session.close()
        if q == None:
            return -1
        return q

    def countMenuContentFast(self, menu_id): # get P2IM.ALL and empty filter
        session = create_session()
        q = session.query(MenuItem).filter(self.menu_item.c.fk_menu == menu_id).count()
        session.close()
        return q
    def countMenuContent(self, menu_id, type = P2IM.ALL, filter = ''):
        if type == P2IM.ALL and filter =='':
            return self.countMenuContentFast(menu_id)

        session = create_session()
        q = 0
        if type == P2IM.ALL or type == P2IM.BOOTSERVICE:
            q1 = session.query(MenuItem).add_entity(BootService).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service))
            q1 = q1.filter(and_(self.menu_item.c.fk_menu == menu_id, self.boot_service.c.default_desc.like('%'+filter+'%'))).count()
            q += q1
        if type == P2IM.ALL or type == P2IM.IMAGE:
            q2 = session.query(MenuItem).add_entity(Image).select_from(self.menu_item.join(self.image_in_menu).join(self.image))
            q2 = q2.filter(and_(self.menu_item.c.fk_menu == menu_id, self.boot_service.c.default_desc.like('%'+filter+'%'))).count()
            q += q2
        session.close()
        return q

###########################################################
    def getEntityUrl(self, location_uuid):
        session = create_session()
        # there should be just one imaging server per entity
        q = session.query(ImagingServer).select_from(self.imaging_server.join(self.entity)).filter(self.entity.c.uuid == location_uuid).first()
        session.close()
        if q == None:
            return None
        return q.url

    def __ImagingLogs4Location(self, session, location_uuid, filter):
        n = session.query(ImagingLog).add_entity(Target).select_from(self.imaging_log.join(self.target).join(self.entity)).filter(self.entity.c.uuid == location_uuid)
        if filter != '':
            n = n.filter(or_(self.imaging_log.c.detail.like('%'+filter+'%'), self.target.c.name.like('%'+filter+'%')))
        return n

    def getImagingLogs4Location(self, location_uuid, start, end, filter):
        session = create_session()
        n = self.__ImagingLogs4Location(session, location_uuid, filter)
        n = n.order_by(desc(self.imaging_log.c.timestamp))
        if end != -1:
            n = n.offset(int(start)).limit(int(end)-int(start))
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
    def __ImagingLogsOnTargetByIdAndType(self, session, target_id, type, filter):
        q = session.query(ImagingLog).add_entity(Target).select_from(self.imaging_log.join(self.target))
        if type in [P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE]:
            q = q.filter(self.target.c.type == type) \
                .filter(self.target.c.uuid == target_id)
        elif type == P2IT.PROFILE:
            # Need to get all computers UUID of the profile
            uuids = map(lambda c: c.uuid,
                        ComputerProfileManager().getProfileContent(target_id))
            q = q.filter(self.target.c.type == P2IT.COMPUTER_IN_PROFILE) \
                .filter(self.target.c.uuid.in_(uuids))
        else:
            self.logger.error("type %s does not exists!" % type)
            # to be sure we don't get anything, this is an error case!
            q = q.filter(self.target.c.type == 0)
        if filter != '':
            q = q.filter(or_(self.imaging_log.c.detail.like('%' + filter + '%'), self.target.c.name.like('%' + filter + '%')))
        return q

    def getImagingLogsOnTargetByIdAndType(self, target_id, type, start, end, filter):
        session = create_session()
        q = self.__ImagingLogsOnTargetByIdAndType(session, target_id, type, filter)
        q = q.order_by(desc(self.imaging_log.c.timestamp))
        if end != -1:
            q = q.offset(int(start)).limit(int(end) - int(start))
        else:
            q = q.all()
        session.close()
        q = self.__mergeTargetInImagingLog(q)
        return q

    def countImagingLogsOnTargetByIdAndType(self, target_id, type, filter):
        session = create_session()
        q = self.__ImagingLogsOnTargetByIdAndType(session, target_id, type, filter)
        q = q.count()
        session.close()
        return q

    ######################
    def getTargetLanguage(self, session, target_uuid):
        ims = session.query(ImagingServer).select_from(self.imaging_server.join(self.target, self.target.c.fk_entity == self.imaging_server.c.fk_entity))
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
        if self.imagingServer_entity.has_key(loc_id):
            if not self.imagingServer_lang.has_key(self.imagingServer_entity[loc_id]):
                ims = session.query(ImagingServer).select_from(self.imaging_server.join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity)).filter(self.entity.c.uuid == loc_id).first()
                self.imagingServer_lang[self.imagingServer_entity[loc_id]] = ims.fk_language
        else:
            q = session.query(ImagingServer).add_entity(Entity).select_from(self.imaging_server.join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity)).filter(self.entity.c.uuid == loc_id).first()
            if q != None:
                ims, en = q
                # the true one! self.imagingServer_entity[id2uuid(ims.id)] = en.uuid
                # the working one in our context :
                self.imagingServer_entity[en.uuid] = id2uuid(ims.id)
                self.imagingServer_lang[self.imagingServer_entity[loc_id]] = ims.fk_language
            else:
                return 1 # default to english
        lang = self.imagingServer_lang[self.imagingServer_entity[loc_id]]
        return lang

    def __PossibleBootServices(self, session, target_uuid, filter):
        lang = self.getTargetLanguage(session, target_uuid)

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)
        q = session.query(BootService).add_column(self.boot_service.c.id).add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2)
        q = q.select_from(self.boot_service \
                .outerjoin(self.boot_service_on_imaging_server, self.boot_service.c.id == self.boot_service_on_imaging_server.c.fk_boot_service) \
                .outerjoin(self.imaging_server, self.imaging_server.c.id == self.boot_service_on_imaging_server.c.fk_imaging_server) \
                .outerjoin(I18n1, and_(self.boot_service.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                .outerjoin(I18n2, and_(self.boot_service.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
                .outerjoin(self.entity).outerjoin(self.target))
        q = q.filter(or_(self.target.c.uuid == target_uuid, self.boot_service_on_imaging_server.c.fk_boot_service == None))
        if filter != '':
            q = q.filter(or_(self.boot_service.c.default_desc.like('%'+filter+'%'), self.boot_service.c.value.like('%'+filter+'%')))
        return q

    def __EntityBootServices(self, session, loc_id, filter):
        lang = self.__getLocLanguage(session, loc_id)

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)
        q = session.query(BootService).add_column(self.boot_service.c.id).add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2)
        q = q.select_from(self.boot_service \
                .outerjoin(self.boot_service_on_imaging_server, self.boot_service.c.id == self.boot_service_on_imaging_server.c.fk_boot_service) \
                .outerjoin(self.imaging_server, self.imaging_server.c.id == self.boot_service_on_imaging_server.c.fk_imaging_server) \
                .outerjoin(I18n1, and_(self.boot_service.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                .outerjoin(I18n2, and_(self.boot_service.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
                .outerjoin(self.entity))
        q = q.filter(or_(self.entity.c.uuid == loc_id, self.boot_service_on_imaging_server.c.fk_boot_service == None))
        if filter != '':
            q = q.filter(or_(self.boot_service.c.default_desc.like('%'+filter+'%'), self.boot_service.c.value.like('%'+filter+'%')))
        return q

    def __PossibleBootServiceAndMenuItem(self, session, bs_ids, menu_id):
        q = session.query(BootService).add_entity(MenuItem)
        q = q.filter(and_(
            self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id,
            self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id,
            self.menu_item.c.fk_menu == menu_id,
            self.boot_service.c.id.in_(bs_ids)
        )).all()
        return q

    def getPossibleBootServices(self, target_uuid, start, end, filter):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid)
        q1 = self.__PossibleBootServices(session, target_uuid, filter)
        q1 = q1.group_by(self.boot_service.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end)-int(start))
        else:
            q1 = q1.all()
        bs_ids = map(lambda bs:bs[1], q1)
        q2 = self.__PossibleBootServiceAndMenuItem(session, bs_ids, menu.id)
        profile = ComputerProfileManager().getComputersProfile(target_uuid)
        if profile != None:
            # this should be the profile uuid!
            menu_root = self.getTargetsMenuTUUID(profile.id)
            q3 = self.__PossibleBootServiceAndMenuItem(session, bs_ids, menu_root.id)
            q4 = []
            already = []
            for bs, mi in q3:
                setattr(mi, 'read_only', True)
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
            q1 = q1.offset(int(start)).limit(int(end)-int(start))
        else:
            q1 = q1.all()
        bs_ids = map(lambda bs:bs[1], q1)
        q2 = self.__PossibleBootServiceAndMenuItem(session, bs_ids, menu.id)
        session.close()

        q = self.__mergeMenuItemInBootService(q1, q2)
        return q

    def countPossibleBootServices(self, target_uuid, filter):
        session = create_session()
        q = self.__PossibleBootServices(session, target_uuid, filter)
        q = q.count()
        session.close()
        return q

    def countEntityBootServices(self, loc_id, filter):
        session = create_session()
        q = self.__EntityBootServices(session, loc_id, filter)
        q = q.count()
        session.close()
        return q

    def __createNewMenuItem(self, session, menu_id, params):
        mi = MenuItem()
        params['order'] = self.getLastMenuItemOrder(menu_id) + 1
        mi = self.__fillMenuItem(session, mi, menu_id, params)
        return mi

    def __fillMenuItem(self, session, mi, menu_id, params):
        if params.has_key('hidden'):
            mi.hidden = params['hidden']
        else:
            mi.hidden = True
        if params.has_key('hidden_WOL'):
            mi.hidden_WOL = params['hidden_WOL']
        else:
            mi.hidden_WOL = True
        if params.has_key('order'):
            mi.order = params['order']
        mi.fk_menu = menu_id
        session.save_or_update(mi)
        return mi

    def __addMenuDefaults(self, session, menu, mi, params):
        is_menu_modified = False
        if params.has_key('default') and 'default' in params and params['default']:
            is_menu_modified = True
            menu.fk_default_item = mi.id
        if params.has_key('default_WOL') and 'default_WOL' in params and params['default_WOL']:
            is_menu_modified = True
            menu.fk_default_item_WOL = mi.id
        if is_menu_modified:
            session.save_or_update(menu)
        return menu

    def __editMenuDefaults(self, session, menu, mi, params):
        is_menu_modified = False
        if type(menu) in (long, int):
            menu = session.query(Menu).filter(self.menu.c.id == menu).first()
        if menu.fk_default_item != mi.id and params['default']:
            is_menu_modified = True
            menu.fk_default_item = mi.id
        if menu.fk_default_item == mi.id and not params['default']:
            is_menu_modified = True
            menu.fk_default_item = None

        if menu.fk_default_item_WOL != mi.id and params['default_WOL']:
            is_menu_modified = True
            menu.fk_default_item_WOL = mi.id
        if menu.fk_default_item_WOL == mi.id and not params['default_WOL']:
            is_menu_modified = True
            menu.fk_default_item_WOL = None

        if is_menu_modified:
            session.save_or_update(menu)
        return menu

    def __computerChangeDefaultMenuItem(self, session, menu, mis, item_number):
        mi = mis[item_number]
        params = {'default':True}
        self.__addMenuDefaults(session, menu, mi, params)
        return mi.id

    def getProfileComputersDefaultMenuItem(self, profile_uuid, session):
        uuids = map(lambda c:c.uuid, ComputerProfileManager().getProfileContent(profile_uuid))

        q = session.query(Target).add_entity(Menu)
        q = q.select_from(self.target.join(self.menu, self.target.c.fk_menu == self.menu.c.id))
        q = q.filter(self.target.c.uuid.in_(uuids)).all()

        return q

    def profileChangeDefaultMenuItem(self, imaging_server_uuid, profile_uuid, item_number, session = None):
        session_need_close = False
        if session == None:
            session = create_session()
            session_need_close = True

        menu = self.getTargetsMenuTUUID(profile_uuid, session)
        mis = session.query(MenuItem).select_from(self.menu_item.join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu))
        mis = mis.filter(self.menu.c.id == menu_root.id).order_by(self.menu_item.c.order).all()

        mi_id = self.__computerChangeDefaultMenuItem(session, menu, mis, item_number)

        if session_need_close:
            session.close()
        return True

    def computerChangeDefaultMenuItem(self, imaging_server_uuid, computer_uuid, item_number):
        session = create_session()

        profile = ComputerProfileManager().getComputersProfile(computer_uuid)
        menu = self.getTargetsMenuTUUID(computer_uuid, session)
        if profile != None:
            # this should be the profile uuid!
            menu_root = self.getTargetsMenuTUUID(profile.id, session)
            mis = session.query(MenuItem).select_from(self.menu_item.join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu))
            mis = mis.filter(self.menu.c.id == menu_root.id).order_by(self.menu_item.c.order).all()
            root_len = len(mis)
            mi_id = None
            if root_len > item_number:
                mi_id = self.__computerChangeDefaultMenuItem(session, menu, mis, item_number)
            else:
                mis = session.query(MenuItem).select_from(self.menu_item.join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu))
                mis = mis.filter(self.menu.c.id == menu.id).order_by(self.menu_item.c.order).all()
                if len(mis) > item_number:
                    mi_id = self.__computerChangeDefaultMenuItem(session, menu, mis, item_number - root_len)
                else:
                    session.close()
                    raise Exception("can't get that element of the menu")
            computers = self.getProfileComputersDefaultMenuItem(profile.getUUID(), session)
            any_not_back_to_first = False
            for computer, m in computers:
                if m.fk_default_item != mi_id:
                    any_not_back_to_first = True

            if not any_not_back_to_first:
                self.profileChangeDefaultMenuItem(imaging_server_uuid, profile.uuid, item_number)

        else:
            mis = session.query(MenuItem).select_from(self.menu_item.join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu))
            mis = mis.filter(self.menu.c.id == menu.id).order_by(self.menu_item.c.order).all()
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
        session.save(bsim)
        session.flush()
        return bsim

    def __addImageInMenu(self, session, mi_id, im_uuid):
        imim = ImageInMenu()
        imim.fk_menuitem = mi_id
        imim.fk_image = uuid2id(im_uuid)
        session.save(imim)
        session.flush()
        return imim

    def __addService(self, session, bs_uuid, menu, params):
        bs = session.query(BootService).filter(self.boot_service.c.id == uuid2id(bs_uuid)).first()
        # TODO : what do we do with bs ?
        if menu == None:
            raise '%s:Please create menu before trying to put a bootservice' % (P2ERR.ERR_TARGET_HAS_NO_MENU)

        mi = self.__createNewMenuItem(session, menu.id, params)
        session.flush()

        self.__addMenuDefaults(session, menu, mi, params)
        self.__addBootServiceInMenu(session, mi.id, bs_uuid)

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
        mi = session.query(MenuItem).select_from(self.menu_item \
                .join(self.boot_service_in_menu, self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                .join(self.boot_service, self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id) \
                .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
        )
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()
        return mi

    def __editService(self, session, bs_uuid, menu, mi, params):
        bs = session.query(BootService).filter(self.boot_service.c.id == uuid2id(bs_uuid)).first()
        # TODO : what do we do with bs ?
        if menu == None:
            raise '%s:Please create menu before trying to put a bootservice' % (P2ERR.ERR_TARGET_HAS_NO_MENU)

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

    def __getMenuItemByUUID(self, session, mi_uuid):
        return session.query(MenuItem).filter(self.menu_item.c.id == uuid2id(mi_uuid)).first()

    def editServiceToEntity(self, mi_uuid, loc_id, params):
        session = create_session()
        if self.isLocalBootService(mi_uuid, session):
            # we can change the title/desc/...
            bs = session.query(BootService).select_form(self.boot_service.join(self.boot_service_in_menu))
            bs = bs.filter(self.boot_service_in_menu.c.fk_menuitem == uuid2id(mi_uuid)).first()
            if bs.default_name != params['default_name']:
                bs.default_name = params['default_name']
                bs.fk_name = 1
                session.save_or_update(bs)
        mi = self.__getMenuItemByUUID(session, mi_uuid)
        if mi == None:
            raise '%s:This MenuItem does not exists'%(P2ERR.ERR_UNEXISTING_MENUITEM)
        ret = self.__fillMenuItem(session, mi, mi.fk_menu, params)
        # TODO : what do we do with ret ?
        session.flush()
        self.__editMenuDefaults(session, mi.fk_menu, mi, params)
        session.flush()
        session.close()
        return None

    def __getFirstMenuItem(self, session, menu_id, exclude = None):
        mi = session.query(MenuItem).filter(self.menu_item.c.fk_menu == menu_id)
        if exclude != None:
            mi = mi.filter(self.menu_item.c.id != exclude)
        mi = mi.order_by(self.menu_item.c.order)
        return mi.first()

    def delServiceToTarget(self, bs_uuid, target_uuid):
        session = create_session()
        mi = session.query(MenuItem).select_from(self.menu_item \
                .join(self.boot_service_in_menu, self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                .join(self.boot_service, self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id) \
                .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                .join(self.target, self.menu.c.id == self.target.c.fk_menu))
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()
        bsim = session.query(BootServiceInMenu).select_from(self.boot_service_in_menu \
                .join(self.menu_item, self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                .join(self.boot_service, self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id) \
                .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                .join(self.target, self.menu.c.id == self.target.c.fk_menu))
        bsim = bsim.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()
        # if mi is the fk_default_item or the fk_default_item_WOL, we need to change that
        menu = session.query(Menu).filter(self.menu.c.id == mi.fk_menu).first()
        need_to_save_menu = False
        first_mi = None
        if menu.fk_default_item == mi.id:
            need_to_save_menu = True
            if first_mi == None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi == None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item = first_mi.id
        if menu.fk_default_item_WOL == mi.id:
            need_to_save_menu = True
            if first_mi == None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi == None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item_WOL = first_mi.id
        if need_to_save_menu:
            session.save_or_update(menu)
            session.flush()
        session.delete(bsim)
        session.flush()
        session.delete(mi)
        session.flush()

        session.close()
        return [True]

    def delServiceToEntity(self, bs_uuid, loc_id):
        # FIXME : fk_default_menu has moved
        # FIXME : explicit joins, check why !
        session = create_session()
        mi = session.query(MenuItem).select_from(self.menu_item
                .join(self.boot_service_in_menu, self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                .join(self.boot_service, self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id) \
                .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                .join(self.imaging_server, self.imaging_server.c.fk_default_menu == self.menu.c.id) \
                .join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity))
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.entity.c.uuid == loc_id)).first()
        bsim = session.query(BootServiceInMenu).select_from(self.boot_service_in_menu \
                .join(self.menu_item, self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                .join(self.boot_service, self.boot_service_in_menu.c.fk_bootservice == self.boot_service.c.id) \
                .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                .join(self.imaging_server, self.imaging_server.c.fk_default_menu == self.menu.c.id) \
                .join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity))
        bsim = bsim.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.entity.c.uuid == loc_id)).first()
        # if mi is the fk_default_item or the fk_default_item_WOL, we need to change that
        menu = session.query(Menu).filter(self.menu.c.id == mi.fk_menu).first()
        need_to_save_menu = False
        first_mi = None
        if menu.fk_default_item == mi.id:
            need_to_save_menu = True
            if first_mi == None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi == None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item = first_mi.id
        if menu.fk_default_item_WOL == mi.id:
            need_to_save_menu = True
            if first_mi == None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi == None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item_WOL = first_mi.id
        if need_to_save_menu:
            session.save_or_update(menu)
            session.flush()

        session.delete(bsim)
        session.flush()
        session.delete(mi)
        session.flush()

        session.close()
        return [True]

    def getMenuItemByUUID(self, mi_uuid, session = None):
        session_need_close = False
        if session == None:
            session_need_close = True
            session = create_session()
        ims = session.query(ImagingServer).select_from(self.menu_item \
                .outerjoin(self.target, self.target.c.fk_menu == self.menu_item.c.fk_menu) \
                .outerjoin(self.imaging_server, or_(
                    self.target.c.fk_entity == self.imaging_server.c.fk_entity, \
                    self.imaging_server.c.fk_default_menu == self.menu_item.c.fk_menu \
                )) \
            ).filter(self.menu_item.c.id == uuid2id(mi_uuid)).first()
        lang = ims.fk_language
        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        # we don't need the i18n trick for the menu name here
        mi = session.query(MenuItem).add_entity(BootService).add_entity(Image).add_entity(Menu)
        mi = mi.add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2)
        mi = mi.select_from(self.menu_item \
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu) \
                .outerjoin(self.boot_service_in_menu) \
                .outerjoin(self.boot_service) \
                .outerjoin(I18n1, and_(self.boot_service.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                .outerjoin(I18n2, and_(self.boot_service.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
                .outerjoin(self.image_in_menu) \
                .outerjoin(self.image) \
        )
        mi = mi.filter(self.menu_item.c.id == uuid2id(mi_uuid)).first()
        mi = self.__mergeBootServiceOrImageInMenuItem(mi)
        if hasattr(mi, 'boot_service'):
            local = self.isLocalBootService(mi_uuid, session)
            setattr(mi.boot_service, 'is_local', local)
        if session_need_close:
            session.close()
        return mi

    ######################
    def __PossibleImages(self, session, target_uuid, is_master, filt):
        q = session.query(Image).add_column(self.image.c.id)
        q = q.select_from(self.image.join(self.image_on_imaging_server).join(self.imaging_server).join(self.entity).join(self.target, self.target.c.fk_entity == self.entity.c.id).join(self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id).join(self.imaging_log, self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log))
        q = q.filter(self.target.c.uuid == target_uuid) # , or_(self.image.c.is_master == True, and_(self.image.c.is_master == False, )))
        if filt != '':
            q = q.filter(or_(self.image.c.desc.like('%'+filt+'%'), self.image.c.name.like('%'+filt+'%')))
        if is_master == P2IIK.IS_MASTER_ONLY:
            q = q.filter(self.image.c.is_master == True)
        elif is_master == P2IIK.IS_IMAGE_ONLY:
            q = q.filter(and_(self.image.c.is_master == False, self.target.c.id == self.imaging_log.c.fk_target))
        elif is_master == P2IIK.IS_BOTH:
            pass

        return q

    def __EntityImages(self, session, loc_id, filt):
        q = session.query(Image).add_column(self.image.c.id)
        q = q.select_from(self.image.join(self.image_on_imaging_server).join(self.imaging_server).join(self.entity))
        q = q.filter(and_(self.entity.c.uuid == loc_id, self.image.c.is_master == True, or_(self.image.c.name.like('%'+filt+'%'), self.image.c.desc.like('%'+filt+'%'))))
        return q

    def __PossibleImageAndMenuItem(self, session, bs_ids, menu_id):
        q = session.query(Image).add_entity(MenuItem)
        q = q.filter(and_(
            self.image_in_menu.c.fk_image == self.image.c.id,
            self.image_in_menu.c.fk_menuitem == self.menu_item.c.id,
            self.menu_item.c.fk_menu == menu_id,
            self.image.c.id.in_(bs_ids)
        )).all()
        return q

    def getPossibleImagesOrMaster(self, target_uuid, target_type, is_master, start, end, filt):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid)
        q1 = self.__PossibleImages(session, target_uuid, is_master, filt)
        q1 = q1.group_by(self.image.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end)-int(start))
        else:
            q1 = q1.all()
        bs_ids = map(lambda bs:bs[1], q1)
        q2 = self.__PossibleImageAndMenuItem(session, bs_ids, menu.id)

        im_ids = map(lambda im:im[0].id, q1)
        q3 = session.query(Target).add_entity(MasteredOn).select_from(self.target.join(self.imaging_log).join(self.mastered_on)).filter(self.mastered_on.c.fk_image.in_(im_ids)).all()
        session.close()

        q = self.__mergeMenuItemInImage(q1, q2, q3)

        if is_master == P2IIK.IS_MASTER_ONLY and target_type == P2IT.COMPUTER:
            profile = ComputerProfileManager().getComputersProfile(target_uuid)
            if profile != None:
                puuid = profile.id
                menu = self.getTargetsMenuTUUID(puuid)
                q1 = self.__PossibleImages(session, puuid, is_master, filt)
                q1 = q1.group_by(self.image.c.id)
                q1 = q1.all()
                bs_ids = map(lambda bs:bs[1], q1)
                q2 = self.__PossibleImageAndMenuItem(session, bs_ids, menu.id)

                in_profile = {}
                for im, mi in q2:
                    if mi != None:
                        in_profile[im.id] = mi

                ret = []
                for i in q:
                    if in_profile.has_key(i.id):
                        setattr(i, 'read_only', True)
                        setattr(i, 'menu_item', in_profile[i.id])
                    ret.append(i)
                q = ret
        return q

    def canRemoveFromMenu(self, image_uuid):
        session = create_session()
        mis = session.query(MenuItem).select_from(self.menu_item \
                .join(self.image_in_menu, self.menu_item.c.id == self.image_in_menu.c.fk_menuitem) \
                .join(self.image, self.image.c.id == self.image_in_menu.c.fk_image) \
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu) \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
        )
        mis = mis.filter(and_(self.image.c.id == uuid2id(image_uuid), self.target.c.type.in_((P2IT.COMPUTER, P2IT.PROFILE)))).group_by(self.menu_item.c.id).all()

        for mi in mis:
            menu = session.query(Menu).filter(self.menu.c.id == mi.fk_menu).first()
            first_mi = None
            if menu.fk_default_item == mi.id:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi == None:
                    session.close()
                    return False
            if menu.fk_default_item_WOL == mi.id:
                if first_mi == None:
                    first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi == None:
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
        il.detail = 'Image %s has been removed from Imaging Server by %s'%(image_uuid, '')
        il.fk_imaging_log_state = 8

        q = session.query(MasteredOn).add_entity(ImageOnImagingServer).add_entity(Image).add_column(self.imaging_log.c.fk_target) \
                .select_from(self.mastered_on \
                    .join(self.image, self.mastered_on.c.fk_image == self.image.c.id) \
                    .join(self.image_on_imaging_server, self.image_on_imaging_server.c.fk_image == self.image.c.id) \
                    .join(self.imaging_log, self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log) \
                ).filter(self.image.c.id == image_id).first()

        mo, iois, image, target_id = q
        il.fk_target = target_id

        # delete PostInstallScriptInImage if exists
        q = session.query(PostInstallScriptInImage).filter(self.post_install_script_in_image.c.fk_image == image_id).first()
        if q:
            session.delete(q)

        # TODO!
        # delete ImageInMenu and MenuItem if exists for all targets and put the synchro state flag to TODO
        q = session.query(ImageInMenu).add_entity(MenuItem).add_entity(Target)
        q = q.select_from(self.menu_item \
                .join(self.image_in_menu, self.menu_item.c.id == self.image_in_menu.c.fk_menuitem) \
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu) \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
        ).filter(self.image_in_menu.c.fk_image == image_id).all()
        targets = {P2IT.COMPUTER:[], P2IT.PROFILE:[]}
        for iim, mi, target in q:
            targets[target.type].append(target.uuid)
            session.delete(iim)
            session.delete(mi)

        for i in (P2IT.COMPUTER, P2IT.PROFILE):
            if len(targets[i]) > 0:
                self.changeTargetsSynchroState(targets[i], i, P2ISS.TODO)

        session.save(il)
        session.delete(mo)
        session.delete(iois)
        session.flush()
        session.delete(image)

        return True

#        mo = session.query(MasteredOn).filter(self.mastered_on.c.fk_image == image_id).first()
#        iois = session.query(ImageOnImagingServer).filter(self.image_on_imaging_server.c.fk_image == image_id).first()
#        image = session.query(Image).filter(self.image.c.id == image_id).first()

    def countPossibleImagesOrMaster(self, target_uuid, type, filt):
        session = create_session()
        q = self.__PossibleImages(session, target_uuid, type, filt)
        q = q.count()
        session.close()
        return q

    def getPossibleImages(self, target_uuid, target_type, start, end, filt):
        return self.getPossibleImagesOrMaster(target_uuid, target_type, P2IIK.IS_IMAGE_ONLY, start, end, filt)

    def getPossibleMasters(self, target_uuid, target_type, start, end, filt):
        return self.getPossibleImagesOrMaster(target_uuid, target_type, P2IIK.IS_MASTER_ONLY, start, end, filt)

    def getEntityMasters(self, loc_id, start, end, filt):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id)
        if menu == None:
            raise "%s:Entity does not have a default menu" % (P2ERR.ERR_ENTITY_HAS_NO_DEFAULT_MENU)
        q1 = self.__EntityImages(session, loc_id, filt)
        q1 = q1.group_by(self.image.c.id)
        if end != -1:
            q1 = q1.offset(int(start)).limit(int(end)-int(start))
        else:
            q1 = q1.all()
        bs_ids = map(lambda bs:bs[1], q1)
        q2 = self.__PossibleImageAndMenuItem(session, bs_ids, menu.id)
        session.close()

        q = self.__mergeMenuItemInImage(q1, q2)
        return q

    def getEntityMastersByUUID(self, loc_id, uuids):
        session = create_session()
        ret = {}
        q1 = self.__EntityImages(session, loc_id, '')
        q1 = q1.filter(self.image.c.id.in_(map(lambda u:uuid2id(u), uuids))).all()

        q2 = session.query(PostInstallScript).add_column(self.post_install_script_in_image.c.fk_image).add_column(self.post_install_script_in_image.c.order)
        q2 = q2.select_from(self.post_install_script.join(self.post_install_script_in_image))
        q2 = q2.filter(self.post_install_script_in_image.c.fk_image.in_(map(lambda u:uuid2id(u), uuids))).all()
        session.close()

        im_pis = {}
        for pis, im_id, order in q2:
            if not im_pis.has_key(im_id):
                im_pis[im_id] = {}
            pis = pis.toH()
            pis['order'] = order
            im_pis[im_id][order] = pis

        for im_id in im_pis:
            h_pis = im_pis[im_id]
            orders = h_pis.keys()
            orders.sort()
            a_pis = []
            for i in orders:
                a_pis.append(h_pis[i])
            im_pis[im_id] = a_pis

        for im, im_id in q1:
            ret[id2uuid(im_id)] = im.toH()
            ret[id2uuid(im_id)]['post_install_scripts'] = im_pis[im_id]
        return ret


    def countPossibleImages(self, target_uuid, filter):
        return self.countPossibleImagesOrMaster(target_uuid, P2IIK.IS_IMAGE_ONLY, filter)

    def countPossibleMasters(self, target_uuid, filter):
        return self.countPossibleImagesOrMaster(target_uuid, P2IIK.IS_MASTER_ONLY, filter)

    def countEntityMasters(self, loc_id, filter):
        session = create_session()
        q = self.__EntityImages(session, loc_id, filter)
        q = q.count()
        session.close()
        return q

    def __addImage(self, session, item_uuid, menu, params):
        im = session.query(Image).filter(self.image.c.id == uuid2id(item_uuid)).first();
        # TODO : what do we do with im ?
        if menu == None:
            raise '%s:Please create menu before trying to put an image' % (P2ERR.ERR_TARGET_HAS_NO_MENU)

        if params.has_key('name') and not params.has_key('default_name'):
            params['default_name'] = params['name']
        mi = self.__createNewMenuItem(session, menu.id, params)
        session.flush()

        self.__addMenuDefaults(session, menu, mi, params)
        self.__addImageInMenu(session, mi.id, item_uuid)

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
        c = session.query(Image).filter(self.image.c.uuid == params['uuid']).count()
        if c != 0:
            self.logger.warn('an image with the same UUID already exists (%s)' % (params['uuid']))
            raise '%s:An image with the same UUID already exists! (%s)' % (P2ERR.ERR_IMAGE_ALREADY_EXISTS, params['uuid'])

        self.logger.error('WOOT : %s' % "a")
        # create the image item
        image = Image()
        image.name = params['name']
        image.desc = params['desc']
        image.path = params['path']
        image.uuid = params['uuid']
        image.checksum = params['checksum']
        image.size = params['size']
        image.creation_date = datetime.datetime.fromtimestamp(time.mktime(params['creation_date']))
        image.fk_creator = 1  # TOBEDONE image['']
        image.is_master = params['is_master']

        if params['state'] in self.r_nomenclatures['ImageState']:
            image.fk_state = self.r_nomenclatures['ImageState'][params['state']]
        elif params['state'] in self.nomenclatures['ImageState']:
            image.fk_state = params['state']
        else:  # this state is unknown!
            self.logger.warn("don't know that imaging log state %s" % (params['state']))
            image.fk_state = 1  # the UNKNOWN entry

        session.save(image)
        session.flush()

        # fill the imaging_log
        #   there is way to much fields!
        imaging_log = ImagingLog()
        imaging_log.timestamp = datetime.datetime.fromtimestamp(time.mktime(params['creation_date']))
        imaging_log.detail = params['desc']
        imaging_log.fk_imaging_log_level = P2ILL.LOG_INFO
        imaging_log.fk_imaging_log_state = 1  # done
        target = session.query(Target).filter(self.target.c.uuid == computer_uuid).first()
        imaging_log.fk_target = target.id
        session.save(imaging_log)
        session.flush()

        # Mastered on
        mastered_on = MasteredOn()
        mastered_on.fk_image = image.id
        mastered_on.fk_imaging_log = imaging_log.id
        session.save(mastered_on)

        # link the image to the imaging_server
        ims = session.query(ImagingServer).filter(self.imaging_server.c.packageserver_uuid == imaging_server_uuid).first()
        ioims = ImageOnImagingServer()
        ioims.fk_image = image.id
        ioims.fk_imaging_server = ims.id
        session.save(ioims)

        # link the image to the machine
        # DONT PUT IN THE MENU BY DEFAULT
        # self.addImageToTarget(id2uuid(image.id), computer_uuid, params)
        session.flush()
        session.close()
        return True

    def logClientAction(self, loc_uuid, item_uuid, log):
        session = create_session()
        imaging_log = ImagingLog()
        imaging_log.timestamp = datetime.datetime.fromtimestamp(time.mktime(time.localtime()))
        imaging_log.detail = log['detail']
        imaging_log.fk_imaging_log_level = log['level']
        if self.r_nomenclatures['ImagingLogState'].has_key(log['state']):
            imaging_log.fk_imaging_log_state = self.r_nomenclatures['ImagingLogState'][log['state']]
        elif self.nomenclatures['ImagingLogState'].has_key(log['state']):
            imaging_log.fk_imaging_log_state = log['state']
        else: # this state is unknown!
            self.logger.warn("don't know that imaging log state %s"%(log['state']))
            imaging_log.fk_imaging_log_state = 1 # the UNKNOWN entry

        target = session.query(Target).filter(self.target.c.uuid == item_uuid).first()
        imaging_log.fk_target = target.id
        session.save(imaging_log)
        session.flush()
        session.close()
        return True

    def addImageToEntity(self, item_uuid, loc_id, params):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id, session)
        ret = self.__addImage(session, item_uuid, menu, params)
        session.close()
        return ret

    def __editImage(self, session, item_uuid, menu, mi, params):
        im = session.query(Image).filter(self.image.c.id == uuid2id(item_uuid)).first();
        # TODO : what do we do with im ?
        if menu == None:
            raise '%s:Please create menu before trying to put an image' % (P2ERR.ERR_TARGET_HAS_NO_MENU)

        mi = self.__fillMenuItem(session, mi, menu.id, params)
        session.flush()

        self.__editMenuDefaults(session, menu, mi, params)

        session.flush()
        return None

    def __getImageMenuItem(self, session, item_uuid, target_uuid):
        mi = session.query(MenuItem).select_from(self.menu_item \
                .join(self.image_in_menu, self.image_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                .join(self.image, self.image_in_menu.c.fk_image == self.image.c.id) \
                .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                .join(self.target, self.menu.c.id == self.target.c.fk_menu) \
        )
        mi = mi.filter(and_(self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid)).first()
        return mi

    def __getImageMenuItem4Entity(self, session, item_uuid, loc_id):
        """
        given an item ID and an entity ID, get I don't now what
        TODO : don't see what has to be done here ...
        """
        j = self.menu_item.join(self.image_in_menu).join(self.image).join(self.menu).join(self.imaging_server)
        f = and_(
            self.image.c.id == uuid2id(item_uuid),
            self.menu.c.id == self.imaging_server.c.fk_default_menu,
            self.entity.c.uuid == loc_id)
        mi = session.query(MenuItem).select_from(j)
        mi = mi.filter(f)
        mi = mi.first()
        return mi

    def editImageToTarget(self, item_uuid, target_uuid, params):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid, session)
        mi = self.__getImageMenuItem(session, item_uuid, target_uuid)
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
        return session.query(Image).add_entity(Target).select_from(self.image \
                .join(self.image_in_menu, self.image.c.id == self.image_in_menu.c.fk_image) \
                .join(self.menu_item, self.menu_item.c.id == self.image_in_menu.c.fk_menuitem) \
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu) \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
        )

    def isImageInMenu(self, item_uuid, target_uuid = None, target_type = None):
        session = create_session()
        q = self.__queryImageInMenu(session)
        if target_uuid != None:
            q = q.filter(and_(self.target.c.uuid == target_uuid, self.target.c.type == target_type, self.image.c.id == uuid2id(item_uuid)))
        else:
            q = q.filter(self.image.c.id == uuid2id(item_uuid))
        q = q.count()
        return (q > 0)

    def areImagesUsed(self, images):
        session = create_session()
        ret = {}
        for item_uuid, target_uuid, target_type in images:
            q = self.__queryImageInMenu(session)
            if target_uuid != None and target_type != None:
                q = q.filter(and_(self.image.c.id == uuid2id(item_uuid), or_(self.target.c.uuid != target_uuid, self.target.c.type != target_type))).all()
            else:
                q = q.filter(self.image.c.id == uuid2id(item_uuid)).all()
            ret1 = []
            for im, target in q:
                target = target.toH()
                ret1.append([target['uuid'], target['type'], target['name']])
            ret[item_uuid] = ret1
        return ret

    def __editImage__grepAndStartOrderAtZero(self, post_install_scripts):
        ret = {}
        inverted = {}
        for pisid in post_install_scripts:
            if post_install_scripts[pisid] != 'None':
                inverted[post_install_scripts[pisid]] = pisid
        i = 0
        my_keys = inverted.keys()
        my_keys.sort()
        for order in my_keys:
            ret[inverted[order]] = i
            i += 1
        return ret

    def editImage(self, item_uuid, params):

        session = create_session()
        im = session.query(Image).filter(self.image.c.id == uuid2id(item_uuid)).first()
        if im == None:
            raise "%s:Cant find the image you are trying to edit." % (P2ERR.ERR_DEFAULT)
        need_to_be_save = False
        for p in ('name', 'desc', 'is_master', 'size'):
            if p in params and params[p] != getattr(im, p):
                need_to_be_save = True
                setattr(im, p, params[p])
        if 'state' in params :
            if params['state'] in self.r_nomenclatures['ImageState']:
                im.fk_state = self.r_nomenclatures['ImageState'][params['state']]
            elif params['state'] in self.nomenclatures['ImageState']:
                im.fk_state = params['state']
            else:  # this state is unknown!
                self.logger.warn("don't know that imaging log state %s" % (params['state']))
                im.fk_state = 1  # the UNKNOWN entry

        if 'is_master' in params:
            if params['is_master'] and 'post_install_scripts' in params or not params['is_master']:
                pisiis = session.query(PostInstallScriptInImage).filter(self.post_install_script_in_image.c.fk_image == uuid2id(item_uuid)).all()
                for p in pisiis:
                    session.delete(p)
                session.flush()

            if params['is_master'] and 'post_install_scripts' in params:
                post_install_scripts = self.__editImage__grepAndStartOrderAtZero(params['post_install_scripts'])
                for pis in post_install_scripts:
                    pisii = PostInstallScriptInImage()
                    pisii.fk_image = uuid2id(item_uuid)
                    pisii.fk_post_install_script = uuid2id(pis)
                    pisii.order = post_install_scripts[pis]
                    session.save(pisii)

        if need_to_be_save:
            session.save_or_update(im)
        session.flush()
        session.close()
        return im.id

    def delImageToTarget(self, item_uuid, target_uuid):
        session = create_session()
        mi = session.query(MenuItem).select_from(self.menu_item \
                .join(self.image_in_menu, self.menu_item.c.id == self.image_in_menu.c.fk_menuitem) \
                .join(self.image, self.image.c.id == self.image_in_menu.c.fk_image) \
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu) \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
        )
        mi = mi.filter(and_(self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid)).first()
        iim = session.query(ImageInMenu).select_from(self.image_in_menu \
                .join(self.menu_item, self.menu_item.c.id == self.image_in_menu.c.fk_menuitem) \
                .join(self.image, self.image.c.id == self.image_in_menu.c.fk_image) \
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu) \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
        )
        iim = iim.filter(and_(self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid)).first()

        menu = session.query(Menu).filter(self.menu.c.id == mi.fk_menu).first()
        need_to_save_menu = False
        first_mi = None
        if menu.fk_default_item == mi.id:
            need_to_save_menu = True
            if first_mi == None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi == None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item = first_mi.id
        if menu.fk_default_item_WOL == mi.id:
            need_to_save_menu = True
            if first_mi == None:
                first_mi = self.__getFirstMenuItem(session, menu.id, mi.id)
                if first_mi == None:
                    session.close()
                    return [False, "cant find any other mi"]
            menu.fk_default_item_WOL = first_mi.id
        if need_to_save_menu:
            session.save_or_update(menu)
            session.flush()

        session.delete(iim)
        session.delete(mi)
        # TODO when it's not a master and the computer is the only one, what should we do with the image?
        session.flush()

        session.close()
        return None

    ######################
    def __TargetImagesQuery(self, session, target_uuid, type, filter):
        q = session.query(Image).add_entity(MenuItem)
        q = q.select_from(self.image.join(self.image_on_imaging_server).join(self.imaging_server).join(self.entity).join(self.target).join(self.image_in_menu).join(self.menu_item))
        q = q.filter(and_(self.target.c.uuid == target_uuid, or_(self.image.c.desc.like('%'+filter+'%'), self.image.c.name.like('%'+filter+'%'))))
        return q

    def __TargetImagesNoMaster(self, session, target_uuid, type, filter):
        q = self.__TargetImagesQuery(session, target_uuid, type, filter)
        q.filter(self.image.c.is_master == False)
        return q

    def __TargetImagesIsMaster(self, session, target_uuid, type, filter):
        q = self.__TargetImagesQuery(session, target_uuid, type, filter)
        q.filter(self.image.c.is_master == True)
        return q

    ##
    def __ImagesInEntityQuery(self, session, entity_uuid, filter):
        q = session.query(Image).add_entity(MenuItem)
        q = q.select_from(self.image.join(self.image_on_imaging_server).join(self.imaging_server).join(self.entity).outerjoin(self.image_in_menu).outerjoin(self.menu_item))
        q = q.filter(and_(self.entity.c.uuid == entity_uuid, or_(self.image.c.desc.like('%'+filter+'%'), self.image.c.name.like('%'+filter+'%'))))
        return q

    def __ImagesInEntityNoMaster(self, session, target_uuid, type, filter):
        q = self.__ImagesInEntityQuery(session, target_uuid, type, filter)
        q.filter(self.image.c.is_master == False)
        return q

    def __ImagesInEntityIsMaster(self, session, target_uuid, type, filter):
        q = self.__ImagesInEntityQuery(session, target_uuid, type, filter)
        q.filter(self.image.c.is_master == False)
        return q

    def getTargetImages(self, target_uuid, target_type, start = 0, end = -1, filter = ''):
        session = create_session()
        q1 = session.query(Image).add_entity(MenuItem) \
                .select_from(self.image \
                    .outerjoin(self.image_in_menu, self.image_in_menu.c.fk_image == self.image.c.id) \
                    .outerjoin(self.menu_item, self.image_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                    .join(self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id) \
                    .join(self.imaging_log, self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log) \
                    .join(self.target, self.target.c.id == self.imaging_log.c.fk_target) \
                ).filter(and_(self.target.c.uuid == target_uuid, self.target.c.type == target_type)).all()
        images_ids = map(lambda r:r[0].id, q1)

        ims = session.query(ImagingServer).select_from(self.imaging_server.join(self.target, self.target.c.fk_entity == self.imaging_server.c.fk_entity)) \
                .filter(and_(self.target.c.uuid == target_uuid, self.target.c.type == target_type)).first()
        lang = ims.fk_language

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q2 = session.query(PostInstallScript).add_column(self.post_install_script_in_image.c.order).add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2).add_column(self.image.c.id) \
                .select_from(self.image \
                    .join(self.post_install_script_in_image, self.post_install_script_in_image.c.fk_image == self.image.c.id) \
                    .join(self.post_install_script, self.post_install_script_in_image.c.fk_post_install_script == self.post_install_script.c.id) \
                    .outerjoin(I18n1, and_(self.post_install_script.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                    .outerjoin(I18n2, and_(self.post_install_script.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
                ).filter(self.image.c.id.in_(images_ids)).all()
        q2 = self.__mergePostInstallScriptI18n(q2)
        h_pis_by_imageid = {}
        for pis in q2:
            if not h_pis_by_imageid.has_key(pis.image_id):
                h_pis_by_imageid[pis.image_id] = []
            h_pis_by_imageid[pis.image_id].append(pis)

        ret = {}
        for im, mi in q1:
            q = self.__mergeMenuItemInImage([(im, im.id)], [[im, mi]])
            q = q[0]
            setattr(q, 'post_install_scripts', h_pis_by_imageid[im.id])
            ret[mi.order] = q

        ret1 = []
        if end != -1:
            for i in range(start, end):
                if ret.has_key(i):
                    ret1.append(ret[i])
        else:
            ret1 = ret

        return ret1

    def countTargetImages(self, target_uuid, target_type, filter):
        session = create_session()
        q1 = session.query(Image) \
                .select_from(self.image \
                    .join(self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id) \
                    .join(self.imaging_log, self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log) \
                    .join(self.target, self.target.c.id == self.imaging_log.c.fk_target) \
                ).filter(and_(self.target.c.uuid == target_uuid, self.target.c.type == target_type)).count()
        return q1

    def __mergePostInstallScriptI18n(self, postinstallscript_list):
        ret = []
        for postinstallscript, order, name_i18n, desc_i18n, im_id in postinstallscript_list:
            if name_i18n != None:
                setattr(postinstallscript, 'default_name', name_i18n.label)
            if desc_i18n != None:
                setattr(postinstallscript, 'default_desc', desc_i18n.label)
            setattr(postinstallscript, 'image_id', im_id)
            setattr(postinstallscript, 'order', order)
            ret.append(postinstallscript)
        return ret

    def getTargetImage(self, uuid, target_type, image_uuid):
        session = create_session()
        q1 = session.query(Image).add_entity(MenuItem) \
                .select_from(self.image \
                    .outerjoin(self.image_in_menu, self.image_in_menu.c.fk_image == self.image.c.id) \
                    .outerjoin(self.menu_item, self.image_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                    .join(self.mastered_on, self.mastered_on.c.fk_image == self.image.c.id) \
                    .join(self.imaging_log, self.imaging_log.c.id == self.mastered_on.c.fk_imaging_log) \
                    .join(self.target, self.target.c.id == self.imaging_log.c.fk_target) \
                ).filter(and_(self.image.c.id == uuid2id(image_uuid), self.target.c.uuid == uuid, self.target.c.type == target_type)).first()
        if q1 == None:
            raise Exception("cant get the image %s for target %s"%(image_uuid, uuid))

        ims = session.query(ImagingServer).select_from(self.imaging_server.join(self.target, self.target.c.fk_entity == self.imaging_server.c.fk_entity)) \
                .filter(and_(self.target.c.uuid == uuid, self.target.c.type == target_type)).first()
        lang = ims.fk_language

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q2 = session.query(PostInstallScript).add_column(self.post_install_script_in_image.c.order).add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2).add_column(self.image.c.id) \
                .select_from(self.image \
                    .join(self.post_install_script_in_image, self.post_install_script_in_image.c.fk_image == self.image.c.id) \
                    .join(self.post_install_script, self.post_install_script_in_image.c.fk_post_install_script == self.post_install_script.c.id) \
                    .outerjoin(I18n1, and_(self.post_install_script.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                    .outerjoin(I18n2, and_(self.post_install_script.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
                ).filter(self.image.c.id == uuid2id(image_uuid)).all()
        q2 = self.__mergePostInstallScriptI18n(q2)
        im, mi = q1
        q = self.__mergeMenuItemInImage([(im, im.id)], [q1])
        q = q[0]
        setattr(q, 'post_install_scripts', q2)
        return q

    ######################
    def getBootServicesOnTargetById(self, target_id, start, end, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return []
        menu_items = self.getMenuContent(menu.id, P2IM.BOOTSERVICE, start, end, filter)
        return menu_items

    def countBootServicesOnTargetById(self, target_id, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return 0
        count_items = self.countMenuContent(menu.id, P2IM.BOOTSERVICE, filter)
        return count_items

    def isLocalBootService(self, mi_uuid, session = None):
        """
        Check if MenuItem mi is a local boot service owned by an imaging
        server, or a global boot service.
        """
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()

        mi = session.query(MenuItem).add_entity(Entity)
        mi = mi.select_from(self.menu_item \
                .join(self.menu, self.menu.c.id == self.menu_item.c.fk_menu) \
                .outerjoin(self.target) \
                .outerjoin(self.imaging_server, self.imaging_server.c.fk_default_menu == self.menu.c.id) \
                .outerjoin(self.entity, or_(self.entity.c.id == self.target.c.fk_entity, self.entity.c.id == self.imaging_server.c.fk_entity)))
        mi = mi.filter(and_(self.menu_item.c.id == uuid2id(mi_uuid), self.entity.c.id != None)).first()
        loc_id = mi[1].uuid

        q = session.query(BootService).add_entity(BootServiceOnImagingServer)
        q = q.select_from(self.boot_service \
                .join(self.boot_service_in_menu).join(self.menu_item) \
                .outerjoin(self.boot_service_on_imaging_server, self.boot_service.c.id == self.boot_service_on_imaging_server.c.fk_boot_service) \
                .outerjoin(self.imaging_server, self.imaging_server.c.id == self.boot_service_on_imaging_server.c.fk_imaging_server) \
                .outerjoin(self.entity))
        q = q.filter(or_(self.boot_service_on_imaging_server.c.fk_boot_service == None, self.entity.c.uuid == loc_id))
        q = q.filter(self.menu_item.c.id == uuid2id(mi_uuid))
        q = q.first()

        ret = (q[1] != None)

        if session_need_to_close:
            session.close()
        return ret

    ######################
    def getBootMenu(self, target_id, type, start, end, filter):
        menu_items = []
        if type == P2IT.COMPUTER:
            profile = ComputerProfileManager().getComputersProfile(target_id)
            if profile != None:
                # this should be the profile uuid!
                menu_root = self.getTargetsMenuTUUID(profile.id)
                menu_items = self.getMenuContent(menu_root.id, P2IM.ALL, start, end, filter)

        menu = self.getTargetsMenuTUUID(target_id)

        if menu == None:
            return menu_items

        root_len = len(menu_items)
        for i in range(0, len(menu_items)):
            setattr(menu_items[i], 'read_only', True)

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

    def countBootMenu(self, target_id, type, filter):
        count_items = 0
        if type == P2IT.COMPUTER:
            profile = ComputerProfileManager().getComputersProfile(target_id)
            if profile != None:
                # this should be the profile uuid!
                menu_root = self.getTargetsMenuTUUID(profile.id)
                count_items = self.countMenuContent(menu_root.id, P2IM.ALL, filter)

        menu = self.getTargetsMenuTUUID(target_id)

        if menu == None:
            return count_items

        count_items += self.countMenuContent(menu.id, P2IM.ALL, filter)
        return count_items

    def getEntityBootMenu(self, loc_id, start, end, filter):
        menu = self.getEntityDefaultMenu(loc_id)
        if menu == None:
            return []
        menu_items = self.getMenuContent(menu.id, P2IM.ALL, start, end, filter)
        return menu_items

    def countEntityBootMenu(self, loc_id, filter):
        menu = self.getEntityDefaultMenu(loc_id)
        if menu == None:
            return 0
        count_items = self.countMenuContent(menu.id, P2IM.ALL, filter)
        return count_items

    ######################
    def __moveItemInMenu(self, menu, mi_uuid, reverse = False):
        session = create_session()
        mis = self.getMenuContent(menu.id, P2IM.ALL, 0, -1, '', session)
        if reverse:
            mis.sort(lambda x,y: cmp(y.order, x.order))
        move = False
        mod_mi = [None, None]
        for mi in mis:
            if move:
                move = False
                mod_mi[1] = mi
            if str(mi.id) == str(uuid2id(mi_uuid)):
                move = True
                mod_mi[0] = mi
        if mod_mi[0] != None and mod_mi[1] != None:
            ord = mod_mi[0].order
            mod_mi[0].order = mod_mi[1].order
            mod_mi[1].order = ord
            session.save_or_update(mod_mi[0])
            session.save_or_update(mod_mi[1])
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
        q = session.query(Target).add_entity(Image).select_from(self.target \
                .join(self.imaging_server, self.target.c.fk_entity == self.imaging_server.c.fk_entity) \
                .join(self.entity, self.entity.c.id == self.target.c.fk_entity) \
                .outerjoin(self.imaging_log, self.imaging_log.c.fk_target == self.target.c.id) \
                .outerjoin(self.mastered_on, self.mastered_on.c.fk_imaging_log == self.imaging_log.c.id) \
                .outerjoin(self.image, self.mastered_on.c.fk_image == self.image.c.id) \
        ).filter(and_(self.entity.c.uuid == location, self.target.c.type.in_((P2IT.COMPUTER, P2IT.COMPUTER_IN_PROFILE))))
        q = q.group_by().all()
        im_total = set()
        im_rescue = set()
        for t, i in q:
            # Targets set
            im_total.add(t)
            if i != None and not i.is_master:
                # Targets set with a rescue image
                im_rescue.add(t)

        im_master = session.query(Image).select_from(self.image \
                .join(self.image_on_imaging_server, self.image_on_imaging_server.c.fk_image == self.image.c.id) \
                .join(self.imaging_server, self.image_on_imaging_server.c.fk_imaging_server == self.imaging_server.c.id) \
                .join(self.entity, self.entity.c.id == self.imaging_server.c.fk_entity) \
        ).filter(and_(self.entity.c.uuid == location, self.image.c.is_master == 1)).count()

        return {'total'  : len(im_total),
                'rescue' : len(im_rescue),
                'master' : im_master}


    def countImagingServerByPackageServerUUID(self, uuid):
        session = create_session()
        q = session.query(ImagingServer).filter(self.imaging_server.c.packageserver_uuid == uuid).count()
        session.close()
        return q

    def getImageAndImagingServer(self, uuid, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        q = session.query(Image).add_entity(ImagingServer).select_from(self.imaging_server \
                .join(self.image_on_imaging_server) \
                .join(self.image) \
        ).filter(self.image.c.id == uuid2id(uuid)).first()

        if session_need_to_close:
            session.close()
        return q

    def getImageImagingServer(self, uuid, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        q = session.query(ImagingServer).select_from(self.imaging_server \
                .join(self.image_on_imaging_server) \
                .join(self.image) \
        ).filter(self.image.c.id == uuid2id(uuid)).first()

        if session_need_to_close:
            session.close()
        return q

    def getImagingServerByUUID(self, uuid, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        q = session.query(ImagingServer).filter(self.imaging_server.c.id == uuid2id(uuid)).first()
        if session_need_to_close:
            session.close()
        return q

    def getImagingServerByEntityUUID(self, uuid, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        q = session.query(ImagingServer).select_from(self.imaging_server.join(self.entity)).filter(self.entity.c.uuid == uuid).first()
        if session_need_to_close:
            session.close()
        return q

    def getImagingServerByPackageServerUUID(self, uuid, with_entity = False):
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
        ims.fk_default_menu = 1  # the default "subscribe" menu, which is shown when an unknown client boots
        ims.associated = 0  # we are registered, but not yet associated
        ims.fk_language = 1  # default on English
        self.imagingServer_lang[uuid] = 1
        session.save(ims)
        session.flush()
        session.close()
        return ims.id

    def getEntityByUUID(self, loc_id, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        ret = session.query(Entity).filter(self.entity.c.uuid == loc_id).first()
        if session_need_to_close:
            session.close()
        return ret

    def getMenusByID(self, menus_id, session):
        q = session.query(Menu).filter(self.menu.c.id.in_(menus_id)).all()
        return q

    def getMenuByUUID(self, menu_uuid, session = None):
        # dont need the i18n trick here, we just want to modify some menu internals
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        q = session.query(Menu).filter(self.menu.c.id == uuid2id(menu_uuid)).first()
        if session_need_to_close:
            session.close()
        return q

    def getProtocolByUUID(self, uuid, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        q = session.query(Protocol).filter(self.protocol.c.id == uuid2id(uuid)).first()
        if session_need_to_close:
            session.close()
        return q

    def getProtocolByLabel(self, label, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        q = session.query(Protocol).filter(self.protocol.c.label == label).first()
        if session_need_to_close:
            session.close()
        return q

    def modifyMenus(self, menus_id, params):
        session = create_session()
        menus = self.getMenusByID(menus_id, session)
        for m in menus:
            for p in ['default_name', 'timeout', 'background_uri', 'message', 'protocol', 'default_item', 'default_item_WOL']:
                if params.has_key(p):
                    setattr(m, p, params[p])
        session.flush()
        session.close()
        return True

    def __modifyMenu(self, menu_uuid, params, session = None):
        """
        Modify menu in database according to params dict content
        """
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        menu = self.getMenuByUUID(menu_uuid, session)
        need_to_be_save = False
        # FIXME: could be factorized
        if params.has_key('default_name') and menu.default_name != params['default_name']:
            need_to_be_save = True
            menu.default_name = params['default_name']
            menu.fk_name = 1
        if params.has_key('timeout') and menu.timeout != params['timeout']:
            need_to_be_save = True
            menu.timeout = params['timeout']

        for option in ['hidden_menu', 'bootcli', 'dont_check_disk_size',
                       'update_nt_boot', 'disklesscli']:
            if option in params and params[option]:
                params[option] = 1
            else:
                params[option] = 0
            if getattr(menu, option) != params[option]:
                need_to_be_save = True
                setattr(menu, option, params[option])
        if params.has_key('background_uri') and menu.background_uri != params['background_uri']:
            need_to_be_save = True
            menu.background_uri = params['background_uri']
        if params.has_key('message') and menu.message != params['message']:
            need_to_be_save = True
            menu.message = params['message']

        if params.has_key('protocol'):
            proto = self.getProtocolByUUID(params['protocol'], session)
            if proto and menu.fk_protocol != proto.id:
                need_to_be_save = True
                menu.fk_protocol = proto.id

        if need_to_be_save:
            session.save_or_update(menu)
        if session_need_to_close:
            session.flush()
            session.close()
        return menu

    def modifyMenu(self, menu_uuid, params):
        self.__modifyMenu(menu_uuid, params)
        return True

    def __getDefaultMenu(self, session, lang = 1):
        ret = session.query(Menu).add_column(self.internationalization.c.label).select_from(self.menu \
                .outerjoin(self.internationalization, and_(self.internationalization.c.id == self.menu.c.fk_name, self.internationalization.c.fk_language == lang)) \
            ).filter(self.menu.c.id == 1).first()
        if ret[1] != None and ret[1] != 'NOTTRANSLATED':
            ret[0].default_name = ret[1]
        return ret[0]

    def __getDefaultMenuItem(self, session, menu_id = 1):
        default_item = session.query(MenuItem).filter(and_(self.menu.c.id == menu_id, self.menu.c.fk_default_item == self.menu_item.c.id)).first()
        default_item_WOL = session.query(MenuItem).filter(and_(self.menu.c.id == menu_id, self.menu.c.fk_default_item_WOL == self.menu_item.c.id)).first()
        return [default_item, default_item_WOL]

    def __getDefaultMenuMenuItems(self, session):
        return self.__getMenuItemsInMenu(session, 1)

    def __getMenuItemsInMenu(self, session, menu_id):
        return session.query(MenuItem).add_entity(BootServiceInMenu).select_from(self.menu_item.join(self.boot_service_in_menu)).filter(self.menu_item.c.fk_menu == menu_id).all()

    def __duplicateDefaultMenuItem(self, session, loc_id = None, p_id = None):
        # warning ! can't be an image !
        default_list = []
        if p_id != None:
            # get the profile menu
            menu = self.getTargetMenu(p_id, P2IT.PROFILE, session)
            default_list = self.__getMenuItemsInMenu(session, menu.id)
            mi = self.__getDefaultMenuItem(session, menu.id)
        elif loc_id != None:
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
        for default_menu_item, default_bsim in default_list:
            menu_item = MenuItem()
            menu_item.order = default_menu_item.order
            menu_item.hidden = default_menu_item.hidden
            menu_item.hidden_WOL = default_menu_item.hidden_WOL
            menu_item.fk_menu = 1 # default Menu, need to be change as soon as we have the menu id!
            session.save(menu_item)
            ret.append(menu_item)
            session.flush()
            if mi[0].id == default_menu_item.id:
                mi_out[0] = menu_item.id
            if mi[1].id == default_menu_item.id:
                mi_out[1] = menu_item.id
            bsim = BootServiceInMenu()
            bsim.fk_menuitem = menu_item.id
            bsim.fk_bootservice = default_bsim.fk_bootservice
            session.save(bsim)
        session.flush()
        return [ret, mi_out]

    def __duplicateDefaultMenu(self, session, loc_id):
        lang = self.__getLocLanguage(session, loc_id)
        default_menu = self.__getDefaultMenu(session, lang)
        return self.__duplicateMenu(session, default_menu)

    def __duplicateMenu(self, session, default_menu, loc_id = None, p_id = None, sub = False):
        menu = Menu()
        menu.default_name = default_menu.default_name
        menu.fk_name = default_menu.fk_name
        menu.timeout = default_menu.timeout
        menu.background_uri = default_menu.background_uri
        menu.message = default_menu.message
        menu.fk_protocol = default_menu.fk_protocol
        menu.ethercard = default_menu.ethercard
        menu.bootcli = default_menu.bootcli
        menu.disklesscli = default_menu.disklesscli
        menu.dont_check_disk_size = default_menu.dont_check_disk_size
        if sub:
            menu_items = []
            menu.fk_default_item = default_menu.fk_default_item
            menu.fk_default_item_WOL = default_menu.fk_default_item_WOL
        elif p_id != None:
            menu_items = []
            menu.fk_default_item = None
            menu.fk_default_item_WOL = None
        else:
            menu_items, mi = self.__duplicateDefaultMenuItem(session, loc_id, p_id)
            menu.fk_default_item = mi[0]
            menu.fk_default_item_WOL = mi[1]
        menu.fk_synchrostate = 1
        session.save(menu)
        session.flush()
        for menu_item in menu_items:
            menu_item.fk_menu = menu.id
            session.save_or_update(menu_item)
        return menu

    def __createMenu(self, session, params):
        menu = Menu()
        menu.default_name = params['default_name']
        menu.timeout = params['timeout']
        menu.background_uri = params['background_uri']
        menu.message = params['message']
        if params.has_key('protocol'):
            proto = self.getProtocolByLabel(params['protocol'], session)
            if proto:
                menu.fk_protocol = proto.id
        if not menu.fk_protocol:
            proto = self.getProtocolByLabel(self.config.web_def_default_protocol, session)
            menu.fk_protocol = proto.id
        menu.fk_default_item = 0
        menu.fk_default_item_WOL = 0
        menu.fk_synchrostate = 1
        menu.fk_name = 1
        session.save(menu)
        return menu

    def __createEntity(self, session, loc_id, loc_name):
        e = Entity()
        e.name = loc_name
        e.uuid = loc_id
        session.save(e)
        return e

    def getImagingServerEntity(self, imaging_server_uuid):
        """
        Get the entity linked to that imaging server, or None if the imaging
        server doesn't exist in database or has not been associated to an
        entity.
        """
        session = create_session()
        entity = session.query(Entity).\
                 select_from(self.entity.join(self.imaging_server, self.imaging_server.c.fk_entity == self.entity.c.id)).\
                 filter(and_(self.imaging_server.c.packageserver_uuid == imaging_server_uuid, self.imaging_server.c.associated == True)).\
                 first()

        if entity == None:
            entity = session.query(Entity).\
                    select_from(self.entity.join(self.imaging_server, self.imaging_server.c.fk_entity == self.entity.c.id)).\
                    filter(and_(self.imaging_server.c.id == uuid2id(imaging_server_uuid), self.imaging_server.c.associated == True)).\
                    first()

        session.close()
        return entity

    def linkImagingServerToEntity(self, is_uuid, loc_id, loc_name):
        """
        Attach the entity loc_id, name loc_name, to the imaging server is_uuid
        """
        session = create_session()

        # checks if IS already exists
        imaging_server = self.getImagingServerByUUID(is_uuid, session)
        if imaging_server == None:
            raise Exception("%s : No server exists with that uuid (%s)" % (P2ERR.ERR_IMAGING_SERVER_DONT_EXISTS, is_uuid))

        # checks if entity is not already linked somewhere else
        potential_imaging_server_id = self.__getLinkedImagingServerForEntity(session, loc_id)
        if potential_imaging_server_id :
            raise Exception("%s : This entity is already linked to the Imaging Server %s" % (P2ERR.ERR_ENTITY_ALREADY_EXISTS, potential_imaging_server_id))

        location = self.getEntityByUUID(loc_id, session)
        if location is None: # entity do not yet exists in database, let's create it !
            location = self.__createEntity(session, loc_id, loc_name)
            session.flush()

        # create default imaging server menu
        menu = self.__duplicateDefaultMenu(session, loc_id)
        session.flush()

        imaging_server.fk_entity = location.id
        imaging_server.fk_default_menu = menu.id
        imaging_server.associated = 1
        session.save_or_update(imaging_server)
        session.flush()

        session.close()
        return True

    def __getLinkedImagingServerForEntity(self, session, loc_id):
        """
        If this entity is linked to an imaging server, returns it's uuid, if not (or if the entity do not exists), return None
        """
        q = session.query(ImagingServer). \
            select_from(self.imaging_server.join(self.entity)).\
            filter(self.imaging_server.c.associated == 1).\
            filter(self.entity.c.uuid == loc_id).\
            first()
        if q:
            return q.name
        return None

    def __AllNonLinkedImagingServer(self, session, filter):
        q = session.query(ImagingServer).filter(self.imaging_server.c.associated == 0)
        if filter and filter != '':
            q = q.filter(or_(self.imaging_server.c.name.like('%' + filter + '%'), self.imaging_server.c.url.like('%' + filter + '%'), self.imaging_server.c.uuid.like('%' + filter + '%')))
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
        q = session.query(ImagingServer).select_from(self.imaging_server.join(self.entity)).filter(self.imaging_server.c.associated == 1).filter(self.entity.c.uuid == loc_id).count()
        return (q == 1)

    def setImagingServerConfig(self, location, config):
        session = create_session()
        imaging_server = self.getImagingServerByEntityUUID(location, session)
        # modify imaging_server
        # session.save(imaging_server)
        # session.flush()
        session.close()
        return True

    def checkLanguage(self, location, language):
        session = create_session()
        imaging_server = self.getImagingServerByEntityUUID(location, session)
        lang = session.query(Language).filter(self.language.c.id == uuid2id(language)).first()
        if imaging_server.fk_language != lang.id:
            imaging_server.fk_language = lang.id
            session.save_or_update(imaging_server)
            session.flush()
        session.close()
        self.imagingServer_lang[location] = lang.id
        return True

    # Protocols
    def getAllProtocols(self):
        session = create_session()
        q = session.query(Protocol).all()
        session.close()
        return q

    ######### REGISTRATION
    def isTargetRegister(self, uuid, target_type, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()

        ret = False
        if type(uuid) == list:
            ret = {}
            q = session.query(Target).filter(and_(self.target.c.uuid.in_(uuid), self.target.c.type == target_type)).all()
            for target in q:
                ret[target.uuid] = True
            for l_uuid in uuid:
                if not ret.has_key(l_uuid):
                    ret[l_uuid] = False
        else:
            q = session.query(Target).filter(and_(self.target.c.uuid == uuid, self.target.c.type == target_type)).first()
            ret = (q != None)

        if session_need_to_close:
            session.close()
        return ret

    def __createTarget(self, session, uuid, name, type, entity_id, menu_id, params):
        target = Target()
        target.uuid = uuid
        target.name = name
        target.type = type
        if params.has_key('target_opt_kernel'):
            target.kernel_parameters = params['target_opt_kernel']
        else:
            target.kernel_parameters = self.config.web_def_kernel_parameters
        if params.has_key('target_opt_image'):
            target.image_parameters = params['target_opt_image']
        else:
            target.image_parameters = self.config.web_def_image_parameters
        target.exclude_parameters = '' # Always empty when creating a target
        target.fk_entity = entity_id
        target.fk_menu = menu_id
        session.save(target)
        return target

    ######### SYNCHRO
    def getTargetsThatNeedSynchroInEntity(self, loc_id, target_type, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()

        q = session.query(Target).add_entity(SynchroState)
        q = q.select_from(self.target.join(self.menu).join(self.entity, self.target.c.fk_entity == self.entity.c.id))
        q = q.filter(and_(
                self.entity.c.uuid == loc_id, \
                self.menu.c.fk_synchrostate.in_((P2ISS.TODO, P2ISS.INIT_ERROR)), \
                self.target.c.type == target_type \
            )).group_by(self.target.c.id).all()

        if session_need_to_close:
            session.close()
        return q

    def getComputersThatNeedSynchroInEntity(self, loc_id, session = None):
        return self.getTargetsThatNeedSynchroInEntity(loc_id, P2IT.COMPUTER, session)
    def getProfilesThatNeedSynchroInEntity(self, loc_id, session = None):
        return self.getTargetsThatNeedSynchroInEntity(loc_id, P2IT.PROFILE, session)

    def getComputersSynchroStates(self, uuids, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()

        q = session.query(Target).add_entity(SynchroState)
        q = q.select_from(self.target.join(self.menu).join(self.synchro_state))
        q = q.filter(self.target.c.uuid.in_(uuids)).all()

        if session_need_to_close:
            session.close()
        return q

    def __getSynchroStates(self, uuids, target_type, session):
        q = session.query(SynchroState).add_entity(Menu)
        q = q.select_from(self.synchro_state.join(self.menu).join(self.target, self.menu.c.id == self.target.c.fk_menu))
        q = q.filter(and_(self.target.c.uuid.in_(uuids), self.target.c.type == target_type)).all()
        return q

    def getTargetsSynchroState(self, uuids, target_type):
        session = create_session()
        q = self.__getSynchroStates(uuids, target_type, session)
        session.close()
        if q:
            return map(lambda x: x[0], q)
        return None

    def getLocationSynchroState(self, uuid):
        """
        Attempt to see if a location uuid needs to be synced, or not

        @param uuid the Entity uuid
        """

        session = create_session()

        # check if the entity menu as to be synced, by looking at its imaging server menu status
        j = self.synchro_state.join(self.menu).join(self.imaging_server).join(self.entity)
        f = self.entity.c.uuid == uuid
        q2 = session.query(SynchroState)
        q2 = q2.select_from(j)
        q2 = q2.filter(f)
        q2 = q2.first()

        if q2.label == "RUNNING" or q2.label == "INIT_ERROR" or q2.label == "TODO": # running => give up
            session.close()
            return q2

        # same, this time by target (we check the state of the content of this entity)
        q1 = session.query(SynchroState)
        j = self.synchro_state.join(self.menu).join(self.target).join(self.entity)
        f = self.entity.c.uuid == uuid
        q1 = q1.select_from(j)
        q1 = q1.filter(f)
        q1 = q1.all()

        session.close()

        a_state = [0, 0]
        for q in q1:
            if q.label == "RUNNING" or q.id == "INIT_ERROR": # running
                return q
            a_state[q.id - 1] += 1
        if a_state[0] == 0:
            return {
                'id' : 2,
                'label' : 'DONE'}

        return {
            'id' : 1,
            'label' : 'TODO'}

    def setLocationSynchroState(self, uuid, state):
        session = create_session()
        q2 = session.query(SynchroState).add_entity(Menu)
        q2 = q2.select_from(
            self.synchro_state.\
            join(self.menu).\
            join(self.imaging_server).\
            join(self.entity))
        q2 = q2.filter(self.entity.c.uuid == uuid).first()

        if q2 :
            synchro_state, menu = q2
            menu.fk_synchrostate = state
            session.save_or_update(menu)
        else :
            logging.getLogger().warn("Imaging.setLocationSynchroState : failed to set synchro_state")

        session.flush()
        session.close()
        return True

    def changeTargetsSynchroState(self, uuids, target_type, state):
        session = create_session()
        synchro_states = self.__getSynchroStates(uuids, target_type, session)
        for synchro_state, menu in synchro_states:
            menu.fk_synchrostate = state
            session.save_or_update(menu)
        session.flush()
        session.close()
        return True

    ######### MENUS
    def delProfileMenuTarget(self, uuids):
        session = create_session()
        targets = session.query(Target).add_entity(Menu)
        targets = targets.select_from(self.target.join(self.menu, self.target.c.fk_menu == self.menu.c.id))
        targets = targets.filter(and_(self.target.c.uuid.in_(uuids), self.target.c.type == P2IT.COMPUTER_IN_PROFILE)).all()
        for t, m in targets:
            session.delete(t)
            session.delete(m)
        session.flush()
        session.close()
        return True

    def delProfileComputerMenuItem(self, uuids):
        session = create_session()

        mis = session.query(MenuItem).add_entity(BootServiceInMenu).add_entity(ImageInMenu)
        mis = mis.select_from(self.menu_item \
                .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
                .outerjoin(self.boot_service_in_menu, self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                .outerjoin(self.image_in_menu, self.image_in_menu.c.fk_menuitem == self.menu_item.c.id) \
            )
        mis = mis.filter(and_(self.target.c.uuid.in_(uuids), self.target.c.type == P2IT.COMPUTER_IN_PROFILE)).all()

        for mi, bsim, iim in mis:
            if bsim != None:
                session.delete(bsim)
            if iim != None:
                session.delete(iim)
            session.delete(mi)

        session.flush()
        session.close()
        return True

    def __getAllProfileMenuItem(self, profile_UUID, session):
        return self.__getAllMenuItem(session, and_(self.target.c.uuid == profile_UUID, self.target.c.type == P2IT.PROFILE))

    def __getAllComputersMenuItem(self, computers_UUID, session):
        return self.__getAllMenuItem(session, and_(self.target.c.uuid.in_(computers_UUID), self.target.c.type.in_(P2IT.COMPUTER_IN_PROFILE, P2IT.COMPUTER)))

    def __getAllMenuItem(self, session, filt):
        ret = session.query(MenuItem).add_entity(Target).add_entity(BootServiceInMenu).add_entity(ImageInMenu) \
                .select_from(self.menu_item \
                    .join(self.menu, self.menu_item.c.fk_menu == self.menu.c.id) \
                    .join(self.target, self.target.c.fk_menu == self.menu.c.id) \
                    .outerjoin(self.boot_service_in_menu, self.boot_service_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                    .outerjoin(self.image_in_menu, self.image_in_menu.c.fk_menuitem == self.menu_item.c.id) \
                ).filter(filt).all()
        return ret

    def __copyMenuInto(self, menu_from, menu_into, session):
        for i in ('default_name', 'timeout', 'background_uri', 'message', 'ethercard', 'bootcli', 'disklesscli', 'dont_check_disk_size', 'hidden_menu', 'debug', 'update_nt_boot', 'fk_protocol'):
            setattr(menu_into, i, getattr(menu_from, i))
        session.save_or_update(menu_into)

    def __copyMenuItemInto(self, mi_from, mi_into, session):
        for i in ('order', 'hidden', 'hidden_WOL'):
            setattr(mi_into, i, getattr(mi_from, i))
        session.save_or_update(mi_into)

    def delComputersFromProfile(self, profile_UUID, computers):
        # we put the profile's mi before the computer's mi
        session = create_session()
        computers_UUID = map(lambda c:c['uuid'], computers.values())
        # copy the profile part of the menu in their own menu
        pmenu = self.getTargetMenu(profile_UUID, P2IT.PROFILE, session)
        pmis = self.__getAllProfileMenuItem(profile_UUID, session)
        pnb_element = len(pmis)
        mis = self.__getAllComputersMenuItem(computers_UUID, session)

        h_tid2target = {}
        for target, tuuid in session.query(Target).add_column(self.target.c.uuid).filter(self.target.c.uuid.in_(computers_UUID)).all():
            h_tid2target[tuuid] = target

        for mi, target, bsim, iim in mis:
            mi.order += pnb_element
            session.save_or_update(mi)

        session.flush()

        a_bsim = []
        a_iim = []
        a_target2default_item = []
        a_target2default_item_WOL = []
        for tuuid in computers_UUID:
            target = h_tid2target[tuuid]

            # put the parameter of the profile's menu in the computer menu
            menu = self.getTargetMenu(tuuid, P2IT.COMPUTER_IN_PROFILE, session)
            self.__copyMenuInto(pmenu, menu, session)

            # change the computer type, it's no longer a computer_in_profile
            target.type = P2IT.COMPUTER
            session.save_or_update(target)

            for mi, target, bsim, iim in pmis:
                # duplicate menu_item
                new_mi = MenuItem()
                new_mi.fk_menu = menu.id
                self.__copyMenuItemInto(mi, new_mi, session)

                # create a bsim if it's a bsim
                if bsim != None:
                    a_bsim.append([new_mi, bsim])

                # create a iim if it's a iim
                if iim != None:
                    a_iim.append([new_mi, iim])

                if mi.id == pmenu.fk_default_item:
                    a_target2default_item.append([menu, new_mi])

                if mi.id == pmenu.fk_default_item_WOL:
                    a_target2default_item_WOL.append([menu, new_mi])

        session.flush()

        for menu, mi in a_target2default_item:
            menu.fk_default_item = mi.id
            session.save_or_update(menu)

        for menu, mi in a_target2default_item_WOL:
            menu.fk_default_item_WOL = mi.id
            session.save_or_update(menu)

        for mi, bsim in a_bsim:
            new_bsim = BootServiceInMenu()
            new_bsim.fk_menuitem = mi.id
            new_bsim.fk_bootservice = bsim.fk_bootservice
            session.save(new_bsim)

        for mi, iim in a_iim:
            new_iim = ImageInMenu()
            new_iim.fk_menuitem = mi.id
            new_iim.fk_image = iim.fk_image
            session.save(new_iim)

        session.flush()
        session.close()

        return True

    def delProfile(self, profile_UUID):
        session = create_session()
        # remove all the possible menuitem that only depend on this profile
        pmis = self.__getAllProfileMenuItem(profile_UUID, session)
        profile, menu = session.query(Target).add_entity(Menu) \
                .select_from(self.target.join(self.menu, self.target.c.fk_menu == self.menu.c.id)) \
                .filter(and_(self.target.c.uuid == profile_UUID, self.target.c.type == P2IT.PROFILE)).one()

        menu.fk_default_item = None
        menu.fk_default_item_WOL = None
        session.save_or_update(menu)
        session.flush()

        for mi, target, bsim, iim in pmis:
            if bsim != None:
                session.delete(bsim)
            if iim != None:
                session.delete(iim)
        session.flush()

        for mi, target, bsim, iim in pmis:
            session.delete(mi)
        session.flush()

        session.delete(profile)
        session.flush()

        session.delete(menu)
        session.flush()
        session.close()
        return True

    def setProfileMenuTarget(self, uuids, profile_uuid, params):
        session = create_session()
        menu = self.getTargetMenu(profile_uuid, P2IT.PROFILE, session)
        cache_location_id = {}
        locations = ComputerLocationManager().getMachinesLocations(uuids)

        hostnames = {}
        if params.has_key('hostnames'):
            params['hostnames']

        registered = self.isTargetRegister(uuids, P2IT.COMPUTER_IN_PROFILE, session)
        for uuid in uuids:
            if not (registered.has_key(uuid) and registered[uuid]):
                loc_id = 0
                location_id = locations[uuid]['uuid']
                if not cache_location_id.has_key(location_id):
                    loc = session.query(Entity).filter(self.entity.c.uuid == location_id).first()
                    cache_location_id[location_id] = loc.id
                loc_id = cache_location_id[location_id]
                target_name = ''
                if hostnames.has_key(uuid):
                    target_name = hostnames[uuid]
                target = self.__createTarget(session, uuid, target_name, P2IT.COMPUTER_IN_PROFILE, loc_id, menu.id, params)
            else:
                target = self.getTargetsByUUID([uuid], session)
                target = target[0]
                target.kernel_parameters = params['target_opt_kernel']
                target.image_parameters = params['target_opt_image']
                session.save_or_update(target)
        session.flush()
        session.close()
        return [True]

    def putComputersInProfile(self, profile_UUID, computers):
        session = create_session()
        menu = self.getTargetMenu(profile_UUID, P2IT.PROFILE, session)
        imaging_server = ComputerProfileManager().getProfileImagingServerUUID(profile_UUID)
        entity = self.getImagingServerEntity(imaging_server)
        location_id = entity.uuid
        loc = session.query(Entity).filter(self.entity.c.uuid == location_id).first()

        for computer in computers.values():
            m = self.__duplicateMenu(session, menu, location_id, profile_UUID, True)
            t = self.__createTarget(session, computer['uuid'], computer['hostname'], P2IT.COMPUTER_IN_PROFILE, loc.id, m.id, {})

        session.flush()
        session.close()

        return True

    def setMyMenuTarget(self, uuid, params, type):
        session = create_session()
        menu = self.getTargetMenu(uuid, type, session)
        location_id = None
        p_id = None

        if not menu:
            if type == P2IT.COMPUTER:
                profile = ComputerProfileManager().getComputersProfile(uuid)
                default_menu = None
                if profile:
                    default_menu = self.getTargetMenu(profile.id, P2IT.PROFILE, session)
                if default_menu == None or not profile:
                    location = ComputerLocationManager().getMachinesLocations([uuid])
                    location_id = location[uuid]['uuid']
                    default_menu = self.getEntityDefaultMenu(location_id, session)
                else:
                    p_id = profile.id
                    location_id = None
            elif type == P2IT.PROFILE:
                imaging_server = ComputerProfileManager().getProfileImagingServerUUID(uuid)
                entity = self.getImagingServerEntity(imaging_server)
                location_id = entity.uuid
                default_menu = self.getEntityDefaultMenu(location_id, session)
            else:
                raise "%s:Don't know that type of target : %s"%(P2ERR.ERR_DEFAULT, type)
            menu = self.__duplicateMenu(session, default_menu, location_id, p_id)
            menu = self.__modifyMenu(id2uuid(menu.id), params, session)
            session.flush()
        else:
            menu = self.__modifyMenu(id2uuid(menu.id), params, session)

        target = None
        if not self.isTargetRegister(uuid, type, session):
            if location_id == None:
                location = ComputerLocationManager().getMachinesLocations([uuid])
                location_id = location[uuid]['uuid']
            loc = session.query(Entity).filter(self.entity.c.uuid == location_id).first()
            target = self.__createTarget(session, uuid, params['target_name'], type, loc.id, menu.id, params)
            # TODO : what do we do with target ?
            if type == P2IT.PROFILE:
                # need to create the targets for all the computers inside the profile
                # and then create them an "empty" menu
                # (ie : a menu with only the default_item* part)

                for computer in ComputerProfileManager().getProfileContent(uuid):
                   m = self.__duplicateMenu(session, menu, location_id, uuid, True)
                   t = self.__createTarget(session, computer.uuid, computer.name, P2IT.COMPUTER_IN_PROFILE, loc.id, m.id, params)

                session.flush()
        else:
            target = self.getTargetsByUUID([uuid], session)
            target = target[0]
            target.kernel_parameters = params['target_opt_kernel']
            target.image_parameters = params['target_opt_image']
            target.exclude_parameters = self._getExcludeString(target, params['target_opt_parts'])
            session.save_or_update(target)

        session.flush()
        session.close()
        return [True, target]

    def getMyMenuTarget(self, uuid, type):
        session = create_session()
        muuid = False
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
                    uuid = profile.id # WARNING we must pass in UUIDs!

        # if profile is registered, get the profile menu and finish
        if uuid and self.isTargetRegister(uuid, P2IT.PROFILE, session):
            target = self.getTargetsByUUID([uuid])
            whose = [uuid, P2IT.PROFILE, target[0].toH()]
            menu = self.getTargetMenu(uuid, P2IT.PROFILE, session)
        # else get the entity menu
        else:
            whose = False
            if muuid:
                location = ComputerLocationManager().getMachinesLocations([muuid])
                loc_id = location[muuid]['uuid']
            else:
                loc_id = ComputerProfileManager().getProfileImagingServerUUID(uuid)
            menu = self.getEntityDefaultMenu(loc_id, session)
        if menu == None:
            menu = False

        session.close()
        return [whose, menu]

    ######### POST INSTALL SCRIPT
    def isLocalPostInstallScripts(self, pis_uuid, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()

        q = session.query(PostInstallScript).add_entity(PostInstallScriptOnImagingServer)
        q = q.select_from(self.post_install_script \
                .outerjoin(self.post_install_script_on_imaging_server, self.post_install_script_on_imaging_server.c.fk_post_install_script == self.post_install_script.c.id) \
                .outerjoin(self.imaging_server, self.post_install_script_on_imaging_server.c.fk_imaging_server == self.imaging_server.c.id) \
                .outerjoin(self.entity))
        q = q.filter(or_(self.post_install_script_on_imaging_server.c.fk_post_install_script == None, self.entity.c.uuid == pis_uuid))
        q = q.filter(self.post_install_script.c.id == uuid2id(pis_uuid))
        q = q.first()

        ret = (q[1] != None)

        if session_need_to_close:
            session.close()
        return ret

    def __AllPostInstallScripts(self, session, location, filter, is_count = False):
        # PostInstallScripts are not specific to an Entity
        lang = self.__getLocLanguage(session, location)
        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q = session.query(PostInstallScript)
        if not is_count:
            q = q.add_entity(PostInstallScriptOnImagingServer).add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2)
            q = q.select_from(self.post_install_script \
                    .outerjoin(self.post_install_script_on_imaging_server, self.post_install_script_on_imaging_server.c.fk_post_install_script == self.post_install_script.c.id) \
                    .outerjoin(self.imaging_server, self.post_install_script_on_imaging_server.c.fk_imaging_server == self.imaging_server.c.id) \
                    .outerjoin(I18n1, and_(self.post_install_script.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                    .outerjoin(I18n2, and_(self.post_install_script.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
                    .outerjoin(self.entity))
            q = q.filter(or_(self.post_install_script_on_imaging_server.c.fk_post_install_script == None, self.entity.c.uuid == location))
        q = q.filter(or_(self.post_install_script.c.default_name.like('%'+filter+'%'), self.post_install_script.c.default_desc.like('%'+filter+'%')))
        return q

    def __mergePostInstallScriptOnImagingServerInPostInstallScript(self, postinstallscript_list):
        ret = []
        for postinstallscript, postinstallscript_on_imagingserver, name_i18n, desc_i18n in postinstallscript_list:
            if name_i18n != None and name_i18n.label != 'NOTTRANSLATED':
            #    setattr(postinstallscript, 'name', name_i18n.label)
                setattr(postinstallscript, 'default_name', name_i18n.label)
            if desc_i18n != None and desc_i18n.label != 'NOTTRANSLATED':
            #    setattr(postinstallscript, 'desc', desc_i18n.label)
                setattr(postinstallscript, 'default_desc', desc_i18n.label)
            setattr(postinstallscript, 'is_local', (postinstallscript_on_imagingserver != None))
            ret.append(postinstallscript)
        return ret

    def getAllTargetPostInstallScript(self, target_uuid, start, end, filter):
        session = create_session()
        loc = session.query(Entity).select_from(self.entity.join(self.target)).filter(self.target.c.uuid == target_uuid).first()
        session.close()
        location = id2uuid(loc.id)
        return self.getAllPostInstallScripts(location, start, end, filter)

    def countAllTargetPostInstallScript(self, target_uuid, filter):
        session = create_session()
        loc = session.query(Entity).select_from(self.entity.join(self.target)).filter(self.target.c.uuid == target_uuid).first()
        session.close()
        location = id2uuid(loc.id)
        return self.countAllPostInstallScripts(location, filter)

    def getAllPostInstallScripts(self, location, start, end, filter):
        session = create_session()
        q = self.__AllPostInstallScripts(session, location, filter)
        if end != -1:
            q = q.offset(int(start)).limit(int(end)-int(start))
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

    def getPostInstallScript(self, pis_uuid, session = None, location_id = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        lang = 1
        if location_id != None:
            lang = self.__getLocLanguage(session, location_id)
        else:
            pass
            # this is used internally to delete or edit a PIS
            # which mean that the day we manage to edit i18n labels, we have to work here
        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q = session.query(PostInstallScript).add_entity(PostInstallScriptOnImagingServer).add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2)
        q = q.select_from(self.post_install_script \
                .outerjoin(self.post_install_script_on_imaging_server) \
                .outerjoin(I18n1, and_(self.post_install_script.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                .outerjoin(I18n2, and_(self.post_install_script.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
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
        pisois = session.query(PostInstallScriptOnImagingServer).filter(self.post_install_script_on_imaging_server.c.fk_post_install_script == uuid2id(pis_uuid)).first()
        if pisois == None:
            # we have a local pis and no pisois !
            return False
        session.delete(pisois)
        session.flush()
        session.delete(pis)
        session.flush()
        session.close
        return True

    def getImagesPostInstallScript(self, ims, session = None, location_id = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        lang = 1
        if location_id != None:
            lang = self.__getLocLanguage(session, location_id)

        I18n1 = sa_exp_alias(self.internationalization)
        I18n2 = sa_exp_alias(self.internationalization)

        q = session.query(PostInstallScript).add_entity(Image).add_entity(Internationalization, alias=I18n1).add_entity(Internationalization, alias=I18n2)
        q = q.select_from(self.post_install_script \
                .join(self.post_install_script_in_image) \
                .join(self.image) \
                .outerjoin(I18n1, and_(self.post_install_script.c.fk_name == I18n1.c.id, I18n1.c.fk_language == lang)) \
                .outerjoin(I18n2, and_(self.post_install_script.c.fk_desc == I18n2.c.id, I18n2.c.fk_language == lang)) \
        )
        q = q.filter(self.image.c.id.in_(ims)).all()

        if session_need_to_close:
            session.close()
        return q

    def editPostInstallScript(self, pis_uuid, params):
        session = create_session()
        pis = self.getPostInstallScript(pis_uuid, session)
        need_to_be_save = False
        if pis.default_name != params['default_name']:
            need_to_be_save = True
            pis.default_name = params['default_name']
            pis.fk_name = 1
        if pis.default_desc != params['default_desc']:
            need_to_be_save = True
            pis.default_desc = params['default_desc']
            pis.fk_desc = 1
        if pis.value != params['value']:
            need_to_be_save = True
            pis.value = params['value']

        if need_to_be_save:
            session.save_or_update(pis)
            session.flush()
        session.close()
        return True

    def addPostInstallScript(self, loc_id, params):
        session = create_session()
        pis = PostInstallScript()
        pis.default_name = params['default_name']
        pis.fk_name = 1
        pis.default_desc = params['default_desc']
        pis.fk_desc = 1
        pis.value = params['value']
        session.save(pis)
        session.flush()
        # link it to the location because it's a local script
        imaging_server = self.getImagingServerByEntityUUID(loc_id, session)
        pisois = PostInstallScriptOnImagingServer()
        pisois.fk_post_install_script = pis.id
        pisois.fk_imaging_server = imaging_server.id
        session.save(pisois)
        session.flush()
        session.close()
        return True

    # Computer basic inventory stuff

    def injectInventory(self, imaging_server_uuid, computer_uuid, inventory):
        """
        Inject a computer inventory into the dabatase.
        For now only the ComputerDisk and ComputerPartition tables are used.
        """
        self.enableLogging(logging.INFO)
        if not isUUID(imaging_server_uuid):
            raise TypeError('Bad imaging server UUID: %s'
                            % imaging_server_uuid)
        if not isUUID(computer_uuid):
            raise TypeError('Bad computer UUID: %s' % computer_uuid)
        session = create_session()
        session.begin()
        try:
            # First remove old computer inventory
            target = session.query(Target).filter_by(uuid=computer_uuid).one()
            for current_disk in target.disks:
                session.delete(current_disk)
            # Then push a new inventory
            if 'disk' in inventory :
                for disknum in inventory['disk']:
                    disk_info = inventory['disk'][disknum]
                    cd = ComputerDisk()
                    cd.num = int(disknum)
                    cd.cyl = int(disk_info['C'])
                    cd.head = int(disk_info['H'])
                    cd.sector = int(disk_info['S'])
                    cd.capacity = int(disk_info['size'])
                    for partnum in disk_info['parts']:
                        part = disk_info['parts'][partnum]
                        cp = ComputerPartition()
                        cp.num = int(partnum)
                        cp.type = part['type']
                        cp.length = int(part['length'])
                        cp.start = int(part['start'])
                        cd.partitions.append(cp)
                        target.disks.append(cd)
            session.save_or_update(target)
            session.commit()
        except:
            session.rollback()
            raise
        session.close()

    def getPartitionsToBackupRestore(self, computer_uuid):
        """
        @return: the computer disks and parts inventory, and flags them as
        excluded according to Target.exclude_parameters value
        @rtype: dict
        """
        if not isUUID(computer_uuid):
            raise TypeError('Bad computer UUID: %s' % computer_uuid)
        session = create_session()
        target = session.query(Target).filter_by(uuid=computer_uuid).one()
        excluded = target.exclude_parameters
        if not excluded:
            excluded = ''
        excluded = excluded.split()
        ret = {}
        for disk in target.disks:
            disknum = str(disk.num)
            ret[disknum] = {}
            if disknum + ':0' in excluded:
                ret[disknum]['exclude'] = True
            for partition in disk.partitions:
                partnum = str(partition.num)
                ret[disknum][partnum] = partition.toH()
                if disknum + ':' + str(partition.num + 1) in excluded:
                    ret[disknum][partnum]['exclude'] = True
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
                        excluded.append(str(disknum -1) + ':' + str(partnum))
            else:
                # Disk completely disabled
                excluded.append(str(disknum - 1) + ':0')
        return ' '.join(excluded)

    def getForbiddenComputersUUID(self, profile_UUID = None):
        """
        @returns: return all the computers that already have an imaging menu
        @rtype: list
        """
        session = create_session()
        targets = session.query(Target).select_from(self.target \
                .join(self.menu, self.target.c.fk_menu == self.menu.c.id) \
            )
        if profile_UUID == None:
            targets = targets.filter(self.target.c.type == P2IT.COMPUTER).all()
        else:
            computers = ComputerProfileManager().getProfileContent(profile_UUID)
            if computers:
                computers = map(lambda c:c.uuid, computers)
                targets = targets.filter(and_(self.target.c.type == P2IT.COMPUTER, not self.target.c.uuid.in_(computers)))
            else:
                targets = targets.filter(self.target.c.type == P2IT.COMPUTER).all()
        session.close()
        ret = map(lambda t:t.uuid, targets)
        return ret

    def areForbiddebComputers(self, computers_UUID):
        """
        @returns: return all the computers from the computer_UUID list that already have an imaging menu
        @rtype: list
        """
        session = create_session()
        targets = session.query(Target).select_from(self.target \
                .join(self.menu, self.target.c.fk_menu == self.menu.c.id) \
            ).filter(and_(self.target.c.uuid.in_(computers_UUID), self.target.c.type == P2IT.COMPUTER)).all()
        session.close()
        ret = map(lambda t:t.uuid, targets)
        return ret

    def getImageIDFromImageUUID(self, image_uuid):
        session = create_session()
        img = session.query(Image).filter(self.image.c.uuid == image_uuid).first()
        session.close()
        if img :
            return img.id
        return None

    def getImageUUIDFromImageUUID(self, image_uuid):
        return id2uuid(self.getImageIDFromImageUUID(image_uuid))

def id2uuid(id):
    return "UUID%d" % id


def uuid2id(uuid):
    return uuid.replace("UUID", "")


###########################################################
class DBObject(object):
    to_be_exported = ['id', 'name', 'label']
    need_iteration = []
    i18n = []
    def getUUID(self):
        if hasattr(self, 'id'):
            return id2uuid(self.id)
        logging.getLogger().warn("try to get %s uuid!"%(type(self)))
        return False
    def to_h(self):
        return self.toH()
    def toH(self, level = 0):
        ImagingDatabase().completeNomenclatureLabel(self)
        ret = {}
        for i in dir(self):
            if i in self.i18n:
                pass

            if i in self.to_be_exported:
                ret[i] = getattr(self, i)
            if i in self.need_iteration and level < 1:
                # we don't want to enter in an infinite loop
                # and generally we don't need more levels
                attr = getattr(self, i)
                if type(attr) == list:
                    new_attr = []
                    for a in attr:
                        new_attr.append(a.toH(level+1))
                    ret[i] = new_attr
                else:
                    ret[i] = attr.toH(level+1)
        if hasattr(self, 'id'):
            ret['imaging_uuid'] = self.getUUID()
        return ret

class BootService(DBObject):
    to_be_exported = ['id', 'value', 'default_desc', 'uri', 'is_local', 'default_name']
    need_iteration = ['menu_item']
    i18n = ['fk_name', 'fk_desc']

class BootServiceInMenu(DBObject):
    pass

class BootServiceOnImagingServer(DBObject):
    pass

class ComputerDisk(DBObject):
    to_be_exported = ['num']

class ComputerPartition(DBObject):
    to_be_exported = ['num', 'type', 'length']

class Entity(DBObject):
    to_be_exported = ['id', 'name', 'uuid']

class Image(DBObject):
    to_be_exported = ['id', 'path', 'checksum', 'size', 'desc', 'is_master', 'creation_date', 'fk_creator', 'name', 'is_local', 'uuid', 'mastered_on_target_uuid', 'read_only']
    need_iteration = ['menu_item', 'post_install_scripts']

class ImageState(DBObject):
    to_be_exported = ['id', 'label']

class ImageInMenu(DBObject):
    pass

class ImagingLog(DBObject):
    to_be_exported = ['id', 'timestamp', 'completeness', 'detail', 'fk_imaging_log_state', 'fk_imaging_log_level', 'fk_target', 'imaging_log_state', 'imaging_log_level']
    need_iteration = ['target']

class ImagingLogState(DBObject):
    to_be_exported = ['id', 'label']

class ImagingLogLevel(DBObject):
    to_be_exported = ['id', 'label']

class ImageOnImagingServer(DBObject):
    pass

class ImagingServer(DBObject):
    to_be_exported = ['id', 'name', 'url', 'packageserver_uuid', 'recursive', 'fk_entity', 'fk_default_menu', 'fk_language', 'language']

class Internationalization(DBObject):
    to_be_exported = ['id', 'label', 'fk_language']

class Language(DBObject):
    to_be_exported = ['id', 'label']

class MasteredOn(DBObject):
    to_be_exported = ['fk_image', 'image', 'fk_imaging_log', 'imaging_log']

class Menu(DBObject):
    to_be_exported = ['id', 'default_name', 'fk_name', 'timeout', 'background_uri', 'message', 'ethercard', 'bootcli', 'disklesscli', 'dont_check_disk_size', 'hidden_menu', 'debug', 'update_nt_boot', 'fk_default_item', 'fk_default_item_WOL', 'fk_protocol', 'protocol', 'synchrostate']
    i18n = ['fk_name']

class MenuItem(DBObject):
    to_be_exported = ['id', 'default_name', 'order', 'hidden', 'hidden_WOL', 'fk_menu', 'fk_name', 'default', 'default_WOL', 'desc', 'read_only']
    need_iteration = ['boot_service', 'image']

class Partition(DBObject):
    to_be_exported = ['id', 'filesystem', 'size', 'fk_image']

class PostInstallScript(DBObject):
    to_be_exported = ['id', 'default_name', 'value', 'default_desc', 'is_local', 'order']
    i18n = ['fk_name', 'fk_desc']

class PostInstallScriptInImage(DBObject):
    to_be_exported = ['order']

class PostInstallScriptOnImagingServer(DBObject):
    pass

class Protocol(DBObject):
    to_be_exported = ['id', 'label']

class SynchroState(DBObject):
    to_be_exported = ['id', 'label']

class Target(DBObject):
    to_be_exported = ['id', 'name', 'uuid', 'type', 'fk_entity', 'fk_menu', 'kernel_parameters', 'image_parameters', 'exclude_parameters']

class TargetType(DBObject):
    to_be_exported = ['id', 'label']

class User(DBObject):
    to_be_exported = ['id', 'login']
