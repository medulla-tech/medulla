#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2020 siveo, http://www.siveo.net
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
# file pluginsmaster/plugin_reversessh_AM_ARS.py
# this plugin can be called from quick action
# eg : plugin_reversessh_AM_ARS@_@{ "proxyport" : 5225", "remoteport" : 9091 }
import json
from utils import name_random
import logging

from pulse2.database.xmppmaster import XmppMasterDatabase

logger = logging.getLogger()
plugin = {"VERSION": "1.0", "NAME": "reversessh_AM_ARS", "TYPE": "master"}

def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug(plugin)
    logger.debug(json.dumps(data, indent=4))
    logger.debug("=====================================================")
    try:
        logger.debug(json.dumps(data['data'], indent=4))
        #logger.debug( json.dumps(data[0], indent=4))
        if 'data' in data and isinstance(data['data'], list):
            proxyport = None
            remoteport = None
            try:
                parameters = json.loads(data['data'][-1][0])
            except Exception:
                logger.error("parameter missing")
                return
            try:
                proxyport = parameters['proxyport']
            except Exception:
                pass
            try:
                remoteport = parameters['remoteport']
            except Exception:
                logger.error("parameter remoteport missing")
                pass
            jidARS = data['data'][1]['groupdeploy']
            jidAM = data['data'][0]
            ipARS = XmppMasterDatabase().ippackageserver(jidARS)[0]
            port_ssh_ars = 22
            type_reverse = "R"
            logger.debug("ipARS %s" % ipARS)
            logger.debug("jidARS %s" % jidARS)
            logger.debug("jidAM %s" % jidAM)
            logger.debug("remoteport %s" % remoteport)
            ## il faut inscrire la clef publique de la machine distante dans
            ## /var/lib/pulse2/clients/reversessh/.ssh/authorized_keys

            result = xmppobject.iqsendpulse(jidARS,
                                            {"action": "information",
                                             "data": {"listinformation": ["get_ars_key_id_rsa_pub",
                                                                          "get_ars_key_id_rsa",
                                                                          "get_free_tcp_port"],
                                                      "param": {}
                                                      }
                                             },
                                            5)
            res = json.loads(result)
            if res['numerror'] != 0:
                logger.error("iq information error to %s on get_ars_key_id_rsa_pub,get_ars_key_id_rsa,get_free_tcp_port" % jidARS)
                return
            resultatinformation = res['result']['informationresult']
            logger.debug("parameter %s" % data['data'][-1])
            if proxyport is None:
                proxyportars = resultatinformation['get_free_tcp_port']
            else:
                proxyportars = proxyport
            timeout = 20
            result = xmppobject.iqsendpulse(jidARS,
                                              {"action": "information",
                                               "data": {"listinformation": ["add_proxy_port_reverse"],
                                                        "param": {"proxyport": proxyportars}
                                                        }
                                               },
                                              timeout)
            structreverse = {"action": "reversesshqa",
                             "sessionid": name_random(5, "plug_rev"),
                             "from": xmppobject.boundjid.bare,
                             "data": {"ipARS": ipARS,
                                      "jidARS": jidARS,
                                      "jidAM": jidAM,
                                      "remoteport": remoteport,
                                      "portproxy": proxyportars,
                                      "type_reverse": type_reverse,
                                      "port_ssh_ars": 22,
                                      "private_key_ars": resultatinformation['get_ars_key_id_rsa'],
                                      "public_key_ars": resultatinformation['get_ars_key_id_rsa_pub']
                                      }
                             }
            result = xmppobject.iqsendpulse(jidAM, structreverse, 15)
    except KeyError as e:
        logger.debug(
            "data[0] not found while calling %s. The plugin is probably called from a quick action." % (plugin['NAME']))
        pass
