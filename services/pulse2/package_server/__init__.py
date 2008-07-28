#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 30 2008-02-08 16:40:54Z nrueff $
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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

import os.path
import logging
import twisted
import re
import time
import signal
import os
import sys

from pulse2.package_server.config import config_addons
from pulse2.package_server.common import Common
from pulse2.package_server.utilities import Singleton
import pulse2.package_server.thread_webserver
from threading import Thread, Semaphore
import threading

"""
    Pulse2 PackageServer
"""

class ThreadPackageDetect(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.logger = logging.getLogger()
        self.config = config

    def log_message(self, format, *args):
        self.logger.info(format % args)

    def run(self):
        while 1:
            time.sleep(self.config.package_detect_loop)
            if self.config.package_detect_tmp_activate:
                Common().moveCorrectPackages()
            Common().detectNewPackages()
    
class ThreadLauncher(Singleton):
    def initialize(self, config):
        self.logger = logging.getLogger()
        self.config = config
        if self.config.package_detect_activate:
            self.logger.debug("Package detect is activated")
            if self.config.package_detect_tmp_activate:
                self.logger.debug("Package detect in temporary folder is activated")
    
        if config.package_detect_activate:
            self.logger.debug("Starting package detect thread")
            threadpd = ThreadPackageDetect(config)
            threadpd.setDaemon(True)
            threadpd.start()
            self.logger.debug("Package detect thread started")

        thread_webserver.initialize(self.config)
