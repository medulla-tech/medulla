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

class proxyProtocol(twisted.internet.protocol.ProcessProtocol):
# this RE matched either ip:port or hostname:port
    RE_TCPIP = '((25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9])\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[1-9]|0)\.(25[0-5]|2[0-4][0-9]|[0-1]{1}[0-9]{2}|[1-9]{1}[0-9]{1}|[0-9])|([A-Za-z][A-Za-z0-9\-\.]+)):(0|([1-9]\d{0,3}|[1-5]\d{4}|[6][0-5][0-5]([0-2]\d|[3][0-5])))'
    RE_PROXYINFOS = '^LINK (%s,%s,%s,%s)$' % (RE_TCPIP, RE_TCPIP, RE_TCPIP, RE_TCPIP)

    sourcePort = None
    proxyPort = None
    passthroughPort = None
    targetPort = None
    sourceIp = None
    proxyIp = None
    targetIp = None
    passthroughIp = None

    defferedLinkStatus = None

    def __init__(self):
        self.defferedLinkStatus = twisted.internet.defer.Deferred()
        self.defferedLinkStatus.addCallback(lambda x: x.proxyPort)

    def outReceived(self, data):
        if re.match(self.RE_PROXYINFOS, data):
            ((self.sourceIp, self.sourcePort), (self.proxyIp, self.proxyPort), (self.passthroughIp, self.passthroughPort), (self.targetIp, self.targetPort))  = map(lambda a: a.split(":"), re.search(self.RE_PROXYINFOS, data).group(1).split(','))
            logging.getLogger().debug('got link status: %s' % data)
            self.defferedLinkStatus.callback(self)
        else:
            return False

def establishProxy(target, requestor_ip, requested_port):
    """
    Establish a TCP connection to client using our proxy
    """
    client = pulse2.launcher.utils.setDefaultClientOptions({'protocol': 'tcpsproxy'})

    # Build final command line
    command_list = [
        LauncherConfig().tcp_sproxy_path,
        requestor_ip,
        target,
        requested_port,
        ','.join(LauncherConfig().ssh_options)
    ]

    proxy = proxyProtocol()
    handler = twisted.internet.reactor.spawnProcess(proxy, command_list[0], command_list, None)
    logging.getLogger().debug('about to execute ' + ' '.join(command_list))
    return proxy.defferedLinkStatus
