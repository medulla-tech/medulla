# -*- coding: utf-8 -*-
#
# (c) 2016 siveo, http://www.siveo.net
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
# file  master/pluginsmaster/plugin_start.py

import base64
import json
import sys, os
import logging
import platform
from utils  import file_get_contents, getRandomName, call_plugin, data_struct_message
import traceback
from sleekxmpp import jid

logger = logging.getLogger()
DEBUGPULSEPLUGIN = 25

# this plugin calling to starting agent

plugin = {"VERSION" : "1.0", "NAME" : "start", "TYPE" : "master"}

def action( objectxmpp, action, sessionid, data, msg, dataerreur):
    logger.debug("=====================================================")
    logger.debug("call %s from %s"%(plugin, msg['from']))
    logger.debug("=====================================================")
    compteurcallplugin = getattr(objectxmpp, "num_call%s"%action)
    for nameplugin in objectxmpp.config.pluginliststart:
        try:
            plugindescriptorparameter = data_struct_message(nameplugin, sessionid = getRandomName(6, nameplugin))
            plugindescriptorparametererreur = data_struct_message( "resultmsginfoerror",
                                                                   data = { "msg" : "error plugin : " + plugindescriptorparameter["action"]},
                                                                   ret = 255,
                                                                   sessionid =  plugindescriptorparameter['sessionid'])
            #call plugin start
            msgt = {'from' : objectxmpp.boundjid.bare, "to" : objectxmpp.boundjid.bare, 'type' : 'chat' }
            module = "%s/plugin_%s.py"%(objectxmpp.modulepath,  plugindescriptorparameter["action"])
            logger.debug("call plugin file : "%module) 
            call_plugin( nameplugin,
                        objectxmpp,
                        plugindescriptorparameter["action"],
                        plugindescriptorparameter['sessionid'],
                        plugindescriptorparameter['data'],
                        msgt,
                        plugindescriptorparametererreur)
        except Exception:
            logger.error("\n%s"%(traceback.format_exc()))
    logger.debug("========= end plugin %s ========="%plugin['NAME'])
