#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import base64
import json
import os
import pprint
import logging
from pulse2.database.xmppmaster import XmppMasterDatabase

plugin = {"VERSION": "1.0", "NAME": "banmachines", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.debug("=====================================================")
    logging.debug(plugin)
    logging.debug("=====================================================")

    struct = {}
    if type(data['data']) is list:
        count_params = len(data['data'])
        if count_params == 0:
            logging.debug("""Missing parameters :
- param1 : subaction
- param2 : jid_ars

* the remaining parameters must be jid_ars
- param3 : jid_ars
- param4 : jid_ars
...
- param N : jid_ars

* or param3 : 'all' to select all machines for the specified relay. In this case, param3 is the last parameter
""")
            return

        elif count_params == 1:
            logging.error("At least the jid's relay must be specified")
            return
        elif count_params == 2:
            subaction = data['data'][0]
            jid_ars = data['data'][1]
            _machines = ['all']

        else:
            subaction = data['data'][0]
            jid_ars = data['data'][1]
            _machines = data['data'][2:]
        struct = {
            'subaction' : data['data'][0],
            'jid_ars' : data['data'][1],
            'jid_machines': [],
        }
    else:
        jid_ars = data['data']['jid_ars']
        _machines = data['data']['jid_machines']
        struct = data['data']


    if struct['subaction'] == "direct_ban":
        # Get  the machines jids which are in the list but not already in the
        # table ban_machines.
        result = XmppMasterDatabase().ban_machines(jid_ars, _machines)
    if struct['subaction'] == "direct_unban":
        # Get  the machines jids which are in the list but not already in the
        # table ban_machines.
        result = XmppMasterDatabase().unban_machines(jid_ars, _machines)
    struct['jid_machines'] = result['jid_machines']
    datasend = {'action': 'banmachines',
                'sessionid': data['sessionid'],
                #'sender': xmppobject.boundjid.bare,
                'data': struct
                }

    xmppobject.send_message(mto=data['data']['jid_ars'],
                            mbody=json.dumps(datasend),
                            mtype='chat')
