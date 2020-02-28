#!/usr/bin/env python
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
# file /pluginsmaster/plugin_assessor_agent.py

import base64
import json
from utils import AESCipher, \
                  subnetnetwork, \
                  ipfromdns
import logging
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
from random import randint
from localisation import Localisation
import operator
import netaddr
import os
import ConfigParser

from manageADorganization import manage_fqdn_window_activedirectory

logger = logging.getLogger()

plugin = {"VERSION": "1.1", "NAME": "assessor_agent", "TYPE": "master"}


def action(objectxmpp, action, sessionid, data, msg, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug("call %s from %s"%(plugin, msg['from']))
    logger.debug("=====================================================")

    compteurcallplugin = getattr(objectxmpp, "num_call%s"%action)

    logger.debug("compteur ASSESSOR num_call%s %s"%(action, compteurcallplugin))

    if compteurcallplugin == 0:
        read_conf_assessor_master(objectxmpp)
        logger.debug("%s  "%objectxmpp.assessor_agent_showinfomachine)

    if objectxmpp.assessor_agent_errorconf:
        logger.debug("error configuration no process action %s for machine %s"%(action , msg['from']))
        return

    try:
        MessagesAgentFromChatroomConfig(objectxmpp,
                                        action,
                                        sessionid,
                                        data,
                                        msg,
                                        ret,
                                        dataobj)
    except Exception:
        sendErrorConnectionConf(objectxmpp, sessionid, msg)
        logger.error("\n%s"%(traceback.format_exc()))

def testsignaturecodechaine(objectxmpp, data, sessionid, msg):
    codechaine="%s"%(msg['from'])
    result = False
    for t in objectxmpp.assessor_agent_keyAES32:
        cipher = AESCipher(t)
        decrypted = cipher.decrypt(data['codechaine'])
        if str(decrypted) == str(codechaine):
            result = True
            break
    if not result:
        logger.warning("authentification False %s"%(codechaine))
        sendErrorConnectionConf(objectxmpp, sessionid, msg)
    return result

def MessagesAgentFromChatroomConfig(objectxmpp, action, sessionid, data, msg, ret, dataobj):
    logger.debug("MessagesAgentFromChatroomConfig")
    codechaine="%s"%(msg['from'])

    logger.debug("CONFIGURATION AGENT MACHINE")
    if data['adorgbymachine'] is not None and data['adorgbymachine'] != "":
        data['adorgbymachine'] = base64.b64decode(data['adorgbymachine'])
    if data['adorgbyuser'] is not None and data['adorgbyuser'] != "":
        data['adorgbyuser'] = base64.b64decode(data['adorgbyuser'])
    try:
        data['information'] = json.loads(base64.b64decode(data['completedatamachine']))
        del data['completedatamachine']
        json.dumps(data, indent = 4)
    except Exception:
        logger.debug("decode msg error from %s"%(codechaine))
        sendErrorConnectionConf(objectxmpp, sessionid, msg)
        return

    if data['agenttype'] == "relayserver":
        objectxmpp.sendErrorConnectionConf(objectxmpp, sessionid, msg)
        return

    if 'codechaine' not in data:
        logger.debug("missing authentification from %s"%(codechaine))
        sendErrorConnectionConf(objectxmpp, sessionid, msg)
        return

    if not testsignaturecodechaine(objectxmpp, data, sessionid, msg):
        return

    if data['ippublic'] is not None and data['ippublic'] != "":
        data['localisationinfo'] = Localisation().geodataip(data['ippublic'])
    else:
        data['localisationinfo'] = {}
    displayData(objectxmpp, data)

    if not ('information' in data and \
                'users' in data['information'] and \
                    len(data['information']['users']) > 0):
        data['information']['users'].append("system")
    else:
        XmppMasterDatabase().log("Warning no user determinated for the machine : %s " %
                                (data['information']['info']['hostname']))

    msgstr = "Search Relay Server for " \
             "connection from user %s "\
             "hostname %s localisation %s"%(data['information']['users'][0],
                                            data['information']['info']['hostname'],
                                            data['localisationinfo'])
    logger.debug(msgstr)
    XmppMasterDatabase().log(msgstr)

    adorgbymachinebool = False
    if 'adorgbymachine' in data and data['adorgbymachine'] != "":
        adorgbymachinebool = True

    adorgbyuserbool = False
    if 'adorgbyuser' in data and data['adorgbyuser'] != "":
        adorgbyuserbool = True

    # Defining relay server for connection
    # Order of rules to be applied
    ordre = XmppMasterDatabase().Orderrules()
    odr = [x[0] for x in ordre]
    logger.debug("Rule order : %s " % odr)
    result = []
    for x in ordre:
        # User Rule : 1
        if x[0] == 1:
            logger.debug("Analysis the 1st rule : select the relay server by User")
            result1 = XmppMasterDatabase().algoruleuser(data['information']['users'][0])
            if len(result1) > 0:
                logger.debug("Applied : Associate the relay server based on user.")
                result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                msg_log("The User",
                        data['information']['info']['hostname'],
                        data['information']['users'][0],
                        result)
                break

        # Hostname Rule : 2
        elif x[0] == 2:
            logger.debug("Analysis the 2nd rule : select the relay server by Hostname")
            result1 = XmppMasterDatabase().algorulehostname(
                data['information']['info']['hostname'])
            if len(result1) > 0:
                logger.debug("applied rule Associate relay server based on hostname")
                result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                msg_log("The Hostname",
                        data['information']['info']['hostname'],
                        data['information']['users'][0],
                        result)
                break

        # Location Rule : 3
        elif x[0] == 3:
            logger.debug("Analysis the 3rd rule : select the relay server by Geolocalisation")
            distance = 40000000000
            listeserver = []
            relayserver = -1
            result = []
            try:
                if 'localisationinfo' in data \
                        and data['localisationinfo'] is not None \
                        and 'longitude' in data['localisationinfo'] \
                        and 'latitude' in data['localisationinfo'] \
                        and data['localisationinfo']['longitude'] != "" \
                        and data['localisationinfo']['latitude'] != "":
                    result1 = XmppMasterDatabase().IdlonglatServerRelay(data['classutil'])
                    a = 0
                    for x in result1:
                        a += 1
                        if x[1] != "" and x[2] != "":
                            distancecalculated = Localisation().determinationbylongitudeandip(
                                float(x[2]), float(x[1]), data['ippublic'])
                            if distancecalculated <= distance:
                                distance = distancecalculated
                                relayserver = x[0]
                                listeserver.append(x[0])
                    nbserver = len(listeserver)
                    if nbserver > 1:
                        index = randint(0, nbserver-1)
                        logger.warn("Geoposition Rule returned %d " \
                                    "relay servers for machine"
                                    "%s user %s \nPossible relay servers" \
                                    " : id list %s " % (nbserver, data['information']['info']['hostname'],
                                                        data['information']['users'][0], listeserver))
                        logger.warn("ARS Random choice : %s"%listeserver[index])
                        result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(listeserver[index])
                        msg_log("The Geoposition",
                                    data['information']['info']['hostname'],
                                    data['information']['users'][0],
                                    result)
                        break
                    else:
                        if relayserver != -1:
                            result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(relayserver)
                            msg_log("The Geoposition",
                                    data['information']['info']['hostname'],
                                    data['information']['users'][0],
                                    result)
                            break
                        else:
                            logger.warn("algo rule 3 inderterminat")
                            continue
            except KeyError:
                logger.error("Error algo rule 3")
                logger.error("\n%s"%(traceback.format_exc()))
                continue

        # Subnet Rule : 4
        elif x[0] == 4:
            logger.debug("Analysis the 4th rule : select the relay server in same subnet")
            logger.debug("rule subnet : Test if network are identical")
            subnetexist = False
            for z in data['information']['listipinfo']:
                result1 = XmppMasterDatabase().algorulesubnet(subnetnetwork(z['ipaddress'],
                                                                            z['mask']),
                                                                data['classutil'])
                if len(result1) > 0:
                    logger.debug("Applied rule : select the relay server in same subnet")
                    subnetexist = True
                    result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    msg_log("same subnet",
                            data['information']['info']['hostname'],
                            data['information']['users'][0],
                            result)
                    break
            if subnetexist:
                break

        # Default Rule : 5
        elif x[0] == 5:
            logger.debug("analysis the 5th rule : use default relay server %s" %
                            objectxmpp.assessor_agent_serverip)
            result = XmppMasterDatabase().jidrelayserverforip(objectxmpp.assessor_agent_serverip)
            msg_log("use default relay server",
                    data['information']['info']['hostname'],
                    data['information']['users'][0],
                    result)
            break

        # Load Balancer Rule : 6
        elif x[0] == 6:
            logger.debug("Analysis the 6th rule : select the relay on less requested ARS (load balancer)")
            result1 = XmppMasterDatabase().algoruleloadbalancer()
            if len(result1) > 0:
                logger.debug("Applied : Rule Chooses the less requested ARS.")
                result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                msg_log("Load Balancer",
                        data['information']['info']['hostname'],
                        data['information']['users'][0],
                        result)
                break

        # OU Machine Rule : 7
        elif x[0] == 7:
            # "AD organised by machines "
            logger.debug("Analysis the 7th rule : AD organized by machines")
            if adorgbymachinebool:
                result1 = XmppMasterDatabase().algoruleadorganisedbymachines(
                    manage_fqdn_window_activedirectory.getOrganizationADmachineOU(data['adorgbymachine']))
                if len(result1) > 0:
                    logger.debug("Applied rule : AD organized by machines")
                    result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    msg_log("AD organized by machine",
                            data['information']['info']['hostname'],
                            data['information']['users'][0],
                            result)
                    break

        # OU User Rule : 8
        elif x[0] == 8:
            # "AD organised by users"
            logger.debug("Analysis the 8th rule : AD organized by users")
            if adorgbyuserbool:
                result1 = XmppMasterDatabase().algoruleadorganisedbyusers(
                    manage_fqdn_window_activedirectory.getOrganizationADuserOU(data['adorgbyuser']))
                if len(result1) > 0:
                    logger.debug("Applied rule : AD organized by users")
                    result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    msg_log("AD organized by User",
                            data['information']['info']['hostname'],
                            data['information']['users'][0],
                            result)
                    break

        # Network Rule : 9
        elif x[0] == 9:
            # Associates relay server based on network address
            logger.debug("Analysis the 9th rule : Associate relay server based on network address")
            networkaddress = netaddr.IPNetwork(data['xmppip'] + "/" + data['xmppmask']).cidr
            logger.debug("Network address: %s" % networkaddress)
            result1 = XmppMasterDatabase().algorulebynetworkaddress(networkaddress,
                                                                    data['classutil'])
            if len(result1) > 0:
                logger.debug("Applied Rule : Associate relay server based on network address")
                result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                msg_log("network address",
                        data['information']['info']['hostname'],
                        data['information']['users'][0],
                        result)
                break
        # Network Rule : 10
        elif x[0] == 10:
            # Associates relay server based on network address
            logger.debug("Analysis the 10th rule : Associate relay server based on netmask address")
            logger.debug("Net mask address: %s" % data['xmppmask'])
            result1 = XmppMasterDatabase().algorulebynetmaskaddress(data['xmppmask'],
                                                                    data['classutil'])
            if len(result1) > 0:
                logger.debug("Applied Rule : Associate relay server based on net Mask address")
                result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                msg_log("net mask address",
                        data['information']['info']['hostname'],
                        data['information']['users'][0],
                        result)
                break

    try:
        msg_string ="[user %s hostanme %s] : "\
                    "Relay server for connection "\
                    "ip %s port %s" % (data['information']['users'][0],
                                       data['information']['info']['hostname'],
                                       result[0],
                                       result[1])

        logger.debug(msg_string)
        XmppMasterDatabase().log(msg_string)

    except Exception:
        logger.warning("Relay server attributed by default")
        try:
            result = XmppMasterDatabase().jidrelayserverforip(objectxmpp.assessor_agent_serverip)
        except Exception:
            logger.warn("Unable to assign the relay server : missing")
            #result = [objectxmpp.assessor_agent_serverip,
                        #objectxmpp.assessor_agent_port,
                        #objectxmpp.domaindefault,
                        #objectxmpp.assessor_agent_guacamole_baseurl]
            result = XmppMasterDatabase().jidrelayserverforip(objectxmpp.assessor_agent_serverip)
            msg_log("error use default relay server",
                    data['information']['info']['hostname'],
                    data['information']['users'][0],
                    result)
    try:
        listars = XmppMasterDatabase().getRelayServerofclusterFromjidars(result[2],
                                                                         "static")
        z = [listars[x] for x in listars]
        z1 = sorted(z, key=operator.itemgetter(4))
        # arsjid = XmppMasterDatabase().getRelayServerfromjid("rspulse@pulse")
        # Start relay server agent configuration
        # we order the ARS from the least used to the most used.
        response = {'action': 'resultconnectionconf',
                    'sessionid': data['sessionid'],
                    'data': z1,
                    'syncthing' : objectxmpp.assessor_agent_announce_server,
                    'ret': 0
                    }
        if len(listars) == 0:
            logger.warning("No configuration sent to machine "\
                "agent %s. ARS %s is found but it is stopped." % (data['information']['info']['hostname'], result[2]))
            logger.warning("ACTION: Re-start the ARS on %s, and wait for the agent to run its reconfiguration."%(result[2]))
            objectxmpp.xmpplog("No configuration sent to machine agent %s. ARS %s is found but it is stopped." % (result[2],
                                                                                  data['information']['info']['hostname'] ),
                            type = 'conf',
                            sessionname =  sessionid,
                            priority = -1,
                            action = "xmpplog",
                            who = data['information']['info']['hostname'],
                            module = "Configuration | Notify | connectionagent",
                            date = None,
                            fromuser = objectxmpp.boundjid.bare)
            sendErrorConnectionConf(objectxmpp, sessionid, msg)
            return
        agentsubscription = "master@pulse"
        if "substitute" in data and \
            "conflist" in data["substitute"] and \
                len(data["substitute"]["conflist"]) > 0:
            response["substitute"] =  XmppMasterDatabase().\
                                    substituteinfo(data["substitute"],
                                                   z1[0][2])

            response["substitute"]["ars_chooose_for_substitute"] = z1[0][2]

            logger.debug("substitute resend to agent : %s"%json.dumps(response["substitute"],indent=4))

            if "subscription" in response["substitute"]:
                agentsubscription = response["substitute"]['subscription'][0]
                listmacadress=[]
                for mac in data['information']['listipinfo']:
                    listmacadress.append(mac['macaddress'])
                XmppMasterDatabase().setuplistSubscription(listmacadress, agentsubscription)
        objectxmpp.send_message(mto=msg['from'],
                            mbody=json.dumps(response),
                            mtype='chat')
    except Exception:
        sendErrorConnectionConf(objectxmpp,sessionid,msg)
        logger.error("Unable to assign a relay server to an agent")
        logger.error("\n%s"%(traceback.format_exc()))

def msg_log(msg_header, hostname, user, result):
    logger.debug("%s Rule selects " \
                 "the relay server for machine " \
                 "%s user %s \n %s" % (msg_header,
                                       hostname,
                                       user,
                                       result))
    pass

def sendErrorConnectionConf(objectxmpp, session,  msg):
    response = {'action': 'resultconnectionconf',
               'sessionid': session,
               'data': [],
               'syncthing' : "",
               'ret': 255}
    objectxmpp.send_message(mto=msg['from'],
                        mbody=json.dumps(response),
                        mtype='chat')


def read_conf_assessor_master(objectxmpp):
    """
        lit la configuration du plugin
    """
    objectxmpp.assessor_agent_errorconf = False
    namefichierconf = plugin['NAME'] + ".ini"
    pathfileconf = os.path.join("/","etc","mmc","plugins", namefichierconf )
    if not os.path.isfile(pathfileconf):
        logger.error("plugin Master %s\nConfiguration file  missing\n  %s"%(plugin['NAME'],
                                                                     pathfileconf))
        message_config(plugin['NAME'], pathfileconf)
        objectxmpp.assessor_agent_errorconf = True
        return False
    else:
        objectxmpp.assessor_agent_errorconf = False
        Config = ConfigParser.ConfigParser()
        Config.read(pathfileconf)
        if os.path.exists(pathfileconf + ".local"):
            Config.read(pathfileconf + ".local")
        if Config.has_section("parameters"):
            if Config.has_option("parameters", "showinfomachine"):
                paramshowinfomachine = Config.get('parameters',
                                                  'showinfomachine')
                objectxmpp.assessor_agent_showinfomachine = [str(x.strip()) for x in paramshowinfomachine.split(",") if x.strip() != ""]
            else:
                #default configuration
                objectxmpp.assessor_agent_showinfomachine = []
                logger.warning("showinfomachine default value is []")

            if Config.has_option("parameters", "keyAES32"):

                paramkeyAES32 = Config.get('parameters', 'keyAES32')
                objectxmpp.assessor_agent_keyAES32 = [str(x.strip()) for x in paramkeyAES32.split(",") if x.strip() != ""]

                #objectxmpp.keyAES32 = Config.get('parameters', 'keyAES32')
                if len(objectxmpp.assessor_agent_keyAES32) >0:
                    for keyAES32items in objectxmpp.assessor_agent_keyAES32:
                        if len(keyAES32items) != 32:
                            logger.warning("parameter taille keyAES32 %s"%keyAES32items)
                            objectxmpp.assessor_agent_errorconf = True
            else:
                logger.error("keyAES32 Key AES 32 char [Mandatory parameter keyAES32]")
                objectxmpp.assessor_agent_errorconf = True

            if Config.has_option("parameters", "announce_server"):
                objectxmpp.assessor_agent_announce_server = Config.get('parameters', 'announce_server')
            else:
                objectxmpp.assessor_agent_announce_server = "default"
                logger.warning("announce_server for syncthing default value is default")

            ######################## default connection ##########################
            ### Connection server parameters if no relay server is available ####

            if Config.has_option("parameters", "serverip"):
                objectxmpp.assessor_agent_serverip = ipfromdns(Config.get('parameters',
                                                                       'serverip'))
                if objectxmpp.assessor_agent_serverip == "":
                    logger.error("see parameter [serverip] in file : %s " \
                                "if Connection server parameters " \
                                "if no relay server is available"%pathfileconf)
                    objectxmpp.assessor_agent_errorconf = True
                ipdatadown = ["localhost", "127.0.0.1"]
                for ip in ipdatadown:
                    if objectxmpp.assessor_agent_serverip == ip:
                        logger.error("see parameter [serverip] in file : %s " \
                                "if Connection server parameters " \
                                "if no relay server is available"%pathfileconf)
                        logging.getLogger().error('parameter section "parameters" ' \
                                                  'serverip must not be %s'%ip)
                        objectxmpp.assessor_agent_errorconf  = True
            else:
                logger.error("see parameter [serverip] " \
                             "missing in file : %s " %pathfileconf)
                objectxmpp.assessor_agent_errorconf  = True

            if Config.has_option("parameters", "port"):
                objectxmpp.assessor_agent_port = Config.get('parameters', 'port')
                if objectxmpp.assessor_agent_port == "":
                    logger.error("see parameter [port] in file : %s " \
                                "if Connection server parameters " \
                                "if no relay server is available"%pathfileconf)
                    objectxmpp.assessor_agent_errorconf  = True
            else:
                logger.error("default value parameter [port] 5222")
                objectxmpp.assessor_agent_port == "5222"

            if Config.has_option("parameters", "guacamole_baseurl"):
                objectxmpp.assessor_agent_baseurlguacamole = Config.get('parameters', 'guacamole_baseurl')
                if objectxmpp.assessor_agent_port == "":
                    logger.error("see parameter [guacamole_baseurl] in file : %s " \
                                "if Connection server parameters " \
                                "if no relay server is available"%pathfileconf)
                    objectxmpp.assessor_agent_errorconf  = True
            else:
                logger.error("see parameter [guacamole_baseurl] " \
                             "missing in file : %s " %pathfileconf)
                objectxmpp.assessor_agent_errorconf  = True

        else:
            logger.error("see SECTION [parameters] mising in file : %s "%pathfileconf)
            objectxmpp.assessor_agent_errorconf  = True
        if objectxmpp.assessor_agent_errorconf:
            message_config(plugin['NAME'], pathfileconf)
            return False
    return True

def message_config(nameplugin, pathfileconf):
    msg ="""=========configuration assessor plugin master==========="
        check MASTER assessor plugin config file "%s"

        The following parameters must be defined:

        serverip : IP of default ARS (or its FQDN if it can be resolved by the clients)
        port : Port of default ARS
        guacamole_baseurl : Guacamole base url of default ARS
        announce_server : Syncthing announce server url of default ARS
        showinfomachine : list of names of the machines whose information we want displayed
        keyAES32 : List of AES keys for checking the agent"""%pathfileconf
    logger.error("%s"%msg)
    logger.error("For the [%s] plugin, it is mandatory " \
                 "to define the following parameters."%(nameplugin))
    logger.error("in files [%s] and file [%s.local]"%(pathfileconf, pathfileconf))
    logger.error("# Connection server parameters if no relay server is available")
    logger.error("[parameters]")
    logger.error("# XMPP server")
    logger.error("serverip = 192.168.56.2 #Mandatory parameter")
    logger.error("# XMPP port")
    logger.error("port = 5222 #Mandatory parameter")
    logger.error("# XMPP password")
    logger.error("password = secret #Mandatory parameter")
    logger.error("# The location of the guacamole server.")
    logger.error("guacamole_baseurl = http://192.168.56.2/guacamole/ #Mandatory parameter")
    logger.error("#for syncthing")
    logger.error("announce_server = https://192.168.56.2:8443/?id=IGQIW2T"\
                 "-OHEFK3P-JHSB6KH-OHHYABS-YEWJRVC-M6F4NLZ-D6U55ES-VXIVMA3")
    logger.error("#for authentification key AES 32 chars")
    logger.error("keyAES32 = abcdefghijklnmopqrstuvwxyz012345")
    logger.error("showinfomachine = infra_jfk_deb1, infra_jfk_deb2")

def displayData(objectxmpp, data):
    if data['machine'].split(".")[0] in objectxmpp.assessor_agent_showinfomachine:
        logger.info("--------------------------")
        if 'action' in data and data['action'] == 'assessor_agent':
            logger.info("** INFORMATION FROM CONFIGURATION AGENT FOR %s" %
                        data['agenttype'].upper())
        else:
            logger.info("** INFORMATION FROM AGENT %s %s" % (data['agenttype'].upper(),
                                                                data['action']))
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

        logger.info("DETAILED INFORMATION")
        if 'information' in data:
            logger.info("%s" % json.dumps(data['information'], indent=4, sort_keys=True))
