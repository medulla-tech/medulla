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
# file pluginsmaster/plugin_resulttransfertfile.py
from utils import pluginmaster, pluginmastersessionaction
import base64
import json
import os
import zlib
from utils import md5
import hashlib

import logging

plugin = {"VERSION": "1.0", "NAME": "resulttransfertfile", "TYPE": "master"}


@pluginmastersessionaction("actualise", 20)
def action(xmppobject, action, sessionid, data, message, ret, dataobj, objsessiondata):
    logging.getLogger().debug(plugin)
    try:
        sessiondata = xmppobject.session.sessionfromsessiondata(sessionid)
        namefile = sessiondata.getdatasession()['qui']

        if dataobj['end']:
            xmppobject.event("pluginaction", {'action': 'transferfile', 'sessionid': sessionid, 'status': 'finished',
                                              'success': True,  'to': message['from'], 'form': message['to'], 'file': sessiondata.getdatasession()['qui']})
            xmppobject.session.clear(sessionid)
            return
        if ret != 0:
            xmppobject.event("pluginaction", {'action': 'transferfile', 'sessionid': sessionid, 'status': 'finished',
                                              'success': False, 'to': message['from'], 'form': message['to'], 'file': sessiondata.getdatasession()['qui']})
            xmppobject.session.clear(sessionid)
            return

        command = {
            'action': 'transferfile',
            'base64': False,
            'sessionid': sessionid,
            'data': ''
        }
        result = {}
        try:
            part = sessiondata.getdatasession()['part']
        except:
            xmppobject.event("pluginaction", {'action': 'transferfile', 'sessionid': sessionid, 'status': 'start',
                                              'to': message['from'], 'form': message['to'], 'file': sessiondata.getdatasession()['qui']})
            sessiondata.datasession['part'] = 0
            sessiondata.datasession['pointeur'] = 0
        pointeur = sessiondata.getdatasession()['pointeur']
        part = sessiondata.getdatasession()['part']
        try:
            f = open(namefile, "rb")
            f.seek(pointeur, 0)
            buffer = f.read(25000)
            sessiondata.datasession['pointeur'] = f.tell()
            xmppobject.event("pluginaction", {'action': 'transferfile', 'sessionid': sessionid, 'status': 'process', 'size': sessiondata.getdatasession()[
                             'pointeur'], 'to': message['from'], 'form': message['to'], 'file': sessiondata.getdatasession()['qui']})
            xmppobject.session.affiche()
        except IOError:
            xmppobject.event("pluginaction", {'action': 'transferfile', 'sessionid': sessionid, 'status': 'error', 'msgerror': 'IOError', 'size': sessiondata.getdatasession()[
                             'pointeur'], 'to': message['from'], 'form': message['to'], 'file': sessiondata.getdatasession()['qui']})
            raise
        finally:
            f.close()
        sessiondata.datasession['part'] = part + 1
        command['md5trame'] = hashlib.md5(buffer).hexdigest()
        if len(buffer) == 0 or buffer == "":
            command['end'] = True
            command['md5trame'] = md5(namefile)
        else:
            command['end'] = False
            aaa = zlib.compress(buffer)
            command['data'] = base64.b64encode(aaa)
        xmppobject.send_message(mto=message['from'],
                                mbody=json.dumps(command),
                                mtype='chat')
    except Exception as e:
        print "erreur %s" % str(e)
        xmppobject.event("pluginaction", {'action': 'transferfile', 'sessionid': sessionid, 'status': 'error', 'msgerror': str(
            e), 'size': sessiondata.getdatasession()['pointeur'], 'to': message['from'], 'form': message['to'], 'file': sessiondata.getdatasession()['qui']})
