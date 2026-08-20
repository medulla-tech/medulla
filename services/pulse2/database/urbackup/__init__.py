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
    inspect,
    text,
)
import sqlite3
from sqlalchemy.orm import create_session, mapper, relation, sessionmaker
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from sqlalchemy.ext.automap import automap_base

from datetime import date, datetime, timedelta

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper

from pulse2.database.urbackup.schema import (
    Profiles,
    MachinesProfiles,
    ClientState,
    Logs,
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
        UrbackupFileDb().activate(self.config.urbackup_server_file_db)
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
    def get_client_ids_from_entity(self, session, entity_id):
        query = session.query(Profiles).filter(Profiles.entity_id == entity_id).first()

        """
        machines_profiles.machine_jid
        profiles.entity_id
        client_state.client_jid
        client_state.client_id


        select distinct cs.client_id
        from client_state cs
        join machines_profiles mp on cs.client_jid = mp.machine_jid
        join profiles p on mp.profile_id = p.id where p.entity_id = :entity_id
        """

        query = session.query(ClientState.client_id).join(MachinesProfiles, ClientState.client_jid == MachinesProfiles.machine_jid).join(Profiles, MachinesProfiles.profile_id == Profiles.id).filter(Profiles.entity_id == entity_id).distinct().all()

        if query is None:
            return []

        return [elem.client_id for elem in query]


    @DatabaseHelper._sessionm
    def update_logs(self, session, client_id, logs):
        ids = []
        ids_to_add = []
        for log in logs:
            ids.append(log["id"])

        # Copy the list of ids into ids_to_add. Later we will remove the matches
        ids_to_add = list(ids)

        # Got the existing logs
        query = session.query(Logs.id).filter(Logs.id.in_(ids))
        if query is not None:
            for row in query:
                if row.id in ids_to_add:
                    ids_to_add.remove(row.id)

        for log in logs:
            if log["id"] in ids_to_add:
                tmp = Logs()
                tmp.client_id = client_id
                tmp.id = log["id"]
                tmp.loglevel = log["loglevel"]
                tmp.msg = log["msg"]
                tmp.time = log["time"]

                try:
                    session.add(tmp)
                    session.commit()
                    session.flush()
                except Exception as e:
                    logging.getLogger().error(str(e))
                    continue
        return ids_to_add

    @DatabaseHelper._sessionm
    def get_logs_for_entity(self, session, entity, start=0, limit=-1, filter=""):
        try:
            start = int(start)
        except:
            start = 0

        try:
            limit = int(limit)
        except:
            limit = -1

        query = session.query(Logs)\
            .join(ClientState, Logs.client_id == ClientState.client_id)\
            .join(MachinesProfiles, ClientState.client_jid == MachinesProfiles.machine_jid)\
            .join(Profiles, MachinesProfiles.profile_id == Profiles.id).filter(and_(Profiles.entity_id == entity))\
            .order_by(Logs.time.desc())

        if filter != "":
            query = query.filter(and_(Logs.msg.like(f"%{filter}%")))

        count = query.count()
        query = query.offset(start)

        if limit != -1:
            query = query.limit(limit)


        datas = query.all()

        result = {"total": count, "data": []}
        if datas is None:
            return result

        for data in datas:
            result["data"].append({
                "id": data.id,
                "client_id": data.client_id,
                "loglevel": data.loglevel,
                "msg": data.msg,
                "time": data.time
            })

        return result

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

    @DatabaseHelper._sessionm
    def remove_group(self, session, groupuuid):
        query = session.query(Profiles)\
            .filter(Profiles.profile_uuid == groupuuid).delete()

        if query is None:
            return False

        group = {
            "id":group.id,
            "entity": group.entity_id,
            "uuid":group.profile_uuid,
            "name": group.profile_name,
        }

        query = session.query(MachinesProfiles)\
            .filter()
        session.commit()
        session.flush()


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
    excluded = []
    included = []

    def __new__(cls):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def activate(self, config):
        if self.is_activated:
            return True
        self.config = config
        self.engine = create_engine(f"sqlite:////{config}", connect_args={'check_same_thread':False})

        # _tables = [table for table in inspect(self.engine).get_table_names() if table not in self.excluded]
        # for element in self.included:
        #     if element not in _tables:
        #         _tables.append(element)

        # self.base = automap_base()
        # self.base.prepare(autoload_with=self.engine, reflection_options={"only": _tables})

        # for name, table in self.base.classes.items():
        #     setattr(self, name.capitalize(), table)

        self.metadata = MetaData(self.engine)
        self.metadata.create_all(self.engine)
        self.Base = automap_base()
        self.Base.prepare(self.engine)
        self.init_mapper()
        self.session_factory = sessionmaker(bind=self.engine)
        self.is_activated = True

        return self.is_activated

    def init_mapper(self):
        pass

    @staticmethod
    def session(fnc):
        def wrapper(self, *args, **kwargs):

            session = self.session_factory()
            try:
                result = fnc(self, session, *args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                logging.getLogger().error(str(e))
                session.rollback()
                raise
            finally:
                session.close()

        return wrapper

class UrbackupSettingsDb(SqliteHelper):

    def init_mapper(self):
        self.Settings = Table("settings", self.metadata, autoload=True)
        self.Si_client_groups = Table("si_client_groups", self.metadata, autoload=True)


    @SqliteHelper.session
    def get_group_by_name(self, session, group_name:str=""):
        if group_name == "":
            return {}

        query = session.query(self.Si_client_groups)\
            .filter(self.Si_client_groups.c.name == group_name)

        query = query.first()

        if query is None:
            return {}

        result = {
            "id" : query.id,
            "name" : query.name,
        }
        return result

    @SqliteHelper.session
    def get_group_by_id(self, session, id):
        query = sesison.query(self.Si_client_groups)\
            .filter(self.Si_client_groups.c.id == id).first()
        if query is None:
            return {}
        result = {
            "id": query.id,
            "name": query.name
        }
        return result

    @SqliteHelper.session
    def update_client_group(self, session, client_id, group_id):
        sql = "update settings set value = :groupid where clientid = :clientid"
        bind = {
            "groupid":group_id,
            "clientid":client_id
        }
        try:
            session.execute(text(sql), bind)
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logger.error(e)
            session.rollback()
            return False



    @SqliteHelper.session
    def get_setting(self, session, key:str, client_id:int) -> None|str:

        sql = """SELECT value FROM settings WHERE key=:key AND clientid = :clientid"""
        bind = {
            "key": key,
            "clientid": client_id
        }
        try:
            query = session.execute(text(sql), bind).fetchone()
        except Exception as e:
            logger.error(str(e))
            return None

        if query is None:
            return None

        return query[0]



class UrbackupDb(SqliteHelper):

    def init_mapper(self):
        self.Clients = Table("clients", self.metadata, autoload=True)

    @SqliteHelper.session
    def get_client_by_name(self, session, name:str=""):
        if name == "":
            return {}

        try:
            sql = """SELECT * from clients where name = :name"""
            bind = {"name":name}
            query = session.execute(text(sql), bind).first()
        except Exception as e:
            logger.error(3)
            logger.error(str(e))
            logger.error(4)
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
    def get_progress_by_group(self, session, group_id):
        sql = f"""SELECT * FROM (
	SELECT a.id AS backupid, clientid, name, strftime('%y-%m-%d %h:%i:%s', a.backuptime) AS backuptime, backuptime AS bt,
	 incremental, (strftime('%s',running)-strftime('%s',a.backuptime)) AS duration, size_bytes, 0 AS image, 0 AS del, size_calculated, resumed, 0 AS restore, '' AS details
	FROM backups a INNER JOIN clients b ON a.clientid=b.id
	 WHERE complete=1
	UNION ALL
	SELECT c.id AS backupid, clientid, name, strftime('%y-%m-%d %h:%i:%s', c.backuptime) AS backuptime, backuptime AS bt,
	incremental, (strftime('%s',running)-strftime('%s',c.backuptime)) AS duration, (size_bytes+IFNULL(0,(
	SELECT SUM(size_bytes) FROM backup_images INNER JOIN (SELECT * FROM assoc_images WHERE img_id=c.id) ON assoc_id=id
	)) ) AS size_bytes, 1 AS image, 0 AS del, 1 as size_calculated, 0 AS resumed, 0 AS restore, letter AS details
	FROM backup_images c INNER JOIN clients d ON c.clientid=d.id
	WHERE complete=1 AND letter!='SYSVOL' AND letter!='ESP'
	UNION ALL
	SELECT e.backupid AS backupid, clientid, name, strftime('%y-%m-%d %h:%i:%s', e.created) AS backuptime, e.created AS bt,
	incremental, (strftime('%s',stoptime)-strftime('%s',e.created)) AS duration, delsize AS size_bytes, image, 1 AS del, 1 AS size_calculated, 0 AS resumed, 0 AS restore, '' AS details
	FROM del_stats e INNER JOIN clients f ON e.clientid=f.id
	WHERE 1=1
	UNION ALL
	SELECT g.id AS backupid, clientid, name, strftime('%y-%m-%d %h:%i:%s', g.created) AS backuptime, g.created as bt,
	0 AS incremental, (strftime('%s',g.finished)-strftime('%s',g.created)) AS duration, -1 AS size_bytes, image, 0 AS del, 0 AS size_calculated, 0 AS resumed, 1 AS restore,
		(CASE WHEN image=1 THEN letter ELSE path END) AS details
	FROM restores g INNER JOIN clients h ON g.clientid=h.id
	WHERE done=1) ORDER BY bt DESC"""

    @SqliteHelper.session
    def get_backups_for_client(self, session, clientid, start=0, end=-1, filter=""):

        sql = "SELECT * FROM backups WHERE clientid = clientid order by backuptime desc limit :start, :offset"
        bind = {
            "clientid":clientid,
            "start":start,
            "offset": end
        }

        sql2 = "select count(*) from backups where clientid = :clientid"
        bind2 = {
            "clientid":clientid
        }
        try:
            query = session.execute(text(sql), bind).fetchall()
        except Exception as e:
            logger.error(str(e))
            return []

        count = 0
        try:
            count = session.execute(text(sql2), bind2).fetchone()[0]
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

    @SqliteHelper.session
    def update_client_group(self, session, client_id, group_id):
        sql = """UPDATE clients set groupid = :groupid where id = :clientid"""
        bind = {
            "groupid":group_id,
            "clientid":client_id
        }
        try:
            session.execute(text(sql), bind)
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logger.error(e)
            session.rollback()
            return False


class UrbackupFileDb(SqliteHelper):
    pass
    # def __init__(self):
    #     """Create an unique instance of BackupServer object."""
    #     super().__init__()
    #     if self.is_activated is False:
    #         self.activate()

    # def activate(self):
    #     """Activation and mapping for the sqlite db wanted"""
    #     super().activate()
    #     self.metadata.create_all(bind=self.engine)
    #     self.metadata.reflect(bind=self.engine)
    #     excludes = []
    #     for element in self.metadata.tables:
    #         if element in excludes:
    #             continue
    #         setattr(self, element.capitalize(), self.metadata.tables[element])
    #     self.is_activated = True
