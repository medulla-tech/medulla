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
"""
Plugin to manage the interface with xmppmaster
"""

import logging
import os
import sys
from mmc.plugins.xmppmaster.config import xmppMasterConfig

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

import json
# Database
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.msc.database import MscDatabase

import zlib
import base64
from master.lib.utils import name_random, simplecommand, file_get_contents
from xmppmaster import *
from mmc.plugins.xmppmaster.master.agentmaster import XmppSimpleCommand, getXmppConfiguration,\
    callXmppFunction, ObjectXmpp, callXmppPlugin,\
    callInventory, callrestartbymaster,\
    callshutdownbymaster, send_message_json,\
    callvncchangepermsbymaster, callInstallKey,\
    callremotefile, calllocalfile, callremotecommandshell,\
    calllistremotefileedit, callremotefileeditaction,\
    callremoteXmppMonitoring
VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################

def getApiVersion():
    return APIVERSION


def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    logger = logging.getLogger()
    config = xmppMasterConfig("xmppmaster")
    if config.disable:
        logger.warning("Plugin xmppmaster: disabled by configuration.")
        return False
    if not XmppMasterDatabase().activate(config):
        logger.warning("Plugin XmppMaster: an error occurred during the database initialization")
        return False
    return True

# #############################################################
# xmppmaster MAIN FUNCTIONS [HTTP INTERFACE]
# #############################################################


def getlinelogssession(sessionxmpp):
    return XmppMasterDatabase().getlinelogssession(sessionxmpp)


def getListPackages():
    resultnamepackage = []
    FichList = [f for f in os.listdir('/var/lib/pulse2/packages/') if os.path.isfile(
        os.path.join('/var/lib/pulse2/packages/', f, 'xmppdeploy.json'))]
    for package in FichList:
        with open(os.path.join('/var/lib/pulse2/packages/', package, 'xmppdeploy.json'), "r") as fichier:
            session = json.load(fichier)
            resultnamepackage.append(session['info']['name'])
    return resultnamepackage


def set_simple_log(textinfo, sessionxmppmessage, typelog, priority, who):
    return XmppMasterDatabase().logtext(textinfo,
                                        sessionname=sessionxmppmessage,
                                        type=typelog,
                                        priority=priority,
                                        who=who)


def updatedeploystate(sessionxmppmessage, status):
    return XmppMasterDatabase().updatedeploystate(sessionxmppmessage, status)


def adddeployabort(
        idcommand,
        jidmachine,
        jidrelay,
        host,
        inventoryuuid,
        uuidpackage,
        state,
        sessionid,
        user,
        login,
        title,
        group_uuid,
        startcmd,
        endcmd,
        macadress):
    return XmppMasterDatabase().adddeploy(idcommand,
                                          jidmachine,
                                          jidrelay,
                                          host,
                                          inventoryuuid,
                                          uuidpackage,
                                          state,
                                          sessionid,
                                          user,
                                          login,
                                          title,
                                          group_uuid,
                                          startcmd,
                                          endcmd,
                                          macadress)


def updatedeploystate1(sessionxmppmessage, status):
    return XmppMasterDatabase().updatedeploystate1(sessionxmppmessage, status)


def getstepdeployinsession(sessionname):
    return XmppMasterDatabase().getstepdeployinsession(sessionname)


def setlogxmpp(text,
               type,
               sessionname,
               priority,
               who,
               how,
               why,
               module,
               action,
               touser,
               fromuser):
    return XmppMasterDatabase().setlogxmpp(text,
                                           type,
                                           sessionname,
                                           priority,
                                           who,
                                           how,
                                           why,
                                           module,
                                           action,
                                           touser,
                                           fromuser)


