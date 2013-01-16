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

MSC Database module
Needed to access all the msc database information

"""

# standard modules
import re
import time
import datetime

# SqlAlchemy
from sqlalchemy import *
from sqlalchemy.orm import *

# MMC modules
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.msc.mirror_api import MirrorApi
from mmc.plugins.msc.scheduler_api import SchedulerApi

# blacklists
from mmc.plugins.msc import blacklist

# Pulse 2 stuff
from pulse2.database import msc

class MscDatabase(msc.MscDatabase):
    """
    Singleton Class to query the msc database.

    """
    def getMachinesSchedulers(self, target):
        """
        Return a deferred object resulting to a scheduler or a list of
        schedulers.
        """
        if type(target[0]) == list: # target = [[uuid, hostname], [uuid, target]]
            return SchedulerApi().getSchedulers(map(lambda t: t[0], target))
        else: # target = [uuid, hostname]
            return SchedulerApi().getScheduler(target[0])

    def getBCast(self, ip, netmask):
        """
        Compute a brodcast address given a network IP and a network mask
        """
        a_ip = ip.split('.')
        a_netmask = netmask.split('.')
        a_network = [0,0,0,0]
        for i in range(0,4):
            a_network[i] = int(a_ip[i]) & int(a_netmask[i])
        a_notnetmask = map(lambda i: int(i) ^ 255, netmask.split('.'))
        for i in range(0,4):
            a_ip[i] = int(a_network[i]) | int(a_notnetmask[i])
        return '.'.join(map(lambda x: str(x), a_ip))


    def prepareTarget(self, computer, group_id):
        """
        Use computer information to prepare data to be inserted in the MSC
        target table.
        """
        h_mac2bcast = []
        h_mac2netmask = []
        bcastAddresses = []
        netmasks = []
        ipAddresses = computer[1]['ipHostNumber']
        netmask = computer[1]['subnetMask']
        macAddresses = computer[1]['macAddress']

        # Compute broadcast address
        for i in range(len(computer[1]['macAddress'])):
            try:
                bcastAddress = self.getBCast(ipAddresses[i], netmask[i])
            except Exception, e:
                self.logger.debug("Can't compute broadcast address for %s: %s" % (str(computer), str(e)))
                bcastAddress = "255.255.255.255"
                self.logger.debug("Using default broadcast address %s" % bcastAddress)
            h_mac2bcast.append(bcastAddress)
            try:
                h_mac2netmask.append(netmask[i])
            except:
                h_mac2netmask.append('0.0.0.0')

        try:
            targetName = computer[1]['cn'][0]
        except KeyError:
            pass
        try:
            targetName = computer[1]['fullname']
        except KeyError:
            pass

        self.logger.debug("Computer known IP addresses before filter: " + str(ipAddresses))
        # Apply IP addresses blacklist
        if self.config.ignore_non_rfc2780:
            ipAddresses = blacklist.rfc2780Filter(ipAddresses)
        if self.config.ignore_non_rfc1918:
            ipAddresses = blacklist.rfc1918Filter(ipAddresses)
        ipAddresses = blacklist.excludeFilter(ipAddresses, self.config.exclude_ipaddr)
        ipAddresses = blacklist.mergeWithIncludeFilter(computer[1]['ipHostNumber'], ipAddresses, self.config.include_ipaddr)
        macs = []
        for i in range(len(computer[1]['ipHostNumber'])):
            if computer[1]['ipHostNumber'][i] in ipAddresses:
                macs.append(macAddresses[i])
        macAddresses = macs
        self.logger.debug("Computer known IP addresses after filter: " + str(ipAddresses))

        self.logger.debug("Computer known MAC addresses before filter: " + str(macAddresses))
        macAddresses = blacklist.macAddressesFilter(macAddresses, self.config.wol_macaddr_blacklist)
        self.logger.debug("Computer known MAC addresses after filter: " + str(macAddresses))

        # Fill bcastAddresses and netmasks lists
        for i in range(len(computer[1]['macAddress'])):
            macAddress = computer[1]['macAddress'][i]
            # Only select non-filtered MAC addresses
            if macAddress in macAddresses:
                bcastAddresses.append(h_mac2bcast[i])
                netmasks.append(h_mac2netmask[i])

        # Multiple IP addresses or IP addresses may be separated by "||"
        targetMac = '||'.join(macAddresses)
        targetIp = '||'.join(ipAddresses)
        targetBCast = '||'.join(bcastAddresses)
        targetNetmask = '||'.join(netmasks)

        targetUuid = computer[1]['objectUUID'][0]
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
        computers = ComputerManager().getComputersNetwork(ctx, {"uuids" : targets})
        middle_time = time.time()
        # Rebuild the targets list, and get computers data
        tmp = []
        targetsdata = []
        for computer in computers:
            if 'fullname' in computer[1]:
                hostname = computer[1]['fullname']
            else:
                hostname = computer[1]['cn'][0]
            tmp.append([computer[1]['objectUUID'][0], hostname])
            targetsdata.append(self.prepareTarget(computer, group_id))
        targets = tmp[:]
        end_time = time.time()
        self.logger.debug("msc.database.getComputersData took %ss to get network data and %ss to treat it"%(middle_time-start_time, end_time-middle_time))
        return tmp, targetsdata

    def addCommands(self, ctx, session, targets, commands, group_id = None):
        """
        Add multiple commands in one database session. Used when inserting a
        bundle in database.
        """
        targets_to_insert_list = []
        targets_name = []
        coh_to_insert = []

        targets, targetsdata = self.getComputersData(ctx, targets, group_id)
        if len(targets) == 0:
            self.logger.error("The machine list is empty, does your machines have a network interface ?")
            return -2

        def cbGetTargetsMirrors(schedulers, session):
            args = map(lambda x: {"uuid" : x[0], "name": x[1]}, targets)
            d1 = MirrorApi().getMirrors(args)
            d1.addCallback(cbGetTargetsFallbackMirrors, schedulers, session)
            d1.addErrback(lambda err: err)
            return d1

        def cbGetTargetsFallbackMirrors(mirrors, schedulers, session):
            args = map(lambda x: {"uuid" : x[0], "name": x[1]}, targets)
            d2 = MirrorApi().getFallbackMirrors(args)
            d2.addCallback(cbCreateTargets, mirrors, schedulers, session)
            d2.addErrback(lambda err: err)
            return d2

        def cbPushModeCreateTargets(schedulers, session):
            return cbCreateTargets(None, None, schedulers, session, push_pull = False)

        def cbCreateTargets(fbmirrors, mirrors, schedulers, session, push_pull = True):
            # For each command, we prepare the targets list
            # There is one targets list per command because the root package
            # path may change according to the package
            for command in commands:
                targets_to_insert = []
                root = command['root']
                if root == None:
                    root = self.config.repopath
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
                    # Keep not blacklisted target name for commands_on_host
                    # creation.
                    targets_name.append(targets[i][1])
                    # Maybe could be done in prepareTarget
                    targetsdata[i] = self.blacklistTargetHostname(targetsdata[i])
                    targets_to_insert.append(dict(targetsdata[i]))
                targets_to_insert_list.append(targets_to_insert)

            if session == None:
                session = create_session(transactional = True)
            ret = []
            for cmd, targets_to_insert in zip(commands, targets_to_insert_list):
                cobj = self.createCommand(session, cmd['package_id'], cmd['start_file'], cmd['parameters'], cmd['files'], cmd['start_script'], cmd['clean_on_success'], cmd['start_date'], cmd['end_date'], cmd['connect_as'], ctx.userid, cmd['title'], cmd['issue_halt_to'], cmd['do_reboot'], cmd['do_wol'], cmd['next_connection_delay'], cmd['max_connection_attempt'], cmd['do_inventory'], cmd['maxbw'], cmd['deployment_intervals'], cmd['fk_bundle'], cmd['order_in_bundle'], cmd['proxies'], cmd['proxy_mode'])
                session.flush()
                ret.append(cobj.getId())

                r = session.execute(self.target.insert(), targets_to_insert)
                first_target_id = r.lastrowid
                for atarget, target_name, ascheduler in zip(targets_to_insert, targets_name, schedulers):
                    order_in_proxy = None
                    max_clients_per_proxy = 0
                    try:
                        candidates = filter(lambda(x): x['uuid'] == atarget["target_uuid"], cmd['proxies'])
                        if len(candidates) == 1:
                            max_clients_per_proxy = candidates[0]['max_clients']
                            order_in_proxy = candidates[0]['priority']
                    except ValueError:
                        pass
                    coh_to_insert.append(self.createCommandsOnHost(cobj.getId(),
                                                                   atarget,
                                                                   first_target_id, 
                                                                   target_name, 
                                                                   cmd['start_date'], 
                                                                   cmd['end_date'], 
                                                                   cmd['max_connection_attempt'], 
                                                                   ascheduler, 
                                                                   order_in_proxy, 
                                                                   max_clients_per_proxy))
                    first_target_id = first_target_id + 1
            session.execute(self.commands_on_host.insert(), coh_to_insert)
            session.commit()

            return ret

        d = self.getMachinesSchedulers(targets)
        mode = commands[0]['mode']
        if mode == 'push_pull':
            d.addCallback(cbGetTargetsMirrors, session)
        else:
            d.addCallback(cbPushModeCreateTargets, session)
        d.addErrback(lambda err: err)
        return d

    def addCommand(self,
                ctx,
                package_id,
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
                do_halt = "done",
                do_reboot = 'disable',
                do_wol = 'enable',
                next_connection_delay = 60,
                max_connection_attempt = 3,
                do_inventory = 'disable',
                maxbw = 0,
                root = None,
                deployment_intervals = "",
                fk_bundle = None,
                order_in_bundle = None,
                proxy_mode = 'none',
                proxies = []
            ):
        """
        Main func to inject a new command in our MSC database

        Return a Deferred object resulting to the command id
        """
        if root == None:
            root = self.config.repopath

        # a time stuff to calculate number of attempts
        fmt = "%Y-%m-%d %H:%M:%S"
        
        if start_date == "0000-00-00 00:00:00":
            start_timestamp = time.time()
            start_date = datetime.datetime.fromtimestamp(start_timestamp).strftime(fmt)
        else :
            start_timestamp = time.mktime(datetime.datetime.strptime(start_date, fmt).timetuple())
            
        if end_date == "0000-00-00 00:00:00":
            delta = int(self.config.web_def_coh_life_time) * 60 * 60
            end_timestamp = start_timestamp + delta
            end_date = datetime.datetime.fromtimestamp(end_timestamp).strftime(fmt)
        else :
            end_timestamp = time.mktime(datetime.datetime.strptime(end_date, fmt).timetuple())
         
        total_time = end_timestamp - start_timestamp
        seconds_per_day = 60 * 60 * 24
        days_nbr = total_time // seconds_per_day
        if days_nbr == 0 : 
            days_nbr = 1

        max_connection_attempt = days_nbr * self.config.web_def_attempts_per_day

        targets_to_insert = []
        targets_name = []
        coh_to_insert = []

        targets, targetsdata = self.getComputersData(ctx, targets, group_id)
        if len(targets) == 0:
            self.logger.error("The machine list is empty, does your machines have a network interface ?")
            return -2

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
                # Keep not blacklisted target name for commands_on_host
                # creation.
                targets_name.append(targets[i][1])
                # Maybe could be done in prepareTarget
                targetsdata[i] = self.blacklistTargetHostname(targetsdata[i])
                targets_to_insert.append(targetsdata[i])

            session = create_session()
            session.begin()
            cmd = self.createCommand(session, package_id, start_file, parameters, files, start_script, clean_on_success, start_date, end_date, connect_as, ctx.userid, title, do_halt, do_reboot, do_wol, next_connection_delay, max_connection_attempt, do_inventory, maxbw, deployment_intervals, fk_bundle, order_in_bundle, proxies, proxy_mode)
            session.flush()

            r = session.execute(self.target.insert(), targets_to_insert)
            first_target_id = r.lastrowid
            for atarget, target_name, ascheduler in zip(targets_to_insert, targets_name, schedulers):
                order_in_proxy = None
                max_clients_per_proxy = 0
                try:
                    candidates = filter(lambda(x): x['uuid'] == atarget["target_uuid"], proxies)
                    if len(candidates) == 1:
                        max_clients_per_proxy = candidates[0]['max_clients']
                        order_in_proxy = candidates[0]['priority']
                except ValueError:
                    pass
                coh_to_insert.append(self.createCommandsOnHost(cmd.getId(), 
                                                               atarget, 
                                                               first_target_id, 
                                                               target_name, 
                                                               max_connection_attempt, 
                                                               start_date,
                                                               end_date, 
                                                               ascheduler, 
                                                               order_in_proxy, 
                                                               max_clients_per_proxy))
                first_target_id = first_target_id + 1
            session.execute(self.commands_on_host.insert(), coh_to_insert)
            session.commit()

            return cmd.getId()

        d = self.getMachinesSchedulers(targets)
        if mode == 'push_pull':
            d.addCallback(cbGetTargetsMirrors)
        else:
            d.addCallback(cbPushModeCreateTargets)
        d.addErrback(lambda err: err)
        return d

    def applyCmdPatterns(self, cmd, patternActions = None):
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
                'do_reboot': "disable",
                'do_halt': self.config.web_def_issue_halt_to,
                'do_inventory': "disable",
                'do_wol': "disable",
            }

        if "@@do_reboot@@" in cmd:
            patternActions['do_reboot'] = "enable"
            cmd = cmd.replace("@@do_reboot@@", "")
        if "@@do_halt@@" in cmd:
            patternActions['do_halt'] = ["done"]
            cmd = cmd.replace("@@do_halt@@", "")
        if "@@do_inventory@@" in cmd:
            patternActions['do_inventory'] = "enable"
            cmd = cmd.replace("@@do_inventory@@", "")
        if "@@do_wol@@" in cmd:
            patternActions['do_wol'] = "enable"
            cmd = cmd.replace("@@do_wol@@", "")

        return [cmd, patternActions]

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

        cmd, patternActions = self.applyCmdPatterns(cmd)

        # run a built-in script
        p1 = re.compile('^\/scripts\/')
        if p1.match(cmd):
            files.append(cmd)

        return self.addCommand(
            ctx,
            None,
            cmd,
            "",
            files,
            targets,
            'push',
            gid,
            True,
            'enable',
            "0000-00-00 00:00:00",
            "0000-00-00 00:00:00",
            "root",     # FIXME: this should be the effective user we want to connect with
            desc,
            patternActions['do_halt'],
            patternActions['do_reboot'],
            patternActions['do_wol'],
            60,
            3,
            patternActions['do_inventory'],
            0,
            0,
            '',
            None,
            None,
            'none',
            []
        )

    def startBundle(self, fk_bundle):
        """
        Start a bundle. In fact we set all its related commands_on_host to the
        scheduled state, and set next_launch_date to immediately.
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        c_ids = select([self.commands.c.id], self.commands.c.fk_bundle == fk_bundle).execute()
        c_ids = map(lambda x:x[0], c_ids)
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands.in_(c_ids), self.commands_on_host.c.current_state != 'done', self.commands_on_host.c.current_state != 'failed')).execute(current_state = "scheduled", next_launch_date = "0000-00-00 00:00:00")
        trans.commit()

    def stopBundle(self, fk_bundle):
        """
        Stop a bundle, by stopping all its related commands_on_host.
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        c_ids = select([self.commands.c.id], self.commands.c.fk_bundle == fk_bundle).execute()
        c_ids = map(lambda x:x[0], c_ids)
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands.in_(c_ids), self.commands_on_host.c.current_state != 'done', self.commands_on_host.c.current_state != 'failed')).execute(current_state ="stopped", next_launch_date = "2031-12-31 23:59:59")
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands.in_(c_ids), self.commands_on_host.c.uploaded == 'WORK_IN_PROGRESS')).execute(uploaded = "FAILED")
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands.in_(c_ids), self.commands_on_host.c.executed == 'WORK_IN_PROGRESS')).execute(executed = "FAILED")
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands.in_(c_ids), self.commands_on_host.c.deleted == 'WORK_IN_PROGRESS')).execute(deleted = "FAILED")
        trans.commit()


    def pauseBundle(self, fk_bundle):
        """
        Pause a bundle, by pausing all its related commands_on_host.
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        c_ids = select([self.commands.c.id], self.commands.c.fk_bundle == fk_bundle).execute()
        c_ids = map(lambda x:x[0], c_ids)
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands.in_(c_ids),\
                self.commands_on_host.c.current_state != 'done',\
                self.commands_on_host.c.current_state != 'failed',\
                self.commands_on_host.c.current_state != 'stop',\
                self.commands_on_host.c.current_state != 'stopped'
                )).execute(current_state ="pause")
        trans.commit()

    def startCommand(self, c_id):
        """
        Start a command. In fact we set all its related commands_on_host to the
        scheduled state, and set next_launch_date to immediately.
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands == c_id, self.commands_on_host.c.current_state != 'done', self.commands_on_host.c.current_state != 'failed')).execute(current_state = "scheduled", next_launch_date = "0000-00-00 00:00:00")
        trans.commit()

    def stopCommand(self, c_id):
        """
        Stop a command, by stopping all its related commands_on_host.
        @returns: the list of all related commands_on_host
        @rtype: list
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands == c_id, self.commands_on_host.c.current_state != 'done', self.commands_on_host.c.current_state != 'failed')).execute(current_state = "stopped", next_launch_date = "2031-12-31 23:59:59")
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands == c_id, self.commands_on_host.c.uploaded == 'WORK_IN_PROGRESS')).execute(uploaded = "FAILED")
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands == c_id, self.commands_on_host.c.executed == 'WORK_IN_PROGRESS')).execute(executed = "FAILED")
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands == c_id, self.commands_on_host.c.deleted == 'WORK_IN_PROGRESS')).execute(deleted = "FAILED")
        trans.commit()

    def pauseCommand(self, c_id):
        """
        Pause a command, by pausing all its related commands_on_host.
        @returns: the list of all related commands_on_host
        @rtype: list
        """
        conn = self.getDbConnection()
        trans = conn.begin()
        self.commands_on_host.update(and_(self.commands_on_host.c.fk_commands == c_id,\
                self.commands_on_host.c.current_state != 'done',\
                self.commands_on_host.c.current_state != 'failed',\
                self.commands_on_host.c.current_state != 'stopped',\
                self.commands_on_host.c.current_state != 'stop'\
                )).execute(current_state = "pause")
        trans.commit()

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

