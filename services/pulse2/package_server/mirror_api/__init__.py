#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
    Pulse2 PackageServer Mirror/Computer link API
"""

import logging
from pulse2.package_server.types import Mirror
from pulse2.package_server.assign_algo import MMAssignAlgoManager
from pulse2.package_server.xmlrpc import MyXmlrpc


class MirrorApi(MyXmlrpc):
    type = "MirrorApi"

    def __init__(self, services={}, name="", assign_algo="default"):
        MyXmlrpc.__init__(self)
        self.name = name
        self.mirrors = {}
        self.url2mirrors = {}
        self.assign = {}
        self.logger = logging.getLogger()
        # Mutable dict services used as default argument to a method or
        # function
        try:
            for service in services:
                if (
                    service["type"] == "package_api_get"
                    or service["type"] == "package_api_put"
                ):
                    type = "package_api"
                else:
                    type = service["type"]

                if type not in self.url2mirrors:
                    self.url2mirrors[type] = {}
                if type not in self.mirrors:
                    self.mirrors[type] = []
                if service["server"] == "":
                    service["server"] = "localhost"
                self.mirrors[type].append(
                    Mirror(
                        service["proto"],
                        service["server"],
                        service["port"],
                        service["mp"],
                    )
                )
                if "url" in service:
                    self.url2mirrors[type][service["url"]] = self.mirrors[type][-1]
            self.logger.debug(
                "(%s) %s api machine/mirror server initialised" % (self.type, self.name)
            )
        except Exception as e:
            self.logger.error(
                "(%s)%s api machine/mirror server can't initialize correctly"
                % (self.type, self.name)
            )
            raise e

        if "mirror" in self.mirrors:
            mirrors = self.mirrors["mirror"]
        else:
            mirrors = []
        if "package_api" in self.mirrors:
            package_api = self.mirrors["package_api"]
        else:
            package_api = []

        if "mirror" in self.url2mirrors:
            url2mirrors = self.url2mirrors["mirror"]
        else:
            url2mirrors = []
        if "package_api" in self.url2mirrors:
            url2package_api = self.url2mirrors["package_api"]
        else:
            url2package_api = []

        # TODO find a clean way to affect another class
        self.assign_algo = MMAssignAlgoManager().getAlgo(assign_algo)
        self.assign_algo.init(
            mirrors, mirrors, package_api, url2mirrors, url2mirrors, url2package_api
        )

    def xmlrpc_getServerDetails(self):
        ret = {}
        if "package_api" in self.mirrors:
            ret["package_api"] = [x.toH() for x in self.mirrors["package_api"]]
        if "mirror" in self.mirrors:
            ret["mirror"] = [x.toH() for x in self.mirrors["mirror"]]
        return ret

    def xmlrpc_getMirror(self, m):
        return self.assign_algo.getMachineMirror(m)

    def xmlrpc_getMirrors(self, machines):
        ret = []
        for m in machines:
            ret.append(self.assign_algo.getMachineMirror(m))
        return ret

    def xmlrpc_getFallbackMirror(self, m):
        return self.assign_algo.getMachineMirrorFallback(m)

    def xmlrpc_getFallbackMirrors(self, machines):
        ret = []
        for m in machines:
            ret.append(self.assign_algo.getMachineMirrorFallback(m))
        return ret

    def xmlrpc_getApiPackage(self, m):
        return self.assign_algo.getMachinePackageApi(m)

    def xmlrpc_getApiPackages(self, machines):
        ret = []
        for m in machines:
            ret.append(self.assign_algo.getMachinePackageApi(m))
        return ret
