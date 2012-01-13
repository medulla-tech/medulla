# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Dyngroup database handler
"""

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.sql import *

# PULSE2 modules
from pulse2.database.database_helper import DatabaseHelper

# Imported last
import logging

SA_MAJOR = 0
SA_MINOR = 4
DATABASEVERSION = 3

class DyngroupDatabase(DatabaseHelper):
    """
    Singleton Class to query the dyngroup database.

    """
    is_activated = False

    def db_check(self):
        self.my_name = "Dyngroup"
        self.configfile = "dyngroup.ini"
        return DatabaseHelper.db_check(self, DATABASEVERSION)

    def activate(self, config): ## conffile = None):
        self.logger = logging.getLogger()
        if not self.is_activated:
            self.logger.info("Dyngroup database is connecting")
            self.config = config
            self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
            self.metadata = MetaData(self.db)
            if not self.initMappersCatchException():
                self.session = None
                return self.is_activated
            self.metadata.create_all()
            self.session = create_session()
            self.is_activated = True
            version = self.version.select().execute().fetchone()[0]
            self.logger.debug("Dyngroup database connected (version:%s)" % version)
            
        return self.is_activated

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the inventory database
        """

        self.version = Table("version", self.metadata, autoload = True)

        # types
        self.shareGroupType = Table("ShareGroupType", self.metadata,autoload = True)
        mapper(ShareGroupType, self.shareGroupType)
        self.groupType = Table("GroupType", self.metadata,autoload = True)
        mapper(GroupType, self.groupType)
        self.userType = Table("UsersType", self.metadata,autoload = True)
        mapper(UsersType, self.userType)

        # Users
        self.users = Table("Users", self.metadata,
                            Column('type', Integer, ForeignKey('UsersType.id')),
                            autoload = True)
        mapper(Users, self.users)

        # Groups
        self.groups = Table("Groups", self.metadata,
                            Column('FK_users', Integer, ForeignKey('Users.id')),
                            Column('type', Integer, ForeignKey('GroupType.id')),
                            autoload = True)
        mapper(Groups, self.groups, properties = {
                'results' : relation(Results),
            }
        )

        # ShareGroup
        self.shareGroup = Table("ShareGroup", self.metadata,
                            Column('FK_groups', Integer, ForeignKey('Groups.id')),
                            Column('FK_users', Integer, ForeignKey('Users.id')),
                            Column('type', Integer, ForeignKey('ShareGroupType.id')),
                            autoload = True)
        mapper(ShareGroup, self.shareGroup)

        # Results
        self.results = Table("Results", self.metadata,
                            Column('FK_groups', Integer, ForeignKey('Groups.id')),
                            Column('FK_machines', Integer, ForeignKey('Machines.id')),
                            autoload = True)
        mapper(Results, self.results)

        # ProfilesResults
        self.profilesResults = Table("ProfilesResults", self.metadata,
                            Column('FK_groups', Integer, ForeignKey('Groups.id')),
                            Column('FK_machines', Integer, ForeignKey('Machines.id'), primary_key=True))
        mapper(ProfilesResults, self.profilesResults)

        # ProfilesPackages
        self.profilesPackages = Table("ProfilesPackages", self.metadata,
                            Column('FK_groups', Integer, ForeignKey('Groups.id'), primary_key=True),
                            autoload = True)
        mapper(ProfilesPackages, self.profilesPackages)

        # ProfilesData
        self.profilesData = Table("ProfilesData", self.metadata,
                            Column('FK_groups', Integer, ForeignKey('Groups.id'), primary_key=True),
                            autoload = True)
        mapper(ProfilesData, self.profilesData)

        # Machines
        self.machines = Table("Machines", self.metadata, autoload = True)
        mapper(Machines, self.machines, properties = {
                'results' : relation(Results),
            }
        )

        # version
        self.version = Table("version", self.metadata, autoload = True)

    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except exceptions.SQLError, e:
                self.logger.error(e)
            except Exception, e:
                self.logger.error(e)
            if ret: break
        if not ret:
            raise "Database connection error"
        return ret

    ####################################
    ## USERS ACCESS

    def getUser(self, id):
        """
        get a user from his id
        """
        session = create_session()
        user = session.query(Users).get(id)
        session.close()
        return user

    def __getOrCreateUser(self, ctx, user_id = None, t = 0):
        """
        try to get a user, and create it if he does not exits
        """
        session = create_session()
        if user_id == None:
            user_id = ctx.userid
        user = self.__getUser(user_id, t)
        if not user:
            user = Users()
            user.login = user_id
            user.type = t
            session.add(user)
            session.flush()
        session.close()
        return user.id

    def __getUser(self, login, t = 0, session = None):
        """
        get a user from his login and type
        """
        if not session:
            session = create_session()
        user = session.query(Users).filter(self.users.c.login == login).filter(self.users.c.type == t).first()
        return user

    def __getUsers(self, logins, t = 0, session = None):
        """
        get several users from their logins and type (the type is the same for all)
        """
        if not session:
            session = create_session()
        users = session.query(Users)
        if t == None:
            users = users.filter(self.users.c.login.in_(logins))
        else:
            users = users.filter(self.users.c.login.in_(logins)).filter(self.users.c.type == t)
        return users

    def __getUsersInGroup(self, gid, session = None):
        """
        get all users that share a group defined by its id
        """
        if not session:
            session = create_session()
        users = session.query(Users).select_from(self.users.join(self.shareGroup).join(self.groups)).filter(self.groups.c.id == gid).all()
        return users

    def getUsersType(self, id):
        """
        get the type of a user defined by his id
        """
        session = create_session()
        s = session.query(UsersType).filter(self.userType.c.id == id).first()
        session.close()
        return s

    ####################################
    ## MACHINES ACCESS

    def getMachineProfile(self, ctx, id):
        """
        get one machine profile
        the machine is defined by its UUID
        """
        session = create_session()
        profile = session.query(ProfilesResults).select_from(self.profilesResults.join(self.machines)).filter(self.machines.c.uuid == id).first()
        session.close()
        if profile:
            return profile.FK_groups
        return False

    def __getMachine(self, uuid, session=None):
        """
        get a machine defined by its UUID
        """
        _session = session or create_session()
        machine = _session.query(Machines).filter(self.machines.c.uuid == uuid).first()
        if session is None:
            _session.close()
        return machine

    def __getOrCreateMachine(self, uuid, name, session=None):
        """
        get a machine defined by its UUID if it exists, else create it
        """
        _session = session or create_session()
        machine = self.__getMachine(uuid, _session)
        if not machine:
            machine = Machines()
            machine.uuid = uuid
            machine.name = name
            session.add(machine)
            session.flush()
        if session is None:
            _session.close()
        return machine.id

    def __updateMachinesTable(self, connection, uuids = []):
        """
        Remove all rows in the Machines table that are no more needed

        if a list of uuids is given, only ghost for the given computers are
        looking for.
        """
        # Get all Machines id that are not a foreign key in Results
        if uuids:
            todelete = connection.execute(select([self.machines.c.id], and_(self.machines.c.uuid.in_(uuids), not_(self.machines.c.id.in_(select([self.results.c.FK_machines])))))).fetchall()
        else:
            todelete = connection.execute(select([self.machines.c.id], not_(self.machines.c.id.in_(select([self.results.c.FK_machines]))))).fetchall()
        todelete = map(lambda x: {"id" : x[0]}, todelete)
        # Delete them if any
        if todelete:
            connection.execute(self.machines.delete(self.machines.c.id == bindparam("id")), todelete)

    def delMachine(self, uuid):
        """
        Delete a computer from all the dyngroup database tables

        @returns: True if the machine has been successfully deleted
        """
        ret = False
        session = create_session()
        m = self.__getMachine(uuid, session)
        if m:
            session.begin()
            try:
                mid = m.id
                session.delete(m)
                self.__deleteResult4AllGroups(mid, session)
                session.commit()
                ret = True
            except:
                session.rollback()
                raise
            session.close()
        return ret

    def getAllMachinesUuid(self):
        """
        get all the existing machines UUIDs
        """
        session = create_session()
        ret = {}
        for m in session.query(Machines):
            ret[m.uuid] = m.name
        session.close()
        return ret

    def updateNewNames(self, machines):
        """
        as the machines are first defined in an inventory plugin and then imported in dyngroup
        it's possible that the name is no longer the good one
        this function purpose is to update the name depending on the UUID
        """
        for uuid in machines:
            self.logger.debug("going to update %s name to %s in dyngroup machines cache"%(uuid, machines[uuid]))
            self.machines.update(self.machines.c.uuid==uuid).execute(name=machines[uuid])

    ####################################
    ## PROFILE ACCESS
    def getProfileByNameImagingServer(self, name, is_uuid):
        """
        Get a profile given it's name and it's imaging server's uuid
        """
        session = create_session()
        q = session.query(Groups).select_from(self.groups.join(self.groupType).join(self.profilesData))
        q = q.filter(and_(self.groupType.c.value == 'Profile', self.groups.c.name == name, self.profilesData.c.imaging_uuid == is_uuid)).all()
        session.close()
        return q

    def getProfileByUUID(self, uuid):
        """
        Get a profile given it's uuid
        """
        session = create_session()
        # WARNING we have to pass to uuid for groups and profiles!)
        q = session.query(Groups).select_from(self.groups.join(self.groupType)).filter(and_(self.groupType.c.value == 'Profile', self.groups.c.id == uuid)).first()
        session.close()
        return q

    def getComputersProfile(self, uuid):
        """
        Get a computer's profile given the computer uuid
        """
        session = create_session()
        q = session.query(Groups).select_from(self.machines.join(self.profilesResults).join(self.groups).join(self.groupType))
        q = q.filter(and_(self.groupType.c.value == 'Profile', self.machines.c.uuid == uuid)).first() # a computer can only be in one profile!
        session.close()
        return q

    def getProfileContent(self, uuid):
        """
        Get all computers that are in a profile
        """
        session = create_session()
        q = session.query(Machines).select_from(self.groups.join(self.profilesResults).join(self.machines).join(self.groupType))
        q = q.filter(and_(self.groupType.c.value == 'Profile', self.groups.c.id == uuid)).all()
        session.close()
        return q

    def setProfileImagingServer(self, gid, imaging_uuid):
        """
        link the profile to an imaging server
        """
        session = create_session()
        pdata = session.query(ProfilesData).filter(self.profilesData.c.FK_groups == gid).first()
        if pdata == None:
            pdata = ProfilesData()
            pdata.FK_groups = gid
        pdata.imaging_uuid = imaging_uuid
        session.add(pdata)
        session.flush()
        session.close()
        return True

    def getProfileImagingServer(self, gid):
        """
        get the imaging server linked to a profile
        """
        session = create_session()
        pdata = session.query(ProfilesData).filter(self.profilesData.c.FK_groups == gid).first()
        session.close()
        if pdata == None:
            return None
        return pdata.imaging_uuid

    def setProfileEntity(self, gid, entity_uuid):
        """
        link the profile to an entity
        """
        session = create_session()
        pdata = session.query(ProfilesData).filter(self.profilesData.c.FK_groups == gid).first()
        if pdata == None:
            pdata = ProfilesData()
            pdata.FK_groups = gid
        pdata.entity_uuid = entity_uuid
        session.add(pdata)
        session.flush()
        session.close()
        return True

    def getProfileEntity(self, gid):
        """
        get the entity linked to a profile
        """
        session = create_session()
        pdata = session.query(ProfilesData).filter(self.profilesData.c.FK_groups == gid).first()
        session.close()
        if pdata == None:
            return None
        return pdata.entity_uuid

    ####################################
    ## SHARE ACCESS

    def __createShare(self, group_id, user_id, visibility = 0, type_id = 0):
        """
        create a share (betwen a group and a user)
        """
        session = create_session()
        share = ShareGroup()
        share.FK_groups = group_id
        share.FK_users = user_id
        share.display_in_menu = visibility
        share.type = type_id
        session.add(share)
        session.flush()
        session.close()
        return share.id

    def __changeShare(self, group_id, user_id, visibility):
        """
        modify a share (betwen a group and a user)
        """
        session = create_session()
        share = self.getShareGroup(group_id, user_id)
        share.display_in_menu = visibility
        session.add(share)
        session.flush()
        session.close()
        return share.id

    def __deleteShares(self, group_id, session=None):
        """
        delete all the shares for a group (betwen a group and several users)
        """
        _session = session or create_session()
        users = self.__getUsersInGroup(group_id, _session)
        for user in users:
            self.__deleteShare(group_id, user.id, _session)
        if session is None:
            _session.close()

    def __deleteShare(self, group_id, user_id, session=None):
        """
        delete a share (betwen a group and a user)
        """
        _session = session or create_session()
        shares = _session.query(ShareGroup).filter(self.shareGroup.c.FK_users == user_id).filter(self.shareGroup.c.FK_groups == group_id).all()
        for share in shares:
            _session.delete(share)
            _session.flush()

        if session is None:
            _session.close()
        return still_linked

    def __getShareGroupInSession(self, id, user_id, session):
        """
        get the share item betwen the group and the user (if it exists)
        (handler for getShareGroup...)
        """
        return self.getShareGroup(id, user_id, session)

    def getShareGroup(self, group_id, user_id, session=None):
        """
        get the share item betwen the group and the user (if it exists)
        """
        _session = session or create_session()
        share = _session.query(ShareGroup).filter(self.shareGroup.c.FK_users == user_id).filter(self.shareGroup.c.FK_groups == group_id).first()
        if session is None:
            _session.close()
        return share

    def getShareGroupType(self, id):
        """
        get a share type (can be 0:View or 1:Edit)
        the share is defined by its id
        """
        session = create_session()
        s = session.query(ShareGroupType).filter(self.shareGroupType.c.id == id).first()
        session.close()
        return s

    def share_with(self, ctx, id):
        """
        get all the share object linked to a group
        identified by the group id
        """
        session = create_session()
        ret = session.query(ShareGroup).filter(self.shareGroup.c.FK_groups == id).all()
        session.close()
        return map(lambda x: x.toH(), ret)

    def can_edit(self, ctx, id):
        """
        tell if a users can edit a group (based on the share type)
        """
        session = create_session()
        ret = session.query(ShareGroup).filter(and_(self.shareGroup.c.FK_users == ctx.userid, self.shareGroup.c.FK_groups == id)).first()
        return ret.type == 1


    ####################################
    ## RESULT ACCESS

    def __createResult(self, group_id, machine_id):
        """
        create an entry in the result table
        (link betwen group and machine)
        """
        session = create_session()
        result = Results()
        result.FK_groups = group_id
        result.FK_machines = machine_id
        session.add(result)
        session.flush()
        session.close()
        return result.id

    def __deleteResult(self, group_id, machine_id, session = None):
        """
        delete an entry in the result table
        if the machine is not linked to any other group, it's removed
        """
        if not session:
            session = create_session()
        results = session.query(Results).filter(self.results.c.FK_machines == machine_id).filter(self.results.c.FK_groups == group_id).all()
        for result in results:
            session.delete(result)
            session.flush()

        still_linked = session.query(Results).filter(self.results.c.FK_machines == machine_id).count()
        if still_linked == 0:
            machine = session.query(Machines).filter(self.machines.c.id == machine_id).first()
            session.delete(machine)
            session.flush()

        session.close()
        return still_linked

    def __deleteResult4AllGroups(self, machine_id, session = None):
        """
        Delete a computer from the result of all groups
        """
        open_session = False
        if not session:
            open_session = True
            session = create_session()
        session.execute(self.results.delete(self.results.c.FK_machines == machine_id))
        session.execute(self.profilesResults.delete(self.profilesResults.c.FK_machines == machine_id))
        if open_session:
            session.flush()
            session.close()
        return True

    #####################################
    ## GROUP ACCESS

    def getGroupType(self, id):
        """
        get the nomenclature of a group type (ie group or profile) depending on the group type id
        """
        session = create_session()
        s = session.query(GroupType).filter(self.groupType.c.id == id).first()
        session.close()
        return s

    #########################################
    ## PERMISSIONS

    #######################################
    ## UTILITIES

    def __merge_join_query(self, select_from, join_tables):
        """
        utility function to merge a list of tables (join_tables) to a previous select_from
        and return the select_from
        """
        for table in join_tables:
            if type(table) == list:
                if table[1]: # outerjoin
                    if len(table) > 2: # specific on clause
                        select_from = select_from.outerjoin(table[0], table[2])
                    else:
                        select_from = select_from.outerjoin(table[0])
                else: # normal join
                    if len(table) > 2: # specific on clause
                        select_from = select_from.join(table[0], table[2])
                    else: # hum... why did u use a list!
                        select_from = select_from.join(table[0])
            else:
                select_from = select_from.join(table)
        return select_from

    ################################
    ## REQUEST / CONTENT / RESULTS

    def __insert_into_machines_and_profilesresults(self, connection, computers, groupid):
        """
        use __insert_into_machines_and_results for profiles
        """
        return self.__insert_into_machines_and_results(connection, computers, groupid, 1)

    def __insert_into_machines_and_results(self, connection, computers, groupid, type = 0):
        """
        This function is called by reload_group and addmembers_to_group to
        update the Results and Machines tables of the database.

        @param computers: list of dicts with {'uuid':uuid, 'hostname':name}
        @type computers: list
        """
        # Get already registered machines
        # and get a uuid to name hash
        uuids = []
        uuids2name = {}
        for x in computers:
            uuids.append(x["uuid"])
            uuids2name[x["uuid"]] = x["hostname"]
        existing = connection.execute(self.machines.select(self.machines.c.uuid.in_(uuids)))
        # Prepare insert for the Results table
        into_results = []
        existing_uuids_hash = {}
        need_name_update_hash = {}
        for machines_id, uuid, name in existing:
            if name != uuids2name[uuid]:
                # TODO update de machine
                need_name_update_hash[uuid] = uuids2name[uuid]
            into_results.append({
                "FK_groups" : groupid,
                "FK_machines" : machines_id
                })
            existing_uuids_hash[uuid] = None
        for uuid in need_name_update_hash:
            self.logger.debug("going to update %s name to %s in dyngroup machines cache"%(uuid, need_name_update_hash[uuid]))
            self.machines.update(self.machines.c.uuid==uuid).execute(name=need_name_update_hash[uuid])
        # Prepare insert for the Machines table
        into_machines = []
        for computer in computers:
            uuid = computer["uuid"]
            if uuid not in existing_uuids_hash:
                into_machines.append({
                    "uuid" : uuid,
                    "name" : computer["hostname"]
                    })
        # Insert needed Machines rows
        if into_machines:
            ret = connection.execute(self.machines.insert(), into_machines)
            id_sequence = ret.lastrowid
            # Prepare remaining insert for Results table
            for elt in into_machines:
                into_results.append({
                    "FK_groups" : groupid,
                    "FK_machines" : id_sequence
                })
                id_sequence = id_sequence + 1
        if into_results:
            if type == 0:
                # Insert into Results table only if there is something to insert
                connection.execute(self.results.insert(), into_results)
            else:
                # check if some machines are already in a profile
                session = create_session()
                ret = session.query(ProfilesResults).filter(self.profilesResults.c.FK_machines.in_(map(lambda x: x["FK_machines"], into_results))).all()
                session.close()
                if ret:
                    into_results_old = into_results
                    into_results = []
                    ret = map(lambda m:m.FK_machines, ret)
                    for result in into_results_old:
                        if not result['FK_machines'] in ret:
                            into_results.append(result)
                # Insert into ProfilesResults table only if there is something to insert
                if into_results:
                    connection.execute(self.profilesResults.insert(), into_results)
                else:
                    return False
        return True

    ################################
    ## MEMBERS

