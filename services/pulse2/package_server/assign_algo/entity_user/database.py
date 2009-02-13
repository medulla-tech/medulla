#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: __init__.py 3 2008-03-03 14:35:11Z cdelfosse $
#
# This file is part of MMC.
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from pulse2.package_server.assign_algo.terminal_type.config import PluginInventoryAAConfig
from pulse2.package_server.utilities import Singleton
from sqlalchemy import *
import sqlalchemy
import logging

SA_MAYOR = 0
SA_MINOR = 3

NB_DB_CONN_TRY = 2

def create_method(m):
    def method(self, already_in_loop = False):
        ret = None
        try:
            old_m = getattr(Query, '_old_'+m)
            ret = old_m(self)
        except exceptions.SQLError, e:
            if e.orig.args[0] == 2013 and not already_in_loop: # Lost connection to MySQL server during query error
                logging.getLogger().warn("SQLError Lost connection (%s) trying to recover the connection" % m)
                for i in range(0, NB_DB_CONN_TRY):
                    new_m = getattr(Query, m)
                    ret = new_m(self, True)
            if ret:
                return ret
            raise e
        return ret
    return method

for m in ['first', 'count', 'all']:
    try:
        getattr(Query, '_old_'+m)
    except AttributeError:
        setattr(Query, '_old_'+m, getattr(Query, m))
        setattr(Query, m, create_method(m))

class DbObject(object):
    def toH(self):
        ret = {}
        for i in filter(lambda f: not f.startswith('_'), dir(self)):
            t = type(getattr(self, i))
            if t == str or t == dict or t == unicode or t == tuple or t == int or t == long:
                ret[i] = getattr(self, i)
        ret['uuid'] = toUUID(getattr(self, 'id'))
        return ret 

class PluginInventoryAADatabase(Singleton):
    def db_check(self):
        if not self.__checkSqlalchemy():
            self.logger.error("Sqlalchemy version error : is not %s.%s.* version" % (SA_MAYOR, SA_MINOR))
            return False
            
        conn = self.connected()
        if conn:
            self.logger.error("Can't connect to database (s=%s, p=%s, b=%s, l=%s, p=******). Please check inventory.ini." % (self.config.dbhost, self.config.dbport, self.config.dbbase, self.config.dbuser))
            return False

        return True

    def __checkSqlalchemy(self):
        try:
            import sqlalchemy
            a_version = sqlalchemy.__version__.split('.')
            if len(a_version) > 2 and str(a_version[0]) == str(SA_MAYOR) and str(a_version[1]) == str(SA_MINOR):
                return True
        except:
            pass
        return False

    def activate(self, conffile = None):
        self.logger = logging.getLogger()
        self.config = PluginInventoryAAConfig()
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, convert_unicode=True)
        self.metadata = BoundMetaData(self.db)
        self.initMappers()
        self.metadata.create_all()
        self.dbversion = self.getInventoryDatabaseVersion()

    def connected(self):
        try:
            if (self.db != None) and (session != None):
                return True
            return False
        except:
            return False

    def makeConnectionPath(self):
        """
        Build and return the db connection path according to the plugin configuration

        @rtype: str
        """
        if self.config.dbport:
            port = ":" + str(self.config.dbport)
        else:
            port = ""
        url = "%s://%s:%s@%s%s/%s" % (self.config.dbdriver, self.config.dbuser, self.config.dbpasswd, self.config.dbhost, port, self.config.dbname)
        if self.config.dbsslenable:
            url = url + "?ssl_ca=%s&ssl_key=%s&ssl_cert=%s" % (self.config.dbsslca, self.config.dbsslkey, self.config.dbsslcert)
        return url

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the inventory database
        """
        self.table = {}
        self.klass = {}

        self.version = Table("Version", self.metadata, autoload = True)
        self.machine = Table("Machine", self.metadata, autoload = True)
        self.inventory = Table("Inventory", self.metadata, autoload = True)

        noms = {'Registry':['Path']}
        for item in ['Registry']:
            # Declare the SQL table
            self.table[item] = Table(item, self.metadata, autoload = True)
            # Create the class that will be mapped
            # This will create the Bios, BootDisk, etc. classes
            exec "class %s(DbObject): pass" % item
            self.klass[item] = eval(item)
            # Map the python class to the SQL table
            mapper(self.klass[item], self.table[item])
            
            # Declare the has* SQL table
            hasitem = "has" + item
            has_columns = [
                          Column("machine", Integer, ForeignKey("Machine.id"), primary_key=True),
                          Column("inventory", Integer, ForeignKey("Inventory.id"), primary_key=True),
                          Column(item.lower(), Integer, ForeignKey(item + ".id"), primary_key=True)
                          ]

            # Declare the nom* SQL table
            for nom in noms[item]:
                nomitem = "nom" + item + nom
                self.table[nomitem] = Table(nomitem, self.metadata, autoload = True)
                # add the needed column in hasTable
                has_columns.append(Column(nom.lower(), Integer, ForeignKey(nomitem + ".id"), primary_key=True))
                # Create the class that will be mapped
                # This will create the hasBios, hasBootDisk, etc. classes
                exec "class %s(object): pass" % nomitem
                self.klass[nomitem] = eval(nomitem)
                # Map the python class to the SQL table
                mapper(eval(nomitem), self.table[nomitem])
               
            self.table[hasitem] = Table(hasitem, self.metadata, *has_columns)
            
            # Create the class that will be mapped
            # This will create the hasBios, hasBootDisk, etc. classes
            exec "class %s(object): pass" % hasitem
            self.klass[hasitem] = eval(hasitem)
            # Map the python class to the SQL table
            mapper(eval(hasitem), self.table[hasitem])

        mapper(Machine, self.machine)
        mapper(InventoryTable, self.inventory)

    def enableLogging(self, level = None):
        """
        Enable log for sqlalchemy.engine module using the level configured by the db_debug option of the plugin configuration file.
        The SQL queries will be loggued.
        """
        if not level:
            level = logging.INFO
        logging.getLogger("sqlalchemy.engine").setLevel(level)

    def disableLogging(self):
        """
        Disable log for sqlalchemy.engine module
        """
        logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

    def getInventoryDatabaseVersion(self):
        """
        Return the inventory database version.
        We don't use this information for now, but if we can get it this means the database connection is working.

        @rtype: int
        """
        return self.version.select().execute().fetchone()[0]

    def getMachineType(self, uuid):
        session = create_session()
        ret = self.__getMachineType(uuid, session)
        session.close()
        return ret

    def getMachinesType(self, uuids):
        session = create_session()
        ret = []
        for uuid in uuids:
            ret.append(self.__getMachineType(uuid, session))
        session.close()
        return ret
        
    def __getMachineType(self, uuid, session):
        query = session.query(self.klass['Registry'])
        query = query.select_from(self.table['Registry'].join(self.table['hasRegistry'].join(self.table['nomRegistryPath'])).join(self.machine).join(self.inventory))
        query = query.filter(self.inventory.c.Last == 1).filter(self.machine.c.id == fromUUID(uuid)).filter(self.table['nomRegistryPath'].c.Path == 'terminalType').first()
        if query == None:
            return None
        return query.Value

def toUUID(id): # TODO : change this method to get a value from somewhere in the db, depending on a config param
    return "UUID%s" % (str(id))

def fromUUID(uuid):
    return int(uuid.replace('UUID', ''))

class Machine(object):
    pass

class InventoryTable(object):
    pass


