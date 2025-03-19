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
)
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update
from datetime import date, datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base


# On importe la base de xmpp
# from pulse2.database.xmppmaster import XmppMasterDatabase

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.updates.schema import Tests

# Imported last
import logging
import json
import time
import traceback
# Session = sessionmaker()

logger = logging.getLogger()


class UpdatesDatabase(DatabaseHelper):
    """
    Singleton Class to query the update database.

    """

    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "updates"
        self.configfile = "updates.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        # Base = automap_base()
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
            except DBAPIError as e:
                logging.getLogger().error(e)
            except Exception as e:
                logging.getLogger().error(e)
            if ret:
                break
        if not ret:
            raise "Database updates connection error"
        return ret

    # =====================================================================
    # updates FUNCTIONS
    # =====================================================================
    @DatabaseHelper._sessionm
    def tests(self, session):
        # Tests c'est la table dans schema.py dans le module updates
        ret = session.query(Tests).all()
        lines = []
        for row in ret:
            lines.append(row.toDict())

        return lines


    @DatabaseHelper._sessionm
    def test_xmppmaster(self, session):
        """
        Test function to retrieve product and title information for a specific revision ID.

        Args:
            session: Database session object for executing queries.

        Returns:
            - List of results (product and title) if data is found.
            - -1 if no data matches the query.
        """
        try:
            # SQL query to retrieve product and title for the given revision ID
            sql = """SELECT update_data.product,
                            update_data.title
                    FROM xmppmaster.update_data
                    WHERE revisionid = '32268448';"""

            # Execute the query
            result = session.execute(sql)
            session.commit()
            session.flush()

            # Convert query result to a list
            resultat = [x for x in result]
            print(resultat)

            # Check if the result is empty
            if len(resultat) == 0:
                return -1
            else:
                # Return the results
                return [x for x in result]
        except Exception as e:
            logger.error(f"Error in function test_xmppmaster: {e}")

    @DatabaseHelper._sessionm
    def get_black_list(self, session, start, limit, filter=""):
        """
        Retrieve the black list of updates with optional filtering, sorting, and pagination.

        Args:
            session: Database session object for executing queries.
            start (int): Starting index for pagination.
            limit (int): Maximum number of results to retrieve.
            filter (str): Optional filter to apply to the query (title, kb, severity, or updateid_or_kb).

        Returns:
            dict: A dictionary containing:
                - nb_element_total (int): Total number of elements matching the query.
                - id (list): List of record IDs.
                - updateid_or_kb (list): List of update IDs or KBs.
                - title (list): List of update titles.
                - severity (list): List of severity levels for each update.
        """
        try:
            # Ensure start and limit are integers
            start = int(start)
        except ValueError:
            start = -1
        try:
            limit = int(limit)
        except ValueError:
            limit = -1

        try:
            # Initialize the result structure
            black_list = {
                "nb_element_total": 0,
                "id": [],
                "updateid_or_kb": [],
                "title": [],
                "severity": [],
            }

            # SQL query combining results from different sources using UNION
            sql = """SELECT SQL_CALC_FOUND_ROWS *
                    FROM (
                        SELECT
                            up_black_list.id,
                            up_black_list.updateid_or_kb,
                            update_data.title,
                            COALESCE(NULLIF(update_data.msrcseverity, ""), "Corrective") AS severity
                        FROM xmppmaster.up_black_list
                        INNER JOIN xmppmaster.update_data
                        ON up_black_list.updateid_or_kb = update_data.kb
                        OR up_black_list.updateid_or_kb = update_data.updateid

                        UNION

                        SELECT
                            up_black_list.id,
                            up_black_list.updateid_or_kb,
                            up_black_list.updateid_or_kb AS title,
                            "major update" AS severity
                        FROM xmppmaster.up_black_list
                        WHERE up_black_list.updateid_or_kb LIKE '%%win10upd_%%'
                            OR up_black_list.updateid_or_kb LIKE '%%win11upd_%%'
                    ) AS combined_results
                """

            # Add a filter condition if the filter is not empty
            if filter:
                sql += """
                    WHERE
                        (title LIKE :filter OR
                        CONCAT("KB", updateid_or_kb) LIKE :filter OR
                        severity LIKE :filter OR
                        updateid_or_kb LIKE :filter)
                """

            # Add ordering and pagination
            sql += """
                ORDER BY FIELD(severity, "major update", "Critical", "Important", "Corrective")
                LIMIT :start, :limit;
            """
            logger.debug(f"Executing SQL: {sql}")

            # Execute the query with bind parameters
            result = session.execute(
                sql,
                {
                    "filter": f"%{filter}%" if filter else None,
                    "start": start,
                    "limit": limit,
                },
            )

            # Count the total number of matching elements
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            black_list["nb_element_total"] = ret_count.first()[0]

            session.commit()
            session.flush()

            # Process query results
            if result:
                for list_b in result:
                    black_list["id"].append(list_b.id)
                    black_list["updateid_or_kb"].append(list_b.updateid_or_kb)
                    black_list["title"].append(list_b.title)
                    black_list["severity"].append(list_b.severity)

        except Exception as e:
            # Log any errors encountered
            logger.error(f"Error in function get_black_list: {e}")
        return black_list

    @DatabaseHelper._sessionm
    def get_grey_list(self, session, start, limit, filter=""):
        """
        Retrieve the grey list of updates with optional filtering, sorting, and pagination.

        Args:
            session: Database session object for executing queries.
            start (int): Starting index for pagination.
            limit (int): Maximum number of results to retrieve.
            filter (str): Optional filter to apply to the query (title, kb, severity, or updateid).

        Returns:
            dict: A dictionary containing:
                - nb_element_total (int): Total number of elements matching the query.
                - updateid (list): List of update IDs.
                - title (list): List of update titles.
                - kb (list): List of knowledge base IDs.
                - valided (list): List of validation statuses.
                - severity (list): List of severity levels for each update.
        """
        try:
            # Ensure start and limit are integers
            start = int(start)
        except ValueError:
            start = -1
        try:
            limit = int(limit)
        except ValueError:
            limit = -1

        try:
            # Initialize the result structure
            grey_list = {
                "nb_element_total": 0,
                "updateid": [],
                "title": [],
                "kb": [],
                "valided": [],
                "severity": [],
            }

            # Base SQL query
            sql_base = """SELECT SQL_CALC_FOUND_ROWS *
                        FROM (
                            SELECT
                                up_gray_list.updateid,
                                up_gray_list.title,
                                up_gray_list.kb,
                                up_gray_list.valided,
                                COALESCE(NULLIF(update_data.msrcseverity, ""), "Corrective") AS severity
                            FROM xmppmaster.up_gray_list
                            JOIN xmppmaster.update_data
                            ON xmppmaster.update_data.updateid = up_gray_list.updateid

                            UNION

                            SELECT
                                up_gray_list.updateid,
                                up_gray_list.title,
                                up_gray_list.kb,
                                up_gray_list.valided,
                                "major update" AS severity
                            FROM xmppmaster.up_gray_list
                            WHERE up_gray_list.title LIKE '%%win10upd_%%'
                                OR up_gray_list.title LIKE '%%win11upd_%%'
                        ) AS combined_results
                    """

            # Add filter clause if filter is provided
            if filter:
                filter_clause = """
                    WHERE (title LIKE :filter OR
                        CONCAT("KB", kb) LIKE :filter OR
                        severity LIKE :filter OR
                        updateid LIKE :filter)
                """
                sql_base += filter_clause

            # Add ordering and pagination
            sql = f"""{sql_base}
                    ORDER BY FIELD(severity, "major update", "Critical", "Important", "Corrective")
                    LIMIT :start, :limit;
                """

            logger.debug(f"Executing SQL: {sql}")

            # Execute the query
            result = session.execute(
                sql,
                {
                    "filter": f"%{filter}%" if filter else None,
                    "start": start,
                    "limit": limit,
                },
            )

            # Count the total number of matching elements
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            grey_list["nb_element_total"] = ret_count.first()[0]

            session.commit()
            session.flush()

            # Process query results
            if result:
                for list_g in result:
                    grey_list["updateid"].append(list_g.updateid)
                    grey_list["title"].append(list_g.title)
                    grey_list["kb"].append(list_g.kb)
                    grey_list["valided"].append(list_g.valided)
                    grey_list["severity"].append(list_g.severity)

        except Exception as e:
            # Log any errors encountered
            logger.error(f"Error in function get_grey_list: {e}")
        return grey_list

    @DatabaseHelper._sessionm
    def get_white_list(self, session, start=0, limit=-1, filter=""):
        """
        Retrieve the white list of updates with optional filtering, sorting, and pagination.

        Args:
            session: Database session object for executing queries.
            start (int): Starting index for pagination. Default is 0.
            limit (int): Maximum number of results to retrieve. Default is -1 (no limit).
            filter (str): Optional filter to apply to the query (title, kb, severity, or updateid).

        Returns:
            dict: A dictionary containing:
                - nb_element_total (int): Total number of elements matching the query.
                - updateid (list): List of update IDs.
                - title (list): List of update titles.
                - kb (list): List of knowledge base IDs.
                - severity (list): List of severity levels for each update.
        """
        try:
            # Ensure 'start' and 'limit' are integers; default to -1 if invalid
            start = int(start)
        except ValueError:
            start = -1
        try:
            limit = int(limit)
        except ValueError:
            limit = -1

        try:
            # Initialize the result structure
            white_list = {
                "nb_element_total": 0,
                "updateid": [],
                "title": [],
                "kb": [],
                "severity": [],
            }

            # Base query without the filter
            sql_base = """SELECT SQL_CALC_FOUND_ROWS *
                        FROM (
                            SELECT
                                up_white_list.updateid,
                                up_white_list.title,
                                up_white_list.kb,
                                COALESCE(NULLIF(update_data.msrcseverity, ""), "Corrective") AS severity
                            FROM xmppmaster.up_white_list
                            JOIN xmppmaster.update_data
                            ON xmppmaster.update_data.updateid = xmppmaster.up_white_list.updateid

                            UNION

                            SELECT
                                up_white_list.updateid,
                                up_white_list.title,
                                up_white_list.kb,
                                "major update" AS severity
                            FROM xmppmaster.up_white_list
                            WHERE up_white_list.title LIKE '%%win10upd_%%'
                                OR up_white_list.title LIKE '%%win11upd_%%'
                        ) AS combined_results
                    """

            # Add the filter condition only if a valid filter is provided
            if filter:
                filter_clause = """
                    WHERE
                    (title LIKE :filter OR
                    CONCAT("KB", kb) LIKE :filter OR
                    severity LIKE :filter OR
                    updateid LIKE :filter)
                """
            else:
                filter_clause = ""

            # Add ordering and pagination
            sql = f"""{sql_base}
                    {filter_clause}
                    ORDER BY FIELD(severity, "major update", "Critical", "Important", "Corrective")
                    LIMIT :start, :limit;
                """

            # Log the query for debugging purposes
            logger.debug(f"Executing SQL: {sql}")

            # Execute the query with bind parameters
            result = session.execute(
                sql,
                {
                    "filter": f"%{filter}%" if filter else None,
                    "start": start,
                    "limit": limit
                }
            )

            # Retrieve the total count of matching elements
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]
            white_list["nb_element_total"] = nb_element_total

            # Process query results and populate the white_list dictionary
            if result:
                for list_w in result:
                    white_list["updateid"].append(list_w.updateid)
                    white_list["title"].append(list_w.title)
                    white_list["kb"].append(list_w.kb)
                    white_list["severity"].append(list_w.severity)

        except Exception as e:
            # Log any errors encountered during execution
            logger.error("Error in function get_white_list: %s", e)
            logger.error("\n%s" % (traceback.format_exc()))

        # Return the resulting white list
        return white_list


    @DatabaseHelper._sessionm
    def get_enabled_updates_list(
        self,
        session,
        entity,
        upd_list="gray",
        start=0,
        limit=-1,
        filter="",
        config=None,
    ):
        """
        Récupère la liste des mises à jour activées pour une entité donnée.

        Args:
            session: Objet de session SQLAlchemy utilisé pour exécuter les requêtes.
            entity (str): L'entité UUID pour laquelle récupérer les mises à jour.
            upd_list (str, optional): Le type de liste de mise à jour ("gray" par défaut).
            start (int, optional): Index de départ pour la pagination (par défaut 0).
            limit (int, optional): Nombre maximal de résultats pour la pagination (par défaut -1 pour aucun).
            filter (str, optional): Chaîne de filtre pour rechercher dans les résultats (par défaut vide).
            config (obj, optional): Configuration additionnelle contenant des filtres dynamiques.

        Returns:
            dict: Un dictionnaire contenant :
                - nb_element_total (int): Le nombre total d'éléments correspondant.
                - updateid (list): Liste des identifiants des mises à jour.
                - title (list): Liste des titres des mises à jour.
                - kb (list): Liste des identifiants KB.
                - missing (list): Nombre de machines manquant les mises à jour.
                - installed (list): Nombre de machines ayant les mises à jour installées.
                - history_list (list): Historique des mises à jour par machine.

        Raises:
            Exception: Si une erreur survient pendant l'exécution des requêtes SQL.
        """
        try:
            # Convertir les paramètres `start` et `limit` en entiers avec gestion d'erreurs
            start = int(start)
        except:
            start = -1
        try:
            limit = int(limit)
        except:
            limit = -1

        # Construire le filtre dynamique en fonction des paramètres de configuration
        filter_on = ""
        if config.filter_on is not None:
            for key in config.filter_on:
                if key == "state":
                    filter_on += f" AND lgf.states_id in ({','.join(config.filter_on[key])})"
                elif key == "type":
                    filter_on += f" AND lgf.computertypes_id in ({','.join(config.filter_on[key])})"
                elif key == "entity":
                    filter_on += f" AND lgf.entities_id in ({','.join(config.filter_on[key])})"

        try:
            # Initialisation du dictionnaire de résultat
            enabled_updates_list = {
                "nb_element_total": 0,
                "updateid": [],
                "title": [],
                "kb": [],
                "missing": [],
                "installed": [],
                "history_list": [],
            }

            # Construire la requête SQL principale pour récupérer les mises à jour
            sql = f"""
                SELECT SQL_CALC_FOUND_ROWS
                    uma.update_id as updateid,
                    ud.kb AS kb,
                    ud.title AS title,
                    ud.description AS description,
                    ud.creationdate AS creationdate,
                    ud.title_short AS title_short,
                    count(uma.update_id) as missing
                FROM xmppmaster.up_machine_activated uma
                JOIN xmppmaster.update_data ud ON uma.update_id = ud.updateid
                JOIN xmppmaster.local_glpi_machines lgm ON lgm.id = uma.glpi_id
                JOIN xmppmaster.local_glpi_filters lgf ON lgf.id = lgm.id
                WHERE uma.entities_id = '{entity.replace("UUID", "")}'
                AND list = "{upd_list}"
                {filter_on}
            """

            # Ajouter des filtres dynamiques si le paramètre `filter` est défini
            if filter:
                filterwhere = f"""AND
                    (ud.title LIKE '%%{filter}%%'
                    OR ud.updateid LIKE '%%{filter}%%'
                    OR ud.kb LIKE '%%{filter}%%'
                    OR ud.description LIKE '%%{filter}%%'
                    OR ud.creationdate LIKE '%%{filter}%%'
                    OR ud.title_short LIKE '%%{filter}%%')"""
                sql += filterwhere

            # Ajouter la clause GROUP BY et LIMIT pour la pagination
            sql += " GROUP BY uma.update_id"
            if start != -1 and limit != -1:
                sql += f" LIMIT {start}, {limit}"
            sql += ";"

            # Exécuter la requête SQL principale
            result = session.execute(sql)

            # Récupérer le nombre total d'éléments correspondant
            sql_count = "SELECT FOUND_ROWS();"
            try:
                ret_count = session.execute(sql_count)
            except Exception as e:
                logging.getLogger().error(e)
            nb_element_total = ret_count.first()[0]
            enabled_updates_list["nb_element_total"] = nb_element_total

            session.commit()
            session.flush()

            # Traiter les résultats de la requête principale
            if result:
                for list_b in result:
                    # Requête SQL secondaire pour obtenir les données d'installation
                    sql2 = f"""
                        SELECT
                            count(ma.id) as count,
                            COALESCE(group_concat(lgm.id), NULL, "") as list
                        FROM xmppmaster.machines ma
                        JOIN xmppmaster.local_glpi_machines lgm ON concat("UUID", lgm.id) = ma.uuid_inventorymachine
                        JOIN xmppmaster.up_history uh ON uh.id_machine = ma.id
                        JOIN xmppmaster.local_glpi_entities lge ON lgm.entities_id = lge.id
                        WHERE uh.update_id = '{list_b.updateid}'
                        AND lge.id = {entity.replace("UUID", "")}
                        AND uh.delete_date IS NOT NULL
                        {filter_on}
                    """
                    try:
                        res = session.execute(sql2)
                    except Exception as e:
                        logger.error(e)
                    installed = 0
                    history_list = ""
                    if res:
                        for _res in res:
                            installed = _res.count
                            history_list = _res.list
                    # Ajouter les résultats au dictionnaire de sortie
                    enabled_updates_list["updateid"].append(list_b.updateid)
                    enabled_updates_list["title"].append(list_b.title)
                    enabled_updates_list["kb"].append(list_b.kb)
                    enabled_updates_list["missing"].append(list_b.missing)
                    enabled_updates_list["installed"].append(installed)

        except Exception as e:
            # Gérer les exceptions et enregistrer l'erreur
            logger.error("error function get_enabled_updates_list %s" % e)

        return enabled_updates_list


    @DatabaseHelper._sessionm
    def approve_update(self, session, updateid):
        try:
            sql = """SELECT updateid,
                        kb,
                        title,
                        description
                    FROM xmppmaster.up_gray_list
                    WHERE updateid = '%s' or kb='%s' LIMIT 1;""" % (
                updateid,
                updateid,
            )
            result = session.execute(sql)
            selected = {"updateid": "", "kb": "", "title": "", "description": ""}

            if result is not None:
                selected = [
                    {
                        "updateid": elem.updateid,
                        "kb": elem.kb,
                        "title": elem.title,
                        "description": elem.description,
                    }
                    for elem in result
                ]
            selected = selected[0]

            sql2 = """INSERT INTO 
                        xmppmaster.up_white_list (updateid, kb, title, description, valided) 
                        VALUES("%s", "%s", "%s", "%s", %s)""" % (
                selected["updateid"],
                selected["kb"],
                selected["title"],
                selected["description"],
                1,
            )
            session.execute(sql2)

            session.commit()
            session.flush()
            return True
        except Exception as e:
            return False

    @DatabaseHelper._sessionm
    def grey_update(self, session, updateid, enabled=0):
        try:
            sql = """UPDATE `xmppmaster`.`up_gray_list`
                    SET
                        valided = %s
                    WHERE
                        (updateid = '%s');""" % (
                enabled,
                updateid,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logging.getLogger().error(str(e))
        return False

    @DatabaseHelper._sessionm
    def exclude_update(self, session, updateid):
        try:
            sql = """INSERT IGNORE INTO xmppmaster.up_black_list (updateid_or_kb, userjid_regexp, enable_rule, type_rule)
                VALUES ('%s', '.*', '1', 'id');""" % (
                updateid
            )

            result = session.execute(sql)
            session.commit()

            session.flush()
            return True
        except Exception as e:
            logging.getLogger().error(str(e))
        return False

    @DatabaseHelper._sessionm
    def delete_rule(self, session, id):
        try:
            sql_add = """INSERT INTO xmppmaster.up_gray_list (updateid, kb, revisionid, title, updateid_package, payloadfiles)
        SELECT xmppmaster.up_packages.updateid, xmppmaster.up_packages.kb, xmppmaster.up_packages.revisionid, xmppmaster.up_packages.title, xmppmaster.up_packages.updateid_package, xmppmaster.up_packages.payloadfiles FROM xmppmaster.up_packages
JOIN xmppmaster.up_black_list ON xmppmaster.up_packages.updateid = xmppmaster.up_black_list.updateid_or_kb or xmppmaster.up_packages.kb = xmppmaster.up_black_list.updateid_or_kb WHERE xmppmaster.up_black_list.id=%s;""" % (
                id
            )

            sql = (
                """DELETE FROM `xmppmaster`.`up_black_list` WHERE (`id` = '%s');"""
                % (id)
            )

            result = session.execute(sql_add)
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True

        except Exception as e:
            logging.getLogger().error(str(e))
        return False

    @DatabaseHelper._sessionm
    def get_family_list(self, session, start, end, filter=""):
        try:
            family_list = {"nb_element_total": 0, "name_procedure": []}

            sql = """SELECT SQL_CALC_FOUND_ROWS
                        *
                    FROM
                        xmppmaster.up_list_produit 
                    WHERE
                        enable = 1 """

            if filter:
                filterwhere = (
                    """AND
                        name_procedure LIKE '%%%s%%'
                    LIMIT 5 OFFSET 5"""
                    % filter
                )
                sql = sql + filterwhere

            sql += ";"

            result = session.execute(sql)

            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]

            family_list["nb_element_total"] = nb_element_total

            session.commit()
            session.flush()

            if result:
                for list_f in result:
                    family_list["name_procedure"].append(list_f.name_procedure)

        except Exception as e:
            logger.error("error function get_family_list")

        return family_list

    @DatabaseHelper._sessionm
    def get_count_machine_as_not_upd(self, session, updateid):
        """
        This function returns the the update already done and update enable
        """
        sql = """SELECT COUNT(*) AS nb_machine_missing_update
                FROM
                    xmppmaster.up_machine_windows
                WHERE
                    (update_id = '%s');""" % (
            updateid
        )

        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        result = [
            {column: value for column, value in rowproxy.items()}
            for rowproxy in resultquery
        ]
        return result

    @DatabaseHelper._sessionm
    def get_machines_needing_update(
        self, session, updateid, uuid, config, start=0, limit=-1, filter=""
    ):
        """
        This function returns the list of machines needing a specific update
        """
        slimit = "limit %s" % start
        try:
            limit = int(limit)
        except:
            limit = -1

        if limit != -1:
            slimit = "%s,%s" % (slimit, limit)

        filter_on = ""

        sfilter = ""
        if filter != "":
            sfilter = """AND
    (lgm.name LIKE '%%%s%%'
    OR uma.update_id LIKE '%%%s%%'
    OR m.platform LIKE '%%%s%%'
    OR uma.kb LIKE '%%%s%%')""" % tuple(
                filter for x in range(0, 4)
            )

        if config.filter_on is not None:
            for key in config.filter_on:
                if key not in ["state", "entity", "type"]:
                    continue
                if key == "state":
                    filter_on = "%s AND lgf.states_id in (%s)" % (
                        filter_on,
                        ",".join(config.filter_on[key]),
                    )
                if key == "type":
                    filter_on = "%s AND lgf.computertypes_id in (%s)" % (
                        filter_on,
                        ",".join(config.filter_on[key]),
                    )
                if key == "entity":
                    filter_on = "%s AND lgf.entities_id in (%s)" % (
                        filter_on,
                        ",".join(config.filter_on[key]),
                    )

        sql = """select
    SQL_CALC_FOUND_ROWS
    lgm.id,
    lgm.name,
    m.platform,
    concat("KB", uma.kb) as kb
from xmppmaster.up_machine_activated uma
join xmppmaster.machines m on uma.id_machine = m.id
join xmppmaster.local_glpi_machines lgm on concat("UUID", lgm.id) = m.uuid_inventorymachine
join xmppmaster.local_glpi_filters lgf on lgf.id = lgm.id
where uma.update_id = "%s"
and lgm.is_deleted = 0
and lgm.is_template = 0
and lgm.entities_id = %s
%s
%s
%s;
""" % (
            updateid,
            uuid.replace("UUID", ""),
            sfilter,
            filter_on,
            slimit,
        )
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        count = session.execute("SELECT FOUND_ROWS();")
        count = [elem[0] for elem in count][0]

        result = {
            "datas": {"id": [], "name": [], "platform": [], "kb": []},
            "total": count,
        }

        if resultquery:
            for row in resultquery:
                result["datas"]["id"].append(row.id)
                result["datas"]["name"].append(row.name)
                result["datas"]["platform"].append(row.platform)
                result["datas"]["kb"].append(row.kb)
        return result

    @DatabaseHelper._sessionm
    def white_unlist_update(self, session, updateid):
        sql = (
            """DELETE FROM xmppmaster.up_white_list WHERE updateid = '%s' or kb='%s'"""
            % (updateid, updateid)
        )
        try:
            session.execute(sql)
            session.commit()
            session.flush()
            return True
        except:
            return False
