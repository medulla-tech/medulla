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
from pulse2.launcher.xmlrpc import getProxy

SEPARATOR = u'·'

def sync_remote_push(command_id, client, files_list, wrapper_timeout):
    """ Handle remote copy on target, sync mode """
    return remote_push(command_id, client, files_list, 'sync', wrapper_timeout)

def async_remote_push(command_id, client, files_list, wrapper_timeout):
    """ Handle remote copy on target, async mode """
    return remote_push(command_id, client, files_list, 'async', wrapper_timeout)

def remote_push(command_id, client, files_list, mode, wrapper_timeout):
    """ Handle remote copy (push) """
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
    if client['protocol'] == "rsyncssh":
        # command is issued though our wrapper, time to build it
        real_files_list = files_list

        # Build "exec" command
        real_command  = ['/usr/bin/rsync']
        real_command += client['proto_args']
        real_command += real_files_list
        real_command += [ "%s@%s:%s/" % (client['user'], client['host'], target_path)]

        # Build "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--max-log-size',
            str(LauncherConfig().wrapper_max_log_size),
            '--max-exec-time',
            str(wrapper_timeout),
            '--exec',
            SEPARATOR.join(real_command),
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec-server-side'
        ]

        # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
        if client['client_check']:
            command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
        if client['server_check']:
            command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
        if client['action']:
            command_list += ['--action', client['action']]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_push',
                LauncherConfig().max_command_age,
                client['group'],
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_pull(command_id, client, files_list, wrapper_timeout):
    """ Handle remote copy on target, sync mode """
    return remote_pull(command_id, client, files_list, 'sync', wrapper_timeout)

def async_remote_pull(command_id, client, files_list, wrapper_timeout):
    """ Handle remote copy on target, async mode """
    return remote_pull(command_id, client, files_list, 'async', wrapper_timeout)

def remote_pull(command_id, client, files_list, mode, wrapper_timeout):
    """ Handle remote copy (pull) on target """
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    if client['protocol'] == "wget":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        real_command  = ['wget']
        real_command += client['proto_args']
        real_command += ['-N']
        real_command += files_list
        real_command += ['-P']
        real_command += [target_path]
        # Make downloaded files executable
        real_command += ['&&']
        real_command += ['chmod']
        real_command += ['u+x']
        real_command += ['-R']
        real_command += [target_path]

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--max-log-size',
            str(LauncherConfig().wrapper_max_log_size),
            '--max-exec-time',
            str(wrapper_timeout),
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            SEPARATOR.join(real_command),
        ]

        # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
        if client['client_check']:
            command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
        if client['server_check']:
            command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
        if client['action']:
            command_list += ['--action', client['action']]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_pull',
                LauncherConfig().max_command_age,
                client['group'],
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_delete(command_id, client, files_list, wrapper_timeout):
    """ Handle remote deletion on target, sync mode """
    return remote_delete(command_id, client, files_list, 'sync', wrapper_timeout)

def async_remote_delete(command_id, client, files_list, wrapper_timeout):
    """ Handle remote deletion on target, async mode """
    return remote_delete(command_id, client, files_list, 'async', wrapper_timeout)

def remote_delete(command_id, client, files_list, mode, wrapper_timeout):
    """ Handle remote deletion on target """
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    if client['protocol'] == "ssh":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        real_command = ['rm', '-fr']
        real_command  += map(lambda(a): os.path.join(target_path, a), files_list)
        real_command += [';', 'if', '!', 'rmdir', target_path, ';']
        real_command += ['then']
        # Use the dellater command if available
        real_command +=  ['if', '[', '-x', '/usr/bin/dellater.exe', ']', ';']
        real_command +=  ['then']
        # The permissions need to be modified, else the directory can't be
        # deleted.
        real_command +=  ['chown', 'SYSTEM.SYSTEM', target_path, ';']
        # The mount/grep/sed stuff is needed to get the directory name for
        # Windows.
        real_command +=  ['dellater', '"$(mount |grep " on / type"|sed "s/ on \/ type.*$//")"' + target_path, ';']
        real_command +=  ['fi', ';']
        real_command += ['fi']
        
        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--max-log-size',
            str(LauncherConfig().wrapper_max_log_size),
            '--max-exec-time',
            str(wrapper_timeout),
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            SEPARATOR.join(real_command),
        ]

        # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
        if client['client_check']:
            command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
        if client['server_check']:
            command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
        if client['action']:
            command_list += ['--action', client['action']]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_deletion',
                LauncherConfig().max_command_age,
                client['group'],
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_exec(command_id, client, command, wrapper_timeout):
    """ Handle remote execution on target, sync mode """
    return remote_exec(command_id, client, command, 'sync', wrapper_timeout)