def getLogxmpp(start_date, end_date, typelog, action, module, user, how, who, why, headercolumn):
    if typelog == "None" and action == "None" and module == "None" and start_date == "":
        return []
    if typelog == "None":
        typelog == ""
    if module == "None":
        module == ""
    if action == "None":
        action == ""
    return XmppMasterDatabase().getLogxmpp(start_date,
                                           end_date,
                                           typelog,
                                           action,
                                           module,
                                           user,
                                           how,
                                           who,
                                           why,
                                           headercolumn)


def getPresenceuuid(uuid):
    return XmppMasterDatabase().getPresenceuuid(uuid)

def getPresenceuuids(uuids):
    return XmppMasterDatabase().getPresenceuuids(uuids)

# topology


def topologypulse():
    return XmppMasterDatabase().topologypulse()


def getMachinefromjid(jid):
    return XmppMasterDatabase().getMachinefromjid(jid)


def getMachinefromuuid(uuid):
    return XmppMasterDatabase().getMachinefromuuid(uuid)


def getRelayServerfromjid(jid):
    return XmppMasterDatabase().getRelayServerfromjid(jid)


def getlistcommandforuserbyos(login, osname=None, min=None, max=None, filt=None, edit=None):
    if osname == '':
        osname = None
    if min == '':
        min = None
    if max == '':
        max = None
    if filt == '':
        filt = None
    if edit == '':
        edit = None

    return XmppMasterDatabase().getlistcommandforuserbyos(login, osname=osname, min=min, max=max, filt=filt, edit=edit)


def delQa_custom_command(login, name, osname):
    return XmppMasterDatabase().delQa_custom_command(login, name, osname)


def create_Qa_custom_command(login, osname, namecmd, customcmd, description):
    return XmppMasterDatabase().create_Qa_custom_command(login, osname, namecmd, customcmd, description)


def updateName_Qa_custom_command(login, osname, namecmd, customcmd, description):
    return XmppMasterDatabase().updateName_Qa_custom_command(login, osname, namecmd, customcmd, description)


def create_local_dir_transfert(pathroot, hostname):
    dirmachine = os.path.join(pathroot, hostname)
    if not os.path.exists(dirmachine):
        os.makedirs(dirmachine)
        os.chmod(dirmachine, 0o777)
    return localfile(dirmachine)


def getGuacamoleRelayServerMachineUuid(uuid):
    return XmppMasterDatabase().getGuacamoleRelayServerMachineUuid(uuid)


def getGuacamoleidforUuid(uuid):
    return XmppMasterDatabase().getGuacamoleidforUuid(uuid)


def getListPresenceAgent():
    return json.dumps(ObjectXmpp().presencedeployment, encoding='latin1')


def getListPresenceMachine():
    return XmppMasterDatabase().getListPresenceMachine()


def getCountPresenceMachine():
    return XmppMasterDatabase().getCountPresenceMachine()


def getjidMachinefromuuid(uuid):
    return XmppMasterDatabase().getjidMachinefromuuid(uuid)


def getListPresenceRelay():
    return XmppMasterDatabase().getListPresenceRelay()


def deploylog(uuidinventory, nblastline):
    return XmppMasterDatabase().deploylog(uuidinventory, nblastline)


def addlogincommand(login,
                    commandid,
                    grpid,
                    nb_machine_in_grp,
                    instructions_nb_machine_for_exec,
                    instructions_datetime_for_exec,
                    parameterspackage,
                    rebootrequired,
                    shutdownrequired,
                    limit_rate_ko,
                    params):
    return XmppMasterDatabase().addlogincommand(login,
                                                commandid,
                                                grpid,
                                                nb_machine_in_grp,
                                                instructions_nb_machine_for_exec,
                                                instructions_datetime_for_exec,
                                                parameterspackage,
                                                rebootrequired,
                                                shutdownrequired,
                                                limit_rate_ko,
                                                params)


def loginbycommand(commandid):
    return XmppMasterDatabase().loginbycommand(commandid)


def getdeployfromcommandid(command_id, uuid):
    return XmppMasterDatabase().getdeployfromcommandid(command_id, uuid)


