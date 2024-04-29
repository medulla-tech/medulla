#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
    Medulla2 PackageServer
"""

import logging
from medulla.package_server.assign_algo import MMAssignAlgo
from medulla.package_server.types import Machine
import random


class MMUserAssignAlgo(MMAssignAlgo):
    name = "multi_site"
    assign = {}

    def getMachineMirror(self, m):
        server = ""
        machine = Machine().from_h(m)
        if machine.uuid not in self.assign:
            self.assign[machine.uuid] = {}
        if "getMirror" not in self.assign[machine.uuid]:
            self.assign[machine.uuid]["getMirror"] = self.mirrors[
                random.randint(0, len(self.mirrors) - 1)
            ].toH()
            if "server" in m and m["server"] != "":
                server = m["server"]
                self.assign[machine.uuid]["getMirror"]["server"] = server
                if "servernane" and "entity_uuid" and "uuid" and "Entity_Name" in m:
                    logging.getLogger().info(
                        "getMachineMirror algo multi_site { machine id [%s] } { pserver ip [%s], name [%s] } { Entity id [%s], entity Name [%s] }"
                        % (
                            m["uuid"],
                            m["server"],
                            m["servernane"],
                            m["entity_uuid"],
                            m["Entity_Name"],
                        )
                    )
        return self.assign[machine.uuid]["getMirror"]

    def getMachineMirrorFallback(self, m):  # To be done
        return 0

    def getMachinePackageApi(self, m):
        machine = Machine().from_h(m)
        if machine.uuid not in self.assign:
            self.assign[machine.uuid] = {}
        if "getMachinePackageApi" not in self.assign[machine.uuid]:
            # ip server corresponding to the imaging server of this machine
            # Get the package apis and replace the server value
            self.assign[machine.uuid]["getMachinePackageApi"] = []
            self.assign[machine.uuid]["getMachinePackageApi"] += [
                papi.toH() for papi in self.package_apis
            ]
            for api in range(len(self.assign[machine.uuid]["getMachinePackageApi"])):
                if "server" in m and m["server"] != "":
                    self.assign[machine.uuid]["getMachinePackageApi"][api]["server"] = (
                        m["server"]
                    )
            if "servernane" and "entity_uuid" and "uuid" and "Entity_Name" in m:
                logging.getLogger().info(
                    "getMachinePackageApi algo multi_site { machine id [%s] } { pserver ip [%s], name [%s] } { Entity id [%s], entity Name [%s] }"
                    % (
                        m["uuid"],
                        m["server"],
                        m["servernane"],
                        m["entity_uuid"],
                        m["Entity_Name"],
                    )
                )
        return self.assign[machine.uuid]["getMachinePackageApi"]
