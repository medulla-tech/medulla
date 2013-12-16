#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
This module define the scheduler API
It provides methods to know which scheduler is a computer depending on
"""

from pulse2.apis import makeURL
from twisted.internet import defer

from pulse2.apis.clients import Pulse2Api

class SchedulerApi(Pulse2Api): # Singleton
    def __init__(self, default_scheduler, *attr):
        self.name = "SchedulerApi"
        self.default_scheduler = default_scheduler
        Pulse2Api.__init__(self, *attr)

    def setConfig(self, config):
        self.config = config

    def convert2id(self, scheduler):
        self.logger.debug("Looking up scheduler id using: " + str(scheduler))
        ret = None
        if type(scheduler) == dict:
            if "server" in scheduler and "port" in scheduler and scheduler["server"] and scheduler["port"]:
                (scheduler, credentials) = makeURL(scheduler)
            elif "mountpoint" in scheduler and scheduler["mountpoint"]:
                ret = scheduler["mountpoint"]
        elif type(scheduler) in (str, unicode):
            ret = scheduler
        if not ret:
            if type(scheduler) in (str, unicode) and self.config.scheduler_url2id.has_key(scheduler):
                self.logger.debug("Found scheduler id from MSC config file using this key %s" % scheduler)
                ret = self.config.scheduler_url2id[scheduler]
        if not ret:
            self.logger.debug("Using default scheduler")
            ret = self.config.default_scheduler
        self.logger.debug("Using scheduler '%s'" % ret)
        return ret

    def cb_convert2id(self, result):
        if type(result) == list:
            return map(lambda s: self.convert2id(s), result)
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
            machines = map(lambda m: self.convertMachineIntoH(m), machines)
            d = self.callRemote("getSchedulers", machines)
            d.addErrback(self.onError, "SchedulerApi:getSchedulers", machines)
            d.addCallback(self.cb_convert2id)
            return d
        else:
            return defer.succeed(map(lambda m: self.default_scheduler, machines))

    def convertMachineIntoH(self, machine):
        if type(machine) != dict:
            machine = {'uuid':machine}
        return machine

