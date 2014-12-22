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

from twisted.trial.unittest import TestCase
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.task import Clock

from pulse2.cm.collector import SessionNotFound
from pulse2.cm.collector import Sessions, Collector

class Test00_SessionsTestCase(TestCase):
    """ Test for sessions tracker"""


    def setUp(self):
        self.clock = Clock()
        self.sessions = Sessions(False, 10, self.clock)


    def test01_all_elements_are_deferred(self):
        """ To be sure if all elements are deferred instances"""
        for i in xrange(20):
            uid, d = self.sessions.make()

        result = all([isinstance(d[1], Deferred) for d in self.sessions.content.values()])
        self.assertTrue(result)


    def test02_exists(self):
        """ An occurence test of added element in container """

        uid, d = self.sessions.make()
        self.assertIn(uid, self.sessions)


    def test03_not_exists_if_removed(self):
        """ An occurence test of removed element from container """

        uid, d = self.sessions.make()
        self.sessions.remove(uid)
        self.assertNotIn(uid, self.sessions)


    def test04_not_exists_if_pop(self):
        """ An occurence test of returned and removed element from container """

        uid, d = self.sessions.make()
        self.sessions.pop(uid)
        self.assertNotIn(uid, self.sessions)

    def test05_try_remove_unexisting(self):
        """ An occurence test of removed element from container """

        uid, d = self.sessions.make()
        self.sessions.remove(uid)

        self.assertRaises(SessionNotFound, self.sessions.remove, uid)
        self.assertRaises(SessionNotFound, self.sessions.get, uid)
        self.assertRaises(SessionNotFound, self.sessions.pop, uid)

    def test06_is_same_deferred_reference(self):
        """
        - create a session and get its uid and deferred
        - get and remove its referrence (returning of deferred)
        - deferred is fired
        -> test if it is always the same deferred
        """

        uid, d_before = self.sessions.make()
        d_after = self.sessions.pop(uid)
        # an action on d_before deferred
        d_before.callback(True)

        self.assertTrue(d_before is d_after)

    def test07_expire(self):
        """ test if expired requests is no more in sessions """

        # create sessions instance with specific result
        sessions = Sessions("I'm an expired request", 10, self.clock)
        uids = []

        for i in xrange(10):
            uid, d = sessions.make()
            @d.addCallback
            def cb(reason):
                """ Callback of all expired requests """
                # All expired requests must return this text
                self.assertEqual(reason, "I'm an expired request")

            uids.append(uid)

        for uid in uids:
            sessions._expire(uid)

        result = all([uid not in uids for uid in sessions.content])
        # verify if all expired uis is no more in sessions content
        self.assertTrue(result)



    def test08_check_for_expired(self):
        """
        - create some tasks
        - wait some time
        - create another lot of tasks
        - wait some time
        -> check if only second lot of tasks present
        """

        sessions = Sessions(False, 10, self.clock)
        to_expire = []
        to_stay = []


        def add_elements(expire):
            print
            for i in range(10):
                uid, d = sessions.make()
                if expire:
                    to_expire.append(uid)
                else:
                    to_stay.append(uid)

        def check_result():
            result = all([uid not in to_expire for uid in sessions.content])
            self.assertTrue(result)


        add_elements(True)
        self.clock.advance(15)
        add_elements(False)

        result = all([uid not in to_expire for uid in sessions.content])
        self.assertTrue(result)



class Test01_CollectorTestCase(TestCase):

    def setUp(self):
        self.sessions = Sessions(False, 10, Clock())

    def test01_first_add_and_get(self):
        """
        First element added to queue will be returned as first.
        """

        collector = Collector(self.sessions)

        first_data = "my first data"

        collector.queue_and_process("192.168.45.12", first_data)
        # We are sure that only one element queued
        uid, ip, request = collector.get()
        self.assertEqual(request, first_data)


    def test02_add_and_release(self):
        """
        - Add an element and get its deferred (as my_deferred)
        - Add another elements
        - Because this is a first element, first get() returns its uid
        -> Release an element with our uid, we get the same deferred
        """

        collector = Collector(self.sessions)

        any_data = "any data"

        my_deferred = collector.queue_and_process("192.168.45.12", any_data)

        for i in xrange(10):

            collector.queue_and_process("192.168.127.22",
                                        "%s_%d" % (any_data, i))

        uid, ip, request = collector.get()

        d = collector.release(uid, "any result")

        self.assertTrue(my_deferred is d)



    def test03_get_from_empty_queue(self):
        """ Empty queue returns a deferred with None """

        collector = Collector(self.sessions)

        reason = collector.get()
        self.assertTrue(reason is None)




    def test04_get_only_valid_requests(self):
        """
        - create a lot of requests marked as 'expired'
        - wait some time
        - create another lot of requests marked as 'valid'
        -> check if only 'valid' requests present
        """

        clock = Clock()

        sessions = Sessions(False, 10, clock)
        collector = Collector(sessions)

        dl = []
        for i in xrange(10):
            d = collector.queue_and_process("192.168.45.12", "expired")
            dl.append(d)

        clock.advance(15)

        for i in xrange(10):
            d = collector.queue_and_process("192.168.45.12", "valid")
            dl.append(d)


        dfl = DeferredList(dl)
        @dfl.addCallback
        def get_result(ignored):

            for i in xrange(10):
                uid, ip, request = collector.get()
                self.assertEqual(request, "valid")





