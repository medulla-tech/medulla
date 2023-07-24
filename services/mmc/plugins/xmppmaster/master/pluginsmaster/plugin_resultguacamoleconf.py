#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.database.xmppmaster import XmppMasterDatabase
import logging

plugin = {"VERSION": "1.11", "NAME": "resultguacamoleconf", "TYPE": "master"}
logger = logging.getLogger()


def action(xmppobject, action, sessionid, data, message, ret, objsessiondata):
    logger.debug("#################################################")
    logger.debug(plugin)
    logger.debug("#################################################")
    try:
        XmppMasterDatabase().addlistguacamoleidformachineid(
            data["machine_id"], data["connection"]
        )
    except Exception as e:
        logger.error("plugin resultguacamoleconf Error: %s" % str(e))
        # logger.error("\n%s"%(traceback.format_exc()))
        pass
