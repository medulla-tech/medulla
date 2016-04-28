#!/usr/bin/env python
# -*- coding: utf-8; -*-
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

import sys, os

import ConfigParser
import sleekxmpp
import netifaces
import random
import base64
import json
from optparse import OptionParser
import copy
from sleekxmpp.exceptions import IqError, IqTimeout
#from lib.network import networkagent
from lib.networkinfo import networkagentinfo
#from lib.configuration import parametreconf
from lib.utils import *
import plugins
from mmc.plugins.xmppmaster.config import xmppMasterConfig
from mmc.plugins.base import getModList
from mmc.plugins.base.computers import ComputerManager
# Database
from pulse2.database.xmppmaster import XmppMasterDatabase
import lib
from lib.localisation import Localisation


global xmpp

##import mysql.connector
##from mysql.connector import errorcode

#addition chemin pour library and plugins
pathbase = os.path.abspath(os.curdir)
pathplugins = os.path.join(pathbase, "plugins")
pathlib     = os.path.join(pathbase, "lib")
pathseelfplugins = os.path.join(pathbase, "pluginmaster")

sys.path.append(pathplugins)
sys.path.append(pathlib)
sys.path.append(pathseelfplugins)
import pluginmaster
import logging

logger = logging.getLogger()

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

class MUCBot(sleekxmpp.ClientXMPP):
    def __init__(self, conf):#jid, password, room, nick):
        self.config = conf
        self.plugintype = {}
        self.plugindata = {}
        self.loadpluginlist()
        sleekxmpp.ClientXMPP.__init__(self,  conf.jidagent, conf.passwordconnection)
        print conf.jidagent
        print conf.passwordconnection
        XmppMasterDatabase().clearMachine()

        self.idm = ""
        self.presencedeploiement = {}
        self.updateguacamoleconfig = {}
        self.xmpppresence={}
 
        # reload plugins list all 15 minutes
        self.schedule('update plugin', 900 , self.loadpluginlist, repeat=True)

        #update configure distante guacamole time all les 6 minutes 
        self.schedule('surveille reseau', 60 ,self.updateGuacamoleConfigRelaisServer , repeat=True)

        self.add_event_handler("session_start", self.start)
        """ nouvelle presense dans salon Master """
        self.add_event_handler("muc::%s::presence" % conf.jidsalonmaster,
                               self.muc_presenceMaster)
        """ desincription presense dans salon Master """
        self.add_event_handler("muc::%s::got_offline" % conf.jidsalonmaster,
                               self.muc_offlineMaster)
        """ inscription presense dans salon Master """
        self.add_event_handler("muc::%s::got_online" % conf.jidsalonmaster,
                               self.muc_onlineMaster)
        """ nouvelle presense dans salon Master """
        self.add_event_handler("muc::%s::presence" % conf.confjidsalon,
                               self.muc_presenceConf)
        """ desincription presense dans salon Master """
        self.add_event_handler("muc::%s::got_offline" % conf.confjidsalon,
                               self.muc_offlineConf)
        """ inscription presense dans salon Master """
        self.add_event_handler("muc::%s::got_online" % conf.confjidsalon,
                               self.muc_onlineConf)
        #fonction appeler pour tous message
        self.add_event_handler('message', self.message)
        # L'événement groupchat_message est déclenchée chaque fois qu'un message
        # Strophe est reçu de toute salle de chat. Si vous aussi vous aussi
        # Enregistrer un gestionnaire pour le 'message' événement, les messages MUC
        # Sera traitée par les deux gestionnaires.
        self.add_event_handler("groupchat_message", self.muc_message)

    def affichedata(self,data):
        if self.config.showinfomaster:
            logger.info("__________________________")
            logger.info("INFORMATION MACHINE")
            logger.info("deploie name : %s"%data['deploiement'])
            logger.info("from : %s"%data['who'])
            logger.info("Jid from : %s"%data['from'])
            logger.info("Machine : %s"%data['machine'])
            logger.info("plateforme : %s"%data['plateforme'])
            logger.info("--------------------------------")
            logger.info("----XMPP INFORMATION MACHINE----")
            logger.info("portxmpp : %s"%data['portxmpp'])
            logger.info("serverxmpp : %s"%data['serverxmpp'])
            logger.info("xmppip : %s"%data['xmppip'])
            logger.info("agenttype : %s"%data['agenttype'])
            logger.info("baseurlguacamole : %s"%data['baseurlguacamole'])
            logger.info("xmppmask : %s"%data['xmppmask'])
            logger.info("subnetxmpp : %s"%data['subnetxmpp'])
            logger.info("xmppbroadcast : %s"%data['xmppbroadcast'])
            logger.info("xmppdhcp : %s"%data['xmppdhcp'])
            logger.info("xmppdhcpserver : %s"%data['xmppdhcpserver'])
            logger.info("xmppgateway : %s"%data['xmppgateway'])
            logger.info("xmppmacaddress : %s"%data['xmppmacaddress'])
            logger.info("xmppmacnonreduite : %s"%data['xmppmacnonreduite'])
            logger.info("classutil : %s"%data['classutil'])
            logger.info("ippublic : %s"%data['ippublic'])
            logger.info("------------LOCALISATION-----------")
            logger.info("localisationifo : %s"%self.localisationifo)
            logger.info("-----------------------------------")
            logger.info("DETAIL INFORMATIONS")
            logger.info("%s"% json.dumps(data['information'], indent=4, sort_keys=True))

    def loadpluginlist(self):
        logger.debug(  "verify base plugin")
        plugindataseach={}
        plugintype={}
        for element in os.listdir(self.config.dirplugins):
            if element.endswith('.py') and element.startswith('plugin_'):
                f = open(os.path.join(self.config.dirplugins,element),'r')
                lignes  = f.readlines()
                f.close() 
                for ligne in lignes:
                    if 'VERSION' in ligne and 'NAME' in ligne:
                        l=ligne.split("=")
                        plugin = eval(l[1])
                        plugindataseach[plugin['NAME']]=plugin['VERSION']
                        try:
                            plugintype[plugin['NAME']]=plugin['TYPE']
                        except:
                            plugintype[plugin['NAME']]="machine"
                        break;
        self.plugindata = plugindataseach
        self.plugintype = plugintype
        print self.plugindata
        print self.plugintype
                #module = __import__(element[:-3]).plugin
                #dataobj['plugin'][module['NAME']] = module['VERSION']

    def loginformation(self,msgdata):
        self.send_message( mbody = msgdata,
                           mto = self.config.jidsalonlog,
                           mtype ='groupchat')   

    def start(self, event):
        self.get_roster()
        self.send_presence()
        #join salon Master
        print "join salon Muc "
        print "%s %s %s"%(self.config.jidsalonmaster,self.config.NickName,self.config.passwordconnexionmuc)
        salonjoin=[self.config.jidsalonmaster,self.config.jidsalonlog,self.config.confjidsalon]
        for salon in salonjoin:
            if salon == self.config.confjidsalon:
                passwordsalon = self.config.confpasswordmuc
            else:
                passwordsalon = self.config.passwordconnexionmuc
            self.plugin['xep_0045'].joinMUC(salon,
                                            self.config.NickName,
                                            # If a room password is needed, use:
                                            password=passwordsalon,
                                            wait=True)

    def register(self, iq):
        """ cette fonction est appelee pour la registration automatique""" 
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        try:
            resp.send(now=True)
            logger.info("Account created for %s!" % self.boundjid)
        except IqError as e:
            logger.error("Could not register account: %s" %
                    e.iq['error']['text'])
            #self.disconnect()
        except IqTimeout:
            logger.error("No response from server.")
            self.disconnect()

    def message(self, msg):
        ### mettre en base
        pass

    def showListClient(self):
        depl={}
        l = self.presencedeploiement.keys()
        for t in l:
            depl[self.presencedeploiement[t]['deploiement']]=[self.presencedeploiement[t]['deploiement']]
        if len(l) != 0:
            logger.info(  "liste machines participante Deploiement")
            for k in depl.keys():
                logger.info(  "Déploiement sur [%s]"%k)
                logger.info('{0:30}|{1:35}|{2:55}|{3:15}'.format("Machine","jid","plateforme", "type"))
                for t in l:
                    if self.presencedeploiement[t]['deploiement'] == k:
                        jidbarre=self.presencedeploiement[t]['fromjid'].split('/')
                        logger.info( '{0:30}|{1:35}|{2:55}|{3:15}'.format(self.presencedeploiement[t]['machine'][:-3],
                                                            jidbarre[0],
                                                            self.presencedeploiement[t]['plateforme'] ,self.presencedeploiement[t]['agenttype']))
        else:
            #if self.config.showinfomaster:
            logger.info(  "AUCUNE MACHINE")

    def restartagent(self , to ):
        if self.config.showplugins:
            logger.info("restart agent on %s"%(to))
        self.send_message(mto=to,
            mbody=json.dumps({'action':'restartbot','data':''}),
            mtype='groupchat')

    def deploiePlugin(self, msg, plugin):
        data =''
        fichierdata={}
        namefile =  os.path.join(self.config.dirplugins,"plugin_%s.py"%plugin)
        #print namefile
        #print self.config.dirplugins
        if os.path.isfile(namefile) :
            logger.debug("file plugin find %s"%namefile)
        else:
            logger.err("file plugin find %s"%namefile)
            return
        try:
            fileplugin = open(namefile, "rb")
            data=fileplugin.read()
            fileplugin.close()
        except :
            logger.err(  "erreur lecture fichier")
            return
        #if len(data)!=0:
        fichierdata['action'] = 'installplugin'
        fichierdata['data'] ={}
        dd={}
        dd['datafile']= data
        dd['pluginname'] = "plugin_%s.py"%plugin
        fichierdata['data']= base64.b64encode(json.dumps(dd))
        fichierdata['sessionid'] = "sans"
        fichierdata['base64'] = True
        #print fichierdata
        #print msg['from']
        self.send_message(mto=msg['from'],
                          mbody=json.dumps(fichierdata),
                          mtype='groupchat')

    def callInstallConfGuacamole(self, toserverrelais, data):
        resultcommand={'action' : 'serverrelais',
                       'sessionid': name_random(5, "serverrelais"),
                       'data' : data }
        self.send_message(mto = toserverrelais,
                            mbody=json.dumps(resultcommand),
                            mtype='groupchat')

    def MessagesAgentFromSalonConfig(self, msg):
        ### message from salon master
        if msg['from'].bare == self.config.confjidsalon:
            return
        if msg['type'] != "groupchat" or \
            msg['body'] == "This room is not anonymous" or not \
                self.plugin['xep_0045'].jidInRoom( self.config.confjidsalon, msg['from']):
            return
        try:
            data = json.loads(msg['body'])
            #verify msg from salonxmpp mater pour subcription
            if data['action'] == 'connectionconf' :
                """ verify information machine depuis agent siveo """
                info = json.loads(base64.b64decode(data['completedatamachine']))
                data['information'] = info
                if data['ippublic'] != None:
                    self.localisationifo = Localisation().geodataip(data['ippublic'])
                else:
                    self.localisationifo = {}
                self.affichedata(data)
        except:
            pass
        if data['agenttype'] == "serverrelais":
            return

        XmppMasterDatabase().log("Search Server Relais for Connection user %s hostname %s localisation %s"%(data['information']['users'][0],data['information']['info']['hostname'],self.localisationifo))
        #determination serverrelais pour connexion
        # ordre des regles a appliquer
        ordre =  XmppMasterDatabase().Orderregles()
        result = []
        for x in ordre:
            if x[0] == 1:
                result1= XmppMasterDatabase().algoregleuser(data['information']['users'][0])
                if len(result1) > 0 :
                    result= XmppMasterDatabase().IpAndPortConnectionFromServerRelais(result1[0].id)[0]
                    logger.debug("regle user select serverrelais for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    break
            elif x[0] == 2:
                result1= XmppMasterDatabase().algoreglehostname(data['information']['info']['hostname'])
                if len(result1) > 0 :
                    result= XmppMasterDatabase().IpAndPortConnectionFromServerRelais(result1[0].id)[0]
                    logger.debug("regle hostname select serverrelais for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    break
            elif x[0] == 3:
                result1= XmppMasterDatabase().algoreglesubnet(data['subnetxmpp'],data['classutil'])
                if len(result1) > 0 :
                    result= XmppMasterDatabase().IpAndPortConnectionFromServerRelais(result1[0].id)[0]
                    logger.debug("regle subnet select serverrelais for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    break
            elif x[0] == 4:
                result = [self.config.defaultserverrelaisip,self.config.defaultserverrelaisport]
                logger.debug("regle default select serverrelais for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                break
            elif x[0] == 5:
                distance = 40000000000
                relaisserver = -1
                if self.localisationifo != None and self.localisationifo['longitude']!="" and self.localisationifo['latitude']!="":
                    result1 = XmppMasterDatabase().IdlonglatServerRelais(data['classutil'])
                    for x in result1:
                        if x[1]!="" and x[2]!="":
                            re = Localisation().determinationbylongitudeandip(float(x[2]),float( x[1]) , data['ippublic'])
                            if re < distance:
                                distance = re
                                relaisserver = x[0]
                                break
                    if relaisserver != -1:
                        result= XmppMasterDatabase().IpAndPortConnectionFromServerRelais(relaisserver)
                        logger.debug("regle geoposition select serverrelais for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                        break
        logger.debug("server connection select by regle by user %s and hostname %s [connection ip %s port : %s]"%(data['information']['users'][0],data['information']['info']['hostname'],result[0][0],result[0][1]))
        XmppMasterDatabase().log("[user %s hostanme %s] : Server Relais for Connection ip %s port %s"%(data['information']['users'][0],data['information']['info']['hostname'],result[0][0],result[0][1] ))
        reponse = {
            'action' : 'resultconnectionconf', 
            'sessionid' : data['sessionid'],
            'data' : [result[0][0],result[0][1]],
            'ret': 0
            }
        self.send_message(mto=msg['from'],
                        mbody=json.dumps(reponse),
                        mtype='groupchat')


    def MessagesAgentFromSalonMaster(self, msg):
        ### message from salon master
        ## remark groupchat pour message prive est pas strictement conforme a xmpp
        ### ejabbert achemine le message.
        if msg['from'].bare == self.config.jidsalonmaster:
            """ message tous les menbres de salon master"""
            return
        if msg['type'] != "groupchat" :
            return
        #print msg['body']
        if  msg['body'] == "This room is not anonymous":
            return
        if not self.plugin['xep_0045'].jidInRoom( self.config.jidsalonmaster, msg['from']):
            """ message agent apppartenant à master """
            return
        restartagent = False
        try:
            data = json.loads(msg['body'])
            #verify msg from salonxmpp mater pour subcription
            if data['action'] == 'infomachine' :
                """ verify information machine depuis agent siveo """
                info = json.loads(base64.b64decode(data['completedatamachine']))
                if data['ippublic'] != None:
                    self.localisationifo = Localisation().geodataip(data['ippublic'])
                else:
                    self.localisationifo = {}
                self.presencedeploiement[data['machine']]={
                    'machine':data['machine'],
                    'fromsalon':data['who'],
                    'fromjid': data['from'],
                    'deploiement':data['deploiement'],
                    'plateforme':data['plateforme'],
                    'information':info,
                    'portxmpp':data['portxmpp'],
                    'serverxmpp':data['serverxmpp'],
                    'xmppip' : data['xmppip'],
                    'subnetxmpp' : data['subnetxmpp'],
                    'xmppmask' : data['xmppmask'],
                    'xmppmacaddress' : data['xmppmacaddress'],
                    'baseurlguacamole' : data['baseurlguacamole'],
                    'agenttype' : data['agenttype'],
                    'localisationifo' : self.localisationifo
                    }

                data['information'] = info
                self.affichedata(data)
                longitude = ""
                latitude = ""
                city = ""
                region_name = ""
                time_zone = ""
                longitude = ""
                latitude = ""
                postal_code = ""
                country_code = ""
                country_name = ""
                if self.localisationifo != None:
                    longitude = str(self.localisationifo['longitude'])
                    latitude  = str(self.localisationifo['latitude'])
                    region_name = str(self.localisationifo['region_name'])
                    time_zone = str(self.localisationifo['time_zone'])
                    postal_code = str(self.localisationifo['postal_code'])
                    country_code = str(self.localisationifo['country_code'])
                    country_name = str(self.localisationifo['country_name'])
                    city = str(self.localisationifo['city'])

                logger.info("---------------------adduser")
                print data['information']['users'][0]
                print data['information']['info']['hostname']
                print "add user"
                useradd = XmppMasterDatabase().adduser(   data['information']['users'][0],
                                                data['information']['info']['hostname'] ,
                                                city,
                                                region_name ,
                                                time_zone ,
                                                longitude,
                                                latitude ,
                                                postal_code ,
                                                country_code,
                                                country_name )
                useradd = useradd[0]

                #add relaisserver ou update status in base
                if data['agenttype'] == "relaisserver":
                    print "add addServerRelais"
                    XmppMasterDatabase().addServerRelais(data['baseurlguacamole'],
                                                            data['subnetxmpp'], 
                                                            data['information']['info']['hostname'],#data['machine'][:-3], 
                                                            data['xmppip'],
                                                            data['portxmpp'],
                                                            data['xmppmask'],
                                                            data['from'],
                                                            longitude,
                                                            latitude,
                                                            True,
                                                            data['classutil']
                                                            )
                #add machine
                #todo
                #classutil = Column(String(20))
                idmachine = XmppMasterDatabase().addPresenceMachine(data['from'],
                                                            data['plateforme'], 
                                                            data['information']['info']['hostname'], 
                                                            data['information']['info']['hardtype'], 
                                                            None,
                                                            data['xmppip'],
                                                            data['subnetxmpp'],
                                                            data['xmppmacaddress'],
                                                            data['agenttype'],
                                                            data['classutil']
                                                            )
                if idmachine != -1:
                    if useradd != -1:
                        print "OOOOOOOOOOOOOOO hasmachineusers %s %s"%(useradd,idmachine)
                        XmppMasterDatabase().hasmachineusers(useradd, idmachine)

                    logging.debug("addPresenceNetwork pour machine  %d"%idmachine)
                    for i in data['information']["listipinfo"]:
                        try:
                            broadcast = i['broadcast']
                        except:
                            broadcast=''
                        XmppMasterDatabase().addPresenceNetwork( i['macaddress'],i['ipaddress'], broadcast, i['gateway'], i['mask'],i['macnonreduite'], idmachine)

                    # update uuid machine pour coherence avec inventory  
                    result = XmppMasterDatabase().listMacAdressforMachine(idmachine)

                    results = result[0].split(",")
                    logging.getLogger().debug("listMacAdressforMachine   %s"%results)
                    uuid =''
                    for t in results:
                        computer = ComputerManager().getComputerByMac(t)
                        if computer != None:
                            uuid = 'UUID' + str(computer.id)
                            logging.getLogger().debug("uuid   %s"%uuid)
                            XmppMasterDatabase().updateMachineidinventory(uuid, idmachine)
                            break
                        else:
                            print "None"
                        logging.getLogger().debug("*****************")

                #afffiche information plugins dans les logs
                if self.config.showplugins:
                    logger.info("___________________________")
                    logger.info("LIST PLUGINS INSTALLED AGENT")
                    logger.info("%s"% json.dumps(data['plugin'], indent=4, sort_keys=True))
                    logger.info("__________________________________________")
                restartagent = False
                if self.config.showplugins:
                    logger.info("_____________Deploy plugin_________________")
                for k,v in self.plugindata.iteritems():
                    deploie = False
                    try:
                        #check version
                        if data['plugin'][k] != v:
                            logger.info("update %s version %s to version %s"%(k,data['plugin'][k],v))
                            deploie = True
                    except:
                        deploie = True
                    if data['agenttype'] != "all":
                        if data['agenttype'] == "serverdata" and  self.plugintype[k] == 'machine':
                            deploie = False
                        if data['agenttype'] == "machine" and  self.plugintype[k] == 'serverdata':
                            deploie = False

                    if deploie:
                        if self.config.showplugins:
                            logger.info("deploie %s version %s on %s"%(k,v,msg['from']))
                        self.deploiePlugin(msg,k)
                        self.restartagent(msg['from'])
                if self.config.showplugins:
                    logger.info("__________________________________________")
                self.showListClient()
                # indique que la configurations guacamole doit etre faite pour sous reseau subnetxmpp
                self.updateguacamoleconfig[data['subnetxmpp']] = True
                # placer ici pour test sans attendre
                #self.updateGuacamoleConfigRelaisServer()
            elif data['action'] == 'participant':
                resultcommand={'action' : 'participant',
                                'participant' : self.presencedeploiement }
                self.send_message(mto=msg['from'],
                        mbody=json.dumps(resultcommand),
                        mtype='groupchat')
            elif data['action'] == 'listparticipant':
                resultcommand={'action' : 'listparticipant',
                                'participant' : self.presencedeploiement }
                self.send_message(mto=msg['from'],
                        mbody=json.dumps(resultcommand),
                        mtype='groupchat')
        except:
            pass


    def muc_message(self, msg):
        """
        fonction traitant tous messages venant d un salon
        attribut type pour selection
        """
        self.MessagesAgentFromSalonMaster( msg)
        self.MessagesAgentFromSalonConfig( msg)
        #call_pluginrecv('test', self, msg)

    def updateGuacamoleConfigRelaisServer(self):
        dataguacamoleconf = {}
        datalocationserverguacamoleconf = {}
        controle="relaisserver"
        for machine, data in self.presencedeploiement.iteritems():
            if self.updateguacamoleconfig.has_key(self.presencedeploiement[machine]['subnetxmpp']) and \
            self.updateguacamoleconfig[self.presencedeploiement[machine]['subnetxmpp']] == True:
                data1 = copy.deepcopy(data)
                data1['hostname'] = data['information']['info']['hostname']
                data1['os'] = data['information']['info']['os']
                del data1['information']['listipinfo']
                if  self.presencedeploiement[machine]['agenttype'] == "machine":
                    if not dataguacamoleconf.has_key(self.presencedeploiement[machine]['subnetxmpp']):
                        dataguacamoleconf[self.presencedeploiement[machine]['subnetxmpp']] = []
                    dataguacamoleconf[self.presencedeploiement[machine]['subnetxmpp']].append(data1)
                elif self.presencedeploiement[machine]['agenttype'] == "relaisserver":
                    datalocationserverguacamoleconf[self.presencedeploiement[machine]['subnetxmpp']] = data1

        for e, v in datalocationserverguacamoleconf.iteritems():
            if dataguacamoleconf.has_key(e) and v.has_key('fromjid'):
                try:
                    print "install configuration"
                    self.callInstallConfGuacamole(v['fromjid'],dataguacamoleconf[e]) 
                    self.updateguacamoleconfig[e] = False
                except:
                    pass

    def muc_offlineMaster(self, presence):
        if presence['muc']['nick'] != self.config.NickName and presence['muc']['nick'] != "SIVEO":
            if self.config.showinfomaster:
                logger.debug("deconnexion %s"% presence['muc']['nick'])
            try:
                del self.presencedeploiement[presence['muc']['nick']]
                result = XmppMasterDatabase().delPresenceMachine( presence['muc']['jid'])
                ##/etc/guacamole/noauth-config.xml
            except:
                pass
            self.showListClient()

    def muc_presenceMaster(self, presence):
        #print "muc_presenceMaster"
        if presence['muc']['nick'] != self.config.NickName:
            if self.config.showinfomaster:
                logger.debug(  "presence %s"%presence['muc']['nick'])

    def muc_onlineMaster(self, presence):
        if presence['muc']['nick'] != self.config.NickName:
            pass

    #traitement presence salon configuration dynamique
    def muc_presenceConf(self, presence):
        print presence
        pass
    def muc_offlineConf(self, presence):
        print presence
        pass
    def muc_onlineConf(self, presence):
        print presence
        pass

#todo faire class 
def stopxmpp():
    global xmpp
    xmpp.disconnect()

def doTask():
    global xmpp
    tg=xmppMasterConfig()

    if tg.debugmode == "NOTSET":
        tg.debugmode = 0
    elif tg.debugmode == "DEBUG":
        tg.debugmode = 10
    elif tg.debugmode == "INFO":
        tg.debugmode = 20
    if tg.debugmode == "LOG" or tg.debugmode == "DEBUGPULSE":
        tg.debugmode = 25
    elif tg.debugmode == "WARNING":
        tg.debugmode = 30
    elif tg.debugmode == "ERROR":
        tg.debugmode = 40
    elif tg.debugmode == "CRITICAL":
        tg.debugmode = 50
    #logging.basicConfig(level=tg.debugmode,
                        #format='[MASTER] %(levelname)-8s %(message)s')
    logging.basicConfig(level=tg.debugmode,
            format='[%(name)s.%(funcName)s:%(lineno)d] %(message)s')
    #logging.log(tg.debugmode,"=======================================test log")
    xmpp = MUCBot(tg)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0050') # Adhoc Commands
    xmpp.register_plugin('xep_0199', {'keepalive': True, 'frequency':15})
    xmpp.register_plugin('xep_0077') # In-band Registration
    xmpp['xep_0077'].force_registration = False
    xmpp.register_plugin('xep_0279')
    if xmpp.connect(address=(tg.Server,tg.Port)):
        xmpp.process(block=True)
        logger.info("done")
    else:
        logger.info("Unable to connect.")
