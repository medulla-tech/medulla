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

SEPARATOR = u'·'

def sync_remote_push(command_id, client, files_list):
    """ Handle remote copy on target, sync mode """
    return remote_push(command_id, client, files_list, 'sync')

def async_remote_push(command_id, client, files_list):
    """ Handle remote copy on target, async mode """
    return remote_push(command_id, client, files_list, 'async')

def remote_push(command_id, client, files_list, mode):
    """ Handle remote copy (push) """
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    wrapper_path = LauncherConfig().wrapper_path
    client = pulse2.launcher.utils.set_default_client_options(client)
    if client['protocol'] == "rsyncssh":
        # command is issued though our wrapper, time to build it
        real_files_list = files_list

        # Build "exec" command
        real_command  = ['/usr/bin/rsync']
        real_command += client['proto_args']
        real_command += real_files_list
        real_command += [ "%s@%s:%s/" % (client['user'], client['host'], target_path)]

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--exec',
            SEPARATOR.join(real_command),
            '--max_log_size',
            LauncherConfig().wrapper_max_log_size
        ]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_push'
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_pull(command_id, client, files_list):
    """ Handle remote copy on target, sync mode """
    return remote_pull(command_id, client, files_list, 'sync')

def async_remote_pull(command_id, client, files_list):
    """ Handle remote copy on target, async mode """
    return remote_pull(command_id, client, files_list, 'async')

def remote_pull(command_id, client, files_list, mode):
    """ Handle remote copy (pull) on target """
    client = pulse2.launcher.utils.set_default_client_options(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "wget":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        real_command  = ['wget']
        real_command  += client['proto_args']
        real_command  += ['-N']
        real_command  += files_list
        real_command  += ['-P']
        real_command  += [target_path]

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            SEPARATOR.join(real_command),
            '--max_log_size',
            LauncherConfig().wrapper_max_log_size
        ]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_pull'
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_delete(command_id, client, files_list):
    """ Handle remote deletion on target, sync mode """
    return remote_delete(command_id, client, files_list, 'sync')

def async_remote_delete(command_id, client, files_list):
    """ Handle remote deletion on target, async mode """
    return remote_delete(command_id, client, files_list, 'async')

def remote_delete(command_id, client, files_list, mode):
    """ Handle remote deletion on target """
    client = pulse2.launcher.utils.set_default_client_options(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "ssh":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        real_command  = ['rm', '-fr']
        real_command  += map(lambda(a): os.path.join(target_path, a), files_list)
        real_command  += [';', 'rmdir', target_path]

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            SEPARATOR.join(real_command),
            '--max_log_size',
            LauncherConfig().wrapper_max_log_size
        ]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_deletion'
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_exec(command_id, client, command):
    """ Handle remote execution on target, sync mode """
    return remote_exec(command_id, client, command, 'sync')

def async_remote_exec(command_id, client, command):
    """ Handle remote execution on target, async mode """
    return remote_exec(command_id, client, command, 'async')

def remote_exec(command_id, client, command, mode):
    """ Handle remote execution on target """
    client = pulse2.launcher.utils.set_default_client_options(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "ssh":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        # TODO: chmod should be done upper
        real_command  = ['cd', target_path, ';', 'chmod', '+x', command, ';', command ]

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            SEPARATOR.join(real_command),
            '--max_log_size',
            LauncherConfig().wrapper_max_log_size
        ]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_execution'
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_quickaction(command_id, client, command):
    """ Handle remote quick action on target, sync mode """
    return remote_quickaction(command_id, client, command, 'sync')

def async_remote_quickaction(command_id, client, command):
    """ Handle remote quick action on target, async mode """
    return remote_quickaction(command_id, client, command, 'async')