def getstatdeployfromcommandidstartdate(command_id, datestart):
    return XmppMasterDatabase().getstatdeployfromcommandidstartdate(command_id, datestart)


def get_machine_stop_deploy(cmdid, uuid):
    result = XmppMasterDatabase().get_machine_stop_deploy(cmdid, uuid)
    msg_stop_deploy = {
        "action": "enddeploy",
        "sessionid": result['sessionid'],
        'data': {"typerequest": "bansessionid"},
        "ret": 0,
        'base64': False
    }
    updatedeploystate(result['sessionid'], 'DEPLOYMENT ABORT')
    if 'jid_relay' in result and result['jid_relay'] != "fake_jidrelay":
        send_message_json(result['jid_relay'], msg_stop_deploy)
    if 'jidmachine' in result and result['jidmachine'] != "fake_jidmachine":
        send_message_json(result['jidmachine'], msg_stop_deploy)
    return True


def get_group_stop_deploy(grpid, cmdid):
    result = XmppMasterDatabase().get_group_stop_deploy(grpid, cmdid)
    msg_stop_deploy = {
        "action": "enddeploy",
        "sessionid": "",
        'data': {"typerequest": "bansessionid"},
        "ret": 0,
        'base64': False}
    for machine in result['objectdeploy']:
        msg_stop_deploy['sessionid'] = machine['sessionid']
        updatedeploystate1(machine['sessionid'], 'DEPLOYMENT ABORT')
        if 'jid_relay' in machine and machine['jid_relay'] != "fake_jidrelay":
            send_message_json(machine['jid_relay'], msg_stop_deploy)
        if 'jidmachine' in machine and machine['jidmachine'] != "fake_jidmachine":
            send_message_json(machine['jidmachine'], msg_stop_deploy)
    return True


def getlinelogswolcmd(idcommand, uuid):
    return XmppMasterDatabase().getlinelogswolcmd(idcommand, uuid)


def getdeploybyuserlen(login):
    if not login:
        login = None
    return XmppMasterDatabase().getdeploybyuserlen(login)


def getdeploybymachinerecent(uuidinventory, state, duree, min, max, filt):
    return XmppMasterDatabase().getdeploybymachinerecent(uuidinventory, state, duree, min, max, filt)


def getdeploybymachinegrprecent(gid, state, duree, min, max, filt):
    return XmppMasterDatabase().getdeploybymachinegrprecent(gid, state, duree, min, max, filt)


def delDeploybygroup(numgrp):
    return XmppMasterDatabase().delDeploybygroup(numgrp)


def getdeploybyuserrecent(login, state, duree, min=None, max=None, filt=None):
    if min == "":
        min = None
    if max == "":
        max = None
    if filt == "":
        filt = None
    return XmppMasterDatabase().getdeploybyuserrecent(login, state, duree, min, max, filt)


def getdeploybyuserpast(login, duree, min=None, max=None, filt=None):
    if min == "":
        min = None
    if max == "":
        max = None
    return XmppMasterDatabase().getdeploybyuserpast(login, duree, min, max, filt)


def getdeploybyuser(login, numrow, offset):
    if not numrow:
        numrow = None
    if not offset:
        offset = None
    return XmppMasterDatabase().getdeploybyuser(login, numrow, offset)


def getshowmachinegrouprelayserver():
    def Nonevalue(x):
        if x == None:
            return ""
        else:
            return x
    machinelist = XmppMasterDatabase().showmachinegrouprelayserver()
    array = []
    for t in machinelist:
        z = [Nonevalue(x) for x in list(t)]
        ob = {'jid': z[0], 'type': z[1], 'os': z[2], 'rsdeploy': z[3],
              'hostname': z[4], 'uuid': z[5], 'ip': z[6], 'subnet': z[7]}
        array.append(ob)
    return array


def get_qaction(groupname, user, grp, completename):
    return XmppMasterDatabase().get_qaction(groupname, user, grp, completename)

