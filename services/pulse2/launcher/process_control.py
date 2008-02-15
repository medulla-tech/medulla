# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: config.py 31 2008-02-13 15:53:32Z nrueff $
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
import shutil
import re
from new import instancemethod
import time

import twisted.internet.defer
import twisted.internet.reactor
import twisted.internet.protocol

def shlaunchDeferred(cmd):
    """
    Return a Deferred resulting in the stdout output of a shell command.
    """
    def cb(shprocess):
        ret = shprocess.out.split("\n")
        if ret: ret.pop()
        return ret
    sh = shLaunchDeferred(cmd)
    sh.addCallback(cb)
    return sh

def shLaunchDeferred(cmd):
    """
    Return a deferred resulting to a shProcessProtocolNonBlocking instance
    """
    shProcess = shProcessProtocolNonBlocking(cmd)
    shProcess.deferred = twisted.internet.defer.Deferred()
    twisted.internet.reactor.spawnProcess(shProcess, "/bin/sh", ['/bin/sh','-c',cmd],env=os.environ)
    return shProcess.deferred

class shProcessProtocol(twisted.internet.protocol.ProcessProtocol):

    def __init__(self, cmd):
        self.cmd = cmd
        self.done = False
        self.error = False
        self.out = ""
        self.stdall = ""
        self.status = ""
        #last output
        self.lastout = ""
        self.err = ""
        #progress
        self.progress = -1
        #description
        self.desc = cmd
        #time
        self.time = time.time()

    def write(self,data):
        self.transport.write(data)
        self.stdall = self.stdall +"<<" + data

    def progressCalc(self, data):
        """
        Try to find a percentage of progression on command output, and put this
        into self.progress and self.status.
        """
        sre = re.search("([0-9]){1,2}", data)
        if sre:
            group = sre.group()
            if group:
                self.progress = group
                self.status = data

    def outReceived(self, data):
        self.out = self.out + data
        self.stdall = self.stdall + ">>"+ data
        self.lastout = data
        self.time = time.time() #update time
        self.progressCalc(data)

    def errReceived(self, data):
        self.err = self.err + data
        self.stdall = self.stdall + ">>"+ data
        self.error = True

    def processEnded(self, reason):
        self.exitCode = reason.value.exitCode
        self.progress = -1;
        self.done = True

    def getExitCode(self):
        while not self.done:
            twisted.internet.reactor.iterate()
        return self.exitCode

class shProcessProtocolNonBlocking(shProcessProtocol):

    def __init__(self, cmd):
        shProcessProtocol.__init__(self, cmd)

    def processEnded(self, status):
        shProcessProtocol.processEnded(self, status)
        self.deferred.callback(self)

    def getExitCode(self):
        return self.exitCode
