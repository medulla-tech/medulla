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
server = xmlrpclib.ServerProxy('%s://%s:9990/imaging_api' % (protocol,ipserver))
menu = { 'timeout' : 20,
         'background_uri' : u'/##PULSE2_F_DISKLESS##/##PULSE2_F_BOOTSPLASH##',
         'name' : u'Default Boot Menu',
         'message' : u'-- Warning! Your PC is being backed up or restored. Do not reboot !',
         'protocol' : 'nfs',
         'default_item' : 1,
         'default_item_wol' : 1,
         'bootservices' : { '1': { 'name' : u'Continue Normal Startup',
                                 'desc' : u'Start as usual',
                                 'value' : u'root (hd0)\nchainloader +1',
                                 'hidden' : 0,
                                 'hidden_WOL' : 0,
                                 'value' : u'root (hd0)\nchainloader +1' },
                           '2': { 'name' : u'Register a Pulse 2 Client',
                                'desc' : u'Record this computer in Pulse 2 Server',
                                'value' : u'identify L=##PULSE2_LANG## P=none\nreboot' }
                            },
         'images' : { '5' : { 'uuid': u'302c19d2-212b-4b9a-b04e-4fced0b83466',
                            'name' : u'Image computer.example.net',
                            'desc' : u'(Thu Dec  3 15:20:02 2009)',
                            'post_install_script' : { 'id' : 2,
                                                      'name' : u'...',
                                                      'desc' : u'...',
                                                      'value' : '...'
                                                    }
                            }
                    },
         'target' : { 'name' : u'...',
                      'kernel_parameters' : u'...',
                      'image_parameters' : u'....',
                    }
        }


class Imaging(unittest.TestCase):

    def test_registerComputer(self):
        result = server.computerRegister('foobar', 'BADMAC')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
        result = server.computerRegister('bad _ name', '00:11:22:33:44:55')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
        result = server.computerRegister('foobar', '00:11:22:33:44:55')
        self.assertEqual(1, result)

    def test_logClientAction(self):
        result = server.logClientAction('mac', 'level', 'phase', 'message')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
        result = server.logClientAction('00:11:22:33:44:55', 'level', 'phase', 'message')
        self.assertTrue(result)

    def test_computerUpdate(self):
        result = server.computerUpdate('BADMAC')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])        
        
    def test_status(self):
        result = server.imagingServerStatus()
        self.assertEqual(dict, type(result))
        self.assertTrue('space_available' in result)
        self.assertTrue('mem_info' in result)
        self.assertTrue('uptime' in result)
        self.assertTrue('stats' in result)

    def test_injectInventory(self):
        pass

    def test_getComputerByMAC(self):
        result = server.getComputerByMac('BADMAC')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
        result = server.getComputerByMac('00:11:22:33:44:55')
        self.assertTrue('uuid' in result and result['uuid'] == 'FAKE_UUID')

    def test_computersMenuSet(self):
        result = server.computersMenuSet([('UUID1', {})])
        self.assertEqual(['UUID1'], result)
        result = server.computersMenuSet([('UUID1', menu)])
        self.assertEqual(['UUID1'], result)

if __name__ == '__main__':
    unittest.main()
