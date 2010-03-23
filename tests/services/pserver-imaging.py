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

import os
import unittest
import xmlrpclib
import copy

from time import gmtime, sleep

from pulse2.utils import reduceMACAddress
from testutils import ipconfig

IPSERVER = ipconfig()
PROTOCOL = 'https' # protocol's SERVER
SERVER = xmlrpclib.ServerProxy('%s://%s:9990/imaging_api'
                               % (PROTOCOL, IPSERVER))
MMCAGENT = xmlrpclib.ServerProxy('%s://mmc:s3cr3t@%s:7080'
                                 % (PROTOCOL, '127.0.0.1'))

MENU = { 'timeout' : 20,
         'background_uri' : u'/##PULSE2_F_DISKLESS##/##PULSE2_F_BOOTSPLASH##',
         'name' : u'Default Boot Menu',
         'message' : u'-- Warning! Your PC is being backed up or restored. Do not reboot !',
         'protocol' : u'nfs',
         'default_item' : 1,
         'default_item_WOL' : 1,
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
                            'post_install_script_dis' : { 'id' : 2,
                                                      'name' : u'...',
                                                      'desc' : u'...',
                                                      'value' : '...'
                                                    }
                            }
                    },
         'target' : { 'name' : u'...',
                      'kernel_parameters' : u'...',
                      'image_parameters' : u'....',
                      'exclude_parameters' : u'',
                    },
         'bootcli' : False,
         'disklesscli' : False,
         'dont_check_disk_size' : False,
         'ethercard' : 0
        }
MENUS = { 'UUID27' : MENU }

