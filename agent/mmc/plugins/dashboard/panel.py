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
MMC Dashboard panels
"""

import os
import socket
import platform
import psutil
from datetime import datetime

from mmc.support.mmctools import size_format, shlaunch
from mmc.plugins.base import getUsersLdap


class Panel(object):

    def __init__(self, id):
        self.id = id

    def serialize(self):
        return {}


class ShortcutsPanel(Panel):
    pass


class GeneralPanel(Panel):

    def serialize(self):
        memory = psutil.virtual_memory()
        try:
            dist = platform.linux_distribution()
        except:
            dist = platform.dist()
        return {
            'hostname': socket.gethostname(),
            'dist': dist,
            'load': [str(val) for val in os.getloadavg()],
            'uptime': str(datetime.now() - datetime.fromtimestamp(psutil.BOOT_TIME)),
            'users': len(getUsersLdap()),
            'memory': {
                'total': size_format(memory.total),
                'used': size_format(memory.used),
                'available': size_format(memory.available),
                'free': size_format(memory.free),
                'percent': memory.percent
            }
        }


class SpacePanel(Panel):

    def serialize(self):

        parts = psutil.disk_partitions()
        partitions = []

        # get --bind mounts
        bind_mounts = []
        exitcode, stdout, stderr = shlaunch("findmnt -nr | fgrep [ | cut -d' ' -f1")
        if exitcode == 0:
            bind_mounts = stdout

        for part in parts:
            if 'loop' not in part.device and part.mountpoint not in bind_mounts:
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
