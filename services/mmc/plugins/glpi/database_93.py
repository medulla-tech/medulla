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
version 9.3
"""
import os
import logging
import re
import datetime
import calendar, hashlib
import time
from configobj import ConfigObj
from xmlrpc.client import ProtocolError

from sqlalchemy import (
    and_,
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Date,
    ForeignKey,
    asc,
    or_,
    not_,
    desc,
    func,
    distinct,
)
from sqlalchemy.orm import create_session, mapper, relationship
from sqlalchemy.engine.row import Row
try:
    from sqlalchemy.sql.expression import ColumnOperators
except ImportError:
    from sqlalchemy.sql.operators import ColumnOperators
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.automap import automap_base
from mmc.support.mmctools import shlaunch
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
from mmc.plugins.glpi.utilities import complete_ctx, literalquery
from mmc.plugins.glpi.database_utils import (
    decode_latin1,
    encode_latin1,
    decode_utf8,
    encode_utf8,
    fromUUID,
    toUUID,
    setUUID,
)
from mmc.plugins.glpi.database_utils import DbTOA  # pyflakes.ignore
from mmc.plugins.dyngroup.config import DGConfig
from distutils.version import LooseVersion, StrictVersion
from mmc.plugins.xmppmaster.config import xmppMasterConfig

from pulse2.database.xmppmaster import XmppMasterDatabase

from mmc.agent import PluginManager
import traceback, sys
from collections import OrderedDict
import decimal

logger = logging.getLogger()


class Glpi93(DyngroupDatabaseHelper):
    """
    Singleton Class to query the glpi database in version > 9.3

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
        self.db = create_engine(
            dburi,
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
        )
        logging.getLogger().debug("Trying to detect if GLPI version is higher than 9.3")

        try:
            self._glpi_version = list(
                self.db.execute("SELECT version FROM glpi_configs").fetchone().values()
            )[0].replace(" ", "")
        except OperationalError:
            self._glpi_version = list(
                self.db.execute('SELECT value FROM glpi_configs WHERE name = "version"')
                .fetchone()
                .values()
            )[0].replace(" ", "")

        if LooseVersion(self._glpi_version) >= LooseVersion("9.3") and LooseVersion(
            self._glpi_version
        ) <= LooseVersion("9.3.9"):
            logging.getLogger().debug("GLPI version %s found !" % self._glpi_version)
            return True
        else:
            logging.getLogger().debug("GLPI higher than version 9.3 was not detected")
            return False

    @property
    def glpi_version(self):
        return self._glpi_version

    def glpi_version_new(self):
        return False

    def activate(self, config=None):
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
        self.db = create_engine(
            dburi,
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
        )
        try:
            self.db.execute('SELECT "\xe9"')
            setattr(Glpi93, "decode", decode_utf8)
            setattr(Glpi93, "encode", encode_utf8)
        except:
            self.logger.warn("Your database is not in utf8, will fallback in latin1")
            setattr(Glpi93, "decode", decode_latin1)
            setattr(Glpi93, "encode", encode_latin1)

        try:
            self._glpi_version = list(
                self.db.execute("SELECT version FROM glpi_configs").fetchone().values()
            )[0].replace(" ", "")
        except OperationalError:
            self._glpi_version = list(
                self.db.execute('SELECT value FROM glpi_configs WHERE name = "version"')
                .fetchone()
                .values()
            )[0].replace(" ", "")

        self.metadata = MetaData(self.db)
        self.initMappers()
        self.logger.info("Glpi is in version %s" % (self.glpi_version))
        self.metadata.create_all()
        self.is_activated = True
        self.logger.debug("Glpi finish activation")

        searchOptionConfFile = os.path.join(
            mmcconfdir, "plugins", "glpi_search_options.ini"
        )
        self.searchOptions = ConfigObj(searchOptionConfFile)

        return True

    def getTableName(self, name):
        return "".join([x.capitalize() for x in name.split("_")])

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the inventory database
        """

        Base = automap_base()
        Base.prepare(self.db, reflect=True)

        # Only federated tables (beginning by local_) are automatically mapped
        # If needed, excludes tables from this list
        exclude_table = []
        # Dynamically add attributes to the object for each mapped class
        for table_name, mapped_class in Base.classes.items():
            if table_name in exclude_table:
                continue
            if table_name.startswith("local"):
                setattr(self, table_name.capitalize(), mapped_class)

        self.klass = {}

        # simply declare some tables (that dont need and FK relations, or anything special to declare)
        for i in (
            "glpi_operatingsystemversions",
            "glpi_computertypes",
            "glpi_operatingsystems",
            "glpi_operatingsystemservicepacks",
            "glpi_operatingsystemarchitectures",
            "glpi_domains",
            "glpi_computermodels",
            "glpi_networks",
        ):
            setattr(self, i, Table(i, self.metadata, autoload=True))
            j = self.getTableName(i)
            exec("class %s(DbTOA): pass" % j)
            mapper(eval(j), getattr(self, i))
            self.klass[i] = eval(j)

        # declare all the glpi_device* and glpi_computer_device*
        # two of these tables have a nomenclature one (devicecasetypes and devicememorytypes) but we dont need it for the moment.
        #
        # List of devices:
        # cases, controls, drives, graphiccards, harddrives, motherboards, networkcards,
        # pcis, powersupplies, soundcards

        self.devices = (
            "devicecases",
            "devicecontrols",
            "devicedrives",
            "devicegraphiccards",
            "deviceharddrives",
            "devicemotherboards",
            "devicenetworkcards",
            "devicepcis",
            "devicepowersupplies",
            "devicesoundcards",
        )
        for i in self.devices:
            setattr(self, i, Table("glpi_%s" % i, self.metadata, autoload=True))
            j = self.getTableName(i)
            exec("class %s(DbTOA): pass" % j)
            mapper(eval(j), getattr(self, i))
            self.klass[i] = eval(j)

            setattr(
                self,
                "computers_%s" % i,
                Table(
                    "glpi_items_%s" % i,
                    self.metadata,
                    Column("items_id", Integer, ForeignKey("glpi_computers_pulse.id")),
                    Column("%s_id" % i, Integer, ForeignKey("glpi_%s.id" % i)),
                    autoload=True,
                ),
            )
            j = self.getTableName("computers_%s" % i)
            exec("class %s(DbTOA): pass" % j)
            mapper(eval(j), getattr(self, "computers_%s" % i))
            self.klass["computers_%s" % i] = eval(j)

        # entity
        self.entities = Table("glpi_entities", self.metadata, autoload=True)
        mapper(Entities, self.entities)

        # rules
        self.rules = Table("glpi_rules", self.metadata, autoload=True)
        mapper(Rule, self.rules)

        self.rule_criterias = Table("glpi_rulecriterias", self.metadata, autoload=True)
        mapper(RuleCriterion, self.rule_criterias)

        self.rule_actions = Table("glpi_ruleactions", self.metadata, autoload=True)
        mapper(RuleAction, self.rule_actions)

        # location
        self.locations = Table("glpi_locations", self.metadata, autoload=True)
        mapper(Locations, self.locations)

        # logs
        self.logs = Table(
            "glpi_logs",
            self.metadata,
            Column("items_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            autoload=True,
        )
        mapper(Logs, self.logs)

        # processor
        self.processor = Table("glpi_deviceprocessors", self.metadata, autoload=True)
        mapper(Processor, self.processor)

        self.computerProcessor = Table(
            "glpi_items_deviceprocessors",
            self.metadata,
            Column("items_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            Column(
                "deviceprocessors_id", Integer, ForeignKey("glpi_deviceprocessors.id")
            ),
            autoload=True,
        )
        mapper(ComputerProcessor, self.computerProcessor)

        # memory
        self.memory = Table(
            "glpi_devicememories",
            self.metadata,
            Column(
                "devicememorytypes_id", Integer, ForeignKey("glpi_devicememorytypes.id")
            ),
            autoload=True,
        )
        mapper(Memory, self.memory)

        self.memoryType = Table("glpi_devicememorytypes", self.metadata, autoload=True)
        mapper(MemoryType, self.memoryType)

        self.computerMemory = Table(
            "glpi_items_devicememories",
            self.metadata,
            Column("items_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            Column("devicememories_id", Integer, ForeignKey("glpi_devicememories.id")),
            autoload=True,
        )
        mapper(ComputerMemory, self.computerMemory)

        # interfaces types
        self.interfaceType = Table("glpi_interfacetypes", self.metadata, autoload=True)

        # os
        self.os = Table("glpi_operatingsystems", self.metadata, autoload=True)
        mapper(OS, self.os)

        self.os_sp = Table(
            "glpi_operatingsystemservicepacks", self.metadata, autoload=True
        )
        mapper(OsSp, self.os_sp)

        self.os_arch = Table(
            "glpi_operatingsystemarchitectures", self.metadata, autoload=True
        )
        mapper(OsArch, self.os_arch)

        # domain
        self.domain = Table("glpi_domains", self.metadata, autoload=True)
        mapper(Domain, self.domain)

        # glpi_infocoms
        self.infocoms = Table(
            "glpi_infocoms",
            self.metadata,
            Column("suppliers_id", Integer, ForeignKey("glpi_suppliers.id")),
            Column("items_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            autoload=True,
        )
        mapper(Infocoms, self.infocoms)

        # glpi_suppliers
        self.suppliers = Table("glpi_suppliers", self.metadata, autoload=True)
        mapper(Suppliers, self.suppliers)

        # glpi_filesystems
        self.diskfs = Table("glpi_filesystems", self.metadata, autoload=True)
        mapper(DiskFs, self.diskfs)

        # glpi_operatingsystemversions
        self.os_version = Table(
            "glpi_operatingsystemversions", self.metadata, autoload=True
        )
        mapper(OsVersion, self.os_version)

        ## Fusion Inventory tables

        self.fusionantivirus = None
        try:
            self.logger.debug("Try to load fusion antivirus table...")
            self.fusionantivirus = Table(
                "glpi_computerantiviruses",
                self.metadata,
                Column("computers_id", Integer, ForeignKey("glpi_computers_pulse.id")),
                Column(
                    "manufacturers_id", Integer, ForeignKey("glpi_manufacturers.id")
                ),
                autoload=True,
            )
            mapper(FusionAntivirus, self.fusionantivirus)
            self.logger.debug("... Success !!")
        except:
            self.logger.warn("Load of fusion antivirus table failed")
            self.logger.warn(
                "This means you can not know antivirus statuses of your machines."
            )
            self.logger.warn("This feature comes with Fusioninventory GLPI plugin")

        # glpi_plugin_fusioninventory_locks
        self.fusionlocks = None
        # glpi_plugin_fusioninventory_agents
        self.fusionagents = None

        if self.fusionantivirus is not None:  # Fusion is not installed
            self.logger.debug("Load glpi_plugin_fusioninventory_locks")
            self.fusionlocks = Table(
                "glpi_plugin_fusioninventory_locks",
                self.metadata,
                Column("items_id", Integer, ForeignKey("glpi_computers_pulse.id")),
                autoload=True,
            )
            mapper(FusionLocks, self.fusionlocks)
            self.logger.debug("Load glpi_plugin_fusioninventory_agents")
            self.fusionagents = Table(
                "glpi_plugin_fusioninventory_agents",
                self.metadata,
                Column("computers_id", Integer, ForeignKey("glpi_computers_pulse.id")),
                autoload=True,
            )
            mapper(FusionAgents, self.fusionagents)

        # glpi_items_disks
        self.disk = Table(
            "glpi_items_disks",
            self.metadata,
            Column("items_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            Column("filesystems_id", Integer, ForeignKey("glpi_filesystems.id")),
            autoload=True,
        )
        mapper(Disk, self.disk)

        #####################################
        # GLPI 0.90 Network tables
        # TODO take care with the itemtype should we always set it to Computer => Yes
        #####################################

        # TODO Are these table needed (inherit of previous glpi database*py files) ?
        self.networkinterfaces = Table(
            "glpi_networkinterfaces", self.metadata, autoload=True
        )
        mapper(NetworkInterfaces, self.networkinterfaces)

        self.net = Table("glpi_networks", self.metadata, autoload=True)
        mapper(Net, self.net)

        # New network tables
        self.ipnetworks = Table("glpi_ipnetworks", self.metadata, autoload=True)
        mapper(IPNetworks, self.ipnetworks)

        self.ipaddresses_ipnetworks = Table(
            "glpi_ipaddresses_ipnetworks",
            self.metadata,
            Column("ipaddresses_id", Integer, ForeignKey("glpi_ipaddresses.id")),
            Column("ipnetworks_id", Integer, ForeignKey("glpi_networks.id")),
            autoload=True,
        )
        mapper(IPAddresses_IPNetworks, self.ipaddresses_ipnetworks)

        self.ipaddresses = Table("glpi_ipaddresses", self.metadata, autoload=True)
        mapper(
            IPAddresses,
            self.ipaddresses,
            properties={
                "ipnetworks": relationship(
                    IPNetworks,
                    secondary=self.ipaddresses_ipnetworks,
                    primaryjoin=self.ipaddresses.c.id
                    == self.ipaddresses_ipnetworks.c.ipaddresses_id,
                    secondaryjoin=self.ipnetworks.c.id
                    == self.ipaddresses_ipnetworks.c.ipnetworks_id,
                    foreign_keys=[
                        self.ipaddresses_ipnetworks.c.ipaddresses_id,
                        self.ipaddresses_ipnetworks.c.ipnetworks_id,
                    ],
                )
            },
        )

        self.networknames = Table("glpi_networknames", self.metadata, autoload=True)
        mapper(
            NetworkNames,
            self.networknames,
            properties={
                # ipaddresses is a one2many relation from NetworkNames to IPAddresses
                # so uselist must be set to True
                "ipaddresses": relationship(
                    IPAddresses,
                    primaryjoin=and_(
                        IPAddresses.items_id == self.networknames.c.id,
                        IPAddresses.itemtype == "NetworkName",
                    ),
                    uselist=True,
                    foreign_keys=[self.networknames.c.id],
                ),
            },
        )

        self.networkports = Table("glpi_networkports", self.metadata, autoload=True)
        mapper(
            NetworkPorts,
            self.networkports,
            properties={
                "networknames": relationship(
                    NetworkNames,
                    primaryjoin=and_(
                        NetworkNames.items_id == self.networkports.c.id,
                        NetworkNames.itemtype == "NetworkPort",
                    ),
                    foreign_keys=[self.networkports.c.id],
                ),
            },
        )

        # machine (we need the foreign key, so we need to declare the table by hand ...
        #          as we don't need all columns, we don't declare them all)
        self.machine = Table(
            "glpi_computers_pulse",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("entities_id", Integer, ForeignKey("glpi_entities.id")),
            Column(
                "operatingsystems_id", Integer, ForeignKey("glpi_operatingsystems.id")
            ),
            Column(
                "operatingsystemversions_id",
                Integer,
                ForeignKey("glpi_operatingsystemversions.id"),
            ),
            Column(
                "operatingsystemservicepacks_id",
                Integer,
                ForeignKey("glpi_operatingsystemservicepacks.id"),
            ),
            Column(
                "operatingsystemarchitectures_id",
                Integer,
                ForeignKey("glpi_operatingsystemarchitectures.id"),
            ),
            Column("locations_id", Integer, ForeignKey("glpi_locations.id")),
            Column("domains_id", Integer, ForeignKey("glpi_domains.id")),
            Column("networks_id", Integer, ForeignKey("glpi_networks.id")),
            Column("computermodels_id", Integer, ForeignKey("glpi_computermodels.id")),
            Column("computertypes_id", Integer, ForeignKey("glpi_computertypes.id")),
            Column("groups_id", Integer, ForeignKey("glpi_groups.id")),
            Column("users_id", Integer, ForeignKey("glpi_users.id")),
            Column("manufacturers_id", Integer, ForeignKey("glpi_manufacturers.id")),
            Column("name", String(255), nullable=False),
            Column("serial", String(255), nullable=False),
            Column("license_number", String(255), nullable=True),
            Column("license_id", String(255), nullable=True),
            Column("is_deleted", Integer, nullable=False),
            Column("is_template", Integer, nullable=False),
            Column("states_id", Integer, ForeignKey("glpi_states.id"), nullable=False),
            Column("comment", String(255), nullable=False),
            Column("date_mod", Date, nullable=False),
            autoload=True,
        )
        mapper(
            Machine,
            self.machine,
            properties={
                # networkports is a one2many relation from Machine to NetworkPorts
                # so uselist must be set to True
                "networkports": relationship(
                    NetworkPorts,
                    primaryjoin=and_(
                        NetworkPorts.items_id == self.machine.c.id,
                        NetworkPorts.itemtype == "Computer",
                    ),
                    uselist=True,
                    foreign_keys=[self.machine.c.id],
                ),
                "domains": relationship(Domain),
            },
        )

        # states
        self.state = Table("glpi_states", self.metadata, autoload=True)
        mapper(State, self.state)
        # profile
        self.profile = Table(
            "glpi_profiles",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(255), nullable=False),
        )
        mapper(Profile, self.profile)

        # user
        self.user = Table(
            "glpi_users",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("locations_id", Integer, ForeignKey("glpi_locations.id")),
            Column("name", String(255), nullable=False),
            Column("password", String(40), nullable=False),
            Column("firstname", String(255), nullable=False),
            Column("realname", String(255), nullable=False),
            Column("auths_id", Integer, nullable=False),
            Column("is_deleted", Integer, nullable=False),
            Column("is_active", Integer, nullable=False),
        )
        mapper(User, self.user)

        # userprofile
        self.userprofile = Table(
            "glpi_profiles_users",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("users_id", Integer, ForeignKey("glpi_users.id")),
            Column("profiles_id", Integer, ForeignKey("glpi_profiles.id")),
            Column("entities_id", Integer, ForeignKey("glpi_entities.id")),
            Column("is_dynamic", Integer),
            Column("is_recursive", Integer),
        )
        mapper(UserProfile, self.userprofile)

        # glpi_manufacturers
        self.manufacturers = Table("glpi_manufacturers", self.metadata, autoload=True)
        mapper(Manufacturers, self.manufacturers)

        # software
        self.software = Table(
            "glpi_softwares",
            self.metadata,
            Column("manufacturers_id", Integer, ForeignKey("glpi_manufacturers.id")),
            autoload=True,
        )
        mapper(Software, self.software)

        # glpi_inst_software
        self.inst_software = Table(
            "glpi_computers_softwareversions",
            self.metadata,
            Column("computers_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            Column(
                "softwareversions_id", Integer, ForeignKey("glpi_softwareversions.id")
            ),
            autoload=True,
        )
        mapper(InstSoftware, self.inst_software)

        # glpi_licenses
        self.licenses = Table(
            "glpi_softwarelicenses",
            self.metadata,
            Column("softwares_id", Integer, ForeignKey("glpi_softwares.id")),
            autoload=True,
        )
        mapper(Licenses, self.licenses)

        # glpi_softwareversions
        self.softwareversions = Table(
            "glpi_softwareversions",
            self.metadata,
            Column("softwares_id", Integer, ForeignKey("glpi_softwares.id")),
            autoload=True,
        )
        mapper(SoftwareVersion, self.softwareversions)

        # model
        self.model = Table("glpi_computermodels", self.metadata, autoload=True)
        mapper(Model, self.model)

        # group
        self.group = Table("glpi_groups", self.metadata, autoload=True)
        mapper(Group, self.group)

        # collects
        self.collects = Table(
            "glpi_plugin_fusioninventory_collects",
            self.metadata,
            Column("entities_id", Integer, ForeignKey("glpi_entities.id")),
            autoload=True,
        )
        mapper(Collects, self.collects)

        # registries
        self.registries = Table(
            "glpi_plugin_fusioninventory_collects_registries",
            self.metadata,
            Column(
                "plugin_fusioninventory_collects_id",
                Integer,
                ForeignKey("glpi_plugin_fusioninventory_collects.id"),
            ),
            autoload=True,
        )
        mapper(Registries, self.registries)

        # registries contents
        self.regcontents = Table(
            "glpi_plugin_fusioninventory_collects_registries_contents",
            self.metadata,
            Column("computers_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            Column(
                "plugin_fusioninventory_collects_registries_id",
                Integer,
                ForeignKey("glpi_plugin_fusioninventory_collects_registries.id"),
            ),
            autoload=True,
        )
        mapper(RegContents, self.regcontents)

        # items contents
        self.computersitems = Table(
            "glpi_computers_items",
            self.metadata,
            Column("computers_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            autoload=True,
        )
        mapper(Computersitems, self.computersitems)

        # use view glpi_view_computers_items_printer
        self.view_computers_items_printer = Table(
            "glpi_view_computers_items_printer",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("items_id", Integer, ForeignKey("glpi_printers.id")),
            Column("computers_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            autoload=True,
        )
        mapper(Computersviewitemsprinter, self.view_computers_items_printer)

        self.view_computers_items_peripheral = Table(
            "glpi_view_computers_items_peripheral",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("items_id", Integer, ForeignKey("glpi_peripherals.id")),
            Column("computers_id", Integer, ForeignKey("glpi_computers_pulse.id")),
            autoload=True,
        )
        mapper(Computersviewitemsperipheral, self.view_computers_items_peripheral)

        self.glpi_view_peripherals_manufacturers = Table(
            "glpi_view_peripherals_manufacturers",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "items_id", Integer, ForeignKey("glpi_peripherals.manufacturers_id")
            ),
            autoload=True,
        )
        mapper(Peripheralsmanufacturers, self.glpi_view_peripherals_manufacturers)

        # Monitors items
        self.monitors = Table("glpi_monitors", self.metadata, autoload=True)
        mapper(Monitors, self.monitors)

        # Phones items
        self.phones = Table("glpi_phones", self.metadata, autoload=True)
        mapper(Phones, self.phones)

        # Printers items
        self.printers = Table("glpi_printers", self.metadata, autoload=True)
        mapper(Printers, self.printers)

        # Peripherals items
        self.peripherals = Table("glpi_peripherals", self.metadata, autoload=True)
        mapper(Peripherals, self.peripherals)

    # internal query generators
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
            for filter_key, filter_values in list(self.config.filter_on.items()):
                if filter_key == "state":
                    self.logger.debug(
                        "will filter %s in (%s)" % (filter_key, str(filter_values))
                    )
                    a_filter_on.append(self.machine.c.states_id.in_(filter_values))
                if filter_key == "type":
                    self.logger.debug(
                        "will filter %s in (%s)" % (filter_key, str(filter_values))
                    )
                    a_filter_on.append(
                        self.machine.c.computertypes_id.in_(filter_values)
                    )
                if filter_key == "entity":
                    self.logger.debug(
                        "will filter %s in (%s)" % (filter_key, str(filter_values))
                    )
                    a_filter_on.append(self.machine.c.entities_id.in_(filter_values))
                if filter_key == "autoupdatesystems_id":
                    self.logger.debug(
                        "will filter %s in (%s)" % (filter_key, str(filter_values))
                    )
                    a_filter_on.append(
                        self.machine.c.autoupdatesystems_id.in_(filter_values)
                    )
                if not filter_key in (
                    "state",
                    "type",
                    "entity",
                    "autoupdatesystems_id",
                ):
                    self.logger.warn("dont know how to filter on %s" % (filter_key))
            if len(a_filter_on) == 0:
                return None
            elif len(a_filter_on) == 1:
                return a_filter_on[0]
            else:
                return and_(*a_filter_on)
        return None

    def __filter_on_entity(self, query, ctx, other_locids=None):
        # Mutable list used other_locids as default argument to a method or function
        other_locids = other_locids or []
        ret = self.__filter_on_entity_filter(query, ctx, other_locids)
        return query.filter(ret)

    def __filter_on_entity_filter(self, query, ctx, other_locids=None):
        # FIXME: I put the locationsid in the security context to optimize the
        # number of requests. locationsid is set by
        # glpi.utilities.complete_ctx, but when querying via the dyngroup
        # plugin it is not called.
        # Mutable list used other_locids as default argument to a method or function
        other_locids = other_locids or []
        if not hasattr(ctx, "locationsid"):
            complete_ctx(ctx)
        return self.machine.c.entities_id.in_(ctx.locationsid + other_locids)

    @DatabaseHelper._sessionm
    def mini_computers_count(self, session):
        """Count all the GLPI machines
        Returns:
            int count of machines"""

        sql = """select count(id) as count_machines from glpi_computers;"""
        res = session.execute(sql)
        for element in res:
            result = element[0]
        return result

    def __xmppmasterfilter(self, filt=None):
        ret = {}
        if "computerpresence" in filt:
            d = XmppMasterDatabase().getlistPresenceMachineid()
            listid = [x.replace("UUID", "") for x in d]
            ret["computerpresence"] = [
                "computerpresence",
                "xmppmaster",
                filt["computerpresence"],
                listid,
            ]
        elif "query" in filt and filt["query"][0] in ["AND", "OR", "NOT"]:
            for q in filt["query"][1]:
                # if len(q) >=3: and  q[2].lower() in ["online computer", "ou user", "ou machine"]:
                if len(q) >= 3:
                    if q[2].lower() in ["online computer", "ou machine", "ou user"]:
                        listid = XmppMasterDatabase().getxmppmasterfilterforglpi(q)
                        q.append(listid)
                        ret[q[2]] = [q[1], q[2], q[3], listid]
        return ret

    @DatabaseHelper._sessionm
    def get_machines_list1(self, session, start, end, ctx):
        # start and end are used to set the limit parameter in the query

        debugfunction = False
        if "filter" in ctx and "@@@DEBUG@@@" in ctx["filter"]:
            debugfunction = True
            ctx["filter"] = ctx["filter"].replace("@@@DEBUG@@@", "").strip()

        start = int(start)
        end = int(end)
        location = ""
        criterion = ""
        field = ""
        contains = ""

        master_config = xmppMasterConfig()
        reg_columns = []
        r = re.compile(r"reg_key_.*")
        regs = list(filter(r.search, self.config.summary))
        for regkey in regs:
            regkeyconf = getattr(master_config, regkey).split("|")[0].split("\\")[-1]
            # logging.getLogger().error(regkeyconf)
            reg_columns.append(regkeyconf)

        # location filter is corresponding to the entity selection in the interface
        if "location" in ctx and ctx["location"] != "":
            location = ctx["location"].replace("UUID", "")

        # "filter" filter is corresponding to the string the user wants to find
        if "filter" in ctx and ctx["filter"] != "":
            criterion = ctx["filter"]

        if "field" in ctx and ctx["field"] != "":
            field = ctx["field"]

        if "contains" in ctx and ctx["contains"] != "":
            contains = ctx["contains"]

        query = (
            session.query(Machine.id.label("uuid"))
            .distinct(Machine.id)
            .outerjoin(
                self.glpi_computertypes,
                Machine.computertypes_id == self.glpi_computertypes.c.id,
            )
            .outerjoin(self.user, Machine.users_id == self.user.c.id)
            .join(Entities, Entities.id == Machine.entities_id)
            .outerjoin(self.locations, Machine.locations_id == self.locations.c.id)
            .outerjoin(
                self.manufacturers, Machine.manufacturers_id == self.manufacturers.c.id
            )
            .outerjoin(
                self.glpi_computermodels,
                Machine.computermodels_id == self.glpi_computermodels.c.id,
            )
            .outerjoin(self.regcontents, Machine.id == self.regcontents.c.computers_id)
        )

        if field != "":
            query = query.outerjoin(
                Computersitems, Machine.id == Computersitems.computers_id
            )
            if field != "type":
                query = query.outerjoin(
                    Peripherals,
                    and_(
                        Computersitems.items_id == Peripherals.id,
                        Computersitems.itemtype == "Peripheral",
                    ),
                ).outerjoin(
                    Peripheralsmanufacturers,
                    Peripherals.manufacturers_id == Peripheralsmanufacturers.id,
                )
        if "cn" in self.config.summary:
            query = query.add_column(Machine.name.label("cn"))

        if "os" in self.config.summary:
            query = query.add_column(self.os.c.name.label("os")).join(self.os)

        if "description" in self.config.summary:
            query = query.add_column(Machine.comment.label("description"))

        if "type" in self.config.summary:
            query = query.add_column(self.glpi_computertypes.c.name.label("type"))

        if "owner_firstname" in self.config.summary:
            query = query.add_column(self.user.c.firstname.label("owner_firstname"))

        if "owner_realname" in self.config.summary:
            query = query.add_column(self.user.c.realname.label("owner_realname"))

        if "owner" in self.config.summary:
            query = query.add_column(self.user.c.name.label("owner"))

        if "user" in self.config.summary:
            query = query.add_column(Machine.contact.label("user"))

        if "entity" in self.config.summary:
            query = query.add_column(Entities.name.label("entity"))

        if "location" in self.config.summary:
            query = query.add_column(self.locations.c.name.label("location"))

        if "model" in self.config.summary:
            query = query.add_column(self.model.c.name.label("model"))

        if "manufacturer" in self.config.summary:
            query = query.add_column(self.manufacturers.c.name.label("manufacturer"))

        # Don't select deleted or template machines
        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)

        # Select machines from the specified entity
        if location != "":
            listentity = [int(x.strip()) for x in location.split(",")]
            query = query.filter(Entities.id.in_(listentity))

        # Add all the like clauses to find machines containing the criterion
        if criterion != "":
            if field == "":
                query = query.filter(
                    or_(
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
                        self.regcontents.c.value.contains(criterion),
                    )
                )
            else:
                if field == "peripherals":
                    if contains == "notcontains":
                        query = query.filter(not_(Peripherals.name.contains(criterion)))
                    else:
                        query = query.filter(Peripherals.name.contains(criterion))
                else:
                    pass

        query = query.order_by(Machine.name)

        # Even if computerpresence is not specified,
        # needed in "all computers" page to know which computer in online or offline
        online_machines = [
            int(id)
            for id in XmppMasterDatabase().getidlistPresenceMachine(presence=True)
            if id != "UUID" and id != ""
        ]
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
        columns_name = [column["name"] for column in query.column_descriptions]

        if debugfunction:
            try:
                self.logger.info("@@@DEBUG@@@ %s" % literalquery(query))
            except Exception as e:
                self.logger.error(
                    "display @@@DEBUG@@@ sql literal from alchemy : %s" % e
                )

        machines = query.all()

        result = {"count": count, "data": {index: [] for index in columns_name}}
        result["data"]["presence"] = []

        nb_columns = len(columns_name)

        regs = {reg_column: [] for reg_column in reg_columns}
        result["data"]["reg"] = regs

        for machine in machines:
            _count = 0
            while _count < nb_columns:
                result["data"][columns_name[_count]].append(machine[_count])
                _count += 1

            if machine[0] in online_machines:
                result["data"]["presence"].append(1)
            else:
                result["data"]["presence"].append(0)

            for column in reg_columns:
                result["data"]["reg"][column].append(None)

        regquery = (
            session.query(
                self.regcontents.c.computers_id,
                self.regcontents.c.key,
                self.regcontents.c.value,
            )
            .filter(
                and_(
                    self.regcontents.c.key.in_(reg_columns),
                    self.regcontents.c.computers_id.in_(result["data"]["uuid"]),
                )
            )
            .all()
        )
        for reg in regquery:
            index = result["data"]["uuid"].index(reg[0])
            result["data"]["reg"][reg[1]][index] = reg[2]

        result["count"] = count

        uuids = []
        for id in result["data"]["uuid"]:
            uuids.append("UUID%s" % id)

        result["xmppdata"] = []
        result["xmppdata"] = XmppMasterDatabase().getmachinesbyuuids(uuids)
        return result

    @DatabaseHelper._sessionm
    def get_machines_list(self, session, start, end, ctx):
        """
        This function is used for afficher the computer view based on glpi.
        Args:
            session: The SQLAlchely session
            start:
            end:
            ctx:
        Returns:
            It returns the list of the machines.
        """
        # start and end are used to set the limit parameter in the query
        start = int(start)
        end = int(end)
        master_config = xmppMasterConfig()
        r = re.compile(r"reg_key_.*")
        regs = list(filter(r.search, self.config.summary))
        list_reg_columns_name = [
            getattr(master_config, regkey).split("|")[0].split("\\")[-1]
            for regkey in regs
        ]
        uuidsetup = ctx["uuidsetup"] if "uuidsetup" in ctx else ""
        idmachine = ctx["idmachine"].replace("UUID", "") if "idmachine" in ctx else ""
        # "location" filter is corresponding to the entity selection in the interface
        location = ctx["location"].replace("UUID", "") if "location" in ctx else ""
        # "filter" filter is corresponding to the string the user wants to find
        criterion = ctx["filter"] if "filter" in ctx else ""
        field = ctx["field"] if "field" in ctx else ""
        contains = ctx["contains"] if "contains" in ctx else ""
        if idmachine == "" and uuidsetup == "":
            online_machines = []
            online_machines = XmppMasterDatabase().getlistPresenceMachineid()
            if online_machines is not None:
                online_machines = [
                    int(uuid.replace("UUID", ""))
                    for uuid in online_machines
                    if uuid != ""
                ]

        query = (
            session.query(Machine.id.label("uuid"))
            .distinct(Machine.id)
            .join(
                self.glpi_computertypes,
                Machine.computertypes_id == self.glpi_computertypes.c.id,
            )
            .outerjoin(self.user, Machine.users_id == self.user.c.id)
            .join(Entities, Entities.id == Machine.entities_id)
            .outerjoin(self.locations, Machine.locations_id == self.locations.c.id)
            .outerjoin(
                self.manufacturers, Machine.manufacturers_id == self.manufacturers.c.id
            )
            .join(
                self.glpi_computermodels,
                Machine.computermodels_id == self.glpi_computermodels.c.id,
            )
            .outerjoin(self.regcontents, Machine.id == self.regcontents.c.computers_id)
        )

        if field != "":
            query = query.join(
                Computersitems, Machine.id == Computersitems.computers_id
            )
            if field != "type":
                query = query.join(
                    Peripherals,
                    and_(
                        Computersitems.items_id == Peripherals.id,
                        Computersitems.itemtype == "Peripheral",
                    ),
                ).join(
                    Peripheralsmanufacturers,
                    Peripherals.manufacturers_id == Peripheralsmanufacturers.id,
                )
        # fild always exist
        query = query.add_column(Machine.name.label("cn"))
        if uuidsetup != "" or idmachine != "":
            query = query.add_column(Machine.uuid.label("uuid_setup"))

        if "os" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(self.os.c.name.label("os")).join(self.os)

        if "description" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(Machine.comment.label("description"))

        if "type" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(self.glpi_computertypes.c.name.label("type"))

        if (
            "owner_firstname" in self.config.summary
            or idmachine != ""
            or uuidsetup != ""
        ):
            query = query.add_column(self.user.c.firstname.label("owner_firstname"))

        if (
            "owner_realname" in self.config.summary
            or idmachine != ""
            or uuidsetup != ""
        ):
            query = query.add_column(self.user.c.realname.label("owner_realname"))

        if "owner" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(self.user.c.name.label("owner"))

        if "user" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(Machine.contact.label("user"))

        if "entity" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(Entities.name.label("entity"))
            query = query.add_column(Entities.completename.label("complete_entity"))
            query = query.add_column(Entities.id.label("entity_glpi_id"))

        if "location" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(self.locations.c.name.label("location"))
            query = query.add_column(
                self.locations.c.completename.label("complete_location")
            )
            query = query.add_column(self.locations.c.id.label("location_glpi_id"))
        if "model" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(self.model.c.name.label("model"))

        if "manufacturer" in self.config.summary or idmachine != "" or uuidsetup != "":
            query = query.add_column(self.manufacturers.c.name.label("manufacturer"))
        if idmachine != "" or uuidsetup != "":
            list_column_add_for_info = [
                "id",
                "entities_id",
                "name",
                "serial",
                "otherserial",
                "contact",
                "contact_num",
                "users_id_tech",
                "groups_id_tech",
                "comment",
                "date_mod",
                "autoupdatesystems_id",
                "locations_id",
                "domains_id",
                "networks_id",
                "computermodels_id",
                "computertypes_id",
                "is_template",
                "template_name",
                "is_deleted",
                "is_dynamic",
                "users_id",
                "groups_id",
                "states_id",
                "ticket_tco",
                "date_creation",
                "is_recursive",
                "operatingsystems_id",
                "operatingsystemversions_id",
                "operatingsystemservicepacks_id",
                "operatingsystemarchitectures_id",
                "license_number",
                "license_id",
                "operatingsystemkernelversions_id",
            ]
            for addcolumn in list_column_add_for_info:
                query = query.add_column(getattr(Machine, addcolumn).label(addcolumn))

        # Don't select deleted or template machines
        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)

        # Select machines from the specified entity
        if location != "":
            listentity = [int(x.strip()) for x in location.split(",")]
            query = query.filter(Entities.id.in_(listentity))

        # Add all the like clauses to find machines containing the criterion
        if criterion != "" and idmachine == "" and uuidsetup == "":
            if field == "":
                query = query.filter(
                    or_(
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
                        self.regcontents.c.value.contains(criterion),
                    )
                )
            else:
                if field == "peripherals":
                    if contains == "notcontains":
                        query = query.filter(not_(Peripherals.name.contains(criterion)))
                    else:
                        query = query.filter(Peripherals.name.contains(criterion))
                else:
                    pass
        if idmachine == "" and uuidsetup == "":
            query = query.order_by(Machine.name)
        query = self.__filter_on(query)

        if idmachine != "":
            query = query.filter(Machine.id == str(idmachine))
        if uuidsetup != "":
            query = query.filter(Machine.uuid == str(uuidsetup))
        count = query.count()

        if idmachine == "" and uuidsetup == "":
            # Then continue with others criterions and filters
            query = query.offset(start).limit(end)

        columns_name = [column["name"] for column in query.column_descriptions]
        machines = query.all()

        # initialisation structure result
        result = {"count": count, "data": {index: [] for index in columns_name}}
        if idmachine == "" and uuidsetup == "":
            result["data"]["presence"] = []

        nb_columns = len(columns_name)
        if idmachine != "" or uuidsetup != "":
            result["data"]["columns_name"] = columns_name
            result["data"]["columns_name_reg"] = list_reg_columns_name

        regs = {reg_column: [] for reg_column in list_reg_columns_name}
        result["data"]["reg"] = regs

        for machine in machines:
            if idmachine == "" and uuidsetup == "":
                result["data"]["presence"].append(
                    1 if machine[0] in online_machines else 0
                )
                for indexcolumn in range(nb_columns):
                    result["data"][columns_name[indexcolumn]].append(
                        machine[indexcolumn]
                    )
            else:
                recordmachinedict = self._machineobjectdymresult(machine, encode="utf8")
                for recordmachine in recordmachinedict:
                    result["data"][recordmachine] = [recordmachinedict[recordmachine]]

            for column in list_reg_columns_name:
                result["data"]["reg"][column].append(None)

        regquery = []
        if list_reg_columns_name:
            regquery = (
                session.query(
                    self.regcontents.c.computers_id,
                    self.regcontents.c.key,
                    self.regcontents.c.value,
                )
                .filter(
                    and_(
                        self.regcontents.c.key.in_(list_reg_columns_name),
                        self.regcontents.c.computers_id.in_(result["data"]["uuid"]),
                    )
                )
                .all()
            )
        for reg in regquery:
            index = result["data"]["uuid"].index(reg[0])
            result["data"]["reg"][reg[1]][index] = reg[2]

        result["count"] = count

        uuids = []
        for id in result["data"]["uuid"]:
            uuids.append("UUID%s" % id)
        if idmachine == "" and uuidsetup == "":
            result["xmppdata"] = []
            result["xmppdata"] = XmppMasterDatabase().getmachinesbyuuids(uuids)
        if idmachine != "" or uuidsetup != "":
            result["data"]["uuidglpicomputer"] = result["data"].pop("uuid")
        return result

    def __getRestrictedComputersListQuery(
        self, ctx, filt=None, session=create_session(), displayList=False, count=False
    ):
        """
        Get the sqlalchemy query to get a list of computers with some filters
        If displayList is True, we are displaying computers list
        """
        if session == None:
            session = create_session()

        query = (
            count and session.query(func.count(Machine.id.distinct()))
        ) or session.query(Machine)
        # manage criterion  for xmppmaster
        ret = self.__xmppmasterfilter(filt)

        if filt:
            # filtering on query
            join_query = self.machine

            if displayList and not count:
                if "os" in self.config.summary:
                    query = query.add_column(self.os.c.name)
                if "type" in self.config.summary:
                    query = query.add_column(self.glpi_computertypes.c.name)
                if "inventorynumber" in self.config.summary:
                    query = query.add_column(self.machine.c.otherserial)
                if "state" in self.config.summary:
                    query = query.add_column(self.state.c.name)
                if "entity" in self.config.summary:
                    query = query.add_column(self.entities.c.name)  # entities
                if "location" in self.config.summary:
                    query = query.add_column(self.locations.c.name)  # locations
                if "model" in self.config.summary:
                    query = query.add_column(self.glpi_computermodels.c.name)
                if "manufacturer" in self.config.summary:
                    query = query.add_column(self.manufacturers.c.name)
                if "owner_firstname" in self.config.summary:
                    query = query.add_column(self.user.c.firstname)
                if "owner_realname" in self.config.summary:
                    query = query.add_column(self.user.c.realname)
                if "owner" in self.config.summary:
                    query = query.add_column(self.user.c.name)

            query_filter = None

            filters = [
                self.machine.c.is_deleted == 0,
                self.machine.c.is_template == 0,
                self.__filter_on_filter(query),
                self.__filter_on_entity_filter(query, ctx),
            ]

            join_query, query_filter = self.filter(
                ctx,
                self.machine,
                filt,
                session.query(Machine),
                self.machine.c.id,
                filters,
            )

            # filtering on locations
            if "location" in filt:
                location = filt["location"]
                if location == "" or location == "" or not self.displayLocalisationBar:
                    location = None
            else:
                location = None

            # Imaging group
            if "imaging_entities" in filt:
                location = filt["imaging_entities"]

            if "ctxlocation" in filt:
                ctxlocation = filt["ctxlocation"]
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
                        locationids = [int(x.replace("UUID", "")) for x in location]
                        for locationid in locationids:
                            if not locationid in locsid:
                                self.logger.warn(
                                    "User '%s' is trying to get the content of an unauthorized entity : '%s'"
                                    % (ctx.userid, "UUID" + location)
                                )
                                session.close()
                                return None
                        query_filter = self.__addQueryFilter(
                            query_filter, (self.machine.c.entities_id.in_(locationids))
                        )
                    else:
                        locationid = int(location.replace("UUID", ""))
                        if locationid in locsid:
                            query_filter = self.__addQueryFilter(
                                query_filter, (self.machine.c.entities_id == locationid)
                            )
                        else:
                            self.logger.warn(
                                "User '%s' is trying to get the content of an unauthorized entity : '%s'"
                                % (ctx.userid, location)
                            )
                            session.close()
                            return None

            if displayList:
                r = re.compile("reg_key_.*")
                regs = list(filter(r.search, self.config.summary))
                if "os" in self.config.summary:
                    join_query = join_query.outerjoin(self.os)
                if "type" in self.config.summary:
                    join_query = join_query.outerjoin(self.glpi_computertypes)
                if "state" in self.config.summary:
                    join_query = join_query.outerjoin(self.state)
                if "location" in self.config.summary:
                    join_query = join_query.outerjoin(self.locations)
                if "model" in self.config.summary:
                    join_query = join_query.outerjoin(self.glpi_computermodels)
                if "manufacturer" in self.config.summary:
                    join_query = join_query.outerjoin(self.manufacturers)
                if (
                    "owner" in self.config.summary
                    or "owner_firstname" in self.config.summary
                    or "owner_realname" in self.config.summary
                ):
                    join_query = join_query.outerjoin(
                        self.user, self.machine.c.users_id == self.user.c.id
                    )
                try:
                    if regs[0]:
                        join_query = join_query.outerjoin(self.regcontents)
                except IndexError:
                    pass

            if self.fusionagents is not None:
                join_query = join_query.outerjoin(self.fusionagents)
            if "antivirus" in filt:  # Used for Antivirus dashboard
                join_query = join_query.outerjoin(self.fusionantivirus)
                join_query = join_query.outerjoin(self.os)

            if query_filter is None:
                query = query.select_from(join_query)
            else:
                query = query.select_from(join_query).filter(query_filter)
            query = query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
            if PluginManager().isEnabled("xmppmaster"):
                if ret:
                    if "computerpresence" in ret:
                        if ret["computerpresence"][2] == "presence":
                            query = query.filter(
                                Machine.id.in_(ret["computerpresence"][3])
                            )
                        else:
                            query = query.filter(
                                Machine.id.notin_(ret["computerpresence"][3])
                            )
            query = self.__filter_on(query)
            query = self.__filter_on_entity(query, ctx)

            if filt.get("hostname"):
                if displayList:
                    clauses = []
                    # UUID filtering
                    if (
                        filt["hostname"].lower().startswith("uuid")
                        and len(filt["hostname"]) > 3
                    ):
                        try:
                            clauses.append(
                                self.machine.c.id == fromUUID(filt["hostname"])
                            )
                        except:
                            pass
                    if "cn" in self.config.summary:
                        clauses.append(
                            self.machine.c.name.like("%" + filt["hostname"] + "%")
                        )
                    if "os" in self.config.summary:
                        clauses.append(
                            self.os.c.name.like("%" + filt["hostname"] + "%")
                        )
                    if "description" in self.config.summary:
                        clauses.append(
                            self.machine.c.comment.like("%" + filt["hostname"] + "%")
                        )
                    if "type" in self.config.summary:
                        clauses.append(
                            self.glpi_computertypes.c.name.like(
                                "%" + filt["hostname"] + "%"
                            )
                        )
                    if "owner" in self.config.summary:
                        clauses.append(
                            self.user.c.name.like("%" + filt["hostname"] + "%")
                        )
                    if "owner_firstname" in self.config.summary:
                        clauses.append(
                            self.user.c.firstname.like("%" + filt["hostname"] + "%")
                        )
                    if "owner_realname" in self.config.summary:
                        clauses.append(
                            self.user.c.realname.like("%" + filt["hostname"] + "%")
                        )
                    if "user" in self.config.summary:
                        clauses.append(
                            self.machine.c.contact.like("%" + filt["hostname"] + "%")
                        )
                    if "state" in self.config.summary:
                        clauses.append(
                            self.state.c.name.like("%" + filt["hostname"] + "%")
                        )
                    if "inventorynumber" in self.config.summary:
                        clauses.append(
                            self.machine.c.otherserial.like(
                                "%" + filt["hostname"] + "%"
                            )
                        )
                    if "entity" in self.config.summary:
                        clauses.append(
                            self.entities.c.name.like("%" + filt["hostname"] + "%")
                        )
                    if "location" in self.config.summary:
                        clauses.append(
                            self.locations.c.name.like("%" + filt["hostname"] + "%")
                        )
                    if "model" in self.config.summary:
                        clauses.append(
                            self.glpi_computermodels.c.name.like(
                                "%" + filt["hostname"] + "%"
                            )
                        )
                    if "manufacturer" in self.config.summary:
                        clauses.append(
                            self.manufacturers.c.name.like("%" + filt["hostname"] + "%")
                        )
                    r = re.compile("reg_key_.*")
                    regs = list(filter(r.search, self.config.summary))
                    try:
                        if regs[0]:
                            clauses.append(
                                self.regcontents.c.value.like(
                                    "%" + filt["hostname"] + "%"
                                )
                            )
                    except IndexError:
                        pass
                    # Filtering on computer list page
                    if clauses:
                        query = query.filter(or_(*clauses))
                else:
                    # filtering on machines (name or uuid)
                    query = query.filter(
                        self.machine.c.name.like("%" + filt["hostname"] + "%")
                    )
            if "name" in filt:
                query = query.filter(self.machine.c.name.like("%" + filt["name"] + "%"))

            if "filter" in filt:  # Used with search field of static group creation
                query = query.filter(
                    self.machine.c.name.like("%" + filt["filter"] + "%")
                )

            if "uuid" in filt:
                query = self.filterOnUUID(query, filt["uuid"])

            if (
                "uuids" in filt
                and type(filt["uuids"]) == list
                and len(filt["uuids"]) > 0
            ):
                query = self.filterOnUUID(query, filt["uuids"])

            if "gid" in filt:
                gid = filt["gid"]
                machines = []
                if ComputerGroupManager().isrequest_group(ctx, gid):
                    machines = [
                        fromUUID(m)
                        for m in ComputerGroupManager().requestresult_group(
                            ctx, gid, 0, -1, ""
                        )
                    ]
                else:
                    machines = [
                        fromUUID(m)
                        for m in ComputerGroupManager().result_group(
                            ctx, gid, 0, -1, ""
                        )
                    ]
                query = query.filter(self.machine.c.id.in_(machines))

            if "request" in filt:
                request = filt["request"]
                if request != "EMPTY":
                    bool = None
                    if "equ_bool" in filt:
                        bool = filt["equ_bool"]
                    machines = [
                        fromUUID(m)
                        for m in ComputerGroupManager().request(
                            ctx, request, bool, 0, -1, ""
                        )
                    ]
                    query = query.filter(self.machine.c.id.in_(machines))

            if "date" in filt:
                state = filt["date"]["states"]
                date_mod = filt["date"]["date_mod"]
                value = filt["date"]["value"]

                if "green" in value:
                    query = query.filter(date_mod > state["orange"])
                if "orange" in value:
                    query = query.filter(
                        and_(date_mod < state["orange"], date_mod > state["red"])
                    )
                if "red" in value:
                    query = query.filter(date_mod < state["red"])

            if "antivirus" in filt:
                if filt["antivirus"] == "green":
                    query = query.filter(
                        and_(
                            FusionAntivirus.is_active == 1,
                            FusionAntivirus.is_uptodate == 1,
                            OS.name.ilike("%windows%"),
                            not_(
                                FusionAntivirus.name.in_(self.config.av_false_positive)
                            ),
                        )
                    )
                elif filt["antivirus"] == "orange":
                    query = query.filter(
                        and_(
                            OS.name.ilike("%windows%"),
                            not_(
                                and_(
                                    FusionAntivirus.is_active == 1,
                                    FusionAntivirus.is_uptodate == 1,
                                ),
                            ),
                            not_(
                                FusionAntivirus.name.in_(self.config.av_false_positive)
                            ),
                        )
                    )
                elif filt["antivirus"] == "red":
                    query = query.filter(
                        and_(
                            OS.name.ilike("%windows%"),
                            or_(
                                FusionAntivirus.is_active == None,
                                FusionAntivirus.is_uptodate == None,
                                and_(
                                    FusionAntivirus.name.in_(
                                        self.config.av_false_positive
                                    ),
                                    not_(
                                        FusionAntivirus.computers_id.in_(
                                            self.getMachineIdsNotInAntivirusRed(ctx),
                                        )
                                    ),
                                ),
                            ),
                        )
                    )

        if count:
            query = query.scalar()
        return query

    def __getId(self, obj):
        if type(obj) == dict:
            return obj["uuid"]
        if type(obj) != str and type(obj) != str:
            return obj.id
        return obj

    def __getName(self, obj):
        if type(obj) == dict:
            return obj["name"]
        if type(obj) != str and type(obj) != str:
            return obj.name
        if type(obj) == str and re.match("UUID", obj):
            l = self.getLocation(obj)
            if l:
                return l.name
        return obj

    def __addQueryFilter(self, query_filter, eq):
        if str(query_filter) == str(
            None
        ):  # don't remove the str, sqlalchemy.sql._BinaryExpression == None return True!
            query_filter = eq
        else:
            query_filter = and_(query_filter, eq)
        return query_filter

    def computersTable(self):
        return [self.machine]

    def computersMapping(self, computers, invert=False):
        if not invert:
            return Machine.id.in_([fromUUID(x) for x in computers])
        else:
            return Machine.id.not_(
                ColumnOperators.in_([fromUUID(x) for x in computers])
            )

    def mappingTable(self, ctx, query):
        """
        Map a table name on a table mapping
        """
        base = []
        base.append(self.entities)
        if query[2] == "OS":
            return base + [self.os]
        elif query[2] == "Entity":
            return base
        elif query[2] == "SOFTWARE":
            return base + [self.inst_software, self.licenses, self.software]
        elif query[2] == "Computer name":
            return base
        elif query[2] == "Last Logged User":
            return base
        elif query[2] == "Owner of the machine":
            return base + [self.user]
        elif query[2] == "Contact":
            return base
        elif query[2] == "Contact number":
            return base
        elif query[2] == "Description":
            return base
        elif query[2] == "System model":
            return base + [self.model]
        elif query[2] == "System manufacturer":
            return base + [self.manufacturers]
        elif query[2] == "State":
            return base + [self.state]
        elif query[2] == "System type":
            return base + [self.glpi_computertypes]
        elif query[2] == "Inventory number":
            return base
        elif query[2] == "Location":
            return base + [self.locations]
        elif query[2] == "Operating system":
            return base + [self.os]
        elif query[2] == "Service Pack":
            return base + [self.os_sp]
        elif query[2] == "Architecture":
            return base + [self.os_arch]
        elif query[2] == "Printer name":
            return base + [self.view_computers_items_printer, self.printers]
        elif query[2] == "Printer serial":
            return base + [self.view_computers_items_printer, self.printers]
        elif query[2] == "Peripheral name":
            return base + [self.view_computers_items_peripheral, self.peripherals]
        elif query[2] == "Peripheral serial":
            return base + [self.view_computers_items_peripheral, self.peripherals]
        elif query[2] == "Group":
            return base + [self.group]
        elif query[2] == "Network":
            return base + [self.net]
        elif query[2] == "Installed software":
            return base + [self.inst_software, self.softwareversions, self.software]
        elif query[2] == "Installed software (specific version)":
            return base + [self.inst_software, self.softwareversions, self.software]
        elif (
            query[2] == "Installed software (specific vendor and version)"
        ):  # hidden internal dyngroup
            return base + [
                self.inst_software,
                self.softwareversions,
                self.software,
                self.manufacturers,
            ]
        elif query[2] == "User location":
            return base + [self.user, self.locations]
        elif query[2] == "Register key":
            return base + [self.regcontents]  # self.collects, self.registries,
        elif query[2] == "Register key value":
            return base + [
                self.regcontents,
                self.registries,
            ]  # self.collects, self.registries,
        elif query[2] == "OS Version":
            return base + [self.os_version]
        elif query[2] == "Architecture":
            return base + [self.os_arch]
        return []

    def mapping(self, ctx, query, invert=False):
        """
        Map a name and request parameters on a sqlalchemy request
        """
        if len(query) >= 4:
            # in case the glpi database is in latin1, don't forget dyngroup is in utf8
            # => need to convert what comes from the dyngroup database
            query[3] = self.encode(query[3])
            r1 = re.compile("\*")
            like = False
            if type(query[3]) == list:
                q3 = []
                for q in query[3]:
                    if r1.search(q):
                        like = True
                        q = r1.sub("%", q)
                    q3.append(q)
                query[3] = q3
            else:
                if r1.search(query[3]):
                    like = True
                    query[3] = r1.sub("%", query[3])

            parts = self.__getPartsFromQuery(ctx, query)
            ret = []

            for part in parts:
                partA, partB = part
                partBcanBeNone = partB == "%"
                if invert:
                    if like:
                        if partBcanBeNone:
                            ret.append(
                                not_(
                                    or_(
                                        partA.like(self.encode(partB)),
                                        partA == None,
                                    )
                                )
                            )
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
                                d = int(partB)
                                ret.append(and_(partA >= d))
                            elif partB.startswith("<="):
                                partB = partB[2:].strip()
                                d = int(partB)
                                ret.append(and_(partA <= d))
                            elif partB.startswith("<"):
                                partB = partB[1:].strip()
                                d = int(partB)
                                ret.append(and_(partA < d))
                            elif partB.startswith(">"):
                                partB = partB[1:].strip()
                                d = int(partB)
                                ret.append(and_(partA > d))
                            else:
                                ret.append(partA.like(self.encode(partB)))
                        except Exception as e:
                            print((str(e)))
                            traceback.print_exc(file=sys.stdout)
                            ret.append(partA.like(self.encode(partB)))
            if ctx.userid != "root":
                ret.append(self.__filter_on_entity_filter(None, ctx))
            return and_(*ret)
        else:
            return self.__treatQueryLevel(query)

    def __getPartsFromQuery(self, ctx, query):
        if query[2] in ["OS", "Operating system"]:
            return [[self.os.c.name, query[3]]]
        elif query[2] == "Entity":
            locid = None
            for loc in ctx.locations:
                if self.__getName(loc) == query[3]:
                    locid = self.__getId(loc)
            if locid is not None:
                return [[self.machine.c.entities_id, locid]]
            else:
                return [[self.entities.c.name, query[3]]]
        elif query[2] == "SOFTWARE":
            return [[self.software.c.name, query[3]]]
        elif query[2] == "Computer name":
            return [[self.machine.c.name, query[3]]]
        elif query[2] == "User location":
            return [[self.locations.c.completename, query[3]]]
        elif query[2] == "Contact":
            return [[self.machine.c.contact, query[3]]]
        elif query[2] == "Last Logged User":
            return [[self.machine.c.contact, query[3]]]
        elif query[2] == "Owner of the machine":
            return [[self.user.c.name, query[3]]]
        elif query[2] == "Contact number":
            return [[self.machine.c.contact_num, query[3]]]
        elif query[2] == "Description":
            return [[self.machine.c.comment, query[3]]]
        elif query[2] == "System model":
            return [[self.model.c.name, query[3]]]
        elif query[2] == "System manufacturer":
            return [[self.manufacturers.c.name, query[3]]]
        elif query[2] == "State":
            return [[self.state.c.name, query[3]]]
        elif query[2] == "System type":
            return [[self.glpi_computertypes.c.name, query[3]]]
        elif query[2] == "Inventory number":
            return [[self.machine.c.otherserial, query[3]]]
        elif query[2] == "Location":
            return [[self.locations.c.completename, query[3]]]
        elif query[2] == "Service Pack":
            return [[self.os_sp.c.name, query[3]]]
        elif query[2] == "Architecture":
            return [[self.os_arch.c.name, query[3]]]
        elif query[2] == "Printer name":
            return [[self.printers.c.name, query[3]]]
        elif query[2] == "Printer serial":
            return [[self.printers.c.serial, query[3]]]
        elif query[2] == "Peripheral name":
            return [[self.peripherals.c.name, query[3]]]
        elif query[2] == "Peripheral serial":
            return [[self.peripherals.c.serial, query[3]]]
        elif query[2] == "Group":  # TODO double join on Entity
            return [[self.group.c.name, query[3]]]
        elif query[2] == "Network":
            return [[self.net.c.name, query[3]]]
        elif query[2] == "Installed software":  # TODO double join on Entity
            return [[self.software.c.name, query[3]]]
        elif (
            query[2] == "Installed software (specific version)"
        ):  # TODO double join on Entity
            return [
                [self.software.c.name, query[3][0]],
                [self.softwareversions.c.name, query[3][1]],
            ]
        elif (
            query[2] == "Installed software (specific vendor and version)"
        ):  # hidden internal dyngroup
            return [
                [self.manufacturers.c.name, query[3][0]],
                [self.software.c.name, query[3][1]],
                [self.softwareversions.c.name, query[3][2]],
            ]
        elif query[2] == "Register key":
            return [[self.registries.c.name, query[3]]]
        elif query[2] == "Register key value":
            return [
                [self.registries.c.name, query[3][0]],
                [self.regcontents.c.value, query[3][1]],
            ]
        elif query[2] == "OS Version":
            return [[self.os_version.c.name, query[3]]]
        elif query[2] == "Architecture":
            return [[self.os_arch.c.name, query[3]]]
        return []

    def __getTable(self, table):
        if table == "OS":
            return self.os.c.name
        elif table == "Entity":
            return self.entities.c.name
        elif table == "SOFTWARE":
            return self.software.c.name
        raise Exception("dont know table for %s" % (table))

    ##################### machine list management
    def getComputer(self, ctx, filt, empty_macs=False):
        """
        Get the first computers that match filters parameters
        """
        ret = self.getRestrictedComputersList(
            ctx, 0, 10, filt, displayList=False, empty_macs=empty_macs
        )
        if len(ret) != 1:
            for i in ["location", "ctxlocation"]:
                try:
                    filt.pop(i)
                except:
                    pass
            ret = self.getRestrictedComputersList(
                ctx, 0, 10, filt, displayList=False, empty_macs=empty_macs
            )
            if len(ret) > 0:
                raise Exception("NOPERM##%s" % (ret[0][1]["fullname"]))
            return False
        return list(ret.values())[0]

    def getRestrictedComputersListStatesLen(self, ctx, filt, orange, red):
        """
        Return number of computers by state
        """
        session = create_session()
        now = datetime.datetime.now()
        states = {
            "orange": now - datetime.timedelta(orange),
            "red": now - datetime.timedelta(red),
        }

        date_mod = self.machine.c.date_mod
        if self.fusionagents is not None:
            date_mod = FusionAgents.last_contact

        for value in ["green", "orange", "red"]:
            # This loop instanciate self.filt_green,
            # self.filt_orange and self.filt_red
            setattr(self, "filt_%s" % value, filt.copy())

            newFilter = getattr(self, "filt_%s" % value)
            values = {
                "states": states,
                "date_mod": date_mod,
                "value": value,
            }
            newFilter["date"] = values

        ret = {
            "green": int(
                self.__getRestrictedComputersListQuery(
                    ctx, self.filt_green, session, count=True
                )
            ),
            "orange": int(
                self.__getRestrictedComputersListQuery(
                    ctx, self.filt_orange, session, count=True
                )
            ),
            "red": int(
                self.__getRestrictedComputersListQuery(
                    ctx, self.filt_red, session, count=True
                )
            ),
        }
        session.close()
        return ret

    def getRestrictedComputersListLen(self, ctx, filt=None):
        """
        Get the size of the computer list that match filters parameters
        """
        session = create_session()

        displayList = None

        # When search field is used on main computer's list page,
        # Pagination PHP Widget must know total machine result
        # So, set displayList to True to count on glpi_computers_pulse
        # and all needed joined tables
        if "hostname" in filt:
            if len(filt["hostname"]) > 0:
                displayList = True

        ret = self.__getRestrictedComputersListQuery(
            ctx, filt, session, displayList, count=True
        )
        if ret == None:
            return 0
        session.close()
        return ret

    def getMachineforentityList(self, min=0, max=-1, filt=None):
        """
        Get the computer list that match filters entity parameters between min and max

        FIXME: may return a list or a dict according to the parameters

        eg. dict filt param {'fk_entity': 1, 'imaging_server': 'UUID1', 'get': ['cn', 'objectUUID']}
        """
        if (
            filt
            and "imaging_server" in filt
            and filt["imaging_server"] != ""
            and "get" in filt
            and len(filt["get"]) == 2
            and filt["get"][0] == "cn"
            and filt["get"][1] == "objectUUID"
            and "fk_entity" in filt
            and filt["fk_entity"] != -1
        ):
            # recherche entity parent.
            entitylist = self.getEntitiesParentsAsList([filt["fk_entity"]])
            session = create_session()
            entitylist.append(filt["fk_entity"])
            q = (
                session.query(
                    Machine.id, Machine.name, Machine.entities_id, Machine.locations_id
                )
                .add_column(self.entities.c.name.label("Entity_name"))
                .select_from(self.machine.join(self.entities))
                .filter(self.machine.c.entities_id.in_(entitylist))
                .filter(self.machine.c.is_deleted == 0)
                .filter(self.machine.c.is_template == 0)
            )
            ret = q.all()
            listentitymachine = {}
            for line in ret:
                uuid = "UUID%s" % line.id
                listentitymachine[uuid] = {"cn": line.name, "objectUUID": uuid}
            session.close()
            return listentitymachine

    def getRestrictedComputersList(
        self,
        ctx,
        min=0,
        max=-1,
        filt=None,
        advanced=True,
        justId=False,
        toH=False,
        displayList=None,
        empty_macs=False,
    ):
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
            if (
                justId or toH or "uuid" in filt
            ):  # if 'uuid' in filt: used where adding a command to a group
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
            ret = [self.getMachineUUID(m) for m in query.all()]
        elif toH:
            ret = [m.toH() for m in query.all()]
        else:
            if filt is not None and "get" in filt:
                ret = self.__formatMachines(
                    query.all(), advanced, filt["get"], empty_macs=empty_macs
                )
            else:
                ret = self.__formatMachines(
                    query.all(), advanced, None, empty_macs=empty_macs
                )
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
        return [
            {"uuid": toUUID(str(machine.id)), "hostname": machine.name}
            for machine in query
        ]

    def getTotalComputerCount(self):
        session = create_session()
        query = session.query(Machine)
        query = self.__filter_on(query)
        c = query.count()
        session.close()
        return c

    def getComputerCount(self, ctx, filt=None):
        """
        Same as getRestrictedComputersListLen
        TODO : remove this one
        """
        return self.getRestrictedComputersListLen(ctx, filt)

    def getComputersList(self, ctx, filt=None):
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
        ret = session.query(Machine).filter(
            self.machine.c.id == int(str(uuid).replace("UUID", ""))
        )
        ret = ret.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        ret = self.__filter_on(ret).first()
        session.close()
        return ret

    def filterOnUUID(self, query, uuid):
        """
        Modify the given query to filter on the machine UUID
        """
        if type(uuid) == list:
            return query.filter(
                self.machine.c.id.in_([int(str(a).split("UUID")[-1]) for a in uuid])
            )
        else:
            if uuid is None:
                uuid = ""
            return query.filter(self.machine.c.id == int(str(uuid).split("UUID")[-1]))

    ##################### Machine output format (for ldap compatibility)
    def __getAttr(self, machine, get):
        ma = {}
        for field in get:
            if hasattr(machine, field):
                ma[field] = getattr(machine, field)
            if field == "uuid" or field == "objectUUID":
                ma[field] = toUUID(str(machine.id))
            if field == "cn":
                ma[field] = machine.name
        return ma

    def __formatMachines(self, machines, advanced, get=None, empty_macs=False):
        """
        Give an LDAP like version of machines
        """
        ret = {}
        if get != None:
            for m in machines:
                m = m[0] if isinstance(m, (tuple, Row)) else m
                ret[m.getUUID()] = self.__getAttr(m, get)
            return ret

        names = {}
        for m in machines:
            displayList = False
            if isinstance(m, (tuple, Row)):
                displayList = True
                # List of fields defined around line 439
                # m, os, type, inventorynumber, state, entity, location, model, manufacturer, owner = m
                l = list(m)
                if "owner" in self.config.summary:
                    owner_login = l.pop()
                if "owner_firstname" in self.config.summary:
                    owner_firstname = l.pop()
                if "owner_realname" in self.config.summary:
                    owner_realname = l.pop()
                if "manufacturer" in self.config.summary:
                    manufacturer = l.pop()
                if "model" in self.config.summary:
                    model = l.pop()
                if "location" in self.config.summary:
                    location = l.pop()
                if "entity" in self.config.summary:
                    entity = l.pop()
                if "state" in self.config.summary:
                    state = l.pop()
                if "inventorynumber" in self.config.summary:
                    inventorynumber = l.pop()
                if "type" in self.config.summary:
                    type = l.pop()
                if "os" in self.config.summary:
                    oslocal = l.pop()

                m = l.pop()
            if isinstance(m, (tuple, Row)):
                m = m[0]
            owner_login, owner_firstname, owner_realname = self.getMachineOwner(m)
            datas = {
                "cn": m.name not in ["", None] and [m.name] or ["(%s)" % m.id],
                "displayName": [m.comment],
                "objectUUID": [m.getUUID()],
                "user": [m.contact],
                "owner": [owner_login],
                "owner_realname": [owner_realname],
                "owner_firstname": [owner_firstname],
            }

            if displayList:
                if "manufacturer" in self.config.summary:
                    datas["manufacturer"] = manufacturer
                if "model" in self.config.summary:
                    datas["model"] = model
                if "location" in self.config.summary:
                    datas["location"] = location
                if "entity" in self.config.summary:
                    datas["entity"] = entity
                if "state" in self.config.summary:
                    datas["state"] = state
                if "inventorynumber" in self.config.summary:
                    datas["inventorynumber"] = inventorynumber
                if "type" in self.config.summary:
                    datas["type"] = type
                if "os" in self.config.summary:
                    datas["os"] = oslocal
                if "owner" in self.config.summary:
                    datas["owner"] = owner_login
                if "owner_firstname" in self.config.summary:
                    datas["owner_firstname"] = owner_firstname
                if "owner_realname" in self.config.summary:
                    datas["owner_realname"] = owner_realname
                master_config = xmppMasterConfig()
                regvalue = []
                r = re.compile(r"reg_key_.*")
                regs = list(filter(r.search, self.config.summary))
                for regkey in regs:
                    regkeyconf = (
                        getattr(master_config, regkey).split("|")[0].split("\\")[-1]
                    )
                    try:
                        keyname, keyvalue = self.getMachineRegistryKey(m, regkeyconf)
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
                    (
                        ret[uuid][1]["macAddress"],
                        ret[uuid][1]["ipHostNumber"],
                        ret[uuid][1]["subnetMask"],
                        ret[uuid][1]["domain"],
                        ret[uuid][1]["networkUuids"],
                    ) = self.orderIpAdresses(
                        uuid, names[uuid], nets[uuid], empty_macs=empty_macs
                    )
                    if ret[uuid][1]["domain"] != "" and len(ret[uuid][1]["domain"]) > 0:
                        ret[uuid][1]["fullname"] = (
                            ret[uuid][1]["cn"][0] + "." + ret[uuid][1]["domain"][0]
                        )
                    else:
                        ret[uuid][1]["fullname"] = ret[uuid][1]["cn"][0]
                except KeyError:
                    ret[uuid][1]["macAddress"] = []
                    ret[uuid][1]["ipHostNumber"] = []
                    ret[uuid][1]["subnetMask"] = []
                    ret[uuid][1]["domain"] = ""
                    ret[uuid][1]["fullname"] = ret[uuid][1]["cn"][0]
        return ret

    def __formatMachine(self, machine, advanced, get=None):
        """
        Give an LDAP like version of the machine
        """

        uuid = self.getMachineUUID(machine)

        if get != None:
            return self.__getAttr(machine, get)

        ret = {
            "cn": [machine.name],
            "displayName": [machine.comment],
            "objectUUID": [uuid],
        }
        if advanced:
            (
                ret["macAddress"],
                ret["ipHostNumber"],
                ret["subnetMask"],
                domain,
                ret["networkUuids"],
            ) = self.orderIpAdresses(uuid, machine.name, self.getMachineNetwork(uuid))
            if domain == None:
                domain = ""
            elif domain != "":
                domain = "." + domain
            ret["fullname"] = machine.name + domain
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

        @return: owner (glpi_computers_pulse.user_id -> name)
        @rtype: str
        """

        ret = None, None, None
        session = create_session()
        machine = machine[0] if isinstance(machine, (tuple, Row)) else machine
        query = session.query(User).select_from(self.user.join(self.machine))
        query = query.filter(self.machine.c.id == machine.id).first()
        if query is not None:
            ret = query.name, query.firstname, query.realname

        session.close()
        return ret

    def getUserProfile(self, user):
        """
        @return: Return the first user GLPI profile as a string, or None
        """
        session = create_session()
        qprofile = (
            session.query(Profile)
            .select_from(self.profile.join(self.userprofile).join(self.user))
            .filter(self.user.c.name == user)
            .first()
        )
        if qprofile == None:
            ret = None
        else:
            ret = qprofile.name
        session.close()
        return ret

    def getUserProfiles(self, user):
        """
        @return: Return all user GLPI profiles as a list of string, or None
        """
        session = create_session()
        profiles = (
            session.query(Profile)
            .select_from(self.profile.join(self.userprofile).join(self.user))
            .filter(self.user.c.name == user)
        )
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
        qentities = (
            session.query(Entities)
            .select_from(self.entities.join(self.userprofile).join(self.user))
            .filter(self.user.c.name == user)
            .first()
        )
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
        if user == "root":
            ret = self.__get_all_locations()
        else:
            # check if user is linked to the root entity
            # (which is not declared explicitly in glpi...
            # we have to emulate it...)
            session = create_session()
            entids = (
                session.query(UserProfile)
                .select_from(self.userprofile.join(self.user).join(self.profile))
                .filter(self.user.c.name == user)
                .filter(self.profile.c.name.in_(self.config.activeProfiles))
                .all()
            )
            for entid in entids:
                if entid.entities_id == 0 and entid.is_recursive == 1:
                    session.close()
                    return self.__get_all_locations()

            # the normal case...
            plocs = (
                session.query(Entities)
                .add_column(self.userprofile.c.is_recursive)
                .select_from(
                    self.entities.join(self.userprofile)
                    .join(self.user)
                    .join(self.profile)
                )
                .filter(self.user.c.name == user)
                .filter(self.profile.c.name.in_(self.config.activeProfiles))
                .all()
            )
            for ploc in plocs:
                if ploc[1]:
                    # The user profile link to the entities is recursive, and so
                    # the children locations should be added too
                    for l in self.__add_children(ploc[0]):
                        ret.append(l)
                else:
                    ret.append(ploc[0])
            if len(ret) == 0:
                ret = []
            session.close()

        ret = [setUUID(l) for l in ret]
        return ret

    def __get_all_locations(self):
        ret = []
        session = create_session()
        q = (
            session.query(Entities)
            .group_by(self.entities.c.completename)
            .order_by(asc(self.entities.c.completename))
            .all()
        )
        session.close()
        for entities in q:
            ret.append(entities)
        return ret

    def __add_children(self, child):
        """
        Recursive function used by getUserLocations to get entities tree if needed
        """
        session = create_session()
        children = (
            session.query(Entities)
            .filter(self.entities.c.entities_id == child.id)
            .all()
        )
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
        ret = (
            session.query(Entities)
            .filter(self.entities.c.id == uuid.replace("UUID", ""))
            .first()
        )
        session.close()
        return ret

    def getLocationName(self, uuid):
        if isinstance(uuid, list):
            uuid = uuid[0]

        return self.getLocation(uuid).name

    def getLocationsList(self, ctx, filt=None):
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
        q = (
            session.query(
                Entities.id,
                Entities.name,
                Entities.completename,
                Entities.comment,
                Entities.level,
            )
            .add_column(self.machine.c.id)
            .select_from(self.entities.join(self.machine))
            .filter(self.machine.c.id.in_(list(map(fromUUID, machine_uuids))))
            .all()
        )
        ret = {}
        for idp, namep, namepc, commentp, levelp, machineid in q:
            val = {}
            val["uuid"] = toUUID(idp)
            val["name"] = namep
            val["completename"] = namepc
            val["comments"] = commentp
            val["level"] = levelp
            ret[toUUID(machineid)] = val
        session.close()
        return ret

    def getUsersInSameLocations(self, userid, locations=None):
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
            q = (
                session.query(User)
                .select_from(self.user.join(self.userprofile).join(self.entities))
                .filter(self.entities.c.name.in_(inloc))
                .filter(self.user.c.name != userid)
                .distinct()
                .all()
            )
            session.close()
            # Only returns the user names
            ret = [u.name for u in q]
        # Always append the given userid
        ret.append(userid)
        return ret

    def getComputerInLocation(self, location=None):
        """
        Get all computers in that location
        """
        session = create_session()
        query = (
            session.query(Machine)
            .select_from(self.machine.join(self.entities))
            .filter(self.entities.c.name == location)
        )
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        ret = []
        for machine in query.group_by(self.machine.c.name).order_by(
            asc(self.machine.c.name)
        ):
            ret[machine.name] = self.__formatMachine(machine)
        session.close()
        return ret

    def getLocationsFromPathString(self, location_path):
        """ """
        session = create_session()
        ens = []
        for loc_path in location_path:
            loc_path = " > ".join(loc_path)
            q = (
                session.query(Entities)
                .filter(self.entities.c.completename == loc_path)
                .all()
            )
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
        if parent_id == -1:  # parent_id is -1 for root entity
            parent_id = 0

        while parent_id != 0:
            en_id = parent_id
            en = session.query(Entities).filter(self.entities.c.id == parent_id).first()
            path.append(toUUID(en.id))
            parent_id = en.entities_id
        path.append("UUID0")
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

        ret = None
        session = create_session()

        query = (
            session.query(RegContents)
            .add_column(self.registries.c.name)
            .add_column(self.regcontents.c.key)
            .add_column(self.regcontents.c.value)
            .select_from(
                self.machine.outerjoin(self.regcontents).outerjoin(self.registries)
            )
        )
        query = query.filter(
            self.machine.c.id == machine.id, self.regcontents.c.key == regkey
        )

        if query.first() is not None:
            ret = query.first().name, query.first().value

        session.close()
        return ret

    def doesUserHaveAccessToMachines(self, ctx, a_machine_uuid, all=True):
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
            a_locations = [loc.name for loc in ctx.locations]
            query = query.select_from(self.machine.join(self.entities))
            query = query.filter(self.entities.c.name.in_(a_locations))
            query = self.filterOnUUID(query, a_machine_uuid)
        ret = query.group_by(self.machine.c.id).all()
        # get the number of computers that had not been deleted
        machines_uuid_size = len(a_machine_uuid)
        all_computers = session.query(Machine)
        all_computers = self.filterOnUUID(all_computers, a_machine_uuid).all()
        all_computers = set([toUUID(str(m.id)) for m in all_computers])
        if len(all_computers) != machines_uuid_size:
            self.logger.info(
                "some machines have been deleted since that list was generated (%s)"
                % (str(set(a_machine_uuid) - all_computers))
            )
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
        ret = set([toUUID(str(m.id)) for m in ret])
        self.logger.info(
            "dont have permissions on %s" % (str(set(a_machine_uuid) - ret))
        )
        return False

    def doesUserHaveAccessToMachine(self, ctx, machine_uuid):
        """
        Check if the user has correct permissions to access this machine

        @rtype: bool
        """
        return self.doesUserHaveAccessToMachines(ctx, [machine_uuid])

    def getMachineInfoImaging(self, uuid):
        """
        Récupère les informations d'inventaire détaillées pour une ou plusieurs machines.

        Paramètre :
        -----------
        uuid : int, str ou list
            UUID unique (int ou str) ou liste d'UUIDs (int ou str) à interroger.
            Les chaînes peuvent être préfixées par "uuid" (insensible à la casse) ou contenir d'autres mots,
            seuls les chiffres extraits seront conservés.

        Retour :
        --------
        list[dict] ou dict
            Liste de dictionnaires contenant les données d'inventaire formatées,
            ou un seul dictionnaire si un seul UUID est fourni.
        """

        def extract_id(value):
            """
            Extrait un entier à partir d'une chaîne ou d'un entier.
            Ignore les préfixes 'uuid' insensibles à la casse, supprime tout sauf chiffres.
            Renvoie None si impossible.
            """
            if value is None:
                return None
            s = str(value).strip()
            if not s:
                return None
            # Retirer le préfixe 'uuid' si présent
            s = re.sub(r"(?i)^uuid", "", s).strip()
            # Extraire la première séquence de chiffres dans la chaîne
            match = re.search(r"\d+", s)
            if match:
                return int(match.group())
            else:
                return None

        uuids_set = set()
        return_single = False

        if isinstance(uuid, int):
            uuids_set.add(uuid)
            return_single = True

        elif isinstance(uuid, str):
            extracted = extract_id(uuid)
            if extracted is not None:
                uuids_set.add(extracted)
                return_single = True
            else:
                self.logger.warning(f"UUID invalide ou vide ignoré : '{uuid}'")
                return []

        elif isinstance(uuid, list):
            for element in uuid:
                extracted = extract_id(element)
                if extracted is not None:
                    uuids_set.add(extracted)
                else:
                    self.logger.warning(f"UUID mal formé ignoré : '{element}'")
            if not uuids_set:
                self.logger.warning("Aucun UUID valide trouvé dans la liste fournie.")
                return []
            return_single = False

        else:
            self.logger.error(f"uuid doit être un int, str ou liste : reçu {type(uuid)}")
            return []

        uuids = list(uuids_set)

        session = create_session()

        query = (
            session.query(Machine)
            .add_columns(
                self.glpi_operatingsystems.c.name.label("os"),
                self.glpi_operatingsystemservicepacks.c.name.label("os_sp"),
                self.glpi_operatingsystemversions.c.name.label("os_version"),
                self.glpi_domains.c.name.label("domain"),
                self.locations.c.name.label("location"),
                self.glpi_computermodels.c.name.label("model"),
                self.glpi_computertypes.c.name.label("type"),
                self.glpi_networks.c.name.label("network"),
                self.entities.c.completename.label("entity"),
                self.glpi_operatingsystemarchitectures.c.name.label("os_arch")
            )
            .select_from(
                self.machine
                .outerjoin(self.glpi_operatingsystems)
                .outerjoin(self.glpi_operatingsystemservicepacks)
                .outerjoin(self.glpi_operatingsystemversions)
                .outerjoin(self.glpi_operatingsystemarchitectures)
                .outerjoin(self.glpi_computertypes)
                .outerjoin(self.glpi_domains)
                .outerjoin(self.locations)
                .outerjoin(self.glpi_computermodels)
                .outerjoin(self.glpi_networks)
                .join(self.entities)
            )
        )

        query = self.filterOnUUID(query, uuids)
        rows = query.all()

        result = []
        for row in rows:
            machine = row[0]
            extra_values = row[1:]
            extra_keys = [
                "os", "os_sp", "os_version", "domain", "location",
                "model", "type", "network", "entity", "os_arch"
            ]

            extra_data = dict(zip(extra_keys, extra_values))

            formatted_result_dict = {
                "id_machine": machine.id,
                "entities": machine.entities_id,
                "realname": machine.name,
                "creationEntity": extra_data.get("entity"),
                "newlocation": extra_data.get("location"),
                "Domain": extra_data.get("domain"),
                "Model": extra_data.get("model"),
                "type": extra_data.get("type"),
                "OperatingSystem": extra_data.get("os"),
                "OperatingSystemSP": extra_data.get("os_sp"),
                "OperatingSystemVersion": extra_data.get("os_version"),
                "OperatingSystemArchitecture": extra_data.get("os_arch"),
                "Network": extra_data.get("network"),
            }

            result.append(formatted_result_dict)

        session.close()

        return result[0] if return_single and result else result

    ##################### for inventory purpose (use the same API than OCSinventory to keep the same GUI)
    def getLastMachineInventoryFull(self, uuid):
        session = create_session()
        # there is glpi_entreprise missing
        query = self.filterOnUUID(
            session.query(Machine)
            .add_column(self.glpi_operatingsystems.c.name)
            .add_column(self.glpi_operatingsystemservicepacks.c.name)
            .add_column(self.glpi_operatingsystemversions.c.name)
            .add_column(self.glpi_domains.c.name)
            .add_column(self.locations.c.name)
            .add_column(self.glpi_computermodels.c.name)
            .add_column(self.glpi_computertypes.c.name)
            .add_column(self.glpi_networks.c.name)
            .add_column(self.entities.c.completename)
            .add_column(self.glpi_operatingsystemarchitectures.c.name)
            .select_from(
                self.machine.outerjoin(self.glpi_operatingsystems)
                .outerjoin(self.glpi_operatingsystemservicepacks)
                .outerjoin(self.glpi_operatingsystemversions)
                .outerjoin(self.glpi_operatingsystemarchitectures)
                .outerjoin(self.glpi_computertypes)
                .outerjoin(self.glpi_domains)
                .outerjoin(self.locations)
                .outerjoin(self.glpi_computermodels)
                .outerjoin(self.glpi_networks)
                .join(self.entities)
            ),
            uuid,
        ).all()
        ret = []
        ind = {
            "os": 1,
            "os_sp": 2,
            "os_version": 3,
            "type": 7,
            "domain": 4,
            "location": 5,
            "model": 6,
            "network": 8,
            "entity": 9,
            "os_arch": 10,
        }  # 'entreprise':9
        for m in query:
            ma1 = m[0].to_a()
            ma2 = []
            for x, y in ma1:
                if x in list(ind.keys()):
                    ma2.append([x, m[ind[x]]])
                else:
                    ma2.append([x, y])
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
            year = int(sourcedate.year + month / 12)
            month = month % 12 + 1
            day = min(sourcedate.day, calendar.monthrange(year, month)[1])
            return datetime.date(year, month, day)

        if infocoms is not None and infocoms.warranty_date is not None:
            endDate = add_months(infocoms.warranty_date, infocoms.warranty_duration)
            if datetime.datetime.now().date() > endDate:
                return (
                    '<span style="color:red;font-weight: bold;">%s</span>'
                    % endDate.strftime("%Y-%m-%d")
                )
            else:
                return endDate.strftime("%Y-%m-%d")

        return ""

    def getManufacturerWarranty(self, manufacturer, serial):
        for manufacturer_key, manufacturer_infos in list(
            self.config.manufacturerWarranty.items()
        ):
            if manufacturer in manufacturer_infos["names"]:
                manufacturer_info = manufacturer_infos.copy()
                manufacturer_info["url"] = manufacturer_info["url"].replace(
                    "@@SERIAL@@", serial
                )
                manufacturer_info["params"] = manufacturer_info["params"].replace(
                    "@@SERIAL@@", serial
                )
                return manufacturer_info
        return False

    def getSearchOptionId(self, filter, lang="en_US"):
        """
        return a list of ids corresponding to filter
        @param filter: a value to search
        @type filter: string
        """

        ids = []
        dict = self.searchOptions[lang]
        for key, value in dict.items():
            if filter.lower() in value.lower():
                ids.append(key)

        return ids

    def getLinkedActionKey(self, filter, lang="en_US"):
        """
        return a list of ids corresponding to filter
        """
        ids = []
        dict = self.getLinkedActions()
        for key, value in dict.items():
            if filter.lower() in value.lower():
                ids.append(key)

        return ids

    def countLastMachineInventoryPart(self, uuid, part, filt=None, options={}):
        # Mutable dict options used as default argument to a method or function
        return self.getLastMachineInventoryPart(
            uuid, part, filt=filt, options=options, count=True
        )

    @property
    def _network_types(self):
        """
        Dict with GLPI available Network types
        """
        return {
            "NetworkPortLocal": "Local",
            "NetworkPortEthernet": "Ethernet",
            "NetworkPortWifi": "Wifi",
            "NetworkPortDialup": "Dialup",
            "NetworkPortAggregate": "Aggregate",
            "NetworkPortAlias": "Alias",
        }

    def _get_network_type(self, instantiation_type):
        """
        Return human readable glpi network type for given instantiation_type
        If not found, return instantiation_type
        """
        if instantiation_type in self._network_types:
            return self._network_types[instantiation_type]
        return instantiation_type

    def getLastMachineNetworkPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
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
                        ipaddresses = list(
                            set(
                                [
                                    ip.name
                                    for ip in networkport.networknames.ipaddresses
                                    if ip.name != ""
                                ]
                            )
                        )
                        gateways = []
                        netmasks = []
                        for ip in networkport.networknames.ipaddresses:
                            gateways += [
                                ipnetwork.gateway
                                for ipnetwork in ip.ipnetworks
                                if ipnetwork.gateway not in ["", "0.0.0.0"]
                            ]
                            netmasks += [
                                ipnetwork.netmask
                                for ipnetwork in ip.ipnetworks
                                if ipnetwork.netmask not in ["", "0.0.0.0"]
                            ]
                        gateways = list(set(gateways))
                        netmasks = list(set(netmasks))
                    l = [
                        ["Name", networkport.name],
                        [
                            "Network Type",
                            self._get_network_type(networkport.instantiation_type),
                        ],
                        ["MAC Address", networkport.mac],
                        ["IP", " / ".join(ipaddresses)],
                        ["Netmask", " / ".join(netmasks)],
                        ["Gateway", " / ".join(gateways)],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineStoragePart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        query = self.filterOnUUID(
            session.query(Disk)
            .add_column(self.diskfs.c.name)
            .select_from(self.machine.outerjoin(self.disk).outerjoin(self.diskfs)),
            uuid,
        )
        if count:
            ret = query.count()
        else:
            ret = []
            for disk, diskfs in query:
                if diskfs not in ["rootfs", "tmpfs", "devtmpfs"]:
                    if disk is not None:
                        l = [
                            ["Name", disk.name],
                            ["Device", disk.device],
                            ["Mount Point", disk.mountpoint],
                            ["Filesystem", diskfs],
                            [
                                "Size",
                                disk.totalsize and str(disk.totalsize) + " MB" or "",
                            ],
                            [
                                "Free Size",
                                disk.freesize and str(disk.freesize) + " MB" or "",
                            ],
                        ]
                        ret.append(l)
        return ret

    def getLastMachineAdministrativePart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        query = self.filterOnUUID(
            session.query(Infocoms)
            .add_column(self.suppliers.c.name)
            .select_from(
                self.machine.outerjoin(self.infocoms).outerjoin(self.suppliers)
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for infocoms, supplierName in query:
                if infocoms is not None:
                    endDate = self.getWarrantyEndDate(infocoms)
                    dateOfPurchase = ""
                    if infocoms.buy_date is not None:
                        dateOfPurchase = infocoms.buy_date.strftime("%Y-%m-%d")

                    l = [
                        ["Supplier", supplierName],
                        ["Invoice Number", infocoms.bill],
                        ["Date Of Purchase", dateOfPurchase],
                        ["Warranty End Date", endDate],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineAntivirusPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        if (
            self.fusionantivirus is None
        ):  # glpi_plugin_fusinvinventory_antivirus doesn't exists
            return []

        query = self.filterOnUUID(
            session.query(FusionAntivirus)
            .add_column(self.manufacturers.c.name)
            .select_from(
                self.machine.outerjoin(self.fusionantivirus).outerjoin(
                    self.manufacturers
                )
            ),
            uuid,
        )

        def __getAntivirusName(manufacturerName, antivirusName):
            """
            Return complete antivirus name (manufacturer + antivirus name)
            if antivirus name is a false positive, display it in bracket
            """
            if antivirusName in self.config.av_false_positive:
                antivirusName += "@@FALSE_POSITIVE@@"

            return (
                manufacturerName
                and " ".join([manufacturerName, antivirusName])
                or antivirusName
            )

        if count:
            ret = query.count()
        else:
            ret = []
            for antivirus, manufacturerName in query:
                if antivirus:
                    l = [
                        ["Name", __getAntivirusName(manufacturerName, antivirus.name)],
                        ["Enabled", antivirus.is_active == 1 and "Yes" or "No"],
                        ["Up-to-date", antivirus.is_uptodate == 1 and "Yes" or "No"],
                    ]
                    if antivirus.antivirus_version:
                        l.insert(1, ["Version", antivirus.antivirus_version])
                    ret.append(l)
        return ret

    def getLastMachineRegistryPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        query = self.filterOnUUID(
            session.query(RegContents)
            .add_column(self.registries.c.name)
            .add_column(self.regcontents.c.key)
            .add_column(self.regcontents.c.value)
            .select_from(
                self.machine.outerjoin(self.regcontents).outerjoin(self.registries)
            ),
            int(str(uuid).replace("UUID", "")),
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
            for row in query:
                if row.key is not None:
                    l = [
                        ["Registry key", row.name],
                        ["Value", row.value],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineSoftwaresPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        hide_win_updates = False
        if "hide_win_updates" in options:
            hide_win_updates = options["hide_win_updates"]

        query = self.filterOnUUID(
            session.query(Software)
            .add_column(self.manufacturers.c.name)
            .add_column(self.softwareversions.c.name)
            .select_from(
                self.machine.outerjoin(self.inst_software)
                .outerjoin(self.softwareversions)
                .outerjoin(self.software)
                .outerjoin(self.manufacturers)
            ),
            uuid,
        )
        query = query.order_by(self.software.c.name)

        if filt:
            clauses = []
            clauses.append(self.manufacturers.c.name.like("%" + filt + "%"))
            clauses.append(self.softwareversions.c.name.like("%" + filt + "%"))
            clauses.append(self.software.c.name.like("%" + filt + "%"))
            query = query.filter(or_(*clauses))

        if hide_win_updates:
            query = query.filter(
                not_(
                    and_(
                        self.manufacturers.c.name.contains("microsoft"),
                        self.software.c.name.op("regexp")(
                            "KB[0-9]+(-v[0-9]+)?(v[0-9]+)?"
                        ),
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
                        ["Vendor", manufacturer],
                        ["Name", software.name],
                        ["Version", version],
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
            "computer_name": (Machine, "name"),
            "description": (Machine, "comment"),
            "inventory_number": (Machine, "otherserial"),
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
            query = session.query(FusionLocks).filter(
                self.fusionlocks.c.items_id == fromUUID(uuid)
            )
            flocks = query.first()
            if flocks is not None:
                # Update glpi_plugin_fusioninventory_locks tablefields table
                flocksFields = eval(flocks.tablefields)
                if field not in flocksFields:
                    flocksFields.append(field)
                    query.update({"tablefields": str(flocksFields).replace("'", '"')})
            else:
                # Create new glpi_plugin_fusioninventory_locks entry
                session.execute(
                    self.fusionlocks.insert().values(
                        {
                            "tablename": table.__tablename__,
                            "items_id": fromUUID(uuid),
                            "tablefields": str([field]).replace("'", '"'),
                        }
                    )
                )

            session.close()
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def getLastMachineSummaryPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        query = self.filterOnUUID(
            session.query(Machine)
            .add_entity(Infocoms)
            .add_column(self.entities.c.name)
            .add_column(self.locations.c.name)
            .add_column(self.os.c.name)
            .add_column(self.manufacturers.c.name)
            .add_column(self.glpi_computertypes.c.name)
            .add_column(self.glpi_computermodels.c.name)
            .add_column(self.glpi_operatingsystemservicepacks.c.name)
            .add_column(self.glpi_operatingsystemversions.c.name)
            .add_column(self.glpi_operatingsystemarchitectures.c.name)
            .add_column(self.glpi_domains.c.name)
            .add_column(self.state.c.name)
            .add_column(self.fusionagents.c.last_contact)
            .select_from(
                self.machine.outerjoin(self.entities)
                .outerjoin(self.locations)
                .outerjoin(self.os)
                .outerjoin(self.manufacturers)
                .outerjoin(self.infocoms)
                .outerjoin(self.glpi_computertypes)
                .outerjoin(self.glpi_computermodels)
                .outerjoin(self.glpi_operatingsystemservicepacks)
                .outerjoin(self.glpi_operatingsystemversions)
                .outerjoin(self.glpi_operatingsystemarchitectures)
                .outerjoin(self.state)
                .outerjoin(self.fusionagents)
                .outerjoin(self.glpi_domains)
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for (
                machine,
                infocoms,
                entity,
                location,
                oslocal,
                manufacturer,
                type,
                model,
                servicepack,
                version,
                architecture,
                domain,
                state,
                last_contact,
            ) in query:
                endDate = ""
                if infocoms is not None:
                    endDate = self.getWarrantyEndDate(infocoms)

                modelType = []
                if model is not None:
                    modelType.append(model)
                if type is not None:
                    modelType.append(type)

                if len(modelType) == 0:
                    modelType = ""
                elif len(modelType) == 1:
                    modelType = modelType[0]
                elif len(modelType) == 2:
                    modelType = " / ".join(modelType)

                manufacturerWarranty = False
                if machine.serial is not None and len(machine.serial) > 0:
                    manufacturerWarranty = self.getManufacturerWarranty(
                        manufacturer, machine.serial
                    )

                if manufacturerWarranty:
                    if manufacturerWarranty["type"] == "get":
                        url = (
                            manufacturerWarranty["url"]
                            + "?"
                            + manufacturerWarranty["params"]
                        )
                        serialNumber = (
                            '%s / <a href="%s" target="_blank">@@WARRANTY_LINK_TEXT@@</a>'
                            % (machine.serial, url)
                        )
                    else:
                        url = manufacturerWarranty["url"]
                        serialNumber = (
                            '%s / <form action="%s" method="post" target="_blank" id="warrantyCheck" style="display: inline">'
                            % (machine.serial, url)
                        )
                        for param in manufacturerWarranty["params"].split("&"):
                            name, value = param.split("=")
                            serialNumber += (
                                '<input type="hidden" name="%s" value="%s" />'
                                % (name, value)
                            )
                        serialNumber += '<a href="#" onclick="jQuery(\'#warrantyCheck\').submit(); return false;">@@WARRANTY_LINK_TEXT@@</a></form>'
                else:
                    serialNumber = machine.serial

                entityValue = ""
                if entity:
                    entityValue += entity
                if location:
                    entityValue += " (%s)" % location

                owner_login, owner_firstname, owner_realname = self.getMachineOwner(
                    machine
                )

                # Last inventory date
                date_mod = machine.date_mod

                if self.fusionagents is not None and last_contact is not None:
                    date_mod = last_contact

                l = [
                    ["Computer Name", ["computer_name", "text", machine.name]],
                    ["Description", ["description", "text", machine.comment]],
                    ["Entity (Location)", "%s" % entityValue],
                    ["Domain", domain],
                    ["Last Logged User", machine.contact],
                    ["Owner", owner_login],
                    ["Owner Firstname", owner_firstname],
                    ["Owner Realname", owner_realname],
                    ["OS", oslocal],
                    ["Service Pack", servicepack],
                    ["Version", version],
                    ["Architecture", architecture],
                    ["Windows Key", machine.license_number],
                    ["Model / Type", modelType],
                    ["Manufacturer", manufacturer],
                    ["Serial Number", serialNumber],
                    ["Uuid", machine.uuid if machine.uuid is not None else ""],
                    [
                        "Inventory Number",
                        ["inventory_number", "text", machine.otherserial],
                    ],
                    ["State", state],
                    ["Warranty End Date", endDate],
                    ["Last Inventory Date", date_mod.strftime("%Y-%m-%d %H:%M:%S")],
                ]
                ret.append(l)
        return ret

    def getLastMachineProcessorsPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        query = self.filterOnUUID(
            session.query(ComputerProcessor)
            .add_column(self.processor.c.designation)
            .select_from(
                self.machine.outerjoin(self.computerProcessor).outerjoin(self.processor)
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for processor, designation in query:
                if processor is not None:
                    l = [
                        ["Name", designation],
                        [
                            "Frequency",
                            processor.frequency
                            and str(processor.frequency) + " MHz"
                            or "",
                        ],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineMemoryPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        query = self.filterOnUUID(
            session.query(ComputerMemory)
            .add_column(self.memoryType.c.name)
            .add_column(self.memory.c.frequence)
            .add_column(self.memory.c.designation)
            .select_from(
                self.machine.outerjoin(self.computerMemory)
                .outerjoin(self.memory)
                .outerjoin(self.memoryType)
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for memory, type, frequence, designation in query:
                if memory is not None:
                    l = [
                        ["Name", designation],
                        ["Type", type],
                        ["Frequency", frequence],
                        ["Size", memory.size and str(memory.size) + " MB" or ""],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineHarddrivesPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass["computers_deviceharddrives"])
            .add_column(self.deviceharddrives.c.designation)
            .select_from(
                self.machine.outerjoin(self.computers_deviceharddrives).outerjoin(
                    self.deviceharddrives
                )
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for hd, designation in query:
                if hd is not None:
                    l = [
                        ["Name", designation],
                        ["Size", hd.capacity and str(hd.capacity) + " MB" or ""],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineNetworkCardsPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass["computers_devicenetworkcards"])
            .add_entity(self.klass["devicenetworkcards"])
            .select_from(
                self.machine.outerjoin(self.computers_devicenetworkcards).outerjoin(
                    self.devicenetworkcards
                )
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for mac, network in query:
                if network is not None:
                    l = [
                        ["Name", network.designation],
                        ["Bandwidth", network.bandwidth],
                        ["MAC Address", mac.mac],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineDrivesPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass["devicedrives"]).select_from(
                self.machine.outerjoin(self.computers_devicedrives).outerjoin(
                    self.devicedrives
                )
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for drive in query:
                if drive is not None:
                    l = [
                        ["Name", drive.designation],
                        ["Writer", drive.is_writer and "Yes" or "No"],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineGraphicCardsPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass["devicegraphiccards"])
            .add_column(self.interfaceType.c.name)
            .select_from(
                self.machine.outerjoin(self.computers_devicegraphiccards)
                .outerjoin(self.devicegraphiccards)
                .outerjoin(
                    self.interfaceType,
                    self.interfaceType.c.id
                    == self.devicegraphiccards.c.interfacetypes_id,
                )
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for card, interfaceType in query:
                if card is not None:
                    l = [
                        ["Name", card.designation],
                        [
                            "Memory",
                            card.memory_default
                            and str(card.memory_default) + " MB"
                            or "",
                        ],
                        ["Type", interfaceType],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineSoundCardsPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass["devicesoundcards"]).select_from(
                self.machine.outerjoin(self.computers_devicesoundcards).outerjoin(
                    self.devicesoundcards
                )
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for sound in query:
                if sound is not None:
                    l = [
                        ["Name", sound.designation],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineControllersPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass["computers_devicecontrols"])
            .add_entity(self.klass["devicecontrols"])
            .select_from(
                self.machine.outerjoin(self.computers_devicecontrols).outerjoin(
                    self.devicecontrols
                )
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for computerControls, deviceControls in query:
                if computerControls is not None:
                    l = [
                        ["Name", deviceControls.designation],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineOthersPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options=None, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        options = options or {}
        query = self.filterOnUUID(
            session.query(self.klass["devicepcis"]).select_from(
                self.machine.outerjoin(self.computers_devicepcis).outerjoin(
                    self.devicepcis
                )
            ),
            uuid,
        )

        if count:
            ret = query.count()
        else:
            ret = []
            for pci in query:
                if pci is not None:
                    l = [
                        ["Name", pci.designation],
                        ["Comment", pci.comment],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineHistoryPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options={}, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        # options = options or {}
        # Set options
        history_delta = "All"
        if "history_delta" in options:
            history_delta = options["history_delta"]

        query = session.query(Logs)
        query = query.filter(
            and_(
                self.logs.c.items_id == int(uuid.replace("UUID", "")),
                self.logs.c.itemtype == "Computer",
            )
        )

        now = datetime.datetime.now()
        if history_delta == "today":
            query = query.filter(self.logs.c.date_mod > now - datetime.timedelta(1))
        elif history_delta == "week":
            query = query.filter(self.logs.c.date_mod > now - datetime.timedelta(7))
        if history_delta == "month":
            query = query.filter(self.logs.c.date_mod > now - datetime.timedelta(30))

        if filt:
            clauses = []
            clauses.append(self.logs.c.date_mod.like("%" + filt + "%"))
            clauses.append(self.logs.c.user_name.like("%" + filt + "%"))
            clauses.append(self.logs.c.old_value.like("%" + filt + "%"))
            clauses.append(self.logs.c.new_value.like("%" + filt + "%"))
            clauses.append(
                self.logs.c.id_search_option.in_(self.getSearchOptionId(filt))
            )
            clauses.append(self.logs.c.itemtype_link.in_(self.getLinkedActionKey(filt)))
            # Treat Software case
            if filt.lower() in "software":
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
                    update = ""
                    if log.old_value == "" and log.new_value != "":
                        update = "%s" % log.new_value
                    elif log.old_value != "" and log.new_value == "":
                        update = "%s" % log.old_value
                    else:
                        update = "%s --> %s" % (log.old_value, log.new_value)

                    update = "%s%s" % (
                        self.getLinkedActionValues(log)["update"],
                        update,
                    )

                    l = [
                        ["Date", log.date_mod.strftime("%Y-%m-%d %H:%m")],
                        ["User", log.user_name],
                        ["Category", self.getLinkedActionValues(log)["field"]],
                        ["Action", update],
                    ]
                    ret.append(l)
        return ret

    def getLastMachineInventoryPart(
        self, uuid, part, minbound=0, maxbound=-1, filt=None, options=None, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        options = options or {}
        session = create_session()

        ret = None
        if hasattr(self, "getLastMachine%sPart" % part):
            ret = getattr(self, "getLastMachine%sPart" % part)(
                session, uuid, part, minbound, maxbound, filt, options, count
            )

        session.close()
        return ret

    def getLastMachineConnectionsPart(
        self, session, uuid, part, min=0, max=-1, filt=None, options=None, count=False
    ):
        # Mutable dict options used as default argument to a method or function
        options = options or {}
        session = create_session()
        uuid = int(uuid.replace("UUID", ""))
        query = session.query(distinct(Computersitems.itemtype)).filter(
            Computersitems.computers_id == uuid
        )
        query = self.__filter_on(query)
        ret = session.execute(query)

        connectionslist = []

        for element in ret:
            itemtype = element[0]
            _itemtype = itemtype.lower() + "s"
            if hasattr(self, _itemtype):
                connection = eval("self.%s" % _itemtype)
                query = (
                    session.query(
                        Computersitems.items_id,
                        Computersitems.itemtype,
                        connection.c.name,
                        connection.c.serial,
                    )
                    .join(connection, connection.c.id == Computersitems.items_id)
                    .filter(
                        Computersitems.computers_id == uuid,
                        Computersitems.itemtype == itemtype,
                    )
                )
                query = self.__filter_on(query).all()

            connectionslist += query
        session.close()

        table = []
        for row in connectionslist:
            tmprow = []

            tmprow.append(["type", row[1]])
            tmprow.append(["name", row[2]])
            tmprow.append(["serial", row[3]])
            table.append(tmprow)

        if count:
            return len(table)

        return table

    def getSearchOptionValue(self, log):
        try:
            return self.searchOptions["en_US"][str(log.id_search_option)]
        except:
            if log.id_search_option != 0:
                logging.getLogger().warn(
                    "I can't get a search option for id %s" % log.id_search_option
                )
            return ""

    def getLinkedActionValues(self, log):
        d = {
            0: {
                "update": "",
                "field": self.getSearchOptionValue(log),
            },
            1: {
                "update": "Add a component: ",
                "field": self.getLinkedActionField(log.itemtype_link),
            },
            2: {
                "update": "Update a component: ",
                "field": self.getLinkedActionField(log.itemtype_link),
            },
            3: {
                "update": "Deletion of a component: ",
                "field": self.getLinkedActionField(log.itemtype_link),
            },
            4: {
                "update": "Install software: ",
                "field": "Software",
            },
            5: {
                "update": "Uninstall software: ",
                "field": "Software",
            },
            6: {
                "update": "Disconnect device: ",
                "field": log.itemtype_link,
            },
            7: {
                "update": "Connect device: ",
                "field": log.itemtype_link,
            },
            8: {
                "update": "OCS Import: ",
                "field": "",
            },
            9: {
                "update": "OCS Delete: ",
                "field": "",
            },
            10: {
                "update": "OCS ID Changed: ",
                "field": "",
            },
            11: {
                "update": "OCS Link: ",
                "field": "",
            },
            12: {
                "update": "Other (often from plugin): ",
                "field": "",
            },
            13: {
                "update": "Delete item (put in trash): ",
                "field": "",
            },
            14: {
                "update": "Restore item from trash: ",
                "field": "",
            },
            15: {
                "update": "Add relation: ",
                "field": log.itemtype_link,
            },
            16: {
                "update": "Delete relation: ",
                "field": log.itemtype_link,
            },
            17: {
                "update": "Add an item: ",
                "field": self.getLinkedActionField(log.itemtype_link),
            },
            18: {
                "update": "Update an item: ",
                "field": self.getLinkedActionField(log.itemtype_link),
            },
            19: {
                "update": "Deletion of an item: ",
                "field": self.getLinkedActionField(log.itemtype_link),
            },
        }

        if log.linked_action in d:
            return d[log.linked_action]
        else:
            return {
                "update": "",
                "field": "",
            }

    def getLinkedActions(self):
        return {
            "DeviceDrive": "Drive",
            "DeviceGraphicCard": "Graphic Card",
            "DeviceHardDrive": "Hard Drive",
            "DeviceMemory": "Memory",
            "DeviceNetworkCard": "Network Card",
            "DevicePci": "Other Component",
            "DeviceProcessor": "Processor",
            "DeviceSoundCard": "Sound Card",
            "ComputerDisk": "Volume",
            "NetworkPort": "Network Port",
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
        unknown_os_pxe_id = self.getUnknownPXEOSId(
            "Unknown operating system (PXE network boot inventory)"
        )
        if unknown_os_pxe_id:
            unknown_os_ids.append(unknown_os_pxe_id)

        query = self.filterOnUUID(
            session.query(Machine).filter(
                not_(self.machine.c.operatingsystems_id.in_(unknown_os_ids))
            ),
            uuid,
        )
        session.close()

        return query.first() and True or False

    ##################### functions used by querymanager
    def getAllOs(self, ctx, filt=""):
        """
        @return: all os defined in the GLPI database
        """
        session = create_session()
        query = session.query(OS).select_from(self.os.join(self.machine))
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.os.c.name.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    def getMachineByOs(self, ctx, osname):
        """
        @return: all machines that have this os
        """
        # TODO use the ctx...
        session = create_session()
        query = (
            session.query(Machine)
            .select_from(self.machine.join(self.os))
            .filter(self.os.c.name == osname)
        )
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getMachineByOsLike(self, session, ctx, osnames, count=0):
        """
        @return: all machines that have this os using LIKE
        """
        if isinstance(osnames, str):
            osnames = [osnames]

        if int(count) == 1:
            query = session.query(func.count(Machine.id)).select_from(
                self.machine.outerjoin(self.os)
            )
        else:
            query = session.query(Machine).select_from(self.machine.outerjoin(self.os))

        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)

        if osnames == ["other"]:
            query = query.filter(
                or_(
                    and_(
                        not_(OS.name.like("%Windows%")),
                        not_(OS.name.like("%Mageia%")),
                        not_(OS.name.like("%macOS%")),
                    ),
                    Machine.operatingsystems_id == 0,
                )
            )
        elif osnames == ["otherw"]:
            query = query.filter(
                and_(
                    not_(OS.name.like("%Windows%10%")),
                    not_(OS.name.like("%Windows%8%")),
                    not_(OS.name.like("%Windows%7%")),
                    not_(OS.name.like("%Windows%Vista%")),
                    not_(OS.name.like("%Windows%XP%")),
                    OS.name.like("%Windows%"),
                )
            )
        # if osnames == ['%'], we want all machines, including machines without OS (used for reporting, per example...)
        elif osnames != ["%"]:
            os_filter = [OS.name.like("%" + osname + "%") for osname in osnames]
            query = query.filter(or_(*os_filter))

        if int(count) == 1:
            return int(query.scalar())
        else:
            return [[q.id, q.name] for q in query]

    def getAllEntities(self, ctx, filt=""):
        """
        @return: all entities defined in the GLPI database
        """
        session = create_session()
        query = session.query(Entities)
        if filter != "":
            query = query.filter(self.entities.c.name.like("%" + filt + "%"))

        # Request only entites current user can access
        if not hasattr(ctx, "locationsid"):
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
        query = (
            session.query(Machine)
            .select_from(self.machine.join(self.entities))
            .filter(self.entities.c.name == enname)
        )
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
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
            lids = lids
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
    def getAllVersion4Software(self, session, ctx, softname, version=""):
        """
        @return: all softwares defined in the GLPI database
        """
        if not hasattr(ctx, "locationsid"):
            complete_ctx(ctx)
        query = session.query(distinct(SoftwareVersion.name)).select_from(
            self.softwareversions.join(self.software)
        )

        my_parents_ids = self.getEntitiesParentsAsList(ctx.locationsid)
        query = query.filter(
            or_(
                Software.entities_id.in_(ctx.locationsid),
                and_(
                    Software.is_recursive == 1, Software.entities_id.in_(my_parents_ids)
                ),
            )
        )

        query = query.filter(Software.name.like("%" + softname + "%"))

        if version:
            query = query.filter(SoftwareVersion.name.like("%" + version + "%"))

        # Last softwareversion entries first
        query = query.order_by(desc(SoftwareVersion.id))

        ret = query.all()
        return ret

    @DatabaseHelper._sessionm
    def getAllSoftwares(self, session, ctx, softname="", vendor=None, limit=None):
        """
        @return: all softwares defined in the GLPI database
        """
        if not hasattr(ctx, "locationsid"):
            complete_ctx(ctx)

        query = session.query(distinct(Software.name))
        query = query.select_from(
            self.software.join(self.softwareversions)
            .join(self.inst_software)
            .join(self.manufacturers, isouter=True)
        )
        my_parents_ids = self.getEntitiesParentsAsList(ctx.locationsid)
        query = query.filter(
            or_(
                Software.entities_id.in_(ctx.locationsid),
                and_(
                    Software.is_recursive == 1, Software.entities_id.in_(my_parents_ids)
                ),
            )
        )
        if vendor is not None:
            query = query.filter(Manufacturers.name.like(vendor))

        if softname != "":
            query = query.filter(Software.name.like("%" + softname + "%"))

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
        if not hasattr(ctx, "locationsid"):
            complete_ctx(ctx)
        query = session.query(Software)
        query = query.join(Manufacturers)
        query = query.filter(Manufacturers.name.like(vendor))
        ret = query.group_by(Software.name).order_by(Software.name).all()
        return ret

    @DatabaseHelper._sessionm
    def getMachineBySoftware(
        self, session, ctx, name, vendor=None, version=None, count=0
    ):
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
        if vendor is not None:
            vendor = check_list(vendor)
        if version is not None:
            version = check_list(version)

        if int(count) == 1:
            query = session.query(func.count(distinct(self.machine.c.id)))
        else:
            query = session.query(distinct(self.machine.c.id))

        query = query.select_from(
            self.machine.join(self.inst_software)
            .join(self.softwareversions)
            .join(self.software)
            .outerjoin(self.manufacturers)
        )
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
    def getAllSoftwaresImproved(
        self, session, ctx, name, vendor=None, version=None, count=0
    ):
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
        if vendor is not None:
            vendor = check_list(vendor)
        if version is not None:
            version = check_list(version)

        if int(count) == 1:
            query = session.query(func.count(self.software.c.name))
        elif int(count) == 2:
            query = session.query(self.software.c.name)
        else:
            query = session.query(
                self.machine.c.id.label("computers_id"),
                self.machine.c.name.label("computers_name"),
                self.machine.c.entities_id.label("entity_id"),
            )

        if int(count) >= 3:
            query = query.select_from(
                self.machine.join(self.inst_software)
                .join(self.softwareversions)
                .join(self.software)
                .outerjoin(self.manufacturers)
            )
        else:
            query = query.select_from(
                self.software.join(self.softwareversions)
                .join(self.inst_software)
                .outerjoin(self.manufacturers)
            )

        name_filter = [Software.name.like(n) for n in name]
        query = query.filter(or_(*name_filter))

        if version is not None:
            version_filter = [SoftwareVersion.name.like(v) for v in version]
            query = query.filter(or_(*version_filter))

        if vendor is not None:
            vendor_filter = [Manufacturers.name.like(v) for v in vendor]
            query = query.filter(or_(*vendor_filter))

        if hasattr(ctx, "locationsid"):
            query = query.filter(Software.entities_id.in_(ctx.locationsid))
        if int(count) >= 3:
            query = query.filter(Machine.is_deleted == 0)
            query = query.filter(Machine.is_template == 0)

        if int(count) == 1:
            return {"count": int(query.scalar())}
        elif int(count) == 2:
            return query.all()
        else:
            ret = query.all()
            return [{"computer": a[0], "name": a[1], "entityid": a[2]} for a in ret]

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

    def getAllHostnames(self, ctx, filt=""):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.machine.c.name.like("%" + filt + "%"))
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
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.name == hostname)
        ret = query.all()
        session.close()
        return ret

    def getAllContacts(self, ctx, filt=""):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.machine.c.contact.like("%" + filt + "%"))
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
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.contact == contact)
        ret = query.all()
        session.close()
        return ret

    def getAllContactNums(self, ctx, filt=""):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.machine.c.contact_num.like("%" + filt + "%"))
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
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.contact_num == contact_num)
        ret = query.all()
        session.close()
        return ret

    def getAllComments(self, ctx, filt=""):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.machine.c.comment.like("%" + filt + "%"))
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
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.comment == comment)
        ret = query.all()
        session.close()
        return ret

    def getAllModels(self, ctx, filt=""):
        """@return: all machine models defined in the GLPI database"""
        session = create_session()
        query = session.query(Model).select_from(self.model.join(self.machine))
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.model.c.name.like("%" + filt + "%"))
        ret = query.group_by(self.model.c.name).all()
        session.close()
        return ret

    def getAllManufacturers(self, ctx, filt=""):
        """@return: all machine manufacturers defined in the GLPI database"""
        session = create_session()
        query = session.query(Manufacturers).select_from(
            self.manufacturers.join(self.machine)
        )
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.manufacturers.c.name.like("%" + filt + "%"))
        ret = query.group_by(self.manufacturers.c.name).all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getAllSoftwareVendors(self, session, ctx, filt="", limit=20):
        """@return: all software vendors defined in the GPLI database"""
        query = session.query(Manufacturers).select_from(
            self.manufacturers.join(self.software)
        )
        query = query.filter(Software.is_deleted == 0)
        query = query.filter(Software.is_template == 0)
        if filt != "":
            query = query.filter(Manufacturers.name.like("%" + filt + "%"))
        query = query.group_by(Manufacturers.name)
        ret = query.order_by(asc(Manufacturers.name)).limit(limit)
        return ret

    @DatabaseHelper._sessionm
    def getAllSoftwareVersions(self, session, ctx, software=None, filt=""):
        """@return: all software versions defined in the GPLI database"""
        query = session.query(SoftwareVersion)
        query = query.select_from(self.softwareversions.join(self.software))
        if software is not None:
            query = query.filter(Software.name.like(software))
        if filt != "":
            query = query.filter(SoftwareVersion.name.like("%" + filt + "%"))
        ret = query.group_by(SoftwareVersion.name).all()
        return ret

    def getAllStates(self, ctx, filt=""):
        """@return: all machine models defined in the GLPI database"""
        session = create_session()
        query = session.query(State).select_from(self.state.join(self.machine))
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.state.c.name.like("%" + filt + "%"))
        ret = query.group_by(self.state.c.name).all()
        session.close()
        return ret

    def getAllTypes(self, ctx, filt=""):
        """@return: all machine types defined in the GLPI database"""
        session = create_session()
        query = session.query(self.klass["glpi_computertypes"]).select_from(
            self.glpi_computertypes.join(self.machine)
        )
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.glpi_computertypes.c.name.like("%" + filt + "%"))
        ret = query.group_by(self.glpi_computertypes.c.name).all()
        session.close()
        return ret

    def getAllInventoryNumbers(self, ctx, filt=""):
        """@return: all machine inventory numbers defined in the GLPI database"""
        ret = []
        return ret

    def getMachineByModel(self, ctx, filt):
        """@return: all machines that have this model"""
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.model))
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.model.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllOwnerMachine(self, ctx, filt=""):
        """@return: all owner defined in the GLPI database"""
        session = create_session()
        query = session.query(User).select_from(self.manufacturers.join(self.machine))
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.user.c.name.like("%" + filt + "%"))
        ret = query.group_by(self.user.c.name).all()
        session.close()
        return ret

    def getAllLoggedUser(self, ctx, filt=""):
        """
        @return: all LoggedUser defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.machine.c.contact.like("%" + filt + "%"))
        ret = query.group_by(self.machine.c.contact).all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getMachineByType(self, session, ctx, types, count=0):
        """@return: all machines that have this type"""
        if isinstance(types, str):
            types = [types]

        if int(count) == 1:
            query = session.query(func.count(Machine.id)).select_from(
                self.machine.join(self.glpi_computertypes)
            )
        else:
            query = session.query(Machine).select_from(
                self.machine.join(self.glpi_computertypes)
            )
        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)

        type_filter = [
            self.klass["glpi_computertypes"].name.like(type) for type in types
        ]
        query = query.filter(or_(*type_filter))

        if int(count) == 1:
            ret = int(query.scalar())
        else:
            ret = query.all()
        return ret

    def getMachineByInventoryNumber(self, ctx, filt):
        """@return: all machines that have this type"""
        session = create_session()
        query = session.query(Machine).select_from(self.machine)
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.otherserial == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByManufacturer(self, ctx, filt):
        """@return: all machines that have this manufacturer"""
        session = create_session()
        query = session.query(Manufacturers).select_from(
            self.machine.join(self.manufacturers)
        )
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.manufacturers.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByState(self, ctx, filt, count=0):
        """@return: all machines that have this state"""
        session = create_session()
        if int(count) == 1:
            query = session.query(func.count(Machine)).select_from(
                self.machine.join(self.state)
            )
        else:
            query = session.query(Machine).select_from(self.machine.join(self.state))
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if "%" in filt:
            query = query.filter(self.state.c.name.like(filt))
        else:
            query = query.filter(self.state.c.name == filt)
        if int(count) == 1:
            ret = int(query.scalar())
        else:
            ret = query.all()
        session.close()
        return ret

    def getAllLocations(self, ctx, filt=""):
        """@return: all hostnames defined in the GLPI database"""
        if not hasattr(ctx, "locationsid"):
            complete_ctx(ctx)
        session = create_session()
        query = session.query(Locations).select_from(self.locations.join(self.machine))
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        my_parents_ids = self.getEntitiesParentsAsList(ctx.locationsid)
        query = self.__filter_on_entity(query, ctx, my_parents_ids)
        query = query.filter(
            or_(
                self.locations.c.entities_id.in_(ctx.locationsid),
                and_(
                    self.locations.c.is_recursive == 1,
                    self.locations.c.entities_id.in_(my_parents_ids),
                ),
            )
        )
        if filter != "":
            query = query.filter(self.locations.c.completename.like("%" + filt + "%"))
        ret = query.group_by(self.locations.c.completename).all()
        session.close()
        return ret

    def getAllLocations1(self, ctx, filt=""):
        """@return: all hostnames defined in the GLPI database"""
        if not hasattr(ctx, "locationsid"):
            complete_ctx(ctx)
        session = create_session()
        query = session.query(Locations)
        if filter != "":
            query = query.filter(self.locations.c.completename.like("%" + filt + "%"))
        ret = query.group_by(self.locations.c.completename)
        ret = ret.all()
        session.close()
        return ret

    def getAllRegistryKey(self, ctx, filt=""):
        """
        Returns the registry keys name.
        @return: list Register key name
        """
        ret = None
        session = create_session()
        query = session.query(Registries.name)
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.registries.c.name.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getAllRegistryKeyValue(self, session, ctx, keyregister, value):
        """
        @return: all key value defined in the GLPI database
        """
        ret = None
        # if not hasattr(ctx, 'locationsid'):
        # complete_ctx(ctx)
        session = create_session()
        query = session.query(distinct(RegContents.value))
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.registries.c.key.like("%" + keyregister + "%"))
        ret = query.all()
        session.close()
        return ret

    def getMachineByLocation(self, ctx, filt):
        """@return: all machines that have this contact number"""
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.locations))
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.locations.c.completename == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllOsSps(self, ctx, filt=""):
        """@return: all hostnames defined in the GLPI database"""
        session = create_session()
        query = session.query(OsSp).select_from(self.os_sp.join(self.machine))
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.os_sp.c.name.like("%" + filt + "%"))
        ret = query.group_by(self.os_sp.c.name).all()
        session.close()
        return ret

    def getMachineByOsSp(self, ctx, filt):
        """@return: all machines that have this contact number"""
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.os_sp))
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.os_sp.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllGroups(self, ctx, filt=""):
        """@return: all hostnames defined in the GLPI database"""
        if not hasattr(ctx, "locationsid"):
            complete_ctx(ctx)
        session = create_session()
        query = session.query(Group).select_from(self.group.join(self.machine))
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        my_parents_ids = self.getEntitiesParentsAsList(ctx.locationsid)
        query = self.__filter_on_entity(query, ctx, my_parents_ids)
        query = query.filter(
            or_(
                self.group.c.entities_id.in_(ctx.locationsid),
                and_(
                    self.group.c.is_recursive == 1,
                    self.group.c.entities_id.in_(my_parents_ids),
                ),
            )
        )
        if filter != "":
            query = query.filter(self.group.c.name.like("%" + filt + "%"))
        ret = query.group_by(self.group.c.name).all()
        session.close()
        return ret

    def getMachineByGroup(self, ctx, filt):  # Entity!
        """@return: all machines that have this contact number"""
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.group))
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.group.c.entities_id.in_(ctx.locationsid))
        query = query.filter(self.group.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllNetworks(self, ctx, filt=""):
        """@return: all hostnames defined in the GLPI database"""
        session = create_session()
        query = session.query(Net).select_from(self.net.join(self.machine))
        query = self.__filter_on(
            query.filter(self.machine.c.is_deleted == 0).filter(
                self.machine.c.is_template == 0
            )
        )
        query = self.__filter_on_entity(query, ctx)
        if filter != "":
            query = query.filter(self.net.c.name.like("%" + filt + "%"))
        ret = query.group_by(self.net.c.name).all()
        session.close()
        return ret

    def getMachineByNetwork(self, ctx, filt):
        """@return: all machines that have this contact number"""
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.net))
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.net.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def _machineobjectdymresult(self, ret, encode="iso-8859-1"):
        """
        this function return dict result sqlalchimy
        """
        resultrecord = {}
        try:
            if ret:
                for keynameresult in list(ret.keys()):
                    try:
                        if getattr(ret, keynameresult) is None:
                            resultrecord[keynameresult] = ""
                        else:
                            typestr = str(type(getattr(ret, keynameresult)))
                            if "class" in typestr:
                                try:
                                    if "decimal.Decimal" in typestr:
                                        resultrecord[keynameresult] = float(
                                            getattr(ret, keynameresult)
                                        )
                                    else:
                                        resultrecord[keynameresult] = str(
                                            getattr(ret, keynameresult)
                                        )
                                except:
                                    self.logger.warning(
                                        "type class %s no used for key %s"
                                        % (typestr, keynameresult)
                                    )
                                    resultrecord[keynameresult] = ""
                            else:
                                if isinstance(
                                    getattr(ret, keynameresult), datetime.datetime
                                ):
                                    resultrecord[keynameresult] = getattr(
                                        ret, keynameresult
                                    ).strftime("%m/%d/%Y %H:%M:%S")
                                else:
                                    strre = getattr(ret, keynameresult)
                                    if isinstance(strre, str):
                                        if encode == "utf8":
                                            resultrecord[keynameresult] = str(strre)
                                        else:
                                            resultrecord[keynameresult] = strre.decode(
                                                encode
                                            ).encode("utf8")
                                    else:
                                        resultrecord[keynameresult] = strre
                    except AttributeError:
                        resultrecord[keynameresult] = ""
        except Exception as e:
            self.logger.error("We encountered the error %s" % str(e))
            self.logger.error("\n with the backtrace \n%s" % (traceback.format_exc()))
        return resultrecord

    def _machineobject(self, ret):
        """result view glpi_computers_pulse"""
        if ret:
            try:
                return {
                    "id": ret.id if hasattr(ret, "id") else ret.uuidglpicomputer,
                    "entities_id": ret.entities_id,
                    "name": ret.name,
                    "serial": ret.serial if ret.serial is not None else "",
                    "otherserial": (
                        ret.otherserial if ret.otherserial is not None else ""
                    ),
                    "contact": ret.contact if ret.contact is not None else "",
                    "contact_num": (
                        ret.contact_num if ret.contact_num is not None else ""
                    ),
                    "users_id_tech": (
                        ret.users_id_tech if ret.users_id_tech is not None else ""
                    ),
                    "groups_id_tech": (
                        ret.groups_id_tech if ret.groups_id_tech is not None else ""
                    ),
                    "comment": ret.comment if ret.comment is not None else "",
                    "date_mod": (
                        ret.date_mod.__str__() if ret.date_mod is not None else ""
                    ),
                    "autoupdatesystems_id": (
                        ret.autoupdatesystems_id
                        if ret.autoupdatesystems_id is not None
                        else ""
                    ),
                    "locations_id": (
                        ret.locations_id if ret.locations_id is not None else ""
                    ),
                    "domains_id": ret.domains_id if ret.domains_id is not None else "",
                    "networks_id": (
                        ret.networks_id if ret.networks_id is not None else ""
                    ),
                    "computermodels_id": (
                        ret.computermodels_id
                        if ret.computermodels_id is not None
                        else ""
                    ),
                    "computertypes_id": (
                        ret.computertypes_id if ret.computertypes_id is not None else ""
                    ),
                    "is_template": (
                        ret.is_template if ret.is_template is not None else ""
                    ),
                    "template_name": (
                        ret.template_name if ret.template_name is not None else ""
                    ),
                    "manufacturers_id": (
                        ret.manufacturers_id if ret.manufacturers_id is not None else ""
                    ),
                    "is_deleted": ret.is_deleted if ret.is_deleted is not None else "",
                    "is_dynamic": ret.is_dynamic if ret.is_dynamic is not None else "",
                    "users_id": ret.users_id if ret.users_id is not None else "",
                    "groups_id": ret.groups_id if ret.groups_id is not None else "",
                    "states_id": ret.states_id if ret.states_id is not None else "",
                    "ticket_tco": float(ret.ticket_tco),
                    "uuid": ret.uuid if ret.uuid is not None else "",
                    "date_creation": (
                        ret.date_creation.__str__()
                        if ret.date_creation is not None
                        else ""
                    ),
                    "is_recursive": (
                        ret.is_recursive if ret.is_recursive is not None else ""
                    ),
                    "operatingsystems_id": (
                        ret.operatingsystems_id
                        if ret.operatingsystems_id is not None
                        else ""
                    ),
                    "operatingsystemversions_id": (
                        ret.operatingsystemversions_id
                        if ret.operatingsystemversions_id is not None
                        else ""
                    ),
                    "operatingsystemservicepacks_id": (
                        ret.operatingsystemservicepacks_id
                        if ret.operatingsystemservicepacks_id is not None
                        else ""
                    ),
                    "operatingsystemarchitectures_id": (
                        ret.operatingsystemarchitectures_id
                        if ret.operatingsystemarchitectures_id is not None
                        else ""
                    ),
                    "license_number": (
                        ret.license_number if ret.license_number is not None else ""
                    ),
                    "license_id": ret.license_id if ret.license_id is not None else "",
                    "operatingsystemkernelversions_id": (
                        ret.operatingsystemkernelversions_id
                        if ret.operatingsystemkernelversions_id is not None
                        else ""
                    ),
                }
            except Exception:
                self.logger.error("\n%s" % (traceback.format_exc()))
        return {}

    def getMachineBySerial(self, serial):
        """@return: all computers that have this mac address"""
        session = create_session()
        ret = session.query(Machine).filter(Machine.serial.like(serial)).first()
        session.close()
        return self._machineobject(ret)

    def getMachineByUuidSetup(self, uuidsetupmachine):
        """@return: all computers that have this uuid setup machine"""
        session = create_session()
        ret = session.query(Machine).filter(Machine.uuid.like(uuidsetupmachine)).first()
        session.close()
        return self._machineobject(ret)

    def getMachineByMacAddress(self, ctx, filt):
        """@return: all computers that have this mac address"""
        session = create_session()
        query = session.query(Machine).join(
            NetworkPorts,
            and_(
                Machine.id == NetworkPorts.items_id, NetworkPorts.itemtype == "Computer"
            ),
        )
        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)
        query = query.filter(NetworkPorts.mac == filt)
        query = self.__filter_on(query)
        if ctx != "imaging_module":
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
        query = session.query(Machine).join(
            NetworkPorts,
            and_(
                Machine.id == NetworkPorts.items_id, NetworkPorts.itemtype == "Computer"
            ),
        )
        query = query.filter(Machine.is_deleted == 0).filter(Machine.is_template == 0)
        query = query.filter(NetworkPorts.mac.in_(macs))
        query = query.filter(self.machine.c.name == hostname)
        query = self.__filter_on(query)
        if ctx != "imaging_module":
            query = self.__filter_on_entity(query, ctx)
        try:
            ret = query.one()
        except (MultipleResultsFound, NoResultFound) as e:
            self.logger.warn(
                "I can't get any UUID for machine %s and macs %s: %s"
                % (hostname, macs, e)
            )
            return None
        return toUUID(ret.id)

    def getMachineByOsVersion(self, ctx, filt):
        """@return: all machines that have this os version"""
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.os_version))
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.os_version.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByArchitecure(self, ctx, filt):
        """@return: all machines that have this architecture"""
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.os_arch))
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.os_arch.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByPrinter(self, ctx, filt):
        session = create_session()
        query = (
            session.query(Machine)
            .select_from(self.machine.join(self.computersitems))
            .select_from(self.computersitems.join(self.printers))
        )
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.printers.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByPrinterserial(self, ctx, filt):
        session = create_session()
        query = (
            session.query(Machine)
            .distinct(Machine.id)
            .join(Computersitems, Machine.id == Computersitems.computers_id)
            .outerjoin(
                Printers,
                and_(
                    Computersitems.items_id == Printers.id,
                    Computersitems.itemtype == "Printer",
                ),
            )
            .outerjoin(
                Peripherals,
                and_(
                    Computersitems.items_id == Peripherals.id,
                    Computersitems.itemtype == "Peripheral",
                ),
            )
        )
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.printers.c.serial == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineByPeripheral(self, ctx, filt):
        session = create_session()
        query = (
            session.query(Machine)
            .distinct(Machine.id)
            .join(Computersitems, Machine.id == Computersitems.computers_id)
            .outerjoin(
                Printers,
                and_(
                    Computersitems.items_id == Printers.id,
                    Computersitems.itemtype == "Printer",
                ),
            )
            .outerjoin(
                Peripherals,
                and_(
                    Computersitems.items_id == Peripherals.id,
                    Computersitems.itemtype == "Peripheral",
                ),
            )
        )
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.peripherals.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getMachineInformationByUuidSetup(self, uuidsetupmachine):
        """
        @return: all computers that have this uuid setup machine"""
        return self.get_machines_list(0, 0, {"uuidsetup": uuidsetupmachine})

    def getMachineInformationByUuidMachine(self, glpi_uuid):
        """@return: all computers that have this uuid  machine"""
        return self.get_machines_list(0, 0, {"idmachine": glpi_uuid})

    def getMachineByPeripheralserial(self, ctx, filt):
        session = create_session()
        query = (
            session.query(Machine)
            .distinct(Machine.id)
            .join(Computersitems, Machine.id == Computersitems.computers_id)
            .outerjoin(
                Printers,
                and_(
                    Computersitems.items_id == Printers.id,
                    Computersitems.itemtype == "Printer",
                ),
            )
            .outerjoin(
                Peripherals,
                and_(
                    Computersitems.items_id == Peripherals.id,
                    Computersitems.itemtype == "Peripheral",
                ),
            )
        )
        query = query.filter(self.machine.c.is_deleted == 0).filter(
            self.machine.c.is_template == 0
        )
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.peripherals.c.serial == filt)
        ret = query.all()
        session.close()
        return ret

    def getComputersOS(self, uuids):
        if isinstance(uuids, str):
            uuids = [uuids]
        session = create_session()
        query = (
            session.query(Machine)
            .add_column(self.os.c.name)
            .select_from(self.machine.join(self.os))
        )
        query = query.filter(self.machine.c.id.in_([fromUUID(uuid) for uuid in uuids]))
        session.close()
        res = []
        for machine, OSName in query:
            res.append(
                {
                    "uuid": toUUID(machine.id),
                    "OSName": OSName,
                }
            )
        return res

    def getComputersCountByOS(self, osname):
        session = create_session()
        query = session.query(func.count(Machine.id)).select_from(
            self.machine.join(self.os)
        )
        query = query.filter(self.os.c.name.like("%" + osname + "%"))
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
        ret = self.getMachineByMacAddress("imaging_module", mac)
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
                                "uuid": toUUID(networkport.id),
                                "domain": domain,
                                "ifmac": networkport.mac,
                                "name": networkport.name,
                                "netmask": "",
                                "subnet": "",
                                "gateway": "",
                                "ifaddr": "",
                            }

                            # IP Address
                            d["ifaddr"] = ipaddress.name

                            # Init old iface dict
                            z = {}

                            for ipnetwork in ipaddress.ipnetworks:
                                oz = z

                                z = d.copy()
                                z["netmask"] = ipnetwork.netmask
                                z["gateway"] = ipnetwork.gateway
                                z["subnet"] = ipnetwork.address

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
            domain = ""
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
            if not empty_macs:
                if not ("ifmac" in iface or iface["ifmac"]):
                    continue
            if "ifaddr" in iface and iface["ifaddr"]:
                if iface["gateway"] == None:
                    ret_ifmac.append(iface["ifmac"])
                    ret_ifaddr.append(iface["ifaddr"])
                    ret_netmask.append(iface["netmask"])
                    ret_networkUuids.append(iface["uuid"])
                    if "domain" in iface:
                        ret_domain.append(iface["domain"])
                    else:
                        ret_domain.append("")
                else:
                    if same_network(
                        iface["ifaddr"], iface["gateway"], iface["netmask"]
                    ):
                        idx_good += 1
                        ret_ifmac.insert(0, iface["ifmac"])
                        ret_ifaddr.insert(0, iface["ifaddr"])
                        ret_netmask.insert(0, iface["netmask"])
                        ret_networkUuids.insert(0, iface["uuid"])
                        if "domain" in iface:
                            ret_domain.insert(0, iface["domain"])
                        else:
                            ret_domain.insert(0, "")
                        failure[0] = False
                    else:
                        ret_ifmac.insert(idx_good, iface["ifmac"])
                        ret_ifaddr.insert(idx_good, iface["ifaddr"])
                        ret_netmask.insert(idx_good, iface["netmask"])
                        ret_networkUuids.insert(idx_good, iface["uuid"])
                        if "domain" in iface:
                            ret_domain.insert(idx_good, iface["domain"])
                        else:
                            ret_domain.insert(idx_good, "")
                        failure[1] = False

        return (ret_ifmac, ret_ifaddr, ret_netmask, ret_domain, ret_networkUuids)

    def dict2obj(d):
        """
        Get a dictionnary and return an object
        """
        from collections import namedtuple

        o = namedtuple("dict2obj", " ".join(list(d.keys())))
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
        """ """

        # Read config from ini file
        orange = self.config.orange
        red = self.config.red

        complete_ctx(ctx)
        filt = {"ctxlocation": ctx.locations}

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
                ret[toUUID(machine.id) + "##" + machine.name] = {
                    "hostname": machine.name,
                    "uuid": toUUID(machine.id),
                }

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
        filt = {"ctxlocation": ctx.locations}

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
        filt = {"ctxlocation": ctx.locations}

        ret = {
            "green": int(
                __computersListQ(
                    ctx, dict(filt, **{"antivirus": "green"}), session, count=True
                )
            ),
            "orange": int(
                __computersListQ(
                    ctx, dict(filt, **{"antivirus": "orange"}), session, count=True
                )
            ),
            "red": int(
                __computersListQ(
                    ctx, dict(filt, **{"antivirus": "red"}), session, count=True
                )
            ),
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

        filt = {"ctxlocation": ctx.locations}

        query1 = __computersListQ(ctx, dict(filt, **{"antivirus": "green"}), session)
        query2 = __computersListQ(ctx, dict(filt, **{"antivirus": "orange"}), session)

        session.close()

        return [machine.id for machine in query1.all()] + [
            machine.id for machine in query2.all()
        ]

    def getMachineListByAntivirusState(self, ctx, groupName):
        session = create_session()

        __computersListQ = self.__getRestrictedComputersListQuery

        complete_ctx(ctx)
        filt = {"ctxlocation": ctx.locations}
        query = __computersListQ(ctx, dict(filt, **{"antivirus": groupName}), session)

        # Limit list according to max_elements_for_static_list param in dyngroup.ini
        limit = DGConfig().maxElementsForStaticList

        query = query.limit(limit)

        ret = {}
        for machine in query.all():
            if machine.name is not None:
                ret[toUUID(machine.id) + "##" + machine.name] = {
                    "hostname": machine.name,
                    "uuid": toUUID(machine.id),
                }

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
        domain = ""
        if machine.domains is not None:
            domain = machine.domains.name
        return domain

    def isComputerNameAvailable(self, ctx, locationUUID, name):
        raise Exception("need to be implemented when we would be able to add computers")

    def _killsession(self, sessionwebservice):
        """
        Destroy a session identified by a session token.

        @param sessionwebservice: session var provided by initSession endpoint.
        @type sessionwebservice: str

        """
        headers = {
            "content-type": "application/json",
            "Session-Token": sessionwebservice,
        }
        url = GlpiConfig.webservices["glpi_base_url"] + "killSession"
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            self.logger.debug("Kill session REST: %s" % sessionwebservice)

    def delMachine(self, uuid):
        """
        Deleting a machine in GLPI (only the flag 'is_deleted' updated)

        @param uuid: UUID of machine
        @type uuid: str

        @return: True if the machine successfully deleted
        @rtype: bool
        """
        authtoken = base64.b64encode(
            bytes(
                "%s:%s"
                % (
                    GlpiConfig.webservices["glpi_username"],
                    GlpiConfig.webservices["glpi_password"],
                ),
                "utf-8",
            )
        )

        headers = {
            "content-type": "application/json",
            "Authorization": "Basic " + authtoken.decode("utf-8"),
        }
        url = GlpiConfig.webservices["glpi_base_url"] + "initSession"
        self.logger.debug("Create session REST")
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sessionwebservice = str(json.loads(r.text)["session_token"])
            self.logger.debug("session %s" % sessionwebservice)
            url = (
                GlpiConfig.webservices["glpi_base_url"]
                + "Computer/"
                + str(fromUUID(uuid))
            )
            headers = {
                "content-type": "application/json",
                "Session-Token": sessionwebservice,
            }
            if GlpiConfig.webservices["purge_machine"]:
                parameters = {"force_purge": "1"}
            else:
                parameters = {"force_purge": "0"}
            r = requests.delete(url, headers=headers, params=parameters)
            if r.status_code == 200:
                self.logger.debug("Machine %s deleted" % str(fromUUID(uuid)))
                self._killsession(sessionwebservice)
                return True
        self._killsession(sessionwebservice)
        return False

    @DatabaseHelper._sessionm
    def addUser(self, session, username, password, entity_rights=None):
        # Check if the user exits or not
        try:
            user = session.query(User).filter_by(name=username).one()
        except NoResultFound:
            user = User()
            user.name = username
        if type(password) is str:
            password = bytes(password, "utf-8")
        user.password = hashlib.sha1(password).hexdigest()
        user.firstname = ""
        user.realname = ""
        user.auths_id = 0
        user.is_deleted = 0
        user.is_active = 1
        user.locations_id = 0
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
        if type(password) is str:
            password = bytes(password, "utf-8")
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
        entity.entities_id = parent_id  # parent
        entity.name = entity_name
        entity.comment = comment
        # Get parent entity object
        parent_entity = (
            session.query(Entities)
            .filter_by(
                id=parent_id,
            )
            .one()
        )
        completename = parent_entity.completename + " > " + entity_name
        entity.completename = completename
        entity.level = parent_entity.level + 1
        session.add(entity)
        session.commit()
        session.flush()
        return True

    @DatabaseHelper._sessionm
    def editEntity(self, session, id, entity_name, parent_id, comment):
        entity = session.query(Entities).filter_by(id=id).one()
        entity.entities_id = parent_id  # parent
        entity.name = entity_name
        entity.comment = comment
        # entity.level = parent_id
        entity = self.updateEntityCompleteName(entity)
        session.commit()
        session.flush()
        return True

    @DatabaseHelper._sessionm
    def updateEntityCompleteName(self, session, entity):
        # Get parent entity object
        parent_entity = session.query(Entities).filter_by(id=entity.entities_id).one()
        completename = parent_entity.completename + " > " + entity.name
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
        location.entities_id = 0  # entity is root
        location.name = name
        location.locations_id = parent_id

        location.comment = comment
        location.level = parent_id
        location.building = ""
        location.room = ""

        # Get parent location object
        parent_location = (
            session.query(Locations)
            .filter_by(
                id=parent_id,
            )
            .one()
        )
        completename = parent_location.completename + " > " + name
        location.completename = completename

        session.add(location)
        session.commit()
        session.flush()
        return True

    @DatabaseHelper._sessionm
    def editLocation(self, session, id, name, parent_id, comment):
        location = session.query(Locations).filter_by(id=id).one()
        location.locations_id = parent_id  # parent
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
        parent_location = (
            session.query(Locations).filter_by(id=location.locations_id).one()
        )
        completename = parent_location.completename + " > " + location.name
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
        return (
            session.query(self.rules)
            .filter_by(sub_type="PluginFusioninventoryInventoryRuleEntity")
            .filter(self.rules.c.name != "Root")
            .order_by(self.rules.c.ranking)
        )

    @DatabaseHelper._sessionm
    def addEntityRule(self, session, rule_data):
        rule = Rule()
        # root entity (this means that rule is appliable on root entity and all subentities)
        rule.entities_id = 0
        rule.sub_type = "PluginFusioninventoryInventoryRuleEntity"
        # Get the last ranking for this class +1
        rank = (
            session.query(func.max(self.rules.c.ranking))
            .filter(self.rules.c.sub_type == "PluginFusioninventoryInventoryRuleEntity")
            .filter(self.rules.c.name != "Root")
            .scalar()
        )
        if rank is None:
            rank = 0
        rule.ranking = rank + 1
        rule.name = rule_data["name"]
        rule.description = rule_data["description"]
        rule.match = rule_data["aggregator"]
        if rule_data["active"] == "on":
            rule.is_active = 1
        else:
            rule.is_active = 0

        session.add(rule)
        session.commit()
        session.flush()

        # Make sure "Root" entity rule ranking is very high
        session.query(Rule).filter_by(
            sub_type="PluginFusioninventoryInventoryRuleEntity", name="Root"
        ).update({"ranking": rule.ranking + 1}, synchronize_session=False)

        # Adding rule criteria

        for i in range(len(rule_data["criteria"])):
            cr = RuleCriterion()
            cr.rules_id = rule.id
            cr.criteria = rule_data["criteria"][i]
            cr.condition = rule_data["operators"][i]
            cr.pattern = rule_data["patterns"][i]
            session.add(cr)
            session.commit()
            session.flush()

        # Adding rule actions

        # If a target entity is specified, add it
        if rule_data["target_entity"] != "-1":
            action = RuleAction()
            action.rules_id = rule.id
            action.action_type = "assign"
            action.field = "entities_id"
            action.value = rule_data["target_entity"]
            session.add(action)

        # If a target location is specified, add it
        if rule_data["target_location"] != "-1":
            action = RuleAction()
            action.rules_id = rule.id
            action.action_type = "assign"
            action.field = "locations_id"
            action.value = rule_data["target_location"]
            session.add(action)

        session.commit()
        session.flush()

        return True

        # it s shit do it from dict directly
        # {'ranking' : 2, 'sub_type': 'PluginFusioninventoryInventoryRuleEntity',
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
        # action_type=regex_result,field=_affect_entity_by_tag, value=?
        # action_type=assign, field=locations_id, value=id

    @DatabaseHelper._sessionm
    def moveEntityRuleUp(self, session, id):
        rule = session.query(Rule).filter_by(id=id).one()
        # get previous rule
        previous = (
            session.query(Rule)
            .filter(Rule.ranking < rule.ranking)
            .filter(Rule.name != "Root")
            .filter(Rule.sub_type == "PluginFusioninventoryInventoryRuleEntity")
            .order_by(Rule.ranking.desc())
            .first()
        )
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
        next_ = (
            session.query(Rule)
            .filter(Rule.ranking > rule.ranking)
            .filter(Rule.name != "Root")
            .filter(Rule.sub_type == "PluginFusioninventoryInventoryRuleEntity")
            .order_by(Rule.ranking.asc())
            .first()
        )
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

        rule.name = rule_data["name"]
        rule.description = rule_data["description"]
        rule.match = rule_data["aggregator"]
        if rule_data["active"] == "on":
            rule.is_active = 1
        else:
            rule.is_active = 0

        session.commit()
        session.flush()

        # Adding rule criteria

        for i in range(len(rule_data["criteria"])):
            cr = RuleCriterion()
            cr.rules_id = rule.id
            cr.criteria = rule_data["criteria"][i]
            cr.condition = rule_data["operators"][i]
            cr.pattern = rule_data["patterns"][i]
            session.add(cr)
            session.commit()
            session.flush()

        # Adding rule actions

        # If a target entity is specified, add it
        if rule_data["target_entity"] != "-1":
            action = RuleAction()
            action.rules_id = rule.id
            action.action_type = "assign"
            action.field = "entities_id"
            action.value = rule_data["target_entity"]
            session.add(action)

        # If a target location is specified, add it
        if rule_data["target_location"] != "-1":
            action = RuleAction()
            action.rules_id = rule.id
            action.action_type = "assign"
            action.field = "locations_id"
            action.value = rule_data["target_location"]
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
        result["active"] = rule.is_active
        result["name"] = rule.name
        result["description"] = rule.description
        result["aggregator"] = rule.match

        result["criteria"] = []
        result["operators"] = []
        result["patterns"] = []

        for cr in criteria:
            result["criteria"].append(cr.criteria)
            result["operators"].append(cr.condition)
            result["patterns"].append(cr.pattern)

        # By default, don't assign entity nor location
        result["target_entity"] = -1
        result["target_location"] = -1

        for action in actions:
            if action.field == "entities_id" and action.action_type == "assign":
                result["target_entity"] = action.value
            if action.field == "locations_id" and action.action_type == "assign":
                result["target_entity"] = action.value

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
        # UPDATE `glpi_computers_pulse`
        # SET `entities_id` = '5' WHERE `id` ='3'

    @DatabaseHelper._sessionm
    def getLocationsForUser(self, session, username):
        try:
            user_id = session.query(User).filter_by(name=username).one().id
        except NoResultFound:
            return []
        entities = []
        for profile in session.query(UserProfile).filter_by(users_id=user_id):
            entities += [
                {
                    "entity_id": profile.entities_id,
                    "profile": profile.profiles_id,
                    "is_recursive": profile.is_recursive,
                    "is_dynamic": profile.is_dynamic,
                }
            ]
        return entities

    @DatabaseHelper._sessionm
    def setLocationsForUser(self, session, username, profiles):
        user_id = session.query(User).filter_by(name=username).one().id
        # Delete all user entity profiles
        session.query(UserProfile).filter_by(users_id=user_id).delete()

        for attr in profiles:
            p = UserProfile()
            p.users_id = user_id
            p.profiles_id = attr["profile"]
            p.entities_id = attr["entity_id"]
            p.is_recursive = attr["is_recursive"]
            p.is_dynamic = attr["is_dynamic"]
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
        hive = full_key.split("\\")[0]
        key = full_key.split("\\")[-1]
        path = full_key.replace(hive + "\\", "").replace("\\" + key, "")
        path = "/" + path + "/"
        # Get registry_id
        try:
            registry_id = (
                session.query(Registries)
                .filter_by(hive=hive, path=path, key=key)
                .first()
                .id
            )
            if registry_id:
                return registry_id
        except:
            return False

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
        hive = full_key.split("\\")[0]
        key = full_key.split("\\")[-1]
        path = full_key.replace(hive + "\\", "").replace("\\" + key, "")
        path = "/" + path + "/"
        # Insert in database
        registry = Registries()
        registry.name = key_name
        # Get collects_id
        try:
            collects_id = (
                session.query(Collects)
                .filter_by(name="PulseRegistryCollects")
                .first()
                .id
            )
        except:
            return False
        registry.plugin_fusioninventory_collects_id = collects_id
        registry.hive = hive
        registry.path = path
        registry.key = key
        session.add(registry)
        session.commit()
        session.flush()
        return True

    def getAllOsVersions(self, ctx, filt=""):
        """@return: all os versions defined in the GLPI database"""
        session = create_session()
        query = session.query(OsVersion)
        if filter != "":
            query = query.filter(OsVersion.name.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    def getAllArchitectures(self, ctx, filt=""):
        """@return: all hostnames defined in the GLPI database"""
        session = create_session()
        query = session.query(OsArch)
        if filter != "":
            query = query.filter(OsArch.name.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    def getAllNamePrinters(self, ctx, filt=""):
        """@return: all printer name in the GLPI database"""
        session = create_session()
        query = session.query(Printers)
        if filter != "":
            query = query.filter(Printers.name.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    def getAllSerialPrinters(self, ctx, filt=""):
        """@return: all printer serial in the GLPI database"""
        session = create_session()
        query = session.query(Printers)
        if filter != "":
            query = query.filter(Printers.serial.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    def getAllNamePeripherals(self, ctx, filt=""):
        """@return: all peripheral name in the GLPI database"""
        session = create_session()
        query = session.query(Peripherals)
        if filter != "":
            query = query.filter(Peripherals.name.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    def getAllSerialPeripherals(self, ctx, filt=""):
        """@return: all peripheral serials in the GLPI database"""
        session = create_session()
        query = session.query(Peripherals)
        if filter != "":
            query = query.filter(
                or_(
                    Peripherals.serial.like("%" + filt + "%"),
                    Peripherals.name.like("%" + filt + "%"),
                )
            )
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def addRegistryCollectContent(self, session, computers_id, registry_id, key, value):
        """
        Add registry collect content

        @param computers_id: the computer_id from glpi_computers_pulse
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
        try:
            contents_id = (
                session.query(RegContents)
                .filter_by(
                    computers_id=computers_id,
                    plugin_fusioninventory_collects_registries_id=registry_id,
                    key=key,
                )
                .first()
                .id
            )
            if contents_id:
                # Update database
                session.query(RegContents).filter_by(id=contents_id).update(
                    {"value": str(value)}
                )
                session.commit()
                session.flush()
                return True
        except AttributeError:
            # Insert in database
            regcontents = RegContents()
            regcontents.computers_id = int(computers_id)
            regcontents.plugin_fusioninventory_collects_registries_id = int(registry_id)
            regcontents.key = str(key)
            regcontents.value = str(value)
            session.add(regcontents)
            session.commit()
            session.flush()
            return True

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

        sql = """SELECT
  glpi_operatingsystems.name as os,
  glpi_operatingsystemversions.name as version_name
FROM
  glpi_computers_pulse
INNER JOIN
  glpi_operatingsystems
ON
  operatingsystems_id = glpi_operatingsystems.id

left JOIN
  glpi_operatingsystemversions
ON
  operatingsystemversions_id = glpi_operatingsystemversions.id
ORDER BY
 glpi_operatingsystems.name, glpi_operatingsystemversions.name ASC;"""
        res = session.execute(sql)
        result = [{"os": os, "version": version, "count": 1} for os, version in res]

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
                if (
                    element["os"] == machine["os"]
                    and element["version"] == machine["version"]
                ):
                    machine["count"] = int(machine["count"]) + int(element["count"])
                    return list

            # If no machine is matching with the element, the element is added
            list.append(element)
            return list

        final_list = []
        for machine in result:
            if machine["version"] is None:
                machine["version"] = "00.00"

            if machine["os"].startswith("Debian"):
                machine["os"] = "Debian"
                try:
                    machine["version"] = machine["version"].split(" ")[0]
                except AttributeError:
                    machine["version"] = ""
            elif machine["os"].startswith("Microsoft"):
                machine["os"] = machine["os"].split(" ")[1:3]
                machine["os"] = " ".join(machine["os"])
            elif machine["os"].startswith("Ubuntu"):
                machine["os"] = "Ubuntu"
                # We want just the XX.yy version number
                try:
                    machine["version"] = machine["version"].split(" ")[0].split(".")
                except AttributeError:
                    machine["version"] = ""
                if len(machine["version"]) >= 2:
                    machine["version"] = machine["version"][0:2]
                    machine["version"] = ".".join(machine["version"])
            elif machine["os"].startswith("Mageia"):
                machine["os"] = machine["os"].split(" ")[0]
            elif machine["os"].startswith("Unknown"):
                machine["os"] = machine["os"].split("(")[0]
                machine["version"] = ""
            elif machine["os"].startswith("CentOS"):
                machine["os"] = machine["os"].split(" ")[0]
                try:
                    machine["version"] = (
                        machine["version"].split("(")[0].split(".")[0:2]
                    )
                    machine["version"] = ".".join(machine["version"])
                except AttributeError:
                    machine["version"] = ""

            elif machine["os"].startswith("macOS") or machine["os"].startswith("OS X"):
                try:
                    machine["version"] = (
                        machine["version"].split(" (")[0].split(".")[0:2]
                    )
                    machine["version"] = ".".join(machine["version"])
                except AttributeError:
                    machine["version"] = ""
            else:
                pass

            final_list = _add_element(machine, final_list)
        return final_list

    @DatabaseHelper._sessionm
    def get_machines_with_os_and_version(self, session, oslocal, version=""):
        """This function returns a list of id of selected OS for dashboard
        Params:
            os: string which contains the searched OS
            version: string which contains the searched version
        Returns:
            list of all the machines with specified OS and specified version
        """

        sql = (
            session.query(Machine.id, Machine.name)
            .join(OS, OS.id == Machine.operatingsystems_id)
            .outerjoin(OsVersion, OsVersion.id == Machine.operatingsystemversions_id)
            .filter(
                and_(OS.name.like("%" + oslocal + "%")),
                OsVersion.name.like("%" + version + "%"),
            )
        )

        sql = sql.filter(Machine.is_deleted == 0, Machine.is_template == 0)
        sql = self.__filter_on(sql)
        res = session.execute(sql)

        result = [{"id": a, "hostname": b} for a, b in res]

        return result

    @DatabaseHelper._sessionm
    def get_machine_for_hostname(self, session, strlisthostname, filter, start, end):
        sqlrequest = """
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
                    and  `glpi_computers`.`name` in (%s);""" % (
            strlisthostname
        )
        id = []
        name = []
        description = []
        os = []
        typemache = []
        contact = []
        entity = []
        result = []
        res = session.execute(sqlrequest)
        for element in res:
            id.append(element.id)
            name.append(element.name)
            description.append(element.description)
            os.append(element.os)
            typemache.append(element.type)
            contact.append(element.contact)
            entity.append(element.entity)
        result.append(id)
        result.append(name)
        result.append(description)
        result.append(os)
        result.append(typemache)
        result.append(contact)
        result.append(entity)
        return result

    @DatabaseHelper._sessionm
    def get_machine_with_update(self, session, kb):
        """
        Get machines with a specific update.

        Args:
            session: Database session object.
            kb (str): The update code (KB code).

        Returns:
            List: A list containing UUIDs, hostnames, entities, update names, and update codes.
        """
        try:
            sqlrequest = """
                SELECT
                    gc.id AS uuid_inventory,
                    gc.name AS hostname,
                    ge.completename AS entity,
                    gs.name AS kb,
                    SUBSTR(gs.name, LOCATE('KB', gs.name)+2, 7) AS numkb
                FROM
                    glpi_computers gc
                    INNER JOIN
                    glpi_computers_softwareversions gcs ON gc.id = gcs.computers_id
                    INNER JOIN
                    glpi_softwareversions gsv ON gcs.softwareversions_id = gsv.id
                    INNER JOIN
                    glpi_softwares gs ON gsv.softwares_id = gs.id
                    INNER JOIN
                    glpi_entities ge ON gc.entities_id = ge.id
                WHERE
                    gs.name LIKE '%%Update (KB%s)%%';""" % (
                kb
            )
            uuid_inventory = []
            hostname = []
            entity = []
            kb = []
            numkb = []
            result = []
            res = session.execute(sqlrequest)
            for element in res:
                uuid_inventory.append(element.uuid_inventory)
                hostname.append(element.hostname)
                entity.append(element.entity)
                kb.append(element.kb)
                numkb.append(element.numkb)
            result.append(uuid_inventory)
            result.append(hostname)
            result.append(entity)
            result.append(kb)
            result.append(numkb)
            return result
        except Exception as e:
            self.logger.error(
                "\n erreur with the backtrace \n%s" % (traceback.format_exc())
            )
            return []

    @DatabaseHelper._sessionm
    def get_count_machine_with_update(self, session, kb, uuid, hlist=""):
        """
        Get the count of machines with the update specified with its KB (Knowledge Base).
        Args:
            session (Session): SQLAlchemy session to interact with the db
            kb (str): The KB name (Knowledge Base) we are looking for.
            uuid (str): the entity uuid on which we have to search.
            hlist (str): ids of machines excluded in this search because they are already counted in history
        Returns:
            dict: A dict containing the count of machines with the specific update.
            The key "nb_machines" contains the count of machine.
        """
        if hlist == "":
            hlist = '""'

        filter_on = ""
        if self.config.filter_on is not None:
            for key in self.config.filter_on:
                if key == "state":
                    filter_on = "%s AND gcp.states_id in (%s)" % (
                        filter_on,
                        ",".join(self.config.filter_on[key]),
                    )
                if key == "type":
                    filter_on = "%s AND gcp.computertypes_id in (%s)" % (
                        filter_on,
                        ",".join(self.config.filter_on[key]),
                    )
                if key == "entity":
                    filter_on = "%s AND gcp.entities_id in (%s)" % (
                        filter_on,
                        ",".join(self.config.filter_on[key]),
                    )

        sqlrequest = """
            SELECT
                COUNT(*) AS nb_machines
            FROM
                glpi_computers_pulse gcp
                    JOIN
                glpi_computers_softwareversions gcsv ON gcp.id = gcsv.computers_id
                    JOIN
                glpi_softwareversions gsv ON gcsv.softwareversions_id = gsv.id
                    JOIN
                glpi_softwares gs ON gs.id = gsv.softwares_id
                    INNER JOIN
                glpi_entities AS ge ON ge.id = gcp.entities_id
            WHERE
                ge.id = %s
            AND
                gcp.is_deleted = 0 AND gcp.is_template = 0
            AND
                gsv.name LIKE '%s'
            AND
                (gsv.comment LIKE '%%Update%%' OR COALESCE(gsv.comment, '') = '')
            AND
                gcp.id not in (%s)
            %s;""" % (
            uuid.replace("UUID", ""),
            kb,
            hlist,
            filter_on,
        )
        result = {}
        res = session.execute(sqlrequest)
        for element in res:
            result["nb_machines"] = element.nb_machines
        return result

    @DatabaseHelper._sessionm
    def get_machine_for_id(self, session, strlistuuid, filter, start, limit):
        criterion = filter["criterion"]
        filter = filter["filter"]

        query = (
            session.query(Machine.id)
            .add_column(Machine.name)
            .add_column(Machine.comment.label("description"))
            .add_column(OS.name.label("os"))
            .add_column(self.glpi_computertypes.c.name.label("type"))
            .add_column(Machine.contact.label("contact"))
            .add_column(self.entities.c.name.label("entity"))
            .join(self.os)
            .join(
                self.glpi_computertypes,
                Machine.computertypes_id == self.glpi_computertypes.c.id,
            )
            .join(Entities, Entities.id == Machine.entities_id)
            .filter(Machine.id.in_(strlistuuid))
        )

        if filter == "infos" and criterion != "":
            query = query.filter(
                or_(
                    Machine.name.contains(criterion),
                    Machine.comment.contains(criterion),
                    OS.name.contains(criterion),
                    self.glpi_computertypes.c.name.contains(criterion),
                    Machine.contact.contains(criterion),
                    self.entities.c.name.contains(criterion),
                )
            )

        query = self.__filter_on(query)
        id = []
        name = []
        description = []
        os = []
        typemache = []
        contact = []
        entity = []
        result = []
        if filter == "infos":
            nb = query.count()
            query = query.offset(start).limit(limit)
        else:
            nb = 0

        query = query.order_by(Machine.name)
        res = query.all()
        session.commit()
        session.flush()

        if res is not None:
            for element in res:
                id.append(element.id)
                name.append(element.name)
                description.append(element.description)
                os.append(element.os)
                typemache.append(element.type)
                contact.append(element.contact)
                entity.append(element.entity)
            result.append(id)
            result.append(name)
            result.append(description)
            result.append(os)
            result.append(typemache)
            result.append(contact)
            result.append(entity)

        result1 = {"total": nb, "listelet": result}

        return result1

    @DatabaseHelper._sessionm
    def get_ancestors(self, session, uuid):
        id = uuid.split("UUID")[1]
        # Get the entity ancestors
        query = (
            session.query(Entities.ancestors_cache).filter(Entities.id == id).first()
        )
        # query can have 3 kind of datas:
        # (None) None value (this is the case for the root entity )
        # ('[0, 1]') list serialized, if the entity has less than 3 ancestors
        # ('{"0":"0", "1": "1", "2":"2"}') dict serialized, if the entity has more than 2 ancestors

        if query[0] is not None:
            # Parse the elements in the initial order
            decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)
            query = decoder.decode(query[0])
        else:
            query = []

        result = []
        if type(query) is dict:
            for key in query:
                # get the key, tke key = the value
                result.append(int(key))
        else:
            result = [int(id) for id in query]
        return result

    @DatabaseHelper._sessionm
    def get_count_installed_updates_by_machines(self, session, ids):
        """
        Récupère le nombre de mises à jour installées par machine pour une liste d'identifiants de machine donnée.

        Args:
            session (Session): Session SQLAlchemy pour interagir avec la base de données.
            ids (list[str]): Liste d'identifiants de machines.

        Returns:
            dict: Un dictionnaire contenant les informations sur les mises à jour installées par machine.
                Les clés du dictionnaire sont des identifiants de machine (au format "UUID{id}").
                Chaque valeur est un autre dictionnaire contenant les détails suivants :
                    - "id": L'identifiant de la machine.
                    - "cn": Le nom de la machine.
                    - "installed": Le nombre de mises à jour installées sur la machine.
        """
        try:
            ids = "(%s)" % ",".join([id for id in ids if id != ""]).replace("UUID", "")
            sql = """SELECT
                        gc.id AS id,
                        gc.name AS name,
                        COUNT(gs.id) AS installed
                    FROM
                        glpi_computers gc
                            JOIN
                        glpi_computers_softwareversions gcs ON gc.id = gcs.computers_id
                            JOIN
                        glpi_softwareversions gsv ON gcs.softwareversions_id = gsv.id
                            JOIN
                        glpi_softwares gs ON gs.id = gsv.softwares_id
                    WHERE
                        gc.id IN %s
                            AND gsv.name REGEXP '^[0-9]{7}$'
                            AND (gsv.comment LIKE '%%Update%%'
                            OR COALESCE(gsv.comment, '') = '')
                    GROUP BY gc.id;""" % (
                ids
            )
            engine_of_session = session.bind
            datas = session.execute(sql)
            result = {}
            for element in datas:
                result["UUID%d" % element.id] = {
                    "id": element.id,
                    "cn": element.name,
                    "installed": element.installed,
                }
            return result
        except Exception as e:
            self.logger.error(f"We failed with the error \n {traceback.format_exc()}")
            return {}

    @DatabaseHelper._sessionm
    def getComputerFilteredByCriterion(self, session, ctx, criterion, values):
        query = session.query(Machine.id, Machine.name)

        if criterion == "Computer name":
            query = query.filter(and_(Machine.name.in_(values)))

        elif criterion == "Register key":
            pass

        elif criterion == "Peripheral serial":
            query = query.filter(and_(Peripherals.serial.in_(values)))
            query = query.join(
                Computersitems, Machine.id == Computersitems.computers_id
            )
            query = query.join(
                Peripherals,
                and_(
                    Computersitems.items_id == Peripherals.id,
                    Computersitems.itemtype == "Peripheral",
                ),
            )

        elif criterion == "State":
            query = query.filter(and_(State.name.in_(values)))
            query = query.join(State, State.id == Machine.states_id)

        elif criterion == "Location":
            query = query.filter(and_(Locations.name.in_(values)))
            query = query.join(Locations, Locations.id == Machine.locations_id)

        elif criterion == "Printer serial":
            query = query.filter(and_(Printers.serial.in_(values)))
            query = query.join(
                Computersitems, Machine.id == Computersitems.computers_id
            )
            query = query.join(
                Printers,
                and_(
                    Computersitems.items_id == Printers.id,
                    Computersitems.itemtype == "Printer",
                ),
            )

        elif criterion == "Printer name":
            query = query.filter(and_(Printers.name.in_(values)))
            query = query.join(
                Computersitems, Machine.id == Computersitems.computers_id
            )
            query = query.join(
                Printers,
                and_(
                    Computersitems.items_id == Printers.id,
                    Computersitems.itemtype == "Printer",
                ),
            )

        elif criterion == "OS Version":
            query = query.filter(and_(OsVersion.name.in_(values)))
            query = query.join(
                OsVersion, OsVersion.id == Machine.operatingsystemversions_id
            )

        elif criterion == "Installed version":
            pass

        elif criterion == "Description":
            query = query.filter(and_(Machine.comment.in_(values)))

        elif criterion == "System model":
            query = query.filter(and_(Model.name.in_(values)))
            query = query.join(Model, Model.id == Machine.computermodels_id)

        elif criterion == "Inventory number":
            query = query.filter(and_(Machine.otherserial.in_(values)))

        elif criterion == "Register key value":
            pass

        elif criterion == "System type":
            query = query.filter(self.glpi_computertypes.c.name.in_(values))
            query = query.join(
                self.glpi_computertypes,
                Machine.computertypes_id == self.glpi_computertypes.c.id,
            )

        elif criterion == "Online computer":
            # for csv import that doesn't make any sense
            online_machines = [
                int(id)
                for id in XmppMasterDatabase().getidlistPresenceMachine(presence=True)
                if id != "UUID" and id != ""
            ]
            query = query.filter(and_(Machine.id.in_(online_machines)))

        elif criterion == "Operating system":
            query = query.filter(and_(OS.name.in_(values)))
            query = query.join(OS, OS.id == Machine.operatingsystems_id)

        elif criterion == "Contact number":
            query = query.filter(and_(Machine.contact_num.in_(values)))

        elif criterion == "Service Pack":
            query = query.filter(and_(OsSp.name.in_(values)))
            query = query.join(OsSp, OsSp.id == Machine.operatingsystemservicepacks_id)

        elif criterion == "Contact":
            query = query.filter(and_(Machine.contact.in_(values)))

        elif criterion == "Architecture":
            query = query.filter(and_(OsArch.name.in_(values)))
            query = query.join(
                OsArch, OsArch.id == Machine.operatingsystemarchitectures_id
            )

        elif criterion == "Installed software (specific version)":
            pass

        elif criterion == "Last Logged User":
            query = query.filter(and_(Machine.contact.in_(values)))

        elif criterion == "User location":
            query = query.filter(and_(Locations.name.in_(values)))
            query = query.join(User, User.id == Machine.users_id)
            query = query.join(Locations, Locations.id == User.locations_id)

        elif criterion == "Vendors":
            pass

        elif criterion == "Peripheral name":
            query = query.filter(and_(Peripherals.name.in_(values)))
            query = query.join(
                Computersitems, Machine.id == Computersitems.computers_id
            )
            query = query.join(
                Peripherals,
                and_(
                    Computersitems.items_id == Peripherals.id,
                    Computersitems.itemtype == "Peripheral",
                ),
            )

        elif criterion == "Entity":
            query = query.filter(
                or_(Entities.id.in_(values), Entities.completename.in_(values))
            )
            query = query.join(Entities, Entities.id == Machine.entities_id)

        elif criterion == "Owner of the machine":
            pass

        elif criterion == "Software versions":
            query = query.filter(and_(SoftwareVersion.name.in_(values)))
            query = query.group_by(Machine.id)
            query.join(InstSoftware, InstSoftware.items_id == Machine.id)
            query.join(
                SoftwareVersion, InstSoftware.softwareversions_id == SoftwareVersion.id
            )

        elif criterion == "System manufacturer":
            query = query.filter(and_(Manufacturers.name.in_(values)))
            query = query.join(
                Manufacturers, Manufacturers.id == Machine.manufacturers_id
            )

        query = query.filter(and_(Machine.is_deleted == 0, Machine.is_template == 0))
        response = query.all()

        result = {}
        for element in response:
            uuid = "UUID%i" % element.id
            name = element.name
            result["UUID%i" % element.id] = {"uuid": uuid, "hostname": name}
        return result

    @DatabaseHelper._sessionm
    def get_plugin_inventory_state(self, session, plugin_name=""):
        where_clause = ""
        if plugin_name != "":
            where_clause = "where directory = '%s'" % plugin_name
        query = session.execute(
            """select id, directory, name, state from glpi_plugins %s""" % where_clause
        )

        result = {}

        for element in query:
            result[element[1]] = {
                "id": element[0],
                "directory": element[1],
                "name": element[2],
                "state": "enabled" if element[3] == 1 else "disabled",
            }
        return result

    @DatabaseHelper._sessionm
    def get_os_update_major_stats(self, session):
        """
        Récupère les statistiques de mise à jour majeure des systèmes d'exploitation Windows 10 et Windows 11.

        Cette fonction retourne un dictionnaire contenant le nombre total de machines Windows 10 et Windows 11, ainsi que des statistiques
        par entité pour les mises à jour nécessaires. Les résultats incluent également un calcul de conformité pour chaque entité.

        Args:
            session (sqlalchemy.orm.session.Session): La session de base de données utilisée pour exécuter les requêtes SQL.

        Returns:
            dict: Un dictionnaire contenant les statistiques de mise à jour des systèmes d'exploitation. La structure du dictionnaire est :
                {
                    "entity": {
                        "<complete_name>": {
                            "name": "<entity_name>",
                            "count": <total_count>,
                            "W10to10": <count_windows_10_not_22H2>,
                            "W10to11": <count_windows_10_22H2>,
                            "W11to11": <count_windows_11_not_24H2>,
                            "conformite": <conformity_percentage>
                        }
                    }
                }

        Raises:
            Exception: En cas d'erreur lors de l'exécution des requêtes SQL.
        """
        try:
            # Dictionnaire final des résultats
            cols=["W10to10", "W10to11", "W11to11"]
            results = {"entity": {}}
            total_os_sql =f'''
                        SELECT
                                e.name AS entity_name,
                                e.completename AS complete_name,
                                COUNT(*) AS count
                            FROM
                                glpi.glpi_computers AS c
                                    INNER JOIN
                                glpi.glpi_items_operatingsystems AS io ON c.id = io.items_id
                                    INNER JOIN
                                glpi.glpi_entities AS e ON e.id = c.entities_id
                                    INNER JOIN
                                glpi.glpi_operatingsystems AS os ON os.id = io.operatingsystems_id
                                    INNER JOIN
                                glpi.glpi_operatingsystemversions AS v ON v.id = io.operatingsystemversions_id
                            WHERE
                                os.name LIKE '%Windows%'
                            GROUP BY e.id
                            ORDER BY e.name;
            '''
            total_os_result = session.execute(total_os_sql).fetchall()
            for row in total_os_result:
                results["entity"].setdefault(row.complete_name, {"count" :  int(row.count)})
                # results["entity"][row.complete_name]["count"] = int(row.count)

            # Requête pour les statistiques par entité
            entity_sql = '''
                    SELECT
                        e.id AS entity_id,
                        e.name AS entity_name,
                        e.completename AS complete_name,
                        COUNT(*) AS nbwin,
                        v.name as ver,
                        os.name as namewin,
                        CASE
                            WHEN
                                os.name LIKE '%Windows 10%'
                                    AND v.name != '22H2'
                            THEN
                                'W10to10'
                            WHEN
                                os.name LIKE '%Windows 10%'
                                    AND v.name = '22H2'
                            THEN
                                'W10to11'
                            WHEN
                                os.name LIKE '%Windows 11%'
                                    AND v.name != '24H2'
                            THEN
                                'W11to11'
                            ELSE 'not_win'
                        END AS os
                    FROM
                        glpi.glpi_computers AS c
                            INNER JOIN
                        glpi.glpi_items_operatingsystems AS io ON c.id = io.items_id
                            INNER JOIN
                        glpi.glpi_entities AS e ON e.id = c.entities_id
                            INNER JOIN
                        glpi.glpi_operatingsystems AS os ON os.id = io.operatingsystems_id
                            INNER JOIN
                        glpi.glpi_operatingsystemversions AS v ON v.id = io.operatingsystemversions_id
                    WHERE
                        os.name LIKE '%Windows%'
                    GROUP BY e.name, os
                    ORDER BY e.name;
            '''
            entity_result = session.execute(entity_sql).fetchall()

            for row in entity_result:
                # initialisation
                results["entity"].setdefault(row.complete_name, {})
                results["entity"][row.complete_name]["name"]=row.entity_name
                results["entity"][row.complete_name][row.os ]=int(row.nbwin)
                results["entity"][row.complete_name]["entity_id" ]=int(row.entity_id)
            # Calcul de la conformiténbwin
            for entity, data in results["entity"].items():
                total=results["entity"][entity]["count"]
                non_conforme = sum(data.get(key, 0) for key in cols)
                results["entity"][entity]["conformite"] = round(((non_conforme - total) / total * 100) if non_conforme > 0 else 0, 2)
            # Copier les clés existantes avant d'itérer
            existing_entities = list(results["entity"].keys())

            for entity in existing_entities:  # Itérer sur la copie des clés
                for col in cols:
                    if col not in results["entity"][entity]:
                        results["entity"][entity][col] = 0

            return results

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques de mise à jour des OS : {str(e)}")
            logger.error(f"Traceback : {traceback.format_exc()}")
            return {}


    @DatabaseHelper._sessionm
    def get_os_update_major_details(self, session, entity_id, filter="", start=0, limit=-1, colonne=True):
        """
        Récupère les détails des machines avec des systèmes d'exploitation Windows à partir de la base de données GLPI.

        Cette fonction exécute une requête SQL pour récupérer des informations sur les machines
        avec des systèmes d'exploitation Windows, y compris une colonne calculée 'os' qui
        catégorise la version du système d'exploitation et indique les mises à jour majeures
        nécessaires entre la version actuelle et la prochaine mise à jour majeure. Les résultats
        peuvent être retournés soit dans un format détaillé ligne par ligne, soit dans un format
        en colonnes, selon le paramètre 'colonne'.

        Paramètres :
            session (Session) : Objet de session SQLAlchemy pour l'interaction avec la base de données.
            entity_id (int) : L'ID de l'entité pour filtrer les résultats.
            filter (str) : Critères de filtrage supplémentaires pour filtrer par nom de machine.
            start (int) : Le décalage pour commencer à retourner les lignes.
            limit (int) : Le nombre maximum de lignes à retourner. Si -1, pas de limitation.
            colonne (bool) : Si True, retourne les résultats dans un format en colonnes. La valeur par défaut est True.

        Retourne :
            dict : Un dictionnaire contenant le nombre de lignes correspondantes et soit
                   des résultats détaillés ligne par ligne, soit des résultats en colonnes,
                   selon le paramètre 'colonne'. La colonne 'os' indique les mises à jour majeures
                   nécessaires, telles que 'W10to10' pour une mise à jour entre versions de Windows 10,
                   'W10to11' pour une mise à jour de Windows 10 vers Windows 11, et 'W11to11' pour une
                   mise à jour entre versions de Windows 11.
        """

        # Base SQL query
        total_os_sql = '''
            SELECT
                SQL_CALC_FOUND_ROWS
                c.id as id_machine,
                c.name AS machine,
                os.name AS platform,
                v.name AS version,
                -- e.id AS entity_id,
                -- e.name AS entity_name,
                -- e.completename AS complete_name,
                CASE
                    WHEN os.name LIKE '%Windows 10%' AND v.name != '22H2' THEN 'W10to10'
                    WHEN os.name LIKE '%Windows 10%' AND v.name = '22H2' THEN 'W10to11'
                    WHEN os.name LIKE '%Windows 11%' AND v.name != '24H2' THEN 'W11to11'
                    ELSE 'not_win'
                END AS 'update'
            FROM
                glpi.glpi_computers AS c
                INNER JOIN glpi.glpi_items_operatingsystems AS io ON c.id = io.items_id
                INNER JOIN glpi.glpi_entities AS e ON e.id = c.entities_id
                INNER JOIN glpi.glpi_operatingsystems AS os ON os.id = io.operatingsystems_id
                INNER JOIN glpi.glpi_operatingsystemversions AS v ON v.id = io.operatingsystemversions_id
            WHERE
                os.name LIKE '%Windows%' AND e.id = :entity_id
        '''

        # Add filter condition if filter is not empty
        if filter:
            total_os_sql += " AND c.name LIKE :filter"

        # Add ORDER BY and LIMIT/OFFSET if limit is not -1
        total_os_sql += " ORDER BY  c.name"
        if limit != -1:
            total_os_sql += " LIMIT :limit OFFSET :start"

        # Convert to text for parameter binding
        total_os_sql = text(total_os_sql)

        # Log the SQL query with parameters
        logger.debug("Executing SQL query: %s", total_os_sql)
        logger.debug("With parameters: entity_id=%s, filter=%s, limit=%s, start=%s", entity_id, f"%{filter}%", limit, start)

        # Execute the SQL query with parameters
        entity_result = session.execute(total_os_sql, {
            'entity_id': entity_id,
            'filter': f"%{filter}%",
            'limit': limit,
            'start': start
        }).fetchall()

        # Count the total number of matching elements using FOUND_ROWS()
        sql_count = text("SELECT FOUND_ROWS();")
        ret_count = session.execute(sql_count).scalar()

        # Extract common fields from the first row
        # common_entity_id = entity_result[0].entity_id if entity_result else ""
        # common_entity_name = entity_result[0].entity_name if entity_result else ""
        # common_complete_name = entity_result[0].complete_name if entity_result else ""

        # Prepare the result dictionary with the count of matching rows and common fields
        result = {
            'nb_machine': ret_count,
            # 'entity_id': common_entity_id,
            # 'entity_name': common_entity_name,
            # 'complete_name': common_complete_name
        }

        if colonne:
            # If colonne is True, return results in columnar format
            result.update({
                'id_machine': [row.id_machine if row.id_machine is not None else "" for row in entity_result],
                'machine': [row.machine if row.machine is not None else "" for row in entity_result],
                'platform': [row.platform if row.platform is not None else "" for row in entity_result],
                'version': [row.version if row.version is not None else "" for row in entity_result],
                'update': [row.update  if row.update is not None else "" for row in entity_result]
            })
        else:
            # If colonne is False, return detailed results in row-wise format
            result['details'] = [
                {
                    'id_machine': row.id_machine if row.id_machine is not None else "",
                    'machine': row.machine if row.machine is not None else "",
                    'platform': row.platform if row.platform is not None else "",
                    'version':  row.version if row.version is not None else "",
                    'update': row.update if row.update is not None else ""
                }
                for row in entity_result
            ]

        return result


# Class for SQLalchemy mapping
class Machine(object):
    __tablename__ = "glpi_computers_pulse"

    def getUUID(self):
        return toUUID(self.id)

    def toH(self):
        return {"hostname": self.name, "uuid": toUUID(self.id)}

    def to_a(self):
        owner_login, owner_firstname, owner_realname = Glpi93().getMachineOwner(self)
        return [
            ["id", self.id],
            ["name", self.name],
            ["comments", self.comment],
            ["serial", self.serial],
            ["otherserial", self.otherserial],
            ["contact", self.contact],
            ["contact_num", self.contact_num],
            ["owner", owner_login],
            ["owner_firstname", owner_firstname],
            ["owner_realname", owner_realname],
            # ['tech_num',self.tech_num],
            ["os", self.operatingsystems_id],
            ["os_version", self.operatingsystemversions_id],
            ["os_sp", self.operatingsystemservicepacks_id],
            ["os_arch", self.operatingsystemarchitectures_id],
            ["license_number", self.license_number],
            ["license_id", self.license_id],
            ["location", self.locations_id],
            ["domain", self.domains_id],
            ["network", self.networks_id],
            ["model", self.computermodels_id],
            ["type", self.computertypes_id],
            ["entity", self.entities_id],
            ["uuid", Glpi93().getMachineUUID(self)],
        ]


class Entities(object):
    def toH(self):
        return {
            "uuid": toUUID(self.id),
            "name": self.name,
            "completename": self.completename,
            "comments": self.comment,
            "level": self.level,
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
    to_be_exported = ["last_contact"]


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
            "uuid": toUUID(self.id),
            "name": self.name,
            "ifaddr": self.ip,
            "ifmac": self.mac,
            "netmask": noNone(self.netmask),
            "gateway": self.gateway,
            "subnet": self.subnet,
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


class OsArch(object):
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


class Registries(object):
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


class Computersitems(DbTOA):
    pass


class Computersviewitemsprinter(DbTOA):
    pass


class Computersviewitemsperipheral(DbTOA):
    pass


class Peripheralsmanufacturers(DbTOA):
    pass


class Monitors(DbTOA):
    pass


class Phones(DbTOA):
    pass


class Printers(DbTOA):
    pass


class Peripherals(DbTOA):
    pass
