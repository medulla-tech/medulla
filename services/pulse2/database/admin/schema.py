# -*- coding: utf-8; -*-
#
# (c) 2020 siveo, http://www.siveo.net
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
