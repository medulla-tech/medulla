# -*- coding: utf-8; -*-
#
# (c) 2018-2022 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime,Text, LargeBinary, Enum
from sqlalchemy.dialects.mysql import  TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime


Base = declarative_base()


class KioskDBObj(DBObj):
    # All Kiosk tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Profiles(Base, KioskDBObj):
    # ====== Table name =========================
    __tablename__ = 'profiles'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(50))
    active = Column(TINYINT)
    creation_date = Column(DateTime)


class Packages(Base, KioskDBObj):
    # ====== Table name =========================
    __tablename__ = 'package'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(45))
    version_package = Column(String(45))
    software = Column(String(45))
    description = Column(String(200), nullable=True)
    version_software = Column(String(45))
    package_uuid = Column(String(45), unique=True)
    os = Column(String(45))


class Profile_has_package(Base, KioskDBObj):
    # ====== Table name =========================
    __tablename__ = 'package_has_profil'
    # ====== Fields =============================
    package_uuid = Column(String(255), nullable=False)
    profil_id = Column(Integer, nullable=False)
    package_status = Column(Enum('allowed','restricted'))


class Profile_has_ou(Base, KioskDBObj):
    # ====== Table name =========================
    __tablename__ = 'profile_has_ous'
    # ====== Fields =============================
    profile_id = Column(Integer, nullable=False)
    ou = Column(Text)

class Acknowledges(Base, KioskDBObj):
    __tablename__ = 'acknowledges'
    id_package_has_profil = Column(Integer, nullable=False)
    askuser = Column(String(255), nullable=False)
    askdate = Column(DateTime, default=datetime.datetime.now, nullable=False)
    acknowledgedbyuser = Column(String(255), nullable=True)
    startdate = Column(DateTime, default=datetime.datetime.now, nullable=False)
    enddate = Column(DateTime, nullable=True)
    status = Column(Enum('waiting', 'accepted', 'rejected'), nullable=False, default="waiting")
