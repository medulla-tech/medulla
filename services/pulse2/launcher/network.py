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
import tempfile
import shutil
import xmlrpclib
import os
import os.path
from twisted.internet import defer

# Other stuff
from pulse2.launcher.config import LauncherConfig
import pulse2.launcher.process_control
SEPARATOR = u'·'

def wolClient(mac_addrs, target_bcast = None):
    """ Send a BCast WOL packet to mac_addrs """
    def __cb_wol_end(shprocess):
        if not shprocess.exit_code == 0:
            logging.getLogger().warn("launcher %s: WOL failed: %s, %s" % (LauncherConfig().name, shprocess.stdout, shprocess.stderr))
            return (False, "mac addresses: %s, target broadcasts: %s" % (mac_addrs, target_bcast), "")
        logging.getLogger().debug("launcher %s: WOL succeeded" % (LauncherConfig().name))
        return (True, "mac addresses: %s, target broadcasts: %s" % (mac_addrs, target_bcast), "")

    def cbReturn(result):
        ret = (True, "mac addresses: %s, target broadcasts: %s" % (mac_addrs, target_bcast), "")
        for res in result:
            if not res[1]:
                return (False, "mac addresses: %s, target broadcasts: %s" % (mac_addrs, target_bcast), "")
        return ret

    command_list = [
        LauncherConfig().wol_path,
        '--port=%s' % LauncherConfig().wol_port,
    ]

    dl = []
    sorted = {}
    for i in range(len(mac_addrs)):
        if mac_addrs[i]:
            bcast = LauncherConfig().wol_bcast
            if target_bcast[i]:
                bcast = target_bcast[i]
            if not sorted.has_key(bcast):
                sorted[bcast] = []
            sorted[bcast].append(mac_addrs[i])
    for bcat in sorted:
        mac_addresses = sorted[bcat]
        cmd = command_list + ['--ipaddr=%s' % bcat] + mac_addresses
        logging.getLogger().debug("launcher %s: WOL: %s" % (str(cmd), LauncherConfig().name))
        dl.append(pulse2.launcher.process_control.commandRunner(cmd, __cb_wol_end))

    if len(dl) == 1:
        return dl[0]
    dl = defer.DeferredList(dl)
    dl.addCallback(cbReturn)
    return dl

def icmpClient(client, timeout):
    """ Send a Ping to our client """
    def __cb_icmp_end(shprocess, client=client):
        if not shprocess.exit_code == 0:
            logging.getLogger().debug("launcher %s: ICMP failed on %s: %s, %s" % (LauncherConfig().name, client, shprocess.stdout, shprocess.stderr))
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
        __cb_icmp_end,
    )

def probeClient(client, timeout):
    """
    Check ssh connectivity with a computer
    """
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
            logging.getLogger().debug("launcher %s: PROBE execution failed on %s: %s, %s" % (LauncherConfig().name, client, stdout, stderr))
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
        'uuid': None
    }
    mydeffered = pulse2.launcher.remote_exec.sync_remote_direct(
        None,
        client,
        "echo $OS; uname",
        None,
        timeout
    )
    if not mydeffered:
        return "Not available"
    mydeffered.addCallback(__cb_probe_end)
    return mydeffered

def downloadFile(client, path, bwlimit, timeout):
    """
    Get the first file found in the given path from client.
    """

    def __cb_dl_end(result, path):
        code, stdout, stderr = result
        ret = False
        if code == 0 or code == 1: # code may be 1 if one of our downloaded folders do not exists
            # Look for the first available file contained in the directory
            for root, dirs, files in os.walk(path):
                if files:
                    ret = (files[0], os.path.join(root, files[0]))
                    break
            # If there was one, build a binary string from its content
            if ret:
                rname, fname = ret
                f = file(fname)
                data = f.read()
                f.close()
                ret = (rname, xmlrpclib.Binary(data))
        shutil.rmtree(path)
        return ret

    def __err_dl_end(failure, path):
        logging.getLogger().error("launcher %s: %s" % (LauncherConfig().name, failure))
        shutil.rmtree(path)
        return False

    targetpath = tempfile.mkdtemp(".p2")
    myDeferred = pulse2.launcher.remote_exec.from_remote_to_launcher(None, client, path, targetpath, bwlimit, timeout)
    myDeferred.addCallback(__cb_dl_end, targetpath)
    myDeferred.addErrback(__err_dl_end, targetpath)
    return myDeferred
