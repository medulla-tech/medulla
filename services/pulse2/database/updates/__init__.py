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

# sql debug mode
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


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
    def get_black_list(self, session,
                    start=0,
                    limit=-1,
                    filter="",
                    entityid=None):
        """
        Retrieve the black list of updates with optional filtering, sorting, and pagination.
        If `entityid` is provided (not None or -1), only returns updates for the specified entity.

        Args:
            session: Database session object for executing queries.
            start (int): Starting index for pagination. Default is 0.
            limit (int): Maximum number of results to retrieve. Default is -1 (no limit).
            filter (str): Optional filter to apply to the query (title, kb, severity, or updateid).
            entityid (int, optional): If provided (not None or -1), filters the results by the specified entity ID. Default is None.

        Returns:
            dict: A dictionary containing:
                - nb_element_total (int): Total number of elements matching the query.
                - id (list): List of record IDs from `up_black_list`.
                - updateid_or_kb (list): List of KB numbers or update IDs.
                - title (list): List of update titles.
                - severity (list): List of severity levels for each update.
        """
        if entityid in (-1, None, "None", ""):
            entityid = None
        else:
            try:
                entityid = int(entityid)
            except Exception:
                entityid = None

        try:
            # Ensure pagination values are integers
            try:
                start = int(start) if start != -1 else 0
            except ValueError:
                start = 0

            try:
                limit = int(limit) if limit != -1 else -1
            except ValueError:
                limit = -1

            # Initialize the result structure
            black_list = {
                "nb_element_total": 0,
                "id": [],
                "updateid_or_kb": [],
                "title": [],
                "severity": [],
            }
            logger.debug(f"entityid{entityid}")
            # Build entity conditions for both parts of the UNION
            if entityid is not None:
                entity_condition_1 = "AND up_black_list.entityid = :entityid"
                entity_condition_2 = "AND up_black_list.entityid = :entityid"
            else:
                entity_condition_1 = ""
                entity_condition_2 = ""

            # Base query with UNION
            sql_base = f"""
                SELECT SQL_CALC_FOUND_ROWS *
                FROM (
                    SELECT
                        up_black_list.id,
                        up_black_list.updateid_or_kb,
                        update_data.title,
                        COALESCE(NULLIF(update_data.msrcseverity, ""), "Corrective") AS severity
                    FROM xmppmaster.up_black_list
                    INNER JOIN xmppmaster.update_data
                    ON (up_black_list.updateid_or_kb = update_data.kb
                        OR up_black_list.updateid_or_kb = update_data.updateid)
                    {entity_condition_1}

                    UNION

                    SELECT
                        up_black_list.id,
                        up_black_list.updateid_or_kb,
                        up_black_list.updateid_or_kb AS title,
                        "major update" AS severity
                    FROM xmppmaster.up_black_list
                    WHERE (up_black_list.updateid_or_kb LIKE '%%win10upd_%%'
                        OR up_black_list.updateid_or_kb LIKE '%%win11upd_%%')
                    {entity_condition_2}
                ) AS combined_results
            """

            # Add filter condition if provided
            if filter:
                filter_clause = """
                    WHERE
                    (title LIKE :filter OR
                    severity LIKE :filter OR
                    updateid_or_kb LIKE :filter)
                """
            else:
                filter_clause = ""

            # Final SQL with ordering and pagination
            sql = f"""{sql_base}
                    {filter_clause}
                    ORDER BY FIELD(severity, "major update", "Critical", "Important", "Corrective")
                    LIMIT :start, :limit;
                """

            # Debug log
            logger.debug(f"Executing SQL: {sql}")

            # Prepare query parameters
            params = {"start": start, "limit": limit}
            if filter:
                params["filter"] = f"%{filter}%"
            if entityid is not None:
                params["entityid"] = entityid

            # Execute query
            result = session.execute(sql, params)

            # Retrieve total count of matching elements
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            nb_element_total = ret_count.first()[0]
            black_list["nb_element_total"] = nb_element_total

            # Process query results
            if result:
                for list_b in result:
                    black_list["id"].append(list_b.id)
                    black_list["updateid_or_kb"].append(list_b.updateid_or_kb)
                    black_list["title"].append(list_b.title)
                    black_list["severity"].append(list_b.severity)

        except Exception as e:
            # Log errors
            logger.error("Error in function get_black_list: %s", e)
            logger.error("\n%s" % (traceback.format_exc()))

        # Return the resulting black list
        return black_list


    @DatabaseHelper._sessionm
    def get_white_list(self, session,
                    start: int = 0,
                    limit: int = -1,
                    filter: str = "",
                    entityid: int = None):
        """
        Retrieve the white list of updates with optional filtering, sorting, and pagination.

        This function queries the `up_white_list` table and joins it with `update_data` to retrieve
        update information. It handles both normal updates (with matching updateid) and
        "major updates" (win10upd_ / win11upd_). If an `entityid` is provided (not None or -1),
        the query will restrict results to updates belonging to that entity.

        Args:
            session: SQLAlchemy database session object used to execute queries.
            start (int): Starting index for pagination. If -1 or invalid, defaults to 0.
            limit (int): Maximum number of results to retrieve. If -1 or invalid, no limit is applied.
            filter (str, optional): Optional text filter applied on title, kb, severity,
                                    or updateid. Default is "" (no filter).
            entityid (int, optional): If provided (not None or -1), only returns updates belonging
                                    to the specified entity. Default is None.

        Returns:
            dict: A dictionary containing:
                - nb_element_total (int): Total number of matching elements across all pages.
                - updateid (list): List of update IDs.
                - title (list): List of update titles.
                - kb (list): List of knowledge base IDs.
                - severity (list): List of severity levels for each update.
        """
        if entityid in (-1, None, "None", ""):
            entityid = None
        else:
            try:
                entityid = int(entityid)
            except Exception:
                entityid = None

        try:
            # Ensure 'start' and 'limit' are integers
            try:
                start = int(start) if start != -1 else 0
            except ValueError:
                start = 0

            try:
                limit = int(limit) if limit != -1 else -1
            except ValueError:
                limit = -1

            # Initialize the result structure
            white_list = {
                "nb_element_total": 0,
                "updateid": [],
                "title": [],
                "kb": [],
                "severity": [],
            }

            # Conditions for entity filtering
            if entityid is not None:
                entity_condition_1 = "AND up_white_list.entityid = :entityid"
                entity_condition_2 = "AND up_white_list.entityid = :entityid"
            else:
                entity_condition_1 = ""
                entity_condition_2 = ""

            # Base query with UNION
            sql_base = f"""
                SELECT SQL_CALC_FOUND_ROWS *
                FROM (
                    SELECT
                        up_white_list.updateid,
                        up_white_list.title,
                        up_white_list.kb,
                        COALESCE(NULLIF(update_data.msrcseverity, ""), "Corrective") AS severity
                    FROM xmppmaster.up_white_list
                    JOIN xmppmaster.update_data
                    ON xmppmaster.update_data.updateid = up_white_list.updateid
                    {entity_condition_1}

                    UNION

                    SELECT
                        up_white_list.updateid,
                        up_white_list.title,
                        up_white_list.kb,
                        "major update" AS severity
                    FROM xmppmaster.up_white_list
                    WHERE (up_white_list.title LIKE '%%win10upd_%%'
                        OR up_white_list.title LIKE '%%win11upd_%%')
                    {entity_condition_2}
                ) AS combined_results
            """

            # Add filter if provided
            if filter:
                sql_base += """
                    WHERE (title LIKE :filter OR
                        CONCAT("KB", kb) LIKE :filter OR
                        severity LIKE :filter OR
                        updateid LIKE :filter)
                """

            # Add ordering and pagination
            sql = f"""{sql_base}
                    ORDER BY FIELD(severity, "major update", "Critical", "Important", "Corrective")
                    LIMIT :start, :limit;
                """

            logger.debug(f"Executing SQL: {sql}")

            # Prepare parameters for the query
            params = {"start": start, "limit": limit}
            if filter:
                params["filter"] = f"%{filter}%"
            if entityid is not None:
                params["entityid"] = entityid

            # Execute the query
            result = session.execute(sql, params)

            # Retrieve total number of elements
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            white_list["nb_element_total"] = ret_count.first()[0]

            session.commit()
            session.flush()

            # Process query results
            if result:
                for row in result:
                    white_list["updateid"].append(row.updateid)
                    white_list["title"].append(row.title)
                    white_list["kb"].append(row.kb)
                    white_list["severity"].append(row.severity)

        except Exception as e:
            logger.error("Error in function get_white_list: %s", e)
            logger.error("\n%s" % (traceback.format_exc()))

        return white_list



    @DatabaseHelper._sessionm
    def get_grey_list(self, session, start, limit, filter: str = "", entityid: int = None):
        """
        Retrieve the grey list of updates with optional filtering, sorting, and pagination.

        This function queries the `up_gray_list` table and joins it with `update_data` to retrieve
        update information. It handles both normal updates (with matching updateid) and
        "major updates" (win10upd_ / win11upd_). If an `entityid` is provided (not None or -1),
        the query will restrict results to updates belonging to that entity.

        Args:
            session: SQLAlchemy database session object used to execute queries.
            start (int): Starting index for pagination. If -1 or invalid, defaults to 0.
            limit (int): Maximum number of results to retrieve. If -1 or invalid, no limit is applied.
            filter (str, optional): Optional text filter applied on title, kb, severity,
                                    or updateid. Default is "" (no filter).
            entityid (int, optional): If provided (not None or -1), only returns updates belonging
                                    to the specified entity. Default is None.

        Returns:
            dict: A dictionary containing:
                - nb_element_total (int): Total number of matching elements across all pages.
                - updateid (list): List of update IDs.
                - title (list): List of update titles.
                - kb (list): List of knowledge base IDs.
                - valided (list): List of validation statuses.
                - severity (list): List of severity levels for each update.
        """
        if entityid in (-1, None, "None", ""):
            entityid = None
        else:
            try:
                entityid = int(entityid)
            except Exception:
                entityid = None
        try:
            # Ensure start and limit are valid integers
            try:
                start = int(start) if start != -1 else 0
            except ValueError:
                start = 0

            try:
                limit = int(limit) if limit != -1 else -1
            except ValueError:
                limit = -1

            # Initialize result structure
            grey_list = {
                "nb_element_total": 0,
                "updateid": [],
                "title": [],
                "kb": [],
                "valided": [],
                "severity": [],
            }

            # Conditions for entity filtering
            if entityid is not None:
                entity_condition_1 = "AND up_gray_list.entityid = :entityid"
                entity_condition_2 = "AND up_gray_list.entityid = :entityid"
            else:
                entity_condition_1 = ""
                entity_condition_2 = ""

            # Base SQL with UNION
            sql_base = f"""
                SELECT SQL_CALC_FOUND_ROWS *
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
                    {entity_condition_1}

                    UNION

                    SELECT
                        up_gray_list.updateid,
                        up_gray_list.title,
                        up_gray_list.kb,
                        up_gray_list.valided,
                        "major update" AS severity
                    FROM xmppmaster.up_gray_list
                    WHERE (up_gray_list.title LIKE '%%win10upd_%%'
                        OR up_gray_list.title LIKE '%%win11upd_%%')
                    {entity_condition_2}
                ) AS combined_results
            """

            # Apply filter if provided
            if filter:
                sql_base += """
                    WHERE (title LIKE :filter OR
                        CONCAT("KB", kb) LIKE :filter OR
                        severity LIKE :filter OR
                        updateid LIKE :filter)
                """

            # Add ordering and pagination
            sql = f"""{sql_base}
                    ORDER BY FIELD(severity, "major update", "Critical", "Important", "Corrective")
                    LIMIT :start, :limit;
                """

            logger.debug(f"Executing SQL: {sql}")

            # Prepare query parameters
            params = {"start": start, "limit": limit}
            if filter:
                params["filter"] = f"%{filter}%"
            if entityid is not None:
                params["entityid"] = entityid

            # Execute query
            result = session.execute(sql, params)

            # Count total results
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            grey_list["nb_element_total"] = ret_count.first()[0]

            session.commit()
            session.flush()

            # Process query results
            if result:
                for row in result:
                    grey_list["updateid"].append(row.updateid)
                    grey_list["title"].append(row.title)
                    grey_list["kb"].append(row.kb)
                    grey_list["valided"].append(row.valided)
                    grey_list["severity"].append(row.severity)

        except Exception as e:
            logger.error(f"Error in function get_grey_list: {e}")

        return grey_list


    # ######################## group update windows ########################
    @DatabaseHelper._sessionm
    def get_machines_update_grp(self,
                                session,
                                entity_id,
                                type="windows",
                                colonne="hardware_requirements"):
        """
        Dispatcher pour les fonctions spécialisées de récupération des machines.
        Appelle la fonction appropriée en fonction de `type` et `colonne`.
        """
        try:
            entity_id = int(entity_id)
        except (ValueError, TypeError):
            return {}

        if type == "windows":
            if colonne == "hardware_requirements":
                return self._get_windows_hardware_requirements(session, entity_id)
            elif colonne == "W11to11":
                return self._get_windows_W11to11(session, entity_id)
            elif colonne == "W10to10":
                return self._get_windows_W10to10(session, entity_id)
            elif colonne == "W10to11":
                return self._get_windows_W10to11(session, entity_id)
            elif colonne == "UPDATED":
                return self._get_windows_UPDATED(session, entity_id)

        return {}

    # Fonction spécialisée pour hardware_requirements
    def _get_windows_hardware_requirements(self, session, entity_id):
        ret = {}
        sql = """
        SELECT hostname, glpi_id
        FROM xmppmaster.up_major_win
        WHERE ent_id = :ent_id
            AND old_version = '10'
            AND new_version = '11'
            AND is_active = 'False';
        """
        rows = session.execute(sql, {"ent_id": entity_id})
        for row in rows:
            hostname = row.hostname
            guid = row.glpi_id
            if hostname:
                id_uuid = f"UUID{guid}"
                ret[f"{id_uuid}##{hostname}"] = {
                    "hostname": hostname,
                    "uuid": id_uuid,
                }
        return ret

    # Fonction spécialisée pour W11to11
    def _get_windows_W11to11(self, session, entity_id):
        ret = {}
        sql = """
        SELECT hostname, glpi_id
        FROM xmppmaster.up_major_win
        WHERE ent_id = :ent_id
            AND old_version = '11'
            AND new_version = '11'
            AND old_code != '25H2';
        """
        rows = session.execute(sql, {"ent_id": entity_id})
        for row in rows:
            hostname = row.hostname
            guid = row.glpi_id
            if hostname:
                id_uuid = f"UUID{guid}"
                ret[f"{id_uuid}##{hostname}"] = {
                    "hostname": hostname,
                    "uuid": id_uuid,
                }
        return ret

    # Fonction spécialisée pour W10to10
    def _get_windows_W10to10(self, session, entity_id):
        ret = {}
        sql = """
        SELECT hostname, glpi_id
        FROM xmppmaster.up_major_win
        WHERE ent_id = :ent_id
            AND old_version = '10'
            AND new_version = '10'
            AND old_code != '22H2';
        """
        rows = session.execute(sql, {"ent_id": entity_id})
        for row in rows:
            hostname = row.hostname
            guid = row.glpi_id
            if hostname:
                id_uuid = f"UUID{guid}"
                ret[f"{id_uuid}##{hostname}"] = {
                    "hostname": hostname,
                    "uuid": id_uuid,
                }
        return ret

    # Fonction spécialisée pour W10to11
    def _get_windows_W10to11(self, session, entity_id):
        ret = {}
        sql = """
        SELECT hostname, glpi_id
        FROM xmppmaster.up_major_win
        WHERE ent_id = :ent_id
            AND old_version = '10'
            AND new_version = '11'
            AND is_active != 'False';
        """
        rows = session.execute(sql, {"ent_id": entity_id})
        for row in rows:
            hostname = row.hostname
            guid = row.glpi_id
            if hostname:
                id_uuid = f"UUID{guid}"
                ret[f"{id_uuid}##{hostname}"] = {
                    "hostname": hostname,
                    "uuid": id_uuid,
                }
        return ret

    # Fonction spécialisée pour UPDATED
    def _get_windows_UPDATED(self, session, entity_id):
        ret = {}
        sql = """
        SELECT hostname, glpi_id
        FROM xmppmaster.up_major_win
        WHERE ent_id = :ent_id
            AND old_version = '11'
            AND new_version = '11'
            AND old_code = '25H2';
        """
        rows = session.execute(sql, {"ent_id": entity_id})
        for row in rows:
            hostname = row.hostname
            guid = row.glpi_id
            if hostname:
                id_uuid = f"UUID{guid}"
                ret[f"{id_uuid}##{hostname}"] = {
                    "hostname": hostname,
                    "uuid": id_uuid,
                }
        return ret

