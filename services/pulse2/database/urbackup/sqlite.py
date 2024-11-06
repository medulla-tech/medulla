#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import os,sys
from datetime import datetime
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

    @SqliteHelper._session
    def get_backups(self, session, clientid, start=0, limit=-1, filter=""):
        try:
            start = int(start)
        except:
            start = 0

        try:
            limit = int(limit)
        except:
            limit = -1

        limit_clause=""
        if limit != -1:
            limit_clause = "limit %s,%s"%(start, limit)
        else:
            limit_clause = "limit %s"%(start)

        filter_clause = ""
        if filter != "":
            filter_clause = """where (path like '%%%s%%'
            or path like '%%%s%%'
            or incremental like '%%%s%%'
            or archived like '%%%s%%'
            or backuptime like '%%%s%%'
            or size_bytes like '%%%s%%')
            """%(tuple([filter for x in range(0,6)]))
        result = {"total":0, "datas":[]}
        sql_count = "SELECT count(rowid) from backups %s"%(filter_clause)
        count_query = session.execute(sql_count)
        count = count_query.fetchone()
        if isinstance(count, tuple):
            count = count[0]

        sql = """SELECT
        id,
        clientid,
        path,
        incremental,
        archived,
        backuptime,
        size_bytes from backups %s
        order by backuptime desc
        %s
        """%(filter_clause, limit_clause)
        query = session.execute(sql)
        datas = query.fetchall()

        for element in datas:
            result["datas"].append({
                "id":element[0],
                "client_id":element[1],
                "path":element[2],
                "full": True if element[3] == 0 else False,
                "archived": True if element[4] != 0 else False,
                "backuptime": element[5] if element[5] != 0 else "",
                "size_bytes": str(element[6])
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
