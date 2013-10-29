# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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

from importlib import import_module
import logging

from sqlalchemy import Column, String, Text, Integer, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base; Base = declarative_base()

from mmc.database.database_helper import DBObj


class ReportingData(Base, DBObj):
    # ====== Table name =========================
    __tablename__ = 'data'
    # ====== Fields =============================
    id = Column(Integer, primary_key=True)
    indicator_id = Column(Integer)
    timestamp = Column(BigInteger)
    value = Column(String(255))
    entity_id = Column(String(50))


class Indicator(Base, DBObj):
    # ====== Table name =========================
    __tablename__ = 'indicators'
    # ====== Fields =============================
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    label = Column(String(255))
    module = Column(String(255))
    request_function = Column(String(255))
    params = Column(String(255))
    active = Column(Integer)
    keep_history = Column(Integer)


    def getCurrentValue(self):
        report = import_module('.'.join(['mmc.plugins', self.module, 'report'])).exportedReport()
        args = eval('[' + self.params + ']')
        return getattr(report, self.request_function)(*args)

    def getValueAtTime(self):
        return 0
