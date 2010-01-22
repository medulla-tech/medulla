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

from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from pulse2.database.utilities import unique, toH, DbObject, handle_deconnect
from pulse2.database.sqlalchemy_tests import checkSqlalchemy

from sqlalchemy import *
from sqlalchemy.orm import *

import datetime
import time
import re
import logging

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
        PossibleQueries().init(self.config)
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize, convert_unicode=True)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            return None
        self.metadata.create_all()
        self.is_activated = True
        self.dbversion = self.getImagingDatabaseVersion()
        self.logger.debug("ImagingDatabase finish activation")
        return self.db_check()

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the imaging database
        """
        self.version = Table("Version", self.metadata, autoload = True)
        mapper(Version, self.version)
        
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
        mapper(Log, self.log)
        mapper(LogState, self.log_state)
        mapper(Menu, self.menu)
        mapper(MenuItem, self.menu_item)
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
            Column('fk_bootservice', Integer, ForeignKey('BootService.id')),
            Column('fk_menuitem', Integer, ForeignKey('MenuItem.id')),
            autoload = True
        )

        self.boot_service_on_imaging_server = Table(
            "BootServiceOnImagingServer",
            self.metadata,
            Column('fk_boot_service', Integer, ForeignKey('BootService.id')),
            Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id')),
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
            Column('fk_image', Integer, ForeignKey('Image.id')),
            Column('fk_menuitem', Integer, ForeignKey('MenuItem.id')),
            autoload = True
        )

        self.image_on_imaging_server = Table(
            "ImageOnImagingServer",
            self.metadata,
            Column('fk_image', Integer, ForeignKey('Image.id')),
            Column('fk_imaging_server', Integer, ForeignKey('ImagingServer.id')),
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
            Column('fk_language', Integer, ForeignKey('Language.id')),
            autoload = True
        )

        self.language = Table(
            "Language",
            self.metadata,
            autoload = True
        )

        self.log = Table(
            "Log",
            self.metadata,
            Column('fk_log_state', Integer, ForeignKey('LogState.id')),
            Column('fk_image', Integer, ForeignKey('Image.id')),
            Column('fk_target', Integer, ForeignKey('Target.id')),
            autoload = True
        )

        self.log_state = Table(
            "LogState",
            self.metadata,
            autoload = True
        )

        self.menu = Table(
            "Menu",
            self.metadata,
            Column('fk_default_item', Integer, ForeignKey('MenuItem.id')),
            Column('fk_default_item_WOL', Integer, ForeignKey('MenuItem.id')),
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
            Column('fk_image', Integer, ForeignKey('Image.id')),
            Column('fk_post_install_script', Integer, ForeignKey('PostInstallScript.id')),
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

    def getImagingDatabaseVersion(self):
        """
        Return the imaging database version.
        We don't use this information for now, but if we can get it this means the database connection is working.

        @rtype: int
        """
        return self.version.select().execute().fetchone()[0]


class DBObject:
    __to_be_exported = ['id', 'name', 'label']
    def to_h(self):
        return self.toH()
    def toH(self):
        ret = {}
        for i in dir(self):
            if i in self.__to_be_exported:
                ret[i] = getattr(self, i)
        return ret

class BootService(DBObject):
    __to_be_exported = ['id', 'value', 'desc', 'uri']

class BootServiceInMenu(DBObject):
    pass

class BootServiceOnImagingServer(DBObject):
    pass

class Entity(DBObject):
    __to_be_exported = ['id', 'name', 'uuid']
    pass

class Image(DBObject):
    __to_be_exported = ['id', 'path', 'checksum', 'size', 'desc', 'is_master', 'creation_date', 'fk_creator']

class ImageInMenu(DBObject):
    pass

class ImageOnImagingServer(DBObject):
    pass

class ImagingServer(DBObject):
    __to_be_exported = ['id', 'name', 'url', 'packageserver_uuid', 'recursive', 'fk_entity']

class Internationalization(DBObject):
    __to_be_exported = ['id', 'label', 'fk_language']

class Language(DBObject):
    __to_be_exported = ['id', 'label']

class Log(DBObject):
    __to_be_exported = ['id', 'timestamp', 'title', 'completeness', 'detail', 'fk_log_state', 'fk_image', 'fk_target']

class LogState(DBObject):
    __to_be_exported = ['id', 'label']

class Menu(DBObject):
    __to_be_exported = ['id', 'default_name', 'fk_name', 'timeout', 'background_uri', 'message', 'fk_default_item', 'fk_default_item_WOL', 'fk_protocol']

class MenuItem(DBObject):
    __to_be_exported = ['id', 'default_name', 'order', 'hidden', 'hidden_WOL', 'fk_menu', 'fk_name']

class Partition(DBObject):
    __to_be_exported = ['id', 'filesystem', 'size', 'fk_image']

class PostInstallScript(DBObject):
    __to_be_exported = ['id', 'name', 'value', 'uri']

class PostInstallScriptInImage(DBObject):
    pass

class Protocol(DBObject):
    __to_be_exported = ['id', 'label']

class Target(DBObject):
    __to_be_exported = ['id', 'name', 'uuid', 'type', 'fk_entity', 'fk_menu']

class TargetType(DBObject):
    __to_be_exported = ['id', 'label']

class User(DBObject):
    __to_be_exported = ['id', 'login']

class Version(DBObject):
    pass

