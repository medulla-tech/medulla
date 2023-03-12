#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import logging


plugin = {"VERSION": "1.0", "NAME": "applicationdeployment", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    try:
        if "Dtypequery" in data:
            if data["Dtypequery"] == "TED":
                print("Delete session %s" % sessionid)
                # Set deployment to done in database
                xmppobject.session.clear(sessionid)

                if __debug__:
                    logging.getLogger().debug(
                        "_______________________RESULT DEPLOYMENT________________________"
                    )
                    logging.getLogger().debug(json.dumps(data["descriptor"]))
                    logging.getLogger().debug(
                        "________________________________________________________________"
                    )
            elif data["Dtypequery"] == "TE":
                # clear session
                xmppobject.session.clear(sessionid)
                # Set deployment to error in database
            else:
                # Update session with data
                xmppobject.session.sessionsetdata(sessionid, data)
        pass
    except Exception as e:
        logging.getLogger().error("Error in plugin %s : %s" % (plugin["NAME"], str(e)))
