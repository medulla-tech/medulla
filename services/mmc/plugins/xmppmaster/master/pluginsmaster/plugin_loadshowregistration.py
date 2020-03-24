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
# file master/pluginsmaster/plugin_loadshowregistration.py

import base64
import json
import os
import logging
import traceback
import types
import ConfigParser
from pulse2.database.xmppmaster import XmppMasterDatabase

logger = logging.getLogger()
DEBUGPULSEPLUGIN = 25

# this plugin calling to starting agent

plugin = {"VERSION" : "1.0", "NAME" : "loadshowregistration", "TYPE" : "master"}

def action( objectxmpp, action, sessionid, data, msg, dataerreur):
    logger.debug("=====================================================")
    logger.debug("call %s from %s"%(plugin, msg['from']))
    logger.debug("=====================================================")
    try:
        compteurcallplugin = getattr(objectxmpp, "num_call%s"%action)

        if compteurcallplugin == 0:
            read_conf_showregistration(objectxmpp)
    except:
        logger.error("plugin %s\n%s"%(plugin['NAME'], traceback.format_exc()))


def read_conf_showregistration(objectxmpp):
    namefichierconf = plugin['NAME'] + ".ini"
    pathfileconf = os.path.join( objectxmpp.config.pathdirconffile, namefichierconf )
    if not os.path.isfile(pathfileconf):
        logger.error("plugin %s\nConfiguration file :\n" \
                     "\t%s missing\n" \
                     "eg conf:\n[parameters]\n" \
                     "showinfo = False\n" \
                     "showinfodeploy = False\n" \
                     "showplugins = False\n" \
                     "showscheduledplugins = False\n" \
                     "showinventoryxmpp = False\n" \
                     "showinfomachine = client_machine_1, client_machine_2\n"%(plugin['NAME'],
                                                                           pathfileconf))
        logger.warning("\ndefault value for showinfodeploy is False\n"\
                       "default value for showinfo is False\n"\
                       "default value for showplugins is False\n"\
                       "default value for showscheduledplugins is False\n"\
                       "default value for showinventoryxmpp is False"\
                       "default value for showinfomachine is no machines list")
        objectxmpp.showinfo = False
        objectxmpp.showinfodeploy = False
        objectxmpp.showplugins = False
        objectxmpp.showscheduledplugins = False
        objectxmpp.showinventoryxmpp = False
        objectxmpp.showinfomachine=[]
    else:
        Config = ConfigParser.ConfigParser()
        Config.read(pathfileconf)
        if os.path.exists(pathfileconf + ".local"):
            Config.read(pathfileconf + ".local")
        if Config.has_option("parameters", "showinfodeploy"):
            objectxmpp.showinfodeploy = Config.getboolean('parameters', 'showinfodeploy')
        else:
            objectxmpp.showinfodeploy = False

        if Config.has_option("parameters", "showinfo"):
            objectxmpp.showinfo = Config.getboolean('parameters', 'showinfo')
        else:
            objectxmpp.showinfo = False

        if Config.has_option("parameters", "showplugins"):
            objectxmpp.showplugins = Config.getboolean('parameters', 'showplugins')
        else:
            objectxmpp.showplugins = False
        if Config.has_option("parameters", "showscheduledplugins"):
            objectxmpp.showscheduledplugins = Config.getboolean('parameters', 'showscheduledplugins')
        else:
            objectxmpp.showscheduledplugins = False
        if Config.has_option("parameters", "showinventoryxmpp"):
            objectxmpp.showinventoryxmpp = Config.getboolean('parameters', 'showinventoryxmpp')
        else:
            objectxmpp.showinventoryxmpp = False
        if Config.has_option("parameters", "showinfomachine"):
            showinfomachinelocal = Config.get('parameters', 'showinfomachine')

            objectxmpp.showinfomachine = [str(x.strip())
                                          for x in showinfomachinelocal.split(",")
                                          if x.strip() != ""]

        else:
            objectxmpp.showinfomachine = []
    objectxmpp.plugin_loadshowregistration = types.MethodType(plugin_loadshowregistration, objectxmpp)

