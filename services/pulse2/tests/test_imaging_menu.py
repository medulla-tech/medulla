# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: test_utils.py 5218 2010-02-04 18:09:02Z cdelfosse $
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
Tests for pulse2.imaging.menu
"""

import unittest

from pulse2.imaging.menu import isMenuStructure, ImagingMenuBuilder

from pulse2.package_server.config import P2PServerCP


config = P2PServerCP()
config.setup('/etc/mmc/pulse2/package-server/package-server.ini')

menu = { 'timeout' : 20,
         'background_uri' : u'/##PULSE2_F_DISKLESS##/##PULSE2_F_BOOTSPLASH##',
         'name' : u'Default Boot Menu',
         'message' : u'-- Warning! Your PC is being backed up or restored. Do not reboot !',
         'protocol' : 'nfs',
         'default_item' : 1,
         'default_item_wol' : 1,
         'bootservices' : { 1: { 'name' : u'Continue Normal Startup',
                                 'desc' : u'Start as usual',
                                 'value' : u'root (hd0)\r\nchainloader +1', 
                                 'hidden' : 0,
                                 'hidden_WOL' : 0,
                                 'value' : u'root (hd0)\r\nchainloader +1' },
                           2: { 'name' : u'Register a Pulse 2 Client',
                                'desc' : u'Record this computer in Pulse 2 Server',
                                'value' : u'identify L=##PULSE2_LANG## P=none\nreboot' }
                            },
         'images' : { 5 : { 'name' : u'...',
                            'desc' : u'...',
                            'post_install_script' : { 'id' : id,
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


class MenuTests(unittest.TestCase):

    def testMenuValid(self):
        self.assertTrue(isMenuStructure(menu))
        self.assertFalse(isMenuStructure('foo'))

    def testMenuGenerate(self):
        m = ImagingMenuBuilder(config, 'dfb7cadf-2c0a-4dd2-a852-4558ffd5de99', menu)
        im = m.make()
        grubmenu = im.buildMenu()
        self.assertEqual(len(grubmenu.split('\n')), 17)


if __name__ == '__main__':
    unittest.main()

