#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Test module for the Pulse 2 MMC Agent init
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
login = "mmc"
password = "s3cr3t"

client = sync.Proxy("https://%s:%s@localhost:7080" % (login, password), False)
client.base.ldapAuth("root", "secret")

"""
Test class
"""


class class01packageInitTest(TestCase):
    """
    Tests classes of the packages module
    """

    def setUp(self):
        self.client = client.pkgs

    def test301getPApiDetail(self):
        # FIXME: Should test the value of "upa" before accessing upa['uuid']
        # result = self.client.getPApiDetail(1337)
        # self.assertEqual(result, False)
        pass

    def test302ppaGetPackageDetail(self):
        # FIXME: Should test the value of "upa" before accessing upa['uuid']
        # result = self.client.ppa_getPackageDetail(1337, 1338)
        # self.assertEqual(result, False)
        pass

    def test303ppaPutPackageDetail(self):
        # FIXME: Should test the value of "upa" before accessing upa['uuid']
        # result = self.client.ppa_putPackageDetail(1337, 1338)
        # self.assertEqual(result, False)
        pass

    def test304ppaDropPackage(self):
        # FIXME: Should test the value of "upa" before accessing upa['uuid']
        # result = self.client.ppa_dropPackage(1337, 1338)
        # self.assertEqual(result, False)
        pass

    def test305ppaGetTemporaryFiles(self):
        # FIXME: Should test the value of "upa" before accessing upa['uuid']
        # result = self.client.ppa_getTemporaryFiles(1337)
        # self.assertEqual(result, False)
        pass

    def test306ppaGetAssociatedPackages(self):
        # FIXME: Should test the value of "upa" before accessing upa['uuid']
        # result = self.client.ppa_associatePackages(1337)
        # self.assertEqual(result, False)
        pass

    def test307ppaGetRsyncStatus(self):
        # FIXME: Should test the value of "upa" before accessing upa['uuid']
        # result = self.client.ppa_getRsyncStatus(1337, 1338)
        # self.assertEqual(result, True)
        pass

    def test308upaaGetUserPackageApi(self):
        # FIXME: Should test the value of "upa" before accessing upa['uuid']
        # result = self.client.upaa_getUserPackageApi()
        # self.assertEqual(result, [{'ERR':'PULSE2ERROR_GETUSERPACKAGEAPI', 'mirror': 'https://192.168.0.239:9990/upaa'}])
        pass


"""
Launch of the tests
"""
if mode == "debug":
    nb = 0
    success = []
    suite = unittest.TestLoader().loadTestsFromTestCase(class01packageInitTest)
    test = unittest.TextTestRunner(verbosity=Verbosity).run(suite)
    success.append(test.wasSuccessful())
    nb = nb + test.testsRun

    if False in success:
        print("One or more test are failed or have an unexpected error")
    else:
        print("All function work")
else:
    unittest.main()
