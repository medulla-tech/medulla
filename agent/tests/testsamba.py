#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: testldap.py 365 2006-04-21 08:15:53Z jwax $
#
# This file is part of LMC.
#
# LMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import unittest

import sys
import os
import os.path
import time

from lmc.plugins.samba import smbConf, sambaLdapControl
from lmc.plugins.base import ldapUserGroupControl


def cleanLdap():
    # Wipe out /home
    os.system("rm -fr /home/*")
    # Wipe out LDAP
    os.system("/etc/init.d/slapd stop")
    os.system("killall -9 slapd")
    os.system("rm -f /var/lib/ldap/*")
    os.system("cp contrib/ldap/*.schema /etc/ldap/schema")
    os.system("dpkg-reconfigure -pcritical slapd")
    os.system("cp contrib/ldap/slapd.conf.samba /etc/ldap/slapd.conf")
    os.system("/etc/init.d/slapd restart")
    time.sleep(5)
    # Create Base OU
    l = ldapUserGroupControl("tests/basetest.ini")
    l.addOu("Groups", "dc=linbox,dc=com")
    l.addOu("Users",  "dc=linbox,dc=com")
    l.addOu("Computers",  "dc=linbox,dc=com")

class TestShares(unittest.TestCase):

    def setUp(self):
        cleanLdap()
        self.l = ldapUserGroupControl("tests/basetest.ini")
        self.l.addGroup("grouptestA")
        self.l.addGroup("grouptestB")
        os.system("cp contrib/samba/smb.conf /etc/samba/smb.conf")
        self.s = smbConf(conffile = "tests/sambatest.ini", conffilebase = "tests/basetest.ini")
        os.system("rm -fr %s" % self.s.sharespath)

    def test_shares(self):
        self.assertEqual(len(self.s.getDetailedShares()) > 0, True)
        self.s.addShare("sharetest", "sharetest comment", ["grouptestA"], False, 1)
        self.assertEqual(os.path.exists(os.path.join(self.s.sharespath, "sharetest")), True)
        self.s.save()
        s = smbConf(conffile = "tests/sambatest.ini", conffilebase = "tests/basetest.ini")
        self.assertEqual(s.getACLOnShare("sharetest"), ["grouptestA"])
        self.assertEqual(["sharetest", "sharetest comment"] in s.getDetailedShares(), True)
        i = s.shareInfo("sharetest")
        self.assertEqual(i["permAll"], 0)
        self.assertEqual(i["group"], "root")
        self.assertEqual(i["antivirus"], True)
        self.assertEqual(i["desc"], "sharetest comment")
        s.delShare("sharetest", True)
        self.assertEqual(os.path.exists(os.path.join(self.s.sharespath, "sharetest")), False)
        s.save()

    def test_pdc(self):
        self.assertEqual(self.s.isPdc(), True)
        self.assertEqual(self.s.getSmbInfo()["homes"], True)
        self.assertEqual(self.s.getSmbInfo()["logons"], True)
        self.assertEqual(self.s.getSmbInfo()["master"], True)
        self.assertEqual(self.s.getSmbInfo()["workgroup"], "LINBOX")
        self.assertEqual(self.s.getSmbInfo()["netbios name"], "LINSRV")
        self.s.smbInfoSave(False, False, self.s.getSmbInfo())
        s2 = smbConf(conffile = "tests/sambatest.ini", conffilebase = "tests/basetest.ini")
        self.assertEqual(s2.isPdc(), False)
        self.assertEqual(s2.getSmbInfo()["homes"], False)

    def test_smbconf(self):
        self.assertEqual(self.s.validate(), True)
        self.s.save()
        self.assertEqual(self.s.validate(), True)
        os.system("echo plop > /etc/samba/smb.conf")
        self.assertEqual(self.s.validate(), False)

class testSambaLdap(unittest.TestCase):

    def setUp(self):
        cleanLdap()
        self.l = ldapUserGroupControl("tests/basetest.ini")
        self.l.addGroup("allusers")
        os.system("cp contrib/samba/smb.conf /etc/samba/smb.conf")
        os.system("/etc/init.d/samba stop")
        os.system("/usr/bin/smbpasswd -w linbox")
        os.system("/etc/init.d/samba start")
        self.s = sambaLdapControl(conffile = "tests/sambatest.ini", conffilebase = "tests/basetest.ini")

    def test_users(self):
        self.l.addUser("usertest", "userpass", "firstname", "sn")
        self.s.addSmbAttr("usertest", "userpass")
        self.assertEqual(self.s.isSmbUser("usertest"), True)
        self.assertEqual(self.s.isEnabledUser("usertest"), True)
        self.assertEqual(self.s.isLockedUser("usertest"), False)
        # Disable and lock
        self.s.disableUser("usertest")
        self.assertEqual(self.s.isEnabledUser("usertest"), False)
        self.s.lockUser("usertest")
        self.assertEqual(self.s.isLockedUser("usertest"), True)
        # Enable and unlock
        self.s.enableUser("usertest")
        self.assertEqual(self.s.isEnabledUser("usertest"), True)
        self.s.unlockUser("usertest")
        self.assertEqual(self.s.isLockedUser("usertest"), False)
        # Delete samba attrs
        self.s.delSmbAttr("usertest")
        self.assertEqual(self.s.isSmbUser("usertest"), False)
       
    def test_groups(self):
        self.s.makeSambaGroup("allusers")
        self.assertEqual(self.s.isSambaGroup("allusers"), True)


if __name__ == "__main__":
    unittest.main()
