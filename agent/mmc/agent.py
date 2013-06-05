# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
XML-RPC server implementation of the MMC agent.
"""
from resource import RLIMIT_NOFILE, RLIM_INFINITY, getrlimit
import signal
import multiprocessing as mp

import twisted.internet.error
import twisted.copyright
from twisted.web import xmlrpc, server
from twisted.internet import reactor, defer
from twisted.python import failure
try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http  # pyflakes.ignore

from mmc.site import localstatedir
from mmc.ssl import makeSSLContext
from mmc.support.mmctools import Singleton
from mmc.core.version import scmRevision
from mmc.core.audit import AuditFactory
from mmc.core.log import ColoredFormatter

import imp
import logging
import logging.config
import xmlrpclib
import os
import sys
import ConfigParser
import glob
import time
import pwd
import grp
import string
import threading

logger = logging.getLogger()

sys.path.append("plugins")

Fault = xmlrpclib.Fault
ctx = None
VERSION = "3.1.0"


class MmcServer(xmlrpc.XMLRPC, object):
    """
    MMC Server implemented as a XML-RPC server.

    config file : @sysconfdir@/agent/config.ini

    Create a twisted XMLRPC server, load plugins in
    "plugins/" directory
    """

    def __init__(self, modules, config):
        xmlrpc.XMLRPC.__init__(self)
        self.modules = modules
        self.config = config

    def _splitFunctionPath(self, functionPath):
        if '.' in functionPath:
            mod, func = functionPath.split('.', 1)
        else:
            mod = None
            func = functionPath
        return mod, func

    def _getFunction(self, functionPath, request):
        """Overrided to use functions from our plugins"""
        mod, func = self._splitFunctionPath(functionPath)
        try:
            if mod:
                try:
                    ret = getattr(self.modules[mod], func)
                except AttributeError:
                    rpcProxy = getattr(self.modules[mod], "RpcProxy")
                    ret = rpcProxy(request, mod).getFunction(func)
            else:
                ret = getattr(self, func)
        except AttributeError:
            logger.error(functionPath + ' not found')
            raise Fault("NO_SUCH_FUNCTION", "No such function " + functionPath)
        return ret

    def _needAuth(self, functionPath):
        """
        @returns: True if the specified function requires a user authentication
        @rtype: boolean
        """
        mod, func = self._splitFunctionPath(functionPath)
        ret = True
        if mod:
            try:
                nanl = self.modules[mod].NOAUTHNEEDED
                ret = func not in nanl
            except (KeyError, AttributeError):
                pass
        return ret

    def render(self, request):
        """
        override method of xmlrpc python twisted framework

        @param request: raw request xmlrpc
        @type request: xml str

        @return: interpreted request
        """
        args, functionPath = xmlrpclib.loads(request.content.read())

        s = request.getSession()
        try:
            s.loggedin
        except AttributeError:
            s.loggedin = False
            # Set session expire timeout
            s.sessionTimeout = self.config.sessiontimeout

        # Check authorization using HTTP Basic
        cleartext_token = self.config.login + ":" + self.config.password
        token = request.getUser() + ":" + request.getPassword()
        if token != cleartext_token:
            logger.error("Invalid login / password for HTTP basic authentication")
            request.setResponseCode(http.UNAUTHORIZED)
            self._cbRender(
                xmlrpc.Fault(http.UNAUTHORIZED, "Unauthorized: invalid credentials to connect to the MMC agent, basic HTTP authentication is required"),
                request
            )
            return server.NOT_DONE_YET

        if not s.loggedin:
            logger.debug("RPC method call from unauthenticated user: %s" % functionPath + str(args))
            # Save the first sent HTTP headers, as they contain some
            # informations
            s.http_headers = request.received_headers.copy()
        else:
            logger.debug("RPC method call from user %s: %s" % (s.userid, functionPath + str(args)))
        try:
            if not s.loggedin and self._needAuth(functionPath):
                msg = "Authentication needed: %s" % functionPath
                logger.error(msg)
                raise Fault(8003, msg)
            else:
                if not s.loggedin and not self._needAuth(functionPath):
                    # Provide a security context when a method which doesn't
                    # require a user authentication is called
                    s = request.getSession()
                    s.userid = 'root'
                    try:
                        self._associateContext(request, s, s.userid)
                    except Exception, e:
                        s.loggedin = False
                        logger.exception(e)
                        f = Fault(8004, "MMC agent can't provide a security context")
                        self._cbRender(f, request)
                        return server.NOT_DONE_YET
                function = self._getFunction(functionPath, request)
        except Fault, f:
            self._cbRender(f, request)
        else:
            request.setHeader("content-type", "text/xml")
            if self.config.multithreading:
                oldargs = args
                args = (function, s,) + args
                defer.maybeDeferred(self._runInThread, *args).addErrback(
                    self._ebRender, functionPath, oldargs, request
                ).addCallback(
                    self._cbRender, request, functionPath, oldargs
                )
            else:
                defer.maybeDeferred(function, *args).addErrback(
                    self._ebRender, functionPath, args, request
                ).addCallback(
                    self._cbRender, request, functionPath, args
                )
        return server.NOT_DONE_YET

    def _runInThread(self, *args, **kwargs):
        """
        Very similar to deferToThread, but also handles function that results
        to a Deferred object.
        """
        def _printExecutionTime(start):
            logger.debug("Execution time: %f" % (time.time() - start))

        def _cbSuccess(result, deferred, start):
            _printExecutionTime(start)
            reactor.callFromThread(deferred.callback, result)

        def _cbFailure(failure, deferred, start):
            _printExecutionTime(start)
            reactor.callFromThread(deferred.errback, failure)

        def _putResult(deferred, f, session, args, kwargs):
            logger.debug("Using thread #%s for %s" % (threading.currentThread().getName().split("-")[2], f.__name__))
            # Attach current user session to the thread
            threading.currentThread().session = session
            start = time.time()
            try:
                result = f(*args, **kwargs)
            except:
                f = failure.Failure()
                reactor.callFromThread(deferred.errback, f)
            else:
                if isinstance(result, defer.Deferred):
                    # If the result is a Deferred object, attach callback and
                    # errback (we are not allowed to result to a Deferred)
                    result.addCallback(_cbSuccess, deferred, start)
                    result.addErrback(_cbFailure, deferred, start)
                else:
                    _printExecutionTime(start)
                    reactor.callFromThread(deferred.callback, result)

        function = args[0]
        context = args[1]
        args = args[2:]
        d = defer.Deferred()
        reactor.callInThread(_putResult, d, function, context, args, kwargs)
        return d

    def _cbRender(self, result, request, functionPath=None, args=None):
        s = request.getSession()
        auth_funcs = ["base.ldapAuth", "base.tokenAuthenticate", "base.authenticate"]
        if functionPath in auth_funcs and not isinstance(result, Fault):
            # if we are logging on and there was no error
            if result:
                s = request.getSession()
                s.loggedin = True
                s.userid = args[0]
                try:
                    self._associateContext(request, s, s.userid)
                except Exception, e:
                    s.loggedin = False
                    logger.exception(e)
                    f = Fault(8004, "MMC agent can't provide a security context for this account")
                    self._cbRender(f, request)
                    return
        if result is None:
            result = 0
        if isinstance(result, xmlrpc.Handler):
            result = result.result
        if not isinstance(result, Fault):
            result = (result,)
        try:
            if type(result[0]) == dict:
                # FIXME
                # Evil hack ! We need this to transport some data as binary instead of string
                if "jpegPhoto" in result[0]:
                    result[0]["jpegPhoto"] = [xmlrpclib.Binary(result[0]["jpegPhoto"][0])]
        except IndexError:
            pass
        try:
            if s.loggedin:
                logger.debug('Result for ' + s.userid + ", " + str(functionPath) + ": " + str(result))
            else:
                logger.debug('Result for unauthenticated user, ' + str(functionPath) + ": " + str(result))
            s = xmlrpclib.dumps(result, methodresponse=1)
        except Exception, e:
            f = Fault(self.FAILURE, "can't serialize output: " + str(e))
            s = xmlrpclib.dumps(f, methodresponse=1)
        request.setHeader("content-length", str(len(s)))
        request.write(s)
        request.finish()

    def _ebRender(self, failure, functionPath, args, request):
        logger.error("Error during render " + functionPath + ": " + failure.getTraceback())
        # Prepare a Fault result to return
        result = {}
        result['faultString'] = functionPath + " " + str(args)
        result['faultCode'] = str(failure.type) + ": " + str(failure.value) + " "
        result['faultTraceback'] = failure.getTraceback()
        return result

    def _associateContext(self, request, session, userid):
        """
        Ask to each activated Python plugin a context to attach to the user
        session.

        @param request: the current XML-RPC request
        @param session: the current session object
        @param userid: the user login
        """
        session.contexts = {}
        for mod in self.modules:
            try:
                contextMaker = getattr(self.modules[mod], "ContextMaker")
            except AttributeError:
                # No context provided
                continue
            cm = contextMaker(request, session, userid)
            context = cm.getContext()
            if context:
                logger.debug("Attaching module '%s' context to user session" % mod)
                session.contexts[mod] = context

    def getRevision(self):
        return scmRevision("$Rev$")

    def getVersion(self):
        return VERSION

    def log(self, fileprefix, content):
        """
        @param fileprefix: Write log file in @localstatedir@/log/mmc/mmc-fileprefix.log
        @param content: string to record in log file
        """
        f = open(localstatedir + '/log/mmc/mmc-' + fileprefix + '.log', 'a')
        f.write(time.asctime() + ': ' + content + "\n")
        f.close()


class MMCApp(object):
    """ Represent the MMCApp
    """
    def __init__(self, config, options):
        self.config = readConfig(config)
        self.conffile = options.inifile
        self.daemon = options.daemonize

        # Shared return state, so that father can know if children goes wrong
        if self.daemon:
            self._shared_state = mp.Value('i', 0)

        if self.daemon:
            self.lock = mp.Lock()

    def getState(self):
        if self.daemon:
            return self._shared_state.value

    def setState(self, s):
        if self.daemon:
            self._shared_state.value = s
    state = property(getState, setState)

    def daemonize(self):
        # Test if mmcagent has been already launched in daemon mode
        if os.path.isfile(self.config.pidfile):
            print  "%s already exist. Maybe mmc-agent is already running\n" % self.config.pidfile
            sys.exit(0)

        # do the UNIX double-fork magic, see Stevens' "Advanced
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        try:
            pid = os.fork()
            if pid > 0:
                # Wait for initialization before exiting
                self.lock.acquire()
                # exit first parent and return
                sys.exit(self.state)
        except OSError, e:
            print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            self.state = 1
            self.lock.release()
            sys.exit(1)

        maxfd = getrlimit(RLIMIT_NOFILE)[1]
        if maxfd == RLIM_INFINITY:
            maxfd = 1024

        for fd in range(0, maxfd):
            # Don't close twisted FDs
            # TODO: make a clean code to be sure nothing is opened before this function
            # ie: daemonize very early, then after import all stuff...
            if fd not in (3, 4, 5, 6, 7, 8):
                try:
                    os.close(fd)
                except OSError:
                    pass

        if (hasattr(os, "devnull")):
            REDIRECT_TO = os.devnull
        else:
            REDIRECT_TO = "/dev/null"

        os.open(REDIRECT_TO, os.O_RDWR)
        os.dup2(0, 1)
        os.dup2(0, 2)

        # write pidfile
        self.writePid()

    def kill(self):
        pid = self.readPid()
        if pid is None:
            print "Can not find a running mmc-agent."
            return 1

        try:
            os.kill(pid, signal.SIGTERM)
        except Exception, e:
            print "Can not terminate running mmc-agent: %s" % e
            return 1

        return 0

    def readPid(self):
        """ Try to read pid of running mmc-agent in pidfile
        Return the pid or None in case of failure
        """
        try:
            if os.path.exists(self.config.pidfile):
                f = open(self.config.pidfile, 'r')
                try:
                    line = f.readline()
                    return int(line.strip())
                finally:
                    f.close()
        except:
            return None

    def writePid(self):
        pid = os.getpid()
        f = open(self.config.pidfile, 'w')
        try:
            f.write('%s\n' % pid)
        finally:
            f.close()

    def cleanPid(self):
        if os.path.exists(self.config.pidfile):
            os.unlink(self.config.pidfile)

    def run(self):
        # If umask = 0077, created files will be rw for effective user only
        # If umask = 0007, they will be rw for effective user and group only
        os.umask(self.config.umask)
        os.setegid(self.config.egid)
        os.seteuid(self.config.euid)

        # Daemonize early
        if self.daemon:
            self.lock.acquire()
            self.daemonize()

        # Do all kind of initialization
        try:
            ret = self.initialize()
        finally:
            # Tell the father how to return, and let him return (release)
            if self.daemon:
                self.state = ret
                self.lock.release()

        if ret:
            return ret

        reactor.run()

    def initialize(self):
        # Initialize logging object
        logging.config.fileConfig(self.conffile)

        # In foreground mode, log to stderr
        if not self.daemon:
            hdlr2 = logging.StreamHandler()
            hdlr2.setFormatter(ColoredFormatter("%(levelname)-18s %(message)s"))
            logger.addHandler(hdlr2)

        # Create log dir if it doesn't exist
        try:
            os.mkdir(localstatedir + "/log/mmc")
        except OSError, (errno, strerror):
            # Raise exception if error is not "File exists"
            if errno != 17:
                raise
            else:
                pass

        # Changing path to probe and load plugins
        os.chdir(os.path.dirname(globals()["__file__"]))

        logger.info("mmc-agent %s starting..." % VERSION)
        logger.info("Using Python %s" % sys.version.split("\n")[0])
        logger.info("Using Python Twisted %s" % twisted.copyright.version)

        logger.debug("Running as euid = %d, egid = %d" % (os.geteuid(), os.getegid()))
        if self.config.multithreading:
            logger.info("Multi-threading enabled, max threads pool size is %d"
                        % self.config.maxthreads)
            reactor.suggestThreadPoolSize(self.config.maxthreads)

        # Export the MMC-AGENT variable in the environement so that
        # child process can know they were spawned by mmc-agent
        os.environ["MMC_AGENT"] = VERSION

        # Start audit system
        l = AuditFactory().log(u'MMC-AGENT', u'MMC_AGENT_SERVICE_START')

        # Ask PluginManager to load MMC plugins
        pm = PluginManager()
        code = pm.loadPlugins()
        if code:
            return code

        try:
            self.startService(pm.plugins)
        except Exception, e:
            # This is a catch all for all the exception that can happened
            logger.exception("Program exception: " + str(e))
            return 1

        l.commit()

        return 0

    def startService(self, mod):
        # Starting XMLRPC server
        r = MmcServer(mod, self.config)
        if self.config.enablessl:
            sslContext = makeSSLContext(self.config.verifypeer, self.config.cacert,
                                        self.config.localcert)
            reactor.listenSSL(self.config.port, MMCSite(r),
                              interface=self.config.host,
                              contextFactory=sslContext)
        else:
            logger.warning("SSL is disabled by configuration.")
            reactor.listenTCP(self.config.port, server.Site(r), interface=self.config.host)

        # Add event handler before shutdown
        reactor.addSystemEventTrigger('before', 'shutdown', self.cleanUp)
        logger.info("Listening to XML-RPC requests on %s:%s"
                    % (self.config.host, self.config.port))

    def cleanUp(self):
        """
        function call before shutdown of reactor
        """
        logger.info('mmc-agent shutting down, cleaning up...')
        l = AuditFactory().log(u'MMC-AGENT', u'MMC_AGENT_SERVICE_STOP')
        l.commit()

        self.cleanPid()


class MMCHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the MMC
    agent is in DEBUG mode, and to log connection errors.
    """

    def connectionMade(self):
        logger.debug("Connection from %s" % (self.transport.getPeer().host,))
        http.HTTPChannel.connectionMade(self)

    def connectionLost(self, reason):
        if not reason.check(twisted.internet.error.ConnectionDone):
            logger.error(reason)
        http.HTTPChannel.connectionLost(self, reason)


