#!/usr/bin/env python
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


# nota jfk todo implement class for gestion call from script or console.
import sys
import os
import platform
import os.path
import json
from multiprocessing import Process, Queue, TimeoutError
import threading
from utils import getRandomName, call_plugin
from sleekxmpp import jid
import traceback
import logging
import time

logger = logging.getLogger()


class manage_infoconsole:
    def __init__(self, queue_in, queue_out, objectxmpp):
        self.namethread = getRandomName(5, "threadevent")
        self.objectxmpp = objectxmpp
        self.queueinfo = queue_in
        self.queueinfoout = queue_out
        self.threadevent = threading.Thread(name=self.namethread, target=self.loopinfoconsol)
        self.threadevent.start()
        logging.info('manage event start')

    def loopinfoconsol(self):
        logging.info('loopinfoconsol')
        while True:
            try:
                event = self.queueinfo.get(60)
                if event == "quit":
                    break
                self.objectxmpp.gestioneventconsole(event, self.queueinfoout)
            except Exception as e:
                logging.error('error in manage infoconsole %s' % str(e))
        logging.error('quit infocommand')
