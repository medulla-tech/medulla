# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-3.0-or-later

# SqlAlchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    select,
    func,
    and_,
    desc,
    or_,
    distinct,
    Table,
)
import sqlite3
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from sqlalchemy.ext.automap import automap_base

from datetime import date, datetime, timedelta

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper

from pulse2.database.urbackup.schema import (
    Profiles,
    MachinesProfiles,
    ClientState
)

# Imported last
import logging
import json
import time

logger = logging.getLogger()
class UrbackupDatabase(DatabaseHelper):
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "urbackup"
        self.configfile = "urbackup.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        if self.is_activated:
            return None
        self.config = config

        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
        )
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)

        Base = automap_base()
        Base.prepare(self.db, reflect=True)

        # Only federated tables (beginning by local_) are automatically mapped
        # If needed, excludes tables from this list
        exclude_table = []
        # Dynamically add attributes to the object for each mapped class
        for table_name, mapped_class in Base.classes.items():
            if table_name in exclude_table:
                continue
            if table_name.startswith("local"):
                setattr(self, table_name.capitalize(), mapped_class)

        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM urbackup.version limit 1;")
        re = [element.Number for element in result]

        UrbackupSettingsDb().activate(self.config.urbackup_server_settings_db)
        UrbackupDb().activate(self.config.urbackup_server_db)
        return True

    def initMappers(self):
        return

    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError as e:
                logging.getLogger().error(e)
            except Exception as e:
                logging.getLogger().error(e)
            if ret:
                break
        if not ret:
            raise "Database urbackup connection error"
        return ret

    @DatabaseHelper._sessionm
    def getClientStatus(self, session, client_id):

        query = session.query(ClientState.state).filter(ClientState.client_id == client_id).first()

        if query is None:
            return 0

        return query.state

        # result = 0
        # try:
        #     sql="""SELECT state FROM urbackup.client_state WHERE client_id = '%s';"""%(client_id)

        #     resultquery = session.execute(sql)
        #     session.commit()
        #     session.flush()

        #     result = resultquery.first()[0]

        # except Exception as e:
        #     logging.getLogger().error("We failed to retrieve the status of the client")
        #     logging.getLogger().error(str(e))

        # return result

    @DatabaseHelper._sessionm
    def editClientState(self, session, state, client_id):
        try:
            sql="""UPDATE client_state SET state = '%s' WHERE client_id = '%s';"""%(state, client_id)

            session.execute(sql)
            session.commit()
            session.flush()

            return True

        except Exception as e:
            logging.getLogger().error(str(e))

            return False

    @DatabaseHelper._sessionm
    def insertNewClient(self, session, client_id, client_jid, authkey):
        tmp = ClientState()

        tmp.client_id = client_id
        tmp.client_jid = client_jid
        tmp.authkey = authkey

        try:
            session.add(tmp)
            session.commit()
            session.flush()
        except Exception as e:
            return False

        return True

    @DatabaseHelper._sessionm
    def update_client_state(self, session, client_id, machine_jid, auth, state=1):

        query = session.query(ClientState).filter(ClientState.client_jid == machine_jid).first()

        if query is None:
            return {}

        query.client_id = client_id
        query.client_jid = machine_jid
        query.authkey = auth
        query.state = state
        session.commit()
        session.flush()

        return {
            "client_id": query.client_id,
            "client_jid": query.client_jid,
            "authkey": query.authkey,
            "state": query.state
        }



    @DatabaseHelper._sessionm
    def getComputersEnableValue(self, session, jid):
        try:
            sql="""SELECT id, jid, enabled FROM xmppmaster.machines WHERE jid = '%s';"""%(jid)

            resultquery = session.execute(sql)
            session.commit()
            session.flush()

            result = [{column: value for column,
                value in rowproxy.items()}
                        for rowproxy in resultquery]

        except Exception as e:
            logging.getLogger().error(str(e))

        return result

    @DatabaseHelper._sessionm
    def insertLog(self, session, msg, time):
        try:
            sql="""INSERT INTO all_logs (`msg`, `time`) VALUES ('%s', '%s');"""%(msg, time)

            resultquery = session.execute(sql)
            session.commit()
            session.flush()

            result = [{column: value for column,
                value in rowproxy.items()}
                        for rowproxy in resultquery]

            return True

        except Exception as e:
            logging.getLogger().error(str(e))

            return False

    @DatabaseHelper._sessionm
    def getAllLogs(self, session):
        try:
            #allLogs = {
            #    "msg": [],
            #    "time": [],
            #}
            allLogs = []

            sql="""SELECT msg, time FROM all_logs;"""

            resultquery = session.execute(sql)
            session.commit()
            session.flush()

            if resultquery:
                allLogs = [
                    {
                        "msg": list_Logs.msg,
                        "time": list_Logs.time,
                    }
                    for list_Logs in resultquery
                ]

            #if resultquery:
            #    for list_Logs in resultquery:
            #        allLogs["msg"].append(list_Logs.msg)
            #        allLogs["time"].append(list_Logs.time)

        except Exception as e:
            logging.getLogger().error(str(e))

        return allLogs

    @DatabaseHelper._sessionm
    def get_profile(self, session, entityId):
        query = session.query(Profiles).filter(Profiles.entity_id == entityId).first()

        if query is None:
            return {}

        result = {
            "id": query.id,
            "entity_id": query.entity_id,
            "profile_uuid": query.profile_uuid,
            "profile_name" : query.profile_name
        }
        return result

    @DatabaseHelper._sessionm
    def add_profile(self, session, entity_id, profile_uuid, profile_name):
        tmp = Profiles()

        tmp.entity_id = entity_id
        tmp.profile_uuid = profile_uuid
        tmp.profile_name = profile_name

        try:
            query = session.add(tmp)
            session.commit()
            session.flush()
        except:
            return {}

        return {
            "id" : tmp.id,
            "profile_uuid": tmp.profile_uuid,
            "profile_name" : tmp.profile_name
        }

    @DatabaseHelper._sessionm
    def get_machine_profile(self, session, machine_jid):
        """
        Get the machine profile association by machine JID.
        This function is used to find out if a specific machine is associated with any profile in the database.
        In this case, the machine has to be associated with the right profile, otherwise we need to update the association in the database.

        Args:
            session: Database session.
            machine_jid (str): The JID of the machine.

        Returns:
            dict: The machine profile association, or empty dict if not found.
        """
        query = session.query(MachinesProfiles).filter(MachinesProfiles.machine_jid == machine_jid).first()

        if query is None:
            return {}

        result = {
            "id": query.id,
            "profile_id": query.profile_id,
            "machine_jid": query.machine_jid
        }
        return result

    @DatabaseHelper._sessionm
    def update_association_machine_profile(self, session, association_id, new_profile_id):
        """
        Update the machine profile association in the database.
        This function is used to update the association of a machine to a new profile in the database.

        Args:
            session: Database session.
            association_id (int): The ID of the machine profile association to update.
            new_profile_id (int): The new profile ID to associate with the machine.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:

            query = session.query(MachinesProfiles).filter(MachinesProfiles.id == association_id).first()

            if query is None:
                logging.getLogger().error(f"No association found with ID {association_id}")
                return False

            query.profile_id = new_profile_id
            session.commit()
            session.flush()
            return True

        except Exception as e:
            logging.getLogger().error(str(e))

            return False

    @DatabaseHelper._sessionm
    def add_machine_to_profile(self, session, profile_id, machine_jid):
        tmp = MachinesProfiles()
        tmp.profile_id = profile_id
        tmp.machine_jid = machine_jid

        try:
            query = session.add(tmp)
            session.commit()
            session.flush()
        except:
            return {}

        return {
            "id":tmp.id,
            "machine_jid": tmp.machine_jid,
            "profile_id": tmp.profile_id
        }


    @DatabaseHelper._sessionm
    def get_client_state(self, session, clientid):
        """
        Get client by JID.

        Args:
            session: Database session.
            clientid (int): The ID of the client.

        Returns:
            dict: Client information if found, empty dict otherwise.
        """
        try:
            query = session.query(ClientState).filter(ClientState.client_id == clientid).first()
            if query is None:
                return {}

            return {
                "client_id": query.client_id,
                "client_jid": query.client_jid,
                "authkey": query.authkey,
                "state": query.state
            }
        except Exception as e:
            logging.getLogger().error(str(e))
            return {}

    @DatabaseHelper._sessionm
    def get_group_info(self, session, entityid):
        query = session.query(Profiles).filter(Profiles.entity_id == entityid).first()

        if query == None:
            return {}

        return {
            "id":query.id,
            "entity_id":query.entity_id,
            "profile_uuid":query.profile_uuid,
            "profile_name":query.profile_name
        }


    # =====================================================================
    # urbackup FUNCTIONS
    # =====================================================================
    # @DatabaseHelper._sessionm
    # def tests(self, session):
    #    ret = session.query(Tests).all()
    #    lines = []
    #    for row in ret:
    #        lines.append(row.toDict())

    #    return lines



class SqliteHelper:
    instance = None
    config = None
    is_activated = False

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def activate(self, config):
        if self.is_activated:
            return True
        self.config = config
        self.engine = sqlite3.connect(self.config, check_same_thread=False)
        self.is_activated = True

        return self.is_activated

    @staticmethod
    def session(fnc):
        def wrapper(self, *args, **kwargs):

            session = self.engine.cursor()
            try:
                result = fnc(self, session, *args, **kwargs)
                self.engine.commit()
                return result
            except Exception as e:
                logging.getLogger().error(str(e))
                self.engine.rollback()
                raise
            finally:
                session.close()

        return wrapper

class UrbackupSettingsDb(SqliteHelper):

    @SqliteHelper.session
    def get_group_by_name(self, session, group_name:str=""):
        if group_name == "":
            return {}

        sql = "SELECT * FROM si_client_groups WHERE name = ?"
        try:
            query = session.execute(sql, (group_name,)).fetchone()
        except Exception as e:
            logger.error(str(e))
            return {}

        if query is None:
            return {}

        result = {
            "id" : query[0],
            "name" : query[1],
        }
        return result

    @SqliteHelper.session
    def update_client_group(self, session, client_id, group_id):
        sql = """UPDATE settings SET value = ? WHERE key=? AND clientid = ?"""
        try:
            session.execute(sql, (group_id, "group_id", client_id))
            return True
        except Exception as e:
            logger.error(str(e))
            return False


    @SqliteHelper.session
    def get_setting(self, session, key:str, client_id:int) -> None|str:
        sql = """SELECT value FROM settings WHERE key=? AND clientid = ?"""
        try:
            query = session.execute(sql, (key, client_id)).fetchone()
        except Exception as e:
            logger.error(str(e))
            return None

        if query is None:
            return None

        return query[0]



class UrbackupDb(SqliteHelper):
    @SqliteHelper.session
    def get_client_by_name(self, session, name:str=""):
        if name == "":
            return {}


        sql = "SELECT * FROM clients WHERE name = ?"
        try:
            query = session.execute(sql, (name,)).fetchone()
        except Exception as e:
            logger.error(str(e))
            return {}

        if query is None:
            return {}

        result = {
            "id" : query[0],
            "name" : query[1],
            "lastbackup" : query[2],
            "lastseen" : query[3],
            "lastbackup_image" : query[4],
            "bytes_used_files" : query[5],
            "bytes_used_images" : query[6],
            "delete_pending" : query[7],
            "virtualmain" : query[8],
            "last_filebackup_issues" : query[9],
            "os_simple" : query[10],
            "os_version_str" : query[11],
            "client_version_str" : query[12],
            "groupid" : query[13],
            "file_ok" : query[14],
            "image_ok" : query[15],
            "alerts_state" : query[16],
            "alerts_next_check" : query[17],
            "created" : query[18],
            "uid" : query[19],
            "capa" : query[20],
            "with_hashes" : query[21]
        }
        return result


    @SqliteHelper.session
    def update_client_group(self, session, client_id, group_id):
        sql = "UPDATE clients SET groupid = ? WHERE id = ?"
        try:
            session.execute(sql, (group_id, client_id))
            return True
        except Exception as e:
            logger.error(str(e))
            return False

    @SqliteHelper.session
    def get_backups_for_client(self, session, clientid, start=0, end=-1, filter=""):

        sql = "SELECT * FROM backups WHERE clientid = ? limit ?, ?"
        sql2 = "select count(*) from backups where clientid = ?"
        try:
            query = session.execute(sql, (clientid, start, end)).fetchall()
        except Exception as e:
            logger.error(str(e))
            return []

        count = 0
        try:
            count = session.execute(sql2, (clientid)).fetchone()[0]
        except Exception as e:
            logger.error(str(e))

        result = []

        for row in query:
            result.append({
                "id": row[0],
                "clientid": row[1],
                "backuptime": row[2],
                "incremental": row[3],
                "path": row[4],
                "complete": row[5],
                "running": row[6],
                "size_bytes": row[7],
                "done": row[8],
                "archived": row[9],
                "archive_timeout": row[10],
                "size_calculated": row[11],
                "resumed": row[12],
                "indexing_time_ms": row[13],
                "tgroup": row[14],
                "synctime": row[15],
                "delete_pending": row[16]
            })

        return {
            "total": count,
            "data": result
        }
