#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


global xmpp

##import mysql.connector
##from mysql.connector import errorcode

#addition chemin pour library and plugins
pathbase = os.path.abspath(os.curdir)
pathplugins = os.path.join(pathbase, "plugins")
pathlib     = os.path.join(pathbase, "lib")
sys.path.append(pathplugins)
sys.path.append(pathlib)

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
        #fonction appeler pour tous message
        self.add_event_handler('message', self.message)
        # L'événement groupchat_message est déclenchée chaque fois qu'un message
        # Strophe est reçu de toute salle de chat. Si vous aussi vous aussi
        # Enregistrer un gestionnaire pour le 'message' événement, les messages MUC
        # Sera traitée par les deux gestionnaires.
        self.add_event_handler("groupchat_message", self.muc_message)

#self.xmpp.register_handler(Callback('MUCMessage', MatchXMLMask("<message xmlns='%s' type='groupchat'><body/></message>" % self.xmpp.default_ns), self.handle_groupchat_message))
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
        self.plugin['xep_0045'].joinMUC(self.config.jidsalonmaster,
                                        self.config.NickName,
                                        # If a room password is needed, use:
                                        password=self.config.passwordconnexionmuc,
                                        wait=True)
        #join salon log
        print "join salon Muc "
        print "%s %s %s"%(self.config.jidsalonlog,self.config.NickName,self.config.passwordconnexionmuc)
        self.plugin['xep_0045'].joinMUC(self.config.jidsalonlog,
                                        self.config.NickName,
                                        # If a room password is needed, use:
                                        password=self.config.passwordconnexionmuc,
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
        print msg
        data =''
        fichierdata={}
        namefile =  os.path.join(self.config.dirplugins,"plugin_%s.py"%plugin)
        print namefile
        print self.config.dirplugins
        if os.path.isfile(namefile) :
            print "file exist"
        else:
            print "file no exist"
        try:
            fileplugin = open(namefile, "rb")
            data=fileplugin.read()
            fileplugin.close()
            print data
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
                       'sessionid': 'dede',
                       'data' : data }
        self.send_message(mto = toserverrelais,
                            mbody=json.dumps(resultcommand),
                            mtype='groupchat')

    def muc_message(self, msg):
        """
        fonction traitant tous messages venant d un salon
        attribut type pour selection
        """
        ## print self.plugin['xep_0279'].check_ip(msg['from'])
        restartagent = False
        if msg['from'].bare == self.config.jidsalonlog:
            return

        if msg['type'] == "groupchat":
            if msg['body'] == "This room is not anonymous":
                return
            try:
                data = json.loads(msg['body'])
                #verify msg from salonxmpp mater pour subcription
                if data['action'] == 'infomachine' and \
                    self.plugin['xep_0045'].jidInRoom( self.config.jidsalonmaster,msg['from']):
                    """ verify information machine depuis agent siveo """
                    info = json.loads(base64.b64decode(data['completedatamachine']))
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
                        }

                    data['information'] = info
                    if self.config.showinfomaster:
                        logger.info("__________________________")
                        logger.info("INFORMATION MACHINE")
                        logger.info("deploie name : %s"%data['deploiement'])
                        logger.info("from : %s"%data['who'])
                        logger.info("Jid from : %s"%data['from'])
                        logger.info("Machine : %s"%data['machine'])
                        logger.info("plateforme : %s"%data['plateforme'])
                        logger.info("----------------------------")
                        logger.info("XMPP INFORMATION MACHINE")
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
                        logger.info("----------------------------")
                        logger.info("DETAIL INFORMATIONS")
                        logger.info("%s"% json.dumps(data['information'], indent=4, sort_keys=True))
                    #traitement reserve pour machine relais server
                    if data['agenttype'] == "relaisserver":
                        XmppMasterDatabase().addServerRelais(data['baseurlguacamole'],
                                                             data['subnetxmpp'], 
                                                             data['machine'][:-3], 
                                                             data['xmppip'], 
                                                             data['xmppmask'],
                                                             data['from'])
                    #add machine 
                    idmachine = XmppMasterDatabase().addPresenceMachine(data['from'],
                                                                data['plateforme'], 
                                                                data['information']['info']['hostname'], 
                                                                data['information']['info']['hardtype'], 
                                                                None,
                                                                data['xmppip'],
                                                                data['subnetxmpp'],
                                                                data['xmppmacaddress'],
                                                                data['agenttype']
                                                                )
                    if idmachine != -1:
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
                    self.updateguacamoleconfig[data['subnetxmpp']]=True
                    # placer ici pour test sans attendre
                    self.updateGuacamoleConfigRelaisServer()
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

    def updateGuacamoleConfigRelaisServer(self):
        print "updateGuacamoleConfigRelaisServer"
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

    logging.log(tg.debugmode,"=======================================test log")
    #if tg.sgbd:
        #try:
            #tg.conn = mysql.connector.connect(host=tg.host, user=tg.user, password=tg.password, database=tg.database)
            #cursor = tg.conn.cursor()
            #cursor.execute('TRUNCATE machines');cursor.execute('TRUNCATE network');
            #tg.conn.commit()
            #cursor.close()

        #except mysql.connector.Error as err:
            #print str(err)
            #tg.sgbd = False
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