def async_remote_exec(command_id, client, command, wrapper_timeout):
    """ Handle remote execution on target, async mode """
    return remote_exec(command_id, client, command, 'async', wrapper_timeout)

def remote_exec(command_id, client, command, mode, wrapper_timeout):
    """ Handle remote execution on target """
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
    target_path = os.path.join(LauncherConfig().target_path, pulse2.launcher.utils.getTempFolderName(command_id, client['uuid']))
    if client['protocol'] == "ssh":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        real_command  = ['cd', target_path, ';', command]

        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--max-log-size',
            str(LauncherConfig().wrapper_max_log_size),
            '--max-exec-time',
            str(wrapper_timeout),
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            SEPARATOR.join(real_command),
        ]

        # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
        if client['client_check']:
            command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
        if client['server_check']:
            command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
        if client['action']:
            command_list += ['--action', client['action']]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_execution',
                LauncherConfig().max_command_age,
                client['group'],
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_quickaction(command_id, client, command, wrapper_timeout):
    """ Handle remote quick action on target, sync mode """
    return remote_quickaction(command_id, client, command, 'sync', wrapper_timeout)

def async_remote_quickaction(command_id, client, command, wrapper_timeout):
    """ Handle remote quick action on target, async mode """
    return remote_quickaction(command_id, client, command, 'async', wrapper_timeout)

def remote_quickaction(command_id, client, command, mode, wrapper_timeout):
    """ Handle remote quick action on target """
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
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
            '--max-log-size',
            str(LauncherConfig().wrapper_max_log_size),
            '--max-exec-time',
            str(wrapper_timeout),
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            real_command, # we do not use the SEPARATOR here, as the command is send "as is"
        ]

        # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
        if client['client_check']:
            command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
        if client['server_check']:
            command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
        if client['action']:
            command_list += ['--action', client['action']]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_quick_action',
                LauncherConfig().max_command_age,
                client['group'],
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_direct(command_id, client, command, max_log_size, wrapper_timeout):
    """ Handle remote direct stuff on target, sync mode """
    return remote_direct(command_id, client, command, 'sync', max_log_size, wrapper_timeout)

def async_remote_direct(command_id, client, command, max_log_size, wrapper_timeout):
    """ Handle remote direct stuff on target, async mode """
    return remote_direct(command_id, client, command, 'async', max_log_size, wrapper_timeout)

def remote_direct(command_id, client, command, mode, max_log_size, wrapper_timeout):
    """ Handle remote direct stuff on target """
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
    if client['protocol'] == "ssh":
        # command is issued though our wrapper, time to build it

        # Built "thru" command
        thru_command_list  = ['/usr/bin/ssh']
        thru_command_list += client['transp_args']
        thru_command_list += [ "%s@%s" % (client['user'], client['host'])]

        # Build "exec" command
        real_command = command

        if max_log_size == None:
            # If no max_log_size set, use the value from the configuration file
            max_log_size = LauncherConfig().wrapper_max_log_size
        # Build final command line
        command_list = [
            LauncherConfig().wrapper_path,
            '--max-log-size',
            str(max_log_size),
            '--max-exec-time',
            str(wrapper_timeout),
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            real_command, # we do not use the SEPARATOR here, as the command is send "as is"
            '--no-wrap',
            '--only-stdout',
            '--remove-empty-lines'
        ]

        # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
        if client['client_check']:
            command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
        if client['server_check']:
            command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
        if client['action']:
            command_list += ['--action', client['action']]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_direct',
                LauncherConfig().max_command_age,
                client['group'],
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def sync_remote_inventory(command_id, client, wrapper_timeout):
    """ Handle remote quick action on target, sync mode """
    return remote_inventory(command_id, client, 'sync', wrapper_timeout)

