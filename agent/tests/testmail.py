#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import unittest
import os
import time

from mmc.plugins.base import ldapUserGroupControl
from mmc.plugins.mail import MailControl

def cleanLdap():
    # Wipe out /home
    os.system("rm -fr /home/*")
    # Wipe out LDAP
    os.system("/etc/init.d/slapd stop")
    os.system("killall -9 slapd")
    os.system("rm -f /var/lib/ldap/*")
    os.system("rm -fr /var/backups/*.ldapdb")
    os.system("cp contrib/ldap/*.schema /etc/ldap/schema")
    os.system("echo slapd slapd/password1 string secret | debconf-set-selections")
    os.system("echo slapd slapd/password2 string secret | debconf-set-selections")
    os.system("dpkg-reconfigure -pcritical slapd")
    os.system("cp contrib/ldap/slapd.conf /etc/ldap")
    os.system("/etc/init.d/slapd restart")
    time.sleep(5)
    # Create Base OU
    l = ldapUserGroupControl("tests/basetest.ini")
    l.addOu("Groups", "dc=mandriva,dc=com")
    l.addOu("Users",  "dc=mandriva,dc=com")
    l.addOu("mailDomains", "dc=mandriva,dc=com")
    l.addGroup("allusers")


class TestMailControl(unittest.TestCase):

    def setUp(self):
        cleanLdap()
        self.m = MailControl(conffile = "tests/vdomaintest.ini", conffilebase = "tests/basetest.ini")

    def test_MailControl(self):
        self.m.addUser("usertest", "userpass", "test", "test")
        self.m.addMailObjectClass("usertest", "usertestmail")
        self.assertEqual(self.m.hasMailObjectClass("usertest"), True)
        self.m.removeUserObjectClass("usertest", "mailAccount")
        self.assertEqual(self.m.hasMailObjectClass("usertest"), False)


class TestMailControlVDomain(unittest.TestCase):

    def setUp(self):
        cleanLdap()
        self.m = MailControl(conffile = "tests/vdomaintest.ini", conffilebase = "tests/basetest.ini")

    def test_MailControl(self):
        self.m.addUser("usertest", "userpass", "test", "test", "/home/mail/usertest", False)
        self.m.addMailObjectClass("usertest", "usertestmail")
        d = self.m.getDetailedUser("usertest")
        self.assertEqual(d["mailbox"][0], "/home/mail/usertest/Maildir")
        self.assertEqual(self.m.hasMailObjectClass("usertest"), True)
        self.m.removeUserObjectClass("usertest", "mailAccount")
        self.assertEqual(self.m.hasMailObjectClass("usertest"), False)

    def test_VDomains(self):
        self.assertEqual(len(self.m.getVDomains("")), 0)
        self.m.addVDomain("mandriva.com")
        self.assertEqual(len(self.m.getVDomains("")), 1)
        self.assertEqual(len(self.m.getVDomain("mandriva.com")), 1)
        self.assertEqual(self.m.getVDomain("mandriva.com")[0][1]["virtualdomain"], ["mandriva.com"])
        self.m.setVDomainDescription("mandriva.com", "test")
        self.assertEqual(self.m.getVDomain("mandriva.com")[0][1]["virtualdomaindescription"], ["test"])
        self.assertEqual(self.m.getVDomainUsersCount("mandriva.com"), 0)

        self.m.addUser("usertest", "userpass", "test", "test")
        self.m.addMailObjectClass("usertest", "usertestmail")
        self.assertEqual(self.m.getVDomainUsersCount("mandriva.com"), 1)
        self.assertEqual(self.m.getVDomainUsers("mandriva.com", ""), [('uid=usertest,ou=Users,dc=mandriva,dc=com', {'mail': ['TEST.TEST@mandriva.com'], 'givenName': ['test'], 'uid': ['usertest'], 'sn': ['test']})])

        self.m.delVDomain("mandriva.com")
        self.assertEqual(len(self.m.getVDomains("")), 0)


if __name__ == "__main__":
    unittest.main()
