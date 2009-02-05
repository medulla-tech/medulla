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
import logging

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

def getBalance(config):
    """ Attempt to give enought information to take a decision on
    how to make a deployment the better way
    """
    from pulse2.launcher.process_control import ProcessList

    # our full process list
    process_list = ProcessList().listProcesses()

    # will contain som stats per group
    group_stats = {}

    # built "counts" struct
    # one item per group, containing the following keys:
    # - total number of process
    # - number of available process
    # - amount of running process
    # - amount of zombie process
    counts = {'total': 0, 'running': 0, 'zombie': 0, 'free': config["slots"]}

    # built "group" struct => to balance by group
    # one item per group, containing the following keys:
    # - total number of process in the group
    # - amount of running process in the group
    # - amount of zombie process in the group
    group_stats = {}

    # built "kind" struct => to balance by kind
    # one item per group, containing the following keys:
    # - total number of process by kind
    # - amount of running process by kind
    # - amount of zombie process by kind
    kind_stats = {}

    for process_id in process_list:
        process_state = process_list[process_id].getState()
        if not process_state['group'] in group_stats: # initialize struct
            group_stats[process_state['group']] = {'total': 0, 'running': 0, 'zombie': 0}
        if not process_state['kind'] in kind_stats: # initialize struct
            kind_stats[process_state['kind']] = {'total': 0, 'running': 0, 'zombie': 0}
        group_stats[process_state['group']]['total'] += 1
        kind_stats[process_state['kind']]['total'] += 1
        counts['total'] += 1
        counts['free'] -= 1
        if process_state['done']:
            group_stats[process_state['group']]['zombie'] += 1
            kind_stats[process_state['kind']]['zombie'] += 1
            counts['zombie'] += 1
        else:
            group_stats[process_state['group']]['running'] += 1
            kind_stats[process_state['kind']]['running'] += 1
            counts['running'] += 1

    return {'by_group': group_stats, 'global': counts, 'by_kind': kind_stats}

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
        cached = 0
        buffers = 0
        swap_total = 0
        swap_free = 0
        meminfo = open("/proc/meminfo")
        for line in meminfo:
            if line.startswith("MemTotal:"):
                total = int(line.split()[1])
            elif line.startswith("MemFree:"):
                free = int(line.split()[1])
            elif line.startswith("Cached:"):
                cached = int(line.split()[1])
            elif line.startswith("Buffers:"):
                buffers = int(line.split()[1])
            elif line.startswith("SwapTotal:"):
                swap_total = int(line.split()[1])
            elif line.startswith("SwapFree:"):
                swap_free = int(line.split()[1])
        meminfo.close()
        return total, total-cached-buffers, swap_total-swap_free # return is always in kB

    from pulse2.launcher.process_control import ProcessList
    total, free, swapused = getMem()
    return {
        "loadavg" : getLoadAvg(),
        "memfree" : free,
        "memused" : total - free,
        "swapused": swapused,
        "slottotal" : config["slots"],
        "slotused" : ProcessList().getProcessCount()
        }

def setDefaultClientOptions(client):
    """
        client is a simple dict, which should contain required connexion infos, for now:
            group: an optional group membership
            server_check: an dict of stuff-to-check-on-client (see pulse2-output-wrapper)
            client_check: an dict of stuff-to-check-on-client (see pulse2-output-wrapper)
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

    # client group, used to define 'targets' groups to gather aggregated stats
    if not 'group' in client:
        client['group'] = None

    if not 'server_check' in client:
        client['server_check'] = None

    if not 'client_check' in client:
        client['client_check'] = None

    if not 'action' in client:
        client['action'] = None

    # command execution throught SSH
    if client['protocol'] == 'ssh':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        client['transp_args'] = ['-T', '-o', 'IdentityFile=%s' % client['cert'], '-o', 'User=%s' % client['user']]
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += ['-o', option]
        if LauncherConfig().ssh_forward_key == 'always' or \
            LauncherConfig().ssh_forward_key == 'let' and 'forward_key' in client:
            client['transp_args'] += ['-A']
        else:
            client['transp_args'] += ['-a']

    # TCP forwarding through SSH, mainly used for VNC proxying
    if client['protocol'] == 'tcpsproxy':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        client['transp_args'] = ['IdentityFile=%s' % client['cert'], 'User=%s' % client['user']]
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += [option]
        client['transp_args'] += ["UserKnownHostsFile=/dev/null"] # required to prevent tcp forwarding failure

    # Push/pull mode using wget driven by SSH
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
        if LauncherConfig().wget_resume:
            client['proto_args'] += ['-c']
        if LauncherConfig().wget_options != '':
            client['proto_args'] += LauncherConfig().wget_options
        if 'maxbw' in client: # FIXME: handle low values of BWLimit (see mechanism below for rsync)
            client['proto_args'] += ['--limit-rate', '%d' % int(client['maxbw'] / 8) ] # bwlimit arg in B/s
        client['transp_args'] = ['-T', '-o', 'IdentityFile=%s' % client['cert'], '-o', 'User=%s' % client['user']]
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += ['-o', option]

    # Local Proxy mode (obviously using rsync)
    if client['protocol'] == 'rsyncproxy':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        client['transp_args'] = ['-T', '-o', 'IdentityFile=%s' % client['cert'], '-o', 'User=%s' % client['user']]
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += ['-o', option]
        client['transp_args'] += ['-A'] # always forward TCP key
        client['transp_args'] += ['-o', 'UserKnownHostsFile=/dev/null'] # required to prevent key forwarding failure
        if not 'proto_args' in client:
            client['proto_args'] = ['--archive', '--verbose']
        # inside ssh get the same args as outside ssh
        client['proto_args'] += ['--rsh="/usr/bin/ssh %s"' % ' '.join(map(lambda x:'-o %s' % x, LauncherConfig().ssh_options))]

    if client['protocol'] == 'rsyncssh':
        if not 'port' in client:
            client['port'] = 22
        if not 'user' in client:
            client['user'] = 'root'
        if not 'cert' in client:
            client['cert'] = LauncherConfig().ssh_keys[LauncherConfig().ssh_defaultkey]
        client['transp_args'] = ['-o', 'IdentityFile=%s' % client['cert'], '-o', 'User=%s' % client['user']]
        if not 'proto_args' in client:
            client['proto_args'] = ['--archive', '--verbose']
            if not LauncherConfig().is_rsync_limited:
                client['proto_args'].extend(['--no-group',  '--no-owner',  '--chmod=%s'%(LauncherConfig().rsync_set_chmod)])
        if LauncherConfig().rsync_resume:
            client['proto_args'] += ['--partial', '--append']
        for option in LauncherConfig().ssh_options:
            client['transp_args'] += ['-o', option]
        client['proto_args'] += ['--rsh', ' '.join(['/usr/bin/ssh'] + client['transp_args'])]
        if 'maxbw' in client:
            if client['maxbw'] == 0: # bwlimit forced to 0 => no BW limit
                pass
            else:
                bwlimit = int(client['maxbw'] / (1024 * 8))
                if bwlimit < 1:
                    bwlimit = 1 # as bwlimit = 0 imply no limit, min bwlimit set to 1
                client['proto_args'] += ['--bwlimit', '%d' %  bwlimit] # bwlimit arg in kB/s
    return client
