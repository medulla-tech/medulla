#!/usr/bin/python3
# -*- coding: utf-8; -*-

import logging
import traceback
import sys
import json
from medulla.database.xmppmaster import XmppMasterDatabase

plugin = {"VERSION": "1.0", "NAME": "resultasynchroremoteQA", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    try:
        XmppMasterDatabase().setCommand_action(
            data["data"]["data"]["uuid_inventorymachine"],
            data["data"]["data"]["cmdid"],
            sessionid,
            "".join(data["result"]["result"]),
            typemessage="result",
        )

        print(json.dumps(data, indent=4))
    except Exception as e:
        logging.getLogger().error("Error loading plugin: %s" % str(e))
        traceback.print_exc(file=sys.stdout)
        pass
