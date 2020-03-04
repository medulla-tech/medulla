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
# file /pluginsmaster/plugin_xmpplog.py

import json
import logging
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback

logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "xmpplog", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, msg, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug("call %s from %s"%(plugin, msg['from']))
    logger.debug("=====================================================")
    try :
        logger.debug("%s : "%data)
        dataobj = data
        if data["action"] == 'xmpplog':
            createlog(xmppobject, data)
        elif data["action"] == 'resultapplicationdeploymentjson':
            data['sessionid'] = sessionid
            xmpplogdeploy(xmppobject, data)
        else:
            logger.warning("message bad formated: msg log from %s" %(msg['from']))
            logger.warning("data msg is \n%s" %( json.dumps(data, indent = 4)))
    except Exception as e:
        logging.error("structure Message from %s %s " %(msg['from'], str(e)))
        logger.error("\n%s"%(traceback.format_exc()))

def createlog(xmppobject, dataobj):
    """
        this function creating log in base from body message xmpp
    """
    try:
        if 'text' in dataobj :
            text = dataobj['text']
        else:
            return
        type = dataobj['type'] if 'type' in dataobj else ""
        sessionname = dataobj['sessionid'] if 'sessionid' in dataobj else ""
        priority = dataobj['priority'] if 'priority' in dataobj else ""
        who = dataobj['who'] if 'who' in dataobj else  ""
        how = dataobj['how'] if 'how' in dataobj else ""
        why = dataobj['why'] if 'why' in dataobj else ""
        module = dataobj['module'] if 'module' in dataobj else ""
        action = dataobj['action'] if 'action' in dataobj else ""
        fromuser = dataobj['fromuser'] if 'fromuser' in dataobj else ""
        touser = dataobj['touser'] if 'touser' in dataobj else ""
        XmppMasterDatabase().setlogxmpp(text,
                                        type = type,
                                        sessionname = sessionname,
                                        priority = priority,
                                        who = who ,
                                        how  =how,
                                        why  =why,
                                        module = module,
                                        fromuser  = fromuser,
                                        touser  = touser,
                                        action = action)
    except Exception as e:
        logger.error("Message deploy error  %s %s" %(dataobj, str(e)))
        logger.error("\n%s"%(traceback.format_exc()))
            
        
def registerlogxmpp(xmppobject,
                    text,
                    type = 'noset',
                    sessionname = '',
                    priority = 0,
                    who = '' ,
                    how  = '',
                    why  = '',
                    module = '',
                    fromuser  = '',
                    touser  = '',
                    action = ''
                    ):
    """
        this function for creating log in base
    """
    XmppMasterDatabase().setlogxmpp(text,
                                    type = 'noset',
                                    sessionname = sessionname,
                                    priority = priority,
                                    who = who ,
                                    how  =how,
                                    why  =why,
                                    module = module,
                                    fromuser  = fromuser,
                                    touser  = touser,
                                    action = action)
        
def xmpplogdeploy(xmppobject, data):
    """
        this function manage msg deploy log
    """
    try:
        if 'text' in data and \
            'type' in data and \
                'sessionid' in data and \
                    'priority' in data and \
                        'who' in data:
            registerlogxmpp(xmppobject,
                            data['text'],
                            type = data['type'],
                            sessionname = data['sessionid'],
                            priority = data['priority'],
                            who = data['who'])
        elif 'action' in data :
            if data['action'] == 'resultapplicationdeploymentjson':
                #log dans base resultat
                if data['ret'] == 0:
                    XmppMasterDatabase().updatedeployresultandstate( data['sessionid'], 
                                                                    "DEPLOYMENT SUCCESS", 
                                                                    json.dumps(data, 
                                                                               indent=4,
                                                                               sort_keys=True) )
                else:
                    XmppMasterDatabase().updatedeployresultandstate(data['sessionid'],
                                                                    "DEPLOYMENT ERROR", 
                                                                    json.dumps(data,
                                                                               indent=4,
                                                                               sort_keys=True) )
    except Exception as e:
        logging.error("obj Message deploy error  %s\nerror text : %s" %(data, str(e)))
        logger.error("\n%s"%(traceback.format_exc()))
