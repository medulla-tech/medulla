#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2011 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Test module for the Pulse 2 cache
"""
import unittest
import time.sleep

from pulse2.cache import CacheManager, getCache, CacheFault, CacheExpired, DEFAULT_TIMEOUT

class CacheTest(unittest.TestCase):
    """ Test Generic Pulse2 cache
    """
    def setUp(self):
        CacheManager().reset()

    def testName(self):
        cache = getCache('test')
        self.assertEqual('test', cache.name)

    def testDiffName(self):
        cache1 = getCache('test1')
        cache2 = getCache('test1')
        self.assertTrue(cache1<>cache2)

    def testTimeout(self):
        cache = getCache('test', 5)
        self.assertEqual(cache.timeout, 5)

    def testDefaultTimeout(self):
        cache = getCache('test')
        self.assertEqual(cache.timeout, DEFAULT_TIMEOUT)

    def testCold(self):
        def f():
            cache = getCache('test')
            cache.get(object())
        self.assertRaises(CacheFault, f)

    def testHot(self):
        obj = object()
        cache = getCache('test')
        cache.set(obj, 'a')
        val = cache.get(obj)
        self.assertEqual(val, 'a')

    def testTimeout3(self):
        obj = object()
        cache = getCache('test')
        cache.set(obj, 'a', timeout=2)
        time.sleep(3)
        
        def f():
            cache.get(obj)
        self.assertRaises(CacheExpired, f)

    def testTimeout2(self):
        obj = object()
        cache = getCache('test')
        cache.set(obj, 'a', timeout=2)
        time.sleep(3)
        
        def f():
            cache.get(obj)
        self.assertRaises(CacheExpired, f)
        self.assertRaises(CacheFault, f)

if __name__ == '__main__':
    unittest.main()
