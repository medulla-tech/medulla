# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
MMC Dashboard panels
"""

import os
import socket
import platform
import psutil
from datetime import datetime

import distro

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
        if hasattr(psutil, "boot_time"):
            uptime = str(datetime.now() - datetime.fromtimestamp(psutil.boot_time()))
        else:
            uptime = str(datetime.now() - datetime.fromtimestamp(psutil.BOOT_TIME))

        try:
            dist = distro.linux_distribution()
        except:
            dist = distro.dist()
        return {
            "hostname": socket.gethostname(),
            "dist": dist,
            "load": [str(val) for val in os.getloadavg()],
            "uptime": uptime,
            "users": len(getUsersLdap()),
            "memory": {
                "total": size_format(memory.total),
                "used": size_format(memory.used),
                "available": size_format(memory.available),
                "free": size_format(memory.free),
                "percent": memory.percent,
            },
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
            if "loop" not in part.device and part.mountpoint not in bind_mounts:
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    partitions.append(
                        {
                            "device": part.device,
                            "mountpoint": part.mountpoint,
                            "fstype": part.fstype,
                            "opts": part.opts,
                            "usage": {
                                "total": size_format(usage.total),
                                "used": size_format(usage.used),
                                "free": size_format(usage.free),
                                "percent": usage.percent,
                            },
                        }
                    )
                except OSError:
                    pass
        return {
            "partitions": partitions,
        }


class ProcessPanel(Panel):
    def serialize(self):
        exitcode, stdout, stderr = shlaunch(
            "ps aux | grep 'pulse\|mmc' | grep -v 'defunct' | grep -v 'grep' | awk '{ if ($11 == \"/usr/bin/python\" || $11 == \"python\" || $11 == \"/bin/sh\") print $12; else print $11 }'"
        )
        if exitcode == 0:
            return {
                "process": stdout,
            }
        else:
            return {
                "process": stderr,
            }


class ComputersOnlinePanel(Panel):
    """This class is called by the ComputerOnline widget from the dashboard"""

    pass


class UpdatePanel(Panel):
    """This class is called by the Pulse Update widget from the dashboard"""

    pass


class BackupPanel(Panel):
    """This class is called by the Backup widget from the dashboard"""

    pass


class SuccessRatePanel(Panel):
    """This class is called by the SuccessRate widget from the dashboard"""

    pass


class DeploymentsLaunchedPanel(Panel):
    """This class is called by the DeploymentsLaunched widget from the dashboard"""

    pass


class AgentsPanel(Panel):
    """This class is called by the Agents widget from the dashboard"""

    pass


class AlertsPanel(Panel):
    """This class is called by the Alerts widget from the dashboard"""

    pass


class AlertsEntityPanel(Panel):
    """This class is called by the Alerts Entity widget from the dashboard"""

    pass
