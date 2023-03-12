#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import logging

plugin = {"VERSION": "1.0", "NAME": "resultwakeonlan", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    try:
        logging.getLogger().debug("%s", data)
        pass
    except Exception as e:
        logging.getLogger().error("Error in plugin %s : %s" % (action, str(e)))
        pass
