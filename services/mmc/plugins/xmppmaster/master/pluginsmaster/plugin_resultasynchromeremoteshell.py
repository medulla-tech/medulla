#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import traceback
import sys
import os
import json
from mmc.plugins.xmppmaster.master.lib.utils import file_put_content


plugin = {"VERSION": "1.0", "NAME": "resultasynchromeremoteshell", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    try:
        pathresult = os.path.join("/", "tmp", sessionid)
        print(pathresult)
        file_put_content(pathresult, json.dumps(data, indent=4), mode="w")
        print(json.dumps(data, indent=4))
    except Exception as e:
        logging.getLogger().error("Error loading plugin: %s" % str(e))
        traceback.print_exc(file=sys.stdout)
        pass
