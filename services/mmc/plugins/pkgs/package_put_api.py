import re
import dircache
import os
import logging

import xmlrpclib
from twisted.web.xmlrpc import Proxy

from mmc.support.mmctools import Singleton
import mmc.plugins.pkgs.config

from mmc.client import XmlrpcSslProxy, makeSSLContext

class PackagePutA:
    def __init__(self, server, port = None, mountpoint = None, proto = 'http', login = ''):
        self.logger = logging.getLogger()
        if type(server) == dict:
            mountpoint = server['mountpoint']
            port = server['port']
            proto = server['protocol']
            bind = server['server']
            if server.has_key('username') and server.has_key('password') and server['username'] != '':
                login = "%s:%s@" % (server['username'], server['password'])

        self.server_addr = '%s://%s%s:%s%s' % (proto, login, bind, str(port), mountpoint)
        self.logger.debug('PackagePutA will connect to %s' % (self.server_addr))

        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")
        if self.config.upaa_verifypeer:
            self.ppaserver = XmlrpcSslProxy(self.server_addr)
            self.sslctx = makeSSLContext(self.config.upaa_verifypeer, self.config.upaa_cacert, self.config.upaa_localcert, False)
            self.ppaserver.setSSLClientContext(self.sslctx)
        else:
            self.ppaserver = Proxy(self.server_addr)
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args = '', value = []):
        self.logger.warn("PackagePutA:%s %s has failed: %s" % (funcname, args, error))
        return value
                    
    def getTemporaryFiles(self):
        if self.initialized_failed:
            return []
        d = self.ppaserver.callRemote("getTemporaryFiles")
        d.addErrback(self.onError, "getTemporaryFiles")
        return d
        
    def putPackageDetail(self, package):
        if self.initialized_failed:
            return -1
        d = self.ppaserver.callRemote("putPackageDetail", package)
        d.addErrback(self.onError, "putPackageDetail", package, -1)
        return d

    def dropPackage(self, pid):
        if self.initialized_failed:
            return -1
        d = self.ppaserver.callRemote("dropPackage", pid)
        d.addErrback(self.onError, "dropPackage", pid, -1)
        return d
