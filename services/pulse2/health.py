# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
"""
    Give stats on-the-fly
"""

import os
from stat import * # for S_*

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
    return {
        "loadavg" : getLoadAvg(),
        "fd": getFDSummary(),
        "memory": getMem()
    }

def getFDSummary():

    result =  {
        'socket': 0,
        'symlink': 0,
        'file': 0,
        'block': 0,
        'folder': 0,
        'char': 0,
        'fifo': 0,
        'other': 0,
    }

    for fd in range(0, os.sysconf('SC_OPEN_MAX') - 1):
        try:
            statinfo = os.fstat(fd)
        except OSError:
            # not a good fd
            continue
        if statinfo.st_mode & S_IFSOCK == S_IFSOCK:
            result['socket'] += 1
        elif statinfo.st_mode & S_IFLNK == S_IFLNK:
            result['symlink'] += 1
        elif statinfo.st_mode & S_IFREG == S_IFREG:
            result['file'] += 1
        elif statinfo.st_mode & S_IFBLK == S_IFBLK:
            result['block'] += 1
        elif statinfo.st_mode & S_IFDIR == S_IFDIR:
            result['folder'] += 1
        elif statinfo.st_mode & S_IFCHR == S_IFCHR:
            result['char'] += 1
        elif statinfo.st_mode & S_IFIFO == S_IFIFO:
            result['fifo'] += 1
        else:
            result['other'] += 1

    return result

def getLoadAvg():
    f = open("/proc/loadavg")
    data = f.read()
    f.close()
    loadavg = float(data.split()[0])
    return loadavg

def getMem():
    total = 0
    free = 0
    cached = 0
    buffers = 0
    swap_total = 0
    swap_free = 0
    meminfo = open("/proc/meminfo")
    for line in meminfo:
        if line.startswith("MemTotal:"):
            total = int(line.split()[1])
        elif line.startswith("MemFree:"):
            free = int(line.split()[1])
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
        'total': total,
        'free': total-cached-buffers,
        'swapused': swap_total-swap_free
    }

    return ret # return is always in kB
