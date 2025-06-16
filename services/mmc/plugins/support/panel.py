# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText:2007-2014 Mandriva, http://www.mandriva.com
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.plugins.dashboard.panel import Panel

class LicensePanel(Panel):
    data = None

    def data_handler(self, data):
        """
        A reference method to actualize by JSON query.

        @param data: info from the license server
        @type data: dict
        """
        self.data = data

    def serialize(self):
        return self.data
