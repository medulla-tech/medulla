#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.database.xmppmaster import XmppMasterDatabase

import logging

plugin = {"VERSION": "1.0", "NAME": "updatenbdeploy", "TYPE": "master"}

# =====================================================
# DEBUG   {'VERSION': '1.0', 'TYPE': 'master', 'NAME': 'updatenbdeploy'} :
# DEBUG   data plugin {
# "idcmd": 39,
# "countnb": 0,
# "grp": 14,
# "exec": true,
# "consignnb": "",
# "nbtotal": 1,
# "login": "root"
# }
# =====================================================


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    try:
        logging.getLogger().debug("End deploy command : %s" % data["idcmd"])
        XmppMasterDatabase().updatedeployinfo(data["idcmd"])
    except Exception as e:
        logging.getLogger().error("Error in plugin %s" % str(e))
        pass
