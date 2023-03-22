#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

plugin = {"VERSION": "1.0", "NAME": "evtfrommachine", "TYPE": "master"}

"""
This plugin is calling from an AM (windows), if AM is stopped by a user.
Ctrl + c for example.
"""
def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    if data['event'] == "SHUTDOWN_EVENT":
        msg_changed_status = {
            "from": data['machine'],
            "type": 'unavailable'
        }
        xmppobject.changed_status(msg_changed_status)
