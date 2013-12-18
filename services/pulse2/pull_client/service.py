# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Pulse Pull Client.
#
# Pulse Pull client is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse Pull Client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
import cx_Threads
import logging
import logging.config
import threading

from poller import Poller
from config import PullClientConfig


class Handler(object):

    # no parameters are permitted; all configuration should be placed in the
    # configuration file and handled in the Initialize() method
    def __init__(self):
        self.stopEvent = cx_Threads.Event()
        self.pollerStop = threading.Event()
        self.config = PullClientConfig.instance()
        logging.config.fileConfig(self.config.config_file)

    # called when the service is starting
    def Initialize(self, configFileName):
        pass

    # called when the service is starting immediately after Initialize()
    # use this to perform the work of the service; don't forget to set or check
    # for the stop event or the service GUI will not respond to requests to
    # stop the service
    def Run(self):
        logger = logging.getLogger()
        logger.info("PullClient starting...")
        self.poller = Poller(self.pollerStop)
        self.poller.start()
        logger.info("PullClient started.")
        self.stopEvent.Wait()

    # called when the service is being stopped by the service manager GUI
    def Stop(self):
        logger = logging.getLogger()
        logger.info("PullClient stopping...")
        self.pollerStop.set()
        self.poller.join()
        logger.info("PullClient stopped.")
        self.stopEvent.Set()
