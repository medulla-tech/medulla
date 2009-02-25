#!/usr/bin/python
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
"""
    Pulse2 Launchers
"""

from pulse2.launcher.process_control import ProcessList

def getBalance(config):
    """ Attempt to give enought information to take a decision on
    how to make a deployment the better way
    """

    # our full process list
    process_list = ProcessList().listProcesses()

    # will contain som stats per group
    group_stats = {}

    # built "counts" struct
    # one item per group, containing the following keys:
    # - total number of process
    # - number of available process
    # - amount of running process
    # - amount of zombie process
    counts = {'total': 0, 'running': 0, 'zombie': 0, 'free': config["slots"]}

    # built "group" struct => to balance by group
    # one item per group, containing the following keys:
    # - total number of process in the group
    # - amount of running process in the group
    # - amount of zombie process in the group
    group_stats = {}

    # built "kind" struct => to balance by kind
    # one item per group, containing the following keys:
    # - total number of process by kind
    # - amount of running process by kind
    # - amount of zombie process by kind
    kind_stats = {}

    for process_id in process_list:
        process_state = process_list[process_id].getState()
        if not process_state['group'] in group_stats: # initialize struct
            group_stats[process_state['group']] = {'total': 0, 'running': 0, 'zombie': 0}
        if not process_state['kind'] in kind_stats: # initialize struct
            kind_stats[process_state['kind']] = {'total': 0, 'running': 0, 'zombie': 0}
        group_stats[process_state['group']]['total'] += 1
        kind_stats[process_state['kind']]['total'] += 1
        counts['total'] += 1
        counts['free'] -= 1
        if process_state['done']:
            group_stats[process_state['group']]['zombie'] += 1
            kind_stats[process_state['kind']]['zombie'] += 1
            counts['zombie'] += 1
        else:
            group_stats[process_state['group']]['running'] += 1
            kind_stats[process_state['kind']]['running'] += 1
            counts['running'] += 1

    return {'by_group': group_stats, 'global': counts, 'by_kind': kind_stats}
