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
from  sleekxmpp import jid
import netifaces
import random
import base64
import json
from optparse import OptionParser
import copy
from sleekxmpp.exceptions import IqError, IqTimeout
from lib.networkinfo import networkagentinfo
from lib.managesession import sessiondatainfo, session
from lib.utils import *
from lib.managepackage import managepackage
from lib.manage_event import manage_event
from lib.manage_process import mannageprocess
import lib
from lib.localisation import Localisation

from mmc.plugins.xmppmaster.config import xmppMasterConfig
from mmc.plugins.base import getModList
from mmc.plugins.base.computers import ComputerManager
# Database
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
import pprint
import pluginsmaster
import cPickle
import logging
import threading
import time
from time import mktime
from datetime import datetime
from multiprocessing import Process, Queue, TimeoutError
from mmc.agent import PluginManager


sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pluginsmaster"))

logger = logging.getLogger()
xmpp = None

if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input

def ObjectXmpp():
    return PluginManager().getEnabledPlugins()['xmppmaster'].xmppMasterthread().xmpp

#JFK
def configurationxmpp():
    return str(xmppMasterConfig())

#commandprocess (command, to, eventstart="startfichier", event= "transfert1terminer", eventerror='transferterror' )
#envoicommand(self, jid, action , data={}, datasession = None, encodebase64 = False, time = 10, eventthread=None)
#def __init__(self, to, action, data, timeout, precommand, postcommand):


def callxmppfunction(functionname, *args, **kwargs ):
    print "**call function %s %s %s"%(functionname, args, kwargs)
    return getattr(ObjectXmpp(),functionname)( *args, **kwargs)

class xmppcommanddiffered:
    """
    Thread chargé de lance pres command.
    precommand terminer
    envoicommand avec session  self, 
    session terminer lance post command 
    """
    def __init__(self, to, action, data, timeout, precommand, postcommand):
        self.xmpp = ObjectXmpp()
        if self.xmpp != None:
            self.namethread = name_random(5, "thread")
            self.e =  threading.Event()
            self.t = timeout
            self.to = to
            self.action = action
            self.data = data
            self.precommand = precommand
            self.postcommand = postcommand
            self.t2 = threading.Thread( name = self.namethread, target=self.differed)
            #print "start thread ",self.namethread
            self.t2.start()
        else:
            print "xmppcommanddiffered error xmpp no initialise"

    def differed(self):
        """
        Code à exécuter pendant l'exécution du thread.
        """
        #traitement precommand
        self.xmpp = ObjectXmpp()
        if self.precommand != None:
            print "exec command %s"%self.precommand
            a = simplecommandestr(self.precommand)
            ##envoi a log a['result']
            if a['code'] != 0:
                print a['result']
                return
            print a['result']
        # traitement action xmpp
        #command xmpp avec creation session
        #print "execute command xmpp",self.action
        self.sessionid = self.xmpp.envoicommand( self.to, self.action , self.data, datasession = None, encodebase64 = False, time = self.t, eventthread = self.e )

        #traitement post command lorsque xmppaction terminer
        if self.postcommand != None:
            while not self.e.isSet():
                #attend timeout end ou eventthread
                event_is_set = self.e.wait(self.t)
                if event_is_set:
                    #print 'action session %s finish'%self.action
                    #execute sur end session
                    print "execution shell command action terminer"
                    #execute post commande shell
                    b = simplecommandestr(self.postcommand)
                    #envoi b log b['result']
                    print b['result']
                else:
                    #timeout
                    if not self.xmpp.session.isexist(self.sessionid):
                        print 'action session %s finish by timeout'%self.action
                        print "error timeout "
                        break;

