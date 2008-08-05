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

# My functions
from pulse2.scheduler.config import SchedulerConfig

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
                logging.getLogger().debug("scheduler %s: will connect to %s as %s using DNS resolver" % (SchedulerConfig().name, target, result))
                return result
            logging.getLogger().debug("scheduler %s: won't connect to %s using DNS resolver" % (SchedulerConfig().name, target))
        if method == 'netbios':
            result = chooseClientIPperNetbios(target)
            if result:
                logging.getLogger().debug("scheduler %s: will connect to %s as %s using Netbios resolver" % (SchedulerConfig().name, target, result))
                return result
            logging.getLogger().debug("scheduler %s: won't connect to %s using Netbios resolver" % (SchedulerConfig().name, target))
        if method == 'hosts':
            result = chooseClientIPperHosts(target)
            if result:
                logging.getLogger().debug("scheduler %s: will connect to %s as %s using Hosts" % (SchedulerConfig().name, target, result))
                return result
            logging.getLogger().debug("scheduler %s: won't connect to %s using Hosts" % (SchedulerConfig().name, target))
        if method == 'ip':
            result = chooseClientIPperIP(target)
            if result:
                logging.getLogger().debug("scheduler %s: will connect to %s as %s using IP given" % (SchedulerConfig().name, target, result))
                return result
            logging.getLogger().debug("scheduler %s: won't connect to %s using IP given" % (SchedulerConfig().name, target))
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
