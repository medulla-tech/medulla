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

from mmc.plugins.inventory.config import InventoryExpertModeConfig, InventoryConfig
from mmc.plugins.inventory.utilities import unique, getInventoryParts
from mmc.support.mmctools import Singleton

from sqlalchemy import *
import logging
import datetime
import time

SA_MAYOR = 0
SA_MINOR = 3

NB_DB_CONN_TRY = 2

def create_method(m):
    def method(self, already_in_loop = False):
        ret = None
        try:
            old_m = getattr(Query, '_old_'+m)
            ret = old_m(self)
        except SQLError, e:
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
 
class Inventory(Singleton):
    """
    Class to query the LRS/Pulse2 inventory database, populated by OCS inventory.

    This class does not read the inventory files created by the LRS during a boot phase (/tftpboot/revoboot/log/*.ini)
    """
    is_activated = False

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
        if self.is_activated:
            self.logger.info("Inventory don't need activation")
            return None
        self.logger.info("Inventory is activating")
        self.config = InventoryConfig("inventory", conffile)
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle)
        self.metadata = BoundMetaData(self.db)
        self.initMappers()
        self.metadata.create_all()
        self.is_activated = True
        self.dbversion = self.getInventoryDatabaseVersion()
        self.logger.debug("Inventory finish activation")

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
        return "%s://%s:%s@%s%s/%s" % (self.config.dbdriver, self.config.dbuser, self.config.dbpasswd, self.config.dbhost, port, self.config.dbname)

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the inventory database
        """
        self.table = {}
        self.klass = {}

        self.version = Table("Version", self.metadata, autoload = True)
        self.machine = Table("Machine", self.metadata, autoload = True)
        self.inventory = Table("Inventory", self.metadata, autoload = True)
        
        for item in getInventoryParts():
            # Declare the SQL table
            self.table[item] = Table(item, self.metadata, autoload = True)
            # Create the class that will be mapped
            # This will create the Bios, BootDisk, etc. classes
            exec "class %s(object): pass" % item
            self.klass[item] = eval(item)
            # Map the python class to the SQL table
            mapper(self.klass[item], self.table[item])

            # Declare the has* SQL table
            hasitem = "has" + item
            self.table[hasitem] = Table(hasitem, self.metadata,
                                        Column("machine", Integer, ForeignKey("Machine.id"), primary_key=True),
                                        Column("inventory", Integer, ForeignKey("Inventory.id"), primary_key=True),
                                        Column(item.lower(), Integer, ForeignKey(item + ".id"), primary_key=True)
                                        )
            # Create the class that will be mapped
            # This will create the hasBios, hasBootDisk, etc. classes
            exec "class %s(object): pass" % hasitem
            self.klass[hasitem] = eval(hasitem)
            # Map the python class to the SQL table
            mapper(eval(hasitem), self.table[hasitem])
                                                                 
        mapper(Machine, self.machine)
        mapper(InventoryTable, self.inventory)

    def getInventoryDatabaseVersion(self):
        """
        Return the inventory database version.
        We don't use this information for now, but if we can get it this means the database connection is working.

        @rtype: int
        """
        return self.version.select().execute().fetchone()[0]

    def inventoryExists(self, name):
        """
        Return True or False depending on the existance of machine "name" in the inventory DB

        @param name: the name of the machine
        @typa name: str

        @return: Return True if the machine exists in the inventory DB
        @rtype: bool
        """
        session = create_session()
        result = session.query(Machine).filter(self.machine.c.Name == name).all()
        session.close()
        if result and len(result) == 1:
            return True
        return False
        
    def getMachines(self, pattern = None):
        """
        Return all available machines with their Bios and Hardware inventory informations
        
        @param pattern: pattern to filter the machine list
        @typa pattern: str
        
        @return: Returns the list of machines recorded into the inventory database in alphabetical order, with the Bios and Hardware inventory information
        @rtype: list
        """
        ret = []
        session = create_session()
        if pattern:
            query = session.query(Machine).filter(self.machine.c.Name.like("%" + pattern + "%"))
        else:
            query = session.query(Machine)
        session.close()

        for machine in query.order_by(asc(self.machine.c.Name)):
            tmp = []
            tmp.append(machine.Name)
            tmp.append(self.getLastMachineInventoryPart("Bios", machine.Name))
            tmp.append(self.getLastMachineInventoryPart("Hardware", machine.Name))
            ret.append(tmp)
        return ret

    def getLastMachineInventoryFull(self, name):
        """
        Return the full and last inventory of a machine

        @param name: the name of the machine to get inventory
        @type name: str

        @return: Returns a dictionary where each key is an inventory part name
        @rtype: dict
        """
        ret = {}
        for part in getInventoryParts():
            ret[part] = self.getLastMachineInventoryPart(part, name)
        return ret

    def getMachinesByDict(self, table, params):
        """
        Return a list of machine that correspond to the params "table.field = value"
        """
        ret = []
        partKlass = self.klass[table]
        partTable = self.table[table]
        haspartTable = self.table["has" + table]
        import re
        p1 = re.compile('\*')
        p2 = re.compile('<')
        p3 = re.compile('>')
        
        filters = []
        for field in params:
            value = params[field]
            if p1.search(value):
                value = p1.sub('%', value)
                filters.append(getattr(partKlass.c, field).like(value))
            elif p2.search(value):
                value = p2.sub('', value)
                filters.append(getattr(partKlass.c, field) < value)
            elif p3.search(value):
                value = p3.sub('', value)
                filters.append(getattr(partKlass.c, field) > value)
            else:
                filters.append(getattr(partKlass.c, field) == value)
                
        session = create_session()
        query = session.query(Machine).add_column(func.max(haspartTable.c.inventory).label("inventoryid")).add_column(func.min(self.inventory.c.Date)).select_from(self.machine.join(haspartTable.join(self.inventory).join(partTable)))

        # apply filters
        for filter in filters:
            query = query.filter(filter)
        
        result = query.group_by(self.machine.c.Name).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
        session.close()

        if result:
            for res in result:
                ret.append(res[0].Name)
        
        return ret
    
    def getMachinesBy(self, table, field, value):
        """
        Return a list of machine that correspond to the table.field = value
        """
        ret = []
        session = create_session()
        partKlass = self.klass[table]
        partTable = self.table[table]
        haspartTable = self.table["has" + table]
        import re
        p1 = re.compile('\*')
        if p1.search(value):
            value = p1.sub('%', value)
            result = session.query(Machine).add_column(func.max(haspartTable.c.inventory).label("inventoryid")).add_column(func.min(self.inventory.c.Date)).select_from(self.machine.join(haspartTable.join(self.inventory).join(partTable))).filter( getattr(partKlass.c, field).like(value)).group_by(self.machine.c.Name).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
        else:
            result = session.query(Machine).add_column(func.max(haspartTable.c.inventory).label("inventoryid")).add_column(func.min(self.inventory.c.Date)).select_from(self.machine.join(haspartTable.join(self.inventory).join(partTable))).filter( getattr(partKlass.c, field) == value).group_by(self.machine.c.Name).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
        session.close()

        if result:
            for res in result:
                ret.append(res[0].Name)
        
        return ret

    def getValues(self, table, field):
        """
        return every possible values for a field in a table
        """
        ret = []
        session = create_session()
        partKlass = self.klass[table]
        partTable = self.table[table]
        
        result = session.query(partKlass).add_column(getattr(partKlass.c, field))
        session.close()

        if result:
            for res in result:
                ret.append(res[1])
        return unique(ret)
                
    def getValuesWhere(self, table, field1, value1, field2):
        """
        return every possible values for a field (field2) in a table, where field1 = value1
        """
        ret = []
        session = create_session()
        partKlass = self.klass[table]
        partTable = self.table[table]

        import re
        p1 = re.compile('\*')
        if p1.search(value1):
            value1 = p1.sub('%', value1)
            result = session.query(partKlass).add_column(getattr(partKlass.c, field2)).filter( getattr(partKlass.c, field1).like(value1))
        else:
            result = session.query(partKlass).add_column(getattr(partKlass.c, field2)).filter( getattr(partKlass.c, field1) == value1)
        session.close()

        if result:
            for res in result:
                ret.append(res[1])
        return unique(ret)
    
        
    def getLastMachineInventoryPart(self, part, name, pattern = None):
        """
        Return a list where each item belongs to the last machine inventory.
        Each item is a dictionary of the inventory description.
        An extra key of the dictionary called 'timestamp' contains the inventory item first appearance.

        @param name: the name of the machine to get inventory
        @type name: str

        @return: Returns a list of dictionary
        @type: list
        """
        ret = []
        session = create_session()
        partKlass = self.klass[part]
        partTable = self.table[part]
        haspartTable = self.table["has" + part]
        # This SQL query has been built using the one from the LRS inventory module
        result = session.query(partKlass).add_column(func.max(haspartTable.c.inventory).label("inventoryid")).add_column(func.min(self.inventory.c.Date)).select_from(partTable.join(haspartTable.join(self.inventory).join(self.machine))).filter(Machine.c.Name==name).group_by(partTable.c.id).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
        session.close()
        if result:
            # Build the result as a simple dictionary
            # We return only the information from the latest inventory
            inventoryid = None
            for res in result:
                if inventoryid == None:
                    inventoryid = res[1]
                else:
                    if inventoryid != res[1]: break
                # Build the dictionary using the partTable column names as keys
                tmp = {}                
                for col in partTable.columns:
                    tmp[col.name] = eval("res[0]." + col.name)
                # Build a time tuple for the appearance timestamp
                d = res[2]
                if type(res[2]) == str:
                    y, m, day = res[2].split("-")
                    d = datetime.datetime(int(y), int(m), int(day))
                tmp["timestamp"] = d
                ret.append(tmp)
        return ret


# Class for SQLalchemy mapping
class Machine(object):
    pass

class InventoryTable(object):
    pass


