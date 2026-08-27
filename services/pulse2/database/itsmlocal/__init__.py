# file : services/pulse2/database/itsmlocal/__init__.py

"""Database access for the Medulla itsmlocal database."""

from mmc.database.database_helper import DatabaseHelper
from sqlalchemy import create_engine

from pulse2.database.itsmlocal.schema import Tests


class ItsmlocalDatabase(DatabaseHelper):
    """Provide the database connection used by the itsmlocal plugin."""

    is_activated = False
    session = None

    def db_check(self):
        """Check the module-owned database configuration."""
        self.my_name = "itsmlocal"
        self.configfile = "itsmlocal.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        """Initialize the SQLAlchemy engine when the plugin is enabled."""
        if self.is_activated:
            return True
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
            pool_timeout=self.config.dbpooltimeout,
        )
        if not self.db_check():
            return False
        self.is_activated = True
        return True

    def tests(self):
        """Return module health-check rows."""
        return []
