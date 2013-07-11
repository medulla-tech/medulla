#!/usr/bin/python 
# -*- coding: utf-8; -*-
"""
"""
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
A mixin of UDP and TCP server listening on the same port.

This proxy communicate with PXE imaging client using a custom protocol.
"""

import logging

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from pulse2.package_server.imaging.pxe.api import PXEImagingApi


class ProcessPacket :
    """Common packet processing"""

    imaging = None

    @classmethod
    def set_imaging(cls, imaging):
        """
        @param imaging: imaging interface to execute methods on package server
        @type imaging: object
        """
        cls.imaging = imaging
        logging.getLogger().debug("PXE Proxy: UDP proxy initialized")

    def method_exec(self, method, args):
        """
        Method execution call

        @param method: method to execute
        @type method: func

        @param args: arguments of executed method
        @type args: list

        @return:  executed method
        @rtype: deferred
        """
        return method(self.imaging, *args)


    def process_data (self, data, client=None):

        fnc, args = self.imaging.get_method(data)
        
        try:
            marker = hex(ord(data[0]))
        except Exception, e:
            logging.getLogger().warn("PXE Proxy: Marker getting: %s" % (str(e)))

        d = self.method_exec(fnc, args)

        d.addCallback(self.send_response, client)
        d.addErrback(self.on_exec_error)

        return d


    def send_response(self, result, client=None):
        """
        Sending the result of executed method to client.

        @param result: data returned by executed method
        @type result: string

        @param client: tuple of (host, port)
        @type client: tuple
        """
        data = bytes(result)
        logging.getLogger().debug("PXE Proxy: send response: %s" % str(data))

        try :
            if client :
                self.transport.write(data, client) # UDP response
            else :
                self.transport.write(data)         # TCP response

        except Exception, e:
            logging.getLogger().warn("PXE Proxy: send response error: %s" % (str(e)))

        return result


    def on_exec_error(failure):
        logging.getLogger().warn("PXE Proxy: send response error: %s" % str(failure))
        return failure


class UDPProxy(ProcessPacket, DatagramProtocol):
    """Proxy to processing a major part of methods"""
    def datagramReceived(self, data, client):
        # special case for GLPI :
        # add the IP address of client as a next argument
        ip, port = client
        data += "IPADDR:%s\n" % ip
        self.process_data(data, client)


class TCPProxy(ProcessPacket, Protocol):
    """Proxy to processing methods of backup"""
    def dataReceived(self, data):
        self.process_data(data)


class PXEProxy :

    def __init__(self, config, api):

        imaging = PXEImagingApi(config)
        imaging.set_api(api)
        
        pxe_port = config.imaging_api["pxe_port"]

        udp = UDPProxy()
        udp.set_imaging(imaging)

        reactor.listenUDP(pxe_port, udp)

        tcp = Factory()
        tcp.protocol = TCPProxy
        tcp.protocol.set_imaging(imaging)

        reactor.listenTCP(pxe_port, tcp)

    



