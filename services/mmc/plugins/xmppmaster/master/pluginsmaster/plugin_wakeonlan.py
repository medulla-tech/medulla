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
# file pluginsmaster/plugin_wakeonlan.py


import base64
import json
import os
import sys
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
import traceback
from utils import name_random
import logging

# plugin run wake on lan on mac adress

plugin = {"VERSION": "1.0", "NAME": "wakeonlan", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    sessionid = name_random(5, "wakeonlan")
    try:
        listserverrelay = XmppMasterDatabase().listserverrelay()
        if 'macadress' in data:
            senddataplugin = {'action': 'wakeonlan',
                              'sessionid': sessionid,
                              'data': {'macaddress': data['macadress']}}
            for serverrelay in listserverrelay:
                xmppobject.send_message(mto=serverrelay[0],
                                        mbody=json.dumps(senddataplugin, encoding='latin1'),
                                        mtype='chat')
                xmppobject.xmpplog("ARS %s : WOL for macadress %s" % (serverrelay[0], data['macadress']),
                                   type='deploy',
                                   sessionname=sessionid,
                                   priority=-1,
                                   action="",
                                   who="",
                                   how="",
                                   why=xmppobject.boundjid.bare,
                                   module="Wol | Start | Creation",
                                   date=None,
                                   fromuser=xmppobject.boundjid.bare,
                                   touser="")
        elif 'UUID' in data:
            listadressmacs = Glpi().getMachineMac(data['UUID'])
            for macadress in listadressmacs:
                if macadress == '00:00:00:00:00:00':
                    continue
                senddataplugin = {'action': 'wakeonlan',
                                  'sessionid': sessionid,
                                  'data': {'macaddress': macadress}}
                for serverrelay in listserverrelay:
                    xmppobject.send_message(mto=serverrelay[0],
                                            mbody=json.dumps(senddataplugin, encoding='latin1'),
                                            mtype='chat')
                    xmppobject.xmpplog("ARS %s : WOL for macadress %s" % (serverrelay[0], macadress),
                                       type='deploy',
                                       sessionname=sessionid,
                                       priority=-1,
                                       action="",
                                       who="",
                                       how="",
                                       why=xmppobject.boundjid.bare,
                                       module="Wol | Start | Creation",
                                       date=None,
                                       fromuser=xmppobject.boundjid.bare,
                                       touser="")
        else:
            raise

    except:
        print "error plugin plugin_wakeonlan %s" % data
        traceback.print_exc(file=sys.stdout)
