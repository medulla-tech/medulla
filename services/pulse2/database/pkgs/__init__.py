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
Provides access to Pkgs database
"""
# standard modules
import time

# SqlAlchemy
from sqlalchemy import and_, create_engine, MetaData, Table, Column, String, \
                       Integer, ForeignKey, select, asc, or_, desc, func, not_, distinct
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import NoSuchTableError, TimeoutError
from sqlalchemy.orm.exc import NoResultFound
#from sqlalchemy.orm import sessionmaker; Session = sessionmaker()
##from sqlalchemy.orm import sessionmaker
import datetime
# ORM mappings
from pulse2.database.pkgs.orm.version import Version
from pulse2.database.pkgs.orm.pakages import Packages
from pulse2.database.pkgs.orm.extensions import Extensions
from pulse2.database.pkgs.orm.dependencies import Dependencies
from mmc.database.database_helper import DatabaseHelper
#from pulse2.database.xmppmaster import XmppMasterDatabase
# Pulse 2 stuff
#from pulse2.managers.location import ComputerLocationManager
# Imported last
import logging
logger = logging.getLogger()


NB_DB_CONN_TRY = 2

# TODO need to check for useless function (there should be many unused one...)



class PkgsDatabase(DatabaseHelper):
    """
    Singleton Class to query the Pkgs database.

    """

    def db_check(self):
        self.my_name = "pkgs"
        self.configfile = "pkgs.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None
        self.logger.info("Pkgs database is connecting")
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, \
                pool_size = self.config.dbpoolsize, pool_timeout = self.config.dbpooltimeout, convert_unicode = True)
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initTables():
            return False
        if not self.initMappersCatchException():
            return False
        self.metadata.create_all()
        # FIXME: should be removed
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("Pkgs database connected")
        return True

    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """
        try:
            # packages
            self.package = Table(
                "packages",
                self.metadata,
                autoload = True
            )

            # extensions
            self.extensions = Table(
                "extensions",
                self.metadata,
                autoload = True
            )

            # Dependencies
            self.dependencies = Table(
                "dependencies",
                self.metadata,
                autoload = True
            )
        except NoSuchTableError, e:
            self.logger.error("Cant load the Pkgs database : table '%s' does not exists"%(str(e.args[0])))
            return False
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the Pkgs database
        """
        mapper(Packages, self.package)
        mapper(Extensions, self.extensions)
        mapper(Dependencies, self.dependencies)

    ####################################

    @DatabaseHelper._sessionm
    def createPackage(self, name = '', descriptif ="", uuid = ''):
        """
        Return a new pkgs
        """
        bdl = Packages()
        bdl.label = name
        bdl.id = uuid
        bdl.description = descriptif
        session.add(bdl)
        session.flush()
        return bdl

    @DatabaseHelper._sessionm
    def list_all(self, session):
        """
        Get the list of all the packages stored in database.

        Returns:
            list of packages serialized as dict
        """

        ret = session.query(Packages).all()
        packages = []
        for package in ret:
            packages.append(package.to_array())
        return packages

    @DatabaseHelper._sessionm
    def list_all_extensions(self, session):
        ret = session.query(Extensions).all()
        extensions = []
        for extension in ret:
            extensions.append(extension.getId())
        return extensions
