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
Configuration class for the MMC base plugin.
"""

from mmc.support.config import PluginConfig
from mmc.plugins.base.ldapconnect import LDAPConnectionConfig
from mmc.plugins.base.subscription import SubscriptionConfig
from mmc.core.audit.config import AuditConfig

class BasePluginConfig(PluginConfig, LDAPConnectionConfig, AuditConfig, SubscriptionConfig):

    def readConf(self):
        PluginConfig.readConf(self)
        LDAPConnectionConfig.readLDAPConf(self, "ldap")
        AuditConfig.readAuditConf(self, "audit")
        # Selected authentication method
        try:
            self.authmethod = self.get("authentication", "method")
        except:
            pass
        # Selected provisioning method
        try:
            self.provmethod = self.get("provisioning", "method")
        except:
            pass
        # Selected computer management method
        try:
            self.computersmethod = self.get("computers", "method")
        except:
            pass
        # User password scheme
        try:
            self.passwordscheme = self.get("ldap", "passwordscheme")
        except:
            pass

        self.baseDN = self.getdn('ldap', 'baseDN')
        self.baseUsersDN = self.getdn('ldap', 'baseUsersDN')

        # Where LDAP computer objects are stored
        # For now we ignore if the option does not exist, because it breaks
        # all existing intallations
        try:
            self.baseComputersDN = self.get('ldap', 'baseComputersDN')
        except:
            pass
        self.backuptools = self.get("backup-tools", "path")
        self.backupdir = self.get("backup-tools", "destpath")
        self.username = self.getdn("ldap", "rootName")
        self.password = self.getpassword("ldap", "password")

    def setDefault(self):
        PluginConfig.setDefault(self)
        self.authmethod = "baseldap"
        self.provmethod = None
        self.computersmethod = "none"
        self.passwordscheme = "ssha"
        self.auditmethod = "none"
