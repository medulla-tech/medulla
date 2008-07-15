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
from sqlalchemy import *
from sqlalchemy.exceptions import NoSuchTableError

# MMC modules
from mmc.plugins.base import getUserGroups
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.dyngroup.config import DGConfig
import mmc.plugins.dyngroup
from mmc.support.mmctools import Singleton

# Imported last
import logging

SA_MAYOR = 0
SA_MINOR = 3
DATABASEVERSION = 2

class DyngroupDatabase(Singleton):
    """
    Singleton Class to query the dyngroup database.

    """
    is_activated = False

    def db_check(self):
        if not self.__checkSqlalchemy():
            self.logger.error("Sqlalchemy version error : is not %s.%s.* version" % (SA_MAYOR, SA_MINOR))
            return False

        conn = self.connected()
        if conn:
            if conn != DATABASEVERSION:
                self.logger.error("Dyngroup database version error: v.%s needeed, v.%s found; please update your schema !" % (DATABASEVERSION, conn))
                return False
            elif type(conn) != int and type(conn) != long:
                self.logger.error("Dyngroup database version error: v.%s needeed, v.alpha found; please update your schema !" % (DATABASEVERSION))
                return False
        else:
            self.logger.error("Can't connect to database (s=%s, p=%s, b=%s, l=%s, p=******). Please check dyngroup.ini." % (self.config.dbhost, self.config.dbport, self.config.dbname, self.config.dbuser))
            return False

        return True

    def activate(self, conffile = None):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("Dyngroup database is connecting")
        self.config = DGConfig("dyngroup", conffile)
        self.db = create_engine(self.makeConnectionPath(), echo=False)
        self.metadata = BoundMetaData(self.db)
        try:
            self.initMappers()
        except NoSuchTableError:
            self.session = None
            return None
        self.metadata.create_all()
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("Dyngroup database connected")

    def __checkSqlalchemy(self):
        import sqlalchemy
        a_version = sqlalchemy.__version__.split('.')
        if len(a_version) > 2 and str(a_version[0]) == str(SA_MAYOR) and str(a_version[1]) == str(SA_MINOR):
            return True
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
        # Groups
        self.groups = Table("Groups", self.metadata,
                            Column('FK_user', Integer, ForeignKey('Users.id')),
                            autoload = True)
        mapper(Groups, self.groups)

        # Users
        self.users = Table("Users", self.metadata, autoload = True)
        mapper(Users, self.users)

        # ShareGroup
        self.shareGroup = Table("ShareGroup", self.metadata,
                            Column('FK_group', Integer, ForeignKey('Groups.id')),
                            Column('FK_user', Integer, ForeignKey('Users.id')),
                            autoload = True)
        mapper(ShareGroup, self.shareGroup)

        # Machines
        self.machines = Table("Machines", self.metadata, autoload = True)
        mapper(Machines, self.machines)

        # Results
        self.results = Table("Results", self.metadata,
                            Column('FK_group', Integer, ForeignKey('Groups.id')),
                            Column('FK_machine', Integer, ForeignKey('Machines.id')),
                            autoload = True)
        mapper(Results, self.results)

        # version
        self.version = Table("version", self.metadata, autoload = True)

    def connected(self):
        try:
            if (self.db != None) and (self.session != None):
                return self.version.select().execute().fetchone()[0]
            elif (self.db != None):
                return True
            return False
        except:
            return False

    def myfunctions(self):
        pass


    def enableLogging(self, level = None):
        """
        Enable log for sqlalchemy.engine module using the level configured by the db_debug option of the plugin configuration file.
        The SQL queries will be loggued.
        """
        if not level:
            level = self.config.dbdebug
        logging.getLogger("sqlalchemy.engine").setLevel(level)

    def disableLogging(self):
        """
        Disable log for sqlalchemy.engine module
        """
        logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

    ####################################
    def doThings(self):
        pass

    def getUser(self, id):
        session = create_session()
        user = session.query(Users).get(id)
        session.close()
        return user

    def __getOrCreateUser(self, ctx, user_id = None, type = 0):
        session = create_session()
        if user_id == None:
            user_id = ctx.userid
        user = self.__getUser(user_id, type)
        if not user:
            user = Users()
            user.login = user_id
            user.type = type
            session.save(user)
            session.flush()
        session.close()
        return user.id
        
    def __getUser(self, login, type = 0, session = create_session()):
        user = session.query(Users).filter(self.users.c.login == login).filter(self.users.c.type == type).first()
        return user

    def __getUsers(self, logins, type = 0, session = create_session()):
        users = session.query(Users)
        if type == None:
            users = users.filter(self.users.c.login.in_(*logins))
        else:
            users = users.filter(self.users.c.login.in_(*logins)).filter(self.users.c.type == type)
        return users

    def __getUsersInGroup(self, gid, session = create_session()):
        users = session.query(Users).select_from(self.users.join(self.share).join(self.groups)).filter(self.groups.c.id == gid).all()
        return users

    def __getMachines(self, gid, session = create_session()):
        machines = session.query(Machines).select_from(self.machines.join(self.results).join(self.groups)).filter(self.groups.c.id == gid).all()
        return machines

    def __getMachine(self, uuid, session = create_session()):
        machine = session.query(Machines).filter(self.machines.c.uuid == uuid).first()
        return machine

    def __getOrCreateMachine(self, uuid, name, session = create_session()):
        machine = self.__getMachine(uuid, session)
        if not machine:
            machine = Machines()
            machine.uuid = uuid
            machine.name = name
            session.save(machine)
            session.flush()
        session.close()
        return machine.id

    def __createShare(self, group_id, user_id):
        session = create_session()
        share = ShareGroup()
        share.FK_group = group_id
        share.FK_user = user_id
        session.save(share)
        session.flush()
        session.close()
        return share.id

    def __deleteShares(self, group_id, session = create_session()):
        users = self.__getUsersInGroup(group_id, session)
        for user in users:
            self.__deleteShare(group_id, user.id, session)

    def __deleteShare(self, group_id, user_id, session = create_session()):
        shares = session.query(ShareGroup).filter(self.shareGroup.c.FK_user == user_id).filter(self.shareGroup.c.FK_group == group_id).all()
        for share in shares:
            session.delete(share)
            session.flush()

        still_linked = session.query(ShareGroup).filter(self.shareGroup.c.FK_user == user_id).count()
        if still_linked == 0:
            user = session.query(Users).get(user_id)
            session.delete(user)
            session.flush()

        session.close()
        return still_linked

    def __createResult(self, group_id, machine_id):
        session = create_session()
        result = Results()
        result.FK_group = group_id
        result.FK_machine = machine_id
        session.save(result)
        session.flush()
        session.close()
        return result.id

    def __deleteResults(self, group_id, session = create_session()):
        machines = self.__getMachines(group_id, session)
        for machine in machines:
            self.__deleteResult(group_id, machine.id, session)

    def __deleteResult(self, group_id, machine_id, session = create_session()):
        results = session.query(Results).filter(self.results.c.FK_machine == machine_id).filter(self.results.c.FK_group == group_id).all()
        for result in results:
            session.delete(result)
            session.flush()

        still_linked = session.query(Results).filter(self.results.c.FK_machine == machine_id).count()
        if still_linked == 0:
            machine = session.query(Machines).filter(self.machines.c.id == machine_id).first()
            session.delete(machine)
            session.flush()

        session.close()
        return still_linked

    def __getGroupInSession(self, ctx, session, id):
        user_id = self.__getOrCreateUser(ctx)
        ug_ids = self.__getUsers(getUserGroups(ctx.userid), 1, session) # get all usergroups ids
        
        group = session.query(Groups).select_from(self.groups.outerjoin(self.shareGroup))
        group = group.filter(or_(self.users.c.login == ctx.userid, self.shareGroup.c.FK_user == user_id, self.shareGroup.c.FK_user.in_(*ug_ids)))
        group = group.filter(self.groups.c.id == id).first()
        return group
        
    def __result_group_query(self, ctx, session, id, filter = ''):
        result = session.query(Machines).select_from(self.machines.join(self.results))
        result = result.filter(self.results.c.FK_group == id)
        result = result.order_by(asc(self.machines.c.name))
        if filter:
            result = result.filter(self.machines.c.name.like('%'+filter+'%'))
        return result

    def __allgroups_query(self, ctx, params, session = create_session()):
        user_id = self.__getOrCreateUser(ctx)
        ug_ids = map(lambda x: x.id, self.__getUsers(getUserGroups(ctx.userid), 1, session)) # get all usergroups ids

        groups = session.query(Groups).select_from(self.groups.join(self.users, self.users.c.id == self.groups.c.FK_user).outerjoin(self.shareGroup, self.groups.c.id == self.shareGroup.c.FK_group))
        groups = groups.filter(or_(self.users.c.login == ctx.userid, self.shareGroup.c.FK_user == user_id, self.shareGroup.c.FK_user.in_(*ug_ids)))
        try:
            if params['canShow']:
                groups = groups.filter(self.groups.c.display_in_menu == 1)
            else:
                groups = groups.filter(self.groups.c.display_in_menu == 0)
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
                 groups = groups.filter(self.groups.c.name.like('%'+params['filter']+'%'))
        except KeyError:
            pass

        try:
            if params['name'] != None:
                groups = groups.filter(self.groups.c.name == params['name'])
        except KeyError:
            pass

        return groups

    def countallgroups(self, ctx, params):
        session = create_session()
        groups = self.__allgroups_query(ctx, params, session)
        count = groups.count()
        session.close()
        return count

    def getallgroups(self, ctx, params):
        session = create_session()
        groups = self.__allgroups_query(ctx, params, session)
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

        ret = groups.all()
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
        user_id = self.__getOrCreateUser(ctx)
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        session.close()
        if group:
            return group
        return False

    def delete_group(self, ctx, id):
        user_id = self.__getOrCreateUser(ctx)

        session = create_session()
        group = session.query(Groups).filter(self.groups.c.id == id).filter(self.groups.c.FK_user == user_id).first()
        if not group:
            return False

        results = session.query(Results).filter(self.results.c.FK_group == group.id).all()
        for result in results:
            machine = session.query(Machines).filter(self.machines.c.id == result.FK_machine).first()
            # check if the machine is in other groups
            inside = session.query(Results).filter(self.results.c.FK_machine == machine.id).count()
            if inside == 1:
                session.delete(machine)
            session.delete(result)
        session.delete(group)
        session.flush()
        session.close()
        return True

    def create_group(self, ctx, name, visibility):
        user_id = self.__getOrCreateUser(ctx)
        session = create_session()
        group = Groups()
        group.name = name
        group.display_in_menu = visibility
        group.FK_user = user_id
        session.save(group)
        session.flush()
        session.close()
        return group.id

    def setname_group(self, ctx, id, name):
        user_id = self.__getOrCreateUser(ctx)

        session = create_session()
        group = session.query(Groups).filter(self.groups.c.id == id).filter(self.groups.c.FK_user == user_id).first()
        if group:
            group.name = name
            session.save(group)
            session.flush()
            session.close()
            return True
        session.close()
        return False

    def setvisibility_group(self, ctx, id, visibility):
        user_id = self.__getOrCreateUser(ctx)

        session = create_session()
        group = session.query(Groups).filter(self.groups.c.id == id).filter(self.groups.c.FK_user == user_id).first()
        if group:
            group.display_in_menu = visibility
            session.save(group)
            session.flush()
            session.close()
            return True
        session.close()
        return False

    def request_group(self, ctx, id):
        group = self.get_group(ctx, id)
        return group.query

    def setrequest_group(self, ctx, gid, request):
        user_id = self.__getOrCreateUser(ctx)
        session = create_session()
        group = session.query(Groups).filter(self.groups.c.id == gid).filter(self.groups.c.FK_user == user_id).first()
        group.query = request
        session.save(group)
        session.flush()
        session.close()

        # remove all previous results
        self.__deleteResults(gid)

        return group.id

    def bool_group(self, ctx, id):
        group = self.get_group(ctx, id)
        return group.bool

    def setbool_group(self, ctx, id, bool):
        user_id = self.__getOrCreateUser(ctx)
        session = create_session()
        group = session.query(Groups).filter(self.groups.c.id == id).filter(self.groups.c.FK_user == user_id).first()
        group.bool = bool
        session.save(group)
        session.flush()
        session.close()
        return group.id

    def request(self, ctx, query, bool, min, max, filter, queryManager):
        return self.__request(ctx, query, bool, min, max, filter, queryManager)
    
    def requestresult_group(self, ctx, id, start, end, filter, queryManager):
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        return self.__request(ctx, group.query, group.bool, start, end, filter, queryManager, session)

    def __request(self, ctx, query, bool, start, end, filter, queryManager, session = create_session()):
        query = queryManager.getQueryTree(query, bool)
        result = mmc.plugins.dyngroup.replyToQuery(ctx, query, bool, start, end)

        ret = []
        if type(result) == dict:
            for key in result:
                machine = self.__getMachine(result[key][1]['objectUUID'][0], session)
                id = None
                if machine:
                    id = machine.id
                ret.append({'uuid': result[key][1]['objectUUID'][0], 'hostname': result[key][1]['cn'][0], 'id': id})
        else:
            for res in result:
                machine = self.__getMachine(res[1]['objectUUID'][0], session)
                id = None
                if machine:
                    id = machine.id
                ret.append({'uuid': res[1]['objectUUID'][0], 'hostname': res[1]['cn'][0], 'id': id})
            
        session.close()
        return ret

    def countrequestresult_group(self, ctx, id, filter, queryManager):
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        query = queryManager.getQueryTree(group.query, group.bool)
        result = mmc.plugins.dyngroup.replyToQueryLen(ctx, query, group.bool)
        session.close()
        return result

    def result_group(self, ctx, id, start, end, filter = ''):
        session = create_session()
        result = self.__result_group_query(ctx, session, id, filter)
        if int(start) != 0 or int(end) != -1:
            result = result.offset(int(start)).limit(int(end) - int(start))
        ret = result.all()
        session.close()
        return ret

    def countresult_group(self, ctx, id, filter = ''):
        session = create_session()
        result = self.__result_group_query(ctx, session, id, filter)
        ret = result.count()
        session.close()
        return ret

    def canshow_group(self, ctx, id):
        group = self.get_group(ctx, id)
        return (group.display_in_menu == 1)

    def show_group(self, ctx, id):
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        group.display_in_menu = 1
        session.save(group)
        session.flush()
        session.close()
        return group.id

    def hide_group(self, ctx, id):
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        group.display_in_menu = 0
        session.save(group)
        session.flush()
        session.close()
        return group.id

    def todyn_group(self, ctx, id):
        return self.__deleteResults(id)

    def isdyn_group(self, ctx, id):
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        q = None
        try:
            q = group.query
        except:
            pass
        session.close()
        return (q != None)

    def isrequest_group(self, ctx, id):
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)
        q = None
        try:
            q = group.query
        except:
            pass
        session.close()
        return (q != None and self.countresult_group(ctx, id) == 0)

    def reload_group(self, ctx, id, queryManager):
        session = create_session()
        group = self.__getGroupInSession(ctx, session, id)

        query = queryManager.getQueryTree(group.query, group.bool)
        result = mmc.plugins.dyngroup.replyToQuery(ctx, query, group.bool, 0, -1)

        for key in result:
            machine_id = self.__getOrCreateMachine(key[1]['objectUUID'][0], key[1]['cn'][0])
            self.__createResult(group.id, machine_id)
        session.close()
        return True

    def addmembers_to_group(self, ctx, id, uuids):
        group = self.get_group(ctx, id)
        session = create_session()
        for uuid in uuids:
            machine_id = self.__getOrCreateMachine(uuid, uuids[uuid]['hostname'])
            self.__createResult(group.id, machine_id)
        session.close()
        return True

    def delmembers_to_group(self, ctx, id, uuids):
        group = self.get_group(ctx, id)
        session = create_session()
        for uuid in uuids:
            machine = self.__getMachine(uuid, session)
            if machine:
                self.__deleteResult(group.id, machine.id, session)
            else:
                self.logger.debug("no member to delete! ('%s')" % (uuid))
        session.close()
        return True

    def share_with(self, ctx, id):
        session = create_session()
        ret = session.query(ShareGroup).filter(self.shareGroup.c.FK_group == id).all()
        session.close()
        return map(lambda x: x.toH(), ret)

    def add_share(self, ctx, id, shares):
        group = self.get_group(ctx, id)
        session = create_session()
        for login, type in shares:
            user_id = self.__getOrCreateUser(ctx, login, type)
            self.__createShare(group.id, user_id)
        session.close()
        return True

    def del_share(self, ctx, id, shares):
        group = self.get_group(ctx, id)
        session = create_session()
        for login, type in shares:
            user = self.__getUser(login, type, session) 
            if user:
                self.__deleteShare(group.id, user.id, session)
            else:
                self.logger.debug("no share to delete! ('%s')" % (login))
        session.close()
        return True

class Groups(object):
    def toH(self):
        return {
            'id':self.id,
            'name':self.name,
            'query':self.query,
            'display_in_menu':self.display_in_menu,
            'bool':self.bool
        }

class Users(object):
    def toH(self):
        return {
            'id':self.id,
            'login':self.login,
            'type':self.type
        }

class ShareGroup(object):
    def toH(self):
        return {
            'id':self.id,
            'group_id':self.FK_group,
            'sharedwith_id':self.FK_user,
            'type':self.FK_type,
            'user':DyngroupDatabase().getUser(self.FK_user).toH()
        }

class Machines(object):
    def toH(self):
        return {
            'id':self.id,
            'hostname':self.name,
            'uuid':self.uuid
        }

class Results(object):
    def toH(self):
        return {
            'id':self.id
        }



