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

# Big modules
import logging
import re

# Twisted
from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor, defer

# Helpers
from mmc.support.mmctools import shLaunch, xmlrpcCleanup
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext

from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.pulse2.group import ComputerGroupManager
from mmc.plugins.msc.database import MscDatabase
from mmc.plugins.msc.config import MscConfig
from mmc.plugins.msc.qaction import qa_list_files
from mmc.plugins.msc.machines import Machines, Machine
import mmc.plugins.msc.actions
import mmc.plugins.msc.keychain
import mmc.plugins.msc.package_api

from mmc.plugins.msc.MSC_Directory import MSC_Directory
from mmc.plugins.msc.MSC_File import MSC_File

# XMLRPC client functions
import mmc.plugins.msc.client.scheduler

# ORM mappings
import mmc.plugins.msc.orm.commands_on_host

VERSION = '2.0.0'
APIVERSION = '0:0:0'
REVISION = int('$Rev$'.split(':')[1].strip(' $'))

def getVersion(): return VERSION
def getApiVersion(): return APIVERSION
def getRevision(): return REVISION

def activate():
    """
    Run some tests to ensure the module is ready to operate.
    """
    config = MscConfig("msc")
    logger = logging.getLogger()
    if config.disabled:
        logger.warning("Plugin msc: disabled by configuration.")
        return False

    if not os.path.isdir(config.qactionspath):
        logger.error("Quick Actions config is invalid: %s is not a directory. Please check msc.ini." % config.qactionspath)
        return False

    MscDatabase().activate()
    if not MscDatabase().db_check():
        return False

    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

##
# config
##
def getRepositoryPath():
    return xmlrpcCleanup(mmc.plugins.msc.MscConfig("msc").repopath)

##
# msc_script
##
def msc_script_list_file():
    return qa_list_files()

##
# exec
##
def msc_exec(command):
    return xmlrpcCleanup(mmc.plugins.msc.actions.msc_exec(command))

def msc_ssh(user, ip, command):
    return xmlrpcCleanup(mmc.plugins.msc.actions.msc_ssh(user, ip, command))

def msc_scp(user, ip, source, destination):
    return xmlrpcCleanup(mmc.plugins.msc.actions.msc_scp(user, ip, source, destination))

class RpcProxy(RpcProxyI):
    ##
    # machines
    ##
    def getMachine(self, params):
        ctx = self.currentContext
        return xmlrpcCleanup2(Machines().getMachine(ctx, params))

    ##
    # commands
    ##
    def dispatch_all_commands(self):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().dispatchAllCommands(ctx))

    ############ Scheduler driving
    def scheduler_start_all_commands(self, scheduler):
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.start_all_commands(scheduler))

    def scheduler_ping_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
        try: # FIXME: dirty bugfix, should be factorized upstream
            computer[1]['fullname']
        except KeyError:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.ping_client(scheduler, computer))

    def scheduler_probe_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
        try: # FIXME: dirty bugfix, should be factorized upstream
            computer[1]['fullname']
        except KeyError:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.probe_client(scheduler, computer))

    def pa_adv_countAllPackages(self, filt):
        ctx = self.currentContext
        return len(_adv_getAllPackages(ctx, filt))

    def pa_adv_getAllPackages(self, filt, start, end):
        ctx = self.currentContext
        return xmlrpcCleanup(_adv_getAllPackages(ctx, filt)[int(start):int(end)])

    ##
    # commands
    ##
    def add_command_quick(self, cmd, target, desc, gid = None):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().addCommandQuick(ctx, cmd, target, desc, gid))

    def add_command_api(self, pid, target, params, p_api, gid = None):
        ctx = self.currentContext
        return xmlrpcCleanup(mmc.plugins.msc.package_api.send_package_command(ctx, pid, target, params, p_api, gid))
        
    def get_id_command_on_host(self, id_command):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getIdCommandOnHost(ctx, id_command))
    
    def count_all_commands_on_group(self, gid, filt = '', history = None):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countAllCommandsOnGroup(ctx, gid, filt, history))
    
    def get_all_commands_on_group(self, gid, min, max, filt = '', history = None):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsOnGroup(ctx, gid, min, max, filt, history))
    
    def count_all_commands_on_host_group(self, gid, cmd_id, filt = '', history = None):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countAllCommandsOnHostGroup(ctx, gid, cmd_id, filt, history))
    
    def get_all_commands_on_host_group(self, gid, cmd_id, min, max, filt = '', history = None):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getAllCommandsOnHostGroup(ctx, gid, cmd_id, min, max, filt, history))
    
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
    
    def count_finished_commands_on_host(self, uuid, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countFinishedCommandsOnHost(ctx, uuid, filt))
    
    def get_finished_commands_on_host(self, uuid, min, max, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getFinishedCommandsOnHost(ctx, uuid, min, max, filt))
    
    def count_unfinished_commands_on_host(self, uuid, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().countUnfinishedCommandsOnHost(ctx, uuid, filt))
    
    def get_unfinished_commands_on_host(self, uuid, min, max, filt = ''):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().getUnfinishedCommandsOnHost(ctx, uuid, min, max, filt))
    
    def get_commands_on_host(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandsOnHost(ctx, coh_id))
    
    def get_target_for_coh(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getTargetForCoh(ctx, coh_id))
    
    def get_commands_history(self, coh_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommandsHistory(ctx, coh_id))
    
    def get_commands(self, cmd_id):
        ctx = self.currentContext
        return xmlrpcCleanup2(MscDatabase().getCommands(ctx, cmd_id))
    
