# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
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

import threading
import time
import logging

from mmc.plugins.xmppmaster.config import xmppMasterConfig
from mmc.plugins.xmppmaster.master.agentmaster import doTask, stopxmpp
logger = logging.getLogger()

class xmppMasterthread(threading.Thread): 
    def __init__(self, args=(), kwargs=None):
        threading.Thread.__init__(self)
        self.args = args
        self.kwargs = kwargs
        self.disable = xmppMasterConfig().disable
        return

    def run(self):
        logger.info("Start XmppMaster")
        doTask()

    def stop(self):
        stopxmpp()
