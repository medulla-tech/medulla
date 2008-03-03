import re
import dircache
import os
import logging

import xmlrpclib

#from mmc.plugins.msc import MscConfig
import mmc.plugins.msc
from mmc.support.mmctools import Singleton

# need to get a PackageApiManager, it will manage a PackageApi for each mirror 
# defined in the conf file.
class MirrorApi(Singleton):
    def __init__(self):
        self.logger = logging.getLogger()
        self.config = mmc.plugins.msc.MscConfig("msc")

        self.server_addr = 'http://'+self.config.ma_server+':'+str(self.config.ma_port) + self.config.ma_mountpoint
        self.logger.debug('MirrorApi will connect to %s' % (self.server_addr))
        try:
            self.server = xmlrpclib.Server(self.server_addr)
            self.xmlrpc = self.server.xmlrpc
            self.initialized_failed = False
        except Exception, e:
            self.logger.error("MirrorApi cant connect to %s" % (self.server_addr))
            self.logger.debug(e)
            self.initialized_failed = True

    def getMirror(self, machine):
        if self.initialized_failed:
            return []
        return self.xmlrpc.getMirror(machine)

    def getMirrors(self, machines):
        if self.initialized_failed:
            return []
        return self.xmlrpc.getMirrors(machines)

    def getFallbackMirror(self, machine):
        if self.initialized_failed:
            return []
        return self.xmlrpc.getFallbackMirror(machine)

    def getFallbackMirrors(self, machines):
        if self.initialized_failed:
            return []
        return self.xmlrpc.getFallbackMirrors(machines)

    def getApiPackage(self, machine):
        self.logger.debug(machine)
        if self.initialized_failed:
            return []
        ret = self.xmlrpc.getApiPackage(machine)
        self.logger.debug(ret)
        return ret

    def getApiPackages(self, machines):
        if self.initialized_failed:
            return []
        return self.xmlrpc.getApiPackages(machines)

class Mirror:
    def __init__(self, server):
        self.logger = logging.getLogger()
        self.logger.debug('Mirror will connect to %s' % (server))
        self.server = xmlrpclib.Server(server)
        self.xmlrpc = self.server.xmlrpc
        
    def isAvailable(self, pid):
        return self.xmlrpc.isAvailable(pid)

    def getFilePath(self, fid):
        return self.xmlrpc.getFilePath(fid)
   
