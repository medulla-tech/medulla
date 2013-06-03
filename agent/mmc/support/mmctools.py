# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Tool and utility classes and methods for MMC
"""

from mmc.site import mmcconfdir

from twisted.internet import defer, reactor
import os
import os.path
import shutil
import logging
import ConfigParser
import re
from new import instancemethod
from time import time, struct_time
import datetime
from twisted.internet import protocol
import fcntl
import array
import struct
import socket
import platform

# python 2.3 fallback for set() in xmlrpcleanup
# also try sqlalchemy.util Sets
try:
    from sqlalchemy.util import Set as sa_set
    try:
        set
    except NameError:
        from sets import Set as set
    set_types = set, sa_set
except ImportError:
    try:
        set
    except NameError:
        from sets import Set as set
    set_types = set,

try:
    import mx.DateTime as mxDateTime
except ImportError:
    mxDateTime = None # pyflakes.ignore

def cleanFilter(f):
    for char in "()&=":
        f = f.replace(char, "")
    return f

# All the command lines launched by this module will use the C locale
os.environ["LANG"] = "C"

def cSort(stringList):
    """
    Case-insensitive sort of list of strings

    See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/170242
    """
    tupleList = [(x.lower(), x) for x in stringList]
    tupleList.sort()
    return [x[1] for x in tupleList]

def rchown(path, uid, gid):
    """
    Recursive chown.
    Symbolic links are not followed.

    @param path: path to traverse
    @type path: str

    @param uid: user id number
    @type uid: int

    @param gid: group id number
    @type gid: int
    """
    for root, dirs, files in os.walk(path):
        os.lchown(root, uid, gid)
        for name in files:
            os.lchown(os.path.join(root, name), uid, gid)

def copytree(src, dst, symlinks=False):
    """
    Code taken from Python 2.5

    Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.
    """
    names = os.listdir(src)
    os.makedirs(dst)
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Exception from the recursive copytree so that we can
        # continue with other files
        except Exception, err:
            errors.extend(err.args[0])
    if errors:
        raise Exception, errors

def xmlrpcCleanup(data):
    """
    Cleanup data content so that they can be send using XML-RPC.

    For example, None is not accepted, and must be converted to False.
    """
    if type(data) == dict:
        ret = {}
        for key in data.keys():
            # array keys must be string
            ret[str(key)] = xmlrpcCleanup(data[key])
    elif type(data) == list:
        ret = []
        for item in data:
            ret.append(xmlrpcCleanup(item))
    elif type(data) in set_types:
        ret = []
        for item in data:
            ret.append(xmlrpcCleanup(item))
    elif type(data) == datetime.date:
        ret = tuple(data.timetuple())
    elif type(data) == datetime.datetime:
        ret = tuple(data.timetuple())
    elif mxDateTime and type(data) == mxDateTime.DateTimeType:
        ret = data.tuple()
    elif type(data) == struct_time:
        ret = tuple(data)
    elif data == None:
        ret = False
    elif type(data) == tuple:
        ret = map(lambda x: xmlrpcCleanup(x), data)
    elif type(data) == long:
        ret = str(data)
    else:
        ret = data
    return ret

def localifs():
    """
    Used to get a list of the up interfaces and associated IP addresses
    on this machine (linux only).

    Returns:
        List of interface tuples.  Each tuple consists of
        (interface name, interface IP)
    """

    SIOCGIFCONF = 0x8912
    MAXBYTES = 8096

    arch = platform.architecture()[0]

    if arch == '32bit':
        var1 = 32
        var2 = 32
    elif arch == '64bit':
        var1 = 16
        var2 = 40
    else:
        raise OSError("Unknown architecture: %s" % arch)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', '\0' * MAXBYTES)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        sock.fileno(),
        SIOCGIFCONF,
        struct.pack('iL', MAXBYTES, names.buffer_info()[0])
        ))[0]

    namestr = names.tostring()
    return [(namestr[i:i+var1].split('\0', 1)[0], socket.inet_ntoa(namestr[i+20:i+24])) \
            for i in xrange(0, outbytes, var2)]

class Singleton(object):

    def __new__(type, *args):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class SingletonN(type):

    def __init__(cls, name, bases, dict):
        super(SingletonN, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(SingletonN, cls).__call__(*args, **kw)
        return cls.instance

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
        self.error = ""
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
        self.exitCode = -1

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

class shProcessProtocolNonBlocking(shProcessProtocol):

    def __init__(self, cmd):
        shProcessProtocol.__init__(self, cmd)

    def processEnded(self, status):
        shProcessProtocol.processEnded(self, status)
        self.deferred.callback(self)

    def getExitCode(self):
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
    logger.debug("support.mmctools.launch(\""+str(cmd)+","+str(param)+"\")")
    shProcess = shProcessProtocol(cmd)
    reactor.spawnProcess(shProcess, cmd, param,os.environ)
    while not shProcess.done:
        reactor.iterate()
    if shProcess.exitCode != 0: #if process not finished correctly
        raise Exception('process not finished with exit code 0'+"\n"+shProcess.out)
    return shProcess.out

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

def shlaunch(cmd):
    """
    Run synchronously a shell command

    @param: cmd shell command
    @type: str
    @return: return code, stdout, stderr
    @type: tuple
    """
    shProcess = shLaunch(cmd)
    stdout = []
    stderr = []

    if isinstance(shProcess.out, basestring):
        stdout = shProcess.out.split("\n")
        if len(stdout) > 1: stdout.pop()
    if isinstance(shProcess.error, basestring):
        stderr = shProcess.error.split("\n")
        if len(stderr) > 1: stderr.pop()

    return (shProcess.exitCode, stdout, stderr)

def shlaunchBackground(cmd, desc = None, progressFunc = None, endFunc = None):
    """
    Follow backup process

    The progressFunc in param can follow processus via stdin and stdout.
        - progressFunc is called each time datas are emmited on stdout
        - shlaunchBackground drop process after 60 seconds on inactivity

    @param cmd: the shell command to launch
    @type cmd: str
    @param desc: description in "background action" (optional)
    @type desc: str
    @param progressFunc: callback function to follow processus evolution.
        @see: progressBackup for an example
    @type progressFunc: function
    """
    logger = logging.getLogger()
    logger.info("support.mmctools.shlaunchBackground(\""+str(cmd)+"\")")
    shProcess = shSharedProcessProtocol(cmd)
    if desc == None:
        shProcess.desc = cmd
    else:
        shProcess.desc = desc

    ProcessScheduler().addProcess(shProcess.desc, shProcess)

    if progressFunc:
        shProcess.progressCalc = instancemethod(progressFunc, shProcess, shSharedProcessProtocol)

    if endFunc:
        shProcess.processEnded = instancemethod(endFunc, shProcess, shSharedProcessProtocol)
    reactor.spawnProcess(shProcess, "/bin/sh", ['/bin/sh','-c',cmd],env=os.environ)


def shLaunchDeferred(cmd):
    """
    Return a deferred resulting to a shProcessProtocolNonBlocking instance
    """
    shProcess = shProcessProtocolNonBlocking(cmd)
    shProcess.deferred = defer.Deferred()
    reactor.spawnProcess(shProcess, "/bin/sh", ['/bin/sh','-c',cmd],env=os.environ)
    return shProcess.deferred

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



def getConfigParser(module, path = mmcconfdir + "/plugins/"):
    """return a configParser for a plugins"""
    config = ConfigParser.ConfigParser()
    inifile = os.path.join(path, module) + ".ini"
    fp = file(inifile, "r")
    config.readfp(fp, inifile)
    return config

def getConfigFile(module, path = mmcconfdir + "/plugins/"):
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

def size_format(b):
    if b < 1000:
        return '%i' % b + 'B'
    elif 1000 <= b < 1000000:
        return '%.1f' % float(b/1000.0) + 'KB'
    elif 1000000 <= b < 1000000000:
        return '%.1f' % float(b/1000000.0) + 'MB'
    elif 1000000000 <= b < 1000000000000:
        return '%.1f' % float(b/1000000000.0) + 'GB'
    elif 1000000000000 <= b:
        return '%.1f' % float(b/1000000000000.0) + 'TB'

class ServiceManager:
    """
    Class to know a service state, and start/stop/reload it
    """

    def __init__(self, pidfile, initfile):
        self.pidfile = pidfile
        self.initfile = initfile

    def isRunning(self):
        ret = False
        if os.path.exists(self.pidfile):
            f = open(self.pidfile)
            pid = f.read()
            f.close()
            ret = os.path.isdir(os.path.join("/proc", pid.strip()))
        return ret

    def start(self):
        shLaunch(self.initfile + " start")

    def stop(self):
        shLaunch(self.initfile + " stop")

    def restart(self):
        shLaunch(self.initfile + " restart")

    def reload(self):
        shLaunch(self.initfile + " reload")

    def command(self, command):
        ret = None
        if command == "status":
            ret = self.isRunning()
        elif command == "start":
            self.start()
        elif command == "stop":
            self.stop()
        elif command == "restart":
            self.restart()
        elif command == "reload":
            self.reload()
        return ret


class RpcProxyI:
    """
    This class allows to associate a request and a session object to a set of
    methods.
    This is useful to change methods behaviour according to the session content
    (which user is logged, etc.)

    @ivar request: the request associated to the XML-RPC call
    @ivar session: the session associated to the XML-RPC call
    @ivar userid: the user id (login) associated to the XML-RPC call
    @ivar currentContext: the current module security context
    """
    def __init__(self, request, mod):
        self.request = request
        self.session = request.getSession()
        try:
            self.userid = self.session.userid
        except AttributeError:
            # The user ID may not be set if the user is being authenticated
            self.userid = None
        try:
            self.currentContext = self.session.contexts[mod]
        except (KeyError, AttributeError):
            self.currentContext = None

    def getFunction(self, funcname):
        return getattr(self, funcname)

class ContextMakerI:
    """
    This class should be used to build a context to attach to a session.

    @ivar request: the request associated to the XML-RPC call
    @ivar session: the session associated to the XML-RPC call
    @ivar userid: the user id (login) associated to the XML-RPC call
    """

    def __init__(self, request, session, userid):
        self.request = request
        self.session = session
        self.userid = userid

    def getContext(self):
        """
        Must return a SecurityContext object according to the request, the
        session and the userid.

        If no context should be returned, just return None

        @return: a SecurityContext object, or None
        """
        raise "Must be implemented by the subclass"


class ContextProviderI:
    """
    Class for object that owns a security context
    """

    def __init__(self):
        self.context = None

    def setContext(self, context):
        """
        Set the current context
        """
        self.context = context

class SecurityContext:
    """
    Class for object that contains a security context.

    Basically, it can be seen as a simple structure where attributes can be get
    and set.
    """
    pass
