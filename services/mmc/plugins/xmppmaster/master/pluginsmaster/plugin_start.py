# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from mmc.plugins.xmppmaster.master.lib.utils import (
    getRandomName,
    call_plugin,
    data_struct_message,
)
import traceback

logger = logging.getLogger()
DEBUGPULSEPLUGIN = 25

# this plugin calling to starting agent

plugin = {"VERSION": "1.0", "NAME": "start", "TYPE": "master"}


def action(objectxmpp, action, sessionid, data, msg, dataerreur):
    logger.debug("=====================================================")
    logger.debug("call %s from %s" % (plugin, msg["from"]))
    logger.debug("=====================================================")
    compteurcallplugin = getattr(objectxmpp, "num_call%s" % action)
    for nameplugin in objectxmpp.config.pluginliststart:
        try:
            plugindescriptorparameter = data_struct_message(
                nameplugin, sessionid=getRandomName(6, nameplugin)
            )
            plugindescriptorparametererreur = data_struct_message(
                "resultmsginfoerror",
                data={"msg": "error plugin : " + plugindescriptorparameter["action"]},
                ret=255,
                sessionid=plugindescriptorparameter["sessionid"],
            )
            # call plugin start
            msgt = {
                "from": objectxmpp.boundjid.bare,
                "to": objectxmpp.boundjid.bare,
                "type": "chat",
            }
            module = "%s/plugin_%s.py" % (
                objectxmpp.modulepath,
                plugindescriptorparameter["action"],
            )
            logger.debug("call plugin file : " + module)
            call_plugin(
                nameplugin,
                objectxmpp,
                plugindescriptorparameter["action"],
                plugindescriptorparameter["sessionid"],
                plugindescriptorparameter["data"],
                msgt,
                plugindescriptorparametererreur,
            )
        except Exception:
            logger.error("\n%s" % (traceback.format_exc()))
    logger.debug("========= end plugin %s =========" % plugin["NAME"])
