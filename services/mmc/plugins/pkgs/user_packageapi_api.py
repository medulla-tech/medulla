# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This module define the user package_api API
It provide methods to tell which package_api a user can use to modify packages.
"""
import logging
from mmc.support.mmctools import Singleton
import pulse2.apis.clients.user_packageapi_api
import mmc

class UserPackageApiApi(Singleton):
    initialized = False

    def __init__(self):
        if self.initialized:
            return
        self.logger = logging.getLogger()
        self.logger.debug("Going to initialize UserPackageApiApi")
        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")
        credentials = ""

        if self.config.upaa_enablessl:
            self.server_addr = "https://"
        else:
            self.server_addr = "http://"

        if self.config.upaa_username != "":
            self.server_addr += self.config.upaa_username
            credentials += self.config.upaa_username
            if self.config.upaa_password != "":
                self.server_addr += ":" + self.config.upaa_password
                credentials += ":" + self.config.upaa_password
            self.server_addr += "@"

        self.server_addr += (
            self.config.upaa_server
            + ":"
            + str(self.config.upaa_port)
            + self.config.upaa_mountpoint
        )
        self.logger.debug("UserPackageApiApi will connect to %s" % (self.server_addr))

        if self.config.upaa_verifypeer:
            self.internal = pulse2.apis.clients.user_packageapi_api.UserPackageApiApi(
                credentials,
                self.server_addr,
                self.config.upaa_verifypeer,
                self.config.upaa_cacert,
                self.config.upaa_localcert,
            )
        else:
            self.internal = pulse2.apis.clients.user_packageapi_api.UserPackageApiApi(
                credentials, self.server_addr
            )

        for method in ("getUserPackageApi",):
            setattr(self, method, getattr(self.internal, method))

        self.initialized = True
