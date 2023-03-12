#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import logging

plugin = {"VERSION": "1.4", "NAME": "force_setup_agent", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    print("_________________________")
    logging.getLogger().debug(plugin)
    # print json.dumps(data, indent = 4)
    print(data["data"][0])
    print("_________________________")

    command = {
        "action": "force_setup_agent",
        "base64": False,
        "sessionid": sessionid,
        "data": "",
    }
    xmppobject.send_message(
        mto=data["data"][0], mbody=json.dumps(command), mtype="chat"
    )
