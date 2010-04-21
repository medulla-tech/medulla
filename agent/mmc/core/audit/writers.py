# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Contains singleton classes that writes to the audit backend
"""

import socket
import sys
import os
import pwd
import logging
import threading

# SqlAlchemy
from sqlalchemy import *
from sqlalchemy.orm import *

from mmc.core.audit.classes import *
from mmc.core.audit.record import *
from mmc.core.audit.readers import AuditReaderDB
from mmc.support.mmctools import Singleton


class AuditWriterI:
    """
    Interface for classes that writes record entry to the audit database.
    """

    def __init__(self):
        self.logger = logging.getLogger()

    def log(self):
        """
        To write a record to the database.
        """
        pass

    def setup(self):
        pass

    def get(self):
        pass

    def getById(self):
        pass

    def getLog(self, start, end, plug, user, type, date1, date2, object, action):
        pass

    def getLogById(self, id):
        pass

    def getActionType(self):
        """
        Return a list of action and type if action=1 it return list of action
        if type=1 it return a list of type

        @param action: if action=1 the function return a list of action
        @type action: int
        @param type: if type=1 the function return a list of action
        @type type: int
        """
        pass

    def commit(self):
        pass

class AuditWriterDB(Singleton, AuditWriterI):

    """
    Singleton class for an object that writes audit data to a database.

    MySQL and PostgreSQL databases are available.
    """

    def __init__(self):
        """
        Init Object AuditWriterDB
        """
        Singleton.__init__(self)
        AuditWriterI.__init__(self)
        # self.fqdn contains the agent FQDN.
        self.fqdn = socket.getfqdn()

    def setConfig(self, config):
        """
        Set the configuration of this object, which contains database options.
        """
        self.config = config

    def connect(self):
        """
        Connect to the database.
        """
        db = create_engine(self.config.auditdbdriver + "://" + self.config.auditdbuser + ":" + self.config.auditdbpassword + "@" + self.config.auditdbhost + ":" + str(self.config.auditdbport) + "/" + self.config.auditdbname)
        self.metadata = MetaData()
        self.metadata.bind = db
        self._initTableVersion()
        mapper(Version, self.version_table)

    def init(self, driver, user, passwd, host, port, name):
        """
        Initialize connection to the database, and checks that it is using
        the wanted version.

        @param driver: driver name mysql (postgres,sqlite)
        @type driver: string
        @param user: username for the database connexion 
        @type user: string
        @param passwd: password of the database user
        @type passwd: string
        @param host: hostname of the database
        @type host: string
        @param port: port for the database connexion
        @type port: int
        @param name: database name
        @type name: string
        """
        self.connect()
        version = self.getCurrentVersion()
        if not self.checkVersion(version):
            raise Exception('Bad audit database schema. Version %d found. Please update the database schema to version %d.' % (version, self.getUptodateVersion()))
        self._initTables()
        self._initMappers()

    def _initTables(self, version = None):
        """
        Init database tables.
        """
        if version == None:
            version = self.getUptodateVersion()
        func = getattr(self, "_initTables" + self.config.auditdbdriver + "V" + str(version))
        func()

    def _initMappers(self, version = None):
        """
        Init database mappers.
        """
        if version == None:
            version = self.getUptodateVersion()
        func = getattr(self, "_initMappers" + self.config.auditdbdriver + "V" + str(version))
        func()

    def _populateTables(self, version = None):
        """
        Populate tables before the first use.
        """
        if version == None:
            version = self.getUptodateVersion()
        func = getattr(self, "_populateTables" + self.config.auditdbdriver + "V" + str(version))
        func()

    def operation(self, op):
        """
        Allow to perform special operations on the audit database

        if op == 'drop', print the string to use to drop the database.
        if op == 'droptables', drop all tables.
        if op == 'create', print the string to use to create the database.
        if op == 'init', initialize the audit database tables.
        if op == 'check', check that the database version is correct.
        if op == 'list', print all records on command line.
        """
        self.connect()
        if op == 'drop':
            if self.config.auditdbdriver == 'mysql':
                print '-- Execute the following lines into the MySQL client'
                print 'DROP DATABASE IF EXISTS %s;' % self.config.auditdbname
                print "DROP USER '%s'@localhost;" % self.config.auditdbuser
            elif self.config.auditdbdriver == 'postgres':
                # FIXME: Do it for PostgreSQL too
                print 'Not yet implemented'
            else:
                self.logger.error("SQL driver '%s' is not supported" % self.config.auditdbdriver)
                return False
        elif op == 'droptables':
            if not self.databaseExists():
                self.logger.error('Database does not exist')
                return False
            version = self.getCurrentVersion()
            self._initTables(version)
            self._initMappers(version)
            self.logger.info('Dropping audit tables as requested')
            self.metadata.drop_all()
            self.logger.info('Done')
        elif op == 'create':
            if self.config.auditdbdriver == 'mysql':
                print '-- Execute the following lines into the MySQL client'
                print 'CREATE DATABASE %s DEFAULT CHARSET utf8;' % self.config.auditdbname
                print "GRANT ALL PRIVILEGES ON %s.* TO '%s'@localhost IDENTIFIED BY '%s';" % (self.config.auditdbname, self.config.auditdbuser, self.config.auditdbpassword)
                print 'FLUSH PRIVILEGES;'
            elif self.config.auditdbdriver == 'postgres':
                # FIXME: Do it for PostgreSQL too
                print 'Not yet implemented'
            else:
                self.logger.error("SQL driver '%s' is not supported" % self.config.auditdbdriver)
                return False
        elif op == 'init':
            if self.databaseExists():
                self.logger.error('Database already exist')
                return False
            self.logger.info('Creating audit tables as requested')
            self.logger.info('Using database schema version %d' % self.getUptodateVersion())
            self._initTables()
            self._initMappers()
            self.metadata.create_all()
            self._populateTables()
            self._updateDatabaseVersion()
            self.logger.info('Done')
        elif op == 'check':
            ret = False
            if self.databaseExists():
                version = self.getCurrentVersion()
                uptodate = self.getUptodateVersion()
                self.logger.info('Current database schema version: %d' % version)
                if version == uptodate:
                    self.logger.info('Database schema version is up to date')
                    ret = True
                elif version < uptodate:
                    self.logger.info('Database schema should be updated')
                else:
                    self.logger.info('Unknown database schema version number. This sofware may need to be updated.')
            return ret
        elif op == 'list':
            self._initTables()
            self._initMappers()
            [nb, records] = self.getLog(0, 0, 0, 0, 0, 0, 0, 0, 0)
            if nb > 0:
                self.logger.info('List all audit records.')
                print "Date".ljust(19)+"\t"+"User".ljust(50)+"\t"+"Event".ljust(25)+"\t"+"Plugin".ljust(15)+"\t"+"Result"
                for record in records:
                    print record["date"]+"\t"+record["user"].ljust(50)+"\t"+record["action"].ljust(25)+"\t"+record["plugin"].ljust(15)+"\t"+str(record["commit"])
            else:
                self.logger.info('No audit record in the database.')
            return True            
        elif op == 'purge':
            pass
        elif op == 'archive':
            pass
        else:
            return False
        
        return True

    def log(self, module, event, objects = [], current=None , previous=None, parameters = {}):
        """
        Allow to log an Action, it uses LogRecordDB

        @param context: current context object, should contain the current
                        user id, etc.
        @type context: Twisted session object
        
        @param module: module name
        @type module: str

        @param action: action name
        @type action: string

        @param objects
        @type objects: tuple of (<object_uri>,<type>)

        @param current: current attribute value saved in database
        @type current: string

        @param previous: previous attribute value stored in Ldap 
        @type previous: string

        @param parameters: list of parameters (get with the locals() builtin)
        @type parameters: dict of param
        """
        try:
            userdn = threading.currentThread().session.contexts['base'].userdn
            user = (userdn, 'USER')
        except:
            # Get effective user id (log from a script)
            user = pwd.getpwuid(os.getuid())[0]
            user = user.decode('ascii')
            user = (user, 'SYSTEMUSER')
        try:
            useragent = threading.currentThread().session.http_headers['user-agent']
        except:
            useragent = sys.argv[0]
        try:
            host = threading.currentThread().session.http_headers['x-browser-ip']
        except:
            # FIXME: Maybe context.peer or something like that is better
            host = socket.getfqdn()
        initiator = (host, useragent)
        source = socket.getfqdn()
        return AuditRecordDB(self, module, event, user, objects, parameters, initiator, source, current, previous)
    
    def getLog(self, start, end, plug, user, type, date1, date2, object, action):
        """
        Allow to get all log
        return a dict of log
        see AuditReaderDB

        @param start: start of search
        @param end: end of search
        @param plug: plugin search
        @param user: searched user
        @param type: type of object searched
        @param date1: begin date
        @param date2: end date
        @param object: object name searched
        @param action: action name searched
        @type start: string
        @type end: string
        @type plug: string
        @type user: string
        @type type: string
        @type date1: string
        @type date2: string
        @type object: string
        @type action: string 
        """
        session = create_session()
        return AuditReaderDB(self, session).getLog(start, end, plug, user, type, date1, date2, object, action)
        
    def getLogById(self, id):
        """
        Allow to get a log by id in database
        @param id: id number in database
        @type id: int
        return a dict of a log 
        """
        session = create_session()
        return AuditReaderDB(self, session).getLogById(id)
    
    def getActionType(self, action, type):
        session = create_session()
        return AuditReaderDB(self, session).getActionType(action, type)
            
    def _initTableVersion(self):
        """
        Create the audit database version table
        """
        self.version_table = Table('version', self.metadata,
                                   Column('number', Integer, primary_key = True)
                                   )
    
    def databaseExists(self):
        """
        Return true if the audit database exists, i.e. the version table exists
        """
        return self.version_table.exists()

    def getCurrentVersion(self):
        """
        @returns: the current audit database schema version
        @rtype: int
        """
        session = create_session()
        version = session.query(Version).all()
        session.close()
        return version[0].number

    def getUptodateVersion(self):
        """
        @returns: the wanted audit database version for this code to works
        """
        return 1

    def checkVersion(self, version):
        return version == self.getUptodateVersion()

    def _updateDatabaseVersion(self, version = None):
        """
        Update database version number in the version table
        """
        if version == None:
            version = self.getUptodateVersion()
        session = create_session()
        session.execute(self.version_table.delete())
        session.close()
        v = Version()
        v.Number = version
        session.save(v)
        session.flush()

    def _initTablesmysqlV1(self):
        """
        Init MySQL table for audit database version 1
        """
        self.module_table = Table("module", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("name", String(15), nullable=False),
                            mysql_engine='InnoDB'
                            )

        self.event_table = Table("event", self.metadata, 
                            Column("id", Integer, primary_key=True, autoincrement=True),
                            Column("module_id", Integer, ForeignKey('module.id')),
                            Column("name", Unicode(50), nullable=False),
                            mysql_engine='InnoDB'
                            )
    
        self.source_table = Table("source", self.metadata,
                           Column("id", Integer, primary_key=True),
                           Column("hostname", String(20), nullable=False),
                           mysql_engine='InnoDB'
                           )
    
        self.param_table=Table("parameters", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("param_name", String(50)),
                            Column("param_value", String(1024)),
                            Column("record_id", Integer, ForeignKey('record.id')),
                            mysql_engine='InnoDB'
                            )
    
        self.initiator_table=Table("initiator", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("application", String(64), nullable=False),
                            Column("hostname", String(20), nullable=False),
                            mysql_engine='InnoDB'
                            )

        self.type_table=Table("type", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("type", String(20), nullable=False),
                            mysql_engine='InnoDB'
                            )

        self.object_table=Table("object", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("uri", String(255), nullable = False),
                            Column("type_id", Integer, ForeignKey('type.id')),
                            Column("parent", Integer, ForeignKey('object.id')),
                            mysql_engine='InnoDB'
                            )

        self.object_log_table=Table("object_log", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_id", Integer, ForeignKey('object.id')),
                            Column("record_id", Integer, ForeignKey('record.id')),
                            mysql_engine='InnoDB'
                            )
                            
        self.previous_value_table=Table("previous_value", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_log_id", Integer, ForeignKey('object_log.id')),
                            Column("value", String(1024)),
                            mysql_engine='InnoDB'
                            )
                            
        self.current_value_table=Table("current_value", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_log_id", Integer, ForeignKey('object_log.id')),
                            Column("value", String(1024)),
                            mysql_engine='InnoDB'
                            )
    
        self.record_table=Table("record", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("date", DateTime , default=func.now(), nullable=False),
                            Column("result", Boolean, nullable=False),
                            Column("initiator_id", Integer, ForeignKey('initiator.id'), nullable=False),
                            Column("source_id", Integer, ForeignKey('source.id'), nullable=False),
                            Column("event_id", Integer, ForeignKey('event.id'), nullable=False),
                            Column("module_id", Integer, ForeignKey('module.id'), nullable=False),
                            Column("user_id", Integer, ForeignKey('object.id'), nullable=False),
                            mysql_engine='InnoDB'
                            )

    def _initTablespostgresV1(self):
        """
        FIXME: to check
        PostgreSQL db tables for audit database version 1
        """        
        self.module_table = Table("module", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("name", String(15), nullable=False)
                            )

        self.event_table = Table("event", self.metadata, 
                            Column("id", Integer, primary_key=True, autoincrement=True),
                            Column("module_id", Integer, ForeignKey('module.id')),
                            Column("name", String(50), nullable=False)
                            )
    
        self.source_table = Table("source", self.metadata,
                           Column("id", Integer, primary_key=True),
                           Column("host", String(20), nullable=False)
                           )
    
        self.param_table=Table("parameters", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("param_name", String(50)),
                            Column("param_value", String(1024)),
                            Column("record_id", Integer, ForeignKey('log.id'))
                            )
    
        self.initiator_table=Table("initiator", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("application", String(64), nullable=False),
                            Column("host", String(20))
                            )

        self.type_table=Table("type", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("type", String(20), nullable=False)
                            )

        self.object_table=Table("object", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("_uri", String(30), nullable=False),
                            Column("type_id", Integer, ForeignKey('type.id')),
                            Column("parent", Integer, ForeignKey('object.id'))
                            )

        self.object_log_table=Table("object_log", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_id", Integer, ForeignKey('object.id')),
                            Column("record_id", Integer, ForeignKey('log.id'))
                            )
                            
        self.previous_value_table=Table("previous_value", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_log_id", Integer, ForeignKey('object_log.id')),
                            Column("value", String(1024))
                            )
                            
        self.current_value_table=Table("current_value", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_log_id", Integer, ForeignKey('object_log.id')),
                            Column("value", String(1024))
                            )
    
        self.record_table=Table("record", self.metadata,
                             Column("id", Integer, primary_key=True),
                             Column("date", DateTime, default=func.now(), nullable=False),
                             Column("result", Boolean, nullable=False),
                             Column("initiator_id", Integer, ForeignKey('initiator.id'), nullable=False),
                             Column("source_id", Integer, ForeignKey('source.id')),
                             Column("event_id", Integer),
                             Column("module_id", Integer),
                             Column("user_id", Integer, ForeignKey('object.id')),
                             ForeignKeyConstraint(('event_id', 'module_id'), ('event.id', 'event.module_id'))
                            )

    def _initMappersmysqlV1(self):
        """
        Init all mappers for audit database version 1
        """
        mapper(Event, self.event_table)
        mapper(Module, self.module_table)
        mapper(Source, self.source_table)
        mapper(Initiator, self.initiator_table)
        mapper(Type, self.type_table)
        mapper(Object, self.object_table)
        mapper(Object_Log, self.object_log_table)
        mapper(Current_Value, self.current_value_table)
        mapper(Previous_Value, self.previous_value_table)
        mapper(Record, self.record_table, properties = {'param_log' : relation(Parameters, backref='parameters'), 'obj_log' : relation(Object, secondary=self.object_log_table, lazy=False)})
        mapper(Parameters, self.param_table)
    # The SA mapper for PostgreSQL is the same than MySQL
    _initMapperspostgresV1 = _initMappersmysqlV1

    def _populateTablesmysqlV1(self):
        """
        Populate table for audit database version 1
        """
        t = Type()
        t.type = 'USER'
        session = create_session()
        session.save(t)
        session.flush()
    # The database population code is the same for PostgreSQL than MySQL
    _populateTablespostgresV1 = _populateTablesmysqlV1


class AuditWriterNull(Singleton, AuditWriterI):
    
    """
    Singleton class for an object that don't record any audit data.
    It is used when audit has not been configured.
    """

    def __init__(self):
        self.logger = logging.getLogger()
    
    def init(self,*args):
        pass
    
    def log(self,*args):
        return self
    
    def setup(self,*args):
        pass
    
    def get(self,*args):
        pass
    
    def getById(self,*args):
        pass

    def getLog(self, start, end, plug, user, type, date1, date2, object, action):
        pass

    def getLogById(self, id):
        pass

    def getActionType(self,*args):
        pass

    def commit(self,*args):
        pass

    def operation(self, op):
        self.logger.info("Configured audit database will do nothing")
        return True
