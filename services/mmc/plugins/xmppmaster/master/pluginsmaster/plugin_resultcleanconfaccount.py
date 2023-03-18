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
# file /pluginsmaster/plugin_resultcleanconfaccount.py

import logging
import traceback
import sys
import json
from mmc.plugins.xmppmaster.master.lib.utils import simplecommandstr, file_get_content, file_put_content

logger = logging.getLogger()

plugin = {"VERSION": "1.03", "NAME": "resultcleanconfaccount", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, msg, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    try:
        recipient = str(msg['from'].user)
        if data['useraccount'].startswith("conf"):
            logger.debug('Clear MUC conf account')
            cmd = "ejabberdctl unregister %s pulse" % recipient
            unregister_command = simplecommandstr(cmd)
            logger.debug(unregister_command['result'])
            logger.info("The ejabberd account %s has been removed for the machine: %s" % (recipient, str(msg['from'].resource)))
    except Exception as e:
        pass
