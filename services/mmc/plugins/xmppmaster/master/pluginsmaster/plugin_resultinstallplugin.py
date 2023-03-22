#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

plugin = {"VERSION": "1.0", "NAME": "resultinstallplugin", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    try:
        logging.getLogger().debug(
            "plugin resultinstallplugin from %s  ret [%s]" % (message['from'], ret))
        pass
    except Exception as e:
        logging.getLogger().debug("Error in plugin resultinstallplugin %s" % str(e))
        pass
