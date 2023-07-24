# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
This module define the scheduler API
It provides methods to know which scheduler is a computer depending on
"""

from pulse2.apis import makeURL
from twisted.internet import defer

from pulse2.apis.clients import Pulse2Api


class SchedulerApi(Pulse2Api):  # Singleton
    def __init__(self, default_scheduler, *attr):
        self.name = "SchedulerApi"
        self.default_scheduler = default_scheduler
        Pulse2Api.__init__(self, *attr)

    def setConfig(self, config):
        self.config = config

    def convert2id(self, scheduler):
        self.logger.debug("Looking up scheduler id using: " + str(scheduler))
        ret = None
        if isinstance(scheduler, dict):
            if (
                "server" in scheduler
                and "port" in scheduler
                and scheduler["server"]
                and scheduler["port"]
            ):
                (scheduler, credentials) = makeURL(scheduler)
            elif "mountpoint" in scheduler and scheduler["mountpoint"]:
                ret = scheduler["mountpoint"]
        elif type(scheduler) in (str, str):
            ret = scheduler
        if not ret:
            # if type(scheduler) in (str, unicode) and scheduler in
            # self.config.scheduler_url2id:
            if (
                type(scheduler) in (str, str)
                and scheduler in self.config.scheduler_url2id
            ):
                self.logger.debug(
                    "Found scheduler id from MSC config file using this key %s"
                    % scheduler
                )
                ret = self.config.scheduler_url2id[scheduler]
        if not ret:
            self.logger.debug("Using default scheduler")
            ret = self.config.default_scheduler
        self.logger.debug("Using scheduler '%s'" % ret)
        return ret

    def cb_convert2id(self, result):
        if isinstance(result, list):
            return [self.convert2id(s) for s in result]
        else:
            return self.convert2id(result)

    def getDefaultScheduler(self):
        return defer.succeed(self.default_scheduler)

    def getScheduler(self, machine):
        if self.config.sa_enable:
            machine = self.convertMachineIntoH(machine)
            d = self.callRemote("getScheduler", machine)
            d.addErrback(self.onError, "SchedulerApi:getScheduler", machine)
            d.addCallback(self.cb_convert2id)
            return d
        else:
            return defer.succeed(self.default_scheduler)

    def getSchedulers(self, machines):
        if self.config.sa_enable:
            machines = [self.convertMachineIntoH(m) for m in machines]
            d = self.callRemote("getSchedulers", machines)
            d.addErrback(self.onError, "SchedulerApi:getSchedulers", machines)
            d.addCallback(self.cb_convert2id)
            return d
        else:
            return defer.succeed([self.default_scheduler for m in machines])

    def convertMachineIntoH(self, machine):
        if not isinstance(machine, dict):
            machine = {"uuid": machine}
        return machine
