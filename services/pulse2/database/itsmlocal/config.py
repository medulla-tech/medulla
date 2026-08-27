# file : services/pulse2/database/itsmlocal/config.py

"""Database configuration for itsmlocal."""

from mmc.database.config import DatabaseConfig


class ItsmlocalDatabaseConfig(DatabaseConfig):
    """Define the database name and configuration section."""

    dbname = "itsmlocal"
    dbsection = "database"
