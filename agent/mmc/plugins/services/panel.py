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

"""
MMC services dasboard panel
"""

from mmc.plugins.dashboard.panel import Panel
from mmc.plugins.services import ServiceManager

class ServicesPanel(Panel):

    def serialize(self):
        data = {}
        for plugin, services in ServiceManager().list_plugins_services().items():
            for service in services:
                if service['active_state'] not in ("active", "unavailable"):
                    if plugin not in data:
                        data[plugin] = []
                    data[plugin].append(service)
        return data


class SystemPanel(Panel):
    pass
