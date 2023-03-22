#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
this plugin can be called from quick action
"""

import json
import logging

from pulse2.database.xmppmaster import XmppMasterDatabase

logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "reversessh", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug(plugin)
    logger.info("%s master plugin called" % plugin['NAME'])
    try:
        logger.debug("data[0]: %s" % json.dumps(data[0], indent=4))
    except KeyError:
        logger.debug("data[0] not found while calling %s. "
                     "The plugin is probably called from a quick action."
                     % (plugin['NAME']))
        pass

    try:
        jidmachine = data[0]['jidmachine']
        machineinfo = XmppMasterDatabase().getMachinefromjid(jidmachine)
        tunnelserverport = data[0]['tunnelserverport']
        tunnelclientport = data[0]['tunnelclientport']
        reversetype = data[0]['reversetype']
    except KeyError:
        logger.debug("data: %s" % json.dumps(data, indent=4))
        jidmachine = data['data'][0]
        machineinfo = XmppMasterDatabase().getMachinefromjid(jidmachine)
        params = data['data'][2]
        if len(params) == 3:
            tunnelserverport = params[0]
            tunnelclientport = params[1]
            reversetype = params[2]
        elif len(params) == 2:
            tunnelserverport = params[0]
            tunnelclientport = params[1]
            reversetype = 'L'
        else:
            logger.error("Parameters missing. Defined parameters: %s" % params)
            logger.error("If called from a quick action, the following "
                         "parameters must be defined: \n"
                         "mandatory: @_@tunnelserverport@_@tunnelclientport \n"
                         "optional: @_@reversetype (L if not defined)")

    logger.info("Starting reversessh connection from machine %s.\n"
                " Tunnel server port: %s\n"
                " Tunnel client port: %s\n"
                " Reverse type: %s" % (jidmachine, tunnelserverport,
                                       tunnelclientport, reversetype))

    datasend = {
        'session_id': sessionid,
        'action': 'reverse_ssh_on',
        'data': {'request': 'askinfo',
                 'port': tunnelserverport,
                 'remoteport': tunnelclientport,
                 'reversetype': reversetype,
                 'jidmachine': jidmachine,
                 # item host is uuid glpi machine
                 'host': machineinfo['uuid_inventorymachine'],
                 'options': 'createreversessh',
                 'persistence': 'SIMPLETUNNEL'
                 },
        'ret': 0,
        'base64': False
    }

    # send message to relayserver
    xmppobject.send_message(mto=machineinfo['groupdeploy'],
                            mbody=json.dumps(datasend),
                            mtype='chat')
