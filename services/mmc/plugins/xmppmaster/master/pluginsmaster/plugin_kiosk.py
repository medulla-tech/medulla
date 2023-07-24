#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import json

plugin = {"VERSION": "1.0", "NAME": "kiosk", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    print(json.dumps(data, indent=4))
    if data["subaction"] == "send_message_to_jid":
        if not "jid" in data:
            logging.getLogger().error(
                "jid missing in kiosk send_message_to_jid sub action"
            )
        elif not ("data" in data and "subaction" in data["data"]):
            logging.getLogger().error("The message is not formated correctly")
        else:
            datasend = {
                "action": "kiosk",
                "sessionid": data["sessionid"],
                "data": data["data"],
            }
            xmppobject.send_message(
                mto=data["jid"], mbody=json.dumps(datasend), mtype="chat"
            )
