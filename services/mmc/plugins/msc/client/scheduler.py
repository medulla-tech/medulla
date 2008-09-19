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
import twisted.internet.defer
import logging

# our stuff
from mmc.client import MMCProxy, makeSSLContext, XmlrpcSslProxy
from mmc.plugins.msc.config import MscConfig, makeURL
from mmc.plugins.msc.scheduler_api import SchedulerApi

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
    return getProxy(__select_scheduler(scheduler)).callRemote(
        'start_all_commands'
    )

def start_these_commands(scheduler, commands):
    return getProxy(__select_scheduler(scheduler)).callRemote(
        'start_these_commands',
        commands
    )

def ping_client(scheduler, computer):
    return process_on_client(scheduler, computer, 'ping_client')

def probe_client(scheduler, computer):
    return process_on_client(scheduler, computer, 'probe_client')

def ping_and_probe_client(scheduler, computer):
    return process_on_client(scheduler, computer, 'ping_and_probe_client')

def download_file(scheduler, computer, path, bwlimit):
    return process_on_client(scheduler, computer, 'download_file', path, bwlimit)

def tcp_sproxy(scheduler, computer, requestor_ip, requested_port):
    return process_on_client(scheduler, computer, 'tcp_sproxy', requestor_ip, requested_port)

def process_on_client(proposed_scheduler_name, computer, function, *args):
    """
        proposed_scheduler will be used in emergency case
        expected struct for computer (the target):
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

        probe is done using available data:
        - uuid
        - fullname
        - cn[]
        - ipHostNumber[]
        - macAddress[]
    """
    def parseResult(result):
        logging.getLogger().debug('%s %s: %s' % (function, computer, result))
        return result

    def runResult(result):
        # attempt to fall back on something known

        if not result or result == '':
            scheduler_name = proposed_scheduler_name
            if not scheduler_name or scheduler_name == '':
                scheduler_name = MscConfig("msc").default_scheduler
        else:
            scheduler_name = result
        logging.getLogger().debug("got %s as scheduler for client %s" % (scheduler_name, computer[1]['objectUUID'][0]))

        if scheduler_name not in MscConfig('msc').schedulers:
            logging.getLogger().warn("scheduler %s do not exists" % (scheduler_name))
            return twisted.internet.defer.fail(twisted.python.failure.Failure("Invalid scheduler %s (do not seems to exists)" % (scheduler_name)))

        mydeffered = getProxy(MscConfig('msc').schedulers[scheduler_name]).callRemote(
            function,
            computer[1]['objectUUID'][0],
            computer[1]['fullname'],
            computer[1]['cn'][0],
            computer[1]['ipHostNumber'],
            computer[1]['macAddress'],
            *args
        )
        mydeffered.addCallback(parseResult).addErrback(lambda reason: reason)
        return mydeffered

    mydeffered = SchedulerApi().getScheduler(computer[1]['objectUUID'][0])
    mydeffered.addCallback(runResult).addErrback(lambda reason: reason)
    return mydeffered

def stopCommand(scheduler, command_id):
    def parseResult(result):
        logging.getLogger().debug('Stop command %s: %s' % (command_id, result))
        return result
    def parseError(reason):
        # FIXME: handle error
        return False
    mydeffered = getProxy(__select_scheduler(scheduler)).callRemote(
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
    mydeffered = getProxy(__select_scheduler(scheduler)).callRemote(
        'start_command',
        command_id
    )
    mydeffered.addCallback(parseResult).addErrback(parseResult)
    return mydeffered


def __select_scheduler(scheduler_name):
    if not scheduler_name:
        scheduler_name = MscConfig("msc").default_scheduler
    if scheduler_name == '':
        scheduler_name = MscConfig("msc").default_scheduler
    return MscConfig('msc').schedulers[scheduler_name]
