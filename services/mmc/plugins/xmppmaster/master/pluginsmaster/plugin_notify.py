# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging

plugin = {"VERSION": "1.0", "NAME": "notify", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("#################################################")
    logging.getLogger().debug(json.dumps(data, indent=4))
    logging.getLogger().debug("#################################################")

    if "msg" in data:
        if "type" in data and data["type"] == "error":
            logging.getLogger().error("%s" % data["msg"])
