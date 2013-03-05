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
import random
import sqlalchemy.orm

# My functions
from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.network import chooseClientIP
from pulse2.scheduler.checks import getCheck, getAnnounceCheck
import pulse2.scheduler.xmlrpc

from pulse2.database.msc.orm.commands_on_host import CommandsOnHost

def chooseLauncher():
    """ return a good launcher, URI form """

    def _extract_best_candidate(launchers):
        # return the best launcher, return the corresponding key

        best_launcher = None
        best_score = 0

        for (k, v) in launchers.items():
            if 'slots' in v:
                v = v['slots'] # to ensure backward compatibility with pre-20090224 launchers
            score = v['slottotal'] - v['slotused'] # score computed using free slots
            if score > best_score:
                best_score = score
                best_launcher = k

        return best_launcher

    def _finalback(stats):
        used_slots = 0
        if len(stats.keys()) == 0:
            raise Exception("Every launchers seems to be dead !!!")
        # remove full launchers
        for k,v in stats.items():
            if 'slots' in v:
                v = v['slots'] # to ensure backward compatibility with pre-20090224 launchers
            used_slots += v['slotused']
            if v['slottotal'] == v['slotused']:
                del stats[k]

        # give up if we may go beyond limit
        if used_slots >= SchedulerConfig().max_slots:
            raise Exception("Gone beyond our max of %s slots used" % SchedulerConfig().max_slots)
        if len(stats.keys()) == 0:
            raise Exception("No free slots on launchers")
        return SchedulerConfig().launchers_uri[_extract_best_candidate(stats)]

    def _eb(reason, stats, launchers, current_launcher):
        logging.getLogger().error("scheduler %s: while talking to launcher %s: %s" % (SchedulerConfig().name, current_launcher, reason.getErrorMessage()))
        if launchers:
            (next_launcher_name, next_launcher_uri) = launchers.popitem()
            d = callOnLauncher(None, next_launcher_uri, 'get_health')
            d.addCallback(_callback, stats, launchers, next_launcher_name).\
            addErrback(_eb, stats, launchers, next_launcher_name)
            return d
        else: # no more launcher left, give up
            return _finalback(stats)

    def _callback(result, stats, launchers, current_launcher):
        # we just got a result from a launcher, let's stack it
        if result:
            stats.update({current_launcher: result})
        # if there is at least one launcher to process, do it
        if launchers:
            # shuffle launchers
            a = launchers.items()
            random.shuffle(a)
            (next_launcher_name, next_launcher_uri) = a.pop()
            launchers = dict(a)

            d = callOnLauncher(None, next_launcher_uri, 'get_health')
            d.addCallback(_callback, stats, launchers, next_launcher_name).\
            addErrback(_eb, stats, launchers, next_launcher_name)
            return d
        else: # no more launcher left, give up
            return _finalback(stats)

    return _callback(None, {}, SchedulerConfig().launchers_uri.copy(), None)

def getLaunchersBalance():
    """ return balancing status for launchers """

    def _eb(reason, stats, launchers, current_launcher):
        logging.getLogger().error("scheduler %s: while talking to launcher %s: %s" % (SchedulerConfig().name, current_launcher, reason.getErrorMessage()))
        if launchers:
            (next_launcher_name, next_launcher_uri) = launchers.popitem()
            d = callOnLauncher(None, next_launcher_uri, 'get_balance')
            d.addCallback(_callback, stats, launchers, next_launcher_name).\
            addErrback(_eb, stats, launchers, next_launcher_name)
            return d
        else: # no more launcher left, give up
            return stats

    def _callback(result, stats, launchers, current_launcher):
        # we just got a result from a launcher, let's stack it
        if result:
            stats.update({current_launcher: result})
        # if there is at least one launcher to process, do it
        if launchers:
            (next_launcher_name, next_launcher_uri) = launchers.popitem()
            d = callOnLauncher(None, next_launcher_uri, 'get_balance')
            d.addCallback(_callback, stats, launchers, next_launcher_name).\
            addErrback(_eb, stats, launchers, next_launcher_name)
            return d
        else: # no more launcher left, give up
            return stats

    return _callback(None, {}, SchedulerConfig().launchers_uri.copy(), None)

def pingClient(uuid, fqdn, shortname, ips, macs, netmasks):
    # choose a way to perform the operation
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs,
            'netmasks': netmasks
    })
    return callOnBestLauncher(None, 'icmp', False, client)

