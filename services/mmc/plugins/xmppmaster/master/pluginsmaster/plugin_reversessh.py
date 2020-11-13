#!/usr/bin/python3
# -*- coding: utf-8; -*-
#
# (c) 2016-2020 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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
#
# file pluginsmaster/plugin_reversessh.py
# this plugin can be called from quick action
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
