#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from twisted.web import server, xmlrpc
import xmlrpc.client
import time
from twisted.internet import defer
from twisted.web.xmlrpc import XMLRPC, Handler

Fault = xmlrpc.client.Fault


class MyXmlrpc(XMLRPC):
    def __init__(self):
        self.mp = ""
        XMLRPC.__init__(self)

    def render(self, request):
        """
        override method of xmlrpc python twisted framework

        @param request: raw request xmlrpc
        @type request: xml str

        @return: interpreted request
        """
        args, functionPath = xmlrpc.client.loads(request.content.read())

        function = getattr(self, "xmlrpc_%s" % (functionPath))
        request.setHeader("content-type", "text/xml")

        start = time.time()

        def _printExecutionTime(start):
            self.logger.debug("Execution time: %f" % (time.time() - start))

        def _cbRender(result, start, request, functionPath=None, args=None):
            _printExecutionTime(start)
            s = request.getSession()
            if result is None:
                result = 0
            if isinstance(result, Handler):
                result = result.result
            if not isinstance(result, Fault):
                result = (result,)
            try:
                self.logger.debug(
                    "Result for " + str(functionPath) + ": " + str(result)
                )
                s = xmlrpc.client.dumps(result, methodresponse=1)
            except Exception as e:
                f = Fault(self.FAILURE, "can't serialize output: " + str(e))
                s = xmlrpc.client.dumps(f, methodresponse=1)
            request.setHeader("content-length", str(len(s)))
            if isinstance(s, str):
                s = s.encode("utf-8")
            request.write(s)
            request.finish()

        def _ebRender(failure, start, functionPath, args, request):
            _printExecutionTime(start)
            self.logger.error(
                "Error during render " + functionPath + ": " + failure.getTraceback()
            )
            # Prepare a Fault result to return
            result = {}
            result["faultString"] = functionPath + " " + str(args)
            result["faultCode"] = str(failure.type) + ": " + str(failure.value) + " "
            result["faultTraceback"] = failure.getTraceback()
            return result

        def _cbLogger(result, request):
            """Logging the HTTP requests"""

            host = request.getHost().host
            method = request.method
            uri = request.uri
            args = request.args

            message = "HTTP request from %s%s method: %s with arguments: %s"
            message = message % (host, uri, method, str(args))

            self.logger.debug(message)

        self.logger.debug(
            "RPC method call for %s.%s%s" % (self.mp, functionPath, str(args))
        )
        defer.maybeDeferred(function, *args).addErrback(
            _ebRender, start, functionPath, args, request
        ).addCallback(_cbRender, start, request, functionPath, args).addCallback(
            _cbLogger, request
        )
        return server.NOT_DONE_YET
