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

import md5

from pulse2.launcher.config import LauncherConfig

def getScheduler():
    """ Get our referent scheduler """
    return 'http://%s:%s' % (LauncherConfig().scheduler_host, LauncherConfig().scheduler_port)

def getTempFolderName(id_command, client_uuid):
    """ Generate a temporary folder name which will contain our deployment stuff """
    return LauncherConfig().temp_folder_prefix + md5.new('%s%s' % (id_command, client_uuid)).hexdigest()[len(LauncherConfig().temp_folder_prefix):]

def getPubKey(key_name):
    """
        Handle remote download of this launcher's pubkey.
        key_name is as define in the config file
    """
    try:
        LauncherConfig().ssh_keys[key_name]
    except KeyError:
        key_name = LauncherConfig().ssh_defaultkey

    if key_name == None or key_name == '':
        key_name = LauncherConfig().ssh_defaultkey
    try:
        ssh_key = open(LauncherConfig().ssh_keys[key_name] + '.pub')
    except IOError: # key does not exists, give up
        return ''
    ret = ' '.join(ssh_key)
    ssh_key.close()
    return ret

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
            '/cygdrive/c' under MS/Win, etc ...
    """

    if client['protocol'] == 'ssh':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        client['transp_args'] = ['-T', '-i', client['cert']]
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += ['-o', option]

    if client['protocol'] == 'wget':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        if not 'proto_args' in client:
            client['proto_args'] = ['-nv']
        if 'maxbw' in client:
            client['proto_args'] += ['--limit-rate', '%d' % client['maxbw'] ] # bwlimit arg in b/s
        client['transp_args'] = ['-T', '-i', client['cert']]
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += ['-o', option]

    if client['protocol'] == 'rsyncssh':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        sshoptions = ['/usr/bin/ssh', '-i', client['cert']]
        if not 'proto_args' in client:
            client['proto_args'] = ['--archive', '--verbose']
        for option in LauncherConfig().ssh_options:
            sshoptions += ['-o', option]
        client['proto_args'] += ['--rsh', ' '.join(sshoptions)]
        if 'maxbw' in client:
            client['proto_args'] += ['--bwlimit', '%d' % int(client['maxbw'] / (1024 * 8)) ] # bwlimit arg in kB/s

    if client['protocol'] == 'wol':
        if not 'addr' in client:
            client['addr'] = 'FF:FF:FF:FF:FF:FF'
        if not 'bcast' in client:
            client['bcast'] = '255.255.255.255'
        if not 'port' in client:
            client['port'] = '40000'
    return client

class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
