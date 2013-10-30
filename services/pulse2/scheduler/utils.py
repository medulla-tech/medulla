# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import logging
try :
    import cPickle as pickle
except ImportError :
    import pickle

from twisted.internet.protocol import Factory, ProcessProtocol
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred

from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.network import chooseClientIP 
from pulse2.scheduler.checks import getCheck

import traceback

class PackUtils :
    @classmethod
    def pack(cls, data):
        return pickle.dumps(data)

    @classmethod
    def unpack(cls, packet):
        return pickle.loads(packet)

def getClientCheck(target):
    return getCheck(SchedulerConfig().client_check, {
        'uuid': target.getUUID(),
        'shortname': target.getShortName(),
        'ips': target.getIps(),
        'macs': target.getMacs()
    })

def getServerCheck(target):
    return getCheck(SchedulerConfig().server_check, {
        'uuid': target.getUUID(),
        'shortname': target.getShortName(),
        'ips': target.getIps(),
        'macs': target.getMacs()
    })

def extractCredentials(mirror):
    if not '@' in mirror:
        return ('', mirror)
    mirror = mirror.replace('http://', '')
    credentials, mirror = mirror.split("@")
    return (credentials, 'http://%s'%mirror)

def chooseClientInfo(target):
    return chooseClientIP({
        'uuid': target.getUUID(),
        'fqdn': target.getFQDN(),
        'shortname': target.getShortName(),
        'ips': target.getIps(),
        'macs': target.getMacs(),
        'netmasks': target.getNetmasks()
    })



class UnixProtocol (object, LineOnlyReceiver):
    def dataReceived(self, data):
        try :
            name, args = PackUtils.unpack(data)
            method = self._lookup_procedure(name)
        except :
            logging.getLogger().error("unix socket recv failed: %s"  % traceback.format_exc())

        d = maybeDeferred(method, self, *args)
        d.addCallback(self._send_response)
        d.addErrback(self._eb_call_failed, name)
        
    def _send_response(self, response):
        if not response :
            response = "OK" 
        logging.getLogger().debug("response: %s" % (response))
        try:
            self.sendLine(response)
        except :
            logging.getLogger().error("UX resp send failed: %s"  % traceback.format_exc())


    def _eb_call_failed(self, failure, method_name):
        logging.getLogger().error("Method calling %s failed: %s" % (method_name, failure))

    def _lookup_procedure(self, name):
        this_class_dict = self.__class__.__mro__[0].__dict__
        method_matches = [f for (k, f) in this_class_dict.items() 
                                      if k == name and callable(f)]
        if len(method_matches)==1 :
            return method_matches[0]


class UNIXFactory(Factory):
    protocol = UnixProtocol

def chooseClientNetwork(target):
    return chooseClientIP({'uuid': target.getUUID(),
                           'fqdn': target.getFQDN(),
                           'shortname': target.getShortName(),
                           'ips': target.getIps(),
                           'macs': target.getMacs(),
                           'netmasks': target.getNetmasks()
                         })


def launcher_proxymethod(*options):
    """
    Decorator to share a decorated method with the scheduler-proxy 
    which is processing the incoming requests from launcher.
    """
    try:
    
        if len(options) == 1 and callable(options[0]) :
            # if only one option, this is a decorator without a parameter
            # so first parameter is decorated function
            fn = options[0]
            name = fn.__name__
            aliased = False
        else :
            # first argument supposed as alias 
            name = options[0]
            aliased = True


        def wrap(f, method_name=name):
            def inner(self, *args, **kwargs):
                # TODO - test if Phase instance
                if self._register_only :
                    if method_name not in self._proxy_methods :
                        self._proxy_methods[method_name] = f#(self, f)#(f, args, kwargs)

                else : 
                    return f(self, *args, **kwargs)

            inner.is_proxy_fnc = True
            return inner

        if not aliased :
            return wrap(fn, name)
        else :
            return wrap
    except Exception, e :
        logging.getLogger().error("launcher_proxymethod: %s"  % str(e))


class ProxyProcessProtocol(ProcessProtocol):

     def processExited(self, reason):
         logging.getLogger().warn("XML Proxy: Process exited: %s" % (reason.value.exitCode))
 
     def errReceived(self, data):
         logging.getLogger().warn("XMLRPC Proxy: STDERR: %s" % repr(data))
    
     def outConnectionLost(self, reason):
         logging.getLogger().info("XMLRPC Proxy: Connection lost: %s" % (reason.value.exitCode))
 
 
class SpawnProxy :
    def __init__(self, path):
         self.protocol = ProxyProcessProtocol()
         if isinstance(path, str):
             self.path = [path]
         else:
             self.path = path
  
    def run(self):
         return reactor.spawnProcess(self.protocol,
                                     self.path[0], 
                                     self.path, 
                                     env=None,
                                     childFDs={0 :"w", 
                                               1 :"r", 
                                               2:'r'}
                                    )
