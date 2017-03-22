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
import re

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
import lib
from lib.networkinfo import networkagentinfo
from lib.managesession import sessiondatainfo, session
from lib.utils import *
from lib.managepackage import managepackage
from lib.manage_event import manage_event
from lib.manage_process import mannageprocess
from lib.manageRSAsigned import MsgsignedRSA
from lib.localisation import Localisation
from mmc.plugins.xmppmaster.config import xmppMasterConfig
from mmc.plugins.base import getModList
from mmc.plugins.base.computers import ComputerManager

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
#ALTER TABLE `xmppmaster`.`machines` 
#ADD COLUMN `picklekeypublic` VARCHAR(550) NULL DEFAULT NULL AFTER `urlguacamole`;
from mmc.plugins.msc.database import MscDatabase


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

def getXmppConfiguration():
    return str(xmppMasterConfig())

def callXmppFunction(functionname, *args, **kwargs ):
    logging.getLogger().debug("**call function %s %s %s"%(functionname, args, kwargs))
    return getattr(ObjectXmpp(),functionname)( *args, **kwargs)

def callXmppPlugin(plugin, data ):
    #logging.getLogger().debug("**call plugin %s %s"%(plugin, data))
    logging.getLogger().debug("**call plugin %s"%(plugin))
    ObjectXmpp().callpluginmasterfrommmc(plugin,  data )

