#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: __init__.py 163 2007-07-04 07:15:46Z cedric $
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

from mmc.support.config import PluginConfig
from mmc.support.mmctools import Singleton, xmlrpcCleanup

from ConfigParser import NoOptionError
from sqlalchemy import *
import logging
import datetime
import time

VERSION = "2.0.0"
APIVERSION = "0:0:0"
REVISION = int("$Rev: 163 $".split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION


inventory = None # See comments in activate()

def activate():
    logger = logging.getLogger()
    config = InventoryConfig("inventory")
    if config.disable:
        logger.warning("Plugin inventory: disabled by configuration.")
        return False
                                
    # When this module is used be the MMC agent, the global inventory variable is shared.
    # This means an Inventory instance is not created each time a XML-RPC call is done.
    global inventory
    inventory = Inventory()
    logger.info("Plugin inventory: Inventory database version is %d" % inventory.dbversion)
    return True
            
def getLastMachineInventoryPart(part, name, pattern = None):
    return xmlrpcCleanup(inventory.getLastMachineInventoryPart(part, name, pattern))

def getAllMachinesInventoryColumn(part, column, pattern = None):
    ret = getAllMachinesInventoryPart(part, pattern)
    retour = []
    for machine in ret:
        name = machine[0]
        invents = []
        for invent in machine[1]:
            invents.append(invent[column])
        retour.append([name, invents])
    return xmlrpcCleanup(retour)

def getMachines(pattern = None):
    return xmlrpcCleanup(inventory.getMachines(pattern))

def inventoryExists(name):
    return xmlrpcCleanup(inventory.inventoryExists(name))

def getLastMachineInventoryFull(name):
    return xmlrpcCleanup(inventory.getLastMachineInventoryFull(name))

def getAllMachinesInventoryPart(part, pattern = None):
    machines = getMachines(pattern)
    result = []
    for machine in machines:
        result.append([machine[0], getLastMachineInventoryPart(part, machine[0])])
    return result
    
def getInventoryParts():
    """
    @return: Return all available inventory parts
    @rtype: list
    """
    return [ "Bios", "BootDisk", "BootGeneral", "BootMem", "BootPart", "BootPCI", "Controller", "Custom", "Drive", "Hardware", "Input", "Memory", "Modem", "Monitor", "Network", "Port", "Printer", "Slot", "Software", "Sound", "Storage", "VideoCard" ]

def getInventoryEM(col):
    conf = InventoryExpertModeConfig("inventory", None)
    return conf.expert_mode[col]

def getInventoryGraph(col):
    conf = InventoryExpertModeConfig("inventory", None)
    return conf.graph[col]

def getMachinesBy(table, field, value):
    return inventory.getMachinesBy(table, field, value)

def getMachinesByDict(table, params):
    return inventory.getMachinesByDict(table, params)

def getValues(table, field):
    return inventory.getValues(table, field)

def getValuesWhere(table, field1, value1, field2):
    return inventory.getValuesWhere(table, field1, value1, field2)

class InventoryExpertModeConfig(PluginConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        self.expert_mode = {}
        self.graph = {}
        for i in getInventoryParts():
            try:
                self.graph[i] = self.get("graph", i).split('|')
            except NoOptionError:
                self.graph[i] = []
            try:
                self.expert_mode[i] = self.get("expert_mode", i).split('|')
            except NoOptionError:
                self.expert_mode[i] = []

class InventoryConfig(PluginConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        self.dbdriver = self.get("main", "dbdriver")
        self.dbhost = self.get("main", "dbhost")
        self.dbname = self.get("main", "dbname")
        self.dbuser = self.get("main", "dbuser")
        self.dbpasswd = self.get("main", "dbpasswd")
        self.disable = self.get("main", "disable")
        try:
            self.dbport = self.getint("main", "dbport")
        except NoOptionError:
            # We will use the default db driver port
            self.dbport = None


class Inventory:
    """
    Class to query the LRS/Pulse2 inventory database, populated by OCS inventory.

    This class does not read the inventory files created by the LRS during a boot phase (/tftpboot/revoboot/log/*.ini)
    """
    
    def __init__(self, conffile = None):
        self.config = InventoryConfig("inventory", conffile)
        self.db = create_engine(self.makeConnectionPath())
        self.metadata = BoundMetaData(self.db)
        self.initMappers()
        self.metadata.create_all()
        # self.metadata.bind.echo = True
        self.session = create_session()
        self.dbversion = self.getInventoryDatabaseVersion()

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

        result = self.session.query(Machine).filter(self.machine.c.Name == name).all()
        logging.getLogger().info(result)
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
        if pattern:
            query = self.session.query(Machine).filter(self.machine.c.Name.like("%" + pattern + "%"))
        else:
            query = self.session.query(Machine)
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
                
        query = self.session.query(Machine).add_column(func.max(haspartTable.c.inventory).label("inventoryid")).add_column(func.min(self.inventory.c.Date)).select_from(self.machine.join(haspartTable.join(self.inventory).join(partTable)))

        # apply filters
        for filter in filters:
            query = query.filter(filter)
        
        result = query.group_by(self.machine.c.Name).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)

        if result:
            for res in result:
                ret.append(res[0].Name)
        
        return ret
    
    def getMachinesBy(self, table, field, value):
        """
        Return a list of machine that correspond to the table.field = value
        """
        ret = []
        partKlass = self.klass[table]
        partTable = self.table[table]
        haspartTable = self.table["has" + table]
        import re
        p1 = re.compile('\*')
        if p1.search(value):
            value = p1.sub('%', value)
            result = self.session.query(Machine).add_column(func.max(haspartTable.c.inventory).label("inventoryid")).add_column(func.min(self.inventory.c.Date)).select_from(self.machine.join(haspartTable.join(self.inventory).join(partTable))).filter( getattr(partKlass.c, field).like(value)).group_by(self.machine.c.Name).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
        else:
            result = self.session.query(Machine).add_column(func.max(haspartTable.c.inventory).label("inventoryid")).add_column(func.min(self.inventory.c.Date)).select_from(self.machine.join(haspartTable.join(self.inventory).join(partTable))).filter( getattr(partKlass.c, field) == value).group_by(self.machine.c.Name).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
        if result:
            for res in result:
                ret.append(res[0].Name)
        
        return ret

    def getValues(self, table, field):
        """
        return every possible values for a field in a table
        """
        ret = []
        partKlass = self.klass[table]
        partTable = self.table[table]
        
        result = self.session.query(partKlass).add_column(getattr(partKlass.c, field))
        if result:
            for res in result:
                ret.append(res[1])
        return unique(ret)
                
    def getValuesWhere(self, table, field1, value1, field2):
        """
        return every possible values for a field (field2) in a table, where field1 = value1
        """
        ret = []
        partKlass = self.klass[table]
        partTable = self.table[table]

        import re
        p1 = re.compile('\*')
        if p1.search(value1):
            value1 = p1.sub('%', value1)
            result = self.session.query(partKlass).add_column(getattr(partKlass.c, field2)).filter( getattr(partKlass.c, field1).like(value1))
        else:
            result = self.session.query(partKlass).add_column(getattr(partKlass.c, field2)).filter( getattr(partKlass.c, field1) == value1)
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
        partKlass = self.klass[part]
        partTable = self.table[part]
        haspartTable = self.table["has" + part]
        # This SQL query has been built using the one from the LRS inventory module
        result = self.session.query(partKlass).add_column(func.max(haspartTable.c.inventory).label("inventoryid")).add_column(func.min(self.inventory.c.Date)).select_from(partTable.join(haspartTable.join(self.inventory).join(self.machine))).filter(Machine.c.Name==name).group_by(partTable.c.id).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
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


def unique(s):
    """Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u


