#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
    Medulla2 PackageServer
"""

import logging
import random
from medulla.package_server.types import Machine
from medulla.package_server.xmlrpc import MyXmlrpc


class SchedulerApi(MyXmlrpc):
    type = "SchedulerApi"

    def __init__(self, name, config):
        MyXmlrpc.__init__(self)
        self.name = name
        self.config = config
        self.logger = logging.getLogger()
        self.assign = {}
        if "schedulers" in self.config:
            self.schedulers = self.config["schedulers"].split(" ")
        else:
            self.schedulers = [""]
        self.logger.info("(%s) %s : initialised" % (self.type, self.name))

    def xmlrpc_getServerDetails(self):
        return self.config

    def xmlrpc_getScheduler(self, m):
        machine = Machine().from_h(m)
        if machine.uuid not in self.assign:
            self.assign[machine.uuid] = self.schedulers[
                random.randint(0, len(self.schedulers) - 1)
            ]
        return self.assign[machine.uuid]

    def xmlrpc_getSchedulers(self, machines):
        ret = []
        for m in machines:
            machine = Machine().from_h(m)
            if machine.uuid not in self.assign:
                self.assign[machine.uuid] = self.schedulers[
                    random.randint(0, len(self.schedulers) - 1)
                ]
            ret.append(self.assign[machine.uuid])
        return ret
