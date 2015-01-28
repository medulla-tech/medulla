# -*- test-case-name: pulse2.msc.client.tests.connect -*-
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


import socket
import ssl
import logging

from parse import Parser
from pexceptions import ConnectionError

class ConnectorException(Exception):
    """A general exception wrapper for client-side errors"""
    def __init__(self, host, port):
        self.host = host
        self.port = port


class ConnectionRefused(ConnectorException):
    """An exception to raise when connection refused from other side"""
    def __repr__(self):
        return "Connection on server %s:%s refused" % (self.host, self.port)


class UnknownService(ConnectorException):
    """An exception to raise when trying contact unable service """
    def __repr__(self):
        return "Unknown service %s:%s. Connection refused" % (self.host, self.port)


class ConnectionTimeout(ConnectorException):
    """An exception to raise when a timeout of connection checked"""
    def __repr__(self):
        return "Timeout of connection to server %s:%s" % (self.host, self.port)



class Connector(object):
    """Provides a simple or SSL secured connection to server."""

    context = None

    def __init__(self, host, port=8443, enablessl=True, crtfile=None, timeout=30):
        """
        @param host: name or IP address of server
        @type host: str

        @param port: port of server
        @type port: int

        @param enablessl: SSL activation flag
        @type enablessl: bool

        @param crtfile: client SSL certificate file path
        @type crtfile: str

        @param timeout: timeout of client connection
        @type timeout: int
        """
        self.logger = logging.getLogger()
        self.host = host
        self.port = port
        self.timeout = timeout

        self.crtfile = crtfile
        self.ssl_enabled = enablessl


    def connect(self):
        """
        Provides a socket connection to server.

        @return: established socket
        @rtype: socket or socket wrapped by SSL context
        """

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(self.timeout)
            if self.ssl_enabled:
                ssl_sock = ssl.wrap_socket(sock,
                                           ssl_version=ssl.PROTOCOL_SSLv3,
                                           )

                ssl_sock.setblocking(True)

                ssl_sock.connect((self.host, self.port))
                ssl_sock.do_handshake()

                return ssl_sock
            else:

                sock.connect((self.host, self.port))
                sock.settimeout(self.timeout)
                return sock

        except socket.gaierror, (code, message):
            if code == -2:
                raise UnknownService(self.host, self.port)


        except socket.error, (code, message):
            if code == 111:
                raise ConnectionRefused(self.host, self.port)

            else:
                self.logger.debug("Another connection error:", code, message)



        except Exception, e:
            self.logger.debug("Client connection failed: %s" % str(e))
            import traceback
            self.logger.debug("\033[31m%s\033[0m" % str(traceback.format_exc()))


class ClientEndpoint(object):

    socket = None
    parser = None

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.connector = Connector(config.server.host,
                                   config.server.port,
                                   config.server.enablessl,
                                   config.server.crtfile,
                                   config.server.timeout,
                                   )
        self.parser = Parser(config.main.serializer)


    def connect(self):
        self.socket = self.connector.connect()

    def request(self, data):

        pack = self.parser.encode(data)

        try:
            self.socket.sendall(pack)
            response = self.socket.read(1024)
        except Exception, e:
            self.logger.warn("Request failed: %s" % str(e))
            raise ConnectionError(self.connector.host)

        try:
            return self.parser.decode(response)
        except ValueError, e:
            self.logger.warn("Decoding of request failed: %s" % str(e))
            raise ConnectionError(self.connector.host)

    def _recv(self, n=1):
        data = ""
        chunk = ""
        while len(data) < n:
            try:
                chunk = self.socket.recv(n - len(data))
                #chunk = self.socket.read(n - len(data))
            except Exception, e:
                self.logger.debug("SSL read failed: %s" % str(e))

            if len(chunk) == 0:
                break
            data += chunk
        self.logger.debug("\033[33mdata: %s\033[0m" % str(data))
        return data

    def close(self):
        if self.socket is not None:
            self.socket.close()

    def __del__(self):
        self.close()


def probe(host, port):
    """
    A simple check of connectivity on host:port

    @param host: name or IP address of server
    @type host: str

    @param port: port of server
    @type port: int
    """
    try:
        socket.socket().connect((host, port))
        return True
    except:
        return False

