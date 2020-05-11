#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2018 siveo, http://www.siveo.net
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
# file plugins/xmppmaster/master/agentmaster.py

import sys
import os
import re

import ConfigParser
import operator
import zlib
import sleekxmpp
from sleekxmpp import jid

import netifaces
import random
import base64
import json
from optparse import OptionParser
import copy
import lib
from lib.networkinfo import networkagentinfo
from lib.managesession import sessiondatainfo, session
from lib.utils import *
from lib.managepackage import managepackage
from lib.manageADorganization import manage_fqdn_window_activedirectory
from lib.manageRSAsigned import MsgsignedRSA
from lib.localisation import Localisation
from mmc.plugins.xmppmaster.config import xmppMasterConfig
from mmc.plugins.base import getModList
from mmc.plugins.base.computers import ComputerManager
from lib.manage_scheduler import manage_scheduler
from pulse2.database.xmppmaster import XmppMasterDatabase
from pulse2.database.pkgs import PkgsDatabase
from mmc.plugins.msc.database import MscDatabase
import traceback
import pprint
import pluginsmaster
import cPickle
import logging
import threading
import netaddr
from time import mktime, sleep
from datetime import datetime
from multiprocessing import Process, Queue, TimeoutError
from mmc.agent import PluginManager
from lib.update_remote_agent import Update_Remote_Agent
from distutils.version import LooseVersion, StrictVersion
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ElementBase, ET, JID
from sleekxmpp.stanza.iq import Iq

from lib.manage_xmppbrowsing import xmppbrowsing

from mmc.plugins.msc import convergence_reschedule
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


def getXmppstrConfiguration():
    return str(xmppMasterConfig().__dict__)

def getXmppConfiguration():
    return xmppMasterConfig().__dict__

def send_message_json(to, jsonstring):
    xmppob = ObjectXmpp()
    xmppob.send_message(mto=to,
                        mbody=json.dumps(jsonstring),
                        mtype='chat')


def callXmppFunction(functionname, *args, **kwargs):
    logging.getLogger().debug("**call function %s %s %s" % (functionname, args, kwargs))
    return getattr(ObjectXmpp(), functionname)(*args, **kwargs)


def callXmppPlugin(plugin, data):
    logging.getLogger().debug("**call plugin %s" % (plugin))
    ObjectXmpp().callpluginmasterfrommmc(plugin, data)


def callInventory(to):
    ObjectXmpp().callinventory(to)


def callrestartbymaster(to):
    return ObjectXmpp().callrestartbymaster(to)


def callrestartbotbymaster(to):
    return ObjectXmpp().restartAgent(to)

def callshutdownbymaster(to, time, msg):
    return ObjectXmpp().callshutdownbymaster(to, time, msg)


def callvncchangepermsbymaster(to, askpermission):
    return ObjectXmpp().callvncchangepermsbymaster(to, askpermission)

##################### call synchronous iq##########################

def callremotefile(jidmachine, currentdir="", timeout=40):
    strctfilestrcompress = ObjectXmpp().iqsendpulse(jidmachine, {"action": "remotefile", "data": currentdir}, timeout)
    try :
        strctfilestr=zlib.decompress(base64.b64decode(strctfilestrcompress))
        return strctfilestr
    except Exception as e:
        logger.error("%s" % (traceback.format_exc()))
    return strctfilestrcompress

def calllistremotefileedit(jidmachine):
    return ObjectXmpp().iqsendpulse(jidmachine, {"action": "listremotefileedit",
                                                 "data": ""}, 10)

def callremotefileeditaction(jidmachine, data, timeout=10):
    return ObjectXmpp().iqsendpulse(jidmachine, {"action": "remotefileeditaction",
                                                 "data": data}, timeout)

def callremotecommandshell(jidmachine, command="", timeout=20):
    return ObjectXmpp().iqsendpulse(jidmachine, {"action": "remotecommandshell",
                                                 "data": command,
                                                 "timeout": timeout}, timeout)


def callremoteXmppMonitoring(jidmachine, suject,  timeout=15):
    return ObjectXmpp().iqsendpulse(jidmachine, {"action": "remotexmppmonitoring",
                                                 "data": suject,
                                                 "timeout": timeout}, timeout)

def calllocalfile(currentdir=""):
    return ObjectXmpp().xmppbrowsingpath.listfileindir(currentdir)


def callInstallKey(jidAM, jidARS):
    return ObjectXmpp().callInstallKey(jidAM, jidARS)
# #################################################################

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
            self.e = threading.Event()
            self.t = timeout
            self.to = to
            self.action = action
            self.data = data
            self.precommand = precommand
            self.postcommand = postcommand
            self.t2 = threading.Thread(name=self.namethread, target=self.differed)
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
            logger.debug("exec command %s" % self.precommand)
            a = simplecommandstr(self.precommand)
            if a['code'] != 0:
                return
            logger.debug(a['result'])
        # Executes XMPP command
        # XMPP command with session creation
        self.sessionid = self.xmpp.send_session_command(self.to,
                                                        self.action,
                                                        self.data,
                                                        datasession=None,
                                                        encodebase64=False,
                                                        time=self.t,
                                                        eventthread=self.e)

        # Post-command running after XMPP Command
        if self.postcommand != None:
            while not self.e.isSet():
                # Wait for timeout or event thread
                event_is_set = self.e.wait(self.t)
                if event_is_set:
                    # After session completes, execute post-command shell
                    b = simplecommandstr(self.postcommand)
                    # Sends b['result'] to log
                    logger.debug(b['result'])
                else:
                    # Timeout
                    if not self.xmpp.session.isexist(self.sessionid):
                        logger.debug('Action session %s timed out' % self.action)
                        logger.debug("Timeout error")
                        break


class XmppSimpleCommand:
    """
        Run XMPP command with session and timeout
        Thread waits for timeout or end of session
        Returns command result
    """

    def __init__(self, to, data, timeout):
        # Get reference on master agent xmpp
        self.xmpp = ObjectXmpp()
        self.e = threading.Event()
        self.result = {}
        self.data = data
        self.t = timeout
        self.sessionid = data['sessionid']
        self.session = self.xmpp.session.createsessiondatainfo(data['sessionid'],
                                                               {},
                                                               self.t,
                                                               self.e)
        self.xmpp.send_message(mto=to,
                               mbody=json.dumps(data),
                               mtype='chat')
        self.t2 = threading.Thread(name='command',
                                   target=self.resultsession)
        self.t2.start()

    def resultsession(self):
        while not self.e.isSet():
            event_is_set = self.e.wait(self.t)
            logger.debug('The event is set to: %s' % event_is_set)
            if event_is_set:
                self.result = self.session.datasession
            else:
                self.result = {u'action': u'resultshellcommand',
                               u'sessionid': self.sessionid,
                               u'base64': False,
                               u'data': {u'msg': "ERROR command\n timeout %s" % self.t},
                               u'ret': 125}
                break
        self.xmpp.session.clearnoevent(self.sessionid)
        return self.result


