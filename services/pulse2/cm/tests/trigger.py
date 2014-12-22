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
from twisted.internet.task import Clock

from pulse2.cm.trigger import Trigger



class Test00_Trigger(TestCase):

    def setUp(self):
        self.clock = Clock()

    def test01_fire(self):

        def test_method():
            self.clock.advance(5)


        trigger = Trigger(test_method)
        d = trigger.fire()
        @d.addCallback
        def get_result1(result):
            self.assertTrue(result)

        self.clock.advance(2)
        d = trigger.fire()
        @d.addCallback
        def get_result2(result):
            self.assertFalse(result)


