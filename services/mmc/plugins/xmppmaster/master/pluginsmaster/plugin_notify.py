# -*- coding: utf-8 -*-
#
# (c) 2016-2019 siveo, http://www.siveo.net
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

# file pluginsmaster/plugin_notify.py

import datetime
import json
import traceback
import sys
import os
import re
from pulse2.database.xmppmaster import XmppMasterDatabase
from pulse2.database.msc import MscDatabase
from managepackage import managepackage
import logging
from utils import name_random, file_put_contents, file_get_contents

from mmc.plugins.kiosk import handlerkioskpresence

plugin = {"VERSION": "1.0", "NAME": "notify", "TYPE": "master"}

def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("#################################################")
    logging.getLogger().debug(json.dumps(data, indent=4))
    logging.getLogger().debug("#################################################")

    if 'msg' in data:
        if 'type' in data and data['type'] == "error":
            logging.getLogger().error("%s"%data['msg'])
