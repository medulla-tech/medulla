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
from pulse2.database.pkgs.orm.syncthingsync import Syncthingsync
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.xmppmaster import XmppMasterDatabase
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

            # Syncthingsync
            self.syncthingsync = Table(
                "syncthingsync",
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
        mapper(Syncthingsync, self.syncthingsync)

    ####################################

    @DatabaseHelper._sessionm
    def createPackage(self, session, package):
        """
        Insert the package config into database.
        Param:
            package : dict of the historical config of the package
        Returns:
            Packages object
        """

        request = session.query(Packages).filter(Packages.uuid == package['id']).first()

        if request is None:
            new_package = Packages()
        else:
            new_package = request

        new_package.label = package['name']
        new_package.uuid = package['id']
        new_package.description = package['description']
        new_package.version = package['version']
        new_package.os = package['targetos']
        new_package.metagenerator = package['metagenerator']
        new_package.entity_id = package['entity_id']
        if type(package['sub_packages']) is str:
            new_package.sub_packages = package['sub_packages']
        elif type(package['sub_packages']) is list:
            new_package.sub_packages = ",".join(package['sub_packages'])
        new_package.reboot = package['reboot']
        new_package.inventory_associateinventory = package['inventory']['associateinventory']
        new_package.inventory_licenses = package['inventory']['licenses']
        new_package.Qversion = package['inventory']['queries']['Qversion']
        new_package.Qvendor = package['inventory']['queries']['Qvendor']
        new_package.Qsoftware = package['inventory']['queries']['Qsoftware']
        new_package.boolcnd = package['inventory']['queries']['boolcnd']
        new_package.postCommandSuccess_command = package['commands']['postCommandSuccess']['command']
        new_package.postCommandSuccess_name = package['commands']['postCommandSuccess']['name']
        new_package.installInit_command = package['commands']['installInit']['command']
        new_package.installInit_name = package['commands']['installInit']['name']
        new_package.postCommandFailure_command = package['commands']['postCommandFailure']['command']
        new_package.postCommandFailure_name = package['commands']['postCommandFailure']['name']
        new_package.command_command = package['commands']['command']['command']
        new_package.command_name = package['commands']['command']['name']
        new_package.preCommand_command = package['commands']['preCommand']['command']
        new_package.preCommand_name = package['commands']['preCommand']['name']

        if request is None:
            session.add(new_package)
        session.commit()
        session.flush()
        return new_package

    @DatabaseHelper._sessionm
    def remove_dependencies(self, session, package_uuid, status="delete"):
        """
        Remove the dependencies for the specified package.
        Params:
            package_uuid : string of the uuid of the package given as reference.
            status : string (default : delete) if the status is delete, then the
                function delete all in the dependencies table which refers to the package
        """
        session.query(Dependencies).filter(Dependencies.uuid_package == package_uuid).delete()
        if status == "delete":
            session.query(Dependencies).filter(Dependencies.uuid_dependency == package_uuid).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def refresh_dependencies(self, session, package_uuid, uuid_list):
        """
        Refresh the list of the dependencies for a specified package.
        Params:
            package_uuid : string of the reference uuid
            uuid_list : list of the dependencies associated to the reference.
                One reference has many dependencies.
        """
        self.remove_dependencies(package_uuid, "refresh")
        for dependency in uuid_list:
            new_dependency = Dependencies()
            new_dependency.uuid_package = package_uuid
            new_dependency.uuid_dependency = dependency
            session.add(new_dependency)
        session.commit()
        session.flush()

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
    def remove_package(self, session, uuid):
        """Delete the specified package from the DB
        Param :
            uuid: string of the uuid of the specified package.
        """
        session.query(Packages).filter(Packages.uuid == uuid).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def list_all_extensions(self, session):
        ret = session.query(Extensions).all()
        extensions = []
        for extension in ret:
            extensions.append(extension.getId())
        return extensions

    @DatabaseHelper._sessionm
    def pkgs_register_synchro_package(self, session, uuidpackage, typesynchro ):
        #list id server relay
        list_server_relay = XmppMasterDatabase().get_List_jid_ServerRelay_enable(enabled=1)
        for jid in list_server_relay:
            #exclude local package server
            if jid[0].startswith("rspulse@pulse/"):
                continue
            self.setSyncthingsync(uuidpackage, jid[0], typesynchro , watching = 'yes')

    # =====================================================================
    # pkgs FUNCTIONS synch syncthing
    # =====================================================================
    @DatabaseHelper._sessionm
    def setSyncthingsync( self, session, uuidpackage, relayserver_jid, typesynchro = "create", watching = 'yes'):
        try:
            new_Syncthingsync = Syncthingsync()
            new_Syncthingsync.uuidpackage = uuidpackage
            new_Syncthingsync.typesynchro =  typesynchro
            new_Syncthingsync.relayserver_jid = relayserver_jid
            new_Syncthingsync.watching =  watching
            session.add(new_Syncthingsync)
            session.commit()
            session.flush()
        except Exception, e:
            logging.getLogger().error(str(e))

    @DatabaseHelper._sessionm
    def get_relayservers_no_sync_for_packageuuid(self, session, uuidpackage):
        result_list = []
        try:
            relayserversync = session.query(Syncthingsync).filter(and_(Syncthingsync.uuidpackage == uuidpackage)).all()
            session.commit()
            session.flush()

            for relayserver in relayserversync:
                res={}
                res['uuidpackage'] = relayserver.uuidpackage
                res['typesynchro'] = relayserver.typesynchro
                res['relayserver_jid'] = relayserver.relayserver_jid
                res['watching'] = relayserver.watching
                res['date'] = relayserver.date
                result_list.append(res)
            return result_list
        except Exception, e:
            logging.getLogger().error(str(e))
            traceback.print_exc(file=sys.stdout)
            return []

    @DatabaseHelper._sessionm
    def pkgs_regiter_synchro_package(self, session, uuidpackage, typesynchro ):
        #list id server relay
        list_server_relay = self.get_List_jid_ServerRelay_enable(enabled=1)
        for jid in list_server_relay:
            #exclude local package server
            if jid[0].startswith("rspulse@pulse/"):
                continue
            self.setSyncthingsync(uuidpackage, jid[0], typesynchro , watching = 'yes')

    @DatabaseHelper._sessionm
    def pkgs_unregister_synchro_package(self, session, uuidpackage, typesynchro, jid_relayserver):
        if typesynchro != None:
            session.query(Syncthingsync).filter(and_(Syncthingsync.uuidpackage == uuidpackage,
                                                    Syncthingsync.relayserver_jid == jid_relayserver,
                                                    Syncthingsync.typesynchro == typesynchro)).delete()
        else:
            session.query(Syncthingsync).filter(and_(Syncthingsync.uuidpackage == uuidpackage,
                                                    Syncthingsync.relayserver_jid == jid_relayserver)).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def pkgs_delete_synchro_package(self, session, uuidpackage):
        session.query(Syncthingsync).filter(Syncthingsync.uuidpackage == uuidpackage).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def list_pending_synchro_package(self, session):
        pendinglist = session.query(distinct(Syncthingsync.uuidpackage).label("uuidpackage")).all()
        session.commit()
        session.flush()
        result_list = []
        for packageuid in pendinglist:
            result_list.append(packageuid.uuidpackage)
        return result_list

    @DatabaseHelper._sessionm
    def clear_old_pending_synchro_package(self, session, timeseconde=35):
        sql ="""DELETE FROM `pkgs`.`syncthingsync`
            WHERE
                `syncthingsync`.`date` < DATE_SUB(NOW(), INTERVAL %d SECOND);"""%timeseconde
        session.execute(sql)
        session.commit()
        session.flush()
