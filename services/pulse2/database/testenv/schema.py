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

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime,Text, LargeBinary, Enum
from sqlalchemy.dialects.mysql import  TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class TestenvDBObj(DBObj):
    # All Testenv tables have id colmun as primary key
    id = Column(Integer, primary_key=True)


class Tests(Base, TestenvDBObj):
    # ====== Table name =========================
    __tablename__ = 'tests'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    name = Column(String(50))
    message = Column(String(255))


class Machines(Base, TestenvDBObj):
    # ====== Table name =========================
    __tablename__ = 'machines'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    id = Column('id_machines', Integer, primary_key=True)
    uuid_machine = Column(String(100), nullable=False, default="")
    nom = Column(String(100), nullable=False, default="")
    plateform = Column(String(60), nullable=False, default="")
    architecture = Column(String(45),  nullable=False, default="")
    cpu = Column(Integer, nullable=False, default=0)
    ram = Column(Integer, nullable=False, default=0)
    state = Column(String(50), nullable=False, default="")
    persistent = Column(String(50), nullable=False, default="")
    has_guacamole = relationship('Has_guacamole', cascade='all, delete')

class Has_guacamole(Base, TestenvDBObj):
    # ====== Table name =========================
    __tablename__ = 'has_guacamole'
    # ====== Fields =============================
    # Here we define columns for the table version.
    # Notice that each column is also a normal Python instance attribute.
    id = Column('id_guac', Integer, primary_key=True)
    idguacamole = Column(String(100), nullable=False, default="")
    protocol = Column(String(10), nullable=False, default="")
    port = Column(Integer, nullable=False, default=0)
    machine_name = Column(String(50), nullable=False, default="")
    id_machines = Column(Integer, ForeignKey('machines.id_machines'), nullable=False, default=0)