def probeClient(uuid, fqdn, shortname, ips, macs, netmasks):
    # choose a way to perform the operation
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs,
            'netmasks': netmasks
    })
    return callOnBestLauncher(None, 'probe', 'Unknown', client)

def pingAndProbeClient(uuid, fqdn, shortname, ips, macs, netmasks):
    """ returns
        0 => ping NOK
        1 => ping OK, ssh NOK
        2 => ping OK, ssh OK
    """
    def _pingcb(result, uuid=uuid, fqdn=fqdn, shortname=shortname, 
            ips=ips,macs=macs, netmasks=netmasks):
        def _probecb(result, uuid=uuid, fqdn=fqdn, shortname=shortname, 
                     ips=ips, macs=macs, netmasks=netmasks):
            if not result == "Not available":
                return 2
            return 1
        if result:
            mydeffered = probeClient(uuid, fqdn, shortname, ips, macs, netmasks)
            mydeffered.addCallback(_probecb)
            return mydeffered
        return 0
    mydeffered = pingClient(uuid, fqdn, shortname, ips, macs, netmasks)
    mydeffered.addCallback(_pingcb)
    return mydeffered

def downloadFile(uuid, fqdn, shortname, ips, macs, netmasks, path, bwlimit):
    # choose a way to perform the operation

    # choose a way to perform the operation
    ip = chooseClientIP({
        'uuid': uuid,
        'fqdn': fqdn,
        'shortname': shortname,
        'ips': ips,
        'macs': macs,
        'netmasks': netmasks
     })

    client = {
        'host': ip,
        'uuid': uuid,
        'shortname': shortname,
        'ip': ips,
        'macs': macs,
        'protocol': 'ssh'
    }
    client['client_check'] = getClientCheck(client)
    client['server_check'] = getServerCheck(client)
    client['action'] = getAnnounceCheck('download')

    return callOnBestLauncher(None, 'download_file', False, client, path, bwlimit)

def establishProxy(uuid, fqdn, shortname, ips, macs, netmasks, requestor_ip, requested_port):
    def _finalize(result):
        if type(result) == list: # got expected struct
            (launcher, host, port) = result
            if host == '':
                host = SchedulerConfig().launchers[launcher]['host']
            return (host, port)
        else:
            return False
    # choose a way to perform the operation
    ip = chooseClientIP({
        'uuid': uuid,
        'fqdn': fqdn,
        'shortname': shortname,
        'ips': ips,
        'macs': macs,
        'netmasks': netmasks
    })

    client = {
        'host': ip,
        'uuid': uuid,
        'shortname': shortname,
        'ip': ips,
        'macs': macs,
        'protocol': 'tcpsproxy'
    }
    client['client_check'] = getClientCheck(client)
    client['server_check'] = getServerCheck(client)
    client['action'] = getAnnounceCheck('vnc')

    return callOnBestLauncher(None, 'tcp_sproxy', False, client, requestor_ip, requested_port).\
        addCallback(_finalize).\
        addErrback(lambda reason: reason)

def getClientCheck(target):
    return getCheck(SchedulerConfig().client_check, target);

def getServerCheck(target):
    return getCheck(SchedulerConfig().server_check, target);

def callOnLauncher(coh_id, launcher, method, *args):
    # coh_id to keep a track of the command, set to None if we don't want to keep a track

    if coh_id: # FIXME: we may want to log launcher_name instead of launcher_uri
        session = sqlalchemy.orm.create_session()
        myCommandOnHost = session.query(CommandsOnHost).get(coh_id)
        session.close()
        for (k,v) in SchedulerConfig().launchers_uri.items():
            if v == launcher:
                myCommandOnHost.setCurrentLauncher(k)
                break

    def _eb(reason):
        logging.getLogger().warn("scheduler %s: while sending command to launcher %s : %s" % (SchedulerConfig().name, launcher, reason.getErrorMessage()))

    return pulse2.scheduler.xmlrpc.getProxy(launcher).\
        callRemote(method, *args).\
        addErrback(_eb)

def callOnBestLauncher(coh_id, method, default_error_return, *args):

    def _cb(launcher):
        return callOnLauncher(coh_id, launcher, method, *args)

    def _eb(reason):
        logging.getLogger().error("scheduler %s: while choosing the best launcher : %s" % (SchedulerConfig().name, reason.getErrorMessage()))
        return default_error_return

    return chooseLauncher().\
        addCallback(_cb).\
        addErrback(_eb)
