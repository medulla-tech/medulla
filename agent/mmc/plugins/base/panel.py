# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
MMC base dasboard panels
"""

from mmc.plugins.dashboard.panel import Panel
from mmc.plugins.base.subscription import SubscriptionManager


class SupportPanel(Panel):
    def serialize(self):
        return SubscriptionManager().getInformations(True)
