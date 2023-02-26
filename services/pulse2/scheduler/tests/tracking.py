# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

""" Unit test for comon circuit trackers """

import time
import random
import unittest

from pulse2.scheduler.tracking.circuits import Tracker, TimedTracker

class Test01_Tracker(unittest.TestCase):


    def test_01_in(self):
	numbers = [int(1000*random.random()) for i in xrange(1000)]
        tracker = Tracker()
	tracker.add(numbers)

        number = random.choice(numbers)
	self.assertIn(number, tracker)

    def test_02_not_in(self):
	numbers = [int(1000*random.random()) for i in xrange(1000)]
        tracker = Tracker()
	tracker.add(numbers)

        number = random.choice(numbers)

	tracker.remove(number)
	self.assertNotIn(number, tracker)

class Test02_TimedTracker(unittest.TestCase):

    def test_01_in(self):
	numbers = [int(1000*random.random()) for i in xrange(1000)]
        tracker = TimedTracker(5)
	tracker.add(numbers)

        number = random.choice(numbers)
	self.assertIn(number, tracker)

    def test_02_not_in(self):
	numbers = [int(1000*random.random()) for i in xrange(1000)]
        tracker = TimedTracker(5)
	tracker.add(numbers)

        number = random.choice(numbers)

	tracker.remove(number)
	self.assertNotIn(number, tracker)

    def test_03_timeout(self):
	numbers = [int(1000*random.random()) for i in xrange(1000)]

        not_expired= []
	for i in xrange(10):
            not_expired.append(random.choice(numbers))

        tracker = TimedTracker(5)

	time.sleep(6)

        for id in not_expired:
            tracker.update(id)

	for id in not_expired:
	    self.assertNotIn(id, tracker.get_expired())


if __name__ == "__main__":
    unittest.main()
