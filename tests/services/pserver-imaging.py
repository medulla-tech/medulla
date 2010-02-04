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
Unit tests for the imaging API of the Pulse 2 Package Server
"""

import unittest
import xmlrpclib
from testutils import ipconfig

ipserver = ipconfig()
protocol = 'https' # protocol's server
server = xmlrpclib.ServerProxy('%s://%s:9990/imaging' % (protocol,ipserver))

class Imaging(unittest.TestCase):

    def test_registerComputer(self):
        result = server.computerRegister('foobar', 'BADMAC')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
        result = server.computerRegister('bad _ name', '00:11:22:33:44:55')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
        result = server.computerRegister('foobar', '00:11:22:33:44:55')
        self.assertEqual(0, result)

    def test_status(self):
        result = server.imagingServerStatus()
        self.assertEqual(int, type(result))
        self.assertTrue(result == -1 or result >= 0 or result <= 100)

if __name__ == '__main__':
    unittest.main()
