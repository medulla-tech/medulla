#!/usr/bin/python3
# -*- coding: utf-8; -*-
#
# (c) 2016-2017 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#

import json
import sys
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
from mmc.plugins.xmppmaster.master.lib.utils import name_random
import logging
import os
from wakeonlan import wol
import ConfigParser

logger = logging.getLogger()

# plugin run wake on lan on mac address
# group mac address wakeonlangroup different wakeonlan
plugin = {"VERSION": "1.3", "NAME": "wakeonlangroup", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug("call %s from %s" % (plugin, message["from"]))
    logger.debug("=====================================================")
    sessionid = name_random(5, "wakeonlangroup")
    try:
        compteurcallplugin = getattr(xmppobject, "num_call%s" % action)
        logger.debug("compteurcallplugin %s" % compteurcallplugin)
        if compteurcallplugin == 0:
            read_conf_wol(xmppobject)
    except:
        logger.error("plugin %s\n%s" % (plugin["NAME"], traceback.format_exc()))

    try:
        if "macadress" in data:
            if xmppobject.wakeonlangroupremotelan:
                senddataplugin = {
                    "action": "wakeonlangroup",
                    "sessionid": sessionid,
                    "data": {"macaddress": ""},
                }
                serverrelaylist = (
                    XmppMasterDatabase().random_list_ars_relay_one_only_in_cluster()
                )
                senddataplugin["data"]["macaddress"] = data["macadress"]
                for serverrelay in serverrelaylist:
                    xmppobject.send_message(
                        mto=serverrelay["jid"],
                        mbody=json.dumps(senddataplugin, encoding="latin1"),
                        mtype="chat",
                    )
                    msglog = (
                        "A WOL request has been sent from the ARS %s "
                        "to the mac address (10 first adress) %s"
                        % (serverrelay["jid"], data["macadress"][:10])
                    )
                    historymessage(xmppobject, sessionid, msglog)
                    logger.debug(msglog)
            else:
                if xmppobject.wakeonlantargetsubnet:
                    # send magic to the broadcast network
                    datamac = XmppMasterDatabase().wolbroadcastadressmacaddress(
                        data["macadress"]
                    )
                    for t in datamac:
                        strdede = ",".join(datamac[t])
                        wol.send_magic_packet(
                            *datamac[t],
                            ip_address=t,
                            port=xmppobject.wakeonlangroupport
                        )
                        msglog = (
                            "A WOL request has been sent on broacast subnet %s "
                            "to the mac address %s" % (t, datamac[t])
                        )
                        historymessage(xmppobject, sessionid, msglog)
                        logger.debug(msglog)
                else:
                    wol.send_magic_packet(
                        *data["macadress"], port=xmppobject.wakeonlangroupport
                    )
                    msglog = (
                        "A local lan WOL request have been sent to the"
                        " mac address %s and port %s"
                        % (data["macadress"], xmppobject.wakeonlangroupport)
                    )
                    historymessage(xmppobject, sessionid, msglog)
                    logger.debug(msglog)
        else:
            msglog = "macadress key missing for plugin wakeonlangroup"
            historymessage(xmppobject, sessionid, msglog)
            logger.debug(msglog)

    except Exception as error_exception:
        msglog = (
            "An error occurent when loading the plugin plugin_wakeonlangroup %s" % data
        )
        tracebackerror = "\n%s" % (traceback.format_exc())
        logger.error("%s\n%s" % (tracebackerror, msglog))
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

    namefichierconf = plugin["NAME"] + ".ini"
    pathfileconf = os.path.join(xmppobject.config.pathdirconffile, namefichierconf)
    logger.debug("fichier de configuration is %s" % pathfileconf)
    xmppobject.wakeonlangroupremotelan = False
    xmppobject.wakeonlangroupport = 9
    xmppobject.wakeonlantargetsubnet = False

    if not os.path.isfile(pathfileconf):
        logger.error(
            "The configuration file for the plugin %s is missing.\n"
            "It should be located to %s)" % (plugin["NAME"], pathfileconf)
        )
        if not xmppobject.wakeonlangroupremotelan:
            logger.error(
                "default parameters is\nremotelan %s"
                "\nwakeonlanport %s\ntargetsubnet %s"
                % (
                    xmppobject.wakeonlangroupremotelan,
                    xmppobject.wakeonlangroupport,
                    xmppobject.wakeonlantargetsubnet,
                )
            )
        else:
            logger.error(
                "default parameters is remotelan %s"
                % (xmppobject.wakeonlangroupremotelan)
            )
    else:
        Config = ConfigParser.ConfigParser()
        Config.read(pathfileconf)
        if os.path.exists(pathfileconf + ".local"):
            Config.read(pathfileconf + ".local")

        if Config.has_option("parameters", "remotelan"):
            xmppobject.wakeonlangroupremotelan = Config.getboolean(
                "parameters", "remotelan"
            )

        if not xmppobject.wakeonlangroupremotelan:
            if Config.has_option("parameters", "wakeonlanport"):
                xmppobject.wakeonlangroupport = Config.getint(
                    "parameters", "wakeonlanport"
                )

            if Config.has_option("parameters", "targetsubnet"):
                xmppobject.wakeonlantargetsubnet = Config.getboolean(
                    "parameters", "targetsubnet"
                )
        if not xmppobject.wakeonlangroupremotelan:
            logger.info(
                "parameters is\nremotelan %s"
                "\nwakeonlanport %s\ntargetsubnet %s"
                % (
                    xmppobject.wakeonlangroupremotelan,
                    xmppobject.wakeonlangroupport,
                    xmppobject.wakeonlantargetsubnet,
                )
            )
        else:
            logger.info(
                "parameters is remotelan %s" % (xmppobject.wakeonlangroupremotelan)
            )