def async_remote_inventory(command_id, client, wrapper_timeout):
    """ Handle remote quick action on target, async mode """
    return remote_inventory(command_id, client, 'async', wrapper_timeout)

def remote_inventory(command_id, client, mode, wrapper_timeout):
    """ Handle remote inventoring on target, sync mode

    This function will simply run the inventory on the othe side
    client is the method used to connect to the client

    TODO: same as sync_remote_push

    Return: same as sync_remote_push
    """
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
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
            '--max-log-size',
            str(LauncherConfig().wrapper_max_log_size),
            '--max-exec-time',
            str(wrapper_timeout),
            '--thru',
            SEPARATOR.join(thru_command_list),
            '--exec',
            real_command, # we do not use the SEPARATOR here, as the command is send "as is"
        ]

        # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
        if client['client_check']:
            command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
        if client['server_check']:
            command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
        if client['action']:
            command_list += ['--action', client['action']]

        if mode == 'async':
            return pulse2.launcher.process_control.commandForker(
                command_list,
                __cb_async_process_end,
                command_id,
                LauncherConfig().defer_results,
                'completed_inventory',
                LauncherConfig().max_command_age,
                client['group'],
            )
        elif mode == 'sync':
            return pulse2.launcher.process_control.commandRunner(
                command_list,
                __cb_sync_process_end
            )
    return None

def from_remote_to_launcher(command_id, client, path, targetpath, bwlimit, wrapper_timeout):
    """
    Recursive copy of a directory from a client to the launcher using scp.
    """
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
    command_list = ['/usr/bin/scp']
    command_list += client['transp_args']
    if bwlimit:
        command_list += ['-l'] + [str(bwlimit)]
    command_list += ['-r']
    command_list += [ "%s@%s:%s" % (client['user'], client['host'], path)]
    command_list += [targetpath]
    # The following ssh options are not used by scp, so we remove them
    command_list.remove('-T')
    command_list.remove('-a')
    
    # Build final command line
    command_list = [
        LauncherConfig().wrapper_path,
        '--max-log-size',
        str(LauncherConfig().wrapper_max_log_size),
        '--max-exec-time',
        str(wrapper_timeout),
        '--exec',
        SEPARATOR.join(command_list),
        ]
    return pulse2.launcher.process_control.commandRunner(
        command_list,
        __cb_sync_process_end)


def __cb_sync_process_end(shprocess):
    """
        Handle sync process termination
    """
    exitcode = shprocess.exit_code
    stdout = unicode(shprocess.stdout, 'utf-8', 'strict')
    stderr = unicode(shprocess.stderr, 'utf-8', 'strict')
    return exitcode, stdout, stderr

def __cb_async_process_end(shprocess):
    """
        Handle async process termination
    """
    def _cb(result, id):
        # as we successfuly sent our result to our scheduler, command can be safely removed from our list
        pulse2.launcher.process_control.ProcessList().removeProcess(id)
    def _eb(reason, id):
        # no result can be sent, log and keep our process in our list
        logging.getLogger().warn('launcher "%s": failed to send results of command #%s to our scheduler at %s: %s' % (LauncherConfig().name, id, scheduler, reason.value))

    exitcode = shprocess.exit_code
    stdout = unicode(shprocess.stdout, 'utf-8', 'strict')
    stderr = unicode(shprocess.stderr, 'utf-8', 'strict')
    id = shprocess.id

    scheduler = pulse2.launcher.utils.getScheduler()
    mydeffered = getProxy(scheduler).callRemote(
        shprocess.returnxmlrpcfunc,
        LauncherConfig().name,
        (exitcode, stdout, stderr),
        id
    )
    mydeffered.\
        addCallback(_cb, id).\
        addErrback(_eb, id)
    return
