# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Define the audit writer interface, and an audit writer that does nothing (used
when audit is disabled)
"""

import logging

from mmc.support.mmctools import Singleton


class AuditWriterI:
    """
    Interface for classes that writes record entry to the audit database.
    """

    def __init__(self):
        self.logger = logging.getLogger()

    def log(self):
        """
        To write a record to the database.
        """
        pass

    def setup(self):
        pass

    def get(self):
        pass

    def getById(self):
        pass

    def getLog(self, start, end, plug, user, type, date1, date2, object, action):
        pass

    def getLogById(self, id):
        pass

    def getActionType(self):
        """
        Return a list of action and type if action=1 it return list of action
        if type=1 it return a list of type

        @param action: if action=1 the function return a list of action
        @type action: int
        @param type: if type=1 the function return a list of action
        @type type: int
        """
        pass

    def commit(self):
        pass


class AuditWriterNull(Singleton, AuditWriterI):

    """
    Singleton class for an object that don't record any audit data.
    It is used when audit has not been configured.
    """

    def __init__(self):
        self.logger = logging.getLogger()

    def init(self, *args):
        pass

    def log(self, *args):
        return self

    def setup(self, *args):
        pass

    def get(self, *args):
        pass

    def getById(self, *args):
        pass

    def getLog(self, start, end, plug, user, type, date1, date2, object, action):
        pass

    def getLogById(self, id):
        pass

    def getActionType(self, *args):
        pass

    def commit(self, *args):
        pass

    def operation(self, op):
        self.logger.info("Configured audit database will do nothing")
        return True