# ######################## end group update windows ########################
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
            if upd_list == "gray|white":
                list_filter = ""
            else:
                list_filter = f""" AND list = "{upd_list}" """

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
                {list_filter}
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
    def approve_update(self, session, updateid, entityid):
        try:
            entityid = int(entityid)

            # 1️⃣ Sélection depuis la gray list avec bind parameters
            sql = """SELECT updateid, kb, title, description, entityid
                    FROM xmppmaster.up_gray_list
                    WHERE (updateid = :updateid OR kb = :updateid)
                    AND entityid = :entityid
                    LIMIT 1;"""

            result = session.execute(sql, {"updateid": updateid, "entityid": entityid}).fetchone()

            if not result:
                return False  # Rien trouvé → on arrête

            # 2️⃣ Insertion dans la white list avec bind parameters
            insert_sql = """INSERT INTO xmppmaster.up_white_list
                            (updateid, entityid, kb, title, description, valided)
                            VALUES (:updateid, :entityid, :kb, :title, :description, :valided);"""

            session.execute(
                insert_sql,
                {
                    "updateid": result.updateid,
                    "entityid": result.entityid,
                    "kb": result.kb,
                    "title": result.title,
                    "description": result.description,
                    "valided": 1,
                },
            )

            session.commit()
            session.flush()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"[approve_update] ERREUR: {e}")
            return False

    @DatabaseHelper._sessionm
    def grey_update(self, session, updateid, entityid, enabled=0):
        """
        Met à jour le champ 'valided' dans la table xmppmaster.up_gray_list
        pour un enregistrement spécifique (updateid + entityid).

        Args:
            session: SQLAlchemy session.
            updateid: str — UUID ou KB de l'update.
            entityid: int-like — identifiant de l'entité.
            enabled: int (0 ou 1) — nouvelle valeur du champ 'valided'.

        Returns:
            True si la mise à jour a réussi, False sinon.
        """
        try:
            # 🔹 Validation basique
            if not updateid or not str(updateid).strip():
                logging.getLogger().warning("[grey_update] updateid vide ou invalide")
                return False

            try:
                entityid = str(entityid)
                enabled = str(enabled)
            except (TypeError, ValueError):
                logging.getLogger().warning(f"[grey_update] entityid invalide: {entityid!r}")
                return False
            logging.getLogger().info(f"[grey_update]  pour {updateid} / entity={entityid} → valided={enabled}")

            # enabled = 1 if enabled in (1, "1", True) else 0

            # 🔹 Requête paramétrée
            update_sql = """
                UPDATE xmppmaster.up_gray_list
                SET valided = :enabled
                WHERE (updateid = :updateid OR kb = :updateid)
                AND entityid = :entityid;
            """

            params = {
                "enabled": enabled,
                "updateid": str(updateid),
                "entityid": entityid,
            }

            result = session.execute(update_sql, params)

            session.commit()
            session.flush()

            if result.rowcount == 0:
                logging.getLogger().info(f"[grey_update] Aucun enregistrement mis à jour pour {updateid} / entity={entityid}")
            else:
                logging.getLogger().info(f"[grey_update] Mise à jour OK pour {updateid} / entity={entityid} → valided={enabled}")

            return True

        except Exception as e:
            session.rollback()
            logging.getLogger().error(f"[grey_update] ERREUR: {e}", exc_info=True)
            return False


    @DatabaseHelper._sessionm
    def exclude_update(self, session, updateid, entityid):
        """
        Ajoute une règle d'exclusion dans up_black_list (INSERT IGNORE) .

        Args:
            session: SQLAlchemy session.
            updateid: str, uuid ou KB à exclure (doit être non vide)
            entityid: int-like, id de l'entité
        Returns:
            True si OK, False sinon
        """
        try:
            # Validation minimale
            if not updateid or not str(updateid).strip():
                logging.getLogger().warning("[exclude_update] updateid vide")
                return False

            try:
                entityid = int(entityid)
            except (TypeError, ValueError):
                logging.getLogger().warning(f"[exclude_update] entityid invalide: {entityid!r}")
                return False

            # Valeurs fixes / contrôlées
            userjid_regexp = ".*"
            enable_rule = 1
            type_rule = "id"  # si d'autres valeurs possibles, valider ici explicitement

            insert_sql = """
                INSERT IGNORE INTO xmppmaster.up_black_list
                    (updateid_or_kb, entityid, userjid_regexp, enable_rule, type_rule)
                VALUES
                    (:updateid_or_kb, :entityid, :userjid_regexp, :enable_rule, :type_rule);
            """

            params = {
                "updateid_or_kb": str(updateid),
                "entityid": entityid,
                "userjid_regexp": userjid_regexp,
                "enable_rule": enable_rule,
                "type_rule": type_rule,
            }

            session.execute(insert_sql, params)
            session.commit()
            session.flush()
            logging.getLogger().info(f"[exclude_update] rule inserted for updateid={updateid} entityid={entityid}")
            return True

        except Exception as e:
            session.rollback()
            logging.getLogger().error(f"[exclude_update] ERREUR: {e}", exc_info=True)
            return False


    @DatabaseHelper._sessionm
    def delete_rule(self, session, id, entityid):
        """
        Supprime une règle de la black_list et réinsère le package correspondant dans la gray_list.

        Args:
            session: SQLAlchemy session.
            id: ID de la règle à supprimer dans up_black_list.
            entityid: ID de l'entité (utilisé pour filtrer les données par entité).
        """
        try:
            # 1️⃣ Réinsertion dans la gray_list depuis up_packages
            sql_add = """
                INSERT INTO xmppmaster.up_gray_list
                    (updateid, kb, revisionid, title, updateid_package, payloadfiles, entityid)
                SELECT
                    p.updateid,
                    p.kb,
                    p.revisionid,
                    p.title,
                    p.updateid_package,
                    p.payloadfiles,
                    b.entityid
                FROM xmppmaster.up_packages AS p
                JOIN xmppmaster.up_black_list AS b
                ON p.updateid = b.updateid_or_kb OR p.kb = b.updateid_or_kb
                WHERE b.id = :id AND b.entityid = :entityid;
            """

            # 2️⃣ Suppression de la règle dans la black_list
            sql_delete = """
                DELETE FROM xmppmaster.up_black_list
                WHERE id = :id AND entityid = :entityid;
            """

            session.execute(sql_add, {"id": id, "entityid": entityid})
            session.execute(sql_delete, {"id": id, "entityid": entityid})
            session.commit()
            session.flush()
            return True

        except Exception as e:
            session.rollback()
            logging.getLogger().error(f"[delete_rule] ERREUR: {e}", exc_info=True)
            return False

    @DatabaseHelper._sessionm
    def get_family_list(self, session, start, end, filter="", entityid=-1):
        """
        Récupère la liste des familles (produits) actives depuis xmppmaster.up_list_produit.

        Args:
            session: SQLAlchemy session.
            start (int): index de départ pour la pagination.
            end (int): nombre maximal d’éléments à retourner.
            filter (str): texte à rechercher dans name_procedure (optionnel).
            entityid (int): identifiant d'entité (-1 = tous).

        Retour:
            dict {
                "nb_element_total": int,
                "name_procedure": [str, ...]
            }
        """
        family_list = {"nb_element_total": 0, "name_procedure": []}

        try:
            # 🔹 Nettoyage / validation des bornes
            try:
                start = int(start)
                if start < 0:
                    start = 0
            except (TypeError, ValueError):
                start = 0

            try:
                end = int(end)
            except (TypeError, ValueError):
                end = -1

            # 🔹 Calcul du LIMIT / OFFSET
            if end != -1:
                slimit = f" LIMIT {start}, {end}"
            else:
                slimit = f" LIMIT {start}"

            # 🔹 Base de la requête
            sql = """
                SELECT SQL_CALC_FOUND_ROWS *
                FROM xmppmaster.up_list_produit
                WHERE enable = 1
            """

            params = {}

            # 🔹 Si entityid est défini
            if entityid != -1:
                sql += " AND entityid = :entityid"
                params["entityid"] = entityid

            # 🔹 Si un filtre est appliqué
            if filter:
                sql += " AND name_procedure LIKE :filter"
                params["filter"] = f"%{filter}%"

            # 🔹 Ajout de la limite
            sql += slimit + ";"

            # 🔹 Exécution principale
            result = session.execute(sql, params)

            # 🔹 Nombre total d’éléments trouvés
            ret_count = session.execute("SELECT FOUND_ROWS();")
            nb_element_total = ret_count.scalar() or 0
            family_list["nb_element_total"] = nb_element_total

            # 🔹 Récupération des résultats
            for row in result:
                if hasattr(row, "name_procedure"):
                    family_list["name_procedure"].append(row.name_procedure)
                elif "name_procedure" in row.keys():
                    family_list["name_procedure"].append(row["name_procedure"])

            session.commit()
            session.flush()

        except Exception as e:
            session.rollback()
            logger.error(f"[get_family_list] ERREUR: {e}", exc_info=True)

        return family_list

    @DatabaseHelper._sessionm
    def get_count_machine_as_not_upd(self, session, updateid, entityid=-1):
        """
        Retourne le nombre de machines (xmppmaster.up_machine_windows)
        pour lesquelles l'update (updateid) est référencé.

        Si entityid == -1 => pas de filtre par entityid (comportement historique).
        Sinon on ajoute "AND entityid = :entityid".

        Retour:
            dict { "nb_machine_missing_update": int }
        """
        try:
            # validation minimale
            if not updateid or not str(updateid).strip():
                logging.getLogger().warning("[get_count_machine_as_not_upd] updateid vide")
                return {"nb_machine_missing_update": 0}

            try:
                entityid = int(entityid)
            except (TypeError, ValueError):
                logging.getLogger().warning(f"[get_count_machine_as_not_upd] entityid invalide: {entityid!r}")
                return {"nb_machine_missing_update": 0}

            # Construire la requête de façon paramétrée
            base_sql = """
                SELECT COUNT(*) AS nb_machine_missing_update
                FROM xmppmaster.up_machine_windows
                WHERE update_id = :updateid
            """

            params = {"updateid": str(updateid)}

            if entityid != -1:
                base_sql += " AND entityid = :entityid"
                params["entityid"] = entityid

            # Exécuter et récupérer le nombre
            result = session.execute(base_sql, params).fetchone()

            if result is None:
                return {"nb_machine_missing_update": 0}

            # result peut être un RowProxy / Row — accéder soit par clé soit par index
            count = result["nb_machine_missing_update"] if "nb_machine_missing_update" in result.keys() else result[0]
            try:
                count = int(count)
            except (TypeError, ValueError):
                count = 0

            return {"nb_machine_missing_update": count}

        except Exception as e:
            # pas de commit pour une SELECT ; rollback si erreur côté transaction
            try:
                session.rollback()
            except Exception:
                pass
            logging.getLogger().error(f"[get_count_machine_as_not_upd] ERREUR: {e}", exc_info=True)
            return {"nb_machine_missing_update": 0}

    @DatabaseHelper._sessionm
    def get_machines_needing_update(
        self,
        session,
        updateid,
        uuid,
        config,
        start=0,
        limit=-1,
        filter=""
    ):
        """
        Récupère la liste des machines nécessitant une mise à jour spécifique.

        Cette fonction interroge plusieurs tables (up_machine_activated, machines,
        local_glpi_machines, local_glpi_filters) pour identifier les machines
        qui doivent recevoir un update donné.

        Args:
            session: Session SQLAlchemy.
            updateid (str): Identifiant de l'update à rechercher.
            uuid (str): Identifiant d'entité sous la forme "UUID<id>".
            config (object): Objet contenant éventuellement un attribut `filter_on`
                            avec des clés "state", "entity" ou "type".
            start (int, optional): Position de départ pour la pagination. Défaut = 0.
            limit (int, optional): Nombre maximum de lignes à retourner. -1 = pas de limite.
            filter (str, optional): Filtre texte sur le nom, la plateforme, le KB, etc.

        Returns:
            dict: {
                "datas": {
                    "id": [int, ...],
                    "name": [str, ...],
                    "platform": [str, ...],
                    "kb": [str, ...]
                },
                "total": int
            }
        """
        result = {"datas": {"id": [], "name": [], "platform": [], "kb": []}, "total": 0}

        try:
            # 🔹 Validation et calcul du LIMIT / OFFSET
            try:
                start = int(start)
                if start < 0:
                    start = 0
            except (TypeError, ValueError):
                start = 0

            try:
                limit = int(limit)
            except (TypeError, ValueError):
                limit = -1

            if limit != -1:
                slimit = f"LIMIT {start}, {limit}"
            else:
                slimit = f"LIMIT {start}"

            # 🔹 Construction sécurisée des filtres
            sfilter = ""
            params = {"updateid": updateid, "entityid": uuid.replace("UUID", "")}

            if filter:
                sfilter = """
                    AND (
                        lgm.name LIKE :filter
                        OR uma.update_id LIKE :filter
                        OR m.platform LIKE :filter
                        OR uma.kb LIKE :filter
                    )
                """
                params["filter"] = f"%{filter}%"

            # 🔹 Application des filtres dynamiques (config.filter_on)
            filter_on = ""
            if getattr(config, "filter_on", None):
                for key, values in config.filter_on.items():
                    if key not in ["state", "entity", "type"]:
                        continue
                    valid_ids = [v for v in values if str(v).isdigit()]
                    if not valid_ids:
                        continue

                    if key == "state":
                        filter_on += f" AND lgf.states_id IN ({','.join(valid_ids)})"
                    elif key == "type":
                        filter_on += f" AND lgf.computertypes_id IN ({','.join(valid_ids)})"
                    elif key == "entity":
                        filter_on += f" AND lgf.entities_id IN ({','.join(valid_ids)})"

            # 🔹 Requête principale
            sql = f"""
                SELECT
                    SQL_CALC_FOUND_ROWS
                    lgm.id,
                    lgm.name,
                    m.platform,
                    CONCAT('KB', uma.kb) AS kb
                FROM xmppmaster.up_machine_activated uma
                JOIN xmppmaster.machines m
                    ON uma.id_machine = m.id
                JOIN xmppmaster.local_glpi_machines lgm
                    ON CONCAT('UUID', lgm.id) = m.uuid_inventorymachine
                JOIN xmppmaster.local_glpi_filters lgf
                    ON lgf.id = lgm.id
                WHERE
                    uma.update_id = :updateid
                    AND lgm.is_deleted = 0
                    AND lgm.is_template = 0
                    AND lgm.entities_id = :entityid
                    {sfilter}
                    {filter_on}
                {slimit};
            """

            # 🔹 Exécution de la requête
            resultquery = session.execute(sql, params)

            # 🔹 Compte total (FOUND_ROWS)
            count = session.execute("SELECT FOUND_ROWS();").scalar() or 0
            result["total"] = count

            # 🔹 Extraction des résultats
            for row in resultquery:
                result["datas"]["id"].append(row.id)
                result["datas"]["name"].append(row.name)
                result["datas"]["platform"].append(row.platform)
                result["datas"]["kb"].append(row.kb)

            session.commit()
            session.flush()

        except Exception as e:
            session.rollback()
            logger = logging.getLogger()
            logger.error(f"[get_machines_needing_update] ERREUR: {e}", exc_info=True)

        return result


    @DatabaseHelper._sessionm
    def white_unlist_update(self, session, updateid, entityid):
        """
        Supprime un update de la white_list selon son updateid ou son KB.

        Args:
            session: SQLAlchemy session.
            updateid: UUID ou KB de l'update.
            entityid: ID de l'entité (filtrage ajouté)
        """
        try:
            delete_sql = """
                DELETE FROM xmppmaster.up_white_list
                WHERE (updateid = :updateid OR kb = :updateid)
                AND entityid = :entityid;
            """
            session.execute(delete_sql, {"updateid": updateid, "entityid": entityid})
            session.commit()
            session.flush()
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"[white_unlist_update] ERREUR: {e}", exc_info=True)
            return False
