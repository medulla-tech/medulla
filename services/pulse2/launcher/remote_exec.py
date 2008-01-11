#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2.
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

""" Pulse2 launcher, remote procedures definition
    Pulse2 Launcher is basicaly a simple XMLRPC service which run
    commands on remote hosts using (preferaly) encrypted and efficient
    protocols, such as SSH, SCP, RSYNC ...
"""

import os
import mmc.support.mmctools

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
                '-o PasswordAuthentication=no'
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
                '-o PasswordAuthentication=no'
            ]
    return client

def sync_remote_push(command_id, client, source_path, target_path, files_list, wrapper):
    """ Handle remote copy on target, sync / push mode.

    This function will simply send files_list on client:/target_path
    from localhost:/root_path

    TODO: handle URI for root_path / target_path (file://...)

    Return:
        * deffered upon success
        * None upon failure (mostly unsupported protocol given)
    """
    client = set_default_client_options(client)
    if client['protocol'] == "scp":
        real_files_list = map(lambda(a): "%s/%s" % (source_path, a), files_list)
        real_command = '%s %s scp %s %s %s@%s:%s' % (wrapper, '', ' '.join(client['options']), ' '.join(real_files_list), client['user'], client['host'], target_path)
        deffered = mmc.support.mmctools.shLaunchDeferred(real_command)
        deffered.addCallback(_remote_sync_cb)
        return deffered
    return None

def sync_remote_delete(command_id, client, target_path, files_list, wrapper):
    """ Handle remote deletion on target, sync mode

    This function will simply delete files_list from client:/target_path

    TODO: same as sync_remote_push

    Return: same as sync_remote_push
    """
    client = set_default_client_options(client)
    if client['protocol'] == "ssh":
        real_files_list = map(lambda(a): os.path.join(target_path, a), files_list)
        real_command = '%s %s ssh %s %s@%s "cd %s; rm -fr %s"' % (wrapper, '', ' '.join(client['options']), client['user'], client['host'], target_path, ' '.join(real_files_list))
        deffered = mmc.support.mmctools.shLaunchDeferred(real_command)
        deffered.addCallback(_remote_sync_cb)
        return deffered
    return None

def sync_remote_exec(command_id, client, target_path, command, wrapper):
    """ Handle remote execution on target, sync mode

    This function will simply run the command on the other side
    client is the method used to connect to the client

    TODO: same as sync_remote_push

    Return: same as sync_remote_push
    """
    client = set_default_client_options(client)
    if client['protocol'] == "ssh":
        real_command = '%s %s ssh %s %s@%s "cd %s; %s"' % (wrapper, '', ' '.join(client['options']), client['user'], client['host'], target_path, command)
        deffered = mmc.support.mmctools.shLaunchDeferred(real_command)
        deffered.addCallback(_remote_sync_cb)
        return deffered
    return None

def sync_remote_inventory(command_id, client, inventory_command, wrapper):
    """ Handle remote inventoring on target, sync mode

    This function will simply run the inventory on the othe side
    client is the method used to connect to the client

    TODO: same as sync_remote_push

    Return: same as sync_remote_push
    """
    client = set_default_client_options(client)
    if client['protocol'] == "ssh":
        real_command = '%s %s ssh %s %s@%s "%s"' % (wrapper, '', ' '.join(client['options']), client['user'], client['host'], inventory_command)
        deffered = mmc.support.mmctools.shLaunchDeferred(real_command)
        deffered.addCallback(_remote_sync_cb)
        return deffered
    return None

def async_remote_exec(id, command, client, wrapper):

    # do not re-inject already running processes
    if (do_background_process_exists(id)):
        return False

    client = set_default_client_options(client)
    if client['protocol'] == "ssh":
        real_command = '%s %s ssh %s %s@%s "%s"' % (wrapper, '', ' '.join(client['options']), client['user'], client['host'], command)
        mmc.support.mmctools.shlaunchBackground(real_command, id, _remote_async_progress_cb, _remote_async_end_cb)
    return True

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

def _remote_sync_cb(shprocess):
    """
    """
    # TODO: have to find a better way to handle these stupid encodings ...
    exitcode = shprocess.exitCode

    stdout = unicode(shprocess.out, 'utf-8', 'strict')
    stderr = unicode(shprocess.err, 'utf-8', 'strict')

    return exitcode, stdout, stderr

def _remote_async_progress_cb(self, data):
    try:
        self.output
    except: # if first loop
        self.output = ""
    self.output += data;
    # FIXME: handle log flood

def _remote_async_end_cb(self, reason):
    self.done = True
    self.exitCode = reason.value.exitCode
    if self.exitCode == 0:
        self.status = "job successfully finished"
    else:
        self.status = "Error: exited with code " + str(self.exitCode) + "\n" + self.stdall
    self.progress = -1
