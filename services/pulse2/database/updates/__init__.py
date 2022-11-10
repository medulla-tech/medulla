# -*- coding: utf-8; -*-
#
# (c) 2020 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct, Table
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta
from sqlalchemy.orm import sessionmaker

# On importe la base de xmpp
# from pulse2.database.xmppmaster import XmppMasterDatabase

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.updates.schema import Tests
# Imported last
import logging
import json
import time

#Session = sessionmaker()

logger = logging.getLogger()


class UpdatesDatabase(DatabaseHelper):
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "updates"
        self.configfile = "updates.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        if self.is_activated:
            return None
        self.config = config

        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        print self.makeConnectionPath()
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        result = self.db.execute("SELECT * FROM updates.version limit 1;")
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
            except DBAPIError, e:
                logging.getLogger().error(e)
            except Exception, e:
                logging.getLogger().error(e)
            if ret: break
        if not ret:
            raise "Database updates connection error"
        return ret

    # =====================================================================
    # updates FUNCTIONS
    # =====================================================================
    @DatabaseHelper._sessionm
    def tests(self, session):
        ret = session.query(Tests).all()
        lines = []
        for row in ret:
            lines.append(row.toDict())

        return lines

    @DatabaseHelper._sessionm
    def test_xmppmaster(self, session):
        sql="""SELECT update_data.product,
                        update_data.title
        FROM xmppmaster.update_data
        WHERE revisionid = '32268448';"""
        
        result = session.execute(sql)
        session.commit()
        session.flush()
        
        resultat =  [x for x in result]
        print(resultat)
        if len(resultat) == 0:
            return -1
        else:
            return [x for x in result]
            # return resultat[0][1]
    
    @DatabaseHelper._sessionm
    def get_black_list(self, session, start, end, filter=""):
        
        black_list = { 'nb_element_total': 0,
                        'updateid_or_kb' : [],
                        'title': [] }

        sql="""SELECT SQL_CALC_FOUND_ROWS
                    *
                FROM 
                    xmppmaster.up_black_list 
                INNER JOIN 
                    xmppmaster.up_packages 
                ON 
                    up_black_list.updateid_or_kb = up_packages.kb
                OR
                    up_black_list.updateid_or_kb = up_packages.updateid """
        
        if filter:
                filterwhere="""AND
                        up_packages.title LIKE '%%%s%%'
                    LIMIT 5 OFFSET 5""" % filter
                sql=sql+filterwhere
           
        sql+=";"
            
        result = session.execute(sql)
        
        sql_count = "SELECT FOUND_ROWS();"
        ret_count = session.execute(sql_count)
        nb_element_total = ret_count.first()[0]
        
        black_list['nb_element_total'] = nb_element_total

        # result = session.execute(sql)

        session.commit()
        session.flush()
        
        if result:
            for list_b in result:
                black_list['updateid_or_kb'].append(list_b.updateid_or_kb)
                black_list['title'].append(list_b.title)
                # black_list.append((list_b.updateid_or_kb))

        return black_list
    
    @DatabaseHelper._sessionm
    def get_grey_list(self, session, start, end, filter=""):
        try:
            grey_list={ 'nb_element_total': 0,
                        'updateid' : [],
                        'title' : [],
                        'kb' : []}
            # Je recupère les infos et je compte le nombre d'entrée

            sql="""SELECT SQL_CALC_FOUND_ROWS
                        *
                    FROM
                        xmppmaster.up_gray_list 
                    WHERE 
                        valided = 0 """
                        
            if filter:
                filterwhere="""WHERE
                        title LIKE '%%%s%%'
                    LIMIT 5 OFFSET 5""" % filter
                sql=sql+filterwhere
           
            sql+=";"

            logger.info("sql function get_grey_list: %s" % (sql))
                
            result = session.execute(sql)
            
            # Je revupère mon nombre de ligne grâce à la requête du dessus SQL_CALC_FOUND_ROWS 
            sql_count = "SELECT FOUND_ROWS();"
            # J'execut la fonction
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]
            
            # Je passe la valeur dans mon objet
            grey_list['nb_element_total'] = nb_element_total
            
            session.commit()
            session.flush()
            
            if result:
                for list_b in result:
                    grey_list['updateid'].append(list_b.updateid)
                    grey_list['title'].append(list_b.title)
                    grey_list['kb'].append(list_b.kb)

        except Exception as e:
            logger.error("error function get_grey_list")
            
        return grey_list
    
    
    @DatabaseHelper._sessionm
    def get_white_list(self, session, start=0, end=-1, filter=""):
        try:
            white_list={ 'nb_element_total': 0,
                        'updateid' : [],
                        'title' : [],
                        'kb' : []}
            
            sql="""SELECT SQL_CALC_FOUND_ROWS
                        *
                    FROM xmppmaster.up_gray_list 
                    WHERE valided = 1 """
                    
            if filter:
                filterwhere="""AND
                        title LIKE '%%%s%%'
                    LIMIT 5 OFFSET 5""" % filter
                sql=sql+filterwhere
           
            sql+=";"
                
            result = session.execute(sql)
            
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]
            
            white_list['nb_element_total'] = nb_element_total
            
            if result:
                for list_w in result:
                   white_list['updateid'].append(list_w.updateid)
                   white_list['title'].append(list_w.title)
                   white_list['kb'].append(list_w.kb)
            
        except Exception as e:
            logger.error("error function get_grey_list")
            
        return white_list
            
    
    @DatabaseHelper._sessionm
    def approve_update(self, session, updateid, enabled=1):
        try:
            sql="""UPDATE `xmppmaster`.`up_gray_list`
                    SET 
                        valided = %s
                    WHERE 
                        (updateid = '%s');"""%(enabled, updateid)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception, e:
            logging.getLogger().error(str(e))
        return False
    
    
    @DatabaseHelper._sessionm
    def grey_update(self, session, updateid, enabled=0):
        try:
            sql="""UPDATE `xmppmaster`.`up_gray_list`
                    SET 
                        valided = %s
                    WHERE 
                        (updateid = '%s');"""%(enabled, updateid)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception, e:
            logging.getLogger().error(str(e))
        return False
