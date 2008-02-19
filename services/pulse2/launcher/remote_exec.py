#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

""" Pulse2 launcher, remote procedures definition
    Pulse2 Launcher is basicaly a simple XMLRPC service which run
    commands on remote hosts using (preferaly) encrypted and efficient
    protocols, such as SSH, SCP, RSYNC ...
"""

import os
import logging

# Twisted stuf
import twisted.web.xmlrpc

# gather our modules
import pulse2.launcher.process_control
import pulse2.launcher.utils
from pulse2.launcher.config import LauncherConfig

def set_default_client_options(client):
    """
        client i a simple dict, which should contain required connexion infos, for now:
            protocol: which one to use for connexion, mandatory
            host: where to connect, mandatory
            port: default depends on chosen protocol
            user: when auth is needed, default is root
            passwd: when auth is needed, default is "" (empty string)
            cert: when auth is needed, default depends on chosen protocol
            options: array of strings to pass to the connexion initiator
            rootpath: used to know where to perform operations ('/' under Unix,
            '/cygdrive/c' uner MS/Win, etc ...
    """

    if client['protocol'] == 'ssh':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'passwd' in client:
            client['passwd'] = '' # unset as we should use RSA/DSA keys
        if not 'cert' in client:
            client['cert'] = '/root/.ssh/id_dsa'
        if not 'options' in client:
            client['options'] = [
                '-T',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'Batchmode=yes',
                '-o', 'PasswordAuthentication=no',
                '-o', 'SetupTimeOut=10',
                '-o', 'ServerAliveInterval=10',
                '-o', 'CheckHostIP=no',
                '-o', 'ConnectTimeout=10'
            ]

    if client['protocol'] == 'wget': # FIXME: should handle both ssh and http auth
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'passwd' in client:
            client['passwd'] = '' # unset as we should use RSA/DSA keys
        if not 'cert' in client:
            client['cert'] = '/root/.ssh/id_dsa'
        if not 'options' in client:
            client['options'] = [
                '-T',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'Batchmode=yes',
                '-o', 'PasswordAuthentication=no',
                '-o', 'SetupTimeOut=10',
                '-o', 'ServerAliveInterval=10',
                '-o', 'CheckHostIP=no',
                '-o', 'ConnectTimeout=10'
            ]

    if client['protocol'] == 'scp':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'passwd' in client:
            client['passwd'] = '' # unset as we should use RSA/DSA keys
        if not 'cert' in client:
            client['cert'] = '/root/.ssh/id_dsa'
        if not 'options' in client:
            client['options'] = [
                '-r',
                '-p',
                '-q',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'Batchmode=yes',
                '-o', 'PasswordAuthentication=no',
                '-o', 'SetupTimeOut=10',
                '-o', 'ServerAliveInterval=10',
                '-o', 'CheckHostIP=no',
                '-o', 'ConnectTimeout=10'
            ]
    return client

    if client['protocol'] == 'wol':
        if not 'addr' in client:
            client['addr'] = 'FF:FF:FF:FF:FF:FF'
        if not 'bcast' in client:
            client['bcast'] = '255.255.255.255'
        if not 'port' in client:
            client['port'] = '40000'
    return client

def sync_remote_push(command_id, client, files_list):
    """ Handle remote copy on target, sync mode """
    return remote_push(command_id, client, files_list, 'sync')

def async_remote_push(command_id, client, files_list):
    """ Handle remote copy on target, async mode """
    return remote_push(command_id, client, files_list, 'async')

def remote_push(command_id, client, files_list, mode):
    """ Handle remote copy (push) """
    source_path = LauncherConfig().source_path
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    wrapper_path = LauncherConfig().wrapper_path
    client = set_default_client_options(client)
    if client['protocol'] == "scp":
        real_files_list = map(lambda(a): "%s/%s" % (source_path, a), files_list)
        command_list = [ \
            wrapper_path,
            '/usr/bin/scp'
        ]
        command_list += client['options']
        command_list += real_files_list
        command_list += [ \
            "%s@%s:%s" % (client['user'], client['host'], target_path),
        ]
        if mode == 'async':
            pulse2.launcher.process_control.commandForker(command_list, command_id, __cb_async_process_end, 'completed_push')
            return True
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

