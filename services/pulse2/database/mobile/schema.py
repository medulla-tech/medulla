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

####### Device table ##########   
# class Devices(Base, MobileDBObj):
#     __tablename__ = "devices"
#     number = Column(String(255))
#     description = Column(String(255))
#     lastupdate = Column(DateTime)
#     configurationid = Column(Integer)
#     oldconfigurationid = Column(Integer)
#     info = Column(Text)
#     imei = Column(String(255))
#     phone = Column(String(255))
#     customerid = Column(Integer)
#     imeiupdatets = Column(DateTime)
#     custom1 = Column(String(255))
#     custom2 = Column(String(255))
#     custom3 = Column(String(255))
#     oldnumber = Column(String(255))
#     fastsearch = Column(String(255))
#     enrolltime = Column(DateTime)
#     infojson = Column(Text)
#     publicip = Column(String(50))

# ####### Configuration table table ########## 

"""
cette table contient plusieurs jointure avec d'autre table 

faut mettre a jours la version de la base de donnée 

UPDATE version SET Number = numofversion;

"""

