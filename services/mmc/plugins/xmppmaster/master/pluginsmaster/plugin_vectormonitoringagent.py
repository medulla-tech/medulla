#!/usr/bin/python3
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
# file pluginsmaster pluginsmaster/plugin_vectormonitoringagent.py
import sys
import json

import logging


import traceback
from pulse2.database.xmppmaster import XmppMasterDatabase
logger = logging.getLogger()

plugin = {"VERSION": "1.0", "NAME": "vectormonitoringagent", "TYPE": "master"}


def process_system(functionname,
                   data,
                   id_machine,
                   hostname,
                   id_mon_machine):
    device_type = functionname[8:]
    logger.debug("Device %s" % device_type)
    serial, status, firmware, alarm_msg = ["", "ready", "", []]
    if "serial" in data:
        serial = data['serial']
        del data['serial']
    if "status" in data and data['status'] != "":
        status = data['status']
        del data['status']
    if "firmware" in data:
        firmware = data['firmware']
        del data['firmware']
    if 'alarms' in data:
        if isinstance(data['alarms'], basestring):
            alarm_msg = [data['alarms']]
        elif isinstance(data['alarms'], list):
            alarm_msg = data['alarms']
        del data['alarms']
    XmppMasterDatabase().setMonitoring_device_reg(hostname,
                                                  id_mon_machine,
                                                  device_type,
                                                  serial,
                                                  firmware,
                                                  status,
                                                  json.dumps(alarm_msg),
                                                  json.dumps(data['metriques']))


def process_nfcReader(functionname,
                      data,
                      id_machine,
                      hostname,
                      id_mon_machine):
    device_type = functionname[8:]
    logger.debug("===========================================================")
    logger.debug("Device %s" % device_type)
    serial, status, firmware, alarm_msg = ["", "ready", "", []]
    if "serial" in data:
        serial = data['serial']
        del data['serial']
    if "status" in data and data['status'] != "":
        status = data['status']
        del data['status']
    if "firmware" in data:
        firmware = data['firmware']
        del data['firmware']
    if 'message' in data:
        if isinstance(data['message'], basestring):
            alarm_msg = [data['message']]
        elif isinstance(data['message'], list):
            alarm_msg = data['message']
        del data['message']
    XmppMasterDatabase().setMonitoring_device_reg(hostname,
                                                  id_mon_machine,
                                                  device_type,
                                                  serial,
                                                  firmware,
                                                  status,
                                                  json.dumps(alarm_msg),
                                                  json.dumps(data['metriques']))


def process_generic(functionname,
                    data,
                    id_machine,
                    hostname,
                    id_mon_machine):
    device_type = functionname[8:]
    logger.debug("Device %s" % device_type)
    serial, status, firmware, alarm_msg = ["", "ready", "", []]
    if "serial" in data:
        serial = data['serial']
        del data['serial']
    if "status" in data and data['status'] != "":
        status = data['status']
        del data['status']
    if "firmware" in data:
        firmware = data['firmware']
        del data['firmware']
    if 'message' in data:
        if isinstance(data['message'], basestring):
            alarm_msg = [data['message']]
        elif isinstance(data['message'], list):
            alarm_msg = data['message']
        del data['message']
    XmppMasterDatabase().setMonitoring_device_reg(hostname,
                                                  id_mon_machine,
                                                  device_type,
                                                  serial,
                                                  firmware,
                                                  status,
                                                  json.dumps(alarm_msg),
                                                  json.dumps(data['metriques']))


def callFunction(functionname, *args, **kwargs):
    functionname = "process_%s" % functionname
    logger.debug("**call function %s %s %s" % (functionname, args, kwargs))
    thismodule = sys.modules[__name__]
    try:
        return getattr(thismodule,
                       functionname)(functionname, *args, **kwargs)
    except AttributeError:
        process_generic(functionname, *args, **kwargs)
    except Exception:
        logger.error("\n%s" % (traceback.format_exc()))


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("#################################################")
    logger.debug(plugin)
    logger.debug(json.dumps(data, indent=4))
    logger.debug("#################################################")

    compteurcallplugin = getattr(xmppobject, "num_call%s" % action)
    logger.debug("compteur num_call pluging %s %s" % (action,
                                                      compteurcallplugin))

    if compteurcallplugin == 0:
        xmppobject.typelistMonitoring_device = \
            XmppMasterDatabase().getlistMonitoring_devices_type()
        logger.debug("list device %s" % (xmppobject.typelistMonitoring_device))

    machine = XmppMasterDatabase().getMachinefromjid(message['from'])
    logger.debug("Machine %s %s" % (machine['id'], machine['hostname']))
    if "subaction" in data:
        if data['subaction'] == "terminalInformations":
            # load version agent agentversion
            statusmsg = ""
            if 'status' in data:
                statusmsg = json.dumps(data['status'])
            id_mom_machine = XmppMasterDatabase().setMonitoring_machine(
                                 machine['id'],
                                 machine['hostname'],
                                 date=data['date'],
                                 statusmsg=statusmsg)
            if 'device_service' in data:
                for element in data['device_service']:
                    for devicename in element:
                        # call process functions defined
                        if devicename.lower() in xmppobject.typelistMonitoring_device:
                            # globals()["process_%s"%element](data['opticalReader'])
                            callFunction(devicename,
                                         element[devicename],
                                         machine['id'],
                                         machine['hostname'],
                                         id_mom_machine)
        elif data['subaction'] == "terminalAlert":
            pass
