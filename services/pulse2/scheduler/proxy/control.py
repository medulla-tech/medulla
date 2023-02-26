# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

from twisted.internet import reactor, task
from twisted.web.server import Site

from pulse2.xmlrpc import OpenSSLContext

from pulse2.scheduler.xmlrpc import SchedulerSite

from pulse2.scheduler.proxy.xmlrpc import ForwardingProxy
from pulse2.scheduler.proxy.unix import Forwarder
from pulse2.scheduler.proxy.buffer import SendingBuffer


class App :
    def __init__(self, config):
        self.config = config
        SendingBuffer().init(config)
        self.socket_file = config.scheduler_proxy_socket_path
        self.logger = logging.getLogger()
        self.xmlrpc_proxy = ForwardingProxy(self.config)
        self.setup()
        reactor.addSystemEventTrigger('before', 'shutdown', self.clean_up)

    def setup(self):
        """Setup the forwarding proxy"""
        response_handler = self.xmlrpc_proxy.client_response
        d = task.deferLater(reactor,
                            2,
                            Forwarder,
                            response_handler,
                            self.socket_file)
        d.addCallback(self._got_forwarder)
        d.addErrback(self._eb_got_forwarder)

    def _got_forwarder(self, forwarder):
        """
        Attached callback on unix proxy socket build.

        To distinct the remote methods to be buffered or not,
        a internal LIFO list, filled by Forwarder.append_cached_method()
        contains all the methods which will be buffered.

        Unlisted methods is forwarded immediatelly.

        @param forwarder: forwarding engine based on unix socket proxy
        @type forwarder: Forwarder
        """
        self.forwarder = forwarder

        self.forwarder.append_cached_method("completed_push")
        self.forwarder.append_cached_method("completed_pull")
        self.forwarder.append_cached_method("completed_quickaction")
        self.forwarder.append_cached_method("completed_exec")
        self.forwarder.append_cached_method("completed_delete")
        self.forwarder.append_cached_method("completed_inventory")
        self.forwarder.append_cached_method("completed_reboot")
        self.forwarder.append_cached_method("completed_halt")

        self.xmlrpc_proxy.register_forwarder(self.forwarder)

        d = task.deferLater(reactor,
                            self.config.proxy_buffer_start_delay,
                            self.start_emitting_buffer)
        d.addErrback(self._eb_got_forwarder)

    def _eb_got_forwarder(self, failure):
        self.logger.error("forwarder get failed: %s" % failure)


    def start_emitting_buffer(self):
        SendingBuffer().restore_buffer()
        SendingBuffer().register_sender(self.forwarder.protocol)
        t = task.LoopingCall(SendingBuffer().send)
        t.start(self.config.proxy_buffer_period)

    listening_port = None

    def clean_up(self):
        self.logger.info("XMLRPC Proxy: cleaning up...")
        self.logger.info("XMLRPC Proxy: stop the unix socket listening")

        self.forwarder.protocol.transport.loseConnection()

        SendingBuffer().backup_buffer()

        if self.listening_port :
            d = self.listening_port.stopListening()
            @d.addCallback
            def __cb(reason):
                self.logger.info("XMLRPC Proxy: stop port succeed")
            @d.addErrback
            def __eb(failure):
                self.logger.error("XMLRPC Proxy: stop listening error: %s" % failure)



    def run(self):
        self.logger.info('XMLRPC Proxy of scheduler %s: starting' % self.config.name)
        try:
            if self.config.enablessl:
                OpenSSLContext().setup(self.config.localcert,
                                       self.config.cacert,
                                       self.config.verifypeer)

                reactor.listenSSL(
                    self.config.port,
                    SchedulerSite(self.xmlrpc_proxy),
                    interface = self.config.host,
                    contextFactory = OpenSSLContext().getContext()
                    )
                self.logger.info('XMLRPC Proxy of scheduler %s: activating SSL mode' % (self.config.name))
            else:
                self.listening_port = reactor.listenTCP(
                    self.config.port,
                    Site(self.xmlrpc_proxy),
                    interface = self.config.host
                    )
        except Exception, e:
            self.logger.error('XMLRPC Proxy of scheduler %s: can\'t bind to %s:%d, reason is %s' %
                    (self.config.name, self.config.host, self.config.port, e))
            return False
        return True
