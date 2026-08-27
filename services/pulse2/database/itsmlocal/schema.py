# file : services/pulse2/database/itsmlocal/schema.py

"""SQLAlchemy declarations for the itsmlocal module-owned tables."""

from mmc.database.database_helper import DBObj
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ItsmlocalDBObj(DBObj):
    """Base class for itsmlocal-specific mapped objects."""

    id = Column(Integer, primary_key=True)


class Tests(Base, ItsmlocalDBObj):
    """Temporary health-check table retained by the module skeleton."""

    __tablename__ = "tests"
    name = Column(String(50))
    message = Column(String(255))
