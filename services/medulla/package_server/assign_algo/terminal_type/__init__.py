#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
    Medulla2 PackageServer
"""

from mmc.site import mmcconfdir

from medulla.package_server.assign_algo import MMAssignAlgo
from medulla.package_server.assign_algo.terminal_type.database import (
    PluginInventoryAADatabase,
)
from medulla.package_server.assign_algo.terminal_type.config import (
    PluginInventoryAAConfig,
)


class MMUserAssignAlgo(MMAssignAlgo):
    name = "terminal_type"
    assign = {}

    def init(
        self,
        mirrors,
        mirrors_fallback,
        package_apis,
        url2mirrors,
        url2mirrors_fallback,
        url2package_apis,
    ):
        MMAssignAlgo.init(
            self,
            mirrors,
            mirrors_fallback,
            package_apis,
            url2mirrors,
            url2mirrors_fallback,
            url2package_apis,
        )
        self.config = PluginInventoryAAConfig()
        self.config.setup(
            mmcconfdir + "/medulla/package-server/plugin_terminal_type.ini"
        )
        self.database = PluginInventoryAADatabase()
        self.database.activate(self.config)
        self.populateCache()
        self.logger.debug("init done for terminal_type assign algo")

    def populateCache(self):
        """
        Map machines UUIDs to type
        """
        self.logger.info("Populating computer type cache")
        self.types = {}
        for row in self.database.buildPopulateCacheQuery():
            self.types["UUID" + str(row[2])] = row[0].Value
        self.logger.info("Populate done (%d computers)" % len(self.types))

    def __getMachineType(self, m):
        try:
            ret = self.types[m["uuid"]]
        except KeyError:
            ret = self.database.getMachineType(m["uuid"])
            # Put result in memory cache
            self.types[m["uuid"]] = ret
        return ret

    def getMachineMirror(self, m):
        if not m["uuid"] in self.assign:
            self.assign[m["uuid"]] = {}
        if "getMirror" not in self.assign[m["uuid"]]:
            type = self.__getMachineType(m)
            self.assign[m["uuid"]]["getMirror"] = []
            if type is not None:
                for u in self.config.type2url[type]["mirror"]:
                    self.assign[m["uuid"]]["getMirror"].append(self.url2mirrors[u])
        return self.assign[m["uuid"]]["getMirror"]

    def getMachineMirrorFallback(self, m):
        if not m["uuid"] in self.assign:
            self.assign[m["uuid"]] = {}
        if "getFallbackMirror" not in self.assign[m["uuid"]]:
            type = self.__getMachineType(m)
            self.assign[m["uuid"]]["getFallbackMirror"] = []
            if type is not None:
                for u in self.config.type2url[type]["mirror"]:
                    self.assign[m["uuid"]]["getFallbackMirror"].append(
                        self.url2mirrors_fallback[u]
                    )
        return self.assign[m["uuid"]]["getFallbackMirror"]

    def getMachinePackageApi(self, m):
        if not m["uuid"] in self.assign:
            self.assign[m["uuid"]] = {}
        if "getMachinePackageApi" not in self.assign[m["uuid"]]:
            type = self.__getMachineType(m)
            self.assign[m["uuid"]]["getMachinePackageApi"] = []
            if type is not None:
                for u in self.config.type2url[type]["package_api"]:
                    self.assign[m["uuid"]]["getMachinePackageApi"].append(
                        self.url2package_apis[u]
                    )
        return self.assign[m["uuid"]]["getMachinePackageApi"]

    def getComputersPackageApi(self, machines):
        pass