class Imaging(unittest.TestCase):

    """
    Tests for the Imaging API of the package server.
    """

    def test_01registerPackageServer(self):
        """
        Check package server registration
        """
        ret = os.system('pulse2-package-server-register-imaging  -n \"Pulse 2 imaging\" -m https://mmc:s3cr3t@localhost:7080')
        self.assertEqual(0, ret)
        self.assertEqual([True, True], MMCAGENT.imaging.linkImagingServerToLocation('UUID1', 'UUID1', 'root'))

    def test_02registerComputer(self):
        """
        Check computer registration
        """
        mac = '00:11:22:33:44:ff'
        result = SERVER.computerRegister('foobar', 'BADMAC')
        self.assertFalse(result)
        result = SERVER.computerRegister('bad _ name', mac)
        self.assertFalse(result)
        result = SERVER.computerRegister('foobar', mac)
        self.assertTrue(result)
        self.assertTrue(os.path.exists('/var/lib/pulse2/imaging/uuid-cache.txt'))
        self.assertTrue(os.path.isdir('/var/lib/pulse2/imaging/computers/%s' % 'UUID2'))
        # Wait a bit for the menu to be generated asynchronously
        sleep(5)
        self.assertTrue(os.path.exists('/var/lib/pulse2/imaging/bootmenus/%s' % reduceMACAddress(mac)))
        # No exclude file should be there
        self.assertFalse(os.path.exists('/var/lib/pulse2/imaging/computers/%s/exclude' % 'UUID2'))

    def test_03registerComputers(self):
        """
        Check mass computers registration
        """
        menu = copy.deepcopy(MENU)
        menu['target']['exclude_parameters'] = '0:0'
        arg = [
            ('hostname1', '00:11:22:33:44:dd',
             { 'uuid' : 'UUID3', 'menu' : { 'UUID3' : menu }}),
            ('hostname2', '00:11:22:33:44:ee',
             { 'uuid' : 'UUID4', 'menu' : { 'UUID4' : MENU }}),
            ]
        result = SERVER.computersRegister(arg)
        self.assertEqual(['UUID3', 'UUID4'], result)
        # Wait a bit for the menu to be generated asynchronously
        sleep(5)
        # Exclude file should be there for UUID3
        self.assertTrue(os.path.exists('/var/lib/pulse2/imaging/computers/%s/exclude' % 'UUID3'))

    def test_04inventory(self):
        """
        Inventory injection test
        """
        inventory = {'memslot': {'speed': 18756, 'type': '7', 'location': 'DIMM 0', 'ff': 9, 'size': 128}, 'numcpu': 1, 'featcpu': [6, 2, 3, 0, 4, 0, 0, 0, 253, 251, 139, 7, 71, 101, 110, 117, 105, 110, 101, 73, 110, 116, 101, 108], 'mem': {'upper': 128972, 'lower': 636}, 'bus': {'0': {'16': {'device': 4369, 'vendor': 4660, 'class': 3, 'subclass': 0}, '9': {'device': 28688, 'vendor': 32902, 'class': 1, 'subclass': 1}, '24': {'device': 4098, 'vendor': 6900, 'class': 5, 'subclass': 0}, '32': {'device': 33081, 'vendor': 4332, 'class': 2, 'subclass': 0}}}, 'macaddr': '52:54:00:C9:D1:0F', 'ipaddr': {'ip': '192.168.21.201', 'port': 1001}, 'sys': {'uuid': '2F6236FC76ABD2F5D88EF2B2CE720853', 'product': 'Bochs', 'version': '-', 'serial': '-', 'manufacturer': 'Bochs'}, 'bios': {'date': '01/01/2007\n', 'version': 'Bochs', 'vendor': 'Bochs'}, 'freqcpu': 2260807, 'enclos': {'type': '1', 'vendor': 'Bochs'}, 'disk': {'0': {'H': 16, 'C': 1023, 'parts': {'0': {'start': 63, 'length': 530082, 'type': 131}, '1': {'start': 530145, 'length': 530145, 'type': 7}, '2': {'start': 1060290, 'length': 2104515, 'type': 142}, '4': {'start': 3164868, 'length': 530082, 'type': 131}, '5': {'start': 3695013, 'length': 497952, 'type': 131}}, 'S': 63, 'size': 63}}}
        result = SERVER.injectInventory('00:11:22:33:44:ff', inventory)
        self.assertTrue(result)

    def atest_computersMenuSet(self):
        #result = SERVER.computersMenuSet([('UUID17', {})])
        #self.assertEqual(['UUID1'], result)
        result = SERVER.computersMenuSet(MENUS)
        self.assertEqual(['UUID27'], result)

    def atest_logClientAction(self):
        result = SERVER.logClientAction('mac', 'level', 'phase', 'message')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
        result = SERVER.logClientAction('00:11:22:33:44:55', 'level', 'phase', 'message')
        self.assertTrue(result)

    def atest_computerUpdate(self):
        result = SERVER.computerUpdate('BADMAC')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
    def atest_status(self):
        result = SERVER.imagingSERVERStatus()
        self.assertEqual(dict, type(result))
        self.assertTrue('space_available' in result)
        self.assertTrue('mem_info' in result)
        self.assertTrue('uptime' in result)
        self.assertTrue('stats' in result)

    def atest_injectInventory(self):
        pass

    def atest_02getComputerByMAC(self):
        result = SERVER.getComputerByMac('BADMAC')
        self.assertTrue('faultCode' in result and
                        'TypeError' in result['faultCode'])
        result = SERVER.getComputerByMac('00:11:22:33:44:55')
        self.assertTrue('uuid' in result and result['uuid'] == 'FAKE_UUID')

    def atest_imagingSERVERImageDelete(self):
        result = SERVER.imagingSERVERImageDelete('foo')
        self.assertFalse(result)
        result = SERVER.imagingSERVERImageDelete('35f23420-4050-4734-b172-d458915ef17d')
        self.assertFalse(result)

    def atest_imageRegister(self):
        result = SERVER.imageRegister('30:11:22:33:44:ff', '35f23420-4050-4734-b172-d458915ef17d', False, 'Image 1', 'Mon Mar  1 15:46:43 CET 2010', '/path/?', 12345, tuple(gmtime()), 'cdelfosse')
        self.assertTrue(result)

    def atest_imagingSERVERDefaultMenuSet(self):
        result = SERVER.imagingSERVERDefaultMenuSet(menu)
        self.assertEqual(['UUID1'], result)

    def atest_iso(self):
        iuuid = 'fe71d487-2a90-11df-99a9-5254001c1e49'
        result = SERVER.imagingServerISOCreate(iuuid, 650 * 1024 * 1024, "Image ISO")


if __name__ == '__main__':
    unittest.main()