def id2uuid(id):
    return "UUID%s"%(str(id))

def uuid2id(uuid):
    return uuid.replace('UUID', '')

##############################################################################################################
class Groups(object):
    def getUUID(self):
        if hasattr(self, 'id'):
            return self.id
        logging.getLogger().warn("try to get %s uuid!"%(type(self)))
        return False

    def toH(self):
        ret = {
            'id':self.id,
            'name':self.name,
            'query':self.query,
            'type':self.type,
            'bool':self.bool,
            'uuid':id2uuid(self.id)
        }
        if hasattr(self, 'is_owner'): ret['is_owner'] = self.is_owner
        if hasattr(self, 'ro'): ret['ro'] = self.ro
#        if DyngroupDatabase().getGroupType(self.type): ret['type_label'] = DyngroupDatabase().getGroupType(self.type).value
        return ret
class GroupType(object): pass

class Machines(object):
    def toH(self):
        return {
            'id':self.id,
            'uuid':id2uuid(self.id),
            'hostname':self.name,
            'uuid':self.uuid
        }

class ProfilesData(object):
    def toH(self):
        return {
            'group_id':self.FK_groups,
            'entity_uuid':self.entity_uuid,
            'imaging_uuid':self.imaging_uuid
        }

class ProfilesPackages(object):
    def toH(self):
        return {
            'group_id':self.FK_groups,
            'package_id':self.package_id
        }

class ProfilesResults(object):
    def toH(self):
        return {
            'group_id':self.FK_groups,
            'machine_id':self.FK_machines
        }

class Results(object):
    def toH(self):
        return {
            'group_id':self.FK_groups,
            'machine_id':self.FK_machines,
            'id':self.id
        }

class ShareGroup(object):
    def toH(self):
        return {
            'id':self.id,
            'group_id':self.FK_groups,
            'sharedwith_id':self.FK_users,
            'display_in_menu':self.display_in_menu,
#            'type_label':DyngroupDatabase().getShareGroupType(self.type).value,
            'type':self.type,
            'user':DyngroupDatabase().getUser(self.FK_users).toH()
        }
class ShareGroupType(object): pass

class Users(object):
    def toH(self):
        return {
            'id':self.id,
            'login':self.login,
#            'type_label':DyngroupDatabase().getUsersType(self.type).value,
            'type':self.type
        }
class UsersType(object): pass