def setCommand_qa(command_name, command_action, command_login, command_grp="", command_machine='', command_os=""):
    return XmppMasterDatabase().setCommand_qa(command_name, command_action, command_login, command_grp, command_machine, command_os)


def getCommand_action_time(during_the_last_seconds, start, stop, filter):
    return XmppMasterDatabase().getCommand_action_time(during_the_last_seconds, start, stop, filter)


def setCommand_action(target, command_id, sessionid, command_result, typemessage):
    return XmppMasterDatabase().setCommand_action(target, command_id, sessionid, command_result, typemessage)


def getCommand_qa_by_cmdid(cmdid):
    return XmppMasterDatabase().getCommand_qa_by_cmdid(cmdid)


def getQAforMachine(cmd_id, uuidmachine):
    resultdata = XmppMasterDatabase().getQAforMachine(cmd_id, uuidmachine)
    if resultdata[0][3] == "result":
        # encode 64 str? to transfer xmlrpc if string with sequence escape
        resultdata[0][4] = base64.b64encode(resultdata[0][4])
    return resultdata


def runXmppApplicationDeployment(*args, **kwargs):
    for count, thing in enumerate(args):
        print '{0}. {1}'.format(count, thing)
    for name, value in kwargs.items():
        print '{0} = {1}'.format(name, value)
    return callXmppFunction(*args, **kwargs)


def CallXmppPlugin(*args, **kwargs):
    return callXmppPlugin(*args, **kwargs)


def callInventoryinterface(uuid):
    jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    if jid != "":
        callInventory(jid)
        return jid
    else:
        logging.getLogger().error("for machine %s : jid xmpp missing" % uuid)
        return "jid missing"


