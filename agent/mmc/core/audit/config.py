# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Configuration classes for the audit module.
"""


class AuditConfig:

    """
    Parse the audit system configuration file.
    """

    def readAuditConf(self, section="audit"):
        if self.has_section(section):
            self.auditmethod = self.get(section, "method")
            if self.auditmethod == "database":
                self.auditdbhost = self.get(section, "dbhost")
                self.auditdbport = self.getint(section, "dbport")
                self.auditdbuser = self.get(section, "dbuser")
                self.auditdbpassword = self.getpassword(section, "dbpassword")
                self.auditdbname = self.get(section, "dbname")
                self.auditdbdriver = self.get(section, "dbdriver")
