import os,sys
from sqlalchemy.orm import Session
from sqlalchemy import (
    create_engine,
    MetaData,
    func,
    and_,
    desc,
    or_,
    distinct,
    not_,
)

from mmc.database.sqlite_helper import SqliteHelper
import logging

logger = logging.getLogger()

class BackupServer(SqliteHelper):
    """Mapper for /var/urbackup/backup_server.db"""

    # Need to declare path and name first
    path = os.path.join("/", "var", "urbackup")
    name = "backup_server"

    def __init__(self):
        """Create an unique instance of BackupServer object."""
        super().__init__()

    def activate(self):
        """Activate sqlalchemy engine, for the part specific to this database"""
        super().activate()
        try:
            self.connect = self.engine.connect()
        except Exception as e:
            logger.error("Error : %s for engine %s"%(e, self.engine))
            self.is_activated = False
            return False

        # Generate automatic mapping
        self.metadata.create_all(bind=self.engine)
        self.metadata.reflect(bind=self.engine)
        excludes = []

        # Bind the mapping in self.Tablename attribute, because it's more convenient than self.metadata.tables["tablename"]
        for element in self.metadata.tables:
            if element in excludes:
                continue
            setattr(self, element.capitalize(), self.metadata.tables[element])

        # Don't forget to declare the engine as activated
        self.is_activated = True

    def get_backups(self):
        """This function has been created to get the backups list"""
        session = self.session

        query = session.query(self.Backups)
        result = {"total":0, "datas":[]}
        count = query.count()
        
        datas = query.all()
        for element in datas:
            result["datas"].append({
                "id":element.id,
                "client_id":element.clientid,
                "path":element.path
            })
        result["total"] = count

        return result

class BackupSettings(SqliteHelper):
    """Mapper for /var/urbackup/backup_server_settings.db"""
    path = os.path.join("/", "var", "urbackup")
    name = "backup_server_settings"

    def __init__(self):
        """Instanciate unique object of BackupSettings"""
        super().__init__()

    def activate(self):
        """Activate the sqlalchemy engine"""
        super().activate()
        try:
            self.connect = self.engine.connect()
        except Exception as e:
            print("Error : %s for engine %s"%(e, self.engine))
        self.metadata.create_all(bind=self.engine)
        self.metadata.reflect(bind=self.engine)
        excludes = []
        for element in self.metadata.tables:
            if element in excludes:
                continue
            setattr(self, element.capitalize(), self.metadata.tables[element])
        self.is_activated = True
