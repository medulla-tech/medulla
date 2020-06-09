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
Class to manage msc mmc-agent plugin
"""

# Big modules
import logging
import time
import datetime
import re
import os

# Twisted
from twisted.internet import defer

# Helpers
from mmc.support.mmctools import xmlrpcCleanup
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.base import LdapUserGroupControl

from mmc.core.tasks import TaskManager
from mmc.plugins.base.computers import ComputerManager
from pulse2.managers.group import ComputerGroupManager
from pulse2.managers.location import ComputerLocationManager
from mmc.plugins.msc.database import MscDatabase
from mmc.plugins.msc.config import MscConfig
from mmc.plugins.msc.machines import Machines, Machine
from mmc.plugins.dyngroup.database import DyngroupDatabase
from mmc.plugins.dyngroup.config import DGConfig
import mmc.plugins.msc.actions
import mmc.plugins.msc.keychain
import mmc.plugins.msc.package_api

# XMLRPC client functions
import mmc.plugins.msc.client.scheduler

# ORM mappings
import pulse2.database.msc.orm.commands_on_host

from pulse2.version import getVersion, getRevision # pyflakes.ignore
from pulse2.utils import noNoneList

APIVERSION = '0:0:0'

NOAUTHNEEDED = [
    'get_web_def_coh_life_time',
    'get_web_def_attempts_per_day',
    'pull_target_awake',
    'is_pull_target',
    'checkLightPullCommands',
    'start_command_on_host',
]

def getApiVersion(): return APIVERSION

def activate():
    """
    Run some tests to ensure the module is ready to operate.
    """
    config = MscConfig()
    config.init("msc")
    logger = logging.getLogger()
    if config.disable:
        logger.warning("Plugin msc: disabled by configuration.")
        return False

    if not os.path.isdir(config.qactionspath):
        logger.error("Quick Actions config is invalid: %s is not a directory. Please check msc.ini." % config.qactionspath)
        return False

    if not MscDatabase().activate(config):
        return False

    if config.check_db_enable:
        scheduleCheckStatus(config.check_db_interval)

    # Add convergence reschedule task in the task manager
    TaskManager().addTask("msc.convergence_reschedule",
                          (convergence_reschedule,),
                          cron_expression=config.convergence_reschedule)
    return True

def activate_2():
    conf = MscConfig()
    conf.init('msc')
    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        s.locationsCount = ComputerLocationManager().getLocationsCount()
        s.userids = ComputerLocationManager().getUsersInSameLocations(self.userid)
        s.filterType = "mine"
        return s

##
# config
##
def getRepositoryPath():
    return xmlrpcCleanup(MscConfig().repopath)

class RpcProxy(RpcProxyI):
    ##
    # machines
    ##
    def getMachine(self, params):
        ctx = self.currentContext
        return xmlrpcCleanup2(Machines().getMachine(ctx, params))

    def scheduler_choose_client_ip(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid}, True)
        network = computer[1]

        interfaces = {"uuid"      : uuid,
                      "fqdn"      : network["cn"][0],
                      "shortname" : network["cn"][0],
                      "ips"       : noNoneList(network["ipHostNumber"]),
                      "macs"      : noNoneList(network["macAddress"]),
                      "netmasks"  : noNoneList(network["subnetMask"]),
                      }
        result = xmlrpcCleanup2(mmc.plugins.msc.client.scheduler.choose_client_ip(scheduler, interfaces))
        return xmlrpcCleanup2(mmc.plugins.msc.client.scheduler.choose_client_ip(scheduler, interfaces))


    ##
    # commands
    ##

    ############ Scheduler driving
    def scheduler_start_all_commands(self, scheduler):
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.start_all_commands(scheduler))

    def scheduler_start_these_commands(self, scheduler, commands):
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.start_these_commands(scheduler, commands))

    def scheduler_ping_and_probe_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid}, True)
        if not 'fullname' in computer[1]:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return mmc.plugins.msc.client.scheduler.ping_and_probe_client(scheduler, computer)

    def scheduler_ping_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid}, True)
        if not 'fullname' in computer[1]:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.ping_client(scheduler, computer))

    def scheduler_probe_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid}, True)
        if not 'fullname' in computer[1]:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.probe_client(scheduler, computer))

    def can_download_file(self):
        path = MscConfig().web_dlpath
        return (len(path) > 0) and os.path.exists(MscConfig().download_directory_path)

    def download_file(self, uuid):
        path = MscConfig().web_dlpath
        ctx = self.currentContext
        if not path:
            ret = False
        else:
            bwlimit = MscConfig().web_def_dlmaxbw
            ctx = self.currentContext
            computer = ComputerManager().getComputer(ctx, {'uuid': uuid}, True)
            try: # FIXME: dirty bugfix, should be factorized upstream
                computer[1]['fullname']
            except KeyError:
                computer[1]['fullname'] = computer[1]['cn'][0]
            mscdlp = MscDownloadProcess(ctx.userid, computer, path, bwlimit)
            ret = mscdlp.startDownload()
        return ret

    def get_downloaded_files_list(self):
        mscdlfiles = MscDownloadedFiles(self.currentContext.userid)
        return mscdlfiles.getFilesList()

    def get_downloaded_file(self, node):
        mscdlfiles = MscDownloadedFiles(self.currentContext.userid)
        return mscdlfiles.getFile(node)

    def remove_downloaded_files(self, ids):
        mscdlfiles = MscDownloadedFiles(self.currentContext.userid)
        mscdlfiles.removeFiles(ids)

    def establish_vnc_proxy(self, scheduler, uuid, requestor_ip):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid}, True)
        try: # FIXME: dirty bugfix, should be factorized upstream
            computer[1]['fullname']
        except KeyError:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.tcp_sproxy(scheduler, computer, requestor_ip, MscConfig().web_vnc_port))

    ##
    # commands management
    ##
    def add_command_quick_with_id(self, idcmd, target, lang, gid = None):
        """
        @param idcmd: id of the quick action
        @type idcmd: str

        @param target: targets, list of computers UUIDs
        @type target: list

        @param lang: language to use for the command title (two characters)
        @type lang: str

        @param gid: if not None, apply command to a group of machine
        @type gid: str
        """
        ctx = self.currentContext
        result, qas = qa_list_files()
        if result and idcmd in qas:
            try:
                desc = qas[idcmd]["title" + lang]
            except KeyError:
                desc = qas[idcmd]["title"]
            if gid:
                # Get all targets corresponding to the computer given group ID
                target = ComputerGroupManager().get_group_results(ctx, gid, 0, -1, '', True)
            # Use maybeDeferred because addCommandQuick will return an error
            # code in case of failure
            d = defer.maybeDeferred(MscDatabase().addCommandQuick, ctx, qas[idcmd]["command"], target, desc, gid)
            d.addCallback(xmlrpcCleanup)
            ret = d
        else:
            ret = -1
        return ret

    def getnotdeploybyuserrecent(self, login, time, min, max, filt):
        return MscDatabase().getnotdeploybyuserrecent(login, time, min, max, filt)

    def getContext(self, user='root'):
            s = SecurityContext()
            s.userid = user
            s.userdn = LdapUserGroupControl().searchUserDN(s.userid)
            return s

    def add_command_api(self, pid, target, params, mode, gid = None, proxy = [], cmd_type = 0):
        """
        @param target: must be list of UUID
        @type target: list
        """
        ctx = self.currentContext
        if gid:
            grp = DyngroupDatabase().get_group(self.getContext(), gid)
            # If convergence group, get context of group's owner
            if grp.type == 2:
                _group_user = DyngroupDatabase()._get_group_user(grp.parent_id)
                ctx = self.getContext(user=_group_user)
            target = ComputerGroupManager().get_group_results(ctx, gid, 0, -1, '', True)
        return mmc.plugins.msc.package_api.SendPackageCommand(ctx, pid, target, params, mode, gid, proxies = proxy, cmd_type = cmd_type).send()

    def get_id_command_on_host(self, id_command):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getIdCommandOnHost(ctx, id_command))

    def get_msc_listhost_commandid(self, command_id):
        return xmlrpcCleanup(MscDatabase().get_msc_listhost_commandid(command_id))

    def get_msc_listuuid_commandid(self, command_id, filter, start, end):
        return xmlrpcCleanup(MscDatabase().get_msc_listuuid_commandid(command_id, filter, start, end))

    def get_deployxmppscheduler(self,login,  nin, max, filt):
        return xmlrpcCleanup(MscDatabase().deployxmppscheduler(login, nin, max, filt))

    def get_deployxmpponmachine(self, command_id):
        return xmlrpcCleanup(MscDatabase().deployxmpponmachine(command_id))

    def get_count_timeout_wol_deploy(self, command_id, date_start):
        return xmlrpcCleanup(MscDatabase().get_count_timeout_wol_deploy(command_id, date_start))

    def expire_all_package_commands(self, pid):
        """
        Expires all commands of a given package
        Used usually when a package is dropped

        @param pid: uuid of dropped package
        @type pid: uuid
        """
        # get all cmd_ids with their start_date  of given package id
        cmds = MscDatabase().get_package_cmds(pid)

        if cmds:
            logging.getLogger().info('%d command will be expired' % len(cmds))

            # for all cmd_ids, get start_date and expire them
            for cmd_id, start_date in cmds.items():
                logging.getLogger().info('Expires command %d' % cmd_id)
                end_date = time.strftime("%Y-%m-%d %H:%M:%S")

            # Delete convergence groups if any
            DyngroupDatabase().delete_package_convergence(pid)
        return True

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
        MscDatabase().extend_command(cmd_id, start_date, end_date)

    def delete_command(self, cmd_id):
        """
        Deletes a command with all related sub-elements.

        @param cmd_id: Commands id
        @type cmd_id: int
        """
        return MscDatabase().deleteCommand(cmd_id)


    def delete_command_on_host(self, coh_id):
        """
        Deletes a command on host with all related sub-elements.

        @param coh_id: CommandsOnHost id
        @type coh_id: int
        """
        return MscDatabase().deleteCommandOnHost(coh_id)


    def get_commands_by_group(self, grp_id):
        return MscDatabase().getCommandsByGroup1(grp_id)


    def is_pull_target(self, uuid):
        """
        Returns True if the machine is a known pull client

        @param uuid: computer UUID
        @type uuid: str

        @return: bool
        """
        return xmlrpcCleanup(MscDatabase().isPullTarget(uuid))

    def get_pull_targets(self):
        """
        Returns list of Pull target UUIDs

        @return: list
        """
        return xmlrpcCleanup(MscDatabase().getPullTargets())

    def remove_pull_targets(self, uuids):
        """
        remove pull targets
        @param uuids: a list of uuids to remove
        @type uuids: list or str

        @return: True or False :-)
        """
        if isinstance(uuids, basestring):
            uuids = [uuids]
        return xmlrpcCleanup(MscDatabase().removePullTargets(uuids))

    def pull_target_awake(self, hostname, macs):
        """
        Gets the requested machine for UUID.

        @param hostname: hostname of computer
        @type hostname: str

        @param macs: MAC addresses of computer
        @type macs: list

        @return: UUID
        @rtype: str
        """
        ctx = self.currentContext
        return xmlrpcCleanup(ComputerManager().getComputerByHostnameAndMacs(ctx,
                                                                            hostname,
                                                                            macs))

    def checkLightPullCommands(self, uuid):
        """
        Returns all coh ids te re-execute.

        @param uuid: uuid of checked computer
        @type uuid: str

        @return: coh ids to start
        @rtype: list
        """
        return xmlrpcCleanup(MscDatabase().checkLightPullCommands(uuid))


    def displayLogs(self, params = {}):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().displayLogs(ctx, params))

    def get_all_commands_for_consult(self, min = 0, max = 10, filt = '', expired = True):
        ctx = self.currentContext
        size, ret1 = MscDatabase().getAllCommandsConsult(ctx, min, max, filt, expired)
        ret = []
        logger = logging.getLogger()
        cache = {}
        for c in ret1:
            if c['gid']:
                if cache.has_key("G%s"%(c['gid'])):
                #if "G%s"%(c['gid']) in cache:
                    c['target'] = cache["G%s"%(c['gid'])]
                else:
                    group = DyngroupDatabase().get_group(ctx, c['gid'], True)
                    if type(group) == bool: # we dont have the permission to view the group
                        c['target'] = 'UNVISIBLEGROUP' # TODO!
                    elif group == None:
                        c['target'] = 'this group has been deleted'
                    elif hasattr(group, 'ro') and group.ro:
                        logger.debug("user %s access to group %s in RO mode"%(ctx.userid, group.name))
                        c['target'] = group.name
                    else:
                        c['target'] = group.name
                    cache["G%s"%(c['gid'])] = c['target']
            else:
                if cache.has_key("M%s"%(c['uuid'])):
                #if "M%s"%(c['uuid']) in cache:
                    c['target'] = cache["M%s"%(c['uuid'])]
                else:
                    if not ComputerLocationManager().doesUserHaveAccessToMachine(ctx, c['uuid']):
                        c['target'] = "UNVISIBLEMACHINE"
                    elif not ComputerManager().getComputer(ctx, {'uuid':c['uuid']}):
                        c['target'] = "UNVISIBLEMACHINE"
                    cache["M%s"%(c['uuid'])] = c['target']
            # treat c['title'] to remove the date when possible
            # "Bundle (1) - 2009/12/14 10:22:24" => "Bundle (1)"
            date_re = re.compile(" - \d\d\d\d/\d\d/\d\d \d\d:\d\d:\d\d")
            c['title'] = date_re.sub('', c['title'])
            ret.append(c)
        return xmlrpcCleanup((size, ret))

    def updategroup(self, grp_id):
        return MscDatabase().updategroup(grp_id)

    def get_all_commandsonhost_currentstate(self):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsonhostCurrentstate(ctx))

    def count_all_commandsonhost_by_currentstate(self, current_state, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countAllCommandsonhostByCurrentstate(ctx, current_state, filt))

    def get_all_commandsonhost_by_currentstate(self, current_state, min = 0, max = 10, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsonhostByCurrentstate(ctx, current_state, min, max, filt))

    def count_all_commandsonhost_by_type(self, type = 0, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countAllCommandsonhostByType(ctx, type, filt))

    def get_all_commandsonhost_by_type(self, type, min, max, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsonhostByType(ctx, type, min, max, filt))

    def count_all_commands_on_host(self, uuid, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countAllCommandsOnHost(ctx, uuid, filt))

    def get_all_commands_on_host(self, uuid, min, max, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsOnHost(ctx, uuid, min, max, filt))

    def get_commands_on_host(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandsOnHost(ctx, coh_id))

    def get_target_for_coh(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getTargetForCoh(ctx, coh_id))

    def get_targets_for_coh(self, coh_ids):
        ctx = self.currentContext
        result = MscDatabase().getTargetsForCoh(ctx, coh_ids)
        return [xmlrpcCleanup2(x) for x in result]

    def get_commands_history(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandsHistory(ctx, coh_id))

    def get_commands(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommands(ctx, cmd_id))

    def is_commands_convergence_type(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().isCommandsCconvergenceType(ctx, cmd_id))

    def is_array_commands_convergence_type(self, array_cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().isArrayCommandsCconvergenceType(ctx, array_cmd_id))

    def get_command_on_group_status(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandOnGroupStatus(ctx, cmd_id))

    def get_command_on_group_by_state(self, cmd_id, state, min = 0, max = -1):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandOnGroupByState(ctx, cmd_id, state, min, max))

    def get_command_on_host_title(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandOnHostTitle(ctx, cmd_id))

    def get_command_on_host_in_commands(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandOnHostInCommands(ctx, cmd_id))

    def getstatbycmd(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getstatbycmd(ctx, cmd_id))

    def getarraystatbycmd(self, arraycmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getarraystatbycmd(ctx, arraycmd_id))

    def get_first_commands_on_cmd_id(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getFirstCommandsOncmd_id(ctx, cmd_id))

    def get_last_commands_on_cmd_id(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getLastCommandsOncmd_id(ctx, cmd_id))

    def get_last_commands_on_cmd_id_start_end(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getLastCommandsOncmd_id_start_end(ctx, cmd_id))

    def get_array_last_commands_on_cmd_id_start_end(self, array_cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getarrayLastCommandsOncmd_id_start_end(ctx, array_cmd_id))

    def set_commands_filter(self, filterType):
        ctx = self.currentContext
        if not filterType in ['mine', 'all']:
            filterType = 'mine'
            logging.getLogger().error('msc.set_commands_filter called without valid parameter')
        ctx.filterType = filterType

    def get_commands_filter(self):
        ctx = self.currentContext
        return ctx.filterType

    def getMachineNamesOnGroupStatus(self, cmd_id, state):
        ctx = self.currentContext
        limit = DGConfig().maxElementsForStaticList
        return xmlrpcCleanup(MscDatabase().getMachineNamesOnGroupStatus(ctx, cmd_id, state, limit))

    def getMachineNamesOnBundleStatus(self, bundle_id, state):
        ctx = self.currentContext
        limit = DGConfig().maxElementsForStaticList
        return xmlrpcCleanup(MscDatabase().getMachineNamesOnBundleStatus(ctx, bundle_id, state, limit))

    #
    # default WEB values handling
    #
    def get_def_package_label(self, label, version):
        localtime = time.localtime()
        return "%s (%s) - %04d/%02d/%02d %02d:%02d:%02d" % (
            label,
            version,
            localtime[0],
            localtime[1],
            localtime[2],
            localtime[3],
            localtime[4],
            localtime[5]
        )

    def get_web_def_awake(self):
        return xmlrpcCleanup(MscConfig().web_def_awake)

    def get_web_def_date_fmt(self):
        return xmlrpcCleanup(MscConfig().web_def_date_fmt)

    def get_web_def_inventory(self):
        return xmlrpcCleanup(MscConfig().web_def_inventory)

    def get_web_def_reboot(self):
        return xmlrpcCleanup(MscConfig().web_def_reboot)

    def get_web_def_mode(self):
        return xmlrpcCleanup(MscConfig().web_def_mode)

    def get_web_def_force_mode(self):
        return xmlrpcCleanup(MscConfig().web_force_mode)

    def get_web_def_maxbw(self):
        return xmlrpcCleanup(MscConfig().web_def_maxbw)

    def get_web_def_delay(self):
        return xmlrpcCleanup(MscConfig().web_def_delay)

    def get_web_def_attempts(self):
        return xmlrpcCleanup(MscConfig().web_def_attempts)

    def get_web_def_deployment_intervals(self):
        return xmlrpcCleanup(MscConfig().web_def_deployment_intervals)

    def get_web_def_vnc_view_only(self):
        return xmlrpcCleanup(MscConfig().web_vnc_view_only)

    def get_web_def_vnc_show_icon(self):
        return xmlrpcCleanup(MscConfig().web_vnc_show_icon)

    def get_web_def_vnc_network_connectivity(self):
        return xmlrpcCleanup(MscConfig().web_vnc_network_connectivity)

    def get_web_def_vnc_allow_user_control(self):
        return xmlrpcCleanup(MscConfig().web_vnc_allow_user_control)

    def get_web_def_allow_local_proxy(self):
        return xmlrpcCleanup(MscConfig().web_allow_local_proxy)

    def get_web_def_local_proxy_mode(self):
        return xmlrpcCleanup(MscConfig().web_def_local_proxy_mode)

    def get_web_def_max_clients_per_proxy(self):
        return xmlrpcCleanup(MscConfig().web_def_max_clients_per_proxy)

    def get_web_def_proxy_number(self):
        return xmlrpcCleanup(MscConfig().web_def_proxy_number)

    def get_web_def_proxy_selection_mode(self):
        return xmlrpcCleanup(MscConfig().web_def_proxy_selection_mode)

    def get_web_def_issue_halt_to(self):
        return xmlrpcCleanup(MscConfig().web_def_issue_halt_to)

    def get_web_def_show_reboot(self):
        return xmlrpcCleanup(MscConfig().web_show_reboot)

    def get_web_def_probe_order(self):
        return xmlrpcCleanup(MscConfig().web_probe_order)

    def get_web_def_probe_order_on_demand(self):
        return xmlrpcCleanup(MscConfig().web_probe_order_on_demand)

    def get_web_def_refresh_time(self):
        return xmlrpcCleanup(MscConfig().web_def_refresh_time)

    def get_web_def_use_no_vnc(self):
        return xmlrpcCleanup(MscConfig().web_def_use_no_vnc)

    def get_web_def_coh_life_time(self):
        return xmlrpcCleanup(MscConfig().web_def_coh_life_time)

    def get_web_def_attempts_per_day(self):
        return xmlrpcCleanup(MscConfig().web_def_attempts_per_day)

    def get_web_def_allow_delete(self):
        return xmlrpcCleanup(MscConfig().web_def_allow_delete)


##
# machines
##
def getPlatform(uuid):
    return xmlrpcCleanup2(Machine(uuid).getPlatform())

def pingMachine(uuid):
    return xmlrpcCleanup2(Machine(uuid).ping())

### Commands on host handling ###
# FIXME: we should realy rationalize this stuff !
def start_command_on_host(coh_id):
    if pulse2.database.msc.orm.commands_on_host.startCommandOnHost(coh_id):
        mmc.plugins.msc.client.scheduler.startCommand(None, coh_id)
        return xmlrpcCleanup(True)
    else:
        return xmlrpcCleanup(False)

def pause_command_on_host(coh_id):
    pulse2.database.msc.orm.commands_on_host.togglePauseCommandOnHost(coh_id)
    return xmlrpcCleanup(True)
def restart_command_on_host(coh_id):
    pulse2.database.msc.orm.commands_on_host.restartCommandOnHost(coh_id)
    return xmlrpcCleanup(True)
def stop_command_on_host(coh_id):
    pulse2.database.msc.orm.commands_on_host.stopCommandOnHost(coh_id)
    mmc.plugins.msc.client.scheduler.stopCommand(None, coh_id)
    return xmlrpcCleanup(True)
### Command on host handling ###

def action_on_command(id, f_name, f_database, f_scheduler):
    # Update command in database
    getattr(MscDatabase(), f_database)(id)

def action_on_bundle(id, f_name, f_database, f_scheduler):
    # Update command in database
    getattr(MscDatabase(), f_database)(id)
    # Stop related commands_on_host on related schedulers
    scheds = MscDatabase().getCommandsonhostsAndSchedulersOnBundle(id)
    logger = logging.getLogger()
    for sched in scheds:
        d = getattr(mmc.plugins.msc.client.scheduler, f_scheduler)(sched, scheds[sched])
        d.addErrback(lambda err: logger.error("%s: " % (f_name) + str(err)))

### Commands handling ###
def stop_command(c_id):
    return action_on_command(c_id, 'stop_command', 'stopCommand', 'stopCommands')

def start_command(c_id):
    return action_on_command(c_id, 'start_command', 'startCommand', 'startCommands')

def pause_command(c_id):
    return action_on_command(c_id, 'pause_command', 'pauseCommand', 'pauseCommands')

def restart_command(c_id):
    return action_on_command(c_id, 'restart_command', 'restartCommand', 'restartCommands')
###

### Bundle handling ###
def stop_bundle(bundle_id):
    action_on_bundle(bundle_id, 'stop_bundle', 'stopBundle', 'stopCommands')
    return True

def start_bundle(bundle_id):
    action_on_bundle(bundle_id, 'start_bundle', 'startBundle', 'startCommands')
    return True

def pause_bundle(c_id):
    return action_on_bundle(c_id, 'pause_bundle', 'pauseBundle', 'pauseCommands')

def restart_bundle(c_id):
    return action_on_bundle(c_id, 'restart_bundle', 'restartBundle', 'restartCommands')
###

##
# common
##
def get_keychain():
    return xmlrpcCleanup(mmc.plugins.msc.keychain.get_keychain())

def file_exists(filename):
    return os.path.exists(filename)

def is_dir(filename):
    return os.path.isdir(filename)

#############################
################# Package API
from mmc.plugins.msc.package_api import PackageGetA

def pa_getAllPackages(p_api, mirror = None):
    return PackageGetA(p_api).getAllPackages(mirror)

def pa_getPackageDetail(p_api, pid):
    return PackageGetA(p_api).getPackageDetail(pid)

def pa_getPackageLabel(p_api, pid):
    return PackageGetA(p_api).getPackageLabel(pid)

def pa_getPackageVersion(p_api, pid):
    return PackageGetA(p_api).getPackageVersion(pid)

def pa_getPackageSize(p_api, pid):
    return PackageGetA(p_api).ps_getPackageSize(pid)

def pa_getPackageInstallInit(p_api, pid):
    return PackageGetA(p_api).getPackageInstallInit(pid)

def pa_getPackagePreCommand(p_api, pid):
    return PackageGetA(p_api).getPackagePreCommand(pid)

def pa_getPackageCommand(p_api, pid):
    return PackageGetA(p_api).getPackageCommand(pid)

def pa_getPackagePostCommandSuccess(p_api, pid):
    return PackageGetA(p_api).getPackagePostCommandSuccess(pid)

def pa_getPackagePostCommandFailure(p_api, pid):
    return PackageGetA(p_api).getPackagePostCommandFailure(pid)

def pa_getPackageHasToReboot(p_api, pid):
    return PackageGetA(p_api).getPackageHasToReboot(pid)

def pa_getPackageFiles(p_api, pid):
    return PackageGetA(p_api).getPackageFiles(pid)

def pa_getFileChecksum(p_api, file):
    return PackageGetA(p_api).getFileChecksum(file)

def pa_getPackagesIds(p_api, label):
    return PackageGetA(p_api).getPackagesIds(label)

def pa_getPackageId(p_api, label, version):
    return PackageGetA(p_api).getPackageId(label, version)

def pa_isAvailable(p_api, pid, mirror):
    return PackageGetA(p_api).isAvailable(pid, mirror)

#############################

def xmlrpcCleanup2(obj):
    try:
        return xmlrpcCleanup(obj.toH())
    except:
        return xmlrpcCleanup(obj)

#############################

def _get_convergence_soon_ended_commands(all=False):
    """
    @param all: If True, get all convergence active commands
    @type all: Bool

    @return: list of soon ended convergence commands
    @rtype: list
    """
    ret = []
    active_convergence_cmd_ids = DyngroupDatabase()._get_convergence_active_commands_ids()
    if all:
        # Return all active_convergence_cmd_ids
        return active_convergence_cmd_ids
    elif active_convergence_cmd_ids:
        # Get active_convergence_cmd_ids who are soon expired
        ret = MscDatabase()._get_convergence_soon_ended_commands(cmd_ids=active_convergence_cmd_ids)
    return xmlrpcCleanup(ret)

def _get_convergence_new_machines_to_add(ctx, cmd_id, convergence_deploy_group_id):
    ret = MscDatabase()._get_convergence_new_machines_to_add(ctx, cmd_id, convergence_deploy_group_id)
    return xmlrpcCleanup(ret)

def _add_machines_to_convergence_command(ctx, cmd_id, new_machine_ids, convergence_group_id, phases={}):
    return MscDatabase().addMachinesToCommand(ctx, cmd_id, new_machine_ids, convergence_group_id, phases=phases)

def _get_convergence_phases(cmd_id, deploy_group_id):
    return DyngroupDatabase()._get_convergence_phases(cmd_id, deploy_group_id)

def _force_command_type(cmd_id, type):
    return MscDatabase()._force_command_type(cmd_id, type)

def _set_command_ready(cmd_id):
    return MscDatabase()._set_command_ready(cmd_id)

def _update_convergence_dates(cmd_id):
    return MscDatabase()._update_convergence_dates(cmd_id)

def _get_machines_in_command(cmd_id):
    return MscDatabase()._get_machines_in_command(cmd_id)

def _get_convergence_deploy_group_id_and_user(cmd_id):
    return DyngroupDatabase()._get_convergence_deploy_group_id_and_user(cmd_id)

def getContext(user='root'):
        s = SecurityContext()
        s.userid = user
        s.userdn = LdapUserGroupControl().searchUserDN(s.userid)
        return s

def convergence_reschedule(all=False):
    """
    Check convergence commands who will be ended soon
    and re-schedule them

    @param all: If True, All convergence commands will be rescheduled
    @type all: Bool
    """
    logger = logging.getLogger()
    cmd_ids = _get_convergence_soon_ended_commands(all=all)
    if cmd_ids:
        logger.info("Convergence cron: %s convergence commands will be rescheduled: %s" % (len(cmd_ids), cmd_ids))
        for cmd_id in cmd_ids:
            try:
                convergence_deploy_group_id, user = _get_convergence_deploy_group_id_and_user(cmd_id)
                ctx = getContext(user=user)
                new_machine_ids = _get_convergence_new_machines_to_add(ctx, cmd_id, convergence_deploy_group_id)
                if new_machine_ids:
                    logger.info("%s machines will be added to convergence group %s" % (len(new_machine_ids), convergence_deploy_group_id))
                    phases = _get_convergence_phases(cmd_id, convergence_deploy_group_id)
                    _add_machines_to_convergence_command(ctx, cmd_id, new_machine_ids, convergence_deploy_group_id, phases=phases)
                _update_convergence_dates(cmd_id)
            except TypeError, e:
                logger.warn("Error while fetching deploy_group_id and user for command %s: %s" % (cmd_id, e))
    else:
        logger.info("Convergence cron: no convergence commands will be rescheduled")
