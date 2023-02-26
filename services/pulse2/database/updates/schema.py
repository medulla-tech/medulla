# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-2.0-or-later

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime,Text, LargeBinary, Enum
from sqlalchemy.dialects.mysql import  TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime


Base = declarative_base()


class UpdatesDBObj(DBObj):
    # All Updates tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Tests(Base, UpdatesDBObj):
    # ====== Table name =========================
    __tablename__ = 'tests'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(50))
    message = Column(String(255))

