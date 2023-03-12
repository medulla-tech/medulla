#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This plugin is called from a quick action
"""
import json
import logging

logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "forcepluginloading", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("###################################################")
    logger.debug("# call %s from %s" % (plugin, message["from"]))
    logger.debug("# Data: %s" % data)
    logger.debug("# JID machine: %s" % data["data"][0])
    logger.debug("# Params: %s" % data["data"][2])
    logger.debug("###################################################")

    # Called from a QA: data['data'][0] contains jid of machine and
    #   data['data'][2] contains the list of parameters passed
    # eg: QA: plugin_forcepluginloading@_@updatefusion
    #   data['data'][2][0] will contain updatefusion

    jidmachine = data["data"][0]
    try:
        # plugin to be loaded passed as first parameter
        loadplugin = data["data"][2][0]
    except (KeyError, IndexError) as e:
        logger.error(
            "Error getting plugin to be loaded on machine %s: %s" % (jidmachine, str(e))
        )
        return
    logger.info("Forcing loading of plugin %s on machine %s" % (loadplugin, jidmachine))
    command = {
        "action": loadplugin,
        "base64": False,
        "sessionid": sessionid,
        "data": "",
    }
    xmppobject.send_message(mto=jidmachine, mbody=json.dumps(command), mtype="chat")
