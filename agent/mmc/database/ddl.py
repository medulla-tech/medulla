#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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
#
"""
This module is a DDL provider to control the schema updates
and database version checkings.
"""
import os
import re
import logging
from subprocess import Popen, PIPE
import MySQLdb

from mmc.site import prefix


SCHEMA_MASK = "schema-xxx.sql"


# This logger is created only for the case when this module
# is called as standallone.
# (usualy is called by pulse2-setup with a passed logger)
def myLogger():
    """ Default logging instance """
    log = logging.getLogger("DDL")
    handler = logging.StreamHandler()
    log.addHandler(handler)
    return log


class DBEngine:
    def __init__(self, user, passwd, host, db, port=None, log=None):
        """
        @param user: database user
        @type user: str

        @param passwd: database password
        @type passwd: str

        @param host: hostname or IP address of database machine
        @type host: str

        @param db: database name
        @type db: str

        @param port: database port
        @type port: int

        @param log: logger instance
        @type log: object
        """
        self.user = user
        self.host = host
        self.passwd = passwd
        self.db = db
        self.port = port or 3306
        self.conn = None
        self.log = log or myLogger()
        try:
            self.conn = MySQLdb.connect(user=self.user,
                                        passwd=self.passwd,
                                        host=self.host,
                                        port=self.port,
                                        db=self.db)
        except Exception, exc:
            self.log.error("Can't connect to the database: %s" % str(exc))
            return None

    def cursor(self):
        """
        @return: dataset cursor
        @rtype: object
        """
        try:
            return self.conn.cursor()
        except Exception, exc:
            self.log.error("Error while creating cursor: %s" % str(exc))

    def __del__(self):
        """ Closing the session """
        if self.conn:
            self.conn.close()


