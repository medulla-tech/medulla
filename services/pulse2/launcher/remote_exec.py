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

# gather our modules
import pulse2.launcher.process_control
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
                '-o StrictHostKeyChecking=no',
                '-o Batchmode=yes',
                '-o PasswordAuthentication=no',
                '-o SetupTimeOut=10',
                '-o ServerAliveInterval=10',
                '-o ConnectTimeout=10'
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
                '-o StrictHostKeyChecking=no',
                '-o Batchmode=yes',
                '-o PasswordAuthentication=no',
                '-o SetupTimeOut=10',
                '-o ServerAliveInterval=10',
                '-o ConnectTimeout=10'
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
                '-o StrictHostKeyChecking=no',
                '-o Batchmode=yes',
                '-o PasswordAuthentication=no',
                '-o SetupTimeOut=10',
                '-o ServerAliveInterval=10',
                '-o ConnectTimeout=10'
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
    """ Handle remote copy on target, sync / push mode.

    This function will simply send files_list on client:/target_path
    from localhost:/root_path

    TODO: handle URI for root_path / target_path (file://...)

    Return:
        * deffered upon success
        * None upon failure (mostly unsupported protocol given)
    """
    source_path = LauncherConfig().source_path
    target_path = LauncherConfig().target_path
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
        return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

def sync_remote_pull(command_id, client, files_list):
    """ Handle remote copy on target, sync / pull mode.

    This function will simply get files_list on client:/target_path

    Return:
        * deffered upon success
        * None upon failure (mostly unsupported protocol given)
    """
    client = set_default_client_options(client)
    target_path = LauncherConfig().target_path
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "wget":
        real_files_list = files_list
        real_command = 'cd %s; wget -nv -N %s' % (target_path, ' '.join(real_files_list))
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


def sync_remote_delete(command_id, client, files_list):
    """ Handle remote deletion on target, sync mode

    This function will simply delete files_list from client:/target_path

    TODO: same as sync_remote_push

    Return: same as sync_remote_push
    """
    client = set_default_client_options(client)
    target_path = LauncherConfig().target_path
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "ssh":
        real_files_list = map(lambda(a): os.path.join(target_path, a), files_list)
        real_command = 'cd %s; rm -fr %s' % (target_path, ' '.join(real_files_list))
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

def sync_remote_exec(command_id, client, command):
    """ Handle remote execution on target, sync mode

    This function will simply exec the command on the other side
    client is the method used to connect to the client
    The command script should have been uploaded earlier

    TODO: same as sync_remote_push

    Return: same as sync_remote_push
    """
    client = set_default_client_options(client)
    target_path = LauncherConfig().target_path
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
        return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

def sync_remote_quickaction(command_id, client, command):
    """ Handle remote quick action on target, sync mode

    This function will simply run the command on the other side
    client is the method used to connect to the client. Used to launch
    qucik commands

    Return: same as sync_remote_push
    """
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
        return pulse2.launcher.process_control.commandRunner(command_list, __cb_sync_process_end)
    return None

def async_remote_quickaction(command_id, client, command):
    """ Handle remote quick action on target, async mode

    This function will simply run the command on the other side
    client is the method used to connect to the client. Used to launch
    qucik commands

    Return: same as sync_remote_quickaction
    """
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
        pulse2.launcher.process_control.commandForker(command_list, command_id, __cb_async_process_end, __cb_async_process_progress)
    return True

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

def async_remote_exec(id, command, client):

    # do not re-inject already running processes
    if (do_background_process_exists(id)):
        return False

    client = set_default_client_options(client)
    wrapper_path = LauncherConfig().wrapper_path
    if client['protocol'] == "ssh":
        real_command = '%s %s ssh %s %s@%s "%s"' % (wrapper_path, '', ' '.join(client['options']), client['user'], client['host'], command)
        pulse2.launcher.process_control.shlaunchBackground(real_command, id, __cb_async_process_progress, __cb_async_process_end)
    return True

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

def __cb_async_process_progress(shprocess, id):
    """
        Handle async process progression
    """
    exitcode = shprocess.exitCode
    stdout = unicode(shprocess.stdout, 'utf-8', 'strict')
    stderr = unicode(shprocess.stderr, 'utf-8', 'strict')
    print "P: |%s|, |%s|, |%s|, |%s|" % (exitcode, stdout, stderr, id)
    return

def __cb_async_process_end(shprocess, id):
    """
        Handle async process termination
    """
    exitcode = shprocess.exitCode
    stdout = unicode(shprocess.stdout, 'utf-8', 'strict')
    stderr = unicode(shprocess.stderr, 'utf-8', 'strict')

    print "E: |%s|, |%s|, |%s|, |%s|" % (exitcode, stdout, stderr, id)
    return
