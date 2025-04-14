#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

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
    DateTime,

)
import logging
from mmc.database.sqlite_helper import SqliteHelper
from datetime import datetime

logger = logging.getLogger()

class BackupServer(SqliteHelper):
    path = os.path.join("/", "var", "urbackup")
    name = "backup_server"

    def __init__(self):
        """Create an unique instance of BackupServer object."""
        super().__init__()
        if self.is_activated is False:
            self.activate()

    def activate(self):
        """Activation and mapping for the sqlite db wanted"""
        super().activate()
        self.metadata.create_all(bind=self.engine)
        self.metadata.reflect(bind=self.engine)
        excludes = []
        for element in self.metadata.tables:
            if element in excludes:
                continue
            setattr(self, element.capitalize(), self.metadata.tables[element])
        self.is_activated = True

        # self.Backups.columns['backuptime'].type = DateTime

    @SqliteHelper._session
    def get_backups(self, session, clientid, start=0, limit=-1, filter=""):
        """This function has been created to get the backups list"""

        query = session.query(self.Backups)
        result = {"total":0, "datas":[]}
        if filter != "":
            query = query.filter(or_(
                self.Backups.c.path.contains(filter),
                self.Backups.c.backuptime.contains(filter),
            ))
        

        count = query.count(self.Backups.c.id)
        query = query.order_by(self.Backups.c.backuptime.desc())
        query = query.offset(start)
        if(limit != -1):
            query = query.limit(limit)
        datas = query.all()
        for element in datas:
            result["datas"].append({
                "id":element.id,
                "client_id":element.clientid,
                "path":element.path,
                "full": element.incremental,
                "archived":element.archived,
                "backuptime":element.backuptime.strftime("%Y-%m-%d"),
                "size_bytes":str(element.size_bytes)
            })

        result["total"] = count

        return result

class BackupFiles(SqliteHelper):
    path = os.path.join("/", "var", "urbackup")
    name = "backup_server_files"

    def __init__(self):
        """Create an unique instance of BackupServer object."""
        super().__init__()
        if self.is_activated is False:
            self.activate()

    def activate(self):
        """Activation and mapping for the sqlite db wanted"""
        super().activate()
        self.metadata.create_all(bind=self.engine)
        self.metadata.reflect(bind=self.engine)
        excludes = []
        for element in self.metadata.tables:
            if element in excludes:
                continue
            setattr(self, element.capitalize(), self.metadata.tables[element])
        self.is_activated = True


class BackupSettings(SqliteHelper):
    path = os.path.join("/", "var", "urbackup")
    name = "backup_server_settings"

    def __init__(self):
        super().__init__()
        if self.is_activated is False:
            self.activate()

    def activate(self):
        """Activation and mapping for the sqlite db wanted"""
        super().activate()
        self.metadata.create_all(bind=self.engine)
        self.metadata.reflect(bind=self.engine)
        excludes = []
        for element in self.metadata.tables:
            if element in excludes:
                continue
            setattr(self, element.capitalize(), self.metadata.tables[element])
        self.is_activated = True


    @SqliteHelper._session
    def get_setting(self, session, key):

        query = session.query(self.Settings).filter(and_(self.Settings.c.key == key, self.Settings.c.clientid == 0)).first()

        if query is not None:
            return query.value
        else:
            return ""