#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2018 siveo, http://www.siveo.net
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
# file pluginsmaster /pluginsmaster/plugin_resultupdateagent.py

import base64
import json
import os
import logging
import zlib
from time import sleep
from utils import name_random, file_put_contents, file_get_contents


logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "resultupdateagent", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("#################################################")
    logger.debug(plugin)
    logger.debug(json.dumps(data, indent=4))
    logger.debug("#################################################")
    if "subaction" in data:
        if data['subaction'] == "update_me":
            # load version agent agentversion
            version = file_get_contents(os.path.join(
                xmppobject.config.diragentbase, "agentversion"))
            if 'descriptoragent' in data:
                if 'program_agent' in data['descriptoragent'] and len(data['descriptoragent']['program_agent']) != 0:
                    logger.debug("Update program script in remote agent [%s]" % message['from'])
                    for script_program_file in data['descriptoragent']['program_agent']:
                        logger.debug("\t- Update program script [%s]" % (script_program_file))
                        sleep(2)
                        load_and_send_remote_agent_file(
                            xmppobject, message['from'], script_program_file, "program_agent", version)
                if 'lib_agent' in data['descriptoragent'] and len(data['descriptoragent']['lib_agent']) != 0:
                    logger.debug("Update lib script in remote agent [%s]" % message['from'])
                    for script_lib_file in data['descriptoragent']['lib_agent']:
                        logger.debug("\t- Update lib script [%s]" % (script_lib_file))
                        sleep(2)
                        load_and_send_remote_agent_file(
                            xmppobject, message['from'], script_lib_file, "lib_agent", version)
                if 'script_agent' in data['descriptoragent'] and len(data['descriptoragent']['script_agent']) != 0:
                    logger.debug("Update script in remote agent [%s]" % message['from'])
                    for script_script_file in data['descriptoragent']['script_agent']:
                        logger.debug("\t- Update script [%s]" % (script_script_file))
                        sleep(2)
                        load_and_send_remote_agent_file(
                            xmppobject, message['from'], script_script_file, "script_agent", version)


def load_and_send_remote_agent_file(xmppobject, jid, filename, type, version):
    msg_script_file_to_remote_agent = {"action": "updateagent",
                                       "sessionid": name_random(3, "update_script_agent"),
                                       "data": {"version": version}}
    if type == "program_agent":
        namescriptfile = os.path.join(xmppobject.config.diragentbase, filename)
    elif type == "lib_agent":
        namescriptfile = os.path.join(xmppobject.config.diragentbase, "lib", filename)
    elif type == "script_agent":
        namescriptfile = os.path.join(xmppobject.config.diragentbase, "script", filename)
    else:
        logger.error("script type incorect for transfert script to update remote agent")
        return
    if os.path.isfile(namescriptfile):
        logger.debug("File script found %s" % namescriptfile)
    else:
        logger.error("File script missing %s" % namescriptfile)
        return
    try:
        # lit contenue binaire du fichier a installer
        filescript = open(namescriptfile, "rb")
        datacontentbinary = filescript.read()
        # compress puis encode en base64
        content = base64.b64encode(zlib.compress(datacontentbinary, 9))
        filescript.close()
    except Exception as e:
        logger.error(str(e))
        traceback.print_exc(file=sys.stdout)
        return

    msg_script_file_to_remote_agent['data'] = {}
    msg_script_file_to_remote_agent['data']['subaction'] = 'install_%s' % type
    msg_script_file_to_remote_agent['data']['content'] = content
    msg_script_file_to_remote_agent['data']['namescript'] = filename
    msg_script_file_to_remote_agent['base64'] = False  # only seul content of data is base 64
    try:
        xmppobject.send_message(mto=jid,
                                mbody=json.dumps(msg_script_file_to_remote_agent),
                                mtype='chat')
    except:
        traceback.print_exc(file=sys.stdout)
