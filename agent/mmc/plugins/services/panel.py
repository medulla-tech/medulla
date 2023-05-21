# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
MMC services dasboard panel
"""

from mmc.plugins.dashboard.panel import Panel
from mmc.plugins.services import ServiceManager


class ServicesPanel(Panel):
    def serialize(self):
        data = {}
        for plugin, services in list(ServiceManager().list_plugins_services().items()):
            for service in services:
                if service["active_state"] not in ("active", "unavailable"):
                    if plugin not in data:
                        data[plugin] = []
                    data[plugin].append(service)
        return data


class SystemPanel(Panel):
    pass
