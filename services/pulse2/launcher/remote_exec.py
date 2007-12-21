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

import logging
import os
import sys
import twisted.internet.reactor

def set_default_client_options(client):
    """
        client i a simple dict, which should contain required connexion infos, for now:
            protocol: which one to use for connexion, default to 'ssh' which is the only one supported for now
            host: where to connect, default to 127.0.0.1, fqdn and ipv4/v6 authorized
            port: default depends on chosen protocol
            user: when auth is needed, default is root
            passwd: when auth is needed, default is "" (empty string)
            cert: when auth is needed, default depends on chosen protocol
            options: array of strings to pass to the connexion initiator
    """

    if not client:
        client = {
            'protocol': None,
            'host': None,
            'port': None,
            'user': None,
            'passwd': None,
            'cert': None,
            'options': []
        }

    if not client['protocol']: client['protocol'] = 'ssh'
    if not client['host']: client['host'] = 'pulse2-win2k'

    if client['protocol'] == 'ssh':
        if not client['port']: client['port'] = 22
        if not client['user']: client['user'] = 'root'
        if not client['passwd']: client['passwd'] = '' # keeped unset as we should use RSA/DSA keys
        if not client['cert']: client['passwd'] = '/root/.ssh/id_dsa'
        if not client['options']: client['options'] = [
            '-T',
            '-R30080:127.0.0.1:80',
            '-o StrictHostKeyChecking=no',
            '-o Batchmode=yes',
            '-o PasswordAuthentication=no'
            ]
    return client

def remote_exec(id, command, client, wrapper, sync = True):
    if sync:
        return sync_remote_exec(id, command, client, wrapper)
    else:
        return async_remote_exec(id, command, client, wrapper)
    return None

def sync_remote_exec(id, command, client, wrapper):
    """
        command is exactly the command line we want to perform on the other side
        client is the method used to connect to the client (see set_default_client_options)
    """

    def cb(shprocess):
        # The callback just return the process outputs
        return shprocess.exitCode, shprocess.out, shprocess.err

    client = set_default_client_options(client)
    if client['protocol'] == "ssh":
        # FIXME: should use annotate_output and get_keychain
#        command = "%s %s ssh %s %s@%s \"%s\"" % (mmc.plugins.msc.MscConfig("msc").annotatepath, mmc.plugins.msc.config.get_keychain(), opts, user, host, command)
        real_command = '%s %s ssh %s %s@%s "%s"' % (wrapper, '', ' '.join(client['options']), client['user'], client['host'], command)
        d = mmc.support.mmctools.shLaunchDeferred(real_command)
        d.addCallback(cb)
        return d
    return None

def async_remote_exec(id, command, client, wrapper):

    def _progress_cb(self, data):
        try:
            self.output
        except: # if first loop
            self.output = ""
        self.output += data;
        # FIXME: handle log flood

    def _end_cb(self, reason):
        self.done = True
        self.exitCode = reason.value.exitCode
        if self.exitCode == 0:
            self.status = "job successfully finished"
        else:
            self.status = "Error: exited with code " + str(self.exitCode) + "\n" + self.stdall
        self.progress = -1;

    # do not re-inject already running processes
    if (do_background_process_exists(id)):
        return False

    client = set_default_client_options(client)
    if client['protocol'] == "ssh":
        # FIXME: should use annotate_output and get_keychain
#        command = "%s %s ssh %s %s@%s \"%s\"" % (mmc.plugins.msc.MscConfig("msc").annotatepath, mmc.plugins.msc.config.get_keychain(), opts, user, host, command)
        real_command = '%s %s ssh %s %s@%s "%s"' % (wrapper, '', ' '.join(client['options']), client['user'], client['host'], command)
        mmc.support.mmctools.shlaunchBackground(real_command, id, _progress_cb, _end_cb)
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
