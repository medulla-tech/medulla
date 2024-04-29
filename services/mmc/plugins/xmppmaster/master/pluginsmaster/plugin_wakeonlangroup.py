#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# file pluginsmaster/plugin_wakeonlangroup.py
import json
from medulla.database.xmppmaster import XmppMasterDatabase
import traceback
from mmc.plugins.xmppmaster.master.lib.utils import name_random
import logging
import os
from wakeonlan import wol
import configparser

logger = logging.getLogger()

# plugin run wake on lan on mac address
# group mac address wakeonlangroup different wakeonlan
plugin = {"VERSION": "1.5", "NAME": "wakeonlangroup", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug("call %s from %s" % (plugin, message["from"]))
    logger.debug("=====================================================")
    # logger.debug("%s " % json.dumps(data,indent=4))
    sessionid = name_random(5, "wakeonlangroup")
    try:
        compteurcallplugin = getattr(xmppobject, "num_call%s" % action)
        logger.debug("compteurcallplugin %s" % compteurcallplugin)
        if compteurcallplugin == 0:
            read_conf_wol(xmppobject)
            xmppobject.brodcastwol = []
            for ifaceName in interfaces():
                addrs = ifaddresses(ifaceName)
                k = addrs[AF_INET]
                for t in k:
                    if "broadcast" not in t:
                        break
                    if "netmask" not in t:
                        break
                    if "addr" not in t:
                        break
                    xmppobject.brodcastwol.append(t["broadcast"])
    except:
        logger.error("plugin %s\n%s" % (plugin["NAME"], traceback.format_exc()))

    senddataplugin = {
        "action": "wakeonlangroup",
        "sessionid": sessionid,
        "data": {"macaddress": ""},
    }

    try:
        if "macadress" in data or "macaddress" in data:
            if xmppobject.wakeonlangroupremotelan:
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
                    if "broadcast" in data:
                        key_uniq = list(set(list(data["broadcast"])))
                        datamac = {}
                        dataars = {}
                        for t in key_uniq:
                            datamac[t] = []
                            dataars[t] = set()
                        for index, ipbroadcast in enumerate(data["broadcast"]):
                            datamac[ipbroadcast].append(data["macadress"][index])
                            dataars[ipbroadcast].add(data["groupdeploy"][index])
                        for ipbroadcast in datamac:
                            # strdede =",".join(datamac[t])
                            try:
                                wol.send_magic_packet(
                                    *datamac[ipbroadcast],
                                    ip_address=ipbroadcast,
                                    port=xmppobject.wakeonlangroupport
                                )
                                msglog = (
                                    "A WOL request has been sent on broacast subnet %s "
                                    "to the mac address %s"
                                    % (ipbroadcast, datamac[ipbroadcast])
                                )
                            except Exception:
                                # wol direct from master erreur send vers ars wol.
                                for ars in dataars[ipbroadcast]:
                                    senddataplugin["data"]["macaddress"] = datamac[
                                        ipbroadcast
                                    ]
                                    senddataplugin["data"]["macaddress"] = datamac[
                                        ipbroadcast
                                    ]
                                    xmppobject.send_message(
                                        mto=ars,
                                        mbody=json.dumps(
                                            senddataplugin, encoding="latin1"
                                        ),
                                    )
                                    msglog = (
                                        "A WOL request has been dispacher to ARS %s "
                                        % (ars)
                                    )
                            historymessage(xmppobject, sessionid, msglog)
                            logger.debug(msglog)
                    else:
                        datamac = XmppMasterDatabase().wolbroadcastadressmacaddress(
                            data["macadress"]
                        )
                        logger.debug("datamac %s" % datamac)
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
                    dellist = []
                    for z in xmppobject.brodcastwol:
                        try:
                            wol.send_magic_packet(
                                *data["macadress"],
                                ip_address=z,
                                port=xmppobject.wakeonlangroupport
                            )
                        except Exception as e:
                            if "Connection refused" in str(e):
                                logger.debug("WOL impossible on broadcast %s" % z)
                                dellist.append(z)
                    for t in dellist:
                        xmppobject.brodcastwol.remove(t)

                    msglog = (
                        "A local lan WOL request have been sent to the"
                        "(display only for 10 adress) mac address %s and port %s"
                        % (data["macadress"][:10], xmppobject.wakeonlangroupport)
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
    xmppobject.wakeonlantargetsubnet = True

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
        Config = configparser.ConfigParser()
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