def createdirectoryuser(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chmod(directory, 0o700)
        return True
    return False


def callInstallKeyAM(jidAM, jidARS):
    if jidARS != "" and jidAM != "":
        callInstallKey(jidAM, jidARS)
        return jidAM
    else:
        logging.getLogger().error("for machine %s : install key ARS %s" % (jidAM, jidARS))
        return "jid (AM or ARS) missing"


def callrestart(uuid):
    jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    if jid != "":
        callrestartbymaster(jid)
        return jid
    else:
        logging.getLogger().error("callrestartbymaster for machine %s : jid xmpp missing" % uuid)
        return "jid missing"


def callshutdown(uuid, time, msg):
    jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    if jid != "":
        callshutdownbymaster(jid, time, msg)
        return jid
    else:
        logging.getLogger().error("callshutdownbymaster for machine %s : jid xmpp missing" % uuid)
        return "jid missing"


def callvncchangeperms(uuid, askpermission):
    jid = XmppMasterDatabase().getjidMachinefromuuid(uuid)
    if jid != "":
        callvncchangepermsbymaster(jid, askpermission)
        return jid
    else:
        logging.getLogger().error("callvncchangepermsbymaster for machine %s : jid xmpp missing" % uuid)
        return "jid missing"


def localfile(currentdir):
    return calllocalfile(currentdir)


def remotefile(currentdir, jidmachine):
    return callremotefile(jidmachine, currentdir)


def listremotefileedit(jidmachine):
    aa = calllistremotefileedit(jidmachine)
    objout = json.loads(aa)
    print objout['data']['result']
    return objout['data']['result']


def remotefileeditaction(jidmachine, data):
    resultjsonstr = callremotefileeditaction(jidmachine, data)
    if not isinstance(resultjsonstr, basestring):
        return resultjsonstr
    objout = json.loads(resultjsonstr)
    if 'data' in objout:
        return objout['data']
    return objout

def getcontentfile(pathfile, deletefile):
    if os.path.isfile(pathfile):
        data = file_get_contents(pathfile)
        if deletefile == True:
            os.remove(pathfile)
        return data
    else:
        return False


def remotecommandshell(command, jidmachine, timeout):
    return callremotecommandshell(jidmachine, command, timeout=timeout)


def remoteXmppMonitoring(suject, jidmachine, timeout):
    data = callremoteXmppMonitoring(jidmachine,  suject, timeout=timeout)
    result = json.loads(data)
    resultdata = zlib.decompress(base64.b64decode(result['result']))
    dataresult = [x for x in resultdata.split('\n')]
    result['result'] = dataresult
    return result


def runXmppAsyncCommand(cmd, infomachine):
    sessionid = name_random(8, "quick_")
    cmd = cmd.strip()
    if cmd.startswith("plugin_"):
        # call plugin master
        lineplugincalling = [x.strip() for x in cmd.split("@_@")]
        plugincalling = lineplugincalling[0]
        del lineplugincalling[0]
        action = plugincalling.strip().split("_")
        action.pop(0)
        action = "_".join(action)
        data = {
            "action": action,
            "sessionid": sessionid,
            "data": [infomachine['jid'], infomachine, lineplugincalling]
        }
        XmppMasterDatabase().setCommand_action(infomachine['uuid_inventorymachine'],
                                               infomachine['cmdid'],
                                               sessionid,
                                               "call plugin %s for Quick Action" % (action),
                                               "log")
        callXmppPlugin(action, data)
    else:
        data = {"action": "asynchroremoteQA",
                "sessionid": sessionid,
                "data": infomachine,
                "base64": False}
        callXmppPlugin("asynchroremoteQA", data)


def runXmppCommand(cmd, machine, information=""):
    data = {
        "action": "cmd",
        "sessionid": name_random(8, "quick_"),
        "data": [machine, information],
        "base64": False
    }
    cmd = cmd.strip()
    if cmd.startswith("plugin_"):
        # call plugin master
        lineplugincalling = [x.strip() for x in cmd.split("@_@")]
        plugincalling = lineplugincalling[0]
        del lineplugincalling[0]
        action = plugincalling.strip().split("_")[1]
        data = {
            "action": action,
            "sessionid": name_random(8, "quick_"),
            "data": [machine, information, lineplugincalling],
            "base64": False
        }
        callXmppPlugin(action, data)
        return {u'action': u'resultshellcommand', u'sessionid': u'mcc_221n4h6h', u'base64': False, u'data': {'result': 'call plugin : %s to machine : %s' % (action, machine)}, u'ret': 0}
    else:
        data = {
            "action": "shellcommand",
            "sessionid": name_random(8, "mcc_"),
            "data": {'cmd': cmd},
            "base64": False
        }
        a = XmppSimpleCommand(machine, data, 70)
        d = a.t2.join()
        print type(a.result)
    return a.result


def runXmppScript(cmd, machine):
    data = {
        "action": "shellcommand",
        "sessionid": name_random(8, "mcc_"),
        "data": {'cmd': cmd},
        "base64": False
    }
    a = XmppSimpleCommand(machine, data, 70)
    d = a.t2.join()
    return a.result


def getCountOnlineMachine():
    return XmppMasterDatabase().getCountOnlineMachine()


def get_agent_descriptor_base():
    return  ObjectXmpp().Update_Remote_Agentlist

def get_plugin_lists():
    pluginlist = {}
    for t in ObjectXmpp().plugindata:
        pluginlist[t] = [ ObjectXmpp().plugindata[t],
                          ObjectXmpp().plugintype[t],
                          ObjectXmpp().pluginagentmin[t]]

    result = [pluginlist,
              ObjectXmpp().plugindatascheduler]
    return result


def get_conf_master_agent():
    rest={}
    conf =  dict(getXmppConfiguration())
    for t in conf:
        if t in ['passwordconnection',
                 'dbpasswd',
                 'confpasswordmuc' ]:
            continue
        if isinstance(conf[t], (dict, list, tuple, int, basestring)):
            rest[t] =  conf[t]
    return  json.dumps(rest, indent = 4)


def get_list_of_users_for_shared_qa(namecmd):
    return XmppMasterDatabase().get_list_of_users_for_shared_qa(namecmd)
