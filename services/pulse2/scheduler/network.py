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

# regular modules
import logging
import re

# My functions
from pulse2.scheduler.config import SchedulerConfig

# MMC
import mmc.support.mmctools

def pingAndProbeClient(uuid, fqdn, shortname, ips, macs):
    # TODO: a cache system ?!
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs
    })
    def _probecb(result):
        ptype = "\n".join(result)
        logging.getLogger().debug(result)
        if ptype == 'FAILED':
            logging.getLogger().debug('scheduler %s: can ping, but can\'t connect to client \'%s\' (got error: %s)' % (SchedulerConfig().name, client, result))
            return 1
        logging.getLogger().debug('scheduler %s: can connect to client \'%s\' (got %s)' % (SchedulerConfig().name, client, ptype))
        return 2
    def _probeeb(result):
        logging.getLogger().debug('scheduler %s: can ping, but can\'t connect to client \'%s\' (got error: %s)' % (SchedulerConfig().name, client, result))
        return 1
    def _pingcb(result, client = client):
        myresult = "\n".join(result)
        if myresult == 'OK':
            command = '%s %s' % (SchedulerConfig().prober_path, client)
            logging.getLogger().debug(command)
            return mmc.support.mmctools.shlaunchDeferred(command).addCallback(_probecb).addErrback(_probeeb)
        logging.getLogger().debug('scheduler %s: can\'t ping client \'%s\' (got %s)' % (SchedulerConfig().name, client, myresult))
        return 0
    def _pingeb(result):
        logging.getLogger().debug('scheduler %s: can\'t ping client \'%s\' (got error: %s)' % (SchedulerConfig().name, client, result))
        return 0
    if client:
        command = '%s %s' % (SchedulerConfig().ping_path, client)
        logging.getLogger().debug("do probe using the following command: %s" % command)
        return mmc.support.mmctools.shlaunchDeferred(command).addCallback(_pingcb).addErrback(_pingeb)
    else:
        return 0


def probeClient(uuid, fqdn, shortname, ips, macs):
    idData = [
         { 'platform': "Microsoft Windows", 'pcre': "Windows", "tmp_path": "/lsc", "root_path": "/cygdrive/c"},
         { 'platform': "GNU Linux", 'pcre': "Linux", "tmp_path": "/tmp/lsc", "root_path": "/"},
         { 'platform': "Sun Solaris", 'pcre': "SunOS", "tmp_path": "/tmp/lsc", "root_path": "/"},
         { 'platform': "IBM AIX", 'pcre': "AIX", "tmp_path": "/tmp/lsc", "root_path": "/"},
         { 'platform': "HP UX", 'pcre': "HP-UX", "tmp_path": "/tmp/lsc", "root_path": "/"},
         { 'platform': "Apple MacOS", 'pcre': "Darwin", "tmp_path": "/tmp/lsc", "root_path": "/"}
    ]
    # TODO: a cache system ?!
    def _cb(result):
        ptype = "\n".join(result)
        for identification in idData:
            if re.compile(identification["pcre"]).search(ptype) or ptype == identification["platform"]:
                logging.getLogger().debug('scheduler %s: found os |%s| for client \'%s\'' % (SchedulerConfig().name, identification["platform"], client))
                return identification["platform"]
        logging.getLogger().debug('scheduler %s: can\'t probe os for client \'%s\' (got %s)' % (SchedulerConfig().name, client, ptype))
        return "Other/N.A."
    def _eb(result):
        logging.getLogger().debug('scheduler %s: can\'t probe os for client \'%s\' (got error: %s)' % (SchedulerConfig().name, client, result))
        return "Can't connect"
    client = chooseClientIP({
            'uuid': uuid,
            'fqdn': fqdn,
            'shortname': shortname,
            'ips': ips,
            'macs': macs
    })
    command = '%s %s' % (SchedulerConfig().prober_path, client)
    return mmc.support.mmctools.shlaunchDeferred(command).addCallback(_cb).addErrback(_eb)

def chooseClientIP(target):
    """
        Attempt to guess how to reach our client

        Available informations:
        - FQDN
        - IP adresses, in order of interrest

        Expected target struct:
        {
            'uuid': ,
            'fqdn': ,
            'shortname': ,
            'ips': [],
            'macs': []
        }

        Probes:
        - FQDN resolution
        - Netbios resolution
        - Host resolution
        - IP check
    """
    for method in SchedulerConfig().resolv_order:
        if method == 'fqdn':
            result = chooseClientIPperFQDN(target)
            if result:
                logging.getLogger().debug("will connect to %s as %s using DNS resolver" % (target, result))
                return result
            logging.getLogger().debug("won't connect to %s using DNS resolver" % (target))
        if method == 'netbios':
            result = chooseClientIPperNetbios(target)
            if result:
                logging.getLogger().debug("will connect to %s as %s using Netbios resolver" % (target, result))
                return result
            logging.getLogger().debug("won't connect to %s using Netbios resolver" % (target))
        if method == 'hosts':
            result = chooseClientIPperHosts(target)
            if result:
                logging.getLogger().debug("will connect to %s as %s using Hosts" % (target, result))
                return result
            logging.getLogger().debug("won't connect to %s using Hosts" % (target))
        if method == 'ip':
            result = chooseClientIPperIP(target)
            if result:
                logging.getLogger().debug("will connect to %s as %s using IP given" % (target, result))
                return result
            logging.getLogger().debug("won't connect to %s using IP given" % (target))
    # (unfortunately) got nothing
    return None

def chooseClientIPperFQDN(target):
    import os
    # FIXME: port to twisted
    # FIXME: drop hardcoded path !
    # FIXME: use deferred
    command = "%s -s 1 -t a %s 2>/dev/null 1>/dev/null" % ('/usr/bin/host', target['fqdn'])
    if not os.system(command):
        return target['fqdn']
    return False

def chooseClientIPperNetbios(target):
    # FIXME: todo
    return False

def chooseClientIPperHosts(target):
    import os
    # FIXME: port to twisted
    # FIXME: drop hardcoded path !
    # FIXME: use deferred
    # FIXME: should be merged with chooseClientIPperFQDN ?
    command = "%s hosts %s 2>/dev/null 1>/dev/null" % ('/usr/bin/getent', target['fqdn'])
    if not os.system(command):
        return target['fqdn']
    command = "%s hosts %s 2>/dev/null 1>/dev/null" % ('/usr/bin/getent', target['shortname'])
    if not os.system(command):
        return target['shortname']
    return False

def chooseClientIPperIP(target):
    # TODO: weird, check only the first IP address :/
    if len(target['ips']) > 0:
        return target['ips'][0]
    return False
