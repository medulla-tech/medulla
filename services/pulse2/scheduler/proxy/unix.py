# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientCreator

from pulse2.scheduler.utils import PackUtils
from pulse2.scheduler.proxy.buffer import SendingBuffer


class Sender(Protocol):

    send_locked = False
    request = None
    func_name = None
    args = None

    def call_remote(self, pack):
        try :
            self.transport.write(pack)
        except Exception, e:
            logging.getLogger().error("\033[31mux call failed: %s\033[0m" % str(e))

        self.send_locked = True

    @classmethod
    def register_response_handler(cls, handler):
        cls.response = handler

    def dataReceived(self, packet):
        data = PackUtils.unpack(packet)
        self.send_locked = False
        self.response(data,
                      self.request,
                      self.func_name,
                      self.args)


class Forwarder:
    """
    This is the base class for streaming
    """
    _protocol = None
    _cached_methods = []

    def __init__(self, response_handler, socket_file):
        """Initiate a connect attempt"""
        self.logger = logging.getLogger()

        Sender.register_response_handler(response_handler)
        client = ClientCreator(reactor, Sender)

        d = client.connectUNIX(socket_file)
        d.addCallback(self._got_protocol)
        d.addErrback(self._eb_got_protocol)

    def append_cached_method(self, name):
        self._cached_methods.append(name)


    @property
    def protocol(self):
        if not self._protocol :
            raise ValueError
            # TODO - log something
        return self._protocol

    @protocol.setter # pyflakes.ignore
    def protocol(self, value):
        self._protocol = value

    def _got_protocol(self, protocol):
        self.logger.debug("got UX socket protocol: %s" % protocol)
        self.protocol = protocol


    def _eb_got_protocol(self, failure):
        self.logger.error("UX protocol failed: %s" % failure)

    def _response_ok(self, result):
        return True


    def call_remote(self, request, func_name, args):
        self.logger.debug("UX:calling %s" %(func_name))
        try :
            packet = PackUtils.pack([func_name, args])
        except Exception, e:
            self.logger.warn("UX call pack method failed: %s" % str(e))



        if func_name in self._cached_methods :
            # response always OK, but cached into buffer
            SendingBuffer().add(packet)
            self.protocol.response(True,
                                   request,
                                   func_name,
                                   args)

        else :
            # response immediately
            try :
                self.protocol.func_name = func_name
                self.protocol.args = args
                self.protocol.request = request
                self.protocol.call_remote(packet)
            except Exception, e:
                self.logger.warn("UX: immediate call method failed: %s" % str(e))