class MUCBot(sleekxmpp.ClientXMPP):
    def __init__(self, conf):  # jid, password, room, nick):
        self.boolimportglpi = False
        namelibplugins = "master/pluginsmaster"
        self.modulepath = os.path.abspath(\
                os.path.join(os.path.dirname(os.path.realpath(__file__)),"..",
                             namelibplugins))
        logger.debug('Module path plugin xmppmaster is %s'%self.modulepath)
        self.listmodulemmc = PluginManager().getAvailablePlugins()
        self.config = conf
        self.session = session()
        self.domaindefault = "pulse"
        self.file_deploy_plugin = []
        self.wolglobal_set = set() #use group wol
        self.confaccount=[] #list des account for clear
        #clear conf compte.
        logger.debug('Clear MUC conf account')
        cmd = "for i in  $(ejabberdctl registered_users pulse | grep '^conf' ); do echo $i; ejabberdctl unregister $i pulse; done"
        try:
            a = simplecommandstr(cmd)
            logger.debug(a['result'])
        except Exception as e:
            pass
        #del old message offline
        logger.debug('del old message offline')
        cmd = "ejabberdctl delete_old_messages 1"
        try:
            a = simplecommandstr(cmd)
            logger.debug(a['result'])
        except Exception as e:
            pass
        # The queues. These objects are like shared lists
        # The command processes use this queue to notify an event to the event manager
        # self.queue_read_event_from_command = Queue()
        # self.eventmanage = manage_event(self.queue_read_event_from_command, self)
        # self.mannageprocess = mannageprocess(self.queue_read_event_from_command)
        self.listdeployinprocess = {}
        self.deploywaitting = {}
        self.plugintype = {}
        self.plugindata = {}
        self.plugindatascheduler = {}
        self.loadbasepluginagent() # update base list plugin and remote agent
        sleekxmpp.ClientXMPP.__init__(self, conf.jidagent, conf.passwordconnection)

        self.manage_scheduler = manage_scheduler(self)
        self.xmppbrowsingpath = xmppbrowsing(defaultdir=self.config.defaultdir,
                                             rootfilesystem=self.config.rootfilesystem)
        # dictionary used for deploy
        self.machineWakeOnLan = {}
        self.machineDeploy = {}

        # Clear machine table
        XmppMasterDatabase().update_enable_for_agent_subscription(self.boundjid.bare)
        # clears synchros
        PkgsDatabase().clear_old_pending_synchro_package(timeseconde=900)
        self.idm = ""
        self.presencedeployment = {}
        self.updateguacamoleconfig = {}
        # Scheduler cycle before wanonlan delivery
        self.xmpppresence = {}

        self.CYCLESCHEDULER = 4
        if self.config.Booltaskdeploy:
            self.config.Boolsessionwork = True
            #if agent substitute pour deploy deconecter cette fonction.deploy
            # Interval between two scans for checking for new deployments (in seconds) 30 by default
            self.schedule('deployment scan interval', conf.deployment_scan_interval, self.scheduledeploy, repeat=True)
            # Interval between two wake on lan for a deployment (in seconds) 60 by default
            ###self.schedule('wol interval', conf.wol_interval, self.scheduledeployrecoveryjob, repeat=True)
            self.schedule('wol interval', 15, self.scheduledeployrecoveryjob, repeat=True)
            # Extra time given to receive the deployment results (in seconds).300 by default
            # After this time, the deployments will be considered as timeout
            self.schedule('deployment end timeout', conf.deployment_end_timeout, self.garbagedeploy, repeat=True)
        if self.config.Boolsessionwork:
            # Interval between two sessions checks for removing dead sessions (in seconds) 15 by default
            self.schedule('session check', conf.session_check_interval, self.handlemanagesession, repeat=True)

        self.schedule('schedulerfunction', 60, self.schedulerfunction, repeat=True)
        # Enable memory leaks checks and define interval (in seconds)
        self.timecheck = 15
        if conf.memory_leak_check:
            self.timecheck = conf.memory_leak_interval
            self.schedule('event leakmemory',self.timecheck, self.__leakmemory, repeat=True)

        # Interval for reloading plugins base (in seconds) 900 by default
        self.schedule('reload plugins base', conf.reload_plugins_base_interval, self.loadbasepluginagent, repeat=True)

        # Interval for installing new plugins on clients (in seconds) 60 by default
        self.schedule('remote update plugin', conf.remote_update_plugin_interval, self.remoteinstallPlugin, repeat=True)

        self.add_event_handler("session_start", self.start)

        # Call function
        self.add_event_handler("restartmachineasynchrone",
                               self.restartmachineasynchrone, threaded=True)
        # Called for all messages
        self.add_event_handler('message', self.message, threaded=True)
        # The groupchat_message event is triggered every time a message
        # Strophe is received from any chat room. If you too
        # Save a handler for the 'message' event, MUC messages
        # Will be processed by both managers.
        self.add_event_handler("pluginaction", self.pluginaction)

        self.add_event_handler('changed_status', self.changed_status)
        self.RSA = MsgsignedRSA("master")

    def schedulerfunction(self):
        self.manage_scheduler.process_on_event()

    def syncthingdeploy(self):
        #nanlyse la table deploy et recupere les deployement syncthing.
        iddeploylist = XmppMasterDatabase().deploysyncthingxmpp()
        if len(iddeploylist)!= 0:
            for iddeploy in iddeploylist:
                # les tables sont create
                # maintenant on appelle le plugin master de syncthing
                data = { "subaction" : "initialisation",
                            "iddeploy" : iddeploy }
                self.callpluginmasterfrommmc("deploysyncthing",
                                                data,
                                                sessionid = name_randomplus(25,
                                                pref="deploysyncthing"))

    def iqsendpulse(self, to, datain, timeout):
        # send iq synchronous message
        if type(datain) == dict or type(datain) == list:
            try:
                data = json.dumps(datain)
            except Exception as e:
                logging.error("iqsendpulse : encode json : %s" % str(e))
                return '{"err" : "%s"}' % str(e).replace('"', "'")
        elif type(datain) == unicode:
            data = str(datain)
        else:
            data = datain
        try:
            data = data.encode("base64")
        except Exception as e:
            logging.error("iqsendpulse : encode base64 : %s" % str(e))
            return '{"err" : "%s"}' % str(e).replace('"', "'")
        try:
            iq = self.make_iq_get(queryxmlns='custom_xep', ito=to)
            itemXML = ET.Element('{%s}data' % data)
            for child in iq.xml:
                if child.tag.endswith('query'):
                    child.append(itemXML)
            try:
                result = iq.send(timeout=timeout)
                if result['type'] == 'result':
                    for child in result.xml:
                        if child.tag.endswith('query'):
                            for z in child:
                                if z.tag.endswith('data'):
                                    # decode result
                                    # TODO : Replace print by log
                                    #print z.tag[1:-5]
                                    return base64.b64decode(z.tag[1:-5])
                                    try:
                                        data = base64.b64decode(z.tag[1:-5])
                                        # TODO : Replace print by log
                                        #print "RECEIVED data"
                                        #print data
                                        return data
                                    except Exception as e:
                                        logging.error("iqsendpulse : %s" % str(e))
                                        logger.error("%s" % (traceback.format_exc()))
                                        return '{"err" : "%s"}' % str(e).replace('"', "'")
                                    return "{}"
            except IqError as e:
                err_resp = e.iq
                logging.error("iqsendpulse : Iq error %s" % str(err_resp).replace('"', "'"))
                logger.error("%s" % (traceback.format_exc()))
                return '{"err" : "%s"}' % str(err_resp).replace('"', "'")

            except IqTimeout:
                logging.error("iqsendpulse : Timeout Error")
                return '{"err" : "Timeout Error"}'
        except Exception as e:
            logging.error("iqsendpulse : error %s" % str(e).replace('"', "'"))
            logger.error("%s" % (traceback.format_exc()))
            return '{"err" : "%s"}' % str(e).replace('"', "'")
        return "{}"

    def garbagedeploy(self):
        MscDatabase().xmppstage_statecurrent_xmpp()
        XmppMasterDatabase().update_status_deploy_end()

    def __leakmemory(self):
        """
            function scheduler use to chase memory leaks
        """
        from time import strftime
        import gc
        #install  module memory_profiler
        from memory_profiler import memory_usage
        # schedule deployement
        if not hasattr(self, 'countseconde'):
            self.mesuref = 0.0
            self.countseconde = 0
            self.mesure = ""
            self.mesuref = 0.0
            self.name_file_log_leak_memory = "/tmp/data.txt"

        self.countseconde += self.timecheck
        mem_usage = memory_usage(-1, interval=1, timeout=1)
        mesure = str(mem_usage[0]).replace(".",",")
        if mesure != self.mesure:
            print "__________leak memory_________"
            taillepris = (mem_usage[0] - self.mesuref)
            self.mesuref = mem_usage[0]
            fichier = open(self.name_file_log_leak_memory, "a")
            datetimewrite = strftime("%H:%M:%S")
            stem = "\n%s count %s\ntime %ss MT %.2f MiB delta [ %s Mo | %s Ko | %s Oc | %s Oc/s]\n"%( datetimewrite,
                                                                                                    gc.get_count(),
                                                                                                    self.countseconde,
                                                                                                    mem_usage[0],
                                                                                                    round(taillepris,2),
                                                                                                    round(taillepris *1024,2),
                                                                                                    round(taillepris *1024 * 1024,2),
                                                                                                    round((taillepris *1024 * 1024)/self.countseconde,2))
            fichier.write(stem)
            self.countseconde = 0
            print stem
            fichier.close()
            self.mesure = mesure
            print "______________________________"
    def sendwol(self, macadress, hostnamemachine = ""):
        listmacadress = macadress.split("||")
        for macadressdata in listmacadress:
            if macadressdata != "":
                logging.debug("wakeonlan machine  [Machine : %s]" % hostnamemachine)
                self.callpluginmasterfrommmc('wakeonlan', {'macadress': macadressdata})

    def _chunklist(self, listseq, nb = 5000):
        nbinlist, rest = divmod(len(listseq), nb)
        avg = len(listseq) / float(nbinlist + 1)
        result = []
        endlist = 0.0
        while endlist < len(listseq):
            result.append(listseq[int(endlist):int(endlist + avg)])
            endlist += avg
        return result

    def _sendwolgroup(self, listorset, nb = 5000):
        # we cut the list into several lists of 5000 mac address maximum
        try:
            listforsplit = self._chunklist(list(listorset), nb)
            for listsend in listforsplit:
                self.callpluginmasterfrommmc('wakeonlangroup',
                                            {'macadress': list(listsend)})
        except Exception:
            logger.error("%s"%(traceback.format_exc()))

    def _addsetwol( self, setdata, macadress):
        listmacadress = macadress.split("||")
        for macadressdata in listmacadress:
            setdata.add(macadressdata)

    def scheduledeployrecoveryjob(self):
        msglog=[]
        wol_set = set()
        try:
            # machine ecart temps de deploiement terminer met status a ABORT ON TIMEOUT
            result = XmppMasterDatabase().Timeouterrordeploy()
            for machine in result:
                hostnamemachine=machine['jidmachine'].split('@')[0][:-4]
                msglog.append("<span class='log_err'>Deployment timed out on machine %s</span>"%hostnamemachine)
                msglog.append("<span class='log_err'>Machine is no longer available</span>")
            for logmsg in msglog:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=machine['sessionid'],
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            date=None,
                            fromuser=machine['login'])
            msglog=[]
            #########################################################################
            machines_scheduled_deploy = XmppMasterDatabase().search_machines_from_state("DEPLOY TASK SCHEDULED")
            for machine in machines_scheduled_deploy:
                ##datetime_startcmd = datetime.strptime(machine['startcmd'], '%Y-%m-%d %H:%M:%S')
                ##datetime_endcmd = datetime.strptime(machine['startcmd'], '%Y-%m-%d %H:%M:%S')
                UUID = machine['inventoryuuid']

                resultpresence = XmppMasterDatabase().getPresenceExistuuids(UUID)
                if resultpresence[UUID][1] == 0:
                    # la machine n'est plus dans la table machine
                    ### voir le message a afficher.
                    # cas on 1 deployement est cheduler.
                    # et la machine n'existe plus. soit son uuid GLPI a changer, ou elle a ete suprimer. la machine n'existe plus.
                    msglog.append("<span class='log_err'>Machine %s disappeared "\
                        "during deployment. GLPI ID: %s</span>"%(machine['jidmachine'], UUID))
                    XmppMasterDatabase().update_state_deploy(machine['id'], "ABORT MACHINE DISAPPEARED")
                elif resultpresence[UUID][0] == 1:
                    XmppMasterDatabase().update_state_deploy(machine['id'], "WAITING MACHINE ONLINE")
                else:
                    XmppMasterDatabase().update_state_deploy(machine['id'], "WOL 3")
            for logmsg in msglog:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=machine['sessionid'],
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            date=None,
                            fromuser=machine['login'])
            msglog=[]
            ###########################################################################
            machines_wol3 = XmppMasterDatabase().search_machines_from_state("WOL 3")
            for machine in machines_wol3:
                XmppMasterDatabase().update_state_deploy(machine['id'], "WAITING MACHINE ONLINE")
                hostnamemachine=machine['jidmachine'].split('@')[0][:-4]
                msglog.append("Waiting for machine %s to be online"%hostnamemachine)
            for logmsg in msglog:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=machine['sessionid'],
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            date=None,
                            fromuser=machine['login'])
            msglog=[]
            ###########################################################################
            machines_wol2 = XmppMasterDatabase().search_machines_from_state("WOL 2")
            for machine in machines_wol2:
                if XmppMasterDatabase().getPresenceuuid(machine['inventoryuuid']):
                    # recu presence machine.
                    XmppMasterDatabase().update_state_deploy(machine['id'], "WAITING MACHINE ONLINE")
                    continue
                XmppMasterDatabase().update_state_deploy(machine['id'], "WOL 3")
                hostnamemachine=machine['jidmachine'].split('@')[0][:-4]
                self._addsetwol(wol_set, machine['macadress'])
                msglog.append("Third WOL sent to machine %s"%hostnamemachine)
            for logmsg in msglog:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=machine['sessionid'],
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            date=None,
                            fromuser=machine['login'])
            msglog=[]
            ###########################################################################
            machines_wol1 = XmppMasterDatabase().search_machines_from_state("WOL 1")
            for machine in machines_wol1:
                if XmppMasterDatabase().getPresenceuuid(machine['inventoryuuid']):
                    # recu presence machine.
                    XmppMasterDatabase().update_state_deploy(machine['id'], "WAITING MACHINE ONLINE")
                    continue
                XmppMasterDatabase().update_state_deploy(machine['id'], "WOL 2")
                hostnamemachine=machine['jidmachine'].split('@')[0][:-4]
                self._addsetwol(wol_set, machine['macadress'])
                #self.sendwol(machine['macadress'], hostnamemachine)

                msglog.append("Second WOL sent to machine %s"%hostnamemachine)
            for logmsg in msglog:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=machine['sessionid'],
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            date=None,
                            fromuser=machine['login'])
            msglog=[]
            ###########################################################################
            #relance machine off_line to on_line
            machines_waitting_online = XmppMasterDatabase().search_machines_from_state("WAITING MACHINE ONLINE")
            #### on verify si il y a des machines online dans cet ensemble
            for machine in machines_waitting_online:
                #machine WAITING MACHINE ONLINE presente ?
                data = json.loads(machine['result'])
                if XmppMasterDatabase().getPresenceuuid(machine['inventoryuuid']):
                    hostnamemachine=machine['jidmachine'].split('@')[0][:-4]
                    msg="Machine %s online. Starting deployment"%hostnamemachine
                    self.xmpplog(msg,
                                type='deploy',
                                sessionname=machine['sessionid'],
                                priority=-1,
                                action="xmpplog",
                                why=self.boundjid.bare,
                                module="Deployment | Start | Creation",
                                date=None,
                                fromuser=machine['login'])
                    XmppMasterDatabase().update_state_deploy(int(machine['id']), "DEPLOYMENT START")
                    #"relance deployement on machine online"
                    # il faut verifier qu'il y ai 1 groupe deja en syncthing.alors seulement on peut decoder de l'incorporer
                    if data['advanced']['grp'] is not None and \
                        'syncthing' in data['advanced'] and \
                            data['advanced']['syncthing'] == 1 and \
                                XmppMasterDatabase().nbsyncthingdeploy(machine['group_uuid'],
                                                                        machine['command']) > 2:
                        msg =  "Starting peer deployment on machine %s" % machine['jidmachine']
                        self.xmpplog(msg,
                                    type='deploy',
                                    sessionname=machine['sessionid'],
                                    priority=-1,
                                    action="xmpplog",
                                    why=self.boundjid.bare,
                                    module="Deployment | Start | Creation",
                                    date=None,
                                    fromuser=data['login'])
                        XmppMasterDatabase().updatedeploytosyncthing(machine['sessionid'])
                        # call plugin master syncthing
                        ###initialisation deployement syncthing
                        self.callpluginsubstitute("deploysyncthing",
                                                    data,
                                                    sessionid = machine['sessionid'])
                        self.syncthingdeploy()
                    else:
                        datasession = self.session.sessiongetdata(machine['sessionid'])
                        msglog.append("Starting deployment on machine %s from ARS %s" %(machine['jidmachine'],
                                                                                machine['jid_relay']))

                        command = {'action': "applicationdeploymentjson",
                                'base64': False,
                                'sessionid': machine['sessionid'],
                                'data': data}

                        self.send_message(mto= machine['jid_relay'],
                                        mbody=json.dumps(command),
                                        mtype='chat')
                        for logmsg in msglog:
                            self.xmpplog(logmsg,
                                        type='deploy',
                                        sessionname=machine['sessionid'],
                                        priority=-1,
                                        action="xmpplog",
                                        why=self.boundjid.bare,
                                        module="Deployment | Start | Creation",
                                        date=None,
                                        fromuser=machine['login'])
                        msglog=[]
                        if 'syncthing' in data['advanced'] and \
                            data['advanced']['syncthing'] == 1:
                            self.xmpplog("<span class='log_warn'>There are not enough machines " \
                                            "to deploy in peer mode</span>",
                                    type='deploy',
                                    sessionname=machine['sessionid'],
                                    priority=-1,
                                    action="xmpplog",
                                    why=self.boundjid.bare,
                                    module="Deployment | Start | Creation",
                                    date=None,
                                    fromuser=data['login'])
        except Exception:
            logger.error("%s"%(traceback.format_exc()))
        finally:
            #send wols
            wol_set.discard("")
            if len(wol_set):
                self._sendwolgroup(wol_set)

    def scheduledeploy(self):
        """
            # Set to pause the folders already shared into the ars.
            # Clean the syncthing deployments.
            # Search all the syncthing deployment done
            # and clean into the network and the machines
        """
        # Firstly we replace the current rule by a new one.
        # 2 transfers done limit the ARS bandwidth.
        # Be aware of the new's deploy creation, its remove the limite rate.
        # TODO
        # If 1 package is in pending state, then the limit rate is removed.
        ###########################################################################
        msg=[]
        list_ars_syncthing_pause =  XmppMasterDatabase().get_ars_for_pausing_syncthing(2)
        for arssyncthing in list_ars_syncthing_pause:
            datasend = {  "action" : "deploysyncthing",
                          "sessionid" : name_random(5, "pausesyncthing"),
                          "data" : {  "subaction" : "pausefolder",
                                      "folder" : arssyncthing[2]}
                        }
            listars = arssyncthing[1].split(",")
            for arssyncthing in listars:
                self.send_message(  mto=arssyncthing,
                                    mbody=json.dumps(datasend),
                                    mtype='chat')
        try:
            deploys_to_clean = XmppMasterDatabase().get_syncthing_deploy_to_clean()
            if type(deploys_to_clean) is list:
                for deploydata in deploys_to_clean:
                    ars = XmppMasterDatabase().get_list_ars_from_cluster(deploydata['numcluster'])
                    datasend = {"action" : "deploysyncthing",
                                "sessionid" : name_random(5, "cleansyncthing"),
                                "data" : {  "subaction" : "cleandeploy",
                                            "iddeploy" : deploydata['directory_tmp'],
                                            "jidmachines" : deploydata['jidmachines'],
                                            "jidrelays" : deploydata['jidrelays'] } }
                    for relay in ars:
                        self.send_message(  mto=relay['jid'],
                                            mbody=json.dumps(datasend),
                                            mtype='chat')
                    XmppMasterDatabase().refresh_syncthing_deploy_clean(deploydata['id'])
        except Exception:
            pass
        listobjnoexist = []
        listobjsupp = []
        #search deploy to rumming
        resultdeploymachine = MscDatabase().deployxmpp()

        for deployobject in resultdeploymachine:
            # creation deployment
            UUID = deployobject['UUID']
            resultpresence = XmppMasterDatabase().getPresenceExistuuids(UUID)
            if resultpresence[UUID][1] == 0:
                sessiondeployementless = name_random(5, "missingagent")
                # machine dans GLPI mais pas enregistré sur tavle machine xmpp.
                listobjnoexist.append(deployobject)
                if not self.boolimportglpi:
                     try:
                         from mmc.plugins.glpi.database import Glpi
                         self.boolimportglpi = True
                     except ImportError:
                         return
                machine = Glpi().getMachineByUUID(UUID)
                #incrition dans deploiement cette machine sans agent

                XmppMasterDatabase().adddeploy(deployobject['commandid'],
                                                deployobject['name'],
                                                deployobject['name'],
                                                deployobject['name'],
                                                UUID,
                                                deployobject['login'],
                                                "ABORT MISSING AGENT",
                                                sessiondeployementless,
                                                user=deployobject['login'],
                                                login=deployobject['login'],
                                                title=deployobject['title'],
                                                group_uuid=deployobject['GUID'],
                                                startcmd=deployobject['start_date'],
                                                endcmd=deployobject['end_date'],
                                                macadress=deployobject['mac'],
                                                result = "",
                                                syncthing = 0)

                msg.append("<span class='log_err'>Agent missing on machine %s. " \
                            "Deployment impossible : GLPI ID is %s</span>"%(deployobject['name'],
                                                                             UUID))
                msg.append("Action : Check that the machine "\
                    "agent is working, or install the agent on the"\
                        " machine %s (%s) if it is missing."%(deployobject['name'],
                                                                       UUID))
                for logmsg in msg:
                    self.xmpplog(logmsg,
                             type='deploy',
                             sessionname=sessiondeployementless,
                             priority=-1,
                             action="xmpplog",
                             why=self.boundjid.bare,
                             module="Deployment | Start | Creation",
                             date=None,
                             fromuser=deployobject['login'])
                continue

            if datetime.now() < deployobject['start_date']:
                deployobject['wol'] = 2 #
            else:
                if resultpresence[UUID][0] == 1:
                    # If a machine is present, add deployment in deploy list to manage.
                    deployobject['wol'] = 0
                else:
                    deployobject['wol'] = 1
            try:
                self.machineDeploy[UUID].append(deployobject)
            except:
                #creation list deployement
                self.machineDeploy[UUID] = []
                self.machineDeploy[UUID].append(deployobject)

        listobjsupp = []
        nbdeploy=len(self.machineDeploy)
        for deployuuid in self.machineDeploy:
            try:
                deployobject = self.machineDeploy[deployuuid].pop(0)
                listobjsupp.append(deployuuid)
                logging.debug("send deploy on machine %s package %s" %
                              (deployuuid, deployobject['pakkageid']))
                self.applicationdeployjsonUuidMachineAndUuidPackage(deployuuid,
                                                                    deployobject['pakkageid'],
                                                                    deployobject['commandid'],
                                                                    deployobject['login'],
                                                                    30,
                                                                    encodebase64=False,
                                                                    start_date=deployobject['start_date'],
                                                                    end_date=deployobject['end_date'],
                                                                    title=deployobject['title'],
                                                                    macadress=deployobject['mac'],
                                                                    GUID=deployobject['GUID'],
                                                                    nbdeploy=nbdeploy,
                                                                    wol=deployobject['wol'])
            except Exception:
                listobjsupp.append(deployuuid)
            if deployobject['wol'] == 1:
                listmacadress = [x.strip() for x in deployobject['mac'].split("||")]
                for macadressdata in listmacadress:
                    self._addsetwol(self.wolglobal_set, macadressdata)
        self.wolglobal_set.discard("")
        if len(self.wolglobal_set):
            self._sendwolgroup(self.wolglobal_set)
        self.wolglobal_set.clear()
        for objsupp in listobjsupp:
            try:
                del self.machineDeploy[objsupp]
            except Exception:
                pass

    def start(self, event):
        if self.config.executiontimeplugins:
            cmd = "cat /proc/%s/status | grep Threads"%os.getpid()
            obj = simplecommandstr(cmd)
            file_put_contents("/tmp/Execution_time_plugin.txt",
                              "%s | %s \n" %(str(datetime.now()),
                              obj['result'] ))
        #self.get_roster()
        #try:
            #self.get_roster()
        #except IqError as err:
            #print('Error: %s' % err.iq['error']['condition'])
        #except IqTimeout:
            #print('Error: Request timed out')
        self.send_presence()
        chatroomjoin = [self.config.confjidchatroom]
        for chatroom in chatroomjoin:
            if chatroom == self.config.confjidchatroom:
                passwordchatroom = self.config.confpasswordmuc
            else:
                passwordchatroom = self.config.passwordconnexionmuc

            self.plugin['xep_0045'].joinMUC(chatroom,
                                            self.config.NickName,
                                            password=passwordchatroom,
                                            wait=True)
        self.logtopulse('Start agent Master', type="MASTER", who=self.boundjid.bare)
        listplugins = [re.sub('plugin_', '', '.'.join(f.split('.')[:-1]))
                       for f in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "pluginsmaster"))
                       if f.startswith("plugin_auto") and f.endswith(".py")]
        logging.debug("=====================================================")
        logging.debug("direct load plugin plugin_auto...")
        logging.debug("=====================================================")
        for plugin in listplugins:
            # Load the plugin and start action
            try:
                logging.debug("Calling plugin %s " % plugin)
                call_plugin(plugin, self)
            except TypeError:
                logging.error("TypeError: executing plugin %s %s" % (plugin, sys.exc_info()[0]))
                logger.error("%s" % (traceback.format_exc()))
            except Exception as e:
                logging.error("Executing plugin %s %s" % (plugin, str(e)))
                logger.error("%s" % (traceback.format_exc()))
        logging.debug("===========END LOAD plugin type auto=================\n")
        #charge plugin start automatiquement
        #call plugin start
        logging.debug("================================================================")
        logging.debug("load plugin start. plugin for loaded plugin from pluginliststart")
        logging.debug("================================================================")
        startparameter={
                        "action": "start",
                        "sessionid" : name_random(6, "start"),
                        "ret" : 0,
                        "base64" : False,
                        "data" : {}}
        dataerreur={ "action" : "result" + startparameter["action"],
                     "data" : { "msg" : "error plugin : " + startparameter["action"]},
                     'sessionid' : startparameter['sessionid'],
                     'ret' : 255,
                     'base64' : False}
        msg = {'from' : self.boundjid.bare, "to" : self.boundjid.bare, 'type' : 'chat' }
        if not 'data' in startparameter:
            startparameter['data'] = {}
        #module = "%s/plugin_%s.py"%(self.modulepath,  startparameter["action"])
        call_plugin( "start",
                     self,
                     startparameter["action"],
                     startparameter['sessionid'],
                     startparameter['data'],
                     msg,
                     dataerreur)
        logging.debug("====================END PLUGIN START=============================\n")
        # reinitialize of relay server charge
        msg_ars_init_charge = {'action': "cluster",
                               'sessionid': name_random(5, "clusterchargeinit"),
                               'data': {'subaction': 'startmmc'} }
        for ars in  XmppMasterDatabase().get_List_jid_ServerRelay_enable():
            self.send_message(mto=ars[0],
                              mbody=json.dumps(msg_ars_init_charge),
                              mtype='chat')

    def xmpplog(self,
                text,
                type = 'noset',
                sessionname = '',
                priority = 0,
                action = "xmpplog",
                who = "",
                how = "",
                why = "",
                module = "",
                date = None ,
                fromuser = "",
                touser = ""):
        if who == "":
            who = self.boundjid.bare
        XmppMasterDatabase().setlogxmpp(text,
                                        type=type,
                                        sessionname=sessionname,
                                        priority=priority,
                                        who=who,
                                        how=how,
                                        why=why,
                                        module=module,
                                        action='',
                                        touser=touser,
                                        fromuser= fromuser)

    def logtopulse(self, text, type='noset', sessionname='', priority=0, who='', ret = 0):
        if who == "":
            who = self.boundjid.bare
        XmppMasterDatabase().setlogxmpp(text,
                                        type=type,
                                        sessionname=sessionname,
                                        priority=priority,
                                        who=who,
                                        how="",
                                        why="",
                                        module="MASTER_LOG",
                                        action='',
                                        touser="",
                                        fromuser= "MASTER")

    def changed_status(self, msg_changed_status):
        try:
            if msg_changed_status['from'].resource == 'MASTER':
                return
        except Exception:
            pass
        logger.debug("%s %s" % (msg_changed_status['from'], msg_changed_status['type']))
        if msg_changed_status['type'] == 'unavailable':
            try:
                result = XmppMasterDatabase().initialisePresenceMachine(msg_changed_status['from'])
                if result is None or len(result) == 0:
                    return
                if "type" in result and result['type'] == "relayserver":
                    # recover list of cluster ARS
                    listrelayserver = XmppMasterDatabase().getRelayServerofclusterFromjidars(
                        str(msg_changed_status['from']))
                    cluster = {'action': "cluster",
                               'sessionid': name_random(5, "cluster"),
                               'data': {'subaction': 'initclusterlist',
                                         'data': listrelayserver
                                        }
                               }
                    # all Relays server in the cluster are notified.
                    for ARScluster in listrelayserver:
                        self.send_message(mto=ARScluster,
                                          mbody=json.dumps(cluster),
                                          mtype='chat')
                else:
                    obj = XmppMasterDatabase().getcluster_resources(msg_changed_status['from'])
                    arscluster = []
                    for t in obj['resource']:
                        if t['jidmachine'] == msg_changed_status['from']:
                            logger.debug("*** resource recovery on ARS %s for deploy"\
                                "sessionid %s on machine  (connection loss) %s " % (t['jidrelay'],
                                                                                    t['sessionid'],
                                                                                    t['hostname']))
                            arscluster.append([ t['jidrelay'],
                                                t['sessionid'],
                                                t['hostname'],
                                                t['jidmachine'] ])
                            ret = XmppMasterDatabase().updatedeploystate1(t['sessionid'], "DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)")
                            if ret >= 1:
                                logger.debug("Update deploy Status for Machine OffLine %s"%t['jidmachine'])
                                self.xmpplog("Freeing deployment resource on ARS %s"\
                                    "sessionid %s on machine %s (connection loss)" % (t['jidrelay'],
                                                                                        t['sessionid'],
                                                                                        t['hostname']),
                                    type = 'deploy',
                                    sessionname = t['sessionid'],
                                    priority = -1,
                                    action = "xmpplog",
                                    who = "",
                                    how = "",
                                    why =  t['jidmachine'],
                                    module = "Deployment| Notify | Cluster",
                                    date = None,
                                    fromuser = "",
                                    touser = "")
                                self.xmpplog('Waiting for reboot',
                                    type = 'deploy',
                                    sessionname = t['sessionid'],
                                    priority = -1,
                                    action = "xmpplog",
                                    who =  t['jidmachine'],
                                    how = "",
                                    why = "",
                                    module = "Deployment | Error | Terminate | Notify",
                                    date = None ,
                                    fromuser = "master",
                                    touser = "")
                    #arscluster = list(set(arscluster))
                    if len(arscluster) > 0:
                        #logger.debug("*** START SEND MSG ARS")
                        listrelayserver = XmppMasterDatabase().getRelayServer(enable = True)
                        cluster = { 'action': "cluster",
                                    'sessionid': name_random(5, "cluster"),
                                    'data': {'subaction': 'removeresource',
                                             'data': { "jidmachine" :str(msg_changed_status['from'])
                                             }
                                    }
                         }
                        #logger.debug("*** list relayserver")
                        for ars in listrelayserver:
                            logger.debug("removeresource on  %s for machine %s "%(ars,str(msg_changed_status['from'])))
                            self.send_message(mto=ars['jid'],
                                              mbody=json.dumps(cluster),
                                              mtype='chat')
            except:
                logger.error("%s"%(traceback.format_exc()))
            self.showListClient()
        elif msg_changed_status['type'] == "available":
            result = XmppMasterDatabase().initialisePresenceMachine(msg_changed_status['from'],
                                                                    presence=1)
            if result is None or len(result) == 0:
                return
            if "type" in result and result['type'] == "machine":
                try:
                    if "reconf" in result and result['reconf'] == 1:
                        result1 = self.iqsendpulse(msg_changed_status['from'],
                                                        { "action": "information",
                                                            "data": { "listinformation" : ["force_reconf"],
                                                                    "param" : {} }},
                                                        10)
                except Exception:
                    pass
                XmppMasterDatabase().updateMachinereconf(msg_changed_status['from'])

    def showListClient(self):
        if self.config.showinfomaster:
            self.presencedeployment = {}
            listrs = XmppMasterDatabase().listjidRSdeploy()
            if len(listrs) != 0:
                for i in listrs:
                    li = XmppMasterDatabase().listmachinesfromdeploy(i[0])
                    logger.info("RS [%s] for deploy on %s Machine" % (i[0], len(li)-1))
                    logger.debug('{0:5}|{1:7}|{2:20}|{3:35}|{4:55}'.format("type",
                                                                           "uuid",
                                                                           "Machine",
                                                                           "jid",
                                                                           "platform"))
                    for j in li:
                        if j[9] == 'relayserver':
                            TY = 'RSer'
                        else:
                            TY = "Mach"
                        logger.debug('{0:5}|{1:7}|{2:20}|{3:35}|{4:55}'.format(TY, j[5],
                                                                               j[4],
                                                                               j[1],
                                                                               j[2]))
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
                                                       encodebase64=False,
                                                       start_date=None,
                                                       end_date=None,
                                                       macadress=None,
                                                       GUID=None,
                                                       title=None,
                                                       nbdeploy=-1,
                                                       wol=0):
        sessiondeployementless = name_random(5, "arsdeploy")
        msg=[]
        name = managepackage.getnamepackagefromuuidpackage(uuidpackage)
        if name is not None:
            return self.applicationdeployjsonuuid(str(uuidmachine),
                                                  str(name),
                                                  idcommand,
                                                  login,
                                                  time,
                                                  start_date=start_date,
                                                  end_date=end_date,
                                                  macadress=macadress,
                                                  GUID=GUID,
                                                  title=title,
                                                  nbdeploy=nbdeploy,
                                                  wol=wol)
        else:
            XmppMasterDatabase().adddeploy( idcommand,
                                            "%s____"%uuidmachine,
                                            "package %s"%uuidpackage,
                                            "error_name_package____",
                                            uuidmachine,
                                            title,
                                            "ABORT PACKAGE IDENTIFIER MISSING",
                                            sessiondeployementless,
                                            user=login,
                                            login=login,
                                            title=title,
                                            group_uuid=GUID,
                                            startcmd=start_date,
                                            endcmd=end_date,
                                            macadress=macadress,
                                            result = "",
                                            syncthing = 0)
            msg.append("<span class='log_err'>Package identifier misssing for %s</span>"%uuidpackage)
            msg.append("Action : Check the package %s"%(uuidpackage))
            for logmsg in msg:
                self.xmpplog(logmsg,
                             type='deploy',
                             sessionname=sessiondeployementless,
                             priority=-1,
                             action="xmpplog",
                             why=self.boundjid.bare,
                             module="Deployment | Start | Creation",
                             date=None,
                             fromuser=login)
            logger.warn('%s package name missing'%uuidpackage)
            return False

    def applicationdeployjsonuuid(self,
                                  uuidmachine,
                                  name,
                                  idcommand,
                                  login,
                                  time,
                                  encodebase64=False,
                                  uuidpackage="",
                                  start_date=None,
                                  end_date=None,
                                  title=None,
                                  macadress=None,
                                  GUID=None,
                                  nbdeploy=-1,
                                  wol=0):
        try:
            sessiondeployementless = name_random(5, "arsdeploy")
            msg=[]
            # search group deploy and jid machine
            objmachine = XmppMasterDatabase().getGuacamoleRelayServerMachineUuid(uuidmachine, None)
            jidrelay = objmachine['groupdeploy']
            jidmachine = objmachine['jid']
            keysyncthing = objmachine['keysyncthing']
            if jidmachine != None and jidmachine != "" and jidrelay != None and jidrelay != "":
                # il y a 1 ARS pour le deploiement
                # on regarde si celui-ci est up dans la table machine
                ARSsearch = XmppMasterDatabase().getMachinefromjid(jidrelay)
                if ARSsearch['enabled'] == 0:
                    msg.append("<span class='log_err'>ARS %s for deployment is down.</span>"%jidrelay)
                    msg.append("Action : Either restart it or rerun the configurator "\
                                "on the machine %s to use another ARS"%(name))
                    msg.append("Searching alternative ARS for deployment")
                    # il faut recherche si on trouve 1 alternative. dans le cluster
                    # on cherche 1 ars disponible et up dans son cluster.
                    cluster = XmppMasterDatabase().clusterlistars(enabled=None)
                    trouver = False
                    for  i in range(1, len(cluster)+1):
                        nbars = len(cluster[i]['listarscluster'])
                        if jidrelay in cluster[i]['listarscluster']:
                            if nbars < 2:
                                msg.append("<span class='log_err'>No alternative ARS found</span>")
                                msg.append("Action : Either restart it or rerun the configurator "\
                                            "on the machine %s to use another ARS"%(name))
                                XmppMasterDatabase().adddeploy(idcommand,
                                                                jidmachine,
                                                                jidrelay,
                                                                name,
                                                                uuidmachine,
                                                                title,
                                                                "ABORT RELAY DOWN",
                                                                sessiondeployementless,
                                                                user=login,
                                                                login=login,
                                                                title=title,
                                                                group_uuid=GUID,
                                                                startcmd=start_date,
                                                                endcmd=end_date,
                                                                macadress=macadress,
                                                                result = "",
                                                                syncthing = 0)
                                for logmsg in msg:
                                    self.xmpplog(logmsg,
                                                type='deploy',
                                                sessionname=sessiondeployementless,
                                                priority=-1,
                                                action="xmpplog",
                                                why=self.boundjid.bare,
                                                module="Deployment | Start | Creation",
                                                fromuser=login)
                                logger.error("deploy %s error on machine %s ARS down" % (name, uuidmachine))
                                return False
                            else:
                                cluster[i]['listarscluster'].remove(jidrelay)
                                nbars = len(cluster[i]['listarscluster'])
                                nbint = random.randint(0, nbars-1)
                                arsalternative = cluster[i]['listarscluster'][nbint]

                                msg.append("<span class='log_err'>ARS %s for deployment is "\
                                            "down. Use alternative ARS for deployment %s. ARS "\
                                                " %s must be restarted</span>"%(jidrelay,arsalternative,jidrelay) )
                                jidrelay = arsalternative
                                ARSsearch = XmppMasterDatabase().getMachinefromjid(jidrelay)
                                if ARSsearch['enabled'] == 1:
                                    trouver = True
                                    break

                    if not trouver:
                        sessiondeployementless = name_random(5, "missinggroupdeploy")
                        XmppMasterDatabase().adddeploy(idcommand,
                                                        jidmachine,
                                                        jidrelay,
                                                        name,
                                                        uuidmachine,
                                                        title,
                                                        "ABORT ALTERNATIVE RELAYS DOWN",
                                                        sessiondeployementless,
                                                        user=login,
                                                        login=login,
                                                        title=title,
                                                        group_uuid=GUID,
                                                        startcmd=start_date,
                                                        endcmd=end_date,
                                                        macadress=macadress,
                                                        result = "",
                                                        syncthing = 0)
                        msg.append("<span class='log_err'>Alternative ARS Down</span>")
                        msg.append("Action : check ARS cluster.")
                        for logmsg in msg:
                            self.xmpplog(logmsg,
                                        type='deploy',
                                        sessionname=sessiondeployementless,
                                        priority=-1,
                                        action="xmpplog",
                                        why=self.boundjid.bare,
                                        module="Deployment | Start | Creation",
                                        fromuser=login)
                        logger.error("deploy error cluster ARS")
                        return False
                else:
                    trouver = True
                #run deploiement
                return self.applicationdeploymentjson(jidrelay,
                                                        jidmachine,
                                                        idcommand,
                                                        login,
                                                        name,
                                                        time,
                                                        encodebase64=False,
                                                        uuidmachine=uuidmachine,
                                                        start_date=start_date,
                                                        end_date=end_date,
                                                        title=title,
                                                        macadress=macadress,
                                                        GUID=GUID,
                                                        keysyncthing = keysyncthing,
                                                        nbdeploy=nbdeploy,
                                                        wol=wol,
                                                        msg=msg)
            else:
                sessiondeployementless = name_random(5, "missinggroupdeploy")
                XmppMasterDatabase().adddeploy(idcommand,
                                                jidmachine,
                                                jidrelay,
                                                name,
                                                uuidmachine,
                                                title,
                                                "ABORT INFO RELAY MISSING",
                                                sessiondeployementless,
                                                user=login,
                                                login=login,
                                                title=title,
                                                group_uuid=GUID,
                                                startcmd=start_date,
                                                endcmd=end_date,
                                                macadress=macadress,
                                                result = "",
                                                syncthing = 0)
                msg.append("<span class='log_err'>ARS for deployment is missing for machine %s </span>"%uuidmachine)
                msg.append("Action : The configurator must be restarted on the machine.")
                for logmsg in msg:
                    self.xmpplog(logmsg,
                                type='deploy',
                                sessionname=sessiondeployementless,
                                priority=-1,
                                action="xmpplog",
                                why=self.boundjid.bare,
                                module="Deployment | Start | Creation",
                                fromuser=login)
                logger.error("deploy %s error on machine %s" % (name, uuidmachine))
                return False
        except:
            logger.error("%s" % (traceback.format_exc()))
            logger.error("deploy %s error on machine %s" % (name, uuidmachine))
            XmppMasterDatabase().adddeploy( idcommand,
                                            jidmachine,
                                            jidrelay,
                                            name,
                                            uuidmachine,
                                            title,
                                            "ERROR UNKNOWN ERROR",
                                            sessiondeployementless,
                                            user=login,
                                            login=login,
                                            title=title,
                                            group_uuid=GUID,
                                            startcmd=start_date,
                                            endcmd=end_date,
                                            macadress=macadress,
                                            result = "",
                                            syncthing = 0)
            msg.append("<span class='log_err'>Error creating deployment on machine %s "\
                    "[%s]</span>"%(name, uuidmachine))
            for logmsg in msg:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=sessiondeployementless,
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            fromuser=login)
            return False

    def parsexmppjsonfile(self, path):
        ### puts the words False in lowercase.
        datastr = file_get_contents(path)
        datastr = re.sub(r"(?i) *: *false", " : false", datastr)
        datastr = re.sub(r"(?i) *: *true", " : true", datastr)
        file_put_contents(path, datastr)

    def totimestamp(self, dt, epoch=datetime(1970,1,1)):
        td = dt - epoch
        # return td.total_seconds()
        return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6

    def applicationdeploymentjson(self,
                                  jidrelay,
                                  jidmachine,
                                  idcommand,
                                  login,
                                  name,
                                  time,
                                  encodebase64=False,
                                  uuidmachine="",
                                  start_date=None,
                                  end_date=None,
                                  title=None,
                                  macadress=None,
                                  GUID=None,
                                  keysyncthing = "",
                                  nbdeploy=-1,
                                  wol=0,
                                  msg=[]):
        """ For a deployment
        1st action: synchronizes the previous package name
        The package is already on the machine and also in relay server.
        """
        sessiondeployementless = name_random(5, "arsdeploy")
        if managepackage.getversionpackagename(name) is None:
            logger.error("deploy %s error package name version missing" % (name))
            msg.append("<span class='log_err'>Package name or version missing for %s</span>"%(name))
            msg.append("Action : check the package %s"%name)
            XmppMasterDatabase().adddeploy(idcommand,
                                            jidmachine,
                                            jidrelay,
                                            name,
                                            uuidmachine,
                                            title,
                                            "ABORT PACKAGE VERSION MISSING",
                                            sessiondeployementless,
                                            user=login,
                                            login=login,
                                            title=title,
                                            group_uuid=GUID,
                                            startcmd=start_date,
                                            endcmd=end_date,
                                            macadress=macadress,
                                            result = "",
                                            syncthing = 0)
            for logmsg in msg:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=sessiondeployementless,
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            fromuser=login)
            return False
        # Name the event
        path = managepackage.getpathpackagename(name)
        if path is None:
            msg.append("<span class='log_err'>Package name missing in package %s</span>"%(name))
            msg.append("Action : check the package %s"%(name))
            XmppMasterDatabase().adddeploy(idcommand,
                                            jidmachine,
                                            jidrelay,
                                            name,
                                            uuidmachine,
                                            title,
                                            "ABORT PACKAGE NAME MISSING",
                                            sessiondeployementless,
                                            user=login,
                                            login=login,
                                            title=title,
                                            group_uuid=GUID,
                                            startcmd=start_date,
                                            endcmd=end_date,
                                            macadress=macadress,
                                            result = "",
                                            syncthing = 0)
            for logmsg in msg:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=sessiondeployementless,
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            fromuser=login)
            logger.error("package Name missing (%s)" % (name))
            return False
        descript = managepackage.loadjsonfile(os.path.join(path, 'xmppdeploy.json'))

        self.parsexmppjsonfile(os.path.join(path, 'xmppdeploy.json'))
        if descript is None:
            XmppMasterDatabase().adddeploy(idcommand,
                                            jidmachine,
                                            jidrelay,
                                            name,
                                            uuidmachine,
                                            title,
                                            "ABORT DESCRIPTOR MISSING",
                                            sessiondeployementless,
                                            user=login,
                                            login=login,
                                            title=title,
                                            group_uuid=GUID,
                                            startcmd=start_date,
                                            endcmd=end_date,
                                            macadress=macadress,
                                            result = "",
                                            syncthing = 0)
            msg.append("<span class='log_err'>Descriptor xmppdeploy.json " \
                        "missing for %s [%s]</span>"%(name, uuidmachine))
            msg.append("Action : Find out why xmppdeploy.json file is missing.")
            for logmsg in msg:
                self.xmpplog(logmsg,
                            type='deploy',
                            sessionname=sessiondeployementless,
                            priority=-1,
                            action="xmpplog",
                            why=self.boundjid.bare,
                            module="Deployment | Start | Creation",
                            fromuser=login)
            logger.error("deploy %s on %s  error : xmppdeploy.json missing" % (name, uuidmachine))
            return False
        objdeployadvanced = XmppMasterDatabase().datacmddeploy(idcommand)

        if jidmachine != None and jidmachine != "" and jidrelay != None and jidrelay != "":
            userjid=jid.JID(jidrelay).user
            iprelay = XmppMasterDatabase().ipserverARS(userjid)[0]
            ippackageserver =   XmppMasterDatabase().ippackageserver(userjid)[0]
            portpackageserver = XmppMasterDatabase().portpackageserver(userjid)[0]
        else:
            iprelay = ""
            ippackageserver =   ""
            portpackageserver = ""
            wol = 3
        data = {"name": name,
                "login": login,
                "idcmd": idcommand,
                "advanced": objdeployadvanced,
                "stardate" : self.totimestamp(start_date),
                "enddate" : self.totimestamp(end_date),
                'methodetransfert': 'pushrsync',
                "path": path,
                "packagefile": os.listdir(path),
                "jidrelay": jidrelay,
                "jidmachine": jidmachine,
                "jidmaster": self.boundjid.bare,
                "iprelay":  iprelay,
                "ippackageserver": ippackageserver,
                "portpackageserver":  portpackageserver,
                "ipmachine": XmppMasterDatabase().ipfromjid(jidmachine, None)[0],
                "ipmaster": self.config.Server,
                "Dtypequery": "TQ",
                "Devent": "DEPLOYMENT START",
                "uuid": uuidmachine,
                "descriptor": descript,
                "transfert": True,
                "nbdeploy" : nbdeploy
                }
        #TODO on verify dans la table syncthing machine
        # si il n'y a pas un partage syncthing en cour pour cette machine
        # si c'est la cas on ignore cette machine car deja en deploy.
        #res = XmppMasterDatabase().deploy_machine_partage_exist( jidmachine,
                                        #descript['info']['packageUuid'])
        #if len(res) > 0:
            #print "il existe 1 deployement de ce package [%s]"\
                #"sur la machine [%s]"%(descript['info']['packageUuid'],
                                       #jidmachine)
            #logger.debug("il existe 1 deployement de ce package [%s]"\
                #"sur la machine [%s]"%(descript['info']['packageUuid'],
                                       #jidmachine))
            #return

        # todo rattacher 1 deployement d'un package d'une machine si partage syncthing sur cluster existe deja pour d'autre machines.
        # res = XmppMasterDatabase().getnumcluster_for_ars(jidrelay)

        ###### ici on peut savoir si c'est 1 groupe et si syncthing est demande
        if wol == 3:
            state="GROUP DEPLOY MISSING"
            data['wol'] = 2
            data['mac'] = macadress #use macadress for WOL
            sessionid = self.createsessionfordeploydiffered(data)
            result = json.dumps(data, indent = 4)
            msg.append("Machine %s is ready for deployment" % jidmachine)
        if wol == 2:
            state="DEPLOY TASK SCHEDULED"
            data['wol'] = 2
            data['mac'] = macadress #use macadress for WOL
            sessionid = self.createsessionfordeploydiffered(data)
            result = json.dumps(data, indent = 4)
            msg.append("Machine %s is ready for deployment" % jidmachine)
        elif wol == 1:
            state = "WOL 1"
            data['wol'] = 1
            data['mac'] = macadress #use macadress for WOL
            sessionid = self.createsessionfordeploydiffered(data)
            result = json.dumps(data, indent = 4)
            msg.append("Machine %s online" % jidmachine)
            msg.append("First WOL sent to machine %s" % uuidmachine)
        else:
            state = "DEPLOYMENT START"
            data['wol'] = 0
            #data['advanced']['syncthing'] = 1
            if data['advanced']['grp'] != None and \
                'syncthing' in data['advanced'] and \
                data['advanced']['syncthing'] == 1 and \
                    nbdeploy > 2:
                # deploiement avec syncthing
                # call plugin preparesyncthing on master or assesseur master
                # addition session
                # send deploy descriptor to machine
                sessionid = self.send_session_command( jidmachine,
                                                    "deploysyncthing",
                                                    data,
                                                    datasession=None,
                                                    encodebase64=False,
                                                    prefix = "command")
                #state = "DEPLOYMENT SYNCTHING"
                result = json.dumps(data, indent = 4)
                msg.append("Starting peer deployment on machine %s" % jidmachine)
            else:
                msg.append("Starting deployment on machine %s from ARS %s" % (jidmachine,jidrelay))
                if data['advanced']['syncthing'] == 1:
                    msg.append("<span class='log_warn'>There are not enough machines " \
                                "to deploy in peer mode</span>")

                data['advanced']['syncthing'] = 0
                result = None
                sessionid = self.send_session_command(jidrelay,
                                                    "applicationdeploymentjson",
                                                    data,
                                                    datasession=None,
                                                    encodebase64=False,
                                                    prefix = "command")
        if wol >= 1:
            avacedpara = 0
        else:
            avacedpara = data['advanced']['syncthing']
        for msglog in msg:
            self.xmpplog(msglog,
                        type='deploy',
                        sessionname=sessionid,
                        priority=-1,
                        action="xmpplog",
                        why=self.boundjid.bare,
                        module="Deployment | Start | Creation",
                        date=None,
                        fromuser=data['login'])
        XmppMasterDatabase().adddeploy(idcommand,
                                       jidmachine,
                                       jidrelay,
                                       jidmachine,
                                       uuidmachine,
                                       descript['info']['name'],
                                       state,
                                       sessionid,
                                       user="",
                                       login=login,
                                       title=title,
                                       group_uuid=GUID,
                                       startcmd=start_date,
                                       endcmd=end_date,
                                       macadress=macadress,
                                       result = result,
                                       syncthing = avacedpara)
        if data['advanced']['syncthing'] == 0:
            XmppMasterDatabase().addcluster_resources(jidmachine,
                                                      jidrelay,
                                                      jidmachine,
                                                      sessionid,
                                                      login=login,
                                                      startcmd = start_date,
                                                      endcmd = end_date)
        self.syncthingdeploy()
        return sessionid

    def pluginaction(self, rep):
        if 'sessionid' in rep.keys():
            sessiondata = self.session.sessionfromsessiondata(rep['sessionid'])
            if 'shell' in sessiondata.getdatasession().keys() and \
                sessiondata.getdatasession()['shell']:
                self.send_message(mto=jid.JID("commandrelay@localhost"),
                                  mbody=json.dumps(rep),
                                  mtype='chat')
        logger.info("Log action plugin %s!" % rep)

    def displayData(self, data):
        if self.config.showinfomaster:
            logger.info("--------------------------")
            if 'action' in data and data['action'] == 'connectionconf':
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

            logger.debug("DETAILED INFORMATION")
            if 'information' in data:
                logger.debug("%s" % json.dumps(data['information'], indent=4, sort_keys=True))

    def handlemanagesession(self):
        self.session.decrementesessiondatainfo()

    def loadbasepluginagent(self):
        self.loadPluginList()
        self.loadPluginschedulerList()
        self.loadfingerprintagentbase()

    def loadfingerprintagentbase(self):
        logger.debug("Load finger print base agent")
        self.autoupdatebool = self.config.autoupdatebyrelay or self.config.autoupdate
        self.Update_Remote_Agentlist = Update_Remote_Agent(self.config.diragentbase,
                                                           self.autoupdatebool)

    def loadPluginList(self):
        PkgsDatabase().clear_old_pending_synchro_package(timeseconde=3600)
        logger.debug("Load and Verify base plugin")
        self.plugindata = {}
        self.plugintype = {}
        self.pluginagentmin = {}
        for element in [x for x in os.listdir(self.config.dirplugins) if x[-3:] == ".py" and x[:7] == "plugin_"]:
            element_name = os.path.join(self.config.dirplugins, element)
            # verify syntax error for plugin python
            # we do not deploy a plugin with syntax error.
            if os.system("python -m py_compile \"%s\"" % element_name) == 0:
                f = open(element_name, 'r')
                lignes = f.readlines()
                f.close()
                for ligne in lignes:
                    if 'VERSION' in ligne and 'NAME' in ligne:
                        l = ligne.split("=")
                        plugin = eval(l[1])
                        self.plugindata[plugin['NAME']] = plugin['VERSION']
                        try:
                            self.plugintype[plugin['NAME']] = plugin['TYPE']
                        except:
                            self.plugintype[plugin['NAME']] = "machine"
                        try:
                            self.pluginagentmin[plugin['NAME']] = plugin['VERSIONAGENT']
                        except:
                            self.pluginagentmin[plugin['NAME']] = "0.0.0"
                        break
            else:
                logger.error("As long as the ERROR SYNTAX is not fixed, the plugin [%s] is ignored." % os.path.join(
                    self.config.dirplugins, element))

    def loadPluginschedulerList(self):
        logger.debug("Load and Verify base plugin scheduler")
        self.plugindatascheduler = {}
        self.plugintypescheduler = {}
        for element in os.listdir(self.config.dirschedulerplugins):
            if element.endswith('.py') and element.startswith('scheduling_'):
                f = open(os.path.join(self.config.dirschedulerplugins, element), 'r')
                lignes = f.readlines()
                f.close()
                for ligne in lignes:
                    if 'VERSION' in ligne and 'NAME' in ligne:
                        line = ligne.split("=")
                        plugin = eval(line[1])
                        self.plugindatascheduler[plugin['NAME']] = plugin['VERSION']
                        try:
                            self.plugintypescheduler[plugin['NAME']] = plugin['TYPE']
                        except:
                            self.plugintypescheduler[plugin['NAME']] = "machine"
                        break

    def remoteinstallPlugin(self):
        """
            This function installs the plugins to agent M and RS
        """
        restart_machine = set()
        for indexplugin in range(0, len(self.file_deploy_plugin)):
            plugmachine = self.file_deploy_plugin.pop(0)
            if XmppMasterDatabase().getPresencejid(plugmachine['dest']):
                if plugmachine['type'] == 'deployPlugin':
                    logger.debug("install plugin normal %s to %s" %
                                 (plugmachine['plugin'], plugmachine['dest']))
                    self.deployPlugin(plugmachine['dest'], plugmachine['plugin'])
                    restart_machine.add(plugmachine['dest'])
                elif plugmachine['type'] == 'deploySchedulingPlugin':
                    # It is the updating code for the scheduling plugins.
                    pass
        for jidmachine in restart_machine:  # Itération pour chaque élément
            # call one function by message to processing asynchronous tasks and can add a tempo on restart action.
            self.event('restartmachineasynchrone', jidmachine)

    def restartmachineasynchrone(self, jid):
        waittingrestart = random.randint(10, 20)
        # TODO : Replace print by log
        # print "Restart Machine jid %s after %s secondes" % (jid, waittingrestart)
        sleep(waittingrestart)
        # TODO : Replace print by log
        # print "Restart Machine jid %s fait" % jid
        # Check if restartAgent is not called from a plugin or a lib.

        self.restartAgent(jid)

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

    def restartAgent(self, to):
        if self.config.showplugins:
            logger.info("Restart agent on %s" % (to))
        self.send_message(mto=to,
                          mbody=json.dumps({'action': 'restartbot', 'data': ''}),
                          mtype='chat')

    def deployPlugin(self, jid, plugin):
        data = ''
        fichierdata = {}
        namefile = os.path.join(self.config.dirplugins, "plugin_%s.py" % plugin)
        if os.path.isfile(namefile):
            logger.debug("File plugin found %s" % namefile)
        else:
            logger.error("File plugin found %s" % namefile)
            return
        try:
            fileplugin = open(namefile, "rb")
            data = fileplugin.read()
            fileplugin.close()
        except:
            logger.error("File read error")
            logger.error("%s" % (traceback.format_exc()))
            return
        fichierdata['action'] = 'installplugin'
        fichierdata['data'] = {}
        dd = {}
        dd['datafile'] = data
        dd['pluginname'] = "plugin_%s.py" % plugin
        fichierdata['data'] = base64.b64encode(json.dumps(dd))
        fichierdata['sessionid'] = "sans"
        fichierdata['base64'] = True
        try:
            self.send_message(mto=jid,
                              mbody=json.dumps(fichierdata),
                              mtype='chat')
        except:
            logger.error("%s" % (traceback.format_exc()))

    def deployPluginscheduled(self, msg, plugin):
        data = ''
        fichierdata = {}
        namefile = os.path.join(self.config.dirschedulerplugins, "%s.py" % plugin)
        if os.path.isfile(namefile):
            logger.debug("File plugin scheduled found %s" % namefile)
        else:
            logger.error("File plugin scheduled not found %s" % namefile)
            return
        try:
            fileplugin = open(namefile, "rb")
            data = fileplugin.read()
            fileplugin.close()
        except:
            logger.error("File read error")
            logger.error("%s" % (traceback.format_exc()))
            return
        fichierdata['action'] = 'installpluginscheduled'
        fichierdata['data'] = {}
        dd = {}
        dd['datafile'] = data
        dd['pluginname'] = "%s.py" % plugin
        fichierdata['data'] = base64.b64encode(json.dumps(dd))
        fichierdata['sessionid'] = "sans"
        fichierdata['base64'] = True
        try:
            self.send_message(mto=msg['from'],
                              mbody=json.dumps(fichierdata),
                              mtype='chat')
        except:
            traceback.print_exc(file=sys.stdout)

    def callrestartbymaster(self, to):
        restartmachine = {
            'action': "restarfrommaster",
            'sessionid': name_random(5, "restart"),
            'data': [],
            'ret': 255
        }
        self.send_message(mto=to,
                          mbody=json.dumps(restartmachine),
                          mtype='chat')
        return True

    def callshutdownbymaster(self, to, time=0, msg=""):
        shutdownmachine = {
            'action': "shutdownfrommaster",
            'sessionid': name_random(5, "shutdown"),
            'data': {'time': time, 'msg': msg},
            'ret': 0
        }
        self.send_message(mto=to,
                          mbody=json.dumps(shutdownmachine),
                          mtype='chat')
        return True

    def callvncchangepermsbymaster(self, to, askpermission=1):
        vncchangepermsonmachine = {
            'action': "vncchangepermsfrommaster",
            'sessionid': name_random(5, "vncchangeperms"),
            'data': {'askpermission': askpermission},
            'ret': 0
        }
        self.send_message(mto=to,
                          mbody=json.dumps(vncchangepermsonmachine),
                          mtype='chat')
        return True

    def callInstallKey(self, jidAM, jidARS):
        try:
            body = {'action': 'installkey',
                    'sessionid': name_random(5, "installkey"),
                    'data': {'jidAM': jidAM
                             }
                    }
            self.send_message(mto=jidARS,
                              mbody=json.dumps(body),
                              mtype='chat')
        except:
            logger.error("%s" % (traceback.format_exc()))

    def callinventory(self, to):
        try:
            body = {'action': 'inventory',
                    'sessionid': name_random(5, "inventory"),
                    'data': {}}
            self.send_message(mto=to,
                              mbody=json.dumps(body),
                              mtype='chat')
        except:
            logger.error("%s" % (traceback.format_exc()))

    def callInstallConfGuacamole(self, torelayserver, data):
        try:
            body = {'action': 'guacamoleconf',
                    'sessionid': name_random(5, "guacamoleconf"),
                    'data': data}
            self.send_message(mto=torelayserver,
                              mbody=json.dumps(body),
                              mtype='chat')
        except:
            logger.error("%s" % (traceback.format_exc()))

    def sendErrorConnectionConf(self, msg):
        reponse = {
            'action': 'resultconnectionconf',
            'sessionid': data['sessionid'],
            'data': [],
            'syncthing' : "",
            'ret': 255
        }
        self.send_message(mto=msg['from'],
                          mbody=json.dumps(reponse),
                          mtype='chat')

    def sendrsconnectiondeploychatroom(self, to, data):
        connection = {
            'action': '@@@@@deploychatroomON@@@@@',
            'sessionid': name_random(5, "deploychatroom"),
            'data': [],
            'ret': 255
        }
        self.send_message(mto=to,
                          mbody=json.dumps(connection),
                          mtype='chat')

    def MessagesAgentFromChatroomlog(self, msg, data):
        """
        Processing of the logs comming from log salon.
        TODO  supp
        """
        try:
            logger.debug("%s [%s]" % (data['data']['msg'], data['data']['tag']))
            return True
        except Exception as e:
            logger.debug("ERROR MessagesAgentFromChatroomlog %s" % (str(e)))
            logger.error("%s" % (traceback.format_exc()))
            return False

    def Showlogmessage(self, msg):
        try:
            data = json.loads(msg['body'])
            if data['action'] == 'infolog':
                logger.error(data['msg'])
                return True
            else:
                return False
        except:
            return False

    def MessagesAgentFromChatroomConfig(self, msg):
        logger.debug("MessagesAgentFromChatroomConfig")
        # Message from chatroom master
        try:
            data = json.loads(msg['body'])
            # Verify msg from chatroom master for subscription
            if data['action'] == 'connectionconf':
                """ Check machine information from agent """

                if data['adorgbymachine'] is not None and data['adorgbymachine'] != "":
                    data['adorgbymachine'] = base64.b64decode(data['adorgbymachine'])
                if data['adorgbyuser'] is not None and data['adorgbyuser'] != "":
                    data['adorgbyuser'] = base64.b64decode(data['adorgbyuser'])

                info = json.loads(base64.b64decode(data['completedatamachine']))
                data['information'] = info
                if data['ippublic'] is not None and data['ippublic'] != "":
                    data['localisationinfo'] = Localisation().geodataip(data['ippublic'])
                else:
                    data['localisationinfo'] = {}
                self.displayData(data)
            else:
                return
        except:
            return
        if data['agenttype'] == "relayserver":
            self.sendErrorConnectionConf(msg)
            return

        if not ('information' in data and 'users' in data['information'] and len(data['information']['users']) > 0):
            data['information']['users'].append("system")
        logger.debug("Search Relay Server for "
                     "connection from user %s hostname %s localisation %s" % (data['information']['users'][0],
                                                                              data['information']['info']['hostname'],
                                                                              data['localisationinfo']))
        XmppMasterDatabase().log("Search Relay server for "
                                 "connection from user %s hostname %s localisation %s" % (data['information']['users'][0],
                                                                                          data['information']['info']['hostname'],
                                                                                          data['localisationinfo']))
        XmppMasterDatabase().log("Warning no user determinated for the machine : %s " %
                                 (data['information']['info']['hostname']))

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
                logger.debug("Analysis the 1st rule")
                result1 = XmppMasterDatabase().algoruleuser(data['information']['users'][0])
                if len(result1) > 0:
                    logger.debug("Applied : Associate the relay server based on user.")
                    result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    logger.debug("The User Rule selects the relay server for machine %s user %s \n %s" % (
                        data['information']['info']['hostname'], data['information']['users'][0], result))
                    break

            # Hostname Rule : 2
            elif x[0] == 2:
                logger.debug("Analysis the 2nd rule")
                result1 = XmppMasterDatabase().algorulehostname(
                    data['information']['info']['hostname'])
                if len(result1) > 0:
                    logger.debug("applied rule Associate relay server based on hostname")
                    result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    logger.debug("The Hostname Rule selects the relay server for machine %s user %s \n %s" % (
                        data['information']['info']['hostname'], data['information']['users'][0], result))
                    break

            # Location Rule : 3
            elif x[0] == 3:
                logger.debug("Analysis the 3rd rule")
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
                            from random import randint
                            index = randint(0, nbserver-1)
                            logger.warn("Geoposition Rule returned %d relay servers for machine"
                                        "%s user %s \nPossible relay servers : id list %s " % (nbserver, data['information']['info']['hostname'],
                                                                                               data['information']['users'][0], listeserver))
                            logger.warn("ARS Random choice : %s"%listeserver[index])
                            result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(listeserver[index])
                            logger.warn("Geoposition Rule selects the relay server for machine %s user %s \n %s " % (
                                    data['information']['info']['hostname'], data['information']['users'][0], result))
                            break
                        else:
                            if relayserver != -1:
                                result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(relayserver)
                                logger.debug("Geoposition Rule selects the relay server for machine %s user %s \n %s " % (
                                    data['information']['info']['hostname'], data['information']['users'][0], result))
                                break
                            else:
                                logger.warn("algo rule 3 inderterminat")
                                continue
                except KeyError:
                    logger.error("Error algo rule 3")
                    logger.error("%s" % (traceback.format_exc()))
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
                        result = XmppMasterDatabase(
                        ).IpAndPortConnectionFromServerRelay(result1[0].id)
                        logger.debug("Subnet Rule selects the relay server for machine %s user %s \n %s" % (
                            data['information']['info']['hostname'], data['information']['users'][0], result))
                        break
                if subnetexist:
                    break

            # Default Rule : 5
            elif x[0] == 5:
                logger.debug("analysis the 5th rule : use default relay server %s" %
                             self.config.defaultrelayserverip)
                result = XmppMasterDatabase().jidrelayserverforip(self.config.defaultrelayserverip)
                break

            # Load Balancer Rule : 6
            elif x[0] == 6:
                result1 = XmppMasterDatabase().algoruleloadbalancer()
                if len(result1) > 0:
                    logger.debug("Applied : Rule Chooses the less requested ARS.")
                    result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    logger.debug("Load Balancer Rule selects the relay server for machine %s user %s \n %s" % (
                        data['information']['info']['hostname'], data['information']['users'][0], result))
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
                        result = XmppMasterDatabase(
                        ).IpAndPortConnectionFromServerRelay(result1[0].id)
                        logger.debug("AD Rule selects the relay server for machine %s user %s \n %s" % (
                            data['information']['info']['hostname'], data['information']['users'][0], result))
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
                        result = XmppMasterDatabase(
                        ).IpAndPortConnectionFromServerRelay(result1[0].id)
                        logger.debug("AD organized by User rule selects relay server for machine %s user %s \n %s" % (
                            data['information']['info']['hostname'], data['information']['users'][0], result))
                        break

            # Network Rule : 9
            elif x[0] == 9:
                # Associates relay server based on network address
                logger.debug("Analysis rule : Associate relay server based on network address")
                networkaddress = netaddr.IPNetwork(data['xmppip'] + "/" + data['xmppmask']).cidr
                logger.debug("Network address: %s" % networkaddress)
                result1 = XmppMasterDatabase().algorulebynetworkaddress(networkaddress,
                                                                        data['classutil'])
                if len(result1) > 0:
                    logger.debug("Applied Rule : Associate relay server based on network address")
                    result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    break
            # Network Rule : 10
            elif x[0] == 10:
                # Associates relay server based on network address
                logger.debug("Analysis the 10th rule : Associate relay server based on netmask adress")
                logger.debug("Net mask adress: %s" % data['xmppmask'])
                result1 = XmppMasterDatabase().algorulebynetmaskaddress(data['xmppmask'],
                                                                        data['classutil'])
                if len(result1) > 0:
                    logger.debug("Applied Rule : Associate relay server based on net Mask address")
                    result = XmppMasterDatabase().IpAndPortConnectionFromServerRelay(result1[0].id)
                    break
        try:
            logger.debug(" user %s and hostname %s [connection ip %s port : %s]" % (
                data['information']['users'][0], data['information']['info']['hostname'], result[0], result[1]))
            XmppMasterDatabase().log("[user %s hostanme %s] : Relay server for connection ip %s port %s" % (
                data['information']['users'][0], data['information']['info']['hostname'], result[0], result[1]))
        except Exception:
            logger.warning("Relay server attributed by default")
            try:
                result = XmppMasterDatabase().jidrelayserverforip(self.config.defaultrelayserverip)
            except Exception:
                logger.warn("Unable to configure the relay server : missing")
                result = [self.config.defaultrelayserverip,
                          self.config.defaultrelayserverport,
                          self.domaindefault,
                          self.config.defaultrelayserverbaseurlguacamole]
        try:
            try:
                listars = XmppMasterDatabase().getRelayServerofclusterFromjidars(result[2],
                                                                                 "static")
            except (RuntimeError, TypeError, NameError):
                msglog = "Verify configuration assessor file name assessor_agent.ini.local."\
                        "\n\terror parameter serverip "\
                            "\nsearch ipconnection in table relayserver for default ARS"\
                                "\nserverip = %s "\
                                    "configuration error"%(self.config.defaultrelayserverip)
                msglog1 = "ERROR: Unable to assign a relay server "\
                            "to an agent %s"%data['information']['info']['hostname']
                logger.error(msglog1)
                logger.error(msglog)
                return
            z = [listars[x] for x in listars]
            z1 = sorted(z, key=operator.itemgetter(4))
            arsjid = XmppMasterDatabase().getRelayServerfromjid("rspulse@pulse")
            # Start relay server agent configuration
            # we order the ARS from the least used to the most used.
            reponse = {'action': 'resultconnectionconf',
                       'sessionid': data['sessionid'],
                       'data': z1,
                       'syncthing' : self.config.announce_server,
                       'ret': 0
                       }
            self.send_message(mto=msg['from'],
                              mbody=json.dumps(reponse),
                              mtype='chat')
            #add account for delete
            self.confaccount.append(msg['from'].user)
        except Exception:
            logger.error("Unable to configure the relay server : missing")

    def messagereturnsession(self, msg):
        data = json.loads(msg['body'])
        try:
            if data['sessionid'].startswith("mcc"):
                sessionmsg = self.session.sessionevent(data['sessionid'])
                if sessionmsg is not None:
                    sessionmsg.setdatasession(data)
                    sessionmsg.callend()
                    return True
                else:
                    logger.debug("No session name")
                    pass
        except KeyError:
            return False
        return False

    def unban(self, room, jid, reason=''):
        resp = self.plugin['xep_0045'].setAffiliation(room, jid, affiliation='none', reason=reason)
        return resp

    def info_xmppmachinebyuuid(self, uuid):
        return XmppMasterDatabase().getGuacamoleRelayServerMachineUuid("UUID%s" % uuid)

    def isInventoried(self, jid):
        machine = XmppMasterDatabase().getMachinefromjid(jid)
        if machine['uuid_inventorymachine'] is None or machine['uuid_inventorymachine'] == "":
            # we try to see if we can update uuid_inventaire by querying glpi
            result = XmppMasterDatabase().listMacAdressforMachine(machine['id'])
            results = result[0].split(",")
            logging.getLogger().debug("listMacAdressforMachine   %s" % results)
            uuid = ''
            for t in results:
                if t in self.config.blacklisted_mac_addresses: continue
                computer = ComputerManager().getComputerByMac(t)
                if computer != None:
                    uuid = 'UUID' + str(computer.id)
                    logger.debug("** update uuid %s for machine %s " % (uuid, machine['jid']))
                    # update inventory
                    XmppMasterDatabase().updateMachineidinventory(uuid, machine['id'])

                    return True
        else:
            return True
        return False

    def XmppUpdateInventoried(self, jid, timewaittinginventor = 50):
        machine = {}
        rangetimewaittinginventor = int(timewaittinginventor) / 2
        try:
            machine = XmppMasterDatabase().getMachinefromjid(jid)
            if not 'id' in machine:
                for t in range( rangetimewaittinginventor ):
                    if 'id' in machine: break
                    sleep(2)
                    machine = XmppMasterDatabase().getMachinefromjid(jid)
            if 'id' in machine:
                result = XmppMasterDatabase().listMacAdressforMachine(machine['id'])
                results = result[0].split(",")
                #logging.getLogger().debug("listMacAdressforMachine   %s" % results)
                uuid = ''
                for t in results:
                    if t in self.config.blacklisted_mac_addresses: continue
                    computer = ComputerManager().getComputerByMac(t)
                    if computer != None:
                        uuid = 'UUID' + str(computer.id)
                        logger.debug("** Update uuid %s for machine %s " % (uuid, machine['jid']))
                        if machine['uuid_inventorymachine'] != "" and \
                            machine['uuid_inventorymachine'] != None:
                            logger.debug("** Update in Organization_ad uuid %s to %s " % (machine['uuid_inventorymachine'],
                                                                                        uuid))
                            XmppMasterDatabase().replace_Organization_ad_id_inventory(machine['uuid_inventorymachine'],
                                                                                    uuid)
                        XmppMasterDatabase().updateMachineidinventory(uuid, machine['id'])
                        return True
                    else:
                        logging.getLogger().warning("Incoherence in the address mac %s" % jid)
            else:
                logging.getLogger().warning("machine [%s] not present. Cant update uuid "\
                    "in machine table. Waitting %s seconds after inject inventory" % (jid, timewaittinginventor))
                return False
        except Exception:
            logger.error("** Update error on inventory %s" % (jid))
            logger.error("%s"%(traceback.format_exc()))
        return False

    # TODO : The to variable is unused
    def senddescriptormd5(self, to):
        """
        send the agent's figerprint descriptor in database to update the machine
        Update remote agent
        """
        datasend = {"action": "updateagent",
                    "data": {'subaction': 'descriptor',
                              'descriptoragent': self.Update_Remote_Agentlist.get_md5_descriptor_agent()},
                    'ret': 0,
                    'sessionid': name_random(5, "updateagent")}
        # Send catalog of files.
        logger.debug("Send descriptor to agent [%s] for update" % to)
        self.send_message(to,
                          mbody=json.dumps(datasend),
                          mtype='chat')

    def MessagesAgentFromChatroomMaster(self, msg):
        # Message from chatroom master
        # jabber routes the message.
        # if msg['from'].bare == self.config.jidchatroommaster:
            # """ message all members of chatroom master """
            # return False
        if msg['body'] == "This room is not anonymous":
            return False
        restartAgent = False
        try:
            data = json.loads(msg['body'])
            if 'action' in data and data['action'] == 'askinfo':
                # Returns machine information
                # TODO : replace print by logs
                #print json.dumps(data, indent=4)
                if not "data" in data:
                    return
                if "fromplugin" in data['data']:
                    # If item exists, redirects to the plugin named by the action
                    data['action'] = data['data']['fromplugin']
                    logger.debug("Response action is calling the plugin %s" % data['action'])
                else:
                    logger.warn(
                        "The item 'fromplugin' doesn't exist, action reponse calls the plugin %s" % data['action'])
                if not "typeinfo" in data['data']:
                    logger.error("The item 'typeinfo' doesn't exists into the message comming from %s plugin %s" % (
                        msg['from'].bare, data['action']))
                    logger.error("######\n%s\n#####" % (json.dumps(data, indent=4)))

                if data['data']['typeinfo'] == "info_xmppmachinebyuuid":
                    if not 'host' in data['data']:
                        logger.error("The host is missing for info_xmppmachinebyuuid")
                        return True
                    data['data']['host'] = data['data']['host'].upper()
                    data['data']['host'] = data['data']['host'].replace('UUID', '')
                    try:
                        integerid = int(data['data']['host'])
                    except ValueError:
                        logger.error("The inventory uuid is missing for info_xmppmachinebyuuid")
                        return True

                    # #####WORKING info_xmppmachinebyuuid######
                    func = getattr(self, "info_xmppmachinebyuuid")
                    result = func(str(integerid))
                    data['data']['infos'] = result

                    if "sendother" in data['data'] and data['data']['sendother'] != "":
                        searchjid = data['data']['sendother'].split('@')
                        sendermachine = data['data']['sendother']
                        jidmachine = dict(data)
                        for t in range(len(searchjid)):
                            try:
                                jidmachine = jidmachine[searchjid[t]]
                            except KeyError:
                                logger.error("jid point item sendother in data false.\n"
                                             "Path in the dictionary described by the keys does not exist.\n"
                                             " example {....sendother : \"autre@infos\"} jid is databpointer by data['autre']['infos']\n"
                                             " data is %s" % (json.dumps(data, indent=4)))
                                break
                        # print jidmachine
                        jidmachine = str(jidmachine)
                        if jidmachine != "":
                            self.send_message(mto=jidmachine,
                                              mbody=json.dumps(data),
                                              mtype='chat')
                            #print "send %s" % json.dumps(data)
                    if not "sendemettor" in data['data']:
                        data['data']['sendemettor'] = True
                    if data['data']['sendemettor'] == True:
                        self.send_message(mto=msg['from'],
                                          mbody=json.dumps(data),
                                          mtype='chat')
                # ########################ASK INFORMATION other#############################
                # elsif information type other
                return True

            # Check msg from chatroom master for subscription
            if 'action' in data and data['action'] == 'loginfos':
                # Process loginfotomaster
                logger.debug("** Processing log from %s" % msg['from'].bare)
                self.MessagesAgentFromChatroomlog(msg, data)
                return True
            # ------------------------------------------------
            if 'action' in data and data['action'] == 'infomachine':
                structinfo ={'data' : data,
                             'action' : "registeryagent",
                             'sessionid' : name_random(5, "registration"),
                             'ret' : 0}
                try:
                    del msg['body']
                    call_plugin(structinfo['action'],
                                self,
                                structinfo['action'],
                                structinfo['sessionid'],
                                structinfo['data'],
                                msg,
                                structinfo['ret'],
                                structinfo
                                )
                except TypeError:
                    logging.error("TypeError: executing plugin %s %s" %
                                  (structinfo['action'], sys.exc_info()[0]))
                    logger.error("%s" % (traceback.format_exc()))

                except Exception as e:
                    logging.error("Executing plugin (%s) %s %s" % (msg['from'], structinfo['action'], str(e)))
                    logger.error("%s" % (traceback.format_exc()))
                return True
            return False
        except Exception as e:
            logging.getLogger().error("machine info %s" % (str(e)))
            logger.error("%s"%(traceback.format_exc()))
        return False

    def timeout(self, data):
        log.warm("%s" % data['timeout'])

    def jidInRoom1(self, room, jid):
        for nick in self.plugin['xep_0045'].rooms[room]:
            entry = self.plugin['xep_0045'].rooms[room][nick]
            if entry is not None and entry['jid'] == jid:
                logger.debug("%s in room %s" % (jid, room))
                return True
        logger.debug("%s not in room %s" % (jid, room))
        return False

    def errorhandlingstanza(self, msg, msgfrom, msgkey):
        logger.error("child elements message")
        messagestanza=""
        for t in msgkey:
            if t != 'error' and t != "lang":
                e = str(msg[t])
                if e != "":
                    messagestanza+="%s : %s\n"%(t, e)
        if 'error' in msgkey:
            messagestanza+="Error information\n"
            msgkeyerror = msg['error'].keys()
            for t in msg['error'].keys():
                if t != "lang":
                    e = str(msg['error'][t])
                    if e != "":
                        messagestanza+="%s : %s\n"%(t, e)
        if messagestanza != "":
            logger.error(messagestanza)

    def message(self, msg):
        """
            ref stanza eg: https://xmpp.org/rfcs/rfc3921.html#stanzas
        """
        try:
            msgkey = msg.keys()
            msgfrom = ""
            if not 'from' in msgkey:
                logger.error("Stanza message bad format %s"%msg)
                return False
            msgfrom = str(msg['from'])
            logger.debug("*******MESSAGE %s"%msgfrom)
            if 'type' in msgkey:
                # eg: ref section 2.1
                type = str(msg['type'])
                if type == "chat" or type == "groupchat":
                    pass
                elif type == "headline":
                    "message automated service"
                    logger.warning("MESSAGE stanza headline %s"%msg)
                    return
                elif type == "normal":
                    "message automated service"
                    logger.warning("MESSAGE stanza normal %s"%msg)
                    msg.reply('Thank you, but I do not treat normal messages').send()
                    return
                elif type == 'error':
                    logger.error("Stanza message from %s"%msgfrom)
                    self.errorhandlingstanza(msg, msgfrom, msgkey)
                    return
                else:
                    logger.error("Stanza message type %s"%type)
                    return
        except:
            logger.error("Stanza message bad format %s"%msg)
            logger.error("%s" % (traceback.format_exc()))
            return
        if not 'body' in msgkey:
            logger.error("Stanza message body missing %s"%msg)
            return False

        # logger.debug(msg['body'])
        if msg['body'] == "This room is not anonymous":
            return False
        if msg['from'].bare == self.config.jidchatroommaster or msg['from'].bare == self.config.confjidchatroom:
            return False
        if self.jidInRoom1(self.config.confjidchatroom, msg['from']):
            if str(msg['from'].user) in self.confaccount:
                self.confaccount.remove(str(msg['from'].user))
                self.callpluginmaster(msg)
                return
            self.MessagesAgentFromChatroomConfig(msg)
            return
        if msg['type'] == 'groupchat':
            return
        if self.Showlogmessage(msg):
            return
        self.signalpresence(msg['from'])
        # if not self.jidInRoom1( self.config.jidchatroommaster, msg['from']):
        # """ message agent belonging to master """
        # return False
        if self.messagereturnsession(msg):
            # Message from the client of mmc command
            return

        if self.MessagesAgentFromChatroomMaster(msg):
            return
        self.callpluginmaster(msg)

    def muc_message(self, msg):
        """
        Processing all messages coming from a room
         type attribute to selection
        """
        pass

    def callpluginmasterfrommmc(self, plugin, data, sessionid=None):
        if sessionid == None:
            sessionid = name_random(5, plugin)
        msg = {}
        msg['from'] = self.boundjid.bare
        msg['body'] = json.dumps({'action': plugin,
                                  'ret': 0,
                                  'sessionid': sessionid,
                                  'data': data})
        self.callpluginmaster(msg)

    def callpluginmaster(self, msg):
        try:
            dataobj = json.loads(msg['body'])
            if dataobj.has_key('action') and dataobj['action'] != "" and dataobj.has_key('data'):
                if dataobj.has_key('base64') and \
                    ((isinstance(dataobj['base64'], bool) and dataobj['base64'] == True) or
                     (isinstance(dataobj['base64'], str) and dataobj['base64'].lower() == 'true')):
                    mydata = json.loads(base64.b64decode(dataobj['data']))
                else:
                    mydata = dataobj['data']
                if not dataobj.has_key('sessionid'):
                    dataobj['sessionid'] = "absent"
                if not 'ret' in dataobj:
                    dataobj['ret'] = 0
                try:
                    logging.debug("Calling plugin %s from  %s" % (dataobj['action'], msg['from']))
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
                    logging.error("TypeError: executing plugin %s %s" %
                                  (dataobj['action'], sys.exc_info()[0]))
                    logger.error("%s" % (traceback.format_exc()))

                except Exception as e:
                    logging.error("Executing plugin (%s) %s %s" % (msg['from'], dataobj['action'], str(e)))
                    logger.error("%s" % (traceback.format_exc()))

        except Exception as e:
            logging.error("Message structure %s   %s " % (msg, str(e)))
            logger.error("%s" % (traceback.format_exc()))

    def muc_presenceMaster(self, presence):
        if presence['muc']['nick'] != self.config.NickName:
            if self.config.showinfomaster:
                logger.debug("Presence of %s" % presence['muc']['nick'])

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

    def createsessionfordeploydiffered(self, data):
        sessionid = name_randomplus(25, "command")
        #calcule duree max de l existance de la session
        timeseconde = data['enddate'] - data['stardate']
        self.session.createsessiondatainfo(sessionid,
                                           datasession=data,
                                           timevalid=timeseconde,
                                           eventend=None)
        return sessionid

    def send_session_command(self, jid, action, data={}, datasession=None,
                             encodebase64=False, time=20, eventthread=None,
                             prefix=None):
        if prefix is None:
            prefix = "command"
        if datasession == None:
            datasession = {}
        command = {'action': action,
                   'base64': encodebase64,
                   'sessionid': name_randomplus(25, pref=prefix),
                   'data': ''
                   }
        if encodebase64:
            command['data'] = base64.b64encode(json.dumps(data))
        else:
            command['data'] = data

        datasession['data'] = data
        datasession['callbackcommand'] = "commandend"
        self.session.createsessiondatainfo(command['sessionid'],
                                           datasession=data,
                                           timevalid=time,
                                           eventend=eventthread)
        if action is not None:
            logging.debug("Send command and creation session")
            if jid == self.boundjid.bare:
                self.callpluginmasterfrommmc(action,
                                            data,
                                            sessionid = command['sessionid'])
            else:
                self.send_message(mto=jid,
                                mbody=json.dumps(command),
                                mtype='chat')
        else:
            logging.debug("creation session")
        return command['sessionid']
