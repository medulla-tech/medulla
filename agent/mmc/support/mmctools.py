# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Tool and utility classes and methods for MMC
"""

from mmc.site import mmcconfdir

from twisted.internet import defer, reactor
import os
import os.path
import shutil
import logging
import configparser
import re
from types import MethodType
from time import time, struct_time
import datetime
from twisted.internet import protocol
import fcntl
import array
import struct
import socket
import platform
import inspect

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
    set_types = (set,)

try:
    import mx.DateTime as mxDateTime
except ImportError:
    mxDateTime = None  # pyflakes.ignore


def cleanFilter(f):
    for char in "()&=":
        f = f.replace(char, "")
    if not f.startswith("*"):
        f = f"*{f}"
    if not f.endswith("*"):
        f = f"{f}*"
    return f


# All the command lines launched by this module will use the C locale
os.environ["LANG"] = "C"


def cSort(stringList):
    """
    Case-insensitive sort of list of strings

    See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/170242
    """
    tupleList = sorted([(x.lower(), x) for x in stringList])
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
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Exception from the recursive copytree so that we can
        # continue with other files
        except Exception as err:
            errors.extend(err.args[0])
    if errors:
        raise Exception(errors)


def xmlrpcCleanup(data):
    """
    Cleanup data content so that they can be send using XML-RPC.

    For example, None is not accepted, and must be converted to False.
    """
    if isinstance(data, dict):
        return {str(key): xmlrpcCleanup(data[key]) for key in list(data.keys())}
    elif isinstance(data, list):
        return [xmlrpcCleanup(item) for item in data]
    elif type(data) in set_types:
        return [xmlrpcCleanup(item) for item in data]
    elif isinstance(data, datetime.date):
        return tuple(data.timetuple())
    elif isinstance(data, datetime.datetime):
        return tuple(data.timetuple())
    elif mxDateTime and isinstance(data, mxDateTime.DateTimeType):
        return data.tuple()
    elif isinstance(data, struct_time):
        return tuple(data)
    elif data is None:
        return False
    elif isinstance(data, tuple):
        return [xmlrpcCleanup(x) for x in data]
    elif isinstance(data, bool):
        return bool(data)
    elif isinstance(data, int):
        return str(data)
    else:
        return data


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

    if arch == "32bit":
        var1 = 32
        var2 = 32
    elif arch == "64bit":
        var1 = 16
        var2 = 40
    else:
        raise OSError(f"Unknown architecture: {arch}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array("B", "\0" * MAXBYTES)
    outbytes = struct.unpack(
        "iL",
        fcntl.ioctl(
            sock.fileno(),
            SIOCGIFCONF,
            struct.pack("iL", MAXBYTES, names.buffer_info()[0]),
        ),
    )[0]

    namestr = names.tostring()
    return [
        (
            namestr[i : i + var1].split("\0", 1)[0],
            socket.inet_ntoa(namestr[i + 20 : i + 24]),
        )
        for i in range(0, outbytes, var2)
    ]


class Singleton(object):
    """
    Une classe Singleton utilisant la méthode `__new__` pour garantir qu'une seule instance
    de la classe est créée.

    Cette implémentation utilise une variable de classe `_the_instance` pour stocker
    l'instance unique de la classe. Chaque appel à la création d'une nouvelle instance
    retourne cette instance unique.

    Attributes:
        _the_instance: L'instance unique de la classe.
    """

    def __new__(cls, *args):
        """
        Crée une nouvelle instance de la classe si elle n'existe pas déjà.

        Args:
            *args: Arguments passés au constructeur de la classe.

        Returns:
            Singleton: L'instance unique de la classe.
        """
        if "_the_instance" not in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


class SingletonN(type):
    """
    Une métaclasse Singleton pour garantir qu'une seule instance de toute classe
    utilisant cette métaclasse est créée.

    Cette métaclasse surcharge la méthode `__call__` pour s'assurer qu'une seule instance
    de la classe est créée et retournée à chaque appel.

    Attributes:
        instance: L'instance unique de la classe utilisant cette métaclasse.
    """

    def __init__(self, name, bases, dict):
        """
        Initialise la métaclasse Singleton.

        Args:
            name (str): Nom de la classe.
            bases (tuple): Classes de base de la classe.
            dict (dict): Espace de noms de la classe.
        """
        super(SingletonN, self).__init__(name, bases, dict)
        self.instance = None

    def __call__(self, *args, **kw):
        """
        Crée une nouvelle instance de la classe si elle n'existe pas déjà.

        Args:
            *args: Arguments positionnels passés au constructeur de la classe.
            **kw: Arguments nommés passés au constructeur de la classe.

        Returns:
            object: L'instance unique de la classe.
        """
        if self.instance is None:
            self.instance = super(SingletonN, self).__call__(*args, **kw)
        return self.instance



class ProcessScheduler(Singleton):
    """
    Singleton class to schedule command line jobs.
    This class has only one instance.
    """

    _processArr = dict()
    _event = list()

    def addProcess(self, name, obj):
        self._processArr[name] = obj

    def getProcess(self, name):
        return self._processArr[name]

    def listProcess(self):
        return self._processArr

    def rmProcess(self, name):
        del self._processArr[name]

    def addEvent(self, obj):
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
        # last output
        self.lastout = ""
        self.err = ""
        # progress
        self.progress = -1
        # description
        self.desc = cmd
        # time
        self.time = time()
        self.exitCode = -1

    def write(self, data):
        self.transport.write(data)
        self.stdall = f"{self.stdall}<<{data}"

    def progressCalc(self, data):
        """
        Try to find a percentage of progression on command output, and put this
        into self.progress and self.status.
        """
        if sre := re.search("([0-9]){1,2}", data):
            if group := sre.group():
                self.progress = group
                self.status = data

    def outReceived(self, data):
        self.out = self.out + data
        self.stdall = f"{self.stdall}>>{data}"
        self.lastout = data
        self.time = time()  # update time
        self.progressCalc(data)

    def errReceived(self, data):
        self.err = self.err + data
        self.stdall = f"{self.stdall}>>{data}"
        self.error = True

    def processEnded(self, reason):
        self.exitCode = reason.value.exitCode
        self.progress = -1
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
    def __init__(self, cmd):
        shProcessProtocol.__init__(self, cmd)

    def processEnded(self, reason):
        self.done = True
        self.exitCode = reason.value.exitCode
        if self.exitCode == 0:
            self.status = "job successfully finished"
        else:
            self.status = (
                f"Error: exited with code {str(self.exitCode)}" + "\n" + self.stdall
            )
        self.progress = -1


class shDebugProcessProtocol(shProcessProtocol):
    def __init(self, cmd):
        shProcessProtocol.__init__(self, cmd)

    def outReceived(self, data):
        print(f"OUT: {data}")
        shProcessProtocol.outReceived(self, data)

    def write(self, data):
        print(f"IN: {data}")
        shProcessProtocol.write(self, data)

    def errReceived(self, data):
        print(f"ERR: {data}")
        shProcessProtocol.errReceived(self, data)


def launch(cmd, param):
    logger = logging.getLogger()
    logger.debug(f'support.mmctools.launch("{str(cmd)},{str(param)}")')
    shProcess = shProcessProtocol(cmd)
    reactor.spawnProcess(shProcess, cmd, param, os.environ)
    while not shProcess.done:
        reactor.iterate()
    if shProcess.exitCode != 0:  # if process not finished correctly
        raise Exception("process not finished with exit code 0" + "\n" + shProcess.out)
    return shProcess.out


def shlaunchDeferred(cmd):
    """
    Return a Deferred resulting in the stdout output of a shell command.
    """

    def cb(shprocess):
        ret = shprocess.out.split("\n")
        if ret:
            ret.pop()
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

    if isinstance(shProcess.out, str):
        stdout = shProcess.out.split("\n")
        if len(stdout) > 1:
            stdout.pop()
    if isinstance(shProcess.error, str):
        stderr = shProcess.error.split("\n")
        if len(stderr) > 1:
            stderr.pop()

    return (shProcess.exitCode, stdout, stderr)


def shlaunchBackground(cmd, desc=None, progressFunc=None, endFunc=None):
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
    logger.info(f'support.mmctools.shlaunchBackground("{str(cmd)}")')
    shProcess = shSharedProcessProtocol(cmd)
    shProcess.desc = cmd if desc is None else desc
    ProcessScheduler().addProcess(shProcess.desc, shProcess)

    if progressFunc:
        shProcess.progressCalc = MethodType(
            progressFunc, shProcess, shSharedProcessProtocol
        )

    if endFunc:
        shProcess.processEnded = MethodType(endFunc, shProcess, shSharedProcessProtocol)

    reactor.spawnProcess(shProcess, "/bin/sh", ["/bin/sh", "-c", cmd], env=os.environ)


def shLaunchDeferred(cmd):
    """
    Return a deferred resulting to a shProcessProtocolNonBlocking instance
    """
    shProcess = shProcessProtocolNonBlocking(cmd)
    shProcess.deferred = defer.Deferred()
    reactor.spawnProcess(shProcess, "/bin/sh", ["/bin/sh", "-c", cmd], env=os.environ)
    return shProcess.deferred


def shLaunch(cmd):
    shProcess = shProcessProtocol(cmd)
    reactor.spawnProcess(shProcess, "/bin/sh", ["/bin/sh", "-c", cmd], env=os.environ)
    while not shProcess.done:
        reactor.iterate()
    return shProcess


def generateBackgroundProcess(cmd):
    shProcess = shProcessProtocol(cmd)
    reactor.spawnProcess(shProcess, "/bin/sh", ["/bin/sh", "-c", cmd], env=os.environ)
    return shProcess


def getConfigParser(module, path=f"{mmcconfdir}/plugins/"):
    """return a configParser for a plugins"""
    config = configparser.ConfigParser()
    inifile = f"{os.path.join(path, module)}.ini"
    with open(inifile, "r") as filepointer:
        config.readfp(filepointer, inifile)
        filepointer.close()
    if os.path.isfile(f"{inifile}.local"):
        config.readfp(open(f"{inifile}.local", "r"))
    return config


def getConfigFile(module, path=f"{mmcconfdir}/plugins/"):
    """Return the path of the default config file for a plugin"""
    return f"{os.path.join(path, module)}.ini"


def progressBackup(self, data):
    """
    Specific function to follow backup process.
    this function is use to follow backup process
    it's also an example of callback function for shlaunchBackground
    """
    pattern = "([0-9]{1,2}).[0-9]{1,2}% done, estimate finish"
    try:
        self.volumeNumber  # if first loop
    except:
        self.volumeNumber = 1
        self.currVolume = 1

    sre = re.search("Creation volume ([0-9]+)/([0-9]+)", data)
    try:
        self.volumeNumber = sre[2]
        self.currVolume = sre[1]
        self.status = f"volume {sre[1]}/{sre[2]}"
    except:
        pass

    if sre := re.search(pattern, data):
        if group := sre[1]:
            self.progress = int(group) / int(self.volumeNumber) + (
                (int(self.currVolume) - 1) * 100 / int(self.volumeNumber)
            )


def size_format(b):
    if b < 1000:
        return "%i" % b + "B"
    elif 1000 <= b < 1000000:
        return "%.1f" % float(b / 1000.0) + "KB"
    elif 1000000 <= b < 1000000000:
        return "%.1f" % float(b / 1000000.0) + "MB"
    elif 1000000000 <= b < 1000000000000:
        return "%.1f" % float(b / 1000000000.0) + "GB"
    else:
        return "%.1f" % float(b / 1000000000000.0) + "TB"


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
            with open(self.pidfile) as f:
                pid = f.read()
            ret = os.path.isdir(os.path.join("/proc", pid.strip()))
        return ret

    def start(self):
        shLaunch(f"{self.initfile} start")

    def stop(self):
        shLaunch(f"{self.initfile} stop")

    def restart(self):
        shLaunch(f"{self.initfile} restart")

    def reload(self):
        shLaunch(f"{self.initfile} reload")

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



class EnhancedSecurityContext:
    """
    Une classe améliorée pour gérer le contexte de sécurité, incluant les informations
    de session, de requête et un dictionnaire personnalisé pour stocker des données supplémentaires.

    Cette classe encapsule les accès aux attributs de session et de requête,
    et fournit des méthodes pour manipuler ces informations de manière sécurisée.

    Attributes:
        _userid (str): Nom d'utilisateur connecté.
        _request (twisted.web.server.Request): Objet de requête HTTP.
        _session (twisted.web.server.Session): Objet de session Twisted.
        _mondict (dict): Dictionnaire pour stocker des données supplémentaires.
    """

    def __init__(self, userid=None, request=None, session=None):
        """
        Initialise une nouvelle instance de EnhancedSecurityContext.

        Args:
            userid (str, optional): Nom d'utilisateur connecté. Defaults to None.
            request (twisted.web.server.Request, optional): Objet de requête HTTP. Defaults to None.
            session (twisted.web.server.Session, optional): Objet de session Twisted. Defaults to None.
        """
        self._userid = userid
        self._request = request
        self._session = session
        self._mondict = {}  # Dictionnaire pour stocker des données supplémentaires

    @property
    def userid(self):
        """
        Retourne le nom d'utilisateur connecté.

        Returns:
            str: Nom d'utilisateur.
        """
        return self._userid

    @userid.setter
    def userid(self, value):
        """
        Définit le nom d'utilisateur connecté.

        Args:
            value (str): Nom d'utilisateur.
        """
        self._userid = value

    @property
    def request(self):
        """
        Retourne l'objet de requête HTTP.

        Returns:
            twisted.web.server.Request: Objet de requête HTTP.
        """
        return self._request

    @request.setter
    def request(self, value):
        """
        Définit l'objet de requête HTTP.

        Args:
            value (twisted.web.server.Request): Objet de requête HTTP.
        """
        self._request = value

    def get_request_headers(self):
        """
        Retourne les headers de la requête sous forme de dictionnaire.

        Returns:
            dict: Dictionnaire des headers de la requête.
        """
        if self._request is not None:
            headers = {}
            for key, values in self._request.getAllHeaders().items():
                headers[key] = values[0] if isinstance(values, list) else values
            return headers
        return {}

    def get_request_header(self, header_name):
        """
        Retourne la valeur d'un header spécifique de la requête.

        Args:
            header_name (str): Nom du header.

        Returns:
            str: Valeur du header, ou None si le header n'existe pas.
        """
        if self._request is not None:
            return self._request.getHeader(header_name)
        return None

    def get_client_ip(self):
        """
        Retourne l'adresse IP du client.

        Returns:
            str: Adresse IP du client, ou None si non disponible.
        """
        if self._request is not None:
            return self._request.getClientIP()
        return None

    @property
    def session(self):
        """
        Retourne l'objet de session Twisted.

        Returns:
            twisted.web.server.Session: Objet de session Twisted.
        """
        return self._session

    @session.setter
    def session(self, value):
        """
        Définit l'objet de session Twisted.

        Args:
            value (twisted.web.server.Session): Objet de session Twisted.
        """
        self._session = value

    def get_session_id(self):
        """
        Retourne l'ID de la session.

        Returns:
            str: ID de la session, ou None si non disponible.
        """
        if self._session is not None:
            return getattr(self._session, 'uid', None)
        return None

    def get_session_expires(self):
        """
        Retourne la date d'expiration de la session.

        Returns:
            int: Timestamp de la date d'expiration, ou None si non disponible.
        """
        if self._session is not None:
            return getattr(self._session, 'expires', None)
        return None

    def get_session_last_modified(self):
        """
        Retourne la dernière activité de la session.

        Returns:
            int: Timestamp de la dernière activité, ou None si non disponible.
        """
        if self._session is not None:
            return getattr(self._session, 'lastModified', None)
        return None

    def get_session_timeout(self):
        """
        Retourne le délai d'expiration de la session.

        Returns:
            int: Délai d'expiration en secondes, ou None si non disponible.
        """
        if self._session is not None:
            return getattr(self._session, 'sessionTimeout', None)
        return None

    def is_logged_in(self):
        """
        Indique si l'utilisateur est connecté.

        Returns:
            bool: True si l'utilisateur est connecté, False sinon.
        """
        if self._session is not None:
            return getattr(self._session, 'loggedin', False)
        return False

    def get_session_userid(self):
        """
        Retourne le nom d'utilisateur connecté depuis la session.

        Returns:
            str: Nom d'utilisateur, ou None si non disponible.
        """
        if self._session is not None:
            return getattr(self._session, 'userid', None)
        return None

    def get_session_http_headers(self):
        """
        Retourne les en-têtes HTTP de la requête initiale.

        Returns:
            dict: Dictionnaire des en-têtes HTTP, ou un dictionnaire vide si non disponible.
        """
        if self._session is not None:
            return getattr(self._session, 'http_headers', {})
        return {}

    def get_session_contexts(self):
        """
        Retourne le contexte spécifique aux modules.

        Returns:
            dict: Dictionnaire des contextes spécifiques aux modules, ou un dictionnaire vide si non disponible.
        """
        if self._session is not None:
            return getattr(self._session, 'contexts', {})
        return {}

    def set_session_attribute(self, attr_name, value):
        """
        Définit un attribut spécifique de la session.

        Args:
            attr_name (str): Nom de l'attribut.
            value: Valeur de l'attribut.
        """
        if self._session is not None:
            setattr(self._session, attr_name, value)

    def get_mondict(self, key=None):
        """
        Retourne une valeur ou tout le dictionnaire mondict.

        Args:
            key (str, optional): Clé pour récupérer une valeur spécifique. Defaults to None.

        Returns:
            dict ou any: Si key est spécifié, retourne la valeur associée.
                         Sinon, retourne le dictionnaire mondict complet.
        """
        if key is not None:
            return self._mondict.get(key)
        return self._mondict

    def set_mondict(self, key, value):
        """
        Définit une valeur dans mondict.

        Args:
            key (str): Clé pour stocker la valeur.
            value (any): Valeur à stocker.
        """
        self._mondict[key] = value

    def update_mondict(self, new_dict):
        """
        Met à jour mondict avec un nouveau dictionnaire.

        Args:
            new_dict (dict): Dictionnaire de clés/valeurs à ajouter ou mettre à jour.
        """
        self._mondict.update(new_dict)

    def clear_mondict(self):
        """
        Efface mondict.
        """
        self._mondict.clear()

    def get_session_info(self):
        """
        Retourne un dictionnaire avec toutes les informations de la session.

        Returns:
            dict: Dictionnaire contenant toutes les informations de la session.
        """
        if self._session is None:
            return {}

        session_info = {
            'uuid': self.get_session_id(),
            'expires': self.get_session_expires(),
            'lastModified': self.get_session_last_modified(),
            'sessionTimeout': self.get_session_timeout(),
            'loggedin': self.is_logged_in(),
            'userid': self.get_session_userid(),
            'http_headers': self.get_session_http_headers(),
            'contexts': self.get_session_contexts(),
            'mondict': self._mondict,
        }
        return session_info


    def _update_filter(filter_dict, allowed_entities):
        """
        Met à jour le filtre 'location' pour ne contenir que les UUID correspondant
        aux entités autorisées.

        Exemple :
            allowed_entities = [1,2]

            {'location': 'UUID3'}  -> {'location': 'UUID1,UUID2'}
            {'location': ''}       -> {'location': 'UUID1,UUID2'}
            {}                     -> {'location': 'UUID1,UUID2'}
            {'location': 'UUID3,UUID1'} -> {'location': 'UUID1'}

        Args:
            filter_dict (dict): dictionnaire du filtre.
            allowed_entities (list[int]): liste d'entiers représentant les entités autorisées.

        Returns:
            dict: dictionnaire avec 'location' corrigé en fonction des droits utilisateur.
        """

        # Chaîne par défaut = toutes les entités permises
        default_location = ",".join(f"UUID{e}" for e in allowed_entities)

        # Cas 1 & 2 : pas de location ou location vide
        if 'location' not in filter_dict or not filter_dict['location']:
            filter_dict['location'] = default_location
            return filter_dict

        # Cas 3 : filtrer les UUID existants selon allowed_entities
        uuids = [u.strip() for u in filter_dict['location'].split(",") if u.strip()]
        valid_uuids = []

        for u in uuids:
            if u.startswith("UUID"):
                try:
                    idx = int(u[4:])  # récupérer l'index après "UUID"
                    if idx in allowed_entities:
                        valid_uuids.append(u)
                except ValueError:
                    continue

        # si rien n'est valide → on applique la valeur par défaut
        if valid_uuids:
            filter_dict['location'] = ",".join(valid_uuids)
        else:
            filter_dict['location'] = default_location

        return filter_dict
