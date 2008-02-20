# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

import os
from new import instancemethod

import twisted.internet.defer
import twisted.internet.reactor
import twisted.internet.protocol

from pulse2.launcher.utils import Singleton

def commandRunner(cmd, cbCommandEnd):
    """
    Return a Deferred resulting in the stdout output of a shell command.
    """
    process = commandProtocol(cmd)
    twisted.internet.reactor.spawnProcess(process, cmd[0], cmd, None)
    process.deferred = twisted.internet.defer.Deferred()
    process.deferred.addCallback(cbCommandEnd)
    return process.deferred

def commandForker(cmd, cbCommandEnd, id, defer_results, callbackName):
    """
    """
    process = commandProtocol(cmd)
    ProcessList().addProcess(process, id)
    twisted.internet.reactor.spawnProcess(process, cmd[0], cmd, None)
    process.returnxmlrpcfunc = callbackName
    process.id = id
    process.defer_results = defer_results
    process.endback = cbCommandEnd

class commandProtocol(twisted.internet.protocol.ProcessProtocol):

    def __init__(self, cmd):
        self.cmd = cmd
        self.done = False
        self.stdout = ""
        self.stderr = ""
        self.stdall = ""
        self.error_code = ""
        self.status = ""
        self.returnxmlrpcfunc = None
        self.id = id
        self.endback = None
        self.defer_results = False

    def write(self,data):
        self.transport.write(data)
        self.stdall += "<<" + data

    def outReceived(self, data):
        self.stdout += data
        self.stdall += ">>" + data
        self.lastout = data

    def errReceived(self, data):
        self.stderr += data
        self.stdall += ">>" + data

    def processEnded(self, reason):
        self.done = True
        self.exitCode = reason.value.exitCode
        if not self.defer_results:
            self.installEndBack()

    def installEndBack(self):
        self.deferred = twisted.internet.defer.Deferred()
        self.deferred.addCallback(self.endback)
        self.deferred.callback(self)

    def getExitCode(self):
        return self.exitCode

class ProcessList(Singleton):
    _processArr = dict()
    _event = list()

    def listProcesses(self):
        return self._processArr

    def getProcessesCount(self):
        return len(self.listProcesses())

    def getProcessesList(self):
        return self.listProcesses().values()

    def listZombies(self):
        ret={}
        for k, v in self.listProcesses().iteritems():
            if v.done:
                ret[k] = v
        return ret

    def getZombiesCount(self):
        return len(self.listZombies())

    def getZombiesList(self):
        return self.listZombies().values()

    def addProcess(self, obj, id):
        self._processArr[id] = obj

    def getProcess(self, id):
        return self._processArr[id]

    def rmProcess(self, id):
        del self._processArr[id]
