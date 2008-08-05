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

# My functions
from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.network import chooseClientIP

def chooseLauncher():
    """ return a good launcher, URI form """

    def _finalback(stats):
        import random
        used_slots = 0
        # remove full launchers
        for k,v in stats.items():
            used_slots += v['slotused']
            if v['slottotal'] == v['slotused']:
                del stats[k]
        # give up if we may go beyond limit
        if used_slots >= SchedulerConfig().max_slots:
            raise Exception('chooseLauncher()', "Giving up, as we may go beyond our max of %s slots used" % SchedulerConfig().max_slots)
        if len(stats.keys()) == 0:
            raise Exception('chooseLauncher()', "Giving up, no slot seems to be left on launchers")
        best_launcher = stats.keys()[random.randint(0, len(stats.keys())-1)]
        return SchedulerConfig().launchers_uri[best_launcher]

    def _callback(result, stats, launchers, current_launcher):
        # we just got a result from a launcher, let's stack it

        if result:
            if stats:
                stats.update({current_launcher: result})
            else:
                stats={current_launcher: result}
        # if there is at least one launcher to process, do it
        if launchers:
            (next_launcher_name, next_launcher_uri) = launchers.popitem()
            d = callOnLauncher(next_launcher_uri, 'get_health')
            d.addCallback(_callback, stats, launchers, next_launcher_name)
            return d
        else: # no more launcher left, give up
            return _finalback(stats)
    return _callback(None, None, SchedulerConfig().launchers_uri.copy(), None)

def pingClient(uuid, fqdn, shortname, ips, macs):
    # choose a way to perform the operation
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs
    })
    return callOnBestLauncher('icmp', client)

def probeClient(uuid, fqdn, shortname, ips, macs):
    # choose a way to perform the operation
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs
    })
    return callOnBestLauncher('probe', client)

def pingAndProbeClient(uuid, fqdn, shortname, ips, macs):
    def _pingcb(result, uuid=uuid, fqdn=fqdn, shortname=shortname, ips=ips, macs=macs):
        def _probecb(result, uuid=uuid, fqdn=fqdn, shortname=shortname, ips=ips, macs=macs):
            if not result == "Not available":
                return 2
            return 1
        if result:
            mydeffered = probeClient(uuid, fqdn, shortname, ips, macs)
            mydeffered.addCallback(_probecb)
            return mydeffered
        return 0
    mydeffered = pingClient(uuid, fqdn, shortname, ips, macs)
    mydeffered.addCallback(_pingcb)
    return mydeffered

def downloadFile(uuid, fqdn, shortname, ips, macs, path):
    # choose a way to perform the operation
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs
    })
    return callOnBestLauncher('download_file', client, path)

def callOnLauncher(launcher, method, *args):
    import pulse2.scheduler.xmlrpc
    return pulse2.scheduler.xmlrpc.getProxy(launcher).callRemote(method, *args)

def callOnBestLauncher(method, *args):
    import pulse2.scheduler.xmlrpc

    def _eb(reason):
        logging.getLogger().error("scheduler %s: error %s" % (SchedulerConfig().name, reason.getErrorMessage()))

    return chooseLauncher().\
        addCallback(pulse2.scheduler.xmlrpc.getProxy).\
        addCallback(lambda x: x.callRemote(method, *args)).\
        addErrback(_eb)
