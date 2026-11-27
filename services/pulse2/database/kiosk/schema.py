# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    Enum,
)
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj

Base = declarative_base()


class KioskDBObj(DBObj):
    # All Kiosk tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Profiles(Base, KioskDBObj):
    # ====== Table name =========================
    __tablename__ = "profiles"
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(50))
    owner = Column(String(255))
    entity_id = Column(INTEGER(unsigned=True), nullable=True)
    source = Column(String(50))
    active = Column(TINYINT)
    creation_date = Column(DateTime)


class Profile_has_package(Base, KioskDBObj):
    # ====== Table name =========================
    __tablename__ = "package_has_profil"
    # ====== Fields =============================
    package_uuid = Column(String(255), nullable=False)
    profil_id = Column(Integer, nullable=False)
    package_status = Column(Enum("allowed", "restricted"))


class Profile_has_ou(Base, KioskDBObj):
    # ====== Table name =========================
    __tablename__ = "profile_has_ous"
    # ====== Fields =============================
    profile_id = Column(Integer, nullable=False)
    ou = Column(Text)

