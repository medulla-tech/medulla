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

from mmc.support.config import PluginConfig
from mmc.support.mmctools import Singleton, xmlrpcCleanup
from mmc.plugins.base import ComputerI
from mmc.plugins.glpi.utilities import unique, same_network, complete_ctx, onlyAddNew
from mmc.plugins.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper

from ConfigParser import NoOptionError
from sqlalchemy import *
from sqlalchemy.exceptions import SQLError
import logging
import re

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

class GlpiConfig(PluginConfig):
    def readConf(self):
        PluginConfig.readConf(self)
        self.dbdriver = self.get("main", "dbdriver")
        self.dbhost = self.get("main", "dbhost")
        self.dbname = self.get("main", "dbname")
        self.dbuser = self.get("main", "dbuser")
        self.dbpasswd = self.get("main", "dbpasswd")
        self.disable = self.getint("main", "disable")
        self.displayLocalisationBar = self.getboolean("main", "localisation")
        try:
            self.activeProfiles = self.get('main', 'active_profiles').split(' ')
        except NoOptionError:
            # put the GLPI default values for actives profiles
            self.activeProfiles = ['admin', 'normal', 'post-only', 'super-admin']
        for option in ["dbport", "dbpoolrecycle"]:
            try:
                self.__dict__[option] = self.getint("main", option)
            except NoOptionError:
                pass
        try:
            filter_on = self.get("main", "filter_on")
            self.filter_on = map(lambda x:x.split('='), filter_on.split(' '))
            logging.getLogger().debug("will filter machines on %s" % (str(self.filter_on)))
        except:
            self.filter_on = None

    def setDefault(self):
        PluginConfig.setDefault(self)
        self.dbpoolrecycle = 60
        self.dbport = None

