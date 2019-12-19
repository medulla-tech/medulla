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
# file pluginsmaster/plugin_resultconfsyncthing.py

import logging
import traceback
import sys
import json
from utils import simplecommandstr, file_get_content, file_put_content

logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "resultconfsyncthing", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, msg, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug("call from %s %s"%(str(msg['from']), plugin))
    logger.debug("=====================================================")
    print data
    try:
        if 'syncthingconf' in data:
            logger.info("configuration Syncthing from %s: %s"%(str(msg['from']),
                                                                   data['syncthingconf']))
        elif 'errorsyncthingconf'  in data:
            configsyncthing = json.loads(data['errorsyncthingconf'])
            logger.error("on syncthing agent (setup) %s"%str(msg['from']) )
            logger.error(json.dumps(configsyncthing, indent=4))
    except Exception as e:
        pass

