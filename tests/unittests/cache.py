#!/usr/bin/python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2011 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
