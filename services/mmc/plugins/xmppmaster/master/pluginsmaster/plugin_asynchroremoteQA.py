#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import json

plugin = {"VERSION": "1.1", "NAME": "asynchroremoteQA", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, dataerreur):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    print(json.dumps(data, indent=4))
    datasend = {"action": action, "sessionid": sessionid, "data": data, "base64": False}

    # call plugin asynchromeremoteshell to machine or relay
    xmppobject.send_message(
        mto=data["data"]["jid"], mbody=json.dumps(datasend), mtype="chat"
    )
