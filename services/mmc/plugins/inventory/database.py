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
from mmc.plugins.inventory.tables_def import possibleQueries
from mmc.plugins.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from mmc.plugins.pulse2.group import ComputerGroupManager
from mmc.support.mmctools import Singleton

from sqlalchemy import *
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

        noms = getInventoryNoms()
        
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
        
    def __machinesOnlyQuery(self, ctx, pattern = None, session = create_session()):
        query = session.query(Machine)
        try:
            query = query.filter(self.machine.c.Name.like("%" + pattern['hostname'] + "%"))
        except KeyError, e:
            pass

        try:
            query = query.filter(self.machine.c.id == fromUUID(pattern['uuid']))
        except KeyError, e:
            pass

        try:
            gid = pattern['gid']
            machines = []
            if ComputerGroupManager().isrequest_group(ctx, gid):
                self.logger.info("isrequest_group")
                machines = map(lambda m: fromUUID(m['uuid']), ComputerGroupManager().requestresult_group(ctx, gid, 0, -1, ''))
                self.logger.info("isrequest_group")
            else:
                machines = map(lambda m: fromUUID(m.uuid), ComputerGroupManager().result_group(ctx, gid, 0, -1, ''))
            query = query.filter(self.machine.c.id.in_(*machines))
        except KeyError, e:
            pass

        # doing dyngroups stuff
        join_query, query_filter = self.filter(self.machine, pattern)
        query = query.select_from(join_query).filter(query_filter).group_by(self.machine.c.id)
        # end of dyngroups
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
                query = query.offset(pattern['min'])
                query = query.limit(int(pattern['max']) - int(pattern['min']))
        except KeyError, e:
            query = query.all()

        session.close()
        return query
    
    def countMachinesOnly(self, ctx, pattern = None):
        """
        Return the number of available machines
        """
        session = create_session()
        query = self.__machinesOnlyQuery(ctx, pattern, session)
        ret = len(query.all())
        session.close()
        return ret
        
    # needed by DyngroupDatabaseHelper
    def mappingTable(self, query):
        table, field = query[2].split('/')
        partTable = self.table[table]
        haspartTable = self.table["has" + table]
        return [haspartTable, partTable]
    
    def mapping(self, query, invert = False):
        table, field = query[2].split('/')
        if possibleQueries()['double'].has_key(query[2]): # double search
            value = possibleQueries()['double'][query[2]]
            partKlass = self.klass[table]
            return and_(
                self.mapping([None, None, value[0][0], query[3][0].replace('(', '')]),
                self.mapping([None, None, value[1][0], query[3][1].replace(')', '')])
            )
        elif possibleQueries()['list'].has_key(query[2]) and possibleQueries()['list'][query[2]][0] == 'int': # Numeric search : ie < > = are possible operators
            partKlass = self.klass[table]
            value = query[3]
            if value.startswith('>') and not invert or value.startswith('<') and invert:
                value = value.replace('>', '').replace('<', '')
                return getattr(partKlass.c, field) > value
            elif value.startswith('>') and invert or value.startswith('<') and not invert:
                value = value.replace('>', '').replace('<', '')
                return getattr(partKlass.c, field) < value
            elif invert:
                return getattr(partKlass.c, field) != value
            else:
                if re.compile('\*').search(value):
                    value = re.compile('\*').sub('%', value)
                    return getattr(partKlass.c, field).like(value)
                return getattr(partKlass.c, field) == value
        elif possibleQueries()['list'].has_key(query[2]): # text search, only = 
            partKlass = self.klass[table]
            value = query[3]
            if invert:
                return getattr(partKlass.c, field) != value
            else:
                if re.compile('\*').search(value):
                    value = re.compile('\*').sub('%', value)
                    return getattr(partKlass.c, field).like(value)
                return getattr(partKlass.c, field) == value

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
        partKlass = self.klass[table]
        partTable = self.table[table]
        
        result = session.query(partKlass).add_column(getattr(partKlass.c, field)).filter(getattr(partKlass.c, field).like('%'+fuzzy_value+'%'))
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
    
    def getMachineNetwork(self, ctx, params):
        return self.getLastMachineInventoryPart(ctx, 'Network', params)

    def getMachineCustom(self, ctx, params):
        return self.getLastMachineInventoryPart(ctx, 'Custom', params)
        
    def countLastMachineInventoryPart(self, ctx, part, params):
        session = create_session()
        partKlass = self.klass[part]
        partTable = self.table[part]
        haspartTable = self.table["has" + part]
        result = self.__lastMachineInventoryPartQuery(session, ctx, part, params)
        result = result.group_by(partTable.c.id).group_by(haspartTable.c.machine)
        result = result.count()
        session.close()
        return result
    
    def getLastMachineInventoryPart(self, ctx, part, params):
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
        result = self.__lastMachineInventoryPartQuery(session, ctx, part, params)
        
        if params.has_key('min') and params.has_key('max'):
            result = result.offset(int(params['min']))
            result = result.limit(int(params['max']) - int(params['min']))
 
        result = result.group_by(partTable.c.id).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
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
                self.logger.debug(machine_inv[res[1]])
            for name in machine_uuid:
                ret.append([name, machine_inv[name], machine_uuid[name]])
        return ret
        
    def __lastMachineInventoryPartQuery(self, session, ctx, part, params):
        partKlass = self.klass[part]
        partTable = self.table[part]
        haspartTable = self.table["has" + part]
        haspartKlass = self.klass["has" + part]

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
              
        result = result.select_from(self.machine.outerjoin(select_from)).filter(self.inventory.c.Last == 1)
        result = self.__filterQuery(ctx, result, params)
        
        # this can't be put in __filterQuer because it's not a generic filter on Machine...
        if params.has_key('where') and params['where'] != '':
            self.logger.debug("1 %s"%(str(params)))
            for where in params['where']:
                self.logger.debug("2 %s"%(str(where)))
                if hasattr(partTable.c, where[0]):
                    self.logger.debug("3 %s"%(str(where[0])))
                    result = result.filter(getattr(partTable.c, where[0]) == where[1])
                else:
                    self.logger.debug("4 %s"%(str(where[0])))
                    if noms.has_key(part):
                        self.logger.debug("5")
                        try:
                            noms[part].index(where[0])
                            nomTableName = 'nom%s%s' % (part, where[0])
                            
                            self.logger.debug("6 %s"%(str(nomTableName)))
                            nomTable = self.table[nomTableName]
                            if hasattr(nomTable.c, where[0]):
                                self.logger.debug("7 %s"%(str(where[1])))
                                result = result.filter(getattr(nomTable.c, where[0]) == where[1])
                            else:
                                self.logger.warn("cant find the required field (%s) in table %s"%(where[0], nomTableName))
                        except ValueError:
                            self.logger.warn("cant find any %s field"%(where[0]))
                    else:
                        self.logger.warn("cant find any %s field"%(where[0]))
        return result
   
    def __filterQuery(self, ctx, query, params):
        if params.has_key('hostname') and params['hostname'] != '':
            query = query.filter(Machine.c.Name==params['hostname'])
        if params.has_key('filter') and params['filter'] != '':
            query = query.filter(Machine.c.Name.like('%'+params['filter']+'%'))
        if params.has_key('uuid') and params['uuid'] != '':
            query = query.filter(Machine.c.id==fromUUID(params['uuid']))
        if params.has_key('gid') and params['gid'] != '':
            machines = map(lambda m: fromUUID(m.uuid), ComputerGroupManager().result_group(ctx, params['gid'], 0, -1, ''))
            query = query.filter(self.machine.c.id.in_(*machines))
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

    def addMachine(self, name, ip, mac, comment = None):
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

