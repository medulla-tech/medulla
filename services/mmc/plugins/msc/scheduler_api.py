# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This module defined the scheduler API
It provides methods to know which scheduler to contact for a computer.
"""
import logging
from mmc.plugins.msc.config import MscConfig
from mmc.support.mmctools import Singleton
import pulse2.apis.clients.scheduler_api


class SchedulerApi(Singleton):
    initialized = False

    def __init__(self):
        if self.initialized:
            return
        self.logger = logging.getLogger()
        self.logger.debug("Going to initialize SchedulerApi")
        self.config = MscConfig()
        credentials = ""

        if self.config.sa_enable:
            if self.config.sa_enablessl:
                self.server_addr = "https://"
            else:
                self.server_addr = "http://"

            if self.config.sa_username != "":
                self.server_addr += self.config.sa_username
                credentials = self.config.sa_username
                if self.config.sa_password != "":
                    self.server_addr += ":" + self.config.sa_password
                    credentials += ":" + self.config.sa_password
                self.server_addr += "@"

            self.server_addr += (
                self.config.sa_server
                + ":"
                + str(self.config.sa_port)
                + self.config.sa_mountpoint
            )
            self.logger.debug("SchedulerApi will connect to %s" % (self.server_addr))

            if self.config.sa_verifypeer:
                self.internal = pulse2.apis.clients.scheduler_api.SchedulerApi(
                    MscConfig().default_scheduler,
                    credentials,
                    self.server_addr,
                    self.config.sa_verifypeer,
                    self.config.sa_cacert,
                    self.config.sa_localcert,
                )
            else:
                self.internal = pulse2.apis.clients.scheduler_api.SchedulerApi(
                    MscConfig().default_scheduler, credentials, self.server_addr
                )

        for method in ("getScheduler", "getSchedulers", "getDefaultScheduler"):
            setattr(self, method, getattr(self.internal, method))

        self.internal.setConfig(self.config)
        self.initialized = True