##
# machines
##
def getPlatform(uuid):
    return xmlrpcCleanup2(Machine(uuid).getPlatform())

def pingMachine(uuid):
    return xmlrpcCleanup2(Machine(uuid).ping())

### Commands on host handling ###
def start_command_on_host(coh_id):
    mmc.plugins.msc.orm.commands_on_host.startCommandOnHost(coh_id)
    return xmlrpcCleanup(True)
def pause_command_on_host(coh_id):
    mmc.plugins.msc.orm.commands_on_host.togglePauseCommandOnHost(coh_id)
    return xmlrpcCleanup(True)
def restart_command_on_host(coh_id):
    mmc.plugins.msc.orm.commands_on_host.restartCommandOnHost(coh_id)
    return xmlrpcCleanup(True)
def stop_command_on_host(coh_id):
    mmc.plugins.msc.orm.commands_on_host.stopCommandOnHost(coh_id)
    return xmlrpcCleanup(True)
### Command on host handling ###

def start_all_commands():
    # well, a little dry are we ?
    MscDatabase().startAllCommands()
    return xmlrpcCleanup(True)

##
# common
##
def get_keychain():
    return xmlrpcCleanup(mmc.plugins.msc.keychain.get_keychain())

###
## scheduler
###
#
#def scheduler_add_command_quick(cmd, hosts, desc):
#    scheduler = MSC_Scheduler(DATABASE)
#    return scheduler.add_command_quick(cmd, hosts, desc)
#
#def scheduler_add_command(start_file, parameters, path_destination, path_source, files, target, create_directory_enable, start_script_enable, delete_file_after_execute_successful_enable, start_date, end_date, username, webmin_username, title, wake_on_lan_enable, next_connection_delay, max_connection_attempt, start_inventory_enable, repeat):
#    scheduler = MSC_Scheduler(DATABASE)
#    return scheduler.add_command(start_file, parameters, path_destination, path_source, files, target, create_directory_enable, start_script_enable, delete_file_after_execute_successful_enable, start_date, end_date, username, webmin_username, title, wake_on_lan_enable, next_connection_delay, max_connection_attempt, start_inventory_enable, repeat)
#
#def scheduler_dispatch_all_commands():
#    scheduler = MSC_Scheduler(DATABASE)
#    scheduler.dispatch_all_commands()
#    return ''
#
#def scheduler_start_all_commands():
#    scheduler = MSC_Scheduler(DATABASE)
#    scheduler.start_all_commands()
#    return ''
#
#def scheduler_get_id_command_on_host(id_command):
#    scheduler = MSC_Scheduler(DATABASE)
##    msc_exec('echo "`date` '+str(id_command)+'" > /tmp/log')
#    return scheduler.get_id_command_on_host(id_command)
#
#def command_detail(id_command):
#    command = MSC_Scheduler_Command(id_command, DATABASE)
#    return xmlrpcCleanup(command.command_detail())
#
#def command_hosts(id_command):
#    command = MSC_Scheduler_Command(id_command, DATABASE)
#    return xmlrpcCleanup(command.command_hosts())
#
#def get_command(id_command):
#    command = MSC_Scheduler_Command(id_command)
#    return xmlrpcCleanup(command.to_h())
#
#def count_commands_filter(target_filter):
#    return xmlrpcCleanup(mmc.plugins.msc.commands.count_commands_filter(target_filter))
#
#def command_list_filter(target_filter, page, number_command_by_page):
#    return xmlrpcCleanup(mmc.plugins.msc.commands.command_list_filter(target_filter, page, number_command_by_page))
#
#def get_number_host_of_command(id_command):
#    return xmlrpcCleanup(mmc.plugins.msc.scheduler.get_number_host_of_command(id_command))
#
#def get_state_of_command(id_command):
#    return xmlrpcCleanup(mmc.plugins.msc.scheduler.get_state_of_command(id_command))
#
#def get_commands_on_host(id_command_on_host):
#    return xmlrpcCleanup(mmc.plugins.msc.commands_on_host_facade.get_commands_on_host(id_command_on_host))
#
#def get_command_history(id_command_on_host):
#    command_on_host = commands_on_host.MSC_Scheduler_Command_on_Host(id_command_on_host)
#    return xmlrpcCleanup(command_on_host.command_history())
#
#def count_all_commands_on_host(hostname):
#    return mmc.plugins.msc.commands_on_host_facade.count_all_commands_on_host(hostname)
#
#def get_all_commands_on_host(hostname, page, number_command_by_page):
#    return xmlrpcCleanup(mmc.plugins.msc.commands_on_host_facade.get_all_commands_on_host(hostname, page, number_command_by_page))
#
#def get_targets():
#    return xmlrpcCleanup(mmc.plugins.msc.commands.get_targets())
#
#def count_commands_with_filter(filter):
#    return xmlrpcCleanup(mmc.plugins.msc.commands.count_commands_with_filter(filter))
#
#def get_command_list(filter, page, number_command_by_page):
#    return xmlrpcCleanup(mmc.plugins.msc.commands.get_command_list(filter, page, number_command_by_page))
#
##OLIVIERdef get_session(mac, user = "", ping_enable = True, os_type = "", home = ""):
#def get_session(name, user = "", ping_enable = True, os_type = "", home = ""):
##OLIVIER    session = mmc.plugins.msc.session.Session(mac, user, ping_enable, os_type, home)
#    session = mmc.plugins.msc.session.Session(name, user, ping_enable, os_type, home)
#    return xmlrpcCleanup(session.to_h())
#
#def getRepositoryPath():
#    return xmlrpcCleanup(mmc.plugins.msc.MscConfig("msc").repopath)
#
#def msc_command_set_play(id_command_play):
#    return xmlrpcCleanup(commands.msc_command_set_play(id_command_play))
#
#def msc_command_set_pause(id_command_pause):
#    return xmlrpcCleanup(commands.msc_command_set_pause(id_command_pause))
#
#def msc_command_set_stop(id_command_stop):
#    return xmlrpcCleanup(commands.msc_command_set_stop(id_command_stop))
#
#def msc_command_on_host_set_play(id_command_play):
#    return xmlrpcCleanup(commands_on_host_facade.msc_command_on_host_set_play(id_command_play))
#
#def msc_command_on_host_set_pause(id_command_pause):
#    return xmlrpcCleanup(commands_on_host_facade.msc_command_on_host_set_pause(id_command_pause))
#
#def msc_command_on_host_set_stop(id_command_stop):
#    return xmlrpcCleanup(commands_on_host_facade.msc_command_on_host_set_stop(id_command_stop))
#
##############################
import os
def file_exists(filename):
    return os.path.exists(filename)

