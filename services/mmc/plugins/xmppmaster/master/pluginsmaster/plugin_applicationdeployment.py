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
# file pluginsmaster/plugin_applicationdeployment.py

import base64
import json
import os
import utils
import pprint
import logging


plugin = {"VERSION": "1.0", "NAME": "applicationdeployment", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    try:
        if 'Dtypequery' in data:
            if data['Dtypequery'] == 'TED':
                print "Delete session %s" % sessionid
                # Set deployment to done in database
                xmppobject.session.clear(sessionid)

                if __debug__:
                    logging.getLogger().debug("_______________________RESULT DEPLOYMENT________________________")
                    logging.getLogger().debug(json.dumps(data['descriptor']))
                    logging.getLogger().debug("________________________________________________________________")
            elif data['Dtypequery'] == 'TE':
                # clear session
                xmppobject.session.clear(sessionid)
                # Set deployment to error in database
            else:
                # Update session with data
                xmppobject.session.sessionsetdata(sessionid, data)
        pass
    except Exception as e:
        logging.getLogger().error("Error in plugin %s : %s" % (plugin['NAME'], str(e)))
