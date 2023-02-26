# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

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
        #########################################################

        self.leak_memorytime = 3600
        if self.has_option("memoryinfo", "time"):
            self.leak_memorytime = self.getint("memoryinfo", "time")
        self.fileoutresult = "/tmp/leak_memory.data"
        if self.has_option("memoryinfo", "outfile"):
            self.fileoutresult   = self.get("memoryinfo", "outfile")
        self.leak_memory_disable = True
        if self.has_option("memoryinfo", "disable"):
            self.leak_memory_disable = self.getboolean("memoryinfo", "disable")

    def setDefault(self):
        PluginConfig.setDefault(self)
        self.authmethod = "baseldap"
        self.provmethod = None
        self.computersmethod = "none"
        self.passwordscheme = "ssha"
        self.auditmethod = "none"
