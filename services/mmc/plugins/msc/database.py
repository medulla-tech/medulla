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

# MMC modules
from mmc.plugins.pulse2.location import ComputerLocationManager
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.msc.config import MscConfig
from mmc.plugins.msc.mirror_api import MirrorApi, Mirror
from mmc.plugins.msc import blacklist
from mmc.support.mmctools import Singleton

# ORM mappings
from mmc.plugins.msc.orm.commands import Commands
from mmc.plugins.msc.orm.commands_on_host import CommandsOnHost
from mmc.plugins.msc.orm.commands_history import CommandsHistory
from mmc.plugins.msc.orm.target import Target

# blacklists
from mmc.plugins.msc import blacklist

# Imported last
import logging

SA_MAYOR = 0
SA_MINOR = 3
DATABASEVERSION = 7

# TODO need to check for useless function (there should be many unused one...)

def create_method(obj, m):
    def method(self, already_in_loop = False):
        ret = None
        try:
            old_m = getattr(obj, '_old_'+m)
            ret = old_m(self)
        except SQLError, e:
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
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, convert_unicode = True )
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

    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """
        # commands
        self.commands = Table("commands", self.metadata,
                            Column('dispatched', String(32), default='YES'),
                            autoload = True)
        # commands_history
        self.commands_history = Table(
            "commands_history",
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
        # target
        self.target = Table(
            "target",
            self.metadata,
        #    Column('fk_commands_on_host', Integer, ForeignKey('commands_on_host.id')),
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
        mapper(Commands, self.commands)
        mapper(CommandsHistory, self.commands_history)
        mapper(CommandsOnHost, self.commands_on_host)
        mapper(Target, self.target)
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
        query = session.query(CommandsOnHost).filter(self.commands.c.id == id).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.username == ctx.userid).all()
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

    def createCommand(self, start_file, parameters, files, start_script, delete_file_after_execute_successful, start_date, end_date, username, webmin_username, title, wake_on_lan, next_connection_delay, max_connection_attempt, start_inventory, repeat, maxbw):
        session = create_session()
        cmd = Commands()
        now = time.localtime()
        cmd.date_created = "%s-%s-%s %s:%s:%s" % (now[0], now[1], now[2], now[3], now[4], now[5])
        cmd.start_file = start_file
        cmd.parameters = parameters
        cmd.files = files
        cmd.start_script = start_script
        cmd.delete_file_after_execute_successful = delete_file_after_execute_successful
        cmd.start_date = start_date
        cmd.end_date = end_date
        cmd.username = username
        cmd.webmin_username = webmin_username
        cmd.title = title
        cmd.wake_on_lan = wake_on_lan
        cmd.next_connection_delay = next_connection_delay
        cmd.max_connection_attempt = max_connection_attempt
        cmd.start_inventory = start_inventory
        cmd.repeat = repeat
        cmd.maxbw = maxbw
        session.save(cmd)
        session.flush()
        session.close()
        return cmd.id

    def createCommandsOnHost(self, cmd_id, target_id, target_name, cmd_max_connection_attempt, cmd_start_date = "0000-00-00 00:00:00", cmd_end_date = "0000-00-00 00:00:00"):
        session = create_session()
        logging.getLogger().debug("Create new command on host '%s'" % (target_name))
        myCommandOnHost = CommandsOnHost()
        myCommandOnHost.fk_commands = cmd_id
        myCommandOnHost.fk_target = target_id
        myCommandOnHost.host = target_name
        myCommandOnHost.start_date = cmd_start_date
        myCommandOnHost.end_date = cmd_end_date
        myCommandOnHost.next_launch_date = cmd_start_date
        myCommandOnHost.current_state = 'scheduled'
        myCommandOnHost.uploaded = 'TODO'
        myCommandOnHost.executed = 'TODO'
        myCommandOnHost.deleted = 'TODO'
        myCommandOnHost.number_attempt_connection_remains = cmd_max_connection_attempt
        myCommandOnHost.next_attempt_date_time = 0
        session.save(myCommandOnHost)
        session.flush()
        session.refresh(myCommandOnHost)
        logging.getLogger().debug("New command on host are created, its id is : %s" % myCommandOnHost.getId())
        return myCommandOnHost.getId()

    def createTarget(self, target, mode, group_id):
        """
        Create a row in the target table.

        @param target: couple made of (uuid, hostname)
        @type target: list

        @param mode: target deployment mode
        @type mode: str

        @param group_id: id of the machine group that requires this target row
        @type group_id: str
        """
        targetUuid = target[0]
        targetName = target[1]
        computer = ComputerManager().getComputer(None, {'uuid': targetUuid})

        ipAddresses = computer[1]['ipHostNumber']
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
            targetName = computer[1]['fullname']
        except KeyError:
            pass

        self.logger.debug("Computer known MAC addresses before filter: " + str(computer[1]['macAddress']))
        macAddresses = blacklist.macAddressesFilter(computer[1]['macAddress'], self.config.wol_macaddr_blacklist)
        self.logger.debug("Computer known MAC addresses after filter: " + str(macAddresses))

        # Multiple IP addresses or IP addresses may be separated by "||"
        targetMac = '||'.join(macAddresses)
        targetIp = '||'.join(ipAddresses)

        # compute URI depending on selected mode
        if mode == 'push_pull':
            mirror = MirrorApi().getMirror({"name": targetName, "uuid": targetUuid})
            fallback = MirrorApi().getFallbackMirror({"name": targetName, "uuid": targetUuid})
            targetUri = '%s://%s:%s%s' % (mirror['protocol'], mirror['server'], str(mirror['port']), mirror['mountpoint']) + \
                '||' + \
                '%s://%s:%s%s' % (fallback['protocol'], fallback['server'], str(fallback['port']), fallback['mountpoint'])
                # FIXME: not sure we should cast to srt ...
        elif mode == 'push':
            targetUri = '%s://%s' % ('file', MscConfig("msc").repopath)
        else:
            targetUri = None

        # TODO: add path
        return MscDatabase().addTarget(
            targetName,
            targetUuid,
            targetIp,
            targetMac,
            targetUri,
            group_id
        ) # TODO change mirrors...

    def addCommand(self,
                start_file,
                parameters,
                files,
                target,
                mode = 'push',
                group_id = '',
                start_script = True,
                delete_file_after_execute_successful = True,
                start_date = "0000-00-00 00:00:00",
                end_date = "0000-00-00 00:00:00",
                username = "root",
                webmin_username = "root",
                title = "",
                wake_on_lan = False,
                next_connection_delay = 60,
                max_connection_attempt = 3,
                start_inventory = False,
                repeat = 0,
                maxbw = 0
            ):
        """ Main func to inject a new command in our MSC database """

        if type(files) == list:
            files = "\n".join(files)

        # create (and save) the command itself
        cmd_id = self.createCommand(start_file, parameters, files, start_script, delete_file_after_execute_successful, start_date, end_date, username, webmin_username, title, wake_on_lan, next_connection_delay, max_connection_attempt, start_inventory, repeat, maxbw)

        # create the corresponding target and commands_on_host
        session = create_session()
        if type(target[0]) == list:
            for t in target:
                target_id = self.createTarget(t, mode, group_id)
                t = session.query(Target).get(target_id)
                self.createCommandsOnHost(cmd_id, t.getId(), t.getShortName(), max_connection_attempt, start_date, end_date)
                self.blacklistTargetHostname(t, session)
        else:
            target_id = self.createTarget(target, mode, group_id)
            target = session.query(Target).get(target_id)
            self.createCommandsOnHost(cmd_id, target.getId(), target.getShortName(), max_connection_attempt, start_date, end_date)
            self.blacklistTargetHostname(target, session)

        # log
        self.logger.debug("addCommand: %s (mode=%s)" % (str(cmd_id), mode))
        return cmd_id


    def blacklistTargetHostname(self, myTarget, session = create_session()):
        # Apply host name blacklist
        if not blacklist.checkWithRegexps(myTarget.target_name, self.config.include_hostname):
            # The host name is not in the whitelist
            if (self.config.ignore_non_fqdn and not blacklist.isFqdn(myTarget.target_name)) or (self.config.ignore_invalid_hostname and not blacklist.isValidHostname(myTarget.target_name)) or blacklist.checkWithRegexps(myTarget.target_name, self.config.exclude_hostname):
                # The host name is not FQDN or invalid, so we don't put it the
                # database. This way the host name won't be use to resolve the
                # computer host name.
                self.logger.debug("Host name has been filtered because '%s' is not FQDN, invalid or matched an exclude regexp" % myTarget.target_name)
                myTarget.target_name = ""
        session.update(myTarget) # not session.save as myTarget was attached to another session
        session.flush()

    def addCommandQuick(self, ctx, cmd, targets, desc, gid = None):
        """
        Schedule a command for immediate execution into database.
        Multiple machines can be specified in the targets parameter.

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
            ctx.userid,
            ctx.userid,
            desc,
            False,
            60,
            3,
            False
        )

    def addTarget(self, targetName, targetUuid, targetIp, targetMac, mirror, groupID = None):
        """ Inject a new Target object in our MSC database """
        myTarget = Target()
        myTarget.target_name = targetName
        myTarget.target_uuid = targetUuid
        myTarget.target_ipaddr = targetIp
        myTarget.target_macaddr = targetMac
        myTarget.mirrors = mirror
        myTarget.id_group = groupID
        myTarget.flush()
        return myTarget.id

    def getAllCommandsonhostCurrentstate(self, ctx): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.username == ctx.userid).group_by(self.commands_on_host.c.current_state).order_by(asc(self.commands_on_host.c.next_launch_date))
        l = map(lambda x: x.current_state, ret.all())
        session.close()
        return l

    def countAllCommandsonhostByCurrentstate(self, ctx, current_state, filt = ''): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands))
        ret = ret.filter(self.commands_on_host.c.current_state == current_state).filter(self.commands.c.username == ctx.userid)
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
        ret = ret.filter(self.commands.c.username == ctx.userid)
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
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.username == ctx.userid)
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
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.username == ctx.userid)
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

    def countAllCommandsOnHostGroup(self, ctx, gid, cmd_id, filt, history): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.target.c.id_group == gid).filter(self.commands.c.username == ctx.userid)
