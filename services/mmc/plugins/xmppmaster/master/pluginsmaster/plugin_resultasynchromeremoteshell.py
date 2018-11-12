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
# file pluginsmaster/resultasynchromeremoteshell


import logging
import traceback
import sys
import os
import json
from utils import file_put_content


plugin = {"VERSION": "1.0", "NAME": "resultasynchromeremoteshell", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    try:
        pathresult = os.path.join("/", "tmp", sessionid)
        print pathresult
        file_put_content(pathresult, json.dumps(data, indent=4), mode="w")
        print json.dumps(data, indent=4)
    except Exception, e:
        logging.getLogger().error("Error loading plugin: %s" % str(e))
        traceback.print_exc(file=sys.stdout)
        pass
