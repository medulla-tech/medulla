# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-2.0-or-later

from sqlalchemy import (
    Column,
    String,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj

Base = declarative_base()


class AdminDBObj(DBObj):
    # All Admin tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Tests(Base, AdminDBObj):
    # ====== Table name =========================
    __tablename__ = "tests"
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(50))
    message = Column(String(255))
