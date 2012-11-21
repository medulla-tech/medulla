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
MMC Dashboard general panel
"""

import psutil

from mmc.support.mmctools import size_format
from mmc.plugins.dashboard import Panel

def get_panel():
    return SpacePanel("space")

class SpacePanel(Panel):

    def serialize(self):

        parts = psutil.disk_partitions()
        partitions = []

        for part in parts:
            if not 'loop' in part.mountpoint:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    'device': part.device,
                    'mountpoint': part.mountpoint,
                    'fstype': part.fstype,
                    'opts': part.opts,
                    'usage': {
                        'total': size_format(usage.total),
                        'used': size_format(usage.used),
                        'free': size_format(usage.free),
                        'percent': usage.percent
                    }
                })

        return {
            'partitions': partitions,
        }
