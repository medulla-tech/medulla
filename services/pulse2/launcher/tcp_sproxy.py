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
import time
import re

import twisted.internet.reactor
import twisted.internet.protocol

import pulse2.launcher.utils
import pulse2.launcher.process_control
from pulse2.launcher.config import LauncherConfig

SEPARATOR = u'·' # FIXME: duplicate of what we found in remote_exec.py !!

class proxyProtocol(twisted.internet.protocol.ProcessProtocol):
# this RE matched either ip:port or hostname:port
    RE_TCPIP = '((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([A-Za-z][A-Za-z0-9\-\.]+)):(0|([1-9]\d{0,3}|[1-5]\d{4}|[6][0-5][0-5]([0-2]\d|[3][0-5])))'
    RE_LINKINFO = '^LINK (%s,%s,%s,%s)$' % (RE_TCPIP, RE_TCPIP, RE_TCPIP, RE_TCPIP)
    RE_LINKERROR = '^LINK ERROR$'

    sourcePort = None
    proxyPort = None
    passthroughPort = None
    targetPort = None
    sourceIp = None
    proxyIp = None
    targetIp = None
    passthroughIp = None
    host = ''
    defferedLinkStatus = None

    def __init__(self):
        self.defferedLinkStatus = twisted.internet.defer.Deferred()
        if LauncherConfig().tcp_sproxy_host:
            self.host = LauncherConfig().tcp_sproxy_host

    def _mycustomcb(self, data):
        logging.getLogger().debug('cb: %s' % data)

    def outReceived(self, data):
        if re.match(self.RE_LINKINFO, data):
            ((self.sourceIp, self.sourcePort), (self.proxyIp, self.proxyPort), (self.passthroughIp, self.passthroughPort), (self.targetIp, self.targetPort))  = map(lambda a: a.split(":"), re.search(self.RE_LINKINFO, data).group(1).split(','))
            logging.getLogger().debug('got link status: %s' % data)
            ret = (LauncherConfig().name, self.host, self.proxyPort);
            self.defferedLinkStatus.callback(ret)
        else:
            logging.getLogger().debug('got link status: %s' % data)
            self.defferedLinkStatus.callback(False)


def establishProxy(target, requestor_ip, requested_port):
    """
    Establish a TCP connection to client using our proxy
    """
    client = pulse2.launcher.utils.setDefaultClientOptions({'protocol': 'tcpsproxy'})

    # FIXME: target should be "client format" compliant

    # Built "exec" command
    real_command = [
        LauncherConfig().tcp_sproxy_path,
        requestor_ip,
        target,
        requested_port,
        ','.join(client['transp_args']),
        str(LauncherConfig().tcp_sproxy_port_range_start),
        str(LauncherConfig().tcp_sproxy_port_range_end),
        str(LauncherConfig().tcp_sproxy_establish_delay),
        str(LauncherConfig().tcp_sproxy_connect_delay),
        str(LauncherConfig().tcp_sproxy_session_lenght)
    ]

    # Built "thru" command
    thru_command_list  = ['/usr/bin/ssh']
    thru_command_list += client['transp_args']
    thru_command_list += [ "%s@%s" % ('root', target)]

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

    """
    X /usr/sbin/pulse2-output-wrapper
    X --no-wrap
    X --only-stdout
    X --remove-empty-lines
    X --exec-server-side
    X --exec=/usr/sbin/pulse2-tcp-sproxy·192.168.21.1·192.168.0.16·5900·IdentityFile=/etc/mmc/pulse2/id_dsa,StrictHostKeyChecking=no,Batchmode=yes,PasswordAuthentication=no,ServerAliveInterval=10,CheckHostIP=no,ConnectTimeout=10,UserKnownHostsFile=/dev/null·8100·8200·20·60·3600
    X --thru /usr/bin/ssh·-o·IdentityFile=/etc/mmc/pulse2/id_dsa·-o·StrictHostKeyChecking=no·-o·PasswordAuthentication=no·-o·CheckHostIP=no·root@192.168.0.16
    --check-server-side IP=1.2.3.4
    --action=VNC
    """

    """
    # from {'a': 'b', 'c: 'd'} to 'a=b,c=d'
    if client['client_check']:
        command_list += ['--check-client-side', ','.join(map((lambda x: '='.join(x)), client['client_check'].items()))]
    if client['server_check']:
        command_list += ['--check-server-side', ','.join(map((lambda x: '='.join(x)), client['server_check'].items()))]
    if client['action']:
        command_list += ['--action', client['action']]
    """

    proxy = proxyProtocol()
    handler = twisted.internet.reactor.spawnProcess(proxy, command_list[0], command_list, None)
    logging.getLogger().debug('about to execute ' + ' '.join(command_list))
    return proxy.defferedLinkStatus
