#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
return enable module mmc
"""
import logging
import json
from mmc.agent import PluginManager

logger = logging.getLogger()
plugin = {"VERSION": "1.0", "NAME": "enable_mmc_module", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug(plugin)
    logger.debug("=====================================================")
    datasend = {
        "action": "resultenablemmcmodul",
        "sessionid": sessionid,
        "data": PluginManager().getEnabledPluginNames(),
    }
    xmppobject.send_message(
        mto=message["from"], mbody=json.dumps(datasend), mtype="chat"
    )
