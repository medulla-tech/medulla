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
from mmc.plugins.inventory.utilities import unique, getInventoryParts, getInventoryNoms
from mmc.plugins.inventory.tables_def import PossibleQueries
from mmc.plugins.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from mmc.plugins.pulse2.group import ComputerGroupManager
from mmc.support.mmctools import Singleton

from sqlalchemy import *
import sqlalchemy
import logging
import datetime
import time
import re

SA_MAYOR = 0
SA_MINOR = 3

NB_DB_CONN_TRY = 2

# TODO need to check for useless function (there should be many unused one...)

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

def toH(w):
    ret = {}
    for i in filter(lambda f: not f.startswith('__'), dir(w)):
        ret[i] = getattr(w, i)
    return ret

class DbObject(object):
    def toH(self):
        ret = {}
        for i in filter(lambda f: not f.startswith('_'), dir(self)):
            t = type(getattr(self, i))
            if t == str or t == dict or t == unicode or t == tuple or t == int or t == long:
                ret[i] = getattr(self, i)
        ret['uuid'] = toUUID(getattr(self, 'id'))
        return ret
        
class Inventory(DyngroupDatabaseHelper):
    """
    Class to query the LRS/Pulse2 inventory database, populated by OCS inventory.

    DyngroupDatabaseHelper is a Singleton, so is Inventory

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
        DyngroupDatabaseHelper.init(self)
        if self.is_activated:
            self.logger.info("Inventory don't need activation")
            return None
        self.logger.info("Inventory is activating")
        self.config = InventoryConfig("inventory", conffile)
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, convert_unicode=True)
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

        noms = getInventoryNoms()
        
        for item in getInventoryParts():
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
            if noms.has_key(item):
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

    def inventoryExists(self, ctx, uuid):
        """
        Return True or False depending on the existance of machine "name" in the inventory DB

        @param name: the name of the machine
        @typa name: str

        @return: Return True if the machine exists in the inventory DB
        @rtype: bool
        """
        session = create_session()
        result = session.query(Machine).filter(self.machine.c.id == fromUUID(uuid)).all()
        session.close()
        if result and len(result) == 1:
            return True
        return False
        
    def __machinesOnlyQuery(self, ctx, pattern = None, session = create_session(), count = False):
        query = session.query(Machine)
        try:
            query = query.filter(self.machine.c.Name.like("%" + pattern['hostname'] + "%"))
        except KeyError, e:
            pass

        try:
            query = query.filter(self.machine.c.Name.like("%" + pattern['filter'] + "%"))
        except KeyError, e:
            pass

        try:
            query = query.filter(self.machine.c.id == fromUUID(pattern['uuid']))
        except KeyError, e:
            pass

        try:
            request = pattern['request']
            bool = None
            if pattern.has_key('equ_bool'):
                bool = pattern['equ_bool']
            machines = map(lambda m: fromUUID(m), ComputerGroupManager().request(ctx, request, bool, 0, -1, ''))
            query = query.filter(self.machine.c.id.in_(*machines))
        except KeyError, e:
            pass
            
        try:
            gid = pattern['gid']
            machines = []
            if ComputerGroupManager().isrequest_group(ctx, gid):
                machines = map(lambda m: fromUUID(m), ComputerGroupManager().requestresult_group(ctx, gid, 0, -1, ''))
            else:
                if (not pattern.has_key('hostname') or pattern['hostname'] == '') \
                    and (not pattern.has_key('filter') or pattern['filter'] == ''):
                        if count:
                            return ComputerGroupManager().countresult_group(ctx, gid, '')
                        else:
                            min = 0
                            max = 10
                            if pattern.has_key('min'):
                                min = pattern['min']
                            if pattern.has_key('max'):
                                max = pattern['max']
                            machines = map(lambda m: fromUUID(m), ComputerGroupManager().result_group(ctx, gid, min, max, ''))
                            
                else:
                    machines = map(lambda m: fromUUID(m), ComputerGroupManager().result_group(ctx, gid, 0, -1, ''))
            query = query.filter(self.machine.c.id.in_(*machines))
            if not ComputerGroupManager().isrequest_group(ctx, gid):
                if count:
                    return query.count()
                else:
                    return query
        except KeyError, e:
            pass

        # doing dyngroups stuff
        join_query, query_filter = self.filter(ctx, self.machine, pattern, session.query(Machine), self.machine.c.id)
        query = query.select_from(join_query).filter(query_filter).group_by(self.machine.c.id)
        # end of dyngroups
        if count:
            return query.count()
        return query
        
    def getMachinesOnly(self, ctx, pattern = None):
        """
        Return all available machines
        """
        session = create_session()
        query = self.__machinesOnlyQuery(ctx, pattern, session)
        query = query.order_by(asc(self.machine.c.Name))
        try:
            if pattern['max'] != -1:
                if (pattern.has_key('gid') and ComputerGroupManager().isrequest_group(ctx, pattern['gid'])) or not pattern.has_key('gid'):
                    query = query.offset(pattern['min'])
                    query = query.limit(int(pattern['max']) - int(pattern['min']))
                else:
                    query = query.all()
            else:
                query = query.all()
        except KeyError, e:
            query = query.all()
        session.close()
        return query
    
    def countMachinesOnly(self, ctx, pattern = None):
        """
        Return the number of available machines
        """
        session = create_session()
        ret = self.__machinesOnlyQuery(ctx, pattern, session, True)
        session.close()
        return ret

    def optimizedQuery(self, ctx, filt):
        """
        @returns: a list of couples (UUID, hostname)
        @rtype: list
        """
        criterion = filt['optimization']['criterion']
        criterion = ["Path", criterion.split("/")[2]]
        values = ['Value', filt['optimization']['data']]
        result = self.getLastMachineInventoryPart(
            ctx, 'Registry',
            {'where' : [criterion, values] } )
        # Just returns a list of couple (UUID, hostname)
        ret = map(lambda x: (x[0], x[2]), result)
        return ret

    def getComputersOptimized(self, ctx, filt):
        """
        Return a list of computers, but try to optimize the way we get its
        inventory.
        """
        optimization = False
        if 'optimization' in filt:
            if 'criterion' in filt['optimization']:
                if filt['optimization']['criterion'].startswith('Registry/Value/'):
                    optimization = True
        if optimization:
            # In optimized mode, we don't return the full of inventory of the
            # computers corresponding to the request, but just list of couples
            # (UUID, hostname)
            return self.optimizedQuery(ctx, filt)
        else:
            result = self.getMachinesOnly(ctx, filt)

        tables = Inventory().config.content
        if len(tables) == 1 and "Registry" in tables:
            # The inventory to display is to be taken from the same Registry
            # table
            computers = {}
            ids = []
            uuids = []
            for machine in result:
                ids.append(machine.id)
                uuid = toUUID(machine.id)
                tmp = [ False,
                        { 'cn' : [machine.Name],
                          'objectUUID' : [uuid] } ]
                computers[uuid] = tmp
                # Keep UUID order
                uuids.append(uuid)
            if len(uuids):
                # For all resulting machines ids, get the inventory part
                inventoryResult = self.getLastMachineInventoryPart(ctx, tables.keys()[0], {'ids' : ids })
                # Process each row, one row == one computer inventory
                for row in inventoryResult:
                    uuid = row[2]
                    # Process inventory content
                    for inv in row[1]:
                        computers[uuid][1][inv["Path"]] = inv["Value"]
            # Build the result
            ret = []
            for uuid in uuids:
                ret.append(computers[uuid])
        else:
            result = self.getMachinesOnly(ctx, filt)
            ret = map(lambda m: m.toDN(ctx), result)
        return ret
        
    # needed by DyngroupDatabaseHelper
    def computersTable(self):
        return [self.machine]

    def computersMapping(self, computers, invert = False):
        if not invert:
            return Machine.c.id.in_(*map(lambda x:fromUUID(x), computers))
        else:
            return Machine.c.id.not_(in_(*map(lambda x:fromUUID(x), computers)))

    def mappingTable(self, query):
        q = query[2].split('/')
        table, field = q[0:2]
        self.logger.debug("### >> table %s, field %s"%(table, field))
        if len(q) > 2:
            self.logger.debug("##### >> semi static name : %s"%(q[2]))
        if table == 'Machine':
            return [self.machine, self.table['hasHardware'], self.inventory]
        else:
            partTable = self.table[table]
            haspartTable = self.table["has" + table]
        if getInventoryNoms(table) == None:
            return [haspartTable, partTable]
        self.logger.debug("### Nom")
        ret = [haspartTable, partTable, self.inventory]
        for nom in getInventoryNoms(table):
            nomTableName = 'nom%s%s' % (table, nom)
            self.logger.debug("### nomTableName %s"%(nomTableName))
            nomTable = self.table[nomTableName]
            ret.append(nomTable)
        return ret
    
    def mapping(self, query, invert = False):
        q = query[2].split('/')
        table, field = q[0:2]
        if PossibleQueries().possibleQueries('double').has_key(query[2]): # double search
            value = PossibleQueries().possibleQueries('double')[query[2]]
            return and_(
                self.mapping([None, None, value[0][0], query[3][0].replace('(', '')]),
                self.mapping([None, None, value[1][0], query[3][1].replace(')', '')])
            )
        elif PossibleQueries().possibleQueries('list').has_key(query[2]): # list search
            if table == 'Machine':
                partKlass = Machine
            else:
                partKlass = self.klass[table]
            value = query[3]
            if value.startswith('>') and not invert or value.startswith('<') and invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass.c, field) > value, self.inventory.c.Last == 1)
            elif value.startswith('>') and invert or value.startswith('<') and not invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass.c, field) < value, self.inventory.c.Last == 1)
            elif invert:
                return and_(getattr(partKlass.c, field) != value, self.inventory.c.Last == 1)
            else:
                if re.compile('\*').search(value):
                    value = re.compile('\*').sub('%', value)
                    return and_(getattr(partKlass.c, field).like(value), self.inventory.c.Last == 1)
                return and_(getattr(partKlass.c, field) == value, self.inventory.c.Last == 1)
        elif PossibleQueries().possibleQueries('halfstatic').has_key(query[2]): # halfstatic search
            if table == 'Machine':
                partKlass = Machine
            else:
                partKlass = self.klass[table]
            value = query[3]

            hs = PossibleQueries().possibleQueries('halfstatic')[query[2]]
            condition = 1
            if getInventoryNoms(table) == None:
                condition = (getattr(partKlass.c, hs[1]) == hs[2])
            else:
                noms = getInventoryNoms(table)
                try:
                    noms.index(hs[1])
                    nomTableName = 'nom%s%s' % (table, hs[1])
                    nomKlass = self.klass[nomTableName]
                    if hasattr(nomKlass.c, hs[1]):
                        condition = (getattr(nomKlass.c, hs[1]) == hs[2])
                except ValueError, e:
                    condition = (getattr(partKlass.c, hs[1]) == hs[2])

            if value.startswith('>') and not invert or value.startswith('<') and invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass.c, field) > value, condition, self.inventory.c.Last == 1)
            elif value.startswith('>') and invert or value.startswith('<') and not invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass.c, field) < value, condition, self.inventory.c.Last == 1)
            elif invert:
                return and_(getattr(partKlass.c, field) != value, condition, self.inventory.c.Last == 1)
            else:
                if re.compile('\*').search(value):
                    value = re.compile('\*').sub('%', value)
                    return and_(getattr(partKlass.c, field).like(value), condition, self.inventory.c.Last == 1)
                return and_(getattr(partKlass.c, field) == value, condition, self.inventory.c.Last == 1)
          
    def getMachines(self, ctx, pattern = None):
        """
        Return all available machines with their Bios and Hardware inventory informations
        
        @param pattern: pattern to filter the machine list
        @typa pattern: str
        
        @return: Returns the list of machines recorded into the inventory database in alphabetical order, with the Bios and Hardware inventory information
        @rtype: list
        """
        ret = []
        for machine in self.getMachinesOnly(ctx, pattern):
            tmp = []
            tmp.append(machine.Name)
            tmp.append(self.getLastMachineInventoryPart(ctx, "Bios", {'hostname':machine.Name}))
            tmp.append(self.getLastMachineInventoryPart(ctx, "Hardware", {'hostname':machine.Name}))
            tmp.append(toUUID(machine.id))
            ret.append(tmp)
        return ret

    def getLastMachineInventoryFull(self, ctx, params):
        """
        Return the full and last inventory of a machine

        @param name: the name of the machine to get inventory
        @type params: dict

        @return: Returns a dictionary where each key is an inventory part name
        @rtype: dict
        """
        ret = {}
        for part in getInventoryParts():
            ret[part] = self.getLastMachineInventoryPart(ctx, part, params)
        return ret

    def getMachinesByDict(self, ctx, table, params):
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
    
    def getMachinesBy(self, ctx, table, field, value):
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
        if table == 'Machine':
            partKlass = Machine
            partTable = self.machine
        else:
            partKlass = self.klass[table]
            partTable = self.table[table]
        
        result = session.query(partKlass).add_column(getattr(partKlass.c, field))
        session.close()

        if result:
            for res in result:
                ret.append(res[1])
        return unique(ret)

    def getValuesFuzzy(self, table, field, fuzzy_value):
        """
        return every possible values for a field in a table where the field is like fuzzy_value
        """
        ret = []
        session = create_session()
        if table == 'Machine':
            partKlass = Machine
            partTable = self.machine
        else:
            partKlass = self.klass[table]
            partTable = self.table[table]
        
        result = session.query(partKlass).add_column(getattr(partKlass.c, field)).filter(getattr(partKlass.c, field).like('%'+fuzzy_value+'%'))
        session.close()

        if result:
            for res in result:
                ret.append(res[1])
        return unique(ret)
                
    def getValueFuzzyWhere(self, table, field1, value1, field2, fuzzy_value):
        """
        return every possible values for a field (field2) in a table, where field1 = value1 and field2 like fuzzy_value
        """
        ret = []
        if table == 'Machine':
            partKlass = Machine
        else:
            partKlass = self.klass[table]
        session = create_session()
        result = self.__getValuesWhereQuery(table, field1, value1, field2, session)
        result = result.filter(getattr(partKlass.c, field2).like('%'+fuzzy_value+'%'))
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
        result = self.__getValuesWhereQuery(table, field1, value1, field2, session)
        session.close()

        if result:
            for res in result:
                ret.append(res[1])
        return unique(ret)

    def __getValuesWhereQuery(self, table, field1, value1, field2, session = create_session()):
        if table == 'Machine':
            partKlass = Machine
            partTable = self.machine
        else:
            partKlass = self.klass[table]
            partTable = self.table[table]
        query = session.query(partKlass).add_column(getattr(partKlass.c, field2))
        filterDone = False
        
        if getInventoryNoms(table) != None:
            for nom in getInventoryNoms(table):
                hasTable = self.table['has%s'%(table)]
                nomTableName = 'nom%s%s' % (table, nom)
                nomKlass = self.klass[nomTableName]
                if hasattr(nomKlass.c, field1):
                    nomTable = self.table[nomTableName]
                    query = query.select_from(partTable.join(hasTable).join(nomTable))
                    query = query.filter(self.__filterOn(nomKlass, field1, value1))
                    filterDone = True

        if not filterDone:
            query = query.filter(self.__filterOn(partKlass, field1, value1))
        return query

    def __filterOn(self, partKlass, field, value):
        import re
        p1 = re.compile('\*')
        self.logger.debug("%s %s"%(field, value))
        if p1.search(value):
            value = p1.sub('%', value)
            return getattr(partKlass.c, field).like(value)
        else:
            return getattr(partKlass.c, field) == value
    
    def getMachineNetwork(self, ctx, params):
        return self.getLastMachineInventoryPart(ctx, 'Network', params)

    def getMachineCustom(self, ctx, params):
        return self.getLastMachineInventoryPart(ctx, 'Custom', params)

    def doesUserHaveAccessToMachine(self, userid, machine_uuid): # TODO implement ...
        return True

    def doesUserHaveAccessToMachines(self, userid, machine_uuid, all = True): # TODO implement ...
        return True
        
    def countLastMachineInventoryPart(self, ctx, part, params):
        session = create_session()
        partKlass = self.klass[part]
        partTable = self.table[part]
        haspartTable = self.table["has" + part]
        result, grp_by = self.__lastMachineInventoryPartQuery(session, ctx, part, params)
        for grp in grp_by:
            result = result.group_by(grp)
        result = result.count()
        session.close()
        return result
    
    def getLastMachineInventoryPart(self, ctx, part, params):
        return self.__getLastMachineInventoryPart(part, params, ctx)
        
    def __getLastMachineInventoryPart(self, part, params, ctx = None):
        """
        Return a list where each item belongs to the last machine inventory.
        Each item is a dictionary of the inventory description.
        An extra key of the dictionary called 'timestamp' contains the inventory item first appearance.

        @param params: parameters to get the machine in the inventory (hostname, uuid, ...)
        @type name: dict

        @return: Returns a list of dictionary
        @type: list
        """
        ret = []
        session = create_session()
        partKlass = self.klass[part]
        partTable = self.table[part]
        haspartTable = self.table["has" + part]
        result, grp_by = self.__lastMachineInventoryPartQuery(session, ctx, part, params)
        
        if params.has_key('min') and params.has_key('max'):
            result = result.offset(int(params['min']))
            result = result.limit(int(params['max']) - int(params['min']))
 
        for grp in grp_by:
            result = result.group_by(grp)
        result = result.order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
        session.close()
        if result:
            # Build the result as a simple dictionary
            # We return only the information from the latest inventory
            inventoryid = None
            machine_inv = {}
            machine_uuid = {}
            for res in result:
                if inventoryid == None:
                    inventoryid = res[3]
                #else:
                #    if inventoryid != res[3]: break
                # Build the dictionary using the partTable column names as keys
                tmp = {}                
                for col in partTable.columns:
                    tmp[col.name] = eval("res[0]." + col.name)
                # Build a time tuple for the appearance timestamp
                d = res[4]
                if type(res[4]) == str:
                    y, m, day = res[4].split("-")
                    d = datetime.datetime(int(y), int(m), int(day))
                tmp["timestamp"] = d
                if not machine_inv.has_key(res[1]):
                    machine_inv[res[1]] = []
                    machine_uuid[res[1]] = toUUID(res[2])
                if len(res) > 5:
                    noms = getInventoryNoms()
                    if noms.has_key(part):
                        for i in range(5, len(res)):
                            tmp[noms[part][i-5]] = res[i]
                machine_inv[res[1]].append(tmp)
            for name in machine_uuid:
                ret.append([name, machine_inv[name], machine_uuid[name]])
        return ret
        
    def __lastMachineInventoryPartQuery(self, session, ctx, part, params):
        partKlass = self.klass[part]
        partTable = self.table[part]
        haspartTable = self.table["has" + part]
        haspartKlass = self.klass["has" + part]
        grp_by = [partTable.c.id, haspartTable.c.machine]

        # This SQL query has been built using the one from the LRS inventory module
        # TODO : this request has to be done on Machine and then add the columns so that the left join works...
        #result = session.query(partKlass).add_column(self.machine.c.Name).add_column(self.machine.c.id).add_column(haspartTable.c.inventory.label("inventoryid")).add_column(self.inventory.c.Date).select_from(partTable.outerjoin(haspartTable.join(self.inventory).join(self.machine))).filter(self.inventory.c.Last == 1)
        result = session.query(partKlass).add_column(self.machine.c.Name).add_column(self.machine.c.id).add_column(haspartTable.c.inventory.label("inventoryid")).add_column(self.inventory.c.Date)
        
        noms = getInventoryNoms()
        select_from = haspartTable.join(self.inventory).join(partTable)
        if noms.has_key(part):
            for nom in noms[part]:
                nomTableName = 'nom%s%s' % (part, nom)
                nomTable = self.table[nomTableName]
                select_from = select_from.join(nomTable)
                result = result.add_column(getattr(nomTable.c, nom))
                grp_by.append(nomTable.c.id)
              
        result = result.select_from(self.machine.outerjoin(select_from)).filter(self.inventory.c.Last == 1)
        result = self.__filterQuery(ctx, result, params)
        
        # this can't be put in __filterQuer because it's not a generic filter on Machine...
        if params.has_key('where') and params['where'] != '':
            for where in params['where']:
                if hasattr(partTable.c, where[0]):
                    if type(where[1]) == list:
                        result = result.filter(getattr(partTable.c, where[0]).in_(*where[1]))
                    else:
                        result = result.filter(getattr(partTable.c, where[0]) == where[1])
                else:
                    if noms.has_key(part):
                        try:
                            noms[part].index(where[0])
                            nomTableName = 'nom%s%s' % (part, where[0])
                            
                            nomTable = self.table[nomTableName]
                            if hasattr(nomTable.c, where[0]):
                                if type(where[1]) == list:
                                    result = result.filter(getattr(nomTable.c, where[0]).in_(*where[1]))
                                else:
                                    result = result.filter(getattr(nomTable.c, where[0]) == where[1])
                            else:
                                self.logger.warn("cant find the required field (%s) in table %s"%(where[0], nomTableName))
                        except ValueError:
                            self.logger.warn("cant find any %s field"%(where[0]))
                    else:
                        self.logger.warn("cant find any %s field"%(where[0]))
        return (result, grp_by)
   
    def __filterQuery(self, ctx, query, params):
        if params.has_key('hostname') and params['hostname'] != '':
            query = query.filter(Machine.c.Name==params['hostname'])
        if params.has_key('filter') and params['filter'] != '':
            query = query.filter(Machine.c.Name.like('%'+params['filter']+'%'))
        if params.has_key('uuid') and params['uuid'] != '':
            query = query.filter(Machine.c.id==fromUUID(params['uuid']))
        if params.has_key('uuids') and len(params['uuids']):
            uuids = map(lambda m: fromUUID(m), params['uuids'])
            query = query.filter(Machine.c.id.in_(*uuids))
        if params.has_key('gid') and params['gid'] != '':
            if ComputerGroupManager().isrequest_group(ctx, params['gid']):
                machines = map(lambda m: fromUUID(m), ComputerGroupManager().requestresult_group(ctx, params['gid'], 0, -1, ''))
            else:
                machines = map(lambda m: fromUUID(m), ComputerGroupManager().result_group(ctx, params['gid'], 0, -1, ''))
            query = query.filter(self.machine.c.id.in_(*machines))
        # Filter using a list of machine ids
        if params.has_key('ids') and len(params['ids']):
            query = query.filter(self.machine.c.id.in_(*params['ids']))
        return query
       
    def getIdInTable(self, tableName, values, session = None):
        sessionCreator = False
        if session == None:
            sessionCreator = True
            session = create_session()
        klass = self.klass[tableName]
        table = self.table[tableName]

        result = session.query(klass)
        for v in values:
            if type(v) == str or type(v) == unicode:
                if hasattr(table.c, v):
                    result = result.filter(getattr(table.c, v) == values[v])
        res = result.first()
        if sessionCreator:
            session.close()
        try:
            return res.id
        except:
            return None
            
    def isElemInTable(self, tableName, values, session = None):
        sessionCreator = False
        if session == None:
            sessionCreator = True
            session = create_session()
        klass = self.klass[tableName]
        table = self.table[tableName]

        result = session.query(klass)
        for v in values:
            if hasattr(table.c, v):
                result = result.filter(getattr(table.c, v) == values[v])
        res = result.count()
        if sessionCreator:
            session.close()
        try:
            return res
        except:
            return None

    def addMachine(self, name, ip, mac, netmask, comment = None, location = None): # TODO add the location association
        session = create_session()
        m = Machine()
        m.Name = name
        session.save(m)
        # TODO need to put all other Last to 0
        query = session.query(InventoryTable).select_from(self.inventory.join(self.table['hasNetwork']).join(self.machine)).filter(self.machine.c.Name == name)
        for inv in query:
            inv.Last = 0
            session.save(inv)
        i = InventoryTable()
        i.Last = 1
        session.save(i)
        session.flush()
        net = self.klass['Network']
        hasNet = self.klass['hasNetwork']
        n = net()
        n.MACAddress = mac
        n.IP = ip
        n.SubnetMask = netmask
        session.save(n)
        session.flush()
        h = hasNet()
        h.machine = m.id
        h.network = n.id
        h.inventory = i.id
        session.save(h)
        session.flush()
        if comment != None:
            custom = self.klass['Custom']
            hasCustom = self.klass['hasCustom']
            c = custom()
            c.Comments = comment
            session.save(c)
            session.flush()
            h = hasCustom()
            h.machine = m.id
            h.custom = c.id
            h.inventory = i.id
            session.save(h)
            session.flush()
        session.close()
        return toUUID(m.id)
        
    def delMachine(self, uuid):
        uuid = fromUUID(uuid)
        session = create_session()
        for item in getInventoryParts():
            tk = self.klass[item]
            tt = self.table[item]
            lk = self.klass['has'+item]
            lt = self.table['has'+item]
# TODO : check if more than one machine use this entry
#            ts = session.query(tk).select_from(tt.join(lt)).filter(lt.c.machine == uuid)
#            for t in ts:
#                session.delete(t)
            ls = session.query(lk).filter(lt.c.machine == uuid)
            for l in ls:
                i = session.query(InventoryTable).filter(self.inventory.c.id == l.inventory).first()
                session.delete(i)
                session.delete(l)
        m = session.query(Machine).filter(self.machine.c.id == uuid).first()
        session.delete(m)
        session.flush()
        session.close()
        return True
        
    def getUserLocations(self, userid):
        session = create_session()
        m = session.query(self.klass['Entity']).all()
        session.close()
        return m

    def getLocationsCount(self):
        session = create_session()
        count = session.query(self.klass['Entity']).count()
        session.close()
        return count

    def getUsersInSameLocations(self, userid):
        # TODO
        return [userid]


def toUUID(id): # TODO : change this method to get a value from somewhere in the db, depending on a config param
    return "UUID%s" % (str(id))

def fromUUID(uuid):
    return int(uuid.replace('UUID', ''))
    
def getComputerDict(c):
    if type(c) == dict:
        return c
    for m in ['toH', 'to_h', 'toh', 'to_H']:
        if hasattr(c, m):
            return getattr(c,m)()
    raise Exception("don't know how to convert in dict")
    
# Class for SQLalchemy mapping
class Machine(object):
    def toH(self):
        return { 'hostname':self.Name, 'uuid':toUUID(self.id) }

    def uuid(self):
        return toUUID(self.id)
        
    def toDN(self, ctx, advanced = False):
        ret = [ False, {'cn':[self.Name], 'objectUUID':[toUUID(self.id)]} ]
        comment = Inventory().getMachineCustom(ctx, {'uuid':toUUID(self.id)})
        if len(comment) != 0:
            ret[1]['displayName'] = [comment[0][1][0]['Comments']]
        for table in Inventory().config.content:
            content = Inventory().config.content[table]
            for col in content:
                params = {'uuid':toUUID(self.id)}
                if len(col) > 2:
                    for p in col[2:]:
                        if not params.has_key('where'):
                            params['where'] = []
                        params['where'].append(p)
                
                part = Inventory().getLastMachineInventoryPart(ctx, table, params)
                if len(part) == 0:
                    ret[1][col[1]] = ''
                else:
                    part = part[0][1]
                    ret[1][col[1]] = []
                    for n in part:
                        ret[1][col[1]].append(n[col[0]])
            
        if advanced:
            net = Inventory().getMachineNetwork(ctx, {'uuid':toUUID(self.id)})
            if len(net) == 0:
                ret[1]['ipHostNumber'] = ''
                ret[1]['macAddress'] = ''
                ret[1]['subnetMask'] = ''
            else:
                net = net[0]
                ret[1]['ipHostNumber'] = []
                ret[1]['macAddress'] = []
                ret[1]['subnetMask'] = []
                for n in net[1]:
                    if n['IP'] != None:
                        ret[1]['ipHostNumber'].append(n['IP'])
                    if n['MACAddress'] != None and n['MACAddress'] != '00-00-00-00-00-00-00-00-00-00-00':
                        ret[1]['macAddress'].append(n['MACAddress'])
                    if n['SubnetMask'] != None:
                        ret[1]['subnetMask'].append(n['SubnetMask'])
        return ret

    def toCustom(self, get):
        ma = {}
        for field in get:
            if hasattr(self, field):
                ma[field] = getattr(self, field)
            if field == 'uuid' or field == 'objectUUID':
                ma[field] = toUUID(self.id)
            if field == 'cn':
                ma[field] = self.Name
        return ma

class InventoryTable(object):
    pass


