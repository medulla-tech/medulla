# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
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
