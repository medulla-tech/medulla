# -*- coding: utf-8 -*-
#
# (c) 2016 siveo, http://www.siveo.net
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
# file pluginsmaster/plugin_loadreconf.py

import json
import os
import logging
from lib.utils import getRandomName
import types
import ConfigParser
from pulse2.database.xmppmaster import XmppMasterDatabase
from sleekxmpp import jid
import time

logger = logging.getLogger()
DEBUGPULSEPLUGIN = 25

# this plugin calling to starting agent

plugin = {"VERSION" : "1.0", "NAME" : "loadreconf", "TYPE" : "master"}

def action( objectxmpp, action, sessionid, data, msg, dataerreur):
    logger.debug("=====================================================")
    logger.debug("call %s from %s"%(plugin, msg['from']))
    logger.debug("=====================================================")

    compteurcallplugin = getattr(objectxmpp, "num_call%s"%action)

    if compteurcallplugin == 0:
        read_conf_loadreconf(objectxmpp)
        logger.debug("Configuration remote update")
        objectxmpp.concurentdata = {}
        objectxmpp.loadreconf = types.MethodType(loadreconf,
                                                 objectxmpp)
        objectxmpp.listconcurentreconf = []
        objectxmpp.schedule('loadreconf',
                            objectxmpp.generate_reconf_interval,
                            objectxmpp.loadreconf,
                            args=(objectxmpp,),
                            repeat=True)


def loadreconf(self, objectxmpp):
    """
        Runs the load fingerprint
    """
    # calcul time entre 2 demandes de reconfiguration.
    t = time.time()
    end = t + objectxmpp.generate_reconf_interval

    datasend = {"action": "force_setup_agent",
                "data": "",
                'ret': 0,
                'sessionid': getRandomName(5, "loadreconf_")}
    result = []
    while(time.time() < end):
        listmachine_timeoutreconf = [x[0] for x in objectxmpp.listconcurentreconf if x[2] <= t]
        if len(listmachine_timeoutreconf) != 0:
            #acquite sur timeout
            logger.warning ("update off presence machine reconf timeout%s"%listmachine_timeoutreconf)
            XmppMasterDatabase().call_set_list_machine(listmachine=listmachine_timeoutreconf)
            # on supprime les non acquites suivant timeout de plus de generate_reconf_interval seconde
            objectxmpp.listconcurentreconf = [x for x in objectxmpp.listconcurentreconf if x[2] > t]
        viability = time.time() + objectxmpp.timeout_reconf

        list_need_reconf = [ x[0] for x in objectxmpp.listconcurentreconf]
        # lists reconf terminate
        if len(list_need_reconf) > 0:
            resultacquite = XmppMasterDatabase().call_acknowledged_reconficuration(list_need_reconf)
            # liste des concurent
            if len(resultacquite) > 0:
                logger.debug ("concurent acquite machines id %s"%resultacquite)
            objectxmpp.listconcurentreconf = [ x for x in objectxmpp.listconcurentreconf \
                                            if x[0] not in resultacquite]
        if len(result) == 0:
            result =  XmppMasterDatabase().call_reconfiguration_machine(limit = objectxmpp.nbconcurrentreconf)
            if len(result) == 0:
                return
        list_updatenopresence = []
        while len(objectxmpp.listconcurentreconf) < objectxmpp.nbconcurrentreconf and \
                len(result) > 0 and \
                    time.time() < end:
            eltmachine = result.pop(0)
            eltmachine.append(viability)
            objectxmpp.listconcurentreconf.append(eltmachine)
            self.send_message(  mto = eltmachine[1],
                                mbody=json.dumps(datasend),
                                mtype='chat')
            logger.debug ("SEND RECONFIGURATION %s (%s)"%(eltmachine[1], eltmachine[0]))
            list_updatenopresence.append(eltmachine[0])
        if len(list_updatenopresence) != 0:
            #logger.debug ("update off presence machine reconf%s"%list_updatenopresence)
            XmppMasterDatabase().call_set_list_machine(listmachine=list_updatenopresence)
        time.sleep(.2)

def read_conf_loadreconf(objectxmpp):
    namefichierconf = plugin['NAME'] + ".ini"
    pathfileconf = os.path.join( objectxmpp.config.pathdirconffile, namefichierconf )
    if not os.path.isfile(pathfileconf):
        logger.warning("plugin %s\nConfiguration file :" \
            "\n\t%s missing" \
        "\neg conf:\n[parameters]\n" \
        "generate_reconf_interval = 60\n" \
        "concurrentreconf = 240\n" \
        "timeout_reconf = 30"%( plugin['NAME'],
                                pathfileconf))
        objectxmpp.generate_reconf_interval = 10
        objectxmpp.nbconcurrentreconf = 240
        objectxmpp.timeout_reconf = 30
    else:
        Config = ConfigParser.ConfigParser()
        Config.read(pathfileconf)
        logger.debug("read file %s"%pathfileconf)
        if os.path.exists(pathfileconf + ".local"):
            Config.read(pathfileconf + ".local")
            logger.debug("read file %s.local"%pathfileconf)
            if Config.has_option("parameters",
                                 "generate_reconf_interval"):
                objectxmpp.generate_reconf_interval = Config.getint('parameters',
                                                                    'generate_reconf_interval')
            else:
                objectxmpp.generate_reconf_interval = 60

            if Config.has_option("parameters",
                                 "concurrentreconf"):
                objectxmpp.nbconcurrentreconf = Config.getint('parameters',
                                                      'concurrentreconf')
            else:
                objectxmpp.nbconcurrentreconf = 240


            if Config.has_option("parameters",
                                 "timeout_reconf"):
                objectxmpp.timeout_reconf = Config.getint('parameters',
                                                                    'timeout_reconf')
            else:
                objectxmpp.timeout_reconf = 500
    objectxmpp.plugin_loadreconf = types.MethodType(plugin_loadreconf, objectxmpp)

def plugin_loadreconf(self, msg, data):
    # Manage update remote agent
    pass
