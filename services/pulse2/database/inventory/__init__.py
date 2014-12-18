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
Inventory database backend
"""

from pulse2.managers.group import ComputerGroupManager

from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from mmc.database.utilities import unique, handle_deconnect
from mmc.database.utilities import DbObject # pyflakes.ignore
from mmc.database.database_helper import DatabaseHelper, DBObj # pyflakes.ignore
from pulse2.database.inventory.mapping import OcsMapping
from pulse2.utils import same_network, Singleton, isUUID

from sqlalchemy import and_, create_engine, MetaData, Table, Column, \
        Integer, ForeignKey, or_, desc, func, not_, distinct
from sqlalchemy.orm import create_session, mapper
import sqlalchemy.databases

import datetime
import re
import logging

MAX_REQ_NUM = 100


class UserTable(object):
    pass

class UserEntitiesTable(object):
    pass

class Hardware(object):
    pass

class Inventory(DyngroupDatabaseHelper):
    """
    Class to query the LRS/Pulse2 inventory database, populated by OCS inventory.

    DyngroupDatabaseHelper is a Singleton, so is Inventory

    This class does not read the inventory files created by the LRS during a boot phase (/tftpboot/revoboot/log/*.ini)
    """

    def db_check(self):
        self.my_name = "inventory"
        self.configfile = "inventory.ini"
        return DyngroupDatabaseHelper.db_check(self)

    def activate(self, config):
        # Activating or not SQLAlchemy logging
        #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        self.logger = logging.getLogger()
        DyngroupDatabaseHelper.init(self)
        if self.is_activated:
            self.logger.info("Inventory doesn't need activation")
            return None
        self.logger.info("Inventory is activating")
        self.config = config
        PossibleQueries().init(self.config)
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize, convert_unicode=True, echo = False)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            return False
        self.metadata.create_all()
        self.is_activated = True
        self.dbversion = self.getInventoryDatabaseVersion()
        self.logger.debug("Inventory finish activation")
        return self.db_check()

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the inventory database
        """

        self.table = {}
        self.klass = {}
        self.version = Table("Version", self.metadata, autoload = True)
        self.machine = Table("Machine", self.metadata, autoload = True)
        self.inventory = Table("Inventory", self.metadata, autoload = True)
        self.user = Table("User", self.metadata, autoload = True)
        self.userentities = Table('UserEntities',
                                  self.metadata,
                                  Column('fk_User', Integer, ForeignKey('User.id'), primary_key = True),
                                  Column('fk_Entity', Integer, ForeignKey('Entity.id'), primary_key = True))

        # Add inventory tables for Search field (used in __filterQuery)
        self.hardware = Table("Hardware", self.metadata, autoload = True)
        self.bios = Table("Bios", self.metadata, autoload = True)
        self.software = Table("Software", self.metadata, autoload = True)
        self.network = Table("Network", self.metadata, autoload = True)
        self.controller = Table("Controller", self.metadata, autoload = True)
        self.registry = Table("Registry", self.metadata, autoload = True)

        noms = self.config.getInventoryNoms()

        self.table['Inventory'] = self.inventory
        self.klass['Inventory'] = InventoryTable

        self.table['Hardware'] = self.hardware
        self.klass['Hardware'] = Hardware

        mapper(Hardware, self.hardware)

        for item in self.config.getInventoryParts():
            # Declare the SQL table
            self.table[item] = Table(item, self.metadata, autoload = True)
            # Create the class that will be mapped
            # This will create the Bios, BootDisk, etc. classes
            # Inherit from DBObj only for __str__ method (debugging purpose)
            exec "class %s(DbObject, DBObj): pass" % item
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

        # hasInventory don't exists, so we pass by hasNetwork and use the inventory field
        # which mean you have to take care, you can have more than one hasNetwork by Inventory!
        # you always have to group_by inventory when you use hasNetwork
        self.table['hasInventory'] = self.table['hasNetwork']
        self.klass['hasInventory'] = self.klass['hasNetwork']

        try:
            mapper(Machine, self.machine)
            mapper(InventoryTable, self.inventory)
            mapper(UserTable, self.user)
            mapper(UserEntitiesTable, self.userentities)
        except:
            pass


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

    def isInventoried(self, macaddr):
        """
        Search if a machine is already inventoried according to its MAC Address
        @param macaddr: a Mac address
        @type macaddr: string

        @return: Return True if the machine exists according to its MAC Address
        @rtype: bool
        """
        session = create_session()
        q = session.query(self.klass['hasNetwork'])
        q = q.select_from(self.table['hasNetwork'] \
                          .join(self.table['Network'], self.table['Network'].c.id == self.table['hasNetwork'].c.network)
                          .join(self.table['hasBios'], self.table['hasBios'].c.machine == self.table['hasNetwork'].c.machine)
                         )
        q = q.filter(self.table['Network'].c.MACAddress == macaddr)

        session.close()

        return bool(q.count())

    def complete_ctx(self, ctx):
        """
        Set user locations in current security context.
        """
        if not hasattr(ctx, "locations") or ctx.locations == None:
            logging.getLogger().debug("adding locations in context for user %s" % (ctx.userid))
            ctx.locations = self.getUserLocations(ctx.userid)
            ctx.locationsid = map(lambda e: e.id, ctx.locations)

    def __machinesOnlyQuery(self, ctx, pattern = None, session = None, count = False):
        self.complete_ctx(ctx)
        if not session:
            session = create_session()

        # doing dyngroups stuff
        join_query, query_filter = self.filter(ctx, self.machine, pattern, session.query(Machine), self.machine.c.id)

        # Join on entity table for location support
        join_query = join_query.join(self.table['hasEntity']).join(self.table['Entity']).join(self.inventory)

        # Getting requested cols
        try:
            requested_cols = set([col[0] for col in Inventory().config.display])
        except:
            requested_cols = set([])

        # Avoid doing joins if search is not requested
        if 'hostname' in pattern and pattern['hostname'].strip():
            if 'displayName' in requested_cols:
                join_query = join_query.outerjoin(self.table['hasCustom']).outerjoin(self.table['Custom'])
            if set(['macAddress','ipHostNumber','subnetMask']) & requested_cols:
                join_query = join_query.outerjoin(self.table['hasNetwork'], self.table['hasNetwork'].c.machine == Machine.id).outerjoin(self.table['Network'], self.table['Network'].c.id == self.table['hasNetwork'].c.network)
            if set(['os','user','type','domain','fullname']) & requested_cols:
                join_query = join_query.outerjoin(self.table['hasHardware'], self.table['hasHardware'].c.machine == Machine.id).outerjoin(self.table['Hardware'], self.table['Hardware'].c.id == self.table['hasHardware'].c.hardware)
            if "Registry" in self.config.content:
                join_query = join_query.outerjoin(self.table['hasRegistry'], self.table['hasRegistry'].c.machine == Machine.id).outerjoin(self.table['Registry'], self.table['Registry'].c.id == self.table['hasRegistry'].c.registry)

        if count:
            query = session.query(func.count(Machine.id)).select_from(join_query).filter(query_filter)
        else:
            query = session.query(Machine).select_from(join_query).filter(query_filter)
        # end of dyngroups

        # Always select the last inventory
        query = query.filter(self.inventory.c.Last == 1)

        # We first filter the computer list according to the entities the user
        # has the right to see.
        query = query.filter(self.table['Entity'].c.id.in_(ctx.locationsid))

        # Then we apply extra filter according to pattern content
        if pattern:
            if 'green' in pattern:
                date_mod = pattern['green']['date_mod']
                orange = pattern['green']['orange']
                query = query.filter(date_mod > orange)
            if 'orange' in pattern:
                date_mod = pattern['orange']['date_mod']
                orange = pattern['orange']['orange']
                red = pattern['orange']['red']
                query = query.filter(and_(date_mod < orange, date_mod > red))
            if 'red' in pattern:
                date_mod = pattern['red']['date_mod']
                red = pattern['red']['red']
                query = query.filter(date_mod < red)
            if 'hostname' in pattern and pattern['hostname'].strip():
                clauses = []
                # Filtering on hostname
                clauses.append(self.machine.c.Name.like("%" + pattern['hostname'] + "%"))
                # Filtering on description
                if 'displayName' in requested_cols:
                    clauses.append(self.table['Custom'].c.Comments.like("%" + pattern['hostname'] + "%"))
                # Filtering on Network params
                if set(['macAddress','ipHostNumber','subnetMask']) & requested_cols:
                    clauses.append(self.table['Network'].c.MACAddress.like("%" + pattern['hostname'] + "%"))
                    clauses.append(self.table['Network'].c.IP.like("%" + pattern['hostname'] + "%"))
                    clauses.append(self.table['Network'].c.SubnetMask.like("%" + pattern['hostname'] + "%"))
                # Filtering on Hardware params
                if set(['os','user','type','domain','fullname']) & requested_cols:
                    clauses.append(self.table['Hardware'].c.OperatingSystem.like("%" + pattern['hostname'] + "%"))
                    clauses.append(self.table['Hardware'].c.User.like("%" + pattern['hostname'] + "%"))
                    clauses.append(self.table['Hardware'].c.Type.like("%" + pattern['hostname'] + "%"))
                    clauses.append(self.table['Hardware'].c.Workgroup.like("%" + pattern['hostname'] + "%"))
                # Filtering on Registy params
                if "Registry" in self.config.content:
                    clauses.append(self.table['Registry'].c.Value.like("%"+ pattern['hostname'] + "%"))

                # Entity filtering
                if 'entity' in requested_cols:
                    clauses.append(self.table['Entity'].c.Label.like("%" + pattern['hostname'] + "%"))
                # Combining clauses and filetering
                query = query.filter(or_(*clauses))
            if 'filter' in pattern:
                query = query.filter(self.machine.c.Name.like("%" + pattern['filter'] + "%"))
            if 'uuid' in pattern:
                query = query.filter(self.machine.c.id == fromUUID(pattern['uuid']))
            if 'uuids' in pattern and type(pattern['uuids']) == list:
                if len(pattern['uuids']) > 0:
                    query = query.filter(self.machine.c.id.in_(map(lambda m:fromUUID(m), pattern['uuids'])))
                else:
                    query = query.filter("1 = 0")
            if 'location' in pattern and pattern['location']:
                query = query.filter(self.table['Entity'].c.id == fromUUID(pattern['location']))
            if 'request' in pattern:
                request = pattern['request']
                if request != 'EMPTY':
                    if 'equ_bool' in pattern:
                        bool = pattern['equ_bool']
                    else:
                        bool = None
                    machines = map(lambda m: fromUUID(m), ComputerGroupManager().request(ctx, request, bool, 0, -1, ''))
                    query = query.filter(self.machine.c.id.in_(machines))
            if 'gid' in pattern:
                gid = pattern['gid']

                machines = list()
                if ComputerGroupManager().isrequest_group(ctx, gid):
                    machines = map(lambda m: fromUUID(m), ComputerGroupManager().requestresult_group(ctx, gid, 0, -1, ''))
                else:
                     filt = ''
                     if pattern.has_key('hostname'):
                         filt = pattern['hostname']
                     if pattern.has_key('filter'):
                         filt = pattern['filter']
                     if count:
                         # when the entities will be in dyngroup, we will be able to use
                         # ComputerGroupManager().countresult_group(ctx, gid, filt) again
                         machines = map(lambda m: fromUUID(m), ComputerGroupManager().result_group(ctx, gid, 0, -1, filt))
                     else:
                         min = 0
                         max = -1
                         if 'location' not in pattern:
                             # this check will be useless when the entities will be in dyngroup
                             if pattern.has_key('min'):
                                 min = pattern['min']
                             if pattern.has_key('max'):
                                 max = pattern['max']
                         machines = map(lambda m: fromUUID(m), ComputerGroupManager().result_group(ctx, gid, min, max, filt))

                query = query.filter(self.machine.c.id.in_(machines))
                if not ComputerGroupManager().isrequest_group(ctx, gid):
                    if count:
                        return query.scalar()
                    else:
                        return query

        if count:
            return query.scalar()

        # Grouping by machine.id
        query = query.group_by(self.machine.c.id)
        return query

    def getUUIDByMachineName(self, ctx, name):

        session = create_session()
        query = session.query(Machine).filter(self.machine.c.Name==name)
        result = query.all()
        if len(result)==1:
            return toUUID(result[0].id)
        else:
            return None

        session.close()

    def getTotalComputerCount(self):
        session = create_session()
        c = session.query(Machine).count()
        session.close()
        return c

    def getMachinesOnly(self, ctx, pattern = None):
        """
        Return all available machines
        """
        session = create_session()
        query = self.__machinesOnlyQuery(ctx, pattern, session)

        # Disable ORDERBY machine name
        #query = query.order_by(asc(self.machine.c.Name))

        if 'max' in pattern:
            if pattern['max'] != -1:
                if ('gid' in pattern and ComputerGroupManager().isrequest_group(ctx, pattern['gid'])) \
                        or 'gid' not in pattern \
                        or 'gid' in pattern and 'location' in pattern:
                            # the last check (or 'gid' in pattern and 'location' in pattern)
                            # will be useless when the entities will be in dyngroup
                    query = query.offset(pattern['min'])
                    query = query.limit(int(pattern['max']) - int(pattern['min']))
                else:
                    query = query.all()
            else:
                query = query.all()
        else:
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

    def isComputerNameAvailable(self, ctx, locationUUID, name):
        """
        Returns true if there is already a computer with that name
        for the moment, it's global (no entity)
        """
        root_ctx = InventoryContext()
        root_ctx.userid = 'root'
        ret = self.countMachinesOnly(root_ctx, {'hostname':name})
        return (ret == 0)

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
        ret = map(lambda x: (False, {'cn':[x[0]], 'objectUUID':[x[2]]}), result)
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

        tables = self.config.content
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
            ret = {}
            for m in result: # glpi mapping
                ret[m.uuid()] = m.toDN(ctx)
        return ret

    # needed by DyngroupDatabaseHelper
    def computersTable(self):
        return [self.machine]

    def computersMapping(self, computers, invert = False):
        if not invert:
            return Machine.id.in_(map(lambda x:fromUUID(x), computers))
        else:
            return not_(Machine.id.in_(map(lambda x:fromUUID(x), computers)))

    def mappingTable(self, ctx, query):
        q = query[2].split('/')
        table, field = q[0:2]
        self.logger.debug("### >> table %s, field %s"%(table, field))
        if len(q) > 2:
            self.logger.debug("##### >> semi static name : %s"%(q[2]))
        if table == 'Machine':
            return [self.machine, self.table['hasHardware'], self.inventory]
        elif table == 'Inventory':
            return [self.machine, self.table['hasHardware'], self.inventory]
        else:
            partTable = self.table[table]
            haspartTable = self.table["has" + table]
        if self.config.getInventoryNoms(table) == None:
            return [haspartTable, partTable, self.inventory]
        self.logger.debug("### Nom")
        ret = [haspartTable, partTable, self.inventory]
        for nom in self.config.getInventoryNoms(table):
            nomTableName = 'nom%s%s' % (table, nom)
            self.logger.debug("### nomTableName %s"%(nomTableName))
            nomTable = self.table[nomTableName]
            ret.append(nomTable)
        return ret

    def mapping(self, ctx, query, invert = False):
        q = query[2].split('/')
        table, field = q[0:2]
        if PossibleQueries().possibleQueries('double').has_key(query[2]): # double search
            value = PossibleQueries().possibleQueries('double')[query[2]]
            return and_(# TODO NEED TO PATH TO GET THE GOOD SEP!
                self.mapping(ctx, [None, None, value[0][0], query[3][0]]),
                self.mapping(ctx, [None, None, value[1][0], query[3][1]])
            )
        elif PossibleQueries().possibleQueries('triple').has_key(query[2]): # triple search
            queries = PossibleQueries().possibleQueries('triple')[query[2]]

            vendor_query = queries[0][0]
            software_query = queries[1][0]
            version_query = queries[2][0]

            vendor_value = query[3][0].replace('*', '%')
            software_value = query[3][1].replace('*', '%')
            version_value = query[3][2].replace('*', '%')

            def _getMapping(query, value):
                if value == '%':
                    return None
                return self.mapping(ctx, [None, None, query, value])

            return and_(
                _getMapping(vendor_query, vendor_value),
                _getMapping(software_query, software_value),
                _getMapping(version_query, version_value),
            )
        elif PossibleQueries().possibleQueries('list').has_key(query[2]): # list search
            if table == 'Machine':
                partKlass = Machine
            else:
                partKlass = self.klass[table]
            value = query[3]
            if value.startswith('>') and not invert or value.startswith('<') and invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass, field) > value, self.inventory.c.Last == 1)
            elif value.startswith('>') and invert or value.startswith('<') and not invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass, field) < value, self.inventory.c.Last == 1)
            elif invert:
                return and_(getattr(partKlass, field) != value, self.inventory.c.Last == 1)
            else:
                value = value.replace('*', '%')
                return and_(getattr(partKlass, field).like(value), self.inventory.c.Last == 1)

        elif PossibleQueries().possibleQueries('halfstatic').has_key(query[2]): # halfstatic search
            if table == 'Machine':
                partKlass = Machine
            else:
                partKlass = self.klass[table]
            value = query[3]

            hs = PossibleQueries().possibleQueries('halfstatic')[query[2]]
            condition = 1
            if self.config.getInventoryNoms(table) == None:
                condition = (getattr(partKlass, hs[1]) == hs[2])
            else:
                noms = self.config.getInventoryNoms(table)
                try:
                    noms.index(hs[1])
                    nomTableName = 'nom%s%s' % (table, hs[1])
                    nomKlass = self.klass[nomTableName]
                    if hasattr(nomKlass, hs[1]):
                        condition = (getattr(nomKlass, hs[1]) == hs[2])
                except ValueError:
                    condition = (getattr(partKlass, hs[1]) == hs[2])

            if value.startswith('>') and not invert or value.startswith('<') and invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass, field) > value, condition, self.inventory.c.Last == 1)
            elif value.startswith('>') and invert or value.startswith('<') and not invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass, field) < value, condition, self.inventory.c.Last == 1)
            elif invert:
                return and_(getattr(partKlass, field) != value, condition, self.inventory.c.Last == 1)
            else:
                value = value.replace('*', '%')
                return and_(getattr(partKlass, field).like(value), condition, self.inventory.c.Last == 1)
        elif query[2] == 'Software/ProductVersion': # third criteria of triple search
            if table == 'Machine':
                partKlass = Machine
            else:
                partKlass = self.klass[table]
            value = query[3]
            if value.startswith('>') and not invert or value.startswith('<') and invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass, field) > value, self.inventory.c.Last == 1)
            elif value.startswith('>') and invert or value.startswith('<') and not invert:
                value = value.replace('>', '').replace('<', '')
                return and_(getattr(partKlass, field) < value, self.inventory.c.Last == 1)
            elif invert:
                return and_(getattr(partKlass, field) != value, self.inventory.c.Last == 1)
            else:
                value = value.replace('*', '%')
                return and_(getattr(partKlass, field).like(value), self.inventory.c.Last == 1)

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
        for part in self.config.getInventoryParts():
            if part != 'Entity':
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
        p1 = re.compile('\*')
        p2 = re.compile('<')
        p3 = re.compile('>')

        filters = []
        for field in params:
            value = params[field]
            if p1.search(value):
                value = p1.sub('%', value)
                filters.append(getattr(partKlass, field).like(value))
            elif p2.search(value):
                value = p2.sub('', value)
                filters.append(getattr(partKlass, field) < value)
            elif p3.search(value):
                value = p3.sub('', value)
                filters.append(getattr(partKlass, field) > value)
            else:
                filters.append(getattr(partKlass, field) == value)

        session = create_session()
        query = session.query(Machine).\
            add_column(func.max(haspartTable.c.inventory).label("inventoryid")).\
            add_column(func.min(self.inventory.c.Date)).\
            select_from(
                self.machine.join(haspartTable.join(self.inventory).join(partTable))
            )

        # apply filters
        for filter in filters:
            query = query.filter(filter)

        result = query.group_by(self.machine.c.Name).group_by(haspartTable.c.machine).order_by(haspartTable.c.machine).order_by(desc("inventoryid")).order_by(haspartTable.c.inventory)
        session.close()

        if result:
            for res in result:
                ret.append(res[0].Name)

        return ret

    def getMachinesBy(self, ctx, table, field, value, onlyName = True):
        """
        Return a list of machine that correspond to the table.field = value
        """
        ret = []
        session = create_session()
        partKlass = self.klass[table]
        partTable = self.table[table]
        haspartTable = self.table["has" + table]

        result = session.query(Machine).\
            add_column(func.max(haspartTable.c.inventory).label("inventoryid")).\
            add_column(func.min(self.inventory.c.Date)).\
            select_from(self.machine.join(haspartTable).join(self.inventory, getattr(haspartTable.c, 'inventory') == self.inventory.c.id).join(partTable))

        import re
        p1 = re.compile('\*')
        if p1.search(value):
            result = result.filter(getattr(partKlass, field).like(p1.sub('%', value)))
        else:
            result = result.filter(getattr(partKlass, field) == value)

        result = result.group_by(self.machine.c.Name).\
            group_by(haspartTable.c.machine).\
            order_by(haspartTable.c.machine).\
            order_by(desc("inventoryid")).\
            order_by(haspartTable.c.inventory)
        session.close()

        if result and onlyName:
            for res in result:
                ret.append(res[0].Name)
        else:
            for res in result:
                ret.append(res[0].toH())

        return ret

    def getComputersOS(self, uuids):
        """
        Get OS for a given computer
        """
        if isinstance(uuids, str):
            uuids = [uuids]
        session = create_session()
        q = session.query(Machine) \
            .add_column(self.table['Hardware'].c.OperatingSystem) \
                .select_from(self.machine
                    .join(self.table['hasHardware'], self.machine.c.id == self.table['hasHardware'].c.machine) \
                    .join(self.table['Hardware'], self.table['Hardware'].c.id == self.table['hasHardware'].c.hardware)
                    .join(self.table['Inventory'], self.table['Inventory'].c.id == self.table['hasHardware'].c.inventory)
                )
        q = q.filter(
            and_(
                self.machine.c.id.in_([fromUUID(uuid) for uuid in uuids]),
                self.inventory.c.Last == 1,
            )
        )
        session.close()
        res = []
        for machine, OSName in q:
            res.append({
                'uuid': toUUID(machine.id),
                'OSName': OSName,
            })
        return res

    def getMachineByInventory(self, ctx, inventory):
        """
        Return the machine resolved by inventory content.

        The machine resolving is based on existing MAC address registered
        in the database.

        @param ctx: Inventory context
        @type ctx: InventoryContext

        @param inventory: Incoming inventory from the client
        @type inventory: dict

        @return: MAC Address, Machine UUID, Machine name
        @rtype: tuple
        """
        if "Network" in inventory :
            logging.getLogger().debug("Try to associate a MAC address to an existing machine")
            networks = inventory["Network"]
            for network in networks:
                # This "network" (read: nic) xml entry contains a mac address
                if 'MACAddress' in network:
                    mac = network["MACAddress"]
                    # If there's no "virtual" attribute or "virtual" attribute is set to 0
                    # virtual attribute means it's a virtual network interface (vpn...)
                    # which may contains duplicates addresses
                    if not 'Virtual' in network or network['Virtual'] == '0':
                        logging.getLogger().info("Trying to associate to an existing machine using MAC %s" % mac)
                        machines = self.getMachinesBy(ctx,
                                                      "Network",
                                                      "MACAddress",
                                                      mac,
                                                      False)

                        if len(machines) == 1 :
                            uuid = machines[0]["uuid"]
                            name = machines[0]["hostname"]
                            message = "Match found using MAC %s! UUID: %s Hostname: %s" % (mac, uuid, name)
                            logging.getLogger().info(message)
                            return mac, uuid, name
                        elif len(machines) > 1 :
                            logging.getLogger().warn("Cannot resolve machine name: duplicate MAC address (%s)" % mac)
                        else:
                            logging.getLogger().debug("Cannot find a machine with MAC %s" % mac)
                    else:
                        logging.getLogger().info("Skipping MAC %s, interface is marked as being virtual" % mac)

        return None, None, None

    def getMachineByHostnameAndMacs(self, ctx, hostname, macs):
        inventory = {'Network': [{'MACAddress': mac} for mac in macs]}
        machine_mac, machine_uuid, machine_name = self.getMachineByInventory(ctx, inventory)
        if machine_name == hostname:
            return machine_uuid
        self.logger.warn('I can\'t get any UUID for machine %s and macs %s' % (hostname, macs))
        return None

    def getValues(self, table, field):
        """
        return every possible values for a field in a table
        """
        ret = []
        session = create_session()
        if table == 'Machine':
            partKlass = Machine
        else:
            partKlass = self.klass[table]

        result = session.query(partKlass).add_column(getattr(partKlass, field)).limit(MAX_REQ_NUM)
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
        else:
            partKlass = self.klass[table]

        result = session.query(partKlass).add_column(getattr(partKlass, field)).filter(getattr(partKlass, field).like('%'+fuzzy_value+'%')).limit(MAX_REQ_NUM).all()
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
        result = result.filter(getattr(partKlass, field2).like('%'+fuzzy_value+'%')).limit(MAX_REQ_NUM)
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
        result = self.__getValuesWhereQuery(table, field1, value1, field2, session).limit(MAX_REQ_NUM)
        session.close()

        if result:
            for res in result:
                ret.append(res[1])
        return unique(ret)

    def __getValuesWhereQuery(self, table, field1, value1, field2, session = None):
        if session == None:
            session = create_session()
        if table == 'Machine':
            partKlass = Machine
            partTable = self.machine
        else:
            partKlass = self.klass[table]
            partTable = self.table[table]
        query = session.query(partKlass).add_column(getattr(partKlass, field2))
        filterDone = False

        if self.config.getInventoryNoms(table) != None:
            for nom in self.config.getInventoryNoms(table):
                hasTable = self.table['has%s'%(table)]
                nomTableName = 'nom%s%s' % (table, nom)
                nomKlass = self.klass[nomTableName]
                if hasattr(nomKlass, field1):
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
            return getattr(partKlass, field).like(value)
        else:
            return getattr(partKlass, field) == value

    def getMachinesNetworkSorted(self, ctx, params):
        net = self.getLastMachineInventoryPart(ctx, 'Network', params)
        ret = []
        for item in net:
            (ifmac, ifaddr, netmask, ids) = orderIpAdresses(item[1])
            ret.append([item[0], {'IP':ifaddr, 'MACAddress':ifmac, 'SubnetMask':netmask, 'networkUuids':map(lambda x: toUUID(x), ids) }, item[2]])
        return ret

    def getMachineNetwork(self, ctx, params):
        return self.getLastMachineInventoryPart(ctx, 'Network', params)

    def getMachineCustom(self, ctx, params):
        return self.getLastMachineInventoryPart(ctx, 'Custom', params)

    def doesUserHaveAccessToMachine(self, userid, machine_uuid): # TODO implement ...
        return True

    def doesUserHaveAccessToMachines(self, userid, machine_uuid, all = True): # TODO implement ...
        return True

    def getMachineByOwner(self, ctx, user):
        result = self.getLastMachineInventoryPart(ctx, "Hardware", {"Owner": user})
        if len(result) > 0:
            uuid = result[0][2]
            computers = self.getComputersOptimized(ctx, {"uuid" :uuid})
            if len(computers)==1:
                return computers[uuid][1]
            #return result[0][1][0] #[q[0] for q in result][0]
        return None

    def getAvgOwner(self, machine_uuid):
        """
        Based on number of inventory injections (AVG_BASE),
        this method returns the most frequently logged user.

        @param machine_uuid: machine
        @typr machine_uuid: str

        @return: the most frequently logged user
        @rtype: str
        """
        AVG_BASE = 10

        machine_id = fromUUID(machine_uuid)
        session = create_session()

        query = session.query(Hardware)
        query = query.select_from(self.hardware.join(self.table['hasHardware'],
                                                     self.table['hasHardware'].c.hardware == self.table["Hardware"].c.id))
        query = query.filter(self.table['hasHardware'].c.machine == machine_id)

        owners = {}

        for i, hardware in enumerate(query.all()):
            if i == AVG_BASE :
                break
            if hardware.User not in owners:
                owners[hardware.User] = 1
            else:
                owners[hardware.User] += 1

        if len(owners) > 0:
            # the most frequent occurence of user
            return max(owners, key=owners.get)










    def countLastMachineInventoryPart(self, ctx, part, params):
        session = create_session()
        result, grp_by = self.__lastMachineInventoryPartQuery(session, ctx, part, params)
        for grp in grp_by:
            result = result.group_by(grp)
        ret = result.count()
        session.close()
        return ret

    def getLastMachineInventoryPart(self, ctx, part, params):
        return self.__getLastMachineInventoryPart(part, params, ctx)

    def getLastMachineInventoryPart2(self, ctx, part, params):
        # =========================================================
        # Function to Adapt inventory output to
        # GLPI-plugin Like getLastMachineInventoryPart function
        # To use for some inventory sections
        #
        # Making all sections manually
        # =========================================================
        ret = []

        # ============== SUMMARY ==================================
        if part == 'Summary':
            fields = []
            hardware = Inventory().getLastMachineInventoryPart(ctx, "Hardware", params)
            if hardware:
                hardware = hardware[0][1][0]
                fields.append(['Computer Name', ['computer_name', 'text', hardware['Host']]])
                fields.append(['Domain', hardware['Workgroup']])
                fields.append(['Last Logged User', hardware['User']])
                fields.append(['Owner', hardware['Owner']])
                fields.append(['OS', hardware['OperatingSystem']])
                fields.append(['Service Pack', hardware['Build']])
                fields.append(['Windows Key', hardware['OsSerialKey']])
            bios = Inventory().getLastMachineInventoryPart(ctx, "Bios", params)
            if bios:
                bios = bios[0][1][0]
                # XML HARDWARE/CHASSIS_TYPE (FusionInventory)
                if hardware and hardware['Type'] is not None and str(hardware['Type']) != "0":
                    machine_type = hardware['Type']
                # XML BIOS/TYPE (OCS ?)
                # May be NULL, or "0" (int ?)
                elif bios and bios['TypeMachine'] is not None and str(bios['TypeMachine']) != "0":
                    machine_type = bios['TypeMachine']
                else:
                    # Valid SMBIOS type
                    machine_type = 'Unknown'
                if bios['Chipset'] is not None:
                    machine_model = bios['Chipset']
                else:
                    machine_model = 'Unknown'
                fields.append(['Model / Type', ' / '.join([machine_model, machine_type])])
                fields.append(['Manufacturer', bios['ChipVendor']])
                fields.append(['Serial Number', bios['Serial']])
            entity = Inventory().getComputersLocations([params['uuid']])
            if entity.values():
                fields.append(['Entity (Location)', entity.values()[0]['Label']])
            # Non-supported fields
            fields.append(['Inventory Number', ''])
            fields.append(['State', ''])
            #
            custom = Inventory().getMachineCustom(ctx, params)

            if len(custom):
                fields.append(['Description', ['description', 'text', custom[0][1][0]['Comments'] ]])
                fields.append(['Warranty End Date', custom[0][1][0]['WarrantyEnd']])

            ret.append(fields)

        # ============== Processors ==================================
        if part == 'Processors':
            fields = []
            hardware = Inventory().getLastMachineInventoryPart(ctx, "Hardware", params)
            if hardware:
                hardware = hardware[0][1][0]
                fields.append(['Name', hardware['ProcessorType']])
                if hardware['ProcessorFrequency']:
                    fields.append(['Frequency', hardware['ProcessorFrequency'] + ' MHz'])
            ret.append(fields)

        # ============== Memory ===================================

        if part == 'Memory':
            memory = Inventory().getLastMachineInventoryPart(ctx, "Memory", params)
            if memory:
                for item in memory[0][1]:
                    z = [['Name', item['Description']], \
                            ['Type', item['ChipsetType']], \
                            ['Frequency', item['Frequency']]]
                    if item['Size']:
                        z.append(['Size', str(item['Size']) + ' Mb'])
                    ret.append(z)

        # Drives and Harddrives are ignored and replaced by Drives section
        # Inventory DB doesn't differentiate between the two
        # ============== Drives ==================================
        if part == 'Drives':
            #fields = []
            storage = Inventory().getLastMachineInventoryPart(ctx, "Storage", params)
            if storage:
                for item in storage[0][1]:
                    ret.append([['Name', item['Model']], \
                            #['DiskSize', item['DiskSize']], \
                            ['DiskSize ', item['DiskSize']]])


        # ============== Controllers ================================

        if part == 'Controllers':
            #fields = []
            controllers = Inventory().getLastMachineInventoryPart(ctx, "Controller", params)
            if controllers:
                for item in controllers[0][1]:
                    ret.append([['Name', item['ExpandedType']]])


        # ============== GraphicCards ================================

        if part == 'GraphicCards':
            graphicCards = Inventory().getLastMachineInventoryPart(ctx, "VideoCard", params)
            if graphicCards:
                for item in graphicCards[0][1]:
                    ret.append([['Name', item['Model']], \
                            ['Memory', item['VRAMSize']], \
                            ['Type ', item['Chipset']]])

        # ============== Soundcards ================================

        if part == 'SoundCards':
            SoundCards = Inventory().getLastMachineInventoryPart(ctx, "Sound", params)
            if SoundCards:
                for item in SoundCards[0][1]:
                    ret.append([['Name', item['Name']]])

        #>>>>>> TODO : Check if other section is not empty

        # ============== Storage ================================

        if part == 'Storage':
            Storages = Inventory().getLastMachineInventoryPart(ctx, "Drive", params)
            if Storages:
                for item in Storages[0][1]:
                    z = [ ['Device', item['DriveType']], \
                            ['Mount Point', item['DriveLetter']], \
                            ['Filesystem', item['FileSystem']]]
                    if item['DriveLetter'] and item['VolumeName']:
                        z.insert(0,['Name', item['DriveLetter'] + ' ' +str(item['VolumeName'])])
                    if item['TotalSpace']:
                        z.append(['Size', str(item['TotalSpace']) + ' Mb'])
                    if item['FreeSpace']:
                        z.append(['Free Size', str(item['FreeSpace']) + ' Mb'])
                    ret.append(z)

        # ============== Network ================================

        if part == 'Network' or part == 'NetworkCards':
            Network = Inventory().getLastMachineInventoryPart(ctx, "Network", params)
            if Network:
                for item in Network[0][1]:
                    ret.append([['Name', item['CardType']], \
                            ['Network Type', item['NetworkType']], \
                            ['MAC Address', item['MACAddress']], \
                            ['IP', item['IP']], \
                            ['Netmask', item['SubnetMask']], \
                            ['Gateway', item['Gateway']]])

        return ret


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
        partTable = self.table[part]
        result, grp_by = self.__lastMachineInventoryPartQuery(session, ctx, part, params)

        for grp in grp_by:
            result = result.group_by(grp)

        # if needed, filter by date and limit the first date
        if(params.has_key('date')) and params['date'] != '':
                result.order_by(desc(self.klass['Inventory'].Date))

        if params.has_key('min') and params.has_key('max'):
            result = result.offset(int(params['min']))
            result = result.limit(int(params['max']) - int(params['min']))

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
                    noms = self.config.getInventoryNoms()
                    if noms.has_key(part):
                        for i in range(5, len(res)):
                            tmp[noms[part][i-5]] = res[i]
                machine_inv[res[1]].append(tmp)
            for name in machine_uuid:
                ret.append([name, machine_inv[name], machine_uuid[name]])
        return ret

    def __lastMachineInventoryPartQuery(self, session, ctx, part, params):
        self.complete_ctx(ctx)
        partKlass = self.klass[part]
        partTable = self.table[part]
        haspartTable = self.table["has" + part]
        grp_by = [partTable.c.id, haspartTable.c.machine]

        # This SQL query has been built using the one from the LRS inventory module
        # TODO : this request has to be done on Machine and then add the columns so that the left join works...
        #result = session.query(partKlass).add_column(self.machine.c.Name).add_column(self.machine.c.id).add_column(haspartTable.c.inventory.label("inventoryid")).add_column(self.inventory.c.Date).select_from(partTable.outerjoin(haspartTable.join(self.inventory).join(self.machine))).filter(self.inventory.c.Last == 1)
        result = session.query(partKlass).\
            add_column(self.machine.c.Name).\
            add_column(self.machine.c.id).\
            add_column(haspartTable.c.inventory.label("inventoryid")).\
            add_column(self.inventory.c.Date)

        noms = self.config.getInventoryNoms()
        select_from = haspartTable.join(self.inventory).join(partTable).outerjoin(self.machine)
        # Also join on the entity related table to filter on the computers the
        # user has the right to see
        # one machine only view
        #select_from = select_from.join(self.table['hasEntity'], self.table['hasEntity'].c.machine == self.machine.c.id)

        if noms.has_key(part):
            for nom in noms[part]:
                nomTable = self.table['nom%s%s' % (part, nom)]
                select_from = select_from.join(nomTable)
                result = result.add_column(getattr(nomTable.c, nom))
                grp_by.append(nomTable.c.id)

        # Apply a filter on the inventory's date if needed
        if params.has_key('date') and params['date'] != '':
            result = result.select_from(select_from).filter(self.klass['Inventory'].Date <= params['date'])
        elif params.has_key('inventoryId') and params['inventoryId'] != '':
            result = result.select_from(select_from).filter(self.klass['Inventory'].id == params['inventoryId'])
        else:
            result = result.select_from(select_from).filter(self.inventory.c.Last == 1)
        # Filter on the entities the user has the right to see
        # No entity filtering
        #result = result.filter(self.table['hasEntity'].c.entity.in_(ctx.locationsid))
        # Apply other filters
        result = self.__filterQuery(part, ctx, result, params)
        if "User" in params:
            result = result.filter(self.klass['Hardware'].User == params["User"])
        if "Owner" in params:
            result = result.filter(self.klass['Hardware'].Owner == params["Owner"])

        # Apply a filter on the software ProductName if asked in parameters (the filter is loaded from a config file)
        if params.has_key('software_filter') and params['software_filter'] == True and part == 'Software':
            # Get the list of software filters
            software_filter = self.config.getSoftwareFilter()
            for softFilter in software_filter:
                # Filter the query result foreach software filter
                result = result.filter(not_(partKlass.ProductName.like(softFilter)))

        # Apply a filter to hide windows updates
        if params.has_key('hide_win_updates') and params['hide_win_updates'] == True and part == 'Software':
            result = result.filter(not_(partKlass.ProductName.op('regexp')('KB[0-9]+(-v[0-9]+)?(v[0-9]+)?')))

        # this can't be put in __filterQuer because it's not a generic filter on Machine...
        if params.has_key('where') and params['where'] != '':
            for where in params['where']:
                if hasattr(partTable.c, where[0]):
                    if type(where[1]) == list:
                        result = result.filter(getattr(partTable.c, where[0]).in_(where[1]))
                    else:
                        result = result.filter(getattr(partTable.c, where[0]) == where[1])
                else:
                    if noms.has_key(part):
                        try:
                            noms[part].index(where[0])
                            nomTableName = 'nom%s%s' % (part, where[0])

                            nomTable = self.table[nomTableName]
                            if hasattr(nomTable.c, where[0]):
                                result = result.filter(getattr(nomTable.c, where[0]) == where[1])
                            else:
                                self.logger.warn("cant find the required field (%s) in table %s"%(where[0], nomTableName))
                        except ValueError:
                            self.logger.warn("cant find any %s field"%(where[0]))
                    else:
                        self.logger.warn("cant find any %s field"%(where[0]))
        return (result, grp_by)

    def __filterQuery(self, part, ctx, query, params):
        """
        @part param is current tab of inventory
        """
        if params.has_key('hostname') and params['hostname'] != '':
            query = query.filter(Machine.Name==params['hostname'])
        if params.has_key('filter') and params['filter'] != '': # params['filter'] is keyword entered in search field
            # Search keyword in all columns of this tab
            clauses = []
            for column in self.__getattribute__(part.lower()).c: # All columns of current tab
                clauses.append(column.like('%'+params['filter']+'%'))
                #clauses.append(column.like('%'+params['filter']+'%')) # self.table['Custom'].c.Comments.like("%" + pattern['hostname'] + "%")
            # Don't forget to search into Machine's Name
            clauses.append(Machine.Name.like('%'+params['filter']+'%'))
            query = query.filter(or_(*clauses))
        if params.has_key('uuid') and params['uuid'] != '':
            query = query.filter(Machine.id==fromUUID(params['uuid']))
        if params.has_key('uuids'):
            if type(params['uuids']) == list and len(params['uuids']) > 0:
                uuids = map(lambda m: fromUUID(m), params['uuids'])
                query = query.filter(Machine.id.in_(uuids))
            else:
                query = query.filter("1 = 0")
        if params.has_key('gid') and params['gid'] != '':
            if ComputerGroupManager().isrequest_group(ctx, params['gid']):
                machines = map(lambda m: fromUUID(m), ComputerGroupManager().requestresult_group(ctx, params['gid'], 0, -1, ''))
            else:
                machines = map(lambda m: fromUUID(m), ComputerGroupManager().result_group(ctx, params['gid'], 0, -1, ''))
            query = query.filter(self.machine.c.id.in_(machines))
        # Filter using a list of machine ids
        if params.has_key('ids') and len(params['ids']):
            query = query.filter(self.machine.c.id.in_(params['ids']))
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
                    result = result.filter(getattr(table.c, v).like(values[v]))
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

    def canAddMachine(self):
        return True

    def addMachine(self, name, ip, mac, netmask, comment = None, location_uuid = None):
        if location_uuid == None:
            location_uuid = 'UUID1'
        if not (isUUID(location_uuid)):
            # if location is not valid, raise a ValueError
            msg = "inventory.addMachine() : tried to add a computer on an invalid entity (%s), linking it to the root entity" % location_uuid
            logging.getLogger().warn(msg)
            raise ValueError(msg)

        assert(isUUID(location_uuid))

        session = create_session()
        m = Machine()
        m.Name = name
        session.add(m)
        # TODO need to put all other Last to 0
        query = session.query(InventoryTable).select_from(self.inventory.join(self.table['hasNetwork']).join(self.machine)).filter(self.machine.c.Name == name)
        for inv in query:
            inv.Last = 0
            session.add(inv)
        i = InventoryTable()
        i.Last = 1
        i.Date, i.Time = str(datetime.datetime.today()).split(" ")
        session.add(i)
        session.flush()
        net = self.klass['Network']
        hasNet = self.klass['hasNetwork']
        n = net()
        n.MACAddress = mac
        n.IP = ip
        n.SubnetMask = netmask
        session.add(n)
        session.flush()
        h = hasNet()
        h.machine = m.id
        h.network = n.id
        h.inventory = i.id
        session.add(h)
        session.flush()
        if comment != None:
            custom = self.klass['Custom']
            hasCustom = self.klass['hasCustom']
            c = custom()
            c.Comments = comment
            session.add(c)
            session.flush()
            h = hasCustom()
            h.machine = m.id
            h.custom = c.id
            h.inventory = i.id
            session.add(h)
            session.flush()

        if location_uuid != None:
            query = session.query(self.klass['Entity']).filter(self.table['Entity'].c.id == fromUUID(location_uuid)).first()
            if query != None:
                hasEntity = self.klass['hasEntity']
                hl = hasEntity()
                hl.machine = m.id
                hl.entity = query.id
                hl.inventory = i.id
                session.add(hl)
                session.flush()
        session.close()
        return toUUID(m.id)

    def delMachine(self, uuid):
        uuid = fromUUID(uuid)
        session = create_session()
        connection = self.getDbConnection()
        trans = connection.begin()

        m = session.query(Machine).filter(self.machine.c.id == uuid).first()
        i = session.query(InventoryTable).select_from(self.inventory.join(self.table['hasInventory'])).filter(self.table['hasInventory'].c.machine == m.id).first()
        for item in self.config.getInventoryParts():
#            tk = self.klass[item]
#            tt = self.table[item]
#            lk = self.klass['has'+item]
            lt = self.table['has'+item]
# TODO : check if more than one machine use this entry
#            ts = session.query(tk).select_from(tt.join(lt)).filter(lt.c.machine == uuid)
#            for t in ts:
#                session.delete(t)
            connection.execute(lt.delete(lt.c.machine == uuid))

        if i == None:
            self.logger.error('delMachine : try to remove a None Inventory! (%s)'%uuid)
        else:
            session.delete(i)
        session.delete(m)

        session.flush()
        session.close()
        trans.commit()
        return True

    def editMachineName(self, uuid, name):
        """
        Edit the computer name

        @param ctx: the context
        @type: currentContext

        @param uuid: the machine uuid
        @type: str

        @param name: new computer name
        @type: str

        @returns: True if the name changed
        @type: bool

        """
        uuid = fromUUID(uuid)
        session = create_session()
        connection = self.getDbConnection()
        trans = connection.begin()

        try:
            m = session.query(Machine).filter(self.machine.c.id == uuid).first()
            m.Name = name
        except Exception :
            session.flush()
            session.close()
            trans.rollback()
            return False

        session.flush()
        session.close()
        trans.commit()
        return True


    # User management method

    def setUserEntities(self, userid, entities):
        """
        Set entities associated to a user.
        A user that doesn't exist in the database will be added.
        Entities that doesn't exist in the database will be added below the
        root entity. The dot character '.' is the root entity.

        @param userid: the user id (login)
        @param entities: list of entity string
        """
        class RootEntity:
            def __init__(self):
                self.id = 1

        session = create_session()
        # Start transaction
        session.begin()
        # Create/get user
        try:
            u = session.query(UserTable).filter_by(uid = userid).one()
        except Exception:
            u = UserTable()
            u.uid = userid
            session.add(u)
            session.flush()

        # Create/get entities
        elist = []
        for entity in entities:
            if entity == '.':
                e = RootEntity()
            else:
                try:
                    e = session.query(self.klass['Entity']).filter_by(Label = entity).one()
                except Exception:
                    e = self.klass['Entity']()
                    e.Label = entity
                    session.add(e)
                    session.flush()
            elist.append(e)
        # Look for the user to entities mappings that need to be added or
        # removed in database
        toadd = elist[:]
        todel = []
        for ue in session.query(UserEntitiesTable).filter_by(fk_User = u.id):
            found = False
            for entity in elist:
                if entity.id == ue.fk_Entity:
                    # The mapping already exists
                    toadd.remove(entity)
                    found = True
                    break
            if not found:
                # The mapping should be removed
                todel.append(ue)
        # Apply changes
        for ue in todel:
            session.delete(ue)
        for entity in toadd:
            ue = UserEntitiesTable()
            ue.fk_User = u.id
            ue.fk_Entity = entity.id
            session.add(ue)
        session.commit()
        session.close()

    def createEntity(self, name, parent_name = False):
        """
        Create a new entity under parent entity

        If parent_name is False the parent will be the root entity
        """
        session = create_session()
        try:
            e = session.query(self.klass['Entity']).filter_by(Label = name).one()
        except Exception:
            e = self.klass['Entity']()
            e.Label = name

            if parent_name:
                try:
                    p = session.query(self.klass['Entity']).filter_by(Label = parent_name).one()
                except Exception:
                    raise Exception("Parent entity %s doesn't exists" % parent_name)
                else:
                    e.parentId = p.id

            session.add(e)
            session.flush()
        session.close()

    def locationExists(self, location):
        """
        Returns true if the given location exists in database
        """
        session = create_session()
        ret = True
        try:
            session.query(self.klass['Entity']).filter_by(Label = location).one()
        except:
            ret = False
        session.close()
        return ret

    @DatabaseHelper._session
    def getMachineByOsLike(self, session, ctx, osnames, count = 0):
        """
        @return: all machines that have this os using LIKE
        """
        if isinstance(osnames, basestring):
            osnames = [osnames]

        # Freely inspired from getComputersOS() for get machines in DB

        if int(count) == 1:
            query = session.query(func.count(Machine.id))
        else:
            query = session.query(Machine)

        query = query.select_from(self.machine
                    .join(self.table['hasHardware'], self.machine.c.id == self.table['hasHardware'].c.machine) \
                    .join(self.table['Hardware'], self.table['Hardware'].c.id == self.table['hasHardware'].c.hardware)
                    .join(self.table['Inventory'], self.table['Inventory'].c.id == self.table['hasHardware'].c.inventory)
                    .join(
                        self.table['hasEntity'],
                        self.table['hasEntity'].c.inventory == self.table['Inventory'].c.id,
                    )
                )

        query = query.filter(self.inventory.c.Last == 1)

        if osnames == ["other"]:
            query = query.filter(
                    not_(self.table['Hardware'].c.OperatingSystem.like('%Microsoft%Windows%')),
            )
        elif osnames == ["otherw"]:
            query = query.filter(
                and_(
                    not_(self.table['Hardware'].c.OperatingSystem.like('%Microsoft%Windows%7%')),\
                    not_(self.table['Hardware'].c.OperatingSystem.like('%Microsoft%Windows%XP%')),
                    self.table['Hardware'].c.OperatingSystem.like('%Microsoft%Windows%')
                )
            )
        # if osnames == ['%'], we want all machines, including machines without OS (used for reporting, per example...)
        elif osnames != ['%']:
            os_filter = [self.table['Hardware'].c.OperatingSystem.like('%' + osname + '%') for osname in osnames]
            query = query.filter(or_(*os_filter))

        if int(count) == 1:
            return int(query.scalar())
        else:
            return [[q.id, q.Name] for q in query]

    def getMachineByState(self):
        """
        Get machine by state is not supported
        """
        pass

    @DatabaseHelper._session
    def getAllComputers(self, session, ctx, count=0):
        """ @return: all machines that have this type """
        if int(count) == 1:
            query = session.query(func.count(Machine.id))
        else:
            query = session.query(Machine)

        query = query.select_from(self.machine
                    .join(
                        self.table['hasEntity'],
                        (self.table['hasEntity'].c.machine == self.machine.c.id) \
                    )
                    .join(self.table['Inventory'],
                        self.table['Inventory'].c.id == self.table['hasEntity'].c.inventory
                    )
                )

        query = query.filter(self.inventory.c.Last == 1)
        if hasattr(ctx, 'locationsid'):
            query = query.filter(self.table['hasEntity'].c.entity.in_(ctx.locationsid))

        if int(count) == 1:
            ret = int(query.scalar())
        else:
            ret = query.all()
        return ret

    @DatabaseHelper._session
    def getMachineByType(self, session, ctx, types, count=0):
        """ @return: all machines that have this type """
        if isinstance(types, basestring):
            types = [types]

        if int(count) == 1:
            query = session.query(func.count(distinct(Machine.id)))
        else:
            query = session.query(Machine)

        query = query.select_from(self.machine
                    .join(self.table['hasHardware'], (self.machine.c.id == self.table['hasHardware'].c.machine)) \
                    .join(self.table['hasBios'], (self.machine.c.id == self.table['hasBios'].c.machine)) \
                    .join(self.table['Hardware'], self.table['Hardware'].c.id == self.table['hasHardware'].c.hardware)
                    .join(self.table['Bios'], self.table['Bios'].c.id == self.table['hasBios'].c.bios)
                    .join(
                        self.table['hasEntity'],
                        (self.table['hasEntity'].c.machine == self.machine.c.id) \
                    )
                    .join(self.table['Inventory'], and_(
                        self.table['Inventory'].c.id == self.table['hasHardware'].c.inventory,
                        self.table['Inventory'].c.id == self.table['hasBios'].c.inventory,
                        self.table['Inventory'].c.id == self.table['hasEntity'].c.inventory
                    ))
                )

        query = query.filter(self.inventory.c.Last == 1)
        if hasattr(ctx, 'locationsid'):
            query = query.filter(self.table['hasEntity'].c.entity.in_(ctx.locationsid))

        hardwareType = self.table['Hardware'].c.Type
        biosType = self.table['Bios'].c.TypeMachine
        typeField = func.if_(func.isnull(hardwareType) | (hardwareType.in_(['', '0'])), biosType, hardwareType)
        type_filter = [typeField.like(type) for type in types]
        query = query.filter(or_(*type_filter))

        if int(count) == 1:
            ret = int(query.scalar())
        else:
            ret = query.all()
        return ret

    @DatabaseHelper._session
    def getAllSoftwaresImproved(self,
                             session,
                             ctx,
                             name,
                             vendor=None,
                             version=None,
                             count=0):
        """
        This method is used for reporting and license count
        it's inspired from getMachineBySoftware method, but instead of count
        number of machines who have this soft, this method count number of
        softwares

        Example: 5 firefox with different version on a single machine:
            getMachineBySoftware: return 1
            this method: return 5

        I should use getAllSoftwares method, but deadline is yesterday....
        """
        def all_elem_are_none(params):
            for param in params:
                if param is not None:
                    return False
            return True
        def check_list(param):
            if not isinstance(param, list):
                return [param]
            elif all_elem_are_none(param):
                return None
            elif not param:
                return None
            else:
                return param

        name = check_list(name)
        if vendor is not None: vendor = check_list(vendor)
        if version is not None: version = check_list(version)

        if int(count) == 1:
            query = session.query(func.count(self.software.c.ProductName))
        else:
            query = session.query(self.software.c.ProductName)

        query = query.select_from(
            self.software
            .join(self.table['hasSoftware'], self.table['hasSoftware'].c.software == self.software.c.id)
            .join(self.table['hasEntity'], self.table['hasEntity'].c.inventory == self.table['hasSoftware'].c.inventory)
            .join(self.table['Inventory'], self.table['Inventory'].c.id == self.table['hasSoftware'].c.inventory)
        )

        query = query.filter(self.inventory.c.Last == 1)

        name_filter = [self.software.c.ProductName.like(n) for n in name]
        query = query.filter(or_(*name_filter))

        if version is not None:
            version_filter = [self.software.c.ProductVersion.like(v) for v in version]
            query = query.filter(or_(*version_filter))

        if vendor is not None:
            vendor_filter = [self.software.c.Company.like(v) for v in vendor]
            query = query.filter(or_(*vendor_filter))

        if hasattr(ctx, 'locationsid'):
            query = query.filter(self.table['hasEntity'].c.entity.in_(ctx.locationsid))

        if int(count) == 1:
            ret = int(query.scalar())
        else:
            ret = query.all()
        return ret

    def getAllEntities(self, ctx):
        return self.getUserLocations(ctx.userid)

    def getUserLocations(self, userid, with_level = False):
        """
        Returns all the locations granted for a given userid.

        @param with_level: if True, the locations level are also returned
        @returns: a list of locations, or a list of couples (location, level)
                  if with_level is true
        """

        def __addChildren(session, rootid, level):
            # Search children of the root id
            ret = []
            level = level + 1
            q = session.query(self.klass['Entity']).filter(self.table['Entity'].c.parentId == rootid).order_by(self.table['Entity'].c.Label)
            for entity in q:
                if entity.id != 1:
                    if with_level:
                        ret.append((entity, level))
                    else:
                        ret.append(entity)
                    ret.extend(__addChildren(session, entity.id, level))
            return ret

        session = create_session()
        ret = []
        if userid != 'root':
            q = session.query(self.klass['Entity']).select_from(self.table['Entity'].join(self.userentities).join(self.user)).filter(self.user.c.uid == userid).order_by(self.table['Entity'].c.Label)
        else:
            q = session.query(self.klass['Entity']).filter(self.table['Entity'].c.id == 1).order_by(self.table['Entity'].c.Label)
        level = 1
        for entity in q:
            setattr(entity, 'uuid', toUUID(entity.id))
            if with_level:
                ret.append((entity, level))
            else:
                ret.append(entity)
            # Also add entity children
            ret.extend(__addChildren(session, entity.id, level))
        session.close()
        return ret

    def getComputersLocations(self, machine_uuids):
        """
        Return the locations in which the computers are
        """
        session = create_session()
        q = session.query(self.klass['Entity']).add_column(self.machine.c.id).select_from(self.table['Entity'].join(self.table['hasEntity']).join(self.machine).join(self.inventory)).filter(self.machine.c.id.in_(map(fromUUID, machine_uuids)))
        # Always select the last inventory
        q = q.filter(self.inventory.c.Last == 1)
        q = q.all()
        session.close()
        ret = {}
        for entity, mid in q:
            ret[toUUID(mid)] = entity.toH()
        return ret

    def getLocationsCount(self):
        session = create_session()
        count = session.query(self.klass['Entity']).count()
        session.close()
        return count

    def getRootLocation(self):
        """
        Returns the root location
        """
        session = create_session()
        q = session.query(self.klass['Entity']).filter(self.table['Entity'].c.id == 1)
        session.close()
        en = q.first()
        setattr(en, 'uuid', toUUID(en.id))
        return en

    def getLocationsFromPathString(self, location_paths):
        """
        @param: list of entites names
        @return: list of entities UUIDs
        """
        session = create_session()
        ens = []
        for name in location_paths:
            try:
                q = session.query(self.klass['Entity']).filter(self.table['Entity'].c.Label == name).one()
            except sqlalchemy.orm.exc.NoResultFound:
                ens.append(False)
            else:
                ens.append(toUUID(str(q.id)))
        session.close()
        return ens

    def getLocationParentPath(self, loc_uuid):
        """
        """
        session = create_session()
        path = []
        en_id = fromUUID(loc_uuid)
        en = session.query(self.klass['Entity']).filter(self.table['Entity'].c.id == en_id).first()
        parent_id = en.parentId

        while parent_id != en_id:
            en_id = parent_id
            en = session.query(self.klass['Entity']).filter(self.table['Entity'].c.id == parent_id).first()
            path.append(toUUID(en.id))
            parent_id = en.parentId
        return path

    def getLocationName(self, loc_uuid):
        """Return the name of the location

        """
        session = create_session()
        en_id = fromUUID(loc_uuid)
        en = session.query(self.klass['Entity']).filter(self.table['Entity'].c.id == en_id).first()

        return en.Label

    def getUsersInSameLocations(self, userid, locations = None):
        """
        Returns all the users id that share the same locations than the given
        user.
        """
        if locations == None:
            locations = self.getUserLocations(userid)
        ret = []
        if locations:
            inloc = []
            for location in locations:
                inloc.append(location.id)
            session = create_session()
            q = session.query(UserTable).select_from(self.user.join(self.userentities)).filter(self.userentities.c.fk_Entity.in_(inloc)).filter(self.user.c.uid != userid).distinct().all()
            session.close()
            # Only returns the user id
            ret = map(lambda u: u.uid, q)
        # Always append the given userid
        ret.append(userid)
        return ret

    def __getInventoryHistory(self, session, days, only_new, pattern, max = 10, min = 0):
        if only_new:
            only_new_filter = self.inventory.c.Last == 1
        else:
            only_new_filter = None

        return session.query(self.klass['Inventory']).add_entity(Machine). \
                  select_from(self.table['hasInventory'].join(self.machine). \
                  join(self.table['Inventory'])). \
                  filter(and_((func.to_days(func.now()) - func.to_days(self.klass['Inventory'].Date)) <= days, \
                  Machine.Name.like('%' + pattern + '%'), only_new_filter)). \
                  order_by(self.klass['Inventory'].id.desc()).group_by(self.klass['Inventory'].id). \
                  offset(min)

    def getInventoryHistory(self, days, only_new, pattern, max, min):
        """
        Returns the last inventories since n days, and for each inventory, the machine concerned
        @param days: number of days to look back for the inventories
        @type days: int
        @rtype: [(String, Date, boolean), ...]
        @return: a tuple with last inventories since n days with their machines
        """
        session = create_session()
        min = int(min)
        max = int(max)

        results = self.__getInventoryHistory(session, days, only_new, pattern, max, min).limit(max - min)

        ret = []
        for res in results:
            newMachine = True
            # check if there was an inventory for this tuple before n days
            for prev in results :
                if res[1].id == prev[1].id and \
                res[0].Date >= prev[0].Date and res[0].Time > prev[0].Time :
                    newMachine = False
                    break

            timestamp = datetime.datetime.combine(res[0].Date, res[0].Time)
            ret.append((res[1].Name, timestamp, newMachine, toUUID(res[1].id)))

        session.close()
        return ret

    def countInventoryHistory(self, days, only_new, pattern):
        """
        Return the number of inventories for the parameters given
        """
        session = create_session()
        results = self.__getInventoryHistory(session, days, only_new, pattern)
        return results.count()

    def getTypeOfAttribute(self, klass, attr):
        """
        Load the table, the column, and return the type
        """
        table = self.table[klass]
        column = getattr(table.c, attr)
        return column.type

    def getComputerInventoryFull(self, ctx, params):
        """
        Return the full and last (before a given date) inventory of a machine

        @param uuid: uuid of the machine to get inventory
        @param date: date before which search
        @param name: the name of the machine to get inventory
        @type params: dict

        @return: Returns a dictionary where each key is an inventory part name
        @rtype: dict
        """
        ret = {}
        for part in self.config.getInventoryParts():
            # Skip Entity table which is not part of an inventory, and breaks
            # SQL query in getLastMachineInventoryPart
            if part != 'Entity':
                ret[part] = self.getLastMachineInventoryPart(ctx, part, params)
        return ret

    def getComputerInventoryHistory(self, ctx, params):
        """
        Return the list of inventories of a given machine

        @param uuid: uuid of the machine to get inventories
        @type params: dict

        @return: Return a list of all the inventory history of the machine
        @rtype: list
        """
        ret = []
        machineId = ""
        if params.has_key('uuid'):
            uuid = params['uuid']
            machineId = fromUUID(uuid)
        if params.has_key('min'):
            min = params['min']
        else:
            min = 0
        if params.has_key('max'):
            max = params['max']
        else:
            max = 10

        session = create_session()
        results = session.query(self.klass['Inventory']). \
                select_from(self.table['hasInventory'].join(self.table['Inventory']).join(self.machine)). \
                filter(Machine.id == machineId). \
                order_by(self.klass['Inventory'].id.desc()). \
                group_by(self.klass['Inventory'].id). \
                offset(min).limit(max - min)
        session.close()

        for res in results:
            ret.append((res.id, res.Date))
        return ret

    def countComputerInventoryHistory(self, ctx, params):
        """
        Return the number of inventories of a given machine

        @param uuid: uuid of the machine to get inventories
        @type params: dict

        @return: Return a list of all the inventory history of the machine
        @rtype: list
        """
        machineId = ""
        if params.has_key('uuid'):
            uuid = params['uuid']
            machineId = fromUUID(uuid)

        session = create_session()
        count = session.query(self.klass['Inventory']). \
                select_from(self.table['hasInventory'].join(self.table['Inventory']).join(self.machine)). \
                filter(Machine.id == machineId). \
                group_by(self.klass['Inventory'].id)
        count = session.query(self.klass['Inventory']).filter(self.klass['Inventory'].id.in_(map(lambda l:l.id, count))).count()
        session.close()

        return count

    def getComputerInventoryDiff(self, ctx, params):
        """
        Returns the differences between an inventory of the given machine and the previous inventory

        @param uuid: uuid of the machine
        @param inventory: id of the inventory to compare with the previous one
        @type params:dict

        @return: Return a list with the added and the removed elements, sorted by inventory part
        @rtype: list
        """
        machineId = ""
        current_inventory_id = None

        if params.has_key('uuid'):
            uuid = params['uuid']
            # Get the machine ID from the uuid given in the parameters to get all infos about the machine
            machineId = fromUUID(uuid)
        else:
            return [{}, {}]
        if params.has_key('inventoryId'):
            current_inventory_id = int(params['inventoryId'])
        else:
            return [{}, {}]

        from time import strftime
        current_date = strftime("%Y-%m-%d")
        current_time = strftime("%H:%M:%S")

        session = create_session()

        # First, get the Date and the Time of the current_inventory
        try:
            result = session.query(self.klass['Inventory']). \
                    select_from(self.table['Inventory']). \
                    filter(self.klass['Inventory'].id == current_inventory_id). \
                    one()
            current_date = result.Date
            current_time = result.Time
        except Exception, e:
            self.logger.error("Unable to get the current inventory Date or Time for the following reason : \n%s"%(str(e)))
            return [{}, {}]

        # Then, send a query to get the previous inventory before the date and time get above for this machine

        try:
            result = session.query(self.klass['Inventory']). \
                    select_from(self.table['hasInventory'].join(self.machine).join(self.table['Inventory'])). \
                    filter(Machine.id == machineId). \
                    filter(self.klass['Inventory'].Date <= current_date). \
                    filter(self.klass['Inventory'].Time < current_time). \
                    order_by(self.klass['Inventory'].id.desc())
            if result.count() < 1:
                raise Exception("No inventory was made before this one.")
            else:
                previous_inventory_id = result.first().id

        except Exception, e:
            self.logger.error("Unable to get the previous inventory for the following reason : \n%s"%(str(e)))
            return [{}, {}]

        session.close()
        self.logger.debug('Comparing inventory id %d and %d'
                          % (current_inventory_id, previous_inventory_id))

        previous_inventory = {}
        current_inventory = {}
        added_elements = {}
        removed_elements = {}

        # Loop in all the parts of the Inventory (except "Entity") to get the inventory part for a given inventory Id
        for part in self.config.getInventoryParts():
            if part != 'Entity':
                # Set the previous inventory Id in the params list
                params['inventoryId'] = previous_inventory_id
                # Call the method to get the relevant inventory part
                machine_previous_inventory_part = self.getLastMachineInventoryPart(ctx, part, params)
                # Extract the inventory part from the tuple if not empty
                if machine_previous_inventory_part != []:
                    previous_inventory[part] = machine_previous_inventory_part[0][1]
                else:
                    previous_inventory[part] = []

                # Set the current inventory Id in the params list
                params['inventoryId'] = current_inventory_id
                # Call the method to get the relevant inventory part
                machine_current_inventory_part = self.getLastMachineInventoryPart(ctx, part, params)
                # Extract the inventory part from the tuple
                try:
                    current_inventory[part] = machine_current_inventory_part[0][1]
                except IndexError:
                    current_inventory[part] = []

                added_elements[part] = []
                removed_elements[part] = []
                # Loop in the current inventory part to test for each element
                # if it was in the previous inventory
                for current_elem in current_inventory[part]:
                    new = True
                    for previous_elem in previous_inventory[part]:
                        new = new and current_elem['id'] != previous_elem['id']
                    # If there is a new element, add it in the returned tuple
                    if new:
                        added_elements[part].append(current_elem)

                # Loop in the previous inventory part to test for each element
                # if it disappears in the current inventory
                for previous_elem in previous_inventory[part]:
                    removed = True
                    for current_elem in current_inventory[part]:
                        removed = removed and previous_elem['id'] != current_elem['id']
                    # If the element is not in the current inventory, add it
                    # in the returned tuple
                    if removed:
                        removed_elements[part].append(previous_elem)
        # Do ignore to report the identical inventories
        # which unimportants elements makes the differences
        if self.__isIdenticalInventory(added_elements,
                                 removed_elements,
                                 exclude={"Hardware": ["ProcessorFrequency", "id"],
                                          }
                                 ) :
            return [[],[]]

        ret = [added_elements, removed_elements]
        return ret

    def countMachinesByState(self, ctx, orange, red):
        """
        Return number of computers by state
        """
        session = create_session()
        now = datetime.datetime.now()
        orange = now - datetime.timedelta(orange)
        red = now - datetime.timedelta(red)

        # FIXME date_mod must be Inventory.Date + Inventory.Time
        date_mod = self.inventory.c.Date

        ret = {
            "green": int(self.__machinesOnlyQuery(ctx, pattern={"green": {"date_mod": date_mod, "orange": orange}}, session=session, count=True)),
            "orange": int(self.__machinesOnlyQuery(ctx, pattern={"orange": {"date_mod": date_mod, "orange": orange, "red": red}}, session=session, count=True)),
            "red": int(self.__machinesOnlyQuery(ctx, pattern={"red": {"date_mod": date_mod, "red": red}}, session=session, count=True)),
        }
        session.close()
        return ret

    def getLastInventoryThresholds(self):

        try:
            from mmc.plugins.inventory.config import InventoryConfig
        except:
            logging.getLogger().error('Cannot import InventoryConfig, make sure that inventory module is installed')
            return

        # Reading red and orange thresholds
        config = InventoryConfig()
        config.init("inventory")
        if config.cp.has_option("lastinventory", "red"):
            red = config.cp.getint("lastinventory", "red")
        else:
            red = 35

        if config.cp.has_option("lastinventory", "orange"):
            orange = config.cp.getint("lastinventory", "orange")
        else:
            orange = 10

        return (red, orange)



    def getMachineListByState(self, ctx, groupName):
        """
        """
        try:
            from mmc.plugins.dyngroup.config import DGConfig
        except:
            logging.getLogger().error('Cannot import DGConfig module, make sure that dyngroup module is installed')
            return

        (red, orange) = self.getLastInventoryThresholds()

        session = create_session()
        now = datetime.datetime.now()
        orange = now - datetime.timedelta(orange)
        red = now - datetime.timedelta(red)

        # FIXME date_mod must be Inventory.Date + Inventory.Time
        date_mod = self.inventory.c.Date

        if groupName == "green":
            result = self.__machinesOnlyQuery(ctx, pattern={"green": {"date_mod": date_mod, "orange": orange}}, session=session)
        elif groupName == "orange":
            result = self.__machinesOnlyQuery(ctx, pattern={"orange": {"date_mod": date_mod, "orange": orange, "red": red}}, session=session)
        elif groupName == "red":
            result = self.__machinesOnlyQuery(ctx, pattern={"red": {"date_mod": date_mod, "red": red}}, session=session)

        # Limit list according to max_elements_for_static_list param in dyngroup.ini
        result.limit(DGConfig().maxElementsForStaticList)

        ret = {}
        for machine in result.all():
            if machine.Name is not None:
                ret[toUUID(machine.id) + '##' + machine.Name] = {"hostname": machine.Name, "uuid": toUUID(machine.id)}

        session.close()
        return ret

    def getMachineNumberByState(self, ctx):
        """
        return number of machines sorted by state
        default states are:
            * green: less than 10 days
            * orange: more than 10 days and less than 35 days
            * red: more than 35 days

        @return: dictionnary with state as key, number as value
        @rtype: dict
        """

        (red, orange) = self.getLastInventoryThresholds()

        ret = {
            "days": {
                "orange": orange,
                "red": red,
            },
            "count": self.countMachinesByState(ctx, orange, red),
            "machine": {
                "green": {},
                "orange": {},
                "red": {},
            }
        }

        return ret

    def __isIdenticalInventory (self, added, removed, exclude={}) :
        """
        Compare two inventories excluding ignored elements.

        @param added: inventory diff containing added elements
        @type added: dict

        @param removed: inventory diff containing removed elements
        @type added: dict

        @param exclude: ignored parts and elements of inventory
        @type exclude: dict (format: {"part": [list of element keys], ..}

        @return: True if passed diffs are the sames (excluding ignored elements)
        @rtype: bool
        """
        a_keys = set(added.keys())
        r_keys = set(removed.keys())

        # test of egality between the intersections of added/removed parts
        if len(a_keys - r_keys) != 0 and len(r_keys - a_keys) != 0 :
            return False

        for part_key in a_keys :
            for added_part in added[part_key] :
                removed_part = removed[part_key][0]
                a_elem_keys = set(added_part.keys())
                r_elem_keys = set(removed_part.keys())
                # test of egality between the intersections of added/removed elements
                if len(a_elem_keys - r_elem_keys) != 0 and \
                        len(r_elem_keys - a_elem_keys) != 0 :
                    return False

                for elem_key in a_elem_keys :
                    if part_key in exclude :
                        # ignore unimportants elements
                        if elem_key in exclude[part_key] :
                            continue
                    if added_part[elem_key] != removed_part[elem_key] :
                        return False
        return True

    def update_owner(self, machine_uuid):
        """
        Updates the owner of machine.

        @param machine_uuid: uuid of Machine
        @type machine_uuid: str

        """
        session = create_session()

        machine_id = fromUUID(machine_uuid)

        logging.getLogger().info("Trying to update the owner (machine UUID%s)" % (machine_id))

        query = session.query(Hardware)
        query = query.select_from(self.hardware.join(self.table['hasHardware'],
                                                     self.table['hasHardware'].c.hardware == self.table["Hardware"].c.id)\
                                               .join(self.table['Inventory'],
                                                     self.table['Inventory'].c.id == self.table['hasHardware'].c.inventory)
                                 )
        query = query.filter(self.table['hasHardware'].c.machine == machine_id)
        query = query.filter(self.inventory.c.Last == 1)


        hardware = query.first()
        if hardware:
            hardware.Owner = self.getAvgOwner(machine_uuid)
            session.add(hardware)
            session.flush()
            logging.getLogger().info("New owner of machine UUID%s is %s" % (machine_id, hardware.Owner))

        session.close()


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
        # Basic info
        ret = [ False, {'cn':[self.Name], 'objectUUID':[toUUID(self.id)]} ]
        # Get requested cols to display SET
        requested_cols = set([col[0] for col in Inventory().config.display])
        # If comment is requested, we request it
        if 'displayName' in requested_cols:
            comment = Inventory().getMachineCustom(ctx, {'uuid':toUUID(self.id)})
            if len(comment) != 0:
                ret[1]['displayName'] = [comment[0][1][0]['Comments']]
                ret[1]['location'] = [comment[0][1][0]['Location']]
        net = Inventory().getMachineNetwork(ctx, {'uuid':toUUID(self.id)})
        if len(net):
            net = net[0]
            (ret[1]['macAddress'], ret[1]['ipHostNumber'], ret[1]['subnetMask'],  ret[1]['networkUuids']) = orderIpAdresses(net[1])
            ret[1]['networkUuids'] = map(lambda x:'UUID'+str(x),ret[1]['networkUuids'])
        # If a hardware table field is requested
        if set(['os','user','type','domain','fullname']) & requested_cols:
            hardware = Inventory().getLastMachineInventoryPart(ctx, "Hardware", {'uuid':toUUID(self.id)})
            if len(hardware):
                ret[1]['os'] = hardware[0][1][0]['OperatingSystem']
                ret[1]['user'] = hardware[0][1][0]['User']
                ret[1]['owner'] = hardware[0][1][0]['Owner']
                ret[1]['type'] = hardware[0][1][0]['Type']
                ret[1]['domain'] = [hardware[0][1][0]['Workgroup']]
                ret[1]['fullname'] = '.'.join(filter(None, [self.Name, hardware[0][1][0]['Workgroup']]))
        # If entity is requested
        if 'entity' in requested_cols:
            entity = Inventory().getComputersLocations([toUUID(self.id)])
            if entity.values():
                ret[1]['entity'] = entity.values()[0]['Label']
            else:
                ret[1]['entity'] = ''
        # Non-supported attributes
        ret[1]['inventorynumber'] = '';
        ret[1]['state'] = '';
        #
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

def orderIpAdresses(netiface):
    ret_ifmac = []
    ret_ifaddr = []
    ret_netmask = []
    ret_ids = []
    idx_good = 0
    for iface in netiface:
        logging.getLogger().debug("Examined network interface: %s" % str(iface))
        if 'IP' in iface and iface['IP'] and iface['MACAddress'] != '00-00-00-00-00-00-00-00-00-00-00':
            logging.getLogger().debug('can work on')
            if iface['Gateway'] == None or iface['Gateway'] == '':
                logging.getLogger().debug("no gateway")
                ret_ifmac.append(iface['MACAddress'])
                ret_ifaddr.append(iface['IP'])
                ret_netmask.append(iface['SubnetMask'])
                ret_ids.append(iface['id'])
            else:
                if same_network(iface['IP'], iface['Gateway'], iface['SubnetMask']):
                    idx_good += 1
                    logging.getLogger().debug("same net")
                    ret_ifmac.insert(0, iface['MACAddress'])
                    ret_ifaddr.insert(0, iface['IP'])
                    ret_netmask.insert(0, iface['SubnetMask'])
                    ret_ids.insert(0, iface['id'])
                else:
                    logging.getLogger().debug("not same net")
                    ret_ifmac.insert(idx_good, iface['MACAddress'])
                    ret_ifaddr.insert(idx_good, iface['IP'])
                    ret_netmask.insert(idx_good, iface['SubnetMask'])
                    ret_ids.insert(idx_good, iface['id'])
    return (ret_ifmac, ret_ifaddr, ret_netmask, ret_ids)

class InventoryTable(object):
    pass

class PossibleQueries(Singleton):
    def init(self, config):
        self.list = config.list
        self.double = config.double
        self.triple = config.triple
        self.halfstatic = config.halfstatic

    def possibleQueries(self, value = None): # TODO : need to put this in the conf file
        if value == None:
            return {
                'list':self.list,
                'double':self.double,
                'triple':self.triple,
                'halfstatic':self.halfstatic
            }
        else:
            if hasattr(self, value):
                return getattr(self, value)
            return []

class InventoryContext:
    pass

class InventoryCreator(Inventory):

    def __init__(self):
        Inventory.__init__(self)
        handle_deconnect()

        if not hasattr(self, 'ctx'):
            self.ctx = InventoryContext()
            self.ctx.userid = 'root'

    def createNewInventory(self, hostname, inventory, date, setLastFlag = True, coming_from_pxe=False, from_ip='N/A'):
        """
        Add a new inventory for a computer
        """
        # TODO : check that inventory is not empty....
        machine_exists = False
        if not self.canAddMachine():
            return False
        k = 0
        for i in map(lambda x: len(inventory[x]), inventory):
            k = i+k
        if k == 0:
            return False
        dates = date.split(' ')
        if len(dates) != 2:
            # Fix needed for MAC OS OCS inventory agent, which is using a
            # different time stamp format
            dates = date.split('-')
            date = "%s-%s-%s %s:%s:%s"%(dates[0], dates[1], dates[2], dates[3], dates[4], dates[5])
            dates = date.split(' ')
        date = dates

        session = create_session()
        session.begin()
        try:
            machine_mac, machine_uuid, machine_name = self.getMachineByInventory(self.ctx, inventory)

            if machine_mac and machine_uuid and machine_name :
                machine_exists = True
                machines = self.getMachinesOnly(self.ctx, {'uuid': machine_uuid})
                if len(machines) == 1 :
                    m = machines[0]
                else :
                    session.close()
                    logging.getLogger().error("Computer %s seem to appear more than one time in database" %
                                               hostname)
                    return False
            else :
                m = Machine()
                m.Name = hostname
                session.add(m)

            # If machine doesn't exists, check if we can add a machine
            from pulse2.inventoryserver.utils import canDoInventory


            # Machine found in database
            if machine_exists:
                try:
                    os_name = self.getComputersOS([machine_uuid])[0]['OSName']
                except:
                    os_name = ''

                # Known OS is OS not null and not PXE OS
                has_known_os = os_name != '' and os_name != 'Unknown operating system (PXE network boot inventory)'

                # Machine found in database with real OS
                if has_known_os:
                    # Machine found in database with real OS and new inventory is PXE
                    if coming_from_pxe:
                        self.logger.info("Machine %s received a new PXE inventory from %s: skipping (don't overwrite real inventory)" % (str(machine_uuid), str(from_ip)))
                        return False
                    # Machine found in database with real OS and new inventory is real inventory
                    else:
                        self.logger.info("Machine %s received a new inventory from %s: forwarding" % (str(machine_uuid), str(from_ip)))
                # Machine found in database with PXE OS
                else:
                    # Machine found in database with PXE OS and new inventory is PXE
                    if coming_from_pxe:
                        self.logger.info("Machine %s received a new PXE inventory from %s: forwarding (overwrite PXE inventory)" % (str(machine_uuid), str(from_ip)))
                    # Machine found in database with PXE OS and new inventory real inventory
                    else:
                        self.logger.info("Machine %s received a new inventory from %s: forwarding (overwrite PXE inventory)" % (str(machine_uuid), str(from_ip)))
            # Machine is not known, forward anyway
            else:
                if canDoInventory():
                    if coming_from_pxe:
                        self.logger.info("PXE inventory received from %s for an unknown machine: forwarding" % str(from_ip))
                    else:
                        self.logger.info("Inventory received from %s for an unknown machine: forwarding" % str(from_ip))
                else:
                    self.logger.info("Cannot forward inventory (operation denied)")
                    return False


            if machine_exists :
                if setLastFlag:
                    result = session.query(InventoryTable).\
                            select_from(self.inventory.join(self.table['hasEntity']).join(self.machine)).\
                            filter(self.machine.c.id == fromUUID(machine_uuid))

                    for inv in result:
                        inv.Last = 0
                        session.add(inv)

            # Create a new empty inventory, and flag it as the last
            i = InventoryTable()
            i.Date, i.Time = date
            i.Last = setLastFlag and 1 or 0
            session.add(i)
            session.flush()

            inventory = InventoryNetworkComplete(inventory).get()

            # Loop on all inventory parts
            for table, entries_list in inventory.items():
                # table: bios, controller, etc.
                # content: list of entries
                tname = table.lower()

                # This part of inventory is empty, so skip it
                if len(entries_list) == 0:
                    continue

                if "has" + table not in self.klass or table not in self.table :
                    continue

                klass = self.klass[table]
                hasKlass = self.klass['has'+table]
                hasTable = self.table['has'+table]

                hasTable.insert()
                # keep track of already inserted datas for this table
                already_inserted = []
                # loop on all inventory part columns
                for entry in entries_list:
                    # skip if empty
                    if len(entry) == 0:
                        continue
                    try:
                        trunc_entry = {}
                        # Check if the length of fields is big enough to put the data
                        for field in entry:
                            trunc_entry[field] = entry[field]

                            if isinstance(field,str) and  hasattr(klass, field):
                                attr = getattr(klass, field)

                                if isinstance(attr, sqlalchemy.types.Integer):
                                    try:
                                        int(entry[field])
                                    except ValueError:
                                        logging.getLogger().warning("The field %s of the table %s is going to be set to ZERO, please report to us." % (field, table))
                                        logging.getLogger().debug("The value |%s| become |0|" % (entry[field]))
                                        trunc_entry[field] = '0'
                                if hasattr(attr, 'length'):
                                    length = attr.length
                                    if len(entry[field]) >= length:
                                        logging.getLogger().warning("The field %s of the table %s is going to be truncated at %s chars, please report to us."%(field, table, length))
                                        logging.getLogger().debug("The value |%s| become |%s|"%(entry[field], entry[field][0:length]))
                                        trunc_entry[field] = entry[field][0:length]

                        # Look up these columns in the inventory table
                        id = self.getIdInTable(table, trunc_entry, session)
                        # Create them if none found
                        if id == None:
                            k = klass()
                            for field in trunc_entry:
                                if type(field) == str or type(field) == unicode:
                                    setattr(k, field, trunc_entry[field])
                            session.add(k)
                            # Immediately flush this new row, because we need an
                            # id
                            session.flush([k])
                            id = k.id

                        nids = {}
                        if OcsMapping().nomenclatures.has_key(table):
                            for nom in OcsMapping().nomenclatures[table]:
                                nomName = 'nom%s%s' % (table, nom)
                                nomKlass = self.klass[nomName]

                                new_entry = {}
                                for field in entry:
                                    if type(field) == tuple and field[0] == nomName:
                                        new_entry[field[1]] = entry[field]

                                nid = self.getIdInTable(nomName, new_entry, session)
                                if nid == None:
                                    n = nomKlass()
                                    for field in new_entry:
                                        setattr(n, field, new_entry[field])
                                    session.add(n)
                                    # Immediately flush this new row, because
                                    # we need an id
                                    session.flush([n])
                                    nid = n.id
                                nids[nom] = nid
                        # closes if block

                        params = {'machine':m.id, 'inventory':i.id, tname:id}
                        if len(nids.keys()) > 0:
                            for nom in nids:
                                params[nom.lower()] = nids[nom]
                        if params not in already_inserted:
                            # Prepare insertion in the 'has' table
                            hk = hasKlass()
                            for attr, value in params.items():
                                setattr(hk, attr, value)
                            # We will flush the new rows for the 'has' tables
                            # at the end, because it's faster to do it in one
                            # shot
                            session.add(hk)
                            already_inserted.append(params)
                    except UnicodeDecodeError, e: # just for test
                        pass
                    except Exception, e:
                        logging.getLogger().exception(e)
                        pass
                # closes for block
            # closes for block on inventory parts
            session.flush()
            session.commit()
        except Exception, e:
            session.rollback()
            session.close()
            logging.getLogger().exception(e)
            raise e

        session.close()
        if machine_exists :
            self.update_owner(machine_uuid)
            return [True, machine_uuid]

        return True




# TODO - Get this info on the PXE client side !
class InventoryNetworkComplete :
    """
    A little hack to complete computer's inventory.

    In the case of absence the OCS processing, the network info
    is not present on the PXE subscription (only IP & MAC address).
    To use the Wake on LAN, we need also the gateway and netmask info.
    Hope to be on the same network, we can use the server network info.
    """

    SIOCGIFNETMASK = 0x891b

    def __init__(self, inventory):
        """
        @param inventory: inventory to update
        @type inventory: dict
        """

        self._inventory = inventory

        if "Network" in inventory :
            network = inventory["Network"][0]

            if "SubnetMask" not in network and "Gateway" not in network :

                netmask, gateway = self._get_networking()
                if netmask and gateway :
                    inventory["Network"][0]["SubnetMask"] = netmask
                    inventory["Network"][0]["Gateway"] = gateway

                    logging.getLogger().debug("Resolved netmask: %s" % netmask)
                    logging.getLogger().debug("Resolved gateway: %s" % gateway)

                    self._inventory = inventory

    def _get_networking (self) :
        """
        Getting the server's netmask & gateway

        @return: netmask and gateway
        @rtype: tuple
        """

        import socket
        import struct
        import fcntl

        filename = "/proc/net/route"

        route = []
        try :
            r_file = open(filename, "r")

            for line in r_file.readlines():
                r_fields = line.strip().split()
                if r_fields[1] != '00000000' or not int(r_fields[3], 16) & 2:
                    continue
                route.append(r_fields)

            r_file.close()

        except IOError :

            logging.getLogger().warn("Cannot read file '%s'" % filename)
            logging.getLogger().warn("Ignore to get the netmask and gateway")

            return False, False


        iface = route[0][0]

        n_sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        netmask = fcntl.ioctl(n_sck, self.SIOCGIFNETMASK, struct.pack('256s', iface))[20:24]
        gateway = struct.pack("<L", int(route[0][2], 16))

        return socket.inet_ntoa(netmask), socket.inet_ntoa(gateway)

    def get(self) :
        """
        Get the updated inventory.

        @return: inventory
        @rtype: dict
        """
        return self._inventory


