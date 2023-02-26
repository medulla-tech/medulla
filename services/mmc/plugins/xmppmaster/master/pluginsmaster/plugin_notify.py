# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

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
from mmc.plugins.xmppmaster.master.lib.utils import name_random, file_put_contents, file_get_contents

from mmc.plugins.kiosk import handlerkioskpresence

plugin = {"VERSION": "1.0", "NAME": "notify", "TYPE": "master"}

def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("#################################################")
    logging.getLogger().debug(json.dumps(data, indent=4))
    logging.getLogger().debug("#################################################")

    if 'msg' in data:
        if 'type' in data and data['type'] == "error":
            logging.getLogger().error("%s"%data['msg'])