#        ret = ret.filter(self.commands_on_host.c.id == self.target.c.fk_commands_on_host)
        if cmd_id:
            ret = ret.filter(self.commands_on_host.c.fk_commands == str(cmd_id))
        if filt != '':
            ret = ret.filter(self.commands.c.title.like('%'+filt+'%'))
        if history:
            ret = ret.filter(self.commands_on_host.c.current_state == 'done')
        else:
            ret = ret.filter(self.commands_on_host.c.current_state != 'done')
        c = ret.count()
        session.close()
        return c

    def countAllCommandsOnGroup(self, ctx, gid, filt, history): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = session.query(Commands).select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.id_group == gid).filter(self.commands.c.username == ctx.userid)
        if filt != '':
            ret = ret.filter(self.commands.c.title.like('%'+filt+'%'))
        if history:
            ret = ret.filter(self.commands_on_host.c.current_state == 'done')
        else:
            ret = ret.filter(self.commands_on_host.c.current_state != 'done')
        c = ret.distinct().count()
        session.close()
        return c

    def countFinishedCommandsOnHost(self, ctx, uuid, filt):
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
            session = create_session()
            ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.target.c.target_uuid == uuid).filter(self.commands_on_host.c.current_state == 'done')
            #.filter(self.commands.c.username == ctx.userid)
            if filt != '':
                ret = ret.filter(self.commands.c.title.like('%'+filt+'%'))
            c = ret.count()
            session.close()
            return c
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return False

    def countUnfinishedCommandsOnHost(self, ctx, uuid, filt):
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
            session = create_session()
            ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.target.c.target_uuid == uuid).filter(self.commands_on_host.c.current_state != 'done')
            #.filter(self.commands.c.username == ctx.userid)
            if filt != '':
                ret = ret.filter(self.commands.c.title.like('%'+filt+'%'))
            c = ret.count()
            session.close()
            return c
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return False

    def countAllCommandsOnHost(self, ctx, uuid, filt):
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
            session = create_session()
            ret = session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands).join(self.target)).filter(self.target.c.target_uuid == uuid)
            #.filter(self.commands.c.username == ctx.userid)
            if filt != '':
                ret = ret.filter(self.commands.c.title.like('%'+filt+'%'))
            c = ret.count()
            session.close()
            return c
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return False

    def getAllCommandsOnHostGroup(self, ctx, gid, cmd_id, min, max, filt, history): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        query = session.query(Commands).add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state).add_column(self.target.c.target_name).add_column(self.target.c.target_uuid).filter(self.commands.c.username == ctx.userid)
        query = query.select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.id_group == gid)
        if cmd_id:
            query = query.filter(self.commands_on_host.c.fk_commands == str(cmd_id))
        if filt != '':
            query = query.filter(self.commands.c.title.like('%'+filt+'%'))
        if history:
            query = query.filter(self.commands_on_host.c.current_state == 'done')
        else:
            query = query.filter(self.commands_on_host.c.current_state != 'done')

        query = query.offset(int(min))
        query = query.limit(int(max)-int(min))
        query = query.order_by(asc(self.commands_on_host.c.next_launch_date))
        ret = query.all()
        session.close()
        return map(lambda x: (x[0].toH(), x[1], x[2], x[3]), ret)

    def getAllCommandsOnGroup(self, ctx, gid, min, max, filt, history): # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        query = session.query(Commands)
        query = query.select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.id_group == gid).filter(self.commands.c.username == ctx.userid)
        if filt != '':
            query = query.filter(self.commands.c.title.like('%'+filt+'%'))
        if history:
            query = query.filter(self.commands_on_host.c.current_state == 'done')
        else:
            query = query.filter(self.commands_on_host.c.current_state != 'done')
        query = query.offset(int(min))
        query = query.limit(int(max)-int(min))
        query = query.order_by(asc(self.commands_on_host.c.next_launch_date))
        ret = query.distinct().all()
        l = map(lambda x: x.toH(), ret)
        session.close()
        return l

    def getFinishedCommandsOnHost(self, ctx, uuid, min, max, filt):
        """
        Get the MSC commands that are flagged as 'done' for a host.
        The last inserted commands are returned first.
        """
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
            session = create_session()
            query = session.query(Commands).order_by(desc(Commands.c.id)).add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state) #.filter(self.commands.c.username == ctx.userid)
            query = query.select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.target_uuid == uuid).filter(self.commands_on_host.c.current_state == 'done')
            if filt != '':
                query = query.filter(self.commands.c.title.like('%'+filt+'%'))
            query = query.offset(int(min))
            query = query.limit(int(max)-int(min))
            query = query.order_by(asc(self.commands_on_host.c.next_launch_date))

            self.enableLogging()
            ret = query.all()
            self.disableLogging()

            session.close()
            return map(lambda x: (x[0].toH(), x[1], x[2]), ret)
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return []

    def getUnfinishedCommandsOnHost(self, ctx, uuid, min, max, filt):
        """
        Get the MSC commands that are flagged as not 'done' for a host.
        The last inserted commands are returned first.
        """
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
            session = create_session()
            query = session.query(Commands).order_by(desc(Commands.c.id)).add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state) #.filter(self.commands.c.username == ctx.userid)
            query = query.select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.target_uuid == uuid).filter(self.commands_on_host.c.current_state != 'done')
            if filt != '':
                query = query.filter(self.commands.c.title.like('%' + filt + '%'))
            query = query.offset(int(min))
            query = query.limit(int(max) - int(min))
            query = query.order_by(asc(self.commands_on_host.c.next_launch_date))

            self.enableLogging()
            ret = query.all()
            self.disableLogging()

            session.close()
            return map(lambda x: (x[0].toH(), x[1], x[2]), ret)
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return []

    def getAllCommandsOnHost(self, ctx, uuid, min, max, filt):
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx.userid, uuid):
            session = create_session()
            query = session.query(Commands).add_column(self.commands_on_host.c.id).add_column(self.commands_on_host.c.current_state)
            query = query.select_from(self.commands.join(self.commands_on_host).join(self.target)).filter(self.target.c.target_uuid == uuid)
            #.filter(self.commands.c.username == ctx.userid)
            if filt != '':
                query = query.filter(self.commands.c.title.like('%'+filt+'%'))
            query = query.offset(int(min))
            query = query.limit(int(max)-int(min))
            query = query.order_by(asc(self.commands_on_host.c.next_launch_date))
            self.enableLogging()
            ret = query.all()
            self.disableLogging()
            session.close()
            return map(lambda x: (x[0].toH(), x[1], x[2]), ret)
        self.logger.warn("User %s does not have good permissions to access '%s'" % (ctx.userid, uuid))
        return []

    def getCommandsOnHost(self, ctx, coh_id): # FIXME should we use the ctx
    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
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

    def getCommandOnGroupStatus(self, ctx, cmd_id):# TODO use ComputerLocationManager().doesUserHaveAccessToMachine
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
        session = create_session()
        for coh in session.query(CommandsOnHost).select_from(self.commands_on_host.join(self.commands)).filter(self.commands.c.id == cmd_id):
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
            ret[i]['total'].append(ret[i]['total'][0] * 100 / ret['total'])
        for i in ['wait_up', 'run_up', 'wait_ex', 'run_ex', 'wait_rm', 'run_rm']:
            ret['running'][i].append(ret['running'][i][0] * 100 / ret['total'])
        for i in ['fail_up', 'conn_up', 'fail_ex', 'conn_ex', 'fail_rm', 'conn_rm']:
            ret['failure'][i].append(ret['failure'][i][0] * 100 / ret['total'])
        session.close()
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
            
