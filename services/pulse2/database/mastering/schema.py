# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime,Text, LargeBinary, Enum
from sqlalchemy.dialects.mysql import  TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime


Base = declarative_base()


class MasteringDBObj(DBObj):
    # All Mastering tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Tests(Base, MasteringDBObj):
    # ====== Table name =========================
    __tablename__ = 'tests'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(50))
    message = Column(String(255))

