import re
import dircache
import os
import logging

import xmlrpclib
from twisted.web.xmlrpc import Proxy

import mmc.plugins.msc
from mmc.support.mmctools import Singleton

from mmc.client import XmlrpcSslProxy, makeSSLContext

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.
class MirrorApi(Singleton):
    def __init__(self):
        self.logger = logging.getLogger()
        self.config = mmc.plugins.msc.MscConfig("msc")

        if self.config.ma_enablessl:
            self.server_addr = 'https://'
        else:
            self.server_addr = 'http://'

        if self.config.ma_username != '':
            self.server_addr += self.config.ma_username
            if self.config.ma_password != '':
                self.server_addr += ":"+self.config.ma_password
            self.server_addr += "@"

        self.server_addr += self.config.ma_server+':'+str(self.config.ma_port) + self.config.ma_mountpoint
        self.logger.debug('MirrorApi will connect to %s' % (self.server_addr))

        if self.config.ma_verifypeer:
            self.maserver = XmlrpcSslProxy(self.server_addr)
            self.sslctx = makeSSLContext(self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert, False)
            self.maserver.setSSLClientContext(self.sslctx)
        else:
            self.maserver = Proxy(self.server_addr)
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args):
        self.logger.warn("%s %s has failed: %s" % (funcname, args, error))
        return []

    def getMirror(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.maserver.callRemote("getMirror", machine)
        d.addErrback(self.onError, "MirrorApi:getMirror", machine)
        return d

    def getMirrors(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.maserver.callRemote("getMirrors", machines)
        d.addErrback(self.onError, "MirrorApi:getMirrors", machines)
        return d

    def getFallbackMirror(self, machine):
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.maserver.callRemote("getFallbackMirror", machine)
        d.addErrback(self.onError, "MirrorApi:getFallbackMirror", machine)
        return d

    def getFallbackMirrors(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.maserver.callRemote("getFallbackMirrors", machines)
        d.addErrback(self.onError, "MirrorApi:getFallbackMirrors", machines)
        return d

    def getApiPackage(self, machine):
        self.logger.debug(machine)
        if self.initialized_failed:
            return []
        machine = self.convertMachineIntoH(machine)
        d = self.maserver.callRemote("getApiPackage", machine)
        d.addErrback(self.onError, "MirrorApi:getApiPackage", machine)
        return d

    def getApiPackages(self, machines):
        if self.initialized_failed:
            return []
        machines = map(lambda m: self.convertMachineIntoH(m), machines)
        d = self.maserver.callRemote("getApiPackages", machines)
        d.addErrback(self.onError, "MirrorApi:getApiPackages", machines)
        return d

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
            #self.xmlrpc = self.server.xmlrpc
            self.xmlrpc = self.server
            self.initialized_failed = False
        except:
            self.logger.warn("Mirror cant connect to %s" % (server))
            self.initialized_failed = True

    def isInitialized(self):
        """ True if inititialized, or False if something goes wrong """
        return not self.initialized_failed

    def getServerDetails(self):
        """ gather stuff about our mirror """
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getServerDetails()
        except: # when the api is not available, the package is also unavailable
            self.logger.warn("Mirror:getServerDetails fails")
            return False

    def isAvailable(self, pid):
        """ Is my package (identified by pid) available ? """
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.isAvailable(pid)
        except: # when the api is not available, the package is also unavailable
            self.logger.warn("Mirror:isAvailable %s fails"%(pid))
            return False

    def getFileURI(self, fid):
        """ convert from a fid (File ID) to a file URI """
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getFileURI(fid)
        except:
            self.logger.warn("Mirror:getFileURI %s fails" % fid)
            return False

    def getFilesURI(self, fids):
        """ convert from a list of fids (File ID) to a list of files URI """
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getFilesURI(fids)
        except:
            self.logger.warn("Mirror:getFilesURI %s fails " % fids)
            return False
