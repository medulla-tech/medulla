#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

""" Tracking of selected menu entries. """

import time
import logging

from pulse2.utils import Singleton, SingletonN
from pulse2.package_server.imaging.pxe.parser import LOG_ACTION, LOG_STATE

class TrackingContainer(Singleton):
    """ A container to store choosen menu entry. """

    entries = {}

    def add(self, mac, entry):
        """
        Add the menu entry

        @param mac: MAC address of client machine
        @type mac: str

        @param entry: Menu entry order
        @type entry: int
        """
        self.entries[mac] = entry, False

    def get(self, mac):
        """
        Get the menu entry

        @param mac: MAC address of client machine
        @type mac: str

        @return: menu entry and mark flag
        @rtype: tuple
        """
        if mac in self.entries :
            return self.entries[mac]

    def mark(self, mac):
        """
        Entry flagging

        @param mac: MAC address of client machine
        @type mac: str
        """
        if mac in self.entries :
            entry, flag = self.entries[mac]
            self.entries[mac] = entry, True

    def delete(self, mac):
        """
        Delete the menu entry

        @param mac: MAC address of client machine
        @type mac: str
        """
        if mac in self.entries :
            del self.entries[mac]

    def __contains__(self, entry):
        return entry in self.entries

CHOOSEN_MENU_ENTRY = LOG_ACTION[1][1]

class EntryTracking(TrackingContainer):
    """
    Each record is identified by MAC address of booted machine,
    number of menu entry as first parameter.
    Second parameter confirms that menu entry is a choice of backup
    or restore.

    The entries are added by extracting of log message from logCientAction,
    which reports all client activities.

    """

    def search_and_extract(self, mac, phase, message):
        """
        Log message extract

        @param mac: MAC address
        @type mac: str

        @param phase: step of imaging workflow
        @type phase: str

        @param message: displayed message
        @type message: str
        """
        if phase == LOG_STATE.MENU and CHOOSEN_MENU_ENTRY in message:
            entry = message.replace(CHOOSEN_MENU_ENTRY, "").replace(":","").strip()
            if entry.isdigit() :
                num = int(entry)
                self.add(mac, num)

        if phase in (LOG_STATE.BACKUP, LOG_STATE.RESTO):
            self.mark(mac)


class MTFTPTracker(object):
    __metaclass__ = SingletonN

    GRP_TIMEOUT = 3600

    FIRST_DELAY = 10
    last_file = 0
    last_time = 0

    def __init__(self):
        self.last_file = 0
        self.last_time = 0


    def get_delay(self, mac, file, timeout):
        wait = 0
        try:
            now = time.time()
            logging.getLogger().debug("PXE Proxy: MTFTP Tracker file: %d last_file: %d last_time: %s" % (file, self.last_file, self.last_time))
            if now - self.last_time > self.GRP_TIMEOUT:
                self.last_time = 0
                self.last_file = 0

            if file == self.last_file:
                wait = timeout + (self.last_time - now)
                if wait < 0:
                    wait = 0
            elif file < self.last_file:
                wait = 0
            elif file > self.last_file:
                wait = timeout
                if self.last_time == 0:
                    wait = wait + 10 # 1st wait after a boot
                self.last_file = file
                self.last_time = now

            logging.getLogger().debug("PXE Proxy: MTFTP Tracker file: %d for MAC: %s delay = %s" % (file, mac, str(wait)))
            return int(wait)

        except Exception, e:
            logging.getLogger().warn("PXE Proxy: MTFTP Tracker failed: %s" % str(e))

