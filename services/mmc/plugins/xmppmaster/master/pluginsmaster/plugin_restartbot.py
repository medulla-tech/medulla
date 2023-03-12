#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This plugin can be called from quick action
"""
import json
import logging

logger = logging.getLogger()

plugin = {"VERSION": "1.1", "NAME": "restartbot", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("###################################################")
    logger.debug("call %s from %s" % (plugin, message["from"]))
    logger.debug("###################################################")
    command = {
        "action": "restartbot",
        "base64": False,
        "sessionid": sessionid,
        "data": "",
    }
    xmppobject.send_message(
        mto=data["data"][0], mbody=json.dumps(command), mtype="chat"
    )
