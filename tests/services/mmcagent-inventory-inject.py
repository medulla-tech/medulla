#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Test module for the Pulse 2 MMC Agent inventory plugin
A inventory is injected to test its good behavior
"""

import unittest
import sys
import os
import time

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
login = "mmc"
password = "s3cr3t"

client = sync.Proxy("https://%s:%s@localhost:7080" % (login, password), False)
client.base.ldapAuth("root", "secret")


class class01inventoryReportTest(TestCase):

    """
    Inventory test class
    """

    def test102hasInventory(self):
        # Load the full inventory to test each part separately
        inventory = client.inventory.getLastMachineInventoryFull({})
        # Assert that the inventory is not empty for the parts which are
        # necessarly used
        for part in inventory:
            if part == "Hardware" or part == "Software":
                self.assertNotEqual(inventory[part], [])

    def test103ubuntuInject(self):
        """
        Inject an Ubuntu UTF-8 inventory containing latin-1 chars
        """
        os.system(
            "gunzip -c ../data/ocs-ubuntu-10.04-lts.xml.gz | ../../../pulse2/services/contrib/Ocsinventory_local.pl -u http://127.0.0.1:9999 --stdin"
        )
        time.sleep(10)
        result = client.inventory.inventoryExists("UUID3")
        self.assertTrue(result)

    def test104macosxInject(self):
        """
        Inject a MAC OS X inventory
        """
        os.system(
            "gunzip -c ../data/ocs-os-x-10.4.xml.gz | ../../../pulse2/services/contrib/Ocsinventory_local.pl -u http://127.0.0.1:9999 --stdin"
        )
        time.sleep(10)
        result = client.inventory.inventoryExists("UUID4")
        self.assertTrue(result)


# Launch of the tests
if mode == "debug":
    nb = 0
    success = []
    for klass in [class01inventoryReportTest]:
        suite = unittest.TestLoader().loadTestsFromTestCase(klass)
        test = unittest.TextTestRunner(verbosity=Verbosity).run(suite)
        success.append(test.wasSuccessful())
        nb = nb + test.testsRun

    if False in success:
        print("One or more test are failed or have an unexpected error")
    else:
        print("All function work")
else:
    unittest.main()
