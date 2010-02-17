# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
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

from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from pulse2.database.imaging.types import *

from sqlalchemy import *
from sqlalchemy.sql import union
from sqlalchemy.orm import *

import logging

DATABASEVERSION = 1

ERR_MISSING_NOMENCLATURE = 1001
ERR_IMAGING_SERVER_DONT_EXISTS = 1003
ERR_ENTITY_ALREADY_EXISTS = 1004

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
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize, convert_unicode=True)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            return False
        self.metadata.create_all()
        self.nomenclatures = {'MasteredOnState':MasteredOnState, 'TargetType':TargetType, 'Protocol':Protocol}
        self.fk_nomenclatures = {'MasteredOn':{'fk_mastered_on_state':'MasteredOnState'}, 'Target':{'type':'TargetType'}, 'Menu':{'fk_protocol':'Protocol'}}
        self.__loadNomenclatureTables()
        self.loadDefaults()
        self.is_activated = True
        self.dbversion = self.getImagingDatabaseVersion()
        self.logger.debug("ImagingDatabase finish activation")
        return self.db_check()

    def loadDefaults(self):
        self.default_params = {
            'default_name':self.config.web_def_default_menu_name,
            'timeout':self.config.web_def_default_timeout,
            'background_uri':self.config.web_def_default_background_uri,
            'message':self.config.web_def_default_message,
            'protocol':self.config.web_def_default_protocol
        }

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the imaging database
        """
        self.version = Table("version", self.metadata, autoload = True)
        
        self.initTables()
        mapper(BootService, self.boot_service)
        mapper(BootServiceInMenu, self.boot_service_in_menu)
        mapper(BootServiceOnImagingServer, self.boot_service_on_imaging_server)
        mapper(Entity, self.entity)
        mapper(Image, self.image)
        mapper(ImageInMenu, self.image_in_menu)
        mapper(ImageOnImagingServer, self.image_on_imaging_server)
        mapper(ImagingServer, self.imaging_server)
        mapper(Internationalization, self.internationalization)
        mapper(Language, self.language)
        mapper(MasteredOn, self.mastered_on)
        mapper(MasteredOnState, self.mastered_on_state)
        mapper(Menu, self.menu, properties = { 'default_item':relation(MenuItem), 'default_item_WOL':relation(MenuItem) } )
        mapper(MenuItem, self.menu_item, properties = { 'menu' : relation(Menu) })
        mapper(Partition, self.partition)
        mapper(PostInstallScript, self.post_install_script)
        mapper(PostInstallScriptInImage, self.post_install_script_in_image)
        mapper(Protocol, self.protocol)
        mapper(Target, self.target)
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

        self.boot_service_in_menu = Table(
            "BootServiceInMenu",
            self.metadata,
            Column('fk_bootservice', Integer, ForeignKey('BootService.id'), primary_key=True),
            Column('fk_menuitem', Integer, ForeignKey('MenuItem.id'), primary_key=True),
            autoload = True
        )

        self.boot_service_on_imaging_server = Table(
            "BootServiceOnImagingServer",
            self.metadata,
            Column('fk_boot_service', Integer, ForeignKey('BootService.id'), primary_key=True),
            Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            autoload = True
        )

        self.entity = Table(
            "Entity",
            self.metadata,
            autoload = True
        )

        self.image = Table(
            "Image",
            self.metadata,
            Column('fk_creator', Integer, ForeignKey('User.id')),
            autoload = True
        )

        self.image_in_menu = Table(
            "ImageInMenu",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_menuitem', Integer, ForeignKey('MenuItem.id'), primary_key=True),
            autoload = True
        )

        self.image_on_imaging_server = Table(
            "ImageOnImagingServer",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id'), primary_key=True),
            autoload = True
        )

        self.imaging_server = Table(
            "ImagingServer",
            self.metadata,
            Column('fk_entity', Integer, ForeignKey('Entity.id')),
            autoload = True
        )

        self.internationalization = Table(
            "Internationalization",
            self.metadata,
            Column('id', Integer, primary_key=True),
            Column('fk_language', Integer, ForeignKey('Language.id'), primary_key=True),
            autoload = True
        )

        self.language = Table(
            "Language",
            self.metadata,
            autoload = True
        )

        self.mastered_on = Table(
            "MasteredOn",
            self.metadata,
            Column('fk_mastered_on_state', Integer, ForeignKey('MasteredOnState.id')),
            Column('fk_image', Integer, ForeignKey('Image.id')),
            Column('fk_target', Integer, ForeignKey('Target.id')),
            autoload = True
        )

        self.mastered_on_state = Table(
            "MasteredOnState",
            self.metadata,
            autoload = True
        )

        self.menu = Table(
            "Menu",
            self.metadata,
            # cant put them for circular dependancies reasons, the join must be explicit
            # Column('fk_default_item', Integer, ForeignKey('MenuItem.id')), 
            # Column('fk_default_item_WOL', Integer, ForeignKey('MenuItem.id')),
            Column('fk_protocol', Integer, ForeignKey('Protocol.id')),
            # fk_name is not an explicit FK, you need to choose the lang before beeing able to join
            autoload = True
        )

        self.menu_item = Table(
            "MenuItem",
            self.metadata,
            Column('fk_menu', Integer, ForeignKey('Menu.id')),
            # fk_name is not an explicit FK, you need to choose the lang before beeing able to join
            autoload = True
        )

        self.partition = Table(
            "Partition",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id')),
            autoload = True
        )

        self.post_install_script = Table(
            "PostInstallScript",
            self.metadata,
            autoload = True
        )

        self.post_install_script_in_image = Table(
            "PostInstallScriptInImage",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id'), primary_key=True),
            Column('fk_post_install_script', Integer, ForeignKey('PostInstallScript.id'), primary_key=True),
            autoload = True
        )

        self.protocol = Table(
            "Protocol",
            self.metadata,
            autoload = True
        )

        self.target = Table(
            "Target",
            self.metadata,
            Column('fk_entity', Integer, ForeignKey('Entity.id')),
            Column('fk_menu', Integer, ForeignKey('Menu.id')),
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

    def __loadNomenclatureTables(self):
        session = create_session()
        for i in self.nomenclatures:
            n = session.query(self.nomenclatures[i]).all()
            self.nomenclatures[i] = {}
            for j in n:
                self.nomenclatures[i][j.id] = j.label
        session.close()

    def completeNomenclatureLabel(self, objs):
        if type(objs) != list and type(objs) != tuple:
            objs = [objs]
        if len(objs) == 0:
            return
        className = str(objs[0].__class__).split("'")[1].split('.')[-1]
        nomenclatures = []
        if self.fk_nomenclatures.has_key(className):
            for i in self.fk_nomenclatures[className]:
                nomenclatures.append([i, i.replace('fk_', ''), self.nomenclatures[self.fk_nomenclatures[className][i]]])
            for obj in objs:
                for fk, field, value in nomenclatures:
                    fk_val = getattr(obj, fk)
                    if fk == field:
                        field = '%s_value'%field
                    if value.has_key(fk_val):
                        setattr(obj, field, value[fk_val])
                    else:
                        self.logger.warn("nomenclature is missing for %s field %s (value = %s)"%(str(obj), field, str(fk_val)))
                        setattr(obj, field, "%s:nomenclature does not exists."%(ERR_MISSING_NOMENCLATURE))
                        

    def completeTarget(self, objs):
        """
        take a list of dict with a fk_target element and add them the target dict that correspond
        """
        ids = {}
        for i in objs:
            ids[i['fk_target']] = None
        ids = ids.keys()
        targets = self.__getTargetById(ids)
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

###########################################################
    def __getTargetById(self, ids):
        session = create_session()
        n = session.query(Target).filter(self.target.c.id.in_(ids)).all()
        session.close()
        return n

    def __mergeTargetInMasteredOn(self, mastered_on_list):
        ret = []
        for mastered_on, target in mastered_on_list:
            setattr(mastered_on, 'target', target)
            ret.append(mastered_on)
        return ret

    def __getTargetsMenuQuery(self, session):
        return session.query(Menu).select_from(self.menu.join(self.target))
        
    def getTargetsMenuTID(self, target_id):
        session = create_session()
        q = self.__getTargetsMenuQuery(session)
        q = q.filter(self.target.c.id == target_id).first() # there should always be only one!
        session.close()
        return q
        
    def getTargetsMenuTUUID(self, target_id, session = None):
        need_to_close_session = False
        if session == None:
            need_to_close_session = True
            session = create_session()
        q = self.__getTargetsMenuQuery(session)
        q = q.filter(self.target.c.uuid == target_id).first() # there should always be only one!
        if need_to_close_session:
            session.close()
        return q

    def getEntityDefaultMenu(self, loc_id, session = None):
        need_to_close_session = False
        if session == None:
            need_to_close_session = True
            session = create_session()
        q = session.query(Menu).filter(and_(self.entity.c.fk_default_menu == self.menu.c.id, self.entity.c.uuid == loc_id)).first() # there should always be only one!
        if need_to_close_session:
            session.close()
        return q
    
    def __mergeMenuItemInBootService(self, list_of_bs, list_of_both):
        ret = []
        temporary = {}
        for bs, mi in list_of_both:
            if mi != None:
                temporary[bs.id] = mi
        for bs, bs_id in list_of_bs:
            if temporary.has_key(bs_id):
                setattr(bs, 'menu_item', temporary[bs_id])
            ret.append(bs)
        return ret
    
    def __mergeBootServiceInMenuItem(self, my_list):
        ret = []
        for mi, bs, menu in my_list:
            if bs != None:
                setattr(mi, 'boot_service', bs)
            if menu != None:
                setattr(mi, 'default', (menu.fk_default_item == mi.id))
                setattr(mi, 'default_WOL', (menu.fk_default_item_WOL == mi.id))
            ret.append(mi)
        return ret
    
    def __mergeMenuItemInImage(self, list_of_im, list_of_both):
        ret = []
        temporary = {}
        for im, mi in list_of_both:
            if mi != None:
                temporary[im.id] = mi
        for im, im_id in list_of_im:
            if temporary.has_key(im_id):
                setattr(im, 'menu_item', temporary[im_id])
            ret.append(im)
        return ret
    
    def __mergeBootServiceOrImageInMenuItem(self, mis):
        """ warning this one does not work on a list but on a tuple of 3 elements (mi, bs, im) """
        (menuitem, bootservice, image, menu) = mis
        if bootservice != None:
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

    def getMenuContent(self, menu_id, type = MENU_ALL, start = 0, end = -1, filter = '', session = None):# TODO implement the start/end with a union betwen q1 and q2
        session_need_close = False
        if session == None:
            session = create_session()
            session_need_close = True

        mi_ids = session.query(MenuItem).add_column(self.menu_item.c.id).select_from(self.menu_item.join(self.menu))
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
        
        q = []
        if type == MENU_ALL or type == MENU_BOOTSERVICE:
            q1 = session.query(MenuItem).add_entity(BootService).add_entity(Menu).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service).join(self.menu))
            q1 = q1.filter(self.menu_item.c.id.in_(mi_ids)).order_by(self.menu_item.c.order).all()
            q1 = self.__mergeBootServiceInMenuItem(q1)
            q.extend(q1)
        if type == MENU_ALL or type == MENU_IMAGE:
            q2 = session.query(MenuItem).add_entity(Image).add_entity(Menu).select_from(self.menu_item.join(self.image_in_menu).join(self.image).join(self.menu))
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
            return 0
        return q

    def countMenuContentFast(self, menu_id): # get MENU_ALL and empty filter
        session = create_session()
        q = session.query(MenuItem).filter(self.menu_item.c.fk_menu == menu_id).count()
        session.close()
        return q
        
    def countMenuContent(self, menu_id, type = MENU_ALL, filter = ''):
        if type == MENU_ALL and filter =='':
            return self.countMenuContentFast(menu_id)
        
        session = create_session()
        q = 0
        if type == MENU_ALL or type == MENU_BOOTSERVICE:
            q1 = session.query(MenuItem).add_entity(BootService).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service))
            q1 = q1.filter(and_(self.menu_item.c.fk_menu == menu_id, self.boot_service.c.desc.like('%'+filter+'%'))).count()
            q += q1
        if type == MENU_ALL or type == MENU_IMAGE:
            q2 = session.query(MenuItem).add_entity(Image).select_from(self.menu_item.join(self.image_in_menu).join(self.image))
            q2 = q2.filter(and_(self.menu_item.c.fk_menu == menu_id, self.boot_service.c.desc.like('%'+filter+'%'))).count()
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
    
    def __MasteredOns4Location(self, session, location_uuid, filter):
        n = session.query(MasteredOn).add_entity(Target).select_from(self.mastered_on.join(self.target).join(self.entity)).filter(self.entity.c.uuid == location_uuid)
        if filter != '':
            n = n.filter(or_(self.mastered_on.c.title.like('%'+filter+'%'), self.target.c.name.like('%'+filter+'%')))
        return n
        
    def getMasteredOns4Location(self, location_uuid, start, end, filter):
        session = create_session()
        n = self.__MasteredOns4Location(session, location_uuid, filter)
        if end != -1:
            n = n.offset(int(start)).limit(int(end)-int(start))
        else:
            n = n.all()
        session.close()
        n = self.__mergeTargetInMasteredOn(n)
        return n

    def countMasteredOns4Location(self, location_uuid, filter):
        session = create_session()
        n = self.__MasteredOns4Location(session, location_uuid, filter)
        n = n.count()
        session.close()
        return n
    
    #####################
    def __MasteredOnsOnTargetByIdAndType(self, session, target_id, type, filter):
        q = session.query(MasteredOn).add_entity(Target).select_from(self.mastered_on.join(self.target)).filter(or_(self.target.c.id == target_id, self.target.c.uuid == target_id))
        if type == TYPE_COMPUTER:
            q = q.filter(self.target.c.type == 1)
        elif type == TYPE_PROFILE:
            q = q.filter(self.target.c.type == 2)
        else:
            self.logger.error("type %s does not exists!"%(type))
            # to be sure we dont get anything, this is an error case!
            q = q.filter(self.target.c.type == 0)
        if filter != '':
            q = q.filter(or_(self.mastered_on.c.title.like('%'+filter+'%'), self.target.c.name.like('%'+filter+'%')))
        return q
        
    def getMasteredOnsOnTargetByIdAndType(self, target_id, type, start, end, filter):
        session = create_session()
        q = self.__MasteredOnsOnTargetByIdAndType(session, target_id, type, filter)
        if end != -1:
            q = q.offset(int(start)).limit(int(end)-int(start))
        else:
            q = q.all()
        session.close()
        q = self.__mergeTargetInMasteredOn(q)
        return q
    
    def countMasteredOnsOnTargetByIdAndType(self, target_id, type, filter):
        session = create_session()
        q = self.__MasteredOnsOnTargetByIdAndType(session, target_id, type, filter)
        q = q.count()
        session.close()
        return q
    
    ######################
    def __PossibleBootServices(self, session, target_uuid, filter):
        q = session.query(BootService).add_column(self.boot_service.c.id)
        q = q.select_from(self.boot_service.join(self.boot_service_on_imaging_server).join(self.imaging_server).join(self.entity).join(self.target))
        q = q.filter(self.target.c.uuid == target_uuid)
        if filter != '':
            q = q.filter(or_(self.boot_service.c.desc.like('%'+filter+'%'), self.boot_service.c.value.like('%'+filter+'%')))
        return q

    def __EntityBootServices(self, session, loc_id, filter):
        q = session.query(BootService).add_column(self.boot_service.c.id)
        q = q.select_from(self.boot_service.join(self.boot_service_on_imaging_server).join(self.imaging_server).join(self.entity))
        q = q.filter(self.entity.c.uuid == loc_id)
        if filter != '':
            q = q.filter(or_(self.boot_service.c.desc.like('%'+filter+'%'), self.boot_service.c.value.like('%'+filter+'%')))
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

    def __createNewMenuItem(self, session, menu_id, desc, params):
        mi = MenuItem()
        params['order'] = self.getLastMenuItemOrder(menu_id) + 1
        mi = self.__fillMenuItem(session, mi, menu_id, desc, params)
        return mi
    
    def __fillMenuItem(self, session, mi, menu_id, desc, params):
        mi.default_name = params['default_name']
        mi.hidden = params['hidden']
        mi.hidden_WOL = params['hidden_WOL']
        if params.has_key('order'):
            mi.order = params['order'] # TODO put the order!
        mi.desc = desc
        mi.fk_name = 0 # TODO i18n in internationalize!
        mi.fk_menu = menu_id
        session.save_or_update(mi)
        return mi
       
    ERR_TARGET_HAS_NO_MENU = 1000
    ERR_ENTITY_HAS_NO_DEFAULT_MENU = 1002
    def __addMenuDefaults(self, session, menu, mi, params):
        is_menu_modified = False
        if params['default']:
            is_menu_modified = True
            menu.fk_default_item = mi.id
        if params['default_WOL']:
            is_menu_modified = True
            menu.fk_default_item_WOL = mi.id
        if is_menu_modified:
            session.save_or_update(menu)
        return menu

    def __editMenuDefaults(self, session, menu, mi, params):
        is_menu_modified = False
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
        bs = session.query(BootService).filter(self.boot_service.c.id == uuid2id(bs_uuid)).first();
        if menu == None:
            raise '%s:Please create menu before trying to put a bootservice'%(ERR_TARGET_HAS_NO_MENU)
            
        mi = self.__createNewMenuItem(session, menu.id, bs.desc, params)
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
        mi = session.query(MenuItem).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service).join(self.menu).join(self.target))
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()
        return mi

    def __getServiceMenuItem4Entity(self, session, bs_uuid, loc_id):
        mi = session.query(MenuItem).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service).join(self.menu))
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.menu.c.id == self.entity.c.fk_default_menu, self.entity.c.uuid == loc_id)).first()
        return mi
        
    def __editService(self, session, bs_uuid, menu, mi, params):
        bs = session.query(BootService).filter(self.boot_service.c.id == uuid2id(bs_uuid)).first();
        if menu == None:
            raise '%s:Please create menu before trying to put a bootservice'%(ERR_TARGET_HAS_NO_MENU)

        mi = self.__fillMenuItem(session, mi, menu.id, bs.desc, params)
        session.flush()

        self.__editMenuDefaults(session, menu, mi, params)

        session.flush()
        return None
 
    def editServiceToTarget(self, bs_uuid, target_uuid, params):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid, session)
        mi = self.__getServiceMenuItem(session, bs_uuid, target_uuid)
        ret = self.__editService(session, bs_uuid, menu, mi, params)
        session.close()
        return ret

    def editServiceToEntity(self, bs_uuid, loc_id, params):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id, session)
        mi = self.__getServiceMenuItem4Entity(session, bs_uuid, loc_id)
        ret = self.__editService(session, bs_uuid, menu, mi, params)
        session.close()
        return ret

    def delServiceToTarget(self, bs_uuid, target_uuid):
        session = create_session()
        mi = session.query(MenuItem).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service).join(self.menu).join(self.target))
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()
        bsim = session.query(BootServiceInMenu).select_from(self.boot_service_in_menu.join(self.menu_item).join(self.boot_service).join(self.menu).join(self.target))
        bsim = bsim.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.target.c.uuid == target_uuid)).first()
        session.delete(mi)
        session.delete(bsim)
        session.flush()

        session.close()
        return None
    
    def delServiceToEntity(self, bs_uuid, loc_id):
        session = create_session()
        mi = session.query(MenuItem).select_from(self.menu_item.join(self.boot_service_in_menu).join(self.boot_service).join(self.menu))
        mi = mi.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.menu.c.id == self.entity.c.fk_default_menu, self.entity.c.uuid == loc_id)).first()
        bsim = session.query(BootServiceInMenu).select_from(self.boot_service_in_menu.join(self.menu_item).join(self.boot_service).join(self.menu))
        bsim = bsim.filter(and_(self.boot_service.c.id == uuid2id(bs_uuid), self.menu.c.id == self.entity.c.fk_default_menu, self.entity.c.uuid == loc_id)).first()
        session.delete(mi)
        session.delete(bsim)
        session.flush()

        session.close()
        return None

    def getMenuItemByUUID(self, mi_uuid, session = None):
        session_need_close = False
        if session == None:
            session_need_close = True
            session = create_session()
        mi = session.query(MenuItem).add_entity(BootService).add_entity(Image).add_entity(Menu)
        mi = mi.select_from(self.menu_item.join(self.menu).outerjoin(self.boot_service_in_menu).outerjoin(self.boot_service).outerjoin(self.image_in_menu).outerjoin(self.image))
        mi = mi.filter(self.menu_item.c.id == uuid2id(mi_uuid)).first()
        mi = self.__mergeBootServiceOrImageInMenuItem(mi)
        if session_need_close:
            session.close()
        return mi
    
    ######################
    def __PossibleImages(self, session, target_uuid, is_master, filter):
        q = session.query(Image).add_column(self.image.c.id)
        q = q.select_from(self.image.join(self.image_on_imaging_server).join(self.imaging_server).join(self.entity).join(self.target))
        q = q.filter(self.target.c.uuid == target_uuid) # , or_(self.image.c.is_master == True, and_(self.image.c.is_master == False, )))
        if filter != '':
            q = q.filter(or_(self.image.c.desc.like('%'+filter+'%'), self.image.c.value.like('%'+filter+'%')))
        if is_master == IMAGE_IS_MASTER_ONLY:
            q = q.filter(self.image.c.is_master == True)
        elif is_master == IMAGE_IS_IMAGE_ONLY:
            q = q.filter(self.image.c.is_master == False)
        elif is_master == IMAGE_IS_BOTH:
            pass
            
        return q

    def __EntityImages(self, session, loc_id, filter):
        q = session.query(Image).add_column(self.image.c.id)
        q = q.select_from(self.image.join(self.image_on_imaging_server).join(self.imaging_server).join(self.entity))
        q = q.filter(and_(self.entity.c.uuid == loc_id, self.image.c.is_master == True))
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

    def getPossibleImagesOrMaster(self, target_uuid, is_master, start, end, filter):
        session = create_session()
        menu = self.getTargetsMenuTUUID(target_uuid)
        q1 = self.__PossibleImages(session, target_uuid, is_master, filter)
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

    def countPossibleImagesOrMaster(self, target_uuid, type, filter):
        session = create_session()
        q = self.__PossibleImages(session, target_uuid, type, filter)
        q = q.count()
        session.close()
        return q

    def getPossibleImages(self, target_uuid, start, end, filter):
        return self.getPossibleImagesOrMaster(target_uuid, IMAGE_IS_IMAGE_ONLY, start, end, filter)
    
    def getPossibleMasters(self, target_uuid, start, end, filter):
        return self.getPossibleImagesOrMaster(target_uuid, IMAGE_IS_MASTER_ONLY, start, end, filter)

    def getEntityMasters(self, loc_id, start, end, filter):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id)
        if menu == None:
            raise "%s:Entity does not have a default menu"%(ERR_ENTITY_HAS_NO_DEFAULT_MENU)
        q1 = self.__EntityImages(session, loc_id, filter)
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

    def countPossibleImages(self, target_uuid, filter):
        return self.countPossibleImagesOrMaster(target_uuid, IMAGE_IS_IMAGE_ONLY, filter)

    def countPossibleMasters(self, target_uuid, filter):
        return self.countPossibleImagesOrMaster(target_uuid, IMAGE_IS_MASTER_ONLY, filter)

    def countEntityMasters(self, loc_id, filter):
        session = create_session()
        q = self.__EntityImages(session, loc_id, filter)
        q = q.count()
        session.close()
        return q

    def __addImage(self, session, item_uuid, menu, params):
        im = session.query(Image).filter(self.image.c.id == uuid2id(item_uuid)).first();
        if menu == None:
            raise '%s:Please create menu before trying to put an image'%(ERR_TARGET_HAS_NO_MENU)
            
        if params.has_key('name') and not params.has_key('default_name'):
            params['default_name'] = params['name']
        mi = self.__createNewMenuItem(session, menu.id, im.desc, params)
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
        
    def addImageToEntity(self, item_uuid, loc_id, params):
        session = create_session()
        menu = self.getEntityDefaultMenu(loc_id, session)
        ret = self.__addImage(session, item_uuid, menu, params)
        session.close()
        return ret

    def __editImage(self, session, item_uuid, menu, mi, params):
        im = session.query(Image).filter(self.image.c.id == uuid2id(item_uuid)).first();
        if menu == None:
            raise '%s:Please create menu before trying to put an image'%(ERR_TARGET_HAS_NO_MENU)

        mi = self.__fillMenuItem(session, mi, menu.id, im.desc, params)
        session.flush()

        self.__editMenuDefaults(session, menu, mi, params)

        session.flush()
        return None

    def __getImageMenuItem(self, session, item_uuid, target_uuid):
        mi = session.query(MenuItem).select_from(self.menu_item.join(self.image_in_menu).join(self.image).join(self.menu).join(self.target))
        mi = mi.filter(and_(self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid)).first()
        return mi

    def __getImageMenuItem4Entity(self, session, item_uuid, loc_id):
        mi = session.query(MenuItem).select_from(self.menu_item.join(self.image_in_menu).join(self.image).join(self.menu))
        mi = mi.filter(and_(self.image.c.id == uuid2id(item_uuid), self.menu.c.id == self.entity.c.fk_default_menu, self.entity.c.uuid == loc_id)).first()
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

    def delImageToTarget(self, item_uuid, target_uuid):
        session = create_session()
        mi = session.query(MenuItem).select_from(self.menu_item.join(self.image_in_menu).join(self.image).join(self.menu).join(self.target))
        mi = mi.filter(and_(self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid)).first()
        iim = session.query(ImageInMenu).select_from(self.image_in_menu.join(self.menu_item).join(self.image).join(self.menu).join(self.target))
        iim = bsim.filter(and_(self.image.c.id == uuid2id(item_uuid), self.target.c.uuid == target_uuid)).first()
        session.delete(mi)
        session.delete(iim)
        # TODO when it's not a master and the computer is the only one, what should we do with the image?
        session.flush()
        
        session.close()
        return None

    ######################
    def __TargetImagesQuery(self, session, target_uuid, type, filter):
        q = session.query(Image).add_entity(MenuItem)
        q = q.select_from(self.image.join(self.image_on_imaging_server).join(self.imaging_server).join(self.entity).join(self.target).join(self.image_in_menu).join(self.menu_item))
        q = q.filter(and_(self.target.c.uuid == target_uuid, or_(self.image.c.desc.like('%'+filter+'%'), self.image.c.value.like('%'+filter+'%'))))
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
        q = q.filter(and_(self.entity.c.uuid == entity_uuid, or_(self.image.c.desc.like('%'+filter+'%'), self.image.c.value.like('%'+filter+'%'))))
        return q

    def __ImagesInEntityNoMaster(self, session, target_uuid, type, filter):
        q = self.__ImagesInEntityQuery(session, target_uuid, type, filter)
        q.filter(self.image.c.is_master == False)
        return q

    def __ImagesInEntityIsMaster(self, session, target_uuid, type, filter):
        q = self.__ImagesInEntityQuery(session, target_uuid, type, filter)
        q.filter(self.image.c.is_master == False)
        return q
    
    def getTargetImages(self, target_id, type, start, end, filter):
        pass

    def countTargetImages(self, target_id, type, filter):
        pass
        
    ######################
    def getBootServicesOnTargetById(self, target_id, start, end, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return []
        menu_items = self.getMenuContent(menu.id, MENU_BOOTSERVICE, start, end, filter)
        return menu_items

    def countBootServicesOnTargetById(self, target_id, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return 0
        count_items = self.countMenuContent(menu.id, MENU_BOOTSERVICE, filter)
        return count_items

    ######################
    def getBootMenu(self, target_id, start, end, filter):
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return []
        menu_items = self.getMenuContent(menu.id, MENU_ALL, start, end, filter)
        return menu_items
        
    def countBootMenu(self, target_id, filter): 
        menu = self.getTargetsMenuTUUID(target_id)
        if menu == None:
            return 0
        count_items = self.countMenuContent(menu.id, MENU_ALL, filter)
        return count_items

    def getEntityBootMenu(self, loc_id, start, end, filter):
        menu = self.getEntityDefaultMenu(loc_id)
        if menu == None:
            return []
        menu_items = self.getMenuContent(menu.id, MENU_ALL, start, end, filter)
        return menu_items

    def countEntityBootMenu(self, loc_id, filter):
        menu = self.getEntityDefaultMenu(loc_id)
        if menu == None:
            return 0
        count_items = self.countMenuContent(menu.id, MENU_ALL, filter)
        return count_items
        
    ######################
    def __moveItemInMenu(self, menu, mi_uuid, reverse = False):
        session = create_session()
        mis = self.getMenuContent(menu.id, MENU_ALL, 0, -1, '', session)
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
    def countImagingServerByPackageServerUUID(self, uuid):
        session = create_session()
        q = session.query(ImagingServer).filter(self.imaging_server.c.packageserver_uuid == uuid).count()
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
        
    def getImagingServerByPackageServerUUID(self, uuid):
        session = create_session()
        q = session.query(ImagingServer).filter(self.imaging_server.c.packageserver_uuid == uuid).all()
        session.close()
        return q
    
    def registerImagingServer(self, name, url, uuid):
        session = create_session()
        ims = ImagingServer()
        ims.name = name
        ims.url = url
        ims.fk_entity = 0
        ims.packageserver_uuid = uuid
        session.save(ims)
        session.flush()
        session.close()
        return ims.id
    
    def __getEntityByUUID(self, session, loc_id):
        return session.query(Entity).filter(self.entity.c.uuid == loc_id).first()
    
    def getMenuByUUID(self, menu_uuid, session = None):
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
    
    def __modifyMenu(self, menu_uuid, params, session = None):
        session_need_to_close = False
        if session == None:
            session_need_to_close = True
            session = create_session()
        menu = self.getMenuByUUID(menu_uuid, session)
        need_to_be_save = False
        if params.has_key('default_name') and menu.default_name != params['default_name']:
            need_to_be_save = True
            menu.default_name = params['default_name']
        if params.has_key('timeout') and menu.timeout != params['timeout']:
            need_to_be_save = True
            menu.timeout = params['timeout']
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
        menu.fk_name = 0
        session.save(menu)
        return menu

    def __createEntity(self, session, loc_id, loc_name, menu_id):
        e = Entity()
        e.name = loc_name
        e.uuid = loc_id
        e.fk_default_menu = menu_id
        session.save(e)
        return e
        
    def linkImagingServerToEntity(self, is_uuid, loc_id, loc_name):
        session = create_session()
        imaging_server = self.getImagingServerByUUID(is_uuid, session)
        if imaging_server == None:
            raise "%s:No server exists with that uuid (%s)" % (ERR_IMAGING_SERVER_DONT_EXISTS, is_uuid)
        location = self.__getEntityByUUID(session, loc_id)
        if location != None:
            raise "%s:This entity already exists (%s) cant be linked again" % (ERR_ENTITY_ALREADY_EXISTS, loc_id)
        
        menu = self.__createMenu(session, self.default_params)
        session.flush()
        location = self.__createEntity(session, loc_id, loc_name, menu.id)
        session.flush()

        imaging_server.fk_entity = location.id
        session.save_or_update(imaging_server)
        session.flush()
        session.close()
        return True

    def __AllNonLinkedImagingServer(self, session, filter):
        q = session.query(ImagingServer).filter(self.imaging_server.c.fk_entity == 0)
        if filter and filter != '':
            q = q.filter(or_(self.imaging_server.c.name.like('%'+filter+'%'), self.imaging_server.c.url.like('%'+filter+'%'), self.imaging_server.c.uuid.like('%'+filter+'%')))
        return q
        
    def getAllNonLinkedImagingServer(self, start, end, filter):
        session = create_session()
        q = self.__AllNonLinkedImagingServer(session, filter)
        if end != -1:
            q = q.offset(int(start)).limit(int(end)-int(start))
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
        q = session.query(ImagingServer).select_from(self.imaging_server.join(self.entity)).filter(self.entity.c.uuid == loc_id).count()
        return (q == 1)

    def setImagingServerConfig(self, location, config):
        session = create_session()
        imaging_server = self.getImagingServerByEntityUUID(location, session)
        # modify imaging_server
        # session.save(imaging_server)
        # session.flush()
        session.close()
        return True

    # Protocols
    def getAllProtocols(self):
        session = create_session()
        q = session.query(Protocol).all()
        session.close()
        return q

def id2uuid(id):
    return "UUID%d" % id
def uuid2id(uuid):
    return uuid.replace("UUID", "")

###########################################################
class DBObject(object):
    to_be_exported = ['id', 'name', 'label']
    need_iteration = []
    def getUUID(self):
        return id2uuid(self.id)
    def to_h(self):
        return self.toH()
    def toH(self, level = 0):
        ImagingDatabase().completeNomenclatureLabel(self)
        ret = {}
        for i in dir(self):
            if i in self.to_be_exported:
                ret[i] = getattr(self, i)
            if i in self.need_iteration and level < 1:
                # we dont want to enter in an infinite loop 
                # and generaly we dont need more levels
                ret[i] = getattr(self, i).toH(level+1)
        if not ret.has_key('uuid'):
            ret['imaging_uuid'] = self.getUUID()
        return ret

class BootService(DBObject):
    to_be_exported = ['id', 'value', 'desc', 'uri']
    need_iteration = ['menu_item']

class BootServiceInMenu(DBObject):
    pass

class BootServiceOnImagingServer(DBObject):
    pass

class Entity(DBObject):
    to_be_exported = ['id', 'name', 'uuid']

class Image(DBObject):
    to_be_exported = ['id', 'path', 'checksum', 'size', 'desc', 'is_master', 'creation_date', 'fk_creator']
    need_iteration = ['menu_item']

class ImageInMenu(DBObject):
    pass

class ImageOnImagingServer(DBObject):
    pass

class ImagingServer(DBObject):
    to_be_exported = ['id', 'name', 'url', 'packageserver_uuid', 'recursive', 'fk_entity']

class Internationalization(DBObject):
    to_be_exported = ['id', 'label', 'fk_language']

class Language(DBObject):
    to_be_exported = ['id', 'label']

class MasteredOn(DBObject):
    to_be_exported = ['id', 'timestamp', 'title', 'completeness', 'detail', 'fk_mastered_on_state', 'fk_image', 'fk_target', 'mastered_on_state', 'image']
    need_iteration = ['target']

class MasteredOnState(DBObject):
    to_be_exported = ['id', 'label']

class Menu(DBObject):
    to_be_exported = ['id', 'default_name', 'fk_name', 'timeout', 'background_uri', 'message', 'fk_default_item', 'fk_default_item_WOL', 'fk_protocol', 'protocol']

class MenuItem(DBObject):
    to_be_exported = ['id', 'default_name', 'order', 'hidden', 'hidden_WOL', 'fk_menu', 'fk_name', 'default', 'default_WOL', 'desc']
    need_iteration = ['boot_service', 'image']

class Partition(DBObject):
    to_be_exported = ['id', 'filesystem', 'size', 'fk_image']

class PostInstallScript(DBObject):
    to_be_exported = ['id', 'name', 'value', 'uri']

class PostInstallScriptInImage(DBObject):
    pass

class Protocol(DBObject):
    to_be_exported = ['id', 'label']

class Target(DBObject):
    to_be_exported = ['id', 'name', 'uuid', 'type', 'fk_entity', 'fk_menu']

class TargetType(DBObject):
    to_be_exported = ['id', 'label']

class User(DBObject):
    to_be_exported = ['id', 'login']