def is_dir(filename):
    return os.path.isdir(filename)

#############################
################# Package API
from mmc.plugins.msc.package_api import PackageA

def pa_getAllPackages(p_api, mirror):
    return PackageA(p_api).getAllPackages(mirror)

def pa_getPackageDetail(p_api, pid):
    return PackageA(p_api).getPackageDetail(pid)

def pa_getPackageLabel(p_api, pid):
    return PackageA(p_api).getPackageLabel(pid)

def pa_getPackageVersion(p_api, pid):
    return PackageA(p_api).getPackageVersion(pid)

def pa_getPackageSize(p_api, pid):
    return PackageA(p_api).ps_getPackageSize(pid)

def pa_getPackageInstallInit(p_api, pid):
    return PackageA(p_api).getPackageInstallInit(pid)

def pa_getPackagePreCommand(p_api, pid):
    return PackageA(p_api).getPackagePreCommand(pid)

def pa_getPackageCommand(p_api, pid):
    return PackageA(p_api).getPackageCommand(pid)

def pa_getPackagePostCommandSuccess(p_api, pid):
    return PackageA(p_api).getPackagePostCommandSuccess(pid)

def pa_getPackagePostCommandFailure(p_api, pid):
    return PackageA(p_api).getPackagePostCommandFailure(pid)

