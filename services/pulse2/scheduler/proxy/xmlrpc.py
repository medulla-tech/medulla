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
import xmlrpclib


from twisted.web.xmlrpc import XMLRPC, Fault
from twisted.web.server import NOT_DONE_YET

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http # pyflakes.ignore

from pulse2.utils import xmlrpcCleanup

from pulse2.scheduler.config import SchedulerConfig


class ForwardingProxy(XMLRPC):
    """ XMLRPC Scheduler Proxy """

    def __init__(self, config):
        XMLRPC.__init__(self)
        self.logger = logging.getLogger()
        self.config = config

    def register_forwarder(self, forwarder):
        self.forwarder = forwarder

    def _ebRender(self, failure, func, args):
        self.logger.error("XMLRPC Proxy : %s" % str(failure))
        if isinstance(failure.value, xmlrpclib.Fault):
            return failure.value
        return xmlrpclib.Fault(self.FAILURE, "Internal Error")

    def client_response(self, result, request, func, args):
        
        if request :
            request.setHeader("content-type", "text/xml")
            return self._cbRender(result, request, func, args)


    def _cbRender(self, result, request, func, args):
        if isinstance(result, ForwardingProxy):
            result = xmlrpcCleanup(result.result)
        if not isinstance(result, xmlrpclib.Fault):
            result = (result,)
        self.logger.debug('xmlrpc: %s%s => %s' % (func, (args), (result)))

        try:
            s = xmlrpclib.dumps(result, methodresponse=1)
        except:
            f = xmlrpclib.Fault(self.FAILURE, "can't serialize output")
            s = xmlrpclib.dumps(f, methodresponse=1)
        request.setHeader("content-length", str(len(s)))
        request.write(s)
        request.finish()

    

    def render(self, request):
        """ override method of xmlrpc python twisted framework """
        args, func_name = xmlrpclib.loads(request.content.read())

        if not self._auth_validate(request, func_name, args):
            return NOT_DONE_YET
        self.forwarder.call_remote(request, func_name, args)

        return NOT_DONE_YET

    def _auth_validate(self, request, func_name, args):
        cleartext_token = '%s:%s' % (self.config.username, 
                                     self.config.password)
        token = '%s:%s' % (request.getUser(), 
                           request.getPassword())
        if token != cleartext_token:
            self.logger.error("Invalid login / password for HTTP basic authentication")
            request.setResponseCode(http.UNAUTHORIZED)
            self._cbRender(Fault(http.UNAUTHORIZED, 
                                 "Unauthorized: invalid credentials to connect to this Pulse 2 Scheduler Proxy, basic HTTP authentication is required"),
                           request,
                           func_name,
                           args
                          )
            return False
        else :
            return True

