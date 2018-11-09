#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2018 Siveo, http://www.siveo.net
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
# file pluginsmaster/plugin_kiosk.py

import logging
import json

plugin = {"VERSION": "1.0", "NAME": "kiosk", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    print json.dumps(data, indent=4)
    if data['subaction'] == 'send_message_to_jid':
        if not 'jid' in data:
            logging.getLogger().error("jid missing in kiosk send_message_to_jid sub action")
        elif not('data' in data and 'subaction' in data['data']):
            logging.getLogger().error("The message is not formated correctly")
        else:
            datasend = {'action': 'kiosk',
                        'sessionid': data['sessionid'],
                        'data': data['data']
                        }
            xmppobject.send_message(mto=data['jid'],
                                    mbody=json.dumps(datasend),
                                    mtype='chat')
