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

def probeClient(client):
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
    command = '%s %s' % (SchedulerConfig().prober_path, client)
    return mmc.support.mmctools.shlaunchDeferred(command).addCallback(_cb).addErrback(_eb)

def pingClient(client):
    # TODO: a cache system ?!
    def _cb(result):
        myresult = "\n".join(result)
        if myresult == 'OK':
            return True
        logging.getLogger().debug('scheduler %s: can\'t ping client \'%s\' (got %s)' % (SchedulerConfig().name, client, myresult))
        return False

    def _eb(result):
        logging.getLogger().debug('scheduler %s: can\'t ping client \'%s\' (got error: %s)' % (SchedulerConfig().name, client, result))
        return False
    command = '%s %s' % (SchedulerConfig().ping_path, client)
    return mmc.support.mmctools.shlaunchDeferred(command).addCallback(_cb).addErrback(_eb)

def wolClient(mac_addrs):
    def _cb(result):
        myresult = "\n".join(result)
        return myresult
    def _eb(result):
        logging.getLogger().debug('scheduler %s: can\'t wol client \'%s\' (got error: %s)' % (SchedulerConfig().name, client, result))
        return False
    # "linear-i-fy" MAC adresses
    if type(mac_addrs) == list:
        mac_addrs = ' '.join(mac_addrs)
    command = '%s --ipaddr=%s --port=%s %s' % (SchedulerConfig().wol_path, SchedulerConfig().wol_bcast, SchedulerConfig().wol_port, mac_addrs)
    return mmc.support.mmctools.shlaunchDeferred(command).addCallback(_cb).addErrback(_eb)

def chooseClientIP(myTarget):
    """
        Attempt to guess how to reach our client

        Available informations:
        - FQDN
        - IP adresses, in order of interrest

        Probes:
        - FQDN resolution
        - Netbios resolution
        - Host resolution
        - IP check
    """
    logger = logging.getLogger()
    for method in pulse2.scheduler.config.SchedulerConfig().resolv_order:
        if method == 'fqdn':
            result = chooseClientIPperFQDN(myTarget)
            if result:
                logger.debug("will connect to %s as %s using DNS resolver" % (myTarget.target_name, myTarget.target_name))
                return myTarget.target_name
        if method == 'netbios':
            result = chooseClientIPperNetbios(myTarget)
            if result:
                logger.debug("will connect to %s as %s using Netbios resolver" % (myTarget.target_name, myTarget.target_name))
                return myTarget.target_name # better return IP here :/
        if method == 'hosts':
            result = chooseClientIPperHosts(myTarget)
            if result:
                logger.debug("will connect to %s as %s using Hosts" % (myTarget.target_name, myTarget.target_name))
                return myTarget.target_name
        if method == 'ip':
            result = chooseClientIPperIP(myTarget)
            if result:
                logger.debug("will connect to %s as %s using IP given" % (myTarget.target_name, myTarget.target_ipaddr.split('||')[0]))
                return myTarget.target_ipaddr.split('||')[0]
    # (unfortunately) got nothing
    return None

def chooseClientIPperFQDN(myTarget):
    import os
    # FIXME: port to twisted
    # FIXME: drop hardcoded path !
    # FIXME: use deferred
    command = "%s -s 1 -t a %s 2>/dev/null 1>/dev/null" % ('/usr/bin/host', myTarget.target_name)
    result = os.system(command)
    return result == 0

def chooseClientIPperNetbios(myTarget):
    # FIXME: todo
    return False

def chooseClientIPperHosts(myTarget):
    import os
    # FIXME: port to twisted
    # FIXME: drop hardcoded path !
    # FIXME: use deferred
    # FIXME: should be merged with chooseClientIPperFQDN ?
    command = "%s hosts %s 2>/dev/null 1>/dev/null" % ('/usr/bin/getent', myTarget.target_name)
    result = os.system(command)
    return result == 0

def chooseClientIPperIP(myTarget):
    # TODO: weird, check only the first IP address :/
    if len(myTarget.target_ipaddr) == 0:
        return False
    result = myTarget.target_ipaddr.split('||')
    return len(result) > 0
