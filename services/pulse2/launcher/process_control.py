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

"""
This module spawns and controls commands executed by the launcher.
"""

# classical Python modules
import time
import signal
import logging

# Twisted stuff
import twisted.internet.defer
import twisted.internet.reactor
import twisted.internet.protocol

# Others Pulse2 Stuff
from pulse2.utils import Singleton, HasSufficientMemory
from pulse2.launcher.config import LauncherConfig
from pulse2.consts import PULSE2_WRAPPER_ERROR_SIGNAL_BASE

@HasSufficientMemory(70)
def commandRunner(cmd, cbCommandEnd):
    """
    Return a Deferred resulting in the stdout output of a shell command.
    Only used in sync mode.
    """
    process = commandProtocol(cmd)
    # FIXME: codec should be taken from conf file
    try:
        process.handler = twisted.internet.reactor.spawnProcess(
            process,
            cmd[0],
            map(lambda(x): x.encode('utf-8', 'ignore'), cmd),
            None, # env
            None, # path
            None, # uid
            None, # gid
            None, # usePTY
            { 0: "w", 1: 'r', 2: 'r' } # FDs: not closing STDIN (might be used)
        )
    except OSError, e:
        logging.getLogger().error('launcher %s: failed daemonization in commandRunner: %d (%s)' % (LauncherConfig().name, e.errno, e.strerror))
        return False
    logging.getLogger().debug('launcher %s: about to execute %s in commandRunner' % (LauncherConfig().name, ' '.join(cmd)))
    process.deferred = twisted.internet.defer.Deferred()
    process.deferred.addCallback(cbCommandEnd)
    return process.deferred

@HasSufficientMemory(70)
def commandForker(cmd, cbCommandEnd, id, defer_results, callbackName, max_exec_time, group, kind):
    """
    """
    if ProcessList().existsProcess(id):
        logging.getLogger().warn('launcher %s: attempted to add command #%s twice' % (LauncherConfig().name, id))
        return False

    if not ProcessList().isOneSlotFree():
        logging.getLogger().warn('launcher %s: running out of slot when adding command #%s' % (LauncherConfig().name, id))
        return False

    process = commandProtocol(cmd)
    process.id = id
    # FIXME: codec should be taken from conf file
    try:
        process.handler = twisted.internet.reactor.spawnProcess(
            process,
            cmd[0],
            map(lambda(x): x.encode('utf-8', 'ignore'), cmd),
            None, # env
            None, # path
            None, # uid
            None, # gid
            None, # usePTY
            { 1: 'r', 2: 'r' } # FDs: closing STDIN as not used
        )
    except OSError, e:
        logging.getLogger().error('launcher %s: failed daemonization in commandForker: %d (%s)' % (LauncherConfig().name, e.errno, e.strerror))
        # do some cleanup
        return False

    if not ProcessList().addProcess(process, id):
        logging.getLogger().warn('launcher %s: attempted to add command %s twice ??' % (LauncherConfig().name, id))
        # FIXME: need to do some cleanup
        return False

    logging.getLogger().debug('launcher %s: about to execute %s in commandForker' % (LauncherConfig().name, ' '.join(cmd)))
    process.returnxmlrpcfunc = callbackName
    process.defer_results = defer_results
    process.endback = cbCommandEnd
    process.max_age = max_exec_time
    process.group = group
    process.kind = kind
    return True

