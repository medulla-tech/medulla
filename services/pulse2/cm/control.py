# -*- test-case-name: pulse2.cm.tests.control -*-
# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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

from twisted.internet.defer import DeferredList

from pulse2.cm.parse import Parser
from pulse2.cm.server import Server
from pulse2.cm.collector import Collector
from pulse2.cm.trigger import Trigger
from pulse2.cm.endpoints import Endpoint
from pulse2.cm.endpoints import PackagesEndpoint
from pulse2.cm.endpoints import InventoryServerEndpoint
from pulse2.cm.endpoints import VPNInstallEndpoint


class MethodNotFound(Exception):
    """ Unexisting method in an inherited endpoint """
    def __repr__(self):
        return "Method %s not found" % repr(self.message)


class MethodWithoutPrefix(Exception):
    """ Method without a necessary prefix """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Method %s without prefix" % repr(self.name)


class RequestExtractor(object):
    """
    Extracts a request received from client.

    Description of format of request:
    Received as tuple containing a global method identifier and its parameters,
    method extract() returns a ready
    """
    DELIMITER = "."
    args_types_allowed = [str, tuple, list, dict]


    def extract(self, _request):
        request = eval(_request)
        if isinstance(request, list) or isinstance(request, tuple):
            if len(request) == 2:
                t_method, args = request
                prefix, method = self._extract_method(t_method)
                args = self._validate_args(args)
                return prefix, method, args
            else:
                raise IndexError("Expected number of elements in request: 2")
        else:
            #print request, type(request)
            raise TypeError("Invalid request format")


    def _extract_method(self, text):
        if isinstance(text, str):
            if self.DELIMITER in text:
                # allowed only one delimiter
                # i.e.: pkgs.get_package
                if text.count(self.DELIMITER) == 1:
                    # returns a prefix of endpoint and a method identifier
                    return text.split(self.DELIMITER)
                else:
                    raise IndexError("Not allowed more than one method delimiter %s" % text)
            else:
                raise MethodWithoutPrefix(text)
        else:
            raise TypeError("Invalid format of method identifier, <str> type expected")

    def _validate_args(self, args):
        if isinstance(args, str):
            return [args]
        for args_type in self.args_types_allowed:
            if isinstance(args, args_type):
                return args
        else:
            raise TypeError("Invalid format of args; one of <%s> expected" % repr(self.args_types_allowed))


class EndpointsRoot(object):

    endpoints = []
    rqex = RequestExtractor()
    parser = Parser()
    collector = None

    def __init__(self, collector):
        self.collector = collector
        self.logger = logging.getLogger()



    def register(self, endpoint):
        if isinstance(endpoint, Endpoint):
            self.endpoints.append(endpoint)
        else:
            raise TypeError("Not a Endpoint type")

    def do_calls(self):

        dl = []

        while True:
            line = self.collector.get()
            if line is None:
                break

            uid, ip, request = line
            d = self.call(request, from_ip=ip)
            d.addCallback(self._reply, uid)
            @d.addErrback
            def _eb(failure):
                self.logger.warn("\033[31mRequest call failed: %s\033[0m" % str(failure))
            dl.append(d)

        return DeferredList(dl)


    def _reply(self, result, uid):
        self.logger.debug("\033[34mResult for session uid: %d: %s\033[0m" % (uid, str(result)))
        self.collector.release(uid, self.parser.encode(result))


    def call(self, request, from_ip):

        prefix, method, args = self.rqex.extract(request)

        for endpoint in self.endpoints:
            if endpoint.prefix == prefix:
                return endpoint.call_method(method, args, from_ip)
        else:
            raise MethodNotFound(method)





class Dispatcher(object):
    """
    Common point providing the cooperation between gateway and endpoints.

    Gateway as producer puts the received requests into a queue and launches
    the getters of endpoints (consumers) by linked trigger.
    Each endpoint may forward incoming request, store them into a database,
    or just treat each incoming request, where for all types of endpoints,
    a result is always returned to producer to pass them to client.
    """
    endpoints = [PackagesEndpoint,
                 InventoryServerEndpoint,
                 VPNInstallEndpoint,
                 ]

    endpoints_root = None
    collector = None

    def __init__(self, config):
        """
        @param config: Configuration container
        @type config: Config
        """
        self.config = config
        self.logger = logging.getLogger()

        self.server = Server(config.server.port,
                             config.server.ssl_key_file,
                             config.server.ssl_crt_file,
                             config.server.ssl_method,
                             )
        self.collector = Collector()
        self.endpoints_root = EndpointsRoot(self.collector)

        self.endpoints_lookup = config.server.endpoints


    def _start_server(self):
        """
        Starts the gateway instance.

        @return: endpoint port instance
        @rtype: Deferred
        """

        trigger = Trigger(self.endpoints_root.do_calls)

        d = self.server.start(self.collector, trigger)
        d.addCallback(self._connect_endpoints)
        d.addErrback(self._eb_start_failed)

        return d

    def _connect_endpoints(self, reason):
        """
        Installs the endpoints consuming the requests from gateway.

        """
        for endpoint in self.endpoints:
            if endpoint.prefix in self.endpoints_lookup:
                self.logger.info("Registering '%s' endpoint" % endpoint.prefix)
                self.endpoints_root.register(endpoint(self.config))



    def _eb_start_failed(self, failure):
        self.logger.warn("\033[31mStart server failed: %s\033[0m" % str(failure))



    def run(self):

        d = self._start_server()
        return d

if __name__ == "__main__":

    import sys
    from mmc.core.log import ColoredFormatter
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    hdlr2 = logging.StreamHandler(sys.stdout)
    hdlr2.setFormatter(ColoredFormatter("%(levelname)-18s %(message)s"))
    logger.addHandler(hdlr2)

    from twisted.internet import reactor
    from pulse2.cm.config import Config



    config = Config()
    dp = Dispatcher(config)
    dp.run()

    reactor.run()

