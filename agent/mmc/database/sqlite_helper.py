#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sqlite3

class SqliteHelper:
    instances = {}
    path=""
    name = ""
    engine = None
    base = None
    metadata=None
    connect=None

    @classmethod
    def __new__(cls, *args, **kwargs):
        """Use __new__ to create singleton on instances
        Params:
            cls: class reference
            *args: bypass for args
            **kwargs: bypass for options
        Returns:
            Unique instance of the class <cls>
            """
        if cls not in cls.instances:
            cls.instances[cls] = object.__new__(*args, **kwargs)
        return cls.instances[cls]
    
    def open(self):
        """Initialise a new connector"""
        self.connect = sqlite3.connect("%s.db"%os.path.join(self.path, self.name))

    def close(self):
        """Close the connector"""
        if self.connect is not None:
            self.connect.close()
            self.connect = None

    def __init__(self):
        """ Object instanciation, load the sqlalchemy activation if it's not already loaded."""
        pass

    @classmethod
    def _session(self, func):
        """Manage the connection and the session"""
        def wrapper(self, *args, **kwargs):
            self.open()
            session = self.connect.cursor()
            result = func(self, session, *args, **kwargs)
            self.connect.commit()
            session.close()
            self.close()
            return result
        return wrapper
