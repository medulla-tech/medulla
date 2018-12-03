# -*- coding: utf-8 -*-
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

# file pluginsmaster/plugin_machineexecutionscheduler.py
"""
this plugin check status of deploy
if deploy is pause, run, abandonned

"""
import base64
import json
import os
import sys
import utils
import pprint
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
import logging

plugin = {"VERSION": "1.0", "NAME": "machineexecutionscheduler", "TYPE": "master"}

"""
#eg : data plugin received
#{
    ...,
    ...,
    #"advanced": {
        #"idcmd": 1,
        #"countnb": 0,
        #"grp": 14,
        #"exec": false,
        #"exectime": "2017-10-18 07:25:11",
        #"nbtotal": 1,
        #"scheduling": true,
        #"login": "root"
    #},
    ...,
    ...
#}
"""
DEBUGPULSEPLUGIN = 25


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)

    advanced = data['advanced']
    try:
        result = XmppMasterDatabase().checkstatusdeploy(advanced['idcmd'])
        advanced['actionscheduler'] = result  # abandonmentdeploy, run or pause
        datasend = {
            'action': data['fromaction'],
            'sessionid': sessionid,
            'data': advanced,
            'ret': 0,
            'base64': False
        }
        xmppobject.send_message(mto=message['from'],
                                mbody=json.dumps(datasend),
                                mtype='chat')
    except Exception as e:
        print "Error in plugin %s" % str(e)
        traceback.print_exc(file=sys.stdout)
        advanced['actionscheduler'] = "error"  # abandonmentdeploy, run or pause
        datasend = {
            'action': data['fromaction'],
            'sessionid': sessionid,
            'data': advanced,
            'ret': 0,
            'base64': False
        }
        xmppobject.send_message(mto=message['from'],
                                mbody=json.dumps(datasend),
                                mtype='chat')