def toUUID(id):
    return "UUID%s" % (str(id))

def fromUUID(uuid):
    return int(uuid.replace('UUID', ''))
    
# Class for SQLalchemy mapping
class Machine(object):
    def toH(self):
        return { 'hostname':self.Name, 'uuid':toUUID(self.id) }
        
    def toDN(self, ctx, advanced = False):
        ret = [ False, {'cn':[self.Name], 'objectUUID':[toUUID(self.id)]} ]
        comment = Inventory().getMachineCustom(ctx, {'uuid':toUUID(self.id)})
        if len(comment) != 0:
            ret[1]['displayName'] = [comment[0][1][0]['Comments']]
        for table in Inventory().config.content:
            content = Inventory().config.content[table]
            for col in content:
                params = {'uuid':toUUID(self.id)}
                logging.getLogger().debug("00 1 %s"%(str(col)))
                if len(col) > 2:
                    for p in col[2:]:
                        if not params.has_key('where'):
                            params['where'] = []
                        params['where'].append(p)
                
                logging.getLogger().debug("00 2 %s"%(str(params)))
                part = Inventory().getLastMachineInventoryPart(ctx, table, params)
                if len(part) == 0:
                    ret[1][col[1]] = ''
                else:
                    part = part[0][1]
                    logging.getLogger().debug("part : %s" %(str(part)))
                    ret[1][col[1]] = []
                    for n in part:
                        ret[1][col[1]].append(n[col[0]])
            
        if advanced:
            net = Inventory().getMachineNetwork(ctx, {'uuid':toUUID(self.id)})
            if len(net) == 0:
                ret[1]['ipHostNumber'] = ''
                ret[1]['macAddress'] = ''
            else:
                net = net[0]
                ret[1]['ipHostNumber'] = []
                ret[1]['macAddress'] = []
                for n in net[1]:
                    if n['IP'] != None:
                        ret[1]['ipHostNumber'].append(n['IP'])
                    if n['MACAddress'] != None and n['MACAddress'] != '00-00-00-00-00-00-00-00-00-00-00':
                        ret[1]['macAddress'].append(n['MACAddress'])
        return ret

class InventoryTable(object):
    pass


