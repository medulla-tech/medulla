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

from pulse2.scheduler.config import SchedulerConfig

def getAnnounceCheck(announce):
    if not announce:
        return ''
    if not announce in SchedulerConfig().announce_check:
        return ''
    return SchedulerConfig().announce_check[announce]

def getCheck(check, target):
    """
        target formating: {
            'uuid':
            'shortname':
            'ip':
            'macs':
        }
        /!\ IP must be a single
    """

    ret = {}
    if not check:
        return ret
    for key in check:
        if check[key] == 'ipaddr':
            if 'chosen_ip' in target and target['chosen_ip']:
                ret[key] = target['chosen_ip']
            elif 'ips' in target and target['ips']:
                ret[key] = target['ips'][0]
        if check[key] == 'name':
            ret[key] = target['shortname']
        if check[key] == 'uuid':
            ret[key] = target['uuid']
        if check[key] == 'macaddr':
            ret[key] = target['macs'][0]
    return ret
