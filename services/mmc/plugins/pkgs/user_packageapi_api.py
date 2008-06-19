import re
import dircache
import os
import logging

import xmlrpclib

from mmc.support.mmctools import Singleton
import mmc.plugins.pkgs.config

class UserPackageApiApi(Singleton):
    def __init__(self):
        self.logger = logging.getLogger()
        self.config = mmc.plugins.pkgs.PkgsConfig("pkgs")
        
        proto = 'http'
        if self.config.upaa_enablessl:
            proto = 'https'

        login = ''
        if self.config.upaa_username != '':
            login = self.config.upaa_username
            if self.config.upaa_password != '':
                login += ':' + self.config.upaa_password
            login += '@'

        self.server_addr = '%s://%s%s:%s%s' % (proto, login, self.config.upaa_server, str(self.config.upaa_port), self.config.upaa_mountpoint)
        self.logger.debug('UserPackageApiApi will connect to %s' % (self.server_addr))
        try:
            self.server = xmlrpclib.Server(self.server_addr)
            self.xmlrpc = self.server.xmlrpc
            self.initialized_failed = False
        except:
            self.logger.warn("UserPackageApiApi cant connect to %s" % (self.server_addr))
            self.initialized_failed = True
        
    def getUserPackageApi(self, user):
        if self.initialized_failed:
            return {}
        try:
            return self.xmlrpc.getUserPackageApi({"name":user, "uuid":user})
        except:
            self.logger.warn("UserPackageApiApi:getUserPackageApi %s fails"%(str(user)))
            return {}
    
