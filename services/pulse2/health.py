# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
    Give stats on-the-fly
"""

import os
import logging
from stat import S_IFSOCK, S_IFLNK, S_IFREG, S_IFBLK, S_IFDIR, S_IFCHR, S_IFIFO


def basicHealth():
    """
    Compute a health indicator as a dict with this keys:
     - usedmem : the used memory in Bytes
     - freemem : the free memory in Bytes
     - avgload : the average load (1 minute)

    @rtype: dict
    @returns: a dict containing the indicators
    """
    total, free, swapused = getMem()
    return {"loadavg": getLoadAvg(), "fd": getFDSummary(), "memory": getMem()}


def getFDSummary():
    result = {
        "socket": 0,
        "symlink": 0,
        "file": 0,
        "block": 0,
        "folder": 0,
        "char": 0,
        "fifo": 0,
        "other": 0,
    }

    for fd in range(0, os.sysconf("SC_OPEN_MAX") - 1):
        try:
            statinfo = os.fstat(fd)
        except OSError:
            # not a good fd
            continue
        if statinfo.st_mode & S_IFSOCK == S_IFSOCK:
            result["socket"] += 1
        elif statinfo.st_mode & S_IFLNK == S_IFLNK:
            result["symlink"] += 1
        elif statinfo.st_mode & S_IFREG == S_IFREG:
            result["file"] += 1
        elif statinfo.st_mode & S_IFBLK == S_IFBLK:
            result["block"] += 1
        elif statinfo.st_mode & S_IFDIR == S_IFDIR:
            result["folder"] += 1
        elif statinfo.st_mode & S_IFCHR == S_IFCHR:
            result["char"] += 1
        elif statinfo.st_mode & S_IFIFO == S_IFIFO:
            result["fifo"] += 1
        else:
            result["other"] += 1

    return result


def getLoadAvg():
    try:
        f = open("/proc/loadavg")
    except IOError as e:
        logging.getLogger().error(
            "error opening /proc/loadavg: %d (%s)" % (e.errno, e.strerror)
        )
        ret = {"1min": 0, "5min": 0, "15min": 0}
        return ret

    data = f.read()
    f.close()
    loadavg = {
        "1min": float(data.split()[0]),
        "5min": float(data.split()[1]),
        "15min": float(data.split()[2]),
    }
    return loadavg


def getMem():
    total = 0
    cached = 0
    buffers = 0
    swap_total = 0
    swap_free = 0
    try:
        meminfo = open("/proc/meminfo")
    except IOError as e:
        logging.getLogger().error(
            "error opening /proc/meminfo: %d (%s)" % (e.errno, e.strerror)
        )
        ret = {"total": 0, "free": 0, "swapused": 0}
        return ret

    for line in meminfo:
        if line.startswith("MemTotal:"):
            total = int(line.split()[1])
        elif line.startswith("Cached:"):
            cached = int(line.split()[1])
        elif line.startswith("Buffers:"):
            buffers = int(line.split()[1])
        elif line.startswith("SwapTotal:"):
            swap_total = int(line.split()[1])
        elif line.startswith("SwapFree:"):
            swap_free = int(line.split()[1])
    meminfo.close()
    ret = {
        "total": total,
        "free": total - cached - buffers,
        "swapused": swap_total - swap_free,
    }

    return ret  # return is always in kB
