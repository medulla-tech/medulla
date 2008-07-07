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

# classical Python modules
import os
import time
import signal
import logging
from new import instancemethod

# Twisted stuff
import twisted.internet.defer
import twisted.internet.reactor
import twisted.internet.protocol

# Launcher stuff
from pulse2.launcher.utils import Singleton

def commandRunner(cmd, cbCommandEnd):
    """
    Return a Deferred resulting in the stdout output of a shell command.
    """
    process = commandProtocol(cmd)
    # FIXME: codec should be taken from conf file
    process.handler = twisted.internet.reactor.spawnProcess(process, cmd[0], map(lambda(x): x.encode('utf-8', 'ignore'), cmd), None)
    process.deferred = twisted.internet.defer.Deferred()
    process.deferred.addCallback(cbCommandEnd)
    return process.deferred

def commandForker(cmd, cbCommandEnd, id, defer_results, callbackName):
    """
    """
    process = commandProtocol(cmd)
    if not ProcessList().addProcess(process, id): # a process with the same ID already exists
        logging.getLogger().warn('Attempt to add command %d twice' % id)
        return False
    # FIXME: codec should be taken from conf file
    process.handler = twisted.internet.reactor.spawnProcess(process, cmd[0], map(lambda(x): x.encode('utf-8', 'ignore'), cmd), None)
    process.returnxmlrpcfunc = callbackName
    process.id = id
    process.defer_results = defer_results
    process.endback = cbCommandEnd
    return True

class commandProtocol(twisted.internet.protocol.ProcessProtocol):

    def __init__(self, cmd):
        # command data
        self.cmd = cmd
        self.done = False
        self.id = id
        self.status = ""
        self.handler = None

        # command output
        self.stdout = ""
        self.stderr = ""
        self.stdall = ""
        self.exit_code = None

        # command stats
        timestamp = time.time()
        self.start_time = timestamp
        self.last_see_time = timestamp
        self.last_stdout_time = 0
        self.last_stderr_time = 0
        self.end_time = 0

        # command handling
        self.returnxmlrpcfunc = None
        self.endback = None
        self.defer_results = False
        self.deferred = None

    def write(self,data):
        self.transport.write(data)
        self.stdall += "<<" + data

    def outReceived(self, data):
        self.stdout += data
        self.stdall += ">>" + data
        self.lastout = data
        timestamp = time.time()
        self.last_see_time = timestamp
        self.last_stdout_time = timestamp

    def errReceived(self, data):
        self.stderr += data
        self.stdall += ">>" + data
        timestamp = time.time()
        self.last_see_time = timestamp
        self.last_stderr_time = timestamp

    def processEnded(self, reason):
        self.done = True
        self.exit_code = reason.value.exitCode
        timestamp = time.time()
        self.last_see_time = timestamp
        self.end_time = timestamp
        if self.deferred:                   # if deffered exists, we should be in sync mode
            self.deferred.callback(self)    # fire callback
            return                          # and stop (will not go further)
        if not self.defer_results:          # if we have to send results when available (ie defer_results == False)
            self.installEndBack()           # install and fire callback immediately

    def installEndBack(self):
        self.deferred = twisted.internet.defer.Deferred()
        self.deferred.addCallback(self.endback)
        self.deferred.callback(self)

    def getExitCode(self):
        return self.exitCode

    def getPID(self):
        return self.hanlder.pid

    def sendSignal(self, signal):
        # signal is posix signal ID, see kill -l
        logging.getLogger().debug('Send signal %s to command %s' % (signal, self.id) )
        try:
            self.handler.signalProcess(signal)
        except:
            logging.getLogger().warn('Send signal %s to command %s which is already finished' % (signal, self.id) )
        return True

    def sendSigCont(self):
        # signal is posix signal ID
        self.sendSignal(signal.SIGCONT)

    def sendSigStop(self):
        # signal is posix signal ID
        self.sendSignal(signal.SIGSTOP)

    def sendSigHup(self):
        # signal is posix signal ID
        self.sendSignal(signal.SIGHUP)

    def sendSigKill(self):
        # signal is posix signal ID
        self.sendSignal(signal.SIGKILL)

    def sendSigInt(self):
        # signal is posix signal ID
        self.sendSignal(signal.SIGINT)

    def sendSigUsr1(self):
        # signal is posix signal ID
        self.sendSignal(signal.SIGUSR1)

    def sendSigUsr2(self):
        # signal is posix signal ID
        self.sendSignal(signal.SIGUSR2)

    def getElapsedTime(self):
        return self.last_see_time - self.start_time

