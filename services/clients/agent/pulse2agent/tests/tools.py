import os
import ssl
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR


from pulse2agent.connect import Connector

PORT = 5555
HOST = 'localhost'
current_dir = os.sep.join((os.path.abspath(__file__)).split(os.sep)[:-1])
cert_dir = os.path.join(current_dir, "tls")

keyfile_server = os.path.join(cert_dir, "server.key")
crtfile_server = os.path.join(cert_dir, "server.crt")
keyfile_client = os.path.join(cert_dir, "client.key")
crtfile_client = os.path.join(cert_dir, "client.crt")
pemfile_root = os.path.join(cert_dir, "root.pem")


class Runner(object):
    def __init__(self):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((HOST, PORT))
        #self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.listen(5)
        #print self.server

        client, address = self.server.accept()
        if client:
            ssl_client = ssl.wrap_socket(client,
                       server_side=True,
                       certfile=crtfile_server,
                       keyfile=keyfile_server,
                       ca_certs=pemfile_root,
                       ssl_version=ssl.PROTOCOL_TLSv1
                       )
            result = ssl_client.read()
            print result
            ssl_client.write(result)
            time.sleep(1)
            #ssl_client.shutdown(SHUT_RDWR)
            ssl_client.close()

#            result = client.recv(1024)
#            print "result of client(%s): %s" % (str(address), str(result))
#            client.sendall(result)
#            client.close()

            self.server.close()

Runner()



