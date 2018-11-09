#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2017 siveo, http://www.siveo.net
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
# file pluginsmaster/plugin_guacamole.py

import json
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
from utils import name_random
import logging

plugin = {"VERSION": "1.0", "NAME": "plugin_guacamole", "TYPE": "master"}
# plugin run guacamole


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    try:
        relayserver = XmppMasterDatabase().getRelayServerForMachineUuid(data['uuid'])
        jidmachine = XmppMasterDatabase().getjidMachinefromuuid(data['uuid'])
        senddataplugin = {'action': 'guacamole',
                          'sessionid': name_random(5, "guacamole"),
                          'data': {'jidmachine': jidmachine, 'cux_id': data['cux_id'], 'cux_type': data['cux_type'], 'uuid': data['uuid']}}
        xmppobject.send_message(mto=relayserver['jid'],
                                mbody=json.dumps(senddataplugin, encoding='latin1'),
                                mtype='chat')

    except:
        logging.getLogger().error("error plugin plugin_guacamole %s" % data)
        traceback.print_exc(file=sys.stdout)
        pass
