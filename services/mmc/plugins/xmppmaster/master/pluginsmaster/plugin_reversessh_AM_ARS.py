#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
this plugin can be called from quick action
eg : plugin_reversessh_AM_ARS@_@{ "proxyport" : 5225", "remoteport" : 9091 }
"""
import json
import logging

from pulse2.database.xmppmaster import XmppMasterDatabase

logger = logging.getLogger()
plugin = {"VERSION": "1.0", "NAME": "reversessh_AM_ARS", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug(plugin)
    logger.debug(json.dumps(data, indent=4))
    logger.debug("=====================================================")
    timeout = 15
    try:
        if "sessionid" in data:
            sessionid = data["sessionid"]
        if "data" in data and isinstance(data["data"], list):
            proxyport = None
            remoteport = None
            uninterrupted = False
            port_ssh_ars = 22
            try:
                parameters = json.loads(data["data"][-1][0])
            except Exception:
                logger.error("parameter missing")
                return
            try:
                uninterrupted = parameters["uninterrupted"]
            except Exception:
                pass
            try:
                port_ssh_ars = parameters["port_ssh_ars"]
            except Exception:
                pass

            try:
                proxyport = parameters["proxyport"]
            except Exception:
                pass
            try:
                remoteport = parameters["remoteport"]
            except Exception:
                logger.error("parameter remoteport missing")
                pass
            jidARS = data["data"][1]["groupdeploy"]
            jidAM = data["data"][0]
            ipARS = XmppMasterDatabase().ippackageserver(jidARS)[0]
            type_reverse = "R"
            logger.debug("ipARS %s" % ipARS)
            logger.debug("jidARS %s" % jidARS)
            logger.debug("jidAM %s" % jidAM)
            logger.debug("remoteport %s" % remoteport)
            ## il faut inscrire la clef publique de la machine distante dans
            ## /var/lib/pulse2/clients/reversessh/.ssh/authorized_keys

            result = xmppobject.iqsendpulse(
                jidARS,
                {
                    "action": "information",
                    "data": {
                        "listinformation": [
                            "get_ars_key_id_rsa_pub",
                            "get_ars_key_id_rsa",
                            "get_free_tcp_port",
                        ],
                        "param": {},
                    },
                },
                timeout,
            )
            res = json.loads(result)
            if res["numerror"] != 0:
                logger.error(
                    "iq information error to %s on get_ars_key_id_rsa_pub,get_ars_key_id_rsa,get_free_tcp_port"
                    % jidARS
                )
                return
            resultatinformation = res["result"]["informationresult"]
            logger.debug("parameter %s" % data["data"][-1])
            if proxyport is None:
                proxyportars = resultatinformation["get_free_tcp_port"]
            else:
                proxyportars = proxyport

            result = xmppobject.iqsendpulse(
                jidARS,
                {
                    "action": "information",
                    "data": {
                        "listinformation": ["add_proxy_port_reverse"],
                        "param": {"proxyport": proxyportars},
                    },
                },
                timeout,
            )
            structreverse = {
                "action": "reversesshqa",
                "sessionid": sessionid,
                "from": xmppobject.boundjid.bare,
                "data": {
                    "ipARS": ipARS,
                    "jidARS": jidARS,
                    "jidAM": jidAM,
                    "remoteport": remoteport,
                    "portproxy": proxyportars,
                    "type_reverse": type_reverse,
                    "port_ssh_ars": port_ssh_ars,
                    "private_key_ars": resultatinformation["get_ars_key_id_rsa"],
                    "public_key_ars": resultatinformation["get_ars_key_id_rsa_pub"],
                },
            }
            result = xmppobject.iqsendpulse(jidAM, structreverse, timeout)

            del structreverse["data"]["private_key_ars"]
            del structreverse["data"]["public_key_ars"]
            structreverse["data"]["uninterrupted"] = uninterrupted
            XmppMasterDatabase().updateaddCommand_action(
                json.dumps(structreverse["data"], indent=4), sessionid
            )
    except KeyError as e:
        logger.debug(
            "data[0] not found while calling %s. The plugin is probably called from a quick action."
            % (plugin["NAME"])
        )
        pass
