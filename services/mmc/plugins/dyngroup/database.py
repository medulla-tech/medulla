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
Add a specific mmc-agent plugin level
"""
import logging

# SqlAlchemy
from sqlalchemy import and_, or_, asc, select
from sqlalchemy.orm import create_session

# MMC modules
from mmc.plugins.base import getUserGroups
import mmc.plugins.dyngroup
# PULSE2 modules
import pulse2.database.dyngroup
from pulse2.database.dyngroup import Groups, Machines, Results, Users
# Imported last
import re

log = logging.getLogger()

class DyngroupDatabase(pulse2.database.dyngroup.DyngroupDatabase):
    """
    The function defined here are only to use in the mmc because
    they need ctx objet to work and sometime some mmc helpers
    """

    ####################################
    ## USERS ACCESS

    ####################################
    ## MACHINES ACCESS

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
        if join_tables == None:
            return (select_from, filter_on)
        return (self.__merge_join_query(select_from, join_tables), filter_on)

    def __getMachines(self, ctx, gid, session = None):
        """
        get all the machines in a group
        the group is defined by its id
        """
        if not session:
            session = create_session()
        select_from, filter_on = self.__getMachinesFirstStep(ctx, session)
        if filter_on == None:
            filter_on = and_(self.groups.c.id == gid)
        else:
            filter_on = and_(self.groups.c.id == gid, filter_on)
        return session.query(Machines).select_from(select_from).filter(filter_on).all()

    def __getMachinesByGroupName(self, ctx, groupname, session = None):
        """
        get all the machines in a group
        the group is defined by its name
        """
        if not session:
            session = create_session()
        select_from, filter_on = self.__getMachinesFirstStep(ctx, session)
        if filter_on == None:
            filter_on = and_(self.groups.c.name == groupname)
        else:
            filter_on = and_(self.groups.c.name == groupname, filter_on)
        return session.query(Machines).select_from(select_from).filter(filter_on).all()

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

    ####################################
    ## SHARE ACCESS

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

    ####################################
    ## RESULT ACCESS

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

    def __getGroupInSessionFirstStep(self, ctx, session, ro = False):
        """
        return the query on groups, filtered on the context
        ie : only the group you can have access!
        """
        user_id = self.__getOrCreateUser(ctx)
        ug_ids = map(lambda x: x.id, self.__getUsers(getUserGroups(ctx.userid), 1, session)) # get all usergroups ids

        group = session.query(Groups).select_from(self.groups.join(self.users, self.groups.c.FK_users == self.users.c.id).outerjoin(self.shareGroup, self.groups.c.id == self.shareGroup.c.FK_groups))
        if ctx.userid == 'root' or ro:
            return group
        return group.filter(or_(self.users.c.login == ctx.userid, self.shareGroup.c.FK_users == user_id, self.shareGroup.c.FK_users.in_(ug_ids)))

    def __getGroupByNameInSession(self, ctx, session, name, ro = False):
        """
        get a group by it's name using the __getGroupInSessionFirstStep function
        wildcards are allowed
        ie : you will see only the group you can have access!
        """
        group = self.__getGroupInSessionFirstStep(ctx, session, ro)
        if re.search("\*", name):
            name = re.sub("\*", "%", name)
            group = group.filter(self.groups.c.name.like(name))
        else:
            group = group.filter(self.groups.c.name == name).first()
        return group

    def __getGroupInSession(self, ctx, session, id, ro = False):
        """
        get a group by it's id using the __getGroupInSessionFirstStep function
        wildcards are not allowed
        ie : you will see only the group you can have access!
        """
        group = self.__getGroupInSessionFirstStep(ctx, session, ro)
        group = group.filter(self.groups.c.id == id).first()
        return group

    def __allgroups_query(self, ctx, params, session = None, type = 0):
        """
        return a query on group
        filtered by several flags like canShow, dynamic, static, type (0 = group, 1 = profile)
        and filters like filter (on the group name with wildcards) and name (on the group name without wildcards)
        """
        (select_from, filter_on) = self.__get_group_permissions_request_first(ctx, session)
        groups = session.query(Groups).add_column(self.users.c.login).select_from(select_from).filter(self.groups.c.type == type)
        root_user = self.__getUser('root')
        if filter_on is not None:
            groups = groups.filter(filter_on)

        if ctx.userid == 'root' \
                and params.has_key('localSidebar') \
                and params['localSidebar'] \
                and root_user:
            groups = groups.filter(self.groups.c.FK_users == root_user.id)

        if params.has_key('canShow'):
            if params['canShow']:
                groups = groups.filter(self.shareGroup.c.display_in_menu == 1)
            else:
                groups = groups.filter(self.shareGroup.c.display_in_menu == 0)

        try:
            if params['owner']:
                groups = groups.filter(self.users.c.login == params['owner'])
        except KeyError:
            pass

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

    def countallgroups(self, ctx, params, type = 0):
        """
        count all group filtered by the params dict
        flags can be canShow, dynamic, static, type (0 = group, 1 = profile)
        and filters can be filter (on the group name with wildcards) and name (on the group name without wildcards)
        """
        session = create_session()
        groups = self.__allgroups_query(ctx, params, session, type)
        ret = groups.count()
        session.close()
        return ret

    def getallgroups(self, ctx, params, type = 0):
        """
        get all group filtered by the params dict
        flags can be canShow, dynamic, static, type (0 = group, 1 = profile)
        and filters can be filter (on the group name with wildcards) and name (on the group name without wildcards)
        it's also possible to use min and max to only have a page of the results
        """
        session = create_session()
        groups = self.__allgroups_query(ctx, params, session, type)
        groups = groups.order_by(self.groups.c.name)

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

        result = groups.all()
        ret = []
        # For each group check if the user is the owner of the group
        # (ie; the user that has created the group)
        for m in result:
            if m[1] == ctx.userid:
                m[0].is_owner = True
            ret.append(m[0])

        session.close()
        return ret

    def groupNameExists(self, ctx, name, id = None, isProfile = False):
        """
        return True if a group with this name exists and does not have the same id
        """
        type = 0
        if isProfile:
            type = 1
        if id == None or id == '':
            if self.countallgroups(ctx, {'name':name, 'owner':ctx.userid}, type) == 0:
                return False
            else:
                return True

        owner = self.get_group_owner(ctx, id)
        if owner == False:
            return True
        grps = self.getallgroups(ctx, {'name':name, 'owner':owner.login}, type)
        for grp in grps:
            if str(grp.id) != str(id):
                return True
        return False

    def get_group_owner(self, ctx, id):
        group = self.get_group(ctx, id)
        if group:
            session = create_session()
            user = session.query(Users).select_from(self.users.join(self.groups)).filter(self.groups.c.id == id).first()
            session.close()
            return user
        return False

    def get_group(self, ctx, id, ro = False):
        """
        get the group defined by it's id only if you can have access!
        """
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id, ro)
        if not group:
            session.close()
            return False
        if ro: # do tests to put the flag ro
            r = self.__getGroupInSession(ctx, session, id, False)
            if r:
                setattr(group, 'ro', False)
            else:
                setattr(group, 'ro', True)
        session.close()
        if group:
            return group
        return False

    def delete_group(self, ctx, id):
        """
        delete a group defined by it's id
        delete the results and the machines linked to that group if needed
        """
        # Is current group a profile ?
        if self.isprofile(ctx, id):
            resultTable = self.profilesResults
        else:
            resultTable = self.results

        self.__getOrCreateUser(ctx)
        connection = self.getDbConnection()
        trans = connection.begin()
        # get machines to possibly delete
        session = create_session()
        to_delete = [x.id for x in session.query(Machines).select_from(self.machines.join(resultTable)).filter(resultTable.c.FK_groups == id)]
        session.close()
        # Delete the previous results for this group in the Results table
        connection.execute(resultTable.delete(resultTable.c.FK_groups == id))
        # Delete all shares on the group before delete group
        self.__deleteShares(id, session)
        # Update the Machines table to remove ghost records
        self.__updateMachinesTable(connection, to_delete)
        # Delete the group from the Groups table
        connection.execute(self.profilesData.delete(self.profilesData.c.FK_groups == id))
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
        session.add(group)
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
            session.add(group)
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
        session.add(s)
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
        session.add(group)
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
        session.add(group)
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
        session.add(s)
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
        # FIXME: Root user cannot change group shortcut status
        # (hide or visible) if he's not creator of this group
        if s is not None:
            s.display_in_menu = 0
            session.add(s)
            session.flush()
            session.close()
            return s.id
        else:
            return None

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
        join_tables = [[self.users, False, self.users.c.id==self.groups.c.FK_users], 
                       [self.shareGroup, True, self.groups.c.id==self.shareGroup.c.FK_groups]]
        filters = None

        if ctx.userid<>'root':
            # Filter on user groups
            user_id = self.__getOrCreateUser(ctx)
            filters = [ self.users.c.login==ctx.userid, 
                        self.shareGroup.c.FK_users==user_id ]

            # get all usergroups ids
            ug_ids = []
            for user in self.__getUsers(getUserGroups(ctx.userid), 1, session):
                ug_ids.append(user.id)            
            if ug_ids:
                filters.append(self.shareGroup.c.FK_users.in_(ug_ids))

            filters = or_(*filters)

        return (join_tables, filters)

    def __get_group_permissions_request_first(self, ctx, session = None):
        """
        assemble the return of __permissions_query to have a couple :
        select_from and filter_on query parts
        """
        if not session:
            session = create_session()
        select_from = self.groups
        join_tables, filter_on = self.__permissions_query(ctx, session)
        if join_tables != None:
            select_from = self.__merge_join_query(select_from, join_tables)
        return (select_from, filter_on)

    def __get_group_permissions_request(self, ctx, session = None):
        """
        assemble the return of __get_group_permissions_request_first
        to get the result of the query
        """
        (select_from, filter_on) = self.__get_group_permissions_request_first(ctx, session)
        groups = session.query(Groups).select_from(select_from)
        if filter_on is not None:
            groups = groups.filter(filter_on)
        return groups

    #######################################
    ## UTILITIES

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
        group = self.__getGroupByNameInSession(ctx, session, name, False)
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

    def reload_group(self, ctx, id, queryManager):
        """
        update the content of a group (defined by it's id)
        """
        connection = self.getDbConnection()
        trans = connection.begin()
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id, False)
        is_profile = self.isprofile(ctx, id)
        filt = {}
        if is_profile:
            imaging_server = self.getProfileImagingServer(id)
            # replyToQuery call getRestrictedComputersList which know what to do with 'imaging_server'
            filt['imaging_server'] = imaging_server
        session.close()
        query = queryManager.getQueryTree(group.query, group.bool)
        result = mmc.plugins.dyngroup.replyToQuery(ctx, query, group.bool, 0, -1, False, True, filt)
        if is_profile:
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
        group = self.__getGroupInSession(ctx, session, id, False)
        session.close()
        connection = self.getDbConnection()
        trans = connection.begin()
        if type(uuids) == dict:
            uuids = uuids.values()
        if self.isprofile(ctx, id):
            if not self.__insert_into_machines_and_profilesresults(connection, uuids, group.id):
                trans.rollback()
                return False
        else:
            self.__insert_into_machines_and_results(connection, uuids, group.id)
        trans.commit()
        return True

    def delmembers_to_group(self, ctx, id, uuids):
        """
        Remove from a group member computers, specified by a uuids list.
        """
        # Is current group a profile ?
        if self.isprofile(ctx, id):
            resultTable = self.profilesResults
        else:
            resultTable = self.results

        group = self.get_group(ctx, id)
        connection = self.getDbConnection()
        trans = connection.begin()
        uuids = [x["uuid"] for x in uuids.values()]
        # Delete the selected machines from the Results table
        connection.execute(resultTable.delete(and_(resultTable.c.FK_groups == group.id, resultTable.c.FK_machines.in_(select([self.machines.c.id], self.machines.c.uuid.in_(uuids))))))
        # Update the Machines table
        self.__updateMachinesTable(connection, uuids)
        trans.commit()
        return True

