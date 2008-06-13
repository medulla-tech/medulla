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
import os

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

    ############ Scheduler driving
    def scheduler_start_all_commands(self, scheduler):
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.start_all_commands(scheduler))

    def scheduler_ping_and_probe_client(self, scheduler, uuid):
        ctx = self.currentContext
        computer = ComputerManager().getComputer(ctx, {'uuid': uuid})
        try: # FIXME: dirty bugfix, should be factorized upstream
            computer[1]['fullname']
        except KeyError:
            computer[1]['fullname'] = computer[1]['cn'][0]
        return xmlrpcCleanup(mmc.plugins.msc.client.scheduler.ping_and_probe_client(scheduler, computer))
            
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
    # commands management
    ##
    def add_command_quick(self, cmd, target, desc, gid = None):
        ctx = self.currentContext
        return xmlrpcCleanup(MscDatabase().addCommandQuick(ctx, cmd, target, desc, gid))

    def add_command_api(self, pid, target, params, p_api, mode, gid = None):
        ctx = self.currentContext
        return xmlrpcCleanup(mmc.plugins.msc.package_api.send_package_command(ctx, pid, target, params, p_api, mode, gid))

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

    #
    # default WEB values handling
    #
    def get_web_def_awake(self):
        return xmlrpcCleanup(MscConfig("msc").web_def_awake)

    def get_web_def_inventory(self):
        return xmlrpcCleanup(MscConfig("msc").web_def_inventory)

    def get_web_def_mode(self):
        return xmlrpcCleanup(MscConfig("msc").web_def_mode)

    def get_web_def_maxbw(self):
        return xmlrpcCleanup(MscConfig("msc").web_def_maxbw)

    def get_web_def_delay(self):
        return xmlrpcCleanup(MscConfig("msc").web_def_delay)

    def get_web_def_attempts(self):
        return xmlrpcCleanup(MscConfig("msc").web_def_attempts)

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
from mmc.plugins.msc.package_api import PackageA

def pa_getAllPackages(p_api, mirror = None):
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
    list.index(x)
  except:
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
        packages.extend(map(lambda m: [m, 0, filt['packageapi']], pa_getAllPackages(filt['packageapi'], False)))
    except KeyError:
        pass
    except Exception, e:
        logging.getLogger().error("Cant connect to package api")
        logging.getLogger().debug(e)
        return []
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
            package_apis = ma_getApiPackages(machines)
            mirror = ma_getMirrors(machines)
            
            mergedlist = []
            for i in range(len(package_apis)):
                tmpmerged = []
                for papi in package_apis[i]:
                    tmpmerged.append((papi, mirror[i]))
                mergedlist.insert(i, tmpmerged)

            plists = []
            for i in range(len(mergedlist[0])): # all line must have the same size!
                plists.insert(i, [])
                map(lambda x: _p_apiuniq(plists[i], x[i]), mergedlist)

            logging.getLogger().debug(plists)
            
            for x in range(len(plists)):
                localepackages = []
                for p_api in plists[x]:
                    localepackages.append(pa_getAllPackages(p_api[0], p_api[1]))

                lp = localepackages[0]
                map(lambda p: _merge_list(lp, p), localepackages)
                packages.extend(map(lambda m: [m, x, plists[x][0][0]], lp))
                
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

def xmlrpcCleanup2(obj):
    try:
        return xmlrpcCleanup(obj.toH())
    except:
        return xmlrpcCleanup(obj)
