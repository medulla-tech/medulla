# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""

MSC Database module
Needed to access all the msc database information

"""

# standard modules
import re
import time
import datetime
import logging

# SqlAlchemy
from sqlalchemy import and_, not_
from sqlalchemy.orm import create_session

# MMC modules
from mmc.plugins.base.computers import ComputerManager

# from mmc.plugins.msc.mirror_api import MirrorApi
from mmc.plugins.msc.scheduler_api import SchedulerApi
from mmc.database.database_helper import DatabaseHelper

# blacklists
from mmc.plugins.msc import blacklist

# Pulse 2 stuff
from pulse2.database import msc
from pulse2.database.msc.orm.target import Target
from pulse2.database.msc.orm.commands import Commands
from pulse2.database.msc.orm.commands_on_host_phase import CommandsOnHostPhase
from pulse2.database.msc import CommandsOnHost


class MscDatabase(msc.MscDatabase):
    """
    Singleton Class to query the msc database.

    """

    def getMachinesSchedulers(self, target):
        """
        Return a deferred object resulting to a scheduler or a list of
        schedulers.
        """
        if (
            not target
        ):  # We can have this case with a convergence command without targets
            return SchedulerApi().getDefaultScheduler()
        elif isinstance(target[0], list):  # target = [[uuid, hostname], [uuid, target]]
            return SchedulerApi().getSchedulers([t[0] for t in target])
        else:  # target = [uuid, hostname]
            return SchedulerApi().getScheduler(target[0])

    def getBCast(self, ip, netmask):
        """
        Compute a brodcast address given a network IP and a network mask
        """
        a_ip = ip.split(".")
        a_netmask = netmask.split(".")
        a_network = [0, 0, 0, 0]
        for i in range(0, 4):
            a_network[i] = int(a_ip[i]) & int(a_netmask[i])
        a_notnetmask = [int(i) ^ 255 for i in netmask.split(".")]
        for i in range(0, 4):
            a_ip[i] = int(a_network[i]) | int(a_notnetmask[i])
        return ".".join([str(x) for x in a_ip])

    def prepareTarget(self, computer, group_id):
        """
        Use computer information to prepare data to be inserted in the MSC
        target table.
        """
        h_mac2bcast = []
        h_mac2netmask = []
        bcastAddresses = []
        netmasks = []
        ipAddresses = computer[1]["ipHostNumber"]
        netmask = computer[1]["subnetMask"]
        macAddresses = computer[1]["macAddress"]

        # Compute broadcast address
        for i in range(len(computer[1]["macAddress"])):
            try:
                bcastAddress = self.getBCast(ipAddresses[i], netmask[i])
            except Exception as e:
                self.logger.debug(
                    "Can't compute broadcast address for %s: %s"
                    % (str(computer), str(e))
                )
                bcastAddress = "255.255.255.255"
                self.logger.debug("Using default broadcast address %s" % bcastAddress)
            h_mac2bcast.append(bcastAddress)
            try:
                h_mac2netmask.append(netmask[i])
            except:
                h_mac2netmask.append("0.0.0.0")

        try:
            targetName = computer[1]["cn"][0]
        except KeyError:
            pass
        try:
            targetName = computer[1]["fullname"]
        except KeyError:
            pass

        self.logger.debug(
            "Computer known IP addresses before filter: " + str(ipAddresses)
        )
        # Apply IP addresses blacklist
        if self.config.ignore_non_rfc2780:
            ipAddresses = blacklist.rfc2780Filter(ipAddresses)
        if self.config.ignore_non_rfc1918:
            ipAddresses = blacklist.rfc1918Filter(ipAddresses)
        ipAddresses = blacklist.excludeFilter(ipAddresses, self.config.exclude_ipaddr)
        ipAddresses = blacklist.mergeWithIncludeFilter(
            computer[1]["ipHostNumber"], ipAddresses, self.config.include_ipaddr
        )
        macs = []
        for i in range(len(computer[1]["ipHostNumber"])):
            if computer[1]["ipHostNumber"][i] in ipAddresses:
                # MAC address can be non-existent (for non-physical interfaces like VPN)
                if macAddresses[i]:
                    macs.append(macAddresses[i])
        macAddresses = macs
        self.logger.debug(
            "Computer known IP addresses after filter: " + str(ipAddresses)
        )

        self.logger.debug(
            "Computer known MAC addresses before filter: " + str(macAddresses)
        )
        macAddresses = blacklist.macAddressesFilter(
            macAddresses, self.config.wol_macaddr_blacklist
        )
        self.logger.debug(
            "Computer known MAC addresses after filter: " + str(macAddresses)
        )

        # Fill bcastAddresses and netmasks lists
        for i in range(len(computer[1]["macAddress"])):
            macAddress = computer[1]["macAddress"][i]
            # Only select non-filtered MAC addresses
            if macAddress in macAddresses:
                bcastAddresses.append(h_mac2bcast[i])
                netmasks.append(h_mac2netmask[i])

        if len(netmasks) == 0 or None in netmasks:
            netmasks = [""]

        # Multiple IP addresses or IP addresses may be separated by "||"
        targetMac = "||".join(macAddresses)
        targetIp = "||".join(ipAddresses)
        targetBCast = "||".join(bcastAddresses)
        targetNetmask = "||".join(netmasks)

        targetUuid = computer[1]["objectUUID"][0]
        return self.createTarget(
            targetName,
            targetUuid,
            targetIp,
            targetMac,
            targetBCast,
            targetNetmask,
            None,
            group_id,
        )

    def getComputersData(self, ctx, targets, group_id):
        """
        Get all targets network information
        """
        start_time = time.time()
        computers = ComputerManager().getComputersNetwork(ctx, {"uuids": targets})
        middle_time = time.time()
        # Rebuild the targets list, and get computers data
        tmp = []
        targetsdata = []
        for computer in computers:
            if "fullname" in computer[1]:
                hostname = computer[1]["fullname"]
            else:
                hostname = computer[1]["cn"][0]
            tmp.append([computer[1]["objectUUID"][0], hostname])
            targetsdata.append(self.prepareTarget(computer, group_id))
        targets = tmp[:]
        end_time = time.time()
        self.logger.debug(
            "msc.database.getComputersData took %ss to get network data and %ss to treat it"
            % (middle_time - start_time, end_time - middle_time)
        )
        return tmp, targetsdata

    def __getTimeDefaults(self, start_date, end_date):
        """time stuff to calculate number of attempts and keep
        the default values
        """
        fmt = "%Y-%m-%d %H:%M:%S"

        if start_date == "0000-00-00 00:00:00":
            start_timestamp = time.time()
            start_date = datetime.datetime.fromtimestamp(start_timestamp).strftime(fmt)
        else:
            start_timestamp = time.mktime(
                datetime.datetime.strptime(start_date, fmt).timetuple()
            )

        if end_date == "0000-00-00 00:00:00":
            delta = int(self.config.web_def_coh_life_time) * 60 * 60
            end_timestamp = start_timestamp + delta
            end_date = datetime.datetime.fromtimestamp(end_timestamp).strftime(fmt)
        else:
            end_timestamp = time.mktime(
                datetime.datetime.strptime(end_date, fmt).timetuple()
            )

        total_time = end_timestamp - start_timestamp
        seconds_per_day = 60 * 60 * 24
        days_nbr = total_time // seconds_per_day
        if days_nbr == 0:
            days_nbr = 1

        max_connection_attempt = days_nbr * self.config.web_def_attempts_per_day

        return start_date, end_date, max_connection_attempt

    def addCommand(
        self,
        ctx,
        package_id,
        start_file,
        parameters,
        files,
        targets,
        mode="push",
        group_id="",
        start_script=True,
        clean_on_success="enable",
        start_date="0000-00-00 00:00:00",
        end_date="0000-00-00 00:00:00",
        connect_as="root",
        title="",
        do_halt="disable",
        do_reboot="disable",
        do_wol="enable",
        do_wol_with_imaging="disable",
        do_windows_update="disable",
        next_connection_delay=60,
        max_connection_attempt=3,
        do_inventory="disable",
        maxbw=0,
        root=None,
        deployment_intervals="",
        fk_bundle=None,
        order_in_bundle=None,
        proxy_mode="none",
        proxies=[],
        state="active",
        is_quick_action=False,
        cmd_type=0,
    ):
        """
        Main func to inject a new command in our MSC database

        Return a Deferred object resulting to the command id
        """
        if root == None:
            root = self.config.repopath
        time_defaults = self.__getTimeDefaults(start_date, end_date)
        start_date, end_date, max_connection_attempt = time_defaults
        targets_to_insert = []
        targets_name = []
        coh_to_insert = []
        targets, targetsdata = self.getComputersData(ctx, targets, group_id)
        # type 2 is convergence command
        # a convergence command can contains no targets
        # not other commands type
        if not targets and cmd_type != 2:
            self.logger.error(
                "The machine list is empty, does your machines have a network interface ?"
            )
            return -2

        def cbCreateTargets():
            for i in range(len(targets)):
                uri = "%s://%s" % ("file", root)
                targetsdata[i]["mirrors"] = uri
                # Keep not blacklisted target name for commands_on_host
                # creation.
                targets_name.append(targets[i][1])
                # Maybe could be done in prepareTarget
                targetsdata[i] = self.blacklistTargetHostname(targetsdata[i])
                targets_to_insert.append((targetsdata[i], targets[i][1], ""))
            session = create_session()
            session.begin()
            cmd = self.createCommand(
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
                parameters,
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
                len(targets),
                cmd_type=cmd_type,
            )
            session.flush()
            # Convergence command (type 2) can have no targets
            # so return command_id if no targets
            if not targets and cmd_type == 2:
                try:
                    session.commit()
                except:
                    pass
                return cmd.getId()
            for atarget, target_name, ascheduler in targets_to_insert:
                target = Target()
                target.target_macaddr = atarget["target_macaddr"]
                target.id_group = atarget["id_group"]
                target.target_uuid = atarget["target_uuid"]
                target.target_bcast = atarget["target_bcast"]
                target.target_name = atarget["target_name"]
                target.target_ipaddr = atarget["target_ipaddr"]
                target.mirrors = atarget["mirrors"]
                target.target_network = atarget["target_network"]
                session.add(target)
                session.flush()
                if hasattr(session, "refresh"):
                    session.refresh(target)
                order_in_proxy = None
                max_clients_per_proxy = 0
                try:
                    candidates = [
                        x for x in proxies if x["uuid"] == atarget["target_uuid"]
                    ]
                    if len(candidates) == 1:
                        max_clients_per_proxy = candidates[0]["max_clients"]
                        order_in_proxy = candidates[0]["priority"]
                except ValueError:
                    self.logger.warn(
                        "Failed to get values 'order_in_proxy' or 'max_clients'"
                    )
                coh_to_insert.append(
                    self.createCommandsOnHost(
                        cmd.getId(),
                        atarget,
                        target.id,
                        target_name,
                        max_connection_attempt,
                        start_date,
                        end_date,
                        ascheduler,
                        order_in_proxy,
                        max_clients_per_proxy,
                    )
                )
                try:
                    session.commit()
                except:
                    pass

            def _getCohIds(session, cmd_id, target_uuids=[]):
                """
                Returns the list of commands_on_host linked to this command
                If list of target_uuids, returns only uuids of this list
                """
                myCommandOnHosts = session.query(CommandsOnHost)
                if target_uuids:
                    myCommandOnHosts = myCommandOnHosts.join(Target)
                    myCommandOnHosts = myCommandOnHosts.filter(
                        Target.target_uuid.in_(target_uuids)
                    )
                myCommandOnHosts = myCommandOnHosts.filter(
                    CommandsOnHost.fk_commands == cmd_id
                )
                return myCommandOnHosts.all()

            if self.config.dbhost and self.config.dbhost == "localhost":
                session.execute(self.commands_on_host.insert(), coh_to_insert)
                cohs = _getCohIds(session, cmd.getId())
            else:
                session.execute(self.commands_on_host.insert(), coh_to_insert)
                cohs = _getCohIds(session, cmd.getId())

            self._createPhases(
                session,
                cohs,
                do_wol_with_imaging,
                do_wol,
                files,
                start_script,
                clean_on_success,
                do_inventory,
                do_halt,
                do_reboot,
                do_windows_update,
                is_quick_action,
            )
            cmd.type = cmd_type
            cmd.ready = True
            return cmd.getId()

        return cbCreateTargets()

    @DatabaseHelper._session
    def get_package_cmds(self, session, pid):
        """
        Get all commands of a given package
        return a dict with cmd_id as key and start_date as value

        @param pid: uuid of dropped package
        @type pid: uuid
        """
        query = session.query(Commands).filter_by(package_id=pid)
        ret = {}
        for x in query:
            ret[x.id] = x.start_date
        return ret

    def extend_command(self, cmd_id, start_date, end_date):
        """
        Custom command re-scheduling.

        @param cmd_id: Commands id
        @type cmd_id: int

        @param start_date: new start date of command
        @type start_date: str

        @param end_date: new end date of command
        @type end_date: str
        """

        self.extendCommand(cmd_id, start_date, end_date)

    def applyCmdPatterns(self, cmd, patternActions=None):
        """
        Replace special patterns in command by special action
        Return a list who contains command and special actions

        special actions are:
            @@do_reboot@@
            @@do_halt@@
            @@do_inventory@@
            @@do_wol@@

        @param cmd: command to start (e.g. '/sbin/shutdown -r now')
        @type cmd: str

        @patternActions: dictionnary of special actions
        @type: dict

        @return list of command and special actions
        """

        if patternActions is None:
            patternActions = {
                "do_reboot": "disable",
                "do_halt": "disable",
                "do_inventory": "disable",
                "do_wol": "disable",
                "do_wol_with_imaging": "disable",
                "do_windows_update": "disable",
            }

        if "@@do_reboot@@" in cmd:
            patternActions["do_reboot"] = "enable"
            cmd = cmd.replace("@@do_reboot@@", "")
        if "@@do_halt@@" in cmd:
            patternActions["do_halt"] = "enable"
            cmd = cmd.replace("@@do_halt@@", "")
        if "@@do_inventory@@" in cmd:
            patternActions["do_inventory"] = "enable"
            cmd = cmd.replace("@@do_inventory@@", "")
        if "@@do_wol@@" in cmd:
            patternActions["do_wol"] = "enable"
            cmd = cmd.replace("@@do_wol@@", "")
        if "@@do_wol_with_imaging@@" in cmd:
            patternActions["do_wol"] = "enable"
            patternActions["do_wol_with_imaging"] = "enable"
            cmd = cmd.replace("@@do_wol_with_imaging@@", "")
        if "@@do_windows_update@@" in cmd:
            patternActions["do_windows_update"] = "enable"
            cmd = cmd.replace("@@do_windows_update@@", "")

        return [cmd, patternActions]

    def addCommandQuick(self, ctx, cmd, targets, desc, gid=None):
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

        cmd, patternActions = self.applyCmdPatterns(cmd)
        is_quick_action = any(
            [True for a in list(patternActions.values()) if a == "enable"]
        )

        # run a built-in script
        p1 = re.compile("^\/scripts\/")
        if p1.match(cmd):
            files.append(cmd)

        return self.addCommand(
            ctx,
            None,
            cmd,
            "",
            files,
            targets,
            "push",
            gid,
            True,
            "enable",
            "0000-00-00 00:00:00",
            "0000-00-00 00:00:00",
            "root",  # FIXME: this should be the effective user we want to connect with
            desc,
            patternActions["do_halt"],
            patternActions["do_reboot"],
            patternActions["do_wol"],
            patternActions["do_wol_with_imaging"],
            patternActions["do_windows_update"],
            60,
            3,
            patternActions["do_inventory"],
            0,
            0,
            "",
            None,
            None,
            "none",
            [],
            "active",
            is_quick_action,
        )

    def startCommand(self, c_id):
        """
        Start a command. In fact we set all its related commands_on_host to the
        scheduled state, and set next_launch_date to immediately.
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        self.commands_on_host.update(
            and_(
                self.commands_on_host.c.fk_commands == c_id,
                self.commands_on_host.c.current_state != "done",
                self.commands_on_host.c.current_state != "failed",
            )
        ).execute(current_state="scheduled", next_launch_date="0000-00-00 00:00:00")
        trans.commit()

    def stopCommand(self, c_id):
        """
        Stop a command, by stopping all its related commands_on_host.
        @returns: the list of all related commands_on_host
        @rtype: list
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        self.commands_on_host.update(
            and_(
                self.commands_on_host.c.fk_commands == c_id,
                self.commands_on_host.c.current_state != "done",
                self.commands_on_host.c.current_state != "failed",
            )
        ).execute(current_state="stopped", next_launch_date="2031-12-31 23:59:59")
        self.commands_on_host.update(
            and_(
                self.commands_on_host.c.fk_commands == c_id,
                self.commands_on_host.c.uploaded == "WORK_IN_PROGRESS",
            )
        ).execute(uploaded="FAILED")
        self.commands_on_host.update(
            and_(
                self.commands_on_host.c.fk_commands == c_id,
                self.commands_on_host.c.executed == "WORK_IN_PROGRESS",
            )
        ).execute(executed="FAILED")
        self.commands_on_host.update(
            and_(
                self.commands_on_host.c.fk_commands == c_id,
                self.commands_on_host.c.deleted == "WORK_IN_PROGRESS",
            )
        ).execute(deleted="FAILED")
        trans.commit()

    def pauseCommand(self, c_id):
        """
        Pause a command, by pausing all its related commands_on_host.
        @returns: the list of all related commands_on_host
        @rtype: list
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        self.commands_on_host.update(
            and_(
                self.commands_on_host.c.fk_commands == c_id,
                self.commands_on_host.c.current_state != "done",
                self.commands_on_host.c.current_state != "failed",
                self.commands_on_host.c.current_state != "stopped",
                self.commands_on_host.c.current_state != "stop",
            )
        ).execute(current_state="pause")
        trans.commit()

    def blacklistTargetHostname(self, target):
        # Apply host name blacklist
        target_name = target["target_name"]
        if not blacklist.checkWithRegexps(target_name, self.config.include_hostname):
            # The host name is not in the whitelist
            if (
                (self.config.ignore_non_fqdn and not blacklist.isFqdn(target_name))
                or (
                    self.config.ignore_invalid_hostname
                    and not blacklist.isValidHostname(target_name)
                )
                or blacklist.checkWithRegexps(target_name, self.config.exclude_hostname)
            ):
                # The host name is not FQDN or invalid, so we don't put it the
                # database. This way the host name won't be use to resolve the
                # computer host name.
                self.logger.debug(
                    "Host name has been filtered because '%s' is not FQDN, invalid or matched an exclude regexp"
                    % target_name
                )
                target["target_name"] = ""
        return target

    @DatabaseHelper._session
    def _get_convergence_soon_ended_commands(self, session, cmd_ids=[]):
        fmt = "%Y-%m-%d %H:%M:%S"
        now_plus_one_hour = (
            datetime.datetime.now() + datetime.timedelta(hours=1)
        ).strftime(fmt)
        query = session.query(Commands)
        query = query.filter(
            and_(
                Commands.id.in_(cmd_ids),
                Commands.end_date < now_plus_one_hour,
            )
        )
        return [x.id for x in query]

    @DatabaseHelper._session
    def _update_convergence_dates(self, session, cmd_id):
        fmt = "%Y-%m-%d %H:%M:%S"
        start_date = datetime.datetime.now().strftime(fmt)
        end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(fmt)
        return self.extendCommand(cmd_id, start_date, end_date)

    @DatabaseHelper._sessionm
    def update_msc_command(
        self,
        session,
        login,
        commandid,
        bandwidth,
        params,
    ):
        """
        Updates only the Start_date, End_date, Deployment_interval and Do_reBoot fields
        in the MSC.Commands table.

        Args:
        Session (session): SQLALCHEMY session managed by the decorator.
        Login (Str): (optional) user login, for example for the 'Creator' field.
        Commandid (int): order identifier in MSC.Commands.
        Bandwidth (int or Str): value for the 'Maxbw' field.If empty, will be treated like 0.
        Params (dict): must contain, if necessary, the following keys:
        -'Start_date': (Ex. "2025-02-12 09:27:37")
        -'End_date': (Ex. "2025-02-13 09:27:37")
        - 'Deployment_intervals': (eg "12-16")
        - 'do_reboot': (expected "enable" or "disable")
        - 'state': (expected "active" or "disabled")

        Returns:
        INT: The Updated Order Identifier, or NO in case of error.
        """
        try:
            command = session.query(Commands).filter_by(id=commandid).first()
            if not command:
                logging.getLogger().error(f"No order found for ID {commandid}.")
                return None

            if isinstance(params, dict):
                if 'start_date' in params:
                    command.start_date = params['start_date']
                if 'end_date' in params:
                    command.end_date = params['end_date']
                if 'deployment_intervals' in params:
                    command.deployment_intervals = params['deployment_intervals']
                if 'do_reboot' in params:
                    command.do_reboot = params['do_reboot']  # Ex: "enable" ou "disable"
                if 'state' in params:
                    command.state = params['state']  # Ex: "active" ou "disabled"
                if 'title' in params:
                    command.title = params['title']

            if not str(bandwidth).strip():
                command.maxbw = 0
            else:
                command.maxbw = int(bandwidth)

            if login:
                command.creator = login

            session.commit()
            session.flush()
            return command.id
        except Exception as e:
            logging.getLogger().error(f"Error when updating the order: {e}")
            session.rollback()
            return None


    def _get_machines_in_command(self, session, cmd_id):
        """
        For a given cmd_id, return machines who are part of this command, except these who are
        in done step in phase table.
        So, machines who are ready, running or failed
        """
        query = (
            session.query(CommandsOnHost)
            .add_entity(Target)
            .join(Target)
            .outerjoin(CommandsOnHostPhase)
        )
        query = query.filter(CommandsOnHost.fk_commands == cmd_id)
        query = query.filter(not_(CommandsOnHostPhase.state.in_(["done"])))
        return [x[1].target_uuid for x in query]

    @DatabaseHelper._session
    def _get_convergence_new_machines_to_add(
        self, session, ctx, cmd_id, convergence_deploy_group_id
    ):
        """
        Check if machines will be added to convergence command
        Return machines who are part of deploy group, but not already present in convergence command, except these
        who are in done step in phase table.
        @see http://projects.mandriva.org/issues/2255:
            if package were already deployed, but was manually removed by a user, it must be redeployed
        """
        machines_in_command = self._get_machines_in_command(session, cmd_id)
        machines_in_deploy_group = ComputerManager().getRestrictedComputersList(
            ctx, filt={"gid": convergence_deploy_group_id}, justId=True
        )
        return [x for x in machines_in_deploy_group if x not in machines_in_command]

    @DatabaseHelper._sessionm
    def addMachinesToCommand(
        self,
        session,
        ctx,
        cmd_id,
        targets,
        group_id="",
        root=None,
        mode="push",
        proxies=[],
        phases={},
    ):
        """
        Update the list of machines to deploy when creating the dynamic group.

        Args:
            ctx: Context
            cmd_id: Id of the command in SQL
            group_id: If of the group we deploy in
            root:
            mode:
            proxies:
            phases:
        Return:
            It returns the updated list of machines
        """
        cmd = self.getCommands(ctx, cmd_id)
        if root is None:
            root = self.config.repopath
        targets_to_insert = []
        coh_to_insert = []
        target_uuids = targets
        existing_coh_ids = [
            coh.id for coh in cmd.getCohIds(session, target_uuids=target_uuids)
        ]
        targets, targetsdata = self.getComputersData(ctx, targets, group_id)

        if len(targets) == 0:
            self.logger.error(
                "The machine list is empty, does your machines have a network interface ?"
            )
            return -2

        def cbCreateTargets():
            uri = ""
            for i in range(len(targets)):
                targets_to_insert.append((targetsdata[i], targets[i][1], None))

            for atarget, target_name, ascheduler in targets_to_insert:
                target = Target()
                target.target_macaddr = atarget["target_macaddr"]
                target.id_group = atarget["id_group"]
                target.target_uuid = atarget["target_uuid"]
                target.target_bcast = atarget["target_bcast"]
                target.target_name = atarget["target_name"]
                target.target_ipaddr = atarget["target_ipaddr"]
                target.mirrors = atarget["mirrors"]
                target.target_network = atarget["target_network"]

                session.add(target)
                session.flush()
                if hasattr(session, "refresh"):
                    session.refresh(target)

                order_in_proxy = None
                max_clients_per_proxy = 0
                try:
                    candidates = [
                        x for x in proxies if x["uuid"] == atarget["target_uuid"]
                    ]
                    if len(candidates) == 1:
                        max_clients_per_proxy = candidates[0]["max_clients"]
                        order_in_proxy = candidates[0]["priority"]
                except ValueError:
                    self.logger.warn(
                        "Failed to get values 'order_in_proxy' or 'max_clients'"
                    )
                coh_to_insert.append(
                    self.createCommandsOnHost(
                        cmd_id,
                        atarget,
                        target.id,
                        target_name,
                        cmd.max_connection_attempt,
                        cmd.start_date,
                        cmd.end_date,
                        ascheduler,
                        order_in_proxy,
                        max_clients_per_proxy,
                    )
                )
            session.execute(self.commands_on_host.insert(), coh_to_insert)

            cohs = [
                coh
                for coh in cmd.getCohIds(session, target_uuids=target_uuids)
                if coh.id not in existing_coh_ids
            ]

            def _get_phase(name):
                return phases.get(name, False) == "on" and "enable" or "disable"

            self._createPhases(
                session,
                cohs,
                cmd.do_imaging_menu,
                _get_phase("do_wol"),
                cmd.files,
                _get_phase("start_script"),
                _get_phase("clean_on_success"),
                _get_phase("do_inventory"),
                _get_phase("do_halt"),
                _get_phase("do_reboot"),
                _get_phase("do_windows_update"),
                is_quick_action=False,
            )
            session.commit()
            self._force_command_type(cmd_id, 2)
            self._set_command_ready(cmd_id)
            return cmd_id

        d = cbCreateTargets()
        return d
