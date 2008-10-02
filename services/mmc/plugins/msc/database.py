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

# standard modules
import time
import re
import os.path

# SqlAlchemy
from sqlalchemy import *

from twisted.internet import defer

# MMC modules
from mmc.plugins.pulse2.location import ComputerLocationManager
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.msc.config import MscConfig
from mmc.plugins.msc.mirror_api import MirrorApi, Mirror
from mmc.plugins.msc.scheduler_api import SchedulerApi
from mmc.plugins.msc import blacklist
from mmc.support.mmctools import Singleton

# ORM mappings
from mmc.plugins.msc.orm.commands import Commands
from mmc.plugins.msc.orm.commands_on_host import CommandsOnHost
from mmc.plugins.msc.orm.commands_history import CommandsHistory
from mmc.plugins.msc.orm.target import Target
from mmc.plugins.msc.orm.bundle import Bundle

# blacklists
from mmc.plugins.msc import blacklist

# Pulse 2 stuff
import pulse2.time_intervals

# Imported last
import logging

SA_MAYOR = 0
SA_MINOR = 3
DATABASEVERSION = 12

# TODO need to check for useless function (there should be many unused one...)

NB_DB_CONN_TRY = 2
def create_method(obj, m):
    def method(self, already_in_loop = False):
        ret = None
        try:
            old_m = getattr(obj, '_old_'+m)
            ret = old_m(self)
        except exceptions.SQLError, e:
            if e.orig.args[0] == 2013 and not already_in_loop: # Lost connection to MySQL server during query error
                logging.getLogger().warn("SQLError Lost connection (%s) trying to recover the connection" % m)
                for i in range(0, NB_DB_CONN_TRY):
                    new_m = getattr(obj, m)
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
        setattr(Query, m, create_method(Query, m))

