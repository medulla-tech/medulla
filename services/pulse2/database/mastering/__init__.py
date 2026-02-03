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
import json
import time

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
