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

from twisted.internet import reactor
from twisted.web import server
from twisted.web import xmlrpc
from twisted.internet import defer, ssl
from twisted.web.xmlrpc import Proxy, QueryFactory
import xmlrpclib

import time
import logging
import ConfigParser
import os
import sys

INIFILE = "/etc/lmc/proxy/config.ini"

class SslProxy(Proxy):

    def __init__(self, url, privkey, certfile):
        self.privkey = privkey
        self.certfile = certfile
        Proxy.__init__(self, url)

    def callRemote(self, method, *args):
        """Override default callRemote because we use certificate to connect to"""
        factory = QueryFactory(self.url, self.host, method, *args)
        if self.secure:
            ctx = ssl.DefaultOpenSSLContextFactory(self.privkey, self.certfile)
            ctx.isClient = 1
            reactor.connectSSL(self.host, self.port or 443, factory, ctx)
        else:
            reactor.connectTCP(self.host, self.port or 80, factory)
        return factory.deferred

class LmcProxy(xmlrpc.XMLRPC):
    """LMC Proxy implemented as a XML-RPC server."""

    def __init__(self, privkey, certfile):
        self.privkey = privkey
        self.certfile = certfile
        xmlrpc.XMLRPC.__init__(self)

    def xmlrpc_redirect(self, url, func, args):

        def printValue(value):
            print repr(value)
            return value

        def printError(error):
            print 'error', error
            return error

        print url, func, args, type(args)
        proxy = Proxy(url)
        if type(args) == str and args != "":
            ret = proxy.callRemote(func, args).addCallbacks(printValue, printError)
        else:
            ret = proxy.callRemote(func, *args).addCallbacks(printValue, printError)
        return ret

class LmcProxyLauncher:
    """Launch a LMC Proxy."""

    def __init__(self, conffile = None, daemonize = True):
        if not conffile: conffile = INIFILE
        config = ConfigParser.ConfigParser()
        config.read(conffile)

        try:
            log = config.get("main", "log")
        except Exception, e:
            print e
            sys.exit(1)

        # Initialize logging object
        logger = logging.getLogger()
        hdlr = logging.FileHandler(log)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.DEBUG)

        # When starting LmcProxyLauncher, we log to stderr too
        hdlr2 = logging.StreamHandler()
        logger.addHandler(hdlr2)

        try:
            name = config.get("main", "log")
            pidfile = config.get("main", "pidfile")
            port = config.get("main", "port")
            ip = config.get("main", "ip")
            privkey = config.get("main", "privkey")
            certfile = config.get("main", "certfile")
        except Exception, e:
            logger.error(e)
            sys.exit(1)

        if daemonize: self.daemon(pidfile)

        # start the main loop
        lmcproxy = LmcProxy(privkey, certfile)
        reactor.listenTCP(int(port), server.Site(lmcproxy))
        reactor.run()

        sys.exit(ret)

    def daemon(self, pidfile):
        # Test if lmcagent has been already launched in daemon mode
        if os.path.isfile(pidfile):
            name = "Lmc Proxy"
            print pidfile+" pid already exist. Maybe "+name+" is already running\n"
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
        os.umask(0)

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


if __name__ == "__main__":
    LmcProxyLauncher(daemonize=False)