class MscDatabase(Singleton):
    """
    Singleton Class to query the msc database.

    """
    # TODO: scheduler algo should move somewhere else
    is_activated = False

    def db_check(self):
        if not self.__checkSqlalchemy():
            self.logger.error("Sqlalchemy version error : is not %s.%s.* version" % (SA_MAYOR, SA_MINOR))
            return False

        conn = self.connected()
        if conn:
            if conn != DATABASEVERSION:
                self.logger.error("Msc database version error: v.%s needeed, v.%s found; please update your schema !" % (DATABASEVERSION, conn))
                return False
        else:
            self.logger.error("Can't connect to database (s=%s, p=%s, b=%s, l=%s, p=******). Please check msc.ini." % (self.config.dbhost, self.config.dbport, self.config.dbbase, self.config.dbuser))
            return False

        return True

    def __checkSqlalchemy(self):
        import sqlalchemy
        a_version = sqlalchemy.__version__.split('.')
        if len(a_version) > 2 and str(a_version[0]) == str(SA_MAYOR) and str(a_version[1]) == str(SA_MINOR):
            return True
        return False

    def activate(self, conffile = None):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("Msc database is connecting")
        self.config = MscConfig("msc", conffile)
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, convert_unicode = True)
        self.metadata = BoundMetaData(self.db)
        self.initTables()
        self.initMappers()
        self.metadata.create_all()
        # FIXME: should be removed
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("Msc database connected")

    def makeConnectionPath(self):
        """
        Build and return the db connection path according to the plugin configuration

        @rtype: str
        """
        if self.config.db_port:
            port = ":" + str(self.config.db_port)
        else:
            port = ""
        url = "%s://%s:%s@%s%s/%s" % (self.config.db_driver, self.config.db_user, self.config.db_passwd, self.config.db_host, port, self.config.db_name)
        if self.config.db_ssl_enable:
            url = url + "?ssl_ca=%s&ssl_key=%s&ssl_cert=%s" % (self.config.db_ssl_ca, self.config.db_ssl_key, self.config.db_ssl_cert)
        return url

    def connected(self):
        if (self.db != None):
            return self.version.select().execute().fetchone()[0]
        return False

    def getDbConnection(self):
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

    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """
        # commands
        self.commands = Table("commands", self.metadata,
                            Column('dispatched', String(32), default='YES'),
                            Column('bundle_id', Integer, ForeignKey('bundle.id')),
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

    def myfunctions(self):
        pass

    def enableLogging(self, level = None):
        """
        Enable log for sqlalchemy.engine module using the level configured by the db_debug option of the plugin configuration file.
        The SQL queries will be loggued.
        """
        if not level:
            level = self.config.db_debug
        logging.getLogger("sqlalchemy.engine").setLevel(level)

    def disableLogging(self):
        """
        Disable log for sqlalchemy.engine module
        """
        logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

    ####################################

    def getIdCommandOnHost(self, ctx, id):
        session = create_session()
        query = session.query(CommandsOnHost).filter(self.commands.c.id == id).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.creator == ctx.userid).all()
        if len(query) == 1:
            ret = query.id
        elif len(query) > 1:
            ret = []
            for q in query:
                ret.append(q.id)
        else:
            ret = -1
        session.close()
        return ret

    def doCommandOnHostExist(self, id):
        session = create_session()
        query = session.query(CommandsOnHost).filter(self.commands_on_host.c.id == id).all()
        # FIXME: use query.count() instead of len(query.all())
        ret = len(query) > 0
        session.close()
        return ret

    # FIXME: The four next methods can be factorized
    # FIXME: The current_state test should be put in the SQL expression

    def isCommandOnHostDone(self, id):
        session = create_session()
        query = session.query(CommandsOnHost).filter(self.commands_on_host.c.id == id).first()
        if query:
            ret = query.current_state == 'done'
        else:
            ret = None
        session.close()
        return ret

    def isCommandOnHostPaused(self, id):
        session = create_session()
        query = self.session.query(CommandsOnHost).filter(self.commands_on_host.c.id == id).first()
        if query:
            ret = q.current_state == 'pause'
        else:
            ret= None
        session.close()
        return ret

    def isCommandOnHostStopped(self, id):
        session = create_session()
        query = self.session.query(CommandsOnHost).filter(self.commands_on_host.c.id == id).first()
        if query:
            ret = q.current_state == 'stop'
        else:
            ret = None
        session.close()
        return ret

    def createBundle(self, title = '', session = create_session()):
        """
        Return a new Bundle
        """
        bdl = Bundle()
        bdl.title = title
        session.save(bdl)
        session.flush()
        return bdl

    def createCommand(self, session, start_file, parameters, files, start_script, clean_on_success, start_date, end_date, connect_as, creator, title, do_reboot, do_wol, next_connection_delay, max_connection_attempt, do_inventory, maxbw, deployment_intervals, bundle_id, order_in_bundle):
        """
        Return a Command object
        """
        if type(files) == list:
            files = "\n".join(files)

        cmd = Commands()
        now = time.localtime()
        cmd.creation_date = "%s-%s-%s %s:%s:%s" % (now[0], now[1], now[2], now[3], now[4], now[5])
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
        cmd.do_reboot = do_reboot
        cmd.do_wol = do_wol
        cmd.next_connection_delay = next_connection_delay
        cmd.max_connection_attempt = max_connection_attempt
        cmd.do_inventory = do_inventory
        cmd.maxbw = maxbw
        cmd.deployment_intervals = pulse2.time_intervals.normalizeinterval(deployment_intervals)
        cmd.bundle_id = bundle_id
        cmd.order_in_bundle = order_in_bundle
        session.save(cmd)
        session.flush()
        return cmd

    def createCommandsOnHost(self, command, target, target_id, target_name, cmd_max_connection_attempt, cmd_start_date = "0000-00-00 00:00:00", cmd_end_date = "0000-00-00 00:00:00", scheduler = None):
        logging.getLogger().debug("Create new command on host '%s'" % target["target_name"])
        return {
            "host" : target_name,
            "start_date" : cmd_start_date,
            "end_date" : cmd_end_date,
            "next_launch_date" : cmd_start_date,
            "current_state" : "scheduled",
            "uploaded" : "TODO",
            "executed" : "TODO",
            "deleted" : "TODO",
            "attempts_left" : cmd_max_connection_attempt,
            "next_attempt_date_time" : 0,
            "scheduler" : scheduler,
            "fk_target" : target_id,
            "fk_commands" : command
            }

    def getMachinesSchedulers(self, target):
        if type(target[0]) == list: # target = [[uuid, hostname], [uuid, target]]
            return SchedulerApi().getSchedulers(map(lambda t: t[0], target))
        else: # target = [uuid, hostname]
            return SchedulerApi().getScheduler(target[0])

    def addCommand(self,
                ctx,
                start_file,
                parameters,
                files,
                targets,
                mode = 'push',
                group_id = '',
                start_script = True,
                clean_on_success = 'enable',
                start_date = "0000-00-00 00:00:00",
                end_date = "0000-00-00 00:00:00",
                connect_as = "root",
                title = "",
                do_reboot = 'disable',
                do_wol = 'enable',
                next_connection_delay = 60,
                max_connection_attempt = 3,
                do_inventory = 'disable',
                maxbw = 0,
                root = MscConfig("msc").repopath,
                deployment_intervals = "",
                bundle_id = None,
                order_in_bundle = None
            ):
        """
        Main func to inject a new command in our MSC database

        Return a Deferred object resulting to the command id
        """

        def getBCast(ip, netmask):
            a_ip = ip.split('.')
            a_netmask = netmask.split('.')
            a_network = [0,0,0,0]
            for i in range(0,4):
                a_network[i] = int(a_ip[i]) & int(a_netmask[i])
            a_notnetmask = map(lambda i: int(i) ^ 255, netmask.split('.'))
            for i in range(0,4):
                a_ip[i] = int(a_network[i]) | int(a_notnetmask[i])
            return '.'.join(map(lambda x: str(x), a_ip))

        def prepareTarget(computer):
            h_mac2bcast = {}
            h_mac2netmask = {}
            bcastAddresses = []
            netmasks = []
            ipAddresses = computer[1]['ipHostNumber']
            netmask = computer[1]['subnetMask']

            for i in range(len(computer[1]['macAddress'])):
                try:
                    bcastAddress = getBCast(ipAddresses[i], netmask[i])
                except Exception, e:
                    self.logger.debug("Can't compute broadcast address for %s: %s" % (str(computer), str(e)))
                    bcastAddress = "255.255.255.255"
                    self.logger.debug("Using default broadcast address %s" % bcastAddress)
                h_mac2bcast[computer[1]['macAddress'][i]] = bcastAddress
                try:
                    h_mac2netmask[computer[1]['macAddress'][i]] = netmask[i]
                except:
                    h_mac2netmask[computer[1]['macAddress'][i]] = '0.0.0.0'

            self.logger.debug("Computer known IP addresses before filter: " + str(ipAddresses))
            # Apply IP addresses blacklist
            if self.config.ignore_non_rfc2780:
                ipAddresses = blacklist.rfc2780Filter(ipAddresses)
            if self.config.ignore_non_rfc1918:
                ipAddresses = blacklist.rfc1918Filter(ipAddresses)
            ipAddresses = blacklist.excludeFilter(ipAddresses, self.config.exclude_ipaddr)
            ipAddresses = blacklist.mergeWithIncludeFilter(computer[1]['ipHostNumber'], ipAddresses, self.config.include_ipaddr)
            self.logger.debug("Computer known IP addresses after filter: " + str(ipAddresses))

            try:
                targetName = computer[1]['cn'][0]
            except KeyError:
                pass
            try:
                targetName = computer[1]['fullname']
            except KeyError:
                pass

            self.logger.debug("Computer known MAC addresses before filter: " + str(computer[1]['macAddress']))
            macAddresses = blacklist.macAddressesFilter(computer[1]['macAddress'], self.config.wol_macaddr_blacklist)
            self.logger.debug("Computer known MAC addresses after filter: " + str(macAddresses))

            for mac in macAddresses:
                bcastAddresses.append(h_mac2bcast[mac])
                netmasks.append(h_mac2netmask[mac])

            # Multiple IP addresses or IP addresses may be separated by "||"
            targetMac = '||'.join(macAddresses)
            targetIp = '||'.join(ipAddresses)
            targetBCast = '||'.join(bcastAddresses)
            targetNetmask = '||'.join(netmasks)

            targetUuid = computer[1]['objectUUID'][0]
            return self.addTarget(
                targetName,
                targetUuid,
                targetIp,
                targetMac,
                targetBCast,
                targetNetmask,
                None,
                group_id,
                )

        connection = self.getDbConnection()
        trans = connection.begin()
        targets_to_insert = []
        targets_scheduler = []
        targets_name = []
        coh_to_insert = []

        # Get all targets network information
        computers = ComputerManager().getComputersNetwork(ctx, {"uuids" : targets})
        # Rebuild the targets list, and get computers data
        tmp = []
        targetsdata = []
        for computer in computers:
            if 'fullname' in computer[1]:
                hostname = computer[1]['fullname']
            else:
                hostname = computer[1]['cn'][0]
            tmp.append([computer[1]['objectUUID'][0], hostname])
            targetsdata.append(prepareTarget(computer))
        targets = tmp[:]

        def cbGetTargetsMirrors(schedulers):
            args = map(lambda x: {"uuid" : x[0], "name": x[1]}, targets)
            d1 = MirrorApi().getMirrors(args)
            d1.addCallback(cbGetTargetsFallbackMirrors, schedulers)
            d1.addErrback(lambda err: err)
            return d1

        def cbGetTargetsFallbackMirrors(mirrors, schedulers):
            args = map(lambda x: {"uuid" : x[0], "name": x[1]}, targets)
            d2 = MirrorApi().getFallbackMirrors(args)
            d2.addCallback(cbCreateTargets, mirrors, schedulers)
            d2.addErrback(lambda err: err)
            return d2

        def cbPushModeCreateTargets(schedulers):
            return cbCreateTargets(None, None, schedulers, push_pull = False)
        
        def cbCreateTargets(fbmirrors, mirrors, schedulers, push_pull = True):
            for i in range(len(targets)):
                if push_pull:
                    # FIXME: we only take the the first mirrors
                    mirror = mirrors[i]
                    fallback = fbmirrors[i]
                    uri = '%s://%s:%s%s' % (mirror['protocol'], mirror['server'], str(mirror['port']), mirror['mountpoint']) + \
                          '||' + \
                          '%s://%s:%s%s' % (fallback['protocol'], fallback['server'], str(fallback['port']), fallback['mountpoint'])
                else:
                    uri = '%s://%s' % ('file', root)
                targetsdata[i]['mirrors'] = uri
                # Maybe could be done in prepareTarget
                targetsdata[i] = self.blacklistTargetHostname(targetsdata[i])
                targets_to_insert.append(targetsdata[i])
                targets_name.append(targets[i][1])

            session = create_session()
            cmd = self.createCommand(session, start_file, parameters, files, start_script, clean_on_success, start_date, end_date, connect_as, ctx.userid, title, do_reboot, do_wol, next_connection_delay, max_connection_attempt, do_inventory, maxbw, deployment_intervals, bundle_id, order_in_bundle)
            session.close()

            r = connection.execute(self.target.insert(), targets_to_insert)
            first_target_id = r.last_inserted_ids()[0]
            for atarget, target_name, ascheduler in zip(targets_to_insert, targets_name, schedulers):
                coh_to_insert.append(self.createCommandsOnHost(cmd.getId(), atarget, first_target_id, target_name, max_connection_attempt, start_date, end_date, ascheduler))
                first_target_id = first_target_id + 1
            connection.execute(self.commands_on_host.insert(), coh_to_insert)
            trans.commit()
            return cmd.getId()

        d = self.getMachinesSchedulers(targets)
        if mode == 'push_pull':
            d.addCallback(cbGetTargetsMirrors)
        else:
            d.addCallback(cbPushModeCreateTargets)
        d.addErrback(lambda err: err)
        return d

    def blacklistTargetHostname(self, target):
        # Apply host name blacklist
        target_name = target["target_name"]
        if not blacklist.checkWithRegexps(target_name, self.config.include_hostname):
            # The host name is not in the whitelist
            if (self.config.ignore_non_fqdn and not blacklist.isFqdn(target_name)) or (self.config.ignore_invalid_hostname and not blacklist.isValidHostname(target_name)) or blacklist.checkWithRegexps(target_name, self.config.exclude_hostname):
                # The host name is not FQDN or invalid, so we don't put it the
                # database. This way the host name won't be use to resolve the
                # computer host name.
                self.logger.debug("Host name has been filtered because '%s' is not FQDN, invalid or matched an exclude regexp" % target_name)
                target["target_name"] = ""
        return target

    def addCommandQuick(self, ctx, cmd, targets, desc, gid = None):
        """
        Schedule a command for immediate execution into database.
        Multiple machines can be specified in the targets parameter.

        Return a Deferred object resulting to the command id.

        @param cmd: command to start (e.g. '/sbin/shutdown -r now')
        @type cmd: str

        @param targets: couple with [UUID, machine name], or list of couples
        @type targets: list

        @param desc: Command description (e.g. 'reboot')
        @type desc: str

        @param gid: Machine group id if the command is started for a group of
                    machines
        @type gid: str
        """
        self.logger.debug("add_command_quick: " + cmd + " on :")
        self.logger.debug(targets)
        files = []

        # run a built-in script
        p1 = re.compile('^\/scripts\/')
        if p1.match(cmd):
            fullpath = basedir + '/msc.script/' + cmd
            files.append(cmd)

        return self.addCommand(
            ctx,
            cmd,
            "",
            files,
            targets,
            'push',
            gid,
            'enable',
            True,
            "0000-00-00 00:00:00",
            "0000-00-00 00:00:00",
            "root",     # FIXME: this should be the effective user we want to connect with
            desc,
            "disable",
            "disable",
            60,
            3,
            "disable",
            0,
            0,
            ''
        )

    def addTarget(self, targetName, targetUuid, targetIp, targetMac, targetBCast, targetNetmask, mirror, groupID = None):
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

    def getAllCommandsonhostCurrentstate(self, ctx): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.creator == ctx.userid).filter(self.commands_on_host.c.current_state <> '').group_by(self.commands_on_host.c.current_state).order_by(asc(self.commands_on_host.c.next_launch_date))
        l = map(lambda x: x.current_state, ret.all())
        session.close()
        return l

    def countAllCommandsonhostByCurrentstate(self, ctx, current_state, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands))
        ret = ret.filter(self.commands_on_host.c.current_state == current_state).filter(self.commands.c.creator == ctx.userid)
        # the join in itself is useless here, but we want to have exactly
        # the same result as in getAllCommandsonhostByCurrentstate
        if filt != '':
            ret = ret.filter(or_(self.commands_on_host.c.host.like('%'+filt+'%'), self.commands.c.title.like('%'+filt+'%')))
        c = ret.count()
        session.close()
        return c

    def getAllCommandsonhostByCurrentstate(self, ctx, current_state, min = 0, max = 10, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands))
        ret = ret.filter(self.commands_on_host.c.current_state == current_state)
        ret = ret.filter(self.commands.c.creator == ctx.userid)
        if filt != '':
            ret = ret.filter(or_(self.commands_on_host.c.host.like('%'+filt+'%'), self.commands.c.title.like('%'+filt+'%')))
        ret = ret.offset(int(min))
        ret = ret.limit(int(max)-int(min))
        ret = ret.order_by(asc(self.commands_on_host.c.next_launch_date))
        l = map(lambda x: x.toH(), ret.all())
        session.close()
        return l

    def countAllCommandsonhostByType(self, ctx, type, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.creator == ctx.userid)
        if filt != '':
            ret = ret.filter(or_(self.commands_on_host.c.host.like('%'+filt+'%'), self.commands.c.title.like('%'+filt+'%')))
        if int(type) == 0: # all
            pass
        elif int(type) == 1: # pending
            ret = ret.filter(self.commands_on_host.c.current_state.in_('upload_failed', 'execution_failed', 'delete_failed', 'inventory_failed', 'not_reachable', 'pause', 'stop', 'scheduled', 'failed'))
        elif int(type) == 2: # running
            ret = ret.filter(self.commands_on_host.c.current_state.in_('upload_in_progress', 'upload_done', 'execution_in_progress', 'execution_done', 'delete_in_progress', 'delete_done', 'inventory_in_progress', 'inventory_done'))
        elif int(type) == 3: # finished
            ret = ret.filter(self.commands_on_host.c.current_state == 'done')
        c = ret.count()
        session.close()
        return c

    def getAllCommandsonhostByType(self, ctx, type, min, max, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.creator == ctx.userid)
        if filt != '':
            ret = ret.filter(or_(self.commands_on_host.c.host.like('%'+filt+'%'), self.commands.c.title.like('%'+filt+'%')))
        if int(type) == 0: # all
            pass
        elif int(type) == 1: # pending
            ret = ret.filter(self.commands_on_host.c.current_state.in_('upload_failed', 'execution_failed', 'delete_failed', 'inventory_failed', 'not_reachable', 'pause', 'stop', 'scheduled', 'failed'))
        elif int(type) == 2: # running
            ret = ret.filter(self.commands_on_host.c.current_state.in_('upload_in_progress', 'upload_done', 'execution_in_progress', 'execution_done', 'delete_in_progress', 'delete_done', 'inventory_in_progress', 'inventory_done'))
        elif int(type) == 3: # finished
            ret = ret.filter(self.commands_on_host.c.current_state == 'done')
        ret = ret.offset(int(min))
        ret = ret.limit(int(max)-int(min))
        ret = ret.order_by(asc(self.commands_on_host.c.next_launch_date))
        l = map(lambda x: x.toH(), ret.all())
        session.close()
        return l

    def countAllCommandsOnHostBundle(self, ctx, uuid, bundle_id, filt, history): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.target.c.target_uuid == uuid).filter(self.commands.c.creator == ctx.userid).filter(self.commands.c.bundle_id == bundle_id)
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
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
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
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
            session = create_session()
            query = session.query(Commands).add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state)
            query = query.select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.target_uuid == uuid)
            #.filter(self.commands.c.creator == ctx.userid)
            if filt != '':
                query = query.filter(self.commands.c.title.like('%'+filt+'%'))
            query = query.offset(int(min))
            query = query.limit(int(max)-int(min))
            query = query.order_by(asc(self.commands_on_host.c.next_launch_date))
            ret = query.all()
            session.close()
            return map(lambda x: (x[0].toH(), x[1], x[2]), ret)
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return []

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
            query = query.filter(self.commands_on_host.c.current_state.in_('done', 'failed'))
        else:
            # If we are querying on a bundle, we also want to display the
            # commands_on_host flagged as done
            if params['b_id'] == None:
                query = query.filter(not_(self.commands_on_host.c.current_state.in_('done', 'failed')))
        return query.group_by(self.commands.c.id).order_by(desc(params['order_by']))

    def __displayLogsQuery2(self, ctx, params, session):
        filter = []
        select_from = None
        group_by = None

        # Get query parts
        query = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target))
        query = query.add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state)
        if params['cmd_id'] != None: # COH
            filter = [self.commands.c.id == params['cmd_id']]
            if params['b_id'] != None:
                filter.append(self.commands.c.bundle_id == params['b_id'])
        else: # CMD
            if params['b_id'] != None:
                filter = [self.commands.c.bundle_id == params['b_id']]
            group_by = self.commands.c.id

        if params['gid'] != None: # Filter on a machines group id
            filter.append(self.target.c.id_group == params['gid'])

        if params['uuid'] != None: # Filter on a machine uuid
            filter.append(self.target.c.target_uuid == params['uuid'])

        if params['filt'] != None: # Filter on a commande names
            filter.append(self.commands.c.title.like('%s%s%s' % ('%', params['filt'], '%')))

        if params['finished']: # Filter on finished commands only
            filter.append(self.commands_on_host.c.current_state.in_('done', 'failed'))
        else:
            # If we are querying on a bundle, we also want to display the
            # commands_on_host flagged as done
            if params['b_id'] == None:
                filter.append(not_(self.commands_on_host.c.current_state.in_('done', 'failed')))

        query = query.filter(and_(*filter))

        if group_by != None:
            query = query.group_by(group_by)

        return query

    def __displayLogsQueryGetIds(self, cmds, min = 0, max = -1):
        i = 0
        min = int(min)
        max = int(max)
        ids = []
        defined = {}
        for cmd in cmds:
            id, bundle_id = cmd
            if max != -1 and max-1 < i:
                break
            if i < min:
                if (bundle_id != 'NULL' or bundle_id != None) and not defined.has_key(bundle_id):
                    defined[bundle_id] = id
                    i += 1
                elif bundle_id == 'NULL' or bundle_id == None:
                    i += 1
                continue
            if (bundle_id != 'NULL' or bundle_id != None) and not defined.has_key(bundle_id):
                defined[bundle_id] = id
                ids.append(id)
                i += 1
            elif bundle_id == 'NULL' or bundle_id == None:
                ids.append(id)
                i += 1
        return ids

    def displayLogs(self, ctx, params = {}): # TODO USE ctx
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
        if params['b_id'] == None and params['cmd_id'] == None:
            ret = self.__displayLogsQuery(ctx, params, session).order_by(asc(params['order_by'])).all()
            cmds = map(lambda c: (c.id, c.bundle_id), ret)
            size = []
            size.extend(cmds)

            ids = self.__displayLogsQueryGetIds(cmds, params['min'], params['max'])
            size = len(self.__displayLogsQueryGetIds(size))

            query = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target))
            query = query.add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state)
            query = query.filter(self.commands.c.id.in_(*ids)).order_by(desc(params['order_by']))
            ret = query.group_by(self.commands.c.id).all()
            session.close()
            return size, map(lambda x: (x[0].toH(), x[1], x[2]), ret)
        else:
            ret = self.__displayLogsQuery2(ctx, params, session).all()
            size = self.__displayLogsQuery2(ctx, params, session).distinct().count()
            session.close()
            return size, map(lambda x: (x[0].toH(), x[1], x[2]), ret)

        return 0, []
    ###################

    def getCommandsOnHost(self, ctx, coh_id): # FIXME should we use the ctx
        session = create_session()
        coh = session.query(CommandsOnHost).get(coh_id)
        session.close()
        target = self.getTargetForCoh(ctx, coh_id)
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, target.target_uuid):
            return coh
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, target.target_name))
        return False

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

    def getBundle(self, ctx, bundle_id):
        session = create_session()
        ret = session.query(Bundle).filter(self.bundle.c.id == bundle_id).first().toH()
        cmds = map(lambda a:a.toH(), session.query(Commands).filter(self.commands.c.bundle_id == bundle_id).all())
        session.close()
        try:
            ret['creation_date'] = cmds[0]['creation_date']
        except:
            ret['creation_date'] = ''
        return [ret, cmds]

    def getCommands(self, ctx, cmd_id):
        a_targets = map(lambda target: target.target_uuid, self.getTargets(cmd_id))
        if ComputerLocationManager().doesUserHaveAccessToMachines(ctx.userid, a_targets):
            session = create_session()
            ret = session.query(Commands).filter(self.commands.c.id == cmd_id).first()
            session.close()
            return ret
        self.logger.warn("User %s does not have good permissions to access command '%s'" % (ctx.userid, str(cmd_id)))
        return False

    def getCommandsByGroup(self, gid):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.id_group == gid).all()
        session.close()
        return ret

    def getTargetsByGroup(self, gid):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(Target).filter(self.target.c.id_group == gid).all()
        session.close()
        return ret

    def getTargets(self, cmd_id):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(Target).select_from(self.target.join(self.commands_on_host)).filter(self.commands_on_host.c.fk_commands == cmd_id).all()
        session.close()
        return ret

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

    def getCommandOnGroupStatus(self, ctx, cmd_id):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        query = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.id == cmd_id)
        ret = self.__getStatus(ctx, query)
        session.close()
        return ret

    def getCommandOnBundleStatus(self, ctx, bundle_id):
        session = create_session()
        query = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.bundle_id == bundle_id)
        ret = self.__getStatus(ctx, query)
        session.close()
        return ret

    def __getStatus(self, ctx, query):
        ret = {
            'total':0,
            'success':{
                'total':[0]
            },
            'running':{
                'total':[0],
                'wait_up':[0],
                'run_up':[0],
                'wait_ex':[0],
                'run_ex':[0],
                'wait_rm':[0],
                'run_rm':[0]
            },
            'failure':{
                'total':[0],
                'fail_up':[0],
                'conn_up':[0],
                'fail_ex':[0],
                'conn_ex':[0],
                'fail_rm':[0],
                'conn_rm':[0]

            }
        }
        running = ['upload_in_progress', 'upload_done', 'execution_in_progress', 'execution_done', 'delete_in_progress', 'delete_done', 'inventory_in_progress', 'inventory_done', 'pause', 'stop'] #, 'scheduled']
        failure = ['failed', 'upload_failed', 'execution_failed', 'delete_failed', 'inventory_failed', 'not_reachable']
        for coh in query:
            ret['total'] += 1
            if coh.current_state == 'done': # success
                ret['success']['total'][0] += 1
            elif coh.uploaded == 'FAILED' or coh.executed == 'FAILED' or coh.deleted == 'FAILED': # failure
                ret['failure']['total'][0] += 1
                if coh.uploaded == 'FAILED':
                    ret['failure']['fail_up'][0] += 1
                    if coh.current_state == 'not_reachable':
                        ret['failure']['conn_up'][0] += 1
                elif coh.executed == 'FAILED':
                    ret['failure']['fail_ex'][0] += 1
                    if coh.current_state == 'not_reachable':
                        ret['failure']['conn_ex'][0] += 1
                elif coh.deleted == 'FAILED':
                    ret['failure']['fail_rm'][0] += 1
                    if coh.current_state == 'not_reachable':
                        ret['failure']['conn_rm'][0] += 1
            else: # running
                ret['running']['total'][0] += 1
                if coh.deleted == 'DONE' or coh.deleted == 'IGNORED': # done
                    ret['running']['total'][0] -= 1
                    ret['success']['total'][0] += 1
                elif coh.executed == 'DONE' or coh.executed == 'IGNORED': # delete running
                    if coh.deleted == 'WORK_IN_PROGRESS':
                        ret['running']['run_rm'][0] += 1
                    else:
                        ret['running']['wait_rm'][0] += 1
                elif coh.uploaded == 'DONE' or coh.uploaded == 'IGNORED': # exec running
                    if coh.executed == 'WORK_IN_PROGRESS':
                        ret['running']['run_ex'][0] += 1
                    else:
                        ret['running']['wait_ex'][0] += 1
                else: # upload running
                    if coh.uploaded == 'WORK_IN_PROGRESS':
                        ret['running']['run_up'][0] += 1
                    else:
                        ret['running']['wait_up'][0] += 1

        for i in ['success', 'running', 'failure']:
            if ret['total'] == 0:
                ret[i]['total'].append(0)
            else:
                ret[i]['total'].append(ret[i]['total'][0] * 100 / ret['total'])
        for i in ['wait_up', 'run_up', 'wait_ex', 'run_ex', 'wait_rm', 'run_rm']:
            if ret['total'] == 0:
                ret['running'][i].append(0)
            else:
                ret['running'][i].append(ret['running'][i][0] * 100 / ret['total'])
        for i in ['fail_up', 'conn_up', 'fail_ex', 'conn_ex', 'fail_rm', 'conn_rm']:
            if ret['total'] == 0:
                ret['failure'][i].append(0)
            else:
                ret['failure'][i].append(ret['failure'][i][0] * 100 / ret['total'])
        return ret

        # nombre total de coh
        # succes (nb, %)
        # en cours (nb, %)
        #   attente up (nb, %)
        #   cours d'up (nb, %)
        #   attente exec (nb, %)
        #   cours d'ex (nb, %)
        #   attente sup (nb, %)
        #   cours sup (nb, %)
        # non dep (nb, %)
        #   echoué durant up (nb, %) coh.uploaded == 'FAILED'
        #       dont injoignables (nb)
        #   echoué durant ex (nb, %) coh.executed == 'FAILED'
        #       dont injoignables (nb)
        #   echoué durant sup (nb, %) coh.deleted == 'FAILED'
        #       dont injoignables (nb)

        # coh.uploaded, coh.executed, coh.deleted

