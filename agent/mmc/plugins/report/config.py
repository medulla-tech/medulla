# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
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

from ConfigParser import NoOptionError, NoSectionError

import os
from mmc.support.config import PluginConfig
from mmc.database.config import DatabaseConfig
from mmc.site import mmcconfdir

reportconfdir = os.path.join(mmcconfdir, 'plugins/report/')


class ReportConfig(PluginConfig, DatabaseConfig):
    def __init__(self, name='report', conffile=None):
        if not hasattr(self, 'initdone'):
            PluginConfig.__init__(self, name, conffile)
            DatabaseConfig.__init__(self)
            self.initdone = True

    def readConf(self):
        PluginConfig.readConf(self)
        DatabaseConfig.setup(self, self.conffile)
        report_img_path = 'file:///etc/mmc/plugins/report/img/'
        try:
            self.historization = self.get('data', 'historization')
        except (NoOptionError, NoSectionError):
            self.historization = '15 22 * * *'
        try:
            self.indicators = self.get('data', 'indicators')
        except (NoOptionError, NoSectionError):
            self.indicators = 'indicators.xml'
        try:
            self.reportTemplate = self.get('data', 'reportTemplate')
        except (NoOptionError, NoSectionError):
            self.reportTemplate = 'default.xml'
        try:
            self.reportCSS = os.path.join(reportconfdir, 'css', self.get('data', 'reportCSS'))
        except (NoOptionError, NoSectionError, OSError):
            self.reportCSS = os.path.join(reportconfdir, 'css', 'style.css')
        try:
            self.graphCSS = [os.path.join(reportconfdir, 'css', f) for f in self.get('data', 'graphCSS').replace(' ', '').split(',')]
        except (NoOptionError, NoSectionError, OSError):
            self.graphCSS = []
        try:
            self.company = self.get('pdfvars', 'company')
        except (NoOptionError, NoSectionError):
            self.company = 'Company'
        try:
            self.company_logo_path = report_img_path + self.get('pdfvars', 'company_logo_path')
        except (NoOptionError, NoSectionError):
            self.company_logo_path = report_img_path + 'mandriva.png'
        try:
            self.pulse_logo_path = report_img_path + self.get('pdfvars', 'pulse_logo_path')
        except (NoOptionError, NoSectionError):
            self.pulse_logo_path = report_img_path + 'pulse.png'
