import re
import os
import logging

import xmlrpclib
from twisted.web.xmlrpc import Proxy

import mmc.plugins.msc
from mmc.plugins.msc.config import MscConfig
from mmc.support.mmctools import Singleton

from mmc.client import XmlrpcSslProxy, makeSSLContext

from twisted.internet import defer

class SchedulerApi(Singleton):
    def __init__(self):
        self.logger = logging.getLogger()
        self.config = mmc.plugins.msc.MscConfig("msc")
        
        if self.config.sa_enable:
            if self.config.sa_enablessl:
                self.server_addr = 'https://'
            else:
                self.server_addr = 'http://'
    
            if self.config.sa_username != '':
                self.server_addr += self.config.sa_username
                if self.config.sa_password != '':
                    self.server_addr += ":"+self.config.sa_password 
                self.server_addr += "@"
    
            self.server_addr += self.config.sa_server+':'+str(self.config.sa_port) + self.config.sa_mountpoint
            self.logger.debug('SchedulerApi will connect to %s' % (self.server_addr))
    
            if self.config.sa_verifypeer:
                self.saserver = XmlrpcSslProxy(self.server_addr)
                self.sslctx = makeSSLContext(self.config.sa_verifypeer, self.config.sa_cacert, self.config.sa_localcert, False)
                self.saserver.setSSLClientContext(self.sslctx)
            else:
                self.saserver = Proxy(self.server_addr)
    
    def onError(self, error, funcname, args):
        self.logger.warn("%s %s has failed: %s" % (funcname, args, error))
        return []

    def getScheduler(self, machine):
        if self.config.sa_enable:
            machine = self.convertMachineIntoH(machine)
            d = self.saserver.callRemote("getScheduler", machine)
            d.addErrback(self.onError, "SchedulerApi:getScheduler", machine)
            return d
        else:
            return defer.succeed(MscConfig("msc").default_scheduler)
        
    def getSchedulers(self, machines):
        if self.config.sa_enable:
            machines = map(lambda m: self.convertMachineIntoH(m), machines)
            d = self.saserver.callRemote("getSchedulers", machines)
            d.addErrback(self.onError, "SchedulerApi:getSchedulers", machines)
            return d
        else:
            return defer.succeed(map(lambda m: MscConfig("msc").default_scheduler, machines))

    def convertMachineIntoH(self, machine):
        if type(machine) != dict:
            machine = {'uuid':machine}
        return machine

