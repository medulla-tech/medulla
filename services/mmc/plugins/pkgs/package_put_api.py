import re
import dircache
import os
import logging

import xmlrpclib

from mmc.support.mmctools import Singleton

class PackagePutA:
    def __init__(self, server, port = None, mountpoint = None):
        self.logger = logging.getLogger()

        login = ''
        if type(server) == dict:
            mountpoint = server['mountpoint']
            port = server['port']
            proto = server['protocol']
            bind = server['server']

            if server.has_key('username') and server.has_key('password') and server['username'] != '':
                login = "%s:%s@" % (server['username'], server['password'])

        self.server_addr = '%s://%s%s:%s%s' % (proto, login, bind, str(port), mountpoint)
        self.logger.debug('PackageA will connect to %s' % (self.server_addr))
        self.logger.debug('PackagePutA will connect to %s' % (self.server_addr))


        try:
            self.server = xmlrpclib.Server(self.server_addr)
            self.xmlrpc = self.server.xmlrpc
            self.initialized_failed = False
        except:
            self.logger.warn('PackagePutA failed to connect to %s' % (self.server_addr))
            self.initialized_failed = True

    def putPackageDetail(self, package):
        if self.initialized_failed:
            return -1
        try:
            return self.xmlrpc.putPackageDetail(package)
        except:
            self.logger.warn("PackagePutA:putPackageDetail %s fails"%(str(package)))
            return -1
    
