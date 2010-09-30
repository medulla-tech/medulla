#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
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
Test module for the Pulse 2 MMC Agent inventory plugin
A inventory is injected to test its good behavior
"""

import unittest
import sys
import os
import os.path
import time

from unittest import TestCase
from testutils import MMCProxy


# Set options to use to run the tests
makefile = False

if "debug" in sys.argv:
    mode = "debug"
    Verbosity = 2
else:
    mode = "info"

if "makefile" in sys.argv:
    makefile = True

"""
Connect to the MMC agent using the MMCProxy class defined above
"""
login = 'mmc'
password = 's3cr3t'

client = MMCProxy('https://%s:%s@localhost:7080'%(login, password), False)
client.base.ldapAuth('root', 'secret')


class class01inventoryReportTest(TestCase):

    """
    Inventory test class
    """

    def test101inventoryInject(self):
        OCS = '/usr/sbin/ocsinventory-agent'
        if not os.path.exists(OCS):
            print "OCS Inventory Agent is not installed, skipping test"
            sys.exit(0)
        # Launch the inventory agent to report an inventory
        os.system(OCS + ' --server=http://127.0.0.1:9999')
        time.sleep(20)
        result = client.inventory.inventoryExists('UUID5')
        self.assertTrue(result)

    def test103hasInventory(self):
        # Load the full inventory to test each part separately
        inventory = client.inventory.getLastMachineInventoryFull({})
        # Assert that the inventory is not empty for the parts which are
        # necessarly used
        for part in inventory:
            if part == 'Hardware' or part == 'Software':
                self.assertNotEqual(inventory[part], [])

    def test104ubuntuInject(self):
        """
        Inject an Ubuntu UTF-8 inventory containing latin-1 chars
        """
        os.system('gunzip -c ../data/ocs-ubuntu-10.04-lts.xml.gz | $PULSE2/services/contrib/Ocsinventory_local.pl -u http://127.0.0.1:9999 --stdin')
        time.sleep(20)
        result = client.inventory.inventoryExists('UUID6')
        self.assertTrue(result)

    def test104macosxInject(self):
        """
        Inject a MAC OS X inventory
        """
        os.system('gunzip -c ../data/ocs-os-x-10.4.xml.gz | $PULSE2/services/contrib/Ocsinventory_local.pl -u http://127.0.0.1:9999 --stdin')
        time.sleep(20)
        result = client.inventory.inventoryExists('UUID7')
        self.assertTrue(result)

# Launch of the tests
if mode == "debug":
    nb = 0
    success = []
    for klass in [class01inventoryReportTest]:
        suite=unittest.TestLoader().loadTestsFromTestCase(klass)
        test=unittest.TextTestRunner(verbosity=Verbosity).run(suite)
        success.append(test.wasSuccessful())
        nb=nb+test.testsRun

    if False in success:
        print "One or more test are failed or have an unexpected error"
    else:
        print "All function work"
else:
    unittest.main()
