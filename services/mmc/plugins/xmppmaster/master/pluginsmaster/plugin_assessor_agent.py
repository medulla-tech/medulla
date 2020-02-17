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
from utils import AESCipher, subnetnetwork
import logging
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
from random import randint
from localisation import Localisation
import operator
import netaddr
from manageADorganization import manage_fqdn_window_activedirectory

logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "assessor_agent", "TYPE": "master"}


def action(objectxmpp, action, sessionid, data, msg, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug("call %s from %s"%(plugin, msg['from']))
    logger.debug("=====================================================")
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
    keyAES32 = [str(x.strip()) for x in objectxmpp.config.keyAES32.split(",") if x.strip() != ""]
    for t in keyAES32:
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
    objectxmpp.displayData(data)

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
                            objectxmpp.config.defaultrelayserverip)
            result = XmppMasterDatabase().jidrelayserverforip(objectxmpp.config.defaultrelayserverip)
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
            result = XmppMasterDatabase().jidrelayserverforip(objectxmpp.config.defaultrelayserverip)
        except Exception:
            logger.warn("Unable to configure the relay server : missing")
            result = [objectxmpp.config.defaultrelayserverip,
                        objectxmpp.config.defaultrelayserverport,
                        objectxmpp.domaindefault,
                        objectxmpp.config.defaultrelayserverbaseurlguacamole]
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
                    'syncthing' : objectxmpp.config.announce_server,
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
            reponse["substitute"] =  XmppMasterDatabase().\
                                    substituteinfo(data["substitute"],
                                                   z1[0][2])

            reponse["substitute"]["ars_chooose_for_substitute"] = z1[0][2]

            logger.debug("substitute resend to agent : %s"%json.dumps(reponse["substitute"],indent=4)) 

            if "subscription" in reponse["substitute"]:
                agentsubscription = reponse["substitute"]['subscription'][0]
                listmacadress=[]
                for mac in data['information']['listipinfo']:
                    listmacadress.append(mac['macaddress'])
                XmppMasterDatabase().setuplistSubscription(listmacadress, agentsubscription)
        objectxmpp.send_message(mto=msg['from'],
                            mbody=json.dumps(reponse),
                            mtype='chat')
        #add account for delete
        #list des comptes a suprimer
        objectxmpp.confaccount.append(msg['from'].user)
    except Exception:
        sendErrorConnectionConf(objectxmpp,sessionid,msg)
        logger.error("Unable to configure agent for one relay server")
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

