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
Test module for the Pulse 2 MMC Agent inventory plugin init
All the values are tested as empty
"""

import unittest
import sys

from unittest import TestCase
from mmc.client import sync

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

client = sync.Proxy('https://%s:%s@localhost:7080'%(login, password), False)
client.base.ldapAuth('root', 'secret')

"""
Test class
"""

class class01inventoryInitTest(TestCase):
    """
    Tests classes of the inventory module
    """
    def setUp(self):
        self.client = client.inventory

    def test101inventoryExists(self):
        result = self.client.inventoryExists('34')
        self.assertEqual(result, False)

    def test102countLastMachineInventoryPart(self):
        result = self.client.countLastMachineInventoryPart("Hardware", {})
        self.assertEqual(result, '0')

    def test103getLastMachineInventoryPart(self):
        result = self.client.getLastMachineInventoryPart("Hardware", {})
        self.assertEqual(result, [])

    def test104getLastMachineInventoryFull(self):
        # FIXME : Add a test not to get the 'Entity' part
        #result = self.client.getLastMachineInventoryFull({'uuid':'1337'})
        #self.assertEqual(result, {})
        pass

    def test105getAllMachinesInventoryColumn(self):
        #result = self.client.getAllMachinesInventoryColumn('Hardware', "id")
        #self.assertEqual(result, [])
        pass

    def test106getMachines(self):
        # FIXME: Add a test before using has_key method
        #result = self.client.getMachines()
        #self.assertEqual(result, [])
        pass

    def test107getInventoryEM(self):
        result = self.client.getInventoryEM("Hardware")
        self.assertEqual(result, ['Build', 'Version', 'ProcessorCount', 'SwapSpace', 'User', 'Date', 'Workgroup', 'RegisteredName', 'RegisteredCompany', 'OSSerialNumber', 'Type', 'OsSerialKey', 'ProcessorFrequency', 'Host'])

    def test108getInventoryGraph(self):
        result = self.client.getInventoryGraph("Hardware")
        self.assertEqual(result, ['OperatingSystem', 'ProcessorType'])

    def test109getMachinesBy(self):
        result = self.client.getMachinesBy("Hardware", "id", "1337")
        self.assertEqual(result, [])

    def test110getMachinesByDict(self):
        # FIXME: SQLAlchemy error with foreign keys
        #result = self.client.getMachinesByDict("Hardware", {"id":"1337"})
        #self.assertEqual(result, [])
        pass

    def test111getValues(self):
        result = self.client.getValues("Hardware", "id")
        self.assertEqual(result, [])

    def test112getValuesWhere(self):
        result = self.client.getValuesWhere("Hardware", "id", "1337", "OperatingSystem")
        self.assertEqual(result, [])

    def test113getValueFuzzyWhere(self):
        result = self.client.getValueFuzzyWhere("Hardware", "id", "1337", "OperatingSystem", "Mandriva")
        self.assertEqual(result, [])

    def test114getValuesFuzzy(self):
        result = self.client.getValuesFuzzy("Hardware", "id", "1337")
        self.assertEqual(result, [])

"""
Launch of the tests
"""
if mode == "debug":
    nb = 0
    success = []
    suite=unittest.TestLoader().loadTestsFromTestCase(class01inventoryInitTest)
    test=unittest.TextTestRunner(verbosity=Verbosity).run(suite)
    success.append(test.wasSuccessful())
    nb=nb+test.testsRun

    if False in success:
        print "One or more test are failed or have an unexpected error"
    else:
        print "All function work"
else:
    unittest.main()
