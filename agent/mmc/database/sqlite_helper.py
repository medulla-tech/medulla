#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from sqlalchemy.orm import Session
from sqlalchemy import (
    create_engine,
    MetaData,
)

class SqliteHelper:
    instances = {}
    path=""
    is_activated = False
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
    
    @classmethod
    def activate(cls):
        """Activate sqlalchemy engine for the common part of all the child classes.
        /!\ Need cls.path and cls.name to be defined on the child class
        Params:
            cls: reference to the object
        """

        cls.engine = create_engine(f"sqlite:///{os.path.join(cls.path, cls.name)}.db")
        cls.metadata = MetaData()

    def __init__(self):
        """ Object instanciation, load the sqlalchemy activation if it's not already loaded. """
        if self.is_activated is False:
            self.activate()

    @classmethod
    @property
    def session(cls):
        """Simplify the creation of session, by calling self.session as an attribute"""
        return Session(cls.engine)