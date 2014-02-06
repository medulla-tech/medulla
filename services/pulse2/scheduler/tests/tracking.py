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

	
