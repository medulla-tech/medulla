# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com
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
This module declare all the necessary stuff to connect to a glpi database in it's
version 0.8x
"""
import os
import logging
import re
from sets import Set
import datetime
import calendar, hashlib
import time
from configobj import ConfigObj
from xmlrpclib import ProtocolError

from sqlalchemy import and_, create_engine, MetaData, Table, Column, String, \
        Integer, Date, ForeignKey, asc, or_, not_, desc, func, distinct
from sqlalchemy.orm import create_session, mapper, relationship
try:
    from sqlalchemy.sql.expression import ColumnOperators
except ImportError:
    from sqlalchemy.sql.operators import ColumnOperators
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import OperationalError
from mmc.support.mmctools import  shlaunch
import base64
import json
import requests
from mmc.site import mmcconfdir
from mmc.database.database_helper import DatabaseHelper
# TODO rename location into entity (and locations in location)
from pulse2.utils import same_network, unique, noNone
from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from pulse2.managers.group import ComputerGroupManager
from mmc.plugins.glpi.config import GlpiConfig
from mmc.plugins.glpi.GLPIClient import XMLRPCClient
from mmc.plugins.glpi.utilities import complete_ctx
from mmc.plugins.glpi.database_utils import decode_latin1, encode_latin1, decode_utf8, encode_utf8, fromUUID, toUUID, setUUID
from mmc.plugins.glpi.database_utils import DbTOA # pyflakes.ignore
from mmc.plugins.dyngroup.config import DGConfig
from distutils.version import LooseVersion, StrictVersion
from mmc.plugins.xmppmaster.config import xmppMasterConfig

from pulse2.database.xmppmaster import XmppMasterDatabase

from mmc.agent import PluginManager
import traceback,sys

class Glpi084(DyngroupDatabaseHelper):
    """
    Singleton Class to query the glpi database in version > 0.80.

    """
    is_activated = False

    def db_check(self):
        self.my_name = "Glpi"
        self.configfile = "glpi.ini"
        return DyngroupDatabaseHelper.db_check(self)

    def try_activation(self, config):
        """
        function to see if that glpi database backend is the one we need to use
        """
        self.config = config
        dburi = self.makeConnectionPath()
        self.db = create_engine(dburi, pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        logging.getLogger().debug('Trying to detect if GLPI version is higher than 0.84')
        try:
            self._glpi_version = self.db.execute('SELECT version FROM glpi_configs').fetchone().values()[0].replace(' ', '')
            return True
        except OperationalError:
            self._glpi_version = self.db.execute('SELECT value FROM glpi_configs WHERE name = "version"').fetchone().values()[0].replace(' ', '')
            if LooseVersion(self._glpi_version) >= LooseVersion('0.84') and LooseVersion(self._glpi_version) <  LooseVersion("0.85"):
                logging.getLogger().debug('GLPI version %s found !' % self._glpi_version)
                return True
            else:
                logging.getLogger().debug('GLPI higher than version 0.84 was not detected')
                return False

    @property
    def glpi_version(self):
        return self._glpi_version

    def glpi_version_new(self):
        return False

    def activate(self, config = None):
        self.logger = logging.getLogger()
        DyngroupDatabaseHelper.init(self)
        if self.is_activated:
            self.logger.info("Glpi don't need activation")
            return None
        self.logger.info("Glpi is activating")
        if config != None:
            self.config = config
        else:
            self.config = GlpiConfig("glpi")
        dburi = self.makeConnectionPath()
        self.db = create_engine(dburi, pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        try:
            self.db.execute(u'SELECT "\xe9"')
            setattr(Glpi084, "decode", decode_utf8)
            setattr(Glpi084, "encode", encode_utf8)
        except:
            self.logger.warn("Your database is not in utf8, will fallback in latin1")
            setattr(Glpi084, "decode", decode_latin1)
            setattr(Glpi084, "encode", encode_latin1)
        try:
            self._glpi_version = self.db.execute('SELECT version FROM glpi_configs').fetchone().values()[0].replace(' ', '')
        except OperationalError:
            self._glpi_version = self.db.execute('SELECT value FROM glpi_configs WHERE name = "version"').fetchone().values()[0].replace(' ', '')
        self.metadata = MetaData(self.db)
        self.initMappers()
        self.logger.info("Glpi is in version %s" % (self.glpi_version))
        self.metadata.create_all()
        self.is_activated = True
        self.logger.debug("Glpi finish activation")

        searchOptionConfFile = os.path.join(mmcconfdir, "plugins", "glpi_search_options.ini")
        self.searchOptions = ConfigObj(searchOptionConfFile)

        return True

    def getTableName(self, name):
        return ''.join(map(lambda x:x.capitalize(), name.split('_')))

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the inventory database
        """

        self.klass = {}

        # simply declare some tables (that dont need and FK relations, or anything special to declare)
        for i in ('glpi_operatingsystemversions', 'glpi_computertypes', 'glpi_operatingsystems', 'glpi_operatingsystemservicepacks', \
        'glpi_domains', 'glpi_computermodels', 'glpi_networks'):
            setattr(self, i, Table(i, self.metadata, autoload = True))
            j = self.getTableName(i)
            exec "class %s(DbTOA): pass" % j
            mapper(eval(j), getattr(self, i))
            self.klass[i] = eval(j)

        # declare all the glpi_device* and glpi_computer_device*
        # two of these tables have a nomenclature one (devicecasetypes and devicememorytypes) but we dont need it for the moment.
        #
        # List of devices:
        # cases, controls, drives, graphiccards, harddrives, motherboards, networkcards,
        # pcis, powersupplies, soundcards

        self.devices = ('devicecases', 'devicecontrols', 'devicedrives', 'devicegraphiccards', 'deviceharddrives', \
                        'devicemotherboards', 'devicenetworkcards', 'devicepcis', 'devicepowersupplies', 'devicesoundcards')
        for i in self.devices:
            setattr(self, i, Table("glpi_%s"%i, self.metadata, autoload = True))
            j = self.getTableName(i)
            exec "class %s(DbTOA): pass" % j
            mapper(eval(j), getattr(self, i))
            self.klass[i] = eval(j)

            setattr(self, "computers_%s"%i, Table("glpi_items_%s"%i, self.metadata,
                Column('items_id', Integer, ForeignKey('glpi_computers.id')),
                Column('%s_id'%i, Integer, ForeignKey('glpi_%s.id'%i)),
                autoload = True))
            j = self.getTableName("computers_%s"%i)
            exec "class %s(DbTOA): pass" % j
            mapper(eval(j), getattr(self, "computers_%s"%i))
            self.klass["computers_%s"%i] = eval(j)

        # entity
        self.entities = Table("glpi_entities", self.metadata, autoload = True)
        mapper(Entities, self.entities)

        # rules
        self.rules = Table("glpi_rules", self.metadata,
        Column('id', Integer, primary_key=True),
        autoload = True)
        mapper(Rule, self.rules)

        self.rule_criterias = Table("glpi_rulecriterias", self.metadata,
        Column('id', Integer, primary_key=True),
        autoload = True)
        mapper(RuleCriterion, self.rule_criterias)

        self.rule_actions = Table("glpi_ruleactions", self.metadata,
        Column('id', Integer, primary_key=True),
        autoload = True)
        mapper(RuleAction, self.rule_actions)

        # location
        self.locations = Table("glpi_locations", self.metadata, autoload = True)
        mapper(Locations, self.locations)

        # logs
        self.logs = Table("glpi_logs", self.metadata,
            Column('items_id', Integer, ForeignKey('glpi_computers.id')),
            autoload = True)
        mapper(Logs, self.logs)

        # processor
        self.processor = Table("glpi_deviceprocessors", self.metadata, autoload = True)
        mapper(Processor, self.processor)

        self.computerProcessor = Table("glpi_items_deviceprocessors", self.metadata,
            Column('items_id', Integer, ForeignKey('glpi_computers.id')),
            Column('deviceprocessors_id', Integer, ForeignKey('glpi_deviceprocessors.id')),
            autoload = True)
        mapper(ComputerProcessor, self.computerProcessor)

        # memory
        self.memory = Table("glpi_devicememories", self.metadata,
            Column('devicememorytypes_id', Integer, ForeignKey('glpi_devicememorytypes.id')),
            autoload = True)
        mapper(Memory, self.memory)

        self.memoryType = Table("glpi_devicememorytypes", self.metadata, autoload = True)
        mapper(MemoryType, self.memoryType)

        self.computerMemory = Table("glpi_items_devicememories", self.metadata,
            Column('items_id', Integer, ForeignKey('glpi_computers.id')),
            Column('devicememories_id', Integer, ForeignKey('glpi_devicememories.id')),
            autoload = True)
        mapper(ComputerMemory, self.computerMemory)

        # interfaces types
        self.interfaceType = Table("glpi_interfacetypes", self.metadata, autoload = True)

        # os
        self.os = Table("glpi_operatingsystems", self.metadata, autoload = True)
        mapper(OS, self.os)

        self.os_sp = Table("glpi_operatingsystemservicepacks", self.metadata, autoload = True)
        mapper(OsSp, self.os_sp)

        # domain
        self.domain = Table('glpi_domains', self.metadata, autoload = True)
        mapper(Domain, self.domain)

        # glpi_infocoms
        self.infocoms = Table('glpi_infocoms', self.metadata,
                              Column('suppliers_id', Integer, ForeignKey('glpi_suppliers.id')),
                              Column('items_id', Integer, ForeignKey('glpi_computers.id')),
                              autoload = True)
        mapper(Infocoms, self.infocoms)

        # glpi_suppliers
        self.suppliers = Table('glpi_suppliers', self.metadata, autoload = True)
        mapper(Suppliers, self.suppliers)

        # glpi_filesystems
        self.diskfs = Table('glpi_filesystems', self.metadata, autoload = True)
        mapper(DiskFs, self.diskfs)

        self.disk = Table("glpi_computerdisks", self.metadata, autoload = True)
        mapper(Disk, self.disk)

        # glpi_operatingsystemversions
        self.os_version = Table('glpi_operatingsystemversions', self.metadata, autoload = True)
        mapper(OsVersion, self.os_version)

        ## Fusion Inventory tables

        self.fusionantivirus = None
        try:
            self.logger.debug('Try to load fusion antivirus table...')
            self.fusionantivirus = Table('glpi_computerantiviruses', self.metadata,
                Column('computers_id', Integer, ForeignKey('glpi_computers.id')),
                Column('manufacturers_id', Integer, ForeignKey('glpi_manufacturers.id')),
                autoload = True)
            mapper(FusionAntivirus, self.fusionantivirus)
            self.logger.debug('... Success !!')
        except:
            self.logger.warn('Load of fusion antivirus table failed')
            self.logger.warn('This means you can not know antivirus statuses of your machines.')
            self.logger.warn('This feature comes with Fusioninventory GLPI plugin')

        # glpi_plugin_fusioninventory_locks
        self.fusionlocks = None
        # glpi_plugin_fusioninventory_agents
        self.fusionagents = None

        if self.fusionantivirus is not None: # Fusion is not installed
            self.logger.debug('Load glpi_plugin_fusioninventory_locks')
            self.fusionlocks = Table('glpi_plugin_fusioninventory_locks', self.metadata,
                Column('items_id', Integer, ForeignKey('glpi_computers.id')),
                autoload = True)
            mapper(FusionLocks, self.fusionlocks)
            self.logger.debug('Load glpi_plugin_fusioninventory_agents')
            self.fusionagents = Table('glpi_plugin_fusioninventory_agents', self.metadata,
                Column('computers_id', Integer, ForeignKey('glpi_computers.id')),
                autoload = True)
            mapper(FusionAgents, self.fusionagents)


        #####################################
        # GLPI 0.84 Network tables
        # TODO take care with the itemtype should we always set it to Computer => Yes
        #####################################

        # TODO Are these table needed (inherit of previous glpi database*py files) ?
        self.networkinterfaces = Table("glpi_networkinterfaces", self.metadata, autoload = True)
        mapper(NetworkInterfaces, self.networkinterfaces)

        self.net = Table("glpi_networks", self.metadata, autoload = True)
        mapper(Net, self.net)

        # New network tables
        self.ipnetworks = Table("glpi_ipnetworks", self.metadata, autoload = True)
        mapper(IPNetworks, self.ipnetworks)

        self.ipaddresses_ipnetworks = Table("glpi_ipaddresses_ipnetworks", self.metadata,
            Column('ipaddresses_id', Integer, ForeignKey('glpi_ipaddresses.id')),
            Column('ipnetworks_id', Integer, ForeignKey('glpi_networks.id')),
            autoload = True)
        mapper(IPAddresses_IPNetworks, self.ipaddresses_ipnetworks)

        self.ipaddresses = Table("glpi_ipaddresses", self.metadata, autoload = True)
        mapper(IPAddresses, self.ipaddresses, properties = {
            'ipnetworks': relationship(IPNetworks, secondary = self.ipaddresses_ipnetworks,
                primaryjoin = self.ipaddresses.c.id == self.ipaddresses_ipnetworks.c.ipaddresses_id,
                secondaryjoin = self.ipnetworks.c.id == self.ipaddresses_ipnetworks.c.ipnetworks_id,
                foreign_keys = [
                    self.ipaddresses_ipnetworks.c.ipaddresses_id,
                    self.ipaddresses_ipnetworks.c.ipnetworks_id,
                ])
        })

        self.networknames = Table("glpi_networknames", self.metadata, autoload = True)
        mapper(NetworkNames, self.networknames, properties = {
            # ipaddresses is a one2many relation from NetworkNames to IPAddresses
            # so uselist must be set to True
            'ipaddresses': relationship(IPAddresses, primaryjoin=and_(
                IPAddresses.items_id == self.networknames.c.id,
                IPAddresses.itemtype == 'NetworkName'
            ), uselist = True, foreign_keys = [self.networknames.c.id]),
        })

        self.networkports = Table("glpi_networkports", self.metadata, autoload = True)
        mapper(NetworkPorts, self.networkports, properties = {
            'networknames': relationship(NetworkNames, primaryjoin=and_(
                NetworkNames.items_id == self.networkports.c.id,
                NetworkNames.itemtype == 'NetworkPort'
            ), foreign_keys = [self.networkports.c.id]),
        })

        # machine (we need the foreign key, so we need to declare the table by hand ...
        #          as we don't need all columns, we don't declare them all)
        self.machine = Table("glpi_computers", self.metadata,
            Column('id', Integer, primary_key=True),
            Column('entities_id', Integer, ForeignKey('glpi_entities.id')),
            Column('operatingsystems_id', Integer, ForeignKey('glpi_operatingsystems.id')),
            Column('operatingsystemversions_id', Integer, ForeignKey('glpi_operatingsystemversions.id')),
            Column('operatingsystemservicepacks_id', Integer, ForeignKey('glpi_operatingsystemservicepacks.id')),
            Column('locations_id', Integer, ForeignKey('glpi_locations.id')),
            Column('domains_id', Integer, ForeignKey('glpi_domains.id')),
            Column('networks_id', Integer, ForeignKey('glpi_networks.id')),
            Column('computermodels_id', Integer, ForeignKey('glpi_computermodels.id')),
            Column('computertypes_id', Integer, ForeignKey('glpi_computertypes.id')),
            Column('groups_id', Integer, ForeignKey('glpi_groups.id')),
            Column('users_id', Integer, ForeignKey('glpi_users.id')),
            Column('manufacturers_id', Integer, ForeignKey('glpi_manufacturers.id')),
            Column('name', String(255), nullable=False),
            Column('serial', String(255), nullable=False),
            #Column('license_id', String(255), nullable=True),
            Column('is_deleted', Integer, nullable=False),
            Column('is_template', Integer, nullable=False),
            Column('states_id', Integer, ForeignKey('glpi_states.id'), nullable=False),
            Column('comment', String(255), nullable=False),
            Column('date_mod', Date, nullable=False),
            autoload = True)
        mapper(Machine, self.machine, properties = {
            # networkports is a one2many relation from Machine to NetworkPorts
            # so uselist must be set to True
            'networkports': relationship(NetworkPorts, primaryjoin=and_(
                NetworkPorts.items_id == self.machine.c.id,
                NetworkPorts.itemtype == 'Computer'
            ), uselist = True, foreign_keys = [self.machine.c.id]),
            'domains': relationship(Domain),
        })


        # states
        self.state = Table("glpi_states", self.metadata, autoload = True)
        mapper(State, self.state)
        # profile
        self.profile = Table("glpi_profiles", self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(255), nullable=False))
        mapper(Profile, self.profile)

        # user
        self.user = Table("glpi_users", self.metadata,
            Column('id', Integer, primary_key=True),
            Column('locations_id', Integer, ForeignKey('glpi_locations.id')),
            Column('name', String(255), nullable=False),
            Column('password', String(40), nullable=False),
            Column('firstname', String(255), nullable=False),
            Column('realname', String(255), nullable=False),
            Column('auths_id', Integer, nullable=False),
            Column('is_deleted', Integer, nullable=False),
            Column('is_active', Integer, nullable=False))
        mapper(User, self.user)

        # userprofile
        self.userprofile = Table("glpi_profiles_users", self.metadata,
            Column('id', Integer, primary_key=True),
            Column('users_id', Integer, ForeignKey('glpi_users.id')),
            Column('profiles_id', Integer, ForeignKey('glpi_profiles.id')),
            Column('entities_id', Integer, ForeignKey('glpi_entities.id')),
            Column('is_dynamic', Integer),
            Column('is_recursive', Integer))
        mapper(UserProfile, self.userprofile)

        # glpi_manufacturers
        self.manufacturers = Table("glpi_manufacturers", self.metadata, autoload = True)
        mapper(Manufacturers, self.manufacturers)

        # software
        self.software = Table("glpi_softwares", self.metadata,
                              Column('manufacturers_id', Integer, ForeignKey('glpi_manufacturers.id')),
                              autoload = True)
        mapper(Software, self.software)

        # glpi_inst_software
        self.inst_software = Table("glpi_computers_softwareversions", self.metadata,
            Column('computers_id', Integer, ForeignKey('glpi_computers.id')),
            Column('softwareversions_id', Integer, ForeignKey('glpi_softwareversions.id')),
            autoload = True)
        mapper(InstSoftware, self.inst_software)

        # glpi_licenses
        self.licenses = Table("glpi_softwarelicenses", self.metadata,
            Column('softwares_id', Integer, ForeignKey('glpi_softwares.id')),
            autoload = True)
        mapper(Licenses, self.licenses)

        # glpi_softwareversions
        self.softwareversions = Table("glpi_softwareversions", self.metadata,
                Column('softwares_id', Integer, ForeignKey('glpi_softwares.id')),
                autoload = True)
        mapper(SoftwareVersion, self.softwareversions)

        # model
        self.model = Table("glpi_computermodels", self.metadata, autoload = True)
        mapper(Model, self.model)

        # group
        self.group = Table("glpi_groups", self.metadata, autoload = True)
        mapper(Group, self.group)

        # collects
        self.collects = Table("glpi_plugin_fusioninventory_collects", self.metadata,
            Column('entities_id', Integer, ForeignKey('glpi_entities.id')),
            autoload = True)
        mapper(Collects, self.collects)

        # registries
        self.registries = Table("glpi_plugin_fusioninventory_collects_registries", self.metadata,
            Column('plugin_fusioninventory_collects_id', Integer, ForeignKey('glpi_plugin_fusioninventory_collects.id')),
            autoload = True)
        mapper(Registries, self.registries)

        # registries contents
        self.regcontents = Table("glpi_plugin_fusioninventory_collects_registries_contents", self.metadata,
            Column('computers_id', Integer, ForeignKey('glpi_computers.id')),
            Column('plugin_fusioninventory_collects_registries_id', Integer, ForeignKey('glpi_plugin_fusioninventory_collects_registries.id')),
            autoload = True)
        mapper(RegContents, self.regcontents)

    ##################### internal query generators
    def __filter_on(self, query):
        """
        Use the glpi.ini conf parameter filter_on to filter machines on some parameters
        The request is in OR not in AND, so be carefull with what you want
        """
        ret = self.__filter_on_filter(query)
        if type(ret) == type(None):
            return query
        else:
            return query.filter(ret)

    def __filter_on_filter(self, query):
        if self.config.filter_on != None:
            a_filter_on = []
            for filter_key, filter_values in self.config.filter_on.items():
                if filter_key == 'state':
                    self.logger.debug('will filter %s in (%s)' % (filter_key, str(filter_values)))
                    a_filter_on.append(self.machine.c.states_id.in_(filter_values))
                if filter_key == 'type':
                    self.logger.debug('will filter %s in (%s)' % (filter_key, str(filter_values)))
                    a_filter_on.append(self.machine.c.computertypes_id.in_(filter_values))
                if filter_key == 'entity':
                    self.logger.debug('will filter %s in (%s)' % (filter_key, str(filter_values)))
                    a_filter_on.append(self.machine.c.entities_id.in_(filter_values))
                if filter_key == 'autoupdatesystems_id':
                    self.logger.debug('will filter %s in (%s)' % (filter_key, str(filter_values)))
                    a_filter_on.append(self.machine.c.autoupdatesystems_id.in_(filter_values))
                if not filter_key in ('state','type','entity','autoupdatesystems_id') :
                    self.logger.warn('dont know how to filter on %s' % (filter_key))
            if len(a_filter_on) == 0:
                return None
            elif len(a_filter_on) == 1:
                return a_filter_on[0]
            else:
                return and_(*a_filter_on)
        return None

    def __filter_on_entity(self, query, ctx, other_locids = None):
        # Mutable list used other_locids as default argument to a method or function
        other_locids = other_locids or []
        ret = self.__filter_on_entity_filter(query, ctx, other_locids)
        return query.filter(ret)

    def __filter_on_entity_filter(self, query, ctx, other_locids = None):
        # FIXME: I put the locationsid in the security context to optimize the
        # number of requests. locationsid is set by
        # glpi.utilities.complete_ctx, but when querying via the dyngroup
        # plugin it is not called.
        # Mutable list used other_locids as default argument to a method or function
        other_locids = other_locids or []
        if not hasattr(ctx, 'locationsid'):
            complete_ctx(ctx)
        return self.machine.c.entities_id.in_(ctx.locationsid + other_locids)

    def mini_computers_count(self):
        """Count all the GLPI machines
            Returns:
                int count of machines"""

        sql = """select count(id) as count_machines from glpi_computers;"""
        res = self.db.execute(sql)
        for element in res:
            result = element[0]
        return result

    def __xmppmasterfilter(self, filt = None):
        ret = {}#if filt['computerpresence'] == "presence":
        if "computerpresence" in filt:
            d = XmppMasterDatabase().getlistPresenceMachineid()
            listid = [x.replace("UUID", "") for x in d]
            ret["computerpresence"] = ["computerpresence","xmppmaster",filt["computerpresence"] , listid]
        elif "query" in filt and filt['query'][0] == "AND":
            for q in filt['query'][1]:
                if len(q) >=3 and (q[2] == "Online computer" or q[2] == "OU user" or q[2] == "OU machine"):
                    listid = XmppMasterDatabase().getxmppmasterfilterforglpi(q)
                    ret[q[2]] = [q[1], q[2], q[3], listid]
        return ret

    @DatabaseHelper._sessionm
    def get_machines_list(self, session, start, end, ctx):
        # start and end are used to set the limit parameter in the query
        start = int(start)
        end = int(end)

        location = ""
        criterion = ""

        master_config = xmppMasterConfig()
        reg_columns = []
        r=re.compile(r'reg_key_.*')
        regs=filter(r.search, self.config.summary)
        for regkey in regs:
            regkeyconf = getattr( master_config, regkey).split("|")[0].split("\\")[-1]
            #logging.getLogger().error(regkeyconf)
            reg_columns.append(regkeyconf)

        # location filter is corresponding to the entity selection in the interface
        if "location" in ctx and ctx['location'] != "":
            location = ctx['location'].replace("UUID", "")

        # "filter" filter is corresponding to the string the user wants to find
        if "filter" in ctx and ctx["filter"] != "":
            criterion = ctx["filter"]


        # Get the list of online computers
        online_machines = []
        online_machines = XmppMasterDatabase().getlistPresenceMachineid()
        online_machines = [int(id.replace("UUID","")) for id in online_machines]

        query = session.query(Machine.id.label('uuid')).distinct(Machine.id)\
        .join(self.glpi_computertypes, Machine.computertypes_id == self.glpi_computertypes.c.id)\
        .outerjoin(self.user, Machine.users_id == self.user.c.id)\
        .join(Entities, Entities.id == Machine.entities_id)\
        .outerjoin(self.locations, Machine.locations_id == self.locations.c.id)\
        .outerjoin(self.manufacturers, Machine.manufacturers_id == self.manufacturers.c.id)\
        .join(self.glpi_computermodels, Machine.computermodels_id == self.glpi_computermodels.c.id)\
        .outerjoin(self.regcontents, Machine.id == self.regcontents.c.computers_id)

        if 'cn' in self.config.summary:
            query = query.add_column(Machine.name.label("cn"))

        if 'os' in self.config.summary:
            query = query.add_column(self.os.c.name.label("os")).join(self.os)

        if 'description' in self.config.summary:
            query = query.add_column(Machine.comment.label("description"))

        if 'type' in self.config.summary:
            query = query.add_column(self.glpi_computertypes.c.name.label("type"))

        if 'owner_firstname' in self.config.summary:
            query = query.add_column(self.user.c.firstname.label("owner_firstname"))

        if 'owner_realname' in self.config.summary:
            query = query.add_column(self.user.c.realname.label("owner_realname"))

        if 'owner' in self.config.summary:
            query = query.add_column(self.user.c.name.label("owner"))

        if 'user' in self.config.summary:
            query = query.add_column(Machine.contact.label("user"))

        if 'entity' in self.config.summary:
            query = query.add_column(Entities.name.label("entity"))

        if 'location' in self.config.summary:
            query = query.add_column(self.locations.c.name.label("location"))

        if 'model' in self.config.summary:
            query = query.add_column(self.model.c.name.label("model"))

        if 'manufacturer' in self.config.summary:
            query = query.add_column(self.manufacturers.c.name.label("manufacturer"))

        # Don't select deleted or template machines
        query = query.filter(Machine.is_deleted==0)\
        .filter(Machine.is_template==0)

        # Select machines from the specified entity
        if location != "":
            query = query.filter(Entities.id == location)

        # Add all the like clauses to find machines containing the criterion
        if filter != "":
            query = query.filter(or_(
                Machine.name.contains(criterion),
                Machine.comment.contains(criterion),
                self.os.c.name.contains(criterion),
                self.glpi_computertypes.c.name.contains(criterion),
                Machine.contact.contains(criterion),
                Entities.name.contains(criterion),
                self.user.c.firstname.contains(criterion),
                self.user.c.realname.contains(criterion),
                self.user.c.name.contains(criterion),
                self.locations.c.name.contains(criterion),
                self.manufacturers.c.name.contains(criterion),
                self.model.c.name.contains(criterion),
                self.regcontents.c.value.contains(criterion)
            ))

        # All computers
        if "computerpresence" not in ctx:
            # Do nothing more
            pass
        elif ctx["computerpresence"] == "no_presence":
            query = query.filter(Machine.id.notin_(online_machines))
        else:
            query = query.filter(Machine.id.in_(online_machines))
        query = self.__filter_on(query)

        # From now we can have the count of machines
        count = query.count()

        # Then continue with others criterions and filters
        query = query.offset(start).limit(end)

        columns_name = [column['name'] for column in query.column_descriptions]
        machines = query.all()

        result = {"count" : count, "data":{index : [] for index in columns_name}}
        result['data']['presence'] = []

        nb_columns = len(columns_name)

        regs = {reg_column :[] for reg_column in reg_columns}
        result['data']['reg'] = regs

        for machine in machines:
            _count = 0
            while _count < nb_columns:
                result['data'][columns_name[_count]].append(machine[_count])
                _count += 1

            if int(machine[0]) in online_machines:
                result['data']['presence'].append(1)
            else:
                result['data']['presence'].append(0)

            for column in reg_columns:
                result['data']['reg'][column].append(None)

        regquery = session.query(
            self.regcontents.c.computers_id,
            self.regcontents.c.key,
            self.regcontents.c.value)\
        .filter(
            and_(
                self.regcontents.c.key.in_(reg_columns),
                self.regcontents.c.computers_id.in_(result['data']['uuid'])
            )
        ).all()
        for reg in regquery:
            print(reg)
            index = result['data']['uuid'].index(reg[0])
            result['data']['reg'][reg[1]][index] = reg[2]

        result['count'] = count
        return result

    def __getRestrictedComputersListQuery(self, ctx, filt = None, session = create_session(), displayList = False, count = False):
        """
        Get the sqlalchemy query to get a list of computers with some filters
        If displayList is True, we are displaying computers list
        """
        if session == None:
            session = create_session()

        query = (count and session.query(func.count(Machine.id))) or session.query(Machine)
        # manage criterion  for xmppmaster
        ret = self.__xmppmasterfilter(filt)

        if filt:
            # filtering on query
            join_query = self.machine

            if displayList and not count:
                if 'os' in self.config.summary:
                    query = query.add_column(self.os.c.name)
                if 'type' in self.config.summary:
                    query = query.add_column(self.glpi_computertypes.c.name)
                if 'inventorynumber' in self.config.summary:
                    query = query.add_column(self.machine.c.otherserial)
                if 'state' in self.config.summary:
                    query = query.add_column(self.state.c.name)
                if 'entity' in self.config.summary:
                    query = query.add_column(self.entities.c.name) # entities
                if 'location' in self.config.summary:
                    query = query.add_column(self.locations.c.name) # locations
                if 'model' in self.config.summary:
                    query = query.add_column(self.glpi_computermodels.c.name)
                if 'manufacturer' in self.config.summary:
                    query = query.add_column(self.manufacturers.c.name)
                if 'owner_firstname' in self.config.summary:
                    query = query.add_column(self.user.c.firstname)
                if 'owner_realname' in self.config.summary:
                    query = query.add_column(self.user.c.realname)
                if 'owner' in self.config.summary:
                    query = query.add_column(self.user.c.name)

            query_filter = None

            filters = [self.machine.c.is_deleted == 0, self.machine.c.is_template == 0, self.__filter_on_filter(query), self.__filter_on_entity_filter(query, ctx)]

            join_query, query_filter = self.filter(ctx, self.machine, filt, session.query(Machine), self.machine.c.id, filters)

            # filtering on locations
            if 'location' in filt:
                location = filt['location']
                if location == '' or location == u'' or not self.displayLocalisationBar:
                    location = None
            else:
                location = None

            # Imaging group
            if 'imaging_entities' in filt:
                location = filt['imaging_entities']

            if 'ctxlocation' in filt:
                ctxlocation = filt['ctxlocation']
                if not self.displayLocalisationBar:
                    ctxlocation = None
            else:
                ctxlocation = None

            if ctxlocation != None:
                locsid = []
                if isinstance(ctxlocation, list):
                    for loc in ctxlocation:
                        locsid.append(self.__getId(loc))
                join_query = join_query.join(self.entities)

                if location is not None:
                    # Imaging group case
                    if isinstance(location, list):
                        locationids = [int(x.replace('UUID', '')) for x in location]
                        for locationid in locationids:
                            if not locationid in locsid:
                                self.logger.warn("User '%s' is trying to get the content of an unauthorized entity : '%s'" % (ctx.userid, 'UUID' + location))
                                session.close()
                                return None
                        query_filter = self.__addQueryFilter(query_filter, (self.machine.c.entities_id.in_(locationids)))
                    else:
                        locationid = int(location.replace('UUID', ''))
                        if locationid in locsid:
                            query_filter = self.__addQueryFilter(query_filter, (self.machine.c.entities_id == locationid))
                        else:
                            self.logger.warn("User '%s' is trying to get the content of an unauthorized entity : '%s'" % (ctx.userid, location))
                            session.close()
                            return None

            if displayList:
                r=re.compile('reg_key_.*')
                regs=filter(r.search, self.config.summary)
                if 'os' in self.config.summary:
                    join_query = join_query.outerjoin(self.os)
                if 'type' in self.config.summary:
                    join_query = join_query.outerjoin(self.glpi_computertypes)
                if 'state' in self.config.summary:
                    join_query = join_query.outerjoin(self.state)
                if 'location' in self.config.summary:
                    join_query = join_query.outerjoin(self.locations)
                if 'model' in self.config.summary:
                    join_query = join_query.outerjoin(self.glpi_computermodels)
                if 'manufacturer' in self.config.summary:
                    join_query = join_query.outerjoin(self.manufacturers)
                if 'owner' in self.config.summary or \
                   'owner_firstname' in self.config.summary or \
                   'owner_realname' in self.config.summary:
                    join_query = join_query.outerjoin(self.user, Machine.users_id == User.id)
                try:
                    if regs[0]:
                        join_query = join_query.outerjoin(self.regcontents)
                except IndexError:
                    pass



            if self.fusionagents is not None:
                join_query = join_query.outerjoin(self.fusionagents)
            if 'antivirus' in filt: # Used for Antivirus dashboard
                join_query = join_query.outerjoin(self.fusionantivirus)
                join_query = join_query.outerjoin(self.os)

            if query_filter is None:
                query = query.select_from(join_query)
            else:
                query = query.select_from(join_query).filter(query_filter)
            query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
            if PluginManager().isEnabled("xmppmaster"):
                if ret:
                    if "Online computer" in ret:
                        if ret["Online computer"][2] == "True":
                            query = query.filter(Machine.id.in_(ret["Online computer"][3]))
                        else:
                            query = query.filter(Machine.id.notin_(ret["Online computer"][3]))
                    if "OU user" in ret:
                        query = query.filter(Machine.id.in_(ret["OU user"][3]))
                    if "OU machine" in ret:
                        query = query.filter(Machine.id.in_(ret["OU machine"][3]))
                    if "computerpresence" in ret:
                        if ret["computerpresence"][2] == "presence":
                            query = query.filter(Machine.id.in_(ret["computerpresence"][3]))
                        else:
                            query = query.filter(Machine.id.notin_(ret["computerpresence"][3]))
            query = self.__filter_on(query)
            query = self.__filter_on_entity(query, ctx)

            if filt.get('hostname'):
                if displayList:
                    clauses = []
                    # UUID filtering
                    if filt['hostname'].lower().startswith('uuid') and len(filt['hostname'])>3:
                        try:
                            clauses.append(self.machine.c.id==fromUUID(filt['hostname']))
                        except:
                            pass
                    if 'cn' in self.config.summary:
                        clauses.append(self.machine.c.name.like('%'+filt['hostname']+'%'))
                    if 'os' in self.config.summary:
                        clauses.append(self.os.c.name.like('%'+filt['hostname']+'%'))
                    if 'description' in self.config.summary:
                        clauses.append(self.machine.c.comment.like('%'+filt['hostname']+'%'))
                    if 'type' in self.config.summary:
                        clauses.append(self.glpi_computertypes.c.name.like('%'+filt['hostname']+'%'))
                    if 'owner' in self.config.summary:
                        clauses.append(self.user.c.name.like('%'+filt['hostname']+'%'))
                    if 'owner_firstname' in self.config.summary:
                        clauses.append(self.user.c.firstname.like('%'+filt['hostname']+'%'))
                    if 'owner_realname' in self.config.summary:
                        clauses.append(self.user.c.realname.like('%'+filt['hostname']+'%'))
                    if 'user' in self.config.summary:
                        clauses.append(self.machine.c.contact.like('%'+filt['hostname']+'%'))
                    if 'state' in self.config.summary:
                        clauses.append(self.state.c.name.like('%'+filt['hostname']+'%'))
                    if 'inventorynumber' in self.config.summary:
                        clauses.append(self.machine.c.otherserial.like('%'+filt['hostname']+'%'))
                    if 'entity' in self.config.summary:
                        clauses.append(self.entities.c.name.like('%'+filt['hostname']+'%'))
                    if 'location' in self.config.summary:
                        clauses.append(self.locations.c.name.like('%'+filt['hostname']+'%'))
                    if 'model' in self.config.summary:
                        clauses.append(self.glpi_computermodels.c.name.like('%'+filt['hostname']+'%'))
                    if 'manufacturer' in self.config.summary:
                        clauses.append(self.manufacturers.c.name.like('%'+filt['hostname']+'%'))
                    r=re.compile('reg_key_.*')
                    regs=filter(r.search, self.config.summary)
                    try:
                        if regs[0]:
                            clauses.append(self.regcontents.c.value.like('%'+filt['hostname']+'%'))
                    except IndexError:
                        pass
                    # Filtering on computer list page
                    if clauses:
                        query = query.filter(or_(*clauses))
                else:
                    # filtering on machines (name or uuid)
                    query = query.filter(self.machine.c.name.like('%'+filt['hostname']+'%'))
            if 'name' in filt:
                query = query.filter(self.machine.c.name.like('%'+filt['name']+'%'))

            if 'filter' in filt: # Used with search field of static group creation
                query = query.filter(self.machine.c.name.like('%'+filt['filter']+'%'))

            if 'uuid' in filt:
                query = self.filterOnUUID(query, filt['uuid'])

            if 'uuids' in filt and type(filt['uuids']) == list and len(filt['uuids']) > 0:
                query = self.filterOnUUID(query, filt['uuids'])

            if 'gid' in filt:
                gid = filt['gid']
                machines = []
                if ComputerGroupManager().isrequest_group(ctx, gid):
                    machines = map(lambda m: fromUUID(m), ComputerGroupManager().requestresult_group(ctx, gid, 0, -1, ''))
                else:
                    machines = map(lambda m: fromUUID(m), ComputerGroupManager().result_group(ctx, gid, 0, -1, ''))
                query = query.filter(self.machine.c.id.in_(machines))

            if 'request' in filt:
                request = filt['request']
                if request != 'EMPTY':
                    bool = None
                    if 'equ_bool' in filt:
                        bool = filt['equ_bool']
                    machines = map(lambda m: fromUUID(m), ComputerGroupManager().request(ctx, request, bool, 0, -1, ''))
                    query = query.filter(self.machine.c.id.in_(machines))

            if 'date' in filt:
                state = filt['date']['states']
                date_mod = filt['date']['date_mod']
                value = filt['date']['value']

                if 'green' in value:
                    query = query.filter(date_mod > state['orange'])
                if 'orange' in value:
                    query = query.filter(and_(date_mod < state['orange'], date_mod > state['red']))
                if 'red' in value:
                    query = query.filter(date_mod < state['red'])

            if 'antivirus' in filt:
                if filt['antivirus'] == 'green':
                    query = query.filter(
                        and_(
                            FusionAntivirus.is_active == 1,
                            FusionAntivirus.is_uptodate == 1,
                            OS.name.ilike('%windows%'),
                            not_(FusionAntivirus.name.in_(self.config.av_false_positive)),
                        )
                    )
                elif filt['antivirus'] == 'orange':
                    query = query.filter(
                        and_(
                            OS.name.ilike('%windows%'),
                            not_(
                                and_(
                                    FusionAntivirus.is_active == 1,
                                    FusionAntivirus.is_uptodate == 1,
                                ),
                            ),
                            not_(FusionAntivirus.name.in_(self.config.av_false_positive)),
                        )
                    )
                elif filt['antivirus'] == 'red':
                    query = query.filter(
                        and_(
                            OS.name.ilike('%windows%'),
                            or_(
                                FusionAntivirus.is_active == None,
                                FusionAntivirus.is_uptodate == None,
                                and_(
                                    FusionAntivirus.name.in_(self.config.av_false_positive),
                                    not_(FusionAntivirus.computers_id.in_(
                                        self.getMachineIdsNotInAntivirusRed(ctx),
                                    )),
                                ),
                            ),
                        )
                    )

        if count: query = query.scalar()
        return query


    def __getId(self, obj):
        if type(obj) == dict:
            return obj['uuid']
        if type(obj) != str and type(obj) != unicode:
            return obj.id
        return obj

    def __getName(self, obj):
        if type(obj) == dict:
            return obj['name']
        if type(obj) != str and type(obj) != unicode:
            return obj.name
        if type(obj) == str and re.match('UUID', obj):
            l = self.getLocation(obj)
            if l: return l.name
        return obj

    def __addQueryFilter(self, query_filter, eq):
        if str(query_filter) == str(None): # don't remove the str, sqlalchemy.sql._BinaryExpression == None return True!
            query_filter = eq
        else:
            query_filter = and_(query_filter, eq)
        return query_filter

    def computersTable(self):
        return [self.machine]

    def computersMapping(self, computers, invert = False):
        if not invert:
            return Machine.id.in_(map(lambda x:fromUUID(x), computers))
        else:
            return Machine.id.not_(ColumnOperators.in_(map(lambda x:fromUUID(x), computers)))

    def mappingTable(self, ctx, query):
        """
        Map a table name on a table mapping
        """
        base = []
        base.append(self.entities)
        if query[2] == 'OS':
            return base + [self.os]
        elif query[2] == 'Entity':
            return base
        elif query[2] == 'SOFTWARE':
            return base + [self.inst_software, self.licenses, self.software]
        elif query[2] == 'Computer name':
            return base
        elif query[2] == 'Last Logged User':
            return base
        elif query[2] == 'Owner of the machine':
            return base + [self.user]
        elif query[2] == 'Contact':
            return base
        elif query[2] == 'Contact number':
            return base
        elif query[2] == 'Description':
            return base
        elif query[2] == 'System model':
            return base + [self.model]
        elif query[2] == 'System manufacturer':
            return base + [self.manufacturers]
        elif query[2] == 'State':
            return base + [self.state]
        elif query[2] == 'System type':
            return base + [self.glpi_computertypes]
        elif query[2] == 'Inventory number':
            return base
        elif query[2] == 'Location':
            return base + [self.locations]
        elif query[2] == 'Operating system':
            return base + [self.os]
        elif query[2] == 'Service Pack':
            return base + [self.os_sp]
        elif query[2] == 'Group':
            return base + [self.group]
        elif query[2] == 'Network':
            return base + [self.net]
        elif query[2] == 'Installed software':
            return base + [self.inst_software, self.softwareversions, self.software]
        elif query[2] == 'Installed software (specific version)':
            return base + [self.inst_software, self.softwareversions, self.software]
        elif query[2] == 'Installed software (specific vendor and version)': # hidden internal dyngroup
            return base + [self.inst_software, self.softwareversions, self.software, self.manufacturers]
        elif query[2] == 'User location':
            return base + [self.user, self.locations]
        elif query[2] == 'OS Version':
            return base + [ self.os_version ]
        return []

    def mapping(self, ctx, query, invert = False):
        """
        Map a name and request parameters on a sqlalchemy request
        """
        if len(query) == 4:
            # in case the glpi database is in latin1, don't forget dyngroup is in utf8
            # => need to convert what comes from the dyngroup database
            query[3] = self.encode(query[3])
            r1 = re.compile('\*')
            like = False
            if type(query[3]) == list:
                q3 = []
                for q in query[3]:
                    if r1.search(q):
                        like = True
                        q = r1.sub('%', q)
                    q3.append(q)
                query[3] = q3
            else:
                if r1.search(query[3]):
                    like = True
                    query[3] = r1.sub('%', query[3])

            parts = self.__getPartsFromQuery(ctx, query)
            ret = []

            for part in parts:
                partA, partB = part
                partBcanBeNone = partB == '%'
                if invert:
                    if like:
                        if partBcanBeNone:
                            ret.append(not_(
                                or_(
                                    partA.like(self.encode(partB)),
                                    partA == None,
                                )
                            ))
                        else:
                            ret.append(not_(partA.like(self.encode(partB))))
                    else:
                        ret.append(not_(partA.like(self.encode(partB))))
                else:
                    if like:
                        if partBcanBeNone:
                            ret.append(
                                or_(
                                    partA.like(self.encode(partB)),
                                    partA == None,
                                )
                            )
                        else:
                            ret.append(partA.like(self.encode(partB)))
                    else:
                        try:
                            partB = partB.strip()
                            if partB.startswith(">="):
                                partB = partB[2:].strip()
                                d=int(partB)
                                ret.append( and_(partA >= d))
                            elif partB.startswith("<="):
                                partB = partB[2:].strip()
                                d=int(partB)
                                ret.append( and_(partA <= d))
                            elif partB.startswith("<"):
                                partB = partB[1:].strip()
                                d=int(partB)
                                ret.append( and_(partA < d))
                            elif partB.startswith(">"):
                                partB = partB[1:].strip()
                                d=int(partB)
                                ret.append( and_(partA > d))
                            else:
                                ret.append(partA.like(self.encode(partB)))
                        except Exception as e:
                            print str(e)
                            traceback.print_exc(file=sys.stdout)
                            ret.append(partA.like(self.encode(partB)))
            if ctx.userid != 'root':
                ret.append(self.__filter_on_entity_filter(None, ctx))
            return and_(*ret)
        else:
            return self.__treatQueryLevel(query)

    def __getPartsFromQuery(self, ctx, query):
        if query[2] in ['OS','Operating system']:
            return [[self.os.c.name, query[3]]]
        elif query[2] == 'Entity':
            locid = None
            for loc in ctx.locations:
                if self.__getName(loc) == query[3]:
                    locid = self.__getId(loc)
            if locid is not None:
                return [[self.machine.c.entities_id, locid]]
            else:
                return [[self.entities.c.name, query[3]]]
        elif query[2] == 'SOFTWARE':
            return [[self.software.c.name, query[3]]]
        elif query[2] == 'Computer name':
            return [[self.machine.c.name, query[3]]]
        elif query[2] == 'User location':
            return [[self.locations.c.completename, query[3]]]
        elif query[2] == 'Contact':
            return [[self.machine.c.contact, query[3]]]
        elif query[2] == 'Last Logged User':
            return [[self.machine.c.contact, query[3]]]
        elif query[2] == 'Owner of the machine':
            return [[self.user.c.name, query[3]]]
        elif query[2] == 'Contact number':
            return [[self.machine.c.contact_num, query[3]]]
        elif query[2] == 'Description':
            return [[self.machine.c.comment, query[3]]]
        elif query[2] == 'System model':
            return [[self.model.c.name, query[3]]]
        elif query[2] == 'System manufacturer':
            return [[self.manufacturers.c.name, query[3]]]
        elif query[2] == 'State':
            return [[self.state.c.name, query[3]]]
        elif query[2] == 'System type':
            return [[self.glpi_computertypes.c.name, query[3]]]
        elif query[2] == 'Inventory number':
            return [[self.machine.c.otherserial, query[3]]]
        elif query[2] == 'Location':
            return [[self.locations.c.completename, query[3]]]
        elif query[2] == 'Service Pack':
            return [[self.os_sp.c.name, query[3]]]
        elif query[2] == 'Group': # TODO double join on Entity
            return [[self.group.c.name, query[3]]]
        elif query[2] == 'Network':
            return [[self.net.c.name, query[3]]]
        elif query[2] == 'Installed software': # TODO double join on Entity
            return [[self.software.c.name, query[3]]]
        elif query[2] == 'Installed software (specific version)': # TODO double join on Entity
            return [[self.software.c.name, query[3][0]], [self.softwareversions.c.name, query[3][1]]]
        elif query[2] == 'Installed software (specific vendor and version)': # hidden internal dyngroup
            return [[self.manufacturers.c.name, query[3][0]], [self.software.c.name, query[3][1]], [self.softwareversions.c.name, query[3][2]]]
        elif query[2] == 'OS Version':
            return [[self.os_version.c.name, query[3]]]
        return []


    def __getTable(self, table):
        if table == 'OS':
            return self.os.c.name
        elif table == 'Entity':
            return self.entities.c.name
        elif table == 'SOFTWARE':
            return self.software.c.name
        raise Exception("dont know table for %s"%(table))

    ##################### machine list management
    def getComputer(self, ctx, filt, empty_macs=False):
        """
        Get the first computers that match filters parameters
        """
        ret = self.getRestrictedComputersList(ctx,
                                              0,
                                              10,
                                              filt,
                                              displayList=False,
                                              empty_macs=empty_macs)
        if len(ret) != 1:
            for i in ['location', 'ctxlocation']:
                try:
                    filt.pop(i)
                except:
                    pass
            ret = self.getRestrictedComputersList(ctx,
                                                  0,
                                                  10,
                                                  filt,
                                                  displayList=False,
                                                  empty_macs=empty_macs)
            if len(ret) > 0:
                raise Exception("NOPERM##%s" % (ret[0][1]['fullname']))
            return False
        return ret.values()[0]

    def getRestrictedComputersListStatesLen(self, ctx, filt, orange, red):
        """
        Return number of computers by state
        """
        session = create_session()
        now = datetime.datetime.now()
        states = {
            'orange': now - datetime.timedelta(orange),
            'red': now - datetime.timedelta(red),
        }

        date_mod = self.machine.c.date_mod
        if self.fusionagents is not None:
            date_mod = FusionAgents.last_contact

        for value in ['green', 'orange', 'red']:
            # This loop instanciate self.filt_green,
            # self.filt_orange and self.filt_red
            setattr(self, 'filt_%s' % value, filt.copy())

            newFilter = getattr(self, 'filt_%s' % value)
            values = {
                'states': states,
                'date_mod': date_mod,
                'value': value,
            }
            newFilter['date'] = values

        ret = {
            "green": int(self.__getRestrictedComputersListQuery(ctx, self.filt_green, session, count=True)),
            "orange": int(self.__getRestrictedComputersListQuery(ctx, self.filt_orange, session, count=True)),
            "red": int(self.__getRestrictedComputersListQuery(ctx, self.filt_red, session, count=True)),
        }
        session.close()
        return ret

    def getRestrictedComputersListLen(self, ctx, filt = None):
        """
        Get the size of the computer list that match filters parameters
        """
        session = create_session()

        displayList = None

        # When search field is used on main computer's list page,
        # Pagination PHP Widget must know total machine result
        # So, set displayList to True to count on glpi_computers
        # and all needed joined tables
        if 'hostname' in filt:
            if len(filt['hostname']) > 0:
                displayList = True

        ret = self.__getRestrictedComputersListQuery(ctx, filt, session, displayList, count=True)
        if ret == None:
            return 0
        session.close()
        return ret

    def getMachineforentityList(self, min = 0, max = -1, filt = None):
        """
        Get the computer list that match filters entity parameters between min and max

        FIXME: may return a list or a dict according to the parameters

        eg. dict filt param {'fk_entity': 1, 'imaging_server': 'UUID1', 'get': ['cn', 'objectUUID']}
        """
        if filt and 'imaging_server' in filt and filt['imaging_server'] != "" and \
            'get' in filt and len(filt['get']) == 2 and filt['get'][0] == 'cn' and filt['get'][1] == 'objectUUID' and\
                'fk_entity' in filt and filt['fk_entity'] != -1:
            #recherche entity parent.
            entitylist =  self.getEntitiesParentsAsList([filt['fk_entity']])
            session = create_session()
            entitylist.append(filt['fk_entity'])
            q = session.query(Machine.id, Machine.name, Machine.entities_id, Machine.locations_id).\
                add_column(self.entities.c.name.label('Entity_name')).\
                    select_from(self.machine.join(self.entities)).\
                        filter(self.machine.c.entities_id.in_(entitylist)).\
                            filter(self.machine.c.is_deleted == 0).\
                                filter(self.machine.c.is_template == 0)
            ret =  q.all()
            listentitymachine = {}
            for line in ret:
                uuid= "UUID%s"%line.id
                listentitymachine[uuid] = {"cn" : line.name, "objectUUID" : uuid }
            session.close()
            return listentitymachine

    def getRestrictedComputersList(self,
                                   ctx,
                                   min = 0,
                                   max = -1,
                                   filt = None,
                                   advanced = True,
                                   justId = False,
                                   toH = False,
                                   displayList = None,
                                   empty_macs=False):
        """
        Get the computer list that match filters parameters between min and max

        FIXME: may return a list or a dict according to the parameters

        @param displayList: if True, we are displaying Computers list main page
        @type displayList: None or bool
        """
        session = create_session()
        ret = {}

        # If we are displaying Computers list main page, set displayList to True
        if displayList is None:
            if justId or toH or 'uuid' in filt: # if 'uuid' in filt: used where adding a command to a group
                displayList = False
            else:
                displayList = True

        query = self.__getRestrictedComputersListQuery(ctx, filt, session, displayList)
        if query == None:
            return {}

        query = query.distinct()

        if self.config.ordered:
            query = query.order_by(asc(self.machine.c.name))

        if min != 0:
            query = query.offset(min)
        if max != -1:
            max = int(max) - int(min)
            query = query.limit(max)

        if justId:
            ret = map(lambda m: self.getMachineUUID(m), query.all())
        elif toH:
            ret = map(lambda m: m.toH(), query.all())
        else:
            if filt is not None and 'get' in filt:
                ret = self.__formatMachines(query.all(),
                                            advanced,
                                            filt['get'],
                                            empty_macs=empty_macs)
            else:
                ret = self.__formatMachines(query.all(),
                                            advanced,
                                            None,
                                            empty_macs=empty_macs)
        session.close()
        return ret

    def get_all_uuids_and_hostnames(self):
        """Get the uuids and hostnames for all the machines
        Returns:
            list of the machines. The list is formated as :
            [
                {'uuid':'uuid1', 'hostname':'machine1'},
                {'uuid':'uuid2', 'hostname':'machine2'}
            ]
        """
        session = create_session()
        query = session.query(Machine.id, Machine.name).all()
        session.close()
        return [{"uuid": toUUID(str(machine.id)), "hostname": machine.name} for machine in query]

    def getTotalComputerCount(self):
        session = create_session()
        query = session.query(Machine)
        query = self.__filter_on(query)
        c = query.count()
        session.close()
        return c

    def getComputerCount(self, ctx, filt = None):
        """
        Same as getRestrictedComputersListLen
        TODO : remove this one
        """
        return self.getRestrictedComputersListLen(ctx, filt)

    def getComputersList(self, ctx, filt = None):
        """
        Same as getRestrictedComputersList without limits
        """
        return self.getRestrictedComputersList(ctx, 0, -1, filt)

    ##################### UUID policies
    def getMachineUUID(self, machine):
        """
        Get this machine UUID
        """
        return toUUID(str(machine.id))

    def getMachineByUUID(self, uuid):
        """
        Get the machine that as this UUID
        """
        session = create_session()
        ret = session.query(Machine).filter(self.machine.c.id == int(str(uuid).replace("UUID", "")))
        ret = ret.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        ret = self.__filter_on(ret).first()
        session.close()
        return ret

    def filterOnUUID(self, query, uuid):
        """
        Modify the given query to filter on the machine UUID
        """
        if type(uuid) == list:
            return query.filter(self.machine.c.id.in_([int(str(a).replace("UUID", "")) for a in uuid]))
        else:
            return query.filter(self.machine.c.id == int(str(uuid).replace("UUID", "")))

    ##################### Machine output format (for ldap compatibility)
    def __getAttr(self, machine, get):
        ma = {}
        for field in get:
            if hasattr(machine, field):
                ma[field] = getattr(machine, field)
            if field == 'uuid' or field == 'objectUUID':
                ma[field] = toUUID(str(machine.id))
            if field == 'cn':
                ma[field] = machine.name
        return ma

    def __formatMachines(self, machines, advanced, get=None, empty_macs=False):
        """
        Give an LDAP like version of machines
        """
        ret = {}
        if get != None:
            for m in machines:
                if isinstance(m, tuple):
                    m = m[0]
                ret[m.getUUID()] = self.__getAttr(m, get)
            return ret

        names = {}
        for m in machines:
            displayList = False
            if isinstance(m, tuple):
                displayList = True
                # List of fields defined around line 439
                # m, os, type, inventorynumber, state, entity, location, model, manufacturer, owner = m
                l = list(m)
                if 'owner' in self.config.summary:
                    owner_login = l.pop()
                if 'owner_firstname' in self.config.summary:
                    owner_firstname = l.pop()
                if 'owner_realname' in self.config.summary:
                    owner_realname = l.pop()
                if 'manufacturer' in self.config.summary:
                    manufacturer = l.pop()
                if 'model' in self.config.summary:
                    model = l.pop()
                if 'location' in self.config.summary:
                    location = l.pop()
                if 'entity' in self.config.summary:
                    entity = l.pop()
                if 'state' in self.config.summary:
                    state = l.pop()
                if 'inventorynumber' in self.config.summary:
                    inventorynumber = l.pop()
                if 'type' in self.config.summary:
                    type = l.pop()
                if 'os' in self.config.summary:
                    oslocal = l.pop()

                m = l.pop()
            owner_login, owner_firstname, owner_realname = self.getMachineOwner(m)
            datas = {
                'cn': m.name not in ['', None] and [m.name] or ['(%s)' % m.id],
                'displayName': [m.comment],
                'objectUUID': [m.getUUID()],
                'user': [m.contact],
                'owner': [owner_login],
                'owner_realname': [owner_realname],
                'owner_firstname': [owner_firstname],
            }

            if displayList:
                if 'manufacturer' in self.config.summary:
                    datas['manufacturer'] = manufacturer
                if 'model' in self.config.summary:
                    datas['model'] = model
                if 'location' in self.config.summary:
                    datas['location'] = location
                if 'entity' in self.config.summary:
                    datas['entity'] = entity
                if 'state' in self.config.summary:
                    datas['state'] = state
                if 'inventorynumber' in self.config.summary:
                    datas['inventorynumber'] = inventorynumber
                if 'type' in self.config.summary:
                    datas['type'] = type
                if 'os' in self.config.summary:
                    datas['os'] = oslocal
                if 'owner' in self.config.summary:
                    datas['owner'] = owner_login
                if 'owner_firstname' in self.config.summary:
                    datas['owner_firstname'] = owner_firstname
                if 'owner_realname' in self.config.summary:
                    datas['owner_realname'] = owner_realname
                master_config = xmppMasterConfig()
                regvalue = []
                r=re.compile(r'reg_key_.*')
                regs=filter(r.search, self.config.summary)
                for regkey in regs:
                    regkeyconf = getattr( master_config, regkey).split("|")[0].split("\\")[-1]
                    try:
                        keyname, keyvalue = self.getMachineRegistryKey(m,regkeyconf)
                        datas[regkey] = keyvalue
                    except TypeError:
                        pass

            ret[m.getUUID()] = [None, datas]

            if advanced:
                names[m.getUUID()] = m.name
        if advanced:
            uuids = []
            for m in machines:
                if isinstance(m, tuple):
                    m = m[0]
                uuids.append(m.getUUID())

            nets = self.getMachinesNetwork(uuids)
            for uuid in ret:
                try:
                    (ret[uuid][1]['macAddress'],
                     ret[uuid][1]['ipHostNumber'],
                     ret[uuid][1]['subnetMask'],
                     ret[uuid][1]['domain'],
                     ret[uuid][1]['networkUuids']) = self.orderIpAdresses(uuid,
                                                                          names[uuid],
                                                                          nets[uuid],
                                                                          empty_macs=empty_macs)
                    if ret[uuid][1]['domain'] != '' and len(ret[uuid][1]['domain']) > 0 :
                        ret[uuid][1]['fullname'] = ret[uuid][1]['cn'][0]+'.'+ret[uuid][1]['domain'][0]
                    else:
                        ret[uuid][1]['fullname'] = ret[uuid][1]['cn'][0]
                except KeyError:
                    ret[uuid][1]['macAddress'] = []
                    ret[uuid][1]['ipHostNumber'] = []
                    ret[uuid][1]['subnetMask'] = []
                    ret[uuid][1]['domain'] = ''
                    ret[uuid][1]['fullname'] = ret[uuid][1]['cn'][0]
        return ret

    def __formatMachine(self, machine, advanced, get = None):
        """
        Give an LDAP like version of the machine
        """

        uuid = self.getMachineUUID(machine)

        if get != None:
            return self.__getAttr(machine, get)

        ret = {
            'cn': [machine.name],
            'displayName': [machine.comment],
            'objectUUID': [uuid]
        }
        if advanced:
            (ret['macAddress'], ret['ipHostNumber'], ret['subnetMask'], domain, ret['networkUuids']) = self.orderIpAdresses(uuid, machine.name, self.getMachineNetwork(uuid))
            if domain == None:
                domain = ''
            elif domain != '':
                domain = '.'+domain
            ret['fullname'] = machine.name + domain
        return [None, ret]

    ##################### entities, profiles and user rigths management
    def displayLocalisationBar(self):
        """
        This module know how to give data to localisation bar
        """
        return True

    def getMachineOwner(self, machine):
        """
        Returns the owner of computer.

        @param machine: computer's instance
        @type machine: Machine

        @return: owner (glpi_computers.user_id -> name)
        @rtype: str
        """

        ret = None, None, None
        session = create_session()
        query = session.query(User).select_from(self.user.join(self.machine))
        query = query.filter(self.machine.c.id==machine.id).first()
        if query is not None:
            ret = query.name, query.firstname, query.realname

        session.close()
        return ret



    def getUserProfile(self, user):
        """
        @return: Return the first user GLPI profile as a string, or None
        """
        session = create_session()
        qprofile = session.query(Profile).select_from(self.profile.join(self.userprofile).join(self.user)).filter(self.user.c.name == user).first()
        if qprofile == None:
            ret = None
        else:
            ret= qprofile.name
        session.close()
        return ret

    def getUserProfiles(self, user):
        """
        @return: Return all user GLPI profiles as a list of string, or None
        """
        session = create_session()
        profiles = session.query(Profile).select_from(self.profile.join(self.userprofile).join(self.user)).filter(self.user.c.name == user)
        if profiles:
            ret = []
            for profile in profiles:
                ret.append(profile.name)
        else:
            ret = None
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getAllUserProfiles(self, session):
        """
        @return: Return all GLPI profiles as a dict
        """
        result = {}
        for profile in session.query(Profile):
            result[profile.id] = profile.name
        return result

    def getUserParentLocations(self, user):
        """
        get
        return: the list of user locations'parents
        """
        pass

    def getUserLocation(self, user):
        """
        @return: Return one user GLPI entities as a list of string, or None
        TODO : check it is still used!
        """
        session = create_session()
        qentities = session.query(Entities).select_from(self.entities.join(self.userprofile).join(self.user)).filter(self.user.c.name == user).first()
        if qentities == None:
            ret = None
        else:
            ret = qentities.name
        session.close()
        return ret

    def getUserLocations(self, user):
        """
        Get the GPLI user locations.

        @return: the list of user locations
        @rtype: list
        """
        ret = []
        if user == 'root':
            ret = self.__get_all_locations()
        else:
            # check if user is linked to the root entity
            # (which is not declared explicitly in glpi...
            # we have to emulate it...)
            session = create_session()
            query = session.query(UserProfile).select_from(self.userprofile.join(self.user).join(self.profile)).filter(self.user.c.name == user).filter(self.profile.c.name.in_(self.config.activeProfiles))
            self.logger.debug("*** Query Users Profiles for Entities ***")
            self.logger.debug("Parameters :")
            self.logger.debug(" User : %s"%user)
            self.logger.debug(" Profile : %s"%self.config.activeProfiles)
            self.logger.debug("Query : ")
            self.logger.debug("%s"%query)

            entids = query.all()
            self.logger.debug("Query Result : ")
            self.logger.debug("%s"%entids)

            for entid in entids:
                if entid.entities_id == 0 and entid.is_recursive == 1:
                    self.logger.debug("Root Entity found with recursivity = return all entities")
                    session.close()
                    return self.__get_all_locations()


            # the normal case...
            query2 = session.query(Entities).add_column(self.userprofile.c.is_recursive).select_from(self.entities.join(self.userprofile).join(self.user).join(self.profile)).filter(self.user.c.name == user).filter(self.profile.c.name.in_(self.config.activeProfiles))
            self.logger.debug("*** Query Entities ***")
            self.logger.debug("Parameters :")
            self.logger.debug(" User : %s"%user)
            self.logger.debug(" Profile : %s"%self.config.activeProfiles)
            self.logger.debug("Query : ")
            self.logger.debug("%s"%query2)
            plocs = query2.all()
            self.logger.debug("Query Result : ")
            self.logger.debug("%s"%entids)
            for ploc in plocs:
                if ploc[1]:
                    # The user profile link to the entities is recursive, and so
                    # the children locations should be added too
                    self.logger.info("Recursive entity detected")
                    for l in self.__add_children(ploc[0]):
                        self.logger.debug("Add Child : %s"%l)
                        ret.append(l)
                else:
                    ret.append(ploc[0])
            if len(ret) == 0:
                ret = []
            session.close()
        self.logger.debug("Entities Found : ")
        self.logger.debug("%s"%ret)
        ret = map(lambda l: setUUID(l), ret)
        return ret

    def __get_all_locations(self):
        ret = []
        session = create_session()
        query = session.query(Entities).group_by(self.entities.c.completename).order_by(asc(self.entities.c.completename))
        self.logger.debug("*** Get All Entities ***")
        self.logger.debug("Query : ")
        self.logger.debug("%s"%query)
        q = query.all()
        session.close()
        for entities in q:
            ret.append(entities)
        self.logger.debug("Result : ")
        self.logger.debug("%s"%ret)
        return ret

    def __add_children(self, child):
        """
        Recursive function used by getUserLocations to get entities tree if needed
        """
        session = create_session()
        children = session.query(Entities).filter(self.entities.c.entities_id == child.id).all()
        ret = [child]
        for c in children:
            for res in self.__add_children(c):
                ret.append(res)
        session.close()
        return ret

    def getLocation(self, uuid):
        """
        Get a Location by it's uuid
        """
        session = create_session()
        ret = session.query(Entities).filter(self.entities.c.id == uuid.replace('UUID', '')).first()
        session.close()
        return ret

    def getLocationName(self, uuid):
        if isinstance(uuid, list):
            uuid = uuid[0]

        return self.getLocation(uuid).name

    def getLocationsList(self, ctx, filt = None):
        """
        Get the list of all entities that user can access
        """
        ret = []
        complete_ctx(ctx)
        filtr = re.compile(filt)
        for loc in ctx.locations:
            if filt:
                if filtr.search(loc.name):
                    ret.append(loc.name)
            else:
                ret.append(loc.name)

        return ret

    def getLocationsCount(self):
        """
        Returns the total count of entities
        """
        session = create_session()
        ret = session.query(Entities).count()
        session.close()
        return ret

    def getMachinesLocations(self, machine_uuids):
        session = create_session()
        q = session.query(Entities.id, Entities.name, Entities.completename, Entities.comment, Entities.level).add_column(self.machine.c.id).select_from(self.entities.join(self.machine)).filter(self.machine.c.id.in_(map(fromUUID, machine_uuids))).all()
        ret = {}
        for idp, namep,namepc,commentp,levelp,machineid in q:
            val={}
            val['uuid']=toUUID(idp)
            val['name']=namep
            val['completename']=namepc
            val['comments']=commentp
            val['level']=levelp
            ret[toUUID(machineid)] = val
        session.close()
        return ret

    def getUsersInSameLocations(self, userid, locations = None):
        """
        Returns all users name that share the same locations with the given
        user
        """
        if locations == None:
            locations = self.getUserLocations(userid)
        ret = []
        if locations:
            inloc = []
            for location in locations:
                inloc.append(location.name)
            session = create_session()
            q = session.query(User).select_from(self.user.join(self.userprofile).join(self.entities)).filter(self.entities.c.name.in_(inloc)).filter(self.user.c.name != userid).distinct().all()
            session.close()
            # Only returns the user names
            ret = map(lambda u: u.name, q)
        # Always append the given userid
        ret.append(userid)
        return ret

    def getComputerInLocation(self, location = None):
        """
        Get all computers in that location
        """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.entities)).filter(self.entities.c.name == location)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        ret = []
        for machine in query.group_by(self.machine.c.name).order_by(asc(self.machine.c.name)):
            ret[machine.name] = self.__formatMachine(machine)
        session.close()
        return ret

    def getLocationsFromPathString(self, location_path):
        """
        """
        session = create_session()
        ens = []
        for loc_path in location_path:
            loc_path = " > ".join(loc_path)
            q = session.query(Entities).filter(self.entities.c.completename == loc_path).all()
            if len(q) != 1:
                ens.append(False)
            else:
                ens.append(toUUID(str(q[0].id)))
        session.close()
        return ens

    def getLocationParentPath(self, loc_uuid):
        session = create_session()
        path = []
        en_id = fromUUID(loc_uuid)
        en = session.query(Entities).filter(self.entities.c.id == en_id).first()
        parent_id = en.entities_id
        if parent_id == -1: # parent_id is -1 for root entity
            parent_id = 0

        while parent_id != 0:
            en_id = parent_id
            en = session.query(Entities).filter(self.entities.c.id == parent_id).first()
            path.append(toUUID(en.id))
            parent_id = en.entities_id
        path.append('UUID0')
        return path

    def getMachineRegistryKey(self, machine, regkey):
        """
        Returns the registry keys and values defined on the computer.

        @param machine: computer's instance
        @type machine: Machine

        @param regkey: registry key
        @type regkey: str

        @return: name, value
        @rtype: tuple
        """

        return []

    def doesUserHaveAccessToMachines(self, ctx, a_machine_uuid, all = True):
        """
        Check if the user has correct permissions to access more than one or to all machines

        Return always true for the root user.

        @rtype: bool
        """
        if not self.displayLocalisationBar:
            return True

        session = create_session()
        # get the number of computers the user have access to
        query = session.query(Machine)
        if ctx.userid == "root":
            query = self.filterOnUUID(query, a_machine_uuid)
        else:
            a_locations = map(lambda loc:loc.name, ctx.locations)
            query = query.select_from(self.machine.join(self.entities))
            query = query.filter(self.entities.c.name.in_(a_locations))
            query = self.filterOnUUID(query, a_machine_uuid)
        ret = query.group_by(self.machine.c.id).all()
        # get the number of computers that had not been deleted
        machines_uuid_size = len(a_machine_uuid)
        all_computers = session.query(Machine)
        all_computers = self.filterOnUUID(all_computers, a_machine_uuid).all()
        all_computers = Set(map(lambda m:toUUID(str(m.id)), all_computers))
        if len(all_computers) != machines_uuid_size:
            self.logger.info("some machines have been deleted since that list was generated (%s)"%(str(Set(a_machine_uuid) - all_computers)))
            machines_uuid_size = len(all_computers)
        size = 1
        if type(ret) == list:
            size = len(ret)
        if all and size == machines_uuid_size:
            return True
        elif (not all) and machines_uuid_size == 0:
            return True
        elif (not all) and len(ret) > 0:
            return True
        ret = Set(map(lambda m:toUUID(str(m.id)), ret))
        self.logger.info("dont have permissions on %s"%(str(Set(a_machine_uuid) - ret)))
        return False

    def doesUserHaveAccessToMachine(self, ctx, machine_uuid):
        """
        Check if the user has correct permissions to access this machine

        @rtype: bool
        """
        return self.doesUserHaveAccessToMachines(ctx, [machine_uuid])

    ##################### for inventory purpose (use the same API than OCSinventory to keep the same GUI)
    def getLastMachineInventoryFull(self, uuid):
        session = create_session()
        # there is glpi_entreprise missing
        query = self.filterOnUUID(session.query(Machine) \
                .add_column(self.glpi_operatingsystems.c.name) \
                .add_column(self.glpi_operatingsystemservicepacks.c.name) \
                .add_column(self.glpi_operatingsystemversions.c.name) \
                .add_column(self.glpi_domains.c.name) \
                .add_column(self.locations.c.name) \
                .add_column(self.glpi_computermodels.c.name) \
                .add_column(self.glpi_computertypes.c.name) \
                .add_column(self.glpi_networks.c.name) \
                .add_column(self.entities.c.completename) \
                .select_from( \
                        self.machine.outerjoin(self.glpi_operatingsystems).outerjoin(self.glpi_operatingsystemservicepacks).outerjoin(self.glpi_operatingsystemversions) \
                        .outerjoin(self.glpi_computertypes).outerjoin(self.glpi_domains).outerjoin(self.locations).outerjoin(self.glpi_computermodels).outerjoin(self.glpi_networks) \
                        .join(self.entities)
                ), uuid).all()
        ret = []
        ind = {'os':1, 'os_sp':2, 'os_version':3, 'type':7, 'domain':4, 'location':5, 'model':6, 'network':8, 'entity':9} # 'entreprise':9
        for m in query:
            ma1 = m[0].to_a()
            ma2 = []
            for x,y in ma1:
                if x in ind.keys():
                    ma2.append([x,m[ind[x]]])
                else:
                    ma2.append([x,y])
            ret.append(ma2)
        if type(uuid) == list:
            return ret
        return ret[0]

    def inventoryExists(self, uuid):
        machine = self.getMachineByUUID(uuid)
        if machine:
            return True
        else:
            return False

    def getWarrantyEndDate(self, infocoms):
        """
        Get a computer's warranty end date
        @param infocoms: Content of glpi_infocoms SQL table
        @type infocoms: self.infocoms sqlalchemy object

        @return: computer's warranty end date if exists, else None
        @rtype: string or None
        """

        def add_months(sourcedate, months):
            """
            Add x months to a datetime object
            thanks to http://stackoverflow.com/questions/4130922/how-to-increment-datetime-month-in-python
            """
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month / 12
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year,month,day)

        if infocoms is not None and infocoms.warranty_date is not None:
            endDate = add_months(infocoms.warranty_date, infocoms.warranty_duration)
            if datetime.datetime.now().date() > endDate:
                return '<span style="color:red;font-weight: bold;">%s</span>' % endDate.strftime('%Y-%m-%d')
            else:
                return endDate.strftime('%Y-%m-%d')

        return ''

    def getManufacturerWarranty(self, manufacturer, serial):
        for manufacturer_key, manufacturer_infos in self.config.manufacturerWarranty.items():
            if manufacturer in manufacturer_infos['names']:
                manufacturer_info = manufacturer_infos.copy()
                manufacturer_info['url'] = manufacturer_info['url'].replace('@@SERIAL@@', serial)
                manufacturer_info['params'] = manufacturer_info['params'].replace('@@SERIAL@@', serial)
                return manufacturer_info
        return False

    def getSearchOptionId(self, filter, lang = 'en_US'):
        """
        return a list of ids corresponding to filter
        @param filter: a value to search
        @type filter: string
        """

        ids = []
        dict = self.searchOptions[lang]
        for key, value in dict.iteritems():
            if filter.lower() in value.lower():
                ids.append(key)

        return ids

    def getLinkedActionKey(self, filter, lang = 'en_US'):
        """
        return a list of ids corresponding to filter
        """
        ids = []
        dict = self.getLinkedActions()
        for key, value in dict.iteritems():
            if filter.lower() in value.lower():
                ids.append(key)

        return ids

    def countLastMachineInventoryPart(self, uuid, part, filt = None, options = {}):
        #Mutable dict options used as default argument to a method or function
        return self.getLastMachineInventoryPart(uuid, part, filt = filt, options = options, count = True)

    @property
    def _network_types(self):
        """
        Dict with GLPI available Network types
        """
        return {
            'NetworkPortLocal': 'Local',
            'NetworkPortEthernet': 'Ethernet',
            'NetworkPortWifi': 'Wifi',
            'NetworkPortDialup': 'Dialup',
            'NetworkPortAggregate': 'Aggregate',
            'NetworkPortAlias': 'Alias',
        }

    def _get_network_type(self, instantiation_type):
        """
        Return human readable glpi network type for given instantiation_type
        If not found, return instantiation_type
        """
        if instantiation_type in self._network_types:
            return self._network_types[instantiation_type]
        return instantiation_type

    def getLastMachineNetworkPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        query = self.filterOnUUID(session.query(Machine), uuid)

        ret = []
        for machine in query:
            if count:
                ret = len(machine.networkports)
            else:
                for networkport in machine.networkports:
                    # Get IP, one networkport can have multiple IPs
                    ipaddresses = []
                    gateways = []
                    netmasks = []
                    if networkport.networknames is not None:
                        ipaddresses = list(set([ip.name for ip in networkport.networknames.ipaddresses if ip.name != '']))
                        gateways = []
                        netmasks = []
                        for ip in networkport.networknames.ipaddresses:
                            gateways += [ipnetwork.gateway for ipnetwork in ip.ipnetworks if ipnetwork.gateway not in ['', '0.0.0.0']]
                            netmasks += [ipnetwork.netmask for ipnetwork in ip.ipnetworks if ipnetwork.netmask not in ['', '0.0.0.0']]
                        gateways = list(set(gateways))
                        netmasks = list(set(netmasks))
                    l = [
                        ['Name', networkport.name],
                        ['Network Type', self._get_network_type(networkport.instantiation_type)],
                        ['MAC Address', networkport.mac],
                        ['IP', ' / '.join(ipaddresses)],
                        ['Netmask', ' / '.join(netmasks)],
                        ['Gateway', ' / '.join(gateways)],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineStoragePart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function

        uuid = uuid.replace("UUID","")
        uuid = int(uuid)
        query = session.query(Disk).add_column(self.diskfs.c.name)\
        .join(self.diskfs, self.disk.c.filesystems_id == self.diskfs.c.id)\
        .filter(self.disk.c.computers_id == uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for disk, diskfs in query:
                if diskfs not in ['rootfs', 'tmpfs', 'devtmpfs']:
                    if disk is not None:
                        l = [
                            ['Name', disk.name],
                            ['Device', disk.device],
                            ['Mount Point', disk.mountpoint],
                            ['Filesystem', diskfs],
                            ['Size', disk.totalsize and str(disk.totalsize) + ' MB' or ''],
                            ['Free Size', disk.freesize and str(disk.freesize) + ' MB' or ''],
                        ]
                        ret.append(l)
        return ret

    def getLastMachineAdministrativePart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        query = self.filterOnUUID(
            session.query(Infocoms).add_column(self.suppliers.c.name).select_from(
                self.machine.outerjoin(self.infocoms).outerjoin(self.suppliers)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for infocoms, supplierName in query:
                if infocoms is not None:
                    endDate = self.getWarrantyEndDate(infocoms)
                    dateOfPurchase = ''
                    if infocoms.buy_date is not None:
                        dateOfPurchase = infocoms.buy_date.strftime('%Y-%m-%d')

                    l = [
                        ['Supplier', supplierName],
                        ['Invoice Number', infocoms.bill],
                        ['Date Of Purchase', dateOfPurchase],
                        ['Warranty End Date', endDate],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineAntivirusPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        if self.fusionantivirus is None: # glpi_plugin_fusinvinventory_antivirus doesn't exists
            return []

        query = self.filterOnUUID(
            session.query(FusionAntivirus).add_column(self.manufacturers.c.name).select_from(
                self.machine.outerjoin(self.fusionantivirus).outerjoin(self.manufacturers)
            ), uuid)

        def __getAntivirusName(manufacturerName, antivirusName):
            """
            Return complete antivirus name (manufacturer + antivirus name)
            if antivirus name is a false positive, display it in bracket
            """
            if antivirusName in self.config.av_false_positive:
                antivirusName += '@@FALSE_POSITIVE@@'

            return manufacturerName and ' '.join([manufacturerName, antivirusName]) or antivirusName

        if count:
            ret = query.count()
        else:
            ret = []
            for antivirus, manufacturerName in query:
                if antivirus:
                    l = [
                        ['Name', __getAntivirusName(manufacturerName, antivirus.name)],
                        ['Enabled', antivirus.is_active == 1 and 'Yes' or 'No'],
                        ['Up-to-date', antivirus.is_uptodate == 1 and 'Yes' or 'No'],
                    ]
                    if antivirus.antivirus_version:
                        l.insert(1, ['Version', antivirus.antivirus_version])
                    ret.append(l)
        return ret

    def getLastMachineRegistryPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        return []

    def getLastMachineSoftwaresPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        hide_win_updates = False
        if 'hide_win_updates' in options:
            hide_win_updates = options['hide_win_updates']

        query = self.filterOnUUID(
            session.query(Software).add_column(self.manufacturers.c.name) \
            .add_column(self.softwareversions.c.name).select_from(
                self.machine.outerjoin(self.inst_software) \
                .outerjoin(self.softwareversions) \
                .outerjoin(self.software) \
                .outerjoin(self.manufacturers)
            ), uuid)
        query = query.order_by(self.software.c.name)

        if filt:
            clauses = []
            clauses.append(self.manufacturers.c.name.like('%'+filt+'%'))
            clauses.append(self.softwareversions.c.name.like('%'+filt+'%'))
            clauses.append(self.software.c.name.like('%'+filt+'%'))
            query = query.filter(or_(*clauses))

        if hide_win_updates:
            query = query.filter(
                not_(
                    and_(
                        self.manufacturers.c.name.contains('microsoft'),
                        self.software.c.name.op('regexp')('KB[0-9]+(-v[0-9]+)?(v[0-9]+)?')
                    )
                )
            )

        if min != 0:
            query = query.offset(min)
        if max != -1:
            max = int(max) - int(min)
            query = query.limit(max)

        if count:
            ret = query.count()
        else:
            ret = []
            for software, manufacturer, version in query:
                if software is not None:
                    l = [
                        ['Vendor', manufacturer],
                        ['Name', software.name],
                        ['Version', version],
                    ]
                    ret.append(l)
        return ret

    def __getTableAndFieldFromName(self, name):
        """
        return table class and field name for a given name
        used for editable fields

        @param name: a given name
        @type name: string

        @return: table class and field name
        @rtype: tuple
        """

        # Reminder:
        #   If you add some other classes, check
        #   if __tablename__ exists for these classes

        values = {
            'computer_name': (Machine, 'name'),
            'description': (Machine, 'comment'),
            'inventory_number': (Machine, 'otherserial'),
        }

        return values[name]

    def setGlpiEditableValue(self, uuid, name, value):
        """
        Set a new value for a Glpi field

        @param uuid: machine uuid
        @type uuid: string

        @param name: Glpi field who will be updated
        @param name: string

        @param value: The new value
        @param value: string
        """

        self.logger.debug("Update an editable field")
        self.logger.debug("%s: Set %s as new value for %s" % (uuid, value, name))
        try:
            session = create_session()

            # Get SQL field who will be updated
            table, field = self.__getTableAndFieldFromName(name)
            session.query(table).filter_by(id=fromUUID(uuid)).update({field: value})

            # Set updated field as a locked field so it won't be updated
            # at next inventory
            query = session.query(FusionLocks).filter(self.fusionlocks.c.items_id == fromUUID(uuid))
            flocks = query.first()
            if flocks is not None:
                # Update glpi_plugin_fusioninventory_locks tablefields table
                flocksFields = eval(flocks.tablefields)
                if field not in flocksFields:
                    flocksFields.append(field)
                    query.update({'tablefields': str(flocksFields).replace("'", '"')})
            else:
                # Create new glpi_plugin_fusioninventory_locks entry
                session.execute(
                    self.fusionlocks.insert().values({
                        'tablename': table.__tablename__,
                        'items_id': fromUUID(uuid),
                        'tablefields': str([field]).replace("'", '"'),
                    })
                )

            session.close()
            return True
        except Exception, e:
            self.logger.error(e)
            return False

    def getLastMachineSummaryPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        query = self.filterOnUUID(
            session.query(Machine).add_entity(Infocoms) \
            .add_column(self.entities.c.name) \
            .add_column(self.locations.c.name) \
            .add_column(self.os.c.name) \
            .add_column(self.manufacturers.c.name) \
            .add_column(self.glpi_computertypes.c.name) \
            .add_column(self.glpi_computermodels.c.name) \
            .add_column(self.glpi_operatingsystemservicepacks.c.name) \
            .add_column(self.glpi_operatingsystemversions.c.name) \
            .add_column(self.glpi_domains.c.name) \
            .add_column(self.state.c.name) \
            #.add_column(self.fusionagents.c.last_contact) \
            .select_from(
                self.machine.outerjoin(self.entities) \
                .outerjoin(self.locations) \
                .outerjoin(self.os) \
                .outerjoin(self.manufacturers) \
                .outerjoin(self.infocoms) \
                .outerjoin(self.glpi_computertypes) \
                .outerjoin(self.glpi_computermodels) \
                .outerjoin(self.glpi_operatingsystemservicepacks) \
                .outerjoin(self.glpi_operatingsystemversions) \
                .outerjoin(self.state) \
                .outerjoin(self.glpi_domains)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for machine, infocoms, entity, location, oslocal, manufacturer, type, model, servicepack, version, domain, state in query:
                endDate = ''
                if infocoms is not None:
                    endDate = self.getWarrantyEndDate(infocoms)

                modelType = []
                if model is not None:
                    modelType.append(model)
                if type is not None:
                    modelType.append(type)

                if len(modelType) == 0:
                    modelType = ''
                elif len(modelType) == 1:
                    modelType = modelType[0]
                elif len(modelType) == 2:
                    modelType = " / ".join(modelType)

                manufacturerWarranty = False
                if machine.serial is not None and len(machine.serial) > 0:
                    manufacturerWarranty = self.getManufacturerWarranty(manufacturer, machine.serial)

                if manufacturerWarranty:
                    if manufacturerWarranty['type'] == 'get':
                        url = manufacturerWarranty['url'] + '?' + manufacturerWarranty['params']
                        serialNumber = '%s / <a href="%s" target="_blank">@@WARRANTY_LINK_TEXT@@</a>' % (machine.serial, url)
                    else:
                        url = manufacturerWarranty['url']
                        serialNumber = '%s / <form action="%s" method="post" target="_blank" id="warrantyCheck" style="display: inline">' % (machine.serial, url)
                        for param in manufacturerWarranty['params'].split('&'):
                            name, value = param.split('=')
                            serialNumber += '<input type="hidden" name="%s" value="%s" />' % (name, value)
                        serialNumber += '<a href="#" onclick="jQuery(\'#warrantyCheck\').submit(); return false;">@@WARRANTY_LINK_TEXT@@</a></form>'
                else:
                    serialNumber = machine.serial

                entityValue = ''
                if entity:
                    entityValue += entity
                if location:
                    entityValue += ' (%s)' % location

                owner_login, owner_firstname, owner_realname = self.getMachineOwner(machine)

                # Last inventory date
                date_mod = machine.date_mod

                l = [
                    ['Computer Name', ['computer_name', 'text', machine.name]],
                    ['Description', ['description', 'text', machine.comment]],
                    ['Entity (Location)', '%s' % entityValue],
                    ['Domain', domain],
                    ['Last Logged User', machine.contact],
                    ['Owner', owner_login],
                    ['Owner Firstname', owner_firstname],
                    ['Owner Realname', owner_realname],
                    ['OS', oslocal],
                    ['Service Pack', servicepack],
                    ['Version', version],
                    ['Model / Type', modelType],
                    ['Manufacturer', manufacturer],
                    ['Serial Number', serialNumber],
                    ['Inventory Number', ['inventory_number', 'text', machine.otherserial]],
                    ['State', state],
                    ['Warranty End Date', endDate],
                    ['Last Inventory Date', date_mod.strftime("%Y-%m-%d %H:%M:%S")],
                    ]
                ret.append(l)
        return ret

    def getLastMachineProcessorsPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        query = self.filterOnUUID(
            session.query(ComputerProcessor).add_column(self.processor.c.designation) \
            .select_from(
                self.machine.outerjoin(self.computerProcessor) \
                .outerjoin(self.processor)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for processor, designation in query:
                if processor is not None:
                    l = [
                        ['Name', designation],
                        ['Frequency', processor.frequency and str(processor.frequency) + ' MHz' or ''],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineMemoryPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        query = self.filterOnUUID(
            session.query(ComputerMemory) \
            .add_column(self.memoryType.c.name) \
            .add_column(self.memory.c.frequence) \
            .add_column(self.memory.c.designation).select_from(
                self.machine.outerjoin(self.computerMemory) \
                .outerjoin(self.memory) \
                .outerjoin(self.memoryType)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for memory, type, frequence, designation in query:
                if memory is not None:
                    l = [
                        ['Name', designation],
                        ['Type', type],
                        ['Frequency', frequence],
                        ['Size', memory.size and str(memory.size) + ' MB' or ''],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineHarddrivesPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass['computers_deviceharddrives']) \
            .add_column(self.deviceharddrives.c.designation) \
            .select_from(
                self.machine.outerjoin(self.computers_deviceharddrives) \
                .outerjoin(self.deviceharddrives)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for hd, designation in query:
                if hd is not None:
                    l = [
                        ['Name', designation],
                        ['Size', hd.capacity and str(hd.capacity) + ' MB' or ''],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineNetworkCardsPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass['computers_devicenetworkcards']) \
            .add_entity(self.klass['devicenetworkcards']) \
            .select_from(
                self.machine.outerjoin(self.computers_devicenetworkcards) \
                .outerjoin(self.devicenetworkcards)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for mac, network in query:
                if network is not None:
                    l = [
                        ['Name', network.designation],
                        ['Bandwidth', network.bandwidth],
                        ['MAC Address', mac.mac],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineDrivesPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass['devicedrives']).select_from(
                self.machine.outerjoin(self.computers_devicedrives) \
                .outerjoin(self.devicedrives)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for drive in query:
                if drive is not None:
                    l = [
                        ['Name', drive.designation],
                        ['Writer', drive.is_writer and 'Yes' or 'No'],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineGraphicCardsPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass['devicegraphiccards']).add_column(self.interfaceType.c.name) \
            .select_from(
                self.machine.outerjoin(self.computers_devicegraphiccards) \
                .outerjoin(self.devicegraphiccards) \
                .outerjoin(self.interfaceType, self.interfaceType.c.id == self.devicegraphiccards.c.interfacetypes_id)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for card, interfaceType in query:
                if card is not None:
                    l = [
                        ['Name', card.designation],
                        ['Memory', card.memory_default and str(card.memory_default) + ' MB' or ''],
                        ['Type', interfaceType],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineSoundCardsPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass['devicesoundcards']).select_from(
                self.machine.outerjoin(self.computers_devicesoundcards) \
                .outerjoin(self.devicesoundcards)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for sound in query:
                if sound is not None:
                    l = [
                        ['Name', sound.designation],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineControllersPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass['computers_devicecontrols']) \
            .add_entity(self.klass['devicecontrols']).select_from(
                self.machine.outerjoin(self.computers_devicecontrols) \
                .outerjoin(self.devicecontrols)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for computerControls, deviceControls in query:
                if computerControls is not None:
                    l = [
                        ['Name', deviceControls.designation],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineOthersPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = None, count = False):
        #Mutable dict options used as default argument to a method or function
        options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass['devicepcis']).select_from(
                self.machine.outerjoin(self.computers_devicepcis) \
                .outerjoin(self.devicepcis)
            ), uuid)

        if count:
            ret = query.count()
        else:
            ret = []
            for pci in query:
                if pci is not None:
                    l = [
                        ['Name', pci.designation],
                        ['Comment', pci.comment],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineHistoryPart(self, session, uuid, part, min = 0, max = -1, filt = None, options = {}, count = False):
        #Mutable dict options used as default argument to a method or function
        #options = options or {}
        # Set options
        history_delta = 'All'
        if 'history_delta' in options:
            history_delta = options['history_delta']

        query = session.query(Logs)
        query = query.filter(and_(
            self.logs.c.items_id == int(uuid.replace('UUID', '')),
            self.logs.c.itemtype == "Computer"
        ))

        now = datetime.datetime.now()
        if history_delta == 'today':
            query = query.filter(self.logs.c.date_mod > now - datetime.timedelta(1))
        elif history_delta == 'week':
            query = query.filter(self.logs.c.date_mod > now - datetime.timedelta(7))
        if history_delta == 'month':
            query = query.filter(self.logs.c.date_mod > now - datetime.timedelta(30))

        if filt:
            clauses = []
            clauses.append(self.logs.c.date_mod.like('%'+filt+'%'))
            clauses.append(self.logs.c.user_name.like('%'+filt+'%'))
            clauses.append(self.logs.c.old_value.like('%'+filt+'%'))
            clauses.append(self.logs.c.new_value.like('%'+filt+'%'))
            clauses.append(self.logs.c.id_search_option.in_(self.getSearchOptionId(filt)))
            clauses.append(self.logs.c.itemtype_link.in_(self.getLinkedActionKey(filt)))
            # Treat Software case
            if filt.lower() in 'software':
                clauses.append(self.logs.c.linked_action.in_([4, 5]))
            query = query.filter(or_(*clauses))

        if count:
            ret = query.count()
        else:
            query = query.order_by(desc(self.logs.c.date_mod))

            if min != 0:
                query = query.offset(min)
            if max != -1:
                max = int(max) - int(min)
                query = query.limit(max)

            ret = []
            for log in query:
                if log is not None:
                    update = ''
                    if log.old_value == '' and log.new_value != '':
                        update = '%s' % log.new_value
                    elif log.old_value != '' and log.new_value == '':
                        update = '%s' % log.old_value
                    else:
                        update = '%s --> %s' % (log.old_value, log.new_value)

                    update = '%s%s' % (self.getLinkedActionValues(log)['update'], update)

                    l = [
                        ['Date', log.date_mod.strftime('%Y-%m-%d %H:%m')],
                        ['User', log.user_name],
                        ['Category', self.getLinkedActionValues(log)['field']],
                        ['Action', update],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineInventoryPart(self, uuid, part, minbound = 0, maxbound = -1, filt = None, options = None, count = False):
        #Mutable dict options used as default argument to a method or function
        options = options or {}
        session = create_session()

        ret = None
        if hasattr(self, 'getLastMachine%sPart' % part):
            ret = getattr(self, 'getLastMachine%sPart' % part)(session, uuid, part, minbound, maxbound, filt, options, count)

        session.close()
        return ret

    def getSearchOptionValue(self, log):
        try:
            return self.searchOptions['en_US'][str(log.id_search_option)]
        except:
            if log.id_search_option != 0:
                logging.getLogger().warn('I can\'t get a search option for id %s' % log.id_search_option)
            return ''

    def getLinkedActionValues(self, log):
        d = {
            0: {
                'update': '',
                'field': self.getSearchOptionValue(log),
            },
            1: {
                'update': 'Add a component: ',
                'field': self.getLinkedActionField(log.itemtype_link),
            },
            2: {
                'update': 'Update a component: ',
                'field': self.getLinkedActionField(log.itemtype_link),
            },
            3: {
                'update': 'Deletion of a component: ',
                'field': self.getLinkedActionField(log.itemtype_link),
            },
            4: {
                'update': 'Install software: ',
                'field': 'Software',
            },
            5: {
                'update': 'Uninstall software: ',
                'field': 'Software',
            },
            6: {
                'update': 'Disconnect device: ',
                'field': log.itemtype_link,
            },
            7: {
                'update': 'Connect device: ',
                'field': log.itemtype_link,
            },
            8: {
                'update': 'OCS Import: ',
                'field': '',
            },
            9: {
                'update': 'OCS Delete: ',
                'field': '',
            },
            10: {
                'update': 'OCS ID Changed: ',
                'field': '',
            },
            11: {
                'update': 'OCS Link: ',
                'field': '',
            },
            12: {
                'update': 'Other (often from plugin): ',
                'field': '',
            },
            13: {
                'update': 'Delete item (put in trash): ',
                'field': '',
            },
            14: {
                'update': 'Restore item from trash: ',
                'field': '',
            },
            15: {
                'update': 'Add relation: ',
                'field': log.itemtype_link,
            },
            16: {
                'update': 'Delete relation: ',
                'field': log.itemtype_link,
            },
            17: {
                'update': 'Add an item: ',
                'field': self.getLinkedActionField(log.itemtype_link),
            },
            18: {
                'update': 'Update an item: ',
                'field': self.getLinkedActionField(log.itemtype_link),
            },
            19: {
                'update': 'Deletion of an item: ',
                'field': self.getLinkedActionField(log.itemtype_link),
            },
        }

        if log.linked_action in d:
            return d[log.linked_action]
        else:
            return {
                'update': '',
                'field': '',
            }

    def getLinkedActions(self):
        return {
            'DeviceDrive': 'Drive',
            'DeviceGraphicCard': 'Graphic Card',
            'DeviceHardDrive': 'Hard Drive',
            'DeviceMemory': 'Memory',
            'DeviceNetworkCard': 'Network Card',
            'DevicePci': 'Other Component',
            'DeviceProcessor': 'Processor',
            'DeviceSoundCard': 'Sound Card',
            'ComputerDisk': 'Volume',
            'NetworkPort': 'Network Port',
        }

    def getLinkedActionField(self, itemtype):
        """
        return Field content
        """
        field = self.getLinkedActions()
        try:
            return field[itemtype]
        except:
            return itemtype

    def getUnknownPXEOSId(self, unknownOsString):
        """
        Return id of Unknown OS depending given string

        @param unknownOsString: unknown OS string
        @type: str

        @return: id of Unknown OS string
        @rtype: int
        """
        ret = None
        session = create_session()
        query = session.query(OS).filter(self.os.c.name == unknownOsString)
        result = query.first()
        if result is not None:
            ret = result.id
        session.close()
        return ret

    def hasKnownOS(self, uuid):
        """
        Return True if machine has a known Operating System
        Used to know if a PXE inventory will be sent or not
         * If no known OS: send inventory
         * if known OS: don't send inventory

        @param uuid: UUID of machine
        @type uuid: str

        @return: True or False if machine has a known OS
        @rtype: boolean
        """
        session = create_session()
        # In GLPI, unknown OS id is 0
        # PXE Inventory create a new one with name: "Unknown operating system (PXE network boot inventory)"
        unknown_os_ids = [0]
        unknown_os_pxe_id = self.getUnknownPXEOSId("Unknown operating system (PXE network boot inventory)")
        if unknown_os_pxe_id:
            unknown_os_ids.append(unknown_os_pxe_id)

        query = self.filterOnUUID(session.query(Machine).filter(not_(self.machine.c.operatingsystems_id.in_(unknown_os_ids))), uuid)
        session.close()

        return query.first() and True or False

    ##################### functions used by querymanager
    def getAllOs(self, ctx, filt = ''):
        """
        @return: all os defined in the GLPI database
        """
        session = create_session()
        query = session.query(OS).select_from(self.os.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.os.c.name.like('%'+filt+'%'))
        ret = query.all()
        session.close()
        return ret
    def getMachineByOs(self, ctx, osname):
        """
        @return: all machines that have this os
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.os)).filter(self.os.c.name == osname)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getMachineByOsLike(self, session, ctx, osnames, count = 0):
        """
        @return: all machines that have this os using LIKE
        """
        if isinstance(osnames, basestring):
            osnames = [osnames]

        if int(count) == 1:
            query = session.query(func.count(Machine.id)).select_from(self.machine.outerjoin(self.os))
        else:
            query = session.query(Machine).select_from(self.machine.outerjoin(self.os))

        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)

        if osnames == ["other"]:
            query = query.filter(
                or_(
            and_(
                not_(OS.name.like('%Windows%')), not_(OS.name.like('%Mageia%')), not_(OS.name.like('%macOS%')),
                ), Machine.operatingsystems_id == 0,
            ))
        elif osnames == ["otherw"]:
            query = query.filter(and_(not_(OS.name.like('%Windows%10%')), not_(OS.name.like('%Windows%8%')),\
                not_(OS.name.like('%Windows%7%')), not_(OS.name.like('%Windows%Vista%')),\
                not_(OS.name.like('%Windows%XP%')), OS.name.like('%Windows%')))
        # if osnames == ['%'], we want all machines, including machines without OS (used for reporting, per example...)
        elif osnames != ['%']:
            os_filter = [OS.name.like('%' + osname + '%') for osname in osnames]
            query = query.filter(or_(*os_filter))

        if int(count) == 1:
            return int(query.scalar())
        else:
            return [[q.id, q.name] for q in query]

    def getAllEntities(self, ctx, filt = ''):
        """
        @return: all entities defined in the GLPI database
        """
        session = create_session()
        query = session.query(Entities)
        if filter != '':
            query = query.filter(self.entities.c.name.like('%'+filt+'%'))

        # Request only entites current user can access
        if not hasattr(ctx, 'locationsid'):
            complete_ctx(ctx)
        query = query.filter(self.entities.c.id.in_(ctx.locationsid))

        query = query.order_by(self.entities.c.name)
        ret = query.all()
        session.close()
        return ret

    def getMachineByEntity(self, ctx, enname):
        """
        @return: all machines that are in this entity
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.entities)).filter(self.entities.c.name == enname)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        ret = query.all()
        session.close()
        return ret

    def getEntitiesParentsAsList(self, lids):
        my_parents_ids = []
        my_parents = self.getEntitiesParentsAsDict(lids)
        for p in my_parents:
            for i in my_parents[p]:
                if not my_parents_ids.__contains__(i):
                    my_parents_ids.append(i)
        return my_parents_ids

    def getEntitiesParentsAsDict(self, lids):
        session = create_session()
        if type(lids) != list and type(lids) != tuple:
            lids = (lids)
        query = session.query(Entities).all()
        locs = {}
        for l in query:
            locs[l.id] = l.entities_id

        def __getParent(i):
            if i in locs:
                return locs[i]
            else:
                return None
        ret = {}
        for i in lids:
            t = []
            p = __getParent(i)
            while p != None:
                t.append(p)
                p = __getParent(p)
            ret[i] = t
        return ret

    @DatabaseHelper._sessionm
    def getAllVersion4Software(self, session, ctx, softname, version = ''):
        """
        @return: all softwares defined in the GLPI database
        """
        if not hasattr(ctx, 'locationsid'):
            complete_ctx(ctx)
        query = session.query(distinct(SoftwareVersion.name)) \
                .select_from(self.softwareversions.join(self.software))

        my_parents_ids = self.getEntitiesParentsAsList(ctx.locationsid)
        query = query.filter(
            or_(
                Software.entities_id.in_(ctx.locationsid),
                and_(
                    Software.is_recursive == 1,
                    Software.entities_id.in_(my_parents_ids)
                )
            )
        )

        query = query.filter(Software.name.like('%' + softname + '%'))

        if version:
            query = query.filter(SoftwareVersion.name.like('%' + version + '%'))

        # Last softwareversion entries first
        query = query.order_by(desc(SoftwareVersion.id))

        ret = query.all()
        return ret

    @DatabaseHelper._sessionm
    def getAllSoftwares(self, session, ctx, softname='', vendor=None, limit=None):
        """
        @return: all softwares defined in the GLPI database
        """
        if not hasattr(ctx, 'locationsid'):
            complete_ctx(ctx)

        query = session.query(distinct(Software.name))
        query = query.select_from(
            self.software \
            .join(self.softwareversions) \
            .join(self.inst_software) \
            .join(self.manufacturers, isouter=True)
        )
        my_parents_ids = self.getEntitiesParentsAsList(ctx.locationsid)
        query = query.filter(
            or_(
                Software.entities_id.in_(ctx.locationsid),
                and_(
                    Software.is_recursive == 1,
                    Software.entities_id.in_(my_parents_ids)
                )
            )
        )
        if vendor is not None:
            query = query.filter(Manufacturers.name.like(vendor))

        if softname != '':
            query = query.filter(Software.name.like('%' + softname + '%'))

        # Last software entries first
        query = query.order_by(desc(Software.id))

        if limit is None:
            ret = query.all()
        else:
            ret = query.limit(limit).all()
        return ret

    @DatabaseHelper._sessionm
    def getAllSoftwaresByManufacturer(self, session, ctx, vendor):
        """
        Return all softwares of a vendor
        """
        if not hasattr(ctx, 'locationsid'):
            complete_ctx(ctx)
        query = session.query(Software)
        query = query.join(Manufacturers)
        query = query.filter(Manufacturers.name.like(vendor))
        ret = query.group_by(Software.name).order_by(Software.name).all()
        return ret

    @DatabaseHelper._sessionm
    def getMachineBySoftware(self,
                             session,
                             ctx,
                             name,
                             vendor=None,
                             version=None,
                             count=0):
        """
        @return: all machines that have this software
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
            query = session.query(func.count(distinct(self.machine.c.id)))
        else:
            query = session.query(distinct(self.machine.c.id))

        query = query.select_from(self.machine
                                  .join(self.inst_software)
                                  .join(self.softwareversions)
                                  .join(self.software)
                                  .outerjoin(self.manufacturers))
        query = query.filter(Machine.is_deleted == 0)
        query = query.filter(Machine.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)

        name_filter = [Software.name.like(n) for n in name]
        query = query.filter(or_(*name_filter))

        if version is not None:
            version_filter = [SoftwareVersion.name.like(v) for v in version]
            query = query.filter(or_(*version_filter))

        if vendor is not None:
            vendor_filter = [Manufacturers.name.like(v) for v in vendor]
            query = query.filter(or_(*vendor_filter))

        if int(count) == 1:
            ret = int(query.scalar())
        else:
            ret = query.all()
        return ret

    @DatabaseHelper._sessionm
    def getAllSoftwaresImproved(self,
                             session,
                             ctx,
                             name,
                             vendor=None,
                             version=None,
                             count=0):
        """
        if count == 1
        This method is used for reporting and license count
        it's inspired from getMachineBySoftware method, but instead of count
        number of machines who have this soft, this method count number of
        softwares

        Example: 5 firefox with different version on a single machine:
            getMachineBySoftware: return 1
            this method: return 5

        I should use getAllSoftwares method, but deadline is yesterday....
        if count = 3
        return: all machines that have this software and the entity

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
            query = session.query(func.count(self.software.c.name))
        elif int(count) == 2:
            query = session.query(self.software.c.name)
        else:
            query = session.query(self.machine.c.id.label('computers_id'), self.machine.c.name.label('computers_name'),self.machine.c.entities_id.label('entity_id'))

        if int(count) >= 3:
            query = query.select_from(self.machine
                                  .join(self.inst_software)
                                  .join(self.softwareversions)
                                  .join(self.software)
                                  .outerjoin(self.manufacturers))
        else:
            query = query.select_from(self.software
                                    .join(self.softwareversions)
                                    .join(self.inst_software)
                                    .outerjoin(self.manufacturers))

        name_filter = [Software.name.like(n) for n in name]
        query = query.filter(or_(*name_filter))

        if version is not None:
            version_filter = [SoftwareVersion.name.like(v) for v in version]
            query = query.filter(or_(*version_filter))

        if vendor is not None:
            vendor_filter = [Manufacturers.name.like(v) for v in vendor]
            query = query.filter(or_(*vendor_filter))

        if hasattr(ctx, 'locationsid'):
            query = query.filter(Software.entities_id.in_(ctx.locationsid))
        if int(count) >= 3:
            query = query.filter(Machine.is_deleted == 0)
            query = query.filter(Machine.is_template == 0)


        if int(count) == 1:
            return {'count' : int(query.scalar())}
        elif int(count) == 2:
            return query.all()
        else:
            ret = query.all()
            return [{'computer':a[0],'name':a[1],'entityid':a[2]}  for a in ret ]

    def getMachineBySoftwareAndVersion(self, ctx, swname, count=0):
        # FIXME: the way the web interface process dynamic group sub-query
        # is wrong, so for the moment we need this loop:
        version = None
        if type(swname) == list:
            while type(swname[0]) == list:
                swname = swname[0]
            name = swname[0]
            version = swname[1]
        return self.getMachineBySoftware(ctx, name, version, count=count)

    def getAllHostnames(self, ctx, filt = ''):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.machine.c.name.like('%'+filt+'%'))
        ret = query.all()
        session.close()
        return ret
    def getMachineByHostname(self, ctx, hostname):
        """
        @return: all machines that have this hostname
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.name == hostname)
        ret = query.all()
        session.close()
        return ret

    def getAllContacts(self, ctx, filt = ''):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.machine.c.contact.like('%'+filt+'%'))
        ret = query.group_by(self.machine.c.contact).all()
        session.close()
        return ret
    def getMachineByContact(self, ctx, contact):
        """
        @return: all machines that have this contact
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.contact == contact)
        ret = query.all()
        session.close()
        return ret

    def getAllContactNums(self, ctx, filt = ''):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.machine.c.contact_num.like('%'+filt+'%'))
        ret = query.group_by(self.machine.c.contact_num).all()
        session.close()
        return ret
    def getMachineByContactNum(self, ctx, contact_num):
        """
        @return: all machines that have this contact number
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.contact_num == contact_num)
        ret = query.all()
        session.close()
        return ret

    def getAllComments(self, ctx, filt = ''):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.machine.c.comment.like('%'+filt+'%'))
        ret = query.group_by(self.machine.c.comment).all()
        session.close()
        return ret
    def getMachineByComment(self, ctx, comment):
        """
        @return: all machines that have this contact number
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.comment == comment)
        ret = query.all()
        session.close()
        return ret

    def getAllModels(self, ctx, filt = ''):
        """ @return: all machine models defined in the GLPI database """
        session = create_session()
        query = session.query(Model).select_from(self.model.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.model.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.model.c.name).all()
        session.close()
        return ret

    def getAllManufacturers(self, ctx, filt = ''):
        """ @return: all machine manufacturers defined in the GLPI database """
        session = create_session()
        query = session.query(Manufacturers).select_from(self.manufacturers.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.manufacturers.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.manufacturers.c.name).all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getAllSoftwareVendors(self, session, ctx, filt='', limit=20):
        """ @return: all software vendors defined in the GPLI database"""
        query = session.query(Manufacturers).select_from(self.manufacturers
                                                         .join(self.software))
        query = query.filter(Software.is_deleted == 0)
        query = query.filter(Software.is_template == 0)
        if filt != '':
            query = query.filter(Manufacturers.name.like('%' + filt + '%'))
        query = query.group_by(Manufacturers.name)
        ret = query.order_by(asc(Manufacturers.name)).limit(limit)
        return ret

    @DatabaseHelper._sessionm
    def getAllSoftwareVersions(self, session, ctx, software=None, filt=''):
        """ @return: all software versions defined in the GPLI database"""
        query = session.query(SoftwareVersion)
        query = query.select_from(self.softwareversions
                                  .join(self.software))
        if software is not None:
            query = query.filter(Software.name.like(software))
        if filt != '':
            query = query.filter(SoftwareVersion.name.like('%' + filt + '%'))
        ret = query.group_by(SoftwareVersion.name).all()
        return ret

    def getAllStates(self, ctx, filt = ''):
        """ @return: all machine models defined in the GLPI database """
        session = create_session()
        query = session.query(State).select_from(self.state.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.state.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.state.c.name).all()
        session.close()
        return ret

    def getAllTypes(self, ctx, filt = ''):
        """ @return: all machine types defined in the GLPI database """
        session = create_session()
        query = session.query(self.klass['glpi_computertypes']).select_from(self.glpi_computertypes.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.glpi_computertypes.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.glpi_computertypes.c.name).all()
        session.close()
        return ret

    def getAllInventoryNumbers(self, ctx, filt = ''):
        """ @return: all machine inventory numbers defined in the GLPI database """
        ret = []
        return ret

    def getMachineByModel(self, ctx, filt):
        """ @return: all machines that have this model """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.model))
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.model.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllOwnerMachine(self, ctx, filt = ''):
        """ @return: all owner defined in the GLPI database """
        session = create_session()
        query = session.query(User).select_from(self.manufacturers.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.user.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.user.c.name).all()
        session.close()
        return ret


    def getAllLoggedUser(self, ctx, filt = ''):
        """
            @return: all LoggedUser defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.machine.c.contact.like('%'+filt+'%'))
        ret = query.group_by(self.machine.c.contact).all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getMachineByType(self, session, ctx, types, count=0):
        """ @return: all machines that have this type """
        if isinstance(types, basestring):
            types = [types]

        if int(count) == 1:
            query = session.query(func.count(Machine.id)).select_from(self.machine.join(self.glpi_computertypes))
        else:
            query = session.query(Machine).select_from(self.machine.join(self.glpi_computertypes))
        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)

        type_filter = [self.klass['glpi_computertypes'].name.like(type) for type in types]
        query = query.filter(or_(*type_filter))

        if int(count) == 1:
            ret = int(query.scalar())
        else:
            ret = query.all()
        return ret

    def getMachineByInventoryNumber(self, ctx, filt):
        """ @return: all machines that have this type """
        session = create_session()
        query = session.query(Machine).select_from(self.machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.otherserial == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByManufacturer(self, ctx, filt):
        """ @return: all machines that have this manufacturer """
        session = create_session()
        query = session.query(Manufacturers).select_from(self.machine.join(self.manufacturers))
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.manufacturers.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByState(self, ctx, filt, count=0):
        """ @return: all machines that have this state """
        session = create_session()
        if int(count) == 1:
            query = session.query(func.count(Machine)).select_from(self.machine.join(self.state))
        else:
            query = session.query(Machine).select_from(self.machine.join(self.state))
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if '%' in filt:
            query = query.filter(self.state.c.name.like(filt))
        else:
            query = query.filter(self.state.c.name == filt)
        if int(count) == 1:
            ret = int(query.scalar())
        else:
            ret = query.all()
        session.close()
        return ret

    def getAllLocations(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        if not hasattr(ctx, 'locationsid'):
            complete_ctx(ctx)
        session = create_session()
        query = session.query(Locations).select_from(self.locations.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        my_parents_ids = self.getEntitiesParentsAsList(ctx.locationsid)
        query = self.__filter_on_entity(query, ctx, my_parents_ids)
        query = query.filter(or_(self.locations.c.entities_id.in_(ctx.locationsid), and_(self.locations.c.is_recursive == 1, self.locations.c.entities_id.in_(my_parents_ids))))
        if filter != '':
            query = query.filter(self.locations.c.completename.like('%'+filt+'%'))
        ret = query.group_by(self.locations.c.completename).all()
        session.close()
        return ret

    def getAllLocations1(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        if not hasattr(ctx, 'locationsid'):
            complete_ctx(ctx)
        session = create_session()
        query = session.query(Locations)
        if filter != '':
            query = query.filter(self.locations.c.completename.like('%'+filt+'%'))
        ret = query.group_by(self.locations.c.completename)
        ret=ret.all()
        session.close()
        return ret

    def getAllRegistryKey(self, ctx, filt = ''):
        """
        Returns the registry keys name.
        @return: list Register key name
        """
        return []

    @DatabaseHelper._sessionm
    def getAllRegistryKeyValue(self, session, ctx, keyregister, value):
        """
        @return: all key value defined in the GLPI database
        """
        return []

    def getMachineByLocation(self, ctx, filt):
        """ @return: all machines that have this contact number """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.locations))
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.locations.c.completename == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllOsSps(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        session = create_session()
        query = session.query(OsSp).select_from(self.os_sp.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.os_sp.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.os_sp.c.name).all()
        session.close()
        return ret
    def getMachineByOsSp(self, ctx, filt):
        """ @return: all machines that have this contact number """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.os_sp))
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.os_sp.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllGroups(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        if not hasattr(ctx, 'locationsid'):
            complete_ctx(ctx)
        session = create_session()
        query = session.query(Group).select_from(self.group.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        my_parents_ids = self.getEntitiesParentsAsList(ctx.locationsid)
        query = self.__filter_on_entity(query, ctx, my_parents_ids)
        query = query.filter(or_(self.group.c.entities_id.in_(ctx.locationsid), and_(self.group.c.is_recursive == 1, self.group.c.entities_id.in_(my_parents_ids))))
        if filter != '':
            query = query.filter(self.group.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.group.c.name).all()
        session.close()
        return ret

    def getMachineByGroup(self, ctx, filt):# Entity!
        """ @return: all machines that have this contact number """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.group))
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.group.c.entities_id.in_(ctx.locationsid))
        query = query.filter(self.group.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllNetworks(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        session = create_session()
        query = session.query(Net).select_from(self.net.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.net.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.net.c.name).all()
        session.close()
        return ret
    def getMachineByNetwork(self, ctx, filt):
        """ @return: all machines that have this contact number """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.net))
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.net.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByMacAddress(self, ctx, filt):
        """ @return: all computers that have this mac address """
        session = create_session()
        query = session.query(Machine).join(NetworkPorts, and_(Machine.id == NetworkPorts.items_id, NetworkPorts.itemtype == 'Computer'))
        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)
        query = query.filter(NetworkPorts.mac == filt)
        query = self.__filter_on(query)
        if ctx != 'imaging_module':
            query = self.__filter_on_entity(query, ctx)
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getMachineByHostnameAndMacs(self, session, ctx, hostname, macs):
        """
        Get machine who match given hostname and at least one of macs

        @param ctx: context
        @type ctx: dict

        @param hostname: hostname of wanted machine
        @type hostname: str

        @param macs: list of macs
        @type macs: list

        @return: UUID of wanted machine or False
        @rtype: str or None
        """
        query = session.query(Machine).join(NetworkPorts, and_(Machine.id == NetworkPorts.items_id, NetworkPorts.itemtype == 'Computer'))
        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)
        query = query.filter(NetworkPorts.mac.in_(macs))
        query = query.filter(self.machine.c.name == hostname)
        query = self.__filter_on(query)
        if ctx != 'imaging_module':
            query = self.__filter_on_entity(query, ctx)
        try:
            ret = query.one()
        except (MultipleResultsFound, NoResultFound) as e:
            self.logger.warn('I can\'t get any UUID for machine %s and macs %s: %s' % (hostname, macs, e))
            return None
        return toUUID(ret.id)

    def getMachineByOsVersion(self, ctx, filt):
        """ @return: all machines that have this os version """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.os_version))
        query = query.filter(self.machine.c.is_deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.os_version.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getComputersOS(self, uuids):
        if isinstance(uuids, str):
            uuids = [uuids]
        session = create_session()
        query = session.query(Machine) \
                .add_column(self.os.c.name) \
                .select_from(self.machine.join(self.os))
        query = query.filter(self.machine.c.id.in_([fromUUID(uuid) for uuid in uuids]))
        session.close()
        res = []
        for machine, OSName in query:
            res.append({
                'uuid': toUUID(machine.id),
                'OSName': OSName,
            })
        return res

    def getComputersCountByOS(self, osname):
        session = create_session()
        query = session.query(func.count(Machine.id)) \
                .select_from(self.machine.join(self.os))
        query = query.filter(self.os.c.name.like('%'+osname+'%'))
        count = query.scalar()
        session.close()
        return count

    def getMachineUUIDByMacAddress(self, mac):
        """
        Return a machine's UUID by MAC address.
        @param mac: MAC address of machine
        @type mac: str

        @return: machine UUID
        @rtype: str
        """
        ret = self.getMachineByMacAddress('imaging_module', mac)
        if type(ret) == list:
            if len(ret) != 0:
                return str(toUUID(ret[0].id))
        return None


    ##################### for msc
    def getMachinesNetwork(self, uuids):
        """
        Get for each machine a list of its networkports

        return {
            computer_uuid1: {
                    'domain': 'xxx',
                    'gateway': 'xxx',
                    'ifaddr': 'xxx',
                    'ifmac': 'xxx',
                    'name': 'xxx',
                    'netmask': 'xxx',
                    'subnet': 'xxx',
                    'uuid': 'xxx', <= UUID of networkport
                },
            computer_uuid2: {},
            etc.,
            }
        """
        def getComputerNetwork(machine, domain):
            result = []
            for networkport in machine.networkports:
                if networkport.networknames is not None:
                    if networkport.networknames.ipaddresses:
                        # If there is multiple adresses per interface, we
                        # create the same number of interfaces
                        for ipaddress in networkport.networknames.ipaddresses:
                            d = {
                                'uuid': toUUID(networkport.id),
                                'domain': domain,
                                'ifmac': networkport.mac,
                                'name': networkport.name,
                                'netmask': '',
                                'subnet': '',
                                'gateway': '',
                                'ifaddr': '',
                            }

                            # IP Address
                            d['ifaddr'] = ipaddress.name

                            # Init old iface dict
                            z = {}

                            for ipnetwork in ipaddress.ipnetworks:
                                oz = z

                                z = d.copy()
                                z['netmask'] = ipnetwork.netmask
                                z['gateway'] = ipnetwork.gateway
                                z['subnet'] = ipnetwork.address

                                # Add this (network/ip/interface) to result
                                # and if its not duplicated
                                if z != oz:
                                    result.append(z)
                            if not ipaddress.ipnetworks:
                                result.append(d)
            return result

        session = create_session()
        query = self.filterOnUUID(session.query(Machine), uuids)
        ret = {}
        for machine in query:
            uuid = toUUID(machine.id)
            domain = ''
            if machine.domains is not None:
                domain = machine.domains.name
            ret[uuid] = getComputerNetwork(machine, domain)
        session.close()
        return ret

    def getMachineNetwork(self, uuid):
        """
        Get a machine network
        @see getMachinesNetwork()
        """
        return self.getMachinesNetwork(uuid)[uuid]

    def getMachinesMac(self, uuids):
        """
        Get several machines mac addresses
        """
        session = create_session()
        query = self.filterOnUUID(session.query(Machine), uuids)
        ret = {}
        for machine in query:
            cuuid = toUUID(machine.id)
            ret[cuuid] = [networkport.mac for networkport in machine.networkports]
        return ret


    def getMachineMac(self, uuid):
        """
        Get a machine mac addresses
        """
        return self.getMachinesMac(uuid)[uuid]

    def orderIpAdresses(self, uuid, hostname, netiface, empty_macs=False):
        ret_ifmac = []
        ret_ifaddr = []
        ret_netmask = []
        ret_domain = []
        ret_networkUuids = []
        idx_good = 0
        failure = [True, True]
        for iface in netiface:
            if not empty_macs :
                if not ('ifmac' in iface or iface['ifmac']):
                    continue
            if 'ifaddr' in iface and iface['ifaddr']:
                if iface['gateway'] == None:
                    ret_ifmac.append(iface['ifmac'])
                    ret_ifaddr.append(iface['ifaddr'])
                    ret_netmask.append(iface['netmask'])
                    ret_networkUuids.append(iface['uuid'])
                    if 'domain' in iface:
                        ret_domain.append(iface['domain'])
                    else:
                        ret_domain.append('')
                else:
                    if same_network(iface['ifaddr'], iface['gateway'], iface['netmask']):
                        idx_good += 1
                        ret_ifmac.insert(0, iface['ifmac'])
                        ret_ifaddr.insert(0, iface['ifaddr'])
                        ret_netmask.insert(0, iface['netmask'])
                        ret_networkUuids.insert(0, iface['uuid'])
                        if 'domain' in iface:
                            ret_domain.insert(0, iface['domain'])
                        else:
                            ret_domain.insert(0, '')
                        failure[0] = False
                    else:
                        ret_ifmac.insert(idx_good, iface['ifmac'])
                        ret_ifaddr.insert(idx_good, iface['ifaddr'])
                        ret_netmask.insert(idx_good, iface['netmask'])
                        ret_networkUuids.insert(idx_good, iface['uuid'])
                        if 'domain' in iface:
                            ret_domain.insert(idx_good, iface['domain'])
                        else:
                            ret_domain.insert(idx_good, '')
                        failure[1] = False

        return (ret_ifmac, ret_ifaddr, ret_netmask, ret_domain, ret_networkUuids)

    def dict2obj(d):
        """
        Get a dictionnary and return an object
        """
        from collections import namedtuple
        o = namedtuple('dict2obj', ' '.join(d.keys()))
        return o(**d)

    def getMachineIp(self, uuid):
        """
        Get a machine ip addresses
        """
        machine_network = self.getMachineNetwork(uuid)
        ret_gw = []
        ret_nogw = []
        for m in machine_network:
            m = self.dict2obj(m)
            if same_network(m.ifaddr, m.gateway, m.netmask):
                ret_gw.append(m.ifaddr)
            else:
                ret_nogw.append(m.ifaddr)
        ret_gw = unique(ret_gw)
        ret_gw.extend(unique(ret_nogw))

        return ret_gw

    def getMachineListByState(self, ctx, groupName):
        """
        """

        # Read config from ini file
        orange = self.config.orange
        red = self.config.red

        complete_ctx(ctx)
        filt = {'ctxlocation': ctx.locations}

        session = create_session()
        now = datetime.datetime.now()
        orange = now - datetime.timedelta(orange)
        red = now - datetime.timedelta(red)

        date_mod = self.machine.c.date_mod
        if self.fusionagents is not None:
            date_mod = FusionAgents.last_contact

        query = self.__getRestrictedComputersListQuery(ctx, filt, session)

        # Limit list according to max_elements_for_static_list param in dyngroup.ini
        limit = DGConfig().maxElementsForStaticList

        if groupName == "green":
            result = query.filter(date_mod > orange).limit(limit)
        elif groupName == "orange":
            result = query.filter(and_(date_mod < orange, date_mod > red)).limit(limit)
        elif groupName == "red":
            result = query.filter(date_mod < red).limit(limit)

        ret = {}
        for machine in result.all():
            if machine.name is not None:
                ret[toUUID(machine.id) + '##' + machine.name] = {"hostname": machine.name, "uuid": toUUID(machine.id)}

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

        # Read config from ini file
        orange = self.config.orange
        red = self.config.red

        complete_ctx(ctx)
        filt = {'ctxlocation': ctx.locations}

        ret = {
            "days": {
                "orange": orange,
                "red": red,
            },
            "count": self.getRestrictedComputersListStatesLen(ctx, filt, orange, red),
        }

        return ret

    def getAntivirusStatus(self, ctx):
        """
        Return number of machine by antivirus status:
            * green: Antivirus OK
            * orange: Antivirus not running or not up-to-date
            * red: No antivirus or unknown status
        """
        session = create_session()

        __computersListQ = self.__getRestrictedComputersListQuery

        complete_ctx(ctx)
        filt = {
            'ctxlocation': ctx.locations
        }

        ret = {
            'green': int(__computersListQ(ctx, dict(filt, **{'antivirus': 'green'}), session, count=True)),
            'orange': int(__computersListQ(ctx, dict(filt, **{'antivirus': 'orange'}), session, count=True)),
            'red': int(__computersListQ(ctx, dict(filt, **{'antivirus': 'red'}), session, count=True)),
        }

        session.close()

        return ret

    def getMachineIdsNotInAntivirusRed(self, ctx):
        """
        return ids list of machines who are not in antivirus red status
        """
        session = create_session()
        __computersListQ = self.__getRestrictedComputersListQuery

        complete_ctx(ctx)

        filt = {
            'ctxlocation': ctx.locations
        }

        query1 = __computersListQ(ctx, dict(filt, **{'antivirus': 'green'}), session)
        query2 = __computersListQ(ctx, dict(filt, **{'antivirus': 'orange'}), session)

        session.close()

        return [machine.id for machine in query1.all()] + [machine.id for machine in query2.all()]

    def getMachineListByAntivirusState(self, ctx, groupName):
        session = create_session()

        __computersListQ = self.__getRestrictedComputersListQuery

        complete_ctx(ctx)
        filt = {
            'ctxlocation': ctx.locations
        }
        query = __computersListQ(ctx, dict(filt, **{'antivirus': groupName}), session)

        # Limit list according to max_elements_for_static_list param in dyngroup.ini
        limit = DGConfig().maxElementsForStaticList

        query = query.limit(limit)

        ret = {}
        for machine in query.all():
            if machine.name is not None:
                ret[toUUID(machine.id) + '##' + machine.name] = {"hostname": machine.name, "uuid": toUUID(machine.id)}

        session.close()
        return ret

    def getIpFromMac(self, mac):
        """
        Get an ip address when a mac address is given
        """
        session = create_session()
        query = session.query(NetworkPorts).filter(NetworkPorts.mac == mac)
        # Get first IP address found
        ret = query.first().networknames.ipaddresses[0]
        session.close()
        return ret

    def getIpFromMachine(self, uuid):
        """
        Same as getMachineIp
        TODO: check where it is used
        """
        return self.getMachineIp(uuid)

    def getMachineDomain(self, uuid):
        """
        Get a machine domain name
        """
        session = create_session()
        machine = self.filterOnUUID(session.query(Machine), uuid).first()
        domain = ''
        if machine.domains is not None:
            domain = machine.domains.name
        return domain

    def isComputerNameAvailable(self, ctx, locationUUID, name):
        raise Exception("need to be implemented when we would be able to add computers")

    def _killsession(self,sessionwebservice):
        """
        Destroy a session identified by a session token.

        @param sessionwebservice: session var provided by initSession endpoint.
        @type sessionwebservice: str

        """
        headers = {'content-type': 'application/json',
                   'Session-Token': sessionwebservice
                   }
        url = GlpiConfig.webservices['glpi_base_url'] + "killSession"
        r = requests.get(url, headers=headers)
        if r.status_code == 200 :
            self.logger.debug("Kill session REST: %s"%sessionwebservice)

    def delMachine(self, uuid):
        """
        Deleting a machine in GLPI (only the flag 'is_deleted' updated)

        @param uuid: UUID of machine
        @type uuid: str

        @return: True if the machine successfully deleted
        @rtype: bool
        """
        session = create_session()
        id = fromUUID(uuid)

        machine = session.query(Machine).filter(self.machine.c.id == id).first()

        if machine:
            webservice_ok = True
            try:
                self._get_webservices_client()
            except ProtocolError, e:
                webservice_ok = False
            except Exception, e:
                webservice_ok = False

            if self.config.webservices['purge_machine']:
                if webservice_ok:
                    return self.purgeMachine(machine.id)
                else:
                    self.logger.warn("Unable to purge machine (uuid=%s) because GLPI webservice is disabled" % uuid)

            connection = self.getDbConnection()
            trans = connection.begin()
            try:
                machine.is_deleted = True
            except Exception, e :
                self.logger.warn("Unable to delete machine (uuid=%s): %s" % (uuid, str(e)))
                session.flush()
                session.close()
                trans.rollback()

                return False

            session.flush()
            session.close()
            trans.commit()
            self.logger.debug("Machine (uuid=%s) successfully deleted" % uuid)

            return True

        else:
            return False

    @DatabaseHelper._sessionm
    def addUser(self, session, username, password, entity_rights=None):
        # Check if the user exits or not
        try:
            user = session.query(User).filter_by(name=username).one()
        except NoResultFound:
            user = User()
            user.name = username
        user.password = hashlib.sha1(password).hexdigest()
        user.firstname = ''
        user.realname = ''
        user.auths_id = 0
        user.is_deleted = 0
        user.is_active = 1
        user.locations_id = ''
        session.add(user)
        session.commit()
        session.flush()

        # Setting entity rights
        if entity_rights is not None:
            self.setLocationsForUser(username, entity_rights)
        return True

    @DatabaseHelper._sessionm
    def setUserPassword(self, session, username, password):
        try:
            user = session.query(User).filter_by(name=username).one()
        except NoResultFound:
            self.addUser(username, password)
            return
        user.password = hashlib.sha1(password).hexdigest()
        session.commit()
        session.flush()

    def removeUser(self, session, username):
        # Too complicated, affects many tables
        return True

    @DatabaseHelper._sessionm
    def addEntity(self, session, entity_name, parent_id, comment):
        entity = Entities()
        entity.id = session.query(func.max(Entities.id)).scalar() + 1
        entity.entities_id = parent_id #parent
        entity.name = entity_name
        entity.comment = comment
        # Get parent entity object
        parent_entity = session.query(Entities).filter_by(id=parent_id,).one()
        completename = parent_entity.completename + ' > ' + entity_name
        entity.completename = completename
        entity.level = parent_entity.level + 1
        session.add(entity)
        session.commit()
        session.flush()
        return True

    @DatabaseHelper._sessionm
    def editEntity(self, session, id, entity_name, parent_id, comment):
        entity = session.query(Entities).filter_by(id=id).one()
        entity.entities_id = parent_id #parent
        entity.name = entity_name
        entity.comment = comment
        #entity.level = parent_id
        entity = self.updateEntityCompleteName(entity)
        session.commit()
        session.flush()
        return True

    @DatabaseHelper._sessionm
    def updateEntityCompleteName(self, session, entity):
        # Get parent entity object
        parent_entity = session.query(Entities).filter_by(id=entity.entities_id).one()
        completename = parent_entity.completename + ' > ' + entity.name
        entity.completename = completename
        entity.level = parent_entity.level + 1
        # Update all children complete names
        children = session.query(Entities).filter_by(entities_id=entity.id).all()
        for item in children:
            self.updateEntityCompleteName(item)
        return entity

    def removeEntity(self, entity_id):
        # Too complicated, affects many tables
        pass

    @DatabaseHelper._listinfo
    @DatabaseHelper._sessionm
    def getAllEntitiesPowered(self, session, params):
        return session.query(Entities).order_by(Entities.completename)

    @DatabaseHelper._sessionm
    def addLocation(self, session, name, parent_id, comment):
        location = Locations()
        location.entities_id = 0 #entity is root
        location.name = name
        location.locations_id = parent_id

        location.comment = comment
        location.level = parent_id
        location.building = ''
        location.room = ''

        # Get parent location object
        parent_location = session.query(Locations).filter_by(id=parent_id,).one()
        completename = parent_location.completename + ' > ' + name
        location.completename = completename

        session.add(location)
        session.commit()
        session.flush()
        return True

    @DatabaseHelper._sessionm
    def editLocation(self, session, id, name, parent_id, comment):
        location = session.query(Locations).filter_by(id=id).one()
        location.locations_id = parent_id #parent
        location.name = name
        location.comment = comment
        location.level = parent_id

        location = self.updateLocationCompleteName(location)

        session.commit()
        session.flush()
        return True

    @DatabaseHelper._sessionm
    def updateLocationCompleteName(self, session, location):
        # Get parent location object
        parent_location = session.query(Locations).filter_by(id=location.locations_id).one()
        completename = parent_location.completename + ' > ' + location.name
        location.completename = completename

        # Update all children complete names
        children = session.query(Locations).filter_by(locations_id=location.id).all()

        for item in children:
            self.updateLocationCompleteName(item)

        return location

    @DatabaseHelper._listinfo
    @DatabaseHelper._sessionm
    def getAllLocationsPowered(self, session, params):
        return session.query(Locations).order_by(Locations.completename)

    @DatabaseHelper._listinfo
    @DatabaseHelper._sessionm
    def getAllEntityRules(self, session, params):
        # TODO: Filter this by user context entities
        return session.query(self.rules).filter_by(sub_type='PluginFusioninventoryInventoryRuleEntity')\
                                        .filter(self.rules.c.name != 'Root')\
                                        .order_by(self.rules.c.ranking)

    @DatabaseHelper._sessionm
    def addEntityRule(self, session, rule_data):
        rule = Rule()
        # root entity (this means that rule is appliable on root entity and all subentities)
        rule.entities_id = 0
        rule.sub_type = 'PluginFusioninventoryInventoryRuleEntity'
        # Get the last ranking for this class +1
        rank = session.query(func.max(self.rules.c.ranking))\
            .filter(self.rules.c.sub_type=='PluginFusioninventoryInventoryRuleEntity')\
            .filter(self.rules.c.name != 'Root')\
            .scalar()
        if rank is None:
            rank = 0
            rule.ranking = rank + 1
            rule.name = rule_data['name']
            rule.description = rule_data['description']
            rule.match = rule_data['aggregator']
            if rule_data['active'] == 'on':
                rule.is_active = 1
            else:
                rule.is_active = 0

        session.add(rule)
        session.commit()
        session.flush()

        # Make sure "Root" entity rule ranking is very high
        session.query(Rule).filter_by(sub_type='PluginFusioninventoryInventoryRuleEntity',\
            name='Root').update({'ranking': rule.ranking+1}, synchronize_session=False)

        # Adding rule criteria

        for i in xrange(len(rule_data['criteria'])):

            cr = RuleCriterion()
            cr.rules_id = rule.id
            cr.criteria = rule_data['criteria'][i]
            cr.condition = rule_data['operators'][i]
            cr.pattern = rule_data['patterns'][i]
            session.add(cr)
            session.commit()
            session.flush()

            # Adding rule actions

        # If a target entity is specified, add it
        if rule_data['target_entity'] != '-1':
            action = RuleAction()
            action.rules_id = rule.id
            action.action_type = 'assign'
            action.field = 'entities_id'
            action.value = rule_data['target_entity']
            session.add(action)

        # If a target location is specified, add it
        if rule_data['target_location'] != '-1':
            action = RuleAction()
            action.rules_id = rule.id
            action.action_type = 'assign'
            action.field = 'locations_id'
            action.value = rule_data['target_location']
            session.add(action)

        session.commit()
        session.flush()

        return True


        # it s shit do it from dict directly
        #{'ranking' : 2, 'sub_type': 'PluginFusioninventoryInventoryRuleEntity',
        # date_mod: NOW(),

        # criteria
        # {'criteria': 'ip', // 'name' => hostanme, 'domain', 'serial', 'subnet', 'tag',
        #'condition': 0=is, 1=is_not, 2=contains, 3=doesnt contain,  4=start with, 5= finishes by
        # 6=regex_check, 7=not_regex, 8=exists, 9=doesnt eixts
        # 'pattern' : 192.168.44.,
        # 'rules_id' : rule_id

        # rule actions
        # { 'rules_id', rid
        # action_type = assign,
        # field = entities_id
        # value = ENTITY_ID
        #
        #action_type=regex_result,field=_affect_entity_by_tag, value=?
        #action_type=assign, field=locations_id, value=id

    @DatabaseHelper._sessionm
    def moveEntityRuleUp(self, session, id):

        rule = session.query(Rule).filter_by(id=id).one()
        # get previous rule
        previous = session.query(Rule).filter(Rule.ranking<rule.ranking)\
                .filter(Rule.name != 'Root')\
                .filter(Rule.sub_type=='PluginFusioninventoryInventoryRuleEntity')\
                .order_by(Rule.ranking.desc()).first()
        if previous:
            previous_ranking = previous.ranking
            rule_ranking = rule.ranking
            previous.ranking = rule_ranking
            session.commit()
            rule.ranking = previous_ranking
            session.commit()
            session.flush()

        return True

    @DatabaseHelper._sessionm
    def moveEntityRuleDown(self, session, id):

        rule = session.query(Rule).filter_by(id=id).one()
        # get next rule
        next_ = session.query(Rule).filter(Rule.ranking>rule.ranking)\
                .filter(Rule.name != 'Root')\
                .filter(Rule.sub_type=='PluginFusioninventoryInventoryRuleEntity')\
                .order_by(Rule.ranking.asc()).first()
        if next_:
            next_ranking = next_.ranking
            rule_ranking = rule.ranking
            next_.ranking = rule_ranking
            session.commit()
            rule.ranking = next_ranking
            session.commit()
            session.flush()

        return True


    @DatabaseHelper._sessionm
    def editEntityRule(self, session, id, rule_data):

        rule = session.query(Rule).filter_by(id=id).one()
        # Delete associated criteria and actions
        session.query(RuleCriterion).filter_by(rules_id=id).delete()
        session.query(RuleAction).filter_by(rules_id=id).delete()

        rule.name = rule_data['name']
        rule.description = rule_data['description']
        rule.match = rule_data['aggregator']
        if rule_data['active'] == 'on':
            rule.is_active = 1
        else:
            rule.is_active = 0

        session.commit()
        session.flush()

        # Adding rule criteria

        for i in xrange(len(rule_data['criteria'])):

            cr = RuleCriterion()
            cr.rules_id = rule.id
            cr.criteria = rule_data['criteria'][i]
            cr.condition = rule_data['operators'][i]
            cr.pattern = rule_data['patterns'][i]
            session.add(cr)
            session.commit()
            session.flush()

        # Adding rule actions

        # If a target entity is specified, add it
        if rule_data['target_entity'] != '-1':
            action = RuleAction()
            action.rules_id = rule.id
            action.action_type = 'assign'
            action.field = 'entities_id'
            action.value = rule_data['target_entity']
            session.add(action)

        # If a target location is specified, add it
        if rule_data['target_location'] != '-1':
            action = RuleAction()
            action.rules_id = rule.id
            action.action_type = 'assign'
            action.field = 'locations_id'
            action.value = rule_data['target_location']
            session.add(action)

        session.commit()
        session.flush()
        return True

    @DatabaseHelper._sessionm
    def getEntityRule(self, session, id):


        rule = session.query(Rule).filter_by(id=id).one()
        criteria = session.query(RuleCriterion).filter_by(rules_id=id).all()
        actions = session.query(RuleAction).filter_by(rules_id=id).all()

        result = {}
        result['active'] = rule.is_active
        result['name'] = rule.name
        result['description'] = rule.description
        result['aggregator'] = rule.match

        result['criteria'] = []
        result['operators'] = []
        result['patterns'] = []

        for cr in criteria:
            result['criteria'].append(cr.criteria)
            result['operators'].append(cr.condition)
            result['patterns'].append(cr.pattern)

        # By default, don't assign entity nor location
        result['target_entity'] = -1
        result['target_location'] = -1

        for action in actions:
            if action.field == 'entities_id' and action.action_type == 'assign':
                result['target_entity'] = action.value
            if action.field == 'locations_id' and action.action_type == 'assign':
                result['target_entity'] = action.value

        return result

    @DatabaseHelper._sessionm
    def deleteEntityRule(self, session, id):

        # Delete rule
        session.query(Rule).filter_by(id=id).delete()
        # Delete associated criteria and actions
        session.query(RuleCriterion).filter_by(rules_id=id).delete()
        session.query(RuleAction).filter_by(rules_id=id).delete()
        return True

    def moveComputerToEntity(self, uuid, entity_id):
        pass
        #UPDATE `glpi_computers`
        #SET `entities_id` = '5' WHERE `id` ='3'

    @DatabaseHelper._sessionm
    def getLocationsForUser(self, session, username):
        try:
            user_id = session.query(User).filter_by(name=username).one().id
        except NoResultFound:
            return []
        entities = []
        for profile in session.query(UserProfile).filter_by(users_id = user_id):
            entities += [{
                            'entity_id' : profile.entities_id,
                            'profile': profile.profiles_id,
                            'is_recursive' : profile.is_recursive,
                            'is_dynamic' : profile.is_dynamic
                        }]
        return entities

    @DatabaseHelper._sessionm
    def setLocationsForUser(self, session, username, profiles):

        user_id = session.query(User).filter_by(name=username).one().id
        # Delete all user entity profiles
        session.query(UserProfile).filter_by(users_id = user_id).delete()

        for attr in profiles:
            p = UserProfile()
            p.users_id = user_id
            p.profiles_id = attr['profile']
            p.entities_id = attr['entity_id']
            p.is_recursive = attr['is_recursive']
            p.is_dynamic = attr['is_dynamic']
            session.add(p)
            session.commit()

        session.flush()
        return True

    @DatabaseHelper._sessionm
    def getRegistryCollect(self, session, full_key):
        """
        Get the registry id where the collect is the defined key

        @param full_key: the registry key in the form hive/path/key
        @type full_key: str

        @return: id of the registry collect
        @rtype: int
        """

        # Split into hive / path / key
        return []

    @DatabaseHelper._sessionm
    def addRegistryCollect(self, session, full_key, key_name):
        """
        Add the registry collect for the defined key

        @param full_key: the registry key in the form hive/path/key
        @type full_key: str

        @param key_name: the name to be displayed
        @type key_name: str

        @return: success of the operation
        @rtype: bool
        """

        # Split into hive / path / key
        return []

    def getAllOsVersions(self, ctx, filt = ''):
        """ @return: all os versions defined in the GLPI database """
        session = create_session()
        query = session.query(OsVersion)
        if filter != '':
            query = query.filter(OsVersion.name.like('%'+filt+'%'))
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def addRegistryCollectContent(self, session, computers_id, registry_id, key, value):
        """
        Add registry collect content

        @param computers_id: the computer_id from glpi_computers
        @type computers_id: str

        @param registry_id: the registry_id from plugin_fusioninventory_collects_registries
        @type registry_id: str

        @param key: the registry key name
        @type key: str

        @param value: the key value
        @type value:

        @return: success of the operation
        @rtype: bool
        """

        # Check if already present
        return []

    @DatabaseHelper._sessionm
    def get_os_for_dashboard(self, session):
        """This function returns a list of OS and its version for dashboard
        Returns:
            dict of all the founded elements

        Dict structure:
            [
                {
                    'count': 1,
                    'version': '1807',
                    'os': 'Windows 10'
                },
                {
                    'count': 3,
                    'version': '16.04',
                    'os': 'Ubuntu'
                },
            ]
        """

        sql = session.query(Machine.operatingsystems_id,
            Machine.operatingsystemversions_id,
            OS.name,
            OsVersion.name)\
        .join(OS, OS.id == Machine.operatingsystems_id)\
        .join(OsVersion, OsVersion.id == Machine.operatingsystemversions_id)\
        .order_by(asc(OsVersion.name))
        sql = sql.filter(Machine.is_deleted == 0, Machine.is_template == 0)
        sql = self.__filter_on(sql)

        res = sql.all()

        result = [{'os': element[2], 'version': element[3], 'count':1} for element in res]

        def _add_element(element, list):
            """Private function which merge the element to the specified list.
            Params:
                element: dict of the os we need to merge into the list
                list : list of all the merged elements.
            Returns:
                list
            """
            # If an item is found, they are merged
            for machine in list:
                if element['os'] == machine['os'] and element['version'] == machine['version']:
                    machine['count'] = int(machine['count']) + int(element['count'])
                    return list

            # If no machine is matching with the element, the element is added
            list.append(element)
            return list

        final_list = []
        for machine in result:
            if machine['os'].startswith('Debian'):
                machine['os'] = 'Debian'
                machine['version'] = machine['version'].split(" ")[0]
            elif machine['os'].startswith('Microsoft'):
                machine['os'] = machine['os'].split(' ')[1:3]
                machine['os'] = ' '.join(machine['os'])
            elif machine['os'].startswith('Ubuntu'):
                machine['os'] = 'Ubuntu'
                # We want just the XX.yy version number
                machine['version'] = machine['version'].split(" ")[0].split(".")
                if len(machine['version']) >= 2:
                    machine['version'] = machine['version'][0:2]
                machine['version'] = '.'.join(machine['version'])
            elif machine['os'].startswith('Mageia'):
                machine['os'] = machine['os'].split(" ")[0]
            elif machine['os'].startswith('Unknown'):
                machine['os'] = machine['os'].split("(")[0]
                machine['version'] = ""
            elif machine['os'].startswith("CentOS"):
                machine['os'] = machine['os'].split(" ")[0]
                machine['version'] = machine['version'].split("(")[0].split(".")[0:2]
                machine['version'] = ".".join(machine['version'])

            elif machine['os'].startswith("macOS") or machine['os'].startswith("OS X"):
                machine['version'] = machine['version'].split(" (")[0].split(".")[0:2]
                machine['version'] = ".".join(machine['version'])

            else:
                pass

            final_list = _add_element(machine, final_list)
        return final_list

    @DatabaseHelper._sessionm
    def get_machines_with_os_and_version(self, session, oslocal, version = ''):
        """This function returns a list of id of selected OS for dashboard
        Params:
            os: string which contains the searched OS
            version: string which contains the searched version
        Returns:
            list of all the machines with specified OS and specified version
        """

        sql = session.query(Machine.id, Machine.name)\
        .join(OS, OS.id == Machine.operatingsystems_id)\
        .outerjoin(OsVersion, OsVersion.id == Machine.operatingsystemversions_id)\
        .filter(and_(OS.name.like('%'+oslocal+'%')), OsVersion.name.like('%'+version+'%'))

        sql = sql.filter(Machine.is_deleted == 0, Machine.is_template == 0)
        sql = self.__filter_on(sql)
        res = session.execute(sql)

        result = [{'id':a, 'hostname':b} for a,b in res]

        return result

    @DatabaseHelper._sessionm
    def get_machine_for_hostname(self, session, strlisthostname, filter, start, end):
        sqlrequest ="""
            SELECT
                `glpi_computers`.`id` AS `id`,
                `glpi_computers`.`name` AS `name`,
                `glpi_computers`.`comment` AS `description`,
                `glpi_operatingsystems`.name AS `os`,
                `glpi_computertypes`.`name` AS `type`,
                `glpi_computers`.`contact` AS `contact`,
                `glpi_entities`.`name` as `entity`
            FROM
                `glpi_computers`
                JOIN `glpi_items_operatingsystems` ON glpi_computers.`id` = `glpi_items_operatingsystems`.`items_id`
                JOIN `glpi_operatingsystems` ON `glpi_operatingsystems`.`id` = `glpi_items_operatingsystems`.`operatingsystems_id`
                JOIN glpi_computertypes ON glpi_computers.`computertypes_id` = `glpi_computertypes`.`id`
                JOIN glpi_entities ON glpi_computers.`entities_id` = glpi_entities.id
                where `glpi_computers`.`is_template` = 0 and `glpi_computers`.`is_deleted` = 0
                    and  `glpi_computers`.`name` in (%s);"""%(strlisthostname)
        id=[]
        name=[]
        description=[]
        os=[]
        typemache=[]
        contact=[]
        entity=[]
        result = []
        res = self.db.execute(sqlrequest)
        for element in res:
            id.append( element.id )
            name.append( element.name )
            description.append( element.description )
            os.append( element.os )
            typemache.append( element.type )
            contact.append( element.contact )
            entity.append( element.entity )
        result.append(id)
        result.append(name)
        result.append(description)
        result.append(os)
        result.append(typemache)
        result.append(contact)
        result.append(entity)
        return result

    @DatabaseHelper._sessionm
    def get_machine_for_id(self, session, strlistuuid, filter, start, limit):
        start = int(start)
        limit = int(limit)
        criteria = ''
        if filter != "":
            criteria = 'AND (glpi_computers.name Like "%%%s%%"\
            OR glpi_computers.comment Like "%%%s%%"\
            OR glpi_operatingsystems.name Like "%%%s%%"\
            OR glpi_computertypes.name Like "%%%s%%"\
            OR glpi_computers.contact Like "%%%s%%"\
            OR glpi_entities.name Like "%%%s%%"\
            )'%(filter, filter, filter, filter, filter, filter)

        sqlrequest = """
SELECT
    count(*) as nb
FROM
    `glpi_computers`
LEFT JOIN
    `glpi_operatingsystems` ON `glpi_computers`.`operatingsystems_id` = `glpi_operatingsystems`.`id`
LEFT JOIN
    `glpi_computertypes` ON `glpi_computers`.`computertypes_id` = `glpi_computertypes`.`id`
LEFT JOIN
    `glpi_entities` ON `glpi_computers`.`entities_id` = `glpi_entities`.`id`
WHERE
    `glpi_computers`.`is_template` = 0
AND `glpi_computers`.`is_deleted` = 0
AND  `glpi_computers`.`id` in (%s) %s;"""%(strlistuuid,
                          criteria)
        print sqlrequest
        res = session.execute(sqlrequest)
        session.commit()
        session.flush()
        nb=0
        for element in res:
            nb = element[0]

        sqlrequest = """
SELECT
    `glpi_computers`.`id` AS `id`,
    `glpi_computers`.`name` AS `name`,
    `glpi_computers`.`comment` AS `description`,
    `glpi_operatingsystems`.name AS `os`,
    `glpi_computertypes`.`name` AS `type`,
    `glpi_computers`.`contact` AS `contact`,
    `glpi_entities`.`name` AS `entity`
FROM
    `glpi_computers`
LEFT JOIN
    `glpi_operatingsystems` ON `glpi_computers`.`operatingsystems_id` = `glpi_operatingsystems`.`id`
LEFT JOIN
    `glpi_computertypes` ON `glpi_computers`.`computertypes_id` = `glpi_computertypes`.`id`
LEFT JOIN
    `glpi_entities` ON `glpi_computers`.`entities_id` = `glpi_entities`.`id`
WHERE
    `glpi_computers`.`is_template` = 0
AND `glpi_computers`.`is_deleted` = 0
AND  `glpi_computers`.`id` in (%s) %s
LIMIT %s, %s;"""%(strlistuuid,
                          criteria,
                          start,
                          limit)


        id=[]
        name=[]
        description=[]
        os=[]
        typemache=[]
        contact=[]
        entity=[]
        result = []
        res = session.execute(sqlrequest)
        session.commit()
        session.flush()

        #res = self.db.execute(sqlrequest)
        if res is not None:
            for element in res:
                id.append( element.id )
                name.append( element.name )
                description.append( element.description )
                os.append( element.os )
                typemache.append( element.type )
                contact.append( element.contact )
                entity.append( element.entity )
            result.append(id)
            result.append(name)
            result.append(description)
            result.append(os)
            result.append(typemache)
            result.append(contact)
            result.append(entity)

        result1={"total" : nb,
                 "listelet" : result}

        return result1


    @DatabaseHelper._sessionm
    def get_computer_count_for_dashboard(self, session, count=True):
        inventory_filtered_machines = self.__filter_on(session.query(Machine.id).filter(Machine.is_deleted == 0, \
                                                                                        Machine.is_template == 0)).all()
        ret = self.__getRestrictedComputersListQuery(None, '', session, True, False)

        inventory_filtered_machines = ['UUID%s'%id[0] for id in inventory_filtered_machines]
        online_machines = XmppMasterDatabase().get_machines_online_for_dashboard()

        unregistred_online_machine = []
        registered_online_machine = []
        registered_offline_machine = []

        registered_online_uuid_list = []
        for machine in online_machines:
            if machine['uuid'] is None or machine['uuid'] == "":
                unregistred_online_machine.append(machine['macaddress'])
            else:
                registered_online_uuid_list.append(machine['uuid'])
                registered_online_machine.append(machine['uuid'])

        for machine in inventory_filtered_machines:
            if machine not in registered_online_machine:
                registered_offline_machine.append(machine)

        if count is True:
            return {"registered" : len(inventory_filtered_machines), "online": len(registered_online_machine), 'offline': len(registered_offline_machine), 'unregistered': len(unregistred_online_machine)}
        else:
            return {"registered" : inventory_filtered_machines, "online": registered_online_machine, 'offline': registered_offline_machine,'unregistered': unregistred_online_machine}

# Class for SQLalchemy mapping
class Machine(object):
    __tablename__ = 'glpi_computers'

    def getUUID(self):
        return toUUID(self.id)
    def toH(self):
        return { 'hostname':self.name, 'uuid':toUUID(self.id) }
    def to_a(self):
        owner_login, owner_firstname, owner_realname = Glpi084().getMachineOwner(self)
        return [
            ['name',self.name],
            ['comments',self.comment],
            ['serial',self.serial],
            ['otherserial',self.otherserial],
            ['contact',self.contact],
            ['contact_num',self.contact_num],
            ['owner', owner_login],
            ['owner_firstname', owner_firstname],
            ['owner_realname', owner_realname],
            # ['tech_num',self.tech_num],
            ['os',self.operatingsystems_id],
            ['os_version',self.operatingsystemversions_id],
            ['os_sp',self.operatingsystemservicepacks_id],
            #['license_number',self.license_number],
            #['licenseid',self.license_id],
            ['location',self.locations_id],
            ['domain',self.domains_id],
            ['network',self.networks_id],
            ['model',self.computermodels_id],
            ['type',self.computertypes_id],
            ['entity',self.entities_id],
            ['uuid',Glpi084().getMachineUUID(self)]
        ]

class Entities(object):
    def toH(self):
        return {
            'uuid':toUUID(self.id),
            'name':self.name,
            'completename':self.completename,
            'comments':self.comment,
            'level':self.level
        }

class State(object):
    pass

class DiskFs(object):
    pass

class FusionAntivirus(object):
    pass

class FusionLocks(object):
    pass

class FusionAgents(object):
    to_be_exported = ['last_contact']

class Disk(object):
    pass

class Suppliers(object):
    pass

class Infocoms(object):
    pass

class Processor(object):
    pass

class ComputerProcessor(object):
    pass

class Memory(object):
    pass

class MemoryType(object):
    pass

class ComputerMemory(object):
    pass

class Logs(object):
    pass

class User(object):
    pass

class Profile(object):
    pass

class UserProfile(object):
    pass

class NetworkPorts(object):
    def toH(self):
        return {
            'uuid':toUUID(self.id),
            'name': self.name,
            'ifaddr': self.ip,
            'ifmac': self.mac,
            'netmask': noNone(self.netmask),
            'gateway': self.gateway,
            'subnet': self.subnet
        }

class OS(object):
    pass

class ComputerDevice(object):
    pass

class Domain(object):
    pass

class Manufacturers(object):
    pass

class Software(object):
    pass

class InstSoftware(object):
    pass

class Licenses(object):
    pass

class SoftwareVersion(object):
    pass

class Group(object):
    pass

class OsSp(object):
    pass

class Model(object):
    pass

class Locations(object):
    pass

class Net(object):
    pass

class NetworkInterfaces(object):
    pass

class IPAddresses(object):
    pass

class IPNetworks(object):
    pass

class NetworkNames(object):
    pass

class IPAddresses_IPNetworks(object):
    pass

class Collects(object):
    pass

class RegContents(object):
    pass

class Rule(DbTOA):
    pass

class RuleCriterion(DbTOA):
    pass

class RuleAction(DbTOA):
    pass

class OsVersion(DbTOA):
    pass
