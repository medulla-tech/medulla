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
    config = LauncherConfig()
    if config.scheduler_enablessl:
        uri = 'https://'
    else:
        uri = 'http://'
    if config.scheduler_username != '':
        uri += '%s:%s@' % (config.scheduler_username, config.scheduler_password)
    uri += '%s:%s' % (config.scheduler_host, config.scheduler_port)
    return uri

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

def getHealth(config):
    """
    Compute a health indicator as a dict with this keys:
     - usedmem : the used memory in Bytes
     - freemem : the free memory in Bytes
     - avgload : the average load (1 minute)

    @rtype: dict
    @returns: a dict containing the indicators
    """
    def getLoadAvg():
        f = open("/proc/loadavg")
        data = f.read()
        f.close()
        loadavg = float(data.split()[0])
        return loadavg

    def getMem():
        total = 0
        free = 0
        meminfo = open("/proc/meminfo")
        for line in meminfo:
            if line.startswith("MemTotal:"):
                total = int(line.split()[1])
            elif line.startswith("MemFree:"):
                free = int(line.split()[1])
        meminfo.close()
        return total * 1024, free * 1024 # return is always in B (not kB)

    from pulse2.launcher.process_control import ProcessList
    total, free = getMem()
    return {
        "loadavg" : getLoadAvg(),
        "memfree" : free,
        "memused" : total - free,
        "slottotal" : config["slots"],
        "slotused" : ProcessList().getProcessCount()
        }

def setDefaultClientOptions(client):
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
    # FIXME: handle missing keys

    if not 'timeout' in client:
        client['timeout'] = LauncherConfig().wrapper_max_exec_time

    if client['protocol'] == 'ssh':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        client['transp_args'] = ['-T', '-o', 'IdentityFile=%s' % client['cert']]
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += ['-o', option]
        if LauncherConfig().ssh_forward_key == 'always' or \
            LauncherConfig().ssh_forward_key == 'let' and 'forward_key' in client:
            client['transp_args'] += ['-A']
        else:
            client['transp_args'] += ['-a']

    if client['protocol'] == 'wget':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        if not 'proto_args' in client:
            client['proto_args'] = ['-nv']
        if not LauncherConfig().wget_check_certs:
            client['proto_args'] += ['--no-check-certificate']
        if LauncherConfig().wget_continue:
            client['proto_args'] += ['-c']
        if LauncherConfig().wget_options != '':
            client['proto_args'] += LauncherConfig().wget_options
        if 'maxbw' in client: # FIXME: handle low values of BWLimit (see mechanism below for rsync)
            client['proto_args'] += ['--limit-rate', '%d' % int(client['maxbw'] / 8) ] # bwlimit arg in B/s
        client['transp_args'] = ['-T', '-o', 'IdentityFile=%s' % client['cert']]
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += ['-o', option]

    if client['protocol'] == 'rsyncssh':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        sshoptions = ['/usr/bin/ssh', '-o', 'IdentityFile=%s' % client['cert']]
        if not 'proto_args' in client:
            client['proto_args'] = ['--archive', '--verbose']
        if LauncherConfig().rsync_partial:
            client['proto_args'] += ['--partial']
        for option in LauncherConfig().ssh_options:
            sshoptions += ['-o', option]
        client['proto_args'] += ['--rsh', ' '.join(sshoptions)]
        if 'maxbw' in client:
            if client['maxbw'] == 0: # bwlimit forced to 0 => no BW limit
                pass
            else:
                bwlimit = int(client['maxbw'] / (1024 * 8))
                if bwlimit < 1:
                    bwlimit = 1 # as bwlimit =0 imply no limit, min bwlimit set to 1
                client['proto_args'] += ['--bwlimit', '%d' %  bwlimit] # bwlimit arg in kB/s

    return client

class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance
