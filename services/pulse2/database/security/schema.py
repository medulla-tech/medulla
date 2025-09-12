# schema.py
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from mmc.database.database_helper import DBObj   # important !

Base = declarative_base()

class Tests(Base, DBObj):  # ← hérite bien de Base + DBObj
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    message = Column(String(255))


class Inventories(Base, DBObj):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True)
    machine_id = Column(String(128), index=True, nullable=False)
    package_name = Column(String(255))
    version = Column(String(64))
    vendor = Column(String(128))
    collected_at = Column(DateTime, server_default=func.now())

    results = relationship("Results", back_populates="inventory")


class Results(Base, DBObj):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, ForeignKey("inventories.id"))
    cve_id = Column(String(64), index=True)
    severity = Column(String(32))
    score = Column(Float)
    description = Column(Text)
    detected_at = Column(DateTime, server_default=func.now())

    inventory = relationship("Inventories", back_populates="results")
