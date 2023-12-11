# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    Enum,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
import datetime

Base = declarative_base()


class GreenitDBObj(DBObj):
    # All greenit tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Tests(Base, GreenitDBObj):
    # ====== Table name =========================
    __tablename__ = "tests"
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(50))
    message = Column(String(255), nullable=True)