class MMCSite(server.Site):
    protocol = MMCHTTPChannel


def readConfig(config):
    """
    Read and check the MMC agent configuration file

    @param config: a MMCConfigParser object reading the agent conf file
    @type config: MMCConfigParser

    @return: MMCConfigParser object with extra attributes set
    @rtype: MMCConfigParser
    """
    # TCP/IP stuff
    try:
        config.host = config.get("main", "host")
        config.port = config.getint("main", "port")
    except Exception, e:
        logger.error(e)
        return 1

    if config.has_section("daemon"):
        config.euid = pwd.getpwnam(config.get("daemon", "user"))[2]
        config.egid = grp.getgrnam(config.get("daemon", "group"))[2]
        config.umask = string.atoi(config.get("daemon", "umask"), 8)
    else:
        config.euid = 0
        config.egid = 0
        config.umask = 0077

    # HTTP authentication login/password
    config.login = config.get("main", "login")
    config.password = config.getpassword("main", "password")

    # RPC session timeout
    try:
        config.sessiontimeout = config.getint("main", "sessiontimeout")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        # Use default session timeout
        config.sessiontimeout = server.Session.sessionTimeout

    # SSL stuff
    try:
        config.enablessl = config.getboolean("main", "enablessl")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        config.enablessl = False
    try:
        config.verifypeer = config.getboolean("main", "verifypeer")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        config.verifypeer = False

    if config.enablessl:
        # For old version compatibility, we try to get the old options name
        try:
            config.localcert = config.get("main", "localcert")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            config.localcert = config.get("main", "privkey")
        try:
            config.cacert = config.get("main", "cacert")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            config.cacert = config.get("main", "certfile")

    try:
        config.pidfile = config.get("daemon", "pidfile")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        # For compatibility with old version
        config.pidfile = config.get("log", "pidfile")

    # Multi-threading support
    config.multithreading = True
    config.maxthreads = 20
    try:
        config.multithreading = config.getboolean("main", "multithreading")
        config.maxthreads = config.getint("main", "maxthreads")
    except ConfigParser.NoOptionError:
        pass

    return config


