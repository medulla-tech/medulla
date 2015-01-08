# -*- test-case-name: pulse2.cm.tests.server -*-
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

from twisted.internet import reactor

from twisted.internet.endpoints import SSL4ServerEndpoint
from twisted.internet.ssl import DefaultOpenSSLContextFactory
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.address import IPv4Address



class GatheringServer(Protocol):
    """
    This service dispatches the communication between server and clients.

    The client machines sends periodically several informations
    to this server where gathered info is forwarded to the handler.
    The handler reference (a service processing received data)
    returns a result which is immediatelly sent to the client.
    """

    _handler = None
    _trigger = None

    @classmethod
    def set_handler(self, value):
        if hasattr(value, "queue_and_process"):
            self._handler = value
        else:
            raise AttributeError, "Handler instance must have 'queue_and_process' attribute"

    @classmethod
    def set_trigger(self, value):
        if hasattr(value, "fire"):
            self._trigger = value
        else:
            raise AttributeError, "Handler instance must have 'fire' attribute"



    def dataReceived(self, data):
        """
        Method invoked when any data received.

        @param data: received data
        @type data: str
        """
        address = self.transport.getPeer()

        if isinstance(address, IPv4Address):
            ip = address.host
        else:
            ip = None

        d = self._handler.queue_and_process(ip, data)
        d.addCallback(self.send_response)
        d.addErrback(self._response_failed)


        logging.getLogger().debug("data received: %s from %s" % (str(data), ip))
        try:
            tr_result = self._trigger.fire()
            @tr_result.addCallback
            def res(result):
                print "trigger result: %s" % (str(result))
        except Exception, e:
            logging.getLogger().warn("trigger firing fail: %s" % str(e))



    def send_response(self, response):
        logging.getLogger().debug("response to client: %s" % str(response))
        self.transport.write(response)

    def _response_failed(self, failure):
        logging.getLogger().warn("response failed: %s" % str(failure))


class GatheringFactory(Factory):
    protocol = GatheringServer

class Server(object):
    def __init__(self, port, key, crt, ssl_method):
        """
        @param port: port to listen
        @type port: int

        @param key: private key filename
        @type key: str

        @param crt: certificate filename
        @type crt: str

        @param ssl_method: SSL method
        @type: str
        """
        self.port = port
        if ssl_method == "TLSv1_METHOD":
            from OpenSSL.SSL import TLSv1_METHOD
            ssl_method = TLSv1_METHOD
        elif ssl_method == "SSLv23_METHOD":
            from OpenSSL.SSL import SSLv23_METHOD
            ssl_method = SSLv23_METHOD
        elif ssl_method == "SSLv2_METHOD":
            from OpenSSL.SSL import SSLv2_METHOD
            ssl_method = SSLv2_METHOD
        elif ssl_method == "SSLv3_METHOD":
            from OpenSSL.SSL import SSLv3_METHOD
            ssl_method = SSLv3_METHOD
        else:
            raise TypeError


        self.ctx_factory = DefaultOpenSSLContextFactory(key,
                                                        crt,
                                                        ssl_method
                                                        )


    def start(self, handler, trigger):

        self.factory = GatheringFactory()

        self.factory.protocol.set_handler(handler)
        self.factory.protocol.set_trigger(trigger)

        endpoint = SSL4ServerEndpoint(reactor,
                                      self.port,
                                      self.ctx_factory)

        d = endpoint.listen(self.factory)

        @d.addCallback
        def cb(reason):
            logging.getLogger().info("endpoint start: %s" % str(reason))
        @d.addErrback
        def eb(failure):
            logging.getLogger().warn("endpoint start failed: %s" % str(failure))


        return d

# for TLS:
# openssl genrsa -out root.key 4096
# openssl req -x509 -new -nodes -key root.key -days 1024 -out root.pem
# openssl genrsa -out server.key 4096
# openssl genrsa -out client.key 4096
# openssl req -new -key server.key -out server.csr
# openssl req -new -key client.key -out client.csr
# openssl x509 -req -in server.csr -CA root.pem -CAkey root.key -CAcreateserial -out server.crt -days 1023
# openssl x509 -req -in client.csr -CA root.pem -CAkey root.key -CAcreateserial -out client.crt -days 1023


