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

import logging
import socket
import fcntl
import struct

import twisted.internet.reactor
import twisted.internet.protocol
from twisted.internet import task
from twisted.internet.error import ProcessDone

import pulse2.launcher.utils
import pulse2.launcher.process_control
from pulse2.launcher.config import LauncherConfig
from pulse2.network import NetUtils

SEPARATOR = u'·' # FIXME: duplicate of what we found in remote_exec.py !!

class proxyProtocol(twisted.internet.protocol.ProcessProtocol):
    def processEnded(self, reason):
        if hasattr(reason, "trap"):
            if reason.trap(ProcessDone):
                logging.getLogger().debug("TCP SSH Proxy successfully terminated")
                return
        logging.getLogger().warn("TCP SSH Proxy terminated with exception: %s" % str(reason))


def establishProxy(client, requestor_ip, requested_port):
    """
    Establish a TCP connection to client using our proxy
    """
    client = pulse2.launcher.utils.setDefaultClientOptions(client)
    """
    client['client_check'] = getClientCheck(client)
    client['server_check'] = getServerCheck(client)
    client['action'] = getAnnounceCheck('vnc')
    """
    def generate_auth_key():
        import random
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$-_.+!*()'
        size = 15
        return ''.join(random.choice(chars) for x in range(size))

    if LauncherConfig().create_web_proxy:
        auth_key = generate_auth_key()
    else:
        auth_key = '-'

    proxy_port, local_port = allocate_port_couple()
    # Built "exec" command
    real_command = [
        LauncherConfig().tcp_sproxy_path,
        requestor_ip,
        client['host'],
        requested_port,
        ','.join(client['transp_args']),
        str(proxy_port),
        str(local_port),
        str(LauncherConfig().tcp_sproxy_establish_delay),
        str(LauncherConfig().tcp_sproxy_connect_delay),
        str(LauncherConfig().tcp_sproxy_session_lenght),
        client['shortname'],
        auth_key,
    ]

    # Built "thru" command
    thru_command_list  = [LauncherConfig().ssh_path]
    for option in client['transp_args']:
        thru_command_list += ['-o', option]
    thru_command_list += [client['host']]

    command_list = [
        LauncherConfig().wrapper_path,
        '--max-log-size',
        str(LauncherConfig().wrapper_max_log_size),
        #'--max-exec-time', # FIXME: wrapper_timeout missing in function signature :/
        #str(wrapper_timeout),
        '--exec',
        SEPARATOR.join(real_command),
        '--thru',
        SEPARATOR.join(thru_command_list),
        '--no-wrap',
        '--only-stdout',
        '--remove-empty-lines',
        '--exec-server-side'
    ]

    # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
    if client['client_check']:
        command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
    if client['server_check']:
        command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
    if client['action']:
        command_list += ['--action', client['action']]

    proxy = proxyProtocol()
    twisted.internet.reactor.spawnProcess(
        proxy,
        command_list[0],
        map(lambda(x): x.encode('utf-8', 'ignore'), command_list),
        None, # env
        None, # path
        None, # uid
        None, # gid
        None, # usePTY
        { 0: "w", 1: 'r', 2: 'r' } # FDs: not closing STDIN (might be used)
    )

    def get_ip_address(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

    def parse_result():
        if LauncherConfig().tcp_sproxy_host:
            tcp_sproxy_host = LauncherConfig().tcp_sproxy_host
        else:
            # Take the first network interface
            logging.getLogger().info('tcp_sproxy_host param was not specified in launcher config')
            logging.getLogger().info('taking first interface IP Address')
            tcp_sproxy_host = get_ip_address('eth0')
        return LauncherConfig().name, tcp_sproxy_host, proxy_port, auth_key
    # Waiting to establish the proxy
    ret = task.deferLater(twisted.internet.reactor, 2, parse_result)
    logging.getLogger().debug('about to execute ' + ' '.join(command_list))
    return ret

def allocate_port_couple():
    """
    Looking for two free ports to establish SSH proxy.

    @return: two free ports
    @rtype: list
    """
    ret_ports = []
    port_range = range(LauncherConfig().tcp_sproxy_port_range_start + 1,
                       LauncherConfig().tcp_sproxy_port_range_end + 1)

    for port in port_range :
        if NetUtils.is_port_free(port):
            ret_ports.append(port)

        if len(ret_ports) == 2 :
            logging.getLogger().debug("Allocated ports to build TCP SSH Proxy: (%d:%d)" % tuple(ret_ports))
            return ret_ports