class XmppCommandDiffered:
    """
    Thread in charge of running precommand
    Pre-command complete
    send_session_command with session self,
    Session complete runs post command
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
            self.t2.start()
        else:
            logger.debug("XmppCommandDiffered error XMPP not initialized")
            pass

    def differed(self):
        """
        Code that runs during execution of the thread.
        """
        # Pre-command
        self.xmpp = ObjectXmpp()
        if self.precommand != None:
            logger.debug( "exec command %s"%self.precommand)
            a = simplecommandstr(self.precommand)
            # Sends a['result'] to log
            if a['code'] != 0:
                return
            logger.debug( a['result'])
        # Executes XMPP command
        # XMPP command with session creation
        self.sessionid = self.xmpp.send_session_command( self.to,
                                                        self.action ,
                                                        self.data,
                                                        datasession = None,
                                                        encodebase64 = False,
                                                        time = self.t,
                                                        eventthread = self.e )

        # Post-command running after XMPP Command
        if self.postcommand != None:
            while not self.e.isSet():
                # Wait for timeout or event thread
                event_is_set = self.e.wait(self.t)
                if event_is_set:
                    # After session completes, execute post-command shell
                    b = simplecommandstr(self.postcommand)
                    # Sends b['result'] to log
                    logger.debug( b['result'])
                else:
                    # Timeout
                    if not self.xmpp.session.isexist(self.sessionid):
                        logger.debug( 'Action session %s timed out'%self.action)
                        logger.debug( "Timeout error")
                        break;

class XmppSimpleCommand:
    """ 
        Run XMPP command with session and timeout
        Thread waits for timeout or end of session
        Returns command result
    """
    def __init__(self, to, data, timeout):
        #Get reference on master agent xmpp
        self.xmpp = ObjectXmpp()
        #self.xmpp = PluginManager().getEnabledPlugins()['xmppmaster'].xmppMasterthread().xmpp
        self.e =  threading.Event()
        self.result = {}
        self.data = data
        self.t = timeout
        self.sessionid = data['sessionid']
        self.session = self.xmpp.session.createsessiondatainfo(data['sessionid'],
                                                               {},
                                                               self.t,
                                                               self.e)
        self.xmpp.send_message( mto = to,
                                mbody = json.dumps(data),
                                mtype = 'chat')
        self.t2 = threading.Thread(name='command',
                      target=self.resultsession)
        self.t2.start()

    def resultsession(self):
        while not self.e.isSet():
            event_is_set = self.e.wait(self.t)
            logger.debug( 'event est signaler set: %s'% event_is_set)
            if event_is_set:
                self.result = self.session.datasession
            else:
                #timeout
                self.result = {u'action': u'resultshellcommand',
                               u'sessionid': self.sessionid,
                               u'base64': False,
                               u'data': {u'msg': "ERROR command\n timeout %s"%self.t },
                               u'ret': 125}
                break;
        self.xmpp.session.clearnoevent(self.sessionid)
        return self.result


class MUCBot(sleekxmpp.ClientXMPP):
    def __init__(self, conf): #jid, password, room, nick):
        self.config = conf
        self.session = session()
        self.domaindefault = "pulse"
        # The queues. These objects are like shared lists
        # The command processes use this queue to notify an event to the event manager
        self.queue_read_event_from_command = Queue()
        self.eventmanage = manage_event(self.queue_read_event_from_command, self)
        self.mannageprocess = mannageprocess(self.queue_read_event_from_command)
        self.listdeployinprocess = {}
        self.deploywaitting = {}
        self.plugintype = {}
        self.plugindata = {}
        self.loadPluginList()
        sleekxmpp.ClientXMPP.__init__(self,  conf.jidagent, conf.passwordconnection)

        # dictionary used for deploy
        self.machineWakeOnLan = {}
        self.machineDeploy = {}

        # Clear machine table
        # XmppMasterDatabase().clearMachine()

        self.idm = ""
        self.presencedeployment = {}
        self.updateguacamoleconfig = {}
        self.xmpppresence={}

        # schedule deployement
        self.schedule('schedule deploy', 30 , self.scheduledeploy, repeat=True)

        # Decrement session time
        self.schedule('manage session', 15 , self.handlemanagesession, repeat=True)

        # Reload plugins list every 15 minutes
        self.schedule('update plugin', 900 , self.loadPluginList, repeat=True)

        self.add_event_handler("session_start", self.start)
        """ New presence in Conf chatroom """
        self.add_event_handler("muc::%s::presence" % conf.confjidchatroom,
                               self.muc_presenceConf)
        """ Unsubscribe from Conf chatroom """
        self.add_event_handler("muc::%s::got_offline" % conf.confjidchatroom,
                               self.muc_offlineConf)
        """ Subscribe to Conf chatroom """
        self.add_event_handler("muc::%s::got_online" % conf.confjidchatroom,
                               self.muc_onlineConf)
        # Called for all messages
        self.add_event_handler('message', self.message)
        # The groupchat_message event is triggered every time a message
        # Strophe is received from any chat room. If you too
        # Save a handler for the 'message' event, MUC messages
        # Will be processed by both managers.
        self.add_event_handler("groupchat_message", self.muc_message)
        self.add_event_handler("pluginaction", self.pluginaction)

        self.add_event_handler ( 'changed_status', self.changed_status)
        self.RSA = MsgsignedRSA("master")

    def scheduledeploy(self):
        resultdeploymachine, e = MscDatabase().deployxmpp();
        #logging.debug( "scheduledeploy")
        #for deploy in resultdeploymachine:
            #logging.debug( "CommandsOnHost info")
            #a = deploy.CommandsOnHost.__dict__
            #for t in a:
                #logging.debug("%s : %s"%(t, a[t]))
            #logging.debug( "Commands info")
            #a = deploy.Commands.__dict__
            #for t in a:
                #logging.debug( "%s : %s"%(t, a[t]))
            #logging.debug( "Target info")
            #a = deploy.Target.__dict__
            #for t in a:
                #logging.debug( "%s : %s"%(t, a[t]))
            #logging.debug( "CommandsOnHostPhase info")
            #a = deploy.CommandsOnHostPhase.__dict__
            #for t in a:
                #logging.debug( "%s : %s"%(t, a[t]))

        for deploy in self.machineWakeOnLan:
            # verify presense machine deploy ou wake in lan
            if XmppMasterDatabase().getPresenceuuid(deploy):
                self.machineDeploy[deploy].extend(self.machineWakeOnLan[deploy])
                del self.machineWakeOnLan[deploy]

        for deploy in resultdeploymachine:
            UUID = str(deploy.Target.target_uuid)
            deployobject = {'pakkageid' : str(deploy.Commands.package_id), 'commandid' :  deploy.Commands.id , 'mac' : deploy.Target.target_macaddr,'count' : 0,'login' : deploy.Commands.creator }
            if XmppMasterDatabase().getPresenceuuid(UUID):
                try:
                    self.machineDeploy[UUID].append(deployobject)
                except:
                    self.machineDeploy[UUID] = []
                    self.machineDeploy[UUID].append(deployobject)
            else:
                try:
                    self.machineWakeOnLan[UUID].append(deployobject)
                except:
                    self.machineWakeOnLan[UUID]=[]
                    self.machineWakeOnLan[UUID].append(deployobject)
        suppobjectwanonlan = []
        for uuidmachine in self.machineWakeOnLan:
            for taballobjectwanonlan in self.machineWakeOnLan[uuidmachine]:
                if taballobjectwanonlan['count'] <  4:
                    listmacadress = taballobjectwanonlan['mac'].split("||");
                    taballobjectwanonlan['count']=taballobjectwanonlan['count'] + 1
                    for macadress in listmacadress:
                        if macadress != "":
                            logging.debug("wakeonlan machine  [Machine : %s]"%uuidmachine)
                            self.callpluginmasterfrommmc('wakeonlan', {'macadress': macadress }  )
                            self.logtopulse("wake on lan on macadress %s"%macadress,type='Wol',
                                            sessionname = taballobjectwanonlan['commandid'],
                                            priority = -1 ,
                                            who= uuidmachine)
                else:
                     self.machineWakeOnLan[uuidmachine].remove(taballobjectwanonlan)
            if len(self.machineWakeOnLan[uuidmachine]) == 0:
                suppobjectwanonlan.append(uuidmachine)

        for clearobjectwanonlan in suppobjectwanonlan:
            del self.machineWakeOnLan[clearobjectwanonlan]
            logging.warn("wakeonlan on machine %s error: to abort after 4 attempts"%clearobjectwanonlan)
            self.logtopulse("wake on lan on machine %s [to ABORT after 4 attempts]"%clearobjectwanonlan,
                            type='Wol',
                            sessionname = taballobjectwanonlan['commandid'],
                            priority = -1 ,
                            who= clearobjectwanonlan)
        suppobjmachineDeploy = []
        for deploy in self.machineDeploy:
            deployobject = self.machineDeploy[deploy].pop(0)
            self.applicationdeployjsonUuidMachineAndUuidPackage(deploy,
                                                                deployobject['pakkageid'],
                                                                deployobject['commandid'],
                                                                deployobject['login'],
                                                                30)
            if len (self.machineDeploy[deploy]) == 0 :
                suppobjmachineDeploy.append(deploy)
        for suppmachineuuid in suppobjmachineDeploy:
            del self.machineDeploy[suppmachineuuid]

    def start(self, event):
        self.get_roster()
        self.send_presence()
        #chatroomjoin=[self.config.jidchatroommaster,self.config.jidchatroomlog,self.config.confjidchatroom]
        chatroomjoin=[self.config.confjidchatroom]
        for chatroom in chatroomjoin:
            if chatroom == self.config.confjidchatroom:
                passwordchatroom = self.config.confpasswordmuc
            else:
                passwordchatroom = self.config.passwordconnexionmuc

            self.plugin['xep_0045'].joinMUC(chatroom,
                                            self.config.NickName,
                                            # If a room password is needed, use:
                                            password=passwordchatroom,
                                            wait=True)
        self.logtopulse('Start agent Master', type="MASTER", who =  self.boundjid.bare)
        #ty = "MASTER"
        #self.logtopulse("Start agent Master",type= ty, who =  self.boundjid.bare) 

    def logtopulse(self,text,type='noset',sessionname = '',priority = 0, who =''):
        msgbody = {
                    'text' : text,
                    'type':type,
                    'session':sessionname,
                    'priority':priority,
                    'who':who
                    }
        self.send_message(mto=jid.JID("log@pulse"),
                                mbody=json.dumps(msgbody),
                                mtype='chat')

    def changed_status(self,msg_changed_status):
        if msg_changed_status['from'].resource == 'MASTER':
            return
        logger.debug( "%s %s"%(msg_changed_status['from'], msg_changed_status['type']))
        if msg_changed_status['type'] == 'unavailable':
            try:
                result = XmppMasterDatabase().delPresenceMachine(msg_changed_status['from'])
            except:
                traceback.print_exc(file=sys.stdout)
            self.showListClient()

    def showListClient(self):
        self.presencedeployment={}
        listrs = XmppMasterDatabase().listjidRSdeploy()
        if len(listrs) != 0:
            for i in listrs:
                li = XmppMasterDatabase().listmachinesfromdeploy(i[0])
                logger.info("RS [%s] for deploy on %s Machine"%(i[0],len(li)-1))
                logger.info('{0:5}|{1:7}|{2:20}|{3:35}|{4:55}'.format("type",
                                                                      "uuid",
                                                                      "Machine",
                                                                      "jid",
                                                                      "platform"))
                for j in li:
                    if j[9] == 'relayserver':
                        TY = 'RSer'
                    else:
                        TY = "Mach"
                    logger.info('{0:5}|{1:7}|{2:20}|{3:35}|{4:55}'.format(TY,j[5],j[4],j[1],j[2]))
        else:
            logger.info("Aucune Machine repertorié")

    def presence(self, message):
        pass

    def unavailable(self, message):
        pass

    def subscribe(self, message):
        pass

    def subscribed(self, message):
        pass

    def applicationdeployjsonUuidMachineAndUuidPackage(self,
                                                       uuidmachine,
                                                       uuidpackage,
                                                       idcommand,
                                                       login,
                                                       time,
                                                       encodebase64 = False):
        name = managepackage.getnamepackagefromuuidpackage(uuidpackage)
        if name is not None:
            return self.applicationdeployjsonuuid(str(uuidmachine), str(name), idcommand, login, time)
        else:
            logger.warn('%s package is not an xmpp package : (The json xmpp descriptor is missing)')
            return False

    def applicationdeployjsonuuid(self,
                                  uuidmachine,
                                  name,
                                  idcommand,
                                  login,
                                  time,
                                  encodebase64 = False,
                                  uuidpackage=""):
        try:
            objmachine = XmppMasterDatabase().getGuacamoleRelayServerMachineUuid(uuidmachine)
            jidrelay = objmachine.groupdeploy
            jidmachine = objmachine.jid
            ### print "jidrelay %s\njidmachine %s"%(jidrelay,jidmachine)
            if jidmachine != None and jidmachine != "" and jidrelay != None and jidrelay != "" :
                return self.applicationdeploymentjson(jidrelay,
                                                      jidmachine,
                                                      idcommand,
                                                      login, 
                                                      name, 
                                                      time,
                                                      encodebase64 = False,
                                                      uuidmachine=uuidmachine)
            else:
                logger.error("deploy jjjjjj %s error uuid machine %s" %(name, uuidmachine))
                return False
        except:
            logger.error("deploy %s error uuid machine %s" %(name, uuidmachine))
            return False

    def parsexmppjsonfile(self, path):
        datastr = file_get_contents(path)

        datastr = re.sub(r"(?i) *: *false", " : false", datastr)
        datastr = re.sub(r"(?i) *: *true" , " : true" , datastr)

        file_put_contents(path,  datastr)

    def applicationdeploymentjson(self,
                                  jidrelay,
                                  jidmachine,
                                  idcommand,
                                  login,
                                  name,
                                  time,
                                  encodebase64 = False,
                                  uuidmachine = ""):
        """ For a deployment
        1st action: synchronize the previous package name
        The package is already on the machine and also in server relay.
        """
        if not managepackage.getversionpackagename(name):
            logger.error("deploy %s error package name" %(name))
            return False
        # Name the event
        dd = name_random(5, "deploy_")
        path =  managepackage.getpathpackagename(name)
        #read descriptor name in variable
        descript =  managepackage.loadjsonfile(os.path.join(path, 'xmppdeploy.json'))
        self.parsexmppjsonfile(os.path.join(path, 'xmppdeploy.json'))
        if descript is None:
            logger.error("deploy %s on %s  error : xmppdeploy.json missing" %(name, uuidmachine))
            return None
        data =  {
                "name" : name,
                "login" : login,
                'methodetransfert' : 'curl',
                "path" : path,
                "packagefile":os.listdir(path),
                "jidrelay" : jidrelay,
                "jidmachine" : jidmachine,
                "jidmaster" : self.boundjid.bare,
                "iprelay" :  XmppMasterDatabase().ipfromjid(jidrelay)[0],
                "ipmachine" : XmppMasterDatabase().ipfromjid(jidmachine)[0],
                "ipmaster" : self.config.Server,
                "Dtypequery" : "TQ",
                "Devent" : "STARDEPLOY",
                "uuid" : uuidmachine,
                "descriptor" : descript,
                "transfert" : True
        }
        sessionid = self.send_session_command(jidmachine,
                                              "applicationdeploymentjson" ,
                                              data,
                                              datasession = None,
                                              encodebase64 = False)
        self.logtopulse("Start deploy on machine %s"%jidmachine,
                        type = 'deploy',
                        sessionname = sessionid,
                        priority = -1,
                        who = "MASTER")
        self.eventmanage.show_eventloop()
        XmppMasterDatabase().adddeploy(idcommand,
                                       jidmachine,
                                       jidrelay,
                                       jidmachine,
                                       uuidmachine,
                                       descript['info']['name'],
                                       "STARDEPLOY",
                                       sessionid,
                                       user="",
                                       login=login,
                                       deploycol="")
        return sessionid

    def pluginaction(self,rep):
        if 'sessionid' in rep.keys():
            sessiondata = self.session.sessionfromsessiondata(rep['sessionid'])
            if 'shell' in sessiondata.getdatasession().keys() and sessiondata.getdatasession()['shell']:
                self.send_message(mto=jid.JID("commandrelay@localhost"),
                                mbody=json.dumps(rep),
                                mtype='chat')
        logger.info("Log action plugin %s!" % rep)

    def displayData(self,data):
        if self.config.showinfomaster:
            logger.info("__________________________")
            logger.info("MACHINE INFORMATION")
            logger.info("Deployment name : %s"%data['deployment'])
            logger.info("From : %s"%data['who'])
            logger.info("Jid from : %s"%data['from'])
            logger.info("Machine : %s"%data['machine'])
            logger.info("Platform : %s"%data['platform'])
            logger.info("--------------------------------")
            logger.info("----MACHINE XMPP INFORMATION----")
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
            logger.info("xmppmacnotshortened : %s"%data['xmppmacnotshortened'])

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

            logger.info("DETAILED INFORMATION")
            if 'information' in data:
                logger.info("%s"% json.dumps(data['information'], indent=4, sort_keys=True))

    def handlemanagesession(self):
        self.session.decrementesessiondatainfo()
        ###test

    def loadPluginList(self):
        logger.debug("Verify base plugin")
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

    def signalpresence(self, jid):
        self.sendPresence(pto=jid, ptype='probe')

    def register(self, iq):
        """ called for automatic registration"""
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
        except IqTimeout:
            logger.error("No response from server.")
            self.disconnect()

    def restartAgent(self , to ):
        if self.config.showplugins:
            logger.info("Restart agent on %s"%(to))
        self.send_message(mto=to,
            mbody=json.dumps({'action':'restartbot','data':''}),
            mtype='chat')

    def deployPlugin(self, msg, plugin):
        data =''
        fichierdata={}
        namefile =  os.path.join(self.config.dirplugins,"plugin_%s.py"%plugin)
        if os.path.isfile(namefile) :
            logger.debug("File plugin found %s"%namefile)
        else:
            logger.error("File plugin found %s"%namefile)
            return
        try:
            fileplugin = open(namefile, "rb")
            data=fileplugin.read()
            fileplugin.close()
        except :
            logger.error("File read error")
            traceback.print_exc(file=sys.stdout)
            return
        fichierdata['action'] = 'installplugin'
        fichierdata['data'] ={}
        dd = {}
        dd['datafile']= data
        dd['pluginname'] = "plugin_%s.py"%plugin
        fichierdata['data']= base64.b64encode(json.dumps(dd))
        fichierdata['sessionid'] = "sans"
        fichierdata['base64'] = True
        try:
            self.send_message(mto=msg['from'],
                            mbody=json.dumps(fichierdata),
                            mtype='chat')
        except:
            traceback.print_exc(file=sys.stdout)

    def callinventory(self, torelayserver, data):
        try:
            body = {'action' : 'inventory',
                    'sessionid': name_random(5, "inventory"),
                    'data' : data }
            self.send_message(  mto = torelayserver,
                                mbody = json.dumps(body),
                                mtype = 'chat')
        except:
            traceback.print_exc(file=sys.stdout)

    def callInstallConfGuacamole(self, torelayserver, data):
        try:
            body = {'action' : 'guacamoleconf',
                    'sessionid': name_random(5, "guacamoleconf"),
                    'data' : data }
            self.send_message(  mto = torelayserver,
                                mbody = json.dumps(body),
                                mtype = 'chat')
        except:
            traceback.print_exc(file=sys.stdout)

    def sendErrorConnectionConf(self,msg):
        reponse = {
            'action' : 'resultconnectionconf',
            'sessionid' : data['sessionid'],
            'data' : [],
            'ret': 255
            }
        self.send_message(mto=msg['from'],
                        mbody=json.dumps(reponse),
                        mtype='chat')

    def sendrsconnectiondeploychatroom(self, to, data):
        connection = {
            'action' : '@@@@@deploychatroomON@@@@@',
            'sessionid' : name_random(5, "deploychatroom"),
            'data' : [],
            'ret': 255
            }
        self.send_message(mto=to,
                        mbody=json.dumps(connection),
                        mtype='chat')

    def MessagesAgentFromChatroomlog(self, msg, data):
        """
        traitement des logs from salon log
        TODO  supp
        """
        try:
            logger.debug("%s [%s]"%( data['data']['msg'] , data['data']['tag']))
            return True
        except Exception as e:
            logger.debug( "ERROR MessagesAgentFromChatroomlog %s"%(str(e)))
            traceback.print_exc(file=sys.stdout)
            return False

    def MessagesAgentFromChatroomConfig(self, msg):
        logger.debug("MessagesAgentFromChatroomConfig")
        ### Message from chatroom master
        try:
            data = json.loads(msg['body'])
            # Verify msg from chatroom master for subscription
            if data['action'] == 'connectionconf' :
                """ Check machine information from agent """
                info = json.loads(base64.b64decode(data['completedatamachine']))
                data['information'] = info
                if data['ippublic'] != None:
                    self.localisationifo = Localisation().geodataip(data['ippublic'])
                else:
                    self.localisationifo = {}
                self.displayData(data)
            else:
                return
        except:
            return
        if data['agenttype'] == "relayserver":
            self.sendErrorConnectionConf(msg)
            return
        #logger.info("%s"% json.dumps(data, indent=4, sort_keys=True))
        logger.debug("Search Relay server for connection from user %s hostname %s localisation %s"%(data['information']['users'][0],data['information']['info']['hostname'],self.localisationifo))
        XmppMasterDatabase().log("Search Relay server for connection from user %s hostname %s localisation %s"%(data['information']['users'][0],data['information']['info']['hostname'],self.localisationifo))
        # Defining relay server for connection
        # Order of rules to be applied
        ordre =  XmppMasterDatabase().Orderrules()
        odr = [ x[0] for x in ordre]
        logger.debug("order rule %s "%odr)
        indetermine = []
        result = []
        for x in ordre:
            if x[0] == 1:
                logger.debug("analyse rule 1")
                result1= XmppMasterDatabase().algoruleuser(data['information']['users'][0])
                if len(result1) > 0 :
                    logger.debug("applied rule 1")
                    result= XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    logger.debug("user rule selects relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    break
            elif x[0] == 2:
                logger.debug("analyse rule 2")
                result1= XmppMasterDatabase().algorulehostname(data['information']['info']['hostname'])
                if len(result1) > 0 :
                    logger.debug("applied rule 2")
                    result= XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    logger.debug("hostname rule selects relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    break
            elif x[0] == 3:
                logger.debug("analyse rule 3")
                distance = 40000000000
                listeserver=[]
                relayserver = -1
                if self.localisationifo != None and self.localisationifo['longitude']!="" and self.localisationifo['latitude']!="":
                    result1 = XmppMasterDatabase().IdlonglatServerRelay(data['classutil'])
                    a=0
                    for x in result1:
                        a=a+1
                        if x[1]!="" and x[2]!="":
                            distancecalculated = Localisation().determinationbylongitudeandip(float(x[2]),float( x[1]) , data['ippublic'])
                            #print distancecalculated
                            if distancecalculated <= distance:
                                distance = distancecalculated
                                relayserver = x[0]
                                listeserver.append(x[0])
                    nbserver = len(listeserver)
                    if nbserver > 1 :
                        from random import randint
                        index = randint(0 , nbserver-1)
                        #print "random %s"%index
                        logger.warn("geoposition rule returned %d relay servers for machine"\
                            "%s user %s \nPossible relay servers : id list %s "%(nbserver, data['information']['info']['hostname'],
                             data['information']['users'][0],listeserver))
                        logger.warn("Continues for other rules. Random choice only if no other findings ")
                        indetermine =  XmppMasterDatabase().IpAndPortConnectionFromServerRelay(listeserver[index])
                    else:
                        if relayserver != -1:
                            result= XmppMasterDatabase().IpAndPortConnectionFromServerRelay(relayserver)
                            logger.debug("geoposition rule selects relayserver for machine %s user %s \n %s "%(data['information']['info']['hostname'],data['information']['users'][0],result))
                            break
                if len(result)!=0:
                    result = [self.config.defaultrelayserverip,self.config.defaultrelayserverport,result2[0],self.config.defaultrelayserverbaseurlguacamole]
                    ##self.defaultrelayserverjid = self.get('defaultconnection', 'jid')
                    logger.debug("default rule selects relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                else:
                    result = [self.config.defaultrelayserverip,self.config.defaultrelayserverport,"self.domaindefault",self.config.defaultrelayserverbaseurlguacamole]
                    ##self.defaultrelayserverjid = self.get('defaultconnection', 'jid')
                    logger.warn("default rule selects relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                    logger.warn("Check parameter [defaultconnection] in xmppmaster.ini....")
                break
            elif x[0] == 4:
                logger.debug("analysis  rule 4")
                logger.debug("rule subnet : Test if network are identical")
                subnetexist = False
                for z in data['information']['listipinfo']:
                    result1 = XmppMasterDatabase().algorulesubnet(subnetnetwork(z['ipaddress'],z['mask']),data['classutil'])
                    if len(result1) > 0 :
                        subnetexist = True
                        result= XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                        logger.debug("subnet rule selects relayserver for machine %s user %s \n %s"%(data['information']['info']['hostname'],data['information']['users'][0],result))
                        break
                if subnetexist: break;
            elif x[0] == 5:
                logger.debug("analysis  rule 5")
                if len(indetermine) > 0:
                    logger.debug("analysis  rule 4")
                    result = indetermine
                    logger.warn("server address is compared to that of relay servers (geoPosition rule)")
                    break;
                else:
                    result2 = XmppMasterDatabase().jidrelayserverforip(self.config.defaultrelayserverip)

        logger.debug(" user %s and hostname %s [connection ip %s port : %s]"%(data['information']['users'][0],data['information']['info']['hostname'],result[0],result[1]))
        XmppMasterDatabase().log("[user %s hostanme %s] : Relay server for connection ip %s port %s"%(data['information']['users'][0],data['information']['info']['hostname'],result[0],result[1] ))

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
                    logger.debug("No session name")
                    pass
        except KeyError:
            return False
        return False

    def unban(self,room, jid, reason=''):
        resp=self.plugin['xep_0045'].setAffiliation(room, jid, affiliation='none', reason=reason)
        return resp

    def MessagesAgentFromChatroomMaster(self, msg):
        ### Message from chatroom master
        ### jabber routes the message.
        #if msg['from'].bare == self.config.jidchatroommaster:
            #""" message all members of chatroom master """
            #return False
        if  msg['body'] == "This room is not anonymous":
            return False
        restartAgent = False
        try:
            data = json.loads(msg['body'])
            # Check msg from chatroom master for subscription
            if 'action' in data and data['action'] == 'loginfos':
                # Process loginformation
                self.MessagesAgentFromChatroomlog(msg,data)
                return True

            if 'action' in data and data['action'] == 'infomachine' :
                # verify si machine Enregistrer
                if XmppMasterDatabase().getPresencejid(msg['from'].bare):
                    return

                """ Check machine information from agent """
                info = json.loads(base64.b64decode(data['completedatamachine']))
                if data['ippublic'] != None:
                    self.localisationifo = Localisation().geodataip(data['ippublic'])
                else:
                    self.localisationifo = {}
                data['information'] = info
                ###################################
                #check is agent machine or agent Relayserver has public key of master
                publickeybase64 =  info['publickey']
                is_masterpublickey =  info['is_masterpublickey']
                del info['publickey']
                del info['is_masterpublickey']
                if not is_masterpublickey:
                    #Send key public if the machine agent does not have one
                    datasend = {
                        "action" : "installkeymaster",
                        "keypublicbase64" : self.RSA.loadkeypublictobase64(),
                        'ret': 0,
                        'sessionid': name_random(5, "publickeymaster"),
                    }
                    self.send_message( mto = msg['from'],
                                    mbody = json.dumps(datasend),
                                    mtype = 'chat')
                ###################################
                self.displayData(data)
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

                logger.info("add user : %s for machine : %s country_name : %s"%(data['information']['users'][0],
                                                                                data['information']['info']['hostname'],
                                                                                country_name))
                useradd = XmppMasterDatabase().adduser(data['information']['users'][0],
                                                data['information']['info']['hostname'] ,
                                                city,
                                                region_name ,
                                                time_zone ,
                                                longitude,
                                                latitude ,
                                                postal_code ,
                                                country_code,
                                                country_name )
                try:
                    useradd = useradd[0]
                except TypeError:
                    pass
                # Add relayserver or update status in database
                if data['agenttype'] == "relayserver":
                    XmppMasterDatabase().addServerRelay(data['baseurlguacamole'],
                                                            data['subnetxmpp'],
                                                            data['information']['info']['hostname'],#data['machine'][:-3],
                                                            data['deployment'],
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
                # Add machine
                idmachine = XmppMasterDatabase().addPresenceMachine(data['from'],
                                                            data['platform'],
                                                            data['information']['info']['hostname'],
                                                            data['information']['info']['hardtype'],
                                                            None,
                                                            data['xmppip'],
                                                            data['subnetxmpp'],
                                                            data['xmppmacaddress'],
                                                            data['agenttype'],
                                                            classutil=data['classutil'],
                                                            urlguacamole =data['baseurlguacamole'],
                                                            groupdeploy =data['deployment'],
                                                            objkeypublic= publickeybase64
                                                            )
                if idmachine != -1:
                    if useradd != -1:
                        XmppMasterDatabase().hasmachineusers(useradd, idmachine)
                    for i in data['information']["listipinfo"]:
                        try:
                            broadcast = i['broadcast']
                        except:
                            broadcast=''
                        XmppMasterDatabase().addPresenceNetwork( i['macaddress'],i['ipaddress'], broadcast, i['gateway'], i['mask'],i['macnotshortened'], idmachine)
                        logging.debug("add Presence Network [Machine : %d]"%idmachine)
                    if data['agenttype'] != "relayserver":
                        # Update uuid machine : for consistency with inventory
                        # call Guacamole config
                        # or add inventory
                        result = XmppMasterDatabase().listMacAdressforMachine(idmachine)
                        results = result[0].split(",")

                        logging.getLogger().debug("listMacAdressforMachine   %s"%results)
                        uuid =''
                        for t in results:
                            computer = ComputerManager().getComputerByMac(t)
                            if computer != None:
                                jidrs = str(jid.JID(data['deployment']).user)
                                jidm = jid.JID(data['from']).domain
                                jidrs = "%s@%s"%(jidrs,jidm)
                                uuid = 'UUID' + str(computer.id)
                                logging.getLogger().debug("uuid   %s"%uuid)
                                XmppMasterDatabase().updateMachineidinventory(uuid, idmachine)
                                self.callInstallConfGuacamole( jidrs, {'hostname' : data['information']['info']['hostname'],
                                                                            'machine_ip' : data['xmppip'],
                                                                            'uuid' : str(computer.id) })
                                break
                            else:
                                logging.getLogger().debug("computer is None")
                                pass
                        else:
                            # Register machine in inventory
                            self.callinventory(data['from'], {})
                # Show plugins information logs
                if self.config.showplugins:
                    logger.info("___________________________")
                    logger.info("LIST PLUGINS INSTALLED AGENT")
                    logger.info("%s"% json.dumps(data['plugin'], indent=4, sort_keys=True))
                    logger.info("__________________________________________")
                restartAgent = False
                if self.config.showplugins:
                    logger.info("_____________Deploy plugin_________________")
                for k,v in self.plugindata.iteritems():
                    deploy = False
                    try:
                        # Check version
                        if data['plugin'][k] != v:
                            logger.info("update %s version %s to version %s"%(k,data['plugin'][k],v))
                            deploy = True
                    except:
                        deploy = True
                    if self.plugintype[k] == "relayserver":
                        self.plugintype[k]="relayserver"
                    if data['agenttype'] != "all":
                        if data['agenttype'] == "relayserver" and  self.plugintype[k] == 'machine':
                            deploy = False
                        if data['agenttype'] == "machine" and  self.plugintype[k] == 'relayserver':
                            deploy = False
                    if deploy:
                        if self.config.showplugins:
                            logger.info("deploy %s version %s on %s"%(k,v,msg['from']))
                        self.deployPlugin(msg,k)
                        self.restartAgent(msg['from'])
                        break

                if self.config.showplugins:
                    logger.info("__________________________________________")
                self.showListClient()
                # indicate that the guacamole configurations must be made
                # for sub network subnetxmpp
                self.updateguacamoleconfig[data['subnetxmpp']] = True
                return True
            return False
        except Exception as e:
            logging.getLogger().error("ERROR : machine info %s"%(str(e)))
            traceback.print_exc(file=sys.stdout)
        return False

    def timeout(self, data):
        log.warm("%s"%data['timeout'])

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
        if msg['from'].bare == self.config.jidchatroommaster or msg['from'].bare == self.config.confjidchatroom:
            return False
        if self.jidInRoom1( self.config.confjidchatroom, msg['from']):
            self.MessagesAgentFromChatroomConfig( msg)
            return
        if  msg['type'] == 'groupchat':
            return
        self.signalpresence(msg['from'] )
        #if not self.jidInRoom1( self.config.jidchatroommaster, msg['from']):
            #""" message agent belonging to master """
            #return False
        if self.messagereturnsession(msg):
            # Message from client of mmc command
            return
        if  self.MessagesAgentFromChatroomMaster( msg):
            return
        self.callpluginmaster(msg)

    def muc_message(self, msg):
        """
        Processing all messages coming from a room
         type attribute to selection
        """
        pass

    def callpluginmasterfrommmc(self, plugin, data ):
        msg={}
        msg['from'] = self.boundjid.bare
        msg['body'] = json.dumps({
                        'action':plugin,
                        'ret':0,
                        'sessionid': name_random(5, plugin),
                        'data': data })
        self.callpluginmaster(msg)

    def callpluginmaster(self, msg):
        try :
            dataobj = json.loads(msg['body'])
            if dataobj.has_key('action') and dataobj['action'] != "" and dataobj.has_key('data'):
                if dataobj.has_key('base64') and \
                    ((isinstance(dataobj['base64'],bool) and dataobj['base64'] == True) or
                    (isinstance(dataobj['base64'],str) and dataobj['base64'].lower()=='true')):
                        mydata = json.loads(base64.b64decode(dataobj['data']))
                else:
                    mydata = dataobj['data']
                if not dataobj.has_key('sessionid'):
                    dataobj['sessionid'] = "absent"
                try:
                    logging.debug("Calling plugin %s from  %s"%( dataobj['action'], msg['from']))
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
                    logging.error("TypeError: executing plugin %s %s" % (dataobj['action'], sys.exc_info()[0]))
                    traceback.print_exc(file=sys.stdout)

                except Exception as e:
                    logging.error("Executing plugin %s %s" % (dataobj['action'], str(e)))
                    traceback.print_exc(file=sys.stdout)

        except Exception as e:
            logging.error("Message structure %s   %s " %(msg,str(e)))
            traceback.print_exc(file=sys.stdout)


    def muc_offlineMaster(self, presence):
        pass

    def muc_presenceMaster(self, presence):
        if presence['muc']['nick'] != self.config.NickName:
            if self.config.showinfomaster:
                logger.debug("Presence of %s"%presence['muc']['nick'])

    def muc_onlineMaster(self, presence):
        if presence['muc']['nick'] != self.config.NickName:
            pass

    # Processing of presence in dynamic configuration chatroom
    def muc_presenceConf(self, presence):
        pass
    def muc_offlineConf(self, presence):
        pass
    def muc_onlineConf(self, presence):
        pass

    def send_session_command(self, jid, action , data = {}, datasession = None, encodebase64 = False, time = 20, eventthread = None):
        logging.debug("send command and creation session")
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
        self.send_message(mto = jid,
                        mbody = json.dumps(command),
                        mtype = 'chat')
        return command['sessionid']
