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

import os
import random
import time
import Queue
import threading
import tempfile

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
"""
try:
    from twisted.trial.unittest import TestCase
except ImportError:
    from unittest import TestCase, main
"""
from unittest import TestCase, main

import ssl

from pulse2agent.connect import Connector, ClientEndpoint
from pulse2agent.connect import ConnectionTimeout, ConnectionRefused

PORT = 5556
HOST = 'localhost'

current_dir = os.sep.join((os.path.abspath(__file__)).split(os.sep)[:-1])
cert_dir = os.path.join(current_dir, "tls")

keyfile_server = os.path.join(cert_dir, "server.key")
crtfile_server = os.path.join(cert_dir, "server.crt")
keyfile_client = os.path.join(cert_dir, "client.key")
crtfile_client = os.path.join(cert_dir, "client.crt")
pemfile_root = os.path.join(cert_dir, "root.pem")

fail_keyfile_server = os.path.join(cert_dir, "failserver.key")
fail_crtfile_server = os.path.join(cert_dir, "failserver.crt")
fail_keyfile_client = os.path.join(cert_dir, "failclient.key")
fail_crtfile_client = os.path.join(cert_dir, "failclient.crt")
fail_pemfile_root = os.path.join(cert_dir, "failroot.pem")


class ConfigHelper(object):
    """A simple struct container"""
    host = HOST
    port = PORT
    keyfile = keyfile_client
    crtfile = crtfile_client
    timeout = 30


# -------------- Server helpers ----------------------------------

class SimpleSocketServer(object):
    """
    Provides a simple socket server.

    This instance built as context manager, allows to encapsulate
    server session with correct shotdown.
    """
    def __init__(self, host, port):

        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(1)

    def __enter__(self):
        return self.server

    def __exit__(self, type, value, traceback):
        self.server.close()

class SSLSocketServer(object):

    SHUTDOWN = "SHUTDOWN"

    handler = lambda x : x

    def __init__(self,
                 recv_queue,
                 send_queue,
                 crtfile,
                 keyfile,
                 pemfile,
                 ):
        """
        Starts a SSL server instance.

        When a packet received, puts them into the queue
        and terminates the service.

        @param recv_queue: queue to put received result
        @type recv_queue: Queue.Queue

        @param send_queue: queue to put the data to send
        @type send_queue: Queue.Queue

        @param keyfile: private key filename
        @type keyfile: str

        @param crtfile: certificate filename
        @type crtfile: str

        @param pemfile: PEM file path
        @type pemfile: str
        """
        self.recv_queue = recv_queue
        self.send_queue = send_queue

        self.crtfile = crtfile
        self.keyfile = keyfile
        self.pemfile = pemfile

        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        self.server.setblocking(1)

    def receive_put_into_queue_shutdown(self):
        result = self._receive()
        self.recv_queue.put(result)
        #self.shutdown()

    def loop(self):
        while True:
            result = self._receive()
            if result == self.SHUTDOWN:
                #self.shutdown()
                print "shutdown !!!!!!!!"
                break

            self.recv_queue.put(result)
            self.send_response()



    def _receive(self):
        client_connection, address = self.server.accept()
        if client_connection:
            ssl_client = ssl.wrap_socket(client_connection,
                   server_side=True,
                   certfile=self.crtfile,
                   keyfile=self.keyfile,
                   ca_certs=self.pemfile,
                   ssl_version=ssl.PROTOCOL_TLSv1
                   )
            result = ssl_client.read(1024)

            print "result received on SSL server: %s" % result
            return result


    def send_response(self):
        data = self.send_queue.get()
        if data is not None:
            time.sleep(1)
            print "sending data: %s" % data
            self.server.send(data)

    def shutdown(self):
        self.server.close()

def build_ssl_server(recv_queue, crtfile, keyfile, pemfile):
    server = SSLSocketServer(recv_queue, None, crtfile, keyfile, pemfile)
    server.receive_put_into_queue_shutdown()
    return server

def build_looped_ssl_server(recv_queue, send_queue, crtfile, keyfile, pemfile):
    server = SSLSocketServer(recv_queue, send_queue, crtfile, keyfile, pemfile)
    server.loop()
    return server




