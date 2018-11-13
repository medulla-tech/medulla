# -*- coding: utf-8 -*-
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

# file pluginsmaster/plugin_resultkiosk.py

import datetime
import json
import traceback
import sys
import os
from pulse2.database.xmppmaster import XmppMasterDatabase
from pulse2.database.msc import MscDatabase
from managepackage import managepackage
import logging
from utils import name_random, file_put_contents, file_get_contents
import re
from mmc.plugins.kiosk import handlerkioskpresence

plugin = {"VERSION": "1.3", "NAME": "resultkiosk", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("#################################################")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug(json.dumps(data, indent=4))
    logging.getLogger().debug("#################################################")
    if 'subaction' in data:
        if data['subaction'] == 'initialization':
            initialisekiosk(data, message, xmppobject)
        elif data['subaction'] == 'launch':
            deploypackage(data,  message, xmppobject)
        elif data['subaction'] == 'delete':
            deploypackage(data,  message, xmppobject)
        elif data['subaction'] == 'install':
            deploypackage(data,  message, xmppobject)
        elif data['subaction'] == 'update':
            deploypackage(data,  message, xmppobject)
        else:
            print "No subaction found"
    else:
        pass


def parsexmppjsonfile(path):
    datastr = file_get_contents(path)

    datastr = re.sub(r"(?i) *: *false", " : false", datastr)
    datastr = re.sub(r"(?i) *: *true", " : true", datastr)

    file_put_contents(path, datastr)


def initialisekiosk(data, message, xmppobject):
    machine = XmppMasterDatabase().getMachinefromjid(message['from'])
    if "userlist" and "oumachine" and "ouuser" in data:
        if len(data['userlist']) == 0:
            user = ""
        else:
            user = data['userlist'][0]
        print "call updatemachineAD"
        XmppMasterDatabase().updatemachineAD(machine['id'], user, data['oumachine'], data['ouuser'])

    print json.dumps(machine, indent=4)
    initializationdatakiosk = handlerkioskpresence(message['from'],
                                                   machine['id'],
                                                   machine['platform'],
                                                   machine['hostname'],
                                                   machine['uuid_inventorymachine'],
                                                   machine['agenttype'],
                                                   classutil=machine['classutil'],
                                                   fromplugin=True)

    datasend = {
        "sessionid": name_random(6, "initialisation_kiosk"),
        "action": "kiosk",
        "data": initializationdatakiosk
    }
    xmppobject.send_message(mto=message['from'],
                            mbody=json.dumps(datasend),
                            mtype='chat')


def deploypackage(data, message, xmppobject):
    machine = XmppMasterDatabase().getMachinefromjid(message['from'])
    print json.dumps(machine, indent=4)

    nameuser = "(kiosk):%s/%s" % (machine['lastuser'], machine['hostname'])

    command = MscDatabase().createcommanddirectxmpp(data['uuid'],
                                                    '',
                                                    '',
                                                    'malistetodolistfiles',
                                                    'enable',
                                                    'enable',
                                                    datetime.datetime.now(),
                                                    datetime.datetime.now() + datetime.timedelta(hours=1),
                                                    nameuser,
                                                    nameuser,
                                                    'titlepackage',
                                                    60,
                                                    4,
                                                    0,
                                                    '',
                                                    None,
                                                    None,
                                                    None,
                                                    'none',
                                                    'active',
                                                    '1',
                                                    cmd_type=0)
    commandid = command.id
    commandstart = command.start_date
    commandstop = command.end_date
    jidrelay = machine['groupdeploy']
    uuidmachine = machine['uuid_inventorymachine']
    jidmachine = machine['jid']
    # try:
    #target = MscDatabase().xmpp_create_Target(uuidmachine, machine['hostname'])

    # except Exception as e:
    # print str(e)
    # traceback.print_exc(file=sys.stdout)

    XmppMasterDatabase().addlogincommand(
        nameuser,
        commandid,
        "",
        "",
        "",
        "",
        "",
        0,
        0,
        0,
        {})

    sessionid = name_random(5, "deploykiosk_")
    name = managepackage.getnamepackagefromuuidpackage(data['uuid'])

    path = managepackage.getpathpackagename(name)

    descript = managepackage.loadjsonfile(os.path.join(path, 'xmppdeploy.json'))
    parsexmppjsonfile(os.path.join(path, 'xmppdeploy.json'))
    if descript is None:
        logger.error("deploy %s on %s  error : xmppdeploy.json missing" %
                     (data['uuid'], machine['hostname']))
        return None
    objdeployadvanced = XmppMasterDatabase().datacmddeploy(commandid)

    datasend = {"name": name,
                "login": nameuser,
                "idcmd": commandid,
                "advanced": objdeployadvanced,
                'methodetransfert': 'pushrsync',
                "path": path,
                "packagefile": os.listdir(path),
                "jidrelay": jidrelay,
                "jidmachine": jidmachine,
                "jidmaster": xmppobject.boundjid.bare,
                "iprelay":  XmppMasterDatabase().ipserverARS(jidrelay)[0],
                "ippackageserver":  XmppMasterDatabase().ippackageserver(jidrelay)[0],
                "portpackageserver":  XmppMasterDatabase().portpackageserver(jidrelay)[0],
                "ipmachine": XmppMasterDatabase().ipfromjid(jidmachine)[0],
                "ipmaster": xmppobject.config.Server,
                "Dtypequery": "TQ",
                "Devent": "DEPLOYMENT START",
                "uuid": uuidmachine,
                "descriptor": descript,
                "transfert": True
                }
    # run deploy

    sessionid = xmppobject.send_session_command(jidrelay,
                                                "applicationdeploymentjson",
                                                datasend,
                                                datasession=None,
                                                encodebase64=False)
    # add deploy in table.
    XmppMasterDatabase().adddeploy(commandid,
                                   machine['jid'],  # jidmachine
                                   machine['groupdeploy'],  # jidrelay,
                                   machine['hostname'],  # host,
                                   machine['uuid_inventorymachine'],  # inventoryuuid,
                                   data['uuid'],  # uuidpackage,
                                   'DEPLOYMENT START',  # state,
                                   sessionid,  # id session,
                                   nameuser,  # user
                                   nameuser,  # login
                                   name + " " + \
                                   commandstart.strftime("%Y/%m/%d/ %H:%M:%S"),  # title,
                                   "",  # group_uuid
                                   commandstart,  # startcmd
                                   commandstop,  # endcmd
                                   machine['macaddress'])
    xmppobject.xmpplog("Start deploy on machine %s" % jidmachine,
                       type='deploy',
                       sessionname=sessionid,
                       priority=-1,
                       action="",
                       who=nameuser,
                       how="",
                       why=xmppobject.boundjid.bare,
                       module="Deployment | Start | Creation",
                       date=None,
                       fromuser=nameuser,
                       touser="")
