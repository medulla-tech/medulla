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
# file plugins/xmppmaster/master/agentmaster.py

import sys
import os
import zlib
import base64
import json
from .lib.utils import *
from mmc.plugins.xmppmaster.config import xmppMasterConfig
import traceback
import logging
import threading
from mmc.agent import PluginManager
import asyncio


sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
sys.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "pluginsmaster")
)

logger = logging.getLogger()
xmpp = None


def ObjectXmpp():
    return PluginManager().getEnabledPlugins()["xmppmaster"].messagefilexmpp


def getXmppstrConfiguration():
    return str(xmppMasterConfig().__dict__)


def getXmppConfiguration():
    return xmppMasterConfig().__dict__


def send_message_json(to, jsonstring):
    ObjectXmpp().send_message_json(to, jsonstring)


def callXmppFunction(functionname, *args, **kwargs):
    logging.getLogger().debug("**call function %s %s %s" % (functionname, args, kwargs))
    return getattr(ObjectXmpp(), functionname)(*args, **kwargs)


def callXmppPlugin(plugin, data):
    logging.getLogger().debug("**call plugin %s" % (plugin))
    ObjectXmpp().callpluginmasterfrommmc(plugin, data)


def callInventory(to):
    ObjectXmpp().callinventory(to)


def callrestartbymaster(to):
    return ObjectXmpp().callrestartbymaster(to)


def callrestartbotbymaster(to):
    return ObjectXmpp().restartAgent(to)


def callshutdownbymaster(to, time, msg):
    return ObjectXmpp().callshutdownbymaster(to, time, msg)


def callvncchangepermsbymaster(to, askpermission):
    return ObjectXmpp().callvncchangepermsbymaster(to, askpermission)


##################### call synchronous iq##########################


def callremotefile(jidmachine, currentdir="", timeout=40):
    strctfilestrcompress = ObjectXmpp().iqsendpulse(
        jidmachine, {"action": "remotefile", "data": currentdir}, timeout
    )
    try:
        strctfilestr = zlib.decompress(base64.b64decode(strctfilestrcompress))
        return strctfilestr
    except Exception as e:
        logger.error("%s" % (traceback.format_exc()))
    return strctfilestrcompress


def calllistremotefileedit(jidmachine):
    return ObjectXmpp().iqsendpulse(
        jidmachine, {"action": "listremotefileedit", "data": ""}, 10
    )


def callremotefileeditaction(jidmachine, data, timeout=10):
    return ObjectXmpp().iqsendpulse(
        jidmachine, {"action": "remotefileeditaction", "data": data}, timeout
    )


def callremotecommandshell(jidmachine, command="", timeout=20):
    return ObjectXmpp().iqsendpulse(
        jidmachine,
        {"action": "remotecommandshell", "data": command, "timeout": timeout},
        timeout,
    )


def callremoteXmppMonitoring(jidmachine, subject, timeout=15):
    return ObjectXmpp().iqsendpulse(
        jidmachine,
        {"action": "remotexmppmonitoring", "data": subject, "timeout": timeout},
        timeout,
    )


def calllocalfile(currentdir=""):
    return ObjectXmpp().xmppbrowsingpath.listfileindir(currentdir)


def callInstallKey(jidAM, jidARS):
    return ObjectXmpp().callInstallKey(jidAM, jidARS)


# #################################################################


class XmppCommandDiffered:
    """
    Thread in charge of running precommand
    Pre-command complete
    send_session_command with session self,
    Session complete runs post command
    """

    def __init__(self, to, action, data, timeout, precommand, postcommand):
        self.xmpp = ObjectXmpp()
        if self.xmpp is not None:
            self.namethread = name_random(5, "thread")
            self.e = threading.Event()
            self.t = timeout
            self.to = to
            self.action = action
            self.data = data
            self.precommand = precommand
            self.postcommand = postcommand
            self.t2 = threading.Thread(name=self.namethread, target=self.differed)
            self.t2.start()
        else:
            logger.debug("XmppCommandDiffered error XMPP not initialized")
            pass

    def differed(self):
        """
        Code that runs during execution of the thread.
        """
        # Pre-command
        self.xmpp = ObjectXmpp()
        if self.precommand is not None:
            logger.debug("exec command %s" % self.precommand)
            a = simplecommandstr(self.precommand)
            if a["code"] != 0:
                return
            logger.debug(a["result"])
        # Executes XMPP command
        # XMPP command with session creation
        self.sessionid = self.xmpp.send_session_command(
            self.to,
            self.action,
            self.data,
            datasession=None,
            encodebase64=False,
            time=self.t,
            eventthread=self.e,
        )

        # Post-command running after XMPP Command
        if self.postcommand is not None:
            while not self.e.isSet():
                # Wait for timeout or event thread
                event_is_set = self.e.wait(self.t)
                if event_is_set:
                    # After session completes, execute post-command shell
                    b = simplecommandstr(self.postcommand)
                    # Sends b['result'] to log
                    logger.debug(b["result"])
                else:
                    # Timeout
                    if not self.xmpp.session.isexist(self.sessionid):
                        logger.debug("Action session %s timed out" % self.action)
                        logger.debug("Timeout error")
                        break


class XmppSimpleCommand:
    """
    Run XMPP command with session and timeout
    Thread waits for timeout or end of session
    Returns command result
    """

    def __init__(self, to, data, timeout):
        # Get reference on master agent xmpp
        self.xmpp = ObjectXmpp()
        self.e = threading.Event()
        self.result = {}
        self.data = data
        self.t = timeout
        self.sessionid = data["sessionid"]
        self.session = self.xmpp.session.createsessiondatainfo(
            data["sessionid"], {}, self.t, self.e
        )
        self.xmpp.send_message(mto=to, mbody=json.dumps(data), mtype="chat")
        self.t2 = threading.Thread(name="command", target=self.resultsession)
        self.t2.start()

    def resultsession(self):
        while not self.e.isSet():
            event_is_set = self.e.wait(self.t)
            logger.debug("The event is set to: %s" % event_is_set)
            if event_is_set:
                self.result = self.session.datasession
            else:
                self.result = {
                    "action": "resultshellcommand",
                    "sessionid": self.sessionid,
                    "base64": False,
                    "data": {"msg": "ERROR command\n timeout %s" % self.t},
                    "ret": 125,
                }
                break
        self.xmpp.session.clearnoevent(self.sessionid)
        return self.result


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()
