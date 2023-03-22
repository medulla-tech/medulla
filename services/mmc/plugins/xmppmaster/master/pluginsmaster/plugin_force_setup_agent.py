#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import base64
import json
import os
import sys
from mmc.plugins.xmppmaster.master.lib.utils import simplecommand, file_get_content, file_put_content
import pprint
import logging

import traceback

import datetime
import ConfigParser

from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.xmppmaster.config import xmppMasterConfig

plugin = {"VERSION": "1.4", "NAME": "force_setup_agent", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    print "_________________________"
    logging.getLogger().debug(plugin)
    # print json.dumps(data, indent = 4)
    print data['data'][0]
    print "_________________________"

    command = {'action': 'force_setup_agent',
               'base64': False,
               'sessionid': sessionid,
               'data': ''}
    xmppobject.send_message(mto=data['data'][0],
                            mbody=json.dumps(command),
                            mtype='chat')
