# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

from configparser import NoOptionError, NoSectionError

import os
from mmc.support.config import PluginConfig
from mmc.database.config import DatabaseConfig
from mmc.site import mmcconfdir

reportconfdir = os.path.join(mmcconfdir, "plugins/report/")


class ReportConfig(PluginConfig, DatabaseConfig):
    def __init__(self, name="report", conffile=None):
        if not hasattr(self, "initdone"):
            PluginConfig.__init__(self, name, conffile)
            DatabaseConfig.__init__(self)
            self.initdone = True

    def readConf(self):
        PluginConfig.readConf(self)
        DatabaseConfig.setup(self, self.conffile)
        report_img_path = "file:///etc/mmc/plugins/report/img/"
        try:
            self.historization = self.get("data", "historization")
        except (NoOptionError, NoSectionError):
            self.historization = "15 22 * * *"
        try:
            self.indicators = self.get("data", "indicators")
        except (NoOptionError, NoSectionError):
            self.indicators = "indicators.xml"
        try:
            self.reportTemplate = self.get("data", "reportTemplate")
        except (NoOptionError, NoSectionError):
            self.reportTemplate = "default.xml"
        try:
            self.reportCSS = os.path.join(
                reportconfdir, "css", self.get("data", "reportCSS")
            )
        except (NoOptionError, NoSectionError, OSError):
            self.reportCSS = os.path.join(reportconfdir, "css", "style.css")
        try:
            self.graphCSS = [
                os.path.join(reportconfdir, "css", f)
                for f in self.get("data", "graphCSS").replace(" ", "").split(",")
            ]
        except (NoOptionError, NoSectionError, OSError):
            self.graphCSS = []
        try:
            self.company = self.get("pdfvars", "company")
        except (NoOptionError, NoSectionError):
            self.company = "Company"
        try:
            self.company_logo_path = report_img_path + self.get(
                "pdfvars", "company_logo_path"
            )
        except (NoOptionError, NoSectionError):
            self.company_logo_path = report_img_path + "mandriva.png"
        try:
            self.pulse_logo_path = report_img_path + self.get(
                "pdfvars", "pulse_logo_path"
            )
        except (NoOptionError, NoSectionError):
            self.pulse_logo_path = report_img_path + "pulse.png"
