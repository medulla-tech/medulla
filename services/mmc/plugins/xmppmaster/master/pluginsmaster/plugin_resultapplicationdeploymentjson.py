#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import traceback
from pulse2.database.xmppmaster import XmppMasterDatabase

logger = logging.getLogger()

plugin = {"VERSION": "1.3", "NAME": "resultapplicationdeploymentjson", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")
    try:
        if ret == 0:
            logger.debug(
                "Succes deploy on %s Package "
                ": %s Session : %s"
                % (message["from"], data["descriptor"]["info"]["name"], sessionid)
            )
            XmppMasterDatabase().delete_resources(sessionid)
        else:
            msg = "Deployment error on %s [Package " ": %s / Session : %s]" % (
                message["from"],
                data["descriptor"]["info"]["name"],
                sessionid,
            )
            logger.error(msg)

            if "status" in data and data["status"] != "":
                XmppMasterDatabase().updatedeploystate(sessionid, data["status"])
            else:
                XmppMasterDatabase().updatedeploystate(
                    sessionid, "ABORT PACKAGE EXECUTION ERROR"
                )
            xmppobject.xmpplog(
                msg,
                type="deploy",
                sessionname=sessionid,
                priority=-1,
                action="xmpplog",
                who="",
                how="",
                why=xmppobject.boundjid.bare,
                module="Deployment | Start | Creation",
                date=None,
                fromuser="",
                touser="",
            )
    except:
        logger.error("%s" % (traceback.format_exc()))
