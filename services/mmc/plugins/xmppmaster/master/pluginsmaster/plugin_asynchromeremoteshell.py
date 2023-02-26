#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import traceback
import sys
import json

plugin = {"VERSION": "1.0", "NAME": "asynchromeremoteshell", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    try:
        print data['data'][1][0]
        print json.dumps(data, indent=4)
        machine = data['data'][0]
        command = data['data'][1][0]['command']
        uidunique = data['data'][1][0]['uidunique']
        datasend = {
            'sessionid': uidunique,
            'action': data['action'],
            'data': {'machine': machine,
                     'command': command
                     }
        }
        print datasend['sessionid']
        # call plugin asynchromeremoteshell to machine or relay
        xmppobject.send_message(mto=data['data'][0],
                                mbody=json.dumps(datasend),
                                mtype='chat')

    except Exception, e:
        logging.getLogger().error("Error loading plugin: %s" % str(e))
        traceback.print_exc(file=sys.stdout)
        pass