def pa_getPackageFiles(p_api, pid):
    return PackageA(p_api).getPackageFiles(pid)

def pa_getFileChecksum(p_api, file):
    return PackageA(p_api).getFileChecksum(file)

def pa_getPackagesIds(p_api, label):
    return PackageA(p_api).getPackagesIds(label)

def pa_getPackageId(p_api, label, version):
    return PackageA(p_api).getPackageId(label, version)

def pa_isAvailable(p_api, pid, mirror):
    return PackageA(p_api).isAvailable(pid, mirror)

#############################
def _p_apiuniq(list, x):
  try:
    if list.index(x) == -1:
      pass
  except:
    print "no "+str(x)+" in lis"
    list.append(x)

def _merge_list(list, x):
    for i in x:
      try:
        list.index(i)
      except:
        pass
    rem = []
    for i in list:
      try:
        x.index(i)
      except:
        rem.append(i)
    for i in rem:
      list.remove(i)

def _adv_getAllPackages(ctx, filt):
    packages = []
    try:
        if filt['uuid']:
            machine = filt['uuid'] # TODO : get machine from uuid
            package_apis = ma_getApiPackage(machine)
            mirror = ma_getMirror(machine)
            x = 0
            for p_api in package_apis:
                packages.extend(map(lambda m: [m, x, p_api], pa_getAllPackages(p_api, mirror)))
                x += 1
    except KeyError:
        pass
    except Exception, e:
        logging.getLogger().error("Cant connect to mirror api")
        logging.getLogger().debug(e)
        return []
    try:
        if filt['group']: # TODO : manage groups with objects
            gid = filt['group']
            machines = []
            if ComputerGroupManager().isdyn_group(ctx, gid):
                if ComputerGroupManager().isrequest_group(ctx, gid):
                    machines = map(lambda m: m['uuid'], ComputerGroupManager().requestresult_group(ctx, gid, 0, -1, ''))
                else:
                    machines = map(lambda m: m.uuid, ComputerGroupManager().result_group(ctx, gid, 0, -1, ''))
            else:
                machines = map(lambda m: m.uuid, ComputerGroupManager().result_group(ctx, gid, 0, -1, ''))

            # TODO split uuid and name
            #machines = filt['group'].split("##")
            logging.getLogger().debug("getApiPackages")
            logging.getLogger().debug(machines)
            package_apis = ma_getApiPackages(machines)
            logging.getLogger().debug("getMirrors")
            mirror = ma_getMirrors(machines)

            # TODO check all the levels, not only the 2 first ones...
            mergedlist = []
            for i in range(len(package_apis)):
                mergedlist.insert(i, [(package_apis[i][0], mirror[i]), (package_apis[i][1],  mirror[i])])

            plist0 = []
            plist1 = []
            map(lambda x: _p_apiuniq(plist0, x[0]), mergedlist)
            map(lambda x: _p_apiuniq(plist1, x[1]), mergedlist)

            logging.getLogger().debug(plist0)
            logging.getLogger().debug(plist1)

            x = 0
            localepackages = []
            for p_api in plist0:
                localepackages.append(pa_getAllPackages(p_api[0], p_api[1]))

            # HERE is a possible source of bugs... we only remember one of the p_api, so if they aren't synchrones, it can be a pb...
            lp = localepackages[0]
            map(lambda x: _merge_list(lp, x), localepackages)
            packages.extend(map(lambda m: [m, x, plist0[0][0]], lp))

            x += 1
            localepackages = []
            for p_api in plist1:
                localepackages.append(pa_getAllPackages(p_api[0], p_api[1]))

            logging.getLogger().debug(localepackages)
            lp = localepackages[0]
            map(lambda x: _merge_list(lp, x), localepackages)
            packages.extend(map(lambda m: [m, x, plist1[0][0]], lp))

    except KeyError:
        pass
    try:
        if filt['filter']:
            packages = filter(lambda p: re.search(filt['filter'], p[0]['label']), packages)
    except KeyError:
        pass

    # sort on the mirror order then on the label, and finally on the version number
    packages.sort(lambda x, y: 10*cmp(x[1], y[1]) + 5*cmp(x[0]['label'], y[0]['label']) + cmp(x[0]['version'], y[0]['version']))

    return packages

