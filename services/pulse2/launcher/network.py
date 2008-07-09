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

def icmpClient(client):
    """ Send a Ping to our client """
    def __cb_wol_end(shprocess):
        if not shprocess.exit_code == 0:
            logging.getLogger().warn("launcher %s: ICMP failed: %s, %s" % (LauncherConfig().name, shprocess.stdout, shprocess.stderr))
            return False
        logging.getLogger().debug("launcher %s: ICMP succeeded" % (LauncherConfig().name))
        return True

    command_list = [
        LauncherConfig().ping_path,
        client
    ]

    return pulse2.launcher.process_control.commandRunner(
        command_list,
        __cb_wol_end
    )