class Test00_Connector(TestCase):
    """Tests the socket connector using server helpers"""


    def test01_establish_and_verify_sent_data_nossl(self):
        """A simple echo test without SSL authentification"""

        with SimpleSocketServer(HOST, PORT) as server:
            # establish a client connection
            connector = Connector(HOST, PORT)
            client_sock = connector.connect()

            client_sock.sendall("something")

            # server side
            client_connection, address = server.accept()
            # client_connection - client's socket on server side
            if client_connection:
                result = client_connection.recv(1024)
                client_connection.close()
                # compare with sent data
                self.assertEqual(result, "something")

            client_sock.close()




    def test02_establish_and_verify_sent_data_ssl(self):
        """A simple echo test with SSL authentification"""

        # result queue
        queue = Queue.Queue()
        # starting the server in a thread
        t = threading.Thread(target=build_ssl_server,
                             args=(queue,
                                   crtfile_server,
                                   keyfile_server,
                                   pemfile_root,
                                   )
                             )
        t.start()

        # client connection
        connector = Connector(HOST,
                              PORT,
                              keyfile_client,
                              crtfile_client,
                              )
        client_sock = connector.connect()
        # sending some data
        client_sock.sendall("something")
        # geting the data received on server
        result = queue.get()
        self.assertEqual(result, "something")

        client_sock.close()

    def test03_connection_refused(self):
        """ Test for catch ConnectionRefused exception. """


        connector = Connector(HOST,
                              PORT,
                              keyfile_client,
                              crtfile_client,
                              )

        self.assertRaises(ConnectionRefused, connector.connect)


    def test04_nossl_server_timeout_raise(self):
        """Try to serve no SSL service to SSL client"""

        timeout = 2

        with SimpleSocketServer(HOST, PORT):

            # client connection
            connector = Connector(HOST,
                                  PORT,
                                  keyfile_client,
                                  crtfile_client,
                                  timeout,
                                  )
            # because client is truing to connect to a server
            # without SSL authentification, client 2 seconds after
            # raises ConnectionTimeout exception
            self.assertRaises(ConnectionTimeout, connector.connect)


    def test05_unknown_ssl_server_timeout_raise(self):
        # result queue
        queue = Queue.Queue()
        # starting the server in a thread
        t = threading.Thread(target=build_ssl_server,
                             args=(queue,
                                   fail_crtfile_server,
                                   fail_keyfile_server,
                                   fail_pemfile_root,
                                   )
                             )
        t.start()

        # client connection
        connector = Connector(HOST,
                              PORT,
                              keyfile_client,
                              crtfile_client,
                              )
        client_sock = connector.connect()
        # sending some data
        client_sock.sendall("something")
        # geting the data received on server
        result = queue.get()
        print "test5 result: %s" % result
        self.assertEqual(result, "something")

        client_sock.close()


class Test01_ClientEndpoint(TestCase):

    def setUp(self):
        self.config = ConfigHelper()


    def test01_simply_send_receive_ssl(self):

        queue = Queue.Queue()
        t = threading.Thread(target=build_ssl_server,
                             args=(queue,
                                   crtfile_server,
                                   keyfile_server,
                                   pemfile_root,
                                   )
                             )
        t.start()
        # give a little lag to establish the server
        time.sleep(1)

        endpoint = ClientEndpoint(self.config)
        endpoint.request("my_data")

        result = queue.get()
        self.assertEqual(result, "my_data")

        endpoint.close()
        time.sleep(1)

    def test02_exchange_some_data_ssl(self):

        recv_queue = Queue.Queue()
        send_queue = Queue.Queue()

        t = threading.Thread(target=build_looped_ssl_server,
                             args=(recv_queue,
                                   send_queue,
                                   crtfile_server,
                                   keyfile_server,
                                   pemfile_root,
                                   )
                             )
        t.start()
        # give a little lag to establish the server
        #time.sleep(1)
        send_queue.put("another_data")

        endpoint = ClientEndpoint(self.config)
        response = endpoint.request("my_data")
        time.sleep(1)

        #request = recv_queue.get()
        #self.assertEqual(request, "my_data")


        self.assertEqual(response, "another_data")


        send_queue.put("SHUTDOWN")

        endpoint.close()



if __name__ == '__main__':

    if TestCase.__module__ != "twisted.trial.unittest" :
        main()