class commandProtocol(twisted.internet.protocol.ProcessProtocol):

    def __init__(self, cmd):
        # command data
        self.cmd = cmd
        self.done = False
        self.isnotifyingparent = False # semaphore to handle possible thread intersections
        self.id = None
        self.group = None
        self.kind = None

        # command process handling
        self.handler = None
        self.status = ""
        self.exit_code = ""
        self.signal = ""
        self.max_age = 0

        # command output
        self.stdout = ""
        self.stderr = ""

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

    def outReceived(self, data):
        self.stdout += data
        self.lastout = data
        timestamp = time.time()
        self.last_see_time = timestamp
        self.last_stdout_time = timestamp

    def errReceived(self, data):
        self.stderr += data
        timestamp = time.time()
        self.last_see_time = timestamp
        self.last_stderr_time = timestamp

    def processEnded(self, reason):
        self.done = True
        # reason.value contain:
        # exitCode
        # signal
        # status
        # error code is <exit status>, or <sig> + PULSE2_WRAPPER_ERROR_SIGNAL_BASE)
        # note: to be posixly-compliant, error code should <sig> + 128,
        # see pulse2/consts.py to know why we do not do this

        self.status = reason.value.status
        self.exit_code = reason.value.exitCode or (reason.value.signal and reason.value.signal + PULSE2_WRAPPER_ERROR_SIGNAL_BASE) or 0 # # no exit code => POSIX compatibility
        self.signal = reason.value.signal or 0  # no signal => force signal to zero

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
        return self.exit_code

    def getStdOut(self):
        return self.stdout

    def getStdErr(self):
        return self.stderr

    def getPID(self):
        return self.handler.pid

    def getTimes(self):
        return {
            'start': self.start_time,
            'last': self.last_see_time,
            'end': self.end_time,
            'now': time.time(),
            'age': self.getAge(),
            'elapsed': self.getElapsedTime()
        }

    def getState(self):
        if self.handler:
            pid = self.handler.pid
        else:
            pid = None
        return {
            'command': self.cmd,
            'id': self.id,
            'group': self.group,
            'kind': self.kind,
            'exit_code': self.exit_code,
            'status': self.status,
            'signal': self.signal,
            'pid': pid,
            'done': self.done,
        }

    def getStatistics(self):
        ret = {}
        ret.update(self.getState())
        ret.update(self.getTimes())
        return ret

    def sendSignal(self, signal):
        # signal is posix signal ID, see kill -l
        logging.getLogger().debug('launcher %s: sent signal %s to command %s' % (LauncherConfig().name, signal, self.id) )
        try:
            self.handler.signalProcess(signal)
            return True
        except:
            logging.getLogger().warn('launcher %s: sent signal %s to command %s which is already finished' % (LauncherConfig().name, signal, self.id) )
            return False

    def sendSigCont(self):
        # signal is posix signal ID
        return self.sendSignal(signal.SIGCONT)

    def sendSigStop(self):
        # signal is posix signal ID
        return self.sendSignal(signal.SIGSTOP)

    def sendSigHup(self):
        # signal is posix signal ID
        return self.sendSignal(signal.SIGHUP)

    def sendSigKill(self):
        # signal is posix signal ID
        return self.sendSignal(signal.SIGKILL)

    def sendSigInt(self):
        # signal is posix signal ID
        return self.sendSignal(signal.SIGINT)

    def sendSigTerm(self):
        # signal is posix signal ID
        return self.sendSignal(signal.SIGTERM)

    def sendSigUsr1(self):
        # signal is posix signal ID
        return self.sendSignal(signal.SIGUSR1)

    def sendSigUsr2(self):
        # signal is posix signal ID
        return self.sendSignal(signal.SIGUSR2)

    def getElapsedTime(self):
        return self.last_see_time - self.start_time

    def getAge(self):
        return time.time() - self.start_time

