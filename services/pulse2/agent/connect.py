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

from parse import Parser

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

    #def __init__(self, host, port=443, keyfile=None, crtfile=None, timeout=30):
    def __init__(self, host, port=443, crtfile=None, timeout=30):
        """
        @param host: name or IP address of server
        @type host: str

        @param port: port of server
        @type port: int

        @param keyfile: client SSL key file path
        @type keyfile: str

        @param crtfile: client SSL certificate file path
        @type crtfile: str

        @param timeout: timeout of client connection
        @type timeout: int
        """
        self.host = host
        self.port = port
        self.timeout = timeout

        self.crtfile = crtfile
    ssl_enabled = True


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

                #tm = struct.pack('LL',
                #                 int(self.timeout),
                #                 int(self.timeout - int(self.timeout))* 1e6
                #                 )
                #ssl_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, tm)
                #ssl_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, tm)
                ssl_sock.setblocking(True)

                ssl_sock.connect((self.host, self.port))
                ssl_sock.do_handshake()

                print "RCV timeout set to %s"  % ssl_sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO)
                print "SND timeout set to %s"  % ssl_sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO)
                print ssl_sock.getpeercert()

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
                # TODO - remove this !!!
                print "Another error:", code, message



        except Exception, e:
            print "\033[31mClient connection failed: %s\033[0m" % str(e)
            import traceback
            print "\033[31m%s\033[0m" % str(traceback.format_exc())


class ClientEndpoint(object):

    socket = None
    parser = None

    def __init__(self, config):
        connector = Connector(config.server.host,
                              config.server.port,
                              #config.server.keyfile,
                              config.server.crtfile,
                              config.server.timeout,
                              )
        self.socket = connector.connect()
        self.parser = Parser(config.main.serializer)


    def request(self, data):

        pack = self.parser.encode(data)

        self.socket.sendall(pack)
        #self.socket.write(pack)
        response = self.socket.read(1024)
        return self.parser.decode(response)
        #return self.parser.decode(self.socket.read(1024))

        #return self.parser.decode(self._recv())

    def _recv(self, n=1):
        data = ""
        chunk = ""
        while len(data) < n:
            try:
                chunk = self.socket.recv(n - len(data))
                #chunk = self.socket.read(n - len(data))
            except Exception, e:
                print "SSL read failed: %s" % str(e)

            if len(chunk) == 0:
                break
            data += chunk
        print "\033[33mdata: %s\033[0m" % str(data)
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

