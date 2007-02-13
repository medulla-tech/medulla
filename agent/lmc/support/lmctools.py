#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of LMC.
#
# LMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from twisted.internet import defer, reactor
from twisted.internet.utils import _BackRelay
import os
import os.path
import logging
import ConfigParser
import re
from new import instancemethod
from time import time
from lmc.support.lmcException import lmcException

from twisted.internet import protocol

def cleanFilter(f):
    for char in "()&=":
        f = f.replace(char, "")
    return f

# All the command lines launched by this module will use the C locale
os.environ["LANG"] = "C"

def cSort(inlist, minisort=True):
    """
    Case insensitive sort.
    """
    sortlist = []
    newlist = []
    sortdict = {}
    for entry in inlist:
        try:
            lentry = entry.lower()
        except AttributeError:
            sortlist.append(lentry)
        else:
            try:
                sortdict[lentry].append(entry)
            except KeyError:
                sortdict[lentry] = [entry]
                sortlist.append(lentry)

    sortlist.sort()
    for entry in sortlist:
        try:
            thislist = sortdict[entry]
            if minisort: thislist.sort()
            newlist = newlist + thislist
        except KeyError:
            newlist.append(entry)
    return newlist

class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class ProcessScheduler(Singleton):
    """
    Singleton class to schedule command line jobs.
    This class has only one instance.
    """
    _processArr = dict()
    _event = list()

    def addProcess(self,name, obj):
        self._processArr[name] = obj

    def getProcess(self,name):
        return self._processArr[name]

    def listProcess(self):
        return self._processArr

    def rmProcess(self,name):
        del self._processArr[name]

    def addEvent(self,obj):
        self._event.append(obj)

    def popEvent(self):
        self._event.pop()

    def listEvent(self):
        return self._event

class shProcessProtocol(protocol.ProcessProtocol):

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
        self.time = time()

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
        self.time = time() #update time
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
            reactor.iterate()
        return self.exitCode


class shSharedProcessProtocol(shProcessProtocol):

    def __init__(self,cmd):
        shProcessProtocol.__init__(self,cmd)

    def processEnded(self, reason):
        self.done = True
        self.exitCode = reason.value.exitCode
        if self.exitCode == 0:
            self.status = "job successfully finished"
        else:
            self.status = "Error: exited with code " + str(self.exitCode) + "\n" + self.stdall
        self.progress = -1;


class shDebugProcessProtocol(shProcessProtocol):
    def __init(self,cmd):
        shProcessProtocol.__init__(self,cmd)

    def outReceived(self, data):
        print "OUT: "+data
        shProcessProtocol.outReceived(self,data)

    def write(self,data):
        print "IN: "+data
        shProcessProtocol.write(self,data)

    def errReceived(self, data):
        print "ERR: "+data
        shProcessProtocol.errReceived(self,data)



def launch(cmd, param):
    logger = logging.getLogger()
    logger.info("support.lmctools.launch(\""+str(cmd)+","+str(param)+"\")")
    shProcess = shProcessProtocol(cmd)
    logger = logging.getLogger()
    reactor.spawnProcess(shProcess, cmd, param,os.environ)
    while not shProcess.done:
        reactor.iterate()
    if shProcess.exitCode != 0: #if process not finished correctly
        raise Exception('process not finished with exit code 0'+"\n"+shProcess.out)
    return shProcess.out

def shlaunch(cmd):
    """
    return direct (non stderr) output from cmd
    """
    ret = shLaunch(cmd).out.split("\n")
    if ret: ret.pop()
    return ret

def shLaunch(cmd):
    shProcess = shProcessProtocol(cmd)
    reactor.spawnProcess(shProcess, "/bin/sh", ['/bin/sh','-c',cmd],env=os.environ)
    while not shProcess.done:
        reactor.iterate()
    return shProcess

def generateBackgroundProcess(cmd):
    shProcess = shProcessProtocol(cmd)
    reactor.spawnProcess(shProcess, "/bin/sh", ['/bin/sh','-c',cmd],env=os.environ)
    return shProcess


def shlaunchBackground(cmd, desc = None, progressFunc = None):
    """
    follow backup process
    the progressFunc in param can follow processus via stdin and stdout.
    progressFunc is called each time datas are emmited on stdout
    shlaunchBackground drop process after 60 seconds on inactivity
    @param param: cmd command to launch
    @param type: cmd str
    @param param: desc (optionnal) description in "background action"
    @param type: desc str
    @param param: progressFunc callback function to follow processus evolution. @see progressBackup for an example
    @param type: func
    """
    logger = logging.getLogger()
    logger.info("support.lmctools.shlaunchBackground(\""+str(cmd)+"\")")
    shProcess = shSharedProcessProtocol(cmd)
    if desc == None:
        shProcess.desc = cmd
    else:
        shProcess.desc = desc

    ProcessScheduler().addProcess(cmd, shProcess)

    if progressFunc:
        shProcess.progressCalc = instancemethod(progressFunc,shProcess,shSharedProcessProtocol)
    reactor.spawnProcess(shProcess, "/bin/sh", ['/bin/sh','-c',cmd],env=os.environ)


def getConfigParser(module, path = "/etc/lmc/plugins/"):
    """return a configParser for a plugins"""
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(path, module) + ".ini")
    return config

def getConfigFile(module, path = "/etc/lmc/plugins/"):
    """Return the path of the default config file for a plugin"""
    return os.path.join(path, module) + ".ini"

def progressBackup(self, data):
    """
    Specific function to follow backup process.
    this function is use to follow backup process
    it's also an example of callback function for shlaunchBackground
    """
    pattern = "([0-9]{1,2}).[0-9]{1,2}% done, estimate finish"
    try: self.volumeNumber #if first loop
    except:
        self.volumeNumber = 1
        self.currVolume = 1

    sre = re.search("Creation volume ([0-9]+)/([0-9]+)",data)
    try:
        self.volumeNumber = sre.group(2)
        self.currVolume = sre.group(1)
        self.status = "volume "+sre.group(1)+"/"+sre.group(2)
    except:
        pass

    sre = re.search(pattern,data)
    if sre:
        group = sre.group(1)
        if (group):
            self.progress = int(group)/int(self.volumeNumber) + ((int(self.currVolume)-1) *100/int(self.volumeNumber))