def remote_quickaction(command_id, client, command, mode):
    """ Handle remote quick action on target """
    client = pulse2.launcher.utils.set_default_client_options(client)
    if client['protocol'] == "ssh":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        real_command = command

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            real_command, # we do not use the SEPARATOR here, as the command is send "as is"
            '--max_log_size',
            LauncherConfig().wrapper_max_log_size
        ]
        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_quick_action'
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_wol(command_id, client, wrapper):
    """ Handle remote WOL on target, sync mode

    Return: same as sync_remote_push
    """
    client = pulse2.launcher.utils.set_default_client_options(client)
    """
    if client['protocol'] == "wol":
        real_command = '%s %s ssh %s %s@%s "%s"' % (wrapper, '', ' '.join(client['options']), client['user'], client['host'], command)
        deffered = pulse2.launcher.process_control.shLaunchDeferred(real_command)
        deffered.addCallback(__cb_sync_process_end)
        return deffered
        """
    return None

def sync_remote_inventory(command_id, client):
    """ Handle remote quick action on target, sync mode """
    return remote_inventory(command_id, client, 'sync')

def async_remote_inventory(command_id, client):
    """ Handle remote quick action on target, async mode """
    return remote_inventory(command_id, client, 'async')

def remote_inventory(command_id, client, mode):
    """ Handle remote inventoring on target, sync mode

    This function will simply run the inventory on the othe side
    client is the method used to connect to the client

    TODO: same as sync_remote_push

    Return: same as sync_remote_push
    """
    client = pulse2.launcher.utils.set_default_client_options(client)
    wrapper_path = LauncherConfig().wrapper_path
    inventory_command = LauncherConfig().inventory_command
    if client['protocol'] == "ssh":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        real_command = inventory_command

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            real_command, # we do not use the SEPARATOR here, as the command is send "as is"
            '--max_log_size',
            LauncherConfig().wrapper_max_log_size
        ]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_inventory'
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def __cb_sync_process_end(shprocess):
    """
        Handle sync process termination
    """
    exitcode = shprocess.exitCode
    stdout = unicode(shprocess.stdout, 'utf-8', 'strict')
    stderr = unicode(shprocess.stderr, 'utf-8', 'strict')
    return exitcode, stdout, stderr

def __cb_async_process_end(shprocess):
    """
        Handle async process termination
    """
    def _cb(result, id):
        # as we successfuly sent our result to our scheduler, command can be safely removed from our list
        pulse2.launcher.process_control.ProcessList().rmProcess(id)
    def _eb(reason, id):
        # no result can be sent, log and keep our process in our list
        logging.getLogger().warn('launcher "%s": failed to send results of command #%s to our scheduler at %s, reason: %s' % (LauncherConfig().name, id, scheduler, reason))

    exitcode = shprocess.exitCode
    stdout = unicode(shprocess.stdout, 'utf-8', 'strict')
    stderr = unicode(shprocess.stderr, 'utf-8', 'strict')
    id = shprocess.id

    scheduler = pulse2.launcher.utils.getScheduler()
    mydeffered = twisted.web.xmlrpc.Proxy(scheduler).callRemote(
        shprocess.returnxmlrpcfunc,
        LauncherConfig().name,
        (exitcode, stdout, stderr),
        id
    )
    mydeffered.\
        addCallback(_cb, id).\
        addErrback(_eb, id)
    return

def get_process_count():
    return pulse2.launcher.process_control.ProcessList().getProcessCount()
def get_running_count():
    return pulse2.launcher.process_control.ProcessList().getRunningCount()
def get_zombie_count():
    return pulse2.launcher.process_control.ProcessList().getZombieCount()

def get_process_ids():
    return pulse2.launcher.process_control.ProcessList().getProcessIds()
def get_running_ids():
    return pulse2.launcher.process_control.ProcessList().getRunningIds()
def get_zombie_ids():
    return pulse2.launcher.process_control.ProcessList().getZombieIds()


def get_process_stderr(id):
    return pulse2.launcher.process_control.ProcessList().getProcessStderr(id)
def get_process_stdout(id):
    return pulse2.launcher.process_control.ProcessList().getProcessStdout(id)
def get_process_exitcode(id):
    return pulse2.launcher.process_control.ProcessList().getProcessExitcode(id)
