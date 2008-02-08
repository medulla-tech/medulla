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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# regular modules
import logging
import re

# My functions
from pulse2.scheduler.config import SchedulerConfig

# MMC
import mmc.support.mmctools

def probe_client(client):
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

def ping_client(client):
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
