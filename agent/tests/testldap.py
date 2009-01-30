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

import sys
import os
import os.path
import time

from mmc.plugins.base import ldapUserGroupControl
from mmc.plugins.base import ldapAuthen

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

class TestEmptyLdap(unittest.TestCase):

    def setUp(self):
        cleanLdap()
        self.l = ldapUserGroupControl("tests/basetest.ini")

    def test_empty(self):
        self.assertEqual(self.l.searchUser(), [])
        self.assertEqual(self.l.searchGroup(), {})
        self.assertEqual(self.l.existUser("usertest"), False)
        self.assertEqual(self.l.existUser(""), False)
        self.assertEqual(self.l.existGroup("group"), False)
        self.assertEqual(self.l.existGroup(""), False)
        self.assertEqual(self.l.maxUID(), 10000)
        self.assertEqual(self.l.maxGID(), 10000)

class TestManageUserGroup(unittest.TestCase):

    def setUp(self):
        cleanLdap()
        self.l = ldapUserGroupControl("tests/basetest.ini")
        self.assertEqual(self.l.addGroup("allusers"), 10001)

    def test_addDelUser(self):
        self.assertEqual(self.l.addUser("usertest", "userpass", u"ùnïcôde", u"çàùôéé"), 0)

        self.assertEqual(ldapAuthen("usertest", "userpass", "tests/basetest.ini").isRightPass(), True)
        self.assertEqual(ldapAuthen("usertest", "userbadpass", "tests/basetest.ini").isRightPass(), False)
        
        self.assertEqual(os.path.exists("/home/usertest"), True)
        self.assertEqual(len(self.l.searchUser()), 1)
        self.assertEqual(len(self.l.searchUser("usertest")), 1)
        self.assertEqual(len(self.l.searchUser("usertestfoo")), 0)
        self.assertEqual(len(self.l.searchGroup()), 1)
        self.assertEqual(len(self.l.searchGroup("allusers")), 1)
        self.assertEqual(len(self.l.searchGroup("usertestfoo")), 0)

        self.assertEqual(self.l.getMembers("allusers"), ["usertest"])
        self.assertEqual(self.l.isEnabled("usertest"), True)
        self.assertEqual(self.l.getAllGroupsFromUser("usertest"), ["allusers"])

        self.assertEqual(os.path.exists("tmp/base_add_user_usertestuserpass"), True)

        self.assertEqual(self.l.delUser("usertest", 1), 0)
        self.assertEqual(os.path.exists("/home/usertest"), False)
        self.assertEqual(len(self.l.searchUser()), 0)
	self.l.delGroup("allusers")
        self.assertEqual(len(self.l.searchGroup()), 0)
        self.assertEqual(os.path.exists("tmp/base_del_user_usertest"), True)

    def test_addDelGroup(self):
        self.assertEqual(self.l.addGroup("grouptest"), 10002)
        self.assertEqual(len(self.l.searchGroup()), 2)
        self.assertEqual(len(self.l.searchUser()), 0)
        self.assertEqual(len(self.l.searchGroup("grouptest")), 1)
        self.assertEqual(len(self.l.searchGroup("grouptestfoo")), 0)
        self.assertEqual(self.l.getMembers("grouptest"), [])
	self.assertEqual(self.l.delGroup("grouptest"), None)
        self.assertEqual(len(self.l.searchGroup("grouptest")), 0)
        self.assertEqual(len(self.l.searchGroup()), 1)

    def test_addUserToGroup(self):
        self.assertEqual(self.l.addUser("usertest", "userpass", u"ùnïcôde", u"çàùôéé"), 0)
        self.assertEqual(self.l.addGroup("grouptest"), 10002)
        self.assertEqual(self.l.addUserToGroup("grouptest", "usertest"), 0)
        self.assertEqual(self.l.getMembers("grouptest"), ["usertest"])
        self.assertEqual(len(self.l.getUserGroups("usertest")), 2)
        self.assertEqual(self.l.delUser("usertest", 1), 0)

    def test_userdefault(self):
        self.l.addUser("usertest", "userpass", u"Héléonôre", u"Rêve")
        d = self.l.getDetailedUser("usertest")
        self.assertEqual(d["mail"][0], "HELEONORE.REVE@mandriva.com")
        self.assertEqual(d["displayName"][0], u"héléonôre rêve".encode("utf-8"))
        self.assertEqual(d["cn"][0], u"Héléonôre Rêve".encode("utf-8"))
        self.assertEqual("shadowExpire" in d, False)
        self.assertEqual("lmcUserObject" in d["objectClass"], True)
        self.assertEqual(d["lmcACL"][0], ":base#users#passwd/")

if __name__ == "__main__":
    cleanLdap()
    unittest.main()