#############################
################# Mirrors API
from mmc.plugins.msc.mirror_api import MirrorApi

def ma_getMirror(machine):
    return MirrorApi().getMirror(machine)

def ma_getMirrors(machines):
    return MirrorApi().getMirrors(machines)

def ma_getFallbackMirror(machine):
    return MirrorApi().getFallbackMirror(machine)

def ma_getFallbackMirrors(machines):
    return MirrorApi().getFallbackMirrors(machines)

def ma_getApiPackage(machine):
    return MirrorApi().getApiPackage(machine)

def ma_getApiPackages(machines):
    return MirrorApi().getApiPackages(machines)

############ MSC_Directory
def repo_directory_scan(directory_path, mime_types_data):
    dir = MSC_Directory(directory_path, mime_types_data)
    dir.scan()
    return dir.array_files

def repo_directory_get_parent(directory_path):
    dir = MSC_Directory(directory_path)
    return dir.get_parent()

def repo_directory_make_directory(directory_path):
    dir = MSC_Directory(directory_path)
    return dir.make_directory()

def repo_directory_delete_directory(directory_path):
    dir = MSC_Directory(directory_path)
    return dir.delete_directory()

def repo_directory_get_directory_only(directory_path):
    dir = MSC_Directory(directory_path)
    return xmlrpcCleanup(dir.get_directory_only())

def repo_directory_get_file_only(directory_path):
    dir = MSC_Directory(directory_path)
    return xmlrpcCleanup(dir.get_file_only())

def repo_directory_show_in_ascii(directory_path):
    dir = MSC_Directory(directory_path)
    return dir.show_in_ascii()

#############################
############ MSC_File
def repo_file_get_content(filename):
    file = MSC_File(filename)
    return file.get_content()

def repo_file_write_content(filename, content):
    file = MSC_File(filename)
    return file.write_content(content)

def repo_file_download(filename, mimetypes = {'':''}):
    file = MSC_File(filename, mimetypes)
    return file.download()

def repo_file_download_to_local_host(filename, path_source):
    file = MSC_File(filename)
    return file.download_to_local_host(path_source)

def repo_file_create(filename):
    file = MSC_File(filename)
    return file.create()

def repo_file_remove(filename):
    file = MSC_File(filename)
    return file.remove()

def repo_file_rename(filename, new_name):
    file = MSC_File(filename)
    return file.rename()

def repo_file_execute(filename):
    file = MSC_File(filename)
    return file.execute()

def repo_file_upload(filename, file_to_upload):
    file = MSC_File(filename)
    return file.upload(file_to_upload)

#############################
def file_exists(filename):
    return os.path.exists(filename)

def is_dir(filename):
    return os.path.isdir(filename)

############# Scheduler driving
#def scheduler_start_all_commands(scheduler):
#    return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.start_all_commands(scheduler))
#
#def scheduler_ping_client(scheduler, client_uuid):
#    return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.ping_client(scheduler, client))
#
#def scheduler_probe_client(scheduler, client):
#    return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.probe_client(scheduler, client))
#
############ /Scheduler driving

def xmlrpcCleanup2(obj):
    try:
        return xmlrpcCleanup(obj.toH())
    except:
        return xmlrpcCleanup(obj)
