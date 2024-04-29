# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 20145 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import logging
import logging.config

import cx_Logging
import cx_Threads

from medullaagent.config import Config
from medullaagent.control import Dispatcher


class Handler(object):
    def __init__(self):
        path = os.path.dirname(os.path.abspath(__file__))
        if "library.zip" in path:
            path = os.path.dirname(path)
        cfg_path = os.path.join(path, "medullaagent.ini")
        logging.config.fileConfig(cfg_path)

        self.stopEvent = cx_Threads.Event()
        config = Config()
        config.read(cfg_path)
        self.dp = Dispatcher(config)

    def Initialize(self, configFileName):
        pass

    def Run(self):
        logger = logging.getLogger()
        cx_Logging.Info("Medulla2 Agent starting...")
        self.dp.mainloop()
        logger.info("Medulla2 Agent started.")
        self.stopEvent.Wait()

    def Stop(self):
        logger = logging.getLogger()
        cx_Logging.Info("Medulla2 Agent stopping...")
        logger.info("Medulla2 Agent stopped.")
        self.stopEvent.Set()
