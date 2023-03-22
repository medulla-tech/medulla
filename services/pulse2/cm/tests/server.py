# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from twisted.trial.unittest import TestCase
from twisted.test.proto_helpers import StringTransport

from twisted.internet.defer import Deferred
from twisted.internet.task import Clock

from pulse2.cm.server import GatheringFactory
from pulse2.cm.collector import Collector, Sessions


class EchoResponse(object):
    """
    A helper to replace the Collector instance.

    This class contains only necessary method queue_and_process
    which makes a simply echo.
    """

    def queue_and_process(self, ip, request):
        d = Deferred()
        d.callback(request)
        return d

class DummyTrigger(object):
    def fire(self):
        return Deferred()


#class RClock(Clock):
#    threadCallQueue = []
#
#    def __init__(self):
#        Clock.__init__(self)
#        self.threadpool = ThreadPool()
#        self.threadpool.start()
#
#    def getThreadPool(self):
#        return self.threadpool
#
#    def callFromThread(self, f, *args, **kw):
#        self.threadCallQueue.append((f, args, kw))
#        f(*args, **kw)

class Test00_GatheringServerTestCase(TestCase):
    """ Tests the factory of GatheringServer"""


    def test01a_assign_invalid_handler(self):
        """ Test of assigning of invalid instance of handler """
        factory = GatheringFactory()

        # Instead of an instance having "queue_and_process" method,
        # we assign a simply object
        self.assertRaises(AttributeError, factory.protocol.set_handler, object)

    def test01b_assign_invalid_trigger(self):
        """ Test of assigning of invalid instance of trigger """
        factory = GatheringFactory()

        # Instead of an instance having "queue_and_process" method,
        # we assign a simply object
        self.assertRaises(AttributeError, factory.protocol.set_trigger, object)



    def test02_make_echo(self):
        """
        Assign a simply echo instance as handler/

        This helper returns immediatelly a same response.
        """
        factory = GatheringFactory()
        collector = EchoResponse()
        trigger = DummyTrigger()
        factory.protocol.set_handler(collector)
        factory.protocol.set_trigger(trigger)

        protocol = factory.buildProtocol(("127.0.0.1", 0))
        transport = StringTransport()
        protocol.makeConnection(transport)


        protocol.dataReceived("hello")
        self.assertEqual(transport.value(), "hello")


    def test03_make_echo_with_collector(self):
        """
        Test with correct handler used in the package.

        - Get the request from server
        - Sending the same response
        """

        clock = Clock()
        sessions = Sessions(False, 10, clock)

        trigger = DummyTrigger()

        factory = GatheringFactory()
        collector = Collector(sessions)
        factory.protocol.set_handler(collector)
        factory.protocol.set_trigger(trigger)

        protocol = factory.buildProtocol(("127.0.0.1", 0))
        transport = StringTransport()
        protocol.makeConnection(transport)


        protocol.dataReceived("hello")


        uid, ip, data = collector.get()
        collector.release(uid, data)

        self.assertEqual(transport.value(), "hello")


#    def test04_with_trigger_and_lot_of_requests(self):
#        """
#        Test with correct handler used in the package.
#
#        - Get the request from server
#        - Sending the same response
#        """
#
#        print
#        clock = RClock()
#
#        sessions = Sessions(False, 600, clock)
#        collector = Collector(sessions)
#
#        def process_responses():
#            #print _collector.queue
#            _collector = collector
#            while True:
#                #clock.advance(10)
#                result = _collector.get()
#
#                if not result:
#                    break
#
#                uid, ip, request = result
#
#                delay = randrange(1, 50)
#                clock.advance(delay)
#                print "\033[33mrelease request: %s (delay=%d)\033[0m" % (request, delay)
#
#                _collector.release(uid, "ok")
#
#        try:
#            trigger = Trigger(clock, process_responses)
#        except Exception, e:
#            print "\033[31mtrigger instance failed: %s\033[0m" % str(e)
#
#
#        factory = GatheringFactory()
#        factory.protocol.set_handler(collector)
#        factory.protocol.set_trigger(trigger)
#
#        protocol = factory.buildProtocol(("127.0.0.1", 0))
#        transport = StringTransport()
#        protocol.makeConnection(transport)
#
#        prev_stamp = 0
#        for i in xrange(10):
#            request = "hello_%d" % randrange(0, 99999)
#            protocol.dataReceived(request)
#            lag = clock.seconds() - prev_stamp
#
#            print "\033[32mrelease request: %d \033[0m" % (lag)
#            prev_stamp = clock.seconds()
#        print len(collector.queue)
