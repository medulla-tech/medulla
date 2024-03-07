# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Provides access to MSC database
"""

# standard modules
import time
import re

# SqlAlchemy
from sqlalchemy import (
    and_,
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    ForeignKey,
    select,
    asc,
    or_,
    desc,
    func,
    not_,
    distinct,
)
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import NoSuchTableError, TimeoutError
from sqlalchemy.orm.exc import NoResultFound

# from sqlalchemy.orm import sessionmaker; Session = sessionmaker()
##from sqlalchemy.orm import sessionmaker
import datetime

# ORM mappings
from pulse2.database.msc.orm.commands import Commands
from pulse2.database.msc.orm.commands_on_host import CommandsOnHost
from pulse2.database.msc.orm.commands_on_host_phase import CommandsOnHostPhase
from pulse2.database.msc.orm.commands_history import CommandsHistory
from pulse2.database.msc.orm.target import Target
from pulse2.database.msc.orm.pull_targets import PullTargets
from pulse2.database.msc.orm.bundle import Bundle
from mmc.database.database_helper import DatabaseHelper

# Pulse 2 stuff
from pulse2.managers.location import ComputerLocationManager

# Imported last
import logging

NB_DB_CONN_TRY = 2

# TODO need to check for useless function (there should be many unused one...)


class MscDatabase(DatabaseHelper):
    """
    Singleton Class to query the msc database.

    """

    def db_check(self):
        self.my_name = "msc"
        self.configfile = "msc.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("Msc database is connecting")
        self.pattern = re.compile("^([0-9]{1,2})[-;'.|@#\"]{1}[0-9]{1,2}$")
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
            pool_timeout=self.config.dbpooltimeout,
            convert_unicode=True,
        )
        if not self.db_check():
            return False
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
        return True

    def initTables(self):
        """
        Initialize all SQLalchemy tables
        """
        try:
            # commands
            self.commands = Table(
                "commands", self.metadata, autoload=True, extend_existing=True
            )
            # commands_history
            self.commands_history = Table(
                "commands_history", self.metadata, autoload=True
            )
            # target
            self.target = Table("target", self.metadata, autoload=True)
            # pull_targets
            self.pull_targets = Table("pull_targets", self.metadata, autoload=True)
            # bundle
            self.bundle = Table("bundle", self.metadata, autoload=True)
            # commands_on_host_phase
            self.commands_on_host_phase = Table(
                "phase", self.metadata, autoload=True, extend_existing=True
            )
            # commands_on_host
            self.commands_on_host = Table(
                "commands_on_host", self.metadata, autoload=True, extend_existing=True
            )
            # version
            self.version = Table("version", self.metadata, autoload=True)
        except NoSuchTableError as e:
            self.logger.error(
                "Cant load the msc database : table '%s' does not exists"
                % (str(e.args[0]))
            )
            return False
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the msc database
        """
        mapper(CommandsHistory, self.commands_history)
        mapper(CommandsOnHostPhase, self.commands_on_host_phase)
        mapper(PullTargets, self.pull_targets)
        mapper(CommandsOnHost, self.commands_on_host)
        mapper(Target, self.target)
        mapper(Bundle, self.bundle)
        mapper(Commands, self.commands)
        # FIXME: Version is missing

    ####################################

    def getIdCommandOnHost(self, ctx, id):
        session = create_session()
        query = (
            session.query(CommandsOnHost)
            .select_from(self.commands_on_host.join(self.commands))
            .filter(self.commands.c.id == id)
        )
        query = self.__queryUsersFilter(ctx, query)
        query = query.all()
        if not isinstance(query, list):
            ret = query.id
            # elif query:
        elif query:
            ret = []
            for q in query:
                ret.append(q.id)
        else:
            ret = -1
        session.close()
        return ret

    def createBundle(self, title="", session=None):
        """
        Return a new Bundle
        """
        if session is None:
            session = create_session()
        bdl = Bundle()
        bdl.title = title
        bdl.do_reboot = "disable"
        session.add(bdl)
        session.flush()
        return bdl

    def createcommanddirectxmpp(
        self,
        package_id,
        start_file,
        parameters,
        files,
        start_script,
        clean_on_success,
        start_date,
        end_date,
        connect_as,
        creator,
        title,
        next_connection_delay,
        max_connection_attempt,
        maxbw,
        deployment_intervals,
        fk_bundle,
        order_in_bundle,
        proxies,
        proxy_mode,
        state,
        sum_running,
        cmd_type=0,
    ):
        session = create_session()
        obj = self.createCommand(
            session,
            package_id,
            start_file,
            parameters,
            files,
            start_script,
            clean_on_success,
            start_date,
            end_date,
            connect_as,
            creator,
            title,
            next_connection_delay,
            max_connection_attempt,
            maxbw,
            deployment_intervals,
            fk_bundle,
            order_in_bundle,
            proxies,
            proxy_mode,
            state,
            sum_running,
            cmd_type=0,
        )
        return obj
        session.close()

    def createCommand(
        self,
        session,
        package_id,
        start_file,
        parameters,
        files,
        start_script,
        clean_on_success,
        start_date,
        end_date,
        connect_as,
        creator,
        title,
        next_connection_delay,
        max_connection_attempt,
        maxbw,
        deployment_intervals,
        fk_bundle,
        order_in_bundle,
        proxies,
        proxy_mode,
        state,
        sum_running,
        cmd_type=0,
    ):
        """
        Return a Command object
        """
        if isinstance(files, list):
            files = "\n".join(files)

        cmd = Commands()
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
        # cmd.do_halt = ','.join(do_halt)
        # cmd.do_reboot = do_reboot
        # cmd.do_wol = do_wol
        # cmd.do_imaging_menu = do_wol_with_imaging
        if next_connection_delay is not None and next_connection_delay == "":
            next_connection_delay = 0

        cmd.next_connection_delay = next_connection_delay
        cmd.max_connection_attempt = max_connection_attempt
        # cmd.do_inventory = do_inventory
        cmd.maxbw = maxbw
        cmd.deployment_intervals = deployment_intervals
        cmd.fk_bundle = fk_bundle
        cmd.order_in_bundle = order_in_bundle
        cmd.proxy_mode = (
            proxy_mode  # FIXME: we may add some code to check everything is OK
        )
        cmd.state = state
        cmd.sum_running = sum_running
        cmd.type = cmd_type
        cmd.ready = False
        session.add(cmd)
        session.flush()
        return cmd

    @DatabaseHelper._session
    def _force_command_type(self, session, cmd_id, type):
        """
        Force type of command cmd_id, usually used for reschedule
        convergence commands
        """
        cmd = session.query(Commands).get(cmd_id)
        if cmd:
            self.logger.debug("Force command %s to type %s" % (cmd_id, type))
            cmd.type = type
            session.add(cmd)
            session.flush()
            return True
        self.logger.warn("Failed to set command %s to type %s" % (cmd, type))
        return False

    @DatabaseHelper._session
    def _set_command_ready(self, session, cmd_id):
        """
        Set command as ready, usually used for reschedule
        convergence commands
        """
        cmd = session.query(Commands).get(cmd_id)
        if cmd:
            self.logger.debug("Set command %s as ready" % (cmd_id))
            cmd.ready = 1
            session.add(cmd)
            session.flush()
            return True
        self.logger.warn("Failed to set command %s as ready" % (cmd))
        return False

    def deleteBundle(self, bundle_id):
        """
        Deletes a bundle with all related sub-elements.

        @param bundle_id: id of bundle
        @type bundle_id: int
        """
        session = create_session()
        session.begin()
        try:
            bundle = session.query(Bundle).get(bundle_id)
            if not bundle:
                self.logger.warn("Unable to find bundle (id=%s)" % bundle_id)
                return False

            cmds = session.query(Commands)
            cmds = cmds.select_from(self.commands)
            cmds = cmds.filter(self.commands.c.fk_bundle == bundle_id)
            # self.logger.warn("Commands : %s)" % cmds.all())

            ok = self._deleteCommands(session, cmds)
            if ok:
                session.delete(bundle)
                session.flush()
                session.commit()
                session.close()
                return True
            else:
                return False

        except Exception as exc:
            self.logger.error(
                "Delete of bundle (id=%s) failed: %s" % (bundle_id, str(exc))
            )
            session.rollback()
            session.close()
            return False

    def get_count(self, q):
        return q.with_entities(func.count()).scalar()

    def xmpp_create_Target(
        self,
        target_uuid,
        target_name,
        mirrors="file:///var/lib/pulse2/packages",
        target_macaddr="",
        target_bcast="",
        target_ipaddr="",
        target_network="",
        id_group="",
    ):
        session = create_session()
        target = Target()
        target.target_macaddr = target_macaddr
        target.id_group = id_group
        target.target_uuid = target_uuid
        target.target_bcast = target_bcast
        target.target_name = target_name
        target.target_ipaddr = target_ipaddr
        target.mirrors = mirrors
        target.target_network = target_network
        session.add(target)
        session.flush()
        session.close()
        result = {
            "id": target.id,
            "target_macaddr": target.target_macaddr,
            "id_group": target.id_group,
            "target_uuid": target.target_uuid,
            "target_bcast": target.target_bcast,
            "target_name": target.target_name,
            "target_ipaddr": target.target_ipaddr,
            "mirrors": target.mirrors,
            "target_network": target.target_network,
        }
        return result

    def uuidtoid(self, uuid):
        if isinstance(uuid, str):
            if uuid.strip().lower().startswith("uuid"):
                return int(uuid[4:])
            else:
                return int(uuid)
        else:
            return uuid

    def xmpp_create_CommandsOnHost(
        self, fk_commands, fk_target, host, end_date, start_date, id_group=None
    ):
        session = create_session()
        commandsOnHost = CommandsOnHost()
        commandsOnHost.fk_commands = fk_commands
        commandsOnHost.host = host
        commandsOnHost.start_date = start_date
        commandsOnHost.end_date = end_date
        commandsOnHost.id_group = id_group
        commandsOnHost.fk_target = self.uuidtoid(fk_target)
        session.add(commandsOnHost)
        session.flush()
        session.close()
        return commandsOnHost

    def xmpp_create_CommandsOnHostPhasedeploykiosk(self, fk_commands):
        names = ["upload", "execute", "delete", "inventory", "done"]
        for indexname in range(len(names)):
            commandsOnHostPhase = self.xmpp_create_CommandsOnHostPhasedeploy(
                fk_commands, names[indexname]
            )
        return commandsOnHostPhase

    def xmpp_create_CommandsOnHostPhasedeploy(self, fk_commands, name, state="ready"):
        session = create_session()
        commandsOnHostPhase = CommandsOnHostPhase()
        commandsOnHostPhase.fk_commands_on_host = fk_commands
        commandsOnHostPhase.state = state
        commandsOnHostPhase.name = name
        if name == "upload":
            commandsOnHostPhase.phase_order = 0
        elif name == "execute":
            commandsOnHostPhase.phase_order = 1
        elif name == "delete":
            commandsOnHostPhase.phase_order = 2
        elif name == "inventory":
            commandsOnHostPhase.phase_order = 3
        elif name == "done":
            commandsOnHostPhase.phase_order = 4
        session.add(commandsOnHostPhase)
        session.flush()
        session.close()
        return commandsOnHostPhase

    def get_counta(self, q):
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

    def get_countb(self, q):
        return q.with_entities(func.count()).scalar()

    def get_count_timeout_wol_deploy(self, id_command, start_date):
        """
        This function is scheduled by xmpp.
        It counts the number of machines out of the deployment intervals
        """
        session = create_session()
        numberTimedout = (
            session.query(func.count(CommandsOnHost))
            .filter(
                and_(
                    CommandsOnHost.fk_commands == id_command,
                    CommandsOnHost.stage == "ended",
                    CommandsOnHost.current_state == "over_timed",
                    CommandsOnHost.start_date == start_date,
                )
            )
            .scalar()
        )
        return numberTimedout

    def deployxmpponmachine(self, command_id, uuid):
        result = {}
        sqlselect = """
            SELECT
                host,
                target_name,
                title,
                commands.start_date AS startdatec,
                commands_on_host.start_date AS startdateh,
                commands.end_date AS enddatec,
                commands_on_host.end_date AS enddateh,
                target_ipaddr,
                target_uuid,
                target_macaddr,
                target_bcast,
                target_network,
                package_id,
                creator,
                connect_as,
                commands.creation_date
            FROM
                commands_on_host
                    INNER JOIN
                commands ON commands.id = commands_on_host.fk_commands
                    INNER JOIN
                target ON target.id = commands_on_host.fk_target
                    INNER JOIN
                phase ON commands_on_host.id = phase.fk_commands_on_host
            WHERE
                commands.id = %s
                and commands_on_host.id_group IS NULL
                and target_uuid = "%s"
            GROUP BY commands_on_host.id
                ;""" % (
            command_id,
            uuid,
        )
        resultsql = self.db.execute(sqlselect)
        for x in resultsql:
            result["host"] = x.host
            result["target_name"] = x.target_name
            result["title"] = x.title
            result["startdatec"] = x.startdatec
            result["startdateh"] = x.startdateh
            result["enddatec"] = x.enddatec
            result["enddateh"] = x.enddateh
            result["target_ipaddr"] = x.target_ipaddr
            result["target_uuid"] = x.target_uuid
            result["target_macaddr"] = x.target_macaddr
            result["target_bcast"] = x.target_bcast
            result["target_network"] = x.target_network
            result["package_id"] = x.package_id
            result["creator"] = x.creator
            result["connect_as"] = x.connect_as
            result["creation_date"] = x.creation_date
        return result

    @DatabaseHelper._sessionm
    def get_msc_listuuid_commandid(self, session, command_id, filter, start, limit):
        start = int(start)
        sqlselect = """
            SELECT
                DISTINCT commands_on_host.start_date as dated,
                commands_on_host.end_date as datef
            FROM
                    commands_on_host
                        INNER JOIN
                    target ON target.id = commands_on_host.fk_target
            WHERE
                    commands_on_host.fk_commands = %s
            ORDER BY dated DESC
            LIMIT 1;""" % (
            command_id
        )
        resultsql = self.db.execute(sqlselect)
        if resultsql is not None:
            dateintervale = [x for x in resultsql]
            if dateintervale:
                datestartstr = dateintervale[0].dated
                dateendstr = dateintervale[0].datef
            else:
                self.logger.warning("command [%s] deploy missing msc" % command_id)
                return ""
        else:
            return ""

        query = (
            session.query(Target.target_uuid)
            .distinct()
            .filter(CommandsOnHost.fk_commands == command_id)
            .filter(CommandsOnHost.start_date <= datestartstr)
            .filter(CommandsOnHost.end_date >= dateendstr)
            .join(CommandsOnHost, Target.id == CommandsOnHost.fk_target)
        )

        if start != -1:
            query = query.offset(int(start)).limit(int(limit))
        query = query.count()

        query1 = (
            session.query(Target.target_uuid)
            .distinct()
            .filter(CommandsOnHost.fk_commands == command_id)
            .filter(CommandsOnHost.start_date <= datestartstr)
            .filter(CommandsOnHost.end_date >= dateendstr)
            .join(CommandsOnHost, Target.id == CommandsOnHost.fk_target)
        )
        if start != -1:
            query1 = query1.offset(int(start)).limit(int(limit))

        query1 = query1.all()
        commands = ""
        if query1 is not None:
            commands = [element[0].split("UUID")[1] for element in query1]
            commands = ",".join(commands)
            return {"total": query, "list": commands}
        else:
            return {"total": 0, "list": commands}

        sqlselect = """
            SELECT
                GROUP_CONCAT(DISTINCT SUBSTR(target_uuid, 5) SEPARATOR ',') as listuuid
            FROM
                (SELECT
                    commands_on_host.fk_commands,
                    target.target_name as dname,
                    target.target_uuid
                FROM
                    commands_on_host
                        INNER JOIN
                    target ON target.id = commands_on_host.fk_target
                WHERE
                    commands_on_host.fk_commands = %s  and
                    commands_on_host.start_date <= '%s' and
                    commands_on_host.end_date >= '%s'
                    %s
                    ) as listhost;
                        """ % (
            command_id,
            datestartstr,
            dateendstr,
            limit,
        )

        resultsql = self.db.execute(sqlselect)

        if resultsql is not None:
            z = [x for x in resultsql][0].listuuid
            if z is not None:
                return z
        self.logger.warning(
            "command [%s] deploy missing for slot [%s,%s]"
            % (command_id, datestartstr, dateendstr)
        )
        return ""

    def get_msc_listhost_commandid(self, command_id):
        sqlselect = """
            SELECT
                DISTINCT commands_on_host.start_date as dated,
                commands_on_host.end_date as datef
            FROM
                    commands_on_host
                        INNER JOIN
                    target ON target.id = commands_on_host.fk_target
            WHERE
                    commands_on_host.fk_commands = %s
            ORDER BY dated DESC
            LIMIT 1;""" % (
            command_id
        )
        resultsql = self.db.execute(sqlselect)
        if resultsql is not None:
            dateintervale = [x for x in resultsql]
            if dateintervale:
                datestartstr = dateintervale[0].dated
                dateendstr = dateintervale[0].datef
            else:
                self.logger.warning("command [%s] deploy missing msc" % command_id)
                return ""
        else:
            return ""
        sqlselect = """
            SELECT
                GROUP_CONCAT(DISTINCT CONCAT('"',
                            SUBSTR(dname,
                                1,
                                CHAR_LENGTH(dname) - 1),
                            '"')
                    SEPARATOR ',') as listhostname
            FROM
                (SELECT
                    commands_on_host.fk_commands,
                    target.target_name as dname,
                    target.target_uuid
                FROM
                    commands_on_host
                        INNER JOIN
                    target ON target.id = commands_on_host.fk_target
                WHERE
                    commands_on_host.fk_commands = %s  and
                    commands_on_host.start_date <= '%s' and
                    commands_on_host.end_date >= '%s'
                    ) as listhost;
                        """ % (
            command_id,
            datestartstr,
            dateendstr,
        )

        resultsql = self.db.execute(sqlselect)

        if resultsql is not None:
            z = [x for x in resultsql][0].listhostname
            if z is not None:
                return z
        self.logger.warning(
            "command [%s] deploy missing for slot [%s,%s]"
            % (command_id, datestartstr, dateendstr)
        )
        return ""

    @DatabaseHelper._sessionm
    def deployxmppscheduler(self, session, login, minimum, maximum, filt):
        """
        This function isued to retrieve all the scheduled deployments on msc

        Args:
            login: The login of the user
            minimum: Minimum value ( for pagination )
            maximum: Maximum value ( for pagination )
            filt: Filter of the search
        Returns:
            It returns the list of all the scheduled deployments on msc
        """
        listuser = []
        if isinstance(login, list):
            listuser = ['"%s"' % x.strip() for x in login if x.strip() != ""]
        datenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sqlselect = """
            SELECT
                COUNT(*) as nbmachine,
                target.id_group AS GRP,
                CONCAT('',
                        IF(target.id_group != NULL
                                OR target.id_group = '',
                            CONCAT('computer', commands.title),
                            CONCAT('GRP ', commands.title))) AS titledeploy,
                CONCAT(commands.title, target.id_group) AS commands_title1,
                commands_on_host.fk_commands AS commands_on_host_fk_commands,
                commands_on_host.host AS commands_on_host_host,
                commands.start_date AS commands_start_date,
                commands.end_date AS commands_end_date,
                commands.creator AS commands_creator,
                commands.title AS commands_title,
                commands.package_id AS commands_package_id,
                target.target_uuid AS target_target_uuid,
                target.target_macaddr AS target_target_macaddr,
                phase.name AS phase_name,
                phase.state AS phase_state
            FROM
                commands_on_host
                    INNER JOIN
                commands ON commands.id = commands_on_host.fk_commands
                    INNER JOIN
                target ON target.id = commands_on_host.fk_target
                    INNER JOIN
                phase ON commands_on_host.id = phase.fk_commands_on_host
            WHERE
            commands.start_date > '%s'
            AND
            """ % datenow
        sqlfilter = """
            phase.name = 'execute'
                AND
                    phase.state = 'ready'"""

        if login:
            if listuser:
                sqlfilter = (
                    sqlfilter
                    + """
                AND
                    commands.creator REGEXP %s """
                    % "|".join(listuser)
                )
            else:
                sqlfilter = (
                    sqlfilter
                    + """
                AND
                    commands.creator = '%s'"""
                    % login
                )

        if filt:
            sqlfilter = (
                sqlfilter
                + """
            AND
            (commands.title like '%%%s%%'
            OR
            commands.creator like '%%%s%%'
            OR
            commands.start_date like '%%%s%%')"""
                % (filt, filt, filt)
            )

        reqsql = sqlselect + sqlfilter

        sqllimit = ""
        if minimum and maximum:
            sqllimit = """
                LIMIT %d
                OFFSET %d""" % (
                int(maximum) - int(minimum),
                int(minimum),
            )
            reqsql = reqsql + sqllimit

        sqlgroupby = """
            GROUP BY titledeploy"""

        reqsql = reqsql + sqlgroupby + ";"

        sqlselect = """
            Select COUNT(nb) AS TotalRecords from(
                SELECT
                    COUNT(*) AS nb,
                    CONCAT('',
                            IF(target.id_group != NULL
                                    OR target.id_group = '',
                                CONCAT('computer', commands.title),
                                CONCAT('GRP ', commands.title))) AS titledeploy
                FROM
                    commands_on_host
                        INNER JOIN
                    commands ON commands.id = commands_on_host.fk_commands
                        INNER JOIN
                    target ON target.id = commands_on_host.fk_target
                        INNER JOIN
                    phase ON commands_on_host.id = phase.fk_commands_on_host
                WHERE
                    commands.start_date > '%s'
            AND
            """ % datenow
        reqsql1 = sqlselect + sqlfilter + sqllimit + sqlgroupby + ") as tmp;"

        result = {}
        resulta = session.execute(reqsql)
        resultb = session.execute(reqsql1)
        sizereq = [x for x in resultb][0][0]
        result["lentotal"] = sizereq
        result["min"] = int(minimum)
        result["nb"] = int(maximum) - int(minimum)
        result["tabdeploy"] = {}
        inventoryuuid = []
        host = []
        command = []
        pathpackage = []
        start = []
        end = []
        tabdeploy = {}
        creator = []
        title = []
        groupid = []
        macadress = []
        nbmachine = []
        titledeploy = []
        for x in resulta:
            nbmachine.append(x.nbmachine)
            host.append(x.commands_on_host_host)
            inventoryuuid.append(x.target_target_uuid)
            command.append(x.commands_on_host_fk_commands)
            pathpackage.append(x.commands_package_id)
            start.append(x.commands_start_date)
            end.append(x.commands_end_date)
            creator.append(x.commands_creator)
            title.append(x.commands_title)
            titledeploy.append(x.titledeploy)
            groupid.append(x.GRP)
            macadress.append(x.target_target_macaddr)
        result["tabdeploy"]["nbmachine"] = nbmachine
        result["tabdeploy"]["host"] = host
        result["tabdeploy"]["inventoryuuid"] = inventoryuuid
        result["tabdeploy"]["command"] = command
        result["tabdeploy"]["pathpackage"] = pathpackage
        result["tabdeploy"]["start"] = start
        result["tabdeploy"]["end"] = end
        result["tabdeploy"]["creator"] = creator
        result["tabdeploy"]["title"] = title
        result["tabdeploy"]["macadress"] = macadress
        result["tabdeploy"]["groupid"] = groupid
        result["tabdeploy"]["titledeploy"] = titledeploy
        return result

    def updategroup(self, group):
        session = create_session()
        join = (
            self.commands_on_host.join(self.commands)
            .join(self.target)
            .join(self.commands_on_host_phase)
        )
        q = session.query(CommandsOnHost, Commands, Target, CommandsOnHostPhase)
        q = q.select_from(join)
        q = q.filter(
            and_(
                self.commands_on_host_phase.c.name == "execute",
                self.commands_on_host_phase.c.state == "ready",
                self.target.c.id_group == group,
            )
        ).all()
        # return informations for update table deploy xmpp
        result = []
        for objdeploy in q:
            resultat = {}
            resultat["gid"] = group
            resultat["pathpackage"] = objdeploy.Commands.package_id
            resultat["state"] = "ABORT DEPLOYMENT CANCELLED BY USER"
            resultat["start"] = objdeploy.CommandsOnHost.start_date
            resultat["end"] = objdeploy.CommandsOnHost.end_date
            resultat["inventoryuuid"] = objdeploy.Target.target_uuid
            resultat["host"] = objdeploy.Target.target_name
            resultat["command"] = objdeploy.Commands.id
            resultat["title"] = objdeploy.Commands.title
            resultat["macadress"] = objdeploy.Target.target_macaddr
            resultat["login"] = objdeploy.Commands.creator
            resultat["startd"] = time.mktime(
                objdeploy.CommandsOnHost.start_date.timetuple()
            )
            resultat["endd"] = time.mktime(
                objdeploy.CommandsOnHost.end_date.timetuple()
            )
            result.append(resultat)
        for x in q:
            # print x.CommandsOnHost.id
            # session.query(CommandsOnHost).filter(CommandsOnHost.id == x.CommandsOnHost.id ).delete()
            # session.flush()
            # session.query(CommandsOnHostPhase).filter(CommandsOnHostPhase.fk_commands_on_host == x.CommandsOnHost.id ).delete()
            # session.flush()
            session.query(CommandsOnHost).filter(
                CommandsOnHost.id == x.CommandsOnHost.id
            ).update(
                {CommandsOnHost.current_state: "done", CommandsOnHost.stage: "ended"}
            )
            session.flush()
            session.query(CommandsOnHostPhase).filter(
                CommandsOnHostPhase.fk_commands_on_host == x.CommandsOnHost.id
            ).update({CommandsOnHostPhase.state: "done"})
            session.flush()
        session.flush()
        session.close()
        return result

    def xmppstage_statecurrent_xmpp(self):
        """
        this function scheduled by xmpp, change current_state et stage if command is out of deployment_intervals
        """
        datenow = datetime.datetime.now()
        session = create_session()
        session.query(CommandsOnHost).filter(
            and_(
                CommandsOnHost.current_state == "scheduled",
                CommandsOnHost.stage == "pending",
                CommandsOnHost.end_date < datenow,
            )
        ).update(
            {CommandsOnHost.current_state: "over_timed", CommandsOnHost.stage: "ended"}
        )
        session.flush()
        session.close()

    @DatabaseHelper._sessionm
    def test_deploy_in_partiel_slot(self, session, title):
        """
        This function is used to check if 1 partial slot constraint does not prohibit deploying on 1 machine
        Args:
            session: The SQL Alchemy session
            title: le nom du deployement.
            Returns:
                True la machine peut etre deploye
                False la machine ne peut pas etre deploye.
        """
        datenow = datetime.datetime.now()
        hactuel = int(datenow.strftime("%H"))
        query = session.query(Commands.deployment_intervals).filter(
            Commands.title.like(title)
        )
        nb = query.count()
        if nb == 0:
            return True
        res = query.first()
        if not res:
            return True
        # analyse si deploy true or false
        tb = [
            re.sub("[-'*;|@#\"]{1}", "-", x)
            for x in res.deployment_intervals.split(",")
            if self.pattern.match(x.strip())
        ]
        for c in tb:
            start, end = c.split("-")
            if hactuel >= int(start) and hactuel <= int(end):
                # on a trouver 1 cas on deploy
                return True
        return False

    @DatabaseHelper._sessionm
    def deployxmpp(self, session, limitnbr=100):
        """
        select deploy machine
        """
        datenow = datetime.datetime.now()
        datestr = datenow.strftime("%Y-%m-%d %H:%M:%S")
        sqlselect = """
        SELECT
                `commands`.`id` AS commands_id,
                `commands`.`title` AS commands_title,
                `commands`.`creator` AS commands_creator,
                `commands`.`package_id` AS commands_package_id,
                `commands`.`start_date` AS commands_start_date,
                `commands`.`end_date` AS commands_end_date,
                `commands_on_host`.`id` AS commands_on_host_id,
                `target`.`target_name` AS target_target_name,
                `target`.`target_uuid` AS target_target_uuid,
                `target`.`id_group` AS target_id_group,
                `target`.`target_macaddr` AS target_target_macaddr
            FROM
                commands_on_host
                    INNER JOIN
                commands ON commands.id = commands_on_host.fk_commands
                    INNER JOIN
                target ON target.id = commands_on_host.fk_target
                    INNER JOIN
                `phase` ON `phase`.fk_commands_on_host = `commands_on_host`.`id`
            WHERE
                `phase`.`name` = 'execute'
                    AND
                `phase`.`state` = 'ready'
                    AND
                    '%s' BETWEEN commands.start_date AND commands.end_date limit %s;""" % (
            datenow,
            limitnbr,
        )
        # self.logger.debug("sqlselect %s"%sqlselect)
        selectedMachines = session.execute(sqlselect)
        nb_machine_select_for_deploy_cycle = selectedMachines.rowcount
        if nb_machine_select_for_deploy_cycle == 0:
            self.logger.debug("Aucun deployement for process")
            return nb_machine_select_for_deploy_cycle, []
        else:
            self.logger.debug("%s mach for deploy" % nb_machine_select_for_deploy_cycle)

        machine_status_update = []
        unique_deploy_on_machine = []
        updatemachine = []

        self.logger.debug("launch new select deploy machine")

        for msc_machine_to_deploy in selectedMachines:
            machine_status_update.append(str(msc_machine_to_deploy.commands_on_host_id))
            # on prepare les machines a mettre a jour.
            self.logger.debug(
                "machine %s [%s] presente for deploy package %s"
                % (
                    msc_machine_to_deploy.target_target_name,
                    msc_machine_to_deploy.target_target_uuid,
                    msc_machine_to_deploy.commands_package_id,
                )
            )
            title = str(msc_machine_to_deploy.commands_title)
            self.logger.info("title '%s'" % title)
            if title.startswith("Convergence on"):
                title = "%s %s" % (title, datestr)

            if msc_machine_to_deploy.target_target_uuid not in unique_deploy_on_machine:
                unique_deploy_on_machine.append(
                    msc_machine_to_deploy.target_target_uuid
                )
                updatemachine.append(
                    {
                        "name": str(msc_machine_to_deploy.target_target_name)[:-1],
                        "pakkageid": str(msc_machine_to_deploy.commands_package_id),
                        "commandid": msc_machine_to_deploy.commands_id,
                        "mac": str(msc_machine_to_deploy.target_target_macaddr),
                        "count": 0,
                        "cycle": 0,
                        "login": str(msc_machine_to_deploy.commands_creator),
                        "start_date": msc_machine_to_deploy.commands_start_date,
                        "end_date": msc_machine_to_deploy.commands_end_date,
                        "title": title,
                        "UUID": str(msc_machine_to_deploy.target_target_uuid),
                        "GUID": msc_machine_to_deploy.target_id_group,
                    }
                )
                # recherche machine existe pour xmpp
                self.logger.info(
                    "deploy on machine %s [%s] -> %s"
                    % (
                        msc_machine_to_deploy.target_target_name,
                        msc_machine_to_deploy.target_target_uuid,
                        msc_machine_to_deploy.commands_package_id,
                    )
                )
            else:
                self.logger.warn(
                    "Cancel deploy in process\n"
                    "Deploy on machine %s [%s] -> %s"
                    % (
                        msc_machine_to_deploy.target_target_name,
                        msc_machine_to_deploy.target_target_uuid,
                        msc_machine_to_deploy.commands_package_id,
                    )
                )
        # deploiement status dans msc imédiatement mis a jour pour libere
        # imediatement le verrou sur la table msc.
        if machine_status_update:
            list_uuid_machine = ",".join(machine_status_update)
            sql = """UPDATE `msc`.`commands_on_host`
                        SET
                           `current_state`='done',
                            `stage`='ended'
                        WHERE `commands_on_host`.`id` in(%s);
                    UPDATE `msc`.`phase`
                        SET
                           `phase`.`state`='done'
                        WHERE `phase`.`fk_commands_on_host` in(%s);
            """ % (
                list_uuid_machine,
                list_uuid_machine,
            )
            # self.logger.debug("sql %s"%sql)
            ret = session.execute(sql)
            self.logger.debug("update deployement %s" % ret.rowcount)
        session.commit()
        session.flush()
        return nb_machine_select_for_deploy_cycle, updatemachine

    @DatabaseHelper._sessionm
    def get_conrainte_slot_deployment_commands(self, session, commands):
        res = (
            session.query(Commands.id, Commands.deployment_intervals)
            .filter(Commands.id.in_(commands))
            .all()
        )
        result = {}
        for element in res:
            result[str(element[0])] = element[1]
        return result

    @DatabaseHelper._sessionm
    def get_deploy_inprogress_by_team_member(
        self,
        session,
        login,
        intervalsearch,
        minimum,
        maximum,
        filt,
        typedeploy="command",
    ):
        """
        This function is used to retrieve not yet done deployements of a team.
        This team is found based on the login of a member.

        Args:
            session: The SQL Alchemy session
            login: The login of the user
            intervalsearch: The interval on which we search the deploys.
            minimum: Minimum value ( for pagination )
            maximum: Maximum value ( for pagination )
            filt: Filter of the search
            Returns:
                It returns all the deployement not yet started of a specific team.
                It can be done by time search too.
        """
        list_login = []
        if login:
            if isinstance(login, (tuple, list)):
                list_login = [x.strip() for x in login if x.strip() != ""]
            else:
                list_login.append(login)
        datenow = datetime.datetime.now()
        delta = datetime.timedelta(seconds=intervalsearch)
        datereduced = datenow - delta
        query = (
            session.query(
                Commands.id,
                func.count(Commands.id).label("nb_machine"),
                Commands.title,
                Commands.creator,
                Commands.package_id,
                Commands.start_date,
                Commands.end_date,
                CommandsOnHost.id,
                Target.target_name,
                Target.target_uuid,
                Target.id_group,
                Target.target_macaddr,
                Commands.deployment_intervals,
            )
            .join(CommandsOnHost, Commands.id == CommandsOnHost.fk_commands)
            .join(Target, Target.id == CommandsOnHost.fk_target)
            .join(
                CommandsOnHostPhase,
                CommandsOnHostPhase.fk_commands_on_host == CommandsOnHost.id,
            )
            .filter(CommandsOnHostPhase.name == "upload")
            .filter(CommandsOnHostPhase.state == "ready")
            .filter(Commands.end_date > datereduced)
            .filter(Commands.type != 2)
        )
        if typedeploy != "command":
            query = query.filter(Commands.title.like("%%-@upd@%%"))
        else:
            query = query.filter(Commands.creator.in_(list_login))

        if list_login:
            query = query.filter(Commands.creator.in_(list_login))
            if filt:
                query = query.filter(
                    or_(
                        Commands.title.like("%%%s%%" % filt),
                        Commands.package_id.like("%%%s%%" % filt),
                        Commands.start_date.like("%%%s%%" % filt),
                        Commands.end_date.like("%%%s%%" % filt),
                        CommandsOnHost.id.like("%%%s%%" % filt),
                        Target.target_name.like("%%%s%%" % filt),
                        Target.target_uuid.like("%%%s%%" % filt),
                        Target.id_group.like("%%%s%%" % filt),
                        Target.target_macaddr.like("%%%s%%" % filt),
                    )
                )
        else:
            if filt:
                query = query.filter(
                    or_(
                        Commands.title.like("%%%s%%" % filt),
                        Commands.creator.like("%%%s%%" % filt),
                        Commands.package_id.like("%%%s%%" % filt),
                        Commands.start_date.like("%%%s%%" % filt),
                        Commands.end_date.like("%%%s%%" % filt),
                        CommandsOnHost.id.like("%%%s%%" % filt),
                        Target.target_name.like("%%%s%%" % filt),
                        Target.target_uuid.like("%%%s%%" % filt),
                        Target.id_group.like("%%%s%%" % filt),
                        Target.target_macaddr.like("%%%s%%" % filt),
                    )
                )
        query = query.group_by(Commands.id, CommandsOnHostPhase.state)
        nb = query.count()
        query = query.offset(int(minimum)).limit(int(maximum) - int(minimum))
        res = query.all()

        result = {"total": nb, "elements": []}
        for element in res:
            result["elements"].append(
                {
                    "cmd_id": element[0],
                    "nb_machines": element[1],
                    "package_name": element[2],
                    "login": element[3],
                    "package_uuid": element[4],
                    "date_start": element[5],
                    "date_end": element[6],
                    "machine_name": element[8],
                    "uuid_inventory": element[9],
                    "gid": element[10],
                    "mac_address": element[11],
                    "deployment_intervals": element[12],
                }
            )
        return result

    def deleteCommand(self, cmd_id):
        """
        Deletes a command with all related sub-elements.

        @param cmd_id: Commands id
        @type cmd_id: int
        """
        session = create_session()
        session.begin()
        try:
            cmds = session.query(Commands)
            cmds = cmds.select_from(self.commands)
            cmds = cmds.filter(self.commands.c.id == cmd_id)

            ok = self._deleteCommands(session, cmds)
            if ok:
                session.commit()
                session.close()
                return True
            else:
                session.rollback()
                session.close()
                return False

        except Exception as exc:
            self.logger.error(
                "Delete of command (id=%s) failed: %s" % (cmd_id, str(exc))
            )
            session.rollback()
            session.close()
            return False

    def deleteCommandOnHost(self, coh_id):
        """
        Deletes a command with all related sub-elements.

        @param cmd_id: Commands id
        @type cmd_id: int
        """
        session = create_session()
        session.begin()
        try:
            cohs = session.query(CommandsOnHost)
            cohs = cohs.select_from(self.commands_on_host)
            cohs = cohs.filter(self.commands_on_host.c.id == coh_id)

            ok = self._deleteCommandsOnHost(session, cohs)
            if ok:
                session.commit()
                session.close()
                return True
            else:
                session.rollback()
                session.close()
                return False

        except Exception as exc:
            self.logger.error(
                "Delete of command on host(id=%s) failed: %s" % (coh_id, str(exc))
            )
            session.rollback()
            session.close()
            return False

    def _deleteCommands(self, session, cmds):
        """
        Deletes a command with all related sub-elements.

        @param cmd_id: Commands id
        @type cmd_id: int
        """
        for cmd in cmds.all():
            cohs = session.query(CommandsOnHost)
            cohs = cohs.select_from(self.commands_on_host)
            cohs = cohs.filter(self.commands_on_host.c.fk_commands == cmd.id)

            ok = self._deleteCommandsOnHost(session, cohs)
            if ok:
                session.delete(cmd)
                session.flush()
                self.logger.info("Command (id=%s) successfully deleted" % (cmd.id))

            else:
                self.logger.warn(
                    "Unable to delete commands on host of command (id=%s)" % cmd.id
                )
                return False

        return True

    def _deleteCommandsOnHost(self, session, cohs):
        """
        Deletes a command with all related sub-elements.

        @param cohs: Commands hon Host
        @type cohs: query list
        """
        for coh in cohs.all():
            session.delete(coh)
            session.flush()

            targets = session.query(Target)
            targets = targets.select_from(self.target)
            targets = targets.filter(self.target.c.id == coh.fk_target)

            for target in targets.all():
                session.delete(target)
                session.flush()

            phases = session.query(CommandsOnHostPhase)
            phases = phases.select_from(self.commands_on_host_phase)
            phases = phases.filter(
                self.commands_on_host_phase.c.fk_commands_on_host == coh.id
            )

            for phase in phases.all():
                session.delete(phase)
                session.flush()

            hists = session.query(CommandsHistory)
            hists = hists.select_from(self.commands_history)
            hists = hists.filter(self.commands_history.c.fk_commands_on_host == coh.id)

            for hist in hists.all():
                session.delete(hist)
                session.flush()

            session.delete(coh)
            session.flush()

        return True

    def extendCommand(self, cmd_id, start_date, end_date):
        """
        Custom command re-scheduling.

        @param cmd_id: Commands id
        @type cmd_id: int

        @param start_date: new start date of command
        @type start_date: str

        @param end_date: new end date of command
        @type end_date: str
        """
        session = create_session()
        cmd = session.query(Commands).get(cmd_id)
        if cmd:
            cmd.start_date = start_date
            cmd.end_date = end_date
            cmd.sum_running = cmd.sum_failed
            cmd.sum_failed = 0
            session.add(cmd)
            session.flush()

            self._extendCommandsOnHost(session, cmd_id, start_date, end_date)
            self.logger.info(
                "msc: re-scheduling command id = <%s> from %s to %s"
                % (cmd_id, start_date, end_date)
            )

        session.close()

    def _extendCommandsOnHost(self, session, cmd_id, start_date, end_date):
        """
        Update of all commands on host attached on updated command.

        @param cmd_id: Commands id
        @type cmd_id: int

        @param start_date: new start date of command_on_host
        @type start_date: str

        @param end_date: new end date of command_on_host
        @type end_date: str
        """
        query = session.query(CommandsOnHost)
        query = query.select_from(self.commands_on_host)
        query = query.filter(self.commands_on_host.c.fk_commands == cmd_id)
        query = query.filter(self.commands_on_host.c.current_state != "done")
        for coh in query.all():
            coh.start_date = start_date
            coh.end_date = end_date
            coh.next_launch_date = start_date
            coh.attempts_failed = 0
            coh.current_state = "scheduled"
            session.add(coh)
            session.flush()

    def _createPhases(
        self,
        session,
        cohs,
        do_imaging_menu,
        do_wol,
        files,
        start_script,
        clean_on_success,
        do_inventory,
        do_halt,
        do_reboot,
        do_windows_update,
        is_quick_action=False,
    ):
        wf_list = [
            "pre_menu",
            "wol",
            "post_menu",
            "upload",
            "execute",
            "wu_parse",
            "delete",
            "inventory",
            "reboot",
            "halt",
            "done",
        ]

        if isinstance(cohs, int):
            cohs = [cohs]
        elif isinstance(cohs, list):
            pass
        else:
            raise TypeError("list or int type required")
        phases_values = []
        for coh in cohs:
            order = 0

            for name in wf_list:
                if name == "pre_menu" and do_imaging_menu == "disable":
                    continue
                if name == "post_menu" and do_imaging_menu == "disable":
                    continue
                if name == "wol" and do_wol == "disable":
                    continue
                if name == "upload" and not files:
                    continue
                if (
                    name == "execute"
                    and (start_script == "disable" or is_quick_action)
                    and do_windows_update == "disable"
                ):
                    continue
                if name == "wu_parse" and do_windows_update == "disable":
                    continue
                if name == "delete" and (
                    clean_on_success == "disable" or is_quick_action
                ):
                    continue
                if name == "inventory" and do_inventory == "disable":
                    continue
                if name == "reboot" and do_reboot == "disable":
                    continue
                if name == "halt" and do_halt == "disable":
                    continue

                phases_values.append(
                    {"fk_commands_on_host": coh.id, "phase_order": order, "name": name}
                )

                order += 1

        session.execute(self.commands_on_host_phase.insert(), phases_values)

    def createCommandsOnHost(
        self,
        command,
        target,
        target_id,
        target_name,
        cmd_max_connection_attempt,
        start_date,
        end_date,
        scheduler=None,
        order_in_proxy=None,
        max_clients_per_proxy=0,
    ):
        logging.getLogger().debug("Create new command on host '%s'" % target_name)
        return {
            "host": target_name,
            "start_date": start_date,
            "end_date": end_date,
            "next_launch_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_state": "scheduled",
            "uploaded": "TODO",
            "executed": "TODO",
            "deleted": "TODO",
            "attempts_left": cmd_max_connection_attempt,
            "next_attempt_date_time": 0,
            "scheduler": scheduler,
            "order_in_proxy": order_in_proxy,
            "max_clients_per_proxy": max_clients_per_proxy,
            "fk_target": target_id,
            "fk_commands": command,
        }

    def createTarget(
        self,
        targetName,
        targetUuid,
        targetIp,
        targetMac,
        targetBCast,
        targetNetmask,
        mirror,
        groupID=None,
    ):
        """
        Inject a new Target object in our MSC database
        Return the corresponding Target object
        """
        target = {
            "target_name": targetName,
            "target_uuid": targetUuid,
            "target_ipaddr": targetIp,
            "target_macaddr": targetMac,
            "target_bcast": targetBCast,
            "target_network": targetNetmask,
            "mirrors": mirror,
            "id_group": groupID,
        }
        return target

    def getCommandsonhostsAndSchedulersOnBundle(self, fk_bundle):
        """ """
        conn = self.getDbConnection()
        c_ids = select(
            [self.commands.c.id], self.commands.c.fk_bundle == fk_bundle
        ).execute()
        c_ids = [x[0] for x in c_ids]
        result = select(
            [self.commands_on_host.c.id, self.commands_on_host.c.scheduler],
            self.commands_on_host.c.fk_commands.in_(c_ids),
        ).execute()
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
        result = select(
            [self.commands_on_host.c.id, self.commands_on_host.c.scheduler],
            self.commands_on_host.c.fk_commands == c_id,
        ).execute()
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
        if ctx.filterType == "mine":
            # User just want to get her/his commands
            return self.commands.c.creator == ctx.userid
        elif ctx.filterType == "all":
            # User want to get all commands she/he has the right to see
            if ctx.userid == "root":
                # root can see everything, so no filter for root
                return True
            elif ctx.locationsCount not in [None, 0, 1] and ctx.userids:
                # We have multiple locations, and a list of userids sharing the
                # same locations of the current user
                userids = ctx.userids
                # If show root commands is activated, we add it
                if self.config.show_root_commands:
                    userids.append("root")
                return self.commands.c.creator.in_(userids)
        else:
            # Unknown filter type
            self.logger.debug("Unknown filter type when querying commands")
            if ctx.locationsCount not in [None, 0, 1]:
                # We have multiple locations (entities) in database, so we
                # filter the results using the current userid
                return self.commands.c.creator == ctx.userid
        return True

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
                userids = ctx.userids
                # If show root commands is activated, we add it
                if self.config.show_root_commands:
                    userids.append("root")
                q = q.filter(self.commands.c.creator.in_(userids))
            # else if we have just one location, we don't apply any filter. The
            #     user can see the commands of all users

        else:
            # Unknown filter type
            self.logger.debug("Unknown filter type when querying commands")
            if ctx.locationsCount not in [None, 0, 1]:
                # We have multiple locations (entities) in database, so we
                # filter the results using the current userid
                q = q.filter(self.commands.c.creator == ctx.userid)
        return q

    def __queryAllCommandsonhostBy(self, session, ctx):
        """
        Built a part of the query for the *AllCommandsonhost* methods
        """

        join = (
            self.commands_on_host.join(self.commands)
            .join(self.target)
            .outerjoin(self.bundle)
        )
        q = session.query(CommandsOnHost, Commands, Target, Bundle)
        q = q.select_from(join)
        q = self.__queryUsersFilter(ctx, q)
        return q

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def getAllCommandsonhostCurrentstate(self, ctx):
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        ret = (
            ret.add_column(self.commands.c.max_connection_attempt)
            .filter(self.commands_on_host.c.current_state != "")
            .group_by(self.commands_on_host.c.current_state)
            .group_by(self.commands_on_host.c.attempts_left)
            .group_by(self.commands.c.max_connection_attempt)
            .order_by(asc(self.commands_on_host.c.next_launch_date))
        )
        # x[0] contains a commands_on_host object x[1] contains commands
        l = []
        for (
            x
        ) in ret.all():  # patch to have rescheduled as a "state" ... must be emulated
            if (
                x[0].current_state == "scheduled"
                and x[0].attempts_left != x[1].max_connection_attempt
                and "rescheduled" not in l
            ):
                l.append("rescheduled")
            elif not x[0].current_state in l:
                l.append(x[0].current_state)
        session.close()
        return l

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def countAllCommandsonhostByCurrentstate(self, ctx, current_state, filt=""):
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        if (
            current_state == "rescheduled"
        ):  # patch to have rescheduled as a "state" ... must be emulated
            ret = ret.filter(
                and_(
                    self.commands.c.max_connection_attempt
                    != self.commands_on_host.c.attempts_left,
                    self.commands_on_host.c.current_state == "scheduled",
                )
            )
        elif current_state == "scheduled":
            ret = ret.filter(
                and_(
                    self.commands.c.max_connection_attempt
                    == self.commands_on_host.c.attempts_left,
                    self.commands_on_host.c.current_state == "scheduled",
                )
            )
        else:
            ret = ret.filter(self.commands_on_host.c.current_state == current_state)
        # the join in itself is useless here, but we want to have exactly
        # the same result as in getAllCommandsonhostByCurrentstate
        if filt != "":
            ret = ret.filter(
                or_(
                    self.commands_on_host.c.host.like("%" + filt + "%"),
                    self.commands.c.title.like("%" + filt + "%"),
                )
            )
        c = ret.count()
        session.close()
        return c

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def getAllCommandsonhostByCurrentstate(
        self, ctx, current_state, min=0, max=10, filt=""
    ):
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        if (
            current_state == "rescheduled"
        ):  # patch to have rescheduled as a "state" ... must be emulated
            ret = ret.filter(
                and_(
                    self.commands.c.max_connection_attempt
                    != self.commands_on_host.c.attempts_left,
                    self.commands_on_host.c.current_state == "scheduled",
                )
            )
        elif current_state == "scheduled":
            ret = ret.filter(
                and_(
                    self.commands.c.max_connection_attempt
                    == self.commands_on_host.c.attempts_left,
                    self.commands_on_host.c.current_state == "scheduled",
                )
            )
        else:
            ret = ret.filter(self.commands_on_host.c.current_state == current_state)
        if filt != "":
            ret = ret.filter(
                or_(
                    self.commands_on_host.c.host.like("%" + filt + "%"),
                    self.commands.c.title.like("%" + filt + "%"),
                )
            )
        ret = ret.order_by(desc(self.commands_on_host.c.id))
        ret = ret.offset(int(min))
        ret = ret.limit(int(max) - int(min))
        l = []
        for x in ret.all():
            bundle = x[3]
            if bundle is not None:
                bundle = bundle.toH()
            l.append([x[0].toH(), x[1].toH(), x[2].toH(), bundle])
        session.close()
        return l

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def countAllCommandsonhostByType(self, ctx, type, filt=""):
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        if filt != "":
            ret = ret.filter(
                or_(
                    self.commands_on_host.c.host.like("%" + filt + "%"),
                    self.commands.c.title.like("%" + filt + "%"),
                )
            )
        if int(type) == 0:  # all
            pass
        elif int(type) == 1:  # pending
            ret = ret.filter(
                self.commands_on_host.c.current_state.in_(
                    (
                        "upload_failed",
                        "execution_failed",
                        "delete_failed",
                        "inventory_failed",
                        "not_reachable",
                        "pause",
                        "stop",
                        "stopped",
                        "scheduled",
                    )
                )
            )
        elif int(type) == 2:  # running
            ret = ret.filter(
                self.commands_on_host.c.current_state.in_(
                    (
                        "upload_in_progress",
                        "upload_done",
                        "execution_in_progress",
                        "execution_done",
                        "delete_in_progress",
                        "delete_done",
                        "inventory_in_progress",
                        "inventory_done",
                    )
                )
            )
        elif int(type) == 3:  # finished
            ret = ret.filter(
                self.commands_on_host.c.current_state.in_(
                    ("done", "failed", "over_timed")
                )
            )
        c = ret.count()
        session.close()
        return c

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def getAllCommandsonhostByType(self, ctx, type, min, max, filt=""):
        session = create_session()
        ret = self.__queryAllCommandsonhostBy(session, ctx)
        if filt != "":
            ret = ret.filter(
                or_(
                    self.commands_on_host.c.host.like("%" + filt + "%"),
                    self.commands.c.title.like("%" + filt + "%"),
                )
            )
        if int(type) == 0:  # all
            pass
        elif int(type) == 1:  # pending
            ret = ret.filter(
                self.commands_on_host.c.current_state.in_(
                    (
                        "upload_failed",
                        "execution_failed",
                        "delete_failed",
                        "inventory_failed",
                        "not_reachable",
                        "pause",
                        "stop",
                        "stopped",
                        "scheduled",
                    )
                )
            )
        elif int(type) == 2:  # running
            ret = ret.filter(
                self.commands_on_host.c.current_state.in_(
                    (
                        "upload_in_progress",
                        "upload_done",
                        "execution_in_progress",
                        "execution_done",
                        "delete_in_progress",
                        "delete_done",
                        "inventory_in_progress",
                        "inventory_done",
                    )
                )
            )
        elif int(type) == 3:  # finished
            ret = ret.filter(
                self.commands_on_host.c.current_state.in_(
                    ("done", "failed", "over_timed")
                )
            )
        ret = ret.order_by(desc(self.commands_on_host.c.id))
        ret = ret.offset(int(min))
        ret = ret.limit(int(max) - int(min))
        l = []
        for x in ret.all():
            bundle = x[3]
            if bundle is not None:
                bundle = bundle.toH()
            l.append([x[0].toH(), x[1].toH(), x[2].toH(), bundle])
        session.close()
        return l

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def countAllCommandsOnHostBundle(self, ctx, uuid, fk_bundle, filt, history):
        session = create_session()
        ret = (
            session.query(CommandsOnHost)
            .select_from(self.commands_on_host.join(self.commands).join(self.target))
            .filter(self.target.c.target_uuid == uuid)
            .filter(self.commands.c.creator == ctx.userid)
            .filter(self.commands.c.fk_bundle == fk_bundle)
        )
        #        ret = ret.filter(self.commands_on_host.c.id == self.target.c.fk_commands_on_host)
        if filt != "":
            ret = ret.filter(self.commands.c.title.like("%" + filt + "%"))
        if history:
            ret = ret.filter(self.commands_on_host.c.current_state == "done")
        else:
            ret = ret.filter(self.commands_on_host.c.current_state != "done")
        c = ret.count()
        session.close()
        return c

    def countAllCommandsOnHost(self, ctx, uuid, filt):
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx, uuid):
            session = create_session()
            ret = (
                session.query(CommandsOnHost)
                .select_from(
                    self.commands_on_host.join(self.commands).join(self.target)
                )
                .filter(self.target.c.target_uuid == uuid)
            )
            # .filter(self.commands.c.creator == ctx.userid)
            if filt != "":
                ret = ret.filter(self.commands.c.title.like("%" + filt + "%"))
            c = ret.count()
            session.close()
            return c
        self.logger.warn(
            "User %s does not have good permissions to access '%s'" % (ctx.userid, uuid)
        )
        return False

    def getAllCommandsOnHost(self, ctx, uuid, min, max, filt):
        if ComputerLocationManager().doesUserHaveAccessToMachine(ctx, uuid):
            session = create_session()
            query = (
                session.query(Commands)
                .add_column(self.commands_on_host.c.id)
                .add_column(self.commands_on_host.c.current_state)
            )
            query = query.select_from(
                self.commands.join(self.commands_on_host).join(self.target)
            ).filter(self.target.c.target_uuid == uuid)
            # .filter(self.commands.c.creator == ctx.userid)
            if filt != "":
                query = query.filter(self.commands.c.title.like("%" + filt + "%"))
            query = query.order_by(asc(self.commands_on_host.c.next_launch_date))
            query = query.offset(int(min))
            query = query.limit(int(max) - int(min))
            ret = query.all()
            session.close()
            return [(x[0].toH(), x[1], x[2]) for x in ret]
        self.logger.warn(
            "User %s does not have good permissions to access '%s'" % (ctx.userid, uuid)
        )
        return []

    def getAllCommandsConsult(self, ctx, min, max, filt, expired=True):
        nowsystem = time.strftime("%Y-%m-%d %H:%M:%S")
        session = create_session()

        # ====== GENERATING FILTERS ============================

        # User context filter
        filters = self.__queryUsersFilterBis(ctx)
        # search text Filtering

        if filt:
            filters = and_(
                filters,
                or_(
                    self.commands.c.title.like("%%%s%%" % (filt)),
                    self.commands.c.creator.like("%%%s%%" % (filt)),
                    self.commands.c.start_date.like("%%%s%%" % (filt)),
                    self.bundle.c.title.like("%%%s%%" % (filt)),
                    self.target.c.target_name.like("%%%s%%" % (filt)),
                ),
            )

        # Bundle join filtering
        # filters = filters & (self.commands.c.fk_bundle == self.bundle.c.id)

        if expired:
            filters = and_(filters, (self.commands.c.end_date <= nowsystem))
        else:
            filters = and_(filters, (self.commands.c.end_date > nowsystem))

        # Adding command type filtering
        # Show default commands type=0 and convegence commands type=2
        filters = and_(filters, (self.commands.c.type.in_([0, 2])))

        # ====== CALCULATING COUNT ============================

        query = session.query(func.count(distinct(Commands.id)))
        query = query.select_from(
            self.commands.join(
                self.commands_on_host,
                self.commands_on_host.c.fk_commands == self.commands.c.id,
            )
            .join(self.target, self.commands_on_host.c.fk_target == self.target.c.id)
            .outerjoin(self.bundle, self.commands.c.fk_bundle == self.bundle.c.id)
        )
        # Filtering on filters
        query = query.filter(filters)
        # Grouping bundle commands by fk_bundle only if fk_bundle is not null
        # So we generate random md5 hash for command that have null fk_bundle
        query = query.group_by(
            func.ifnull(self.commands.c.fk_bundle, func.md5(self.commands.c.id))
        )
        size = len(query.all())

        # ====== MAIN QUERY ============================
        query = session.query(Commands)
        query = (
            query.add_column(self.commands.c.fk_bundle)
            .add_column(self.commands_on_host.c.host)
            .add_column(self.commands_on_host.c.id)
        )
        query = (
            query.add_column(self.target.c.id_group)
            .add_column(self.bundle.c.title)
            .add_column(self.target.c.target_uuid)
        )
        query = query.add_column(self.pull_targets.c.target_uuid)
        query = query.select_from(
            self.commands.join(
                self.commands_on_host,
                self.commands_on_host.c.fk_commands == self.commands.c.id,
            )
            .join(self.target, self.commands_on_host.c.fk_target == self.target.c.id)
            .outerjoin(self.bundle, self.commands.c.fk_bundle == self.bundle.c.id)
        ).outerjoin(
            self.pull_targets,
            self.target.c.target_uuid == self.pull_targets.c.target_uuid,
        )
        # Filtering on filters
        query = query.filter(filters)
        # Grouping bundle commands by fk_bundle only if fk_bundle is not null
        # So we generate random md5 hash for command that have null fk_bundle
        query = query.group_by(
            func.ifnull(self.commands.c.fk_bundle, func.md5(self.commands.c.id))
        )  # .group_by(self.commands.c.id)
        query = query.order_by(desc(self.commands.c.id))
        # Limit result
        cmds = query.offset(int(min)).limit(int(max) - int(min)).all()

        session.close()

        ret = []
        for (
            cmd,
            bid,
            target_name,
            cohid,
            gid,
            btitle,
            target_uuid,
            machine_pull,
        ) in cmds:
            if bid is not None:  # we are in a bundle
                if gid is not None and gid != "":
                    ret.append(
                        {
                            "title": btitle,
                            "creator": cmd.creator,
                            "creation_date": cmd.creation_date,
                            "start_date": cmd.start_date,
                            "end_date": cmd.end_date,
                            "sum_running": cmd.sum_running,
                            "sum_failed": cmd.sum_failed,
                            "sum_done": cmd.sum_done,
                            "sum_stopped": cmd.sum_stopped,
                            "sum_overtimed": cmd.sum_overtimed,
                            "bid": bid,
                            "cmdid": "",
                            "target": "group %s" % gid,
                            "gid": gid,
                            "uuid": "",
                            "machine_pull": machine_pull,
                            "deployment_intervals": cmd.deployment_intervals,
                        }
                    )
                else:
                    ret.append(
                        {
                            "title": btitle,
                            "creator": cmd.creator,
                            "creation_date": cmd.creation_date,
                            "start_date": cmd.start_date,
                            "end_date": cmd.end_date,
                            "sum_running": cmd.sum_running,
                            "sum_failed": cmd.sum_failed,
                            "sum_done": cmd.sum_done,
                            "sum_stopped": cmd.sum_stopped,
                            "sum_overtimed": cmd.sum_overtimed,
                            "bid": bid,
                            "cmdid": "",
                            "target": target_name,
                            "uuid": target_uuid,
                            "machine_pull": machine_pull,
                            "gid": "",
                            "deployment_intervals": cmd.deployment_intervals,
                        }
                    )
            else:  # we are not in a bundle
                if gid is not None and gid != "":
                    ret.append(
                        {
                            "title": cmd.title,
                            "creator": cmd.creator,
                            "creation_date": cmd.creation_date,
                            "start_date": cmd.start_date,
                            "end_date": cmd.end_date,
                            "sum_running": cmd.sum_running,
                            "sum_failed": cmd.sum_failed,
                            "sum_done": cmd.sum_done,
                            "sum_stopped": cmd.sum_stopped,
                            "sum_overtimed": cmd.sum_overtimed,
                            "bid": "",
                            "cmdid": cmd.id,
                            "target": "group %s" % gid,
                            "gid": gid,
                            "uuid": "",
                            "machine_pull": machine_pull,
                            "deployment_intervals": cmd.deployment_intervals,
                            "type": cmd.type,
                        }
                    )
                else:
                    ret.append(
                        {
                            "title": cmd.title,
                            "creator": cmd.creator,
                            "creation_date": cmd.creation_date,
                            "start_date": cmd.start_date,
                            "end_date": cmd.end_date,
                            "sum_running": cmd.sum_running,
                            "sum_failed": cmd.sum_failed,
                            "sum_done": cmd.sum_done,
                            "sum_stopped": cmd.sum_stopped,
                            "sum_overtimed": cmd.sum_overtimed,
                            "bid": "",
                            "cmdid": cmd.id,
                            "cohid": cohid,
                            "target": target_name,
                            "uuid": target_uuid,
                            "machine_pull": machine_pull,
                            "gid": "",
                            "status": {},
                            "deployment_intervals": cmd.deployment_intervals,
                            "type": cmd.type,
                        }
                    )

        return [size, ret]

    ###################
    def __displayLogsQuery(self, ctx, params, session):
        nowsystem = time.strftime("%Y-%m-%d %H:%M:%S")
        query = session.query(Commands).select_from(
            self.commands.join(self.commands_on_host).join(self.target)
        )
        if params["gid"] is not None:
            query = query.filter(self.target.c.id_group == params["gid"])
        if params["uuid"] is not None:
            query = query.filter(self.target.c.target_uuid == params["uuid"])
        if params["filt"] is not None:
            query = query.filter(self.commands.c.title.like("%" + params["filt"] + "%"))
        # if params['finished']:
        #    query = query.filter(self.commands_on_host.c.current_state.in_(['done', 'failed', 'over_timed']))
        else:
            # If we are querying on a bundle, we also want to display the
            # commands_on_host flagged as done
            # if params['b_id'] == None:
            #    query = query.filter(not_(self.commands_on_host.c.current_state.in_(['done', 'failed', 'over_timed'])))
            pass
        query = self.__queryUsersFilter(ctx, query)

        # Finished param
        if "finished" in params and params["finished"] == "1":
            query = query.filter(self.commands.c.end_date <= nowsystem)
        elif "finished" in params and params["finished"] == "0":
            query = query.filter(self.commands.c.end_date > nowsystem)

        return query.group_by(self.commands.c.id).order_by(desc(params["order_by"]))

    def __doneBundle(self, params, session):
        query = session.query(Commands).select_from(
            self.commands.join(self.commands_on_host)
        )
        filter = []
        if params["b_id"] is not None:
            filter = [self.commands.c.fk_bundle == params["b_id"]]
        elif params["cmd_id"] is not None:
            filter = [self.commands.c.id == params["cmd_id"]]
        # filter.append(not_(self.commands_on_host.c.current_state.in_(['done', 'failed', 'over_timed'])))
        query = query.filter(and_(*filter))
        how_much = query.count()
        if how_much > 0:
            return False
        return True

    def __displayLogsQuery2(self, ctx, params, session, count=False):
        nowsystem = time.strftime("%Y-%m-%d %H:%M:%S")
        filter = []
        group_by = False
        group_clause = False

        # Get query parts
        if count:
            query = session.query(func.count("*")).select_from(
                self.commands.join(self.commands_on_host).join(self.target)
            )
        else:
            query = session.query(Commands).select_from(
                self.commands.join(self.commands_on_host)
                .join(self.target)
                .outerjoin(
                    self.pull_targets,
                    self.pull_targets.c.target_uuid == self.target.c.target_uuid,
                )
            )
            query = (
                query.add_column(self.commands_on_host.c.id)
                .add_column(self.commands_on_host.c.current_state)
                .add_column(PullTargets.target_uuid)
            )

        if params["cmd_id"] is not None:  # COH
            filter = [self.commands.c.id == params["cmd_id"]]
            if params["b_id"] is not None:
                filter.append(self.commands.c.fk_bundle == params["b_id"])
        else:  # CMD
            if params["b_id"] is not None:
                filter = [self.commands.c.fk_bundle == params["b_id"]]
            group_by = True
            group_clause = self.commands.c.id

        if params["gid"] is not None:  # Filter on a machines group id
            filter.append(self.target.c.id_group == params["gid"])

        if params["uuid"] is not None:  # Filter on a machine uuid
            filter.append(self.target.c.target_uuid == params["uuid"])

        if params["filt"] is not None:  # Filter on a commande names
            filter.append(
                self.commands.c.title.like("%s%s%s" % ("%", params["filt"], "%"))
                | self.target.c.target_name.like("%s%s%s" % ("%", params["filt"], "%"))
            )

        # Finished param
        if "finished" in params and params["finished"] == "1":
            filter.append(self.commands.c.end_date <= nowsystem)
        elif "finished" in params and params["finished"] == "0":
            filter.append(self.commands.c.end_date > nowsystem)

        # Filtering on COH State
        if "state" in params and params["state"]:
            filter.append(self.commands_on_host.c.current_state.in_(params["state"]))

        # if params['b_id'] == None:
        #    is_done = self.__doneBundle(params, session)
        # if params['finished'] and not is_done: # Filter on finished commands only
        #    filter.append(1 == 0) # send nothing
        # elif not params['finished'] and is_done:
        # If we are querying on a bundle, we also want to display the
        # commands_on_host flagged as done
        #    filter.append(1 == 0) # send nothing
        #        else:
        #            is_done = self.__doneBundle(params, session)
        #            self.logger.debug("is the bundle done ? %s"%(str(is_done)))

        query = self.__queryUsersFilter(ctx, query)
        query = query.filter(and_(*filter))

        if group_by:
            query = query.group_by(group_clause)

        if not count:
            return query
        else:
            return query.all()[0][0]

    def __displayLogsQueryGetIds(self, cmds, min=0, max=-1, params={}):
        i = 0
        min = int(min)
        max = int(max)
        ids = []
        defined = {}
        for cmd in cmds:
            id, fk_bundle = cmd
            if max != -1 and max - 1 < i:
                break
            if i < min:
                if (
                    fk_bundle != "NULL"
                    and fk_bundle is not None
                    and fk_bundle not in defined
                ):
                    defined[fk_bundle] = id
                    i += 1
                elif fk_bundle == "NULL" or fk_bundle is None:
                    i += 1
                continue
            if (
                fk_bundle != "NULL"
                and fk_bundle is not None
                and fk_bundle not in defined
            ):
                defined[fk_bundle] = id
                ids.append(id)
                i += 1
            elif fk_bundle == "NULL" or fk_bundle is None:
                ids.append(id)
                i += 1
        return ids

    def __displayLogReturn(self, ctx, list):
        # list is : cmd, cohid, cohstate
        cohids = [x[1] for x in list]
        cohs = self.getCommandsOnHosts(ctx, cohids)
        ret = []
        for element in list:
            if element[1] in cohs:
                if len(element) == 4:
                    ret.append(
                        (
                            element[0].toH(),
                            element[1],
                            element[2],
                            cohs[element[1]].toH(),
                            element[3],
                        )
                    )
                else:
                    ret.append(
                        (
                            element[0].toH(),
                            element[1],
                            element[2],
                            cohs[element[1]].toH(),
                        )
                    )
            else:
                ret.append((element[0].toH(), element[1], element[2], False))
        return ret

    def checkLightPullCommands(self, uuid):
        """
        Returns all coh ids te re-execute.

        @param uuid: uuid of checked computer
        @type uuid: str

        @return: coh ids to start
        @rtype: list
        """
        session = create_session()

        query = session.query(CommandsOnHost)
        query = query.select_from(
            self.commands.join(self.commands_on_host).join(self.target)
        )
        query = query.filter(self.target.c.target_uuid == uuid)
        query = query.filter(self.commands_on_host.c.current_state == "scheduled")

        ret = [q.id for q in query.all()]

        session.close()

        return ret

    def displayLogs(self, ctx, params=None):  # TODO USE ctx
        if params is None:  # do not change the default value!
            params = {}
        session = create_session()
        for i in ("b_id", "cmd_id", "coh_id", "gid", "uuid", "filt"):
            if i not in params or params[i] == "":
                params[i] = None
        if "min" not in params:
            params["min"] = 0
        if "max" not in params:
            params["max"] = -1
        # if not params.has_key('finished') or params['finished'] == '':
        #    params['finished'] = False
        try:
            params["order_by"] = getattr(self.commands_on_host.c, params["order_by"])
        except BaseException:
            params["order_by"] = getattr(self.commands_on_host.c, "id")

        size = 0

        #   msc.displayLogs({'max': 10, 'finished': '', 'filt': '', 'uuid': 'UUID1620', 'min': 0},)
        if (
            params["gid"] or params["uuid"]
        ):  # we want informations about one group / host
            # we want informations about one command on one group / host
            if params["cmd_id"]:
                # Using min/max, we get a range of commands, but we always want
                # the total count of commands.
                ret = (
                    self.__displayLogsQuery2(ctx, params, session)
                    .offset(int(params["min"]))
                    .limit(int(params["max"]) - int(params["min"]))
                    .all()
                )
                size = self.__displayLogsQuery2(ctx, params, session, True)
                session.close()
                return size, self.__displayLogReturn(ctx, ret)
            # we want informations about one bundle on one group / host
            elif params["b_id"]:
                # Using min/max, we get a range of commands, but we always want
                # the total count of commands.
                ret = (
                    self.__displayLogsQuery2(ctx, params, session)
                    .order_by(self.commands.c.order_in_bundle)
                    .offset(int(params["min"]))
                    .limit(int(params["max"]) - int(params["min"]))
                    .all()
                )
                size = self.__displayLogsQuery2(ctx, params, session, True)
                session.close()
                return size, self.__displayLogReturn(ctx, ret)
            else:  # we want all informations about on one group / host
                # Get all commands related to the given computer UUID or group
                # id
                ret = (
                    self.__displayLogsQuery(ctx, params, session)
                    .order_by(asc(params["order_by"]))
                    .all()
                )
                cmds = []
                for c in ret:
                    cmds.append((c.id, c.fk_bundle))

                size = []
                size.extend(cmds)
                size = len(self.__displayLogsQueryGetIds(size, params=params))

                ids = self.__displayLogsQueryGetIds(
                    cmds, params["min"], params["max"], params
                )

                query = session.query(Commands).select_from(
                    self.commands.join(self.commands_on_host).join(self.target)
                )
                query = query.add_column(self.commands_on_host.c.id).add_column(
                    self.commands_on_host.c.current_state
                )
                query = query.filter(self.commands.c.id.in_(ids))
                if params["uuid"]:
                    # Filter target according to the given UUID
                    query = query.filter(self.target.c.target_uuid == params["uuid"])
                query = query.order_by(desc(params["order_by"]))
                ret = query.group_by(self.commands.c.id).all()

                session.close()
                return size, self.__displayLogReturn(ctx, ret)
        else:  # we want all informations
            if params["cmd_id"]:  # we want all informations about one command
                ret = self.__displayLogsQuery2(ctx, params, session).all()
                # FIXME: using distinct, size will always return 1 ...
                size = self.__displayLogsQuery2(ctx, params, session, True)
                session.close()
                return size, self.__displayLogReturn(ctx, ret)
            elif params["b_id"]:  # we want all informations about one bundle
                ret = (
                    self.__displayLogsQuery2(ctx, params, session)
                    .order_by(self.commands.c.order_in_bundle)
                    .all()
                )
                # FIXME: using distinct, size will always return 1 ...
                size = self.__displayLogsQuery2(ctx, params, session, True)
                session.close()
                return size, self.__displayLogReturn(ctx, ret)
            else:  # we want all informations about everything
                ret = (
                    self.__displayLogsQuery(ctx, params, session)
                    .order_by(asc(params["order_by"]))
                    .all()
                )
                cmds = [(c.id, c.fk_bundle) for c in ret]

                size = []
                size.extend(cmds)
                size = len(self.__displayLogsQueryGetIds(size))

                ids = self.__displayLogsQueryGetIds(
                    cmds, params["min"], params["max"], params=params
                )

                query = session.query(Commands).select_from(
                    self.commands.join(self.commands_on_host).join(self.target)
                )
                query = query.add_column(self.commands_on_host.c.id).add_column(
                    self.commands_on_host.c.current_state
                )
                query = query.filter(self.commands.c.id.in_(ids))
                query = query.order_by(desc(params["order_by"]))
                ret = query.group_by(self.commands.c.id).all()

                session.close()
                return size, self.__displayLogReturn(ctx, ret)

    ###################
    def getCommandsOnHosts(self, ctx, coh_ids):
        session = create_session()
        cohs = (
            session.query(CommandsOnHost)
            .add_column(self.commands_on_host.c.id)
            .filter(self.commands_on_host.c.id.in_(coh_ids))
            .all()
        )
        session.close()
        targets = self.getTargetsForCoh(ctx, coh_ids)
        if ComputerLocationManager().doesUserHaveAccessToMachines(
            ctx, [t.target_uuid for t in targets], False
        ):
            ret = {}
            session = create_session()
            for e in cohs:
                # Loading coh phases
                e[0].phases = (
                    session.query(CommandsOnHostPhase)
                    .filter_by(fk_commands_on_host=e[1])
                    .all()
                )
                e[0].phases = [phase.toDict() for phase in e[0].phases]
                ret[e[1]] = e[0]
            session.close()
            return ret
        return {}

    def getCommandsOnHost(self, ctx, coh_id):
        session = create_session()
        coh = session.query(CommandsOnHost).get(coh_id)
        if coh is None:
            self.logger.warn(
                "User %s try to access an coh that don't exists '%s'"
                % (ctx.userid, coh_id)
            )
            return False
        coh.phases = (
            session.query(CommandsOnHostPhase)
            .filter_by(fk_commands_on_host=coh_id)
            .all()
        )
        coh.phases = [phase.toDict() for phase in coh.phases]
        session.close()
        target = self.getTargetForCoh(ctx, coh_id)
        if ComputerLocationManager().doesUserHaveAccessToMachine(
            ctx, target.target_uuid
        ):
            return coh
        self.logger.warn(
            "User %s does not have right permissions to access '%s'"
            % (ctx.userid, target.target_name)
        )
        return False

    def getTargetsForCoh(self, ctx, coh_ids):  # FIXME should we use the ctx
        session = create_session()
        targets = (
            session.query(Target)
            .select_from(self.target.join(self.commands_on_host))
            .filter(self.commands_on_host.c.id.in_(coh_ids))
            .all()
        )
        session.close()
        return targets

    def getTargetForCoh(self, ctx, coh_id):  # FIXME should we use the ctx
        # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        target = (
            session.query(Target)
            .select_from(self.target.join(self.commands_on_host))
            .filter(self.commands_on_host.c.id == coh_id)
            .first()
        )
        session.close()
        return target

    def getCommandsHistory(self, ctx, coh_id):  # FIXME should we use the ctx
        # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
        session = create_session()
        ret = (
            session.query(CommandsHistory)
            .filter(self.commands_history.c.fk_commands_on_host == coh_id)
            .all()
        )
        session.close()
        return [x.toH() for x in ret]

    # def getBundle(self, ctx, fk_bundle):
    # session = create_session()
    # try:
    # ret = session.query(Bundle).filter(self.bundle.c.id == fk_bundle).first().toH()
    # except:
    # self.logger.info("Bundle '%s' cant be retrieved by '%s'"%(fk_bundle, ctx.userid))
    # return [None, []]
    # try:
    # cmds = map(lambda a:a.toH(), session.query(Commands).filter(self.commands.c.fk_bundle == fk_bundle).order_by(self.commands.c.order_in_bundle).all())
    # except:
    # self.logger.info("Commands for bundle '%s' cant be retrieved by '%s'"%(fk_bundle, ctx.userid))
    # return [ret, []]
    # session.close()
    # try:
    # ret['creation_date'] = cmds[0]['creation_date']
    # except:
    # ret['creation_date'] = ''
    # return [ret, cmds]

    @DatabaseHelper._session
    def isCommandsCconvergenceType(self, session, ctx, cmd_id):
        if cmd_id is None or cmd_id == "":
            return False
        result = session.query(Commands).filter_by(id=cmd_id).one()
        return result.type

    @DatabaseHelper._session
    def isArrayCommandsCconvergenceType(self, session, ctx, arraycmd_id):
        result = {}
        for idcmd in arraycmd_id:
            result[idcmd] = 0
            try:
                ret = session.query(Commands.type).filter_by(id=idcmd).one()
                result[idcmd] = int(ret[0])
            except BaseException:
                pass
        return result

    @DatabaseHelper._session
    def getCommands(self, session, ctx, cmd_id):
        if cmd_id == "0" or cmd_id is None or cmd_id == "":
            return False
        a_targets = [target[0] for target in self.getTargets(cmd_id, True)]
        if ComputerLocationManager().doesUserHaveAccessToMachines(ctx, a_targets):

            def _update_command(command, phases):
                """
                New scheduler introduce phase table and some statuses are no longer
                updated in command table, but in phase table
                So, put these missing results in return
                """
                __statuses = {
                    "do_wol": "wol",
                    "clean_on_success": "delete",
                    "do_inventory": "inventory",
                    "do_reboot": "reboot",
                    "do_halt": "halt",
                    "do_windows_update": "windows_update",
                }
                # for step in ['do_wol', 'clean_on_success', 'do_inventory',
                # 'do_reboot', 'do_halt']:
                for step in list(__statuses.keys()):
                    setattr(
                        command,
                        step,
                        __statuses[step] in phases and "enable" or "disable",
                    )
                return command

            command, coh = (
                session.query(Commands)
                .filter_by(id=cmd_id)
                .add_entity(CommandsOnHost)
                .outerjoin((CommandsOnHost, Commands.id == CommandsOnHost.fk_commands))
                .first()
            )
            if coh is not None:
                phases = (
                    session.query(CommandsOnHostPhase)
                    .filter_by(fk_commands_on_host=coh.id)
                    .all()
                )
                phases = [phase.toDict()["name"] for phase in phases]
                # _update_command call for missing statuses
                return _update_command(command, phases)
            else:
                return command

        self.logger.warn(
            "User %s does not have good permissions to access command '%s'"
            % (ctx.userid, str(cmd_id))
        )
        return False

    def getCommandsByGroup1(self, gid):
        session = create_session()
        ret = (
            session.query(Commands)
            .select_from(self.commands.join(self.commands_on_host).join(self.target))
            .filter(self.target.c.id_group == gid)
        )
        ret = ret.order_by(desc(self.commands.c.start_date)).all()
        session.close()
        arraycommands_id = [c.id for c in ret]
        return arraycommands_id

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def getCommandsByGroup(self, gid):
        session = create_session()
        ret = (
            session.query(Commands)
            .select_from(self.commands.join(self.commands_on_host).join(self.target))
            .filter(self.target.c.id_group == gid)
        )
        ret = ret.order_by(desc(self.commands.c.start_date)).all()
        session.close()
        return ret

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def getTargetsByGroup(self, gid):
        session = create_session()
        ret = session.query(Target).filter(self.target.c.id_group == gid).all()
        session.close()
        return ret

    @DatabaseHelper._session
    def isPullTarget(self, session, uuid):
        try:
            session.query(PullTargets).filter(PullTargets.target_uuid == uuid).one()
            return True
        except NoResultFound:
            return False

    @DatabaseHelper._session
    def getPullTargets(self, session):
        query = session.query(PullTargets)
        return [uuid.target_uuid for uuid in query]

    @DatabaseHelper._session
    def removePullTargets(self, session, uuids):
        query = session.query(PullTargets).filter(PullTargets.target_uuid.in_(uuids))
        query.delete(synchronize_session="fetch")
        return True

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def getTargets(self, cmd_id, onlyId=False):
        if onlyId:
            connection = self.getDbConnection()
            ret = connection.execute(
                select(
                    [self.target.c.target_uuid],
                    and_(
                        self.commands_on_host.c.fk_commands == cmd_id,
                        self.target.c.id == self.commands_on_host.c.fk_target,
                    ),
                )
            ).fetchall()
        else:
            session = create_session()
            ret = (
                session.query(Target)
                .select_from(self.target.join(self.commands_on_host))
                .filter(self.commands_on_host.c.fk_commands == cmd_id)
                .all()
            )
            session.close()
        return ret

    def getCommandOnHostCurrentState(self, ctx, cmd_id):
        session = create_session()
        ret = (
            session.query(Commands)
            .add_column(self.commands_on_host.c.current_state)
            .select_from(self.commands.join(self.commands_on_host))
            .filter(self.commands.c.id == cmd_id)
            .first()
        )
        session.close()
        return ret[1]

    def getCommandOnHostTitle(self, ctx, cmd_id):
        session = create_session()
        ret = (
            session.query(Commands)
            .select_from(self.commands.join(self.commands_on_host))
            .filter(self.commands.c.id == cmd_id)
            .first()
        )
        session.close()
        return ret.title

    def getCommandOnHostInCommands(self, ctx, cmd_id):
        session = create_session()
        ret = (
            session.query(CommandsOnHost)
            .filter(self.commands_on_host.c.fk_commands == cmd_id)
            .all()
        )
        session.close()
        return [c.id for c in ret]

    def getstatbycmd(self, ctx, cmd_id):
        session = create_session()
        ret = (
            session.query(func.count(self.commands_on_host.c.current_state))
            .filter(self.commands_on_host.c.fk_commands == cmd_id)
            .scalar()
        )
        nbmachinegroupe = int(ret)
        ret = (
            session.query(
                func.count(self.commands_on_host.c.current_state), CommandsOnHost
            )
            .filter(
                and_(
                    self.commands_on_host.c.fk_commands == cmd_id,
                    self.commands_on_host.c.current_state == "done",
                )
            )
            .scalar()
        )
        nbdeploydone = int(ret)
        session.close()
        return {"nbmachine": nbmachinegroupe, "nbdeploydone": nbdeploydone}

    def getarraystatbycmd(self, ctx, arraycmd_id):
        result = {"nbmachine": {}}
        # result = {'nbmachine' : {}, 'nbdeploydone' : {}}
        session = create_session()
        ret = (
            session.query(
                CommandsOnHost.fk_commands.label("idcmd"),
                func.count(self.commands_on_host.c.current_state).label("nb"),
            )
            .filter(and_(self.commands_on_host.c.fk_commands.in_(arraycmd_id)))
            .group_by(self.commands_on_host.c.fk_commands)
        )
        ret.all()
        for x in ret:
            result["nbmachine"][x[0]] = x[1]

        # ret = session.query(CommandsOnHost.fk_commands.label("idcmd") ,
        # func.count(self.commands_on_host.c.current_state).label("nb")).\
        # filter(and_(self.commands_on_host.c.fk_commands.in_(arraycmd_id),
        # self.commands_on_host.c.current_state == "done")).\
        # group_by(self.commands_on_host.c.fk_commands)
        # ret.all()
        # for x in ret:
        # result['nbdeploydone'][x[0]]=x[1]
        return result

    def getFirstCommandsOncmd_id(self, ctx, cmd_id):
        session = create_session()
        ret = (
            session.query(CommandsOnHost)
            .filter(self.commands_on_host.c.fk_commands == cmd_id)
            .first()
        )
        session.close()
        return ret

    def _getarraycommanddatadate(self, arrayCommandsOnHostdata):
        ret = []
        listcmd = [x for x in arrayCommandsOnHostdata]
        for x in listcmd:
            t = {
                "fk_target": x[0],
                "startdate": x[1].strftime("%Y-%m-%d %H:%M:%S"),
                "enddate": x[2].strftime("%Y-%m-%d %H:%M:%S"),
                "next_launch_date": x[3].strftime("%Y-%m-%d %H:%M:%S")
                if x[3] is not None
                else "",
                "start_dateunixtime": time.mktime(x[1].timetuple()),
                "end_dateunixtime": time.mktime(x[2].timetuple()),
                "next_launch_dateunixtime": time.mktime(x[3].timetuple())
                if x[3] is not None
                else "",
            }
            ret.append(t)
        return ret

    def _getcommanddatadate(self, CommandsOnHostdata):
        start_dateunixtime = time.mktime(CommandsOnHostdata.start_date.timetuple())
        end_dateunixtime = time.mktime(CommandsOnHostdata.end_date.timetuple())
        next_launch_dateunixtime = time.mktime(
            CommandsOnHostdata.next_launch_date.timetuple()
        )
        if hasattr(CommandsOnHostdata, "package_id"):
            return {
                "start_dateunixtime": start_dateunixtime,
                "end_dateunixtime": end_dateunixtime,
                "next_launch_dateunixtime": next_launch_dateunixtime,
                "package_id": CommandsOnHostdata.package_id,
            }
        else:
            return {
                "start_dateunixtime": start_dateunixtime,
                "end_dateunixtime": end_dateunixtime,
                "next_launch_dateunixtime": next_launch_dateunixtime,
            }

    def _getcommanddata(self, CommandsOnHostdata):
        ret = {
            "uploaded": CommandsOnHostdata.uploaded,
            "next_attempt_date_time": CommandsOnHostdata.next_attempt_date_time,
            "deleted": CommandsOnHostdata.deleted,
            "imgmenu_changed": CommandsOnHostdata.imgmenu_changed,
            "halted": CommandsOnHostdata.halted,
            "host": CommandsOnHostdata.host,
            "attempts_left": CommandsOnHostdata.attempts_left,
            "scheduler": CommandsOnHostdata.scheduler,
            "fk_commands": CommandsOnHostdata.fk_commands,
            "fk_target": CommandsOnHostdata.fk_target,
            "stage": CommandsOnHostdata.stage,
            "last_wol_attempt": CommandsOnHostdata.last_wol_attempt,
            "rebooted": CommandsOnHostdata.rebooted,
            "executed": CommandsOnHostdata.executed,
            "inventoried": CommandsOnHostdata.inventoried,
            "awoken": CommandsOnHostdata.awoken,
            "max_clients_per_proxy": CommandsOnHostdata.max_clients_per_proxy,
            "id": CommandsOnHostdata.id,
            "order_in_proxy": CommandsOnHostdata.order_in_proxy,
            "phases": CommandsOnHostdata.phases,
            "end_date": CommandsOnHostdata.end_date,
            "current_launcher": CommandsOnHostdata.current_launcher,
            "start_date": CommandsOnHostdata.start_date,
            "next_launch_date": CommandsOnHostdata.next_launch_date,
            "current_state": CommandsOnHostdata.current_state,
            "fk_use_as_proxy": CommandsOnHostdata.fk_use_as_proxy,
        }
        return dict(ret, **self._getcommanddatadate(CommandsOnHostdata))

    def getLastCommandsOncmd_id(self, ctx, cmd_id):
        session = create_session()
        ret = (
            session.query(CommandsOnHost)
            .filter(self.commands_on_host.c.fk_commands == cmd_id)
            .order_by(desc(self.commands_on_host.c.id))
            .first()
        )
        session.close()
        return self._getcommanddata(ret)

    def getLastCommandsOncmd_id_start_end(self, ctx, cmd_id):
        session = create_session()
        ret = (
            session.query(
                CommandsOnHost.start_date,
                CommandsOnHost.end_date,
                CommandsOnHost.next_launch_date,
                Commands.package_id,
            )
            .join(Commands)
            .filter(self.commands_on_host.c.fk_commands == cmd_id)
            .order_by(desc(self.commands_on_host.c.id))
            .first()
        )
        session.close()
        return self._getcommanddatadate(ret)

    def getarrayLastCommandsOncmd_id_start_end(self, ctx, array_cmd_id):
        session = create_session()
        ret = (
            session.query(
                distinct(CommandsOnHost.fk_target),
                CommandsOnHost.start_date,
                CommandsOnHost.end_date,
                CommandsOnHost.next_launch_date,
            )
            .filter(self.commands_on_host.c.fk_commands.in_(array_cmd_id))
            .order_by(desc(self.commands_on_host.c.id))
            .all()
        )
        session.close()
        return self._getarraycommanddatadate(ret)

    def getCommandOnGroupByState(self, ctx, cmd_id, state, min=0, max=-1):
        session = create_session()
        query = (
            session.query(CommandsOnHost)
            .add_column(self.target.c.target_uuid)
            .select_from(self.commands_on_host.join(self.commands).join(self.target))
            .filter(self.commands.c.id == cmd_id)
            .order_by(self.commands_on_host.c.host)
        )
        ret = self.__filterOnStatus(ctx, query, state)
        session.close()
        if max != -1:
            ret = ret[min:max]
        return [
            {
                "coh_id": coh.id,
                "uuid": coh.target_uuid,
                "host": coh.host,
                "start_date": coh.start_date,
                "end_date": coh.end_date,
                "current_state": coh.current_state,
            }
            for coh in ret
        ]

    # TODO use ComputerLocationManager().doesUserHaveAccessToMachine
    def getCommandOnGroupStatus(self, ctx, cmd_id):
        session = create_session()
        query = (
            session.query(func.count(self.commands_on_host.c.id), CommandsOnHost)
            .select_from(self.commands_on_host.join(self.commands))
            .filter(self.commands.c.id == cmd_id)
        )
        ret = self.__getStatus(ctx, query)
        session.close()
        return ret

    def getMachineNamesOnGroupStatus(self, ctx, cmd_id, state, limit):
        session = create_session()
        query = (
            session.query(CommandsOnHost)
            .add_column(self.target.c.target_uuid)
            .select_from(self.commands_on_host.join(self.commands).join(self.target))
            .filter(self.commands.c.id == cmd_id)
        )
        if state in [
            "success",
            "paused",
            "stopped",
            "running",
            "failure",
        ]:  # Global statues
            query = query.filter(
                self.commands_on_host.c.current_state.in_(self.__getAllStatus()[state])
            )
        # Treat failed statues
        elif state == "fail_up":
            query = query.filter(self.commands_on_host.c.uploaded == "FAILED")
        elif state == "fail_ex":
            query = query.filter(self.commands_on_host.c.executed == "FAILED")
        elif state == "fail_rm":
            query = query.filter(self.commands_on_host.c.deleted == "FAILED")
        elif state == "fail_inv":
            query = query.filter(self.commands_on_host.c.inventoried == "FAILED")
        elif state == "fail_wol":
            query = query.filter(self.commands_on_host.c.awoken == "FAILED")
        elif state == "fail_reboot":
            query = query.filter(self.commands_on_host.c.rebooted == "FAILED")
        elif state == "fail_halt":
            query = query.filter(self.commands_on_host.c.halted == "FAILED")
        elif state == "over_timed":
            query = query.filter(self.commands_on_host.c.current_state == "over_timed")

        # Limit list according to max_elements_for_static_list param in
        # dyngroup.ini
        query.limit(limit)
        ret = [
            {"hostname": machine[0].host, "target_uuid": machine[1]}
            for machine in query
        ]
        session.close()
        return ret

    def getMachineNamesOnBundleStatus(self, ctx, fk_bundle, state, limit):
        session = create_session()
        query = (
            session.query(CommandsOnHost)
            .add_column(self.target.c.target_uuid)
            .select_from(self.commands_on_host.join(self.commands).join(self.target))
            .filter(self.commands.c.fk_bundle == fk_bundle)
        )
        if state in [
            "success",
            "paused",
            "stopped",
            "running",
            "failure",
        ]:  # Global statues
            query = query.filter(
                self.commands_on_host.c.current_state.in_(self.__getAllStatus()[state])
            )
        # Treat failed statues
        elif state == "fail_up":
            query = query.filter(self.commands_on_host.c.uploaded == "FAILED")
        elif state == "fail_ex":
            query = query.filter(self.commands_on_host.c.executed == "FAILED")
        elif state == "fail_rm":
            query = query.filter(self.commands_on_host.c.deleted == "FAILED")
        elif state == "fail_inv":
            query = query.filter(self.commands_on_host.c.inventoried == "FAILED")
        elif state == "fail_wol":
            query = query.filter(self.commands_on_host.c.awoken == "FAILED")
        elif state == "fail_reboot":
            query = query.filter(self.commands_on_host.c.rebooted == "FAILED")
        elif state == "fail_halt":
            query = query.filter(self.commands_on_host.c.halted == "FAILED")
        elif state == "over_timed":
            query = query.filter(self.commands_on_host.c.current_state == "over_timed")

        # Limit list according to max_elements_for_static_list param in
        # dyngroup.ini
        query.limit(limit)
        ret = [
            {"hostname": machine[0].host, "target_uuid": machine[1]}
            for machine in query
        ]
        session.close()
        return ret

    def getCommandOnBundleByState(self, ctx, fk_bundle, state, min=0, max=-1):
        session = create_session()
        query = (
            session.query(CommandsOnHost)
            .add_column(self.target.c.target_uuid)
            .select_from(self.commands_on_host.join(self.commands).join(self.target))
            .filter(self.commands.c.fk_bundle == fk_bundle)
            .order_by(self.commands_on_host.c.host)
        )
        ret = self.__filterOnStatus(ctx, query, state)
        session.close()
        if max != -1:
            ret = ret[min:max]
        return [
            {
                "coh_id": coh.id,
                "uuid": coh.target_uuid,
                "host": coh.host,
                "start_date": coh.start_date,
                "end_date": coh.end_date,
                "current_state": coh.current_state,
            }
            for coh in ret
        ]

    def getCommandOnBundleStatus(self, ctx, fk_bundle):
        session = create_session()
        query = (
            session.query(func.count(self.commands_on_host.c.id), CommandsOnHost)
            .select_from(self.commands_on_host.join(self.commands))
            .filter(self.commands.c.fk_bundle == fk_bundle)
        )
        ret = self.__getStatus(ctx, query)
        session.close()
        return ret

    def __putUUIDInCOH(self, coh, uuid):
        setattr(coh, "target_uuid", uuid)
        return coh

    def __filterOnStatus(self, ctx, query, state):
        query = [self.__putUUIDInCOH(x[0], x[1]) for x in query]
        ret = self.__getStatus(ctx, query, True)
        if state in ret:
            return ret[state]["total"][1]
        for l1 in ret:
            if state in ret[l1]:
                return ret[l1][state][1]
        return None

    def getStateCoh(self, query, filter):
        """
        Add filters to query and return a SQL count() of this query
        @param query: the query
        @type query: sqlalchemy query object
        @param filter: a list formated like this: [[field, state], [field, state], ...]
                        field is name of field in commands_on_host table
                        state is a list of possible states to filter on
        @type filter: list

        @return: SQL count()
        @rtype: int
        """
        for f in filter:
            if isinstance(f[1], str):  # f[1] must be a list
                f[1] = [f[1]]
            if len(f) == 3 and not f[2]:
                query = query.filter(
                    not_(getattr(self.commands_on_host.c, f[0]).in_(f[1]))
                )
            else:
                query = query.filter(getattr(self.commands_on_host.c, f[0]).in_(f[1]))

        return [machine[0] for machine in query]

    def getStateLen(self, query, filter):
        """
        Add filters to query and return a SQL count() of this query
        @param query: the query
        @type query: sqlalchemy query object
        @param filter: a list formated like this: [[field, state], [field, state], ...]
                        field is name of field in commands_on_host table
                        state is a list of possible states to filter on
        @type filter: list

        @return: SQL count()
        @rtype: int
        """
        try:
            for f in filter:
                if isinstance(f[1], str):  # f[1] must be a list
                    f[1] = [f[1]]
                if len(f) == 3:
                    if isinstance(f[2], bool):
                        if f[2]:
                            query = query.filter(
                                getattr(self.commands_on_host.c, f[0]).in_(f[1])
                            )
                        else:
                            query = query.filter(
                                not_(getattr(self.commands_on_host.c, f[0]).in_(f[1]))
                            )
                    elif f[2] == "<=":
                        query = query.filter(
                            getattr(self.commands_on_host.c, f[0]) <= f[1][0]
                        )
                    elif f[2] == ">=":
                        query = query.filter(
                            getattr(self.commands_on_host.c, f[0]) >= f[1][0]
                        )
                else:
                    query = query.filter(
                        getattr(self.commands_on_host.c, f[0]).in_(f[1])
                    )
            return int(query.scalar())
        except BaseException:
            return 0

    def __getAllStatus(self):
        """
        return global statuses (success, paused, stopped, running, failure) by commands_on_host's current_state
        """
        return {
            "success": ["done"],
            "paused": ["paused", "pause"],
            "stopped": ["stopped", "stop"],
            "running": [
                "wol_in_progress",
                "upload_in_progress",
                "upload_done",
                "execution_in_progress",
                "execution_done",
                "delete_in_progress",
                "delete_done",
                "inventory_in_progress",
                "inventory_done",
                "reboot_in_progress",
                "reboot_done",
                "scheduled",
                "re_scheduled",
                "halt_in_progress",
                "halt_done",
            ],
            "failure": [
                "failed",
                "upload_failed",
                "execution_failed",
                "delete_failed",
                "inventory_failed",
                "reboot_failed",
                "halt_failed",
                "not_reachable",
            ],
        }

    def __getStatus(self, ctx, query, verbose=False):
        running = self.__getAllStatus()["running"]
        failure = self.__getAllStatus()["failure"]
        stopped = self.__getAllStatus()["stopped"]
        paused = self.__getAllStatus()["paused"]
        success = self.__getAllStatus()["success"]
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        sec_up = self.getStateLen(
            query,
            [
                ["current_state", ["over_timed"], False],
                ["end_date", [now], ">="],
                ["current_state", paused, False],
                ["current_state", stopped, False],
                ["attempts_left", [0], False],
                ["uploaded", ["FAILED"]],
            ],
        )
        sec_ex = self.getStateLen(
            query,
            [
                ["current_state", ["over_timed"], False],
                ["end_date", [now], ">="],
                ["current_state", paused, False],
                ["current_state", stopped, False],
                ["attempts_left", [0], False],
                ["executed", ["FAILED"]],
            ],
        )
        sec_rm = self.getStateLen(
            query,
            [
                ["current_state", ["over_timed"], False],
                ["end_date", [now], ">="],
                ["current_state", paused, False],
                ["current_state", stopped, False],
                ["attempts_left", [0], False],
                ["deleted", ["FAILED"]],
            ],
        )
        sec_inv = self.getStateLen(
            query,
            [
                ["current_state", ["over_timed"], False],
                ["end_date", [now], ">="],
                ["current_state", paused, False],
                ["current_state", stopped, False],
                ["attempts_left", [0], False],
                ["inventoried", ["FAILED"]],
            ],
        )

        success_total = self.getStateLen(query, [["current_state", success]])
        stopped_total = self.getStateLen(query, [["current_state", stopped]])
        paused_total = self.getStateLen(query, [["current_state", paused]])
        running_total = self.getStateLen(
            query, [["current_state", running]]
        ) + self.getStateLen(
            query,
            [
                ["current_state", failure],
                ["end_date", now, ">="],
                ["attempts_left", [0], False],
            ],
        )
        failure_total = (
            self.getStateLen(
                query, [["current_state", failure], ["attempts_left", [0]]]
            )
            + self.getStateLen(query, [["current_state", ["over_timed"]]])
            + self.getStateLen(
                query,
                [
                    ["current_state", failure],
                    ["attempts_left", [0], False],
                    ["end_date", now, "<="],
                ],
            )
        )

        try:
            total = int(query.scalar())
        except BaseException:
            total = 0

        ret = {
            "total": total,
            "success": {
                "total": [success_total, []],
            },
            "stopped": {
                "total": [stopped_total, []],
            },
            "paused": {
                "total": [paused_total, []],
            },
            "running": {
                "total": [running_total, []],
                "wait_up": [
                    sum(
                        [
                            sec_up,
                            self.getStateLen(
                                query,
                                [
                                    ["current_state", ["over_timed"], False],
                                    ["current_state", paused, False],
                                    ["current_state", stopped, False],
                                    ["uploaded", ["TODO"]],
                                ],
                            ),
                        ]
                    ),
                    [],
                ],
                "run_up": [
                    self.getStateLen(
                        query,
                        [
                            ["current_state", "upload_in_progress"],
                        ],
                    ),
                    [],
                ],
                "sec_up": [sec_up, []],
                "wait_ex": [
                    sum(
                        [
                            sec_ex,
                            self.getStateLen(
                                query,
                                [
                                    ["current_state", ["over_timed"], False],
                                    ["current_state", paused, False],
                                    ["current_state", stopped, False],
                                    [
                                        "uploaded",
                                        ["TODO", "FAILED", "WORK_IN_PROGRESS"],
                                        False,
                                    ],
                                    ["executed", ["TODO"]],
                                ],
                            ),
                        ]
                    ),
                    [],
                ],
                "run_ex": [
                    self.getStateLen(
                        query,
                        [
                            ["current_state", ["execution_in_progress"]],
                        ],
                    ),
                    [],
                ],
                "sec_ex": [sec_ex, []],
                "wait_rm": [
                    sum(
                        [
                            sec_rm,
                            self.getStateLen(
                                query,
                                [
                                    ["current_state", ["over_timed"], False],
                                    ["current_state", paused, False],
                                    ["current_state", stopped, False],
                                    [
                                        "executed",
                                        ["TODO", "FAILED", "WORK_IN_PROGRESS"],
                                        False,
                                    ],
                                    ["deleted", ["TODO"]],
                                ],
                            ),
                        ]
                    ),
                    [],
                ],
                "run_rm": [
                    self.getStateLen(
                        query,
                        [
                            ["current_state", ["delete_in_progress"]],
                        ],
                    ),
                    [],
                ],
                "sec_rm": [sec_rm, []],
                "wait_inv": [
                    sum(
                        [
                            sec_inv,
                            self.getStateLen(
                                query,
                                [
                                    ["current_state", ["over_timed"], False],
                                    ["current_state", paused, False],
                                    ["current_state", stopped, False],
                                    [
                                        "deleted",
                                        ["TODO", "FAILED", "WORK_IN_PROGRESS"],
                                        False,
                                    ],
                                    ["inventoried", ["TODO"]],
                                ],
                            ),
                        ]
                    ),
                    [],
                ],
                "run_inv": [
                    self.getStateLen(
                        query,
                        [
                            ["current_state", ["inventory_in_progress"]],
                        ],
                    ),
                    [],
                ],
                "sec_inv": [sec_inv, []],
            },
            "failure": {
                "total": [failure_total, []],
                "fail_up": [
                    self.getStateLen(
                        query, [["current_state", ["failed"]], ["uploaded", ["FAILED"]]]
                    ),
                    [],
                ],
                "conn_up": [
                    self.getStateLen(
                        query,
                        [
                            ["attempts_left", [0]],
                            ["uploaded", ["FAILED"]],
                            ["current_state", ["not_reachable"]],
                        ],
                    ),
                    [],
                ],
                "fail_ex": [
                    self.getStateLen(
                        query, [["current_state", ["failed"]], ["executed", ["FAILED"]]]
                    ),
                    [],
                ],
                "conn_ex": [
                    self.getStateLen(
                        query,
                        [
                            ["attempts_left", [0]],
                            ["executed", ["FAILED"]],
                            ["current_state", ["not_reachable"]],
                        ],
                    ),
                    [],
                ],
                "fail_rm": [
                    self.getStateLen(
                        query, [["current_state", ["failed"]], ["deleted", ["FAILED"]]]
                    ),
                    [],
                ],
                "conn_rm": [
                    self.getStateLen(
                        query,
                        [
                            ["attempts_left", [0]],
                            ["deleted", ["FAILED"]],
                            ["current_state", ["not_reachable"]],
                        ],
                    ),
                    [],
                ],
                "fail_inv": [
                    self.getStateLen(
                        query,
                        [["current_state", ["failed"]], ["inventoried", ["FAILED"]]],
                    ),
                    [],
                ],
                "conn_inv": [
                    self.getStateLen(
                        query,
                        [
                            ["attempts_left", [0]],
                            ["inventoried", ["FAILED"]],
                            ["current_state", ["not_reachable"]],
                        ],
                    ),
                    [],
                ],
                "over_timed": [
                    self.getStateLen(query, [["current_state", ["over_timed"]]]),
                    [],
                ],
                "fail_wol": [
                    self.getStateLen(
                        query, [["current_state", ["failed"]], ["awoken", ["FAILED"]]]
                    ),
                    [],
                ],
                "fail_reboot": [
                    self.getStateLen(
                        query, [["current_state", ["failed"]], ["rebooted", ["FAILED"]]]
                    ),
                    [],
                ],
                "fail_halt": [
                    self.getStateLen(
                        query, [["current_state", ["failed"]], ["halted", ["FAILED"]]]
                    ),
                    [],
                ],
            },
        }

        if verbose:  # used for CSV generation
            for coh in query:
                if coh.current_state == "done":  # success
                    if verbose:
                        ret["success"]["total"][1].append(coh)
                elif (
                    coh.current_state == "stop" or coh.current_state == "stopped"
                ):  # stopped coh
                    if verbose:
                        ret["stopped"]["total"][1].append(coh)
                elif coh.current_state == "pause":
                    if verbose:
                        ret["paused"]["total"][1].append(coh)
                # out of the valid period of execution (= failed)
                elif coh.current_state == "over_timed":
                    if verbose:
                        ret["failure"]["total"][1].append(coh)
                    if verbose:
                        ret["failure"]["over_timed"][1].append(coh)
                # failure
                elif coh.attempts_left == 0 and (
                    coh.uploaded == "FAILED"
                    or coh.executed == "FAILED"
                    or coh.deleted == "FAILED"
                ):
                    if verbose:
                        ret["failure"]["total"][1].append(coh)
                    if coh.uploaded == "FAILED":
                        if verbose:
                            ret["failure"]["fail_up"][1].append(coh)
                        if coh.current_state == "not_reachable":
                            if verbose:
                                ret["failure"]["conn_up"][1].append(coh)
                    elif coh.executed == "FAILED":
                        if verbose:
                            ret["failure"]["fail_ex"][1].append(coh)
                        if coh.current_state == "not_reachable":
                            if verbose:
                                ret["failure"]["conn_ex"][1].append(coh)
                    elif coh.deleted == "FAILED":
                        if verbose:
                            ret["failure"]["fail_rm"][1].append(coh)
                        if coh.current_state == "not_reachable":
                            if verbose:
                                ret["failure"]["conn_rm"][1].append(coh)
                # fail but can still try again
                elif coh.attempts_left != 0 and (
                    coh.uploaded == "FAILED"
                    or coh.executed == "FAILED"
                    or coh.deleted == "FAILED"
                ):
                    if verbose:
                        ret["running"]["total"][1].append(coh)
                    if coh.uploaded == "FAILED":
                        if verbose:
                            ret["running"]["wait_up"][1].append(coh)
                        if verbose:
                            ret["running"]["sec_up"][1].append(coh)
                    elif coh.executed == "FAILED":
                        if verbose:
                            ret["running"]["wait_ex"][1].append(coh)
                        if verbose:
                            ret["running"]["sec_ex"][1].append(coh)
                    elif coh.deleted == "FAILED":
                        ret["running"]["wait_rm"][0] += 1
                        ret["running"]["sec_rm"][0] += 1
                else:  # running
                    if verbose and coh.deleted != "DONE" and coh.deleted != "IGNORED":
                        ret["running"]["total"][1].append(coh)
                    if coh.deleted == "DONE" or coh.deleted == "IGNORED":  # done
                        if verbose:
                            ret["success"]["total"][1].append(coh)
                    elif (
                        coh.executed == "DONE" or coh.executed == "IGNORED"
                    ):  # delete running
                        if coh.deleted == "WORK_IN_PROGRESS":
                            if verbose:
                                ret["running"]["run_rm"][1].append(coh)
                        else:
                            if verbose:
                                ret["running"]["wait_rm"][1].append(coh)
                    elif (
                        coh.uploaded == "DONE" or coh.uploaded == "IGNORED"
                    ):  # exec running
                        if coh.executed == "WORK_IN_PROGRESS":
                            if verbose:
                                ret["running"]["run_ex"][1].append(coh)
                        else:
                            if verbose:
                                ret["running"]["wait_ex"][1].append(coh)
                    else:  # upload running
                        if coh.uploaded == "WORK_IN_PROGRESS":
                            if verbose:
                                ret["running"]["run_up"][1].append(coh)
                        else:
                            if verbose:
                                ret["running"]["wait_up"][1].append(coh)

        return ret

    def antiPoolOverflowErrorback(self, reason):
        """
        an erroback, with handle QueuePool error-like by :
        - intercepting all exception
        - trap only SA "TimeoutError" Exceptions
        - if exception identified as TimeoutError, recreate pool
        - then raise the error anew
        """
        reason.trap(TimeoutError)
        if (
            self.db.pool._max_overflow > -1
            and self.db.pool._overflow >= self.db.pool._max_overflow
        ):
            logging.getLogger().error(
                "Timeout then overflow (%d vs. %d) detected in SQL pool : check your network connectivity !"
                % (self.db.pool._overflow, self.db.pool._max_overflow)
            )
            self.db.pool.dispose()
            self.db.pool = self.db.pool.recreate()
        return reason
