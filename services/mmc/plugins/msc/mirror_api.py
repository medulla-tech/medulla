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
        except:
            self.logger.warn("MirrorApi cant connect to %s" % (self.server_addr))
            self.initialized_failed = True

    def getMirror(self, machine):
        if self.initialized_failed:
            return []
        try:
            machine = self.convertMachineIntoH(machine)
            return self.xmlrpc.getMirror(machine)
        except:
            self.logger.warn("MirrorApi:getMirror %s fails"%(str(machine)))
            return []

    def getMirrors(self, machines):
        if self.initialized_failed:
            return []
        try:
            machines = map(lambda m: convertMachineIntoH(m), machines)
            return self.xmlrpc.getMirrors(machines)
        except:
            self.logger.warn("MirrorApi:getMirrors %s fails"%(str(machines)))
            return []

    def getFallbackMirror(self, machine):
        if self.initialized_failed:
            return []
        try:
            machine = self.convertMachineIntoH(machine)
            return self.xmlrpc.getFallbackMirror(machine)
        except:
            self.logger.warn("MirrorApi:getFallbackMirror %s fails"%(str(machine)))
            return []

    def getFallbackMirrors(self, machines):
        if self.initialized_failed:
            return []
        try:
            machines = map(lambda m: convertMachineIntoH(m), machines)
            return self.xmlrpc.getFallbackMirrors(machines)
        except:
            self.logger.warn("MirrorApi:getFallbackMirrors %s fails"%(str(machines)))
            return []
        
    def getApiPackage(self, machine):
        self.logger.debug(machine)
        if self.initialized_failed:
            return []
        try:
            machine = self.convertMachineIntoH(machine)
            return self.xmlrpc.getApiPackage(machine)
        except Exception, e:
            self.logger.warn("MirrorApi:getApiPackage %s fails"%(str(machine)))
            self.logger.warn(e)
            return []

    def getApiPackages(self, machines):
        if self.initialized_failed:
            return []
        try:
            machines = map(lambda m: convertMachineIntoH(m), machines)
            return self.xmlrpc.getApiPackages(machines)
        except:
            self.logger.warn("MirrorApi:getApiPackages %s fails"%(str(machines)))
            return []

    def convertMachineIntoH(self, machine):
        if type(machine) != dict:
            machine = {'uuid':machine}
        return machine
        
class Mirror:
    def __init__(self, server):
        self.logger = logging.getLogger()
        self.logger.debug('Mirror will connect to %s' % (server))
        try:
            self.server = xmlrpclib.Server(server)
            self.xmlrpc = self.server.xmlrpc
            self.initialized_failed = False
        except:
            self.logger.warn("Mirror cant connect to %s" % (server))
            self.initialized_failed = True
        
    def isAvailable(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.isAvailable(pid)
        except: # when the api is not available, the package is also unavailable
            self.logger.warn("Mirror:isAvailable %s fails"%(pid))
            return False

    def getFilePath(self, fid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getFilePath(fid)
        except:
            self.logger.warn("Mirror:getFilePath %s fails"%(fid))
            return False
   
