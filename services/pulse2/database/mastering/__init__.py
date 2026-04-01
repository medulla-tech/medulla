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
    def create_action(self, session, action, gid, uuid, server, begin_date, end_date, config, workflow, entity_id=-1):
        """
        Create a new action on mastering.

        Args:
            self (MasteringDatabase) : instance of class
            session (sqlalchemy.session) : session to access to the database. Generated by decorator
            action: the mastering action executed by the workflow
            gid : groupe gid selected to associate this new action
            uuid: machine uuid selected to associate this new action
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

        sql = """INSERT INTO actions (server_id, entity_id, gid, uuid, name, config, content, status, date_start, date_end) values(
        (select id from servers where jid="%s"), "%s", "%s", "%s", '%s', '%s', "%s", "%s", "%s")"""%(server, entity_id, gid, uuid, action, config_dump, workflow_dump, "TODO", begin_date, end_date)

        try:
            session.execute(sql)
        except Exception as e:
            logger.error("Failed to execute : %s <=>%s"%(sql, e))
            session.rollback()
            return {"status": 1, "msg": "e"}

        session.commit()
        session.flush()
        return {"status": 0, "msg": "success"}

    @DatabaseHelper._sessionm
    def get_actions_for_entity(self, session, server, entity=-1, type="all", start=0, end=-1, filter=""):
        """
        Get the list of actions for an entity.

        Args:
            self (MasteringDatabase) : instance of class

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
            "total":0, "data":[]
        }

        sql = """SELECT
    SQL_CALC_FOUND_ROWS
    *
FROM actions
WHERE """

        # No entity specified, case for actions on new machines. In this case we get the entity associated to the server.
        binds = {}

        # Search based on direct entity id
        if entity == -1:
            sql += """server_id = (SELECT id from servers where jid=:jid) """
            binds["jid"] = server
        # Search based on server entity id
        else:
            sql += "entity_id = :entity_id or server_id = (SELECT id from servers where entity_id=:entity_id1) "
            binds["entity_id"] = entity
            binds["entity_id1"] = entity

        if filter != "":
            sql += """AND (uuid like :filt1 or name like :filt2 or date_start like :filt3 or date_end like :filt4 or content like :filt5 or status like :filt6 or gid like :filt7) """
            binds["filt1"] = f"%{filter}%"
            binds["filt2"] = f"%{filter}%"
            binds["filt3"] = f"%{filter}%"
            binds["filt4"] = f"%{filter}%"
            binds["filt5"] = f"%{filter}%"
            binds["filt6"] = f"%{filter}%"
            binds["filt7"] = f"%{filter}%"

        sql += """LIMIT :start,:end"""

        binds["start"] = start
        binds["end"] = end



        datas = session.execute(sql, binds).all()
        count = session.execute("SELECT FOUND_ROWS();").scalar()

        if count == 0:
            return result

        result["total"] = count

        result["machines"] = []
        result["groups"] = []

        for row in datas:
            _gid = row[3] if row[3] is not None else ""
            _uuid = row[4] if row[4] is not None else ""

            # Keep an array of all uuids and gids to retrive datas with one request.
            if _gid != "" and _gid not in result["groups"]:
                result["groups"].append(_gid)
            if _uuid != "" and _uuid not in result["machines"]:
                result["machines"].append(_uuid)

            result["data"].append({
                "id": row[0],
                "server_id": row[1],
                "entity_id": row[2] if row[2] is not None else -1,
                "gid": _gid,
                "uuid": _uuid,
                "name": row[6] if row[6] is not None else "",
                "config": json.loads(row[7]) if row[7] is not None else {},
                "content": json.loads(row[8]) if row[8] is not None else {},
                "status": row[9] if row[9] is not None else "",
                "date_creation": str(row[10]) if row[10] is not None else "",
                "date_start": str(row[11]) if row[11] is not None else "",
                "date_end": str(row[12]) if row[12] is not None else "",
            })

        return result
