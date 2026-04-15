# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

# SqlAlchemy

from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct, Table
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta
# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.mastering.schema import Tests

# Imported last
import logging
import base64
import json
import time
import os
logger = logging.getLogger()

class MasteringDatabase(DatabaseHelper):
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "mastering"
        self.configfile = "mastering.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        if self.is_activated:
            return None
        self.config = config

        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        print(self.makeConnectionPath())
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM mastering.version limit 1;")
        re = [element.Number for element in result]
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
            if ret: break
        if not ret:
            raise "Database mastering connection error"
        return ret

    # =====================================================================
    # mastering FUNCTIONS
    # =====================================================================

    @DatabaseHelper._sessionm
    def get_server_from_parent_entities(self, session, entities=[]):
        if entities == []:
            return ""

        entities = [e.replace("UUID", "") for e in entities if e.startswith("UUID")]
        entities_str = "(%s)"%(",".join(entities))
        # Get the first server found among the entities hierarchy.
        # The entities are sorted by order desc to get child server (if specified) before the top level.
        sql = """SELECT jid from servers where entity_id in %s order by entity_id desc limit 1"""%entities_str

        query = session.execute(sql).all()

        if query == None:
            return ""
        result = ""
        for row in query:
            result = row[0]
        return result

    @DatabaseHelper._sessionm
    def get_masters_for_entity(self, session, entity, start=0, limit=-1, filter=""):

        result = {
            "total": 0,
            "data": {
                "id" : [],
                "name" : [],
                "description" : [],
                "os" : [],
                "uuid": [],
                "path": [],
                "size" : [],
                "creation_date" : [],
                "modification_date" : []
            }
        }
        if entity == "":
            return result

        limit_str = ""
        if limit != -1:
            limit_str = "limit %s, %s"%(start, limit)

        if entity.startswith("UUID"):
            entity = entity.replace("UUID", "")

        filter_str = ""
        if filter != "":
            filter_str = " AND name like \"%%%s%%\" or description like \"%%%s%%\" or uuid like \"%%%s%%\" or os like \"%%%s%%\" or creation_date like \"%%%s%%\""%(filter, filter, filter, filter, filter)

        sql ="""
        SELECT
            SQL_CALC_FOUND_ROWS
            m.*
        from masters m
        join mastersEntities me on m.id = me.master_id
        where me.entity_id = %s
        %s
        order by name
        %s
        """%(entity, filter_str, limit_str)

        datas = session.execute(sql).all()
        count = session.execute("SELECT FOUND_ROWS();").scalar()

        if datas is None:
            return result

        result["total"] = count
        for row in datas:
            result["data"]["id"].append(row[0])
            result["data"]["name"].append(row[1])
            result["data"]["description"].append(row[2])
            result["data"]["uuid"].append(row[3])
            result["data"]["path"].append(row[4])
            result["data"]["size"].append(str(row[5]) if row[5] is not None else 0)
            result["data"]["os"].append(row[6] if row[6] is not None else "")
            result["data"]["creation_date"].append(row[8] if row[8] is not None else "")
            result["data"]["modification_date"].append(row[9] if row[9] is not None else "")

        return result


    @DatabaseHelper._sessionm
    def create_action(self, session, action, gid, uuid, target, server, begin_date, end_date, config, workflow, entity_id=-1):
        """
        Create a new action on mastering.

        Args:
            self (MasteringDatabase) : instance of class
            session (sqlalchemy.session) : session to access to the database. Generated by decorator
            action: the mastering action executed by the workflow
            gid : groupe gid selected to associate this new action
            uuid: machine uuid selected to associate this new action
            target: the target name associated to this action, can be empty.
            server: unknown machine querying on this server. Should be always specified
            begin_date: start date when the action is usable
            end_date: expiration date to specify when the action is no longer usable
            workflow (base64  stringified json): container of the workflow to proceed on this action
            entity_id: the entity id associated to the server. -1 if no entity specified. In this case, use the entity associated to the server. This data is used to list all elements from unique entity.
        Workflow shape:
        [
            {
                "type": "script",
                "name": "myscript.sh",
                "dependencies": [
                    "preinstall.sh"
                ],
            },
            {
                "type": "action",
                "name": "register",
            },
            {
                "type": "script",
                "name": "copydrivers",
                "dependencies": [
                    "mySetupComplete.cmd", // moved / renamed by the script
                    "mySysprep.xml",
                    "Medulla-Agent-Full-Latest.exe"
                ]
            }

        ]
        """
        config_dump = json.dumps(config)
        workflow_dump = json.dumps(workflow)


        binds = {}
        sql = """INSERT INTO actions (server_id, entity_id, gid, uuid, target, name, config, content, status, date_start, date_end) values(
    (select id from servers where jid=:jid), :entity_id, :gid, :uuid, :target, :name, :config, :content, :status, :date_start, :date_end)"""
        binds["jid"] = server
        binds["entity_id"] = entity_id
        binds["gid"] = gid
        binds["uuid"] = uuid
        binds["target"] = target
        binds["name"] = action
        binds["config"] = config_dump
        binds["content"] = workflow_dump
        binds["status"] = "TODO"
        binds["date_start"] = begin_date
        binds["date_end"] = end_date

        # Disabled for now
        try:
            session.execute(sql, binds)
        except Exception as e:
            logger.error("Failed to execute : %s <=>%s"%(sql, e))
            session.rollback()
            return {"status": 1, "msg": str(e)}

        session.commit()
        session.flush()
        return {"status": 0, "msg": "success"}

    @DatabaseHelper._sessionm
    def get_actions_for_entity(self, session, entity, start=0, end=-1, _filter=""):
        """
        Get the list of actions for an entity.

        Args:
            self (MasteringDatabase) : instance of class
            session (sqlalchemy.session) : session to access to the database. Generated by decorator
            entity: the entity id to get actions for. This is used to get actions for a specific entity. This can be -1 to get actions for all entities.
            start: pagination parameter to specify the offset of the first element.
            end: pagination parameter to specify the last element. -1 to get all elements.
            _filter: filter to apply on results. This is used to filter results based on their content.

        Return:
            A dict with total number of actions and the list of actions.
            The dict have the following shape:
            {
                "total": 0,
                "data": [
                    {
                        "id": action id,
                        "server_id": server id associated to the action,
                        "entity_id": entity id associated to the action,
                        "gid": group gid associated to the action,
                        "uuid": machine uuid associated to the action,
                        "target": target name associated to the action,
                        "name": name of the action,
                        "config": config of the action,
                        "content": workflow of the action,
                        "status": status of the action,
                        "date_creation": creation date of the action,
                        "date_start": start date when the action is usable,
                        "date_end": expiration date when the action is no longer usable
                    },
                    ...

        """
        try:
            start = int(start)
        except:
            start = 0
        try:
            end = int(end)
        except:
            end = -1

        if end == -1:
            end = 99999

        result = {
            "total":0,
            "data":[],
        }

        sql = """SELECT
    SQL_CALC_FOUND_ROWS
    *
FROM actions
WHERE """

        # No entity specified, case for actions on new machines. In this case we get the entity associated to the server.
        binds = {}
        sql += "entity_id = :entity_id "
        binds["entity_id"] = entity

        if _filter != "":
            if _filter == "N/P":
                    sql += """AND target  = '' """
            else:
                sql += """AND (uuid like :filt1 or name like :filt2 or date_start like :filt3 or date_end like :filt4 or content like :filt5 or status like :filt6 or gid like :filt7 or target like :filt8) """
                binds["filt1"] = f"%{_filter}%"
                binds["filt2"] = f"%{_filter}%"
                binds["filt3"] = f"%{_filter}%"
                binds["filt4"] = f"%{_filter}%"
                binds["filt5"] = f"%{_filter}%"
                binds["filt6"] = f"%{_filter}%"
                binds["filt7"] = f"%{_filter}%"
                binds["filt8"] = f"%{_filter}%"


        sql += """ORDER BY date_start DESC """
        sql += """LIMIT :start,:end"""

        binds["start"] = start
        binds["end"] = end

        datas = session.execute(sql, binds).all()
        count = session.execute("SELECT FOUND_ROWS();").scalar()

        if count == 0:
            return result

        result["total"] = count



        for row in datas:
            _gid = row[3] if row[3] is not None else ""
            _uuid = row[4] if row[4] is not None else ""

            result["data"].append({
                "id": row[0],
                "server_id": row[1],
                "entity_id": row[2] if row[2] is not None else -1,
                "gid": _gid,
                "uuid": _uuid,
                "target": row[5] if row[5] is not None else "",
                "name": row[6] if row[6] is not None else "",
                "config": json.loads(row[7]) if row[7] is not None else {},
                "content": json.loads(row[8]) if row[8] is not None else {},
                "status": row[9] if row[9] is not None else "",
                "date_creation": str(row[10]) if row[10] is not None else "",
                "date_start": str(row[11]) if row[11] is not None else "",
                "date_end": str(row[12]) if row[12] is not None else "",
            })

        return result

    @DatabaseHelper._sessionm
    def get_actions_for_machine(self, session, uuid, start, maxperpage, _filter):
        try:
            start = int(start)
        except:
            start = 0
        try:
            end = int(end)
        except:
            end = -1

        if end == -1:
            end = 99999

        result = {
            "total":0,
            "data":[],
        }

        sql = """SELECT
    SQL_CALC_FOUND_ROWS
    *
FROM actions
WHERE """

        # No entity specified, case for actions on new machines. In this case we get the entity associated to the server.
        binds = {}
        sql += "uuid = :uuid "
        binds["uuid"] = uuid

        if _filter != "":
            if _filter == "N/P":
                    sql += """AND target  = '' """
            else:
                sql += """AND (uuid like :filt1 or name like :filt2 or date_start like :filt3 or date_end like :filt4 or content like :filt5 or status like :filt6 or gid like :filt7 or target like :filt8) """
                binds["filt1"] = f"%{_filter}%"
                binds["filt2"] = f"%{_filter}%"
                binds["filt3"] = f"%{_filter}%"
                binds["filt4"] = f"%{_filter}%"
                binds["filt5"] = f"%{_filter}%"
                binds["filt6"] = f"%{_filter}%"
                binds["filt7"] = f"%{_filter}%"
                binds["filt8"] = f"%{_filter}%"


        sql += """ORDER BY date_start DESC """
        sql += """LIMIT :start,:end"""

        binds["start"] = start
        binds["end"] = end

        datas = session.execute(sql, binds).all()
        count = session.execute("SELECT FOUND_ROWS();").scalar()

        if count == 0:
            return result

        result["total"] = count



        for row in datas:
            _gid = row[3] if row[3] is not None else ""
            _uuid = row[4] if row[4] is not None else ""

            result["data"].append({
                "id": row[0],
                "server_id": row[1],
                "entity_id": row[2] if row[2] is not None else -1,
                "gid": _gid,
                "uuid": _uuid,
                "target": row[5] if row[5] is not None else "",
                "name": row[6] if row[6] is not None else "",
                "config": json.loads(row[7]) if row[7] is not None else {},
                "content": json.loads(row[8]) if row[8] is not None else {},
                "status": row[9] if row[9] is not None else "",
                "date_creation": str(row[10]) if row[10] is not None else "",
                "date_start": str(row[11]) if row[11] is not None else "",
                "date_end": str(row[12]) if row[12] is not None else "",
            })

        return result

    @DatabaseHelper._sessionm
    def get_action_results(self, session, _id, uuid, start=0, end=-1, _filter=""):
        """Get the list of results for a specific action. The results are selected based on action_id and the machine uuid because an action can be used for a group.

        Args:
            self (MasteringDatabase) : instance of class
            session (sqlalchemy.session) : session to access to the database. Generated by decorator
            _id: the action id
            uuid: the machine uuid to get results for. This is used to get results for a specific machine when the action is used for a group.
            start: pagination parameter to specify the offset of the first element.
            end: pagination parameter to specify the last element. -1 to get all elements.
            _filter: filter to apply on results. This is used to filter results based on their content."""

        try:
            start = int(start)
        except:
            start = 0

        try:
            end = int(end)
        except:
            end = -1

        if end == -1:
            end = 99999

        result = {
            "total":0,
            "data":[]
        }

        binds = {}
        sql = """ SELECT
    SQL_CALC_FOUND_ROWS
    *
FROM results
WHERE action_id = :action_id
and uuid = :uuid
"""
        binds["action_id"] = _id
        binds["uuid"] = uuid

        if _filter != "":
            sql += """AND (content like :filt1 OR creation_date like :filt2) """
            binds["filt1"] = f"%{_filter}%"
            binds["filt2"] = f"%{_filter}%"

        sql += """ORDER BY creation_date ASC """

        sql += """LIMIT :start,:end """
        binds["start"] = start
        binds["end"] = end

        datas = session.execute(sql, binds).all()
        count = session.execute("SELECT FOUND_ROWS();").scalar()

        if datas is None:
            return result

        result["total"] = count

        for row in datas:
            content = base64.b64encode(row[4].encode()).decode()
            creation_date = row[5]
            if isinstance(creation_date, datetime):
                creation_date = creation_date.strftime("%Y-%m-%d %H:%M:%S")
            result["data"].append({
                "id": row[0],
                "action_id": row[1],
                "session_id": row[2],
                "uuid": row[3],
                "content": content,
                "creation_date": creation_date if creation_date is not None else "",
            })


        return result


    @DatabaseHelper._sessionm
    def get_machines_action_results(self, session, id, start=0, end=-1, _filter=""):
        """Get the list of results for a specific action. The results are grouped by machine uuid to get an overview of all machines results for an action.

        Args:
            self (MasteringDatabase) : instance of class
            session (sqlalchemy.session) : session to access to the database. Generated by decorator
            _id: the action id
            start: pagination parameter to specify the offset of the first element.
            end: pagination parameter to specify the last element. -1 to get all elements.
            _filter: filter to apply on results. This is used to filter results based on their content.

        Return:
            A dict with total number of results and the list of results grouped by machine uuid.
            The dict have the following shape:
            {
                "total": 0,
                "data": [
                    {
                        "uuid": "machine uuid",
                        "results": [
                            {
                                "id": result id,
                                "uuid": machine_uuid,
                                "target": machine_name,
                                "session_id": session id of the result,
                                "creation_date": result creation date
                            },
                            ...
                        ]
                    },
                    ...
                ]
            }"""

        try:
            start = int(start)
        except:
            start = 0

        try:
            end = int(end)
        except:
            end = -1

        if end == -1:
            end = 99999

        result = {
            "total":0,
            "data":[]
        }

        binds = {}
        sql = """ SELECT SQL_CALC_FOUND_ROWS
    uuid,
    session_id,
    creation_date
FROM results
WHERE action_id = :action_id """

        binds["action_id"] = id

        if _filter != "":
            sql += """AND (uuid like :filt1 OR creation_date like :filt2 or session_id like :filt3) """
            binds["filt1"] = f"%{_filter}%"
            binds["filt2"] = f"%{_filter}%"
            binds["filt3"] = f"%{_filter}%"

        sql += """GROUP BY uuid """
        sql += """ORDER BY creation_date ASC """
        sql += """LIMIT :start,:end """
        binds["start"] = start
        binds["end"] = end

        datas = session.execute(sql, binds).all()
        count = session.execute("SELECT FOUND_ROWS();").scalar()

        if datas is None:
            return result

        result["total"] = count

        for row in datas:
            uuid = row[0] if row[0] is not None else ""
            creation_date = row[2]
            if isinstance(creation_date, datetime):
                creation_date = creation_date.strftime("%Y-%m-%d %H:%M:%S")
            result["data"].append({
                "uuid": uuid,
                "session_id": row[1] if row[1] is not None else "",
                "creation_date": creation_date if creation_date is not None else "",
            })

        return result

    @DatabaseHelper._sessionm
    def delete_master(self, session, server, entity, masterId):
        """
        Delete a master. This function first delete the association between the master and the entity. Then if there is no more association for this master, it deletes the master and its file.

        Args:
            self (MasteringDatabase) : instance of class
            session (sqlalchemy.session) : session to access to the database. Generated by decorator
            server: the server jid to check if the master is associated to an entity linked to this server. This is used to avoid deleting a master that is not associated to the server.
            entity: the entity id to check if the master is associated to this entity. This is used to avoid deleting a master that is not associated to the entity.
            masterId: the master id to delete.

        Return:
            A dict with status and message of the operation.
        """

        if isinstance(entity, str):
            if entity.startswith("UUID"):
                entity = entity.replace("UUID", "")
            entity = int(entity)

        # Delete the association between master and entity
        sql = """DELETE FROM mastersEntities where master_id = :master_id and entity_id = :entity_id"""
        binds = {
            "master_id": masterId,
            "entity_id": entity
        }
        try:
            session.execute(sql, binds)
        except Exception as e:
            session.rollback()

        session.commit()
        session.flush()

        # Now we have to check if there is no more association for this master
        sql = """select count(masters.uuid) as nb, masters.* from mastersEntities join masters on masters.id = mastersEntities.master_id where id = :master_id"""
        binds = {
            "master_id": masterId,
        }
        datas = session.execute(sql, binds).all()

        if datas is None:
            return {"status": 1, "msg": "Master not found"}

        master = datas[0]
        count = master[0]
        name = master[3]
        path = master[5]

        if count > 0:
            # There is still an association for this master, we don't delete the file
            return {"status": 0, "msg": "Master %s unlinked from entity"%name}

        # Delete the master from file system
        if path is not None and path != "":
            try:
                os.remove(path)
            except Exception as e:
                logger.error("Failed to delete master file : %s <=>%s"%(path, e))
                return {"status": 1, "msg": "Failed to delete master file"}

        sql = """DELETE FROM masters where id = :master_id"""
        binds = {
            "master_id": masterId,
        }
        try:
            session.execute(sql, binds)
        except Exception as e:
            session.rollback()
            logger.error("Failed to delete master : %s <=>%s"%(masterId, e))
            return {"status": 1, "msg": "Failed to delete master"}
        session.commit()
        session.flush()
        return {"status": 0, "msg": "Master %s deleted"%name}


    @DatabaseHelper._sessionm
    def delete_action(self, session, _id):
        """
        Delete an action. This function deletes the action and all its results.

        Args:
            self (MasteringDatabase) : instance of class
            session (sqlalchemy.session) : session to access to the database. Generated by decorator
            _id: the action id to delete.
        Return:
            A dict with status and message of the operation.
        """

        sql = """SELECT count(uuid) from results where action_id = :action_id"""
        binds = {
            "action_id": _id,
        }
        count = session.execute(sql, binds).scalar()

        # Count == 0 we can delete it. Else we put it in archived status
        if count == 0:
            sql = """DELETE FROM actions where id = :action_id"""
        else:
            sql = """UPDATE actions set status = 'ARCHIVED' where id = :action_id"""
        binds = {
            "action_id": _id,
        }

        try:
            session.execute(sql, binds)
        except Exception as e:
            session.rollback()
            logger.error("Failed to delete action : %s <=>%s"%(_id, e))
            if count == 0:
                return {"status": 1, "msg": "Failed to delete action"}
            else:
                return {"status": 1, "msg": "Failed to archive action"}

        session.commit()
        session.flush()
        if count == 0:
            return {"status": 0, "msg": "Action deleted"}
        else:
            return {"status": 0, "msg": "Action archived"}
