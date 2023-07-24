# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

plugin = {"VERSION": "1.0", "NAME": "resultapplicationdeploymentjson", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("%s from %s" % (data["msg"], message["from"]))
    pass
