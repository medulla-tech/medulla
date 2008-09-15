# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# Twisted
import twisted.web.xmlrpc
import logging

# our stuff
from mmc.client import MMCProxy, makeSSLContext, XmlrpcSslProxy
from mmc.plugins.msc.config import MscConfig, makeURL

def getProxy(schedulerConfig):
    """
    Return a suitable Proxy object to communicate with the scheduler
    """
    config = MscConfig("msc")

    url =  makeURL(schedulerConfig)

    if url.startswith("http://"):
        ret = twisted.web.xmlrpc.Proxy(url)
    else:
        if schedulerConfig['verifypeer']:
            # We have to build the SSL context to include launcher certificates
            ctx = makeSSLContext(schedulerConfig['verifypeer'], schedulerConfig['cacert'], schedulerConfig['localcert'], False)
            ret = XmlrpcSslProxy(url)
            ret.setSSLClientContext(ctx)
        else:
            ret = twisted.web.xmlrpc.Proxy(url)
    return ret

def start_all_commands(scheduler):
    # FIXME: return something usefull !
    return getProxy(select_scheduler(scheduler)).callRemote(
        'start_all_commands'
    )

def start_these_commands(scheduler, commands):
    return getProxy(select_scheduler(scheduler)).callRemote(
        'start_these_commands',
        commands
    )

def ping_client(scheduler, computer):
    """
    expected struct for computer:
        [
            None,
            {
                'macAddress': ['XX:XX:XX:XX:XX:XX'],
                'displayName': ['NomType=A Dummy Client'],
                'cn': ['my-short-name'],
                'objectUUID': ['UUID1234'],
                'ipHostNumber': ['IP.AD.DR.ES'],
                'fullname': 'my-fully.qualified.domain.tld'
            }
        ]
    """
    def parseResult(result):
        logging.getLogger().debug('Ping computer %s: %s' % (computer, result))
        return result
    def parseError(reason):
        # FIXME: handle error
        return False
    # ping is done using available data:
    # - uuid
    # - fullname
    # - cn[]
    # - ipHostNumber[]
    # - macAddress[]
    mydeffered = getProxy(select_scheduler(scheduler)).callRemote(
        'ping_client',
        computer[1]['objectUUID'][0],
        computer[1]['fullname'],
        computer[1]['cn'][0],
        computer[1]['ipHostNumber'],
        computer[1]['macAddress'],
    )
    mydeffered.addCallback(parseResult).addErrback(parseResult)
    return mydeffered

def probe_client(scheduler, computer):
    def parseResult(result):
        logging.getLogger().debug('Probe client %s: %s' % (computer, result))
        return result
    def parseError(reason):
        # FIXME: handle error
        return False
    # probe is done using available data:
    # - uuid
    # - fullname
    # - cn[]
    # - ipHostNumber[]
    # - macAddress[]
    mydeffered = getProxy(select_scheduler(scheduler)).callRemote(
        'probe_client',
        computer[1]['objectUUID'][0],
        computer[1]['fullname'],
        computer[1]['cn'][0],
        computer[1]['ipHostNumber'],
        computer[1]['macAddress'],
    )
    mydeffered.addCallback(parseResult).addErrback(parseResult)
    return mydeffered

def ping_and_probe_client(scheduler, computer):
    def parseResult(result):
        logging.getLogger().debug('Ping then probe client %s: %s' % (computer, result))
        return result
    def parseError(reason):
        # FIXME: handle error
        return False
    # probe is done using available data:
    # - uuid
    # - fullname
    # - cn[]
    # - ipHostNumber[]
    # - macAddress[]
    mydeffered = getProxy(select_scheduler(scheduler)).callRemote(
        'ping_and_probe_client',
        computer[1]['objectUUID'][0],
        computer[1]['fullname'],
        computer[1]['cn'][0],
        computer[1]['ipHostNumber'],
        computer[1]['macAddress'],
    )
    mydeffered.addCallback(parseResult).addErrback(parseResult)
    return mydeffered

def stopCommand(scheduler, command_id):
    def parseResult(result):
        logging.getLogger().debug('Stop command %s: %s' % (command_id, result))
        return result
    def parseError(reason):
        # FIXME: handle error
        return False
    mydeffered = getProxy(select_scheduler(scheduler)).callRemote(
        'stop_command',
        command_id
    )
    mydeffered.addCallback(parseResult).addErrback(parseResult)
    return mydeffered

def startCommand(scheduler, command_id):
    def parseResult(result):
        logging.getLogger().debug('Start command %s: %s' % (command_id, result))
        return result
    def parseError(reason):
        # FIXME: handle error
        return False
    mydeffered = getProxy(select_scheduler(scheduler)).callRemote(
        'start_command',
        command_id
    )
    mydeffered.addCallback(parseResult).addErrback(parseResult)
    return mydeffered


def download_file(scheduler, computer, path, bwlimit):
    mydeffered = getProxy(select_scheduler(scheduler)).callRemote(
        'download_file',
        computer[1]['objectUUID'][0],
        computer[1]['fullname'],
        computer[1]['cn'][0],
        computer[1]['ipHostNumber'],
        computer[1]['macAddress'],
        path,
        bwlimit
    )
    return mydeffered

def tcp_sproxy(scheduler, computer, requestor_ip, requested_port):
    mydeffered = getProxy(select_scheduler(scheduler)).callRemote(
        'tcp_sproxy',
        computer[1]['objectUUID'][0],
        computer[1]['fullname'],
        computer[1]['cn'][0],
        computer[1]['ipHostNumber'],
        computer[1]['macAddress'],
        requestor_ip,
        requested_port
    )
    return mydeffered

def select_scheduler(scheduler_name):
    if not scheduler_name:
        scheduler_name = MscConfig("msc").default_scheduler
    if scheduler_name == '':
        scheduler_name = MscConfig("msc").default_scheduler
    return MscConfig('msc').schedulers[scheduler_name]