#def deploieapplication(self, jidrelais, jidmachine, name, time, encodebase64 = False):
class simplecommandxmpp:
    def __init__(self, to, data, timeout, ok, err):
        #self.xmpp = PluginManager().getEnabledPlugins()['xmppmaster'].xmppMasterthread().xmpp
        self.xmpp = ObjectXmpp()
        self.e =  threading.Event()
        self.result = {}
        self.data = data
        self.t = timeout

        self.session = self.xmpp.session.createsessiondatainfo(data['sessionid'],{}, self.t, self.e)
        self.xmpp.send_message(mto = to,
                        mbody = json.dumps(data),
                        mtype = 'chat')

        self.t2 = threading.Thread(name='block1', 
                      target=self.resultsession)
        self.t2.start()

    def resultsession(self):
        while not self.e.isSet():
            event_is_set = self.e.wait(self.t)
            #print 'event set: %s'% event_is_set
            if event_is_set:
                ok(self.session.datasession['result'])
            else:
                err(self.session.datasession['result'])
                break;

class simplecommandxmpp1:
    """ envoi xmpp 
        run xmpp command with session and timeout
        thread attend timeout end or end session
        return result command
    """
    def __init__(self, to, data, timeout):
        self.xmpp = ObjectXmpp()
        #self.xmpp = PluginManager().getEnabledPlugins()['xmppmaster'].xmppMasterthread().xmpp
        self.e =  threading.Event()
        self.result = {}
        self.data = data
        self.t = timeout
        self.sessionid = data['sessionid']
        self.session = self.xmpp.session.createsessiondatainfo(data['sessionid'],{}, self.t, self.e)
        self.xmpp.send_message( mto = to,
                                mbody = json.dumps(data),
                                mtype = 'chat')
        self.t2 = threading.Thread(name='command',
                      target=self.resultsession)
        self.t2.start()

    def resultsession(self):
        while not self.e.isSet():
            event_is_set = self.e.wait(self.t)
            print 'event est signaler set: %s'% event_is_set
            if event_is_set:
                self.result = self.session.datasession
            else:
                #tineout
                self.result = {u'action': u'resultshellcommand',
                               u'sessionid': self.sessionid,
                               u'base64': False,
                               u'data': {u'msg': "ERROR commande\n timeout %s"%self.t },
                               u'ret': 125}
                break;
        self.xmpp.session.clearnoevent(self.sessionid)
        return self.result


