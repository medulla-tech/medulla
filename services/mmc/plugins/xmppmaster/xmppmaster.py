# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import threading
import time
import logging
from master.agentmaster import MUCBot

from mmc.plugins.xmppmaster.config import xmppMasterConfig
from mmc.agent import PluginManager

logger = logging.getLogger()


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class xmppMasterthread(threading.Thread):

    def __init__(self, args=(), kwargs=None):
        threading.Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.disable = xmppMasterConfig().disable
        self.xmpp = None

    def doTask(self):
        tg = xmppMasterConfig()
        if tg.debugmode == "NOTSET":
            tg.debugmode = 0
        elif tg.debugmode == "DEBUG":
            tg.debugmode = 10
        elif tg.debugmode == "INFO":
            tg.debugmode = 20
        if tg.debugmode == "LOG" or tg.debugmode == "DEBUGPULSE":
            tg.debugmode = 25
        elif tg.debugmode == "WARNING":
            tg.debugmode = 30
        elif tg.debugmode == "ERROR":
            tg.debugmode = 40
        elif tg.debugmode == "CRITICAL":
            tg.debugmode = 50
        logging.basicConfig(level=tg.debugmode,
                            format='[%(name)s.%(funcName)s:%(lineno)d] %(message)s')
        #logging.log(tg.debugmode,"=======================================test log")
        self.xmpp = MUCBot(tg)
        self.xmpp.register_plugin('xep_0030')  # Service Discovery
        self.xmpp.register_plugin('xep_0045')  # Multi-User Chat
        self.xmpp.register_plugin('xep_0004')  # Data Forms
        self.xmpp.register_plugin('xep_0050')  # Adhoc Commands
        self.xmpp.register_plugin('xep_0199', {'keepalive': True,
                                               'frequency': 300,
                                               'interval': 300,
                                               'timeout': 200})
        self.xmpp.register_plugin('xep_0077')  # Registration
        # xmpp.register_plugin('xep_0047') # In-band Registration
        # xmpp.register_plugin('xep_0096') # file transfer
        # xmpp.register_plugin('xep_0095') # file transfer
        self.xmpp['xep_0077'].force_registration = False
        self.xmpp.register_plugin('xep_0279')
        if tg.Server == "" or tg.Port == "":
            logger.error("Parameters connection server xmpp missing.")
        if self.xmpp.connect(address=(tg.Server, tg.Port)):
            self.xmpp.process(block=True)
            logger.info("done")
        else:
            logger.info("Unable to connect.")

    # todo faire class
    def stopxmpp(self):
        if self.xmpp != None:
            # _remove_schedules
            self.xmpp.scheduler.quit()
            self.xmpp.session.sessionstop()
            time.sleep(2)
            #xmpp.scheduler.remove("manage session")
            self.xmpp.disconnect()

    def run(self):
        logger.info("Start XmppMaster")
        self.doTask()

    def stop(self):
        self.stopxmpp()
