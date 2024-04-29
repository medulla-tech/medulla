# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
this plugin check status of deploy
if deploy is pause, run, abandonned

"""
import json
import sys
from medulla.database.xmppmaster import XmppMasterDatabase
import traceback
import logging

plugin = {"VERSION": "1.0", "NAME": "machineexecutionscheduler", "TYPE": "master"}

"""
#eg : data plugin received
#{
    ...,
    ...,
    #"advanced": {
        #"idcmd": 1,
        #"countnb": 0,
        #"grp": 14,
        #"exec": false,
        #"exectime": "2017-10-18 07:25:11",
        #"nbtotal": 1,
        #"scheduling": true,
        #"login": "root"
    #},
    ...,
    ...
#}
"""
DEBUGPULSEPLUGIN = 25


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)

    advanced = data["advanced"]
    try:
        result = XmppMasterDatabase().checkstatusdeploy(advanced["idcmd"])
        advanced["actionscheduler"] = result  # abandonmentdeploy, run or pause
        datasend = {
            "action": data["fromaction"],
            "sessionid": sessionid,
            "data": advanced,
            "ret": 0,
            "base64": False,
        }
        xmppobject.send_message(
            mto=message["from"], mbody=json.dumps(datasend), mtype="chat"
        )
    except Exception as e:
        print("Error in plugin %s" % str(e))
        traceback.print_exc(file=sys.stdout)
        advanced["actionscheduler"] = "error"  # abandonmentdeploy, run or pause
        datasend = {
            "action": data["fromaction"],
            "sessionid": sessionid,
            "data": advanced,
            "ret": 0,
            "base64": False,
        }
        xmppobject.send_message(
            mto=message["from"], mbody=json.dumps(datasend), mtype="chat"
        )
