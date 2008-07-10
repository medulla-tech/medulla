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

# Python stuff
import logging
import re

# Other stuff
from pulse2.launcher.config import LauncherConfig
import pulse2.launcher.process_control
import mmc.support.mmctools

def wolClient(mac_addrs):
    """ Send a BCast WOL packet to mac_addrs """
    def __cb_wol_end(shprocess):
        if not shprocess.exit_code == 0:
            logging.getLogger().warn("launcher %s: WOL failed: %s, %s" % (LauncherConfig().name, shprocess.stdout, shprocess.stderr))
            return False
        logging.getLogger().debug("launcher %s: WOL succeeded" % (LauncherConfig().name))
        return True

    command_list = [
        LauncherConfig().wol_path,
        '--ipaddr=%s' % LauncherConfig().wol_bcast,
        '--port=%s' % LauncherConfig().wol_port,
    ]

    # clean empty macs
    purged_mac_addrs = []
    for i in mac_addrs:
        if i:
            purged_mac_addrs.append(i)
    command_list += purged_mac_addrs

    return pulse2.launcher.process_control.commandRunner(
        command_list,
        __cb_wol_end
    )

def icmpClient(client, timeout):
    """ Send a Ping to our client """
    def __cb_wol_end(shprocess, client=client):
        if not shprocess.exit_code == 0:
            logging.getLogger().warn("launcher %s: ICMP failed on %s: %s, %s" % (LauncherConfig().name, client, shprocess.stdout, shprocess.stderr))
            return False
        logging.getLogger().debug("launcher %s: ICMP succeeded on %s" % (LauncherConfig().name, client))
        return True
    command_list = [
        LauncherConfig().ping_path,
        client
    ]
    # FIXME: use timeout
    return pulse2.launcher.process_control.commandRunner(
        command_list,
        __cb_wol_end,
    )

def probeClient(client, timeout):
    def __cb_probe_end(result, client=client):
        (exitcode, stdout, stderr) = result
        idData = [
             { 'platform': "Microsoft Windows", 'pcre': "Windows", "tmp_path": "/lsc", "root_path": "/cygdrive/c"},
             { 'platform': "GNU Linux", 'pcre': "Linux", "tmp_path": "/tmp/lsc", "root_path": "/"},
             { 'platform': "Sun Solaris", 'pcre': "SunOS", "tmp_path": "/tmp/lsc", "root_path": "/"},
             { 'platform': "IBM AIX", 'pcre': "AIX", "tmp_path": "/tmp/lsc", "root_path": "/"},
             { 'platform': "HP UX", 'pcre': "HP-UX", "tmp_path": "/tmp/lsc", "root_path": "/"},
             { 'platform': "Apple MacOS", 'pcre': "Darwin", "tmp_path": "/tmp/lsc", "root_path": "/"}
        ]
        if not exitcode == 0:
            logging.getLogger().warn("launcher %s: PROBE execution failed o %s: %s, %s" % (LauncherConfig().name, client, stdout, stderr))
            return "Not available"
        for identification in idData:
            if re.compile(identification["pcre"]).search(stdout) or stdout == identification["platform"]:
                logging.getLogger().debug("launcher %s: PROBE identification succeded on %s: %s" % (LauncherConfig().name, client, identification["platform"]))
                return identification["platform"]
        logging.getLogger().debug("launcher %s: PROBE identification failed on %s: %s, %s" % (LauncherConfig().name, client, stdout, stderr))
        return "Other"

    client = {
        'protocol': 'ssh',
        'host': client,
        'uuid': None,
        'timeout': timeout
    }
    mydeffered = pulse2.launcher.remote_exec.sync_remote_direct(
        None,
        client,
        "echo $OS; uname"
    )
    mydeffered.addCallback(__cb_probe_end)
    return mydeffered
