#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
A mixin of UDP and TCP server listening on the same port.

This proxy communicate with PXE imaging client using a custom protocol.
"""


import logging
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from pulse2.package_server.imaging.pxe.api import PXEImagingApi


class ProcessPacket:
    """Common packet processing"""

    config = None
    api = None

    @classmethod
    def set_imaging_args(cls, config, api):
        """
        Classmethod to pass some references

        @param config: config container
        @type config: PackageServerConfig

        @param api: Imaging API
        @type api: ImagingAPI
        """
        cls.api = api
        cls.config = config
        logging.getLogger().debug("PXE Proxy: UDP proxy initialized")

    def method_exec(self, imaging, method, args):
        """
        Method execution call

        @param imaging: interface to execute PXE methods
        @type imaging: PXEImagingApi

        @param method: method to execute
        @type method: func

        @param args: arguments of executed method
        @type args: list

        @return:  executed method
        @rtype: deferred
        """
        return method(imaging, *args)

    def xmpp_process(self, data, client=None):
        """
        Processus XMPP.

        Cette fonction traite les données reçues via XMPP.

        @param data: Les données reçues.
        @type data: str

        @param client: Tuple représentant l'adresse du client (hôte, port).
        @type client: tuple

        @return: False si la chaîne est vide ou si le premier octet est 0xBB ou 0xBA, True sinon.
        @rtype: bool
        """
        logging.getLogger().debug("PXE Proxy: self.config: %s " % self.config)
        logging.getLogger().debug("PXE Proxy: method: %s " % data)
        dataf = data[:]
        if not data:
            return False
        first_byte = ord(dataf.decode("utf-8")[0])
        if first_byte == 0xBB:
            imaging = PXEImagingApi(self.config)
            imaging.set_api(self.api)
            fnc, args = imaging.get_method(data)
            result = self.method_exec(imaging, fnc, args)
            return False
        return True

    def process_data(self, data, client=None):
        """
        Called when a packet received.

        @param data: packet
        @type data: str

        @param client: client (host, port) tuple
        @type client: tuple
        """
        # For each session a new instance of PXEImagingApi created
        if not self.xmpp_process(data, client):
            return False

        imaging = PXEImagingApi(self.config)
        imaging.set_api(self.api)

        fnc, args = imaging.get_method(data)

        d = self.method_exec(imaging, fnc, args)

        d.addCallback(self.send_response, fnc, client)
        d.addErrback(self.on_exec_error)

        return d

    def send_response(self, result, fnc, client=None):
        """
        Sending the result of executed method to client.

        @param result: data returned by executed method
        @type result: string

        @param client: tuple of (host, port)
        @type client: tuple
        """
        if result:
            data = bytes(result + "\x00", "utf-8")
            try:
                if client:
                    self.transport.write(data, client)  # UDP response
                else:
                    self.transport.write(data)  # TCP response
                if client:
                    ip, port = client
                    logging.getLogger().debug(
                        "PXE Proxy: method: %s / response sent: %s on %s:%d"
                        % (fnc.__name__, str(data), ip, port)
                    )
                else:
                    logging.getLogger().debug(
                        "PXE Proxy: method: %s / response sent: %s"
                        % (fnc.__name__, str(data))
                    )

            except Exception as e:
                logging.getLogger().warn(
                    "PXE Proxy: send response error: %s" % (str(e))
                )

        return result

    def on_exec_error(self, failure):
        logging.getLogger().warn("PXE Proxy: send response error: %s" % str(failure))
        return failure


class UDPProxy(ProcessPacket, DatagramProtocol):
    """Proxy to processing a major part of methods"""

    def datagramReceived(self, data, client):
        # special case for GLPI :
        # add the IP address of client as a next argument
        ip, port = client
        logging.getLogger().debug("PXE Proxy: packet received from: %s" % ip)
        data += bytes("\nIPADDR:%s:0" % ip, "utf-8")
        self.process_data(data, client)


class TCPProxy(ProcessPacket, Protocol):
    """Proxy to processing methods of backup"""

    def dataReceived(self, data):
        self.process_data(data)


class PXEProxy:
    def __init__(self, config, api):
        pxe_port = config.imaging_api["pxe_port"]

        udp = UDPProxy()
        udp.set_imaging_args(config, api)

        reactor.listenUDP(pxe_port, udp)

        tcp = Factory()
        tcp.protocol = TCPProxy
        tcp.protocol.set_imaging_args(config, api)

        reactor.listenTCP(pxe_port, tcp)
