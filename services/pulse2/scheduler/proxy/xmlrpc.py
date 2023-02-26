# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import xmlrpclib

from twisted.internet.defer import maybeDeferred
from twisted.web.xmlrpc import XMLRPC, Fault
from twisted.web.server import NOT_DONE_YET

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http # pyflakes.ignore

from pulse2.utils import xmlrpcCleanup


class ForwardingProxy(XMLRPC):
    """ XMLRPC Scheduler Proxy """

    def __init__(self, config):
        XMLRPC.__init__(self)
        self.logger = logging.getLogger()
        self.config = config

    def register_forwarder(self, forwarder):
        self.forwarder = forwarder

    def _ebRender(self, failure, request):
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
        try:
            request.write(s)
            if not request.finished :
                request.finish()
        except Exception, e :
            self.logger.debug("XMLRPC Proxy : request finish: %s" % str(e))



    def render(self, request):
        """ override method of xmlrpc python twisted framework """
        try :
            args, func_name = xmlrpclib.loads(request.content.read())
        except Exception, e:
            self.logger.error("xmlrpc render failed: %s"% str(e))

            return NOT_DONE_YET

        if not self._auth_validate(request, func_name, args):
            return NOT_DONE_YET

        d = maybeDeferred(self.forwarder.call_remote, request, func_name, args)
        d.addErrback(self._ebRender, func_name, args)

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