class PluginManager(Singleton):
    """
    This singleton class imports available MMC plugins, activates them, and
    keeps track of all enabled plugins.
    """

    pluginDirectory = 'plugins/'
    # Will contains the enabled plugins name and corresponding python
    # module objects
    plugins = {}

    def __init__(self):
        Singleton.__init__(self)

    def isEnabled(self, plugin):
        """
        @rtype: bool
        @return: Return True if the plugin has been enabled
        """
        return plugin in self.plugins

    def getEnabledPlugins(self):
        """
        @rtype: dict
        @return: the enabled plugins as a dict, key is the plugin name, value
                 is the python module object
        """
        return self.plugins

    def getEnabledPluginNames(self):
        """
        @rtype: list
        @return: the names of the enabled plugins
        """
        return self.getEnabledPlugins().keys()

    def getAvailablePlugins(self):
        """
        Fetch all available MMC plugin

        @return: list of all mmc plugins names
        @rtype: list
        """
        plugins = []
        for path in glob.glob(os.path.join(self.pluginDirectory, "*", "__init__.py*")):
            plugin = path.split("/")[1]
            if not plugin in plugins:
                plugins.append(plugin)
        return plugins

    def loadPlugin(self, name, force=False):
        """
        Load a plugin with the given name.

        To start one single module after the agent startup, use startPlugin()
        instead

        @returns: 4 on fatal error (mmc agent should not start without that
        plugin), 0 on non-fatal failure, and the module itself if
        the load was successful
        """
        f, p, d = imp.find_module(name, ['plugins'])

        try:
            logger.debug("Trying to load module %s" % name)
            plugin = imp.load_module(name, f, p, d)
            logger.debug("Module %s loaded" % name)
        except Exception, e:
            logger.exception(e)
            logger.error('Module ' + name + " raise an exception.\n" + name + " not loaded.")
            return 0

        # If module has no activate function
        try:
            # if not force:
            #     func = getattr(plugin, "activate")
            # else:
                # logger.debug('Forcing plugin startup')
                # try:
            # func = getattr(plugin, "activateForced")
        # except AttributeError:
            # logger.debug('Trying to force startup of plugin %s but no "activateForced" method found\nFalling back to the normale activate method' % (name,))
            func = getattr(plugin, "activate")
        except AttributeError:
            logger.error('%s is not a MMC plugin.' % name)
            plugin = None
            return 0

        # If is active
        try:
            if (func()):
                version = 'version: ' + str(getattr(plugin, "getVersion")())
                logger.info('Plugin %s loaded, %s' % (name, version))
            else:
                # If we can't activate it
                logger.warning('Plugin %s not loaded.' % name)
                plugin = None
        except Exception, e:
            logger.error('Error while trying to load plugin ' + name)
            logger.exception(e)
            plugin = None
            # We do no exit but go on when another plugin than base fail

        # Check that "base" plugin was loaded
        if name == "base" and not plugin:
            logger.error("MMC agent can't run without the base plugin. Exiting.")
            return 4
        return plugin

    def startPlugin(self, name):
        """
        Force a plugin load.
        Even if the configuration indicates the plugin is disabled,
        we load it and add it to the loaded list.

        Use it to start a plugin after the mmc agent startup, dynamically.

        This tries to call the activateForced method of the plugin (for example to
        ignore the disable = 1 configuration option)
        """
        if name in self.getEnabledPluginNames() or name in self.plugins:
            logger.warning('Trying to start an already loaded plugin: %s' % (name,))
            return 0
        res = self.loadPlugin(name, force=True)
        if res == 0:
            return 0
        elif res is not None and not isinstance(res, int):
            self.plugins[name] = res
            getattr(self.plugins["base"], "setModList")([name for name in self.plugins.keys()])
        elif res == 4:
            return 4
        return res

    def loadPlugins(self):
        """
        Find and load available MMC plugins

        @rtype: int
        @returns: exit code > 0 on error
        """
        # Find available plugins
        mod = {}
        sys.path.append("plugins")
        # self.modList = []
        plugins = self.getAvailablePlugins()
        if not "base" in plugins:
            logger.error("Plugin 'base' is not available. Please install it.")
            return 1
        else:
            # Set base plugin as the first plugin to load
            plugins.remove("base")
            plugins.insert(0, "base")

        # Put pulse2 plugins as the last to be imported, else we may get a mix
        # up with pulse2 module available in the main python path
        if "pulse2" in plugins:
            plugins.remove("pulse2")
            plugins.append("pulse2")

        # Load plugins
        logger.info("Importing available MMC plugins")
        for plugin in plugins:
            res = self.loadPlugin(plugin)
            if res == 0:
                continue
            elif res is not None and not isinstance(res, int):
                mod[plugin] = res
            elif res == 4:
                return 4

        # store enabled plugins
        self.plugins = mod

        logger.info("MMC plugins activation stage 2")
        for plugin in plugins:
            if self.isEnabled(plugin):
                try:
                    func = getattr(mod[plugin], "activate_2")
                except AttributeError:
                    func = None
                if func:
                    if not func():
                        logger.error("Error in activation stage 2 for plugin '%s'" % plugin)
                        logger.error("Please check your MMC agent configuration and log")
                        return 4

        # Set module list
        getattr(self.plugins["base"], "setModList")([name for name in self.plugins.keys()])
        return 0

    def stopPlugin(self, name):
        """
        Stops a plugin.

        @rtype: boolean
        returns: True on success, False if the module is not loaded.
        """
        if not name in self.plugins:
            return False
        plugin = self.plugins[name]
        try:
            deactivate = getattr(plugin, 'deactivate')
        except AttributeError:
            logger.info('Plugin %s has no deactivate function' % (name,))
        else:
            logger.info('Deactivating plugin %s' % (name,))
            deactivate()
        del self.plugins[name]
        getattr(self.plugins["base"], "setModList")([name for name in self.plugins.keys()])
        return True
