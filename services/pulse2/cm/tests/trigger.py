# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
