#!/usr/bin/python3
# -*- coding: utf-8; -*-

# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
""" Tracking of selected menu entries. """

from pulse2.utils import Singleton
from pulse2.package_server.imaging.pxe.parser import LOG_ACTION, LOG_STATE


class TrackingContainer(Singleton):
    """A container to store choosen menu entry."""

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
        if mac in self.entries:
            return self.entries[mac]

    def mark(self, mac):
        """
        Entry flagging

        @param mac: MAC address of client machine
        @type mac: str
        """
        if mac in self.entries:
            entry, flag = self.entries[mac]
            self.entries[mac] = entry, True

    def delete(self, mac):
        """
        Delete the menu entry

        @param mac: MAC address of client machine
        @type mac: str
        """
        if mac in self.entries:
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
            entry = message.replace(CHOOSEN_MENU_ENTRY, "").replace(":", "").strip()
            if entry.isdigit():
                num = int(entry)
                self.add(mac, num)

        if phase in (LOG_STATE.BACKUP, LOG_STATE.RESTO):
            self.mark(mac)
