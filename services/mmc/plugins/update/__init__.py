# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
"""
Update plugin for the MMC agent
"""
import logging
import subprocess
from time import time

logger = logging.getLogger()

from mmc.support.mmctools import SecurityContext, RpcProxyI
from mmc.core.tasks import TaskManager
from mmc.plugins.update.config import updateConfig
from mmc.plugins.update.database import updateDatabase
from mmc.plugins.msc import create_update_command
from mmc.plugins.base.computers import ComputerManager

from pulse2.version import getVersion, getRevision # pyflakes.ignore

APIVERSION = "0:1:0"
last_update_check_ts = None
available_updates = None

def getApiVersion(): return APIVERSION


def activate():
    config = updateConfig("update")
    if config.disabled:
        logger.warning("Plugin UpdateMgr: disabled by configuration.")
        return False
    if not updateDatabase().activate(config):
        logger.error("UpdateMgr database not activated")
        return False
    # Add create update commands in the task manager
    if config.enable_update_commands:
        TaskManager().addTask("update.create_update_commands",
                            (create_update_commands,),
                            cron_expression=config.update_commands_cron)
    return True


def calldb(func, *args, **kw):
    return getattr(updateDatabase(), func).__call__(*args, **kw)


def get_os_classes(params):
    return updateDatabase().get_os_classes(params)

def enable_only_os_classes(os_classes_ids):
    """
    Enable spacified os_classes and disble others
    """
    return updateDatabase().enable_only_os_classes(os_classes_ids)


def get_update_types(params):
    return updateDatabase().get_update_types(params)


def get_updates(params):
    return updateDatabase().get_updates(params)


def set_update_status(update_id, status):
    return updateDatabase().set_update_status(update_id, status)


def create_update_commands():
    # TODO: ensure that this method is called by taskmanager
    # and not directly by XMLRPC

    # Creating root context
    ctx = SecurityContext()
    ctx.userid = 'root'
    # Get active computer manager
    computer_manager = ComputerManager().getManagerName()

    if computer_manager == 'inventory':
        dyngroup_pattern = '%d==inventory::Hardware/OperatingSystem==%s'
    elif computer_manager == 'glpi':
        dyngroup_pattern = '%d==glpi::Operating system==%s'
    else:
        logging.getLogger().error('Update module: Unsupported computer manager %s' % computer_manager)
        return False

    # Get all enabled os_classes
    os_classes = updateDatabase().get_os_classes({'filters': {'enabled': 1}})

    # Create update command for enabled os_classes
    for os_class in os_classes['data']:

        patterns = os_class['pattern'].split('||')
        request = []
        equ_bool = []

        for i in xrange(len(patterns)):
            request.append(dyngroup_pattern % (i+1, patterns[i]))
            equ_bool.append(str(i+1))

        request = '||'.join(request)
        equ_bool = 'OR(%s)' % ','.join(equ_bool)

        targets = ComputerManager().getComputersList(ctx, {'request':  request, 'equ_bool': equ_bool}).keys()

        # Fetching all targets
        for uuid in targets:
            machine_id = int(uuid.lower().replace('uuid', ''))
            updates = updateDatabase().get_eligible_updates_for_host(machine_id)

            update_list = [update['uuid'] for update in updates]

            # Create update command for this host with update_list
            create_update_command(ctx, [uuid], update_list)
    return True


class OSHandler(object):
    
    def runInShell(self, cmd):
        process = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        return out.strip(), err.strip(), process.returncode

class DebianHandler(OSHandler):
    
    def getPackageTitle(self, pkg):
        cmd = "LANG=C apt-cache show %s|awk '/^Description/ {first = $1; $1 = \"\"; print $0;}' | sed 's/^[[:space:]]*//'|head -1" % pkg
        out, err, ec = self.runInShell(cmd)
        return out if ec == 0 and out else pkg
    
    def getCandidateVersion(self, pkg):
        cmd = "LANG=C apt-cache policy %s|awk '/Candidate/ { print $2 }'" % pkg
        out, err, ec = self.runInShell(cmd)
        return out if ec == 0 and out else 'N/A'
    
    def getAvailableUpdates(self):
        
        global last_update_check_ts, available_updates
        # If last checking is least than 4 hours, return cached value
        logger.fatal(last_update_check_ts)
        if last_update_check_ts and (time() - last_update_check_ts) < 14400:
            return available_updates
        
        #ctx = self.currentContext
        # Check if user is root
        #logging.getLogger().fatal(ctx.userid)
        # ============== apt-get update ====================
        out, err, ec = self.runInShell('apt-get update')
        # Update error occured
        if ec != 0:
            logging.getLogger().error(out)
            logging.getLogger().error(err)
            return []
        # ============ apt-get dist-upgrade =====================
        # get available updates
        cmd = "LANG=C apt-get -s dist-upgrade | awk '/^Inst/ { print $2 }'"
        pulse_packages_filter = "|grep -e '^python-mmc' -e '^python-pulse2' -e '^mmc-web' -e '^pulse2' -e '^mmc-agent$'"
        cmd += pulse_packages_filter
        
        out, err, ec = self.runInShell(cmd)
        
        if ec != 0:
            logging.getLogger().error(out)
            logging.getLogger().error(err)
            return []
        
        packages = out.strip().split('\n')
        
        result = []
        
        for pkg in packages:
            result.append({
                'name': pkg,
                'title': self.getPackageTitle(pkg),
                'version': self.getCandidateVersion(pkg)
            })
            
        available_updates = result
        last_update_check_ts = time()
            
        return result
    
    def installUpdates(self):
        
        pulse_packages_filter = "|grep -e '^python-mmc' -e '^python-pulse2' -e '^mmc-web' -e '^pulse2' -e '^mmc-agent$'"
        install_cmd = "LANG=C dpkg -l|awk '{print $2}' %s|xargs apt-get -y install" % pulse_packages_filter
        
        # Running this command with no pipe
        subprocess.call(install_cmd, shell=True)
    

class RpcProxy(RpcProxyI):
       
    def getAvailableUpdates(self):
        return DebianHandler().getAvailableUpdates()
    
    def installUpdates(self):
        return DebianHandler().installUpdates()
    
 