class Glpi(DyngroupDatabaseHelper):
    """
    Singleton Class to query the glpi database.

    """
    is_activated = False

    def db_check(self):
        if not self.__checkSqlalchemy():
            self.logger.error("Sqlalchemy version error : is not %s.%s.* version" % (SA_MAYOR, SA_MINOR))
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
            if len(a_version) > 2 and str(a_version[0]) == str(SA_MAYOR) and str(a_version[1]) == str(SA_MINOR):
                return True
        except: 
            pass
        return False

    def activate(self, conffile = None):
        self.logger = logging.getLogger()
        if self.is_activated:
            self.logger.info("Glpi don't need activation")
            return None
        self.logger.info("Glpi is activating")
        self.config = GlpiConfig("glpi", conffile)
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle)
        self.metadata = BoundMetaData(self.db)
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
        return "%s://%s:%s@%s%s/%s" % (self.config.dbdriver, self.config.dbuser, self.config.dbpasswd, self.config.dbhost, port, self.config.dbname)

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the inventory database
        """

        # location
        self.location = Table("glpi_entities", self.metadata, autoload = True)
        mapper(Location, self.location)

        # processor
        self.processor = Table("glpi_device_processor", self.metadata, autoload = True)
        mapper(Processor, self.processor)

        # network
        self.network = Table("glpi_networking_ports", self.metadata,
            Column('on_device', Integer, ForeignKey('glpi_computers.ID')),
            autoload = True)
        mapper(Network, self.network)

        # os
        self.os = Table("glpi_dropdown_os", self.metadata, autoload = True)
        mapper(OS, self.os)

        # domain
        self.domain = Table('glpi_dropdown_domain', self.metadata, autoload = True)
        mapper(Domain, self.domain)

        # machine (we need the foreign key, so we need to declare the table by hand ...
        #          as we don't need all columns, we don't declare them all)
        self.machine = Table("glpi_computers", self.metadata,
            Column('ID', Integer, primary_key=True),
            Column('FK_entities', Integer, ForeignKey('glpi_entities.ID')),
            Column('name', String(255), nullable=False),
            Column('serial', String(255), nullable=False),
            Column('os', Integer, ForeignKey('glpi_dropdown_os.ID')),
            Column('os_version', Integer, nullable=False),
            Column('os_sp', Integer, nullable=False),
            Column('os_license_number', String(255), nullable=True),
            Column('os_license_id', String(255), nullable=True),
            Column('location', Integer, nullable=False),
            Column('domain', Integer, ForeignKey('glpi_dropdown_domain.ID')),
            Column('network', Integer, nullable=False),
            Column('model', Integer, nullable=False),
            Column('type', Integer, nullable=False),
            Column('deleted', Integer, nullable=False),
            Column('is_template', Integer, nullable=False),
            Column('state', Integer, nullable=False), #ForeignKey('glpi_dropdown_state.ID')),
            Column('comments', String(255), nullable=False))
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
        if self.config.filter_on != None:
            a_filter_on = []
            for filter_key, filter_value in self.config.filter_on:
                if filter_key == 'state':
                    self.logger.debug('will filter %s == %s' % (filter_key, filter_value))
                    a_filter_on.append(self.machine.c.state == filter_value)
                else:
                    self.logger.warn('dont know how to filter on %s' % (filter_key))
            if len(a_filter_on) == 0:
                return query
            elif len(a_filter_on) == 1:
                return query.filter(a_filter_on[0])
            else:
                return query.filter(or_(*a_filter_on))
        return query

    def __getRestrictedComputersListQuery(self, filt = None, session = create_session()):
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
                query = self.filterOnUUID(query, filt['uuid'])
            except KeyError:
                pass

            # filtering on query
            join_query = self.machine
            query_filter = None

            join_query, query_filter = self.filter(self.machine, filt)

            # filtering on locations
            try:
                location = filt['location']
            except KeyError:
                location = None

            try:
                ctxlocation = filt['ctxlocation']
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
                        return {}
                else:
                    query_filter = self.__addQueryFilter(query_filter, self.location.c.name.in_(*locs))
            elif location != None:
                join_query = join_query.join(self.location)
                
                location = self.__getName(location)
                query_filter = self.__addQueryFilter(query_filter, (self.location.c.name == location))

            query = query.select_from(join_query).filter(query_filter)
        return query

    def __getName(self, obj):
        if type(obj) != str and type(obj) != unicode:
            return obj.name
        return obj
        
    def __addQueryFilter(self, query_filter, eq):
        if str(query_filter) == None: # don't remove the str, sqlalchemy.sql._BinaryExpression == None return True!
            query_filter = eq
        else:
            query_filter = and_(query_filter, eq)
        return query_filter
    
    def mappingTable(self, query):
        """
        Map a table name on a table mapping
        """
        if query[2] == 'OS':
            return self.os
        elif query[2] == 'ENTITY':
            return self.location
        elif query[2] == 'SOFTWARE':
            return [self.inst_software, self.licenses, self.software]
        return []

    def mapping(self, query, invert = False):
        """
        Map a name and request parameters on a sqlalchemy request
        """
        if len(query) == 4:
            if query[2] == 'OS':
                if invert:
                    return self.os.c.name != query[3]
                else:
                    return self.os.c.name == query[3]
            elif query[2] == 'ENTITY':
                if invert:
                    return self.location.c.name != query[3]
                else:
                    return self.location.c.name == query[3]
            elif query[2] == 'SOFTWARE':
                if invert:
                    return self.software.c.name != query[3]
                else:
                    return self.software.c.name == query[3]
        else:
            return self.__treatQueryLevel(query)

    ##################### machine list management
    def getComputer(self, filt):
        """
        Get the first computers that match filters parameters
        """
        ret = self.getRestrictedComputersList(0, 10, filt)
        if len(ret) != 1:
            for i in ['location', 'ctxlocation']:
                try:
                    filt.pop(i)
                except:
                    pass
            ret = self.getRestrictedComputersList(0, 10, filt)
            if len(ret) > 0:
                raise Exception("NOPERM##%s" % (ret[ret.keys()[0]][1]['fullname']))
            return False
        return ret[ret.keys()[0]]

    def getRestrictedComputersListLen(self, filt = None):
        """
        Get the size of the computer list that match filters parameters
        """
        session = create_session()
        query = self.__getRestrictedComputersListQuery(filt, session)
        count = query.group_by([self.machine.c.name, self.machine.c.domain]).count()
        session.close()
        return count

    def getRestrictedComputersList(self, min = 0, max = -1, filt = None, advanced = True):
        """
        Get the computer list that match filters parameters between min and max
        """
        session = create_session()
        ret = {}

        query = self.__getRestrictedComputersListQuery(filt, session)

        if min != 0:
            query = query.offset(min)
        if max != -1:
            max = int(max) - int(min)
            query = query.limit(max)

        # TODO : need to find a way to remove group_by/order_by ...
        for machine in query.group_by([self.machine.c.name, self.machine.c.domain]).order_by(asc(self.machine.c.name)):
            machine = self.__formatMachine(machine, advanced)
            try:
                self.logger.error("%s already exists" % (ret[machine[1]['fullname']][1]['fullname']))
            except:
                pass
            ret[machine[1]['fullname']] = machine
        session.close()
        return ret

    def getComputerCount(self, filt = None):
        """
        Same as getRestrictedComputersListLen
        TODO : remove this one
        """
        return self.getRestrictedComputersListLen(filt)

    def getComputersList(self, filt = None):
        """
        Same as getRestrictedComputersList without limits
        """
        return self.getRestrictedComputersList(0, -1, filt)

    ##################### UUID policies
    def getMachineUUID(self, machine):
        """
        Get this machine UUID
        """
        return "UUID" + str(machine.ID)

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
            return query.filter(self.machine.c.ID.in_(*map(lambda a:int(str(a).replace("UUID", "")), uuid)))
        else:
            return query.filter(self.machine.c.ID == int(str(uuid).replace("UUID", "")))

    ##################### Machine output format (for ldap compatibility)
    def __formatMachine(self, machine, advanced):
        """
        Give an LDAP like version of the machine
        """
        domain = self.getMachineDomain(machine.ID)
        uuid = self.getMachineUUID(machine)
        if domain != '':
            domain = '.'+domain
        ret = {
            'cn': [machine.name],
            'displayName': [machine.comments],
            'objectUUID': [uuid],
            'fullname': machine.name + domain,
        }
        if advanced:
            ret['macAddress'] = self.getMachineMac(uuid)
            ret['ipHostNumber'] = self.getMachineIp(uuid)
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
            entids = session.query(UserProfile).select_from(self.userprofile.join(self.user).join(self.profile)).filter(self.user.c.name == user).filter(self.profile.c.name.in_(*self.config.activeProfiles)).all()
            for entid in entids:
                if entid.FK_entities == 0 and entid.recursive == 1:
                    session.close()
                    return self.__get_all_locations()
            
            # the normal case...
            plocs = session.query(Location).add_column(self.userprofile.c.recursive).select_from(self.location.join(self.userprofile).join(self.user).join(self.profile)).filter(self.user.c.name == user).filter(self.profile.c.name.in_(*self.config.activeProfiles)).all()
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
        """
        a_locations = map(lambda loc:loc.name, self.getUserLocations(userid))
        session = create_session()
        query = session.query(Machine).select_from(self.machine.join(self.location))
        query = query.filter(self.location.c.name.in_(*a_locations))
        query = self.filterOnUUID(query, a_machine_uuid)
        ret = query.group_by(self.machine.c.name).all()
        size = 1
        if type(ret) == list:
            size = len(ret)
        if all and size == len(a_machine_uuid):
            return True
        elif (not all) and len(query.group_by(self.machine.c.name)) > 0:
            return True
        return False
        
    def doesUserHaveAccessToMachine(self, userid, machine_uuid):
        """
        Check if the user has correct permissions to access this machine
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
    def getAllOs(self, filt = ''):
        """
        @return: all os defined in the GLPI database
        """
        session = create_session()
        query = session.query(OS)
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
        ret = query.all()
        session.close()
        return ret

    def getAllEntities(self, filt = ''):
        """
        @return: all entities defined in the GLPI database
        """
        session = create_session()
        query = session.query(Location)
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
        ret = query.all()
        session.close()
        return ret

    def getAllSoftwares(self, filt = ''):
        """
        @return: all softwares defined in the GLPI database
        """
        session = create_session()
        query = session.query(Software)
        if filter != '':
            query = query.filter(self.software.c.name.like('%'+filt+'%'))
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
        query = query.filter(self.software.c.name == swname)
        ret = query.all()
        session.close()
        return ret

    ##################### for msc
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

# Class for SQLalchemy mapping
class Machine(object):
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
    pass

class Processor(object):
    pass

class User(object):
    pass

class Profile(object):
    pass

class UserProfile(object):
    pass

class Network(object):
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

