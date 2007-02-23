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

from twisted.web import xmlrpc, server
from twisted.internet import ssl
from twisted.internet import reactor

import re
import imp
import logging
import logging.config
import xmlrpclib
import os
import sys
import ConfigParser
import base64
import glob
import traceback
import time

sys.path.append("plugins")
import support.lmcException

Fault = xmlrpclib.Fault
__config = None #shared config object

VERSION = "1.1.2"

def getAvailablePlugins(path):
    """
    Fetch all available LMC plugin

    @param path: UNIX path where the plugins are located
    @type path: str

    @return: list of all .py in a path
    @rtype: list
    """
    ret = []
    for item in glob.glob(os.path.join(path, "*", "__init__.py")):
        ret.append(item.split("/")[1])
    return ret

class LmcServer(xmlrpc.XMLRPC,object):
    """
    LMC Server implemented as a XML-RPC server.

    config file : /etc/lmc/agent/config.ini

    Create a twisted XMLRPC server, load plugins in
    "plugins/" directory
    """

    def __init__(self, modules, login, password):
        xmlrpc.XMLRPC.__init__(self)
        self.modules = modules
        self.login = login
        self.password = password

    def _getFunction(self, functionPath):
        """Overrided to use functions from our plugins"""

        if ('.' in functionPath):
            mod, func = functionPath.split('.')
        else:
            func = functionPath
        logger = logging.getLogger()

        try:
            if '.' in functionPath:
                return getattr(self.modules[mod], func)
            else:
                return getattr(self, func)
        except:
            logger.error(functionPath+' not found')
            raise Fault("NO_SUCH_FUNCTION", "No such function " + functionPath)

    def render(self, request):
        """
        override method of xmlrpc python twisted framework

        @param request: raw request xmlrpc
        @type request: xml str

        @return: interpreted request
        """
        request.content.seek(0, 0)
        args, functionPath = xmlrpclib.loads(request.content.read())
        logger = logging.getLogger()
        logger.debug('Calling ' + functionPath + str(args))
        try:
            function = self._getFunction(functionPath)
        except Fault, f:
            self._cbRender(f, request)
        else:
            request.setHeader("content-type", "text/xml")
            result = None
            try:
                result = apply(function, args)
            except support.lmcException.lmcException, e:
                result = {}
                result['faultString'] = e.funcname
                result['faultCode'] = str(e.__class__)+": "+str(e)
                result['faultTraceback']= "";
                for msg in traceback.format_tb(sys.exc_info()[2]):
                    result['faultTraceback']+= "\n"+msg;
            except Exception, e:
                logger.exception("Error during render " + functionPath + ": " + str(e))
                result = {}
                result['faultString'] = functionPath
                result['faultCode'] = str(e.__class__) + ": " + str(e) + " " + str(args)
                result['faultTraceback']= "";
                for msg in traceback.format_tb(sys.exc_info()[2]):
                    result['faultTraceback']+= "\n"+msg;

            logger.debug('response ' + str(result))
            self._cbRender(result, request)
        return server.NOT_DONE_YET

    def _cbRender(self, result, request):
        if result == None: result = 0
        if isinstance(result, xmlrpc.Handler):
            result = result.result
        if not isinstance(result, Fault):
            result = (result,)
        try:
            s = xmlrpclib.dumps(result, methodresponse=1)
        except:
            f = Fault(self.FAILURE, "can't serialize output")
            s = xmlrpclib.dumps(f, methodresponse=1)
        request.setHeader("content-length", str(len(s)))
        request.write(s)
        request.finish()

    def getRevision(self):
        return int("$Rev$".split(':')[1].strip(' $'))

    def getVersion(self):
        return VERSION

    def log(self, fileprefix, content):
        """
        @param fileprefix: Write log file in /var/log/lmc/lmc-fileprefix.log
        @param content: string to record in log file
        """
        f = open('/var/log/lmc/lmc-' + fileprefix + '.log', 'a')
        f.write(time.asctime() + ': ' + content + "\n")
        f.close()


def daemon(config):
    """
    daemonize lmc-agent

    @param pidfile: path to pid file
    @type pidfile: str
    """
    try:
        pidfile = config.get("main", "pidfile")
    except ConfigParser.NoOptionError:
        # For compatibility with old version
        pidfile = config.get("log", "pidfile")

    # Test if lmcagent has been already launched in daemon mode
    if os.path.isfile(pidfile):
        print pidfile+" pid already exist. Maybe lmc-agent is already running\n"
        print "use /etc/init.d script to stop and relaunch it"
        sys.exit(0)

    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
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
            # exit from second parent, print eventual PID before
            print "Daemon PID %d" % pid
            os.system("echo " + str(pid) + " > " + pidfile)
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

