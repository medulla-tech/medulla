import re
import dircache
import os
import logging

import xmlrpclib

from mmc.support.mmctools import Singleton
import mmc.plugins.pkgs.config

from mmc.client import XmlrpcSslProxy, makeSSLContext

class UserPackageApiApi(Singleton):
    def __init__(self):
        self.logger = logging.getLogger()
        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")
        
        if self.config.upaa_enablessl:
            self.server_addr = 'https://'
        else:
            self.server_addr = 'http://'

        if self.config.upaa_username != '':
            self.server_addr += self.config.upaa_username
            if self.config.upaa_password != '':
                self.server_addr += ":"+self.config.upaa_password
            self.server_addr += "@"

        self.server_addr += self.config.upaa_server+':'+str(self.config.upaa_port) + self.config.upaa_mountpoint
        self.logger.debug('UserPackageApiApi will connect to %s' % (self.server_addr))

        self.upaaserver = XmlrpcSslProxy(self.server_addr)
        if self.config.upaa_verifypeer:
            self.sslctx = makeSSLContext(self.config.upaa_verifypeer, self.config.upaa_cacert, self.config.upaa_localcert, False)
            self.upaaserver.setSSLClientContext(self.sslctx)
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args):
        self.logger.warn("%s %s has failed: %s" % (funcname, args, error))
        return []

    def getUserPackageApi(self, user):
        if self.initialized_failed:
            return {}
        d = self.upaaserver.callRemote("getUserPackageApi", {"name":user, "uuid":user})
        d.addErrback(self.onError, "UserPackageApiApi:getUserPackageApi", {"name":user, "uuid":user})
        return d
