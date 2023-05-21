#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
    Pulse2 PackageServer
"""

import logging
from pulse2.package_server.types import Mirror
from pulse2.package_server.assign_algo import UPAssignAlgoManager
from pulse2.package_server.xmlrpc import MyXmlrpc


class UserPackageApi(MyXmlrpc):
    type = "UserPackageApi"

    def __init__(self, services=None, name="", assign_algo="default"):
        # Mutable dict services used as default argument to a method or
        # function
        services = services or {}
        MyXmlrpc.__init__(self)
        self.logger = logging.getLogger()
        self.name = name
        package_api_put = []

        try:
            for service in services:
                if service["type"] == "package_api_put":
                    if service["server"] == "":
                        service["server"] = "localhost"
                    package_api_put.append(
                        Mirror(
                            service["proto"],
                            service["server"],
                            service["port"],
                            service["mp"],
                        )
                    )
            self.logger.debug(
                "(%s) %s api user/packageApi server initialised"
                % (self.type, self.name)
            )
        except Exception as e:
            self.logger.error(
                "(%s) %s api user/packageApi server can't initialize correctly"
                % (self.type, self.name)
            )
            raise e

        self.assign_algo = UPAssignAlgoManager().getAlgo(assign_algo)
        self.assign_algo.init(package_api_put)

    def xmlrpc_getServerDetails(self):
        return [m.toH() for m in self.package_api_put]

    def xmlrpc_getUserPackageApi(self, u):
        return self.assign_algo.getUserPackageApi(u)
