#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import json
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
import traceback
from mmc.plugins.xmppmaster.master.lib.utils import name_random
import logging
import os
import configparser
from wakeonlan import wol

logger = logging.getLogger()

plugin = {"VERSION": "1.2", "NAME": "wakeonlan", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug("call %s from %s" % (plugin, message["from"]))
    logger.debug("=====================================================")
    sessionid = name_random(5, "wakeonlan")

    try:
        compteurcallplugin = getattr(xmppobject, "num_call%s" % action)
        logger.debug("compteurcallplugin %s" % compteurcallplugin)
        if compteurcallplugin == 0:
            read_conf_wol(xmppobject)
    except:
        logger.error("plugin %s\n%s" % (plugin["NAME"], traceback.format_exc()))

    try:
        if xmppobject.wakeonlanremotelan:
            # remote msg to ars for WOL
            senddataplugin = {
                "action": "wakeonlan",
                "sessionid": sessionid,
                "data": {"macaddress": ""},
            }
            serverrelaylist = (
                XmppMasterDatabase().random_list_ars_relay_one_only_in_cluster()
            )
            if "macadress" in data:
                senddataplugin["data"]["macaddress"] = data["macadress"]
                for serverrelay in serverrelaylist:
                    xmppobject.send_message(
                        mto=serverrelay["jid"],
                        mbody=json.dumps(senddataplugin, encoding="latin1"),
                        mtype="chat",
                    )
                    msglog = (
                        "A WOL request has been sent from the ARS %s "
                        "to the mac address %s"
                        % (serverrelay["jid"], data["macadress"])
                    )
                    historymessage(xmppobject, sessionid, msglog)
                    logger.debug(msglog)

            elif "UUID" in data:
                listadressmacs = Glpi().getMachineMac(data["UUID"])
                listadressmacs = [x.strip() for x in listadressmacs if x != ""]
                for macadress in listadressmacs:
                    if macadress == "00:00:00:00:00:00":
                        continue
                    senddataplugin["data"]["macaddress"] = macadress
                    for serverrelay in serverrelaylist:
                        xmppobject.send_message(
                            mto=serverrelay["jid"],
                            mbody=json.dumps(senddataplugin, encoding="latin1"),
                            mtype="chat",
                        )
                        msglog = (
                            "A WOL request has been sent from the ARS %s"
                            "to the mac address %s "
                            "for the computer with the uuid %s"
                            % (serverrelay["jid"], macadress, data["UUID"])
                        )
                        historymessage(xmppobject, sessionid, msglog)
                        logger.debug(msglog)
            else:
                raise
        else:
            if "macadress" in data:
                wol.send_magic_packet(data["macadress"], port=xmppobject.wakeonlanport)
                msglog = (
                    "A local lan WOL request have been sent to the"
                    " mac address %s and port %s"
                    % (data["macadress"], xmppobject.wakeonlanport)
                )
                historymessage(xmppobject, sessionid, msglog)
                logger.debug(msglog)

            elif "UUID" in data:
                listadressmacs = Glpi().getMachineMac(data["UUID"])
                listadressmacs = [x.strip() for x in listadressmacs if x != ""]
                for macadress in listadressmacs:
                    if macadress == "00:00:00:00:00:00":
                        continue
                    wol.send_magic_packet(macadress, port=xmppobject.wakeonlanport)
                    msglog = (
                        "A local lan WOL request have been sent to the"
                        " mac address %s and port %s"
                        % (macadress, xmppobject.wakeonlanport)
                    )

                    historymessage(xmppobject, sessionid, msglog)
                    logger.debug(msglog)
    except Exception as error_exception:
        msglog = "An error occurent when loading the plugin plugin_wakeonlan %s" % data
        tracebackerror = "\n%s" % (traceback.format_exc())
        logger.error("%s" % (tracebackerror))
        logger.error(msglog)
        logger.error("The exception raised is %s" % error_exception)
        historymessage(
            xmppobject, sessionid, "%s\ndetail error:\n%s" % (msglog, tracebackerror)
        )


def historymessage(xmppobject, sessionid, msg):
    xmppobject.xmpplog(
        msg,
        type="deploy",
        sessionname=sessionid,
        priority=-1,
        action="xmpplog",
        who="",
        how="",
        why=xmppobject.boundjid.bare,
        module="Wol | Start | Creation",
        date=None,
        fromuser=xmppobject.boundjid.bare,
        touser="",
    )


def read_conf_wol(xmppobject):
    """
    This function read the configuration file for the wol plugin.
    The configuration file should be like:
    [parameters]
    remotelan = True
    # wakeonlanport using only for remotelan is False
    wakeonlanport = 9
    """
    conf_filename = plugin["NAME"] + ".ini"
    pathfileconf = os.path.join(xmppobject.config.pathdirconffile, conf_filename)
    xmppobject.wakeonlanremotelan = True
    xmppobject.wakeonlanport = 9
    if not os.path.isfile(pathfileconf):
        logger.error(
            "The configuration file for the plugin %s is missing.\n"
            "It should be located to %s)" % (plugin["NAME"], pathfileconf)
        )
    else:
        Config = configparser.ConfigParser()
        Config.read(pathfileconf)
        if os.path.exists(pathfileconf + ".local"):
            Config.read(pathfileconf + ".local")

        if Config.has_option("parameters", "remotelan"):
            xmppobject.wakeonlanremotelan = Config.getboolean("parameters", "remotelan")

        if not xmppobject.wakeonlanremotelan:
            if Config.has_option("parameters", "wakeonlanport"):
                xmppobject.wakeonlanport = Config.getint("parameters", "wakeonlanport")