def plugin_loadshowregistration(self, msg, data):
    if "all" in self.showinfomachine or \
        "ALL" in self.showinfomachine or \
            data['machine'].split(".")[0] in self.showinfomachine:
        if self.showinfodeploy:
            self.presencedeployment = {}
            listrs = XmppMasterDatabase().listjidRSdeploy()
            if len(listrs) != 0:
                strchaine = ""
                for i in listrs:
                    li = XmppMasterDatabase().listmachinesfromdeploy(i[0])
                    strchaine += "\nRS [%s] for deploy on %s Machine\n" % (i[0], len(li)-1)
                    strchaine +='|{0:5}|{1:7}|{2:20}|{3:35}|{4:55}|\n'.format("type",
                                                                            "uuid",
                                                                            "Machine",
                                                                            "jid",
                                                                            "platform")
                    for j in li:
                        if j[9] == 'relayserver':
                            TY = 'RSer'
                        else:
                            TY = "Mach"
                        strchaine +='|{0:5}|{1:7}|{2:20}|{3:35}|{4:55}|\n'.format(TY,
                                                                                j[5],
                                                                                j[4],
                                                                                j[1],
                                                                                j[2])
                logger.debug(strchaine)
            else:
                logger.debug("No Machine Listed")
        strlistplugin = ""
        if self.showplugins:
            #logger.debug("Machine %s"%msg['from'])
            if 'plugin' in data:
                strlistplugin += "\nlist plugins on machine %s\n"%msg['from']
                strlistplugin += "|{0:35}|{1:10}|\n".format("Plugin Name", "Version")
                for key, value in data['plugin'].iteritems():
                    strlistplugin += "|{0:35}|{1:10}|\n".format(key, value)
        if self.showscheduledplugins:
            if 'pluginscheduled' in data:
                strlistplugin += "\nlist scheduled plugins on machine %s\n"%msg['from']
                strlistplugin += "|{0:35}|{1:10}|\n".format("scheduled Plugin Name", "Version")
                for key, value in data['pluginscheduled'].iteritems():
                    strlistplugin += "|{0:35}|{1:10}|\n".format(key, value)
        if strlistplugin != "":
            logger.debug(strlistplugin)

        if self.showinfo:
            logger.info("--------------------------")
            logger.info("** INFORMATION FROM AGENT %s %s" % (data['agenttype'].upper(),
                                                                data['from']))
            logger.info("__________________________")
            logger.info("MACHINE INFORMATION")
            logger.info("Deployment name : %s" % data['deployment'])
            logger.info("From : %s" % data['who'])
            logger.info("Jid from : %s" % data['from'])
            logger.info("Machine : %s" % data['machine'])
            logger.info("Platform : %s" % data['platform'])
            if 'versionagent' in data:
                logger.info("Version agent : %s" % data['versionagent'])
            if "win" in data['platform'].lower():
                logger.info("__________________________")
                logger.info("ACTIVE DIRECTORY")
                logger.info("OU Active directory")
                logger.info("OU by machine : %s" % data['adorgbymachine'])
                logger.info("OU by user : %s" % data['adorgbyuser'])
                if 'lastusersession' in data:
                    logger.info("last user session: %s" % data['lastusersession'])
            logger.info("--------------------------------")
            logger.info("----MACHINE XMPP INFORMATION----")
            logger.info("portxmpp : %s" % data['portxmpp'])
            logger.info("serverxmpp : %s" % data['serverxmpp'])
            logger.info("xmppip : %s" % data['xmppip'])
            logger.info("agenttype : %s" % data['agenttype'])
            if 'moderelayserver' in data:
                logger.info("mode relay server : %s" % data['moderelayserver'])
            logger.info("baseurlguacamole : %s" % data['baseurlguacamole'])
            logger.info("xmppmask : %s" % data['xmppmask'])
            logger.info("subnetxmpp : %s" % data['subnetxmpp'])
            logger.info("xmppbroadcast : %s" % data['xmppbroadcast'])
            logger.info("xmppdhcp : %s" % data['xmppdhcp'])
            logger.info("xmppdhcpserver : %s" % data['xmppdhcpserver'])
            logger.info("xmppgateway : %s" % data['xmppgateway'])
            logger.info("xmppmacaddress : %s" % data['xmppmacaddress'])
            logger.info("xmppmacnotshortened : %s" % data['xmppmacnotshortened'])
            if data['agenttype'] == "relayserver":
                logger.info("package server : %s" % data['packageserver'])
            if 'ipconnection' in data:
                logger.info("ipconnection : %s" % data['ipconnection'])
            if 'portconnection' in data:
                logger.info("portconnection : %s" % data['portconnection'])
            if 'classutil' in data:
                logger.info("classutil : %s" % data['classutil'])
            if 'ippublic' in data:
                logger.info("ippublic : %s" % data['ippublic'])
            if 'localisationinfo' in data:
                logger.info("------------LOCALISATION-----------")
                logger.info("localisationinfo : %s" % data['localisationinfo'])
            if "win" in data['platform'].lower():
                if 'adorgbymachine' in data and data['adorgbymachine']:
                    logger.info("AD found for the Machine : %s" % data['adorgbymachine'])
                else:
                    logger.info("No AD found for the Machine")
                if 'adorgbyuser' in data and data['adorgbyuser']:
                    logger.info("AD found for the User : %s" % data['adorgbyuser'])
                else:
                    logger.info("No AD found for the User")
            logger.info("-----------------------------------")

            if self.showinventoryxmpp:
                logger.info("DETAILED COMPLETINFORMATION")
                if 'completedatamachine' in data:
                    info = json.loads(base64.b64decode(data['completedatamachine']))
                    data['information'] = info
                    del data['completedatamachine']
                logger.info("%s" % json.dumps(data, indent=4, sort_keys=True))

