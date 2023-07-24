# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Contains singleton classes that writes to the audit backend
"""
# standard modules
import time

import socket
import sys
import os
import pwd
import threading

# SqlAlchemy
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy import (
    Table,
    Column,
    Integer,
    ForeignKey,
    String,
    Boolean,
    Unicode,
    DateTime,
    ForeignKeyConstraint,
    MetaData,
    create_engine,
)

from mmc.core.audit.classes import (
    Record,
    Module,
    Object,
    Object_Log,
    Event,
    Parameters,
    Initiator,
    Type,
    Source,
    Previous_Value,
    Current_Value,
    Version,
)
from mmc.core.audit.record import AuditRecordDB
from mmc.core.audit.readers import AuditReaderDB
from mmc.core.audit.writernull import AuditWriterI
from mmc.support.mmctools import Singleton


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
        dboptions = {}
        dburl = f"{self.config.auditdbdriver}://{self.config.auditdbuser}:{self.config.auditdbpassword}@{self.config.auditdbhost}:{str(self.config.auditdbport)}/{self.config.auditdbname}"
        if self.config.auditdbdriver == "mysql":
            dburl += "?charset=utf8&use_unicode=0"
            dboptions = {"pool_recycle": 3600, "convert_unicode": True}
        db = create_engine(dburl, **dboptions)

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
            raise Exception(
                "Bad audit database schema. Version %d found. Please update the database schema to version %d."
                % (version, self.getUptodateVersion())
            )
        self._initTables()
        self._initMappers()

    def _initTables(self, version=None):
        """
        Init database tables.
        """
        if version is None:
            version = self.getUptodateVersion()
        getattr(self, f"_initTables{self.config.auditdbdriver}V{str(version)}")()

    def _initMappers(self, version=None):
        """
        Init database mappers.
        """
        if version is None:
            version = self.getUptodateVersion()
        getattr(self, f"_initMappers{self.config.auditdbdriver}V{str(version)}")()

    def _populateTables(self, version=None):
        """
        Populate tables before the first use.
        """
        if version is None:
            version = self.getUptodateVersion()
        getattr(self, f"_populateTables{self.config.auditdbdriver}V{str(version)}")()

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
        if op == "drop":
            if self.config.auditdbdriver == "mysql":
                print("-- Execute the following lines into the MySQL client")
                print(f"DROP DATABASE IF EXISTS {self.config.auditdbname};")
                print(f"DROP USER '{self.config.auditdbuser}'@localhost;")
            elif self.config.auditdbdriver == "postgres":
                # FIXME: Do it for PostgreSQL too
                print("Not yet implemented")
            else:
                self.logger.error(
                    f"SQL driver '{self.config.auditdbdriver}' is not supported"
                )
                return False
        elif op == "droptables":
            if not self.databaseExists():
                self.logger.error("Database does not exist")
                return False
            version = self.getCurrentVersion()
            self._initTables(version)
            self._initMappers(version)
            self.logger.info("Dropping audit tables as requested")
            self.metadata.drop_all()
            self.logger.info("Done")
        elif op == "create":
            if self.config.auditdbdriver == "mysql":
                print("-- Execute the following lines into the MySQL client")
                print(
                    f"CREATE DATABASE {self.config.auditdbname} DEFAULT CHARSET utf8;"
                )
                print(
                    f"GRANT ALL PRIVILEGES ON {self.config.auditdbname}.* TO '{self.config.auditdbuser}'@localhost IDENTIFIED BY '{self.config.auditdbpassword}';"
                )
                print("FLUSH PRIVILEGES;")
            elif self.config.auditdbdriver == "postgres":
                # FIXME: Do it for PostgreSQL too
                print("Not yet implemented")
            else:
                self.logger.error(
                    f"SQL driver '{self.config.auditdbdriver}' is not supported"
                )
                return False
        elif op == "init":
            if self.databaseExists():
                self.logger.info("Database already exist")
                return True
            self.logger.info("Creating audit tables as requested")
            self.logger.info(
                "Using database schema version %d" % self.getUptodateVersion()
            )
            self._initTables()
            self._initMappers()
            self.metadata.create_all()
            self._populateTables()
            self._updateDatabaseVersion()
            self.logger.info("Done")
        elif op == "check":
            ret = False
            if self.databaseExists():
                version = self.getCurrentVersion()
                uptodate = self.getUptodateVersion()
                self.logger.info("Current database schema version: %d" % version)
                if version == uptodate:
                    self.logger.info("Database schema version is up to date")
                    ret = True
                elif version < uptodate:
                    self.logger.info("Database schema should be updated")
                else:
                    self.logger.info(
                        "Unknown database schema version number. This sofware may need to be updated."
                    )
            return ret
        elif op == "list":
            self._initTables()
            self._initMappers()
            [nb, records] = self.getLog(0, 0, 0, 0, 0, 0, 0, 0, 0)
            if nb > 0:
                self.logger.info("List all audit records.")
                print(
                    "Date".ljust(19)
                    + "\t"
                    + "User".ljust(50)
                    + "\t"
                    + "Event".ljust(25)
                    + "\t"
                    + "Plugin".ljust(15)
                    + "\t"
                    + "Result"
                )
                for record in records:
                    print(
                        record["date"]
                        + "\t"
                        + record["user"].ljust(50)
                        + "\t"
                        + record["action"].ljust(25)
                        + "\t"
                        + record["plugin"].ljust(15)
                        + "\t"
                        + str(record["commit"])
                    )
            else:
                self.logger.info("No audit record in the database.")
            return True
        elif op == "purge":
            pass
        elif op != "archive":
            return False

        return True

    def log(
        self, module, event, objects=[], current=None, previous=None, parameters={}
    ):
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
        ## Mutable list objects used as default argument to a method or function
        # objects = objects or []
        ## Mutable dict parameters used as default argument to a method or function
        # parameters = parameters or {}
        try:
            userdn = threading.currentThread().session.contexts["base"].userdn
            user = (userdn, "USER")
        except:
            # Get effective user id (log from a script)
            user = pwd.getpwuid(os.getuid())[0]
            user = user.decode("ascii")
            user = (user, "SYSTEMUSER")
        try:
            useragent = threading.currentThread().session.http_headers["user-agent"]
        except:
            useragent = sys.argv[0]
        try:
            host = threading.currentThread().session.http_headers["x-browser-ip"]
        except:
            # FIXME: Maybe context.peer or something like that is better
            host = socket.getfqdn()
        initiator = (host, useragent)
        source = socket.getfqdn()
        return AuditRecordDB(
            self,
            module,
            event,
            user,
            objects,
            parameters,
            initiator,
            source,
            current,
            previous,
        )

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
        return AuditReaderDB(self, session).getLog(
            start, end, plug, user, type, date1, date2, object, action
        )

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
        self.version_table = Table(
            "version", self.metadata, Column("number", Integer, primary_key=True)
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
        return 2

    def checkVersion(self, version):
        return version == self.getUptodateVersion()

    def _updateDatabaseVersion(self, version=None):
        """
        Update database version number in the version table
        """
        if version is None:
            version = self.getUptodateVersion()
        session = create_session()
        session.execute(self.version_table.delete())
        session.close()
        v = Version()
        v.number = version
        session.add(v)
        session.flush()

    def _initTablesmysqlV2(self):
        """
        Init MySQL table for audit database version 2
        """
        nowsystem = time.strftime("%Y-%m-%d %H:%M:%S")
        self.module_table = Table(
            "module",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(15), nullable=False),
            mysql_engine="InnoDB",
        )

        self.event_table = Table(
            "event",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("module_id", Integer, ForeignKey("module.id")),
            Column("name", Unicode(50), nullable=False),
            mysql_engine="InnoDB",
        )

        self.source_table = Table(
            "source",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("hostname", String(32), nullable=False),
            mysql_engine="InnoDB",
        )

        self.param_table = Table(
            "parameters",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("param_name", String(50)),
            Column("param_value", String(1024)),
            Column("record_id", Integer, ForeignKey("record.id")),
            mysql_engine="InnoDB",
        )

        self.initiator_table = Table(
            "initiator",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("application", String(64), nullable=False),
            Column("hostname", String(32), nullable=False),
            mysql_engine="InnoDB",
        )

        self.type_table = Table(
            "type",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("type", String(20), nullable=False),
            mysql_engine="InnoDB",
        )

        self.object_table = Table(
            "object",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("uri", String(255), nullable=False),
            Column("type_id", Integer, ForeignKey("type.id")),
            Column("parent", Integer, ForeignKey("object.id")),
            mysql_engine="InnoDB",
        )

        self.object_log_table = Table(
            "object_log",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("object_id", Integer, ForeignKey("object.id")),
            Column("record_id", Integer, ForeignKey("record.id")),
            mysql_engine="InnoDB",
        )

        self.previous_value_table = Table(
            "previous_value",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("object_log_id", Integer, ForeignKey("object_log.id")),
            Column("value", String(1024)),
            mysql_engine="InnoDB",
        )

        self.current_value_table = Table(
            "current_value",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("object_log_id", Integer, ForeignKey("object_log.id")),
            Column("value", String(1024)),
            mysql_engine="InnoDB",
        )

        self.record_table = Table(
            "record",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("date", DateTime, default=nowsystem, nullable=False),
            Column("result", Boolean, nullable=False),
            Column("initiator_id", Integer, ForeignKey("initiator.id"), nullable=False),
            Column("source_id", Integer, ForeignKey("source.id"), nullable=False),
            Column("event_id", Integer, ForeignKey("event.id"), nullable=False),
            Column("module_id", Integer, ForeignKey("module.id"), nullable=False),
            Column("user_id", Integer, ForeignKey("object.id"), nullable=False),
            mysql_engine="InnoDB",
        )

    def _initTablespostgresV2(self):
        """
        FIXME: to check
        PostgreSQL db tables for audit database version 2
        """
        nowsystem = time.strftime("%Y-%m-%d %H:%M:%S")
        self.module_table = Table(
            "module",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(15), nullable=False),
        )

        self.event_table = Table(
            "event",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("module_id", Integer, ForeignKey("module.id")),
            Column("name", String(50), nullable=False),
        )

        self.source_table = Table(
            "source",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("hostname", String(32), nullable=False),
        )

        self.param_table = Table(
            "parameters",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("param_name", String(50)),
            Column("param_value", String(1024)),
            Column("record_id", Integer, ForeignKey("log.id")),
        )

        self.initiator_table = Table(
            "initiator",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("application", String(64), nullable=False),
            Column("hostname", String(32)),
        )

        self.type_table = Table(
            "type",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("type", String(20), nullable=False),
        )

        self.object_table = Table(
            "object",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("_uri", String(30), nullable=False),
            Column("type_id", Integer, ForeignKey("type.id")),
            Column("parent", Integer, ForeignKey("object.id")),
        )

        self.object_log_table = Table(
            "object_log",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("object_id", Integer, ForeignKey("object.id")),
            Column("record_id", Integer, ForeignKey("log.id")),
        )

        self.previous_value_table = Table(
            "previous_value",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("object_log_id", Integer, ForeignKey("object_log.id")),
            Column("value", String(1024)),
        )

        self.current_value_table = Table(
            "current_value",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("object_log_id", Integer, ForeignKey("object_log.id")),
            Column("value", String(1024)),
        )

        self.record_table = Table(
            "record",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("date", DateTime, default=nowsystem, nullable=False),
            Column("result", Boolean, nullable=False),
            Column("initiator_id", Integer, ForeignKey("initiator.id"), nullable=False),
            Column("source_id", Integer, ForeignKey("source.id")),
            Column("event_id", Integer),
            Column("module_id", Integer),
            Column("user_id", Integer, ForeignKey("object.id")),
            ForeignKeyConstraint(
                ("event_id", "module_id"), ("event.id", "event.module_id")
            ),
        )

    def _initMappersmysqlV2(self):
        """
        Init all mappers for audit database version 2
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
        mapper(
            Record,
            self.record_table,
            properties={
                "param_log": relation(Parameters, backref="parameters"),
                "obj_log": relation(
                    Object, secondary=self.object_log_table, lazy=False
                ),
            },
        )
        mapper(Parameters, self.param_table)

    # The SA mapper for PostgreSQL is the same than MySQL
    _initMapperspostgresV2 = _initMappersmysqlV2

    def _populateTablesmysqlV2(self):
        """
        Populate table for audit database version 2
        """
        t = Type()
        t.type = "USER"
        session = create_session()
        session.add(t)
        session.flush()

    # The database population code is the same for PostgreSQL than MySQL
    _populateTablespostgresV2 = _populateTablesmysqlV2
