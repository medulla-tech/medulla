#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

logger = logging.getLogger()

DEBUGPULSEPLUGIN = 25
plugin = {"VERSION": "1.21", "NAME": "resultmsginfoerror", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    if "msg" in data:
        if ret >= 50 and ret <= 80:
            logging.getLogger().warning(
                "msg [%s] : %s" % (message["from"], data["msg"])
            )
        elif ret == 0:
            logging.getLogger().info("msg [%s] : %s" % (message["from"], data["msg"]))
        else:
            logging.getLogger().error("msg [%s] : %s" % (message["from"], data["msg"]))
