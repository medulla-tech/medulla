import xmlrpclib

import twisted.web.xmlrpc
import twisted.web.server

import twisted.internet.defer
import twisted.internet.reactor

import logging

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http

class P2PServerService(twisted.web.xmlrpc.XMLRPC):
    def __init__(self, config, root):
        twisted.web.xmlrpc.XMLRPC.__init__(self)
        self.config = config
        self.logger = logging.getLogger()
        self.paths = {}
        self.root_path = root

    def _ebRender(self, failure):
        self.logger.error(failure)
        if isinstance(failure.value, xmlrpclib.Fault):
            return failure.value
        return xmlrpclib.Fault(self.FAILURE, "Internal Error on launcher ")

    def _cbRender(self, result, request, name, type):
        args, func = xmlrpclib.loads(request.content.getvalue())
        if isinstance(result, P2PServerService):
            result = mmc.support.mmctools.xmlrpcCleanup(result.result)
        if not isinstance(result, xmlrpclib.Fault):
            result = (result,)
        self.logger.debug('xmlrpc:(%s)%s %s%s => %s' % (type, name, func, (args), (result)))
        try:
            s = xmlrpclib.dumps(result, methodresponse=1)
        except:
            f = xmlrpclib.Fault(self.FAILURE, "can't serialize output")
            s = xmlrpclib.dumps(f, methodresponse=1)
        request.setHeader("content-length", str(len(s)))
        request.write(s)
        request.finish()

    def register(self, obj, path):
        if self.paths.has_key(path):
            self.logger.error("path %s is already registered, check your config file"%(path))
            return False
        self.paths[path] = obj
        return True

    def registerRoot(self, obj):
        self.root_path = obj

    def render(self, request):
        """
        override method of xmlrpc python twisted framework
        """
        headers = request.getAllHeaders()
        content = request.content.read()
        args, functionPath = xmlrpclib.loads(content)

        path = functionPath.split('.')
        func = path.pop()
        functionPath = '.'.join(path)

        obj = self.root_path
        if self.paths.has_key("/"+request.postpath[0]):
            obj = self.paths["/"+request.postpath[0]]

        if functionPath != 'xmlrpc': # TODO raise an exception ?
            return twisted.web.server.NOT_DONE_YET

        function = obj._getFunction(func)

        cleartext_token = '%s:%s' % (self.config.username, self.config.password)
        token = '%s:%s' % (request.getUser(), request.getPassword())
        if token != cleartext_token:
            self.logger.error("Invalid login / password for HTTP basic authentication")
            request.setResponseCode(http.UNAUTHORIZED)
            self._cbRender(
                twisted.web.xmlrpc.Fault(http.UNAUTHORIZED, "Unauthorized: invalid credentials to connect to this P2PServerService, basic HTTP authentication is required"),
                request
                )
            return twisted.web.server.NOT_DONE_YET

        request.setHeader("content-type", "text/xml")
        twisted.internet.defer.maybeDeferred(function, *args).addErrback(
            self._ebRender
        ).addCallback(
            self._cbRender, request, obj.name, obj.type
        )
        return twisted.web.server.NOT_DONE_YET

