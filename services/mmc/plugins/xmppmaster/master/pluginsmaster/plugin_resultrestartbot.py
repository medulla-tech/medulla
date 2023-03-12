#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

plugin = {"VERSION": "1.0", "NAME": "resultrestartbot", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    try:
        logging.getLogger().debug("restart bot machine %s" % message["from"])
        pass
    except Exception as e:
        logging.getLogger().error("Error in plugin restart bot%s" % str(e))
        pass
