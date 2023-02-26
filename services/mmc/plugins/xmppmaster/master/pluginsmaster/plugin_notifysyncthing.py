#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import base64
import json
import os
import mmc.plugins.xmppmaster.master.lib.utils
import pprint
import logging
from pulse2.database.pkgs import PkgsDatabase
logger = logging.getLogger()

plugin = { "VERSION" : "1.2", "NAME" : "notifysyncthing", "TYPE" : "master" }

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug(plugin)
    logger.debug("=====================================================")
    print json.dumps(data, indent = 4)
    if 'suppdir' in data or 'adddir' in data:
        logger.debug("removing package %s %s %s"%( data['packageid'], 'create', str(message['from'])))
        PkgsDatabase().pkgs_unregister_synchro_package( data['packageid'],
                                                      None,
                                                      str(message['from']))
    elif 'MotifyFile' in data:
        logger.debug("removing package %s %s %s"%( data['packageid'], 'chang', str(message['from'])))
        PkgsDatabase().pkgs_unregister_synchro_package( data['packageid'],
                                                      'chang',
                                                      str(message['from']))
