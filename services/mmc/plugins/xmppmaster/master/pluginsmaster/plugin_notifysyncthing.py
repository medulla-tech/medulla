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
# file pluginsmaster/plugin_notifysyncthing.py

import base64
import json
import os
import mmc.plugins.xmppmaster.master.lib.utils
import pprint
import logging
from pulse2.database.pkgs import PkgsDatabase
logger = logging.getLogger()

plugin = { "VERSION" : "1.2", "NAME" : "notifysyncthing", "TYPE" : "master" }

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug(plugin)
    logger.debug("=====================================================")
    print json.dumps(data, indent = 4)
    if 'suppdir' in data or 'adddir' in data:
        logger.debug("removing package %s %s %s"%( data['packageid'], 'create', str(message['from'])))
        PkgsDatabase().pkgs_unregister_synchro_package( data['packageid'],
                                                      None,
                                                      str(message['from']))
    elif 'MotifyFile' in data:
        logger.debug("removing package %s %s %s"%( data['packageid'], 'chang', str(message['from'])))
        PkgsDatabase().pkgs_unregister_synchro_package( data['packageid'],
                                                      'chang',
                                                      str(message['from']))
