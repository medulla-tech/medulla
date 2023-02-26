# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from importlib import import_module

from sqlalchemy import Column, String, Integer, Float, BigInteger, func, orm
from sqlalchemy.ext.declarative import declarative_base; Base = declarative_base()

from mmc.database.database_helper import DBObj


class ReportingData(DBObj):
    # only for inherit, don't use this class directly
    # ====== Fields =============================
    id = Column(Integer, primary_key=True)
    indicator_id = Column(Integer)
    timestamp = Column(BigInteger)
    entity_id = Column(Integer)

class ReportingIntData(Base, ReportingData):
    # ====== Table name =========================
    __tablename__ = 'data'
    # ====== Fields =============================
    value = Column(Integer)


class ReportingFloatData(Base, ReportingData):
    # ====== Table name =========================
    __tablename__ = 'data_float'
    # ====== Fields =============================
    value = Column(Float)


class ReportingTextData(Base, ReportingData):
    # ====== Table name =========================
    __tablename__ = 'data_text'
    # ====== Fields =============================
    value = Column(String(255))


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
    data_type = Column(Integer)
    active = Column(Integer)
    keep_history = Column(Integer)


    @orm.reconstructor
    def afterLoad(self):
        """
        method to set additional fields according to datatype
        will be called automatically by SQLAlchmey on load
        """
        if self.data_type == 0:
            self.dataClass = ReportingIntData
            self.aggregate_func = func.sum
            self.format_func = int
        elif self.data_type == 1:
            self.dataClass = ReportingFloatData
            self.aggregate_func = func.sum
            self.format_func = float
        elif self.data_type == 2:
            self.dataClass = ReportingTextData
            self.aggregate_func = func.concat
            self.format_func = str


    def getCurrentValue(self, entities = []):
        #Mutable list entities used as default argument to a method or function
        report = import_module('.'.join(['mmc.plugins', self.module, 'report'])).exportedReport()
        args = [entities] + eval('[' + self.params + ']')
        return getattr(report, self.request_function)(*args)

    def getValueAtTime(self, session, ts_min, ts_max , entities = []):
        # DBClass, aggegate and finalformat functions according to DataType
        #Mutable list entities used as default argument to a method or function
        ret = session.query(self.aggregate_func(self.dataClass.value))\
                .filter_by(indicator_id = self.id)
        # Selected entities filter, else all entities are included
        if entities:
            ret = ret.filter(self.dataClass.entity_id.in_(entities))
        # Timestamp range filter
        ret = ret.filter(self.dataClass.timestamp.between(ts_min, ts_max))

        result = ret.scalar()
        return self.format_func(result) if result is not None else None
