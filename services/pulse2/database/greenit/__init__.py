# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# file : pulse2/database/greenit/__init__.py

"""
greenit database handler
"""
# SqlAlchemy
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import types

Session = sessionmaker()
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta

from mmc.database.database_helper import DatabaseHelper
#from pulse2.database.greenit.schema import (
    #Tests,
#)
# Imported last
import logging
import json
import time
from datetime import datetime
class GreenitDatabase(DatabaseHelper):
    """
    Singleton Class to query the greenit database.
    1 convention de nommage est utilisé pour mapper les tables d'une base de données relationnelle dans cette class Python utilisant SQLAlchemy.

    Dans notre  modèle de convention :

    Nom des tables de la base de données : Les noms des tables dans la base de données greenit  sont écrits en minuscules et généralement au pluriel.
    Par exemple, tests, utilisateurs, produits, etc.

    Nom des classes Python : Les tables sont mappées sur des classes Python, où le nom de la classe correspond au nom de la table, mais avec la première lettre en majuscule. Par exemple, si nous avons une table tests dans la base de données greenit, elle sera mappée sur une classe Python nommée Tests.

    En utilisation dans les requêtes SQLAlchemy de la class GreenitDatabase:
    A la redaction des requêtes SQLAlchemy dans notre class, on utilise les noms de classe Python mappés pour accéder aux données de la table correspondante.
    Par exemple, Récupéreration de toutes les lignes de la table tests, on utilise result = session.query(self.Tests).all()

    Cette convention de nommage permet une correspondance simple et directe entre les tables de la base de données et les classes Python de notre class, cela facilite la compréhension et la maintenance du code.
    Pour mettre en oeuvre 1 nouvelle table il suffit de la créer juste dans mysql.
    On peut les utiliser directement dans les methodes de notre class en respectant la convention.
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
            pool_timeout=self.config.dbpooltimeout,
        )

        if not self.db_check():
            return False

        self.metadata = MetaData(self.db)

        # Créer une instance de AutomapBase
        # oncree tout les mapper automatiquement dynamiquement
        Base = automap_base()

        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.reflect()
        self.metadata.create_all()

        self.is_activated = True
        result = self.db.execute("SELECT * FROM %s.version limit 1;" % self.my_name)
        re = [element.Number for element in result]
        logging.getLogger().debug("%s database connected (version:%s)"% (self.my_name, re[0]))

        result = self.db.execute("""SELECT
                                        table_name
                                    FROM
                                        INFORMATION_SCHEMA.TABLES
                                    WHERE
                                        TABLE_TYPE = 'BASE TABLE'
                                            AND table_schema = '%s';""" % self.my_name)
        table_names = [row[0] for row in result.fetchall()]

        logging.getLogger().debug(f"list des Tables {table_names}")
        # Vous pouvez ensuite mapper ces tables si nécessaire
        for table_name in table_names:
            # Mapper la table dynamiquement
            table = self.metadata.tables.get(table_name)
            if table is not None:
                setattr(self, table_name.capitalize(), table)
                # Maintenant, vous pouvez utiliser les tables mappées
                logging.getLogger().debug(f"Table {table_name} a été mappée dans la class sqlalchemy {table_name.capitalize()}.")
            else:
                logging.getLogger().warning(f"La table {table_name} n'a pas été trouvée dans la base de données.")

        #if hasattr(self, 'Tests'):
            #self.getTests()
        self.init_const()
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the xmppmaster database
        """
        # No mapping is needed, all is done on schema file
        return

    def init_const(self):
        self.mois= ['January',
                    'February',
                    'March',
                    'April',
                    'May',
                    'June',
                    'July',
                    'August',
                    'September',
                    'October',
                    'November',
                    'December']
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


    # ---------------------- function dict from dataset ----------------------
    def _return_dict_from_dataset_mysql(self, resultproxy):
        return [rowproxy._asdict() for rowproxy in resultproxy]
    # =====================================================================
    @DatabaseHelper._sessionm
    def getTests(self, session):
        query = session.query(self.Tests)
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
        logging.getLogger().debug(f"result test {result}")
        return result


    @DatabaseHelper._sessionm
    def getDatasyear(self, session, annee=None):
        if annee is None:
            annee = datetime.now().year
        sql = """SELECT
                    annee,
                    mois,
                    sum(Energie) as "energie(W)",
                    AVG(moyenne_charge) as "charge(%%)"
                FROM
                    greenit.conso_annee
                WHERE
                    annee = :annee
                GROUP BY
                    annee,
                    mois
                ORDER BY
                    FIELD(mois,
                        'January',
                        'February',
                        'March',
                        'April',
                        'May',
                        'June',
                        'July',
                        'August',
                        'September',
                        'October',
                        'November',
                        'December');
                        ;"""

        ret = session.execute(sql, {"annee": annee})
        result_set = ret.fetchall()
        result = [dict(row) for row in result_set]
        record_count = len(result)
        resultatannee={ "annee" : result[0][0]}
        moisdata={}
        # prepare structure les 12 mois avec des valeurs null
        for t in range(12):
            moisdata[ self.mois[t]] ={ {"E" :  "null", "C" : "null"} }
        # suivant less mesures en remplis le dict des mois
        for t in result:
            moisdata[t[0][1]]["E"]= t[0][1]]
            moisdata[t[0][1]]["C"]= t[0][2]]
        return moisdata
