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

import twisted.web.xmlrpc

# My functions
from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.network import chooseClientIP

def getPubKey(launcher, key_name):
    """ returns a pubkey from launcher "launcher" """
    def __cb(result):
        return result
    def __eb(reason):
        return ''

    if launcher == None or launcher == '':
        launcher = chooseLauncher()
    mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
        'get_pubkey',
        key_name
    )
    mydeffered.addCallback(__cb).addErrback(__eb)
    return mydeffered

def chooseLauncher():
    """ Select a launcher """
    import random
    launchers = SchedulerConfig().launchers
    launcher = launchers[random.sample(launchers.keys(), 1).pop()]
    if launcher["enablessl"]:
        uri = "https://"
    else:
        uri = 'http://'
    if launcher['username'] != '':
        uri += '%s:%s@' % (launcher['username'], launcher['password'])
    uri += '%s:%d' % (launcher['host'], int(launcher['port']))
    return uri

def pingClient(uuid, fqdn, shortname, ips, macs):
    # choose launcher
    launcher = chooseLauncher()
    # choose a way to perform the operation
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs
    })
    # perform call
    mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
        'icmp',
        client
    )
    return mydeffered

def probeClient(uuid, fqdn, shortname, ips, macs):
    # choose launcher
    launcher = chooseLauncher()
    # choose a way to perform the operation
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs
    })
    # perform call
    mydeffered = twisted.web.xmlrpc.Proxy(launcher).callRemote(
        'probe',
        client
    )
    return mydeffered

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