class MUCBot(sleekxmpp.ClientXMPP):
    def __init__(self, conf):#jid, password, room, nick):
        self.config = conf
        self.session = session()
        # les queues. Ces objets sont comme des listes partageables entrent
        # les process command utilise cette queue pour signaler un evenement a magager event.
        self.queue_read_event_from_command = Queue()
        self.eventmanage = manage_event(self.queue_read_event_from_command, self)
        self.mannageprocess = mannageprocess(self.queue_read_event_from_command)

        self.plugintype = {}
        self.plugindata = {}
        self.loadpluginlist()
        sleekxmpp.ClientXMPP.__init__(self,  conf.jidagent, conf.passwordconnection)
        #print conf.jidagent
        #print conf.passwordconnection
        #clear table machine
        XmppMasterDatabase().clearMachine()

        self.idm = ""
        self.presencedeploiement = {}
        self.updateguacamoleconfig = {}
        self.xmpppresence={}

        # decremente session time
        self.schedule('manage session', 15 , self.handlemanagesession, repeat=True)

        # reload plugins list all 15 minutes
        self.schedule('update plugin', 900 , self.loadpluginlist, repeat=True)

        #update configure distante guacamole time all les 6 minutes 
        self.schedule('surveille reseau', 60 ,self.updateGuacamoleConfigRelayServer , repeat=True)

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

        #self.add_event_handler('BYTE_STREAM_SENDING_COMPLETE',
                               #self.finishedsending)
        #self.add_event_handler('BYTE_STREAM_RECEIVING_COMPLETE',
                               #self.finishedreceving)

        #fonction appeler pour tous message
        self.add_event_handler('message', self.message)
        # L'événement groupchat_message est déclenchée chaque fois qu'un message
        # Strophe est reçu de toute salle de chat. Si vous aussi vous aussi
        # Enregistrer un gestionnaire pour le 'message' événement, les messages MUC
        # Sera traitée par les deux gestionnaires.
        self.add_event_handler("groupchat_message", self.muc_message)
        self.add_event_handler("pluginaction", self.pluginaction)


    def applicationdeployment(self, jidrelais, jidmachine, name, time, encodebase64 = False):
        """ lors d'un deploiement 
        1er action synchronise le package name precemmand
        """
        if not managepackage.getversionpackagename(name):
            return False

        #attribut nom au evenement
        dd = name_random(5, "")
        evenementfinish =  "Mastereventfinish_%s"%dd
        evenementstart  =  "Mastereventstart_%s"%dd
        evenementerror  =  "Mastereventerror_%s"%dd
        evenementfinishMachine =  "Machineeventfinish_%s"%dd
        evenementstartMachine  =  "Machineeventstart_%s"%dd
        evenementerrorMachine  =  "Machineeventerror_%s"%dd                        
        #evenementfinish =  name_random(15, "eventfinish_%s"%name)
        #evenementstart  =  name_random(15, "eventstart_%s"%name)
        #evenementerror  =  name_random(15, "eventerror_%s"%name)
        data =  {
                "name" : name,
                "path" : managepackage.getpathpackagename(name),
                "jidrelais": jidrelais,
                "jidmachine" : jidmachine,
                "jidmaster" : self.boundjid.bare,
                "iprelais" :  XmppMasterDatabase().ipfromjid(jidrelais)[0],
                "ipmachine" : XmppMasterDatabase().ipfromjid(jidmachine)[0],
                "ipmaster" : self.config.Server,
                "Dtypequery" : "TQ",
                "Devent" : "STARDEPLOY",
                'RSstartevent' : evenementstart,
                'RSfinishevent' : evenementfinish,
                'RSerrorevent' : evenementerror,
                'Mstartevent' : evenementstartMachine,
                'Mfinishevent' : evenementfinishMachine,
                'Merrorevent' : evenementerrorMachine
        }

        sessionid = self.envoicommand( jidrelais, "applicationdeployment" , data, datasession = None, encodebase64 = False)
        # register les evenements possibles
        self.eventmanage.show_eventloop()
        #command =  "rsync --delete -av %s %s:%s"%(data['path'], data['iprelais'], data['path'])
        command ="ls -al"
        self.mannageprocess.add_processcommand( command ,
                                               sessionid,
                                               False,
                                               self.eventmanage.create_TEVENT(jidrelais,"applicationdeployment",sessionid,evenementfinish ),
                                               self.eventmanage.create_TEVENT(jidrelais, "applicationdeployment", sessionid, evenementerror ))
    def pluginaction(self,rep):
        if 'sessionid' in rep.keys():
            sessiondata = self.session.sessionfromsessiondata(rep['sessionid'])
            if 'shell' in sessiondata.getdatasession().keys() and sessiondata.getdatasession()['shell']:
                #print "ENVOI MESSAGE commandrelay@localhost"
                #print rep
                self.send_message(mto=jid.JID("commandrelay@localhost"),
                                mbody=json.dumps(rep),
                                mtype='chat')
        #else:

        logger.info("log action plugin %s!" % rep)
        pass

        ##self.xmpp.event(FileTransferProtocol.FILE_FINISHED_SENDING, {'sid': sid, 'success':success}) 
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

            if 'ipconnection' in data:
                logger.info("ipconnection : %s"%data['ipconnection'])
            if 'portconnection' in data:
                logger.info("portconnection : %s"%data['portconnection'])
            if 'classutil' in data:
                logger.info("classutil : %s"%data['classutil'])
            if 'ippublic' in data:
                logger.info("ippublic : %s"%data['ippublic'])

            logger.info("------------LOCALISATION-----------")
            logger.info("localisationifo : %s"%self.localisationifo)
            logger.info("-----------------------------------")

            logger.info("DETAIL INFORMATIONS")
            if 'information' in data:
                logger.info("%s"% json.dumps(data['information'], indent=4, sort_keys=True))

    def handlemanagesession(self):
        self.session.decrementesessiondatainfo()
        #print self.session.affiche()

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
        #print self.plugindata
        #print self.plugintype
                #module = __import__(element[:-3]).plugin
                #dataobj['plugin'][module['NAME']] = module['VERSION']

    def loginformation(self,msgdata):
        self.send_message( mbody = msgdata,
                           mto = self.config.jidsalonlog,
                           mtype ='chat')

    def start(self, event):
        self.get_roster()
        self.send_presence()
        #join salon Master
        #print "join salon Muc "
        #print "%s %s %s"%(self.config.jidsalonmaster,self.config.NickName,self.config.passwordconnexionmuc)
        salonjoin=[self.config.jidsalonmaster,self.config.jidsalonlog,self.config.confjidsalon]
        for salon in salonjoin:
            if salon == self.config.confjidsalon:
                passwordsalon = self.config.confpasswordmuc
            else:
                passwordsalon = self.config.passwordconnexionmuc
            #print "kkkkkkkkkkkkkkkk",salon
            self.plugin['xep_0045'].joinMUC(salon,
                                            self.config.NickName,
                                            # If a room password is needed, use:
                                            password=passwordsalon,
                                            wait=True)

        #print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
        #self.envoicommand('dede1@localhost', 'downloadfile' , {'namesource':'/tmp/GeoIP.dat.gz'}, {'whowritefile': '/tmp/GeoIP.dat.gz1'}, False)
        #print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
        ##print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
        #self.envoicommand('dede1@localhost', 'transfertfile' , {'ou': '/tmp/dede.tarcppplcp'}, {'qui':'/tmp/GeoIP.dat.gz'}, False)
        ##print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"


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



    def showListClient(self):
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(self.presencedeploiement)
        depl={}
        l = self.presencedeploiement.keys()
        for t in l:
            depl[self.presencedeploiement[t]['deploiement']] = [self.presencedeploiement[t]['deploiement']]
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
            mtype='chat')

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
            traceback.print_exc(file=sys.stdout)
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
                          mtype='chat')

    def callInstallConfGuacamole(self, torelayserver, data):
        resultcommand={'action' : 'relayserver',
                       'sessionid': name_random(5, "relayserver"),
                       'data' : data }
        self.send_message(mto = torelayserver,
                            mbody=json.dumps(resultcommand),
                            mtype='chat')

    def senderrorconnectionconf(self,msg):
        reponse = {
            'action' : 'resultconnectionconf', 
            'sessionid' : data['sessionid'],
            'data' : [],
            'ret': 255
            }
        self.send_message(mto=msg['from'],
                        mbody=json.dumps(reponse),
                        mtype='chat')

    #jfk
    def MessagesAgentFromSalonlog(self, msg, data):
        """
        traitement des log 
        """
        try:
            print "*********%s [%s]"%( data['data']['msg'] , data['data']['tag'])
            return True
        except Exception as e:
            print "ERROR MessagesAgentFromSalonlog %s"%(str(e))
            traceback.print_exc(file=sys.stdout)
            return False

    def MessagesAgentFromSalonConfig(self, msg):
        print "MessagesAgentFromSalonConfig"
        ### message from salon master
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
            else:
                return
        except:
            return
        if data['agenttype'] == "relayserver":
            self.senderrorconnectionconf(msg)
            return

        logger.debug("Search Server Relay for Connection user %s hostname %s localisation %s"%(data['information']['users'][0],data['information']['info']['hostname'],self.localisationifo))
        XmppMasterDatabase().log("Search Server Relay for Connection user %s hostname %s localisation %s"%(data['information']['users'][0],data['information']['info']['hostname'],self.localisationifo))
        #determination relayserver pour connexion
        # ordre des regles a appliquer
        ordre =  XmppMasterDatabase().Orderregles()
        indetermine = []
        result = []
        for x in ordre:
            if x[0] == 1:
                result1= XmppMasterDatabase().algoregleuser(data['information']['users'][0])
                if len(result1) > 0 :
                    result= XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    logger.debug("regle user select relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    break
            elif x[0] == 2:
                result1= XmppMasterDatabase().algoreglehostname(data['information']['info']['hostname'])
                if len(result1) > 0 :
                    result= XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    logger.debug("regle hostname select relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    break
            elif x[0] == 3:
                result1 = XmppMasterDatabase().algoreglesubnet(data['subnetxmpp'],data['classutil'])
                if len(result1) > 0 :
                    print result1[0]
                    result= XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    logger.debug("regle subnet select relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    break
            elif x[0] == 4:
                if len(indetermine) > 0:
                    result = indetermine
                    logger.warn("server address is made possible among servers (Rule geoPosition)")
                    break;
                result2 = XmppMasterDatabase().jidrelayserverforip(self.config.defaultrelayserverip)
                if len(result)!=0:
                    result = [self.config.defaultrelayserverip,self.config.defaultrelayserverport,result2[0],self.config.defaultrelayserverbaseurlguacamole]
                    ##self.defaultrelayserverjid = self.get('defaultconnection', 'jid')
                    logger.debug("regle default select relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                else:
                    result = [self.config.defaultrelayserverip,self.config.defaultrelayserverport,"",self.config.defaultrelayserverbaseurlguacamole]
                    ##self.defaultrelayserverjid = self.get('defaultconnection', 'jid')
                    logger.warn("regle default select relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    logger.warn("check parameters [defaultconnection] in xmppmaster.ini....")
                break
            elif x[0] == 5:
                distance = 40000000000
                listeserver=[]
                relayserver = -1
                if self.localisationifo != None and self.localisationifo['longitude']!="" and self.localisationifo['latitude']!="":
                    result1 = XmppMasterDatabase().IdlonglatServerRelay(data['classutil'])
                    a=0
                    for x in result1:
                        a=a+1
                        print "roule %d"%a
                        if x[1]!="" and x[2]!="":
                            distancecalculer = Localisation().determinationbylongitudeandip(float(x[2]),float( x[1]) , data['ippublic'])
                            print distancecalculer
                            if distancecalculer <= distance:
                                distance = distancecalculer
                                relayserver = x[0]
                                listeserver.append(x[0])
                    nbserver = len(listeserver)
                    if nbserver > 1 :
                        from random import randint
                        index = randint(0 , nbserver-1)
                        print "randon %s"%index
                        logger.warn("regle geoposition return %d server xmpp possible for machine"\
                            "%s user %s \npossible server xmpp : id list  %s "%(nbserver, data['information']['info']['hostname'],
                             data['information']['users'][0],listeserver))
                        logger.warn("continues for another rule. Random choice only if no other finds ")
                        indetermine =  XmppMasterDatabase().IpAndPortConnectionFromServerRelay(listeserver[index])
                    else:
                        if relayserver != -1:
                            result= XmppMasterDatabase().IpAndPortConnectionFromServerRelay(relayserver)
                            logger.debug("regle geoposition select relayserver for machine %s user %s \n %s "%(data['information']['info']['hostname'],data['information']['users'][0],result))
                            break

        logger.debug(" user %s and hostname %s [connection ip %s port : %s]"%(data['information']['users'][0],data['information']['info']['hostname'],result[0],result[1]))
        XmppMasterDatabase().log("[user %s hostanme %s] : Server Relay for Connection ip %s port %s"%(data['information']['users'][0],data['information']['info']['hostname'],result[0],result[1] ))

        reponse = {
            'action' : 'resultconnectionconf', 
            'sessionid' : data['sessionid'],
            'data' : [result[0],result[1],result[2],result[3]],
            'ret': 0
            }
        self.send_message(mto=msg['from'],
                        mbody=json.dumps(reponse),
                        mtype='chat')

    def messagereturnsession(self, msg):
        data = json.loads(msg['body'])
        try:
            if data['sessionid'].startswith("mcc"):
                sessionmsg = self.session.sessionevent(data['sessionid'])
                if sessionmsg is not None:
                    sessionmsg.setdatasession(  data )
                    sessionmsg.callend()
                    return True
                else:
                    print "pas de session name"
        except KeyError:
            print "except"
            return False
        return False

    def unban(self,room, jid, reason=''):
        resp=self.plugin['xep_0045'].setAffiliation(room, jid, affiliation='none', reason=reason)
        return resp

    def MessagesAgentFromSalonMaster(self, msg):
        ### message from salon master
        ### ejabbert achemine le message.
        if msg['from'].bare == self.config.jidsalonmaster:
            """ message tous les menbres de salon master"""
            return False
        #if msg['type'] != "chat" :
            #return False
        #print msg['body']
        if  msg['body'] == "This room is not anonymous":
            return False
        if not (self.jidInRoom1( self.config.jidsalonmaster, msg['from'] ) or self.jidInRoom1(self.config.jidsalonlog, msg['from'])):
            """ message agent apppartenant à master """
            return False
        restartagent = False
        try:
            data = json.loads(msg['body'])
            #verify msg from salonxmpp mater pour subcription
            #jfk
            if data['action'] == 'loginfos':
                #traitement loginformation
                self.MessagesAgentFromSalonlog(msg,data)
                return True

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
                    'localisationifo' : self.localisationifo,
                    'ipconnection':data['ipconnection'],
                    'portconnection':data['portconnection']
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

                #add relayserver ou update status in base
                if data['agenttype'] == "relayserver":
                    print "add addServerRelay"
                    XmppMasterDatabase().addServerRelay(data['baseurlguacamole'],
                                                            data['subnetxmpp'], 
                                                            data['information']['info']['hostname'],#data['machine'][:-3],
                                                            data['deploiement'],
                                                            data['xmppip'],
                                                            data['ipconnection'],
                                                            data['portconnection'],
                                                            data['portxmpp'],
                                                            data['xmppmask'],
                                                            data['from'],
                                                            longitude,
                                                            latitude,
                                                            True,
                                                            data['classutil'])
                    # creation deployment salon for relayserver
                    print "********************************************creation salon", data['deploiement']
                    self.plugin['xep_0045'].joinMUC(data['deploiement'],
                                                self.config.NickName,
                                                password=self.config.confpasswordmuc,
                                                wait=True)
                    #master exit salon for relayserver 
                    print "********************************************quit  salon", data['deploiement']
                    self.plugin['xep_0045'].leaveMUC( data['deploiement'], "MASTER")
                #add machine
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
                        print "hasmachineusers %s %s"%(useradd,idmachine)
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
                    # print "---------------- plugins master %s %s"%(k,v)
                    deploie = False
                    try:
                        #check version
                        if data['plugin'][k] != v:
                            logger.info("update %s version %s to version %s"%(k,data['plugin'][k],v))
                            deploie = True
                    except:
                        deploie = True
                    if self.plugintype[k] == "relayserver":
                        self.plugintype[k]="relayserver"

                    #print data['agenttype']
                    if data['agenttype'] != "all":
                        if data['agenttype'] == "relayserver" and  self.plugintype[k] == 'machine':
                            deploie = False
                        if data['agenttype'] == "machine" and  self.plugintype[k] == 'relayserver':
                            deploie = False
                    if deploie:
                        if self.config.showplugins:
                            logger.info("deploie %s version %s on %s"%(k,v,msg['from']))
                        self.deploiePlugin(msg,k)
                        self.restartagent(msg['from'])
                        break

                if self.config.showplugins:
                    logger.info("__________________________________________")
                self.showListClient()
                # indique que la configurations guacamole doit etre faite pour sous reseau subnetxmpp
                self.updateguacamoleconfig[data['subnetxmpp']] = True
                # placer ici pour test sans attendre
                #self.updateGuacamoleConfigRelayServer()
                return True
            elif data['action'] == 'participant':
                resultcommand={'action' : 'participant',
                                'participant' : self.presencedeploiement }
                self.send_message(mto=msg['from'],
                        mbody=json.dumps(resultcommand),
                        mtype='chat')
                return True
            elif data['action'] == 'listparticipant':
                resultcommand={'action' : 'listparticipant',
                                'participant' : self.presencedeploiement }
                self.send_message(mto=msg['from'],
                        mbody=json.dumps(resultcommand),
                        mtype='chat')
                return True
        #jfk    
        except Exception as e:
            print "ERROR : infos machine %s"%(str(e))
            traceback.print_exc(file=sys.stdout)
        return False

    def timeout(self, data):
        log.warm("%s"%data['timeout'])

    #def timeout(self, *args, **kwargs):
        #if kwargs is not None:
            #for key, value in kwargs.iteritems():
                #logger.warn("%s == %s" %(key,value))
        #for arg in argv:
            #print "[", arg,"]"

    ### passer des commande or mmc
    #def muc_Messageschell(self,msg):
        #if msg['from'].bare == "commandrelay@localhost":
            #a = json.loads(msg['body'])
            #k = a.keys()
            #datasession = {}
            #data = {}

            #if 'session' in k :
                #datasession = a['session']

            #if 'data' in k :
                #data  = a['data']
            #self.envoicommand(a['to'], a['pluginname'] , data, datasession)
            #return True
        #return False
    def jidInRoom1(self, room, jid):
        for nick in self.plugin['xep_0045'].rooms[room]:
            entry = self.plugin['xep_0045'].rooms[room][nick]
            if entry is not None and entry['jid'] == jid:
                logger.debug("%s in room %s"%(jid,room))
                return True
        logger.debug("%s not in room %s"%(jid,room))
        return False 

    def message(self, msg):
        if  msg['body'] == "This room is not anonymous":
            return False
 

        #print self.plugin['xep_0045'].rooms
        if msg['from'].bare == self.config.jidsalonmaster or msg['from'].bare == self.config.confjidsalon:
            return False

        if self.jidInRoom1( self.config.confjidsalon, msg['from']):
            #print "*********************il appartient au salon config"
            self.MessagesAgentFromSalonConfig( msg)
            return

        if not self.jidInRoom1( self.config.jidsalonmaster, msg['from']):
            """ message agent apppartenant à master """
            #print "il n appartient pas au salon master"
            return False

        if self.messagereturnsession(msg):
            #print "messagereturnsession **********************"
            #message from client commande mmc
            return
        #JFK
        if  self.MessagesAgentFromSalonMaster( msg):
            return
        self.callpluginmaster(msg)

    def muc_message(self, msg):
        """
        fonction traitant tous messages venant d un salon
        attribut type pour selection
        """
        pass

    def callpluginmaster(self, msg):
        try :
            dataobj = json.loads(msg['body'])
            #dataobj['action']="testmaster"
            #dataobj['data'] = {}
            #dataobj['base64'] = False
            #dataobj['sessionid'] = name_random(5,"sesionid")
            #dataobj['ret'] = 0
            #self.session.createsessiondatainfo( dataobj['sessionid'], {'dede':34})
            #self.session.decrementesessiondatainfo()
            #self.session.decrementesessiondatainfo()
            #self.session.decrementesessiondatainfo()
            #self.session.affiche()
            if dataobj.has_key('action') and dataobj['action'] != "" and dataobj.has_key('data'):
                if dataobj.has_key('base64') and \
                    ((isinstance(dataobj['base64'],bool) and dataobj['base64'] == True) or 
                    (isinstance(dataobj['base64'],str) and dataobj['base64'].lower()=='true')):
                        mydata = json.loads(base64.b64decode(dataobj['data']))
                else:
                    mydata = dataobj['data']
                if not dataobj.has_key('sessionid'):
                    dataobj['sessionid'] = "absente"
                try:
                    print "appelle plugin",  dataobj['action'], "depuis ", msg['from']
                    msg['body'] = dataobj
                    del dataobj['data']
                    call_plugin(dataobj['action'],
                                self,
                                dataobj['action'],
                                dataobj['sessionid'],
                                mydata,
                                msg,
                                dataobj['ret'],
                                dataobj
                                )
                except TypeError:
                    logging.error("TypeError execution plugin %s %s" % (dataobj['action'], sys.exc_info()[0]))
                    print dataobj['action']
                    print mydata
                    print dataobj['ret']
                    print dataobj['sessionid']
                    print msg['from']
                    print dataobj
                    print os.path.join(os.path.dirname(os.path.realpath(__file__)), "pluginsmaster")
                    traceback.print_exc(file=sys.stdout)

                except Exception as e:
                    logging.error("execution plugin %s %s" % (dataobj['action'], str(e)))
                    print dataobj['action']
                    print mydata
                    print dataobj['ret']
                    print dataobj['sessionid']
                    print msg['from']
                    print dataobj
                    print os.path.join(os.path.dirname(os.path.realpath(__file__)), "pluginsmaster")
                    traceback.print_exc(file=sys.stdout)

        except Exception as e:
            logging.error("structure Message %s   %s " %(msg,str(e)))
            traceback.print_exc(file=sys.stdout)


    def updateGuacamoleConfigRelayServer(self):
        print "updateGuacamoleConfigRelayServer"
        dataguacamoleconf = {}
        datalocationserverguacamoleconf = {}
        controle="relayserver"
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
                elif self.presencedeploiement[machine]['agenttype'] == "relayserver":
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
        #print "*********muc_offlineMaster %s"%presence
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
        #print "*********muc_presenceMaster %s"%presence
        if presence['muc']['nick'] != self.config.NickName:
            if self.config.showinfomaster:
                logger.debug(  "presence %s"%presence['muc']['nick'])

    def muc_onlineMaster(self, presence):
        if presence['muc']['nick'] != self.config.NickName:
            pass

    #traitement presence salon configuration dynamique
    def muc_presenceConf(self, presence):
        #print "*********muc_presenceConf %s"%presence
        pass
    def muc_offlineConf(self, presence):
        #print "*********muc_offlineConf %s"%presence
        pass
    def muc_onlineConf(self, presence):
        #print "*********muc_onlineConf %s"%presence
        pass


#JFK
    def applicationdeployment1(self, jidrelais, jidmachine, name, time, encodebase64 = False):
        """ lors d'un deploiement 
        1er action synchronise le package name precemmand
        """
        if not managepackage.getversionpackagename(name):
            return False

        data =  {
                "name" : name,
                "path":managepackage.getpathpackagename(name),
                "jidrelais": jidrelais,
                "jidmachine":jidmachine,
                "jidmaster": self.boundjid.bare,
                "iprelais" :  XmppMasterDatabase().ipfromjid(jidrelais)[0],
                "ipmachine": XmppMasterDatabase().ipfromjid(jidmachine)[0],
                "ipmaster" : self.config.Server,
                "Dtypequery" : "TQ",
                "Devent" : "STARDEPLOY"
        }
        #print data['ipmaster']
        #print data['iprelais']
        #rsync --delete -av localhost:/var/lib/pulse2/packages/ ['192.168.56.2']:/var/lib/pulse2/packages/
        if data['ipmaster'] ==  data['iprelais']:
            precommand = None
        else:
            precommand =  "rsync --delete -av %s %s:%s"%(data['path'], data['iprelais'], data['path'])

        xmppcommanddiffered(jidrelais,"applicationdeployment", data, 20, precommand, None)

        #faire un rsync
        ##rsync --delete -anv /var/lib/pulse2/packages/ /tmp/test/
        return True
        #return self.envoicommand( jidrelais, "applicationdeployment" , data, datasession = None, time=50)

    def envoicommand(self, jid, action , data={}, datasession = None, encodebase64 = False, time = 10, eventthread=None):
        if datasession == None:
            datasession = {}
        command={
            'action' : action,
            'base64' : encodebase64,
            'sessionid': name_random(5, "command"),
            'data' : ''
            }

        if encodebase64 :
            command['data'] = base64.b64encode(json.dumps(data))
        else:
            command['data'] = data

        datasession['data'] = data
        datasession['callbackcommand'] = "commandend"
        self.session.createsessiondatainfo(command['sessionid'],  datasession = data, timevalid = time, eventend = eventthread)
        #print "send message"
        self.send_message(mto = jid,
                        mbody = json.dumps(command),
                        mtype = 'chat')
        return command['sessionid']

