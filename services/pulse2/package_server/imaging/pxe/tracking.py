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

from pulse2.utils import Singleton
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

    def __contains__(self, mac):
        return mac in self.entries

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