class ProcessList(Singleton):
    """
        Launcher core: kep a track of launched commands
    """
    _processArr = dict()
    _event = list()

    """ Process handling """
    def addProcess(self, obj, id):
        if id in self._processArr.keys():
            return False
        self._processArr[id] = obj
        return True

    def getProcess(self, id):
        if id in self._processArr:
            return self._processArr[id]
        return None

    def existsProcess(self, id):
        return id in self.listProcesses()

    def removeProcess(self, id):
        del self._processArr[id]

    def getProcessStdout(self, id, purge = False):
        if self.existsProcess(id):
            ret = self.getProcess(id).stdout;
        else:
            return None
        if purge:
            self.getProcess(id).stdout = '';
        return ret

    def getProcessStderr(self, id, purge = False):
        if self.existsProcess(id):
            ret = self.getProcess(id).stderr;
        else:
            return None
        if purge:
            self.getProcess(id).stderr = '';
        return ret

    def getProcessExitcode(self, id):
        if self.existsProcess(id):
            return self.getProcess(id).getExitCode();
        return None

    def getProcessExitcode(self, id):
        if self.existsProcess(id):
            return self.getProcess(id).getExitCode();
        return None

    def getProcessTimes(self, id):
        if self.existsProcess(id):
            return {
                'start': self.getProcess(id).start_time,
                'last': self.getProcess(id).last_see_time,
                'end': self.getProcess(id).end_time,
                'now': time.time(),
                'elaped': self.getProcess(id).last_see_time - self.getProcess(id).start_time
            }
        return None

    """ Massive process handling """
    def listProcesses(self):
        """ The process list """
        return self._processArr

    def getProcessIds(self):
        return self.listProcesses().keys()

    def getProcessCount(self):
        return len(self.listProcesses())

    def getProcessList(self):
        return self.listProcesses().values()

    """ Zombies handling """
    def listZombies(self):
        """ a zombie is a command already finished which has not been processed yet """
        ret={}
        for k, v in self.listProcesses().iteritems():
            if v.done:
                ret[k] = v
        return ret

    def getZombieIds(self):
        ret=[]
        for process in self.listZombies().values():
            ret.append(process.id)
        return ret

    def getZombiesCount(self):
        return len(self.listZombies())

    """ Running handling """
    def listRunning(self):
        """ a running process is a command not yet finished """
        ret={}
        for k, v in self.listProcesses().iteritems():
            if not v.done:
                ret[k] = v
        return ret

    def getRunningIds(self):
        ret=[]
        for process in self.listRunning():
            ret.append(process.id)
        return ret

    def getRunningCount(self):
        return len(self.listRunning())

""" XMLRPC functions """
def get_process_count():
    return ProcessList().getProcessCount()
def get_running_count():
    return ProcessList().getRunningCount()
def get_zombie_count():
    return ProcessList().getZombieCount()

def get_process_ids():
    return ProcessList().getProcessIds()
def get_running_ids():
    return ProcessList().getRunningIds()
def get_zombie_ids():
    return ProcessList().getZombieIds()


def get_process_stderr(id):
    return ProcessList().getProcessStderr(id)
def get_process_stdout(id):
    return ProcessList().getProcessStdout(id)
def get_process_exitcode(id):
    return ProcessList().getProcessExitcode(id)
def get_process_times(id):
    return ProcessList().getProcessTimes(id)

def stop_process(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigStop()

def cont_process(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigCont()
def int_process(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigInt()
def kill_process(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigKill()
def hup_process(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigHup()
