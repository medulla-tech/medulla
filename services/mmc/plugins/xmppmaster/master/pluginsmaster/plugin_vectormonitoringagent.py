#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import sys
import json
import logging
import traceback
from pulse2.database.xmppmaster import XmppMasterDatabase

logger = logging.getLogger()

plugin = {"VERSION": "1.3", "NAME": "vectormonitoringagent", "TYPE": "master"}


def process_system(
    functionname,
    xmppobject,
    msg_from,
    sessionid,
    data,
    id_machine,
    hostname,
    id_mon_machine,
):
    device_type = functionname[8:]
    logger.debug("Device %s" % device_type)
    serial, status, firmware, alarm_msg = ["", "ready", "", []]
    if "serial" in data:
        serial = data["serial"]
        del data["serial"]
    if "status" in data and data["status"] != "":
        status = data["status"]
        del data["status"]
    if "firmware" in data:
        firmware = data["firmware"]
        del data["firmware"]
    if "alarms" in data:
        if isinstance(data["alarms"], str):
            alarm_msg = [data["alarms"]]
        elif isinstance(data["alarms"], list):
            alarm_msg = data["alarms"]
        del data["alarms"]
    XmppMasterDatabase().setMonitoring_device_reg(
        hostname,
        xmppobject,
        msg_from,
        sessionid,
        id_mon_machine,
        device_type,
        serial,
        firmware,
        status,
        json.dumps(alarm_msg),
        json.dumps(data["metriques"]),
    )


def process_nfcreader(
    functionname,
    xmppobject,
    msg_from,
    sessionid,
    data,
    id_machine,
    hostname,
    id_mon_machine,
):
    device_type = functionname[8:]
    logger.debug("===========================================================")
    logger.debug("Device %s" % device_type)
    serial, status, firmware, alarm_msg = ["", "ready", "", []]
    if "serial" in data:
        serial = data["serial"]
        del data["serial"]
    if "status" in data and data["status"] != "":
        status = data["status"]
        del data["status"]
    if "firmware" in data:
        firmware = data["firmware"]
        del data["firmware"]
    if "message" in data:
        if isinstance(data["message"], str):
            alarm_msg = [data["message"]]
        elif isinstance(data["message"], list):
            alarm_msg = data["message"]
        del data["message"]
    XmppMasterDatabase().setMonitoring_device_reg(
        hostname,
        xmppobject,
        msg_from,
        sessionid,
        id_mon_machine,
        device_type,
        serial,
        firmware,
        status,
        json.dumps(alarm_msg),
        json.dumps(data["metriques"]),
    )


def process_generic(
    functionname,
    xmppobject,
    msg_from,
    sessionid,
    data,
    id_machine,
    hostname,
    id_mon_machine,
):
    device_type = functionname[8:]
    logger.debug("Device %s" % device_type)
    serial, status, firmware, alarm_msg = ["", "ready", "", []]
    if "serial" in data:
        serial = data["serial"]
        del data["serial"]
    if "status" in data and data["status"] != "":
        status = data["status"]
        del data["status"]
    if "firmware" in data:
        firmware = data["firmware"]
        del data["firmware"]
    if "message" in data:
        if isinstance(data["message"], str):
            alarm_msg = [data["message"]]
        elif isinstance(data["message"], list):
            alarm_msg = data["message"]
        del data["message"]
    logger.debug(
        "call setMonitoring_device_reg hostname %s\n"
        " id_mon_machine %s \n"
        " device_type, %s\n"
        " serial %s \n"
        " firmware %s\n"
        " status %s\n"
        " alarm_msg %s\n"
        " metriques %s"
        % (
            hostname,
            id_mon_machine,
            device_type,
            serial,
            firmware,
            status,
            json.dumps(alarm_msg),
            json.dumps(data["metriques"]),
        )
    )
    XmppMasterDatabase().setMonitoring_device_reg(
        hostname,
        xmppobject,
        msg_from,
        sessionid,
        id_mon_machine,
        device_type,
        serial,
        firmware,
        status,
        json.dumps(alarm_msg),
        json.dumps(data["metriques"]),
    )


def callFunction(functionname, *args, **kwargs):
    functionname = "process_%s" % functionname.lower()
    logger.debug("**call function %s %s %s" % (functionname, args, kwargs))
    thismodule = sys.modules[__name__]
    try:
        return getattr(thismodule, functionname)(functionname, *args, **kwargs)
    except AttributeError:
        process_generic(functionname, *args, **kwargs)
    except Exception:
        logger.error("\n%s" % (traceback.format_exc()))


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("#################################################")
    logger.debug("call plugin %s from %s" % (plugin, message["from"]))
    logger.debug(json.dumps(data, indent=4))
    logger.debug("#################################################")

    compteurcallplugin = getattr(xmppobject, "num_call%s" % action)
    logger.debug("compteur num_call pluging %s %s" % (action, compteurcallplugin))

    if compteurcallplugin == 0:
        xmppobject.typelistMonitoring_device = (
            XmppMasterDatabase().getlistMonitoring_devices_type()
        )
        logger.debug("list device %s" % (xmppobject.typelistMonitoring_device))

    machine = XmppMasterDatabase().getMachinefromjid(message["from"])
    logger.debug("Machine %s %s" % (machine["id"], machine["hostname"]))
    if "subaction" in data and data["subaction"].lower() in [
        "terminalinformations",
        "terminalalert",
    ]:
        # inscription message alert depuis machine
        statusmsg = ""
        if "status" in data:
            statusmsg = json.dumps(data["status"])
        id_mom_machine = XmppMasterDatabase().setMonitoring_machine(
            machine["id"], machine["hostname"], date=data["date"], statusmsg=statusmsg
        )
        # for each device/service call process
        if "device_service" in data:
            for element in data["device_service"]:
                for devicename in element:
                    # call process functions defined
                    if devicename.lower() in xmppobject.typelistMonitoring_device:
                        # globals()["process_%s"%element](data['opticalReader'])
                        callFunction(
                            devicename,
                            xmppobject,
                            str(message["from"]),
                            sessionid,
                            element[devicename],
                            machine["id"],
                            machine["hostname"],
                            id_mom_machine,
                        )