class ProcessList(Singleton):
    """
        Launcher core: kep a track of launched commands
    """
    _processArr = dict()
    _event = list()
    slots = 0           # max number of commands
    sleepperiod = 60    # amount of second between two wake-up
    default_timeout = 0 # number of second above which we kill a process

    """ Singleton Setup """
    def setup(self, slots, default_timeout):
        self.slots = slots
        self.default_timeout = default_timeout
        self.scheduleWakeUp()

    """ Periodical wake-up stuff """
    def wakeUp(self):
        # do things here
        self.killOldCommands()
        # reschedule
        self.scheduleWakeUp()

    def scheduleWakeUp(self):
        twisted.internet.reactor.callLater(self.sleepperiod, self.wakeUp)

    """ Administrative tasks """
    def killOldCommands(self):
        """ attempt to kill out-of-time commands """
        if self.getRunningCount() > 0:
            for id in self.getRunningIds():
                process = self.getProcess(id)
                times = process.getTimes()
                # priority check order: use process.max_age if not 0, else use self.default_timeout if not 0
                if not process.max_age == 0:
                    if times['age'] > process.max_age: # kill time
                        logging.getLogger().warn('launcher %s: killing %s (out of time: current %s, max %s)' % (LauncherConfig().name, id, times['age'], process.max_age))
                        killProcess(id)
                elif not self.default_timeout == 0:
                    if times['age'] > self.default_timeout: # kill time
                        logging.getLogger().warn('launcher %s: killing %s (out of time: current %s, max %s)' % (LauncherConfig().name, id, times['age'], self.default_timeout))
                        killProcess(id)

    """ Process handling """
    def addProcess(self, obj, id):
        logging.getLogger().info("IBT23SEC5 : Process count : %d" %len(self.listProcesses()))
        if not self.canAddThisProcess(id):
            return False
        self._processArr[id] = obj
        return True

    def canAddThisProcess(self, id):
        if self.existsProcess(id):
            return False
        if not self.isOneSlotFree():
            return False
        return True

    def isOneSlotFree(self):
        return self.getProcessCount() < self.slots

    def getProcess(self, id):
        if self.existsProcess(id):
            return self._processArr[id]
        return None

    def existsProcess(self, id):
        return id in self._processArr.keys()

    def removeProcess(self, id):
        del self._processArr[id]

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
    def isZombie(self, id):
        return self.getProcess(id).done

    def getZombieIds(self):
        ret = []
        for i in self.listProcesses().keys():
            if self.isZombie(i):
                ret.append(i)
        return ret

    def getZombiesCount(self):
        return len(self.getZombieIds())

    """ Running handling """
    def isRunning(self, id):
        return not self.isZombie(id)

    def getRunningIds(self):
        ret = []
        for i in self.listProcesses().keys():
            if self.isRunning(i):
                ret.append(i)
        return ret

    def getRunningCount(self):
        return len(self.getRunningIds())

""" XMLRPC functions """
def getProcessCount():
    return ProcessList().getProcessCount()
def getRunningCount():
    return ProcessList().getRunningCount()
def getZombiesCount():
    return ProcessList().getZombiesCount()

def getProcessIds():
    return ProcessList().getProcessIds()
def getRunningIds():
    return ProcessList().getRunningIds()
def getZombieIds():
    return ProcessList().getZombieIds()

def getProcessStderr(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.getStdErr()
    return None
def getProcessStdout(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.getStdOut()
    return None
def getProcessExitcode(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.getExitCode()
    return None
def getProcessTimes(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.getTimes()
    return None
def getProcessState(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.getState()
    return None
def getProcessStatistics(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.getStatistics()
    return None

def stopProcess(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigStop()
    return False
def contProcess(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigCont()
    return False
def intProcess(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigInt()
    return False
def termProcess(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigTerm()
    return False
def killProcess(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigKill()
    return False
def hupProcess(id):
    process = ProcessList().getProcess(id)
    if process:
        return process.sendSigHup()
    return False

def stopAllProcess():
    for id in ProcessList().getRunningIds():
        stopProcess(id)
    return True
def contAllProcess():
    for id in ProcessList().getRunningIds():
        contProcess(id)
    return True
def intAllProcess():
    for id in ProcessList().getRunningIds():
        intProcess(id)
    return True
def termAllProcess():
    for id in ProcessList().getRunningIds():
        termProcess(id)
    return True
def killAllProcess():
    for id in ProcessList().getRunningIds():
        killProcess(id)
    return True
def hupAllProcess():
    for id in ProcessList().getRunningIds():
        hupProcess(id)
    return True