def agentService(config, conffile, daemonize):
    # File will be rw for root user only
    os.umask(0077)

    # Create log dir if it doesn't exist
    os.system('mkdir -p /var/log/lmc')

    # Initialize logging object
    logging.config.fileConfig(conffile)
    logger = logging.getLogger()

    # When starting LmcServer, we log to stderr too
    hdlr2 = logging.StreamHandler()
    logger.addHandler(hdlr2)

    # Changing path to probe and load plugins
    os.chdir(os.path.dirname(globals()["__file__"]))

    logger.info("lmc-agent starting...")

    # Find available plugins
    mod = {}
    sys.path.append("plugins")
    modList = []
    plugins = getAvailablePlugins("plugins/")
    if not "base" in plugins:
        logger.error("Plugin 'base' is not available. Please install it.")
        return 1
    else:
        # Set base plugin as the first plugin to load
        plugins.remove("base")
        plugins.insert(0, "base")

    # Load plugins
    for plugin in plugins:
        f, p, d = imp.find_module(plugin, ['plugins'])

        try:
            mod[plugin] = imp.load_module(plugin, f, p, d)
        except Exception,e:
            logger.exception(e)
            logger.error('Plugin '+ plugin+ " raise an exception.\n"+ plugin+ " not loaded.")
            continue

        # If module has no activate function
        try:
            func = getattr(mod[plugin], "activate")
        except:
            logger.error('File '+ plugin+ ' is not a LMC plugin.')
            del mod[plugin]
            continue

        # If is active
	try:
            if (func()):
                version = 'API version: '+str(getattr(mod[plugin], "getApiVersion")())+' build(' +str(getattr(mod[plugin], "getRevision")())+')'
                logger.info('Plugin ' + plugin + ' loaded, ' + version)
                modList.append(str(plugin))
            else:
                # If we can't activate it
                logger.info('Plugin '+plugin+' not loaded.')
                del mod[plugin]
        except Exception, e:
            logger.error('Error while trying to load plugin ' + plugin)
            logger.exception(e)
            del mod[plugin]
            # We do no exit but go on when another plugin than base fail

        # Check that "base" plugin was loaded
        if plugin == "base" and not "base" in mod:
            logger.error("LMC agent can't run without the base plugin. Exiting.")
            return 4

    # Set module list
    setModList = getattr(mod["base"], "setModList")
    setModList(modList)

    # No more log to stderr
    logger.removeHandler(hdlr2)

    # Become a daemon
    if daemonize: daemon(config)

    return startService(config,logger,mod)

def cleanUp():
    """
    function call before shutdown of reaction
    """
    logger = logging.getLogger()
    logger.info('Lmc shutting down, cleaning up...')
    # FIXME: do we really need this global __config ?
    try:
        pidfile = __config.get("main", "pidfile")
    except ConfigParser.NoOptionError:
        pidfile = __config.get("log", "pidfile")

    # Test if lmcagent pidfile exist
    if os.path.isfile(pidfile):
        os.unlink(pidfile)


def startService(config,logger,mod):
    # TCP/IP stuff
    try:
        host = config.get("main", "host")
        port = config.getint("main", "port")
    except Exception,e:
        logger.error(e)
        return 1

    # SSL stuff
    try:
        enablessl = config.getboolean("main", "enablessl")
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        enablessl = 0
    if enablessl:
        try:
            privkey = config.get("main", "privkey")
            certfile = config.get("main", "certfile")
        except Exception, e:
            logger.error(e)
            return 1
    else:
        logger.warning("SSL is disabled by configuration.")

    # HTTP authentication login/password
    try:
        login = config.get("main", "login")
        password = config.get("main", "password")
    except Exception, e:
        # Default login/pass if not set
        login = "lmc"
        password = "s3cr3t"
        logger.warning("Default login/password are used: your configuration is not secure. Please fix it.")

    # Starting XMLRPC server
    ret = 0
    try:
        r = LmcServer(mod, login, password)
        if enablessl:
            sslContext = ssl.DefaultOpenSSLContextFactory(privkey, certfile)
            reactor.listenSSL(port, server.Site(r), interface = host, contextFactory = sslContext)
        else:
            reactor.listenTCP(port, server.Site(r), interface = host)
        #add event handler before shutdown
        global __config
        __config = config #set shared config object
        reactor.addSystemEventTrigger('before','shutdown',cleanUp)
        reactor.run()
    except Exception, e:
        # This is a catch all for all the exception that can happened
        logger.exception("Program exception:")
        ret = 1

    return ret
