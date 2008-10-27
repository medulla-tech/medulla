#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
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

# TODO rename location into entity (and locations in location)
from mmc.support.config import PluginConfig
from mmc.support.mmctools import Singleton, xmlrpcCleanup
from mmc.plugins.base import ComputerI
from mmc.plugins.glpi.config import GlpiConfig
from mmc.plugins.glpi.utilities import unique, same_network, complete_ctx, onlyAddNew
from mmc.plugins.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper
from mmc.plugins.pulse2.group import ComputerGroupManager

from ConfigParser import NoOptionError

from sqlalchemy import *
from sqlalchemy.orm import *

import logging
import re
from sets import Set

SA_MAJOR = 0
SA_MINOR = 4

class Glpi(DyngroupDatabaseHelper):
    """
    Singleton Class to query the glpi database.

    """
    is_activated = False

    def db_check(self):
        if not self.__checkSqlalchemy():
            self.logger.error("Sqlalchemy version error : is not %s.%s.* version" % (SA_MAJOR, SA_MINOR))
            return False

        conn = self.connected()
        if conn:
            self.logger.error("Can't connect to database (s=%s, p=%s, b=%s, l=%s, p=******). Please check glpi.ini." % (self.config.dbhost, self.config.dbport, self.config.dbbase, self.config.dbuser))
            return False

        return True

    def __checkSqlalchemy(self):
        try:
            import sqlalchemy
            a_version = sqlalchemy.__version__.split('.')
            if len(a_version) > 2 and str(a_version[0]) == str(SA_MAJOR) and str(a_version[1]) == str(SA_MINOR):
                return True
        except:
            pass
        return False

    def activate(self, conffile = None):
        self.logger = logging.getLogger()
        DyngroupDatabaseHelper.init(self)
        if self.is_activated:
            self.logger.info("Glpi don't need activation")
            return None
        self.logger.info("Glpi is activating")
        self.config = GlpiConfig("glpi", conffile)
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, echo = True)
        self.metadata = MetaData(self.db)
        self.initMappers()
        self.metadata.create_all()
        self.is_activated = True
        self.logger.debug("Glpi finish activation")

    def connected(self):
        try:
            if (self.db != None) and (self.session != None):
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

        # entity
        self.location = Table("glpi_entities", self.metadata, autoload = True)
        mapper(Location, self.location)

        # location
        self.locations = Table("glpi_dropdown_locations", self.metadata, autoload = True)
        mapper(Locations, self.locations)

        # processor
        self.processor = Table("glpi_device_processor", self.metadata, autoload = True)
        mapper(Processor, self.processor)

        # network
        self.network = Table("glpi_networking_ports", self.metadata,
            Column('on_device', Integer, ForeignKey('glpi_computers.ID')),
            autoload = True)
        mapper(Network, self.network)

        self.net = Table("glpi_dropdown_network", self.metadata, autoload = True)
        mapper(Net, self.net)

        # os
        self.os = Table("glpi_dropdown_os", self.metadata, autoload = True)
        mapper(OS, self.os)

        self.os_sp = Table("glpi_dropdown_os_sp", self.metadata, autoload = True)
        mapper(OsSp, self.os_sp)

        # domain
        self.domain = Table('glpi_dropdown_domain', self.metadata, autoload = True)
        mapper(Domain, self.domain)

        # machine (we need the foreign key, so we need to declare the table by hand ...
        #          as we don't need all columns, we don't declare them all)
        self.machine = Table("glpi_computers", self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('FK_entities', Integer, ForeignKey('glpi_entities.ID')),
            Column('FK_groups', Integer, ForeignKey('glpi_groups.ID')),
            Column('name', String(255), nullable=False),
            Column('serial', String(255), nullable=False),
            Column('os', Integer, ForeignKey('glpi_dropdown_os.ID')),
            Column('os_version', Integer, nullable=False),
            Column('os_sp', Integer, ForeignKey('glpi_dropdown_os_sp.ID')),
            Column('os_license_number', String(255), nullable=True),
            Column('os_license_id', String(255), nullable=True),
            Column('location', Integer, ForeignKey('glpi_dropdown_locations.ID')),
            Column('domain', Integer, ForeignKey('glpi_dropdown_domain.ID')),
            Column('network', Integer, ForeignKey('glpi_dropdown_network.ID')),
            Column('model', Integer, ForeignKey('glpi_dropdown_model.ID')),
            Column('type', Integer, nullable=False),
            Column('deleted', Integer, nullable=False),
            Column('is_template', Integer, nullable=False),
            Column('state', Integer, nullable=False), #ForeignKey('glpi_dropdown_state.ID')),
            Column('comments', String(255), nullable=False),
            autoload = True)
        mapper(Machine, self.machine) #, properties={'FK_entities': relation(Location)})

        # profile
        self.profile = Table("glpi_profiles", self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('name', String(255), nullable=False))
        mapper(Profile, self.profile)

        # user
        self.user = Table("glpi_users", self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('name', String(255), nullable=False),
            Column('id_auth', Integer, nullable=False),
            Column('deleted', Integer, nullable=False),
            Column('active', Integer, nullable=False))
        mapper(User, self.user)

        # userprofile
        self.userprofile = Table("glpi_users_profiles", self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('FK_users', Integer, ForeignKey('glpi_users.ID')),
            Column('FK_profiles', Integer, ForeignKey('glpi_profiles.ID')),
            Column('FK_entities', Integer, ForeignKey('glpi_entities.ID')),
            Column('recursive', Integer))
        mapper(UserProfile, self.userprofile)

        # devices
        self.computer_device = Table("glpi_computer_device", self.metadata,
            Column('FK_computers', Integer, ForeignKey('glpi_computers.ID')),
            autoload = True)
        mapper(ComputerDevice, self.computer_device)

        # software
        self.software = Table("glpi_software", self.metadata, autoload = True)
        mapper(Software, self.software)

        # glpi_inst_software
        self.inst_software = Table("glpi_inst_software", self.metadata,
            Column('cID', Integer, ForeignKey('glpi_computers.ID')),
            Column('license', Integer, ForeignKey('glpi_licenses.ID')),
            autoload = True)
        mapper(InstSoftware, self.inst_software)

        # glpi_licenses
        self.licenses = Table("glpi_licenses", self.metadata,
            Column('sID', Integer, ForeignKey('glpi_software.ID')),
            autoload = True)
        mapper(Licenses, self.licenses)

        # model
        self.model = Table("glpi_dropdown_model", self.metadata, autoload = True)
        mapper(Model, self.model)

        # group
        self.group = Table("glpi_groups", self.metadata, autoload = True)
        mapper(Group, self.group)



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
            for filter_key, filter_value in self.config.filter_on:
                if filter_key == 'state':
                    self.logger.debug('will filter %s == %s' % (filter_key, filter_value))
                    a_filter_on.append(self.machine.c.state == filter_value)
                else:
                    self.logger.warn('dont know how to filter on %s' % (filter_key))
            if len(a_filter_on) == 0:
                return None
            elif len(a_filter_on) == 1:
                return a_filter_on[0]
            else:
                return or_(*a_filter_on)
        return None

    def __filter_on_entity(self, query, ctx):
        ret = self.__filter_on_entity_filter(query, ctx)
        return query.filter(ret)

    def __filter_on_entity_filter(self, query, ctx):
        entities = map(lambda e: e.ID, self.getUserLocations(ctx.userid))
        return self.machine.c.FK_entities.in_(entities)

    def __getRestrictedComputersListQuery(self, ctx, filt = None, session = create_session()):
        """
        Get the sqlalchemy query to get a list of computers with some filters
        """
        query = session.query(Machine)
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        if filt:
            # filtering on machines (name or uuid)
            try:
                query = query.filter(self.machine.c.name.like(filt['hostname']+'%'))
            except KeyError:
                pass
            try:
                query = query.filter(self.machine.c.name.like(filt['name']+'%'))
            except KeyError:
                pass
            try:
                query = query.filter(self.machine.c.name.like(filt['filter']+'%'))
            except KeyError:
                pass

            try:
                query = self.filterOnUUID(query, filt['uuid'])
            except KeyError:
                pass

            try:
                gid = filt['gid']
                machines = []
                if ComputerGroupManager().isrequest_group(ctx, gid):
                    machines = map(lambda m: fromUUID(m), ComputerGroupManager().requestresult_group(ctx, gid, 0, -1, ''))
                else:
                    machines = map(lambda m: fromUUID(m), ComputerGroupManager().result_group(ctx, gid, 0, -1, ''))
                query = query.filter(self.machine.c.ID.in_(machines))

            except KeyError:
                pass

            try:
                request = filt['request']
                bool = None
                if filt.has_key('equ_bool'):
                    bool = filt['equ_bool']
                machines = map(lambda m: fromUUID(m), ComputerGroupManager().request(ctx, request, bool, 0, -1, ''))
                query = query.filter(self.machine.c.ID.in_(machines))
            except KeyError, e:
                pass

            # filtering on query
            join_query = self.machine
            query_filter = None

            filters = [self.machine.c.deleted == 0, self.machine.c.is_template == 0, self.__filter_on_filter(query), self.__filter_on_entity_filter(query, ctx)]

            join_query, query_filter = self.filter(ctx, self.machine, filt, session.query(Machine), self.machine.c.ID, filters)

            # filtering on locations
            try:
                location = filt['location']
                if location == '' or location == u'' or not self.displayLocalisationBar:
                    location = None
            except KeyError:
                location = None

            try:
                ctxlocation = filt['ctxlocation']
                if not self.displayLocalisationBar:
                    ctxlocation = None
            except KeyError:
                ctxlocation = None

            if ctxlocation != None:
                locs = []
                if type(ctxlocation) == list:
                    for loc in ctxlocation:
                        locs.append(self.__getName(loc))
                join_query = join_query.join(self.location)

                if location != None:
                    location = self.__getName(location)
                    try:
                        locs.index(location) # just check that location is in locs, or throw an exception
                        query_filter = self.__addQueryFilter(query_filter, (self.location.c.name == location))
                    except ValueError:
                        self.logger.warn("User '%s' is trying to get the content of an unauthorized entity : '%s'" % (ctx.userid, location))
                        session.close()
                        return None
                else:
                    query_filter = self.__addQueryFilter(query_filter, self.location.c.name.in_(locs))
            elif location != None:
                join_query = join_query.join(self.location)

                location = self.__getName(location)
                query_filter = self.__addQueryFilter(query_filter, (self.location.c.name == location))

            query = query.select_from(join_query).filter(query_filter)
            query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
            query = self.__filter_on(query)
            query = self.__filter_on_entity(query, ctx)

        return query

    def __getName(self, obj):
        if type(obj) == dict:
            return obj['name']
        if type(obj) != str and type(obj) != unicode:
            return obj.name
        return obj

    def __addQueryFilter(self, query_filter, eq):
        if str(query_filter) == None: # don't remove the str, sqlalchemy.sql._BinaryExpression == None return True!
            query_filter = eq
        else:
            query_filter = and_(query_filter, eq)
        return query_filter

    def computersTable(self):
        return [self.machine]

    def computersMapping(self, computers, invert = False):
        if not invert:
            return Machine.c.ID.in_(map(lambda x:fromUUID(x), computers))
        else:
            return Machine.c.ID.not_(in_(map(lambda x:fromUUID(x), computers)))

    def mappingTable(self, ctx, query):
        """
        Map a table name on a table mapping
        """
        base = []
        if ctx.userid != 'root':
            base.append(self.location)
        if query[2] == 'OS':
            return base + [self.os]
        elif query[2] == 'ENTITY':
            return base + [self.location]
        elif query[2] == 'SOFTWARE':
            return base + [self.inst_software, self.licenses, self.software]
        elif query[2] == 'Nom':
            return base
        elif query[2] == 'Contact':
            return base
        elif query[2] == 'Numero du contact':
            return base
        elif query[2] == 'Comments':
            return base
        elif query[2] == 'Modele':
            return base + [self.model]
        elif query[2] == 'Lieu':
            return base + [self.locations]
        elif query[2] == 'OS':
            return base + [self.os]
        elif query[2] == 'ServicePack':
            return base + [self.os_sp]
        elif query[2] == 'Groupe':
            return base + [self.group]
        elif query[2] == 'Reseau':
            return base + [self.network]
        elif query[2] == 'Logiciel':
            return base + [self.inst_software, self.licenses, self.software]
        elif query[2] == 'Version':
            return base + [self.inst_software, self.licenses, self.software]
        return []

    def mapping(self, ctx, query, invert = False):
        """
        Map a name and request parameters on a sqlalchemy request
        """
        if len(query) == 4:
            r1 = re.compile('\*')
            like = False
            if type(query[3]) == list:
                q3 = []
                query[3][0] = re.sub('^\(', '', query[3][0])
                query[3][-1] = re.sub('\)$', '', query[3][-1])
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

            parts = self.__getPartsFromQuery(query)
            ret = []
            for part in parts:
                partA, partB = part
                if invert:
                    if like:
                        ret.append(not_(partA.like(partB)))
                    else:
                        ret.append(partA != partB)
                else:
                    if like:
                        ret.append(partA.like(partB))
                    else:
                        ret.append(partA == partB)
            if ctx.userid != 'root':
                ret.append(self.__filter_on_entity_filter(None, ctx))
            return and_(*ret)
        else:
            return self.__treatQueryLevel(query)

    def __getPartsFromQuery(self, query):
        if query[2] == 'OS':
            return [[self.os.c.name, query[3]]]
        elif query[2] == 'ENTITY':
            return [[self.location.c.name, query[3]]]
        elif query[2] == 'SOFTWARE':
            return [[self.software.c.name, query[3]]]
        elif query[2] == 'Nom':
            return [[self.machine.c.name, query[3]]]
        elif query[2] == 'Contact':
            return [[self.machine.c.contact, query[3]]]
        elif query[2] == 'Numero du contact':
            return [[self.machine.c.contact_num, query[3]]]
        elif query[2] == 'Comments':
            return [[self.machine.c.comments, query[3]]]
        elif query[2] == 'Modele':
            return [[self.model.c.name, query[3]]]
        elif query[2] == 'Lieu':
            return [[self.locations.c.completename, query[3]]]
        elif query[2] == 'ServicePack':
            return [[self.os_sp.c.name, query[3]]]
        elif query[2] == 'Groupe': # TODO double join on ENTITY
            return [[self.group.c.name, query[3]]]
        elif query[2] == 'Reseau':
            return [[self.network.c.name, query[3]]]
        elif query[2] == 'Logiciel': # TODO double join on ENTITY
            return [[self.software.c.name, query[3]]]
        elif query[2] == 'Version': # TODO double join on ENTITY
            return [[self.software.c.name, query[3][0]], [self.licenses.c.version, query[3][1]]]
        return []


    def __getTable(self, table):
        if table == 'OS':
            return self.os.c.name
        elif table == 'ENTITY':
            return self.location.c.name
        elif table == 'SOFTWARE':
            return self.software.c.name
        raise Exception("dont know table for %s"%(table))

    ##################### machine list management
    def getComputer(self, ctx, filt):
        """
        Get the first computers that match filters parameters
        """
        ret = self.getRestrictedComputersList(ctx, 0, 10, filt)
        if len(ret) != 1:
            for i in ['location', 'ctxlocation']:
                try:
                    filt.pop(i)
                except:
                    pass
            ret = self.getRestrictedComputersList(ctx, 0, 10, filt)
            if len(ret) > 0:
                raise Exception("NOPERM##%s" % (ret[0][1]['fullname']))
            return False
        return ret[0]

    def getRestrictedComputersListLen(self, ctx, filt = None):
        """
        Get the size of the computer list that match filters parameters
        """
        self.logger.debug("getRestrictedComputersListLen")
        session = create_session()
        query = self.__getRestrictedComputersListQuery(ctx, filt, session)
        if query == None:
            return 0
        query = query.group_by([self.machine.c.name, self.machine.c.domain]).all()
        self.logger.debug(query)
        session.close()
        # I didn't find how to easily count() all the computers after the
        # group_by.
        return query

    def getRestrictedComputersList(self, ctx, min = 0, max = -1, filt = None, advanced = True, justId = False, toH = False):
        """
        Get the computer list that match filters parameters between min and max
        """
        session = create_session()
        ret = {}

        query = self.__getRestrictedComputersListQuery(ctx, filt, session)
        if query == None:
            return {}

        if min != 0:
            query = query.offset(min)
        if max != -1:
            max = int(max) - int(min)
            query = query.limit(max)

        # TODO : need to find a way to remove group_by/order_by ...
        if justId:
            ret = map(lambda m: self.getMachineUUID(m), query.group_by([self.machine.c.name, self.machine.c.domain]).order_by(asc(self.machine.c.name)))
        elif toH:
            ret = map(lambda m: m.toH(), query.group_by([self.machine.c.name, self.machine.c.domain]).order_by(asc(self.machine.c.name)))
        else:
            if filt.has_key('get'):
                ret = map(lambda m: self.__formatMachine(m, advanced, filt['get']), query.group_by([self.machine.c.name, self.machine.c.domain]).order_by(asc(self.machine.c.name)))
            else:
                ret = map(lambda m: self.__formatMachine(m, advanced), query.group_by([self.machine.c.name, self.machine.c.domain]).order_by(asc(self.machine.c.name)))
        session.close()
        return ret

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
        return toUUID(str(machine.ID))

    def getMachineByUUID(self, uuid):
        """
        Get the machine that as this UUID
        """
        session = create_session()
        ret = session.query(Machine).filter(self.machine.c.ID == int(str(uuid).replace("UUID", "")))
        ret = ret.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        ret = self.__filter_on(ret).first()
        session.close()
        return ret

    def filterOnUUID(self, query, uuid):
        """
        Modify the given query to filter on the machine UUID
        """
        if type(uuid) == list:
            return query.filter(self.machine.c.ID.in_(map(lambda a:int(str(a).replace("UUID", "")), uuid)))
        else:
            return query.filter(self.machine.c.ID == int(str(uuid).replace("UUID", "")))

    ##################### Machine output format (for ldap compatibility)
    def __formatMachine(self, machine, advanced, get = None):
        """
        Give an LDAP like version of the machine
        """

        uuid = self.getMachineUUID(machine)

        if get != None:
            ma = {}
            for field in get:
                if hasattr(machine, field):
                    ma[field] = getattr(machine, field)
                if field == 'uuid' or field == 'objectUUID':
                    ma[field] = uuid
                if field == 'cn':
                    ma[field] = machine.name
            return ma

        ret = {
            'cn': [machine.name],
            'displayName': [machine.comments],
            'objectUUID': [uuid]
        }
        if advanced:
            net = self.getMachineNetwork(uuid)
            ret['macAddress'] = map(lambda n: n['ifmac'], net) #self.getMachineMac(uuid)
            ret['ipHostNumber'] = map(lambda n: n['ifaddr'], net) #self.getMachineIp(uuid)
            ret['subnetMask'] = map(lambda n: n['netmask'], net)
            domain = self.getMachineDomain(machine.ID)
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

    def getUserLocation(self, user):
        """
        @return: Return one user GLPI entities as a list of string, or None
        TODO : check it is still used!
        """
        session = create_session()
        qlocation = session.query(Location).select_from(self.location.join(self.userprofile).join(self.user)).filter(self.user.c.name == user).first()
        if qlocation == None:
            ret = None
        else:
            ret = qlocation.name
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
            entids = session.query(UserProfile).select_from(self.userprofile.join(self.user).join(self.profile)).filter(self.user.c.name == user).filter(self.profile.c.name.in_(self.config.activeProfiles)).all()
            for entid in entids:
                if entid.FK_entities == 0 and entid.recursive == 1:
                    session.close()
                    return self.__get_all_locations()

            # the normal case...
            plocs = session.query(Location).add_column(self.userprofile.c.recursive).select_from(self.location.join(self.userprofile).join(self.user).join(self.profile)).filter(self.user.c.name == user).filter(self.profile.c.name.in_(self.config.activeProfiles)).all()
            for ploc in plocs:
                if ploc[1]:
                    # The user profile link to the location is recursive, and so
                    # the children locations should be added too
                    for l in self.__add_children(ploc[0]):
                        ret.append(l)
                else:
                    ret.append(ploc[0])
            if len(ret) == 0:
                ret = []
            session.close()
        return ret

    def __get_all_locations(self):
        ret = []
        session = create_session()
        q = session.query(Location).group_by(self.location.c.name).order_by(asc(self.location.c.name)).all()
        session.close()
        for location in q:
            ret.append(location)
        return ret

    def __add_children(self, child):
        """
        Recursive function used by getUserLocations to get entities tree if needed
        """
        session = create_session()
        children = session.query(Location).filter(self.location.c.parentID == child.ID).all()
        ret = [child]
        for c in children:
            for res in self.__add_children(c):
                ret.append(res)
        session.close()
        return ret

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
        Returns the total count of locations
        """
        session = create_session()
        ret = session.query(Location).count()
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
            q = session.query(User).select_from(self.user.join(self.userprofile).join(self.location)).filter(self.location.c.name.in_(inloc)).filter(self.user.c.name != userid).distinct().all()
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
        query = session.query(Machine).select_from(self.machine.join(self.location)).filter(self.location.c.name == location)
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        ret = []
        for machine in query.group_by(self.machine.c.name).order_by(asc(self.machine.c.name)):
            ret[machine.name] = self.__formatMachine(machine)
        session.close()
        return ret

    def doesUserHaveAccessToMachines(self, userid, a_machine_uuid, all = True):
        """
        Check if the user has correct permissions to access more than one or to all machines

        Return always true for the root user.

        @rtype: bool
        """
        if not self.displayLocalisationBar or userid == "root":
            return True
        a_locations = map(lambda loc:loc.name, self.getUserLocations(userid))
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.location))
        query = query.filter(self.location.c.name.in_(a_locations))
        query = self.filterOnUUID(query, a_machine_uuid)
        ret = query.group_by(self.machine.c.ID).all()
        size = 1
        if type(ret) == list:
            size = len(ret)
        if all and size == len(a_machine_uuid):
            return True
        elif (not all) and len(ret) > 0:
            return True
        ret = Set(map(lambda m:toUUID(str(m.ID)), ret))
        self.logger.info("dont have permissions on %s"%(str(Set(a_machine_uuid) - ret)))
        return False

    def doesUserHaveAccessToMachine(self, userid, machine_uuid):
        """
        Check if the user has correct permissions to access this machine

        @rtype: bool
        """
        return self.doesUserHaveAccessToMachines(userid, [machine_uuid])

    ##################### for inventory purpose (use the same API than OCSinventory to keep the same GUI)
    def getLastMachineInventoryFull(self, uuid):
        machine = self.getMachineByUUID(uuid)
        return machine.to_a()

    def inventoryExists(self, uuid):
        machine = self.getMachineByUUID(uuid)
        if machine:
            return True
        else:
            return False

    def getLastMachineInventoryPart(self, uuid, part):
        if part == 'Network':
            session = create_session()
            query = self.filterOnUUID(session.query(Network).select_from(self.machine.join(self.network)), uuid).all()
            ret = map(lambda a:a.to_a(), query)
            session.close()
        else:
            ret = None
        return ret

    ##################### functions used by querymanager
    def getAllOs(self, ctx, filt = ''):
        """
        @return: all os defined in the GLPI database
        """
        session = create_session()
        query = session.query(OS).select_from(self.os.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0))
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        ret = query.all()
        session.close()
        return ret

    def getAllEntities(self, ctx, filt = ''):
        """
        @return: all entities defined in the GLPI database
        """
        session = create_session()
        query = session.query(Location).select_from(self.model.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.location.c.name.like('%'+filt+'%'))
        ret = query.all()
        session.close()
        return ret
    def getMachineByEntity(self, ctx, enname):
        """
        @return: all machines that are in this entity
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.location)).filter(self.location.c.name == enname)
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        ret = query.all()
        session.close()
        return ret

    def getAllSoftwares(self, ctx, filt = ''):
        """
        @return: all softwares defined in the GLPI database
        """
        session = create_session()
        query = session.query(Software).select_from(self.software.join(self.licenses).join(self.inst_software).join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        entities = map(lambda e: e.ID, self.getUserLocations(ctx.userid))
        query = query.filter(self.software.c.FK_entities.in_(entities))
        if filter != '':
            query = query.filter(self.software.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.software.c.name).all()
        ret = query.all()
        session.close()
        return ret
    def getMachineBySoftware(self, ctx, swname):
        """
        @return: all machines that have this software
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.inst_software).join(self.licenses).join(self.software))
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if type(swname) == list:
            # FIXME: the way the web interface process dynamic group sub-query
            # is wrong, so for the moment we need this loop:
            while type(swname[0]) == list:
                swname = swname[0]
            query = query.filter(and_(self.software.c.name == swname[0], glpi_license.version == swname[1]))
        else:
            query = query.filter(self.software.c.name == swname)
        ret = query.all()
        session.close()
        return ret
    def getMachineBySoftwareAndVersion(self, ctx, swname):
        return self.getMachineBySoftware(ctx, swname)

    def getAllHostnames(self, ctx, filt = ''):
        """
        @return: all hostnames defined in the GLPI database
        """
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.machine.c.comments.like('%'+filt+'%'))
        ret = query.group_by(self.machine.c.comments).all()
        session.close()
        return ret
    def getMachineByComment(self, ctx, comment):
        """
        @return: all machines that have this contact number
        """
        # TODO use the ctx...
        session = create_session()
        query = session.query(Machine)
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.machine.c.comments == comment)
        ret = query.all()
        session.close()
        return ret

    def getAllModels(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        session = create_session()
        query = session.query(Model).select_from(self.model.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.model.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.model.c.name).all()
        session.close()
        return ret
    def getMachineByModel(self, ctx, filt):
        """ @return: all machines that have this contact number """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.model))
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.model.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllLocations(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        session = create_session()
        query = session.query(Locations).select_from(self.locations.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        if filter != '':
            query = query.filter(self.locations.c.completename.like('%'+filt+'%'))
        ret = query.group_by(self.locations.c.completename).all()
        session.close()
        return ret
    def getMachineByLocation(self, ctx, filt):
        """ @return: all machines that have this contact number """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.locations))
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
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
        query = self.__filter_on(query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0))
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.os_sp.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllGroups(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        session = create_session()
        query = session.query(Group).select_from(self.group.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0))
        query = self.__filter_on_entity(query, ctx)
        entities = map(lambda e: e.ID, self.getUserLocations(ctx.userid))
        query = query.filter(self.group.c.FK_entities.in_(entities))
        if filter != '':
            query = query.filter(self.group.c.name.like('%'+filt+'%'))
        ret = query.group_by(self.group.c.name).all()
        session.close()
        return ret
    def getMachineByGroup(self, ctx, filt):# ENTITY!
        """ @return: all machines that have this contact number """
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.group))
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        entities = map(lambda e: e.ID, self.getUserLocations(ctx.userid))
        query = query.filter(self.group.c.FK_entities.in_(entities))
        query = query.filter(self.group.c.name == filt)
        ret = query.all()
        session.close()
        return ret

    def getAllNetworks(self, ctx, filt = ''):
        """ @return: all hostnames defined in the GLPI database """
        session = create_session()
        query = session.query(Net).select_from(self.net.join(self.machine))
        query = self.__filter_on(query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0))
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
        query = query.filter(self.machine.c.deleted == 0).filter(self.machine.c.is_template == 0)
        query = self.__filter_on(query)
        query = self.__filter_on_entity(query, ctx)
        query = query.filter(self.net.c.name == filt)
        ret = query.all()
        session.close()
        return ret


    ##################### for msc
    def getMachineNetwork(self, uuid):
        """
        Get a machine network
        """
        session = create_session()
        query = session.query(Network).select_from(self.machine.join(self.network))
        query = self.filterOnUUID(query.filter(self.network.c.device_type == 1), uuid)
        ret = unique(map(lambda m: m.toH(), query.all()))
        session.close()
        return ret

    def getMachineMac(self, uuid):
        """
        Get a machine mac addresses
        """
        session = create_session()
        query = session.query(Network).select_from(self.machine.join(self.network))
        query = self.filterOnUUID(query.filter(self.network.c.device_type == 1), uuid)
        ret = unique(map(lambda m: m.ifmac, query.all()))
        session.close()
        return ret

    def getMachineIp(self, uuid):
        """
        Get a machine ip addresses
        """
        # FIXME: order IP adresses, first one should be on the "defaut" network (ie with the default gw)
        session = create_session()
        query = session.query(Network).select_from(self.machine.join(self.network))
        query = self.filterOnUUID(query.filter(self.network.c.device_type == 1), uuid)
        ret_gw = []
        ret_nogw = []
        for m in query.all():
            if same_network(m.ifaddr, m.gateway, m.netmask):
                ret_gw.append(m.ifaddr)
            else:
                ret_nogw.append(m.ifaddr)

        ret_gw = unique(ret_gw)
        ret_gw.extend(unique(ret_nogw))
        session.close()
        return ret_gw

    def getIpFromMac(self, mac):
        """
        Get an ip address when a mac address is given
        """
        session = create_session()
        query = session.query(Network).filter(self.network.c.ifmac == mac)
        ret = query.first().ifaddr
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
        query = self.filterOnUUID(session.query(Domain).select_from(self.domain.join(self.machine)), uuid)
        ret = query.first()
        if ret != None:
            return ret.name
        else:
            return ''

def fromUUID(uuid):
    return int(uuid.replace('UUID', ''))

def toUUID(id):
    return "UUID%s" % (str(id))

# Class for SQLalchemy mapping
class Machine(object):
    def toH(self):
        return { 'hostname':self.name, 'uuid':toUUID(self.ID) }
    def to_a(self):
        return [
            ['name',self.name],
            ['comments',self.comments],
            ['name',self.name],
            ['serial',self.serial],
            ['os',self.os],
            ['os_version',self.os_version],
            ['os_sp',self.os_sp],
            ['os_license_number',self.os_license_number],
            ['os_license_id',self.os_license_id],
            ['location',self.location],
            ['domain',self.domain],
            ['network',self.network],
            ['model',self.model],
            ['type',self.type],
            ['uuid',Glpi().getMachineUUID(self)]
        ]

class Location(object):
    def toH(self):
        return {
            'uuid':toUUID(self.ID),
            'name':self.name,
            'completename':self.completename,
            'comments':self.comments,
            'level':self.level
        }

class Processor(object):
    pass

class User(object):
    pass

class Profile(object):
    pass

class UserProfile(object):
    pass

class Network(object):
    def toH(self):
        return {
            'name': self.name,
            'ifaddr': self.ifaddr,
            'ifmac': self.ifmac,
            'netmask': self.netmask,
            'gateway': self.gateway,
            'subnet': self.subnet
        }

    def to_a(self):
        return [
            ['name', self.name],
            ['ifaddr', self.ifaddr],
            ['ifmac', self.ifmac],
            ['netmask', self.netmask],
            ['gateway', self.gateway],
            ['subnet', self.subnet]
        ]

class OS(object):
    pass

class ComputerDevice(object):
    pass

class Domain(object):
    pass

class Software(object):
    pass

class InstSoftware(object):
    pass

class Licenses(object):
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

