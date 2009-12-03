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

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.sql import *

from sqlalchemy.exceptions import NoSuchTableError

# MMC modules
from mmc.plugins.base import getUserGroups
from mmc.plugins.dyngroup.config import DGConfig
import mmc.plugins.dyngroup
from pulse2.database.database_helper import DatabaseHelper
# Imported last
import logging
import re

SA_MAJOR = 0
SA_MINOR = 4
DATABASEVERSION = 2

class DyngroupDatabase(DatabaseHelper):
    """
    Singleton Class to query the dyngroup database.

    """
    is_activated = False

    def db_check(self):
        self.my_name = "Dyngroup"
        self.configfile = "dyngroup.ini"
        return DatabaseHelper.db_check(self, DATABASEVERSION)
    
    def activate(self, conffile = None):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("Dyngroup database is connecting")
        self.config = DGConfig("dyngroup", conffile)
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        self.metadata = MetaData(self.db)
        try:
            self.initMappers()
        except NoSuchTableError, e:
            self.logger.error(e)
            self.session = None
            return None
        self.metadata.create_all()
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("Dyngroup database connected (version:%s)"%(self.version.select().execute().fetchone()[0]))

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the inventory database
        """
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
            session.save_or_update(user)
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
        users = session.query(Users).select_from(self.users.join(self.share).join(self.groups)).filter(self.groups.c.id == gid).all()
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
        
    def getMachines(self, ctx, params):
        """
        get all machines defined by the given group name or id
        """
        if params.has_key('gname'):
            return self.__getMachinesByGroupName(ctx, params['gname'])
        if params.has_key('gid'):
            return self.__getMachines(ctx, params['gid'])
        return []

    def __getMachinesFirstStep(self, ctx, session = None):
        """
        utility function to get machines
        return the join and the filter part to build the query
        """
        if not session:
            session = create_session()
        select_from = self.machines.join(self.results).join(self.groups)
        (join_tables, filter_on) = self.__permissions_query(ctx, session)
        return (self.__merge_join_query(select_from, join_tables), filter_on)

    def __getMachines(self, ctx, gid, session = None):
        """
        get all the machines in a group
        the group is defined by its id
        """
        if not session:
            session = create_session()
        select_from, filter_on = self.__getMachinesFirstStep(ctx, session)
        return session.query(Machines).select_from(select_from).filter(and_(self.groups.c.id == gid, filter_on)).order_by(self.machines.c.name).all()

    def __getMachinesByGroupName(self, ctx, groupname, session = None):
        """
        get all the machines in a group
        the group is defined by its name
        """
        if not session:
            session = create_session()
        select_from, filter_on = self.__getMachinesFirstStep(ctx, session)
        return session.query(Machines).select_from(select_from).filter(and_(self.groups.c.name == groupname, filter_on)).order_by(self.machines.c.name).all()

    def __getMachine(self, uuid, session = None):
        """
        get a machine defined by its UUID
        """
        if not session:
            session = create_session()
        machine = session.query(Machines).filter(self.machines.c.uuid == uuid).first()
        return machine

    def __getOrCreateMachine(self, uuid, name, session = None):
        """
        get a machine defined by its UUID if it exists, else create it
        """
        if not session:
            session = create_session()
        machine = self.__getMachine(uuid, session)
        if not machine:
            machine = Machines()
            machine.uuid = uuid
            machine.name = name
            session.save_or_update(machine)
            session.flush()
        session.close()
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
        m = self.__getMachine(uuid)
        if m:
            session = create_session()
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
        session.save_or_update(share)
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
        session.save_or_update(share)
        session.flush()
        session.close()
        return share.id
        
    def __deleteShares(self, group_id, session = None):
        """
        delete all the shares for a group (betwen a group and several users)
        """
        if not session:
            session = create_session()
        users = self.__getUsersInGroup(group_id, session)
        for user in users:
            self.__deleteShare(group_id, user.id, session)
    
    def __deleteShare(self, group_id, user_id, session = None):
        """
        delete a share (betwen a group and a user)
        """
        if not session:
            session = create_session()
        shares = session.query(ShareGroup).filter(self.shareGroup.c.FK_users == user_id).filter(self.shareGroup.c.FK_groups == group_id).all()
        for share in shares:
            session.delete(share)
            session.flush()
    
        still_linked = session.query(ShareGroup).filter(self.shareGroup.c.FK_users == user_id).count()
        if still_linked == 0:
            user = session.query(Users).get(user_id)
            session.delete(user)
            session.flush()
    
        session.close()
        return still_linked

    def __getShareGroupInSession(self, id, user_id, session):
        """
        get the share item betwen the group and the user (if it exists)
        (handler for getShareGroup...)
        """
        return self.getShareGroup(id, user_id, session)
    
    def getShareGroup(self, group_id, user_id, session = None):
        """
        get the share item betwen the group and the user (if it exists)
        """
        if not session:
            session = create_session()
        share = session.query(ShareGroup).filter(self.shareGroup.c.FK_users == user_id).filter(self.shareGroup.c.FK_groups == group_id).first()
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

    def add_share(self, ctx, id, shares, visibility = 0):
        """
        add several shares, creating the users if they don't already exists
        """
        # often used with visibility = 0 as it's not at the same place that 
        # the share is created and that the visibility is set
        group = self.get_group(ctx, id)
        session = create_session()
        for login, t in shares:
            user_id = self.__getOrCreateUser(ctx, login, t)
            self.__createShare(group.id, user_id, visibility)
        session.close()
        return True

    def change_share_visibility(self, ctx, id, login, type, visibility = 0):
        """
        change the visibility flag on a share
        ie : change the fact that the user defined by it's id and login 
        see the group in the left menu
        """
        group = self.get_group(ctx, id)
        session = create_session()
        user_id = self.__getOrCreateUser(ctx, login, type)
        self.__changeShare(group.id, user_id, visibility)
        session.close()
        return True

    def del_share(self, ctx, id, shares):
        """
        remove the shares betwen the group defined by it's id
        and the users defined in shares (login and type)
        """
        group = self.get_group(ctx, id)
        session = create_session()
        for login, t in shares:
            user = self.__getUser(login, t, session)
            if user:
                self.__deleteShare(group.id, user.id, session)
            else:
                self.logger.debug("no share to delete! ('%s')" % (login))
        session.close()
        return True

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
        session.save_or_update(result)
        session.flush()
        session.close()
        return result.id
    
    def __deleteResults(self, ctx, group_id, session = None):
        """
        delete all the result objects linked to a group
        defined by it's id
        """
        if not session:
            session = create_session()
        machines = self.__getMachines(ctx, group_id, session)
        for machine in machines:
            self.__deleteResult(group_id, machine.id, session)
    
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
        if open_session:
            session.flush()
            session.close()
        return True
    
    def __result_group_query(self, ctx, session, id, filter = ''):
        """
        return the list of machines linked to a group (result) defined by the group id
        and filtered on the machine name
        """
        result = session.query(Machines)
        if self.isprofile(ctx, id):
            result = result.select_from(self.machines.join(self.profilesResults))
            result = result.filter(self.profilesResults.c.FK_groups == id)
            if filter:
                result = result.filter(self.machines.c.name.like('%'+filter+'%'))
        else:
            result = result.select_from(self.machines.join(self.results))
            result = result.filter(self.results.c.FK_groups == id)
            if filter:
                result = result.filter(self.machines.c.name.like('%'+filter+'%'))
        result = result.order_by(asc(self.machines.c.name))
        return result

    #####################################
    ## GROUP ACCESS

    def __getGroupInSessionFirstStep(self, ctx, session):
        """
        return the query on groups, filtered on the context
        ie : only the group you can have access!
        """
        user_id = self.__getOrCreateUser(ctx)
        ug_ids = map(lambda x: x.id, self.__getUsers(getUserGroups(ctx.userid), 1, session)) # get all usergroups ids
    
        group = session.query(Groups).select_from(self.groups.join(self.users, self.groups.c.FK_users == self.users.c.id).outerjoin(self.shareGroup, self.groups.c.id == self.shareGroup.c.FK_groups))
        return group.filter(or_(self.users.c.login == ctx.userid, self.shareGroup.c.FK_users == user_id, self.shareGroup.c.FK_users.in_(ug_ids)))
    
    def __getGroupByNameInSession(self, ctx, session, name):
        """
        get a group by it's name using the __getGroupInSessionFirstStep function 
        wildcards are allowed
        ie : you will see only the group you can have access!
        """
        group = self.__getGroupInSessionFirstStep(ctx, session)
        if re.search("\*", name):
            name = re.sub("\*", "%", name)
            group = group.filter(self.groups.c.name.like(name))
        else:
            group = group.filter(self.groups.c.name == name).first()
        return group
    
    def __getGroupInSession(self, ctx, session, id):
        """
        get a group by it's id using the __getGroupInSessionFirstStep function 
        wildcards are not allowed
        ie : you will see only the group you can have access!
        """
        group = self.__getGroupInSessionFirstStep(ctx, session)
        group = group.filter(self.groups.c.id == id).first()
        return group

    def __allgroups_query(self, ctx, params, session = None, type = 0):
        """
        return a query on group
        filtered by several flags like canShow, dynamic, static, type (0 = group, 1 = profile)
        and filters like filter (on the group name with wildcards) and name (on the group name without wildcards)
        """
        (select_from, filter_on) = self.__get_group_permissions_request_first(ctx, session)
        groups = session.query(Groups).add_column(self.users.c.login).select_from(select_from).filter(filter_on).filter(self.groups.c.type == type)
        
        if params.has_key('canShow'):
            if params['canShow']:
                groups = groups.filter(self.shareGroup.c.display_in_menu == 1)
            else:
                groups = groups.filter(self.shareGroup.c.display_in_menu == 0)
    
        try:
            if params['dynamic']:
                groups = groups.filter(self.groups.c.query != None)
        except KeyError:
            pass
    
        try:
            if params['static']:
                groups = groups.filter(self.groups.c.query == None)
        except KeyError:
            pass
    
        try:
            if params['filter']:
                 groups = groups.filter(self.groups.c.name.like('%'+params['filter'].encode('utf-8')+'%'))
        except KeyError:
            pass
    
        try:
            if params['name'] != None:
                groups = groups.filter(self.groups.c.name == params['name'].encode('utf-8'))
        except KeyError:
            pass
    
        return groups.group_by(self.groups.c.id)

    def getGroupType(self, id):
        """
        get the nomenclature of a group type (ie group or profile) depending on the group type id
        """
        session = create_session()
        s = session.query(GroupType).filter(self.groupType.c.id == id).first()
        session.close()
        return s

    def countallgroups(self, ctx, params, type = 0):
        """
        count all group filtered by the params dict
        flags can be canShow, dynamic, static, type (0 = group, 1 = profile)
        and filters can be filter (on the group name with wildcards) and name (on the group name without wildcards)
        """
        session = create_session()
        groups = self.__allgroups_query(ctx, params, session, type)
        s = select([func.count(text('*'))]).select_from(groups.compile().alias('foo'))
        result = session.execute(s)
        session.close()
        return result.fetchone()[0]

    def getallgroups(self, ctx, params, type = 0):
        """
        get all group filtered by the params dict
        flags can be canShow, dynamic, static, type (0 = group, 1 = profile)
        and filters can be filter (on the group name with wildcards) and name (on the group name without wildcards)
        it's also possible to use min and max to only have a page of the results
        """
        session = create_session()
        groups = self.__allgroups_query(ctx, params, session, type)
        
        min = 0
        try:
            if params['min']:
                min = int(params['min'])
                groups = groups.offset(int(min))
        except KeyError:
            pass

        try:
            if params['max'] != -1:
                max = int(params['max']) - min
                groups = groups.limit(max)
        except KeyError:
            pass

        ret = groups.order_by(self.groups.c.name).all()
        ret = map(lambda m: setattr(m[0], 'is_owner', m[1] == ctx.userid) or m[0], ret)
        
        session.close()
        return ret

    def groupNameExists(self, ctx, name, id = None):
        """
        return True if a group with this name exists and does not have the same id
        """
        if self.countallgroups(ctx, {'name':name}) == 0:
            return False
        if id == None:
            return True
        grps = self.getallgroups(ctx, {'name':name})
        for grp in grps:
            if str(grp.id) != str(id):
                return True
        return False

    def get_group(self, ctx, id):
        """
        get teh group defined by it's id only if you can have access!
        """
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        session.close()
        if group:
            return group
        return False

    def delete_group(self, ctx, id):
        """
        delete a group defined by it's id
        delete the results and the machines linked to that group if needed
        """
        user_id = self.__getOrCreateUser(ctx)
        connection = self.getDbConnection()
        trans = connection.begin()
        # get machines to possibly delete 
        session = create_session()
        to_delete = map(lambda x: x.id, session.query(Machines).select_from(self.machines.join(self.results)).filter(self.results.c.FK_groups == id))
        session.close()
        # Delete the previous results for this group in the Results table
        connection.execute(self.results.delete(self.results.c.FK_groups == id))
        # Update the Machines table to remove ghost records
        self.__updateMachinesTable(connection, to_delete)
        # Delete the group from the Groups table
        connection.execute(self.groups.delete(self.groups.c.id == id))
        trans.commit()
        return True

    def create_group(self, ctx, name, visibility, type = 0):
        """
        create a new group with the name, visibility and type (0 = group, 1 = profile)
        the owner will be the ctx
        a share will be created for the owner (needed to set the visibility)
        """
        user_id = self.__getOrCreateUser(ctx)
        session = create_session()
        group = Groups()
        group.name = name.encode('utf-8')
        group.FK_users = user_id
        group.type = type
        session.save_or_update(group)
        session.flush()
        session.close()
        
        # we now need to add an entry in ShareGroup for the creator
        self.__createShare(group.id, user_id, visibility, 1)
        return group.id

    def setname_group(self, ctx, id, name):
        """
        set a new name to the group defined by it's id
        only if the ctx user have the good permissions on it
        """
        session = create_session()
        group = self.__get_group_permissions_request(ctx, session).filter(self.groups.c.id == id).first()
        if group:
            group.name = name.encode('utf-8')
            session.save_or_update(group)
            session.flush()
            session.close()
            return True
        session.close()
        return False

    def setvisibility_group(self, ctx, id, visibility):
        """
        change the visibility on the group for the current user (ctx)
        """
        user_id = self.__getOrCreateUser(ctx)
        
        session = create_session()
        s = self.__getShareGroupInSession(id, user_id, session)
        s.display_in_menu = visibility
        session.save_or_update(s)
        session.flush()
        session.close()
        return True
                
    def request_group(self, ctx, id):
        """
        get the group (defined by it's id) request field
        """
        group = self.get_group(ctx, id)
        return group.query

    def setrequest_group(self, ctx, gid, request):
        """
        set a request to a group (defined by it's id)
        if the group is associated to machines, they are updated (to follow the new request)
        """
        session = create_session()
        group = self.__get_group_permissions_request(ctx, session).filter(self.groups.c.id == gid).first()
        group.query = request.encode('utf-8')
        session.save_or_update(group)
        session.flush()
        session.close()

        connection = self.getDbConnection()
        trans = connection.begin()
        c = session.query(Results).filter(self.results.c.FK_groups == gid).count()
        if c > 0:
            # Delete the previous results for this group in the Results table
            connection.execute(self.results.delete(self.results.c.FK_groups == gid))
            # Update the Machines table to remove ghost records
            self.__updateMachinesTable(connection)
        trans.commit()

        return group.id

    def bool_group(self, ctx, id):
        """
        get the group (defined by it's id) boolean equation
        """
        group = self.get_group(ctx, id)
        return group.bool

    def setbool_group(self, ctx, id, bool):
        """
        set a boolean equation to a group (defined by its id)
        """
        session = create_session()
        group = self.__get_group_permissions_request(ctx, session).filter(self.groups.c.id == id).first()
        group.bool = bool
        session.save_or_update(group)
        session.flush()
        session.close()
        return group.id

    def canshow_group(self, ctx, id):
        """
        tell if the group has to be shown in the left menu for the current user (ctx)
        """
        user_id = self.__getOrCreateUser(ctx)
        s = self.getShareGroup(id, user_id)
        if not s:
            return False
        return (s.display_in_menu == 1)

    def show_group(self, ctx, id):
        """
        set the visibility flag to true for the current user (ctx)
        """
        user_id = self.__getOrCreateUser(ctx)
        session = create_session()
        s = self.__getShareGroupInSession(id, user_id, session)
        s.display_in_menu = 1
        session.save_or_update(s)
        session.flush()
        session.close()
        return s.id

    def hide_group(self, ctx, id):
        """
        set the visibility flag to false for the current user (ctx)
        """
        user_id = self.__getOrCreateUser(ctx)
        session = create_session()
        s = self.__getShareGroupInSession(id, user_id, session)
        s.display_in_menu = 0
        session.save_or_update(s)
        session.flush()
        session.close()
        return s.id

    def todyn_group(self, ctx, id):
        """
        transform the group (defined by it's id) from result to request
        by removing all the linked results
        """
        return self.__deleteResults(ctx, id)

    def isdyn_group(self, ctx, id):
        """
        tell if a group (defined by it's id) is a dynamic group or a static one
        """
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        q = None
        try:
            q = group.query
        except:
            pass
        session.close()
        return (q != None and q != '')

    def isrequest_group(self, ctx, id):
        """
        tell if a group (defined by it's id) is a request or a result
        """
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        q = None
        try:
            q = group.query
        except:
            pass
        session.close()
        return (q != None and q != '' and self.countresult_group(ctx, id) == 0)

    ## GROUP / PROFILE

    def isprofile(self, ctx, id):
        """
        tell if an entry in the database is a group or a profile
        (as the 2 are stocked in the same table)
        """
        session = create_session()
        g = self.__getGroupInSession(ctx, session, id)
        session.close()
        if g:
            return (g.type == 1)
        else:
            return False
 
    #########################################
    ## PERMISSIONS

    def __permissions_query(self, ctx, session):
        """
        get all the parts to build a query to get only the group which the user can have access
        """
        user_id = self.__getOrCreateUser(ctx)
        ug_ids = map(lambda x: x.id, self.__getUsers(getUserGroups(ctx.userid), 1, session)) # get all usergroups ids
    
        return ([[self.users, False, self.users.c.id == self.groups.c.FK_users], [self.shareGroup, True, self.groups.c.id == self.shareGroup.c.FK_groups]], or_(self.users.c.login == ctx.userid, self.shareGroup.c.FK_users == user_id, self.shareGroup.c.FK_users.in_(ug_ids)))
    
    def __get_group_permissions_request_first(self, ctx, session = None):
        """
        assemble the return of __permissions_query to have a couple :
        select_from and filter_on query parts
        """
        if not session:
            session = create_session()
        select_from = self.groups
        join_tables, filter_on = self.__permissions_query(ctx, session)
        select_from = self.__merge_join_query(select_from, join_tables)
        return (select_from, filter_on)
    
    def __get_group_permissions_request(self, ctx, session = None):
        """
        assemble the return of __get_group_permissions_request_first
        to get the result of the query
        """
        (select_from, filter_on) = self.__get_group_permissions_request_first(ctx, session)
        groups = session.query(Groups).select_from(select_from).filter(filter_on)
        return groups
  
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
   
    def __getContent(self, ctx, group, queryManager):
        """
        get a group content (machines)
        """
        if group == None: return []
        session = create_session()
        if self.isrequest_group(ctx, group.id):
            ret = self.__request(ctx, group.query, group.bool, 0, -1, '', queryManager, session)
        else:
            ret = self.result_group(ctx, group.id, 0, -1)
        session.close()
        return ret

    def request(self, ctx, query, bool, min, max, filter, queryManager):
        """
        handler for __request (see __request)
        """
        return self.__request(ctx, query, bool, min, max, filter, queryManager)

    def requestresult_group(self, ctx, id, start, end, filter, queryManager):
        """
        handler for request taking the group as param (not the query and the boolean)
        """
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        return self.__request(ctx, group.query, group.bool, start, end, filter, queryManager, session)

    def result_group_by_name(self, ctx, name, min, max, filter, queryManager):
        """
        get the list of machines of the group (defined by it's name)
        """
        session = create_session()
        group = self.__getGroupByNameInSession(ctx, session, name)
        content = self.__getContent(ctx, group, queryManager)
        return content

    def __request(self, ctx, query, bool, start, end, filter, queryManager, session = None):
        """
        resolve a request (query to mmc.plugins.dyngroup.replyToQuery)
        """
        if not session:
            session = create_session()
        query = queryManager.getQueryTree(query, bool)
        result = mmc.plugins.dyngroup.replyToQuery(ctx, query, bool, start, end, True)
        if type(result) == dict:
            result = result.values()
        session.close()
        return result

    def countrequestresult_group(self, ctx, id, filter, queryManager):
        """
        count the number of result for the group defined by it's id
        """
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        query = queryManager.getQueryTree(group.query, group.bool)
        result = mmc.plugins.dyngroup.replyToQueryLen(ctx, query, group.bool)
        session.close()
        return result

    def result_group(self, ctx, id, start, end, filter = '', justId = True):
        """
        get the list of machines of the group (defined by it's id)
        the result can be only a list of ids (if justId is True) or the machines
        """
        session = create_session()
        result = self.__result_group_query(ctx, session, id, filter)
        if int(start) != 0 or int(end) != -1:
            result = result.offset(int(start)).limit(int(end) - int(start))
        if justId:
            ret = map(lambda m:m.uuid, result.all())
        else:
            ret = result.all()
        session.close()
        return ret

    def countresult_group(self, ctx, id, filter = ''):
        """
        count the number of result for the group defined by it's id
        """
        session = create_session()
        result = self.__result_group_query(ctx, session, id, filter)
        ret = result.count()
        session.close()
        return ret
       
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
            id_sequence = ret.cursor.lastrowid
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
                    print into_results
                    into_results = []
                    ret = map(lambda m:m.FK_machines, ret)
                    for result in into_results_old:
                        if not result['FK_machines'] in ret:
                            into_results.append(result)
                    print into_results
                # Insert into ProfilesResults table only if there is something to insert
                if into_results:
                    connection.execute(self.profilesResults.insert(), into_results)
                else:
                    return False
        return True
                    
    def reload_group(self, ctx, id, queryManager):
        """
        update the content of a group (defined by it's id)
        """
        connection = self.getDbConnection()
        trans = connection.begin()
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        session.close()
        query = queryManager.getQueryTree(group.query, group.bool)
        result = mmc.plugins.dyngroup.replyToQuery(ctx, query, group.bool, 0, -1, False, True)
        if self.isprofile(ctx, id):
            if not self.__insert_into_machines_and_profilesresults(connection, result, group.id):
                trans.rollback()
                return False
        else:
            self.__insert_into_machines_and_results(connection, result, group.id)
        trans.commit()
        return True

    ################################
    ## MEMBERS

    def addmembers_to_group(self, ctx, id, uuids):
        """
        Add member computers specified by a uuids list to a group.
        """
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        session.close()
        connection = self.getDbConnection()
        trans = connection.begin()
        if self.isprofile(ctx, id):
            if not self.__insert_into_machines_and_profilesresults(connection, uuids.values(), group.id):
                trans.rollback()
                return False
        else:
            self.__insert_into_machines_and_results(connection, uuids.values(), group.id)
        trans.commit()
        return True

    def delmembers_to_group(self, ctx, id, uuids):
        """
        Remove from a group member computers, specified by a uuids list.
        """
        group = self.get_group(ctx, id)
        connection = self.getDbConnection()
        trans = connection.begin()
        uuids = map(lambda x: x["uuid"], uuids.values())
        # Delete the selected machines from the Results table
        connection.execute(self.results.delete(and_(self.results.c.FK_groups == group.id, self.results.c.FK_machines.in_(select([self.machines.c.id], self.machines.c.uuid.in_(uuids))))))
        # Update the Machines table
        self.__updateMachinesTable(connection, uuids)
        trans.commit()
        return True


##############################################################################################################
class Groups(object):
    def toH(self):
        ret = {
            'id':self.id,
            'name':self.name,
            'query':self.query,
            'type':self.type,
            'bool':self.bool
        }
        if hasattr(self, 'is_owner'): ret['is_owner'] = self.is_owner
        if DyngroupDatabase().getGroupType(self.type): ret['type_label'] = DyngroupDatabase().getGroupType(self.type).value
        return ret
class GroupType(object): pass

class Machines(object):
    def toH(self):
        return {
            'id':self.id,
            'hostname':self.name,
            'uuid':self.uuid
        }

class ProfilesData(object):
    def toH(self):
        return {
            'group_id':self.FK_groups,
            'entity_id':self.entity_id,
            'imaging_id':self.imaging_id
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
            'type_label':DyngroupDatabase().getShareGroupType(self.type).value,
            'type':self.type,
            'user':DyngroupDatabase().getUser(self.FK_users).toH()
        }
class ShareGroupType(object): pass

class Users(object):
    def toH(self):
        return {
            'id':self.id,
            'login':self.login,
            'type_label':DyngroupDatabase().getUsersType(self.type).value,
            'type':self.type
        }
class UsersType(object): pass

