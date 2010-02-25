# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.


"""
Tests for pulse2.utils
"""

import unittest

from pulse2.utils import isMACAddress, isUUID, splitComputerPath

class InputTests(unittest.TestCase):

    def test_MACValid(self):
        self.assertTrue(isMACAddress('00:11:aa:BB:22:33'))

    def test_MACNotValid(self):
        self.assertFalse(isMACAddress('00:11:aa:BB:22:zz'))
        self.assertFalse(isMACAddress('00:11:aa:BB:22:33:00'))

    def test_UUIDValid(self):
        self.assertTrue(isUUID('UUID1'))
        self.assertTrue(isUUID(u'UUID1'))
        self.assertTrue(isUUID('1a10b1f4-bb6e-4798-b39e-bb8d090dd8b6'))

    def test_UUIDNotValid(self):
        self.assertFalse(isUUID('UUID0'))
        self.assertFalse(isUUID('UUID-10'))
        self.assertFalse(isUUID(''))
        self.assertFalse(isUUID('1a10b1f4-bb6e-4798-b39e-bb8d090dd8b'))
        self.assertFalse(isUUID(42))

    def test_computerPathValid(self):
        self.assertEqual(splitComputerPath('hostname'), ('', '', 'hostname', ''))
        self.assertEqual(splitComputerPath('hostname.domain-example.net'), ('', '', 'hostname', 'domain-example.net'))
        self.assertEqual(splitComputerPath('profile:hostname'), ('profile', '', 'hostname', ''))
        self.assertEqual(splitComputerPath('profile:/hostname'), ('profile', '', 'hostname', ''))
        self.assertEqual(splitComputerPath('/root/sub1/sub2/hostname'), ('', '/root/sub1/sub2', 'hostname', ''))
        self.assertEqual(splitComputerPath('profile:/root/sub1/sub2/hostname'), ('profile', '/root/sub1/sub2', 'hostname', ''))
        self.assertRaises(TypeError, splitComputerPath, 'profile:root/sub1/sub2/hostname')
        self.assertRaises(TypeError, splitComputerPath, 'profile:')        

if __name__ == '__main__':
    unittest.main()
