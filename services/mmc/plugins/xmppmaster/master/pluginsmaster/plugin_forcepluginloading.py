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
# file pluginsmaster/plugin_forcepluginloading.py
# this plugin is called from a quick action
import json
import logging

logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "forcepluginloading", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("###################################################")
    logger.debug("# call %s from %s" % (plugin, message['from']))
    logger.debug("# Data: %s" % data)
    logger.debug("# JID machine: %s" % data['data'][0])
    logger.debug("# Params: %s" % data['data'][2])
    logger.debug("###################################################")

    # Called from a QA: data['data'][0] contains jid of machine and
    #   data['data'][2] contains the list of parameters passed
    # eg: QA: plugin_forcepluginloading@_@updatefusion
    #   data['data'][2][0] will contain updatefusion

    jidmachine = data['data'][0]
    try:
        # plugin to be loaded passed as first parameter
        loadplugin = data['data'][2][0]
    except (KeyError, IndexError) as e:
        logger.error("Error getting plugin to be loaded on machine %s: %s"
                     % (jidmachine, str(e)))
        return
    logger.info("Forcing loading of plugin %s on machine %s"
                % (loadplugin, jidmachine))
    command = {'action': loadplugin,
               'base64': False,
               'sessionid': sessionid,
               'data': ''}
    xmppobject.send_message(mto=jidmachine,
                            mbody=json.dumps(command),
                            mtype='chat')
