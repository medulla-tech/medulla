# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
greenit database handler
"""
# SqlAlchemy
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta

from mmc.database.database_helper import DatabaseHelper
from pulse2.database.greenit.schema import (
    Tests,
)
# Imported last
import logging
import json
import time
from datetime import datetime


class GreenitDatabase(DatabaseHelper):
    """
    Singleton Class to query the greenit database.

    """

    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "greenit"
        self.configfile = "greenit.ini"
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
        print(self.makeConnectionPath())
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM greenit.version limit 1;")
        re = [element.Number for element in result]
        # logging.getLogger().debug("xmppmaster database connected (version:%s)"%(re[0]))
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the xmppmaster database
        """
        # No mapping is needed, all is done on schema file
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
            raise "Database greenit connection error"
        return ret

    # =====================================================================
    # greenit FUNCTIONS
    # =====================================================================

    @DatabaseHelper._sessionm
    def tests(self, session):
        query = session.query(Tests)
        count = query.count()
        query = query.all()
        result = {
            "count": count,
            "datas": []
            }

        for element in query:
            result["datas"].append({
                "id": element.id,
                "name": element.name,
                "message": element.message if element.message is not None else ""
            })
        
        return result
