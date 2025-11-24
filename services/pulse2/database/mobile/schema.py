# -*- coding: utf-8; -*-
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Text, LargeBinary, Enum
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class MobileDBObj(DBObj):
    id = Column(Integer, primary_key=True)

class Tests(Base, MobileDBObj):
    __tablename__ = 'tests'
    name = Column(String(50))
    message = Column(String(255))



"""
cette table contient plusieurs jointure avec d'autre table 

faut mettre a jours la version de la base de donnée 

UPDATE version SET Number = numofversion;

"""

