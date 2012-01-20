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
Provides access to MSC database
"""

# standard modules
import time

# SqlAlchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.sql import union
from sqlalchemy.exc import NoSuchTableError, TimeoutError

# ORM mappings
from pulse2.database.msc.orm.commands import Commands
from pulse2.database.msc.orm.commands_on_host import CommandsOnHost
from pulse2.database.msc.orm.commands_history import CommandsHistory
from pulse2.database.msc.orm.target import Target
from pulse2.database.msc.orm.bundle import Bundle
from pulse2.database.database_helper import DatabaseHelper

# Pulse 2 stuff
from pulse2.managers.location import ComputerLocationManager
import pulse2.time_intervals

# Imported last
import logging

DATABASEVERSION = 16
NB_DB_CONN_TRY = 2

# TODO need to check for useless function (there should be many unused one...)

class MscDatabase(DatabaseHelper):
    """
    Singleton Class to query the msc database.

    """

    def db_check(self):
        self.my_name = "Msc"
        self.configfile = "msc.ini"
        return DatabaseHelper.db_check(self, DATABASEVERSION)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("Msc database is connecting")
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize, pool_timeout = self.config.dbpooltimeout, convert_unicode = True)
        self.metadata = MetaData(self.db)
        if not self.initTables():
            return False
        if not self.initMappersCatchException():
            return False
        self.metadata.create_all()
        # FIXME: should be removed
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("Msc database connected")
        return self.db_check()

    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """
        try:
            # commands
            self.commands = Table("commands", self.metadata,
                                Column('dispatched', String(32), default='YES'),
                                Column('fk_bundle', Integer, ForeignKey('bundle.id')),
                                autoload = True)
            # commands_history
            self.commands_history = Table(
                "commands_history",
                self.metadata,
                Column('fk_commands_on_host', Integer, ForeignKey('commands_on_host.id')),
                autoload = True
            )
            # target
            self.target = Table(
                "target",
                self.metadata,
                autoload = True
            )
            # bundle
            self.bundle = Table(
                "bundle",
                self.metadata,
                autoload = True
            )
            # commands_on_host
            self.commands_on_host = Table(
                "commands_on_host",
                self.metadata,
                Column('fk_commands', Integer, ForeignKey('commands.id')),
                Column('fk_target', Integer, ForeignKey('target.id')),
                autoload = True
            )
            # version
            self.version = Table(
                "version",
                self.metadata,
                autoload = True
            )
        except NoSuchTableError, e:
            self.logger.error("Cant load the msc database : table '%s' does not exists"%(str(e.args[0])))
            return False
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the msc database
        """
        mapper(CommandsHistory, self.commands_history)
        mapper(CommandsOnHost, self.commands_on_host, properties = {
            'historys' : relation(CommandsHistory),
            }
        )
        mapper(Target, self.target, properties = {
            'commandsonhosts' : relation(CommandsOnHost)
            }
        )
        mapper(Bundle, self.bundle, properties = {})
        mapper(Commands, self.commands, properties = {
            'commandsonhosts' : relation(CommandsOnHost),
            'bundle' : relation(Bundle),
            }
        )
        # FIXME: Version is missing

    ####################################

    def getIdCommandOnHost(self, ctx, id):
        session = create_session()
        query = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.id == id)
        query = self.__queryUsersFilter(ctx, query)
        query = query.all()
        if type(query) != list:
            ret = query.id
        elif len(query) > 0:
            ret = []
            for q in query:
                ret.append(q.id)
        else:
            ret = -1
        session.close()
        return ret

    def createBundle(self, title = '', session = None):
        """
        Return a new Bundle
        """
        if session is None:
            session = create_session()
        bdl = Bundle()
        bdl.title = title
        bdl.do_reboot = 'disable'
        session.add(bdl)
        session.flush()
        return bdl

    def createCommand(self, session, package_id, start_file, parameters, files, start_script, clean_on_success, start_date, end_date, connect_as, creator, title, do_halt, do_reboot, do_wol, next_connection_delay, max_connection_attempt, do_inventory, maxbw, deployment_intervals, fk_bundle, order_in_bundle, proxies, proxy_mode):
        """
        Return a Command object
        """
        if type(files) == list:
            files = "\n".join(files)

        cmd = Commands()
        now = time.localtime()
        cmd.creation_date = time.strftime("%Y-%m-%d %H:%M:%S")
        cmd.package_id = package_id
        cmd.start_file = start_file
        cmd.parameters = parameters
        cmd.files = files
        cmd.start_script = start_script
        cmd.clean_on_success = clean_on_success
        cmd.start_date = start_date
        cmd.end_date = end_date
        cmd.connect_as = connect_as
        cmd.creator = creator
        cmd.title = title
        cmd.do_halt = ','.join(do_halt)
        cmd.do_reboot = do_reboot
        cmd.do_wol = do_wol
        cmd.next_connection_delay = next_connection_delay
        cmd.max_connection_attempt = max_connection_attempt
        cmd.do_inventory = do_inventory
        cmd.maxbw = maxbw
        cmd.deployment_intervals = pulse2.time_intervals.normalizeinterval(deployment_intervals)
        cmd.fk_bundle = fk_bundle
        cmd.order_in_bundle = order_in_bundle
        cmd.proxy_mode = proxy_mode # FIXME: we may add some code to check everything is OK
        cmd.state = 'active'
        session.add(cmd)
        session.flush()
        return cmd

    def createCommandsOnHost(self, command, target, target_id, target_name, cmd_max_connection_attempt, scheduler = None, order_in_proxy = None, max_clients_per_proxy = 0):
        logging.getLogger().debug("Create new command on host '%s'" % target_name)
        return {
            "host" : target_name,
            "start_date" : None,
            "end_date" : None,
            "next_launch_date" : time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_state" : "scheduled",
            "uploaded" : "TODO",
            "executed" : "TODO",
            "deleted" : "TODO",
            "attempts_left" : cmd_max_connection_attempt,
            "next_attempt_date_time" : 0,
            "scheduler" : scheduler,
            "order_in_proxy" : order_in_proxy,
            "max_clients_per_proxy": max_clients_per_proxy,
            "fk_target" : target_id,
            "fk_commands" : command
            }

    def createTarget(self, targetName, targetUuid, targetIp, targetMac, targetBCast, targetNetmask, mirror, groupID = None):
        """
        Inject a new Target object in our MSC database
        Return the corresponding Target object
        """
        target = { "target_name" : targetName,
                   "target_uuid" : targetUuid,
                   "target_ipaddr" : targetIp,
                   "target_macaddr" : targetMac,
                   "target_bcast" : targetBCast,
                   "target_network" : targetNetmask,
                   "mirrors" : mirror,
                   "id_group" : groupID }
        return target

    def getCommandsonhostsAndSchedulersOnBundle(self, fk_bundle):
        """
        """
        conn = self.getDbConnection()
        c_ids = select([self.commands.c.id], self.commands.c.fk_bundle == fk_bundle).execute()
        c_ids = map(lambda x:x[0], c_ids)
        result = select([self.commands_on_host.c.id, self.commands_on_host.c.scheduler], self.commands_on_host.c.fk_commands.in_(c_ids)).execute()
        schedulers = {}
        for row in result:
            coh, scheduler = row
            if scheduler in schedulers:
                schedulers[scheduler].append(coh)
            else:
                schedulers[scheduler] = [coh]
        conn.close()
        return schedulers

    def getCommandsonhostsAndSchedulers(self, c_id):
        """
        For a given command id, returns a dict with:
         - keys: a scheduler id (e.g. scheduler_01)
         - values: the related commands_on_host for each scheduler
        """
        conn = self.getDbConnection()
        result = select([self.commands_on_host.c.id, self.commands_on_host.c.scheduler], self.commands_on_host.c.fk_commands == c_id).execute()
        schedulers = {}
        for row in result:
            coh, scheduler = row
            if scheduler in schedulers:
                schedulers[scheduler].append(coh)
            else:
                schedulers[scheduler] = [coh]
        conn.close()
        return schedulers

    def __queryUsersFilterBis(self, ctx):
        """
        Build a part of a query for commands, that add user filtering
        """
        q = 1==1
        if ctx.filterType == "mine":
            # User just want to get her/his commands
            return self.commands.c.creator == ctx.userid
        elif ctx.filterType == "all":
            # User want to get all commands she/he has the right to see
            if ctx.userid == "root":
                # root can see everything, so no filter for root
                return 1 == 1
            elif ctx.locationsCount not in [None, 0, 1] and ctx.userids:
                # We have multiple locations, and a list of userids sharing the
                # same locations of the current user
                return self.commands.c.creator.in_(ctx.userids)
        else:
            # Unknown filter type
            self.logger.warn("Unknown filter type when querying commands")
            if ctx.locationsCount not in [None, 0, 1]:
                # We have multiple locations (entities) in database, so we
                # filter the results using the current userid
                return self.commands.c.creator == ctx.userid
        return 1 == 1

    def __queryUsersFilter(self, ctx, q):
        """
        Build a part of a query for commands, that add user filtering
        """
        # should use return q.filter(self.__queryUsersFilterBis(ctx))
        if ctx.filterType == "mine":
            # User just want to get her/his commands
            q = q.filter(self.commands.c.creator == ctx.userid)
        elif ctx.filterType == "all":
            # User want to get all commands she/he has the right to see
            if ctx.userid == "root":
                # root can see everything, so no filter for root
                pass
            elif ctx.locationsCount not in [None, 0, 1] and ctx.userids:
                # We have multiple locations, and a list of userids sharing the
                # same locations of the current user
                q = q.filter(self.commands.c.creator.in_(ctx.userids))
            # else if we have just one location, we don't apply any filter. The
            #     user can see the commands of all users

        else:
            # Unknown filter type
            self.logger.warn("Unknown filter type when querying commands")
            if ctx.locationsCount not in [None, 0, 1]:
                # We have multiple locations (entities) in database, so we
                # filter the results using the current userid
                q = q.filter(self.commands.c.creator == ctx.userid)
        return q

    def __queryAllCommandsonhostBy(self, session, ctx):
        """
        Built a part of the query for the *AllCommandsonhost* methods
        """

        join = self.commands_on_host.join(self.commands).join(self.target).outerjoin(self.bundle)
        q = session.query(CommandsOnHost, Commands, Target, Bundle)
        q = q.select_from(join)
        q = self.__queryUsersFilter(ctx, q)
        return q

    def getAllCommandsonhostCurrentstate(self, ctx): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        ret = ret.add_column(self.commands.c.max_connection_attempt).filter(self.commands_on_host.c.current_state <> ''). \
                group_by([self.commands_on_host.c.current_state, self.commands_on_host.c.attempts_left, self.commands.c.max_connection_attempt]). \
                order_by(asc(self.commands_on_host.c.next_launch_date))
        # x[0] contains a commands_on_host object x[1] contains commands
        l = []
        for x in ret.all(): # patch to have rescheduled as a "state" ... must be emulated
            if x[0].current_state == 'scheduled' and x[0].attempts_left != x[1].max_connection_attempt and not 'rescheduled' in l:
                l.append('rescheduled')
            elif not x[0].current_state in l:
                l.append(x[0].current_state)
        session.close()
        return l

    def countAllCommandsonhostByCurrentstate(self, ctx, current_state, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        if current_state == 'rescheduled': # patch to have rescheduled as a "state" ... must be emulated
            ret = ret.filter(and_(self.commands.c.max_connection_attempt != self.commands_on_host.c.attempts_left, self.commands_on_host.c.current_state == 'scheduled'))
        elif current_state == 'scheduled':
            ret = ret.filter(and_(self.commands.c.max_connection_attempt == self.commands_on_host.c.attempts_left, self.commands_on_host.c.current_state == 'scheduled'))
        else:
            ret = ret.filter(self.commands_on_host.c.current_state == current_state)
        # the join in itself is useless here, but we want to have exactly
        # the same result as in getAllCommandsonhostByCurrentstate
        if filt != '':
            ret = ret.filter(or_(self.commands_on_host.c.host.like('%'+filt+'%'), self.commands.c.title.like('%'+filt+'%')))
        c = ret.count()
        session.close()
        return c

    def getAllCommandsonhostByCurrentstate(self, ctx, current_state, min = 0, max = 10, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        if current_state == 'rescheduled': # patch to have rescheduled as a "state" ... must be emulated
            ret = ret.filter(and_(self.commands.c.max_connection_attempt != self.commands_on_host.c.attempts_left, self.commands_on_host.c.current_state == 'scheduled'))
        elif current_state == 'scheduled':
            ret = ret.filter(and_(self.commands.c.max_connection_attempt == self.commands_on_host.c.attempts_left, self.commands_on_host.c.current_state == 'scheduled'))
        else:
            ret = ret.filter(self.commands_on_host.c.current_state == current_state)
        if filt != '':
            ret = ret.filter(or_(self.commands_on_host.c.host.like('%'+filt+'%'), self.commands.c.title.like('%'+filt+'%')))
        ret = ret.order_by(desc(self.commands_on_host.c.id))
        ret = ret.offset(int(min))
        ret = ret.limit(int(max)-int(min))
        l = []
        for x in ret.all():
            bundle = x[3]
            if bundle != None:
                bundle = bundle.toH()
            l.append([x[0].toH(), x[1].toH(), x[2].toH(), bundle])
        session.close()
        return l

    def countAllCommandsonhostByType(self, ctx, type, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        if filt != '':
            ret = ret.filter(or_(self.commands_on_host.c.host.like('%'+filt+'%'), self.commands.c.title.like('%'+filt+'%')))
        if int(type) == 0: # all
            pass
        elif int(type) == 1: # pending
            ret = ret.filter(self.commands_on_host.c.current_state.in_( ('upload_failed', 'execution_failed', 'delete_failed', 'inventory_failed', 'not_reachable', 'pause', 'stop', 'stopped', 'scheduled') ))
        elif int(type) == 2: # running
            ret = ret.filter(self.commands_on_host.c.current_state.in_( ('upload_in_progress', 'upload_done', 'execution_in_progress', 'execution_done', 'delete_in_progress', 'delete_done', 'inventory_in_progress', 'inventory_done') ))
        elif int(type) == 3: # finished
            ret = ret.filter(self.commands_on_host.c.current_state.in_( ('done', 'failed', 'over_timed') ))
        c = ret.count()
        session.close()
        return c

    def getAllCommandsonhostByType(self, ctx, type, min, max, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        if filt != '':
            ret = ret.filter(or_(self.commands_on_host.c.host.like('%'+filt+'%'), self.commands.c.title.like('%'+filt+'%')))
        if int(type) == 0: # all
            pass
        elif int(type) == 1: # pending
            ret = ret.filter(self.commands_on_host.c.current_state.in_( ('upload_failed', 'execution_failed', 'delete_failed', 'inventory_failed', 'not_reachable', 'pause', 'stop', 'stopped', 'scheduled') ))
        elif int(type) == 2: # running
            ret = ret.filter(self.commands_on_host.c.current_state.in_( ('upload_in_progress', 'upload_done', 'execution_in_progress', 'execution_done', 'delete_in_progress', 'delete_done', 'inventory_in_progress', 'inventory_done') ))
        elif int(type) == 3: # finished
            ret = ret.filter(self.commands_on_host.c.current_state.in_( ('done', 'failed', 'over_timed') ))
        ret = ret.order_by(desc(self.commands_on_host.c.id))
        ret = ret.offset(int(min))
        ret = ret.limit(int(max)-int(min))
        l = []
        for x in ret.all():
            bundle = x[3]
            if bundle != None:
                bundle = bundle.toH()
            l.append([x[0].toH(), x[1].toH(), x[2].toH(), bundle])
        session.close()
        return l

    def countAllCommandsOnHostBundle(self, ctx, uuid, fk_bundle, filt, history): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.target.c.target_uuid == uuid).filter(self.commands.c.creator == ctx.userid).filter(self.commands.c.fk_bundle == fk_bundle)
#        ret = ret.filter(self.commands_on_host.c.id == self.target.c.fk_commands_on_host)
        if filt != '':
            ret = ret.filter(self.commands.c.title.like('%'+filt+'%'))
        if history:
            ret = ret.filter(self.commands_on_host.c.current_state == 'done')
        else:
            ret = ret.filter(self.commands_on_host.c.current_state != 'done')
        c = ret.count()
        session.close()
        return c

    def countAllCommandsOnHost(self, ctx, uuid, filt):
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx, uuid):
            session = create_session()
            ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.target.c.target_uuid == uuid)
            #.filter(self.commands.c.creator == ctx.userid)
            if filt != '':
                ret = ret.filter(self.commands.c.title.like('%'+filt+'%'))
            c = ret.count()
            session.close()
            return c
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return False

    def getAllCommandsOnHost(self, ctx, uuid, min, max, filt):
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx, uuid):
            session = create_session()
            query = session.query(Commands).add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state)
            query = query.select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.target_uuid == uuid)
            #.filter(self.commands.c.creator == ctx.userid)
            if filt != '':
                query = query.filter(self.commands.c.title.like('%'+filt+'%'))
            query = query.order_by(asc(self.commands_on_host.c.next_launch_date))
            query = query.offset(int(min))
            query = query.limit(int(max)-int(min))
            ret = query.all()
            session.close()
            return map(lambda x: (x[0].toH(), x[1], x[2]), ret)
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return []

    def getAllCommandsConsult(self, ctx, min, max, filt):
        filtering2_1 = and_(self.commands.c.fk_bundle == None, or_(self.commands.c.title.like('%%%s%%'%(filt)), self.commands.c.creator.like('%%%s%%'%(filt))), self.__queryUsersFilterBis(ctx))
        filtering2_2 = and_(self.commands.c.fk_bundle == self.bundle.c.id, or_(self.commands.c.title.like('%%%s%%'%(filt)), self.commands.c.creator.like('%%%s%%'%(filt)), self.bundle.c.title.like('%%%s%%'%(filt))), self.__queryUsersFilterBis(ctx))
                
        session = create_session()
        size1 = session.query(Commands).filter(filtering2_1).filter(self.commands.c.fk_bundle == None).count() or 0
        size2 = select(['bid'], True, select([self.commands.c.fk_bundle.label('bid')], and_(filtering2_2, self.commands.c.fk_bundle != None)).group_by('bid').alias('BIDS') ).alias('C').count()
 
        conn = self.getDbConnection()
        size2 = conn.execute(size2).fetchone()
        
        size = int(size1) + int(size2[0])

        u2 = union(
                select([self.commands.c.id, func.concat('CMD_', self.commands.c.id).label('bid'), self.commands.c.creation_date], filtering2_1),
                select([self.commands.c.id, self.commands.c.fk_bundle.label('bid'), self.commands.c.creation_date], filtering2_2) 
        ).group_by('bid').order_by(desc('creation_date')).offset(int(min)).limit(int(max)-int(min))

        conn = self.getDbConnection()
        cmds = map(lambda e: e[0], conn.execute(u2).fetchall())
        conn.close()

        session = create_session()

        query = session.query(Commands).add_column(self.commands.c.fk_bundle).add_column(self.commands_on_host.c.host).add_column(self.commands_on_host.c.id)
        query = query.add_column(self.target.c.id_group).add_column(self.bundle.c.title).add_column(self.target.c.target_uuid)
        query = query.select_from(self.commands.join(self.commands_on_host).join(self.target).outerjoin(self.bundle))
        
        cmds = query.filter(self.commands.c.id.in_(cmds)).group_by(self.commands.c.id).order_by(desc(self.commands.c.creation_date)).all()

        session.close()

        ret = []
        for cmd, bid, target_name, cohid, gid, btitle, target_uuid in cmds:
            if bid != None: # we are in a bundle
                if gid != None and gid != '':
                    ret.append({
                            'title':btitle,
                            'creator':cmd.creator,
                            'creation_date':cmd.creation_date,
                            'bid':bid,
                            'cmdid':'',
                            'target':'group %s'%gid,
                            'gid':gid, 
                            'uuid':'',
                            'status':self.getCommandOnBundleStatus(ctx, bid)
                    })
                else:
                    ret.append({
                            'title':btitle,
                            'creator':cmd.creator,
                            'creation_date':cmd.creation_date,
                            'bid':bid,
                            'cmdid':'',
                            'target':target_name,
                            'uuid':target_uuid,
                            'gid':'',
                            'status':self.getCommandOnBundleStatus(ctx, bid)
                    })
            else: # we are not in a bundle
                if gid != None and gid != '':
                    ret.append({
                            'title':cmd.title,
                            'creator':cmd.creator,
                            'creation_date':cmd.creation_date,
                            'bid':'',
                            'cmdid':cmd.id,
                            'target':'group %s'%gid,
                            'gid':gid,
                            'uuid':'',
                            'status':self.getCommandOnGroupStatus(ctx, cmd.id)
                    })
                else:
                    ret.append({
                            'title':cmd.title,
                            'creator':cmd.creator,
                            'creation_date':cmd.creation_date,
                            'bid':'',
                            'cmdid':cmd.id,
                            'cohid':cohid,
                            'target':target_name,
                            'uuid':target_uuid,
                            'gid':'',
                            'status':{},
                            'current_state':self.getCommandOnHostCurrentState(ctx, cmd.id)
                    })
            
        return [size, ret]

    ###################
    def __displayLogsQuery(self, ctx, params, session):
        query = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target))
        if params['gid'] != None:
            query = query.filter(self.target.c.id_group == params['gid'])
        if params['uuid'] != None:
            query = query.filter(self.target.c.target_uuid == params['uuid'])
        if params['filt'] != None:
            query = query.filter(self.commands.c.title.like('%'+params['filt']+'%'))
        if params['finished']:
            query = query.filter(self.commands_on_host.c.current_state.in_(['done', 'failed', 'over_timed']))
        else:
            # If we are querying on a bundle, we also want to display the
            # commands_on_host flagged as done
            if params['b_id'] == None:
                query = query.filter(not_(self.commands_on_host.c.current_state.in_(['done', 'failed', 'over_timed'])))
        query = self.__queryUsersFilter(ctx, query)
        return query.group_by(self.commands.c.id).order_by(desc(params['order_by']))

    def __doneBundle(self, params, session):
        query = session.query(Commands).select_from(self.commands.join(self.commands_on_host))
        filter = []
        if params['b_id'] != None:
            filter = [self.commands.c.fk_bundle == params['b_id']]
        elif params['cmd_id'] != None:
            filter = [self.commands.c.id == params['cmd_id']]
        filter.append(not_(self.commands_on_host.c.current_state.in_(['done', 'failed', 'over_timed'])))
        query = query.filter(and_(*filter))
        how_much = query.count()
        if how_much > 0:
            return False
        return True

    def __displayLogsQuery2(self, ctx, params, session):
        filter = []
        select_from = None
        group_by = False
        group_clause = False

        # Get query parts
        query = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target))
        query = query.add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state)
        if params['cmd_id'] != None: # COH
            filter = [self.commands.c.id == params['cmd_id']]
            if params['b_id'] != None:
                filter.append(self.commands.c.fk_bundle == params['b_id'])
        else: # CMD
            if params['b_id'] != None:
                filter = [self.commands.c.fk_bundle == params['b_id']]
            group_by = True
            group_clause = self.commands.c.id

        if params['gid'] != None: # Filter on a machines group id
            filter.append(self.target.c.id_group == params['gid'])

        if params['uuid'] != None: # Filter on a machine uuid
            filter.append(self.target.c.target_uuid == params['uuid'])

        if params['filt'] != None: # Filter on a commande names
            filter.append(self.commands.c.title.like('%s%s%s' % ('%', params['filt'], '%')))

        if params['b_id'] == None:
            is_done = self.__doneBundle(params, session)
            if params['finished'] and not is_done: # Filter on finished commands only
                filter.append(1 == 0) # send nothing
            elif not params['finished'] and is_done:
                # If we are querying on a bundle, we also want to display the
                # commands_on_host flagged as done
                filter.append(1 == 0) # send nothing
#        else:
#            is_done = self.__doneBundle(params, session)
#            self.logger.debug("is the bundle done ? %s"%(str(is_done)))

        query = self.__queryUsersFilter(ctx, query)
        query = query.filter(and_(*filter))

        if group_by:
            query = query.group_by(group_clause)

        return query

    def __displayLogsQueryGetIds(self, cmds, min = 0, max = -1, params = {}):
        i = 0
        min = int(min)
        max = int(max)
        ids = []
        defined = {}
        for cmd in cmds:
            id, fk_bundle = cmd
            if max != -1 and max-1 < i:
                break
            if i < min:
                if fk_bundle != 'NULL' and fk_bundle != None and not defined.has_key(fk_bundle):
                    defined[fk_bundle] = id
                    i += 1
                elif fk_bundle == 'NULL' or fk_bundle == None:
                    i += 1
                continue
            if fk_bundle != 'NULL' and fk_bundle != None and not defined.has_key(fk_bundle):
                defined[fk_bundle] = id
                if 'finished' in params and params['finished']:
                    # Check that the bundle has all its commands_on_host set
                    # to state done or failed.
                    session = create_session()
                    count_query = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.fk_bundle == fk_bundle).filter(not_(self.commands_on_host.c.current_state.in_( ('done', 'failed', 'over_timed') ))).count()
                    session.close()
                    if count_query > 0:
                        # Some CoH are not in the done or failed states, so
                        # we won't display this bundle.
                        continue
                else:
                    # Check that the bundle has all its commands_on_host set
                    # to state done or failed.
                    session = create_session()
                    count_query = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.fk_bundle == fk_bundle).filter(not_(self.commands_on_host.c.current_state.in_( ('done', 'failed', 'over_timed') ))).count()
                    session.close()
                    if count_query == 0:
                        # Some CoH are not in the done or failed states, so
                        # we won't display this bundle.
                        continue
                ids.append(id)
                i += 1
            elif fk_bundle == 'NULL' or fk_bundle == None:
                ids.append(id)
                i += 1
        return ids

    def __displayLogReturn(self, ctx, list):
        # list is : cmd, cohid, cohstate
        cohids = map(lambda x: x[1], list)
        cohs = self.getCommandsOnHosts(ctx, cohids)
        ret = []
        for element in list:
            if cohs.has_key(element[1]):
                ret.append((element[0].toH(), element[1], element[2], cohs[element[1]].toH()))
            else:
                ret.append((element[0].toH(), element[1], element[2], False))
        return ret

    def displayLogs(self, ctx, params = None): # TODO USE ctx
        if params is None: # do not change the default value!
            params = {}
        session = create_session()
        for i in ('b_id', 'cmd_id', 'coh_id', 'gid', 'uuid', 'filt'):
            if not params.has_key(i) or params[i] == '':
                params[i] = None
        if not params.has_key('min'):
            params['min'] = 0
        if not params.has_key('max'):
            params['max'] = -1
        if not params.has_key('finished') or params['finished'] == '':
            params['finished'] = False
        try:
            params['order_by'] = getattr(self.commands_on_host.c, params['order_by'])
        except:
            params['order_by'] = getattr(self.commands_on_host.c, 'id')

        size = 0

#   msc.displayLogs({'max': 10, 'finished': '', 'filt': '', 'uuid': 'UUID1620', 'min': 0},)
        if params['gid'] or params['uuid']:     # we want informations about one group / host
            if params['cmd_id']:                # we want informations about one command on one group / host
                # Using min/max, we get a range of commands, but we always want
                # the total count of commands.
                ret = self.__displayLogsQuery2(ctx, params, session).offset(int(params['min'])).limit(int(params['max'])-int(params['min'])).all()
                size = self.__displayLogsQuery2(ctx, params, session).count()
                session.close()
                return size, self.__displayLogReturn(ctx, ret)
            elif params['b_id']:                # we want informations about one bundle on one group / host
                # Using min/max, we get a range of commands, but we always want
                # the total count of commands.
                ret = self.__displayLogsQuery2(ctx, params, session).order_by(self.commands.c.order_in_bundle).offset(int(params['min'])).limit(int(params['max'])-int(params['min'])).all()
                size = self.__displayLogsQuery2(ctx, params, session).order_by(self.commands.c.order_in_bundle).distinct().count()
                session.close()
                return size, self.__displayLogReturn(ctx, ret)
            else:                               # we want all informations about on one group / host
                # Get all commands related to the given computer UUID or group
                # id
                ret = self.__displayLogsQuery(ctx, params, session).order_by(asc(params['order_by'])).all()
                cmds = []
                for c in ret:
                    if self.__doneBundle({'cmd_id':c.id, 'b_id':None}, session) and params['finished'] or not self.__doneBundle({'cmd_id':c.id, 'b_id':None}, session) and not params['finished']:
                        cmds.append((c.id, c.fk_bundle))

                size = []
                size.extend(cmds)
                size = len(self.__displayLogsQueryGetIds(size, params = params))

                ids = self.__displayLogsQueryGetIds(cmds, params['min'], params['max'], params)

                query = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target))
                query = query.add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state)
                query = query.filter(self.commands.c.id.in_(ids))
                if params['uuid']:
                    # Filter target according to the given UUID
                    query = query.filter(self.target.c.target_uuid == params['uuid'])
                query = query.order_by(desc(params['order_by']))
                ret = query.group_by(self.commands.c.id).all()

                session.close()
                return size, self.__displayLogReturn(ctx, ret)
        else:                                   # we want all informations
            if params['cmd_id']:                # we want all informations about one command
                ret = self.__displayLogsQuery2(ctx, params, session).all()
                # FIXME: using distinct, size will always return 1 ...
                size = self.__displayLogsQuery2(ctx, params, session).distinct().count()
                session.close()
                return size, self.__displayLogReturn(ctx, ret)
            elif params['b_id']:                # we want all informations about one bundle
                ret = self.__displayLogsQuery2(ctx, params, session).order_by(self.commands.c.order_in_bundle).all()
                # FIXME: using distinct, size will always return 1 ...
                size = self.__displayLogsQuery2(ctx, params, session).order_by(self.commands.c.order_in_bundle).distinct().count()
                session.close()
                return size, self.__displayLogReturn(ctx, ret)
            else:                               # we want all informations about everything
                ret = self.__displayLogsQuery(ctx, params, session).order_by(asc(params['order_by'])).all()
                cmds = map(lambda c: (c.id, c.fk_bundle), ret)

                size = []
                size.extend(cmds)
                size = len(self.__displayLogsQueryGetIds(size))

                ids = self.__displayLogsQueryGetIds(cmds, params['min'], params['max'], params = params)

                query = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target))
                query = query.add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state)
                query = query.filter(self.commands.c.id.in_(ids))
                query = query.order_by(desc(params['order_by']))
                ret = query.group_by(self.commands.c.id).all()

                session.close()
                return size, self.__displayLogReturn(ctx, ret)

    ###################
    def getCommandsOnHosts(self, ctx, coh_ids):
        session = create_session()
        cohs = session.query(CommandsOnHost).add_column(self.commands_on_host.c.id).filter(self.commands_on_host.c.id.in_(coh_ids)).all()
        session.close()
        targets = self.getTargetsForCoh(ctx, coh_ids)
        if ComputerLocationManager().doesUserHaveAccessToMachines(ctx, map(lambda t:t.target_uuid, targets), False):
            ret = {}
            for e in cohs:
                ret[e[1]] = e[0]
            return ret
        return {}

    def getCommandsOnHost(self, ctx, coh_id):
        session = create_session()
        coh = session.query(CommandsOnHost).get(coh_id)
        if coh == None:
            self.logger.warn("User %s try to access an coh that don't exists '%s'" % (ctx.userid, coh_id))
            return False
        session.close()
        target = self.getTargetForCoh(ctx, coh_id)
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx, target.target_uuid):
            return coh
        self.logger.warn("User %s does not have right permissions to access '%s'" % (ctx.userid, target.target_name))
        return False

    def getTargetsForCoh(self, ctx, coh_ids): # FIXME should we use the ctx
        session = create_session()
        targets = session.query(Target).select_from(self.target.join(self.commands_on_host)).filter(self.commands_on_host.c.id.in_(coh_ids)).all()
        session.close()
        return targets

    def getTargetForCoh(self, ctx, coh_id): # FIXME should we use the ctx
    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        target = session.query(Target).select_from(self.target.join(self.commands_on_host)).filter(self.commands_on_host.c.id == coh_id).first()
        session.close()
        return target

    def getCommandsHistory(self, ctx, coh_id): # FIXME should we use the ctx
    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsHistory).filter(self.commands_history.c.fk_commands_on_host == coh_id).all()
        session.close()
        return map(lambda x: x.toH(), ret)

    def getBundle(self, ctx, fk_bundle):
        session = create_session()
        try:
            ret = session.query(Bundle).filter(self.bundle.c.id == fk_bundle).first().toH()
        except:
            self.logger.info("Bundle '%s' cant be retrieved by '%s'"%(fk_bundle, ctx.userid))
            return [None, []]
        try:
            cmds = map(lambda a:a.toH(), session.query(Commands).filter(self.commands.c.fk_bundle == fk_bundle).order_by(self.commands.c.order_in_bundle).all())
        except:
            self.logger.info("Commands for bundle '%s' cant be retrieved by '%s'"%(fk_bundle, ctx.userid))
            return [ret, []]
        session.close()
        try:
            ret['creation_date'] = cmds[0]['creation_date']
        except:
            ret['creation_date'] = ''
        return [ret, cmds]

    def getCommands(self, ctx, cmd_id):
        if cmd_id == None or cmd_id == '':
            return False
        a_targets = map(lambda target:target[0], self.getTargets(cmd_id, True))
        if ComputerLocationManager().doesUserHaveAccessToMachines(ctx, a_targets):
            session = create_session()
            ret = session.query(Commands).filter(self.commands.c.id == cmd_id).first()
            session.close()
            return ret
        self.logger.warn("User %s does not have good permissions to access command '%s'" % (ctx.userid, str(cmd_id)))
        return False

    def getCommandsByGroup(self, gid):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.id_group == gid)
        ret = ret.order_by(desc(self.commands.c.start_date)).all()
        session.close()
        return ret

    def getTargetsByGroup(self, gid):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(Target).filter(self.target.c.id_group == gid).all()
        session.close()
        return ret

    def getTargets(self, cmd_id, onlyId = False):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        if onlyId:
            connection = self.getDbConnection()
            ret = connection.execute(select([self.target.c.target_uuid], and_(self.commands_on_host.c.fk_commands == cmd_id, self.target.c.id == self.commands_on_host.c.fk_target))).fetchall()
        else:
            session = create_session()
            ret = session.query(Target).select_from(self.target.join(self.commands_on_host)).filter(self.commands_on_host.c.fk_commands == cmd_id).all()
            session.close()
        return ret

    def getCommandOnHostCurrentState(self, ctx, cmd_id):
        session = create_session()
        ret = session.query(Commands).add_column(self.commands_on_host.c.current_state).select_from(self.commands.join(self.commands_on_host)).filter(self.commands.c.id == cmd_id).first()
        session.close()
        return ret[1]

    def getCommandOnHostTitle(self, ctx, cmd_id):
        session = create_session()
        ret = session.query(Commands).select_from(self.commands.join(self.commands_on_host)).filter(self.commands.c.id == cmd_id).first()
        session.close()
        return ret.title

    def getCommandOnHostInCommands(self, ctx, cmd_id):
        session = create_session()
        ret = session.query(CommandsOnHost).filter(self.commands_on_host.c.fk_commands == cmd_id).all()
        session.close()
        return map(lambda c:c.id, ret)

    def getCommandOnGroupByState(self, ctx, cmd_id, state, min = 0, max = -1):
        session = create_session()
        query = session.query(CommandsOnHost).add_column(self.target.c.target_uuid).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.commands.c.id == cmd_id).order_by(self.commands_on_host.c.host)
        ret = self.__filterOnStatus(ctx, query, state)
        session.close()
        if max != -1: ret = ret[min:max]
        return map(lambda coh: {'coh_id':coh.id, 'uuid':coh.target_uuid, 'host':coh.host, 'start_date':coh.start_date, 'end_date':coh.end_date, 'current_state':coh.current_state}, ret)
    
    def getCommandOnGroupStatus(self, ctx, cmd_id):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        query = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.id == cmd_id)
        ret = self.__getStatus(ctx, query)
        session.close()
        return ret

    def getCommandOnBundleByState(self, ctx, fk_bundle, state, min = 0, max = -1):
        session = create_session()
        query = session.query(CommandsOnHost).add_column(self.target.c.target_uuid).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.commands.c.fk_bundle == fk_bundle).order_by(self.commands_on_host.c.host)
        ret = self.__filterOnStatus(ctx, query, state)
        session.close()
        if max != -1: ret = ret[min:max]
        return map(lambda coh: {'coh_id': coh.id, 'uuid':coh.target_uuid, 'host':coh.host, 'start_date':coh.start_date, 'end_date':coh.end_date, 'current_state':coh.current_state}, ret)
        
    def getCommandOnBundleStatus(self, ctx, fk_bundle):
        session = create_session()
        query = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.fk_bundle == fk_bundle)
        ret = self.__getStatus(ctx, query)
        session.close()
        return ret

    def __putUUIDInCOH(self, coh, uuid):
        setattr(coh, 'target_uuid', uuid)
        return coh
    
    def __filterOnStatus(self, ctx, query, state):
        query = map(lambda x: self.__putUUIDInCOH(x[0], x[1]), query)
        ret = self.__getStatus(ctx, query, True)
        if state in ret:
            return ret[state]['total'][1]
        for l1 in ret:
            if state in ret[l1]:
                return ret[l1][state][1]
        return None

    def __getStatus(self, ctx, query, verbose = False):
        ret = {
            'total':0,
            'success':{
                'total':[0, []]
            },
            'stopped':{
                'total':[0, []]
            },
            'paused':{
                'total':[0, []]
            },
            'running':{
                'total':[0, []],
                'wait_up':[0, []],
                'run_up':[0, []],
                'sec_up':[0, []],
                'wait_ex':[0, []],
                'run_ex':[0, []],
                'sec_ex':[0, []],
                'wait_rm':[0, []],
                'run_rm':[0, []],
                'sec_rm':[0, []]
            },
            'failure':{
                'total':[0, []],
                'fail_up':[0, []],
                'conn_up':[0, []],
                'fail_ex':[0, []],
                'conn_ex':[0, []],
                'fail_rm':[0, []],
                'conn_rm':[0, []],
                'over_timed':[0, []]

            }
        }
        running = ['upload_in_progress', 'upload_done', 'execution_in_progress', 'execution_done', 'delete_in_progress', 'delete_done', 'inventory_in_progress', 'inventory_done', 'pause', 'stop', 'stopped'] #, 'scheduled']
        failure = ['failed', 'upload_failed', 'execution_failed', 'delete_failed', 'inventory_failed', 'not_reachable']
        for coh in query:
            ret['total'] += 1
            if coh.current_state == 'done': # success
                ret['success']['total'][0] += 1
                if verbose: ret['success']['total'][1].append(coh)
            elif coh.current_state == 'stop' or coh.current_state == 'stopped': # stopped coh
                ret['stopped']['total'][0] += 1
                if verbose: ret['stopped']['total'][1].append(coh)
            elif coh.current_state == 'pause':
                ret['paused']['total'][0] += 1
                if verbose: ret['paused']['total'][1].append(coh)
            elif coh.current_state == 'over_timed': # out of the valid period of execution (= failed)
                ret['failure']['total'][0] += 1
                if verbose: ret['failure']['total'][1].append(coh)
                ret['failure']['over_timed'][0] += 1
                if verbose: ret['failure']['over_timed'][1].append(coh)
            elif coh.attempts_left == 0 and (coh.uploaded == 'FAILED' or coh.executed == 'FAILED' or coh.deleted == 'FAILED'): # failure
                ret['failure']['total'][0] += 1
                if verbose: ret['failure']['total'][1].append(coh)
                if coh.uploaded == 'FAILED':
                    ret['failure']['fail_up'][0] += 1
                    if verbose: ret['failure']['fail_up'][1].append(coh)
                    if coh.current_state == 'not_reachable':
                        ret['failure']['conn_up'][0] += 1
                        if verbose: ret['failure']['conn_up'][1].append(coh)
                elif coh.executed == 'FAILED':
                    ret['failure']['fail_ex'][0] += 1
                    if verbose: ret['failure']['fail_ex'][1].append(coh)
                    if coh.current_state == 'not_reachable':
                        ret['failure']['conn_ex'][0] += 1
                        if verbose: ret['failure']['conn_ex'][1].append(coh)
                elif coh.deleted == 'FAILED':
                    ret['failure']['fail_rm'][0] += 1
                    if verbose: ret['failure']['fail_rm'][1].append(coh)
                    if coh.current_state == 'not_reachable':
                        ret['failure']['conn_rm'][0] += 1
                        if verbose: ret['failure']['conn_rm'][1].append(coh)
            elif coh.attempts_left != 0 and (coh.uploaded == 'FAILED' or coh.executed == 'FAILED' or coh.deleted == 'FAILED'): # fail but can still try again
                ret['running']['total'][0] += 1
                if verbose: ret['running']['total'][1].append(coh)
                if coh.uploaded == 'FAILED':
                    ret['running']['wait_up'][0] += 1
                    if verbose: ret['running']['wait_up'][1].append(coh)
                    ret['running']['sec_up'][0] += 1
                    if verbose: ret['running']['sec_up'][1].append(coh)
                elif coh.executed == 'FAILED':
                    ret['running']['wait_ex'][0] += 1
                    if verbose: ret['running']['wait_ex'][1].append(coh)
                    ret['running']['sec_ex'][0] += 1
                    if verbose: ret['running']['sec_ex'][1].append(coh)
                elif coh.deleted == 'FAILED':
                    ret['running']['wait_rm'][0] += 1
                    if verbose: ret['running']['wait_rm'][1].append(coh)
                    ret['running']['sec_rm'][0] += 1
                    if verbose: ret['running']['sec_rm'][1].append(coh)
            else: # running
                ret['running']['total'][0] += 1
                if verbose and coh.deleted != 'DONE' and coh.deleted != 'IGNORED': ret['running']['total'][1].append(coh)
                if coh.deleted == 'DONE' or coh.deleted == 'IGNORED': # done
                    ret['running']['total'][0] -= 1
                    ret['success']['total'][0] += 1
                    if verbose: ret['success']['total'][1].append(coh)
                elif coh.executed == 'DONE' or coh.executed == 'IGNORED': # delete running
                    if coh.deleted == 'WORK_IN_PROGRESS':
                        ret['running']['run_rm'][0] += 1
                        if verbose: ret['running']['run_rm'][1].append(coh)
                    else:
                        ret['running']['wait_rm'][0] += 1
                        if verbose: ret['running']['wait_rm'][1].append(coh)
                elif coh.uploaded == 'DONE' or coh.uploaded == 'IGNORED': # exec running
                    if coh.executed == 'WORK_IN_PROGRESS':
                        ret['running']['run_ex'][0] += 1
                        if verbose: ret['running']['run_ex'][1].append(coh)
                    else:
                        ret['running']['wait_ex'][0] += 1
                        if verbose: ret['running']['wait_ex'][1].append(coh)
                else: # upload running
                    if coh.uploaded == 'WORK_IN_PROGRESS':
                        ret['running']['run_up'][0] += 1
                        if verbose: ret['running']['run_up'][1].append(coh)
                    else:
                        ret['running']['wait_up'][0] += 1
                        if verbose: ret['running']['wait_up'][1].append(coh)

        if not verbose:
            for i in ['success', 'stopped', 'running', 'failure', 'paused']:
                if ret['total'] == 0:
                    ret[i]['total'][1] = 0
                else:
                    ret[i]['total'][1] = ret[i]['total'][0] * 100 / ret['total']
            for i in ['wait_up', 'run_up', 'wait_ex', 'run_ex', 'wait_rm', 'run_rm']:
                if ret['total'] == 0:
                    ret['running'][i][1] = 0
                else:
                    ret['running'][i][1] = ret['running'][i][0] * 100 / ret['total']
            for i in ['fail_up', 'conn_up', 'fail_ex', 'conn_ex', 'fail_rm', 'conn_rm', 'over_timed']:
                if ret['total'] == 0:
                    ret['failure'][i][1] = 0
                else:
                    ret['failure'][i][1] = ret['failure'][i][0] * 100 / ret['total']
        return ret

        # nombre total de coh
        # succes (nb, %)
        # stopped (nb, %)
        # paused  (nb, %)
        # en cours (nb, %)
        #   attente up (nb, %)
        #   cours d'up (nb, %)
        #   deja essaye d'up (nb)
        #   attente exec (nb, %)
        #   cours d'ex (nb, %)
        #   deja essaye d'ex (nb)
        #   attente sup (nb, %)
        #   cours sup (nb, %)
        #   deja essaye de sup (nb)
        # non dep (nb, %)
        #   echoué durant up (nb, %) coh.uploaded == 'FAILED'
        #       dont injoignables (nb)
        #   echoué durant ex (nb, %) coh.executed == 'FAILED'
        #       dont injoignables (nb)
        #   echoué durant sup (nb, %) coh.deleted == 'FAILED'
        #       dont injoignables (nb)

        # coh.uploaded, coh.executed, coh.deleted

    def antiPoolOverflowErrorback(self, reason):
        """
            an erroback, with handle QueuePool error-like by :
            - intercepting all exception
            - trap only SA "TimeoutError" Exceptions
            - if exception identified as TimeoutError, recreate pool
            - then raise the error anew
        """
        reason.trap(TimeoutError)
        if self.db.pool._max_overflow > -1 and self.db.pool._overflow >= self.db.pool._max_overflow :
            logging.getLogger().error('Timeout then overflow (%d vs. %d) detected in SQL pool : check your network connectivity !' % (self.db.pool._overflow, self.db.pool._max_overflow))
            self.db.pool.dispose()
            self.db.pool = self.db.pool.recreate()
        return reason
