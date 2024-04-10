# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-2.0-or-later

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct, Table
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta
# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
#from pulse2.database.urbackup.schema import Tests
# Imported last
import logging
import json
import time


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
            pool_size=self.config.dbpoolsize)
        print(self.makeConnectionPath())
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM urbackup.version limit 1;")
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
            if ret:
                break
        if not ret:
            raise "Database urbackup connection error"
        return ret
    
    @DatabaseHelper._sessionm
    def getClientStatus(self, session, client_id):
        try:
            sql="""SELECT * FROM urbackup.client_state WHERE client_id = '%s';"""%(client_id)

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
    def insertNewClient(self, session, client_id, authkey):
        try:
            sql="""INSERT INTO client_state VALUES ('%s', '1', '%s');"""%(client_id, authkey)

            session.execute(sql)
            session.commit()
            session.flush()
            
            return True
            
        except Exception as e:
            logging.getLogger().error(str(e))
            
            return False

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