class DBScriptLaunchInterface:
    """To launch a SQL script, we need the command line mysql executable"""

    def __init__(self, user, passwd, host, port, db, log=None):
        """
        @param user: database user
        @type user: str

        @param passwd: database password
        @type passwd: str

        @param host: hostname or IP address of database machine
        @type host: str

        @param port: database port
        @type port: int

        @param db: database name
        @type db: str

        @param log: logger instance
        @type log: object
        """
        self.log = log or myLogger()
        self.cmd = "mysql %s -u%s -h%s" % (db, user, host)
        if len(passwd) > 0:
            self.cmd += " -p%s" % passwd
        if port:
            self.cmd += " -P%d" % port

    def execute(self, filename):
        """
        Executing the SQL script.

        @param filename: script to execute
        @type filename: str
        """
        process = Popen(self.cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
        try:
            ret, err = process.communicate('source ' + filename)
            if err:
                self.log.error("Error while execute script '%s': %s" % (filename, err))
                return None
            return ret
        except Exception, exc:
            self.log.error("Error while execute script '%s': %s" % (filename, str(exc)))
            return None


class DDLContentManager:
    """ Class to manage DDL scripts content """

    # ommitting of checking the following databases :
    blacklisted_databases = ("glpi")

    def __init__(self, log=None):
        """
        @param log: logger instance
        @type log: logger object
        """
        self.log = log or myLogger()

    @classmethod
    def get_script_number(cls, filename):
        """
        Extract the number of script from filename

        @param filename: filename containing a number to extract
        @type filename: str

        @return: number of script in fix format xxx
        @rtype: str
        """
        numbers = re.findall(r'\d{3}', '%s' % filename)
        if len(numbers) == 1:
            return numbers[0]
        else:
            return None

    @classmethod
    def is_schema_builder(cls, filename):
        """
        Returns true if the filename is a schema script.

        @param filename: name of file from script folder
        @type filename: str

        @return: true if the filename is a schema script
        @rtype: bool
        """
        number = cls.get_script_number(filename)
        if number:
            return filename.replace(number, "xxx") == SCHEMA_MASK
        return False

    def get_scripts(self, module, fullpath=False):
        """
        Get a list of scripts to install assigned on module.

        @param module: directory name (=database name)
        @type module: str

        @param fullpath: if true, returns filenames with absolute path,
                         otherwise only filenames
        @type fullpath: bool

        @return: list generator of filenames
        @rtype: string
        """
        sqldirs = [os.path.join(prefix, 'share', 'mmc', 'sql', module),
                   os.path.join(prefix, 'share', 'doc', 'mmc', 'contrib', module, 'sql')]
        found = False
        for sqldir in sqldirs:
            if os.path.exists(sqldir):
                found = True
                break
        if not found:
            raise Exception("SQL schemas not found for module %s" % module)

        # get only schema scripts - schema-xxx.sql
        scripts = [s for s in os.listdir(sqldir) if self.is_schema_builder(s)]

        for script in sorted(scripts):
            if fullpath:
                yield os.path.join(sqldir, script)
            else:
                yield script

    def get_version(self, module):
        """
        Getting the last schema version on SQL folder.

        @param module: folder name (=database name)
        @type module: str

        @return: last schema version to install
        @rtype: int
        """
        if module.lower() in self.blacklisted_databases:
            return -1

        scripts = self.get_scripts(module)
        numbers = [int(self.get_script_number(s)) for s in scripts]
        return max(numbers)


class DBControl:
    """ Main base to check and update the database """

    def __init__(self, user, passwd, host, port,
                 module, log=None, use_same_db=False):
        """
        @param user: database user
        @type user: str

        @param passwd: database password
        @type passwd: str

        @param host: hostname or IP address of database machine
        @type host: str

        @param port: database port
        @type port: int

        @param module: database name
        @type module: str

        @param log: logger instance
        @type log: object

        @param use_same_db: If True, same database used, otherwise "mysql"
        @type use_same_db: bool
        """

        self.log = log or myLogger()

        if use_same_db:
            db = module
        else:
            db = "mysql"
        self.db = DBEngine(user,
                           passwd,
                           host,
                           db,
                           port=port,
                           log=log)

        self.module = module
        self.ddl_manager = DDLContentManager(log)
        self.script_manager = DBScriptLaunchInterface(user,
                                                      passwd,
                                                      host,
                                                      port,
                                                      module,
                                                      log)

    @property
    def db_exists(self):
        """
        Test if database exists.

        @return: True if database exists
        @rtype: bool
        """
        statement = "SELECT 1 FROM information_schema.schemata"
        statement += " WHERE schema_name = '%s';" % self.module
        c = self.db.cursor()
        c.execute(statement)
        if len(c.fetchall()) == 1:
            return True
        return False

    def _get_version_table_name(self):
        """
        Some databases are the different cases of 'version' table name.

        @return: table name (Version|version)
        @rtype: str
        """
        statement = "SELECT table_name FROM information_schema.tables "
        statement += "WHERE UPPER(table_name) = 'VERSION' "
        statement += "  AND table_schema = '%s';" % self.module

        c = self.db.cursor()
        c.execute(statement)
        dataset = c.fetchall()
        if len(dataset) == 1:
            return dataset[0][0]
        return False

    @property
    def db_version(self):
        """
        Getting of version installed in database.

        @return: database version
        @rtype: int
        """
        table_name = self._get_version_table_name()
        statement = "SELECT Number FROM %s.%s;" % (self.module, table_name)
        c = self.db.cursor()
        c.execute(statement)
        dataset = c.fetchall()
        if len(dataset) == 1:
            return dataset[0][0]
        return False

    def _db_create(self):
        """ Creating the database """
        statement = "CREATE DATABASE %s;" % self.module
        c = self.db.cursor()
        c.execute(statement)

    def _get_scripts_to_install(self, version_in_db, version_to_install):
        """
        Get all the scripts needed to processing the upgrade.

        @param version_in_db: installed version
        @type version_in_db: int

        @param version_to_install: proposed version
        @type version_to_install: int

        @return: generator of paths of scripts to install
        @rtype: string
        """

        version_slice = range(version_in_db + 1, version_to_install + 1)

        for script in self.ddl_manager.get_scripts(self.module, fullpath=True):
            script_number = self.ddl_manager.get_script_number(script)
            if script_number:
                version = int(script_number)
                if version in version_slice:
                    self.log.debug("Installing schema version: v.%s" % (script_number))
                    yield script

    def process(self):
        """ Processing all the actions """
        version_to_install = self.ddl_manager.get_version(self.module)
        if not self.db_exists:
            self._db_create()
            version_in_db = 0
        else:
            version_in_db = self.db_version

        if version_in_db == version_to_install:
            self.log.debug("Database '%s' is up-to-date" % (self.module))
            return True

        elif version_in_db < version_to_install:
            self.log.info("'%s' database updated from version %d to %d" %
                          (self.module, version_in_db, version_to_install))
            scripts = self._get_scripts_to_install(version_in_db,
                                                   version_to_install)
            for script in scripts:
                if self.script_manager.execute(script) is None:
                    if self.module == 'dyngroup':
                        self.log.warn('Dyngroup known issue: Maybe your SQL engine is MyISAM, you can check with: SHOW TABLE STATUS')
                        self.log.warn('Here is SQL request who will help you to convert from MyISAM to InnoBD engine:')
                        self.log.warn('SELECT CONCAT("ALTER TABLE ",table_schema,".",table_name," ENGINE=InnoDB;") FROM information_schema.tables WHERE table_schema="dyngroup";')
                    return False
            return True
        else:
            self.log.error("Database '%s' version conflict" % self.module)
            self.log.error("Installed version is %d, but you are trying to install the version %d." %
                           (self.module, version_in_db, version_to_install))
            return False