def sync_remote_pull(command_id, client, files_list):
    """ Handle remote copy on target, sync mode """
    return remote_pull(command_id, client, files_list, 'sync')

def async_remote_pull(command_id, client, files_list):
    """ Handle remote copy on target, async mode """
    return remote_pull(command_id, client, files_list, 'async')

def remote_pull(command_id, client, files_list, mode):
    """ Handle remote copy (pull) on target """
    client = set_default_client_options(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "wget":
        real_files_list = files_list
        real_command = 'mkdir -p %s; cd %s; wget -nv -N %s' % (target_path, target_path, ' '.join(real_files_list))
        command_list = [ \
            wrapper_path,
            '/usr/bin/ssh'
        ]
        command_list += client['options']
        command_list += [ \
            "%s@%s" % (client['user'], client['host']),
            real_command
        ]
        if mode == 'async':
            pulse2.launcher.process_control.commandForker(command_list, command_id, __cb_async_process_end, 'completed_pull')
            return True
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

def sync_remote_delete(command_id, client, files_list):
    """ Handle remote deletion on target, sync mode """
    return remote_delete(command_id, client, files_list, 'sync')

def async_remote_delete(command_id, client, files_list):
    """ Handle remote deletion on target, async mode """
    return remote_delete(command_id, client, files_list, 'async')

def remote_delete(command_id, client, files_list, mode):
    """ Handle remote deletion on target """
    client = set_default_client_options(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "ssh":
        real_files_list = map(lambda(a): os.path.join(target_path, a), files_list)
        real_command = 'cd %s; rm -fr %s; rmdir %s' % (target_path, ' '.join(real_files_list), target_path)
        command_list = [ \
            wrapper_path,
            '/usr/bin/ssh'
        ]
        command_list += client['options']
        command_list += [ \
            "%s@%s" % (client['user'], client['host']),
            real_command
        ]
        if mode == 'async':
            pulse2.launcher.process_control.commandForker(command_list, command_id, __cb_async_process_end, 'completed_deletion')
            return True
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

def sync_remote_exec(command_id, client, command):
    """ Handle remote execution on target, sync mode """
    return remote_exec(command_id, client, command, 'sync')

def async_remote_exec(command_id, client, command):
    """ Handle remote execution on target, async mode """
    return remote_exec(command_id, client, command, 'async')

def remote_exec(command_id, client, command, mode):
    """ Handle remote execution on target """
    client = set_default_client_options(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "ssh":
        # TODO: chmod should be done upper
        real_command = 'cd %s; chmod +x %s; %s' % (target_path, command, command)
        command_list = [ \
            wrapper_path,
            '/usr/bin/ssh'
        ]
        command_list += client['options']
        command_list += [ \
            "%s@%s" % (client['user'], client['host']),
            real_command
        ]
        if mode == 'async':
            pulse2.launcher.process_control.commandForker(command_list, command_id, __cb_async_process_end, 'completed_execution')
            return True
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

def sync_remote_quickaction(command_id, client, command):
    """ Handle remote quick action on target, sync mode """
    return remote_quickaction(command_id, client, command, 'sync')

def async_remote_quickaction(command_id, client, command):
    """ Handle remote quick action on target, async mode """
    return remote_quickaction(command_id, client, command, 'async')

def remote_quickaction(command_id, client, command, mode):
    """ Handle remote quick action on target """
    client = set_default_client_options(client)
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "ssh":
        real_command = command
        command_list = [ \
            wrapper_path,
            '/usr/bin/ssh'
        ]
        command_list += client['options']
        command_list += [ \
            "%s@%s" % (client['user'], client['host']),
            real_command
        ]
        if mode == 'async':
            pulse2.launcher.process_control.commandForker(command_list, command_id, __cb_async_process_end, 'completed_quick_action')
            return True
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

def sync_remote_wol(command_id, client, wrapper):
    """ Handle remote WOL on target, sync mode

    Return: same as sync_remote_push
    """
    client = set_default_client_options(client)
    """
    if client['protocol'] == "wol":
        real_command = '%s %s ssh %s %s@%s "%s"' % (wrapper, '', ' '.join(client['options']), client['user'], client['host'], command)
        deffered = pulse2.launcher.process_control.shLaunchDeferred(real_command)
        deffered.addCallback(__cb_sync_process_end)
        return deffered
        """
    return None

def sync_remote_inventory(command_id, client):
    """ Handle remote inventoring on target, sync mode

    This function will simply run the inventory on the othe side
    client is the method used to connect to the client

    TODO: same as sync_remote_push

    Return: same as sync_remote_push
    """
    client = set_default_client_options(client)
    wrapper_path = LauncherConfig().wrapper_path
    inventory_command = LauncherConfig().inventory_command
    if client['protocol'] == "ssh":
        real_command = inventory_command
        command_list = [ \
            wrapper_path,
            '/usr/bin/ssh'
        ]
        command_list += client['options']
        command_list += [ \
            "%s@%s" % (client['user'], client['host']),
            real_command
        ]
        return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

"""
def get_background_process_count():
    return len(mmc.support.mmctools.ProcessScheduler().listProcess())

def get_background_process_list():
    return mmc.support.mmctools.ProcessScheduler().listProcess().keys()

def get_background_running_process_count():
    count = 0
    for i in mmc.support.mmctools.ProcessScheduler().listProcess().values():
        if not i.done:
            count += 1
    return count

def get_background_running_process_list():
    ret = []
    for i in mmc.support.mmctools.ProcessScheduler().listProcess().values():
        if not i.done:
            ret.append(i.desc)
    return ret

def do_background_process_exists(id):
    return id in mmc.support.mmctools.ProcessScheduler().listProcess().keys()

def is_background_process_done(id):
    return mmc.support.mmctools.ProcessScheduler().listProcess()[id].done

def purge_background_process(id):
    try:
        if is_background_process_done(id):
            process = mmc.support.mmctools.ProcessScheduler().getProcess(id)
            ret = {
                'out': process.out,
                'err': process.err,
                'exitcode' : process.getExitCode()
            }
            clean_background_process(id)
            return ret
    except KeyError:
        return False
    return True;

def clean_background_process(id):
    mmc.support.mmctools.ProcessScheduler().rmProcess(id)
    return True;
"""
def __cb_sync_process_end(shprocess):
    """
        Handle sync process termination
    """
    exitcode = shprocess.exitCode
    stdout = unicode(shprocess.stdout, 'utf-8', 'strict')
    stderr = unicode(shprocess.stderr, 'utf-8', 'strict')
    return exitcode, stdout, stderr

def __cb_async_process_end(shprocess, id, return_callback):
    """
        Handle async process termination
    """
    def _cb(result):
        pass
    def _eb(reason):
        logger = logging.getLogger()
        logger.warn('launcher "%s": failed to send results to our scheduler at %s, reason: %s' % (LauncherConfig().name, scheduler, reason))
        pass

    exitcode = shprocess.exitCode
    stdout = unicode(shprocess.stdout, 'utf-8', 'strict')
    stderr = unicode(shprocess.stderr, 'utf-8', 'strict')

    scheduler = pulse2.launcher.utils.getScheduler()
    mydeffered = twisted.web.xmlrpc.Proxy(scheduler).callRemote(
        return_callback,
        LauncherConfig().name,
        (exitcode, stdout, stderr),
        id
    )
    mydeffered.\
        addCallback(_cb).\
        addErrback(_eb)
    return
