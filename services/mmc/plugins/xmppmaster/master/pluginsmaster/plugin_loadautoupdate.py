# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import json
import os
import logging
from mmc.plugins.xmppmaster.master.lib.utils import getRandomName
from update_remote_agent import Update_Remote_Agent
import types
import ConfigParser
from sleekxmpp import jid
from pulse2.database.xmppmaster import XmppMasterDatabase

logger = logging.getLogger()
DEBUGPULSEPLUGIN = 25

# this plugin calling to starting agent

plugin = {"VERSION" : "1.3", "NAME" : "loadautoupdate", "TYPE" : "master"}

def action( objectxmpp, action, sessionid, data, msg, dataerreur):
    logger.debug("=====================================================")
    logger.debug("call %s from %s"%(plugin, msg['from']))
    logger.debug("=====================================================")

    compteurcallplugin = getattr(objectxmpp, "num_call%s"%action)

    if compteurcallplugin == 0:
        read_conf_remote_update(objectxmpp)
        logger.debug("Configuration remote update")
        objectxmpp.Update_Remote_Agentlist = Update_Remote_Agent(objectxmpp.diragentbase,
                                                       objectxmpp.loadautoupdate)

        objectxmpp.loadfingerprint = types.MethodType(loadfingerprint,
                                                      objectxmpp)
        objectxmpp.schedule('loadfingerprint',
                            objectxmpp.generate_baseagent_fingerprint_interval,
                            objectxmpp.loadfingerprint,
                            repeat=True)

def loadfingerprint(self):
    """
        Runs the load fingerprint
    """
    self.Update_Remote_Agentlist = Update_Remote_Agent(self.diragentbase,
                                                       self.loadautoupdate)
    logger.debug("load fingerprint: %s"%\
        self.Update_Remote_Agentlist.get_fingerprint_agent_base())


def read_conf_remote_update(objectxmpp):
    namefichierconf = plugin['NAME'] + ".ini"
    pathfileconf = os.path.join( objectxmpp.config.pathdirconffile, namefichierconf )
    if not os.path.isfile(pathfileconf):
        logger.error("plugin %s\nConfiguration file :" \
            "\n\t%s missing" \
        "\neg conf:\n[parameters]\n" \
            "diragentbase = /var/lib/pulse2/xmpp_baseremoteagent/\n" \
                "autoupdate = True"%(plugin['NAME'], pathfileconf))
        logger.warning("default value for diragentbase " \
            "is /var/lib/pulse2/xmpp_baseremoteagent/"\
            "\ndefault value for autoupdate is True")
        objectxmpp.diragentbase = "/var/lib/pulse2/xmpp_baseremoteagent/"
        objectxmpp.loadautoupdate = True
        objectxmpp.generate_baseagent_fingerprint_interval = 900
    else:
        Config = ConfigParser.ConfigParser()
        Config.read(pathfileconf)
        logger.debug("read file %s"%pathfileconf)
        if os.path.exists(pathfileconf + ".local"):
            Config.read(pathfileconf + ".local")
            logger.debug("read file %s.local"%pathfileconf)
        if Config.has_option("parameters", "diragentbase"):
            objectxmpp.diragentbase = Config.get('parameters', 'diragentbase')
        else:
            objectxmpp.diragentbase = "/var/lib/pulse2/xmpp_baseremoteagent/"
        if Config.has_option("parameters", "autoupdate"):
            objectxmpp.loadautoupdate = Config.getboolean('parameters', 'autoupdate')
        else:
            objectxmpp.loadautoupdate = True
        if Config.has_option("parameters", "autoupdatebyrelay"):
            objectxmpp.autoupdatebyrelay = Config.getboolean('parameters', 'autoupdatebyrelay')
        else:
            objectxmpp.autoupdatebyrelay = True
        if Config.has_option("parameters", "generate_baseagent_fingerprint_interval"):
            objectxmpp.generate_baseagent_fingerprint_interval = Config.getint('parameters', 'generate_baseagent_fingerprint_interval')
        else:
            objectxmpp.generate_baseagent_fingerprint_interval = 900
    logger.debug("directory base agent is %s"%objectxmpp.diragentbase)
    logger.debug("autoupdate agent is %s"%objectxmpp.loadautoupdate)
    logger.debug("generate baseagent "\
        "fingerprint interval agent is %s"%objectxmpp.generate_baseagent_fingerprint_interval)
    objectxmpp.senddescriptormd5 = types.MethodType(senddescriptormd5, objectxmpp)
    objectxmpp.plugin_loadautoupdate = types.MethodType(plugin_loadautoupdate, objectxmpp)

def senddescriptormd5(self, to):
    """
        send the agent's figerprint descriptor in database to update the machine
        Update remote agent
    """
    datasend = {"action": "updateagent",
                "data": {'subaction': 'descriptor',
                            'descriptoragent': self.Update_Remote_Agentlist.get_md5_descriptor_agent()},
                'ret': 0,
                'sessionid': getRandomName(5, "updateagent")}
    # Send catalog of files.
    logger.debug("Send descriptor to agent [%s] for update" % to)
    if self.autoupdatebyrelay:
        relayjid = XmppMasterDatabase().groupdeployfromjid(to)
        relayjid = jid.JID(str(relayjid[0])).bare
        datasend['data']['ars_update'] = relayjid
    self.send_message(to,
                      mbody=json.dumps(datasend),
                      mtype='chat')

def plugin_loadautoupdate(self, msg, data):
    # Manage update remote agent
    if self.loadautoupdate and 'md5agent' in data and \
        self.Update_Remote_Agentlist.get_fingerprint_agent_base() != data['md5agent']:
        if data['md5agent'].upper() != "DEV" or data['md5agent'].upper() != "DEBUG":
            # send md5 descriptor of the agent for remote update.
            self.senddescriptormd5(msg['from'])
