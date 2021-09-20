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
# file : /plugin_resultmsginfoerror.py

import logging
logger = logging.getLogger()

DEBUGPULSEPLUGIN = 25
plugin = {"VERSION": "1.21", "NAME": "resultmsginfoerror", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    if 'msg' in data:
        if ret >= 50 and ret <= 80:
            logging.getLogger().warning("msg [%s] : %s" %(message['from'],
                                                          data['msg']))
        elif ret == 0:
            logging.getLogger().info("msg [%s] : %s" %(message['from'],
                                                          data['msg']))
        else:
            logging.getLogger().error("msg [%s] : %s" %(message['from'],
                                                          data['msg']))
