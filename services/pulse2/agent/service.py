# -*- coding: utf-8; -*-
#
# (c) 2015 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Pulse.
#
# Pulse2 is free software; you can redistribute it and/or modify
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

import os
import logging
import logging.config

import cx_Logging
import cx_Threads

from config import Config
from control import Dispatcher


class Handler(object):

    def __init__(self):

        path = os.path.dirname(os.path.abspath(__file__))
        if "library.zip" in path:
            path = os.path.dirname(path)
        cfg_path = os.path.join(path, "agent.ini")
        logging.config.fileConfig(cfg_path)

        self.stopEvent = cx_Threads.Event()
        config = Config()
        config.read(cfg_path)
        self.dp = Dispatcher(config)

    def Initialize(self, configFileName):
        pass

    def Run(self):
        logger = logging.getLogger()
        cx_Logging.Info("Pulse2 Agent starting...")
        self.dp.mainloop()
        logger.info("Pulse2 Agent started.")
        self.stopEvent.Wait()

    def Stop(self):
        logger = logging.getLogger()
        cx_Logging.Info("Pulse2 Agent stopping...")
        logger.info("Pulse2 Agent stopped.")
        self.stopEvent.Set()

