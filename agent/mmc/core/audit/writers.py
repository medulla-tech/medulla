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

import socket
import sys
import os
import pwd
import logging

# SqlAlchemy
from sqlalchemy import *
from sqlalchemy import exceptions
from sqlalchemy.orm import *

from mmc.core.audit.classes import *
from mmc.core.audit.record import *
from mmc.core.audit.readers import AuditReaderDB
from mmc.support.mmctools import Singleton


class AuditWriterI:
    """
    Interface for LogAction*
    """    
    def log(self):
        pass
    
    def setup(self):
        pass

    def get(self):
        pass

    def get_by_Id(self):
        pass

    def get_action_type(self):
        pass

    def commit(self):
        pass

class AuditWriterDB(Singleton, AuditWriterI):
    
    def __init__(self):
        """
        Init Object AuditWriterDB self.fqdn contains the agent hostname
        """
        Singleton.__init__(self)
        self.fqdn = socket.getfqdn()

    def setConfig(self, config):
        self.config = config

    def connect(self):
        """
        Prepare database connection
        """
        db = create_engine(self.config.logdbdriver + "://" + self.config.logdbuser + ":" + self.config.logdbpassword + "@" + self.config.logdbhost + ":" + self.config.logdbport + "/" + self.config.logdbname)
        self.metadata = MetaData()
        self.metadata.bind = db
        self.initTableVersion()
        mapper(Version, self.version_table)

    def init(self, driver, user, passwd, host, port, name):
        """
        This function init database connexion
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
        self.initTables()
        self.initMappers()

    def initTables(self, version = None):
        if version == None:
            version = self.getUptodateVersion()
        func = getattr(self, "initTables" + self.config.logdbdriver + "V" + str(version))
        func()

    def initMappers(self, version = None):
        if version == None:
            version = self.getUptodateVersion()
        func = getattr(self, "initMappers" + self.config.logdbdriver + "V" + str(version))
        func()

    def populateTables(self, version = None):
        if version == None:
            version = self.getUptodateVersion()
        func = getattr(self, "populateTables" + self.config.logdbdriver + "V" + str(version))
        func()        

    def operation(self, op):
        """
        Allow to perform special operations on the audit database

        if op == 'drop', drop all tables.
        if op == 'init', initialize the audit database.
        """
        self.logger = logging.getLogger()
        self.connect()
        if op == 'dropdb':
            if not self.databaseExists():
                self.logger.error('Database does not exist')
                return False
            version = self.getCurrentVersion()
            self.initTables(version)
            self.initMappers(version)
            self.logger.info('Dropping audit tables as requested')
            self.metadata.drop_all()
            self.logger.info('Done')
        elif op == 'initdb':
            if self.databaseExists():
                self.logger.error('Database already exist')
                return False
            self.logger.info('Creating audit tables as requested')
            self.logger.info('Using database schema version %d' % self.getUptodateVersion())
            self.initTables()
            self.initMappers()
            self.metadata.create_all()
            self.populateTables()
            self.updateDatabaseVersion()
            self.logger.info('Done')
        elif op == 'checkdb':
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
        elif op == 'purgedb':
            pass
        elif op == 'archivedb':
            pass
        return True

    def log(self, module, action, context = None, objects = None, current=None, previous=None, parameters = None):
        """
        Allow to log an Action, it uses LogRecordDB

        @param context: current context object, should contain the current
                        user id, etc.
        @type context: Twisted session object
        
        @param module: module name
        @type moude: str

        @param action: action name
        @type action: string

        @param objects
        @type objects: tuple of (<object_name>,<type>)

        @param current: current attribute value saved in database
        @type current: string

        @param previous: previous attribute value stored in Ldap 
        @type previous: string

        @param parameters: list of parameters (get with the locals() builtin)
        @type parameters: dict of param
        """
        
        session = create_session()
        # Use context information for the log record
        try:
            user = context.userid
        except:
            # Get effective user id (log from a script)
            user = pwd.getpwuid(os.getuid())[0]
        try:
            useragent = context.http_headers['user-agent']
        except:
            useragent = sys.argv[0]
        try:
            host = context.http_headers['x-browser-ip']
        except:
            # FIXME: maybe context.peer or something like that
            host = socket.getfqdn()
        client = (host, useragent)
        agent = socket.getfqdn()
        return AuditRecordDB(self, session, action, module, user, objects, parameters, client, agent, current, previous)
    
    def get(self, start, end, plug, user, type, date1, date2, object, action):
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
        return AuditReaderDB(self, session).getlog(start, end, plug, user, type, date1, date2, object, action)
        
    def get_by_Id(self,id):
        """
        Allow to get a log by id in database
        @param id: id number in database
        @type id: int
        return a dict of a log 
        """
        session = create_session()
        return AuditReaderDB(self, session).get_by_Id(id)
    
    def get_action_type(self,action,type):
        """
        Return a list of action and type if action=1 it return list of action
        if type=1 it return a list of type
        @param action: if action=1 the function return a list of action
        @type action: int
        @param type: if type=1 the function return a list of action
        @type type: int
        """
        session = create_session()
        return AuditReaderDB(self, session).get_action_type(action, type)
            
            
    def initTableVersion(self):
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
        @returns: the wanted audit database version
        """
        return 1

    def checkVersion(self, version):
        return version == self.getUptodateVersion()

    def updateDatabaseVersion(self, version = None):
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

    def initTablesmysqlV1(self):
        """
        Init MySQL table for audit database version 1
        """
        self.module_table = Table("module", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("module_name", String(15)),
                            mysql_engine='InnoDB'
                            )

        self.action_table = Table("action", self.metadata, 
                            Column("id", Integer, primary_key=True,autoincrement=False),
                            Column("module_id", Integer, ForeignKey('module.id'),primary_key=True),
                            Column("action_details", String(50)),
                            mysql_engine='InnoDB'
                            )
    
        self.agent_table = Table("agent", self.metadata,
                           Column("id", Integer, primary_key=True),
                           Column("agent_host", String(20)),
                           mysql_engine='InnoDB'
                           )
    
        self.param_table=Table("parameters", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("param_name", String(50)),
                            Column("param_value", String(1024)),
                            Column("log_id", Integer, ForeignKey('log.id')),
                            mysql_engine='InnoDB'
                            )
    
        self.client_table=Table("client", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("client_type", String(64)),
                            Column("client_host", String(20)),
                            mysql_engine='InnoDB'
                            )

        self.type_table=Table("type", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("type", String(20)),
                            mysql_engine='InnoDB'
                            )

        self.object_table=Table("object", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_name", String(30)),
                            Column("type_id", Integer, ForeignKey('type.id')),
                            Column("parent", Integer, ForeignKey('object.id')),

                            mysql_engine='InnoDB'
                            )

        self.object_log_table=Table("object_log", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_id", Integer, ForeignKey('object.id')),
                            Column("log_id", Integer, ForeignKey('log.id')),
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
    
        self.log_table=Table("log", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("log_date", DateTime ,default=func.now()),
                            Column("result", Boolean),
                            Column("client_id", Integer, ForeignKey('client.id')),
                            Column("agent_id", Integer, ForeignKey('agent.id')),
                            Column("action_id", Integer, ForeignKey('action.id')),
                            Column("module_id", Integer, ForeignKey('module.id')),
                            Column("object_user_id", Integer, ForeignKey('object.id')),
                            
                            mysql_engine='InnoDB'
                            )

    def initTablespostgresV1(self):
        """
        FIXME: to check
        PostgreSQL db tables for audit database version 1
        """        
        self.module_table = Table("module", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("module_name", String(15))
                            )

        self.action_table = Table("action", self.metadata, 
                            Column("id", Integer, primary_key=True,autoincrement=False),
                            Column("module_id", Integer, ForeignKey('module.id'),primary_key=True),
                            Column("action_details", String(50))
                            )
    
        self.agent_table = Table("agent", self.metadata,
                           Column("id", Integer, primary_key=True),
                           Column("agent_host", String(20))
                           )
    
        self.param_table=Table("parameters", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("param_name", String(50)),
                            Column("param_value", String(1024)),
                            Column("log_id", Integer, ForeignKey('log.id'))
                            )
    
        self.client_table=Table("client", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("client_type", String(64)),
                            Column("client_host", String(20))
                            )

        self.type_table=Table("type", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("type", String(20))
                            )

        self.object_table=Table("object", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_name", String(30)),
                            Column("type_id", Integer, ForeignKey('type.id')),
                            Column("parent", Integer, ForeignKey('object.id'))
                            )

        self.object_log_table=Table("object_log", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("object_id", Integer, ForeignKey('object.id')),
                            Column("log_id", Integer, ForeignKey('log.id'))
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
    
        self.log_table=Table("log", self.metadata,
                             Column("id", Integer, primary_key=True),
                             Column("log_date", DateTime ,default=func.now()),
                             Column("result", Boolean),
                             Column("client_id", Integer, ForeignKey('client.id')),
                             Column("agent_id", Integer, ForeignKey('agent.id')),
                             Column("action_id", Integer),
                             Column("module_id", Integer),
                             Column("object_user_id", Integer, ForeignKey('object.id')),
                             ForeignKeyConstraint(('action_id', 'module_id'), ('action.id', 'action.module_id'))
                            )

    def initMappersmysqlV1(self):
        """
        Init all mappers for audit database version 1
        """
        mapper(Action, self.action_table)
        mapper(Module, self.module_table)
        mapper(Agent, self.agent_table)
        mapper(Client, self.client_table)
        mapper(Type, self.type_table)
        mapper(Object, self.object_table)
        mapper(Object_Log, self.object_log_table)
        mapper(Current_Value, self.current_value_table)
        mapper(Previous_Value, self.previous_value_table)
        mapper(Log,self.log_table, properties = {'param_log' : relation(Parameters, backref='parameters'), 'obj_log' : relation(Object, secondary=self.object_log_table, lazy=False)})
        mapper(Parameters, self.param_table)
    initMapperspostgresV1 = initMappersmysqlV1

    def populateTablesmysqlV1(self):
        """
        Populate table for audit database version 1
        """
        t = Type()
        t.type = 'USER'
        session = create_session()
        session.save(t)
        session.flush()
    populateTablespostgresV1 = populateTablesmysqlV1

    def _get_session(self):
        return create_session()


class AuditWriterNull(Singleton, AuditWriterI):
    
    """
    Will log nothing
    """
    
    def init(self,*args):
        pass
    
    def log(self,*args):
        return self
    
    def setup(self,*args):
        pass
    
    def get(self,*args):
        pass
    
    def get_by_Id(self,*args):
        pass

    def get_action_type(self,*args):
        pass

    def commit(self,*args):
        pass

    def operation(self, op):
        pass
