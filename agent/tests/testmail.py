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
import os
import time

from lmc.plugins.base import ldapUserGroupControl
from lmc.plugins.mail import MailControl

def cleanLdap():
    # Wipe out /home
    os.system("rm -fr /home/*")
    # Wipe out LDAP
    os.system("/etc/init.d/slapd stop")
    os.system("killall -9 slapd")
    os.system("rm -f /var/lib/ldap/*")
    os.system("cp contrib/ldap/*.schema /etc/ldap/schema")    
    os.system("dpkg-reconfigure -pcritical slapd")
    os.system("cp contrib/ldap/slapd.conf /etc/ldap")
    os.system("/etc/init.d/slapd restart")
    time.sleep(5)
    # Create Base OU
    l = ldapUserGroupControl("tests/basetest.ini")
    l.addOu("Groups", "dc=linbox,dc=com")
    l.addOu("Users",  "dc=linbox,dc=com")
    l.addGroup("allusers")


class TestMailControl(unittest.TestCase):

    def setUp(self):
        cleanLdap()
        self.m = MailControl(conffilebase = "tests/basetest.ini")

    def test_MailControl(self):
        self.m.addUser("usertest", "userpass", "test", "test")
        self.m.addMailObjectClass("usertest", "usertestmail")
        self.assertEqual(self.m.hasMailObjectClass("usertest"), True)
        self.m.removeUserObjectClass("usertest", "mailAccount")
        self.assertEqual(self.m.hasMailObjectClass("usertest"), False)

if __name__ == "__main__":
    unittest.main()
