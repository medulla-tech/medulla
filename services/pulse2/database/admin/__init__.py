# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

import traceback

# SqlAlchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.automap import automap_base


# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper

# Imported last
import logging

logger = logging.getLogger()

class AdminDatabase(DatabaseHelper):
    """
    A class to handle database operations specific to the admin module.
    This class extends DatabaseHelper to provide additional functionality
    for managing admin-specific database tasks.
    """

    is_activated = False
    session = None

    def db_check(self):
        """
        Perform a database check specific to the admin module.
        Sets the module name and configuration file name before performing the check.

        Returns:
            bool: The result of the database check.
        """
        self.my_name = "admin"
        self.configfile = "admin.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        """
        Activate the database connection and prepare the metadata and mappers.

        Args:
            config: Configuration object containing database settings.

        Returns:
            bool: True if activation is successful, False otherwise.
        """
        if self.is_activated:
            return None

        self.config = config

        try:
            # Create a database engine using the provided configuration
            self.db = create_engine(
                self.makeConnectionPath(),
                pool_recycle=self.config.dbpoolrecycle,
                pool_size=self.config.dbpoolsize,
            )
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            return False

        if not self.db_check():
            logger.error("Database check failed.")
            return False

        try:
            # Prepare metadata and automap base for SQLAlchemy
            self.metadata = MetaData(self.db)
            Base = automap_base()
            Base.prepare(self.db, reflect=True)
        except Exception as e:
            logger.error(f"Failed to prepare automap base: {e}")
            return False

        # Lists to exclude or include specific tables for mapping
        exclude_table = []
        include_table = []

        # Dynamically add attributes to the object for each mapped class
        for table_name, mapped_class in Base.classes.items():
            if table_name in exclude_table:
                continue
            if table_name.startswith("saas_"):
                logger.debug(f"Mapping table by automap: {table_name.capitalize()}")
                # Set the mapped class as an attribute of this instance
                setattr(self, table_name.capitalize(), mapped_class)
            if table_name in include_table:
                logger.debug(f"Mapping table by automap by list include: {table_name.capitalize()}")
                setattr(self, table_name.capitalize(), mapped_class)

        if not self.initMappersCatchException():
            self.session = None
            return False

        # Create all tables defined in metadata
        self.metadata.create_all()
        self.is_activated = True

        # Execute a sample query to check the database connection
        result = self.db.execute("SELECT * FROM admin.version LIMIT 1;")
        re = [element.Number for element in result]
        return True

    def initMappers(self):
        """
        Initialize mappers. This method can be overridden to provide specific mapper initialization.
        """
        return

    def getDbConnection(self):
        """
        Attempt to establish a database connection with retries.

        Returns:
            Connection: A database connection object.

        Raises:
            Exception: If unable to establish a connection after retries.
        """
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
            raise Exception("Database admin connection error")
        return ret

    def _return_dict_from_dataset_mysql(self, resultproxy):
        """
        Convert a SQLAlchemy result proxy to a list of dictionaries.

        Args:
            resultproxy: The result proxy object from SQLAlchemy.

        Returns:
            list: A list of dictionaries representing the rows.
        """
        return [rowproxy._asdict() for rowproxy in resultproxy]

    @DatabaseHelper._sessionm
    def get_CONNECT_API(self, session):
        """
        Retrieve API connection settings from the database.

        Args:
            session: The database session to use for the query.

        Returns:
            dict: A dictionary containing the API connection settings.
        """
        config_api = {}
        try:
            # Query the Saas_application table to get API settings
            api_admin = session.query(self.Saas_application).all()

            # Construct the configuration dictionary
            for param_connect in api_admin:
                config_api[param_connect.setting_name] = param_connect.setting_value.strip()
            return config_api
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            logger.error("\n%s", traceback.format_exc())
            return config_api

    @DatabaseHelper._sessionm
    def create_entity_under_custom_parent(self, session, entity_id, name, tag_value):
        """
        Insère une nouvelle entité dans la table saas_organisations
        après création dans GLPI, en utilisant l'UUID/tag généré côté Python.

        Args:
            session (Session): session SQLAlchemy ouverte
            entity_id (int|str): ID GLPI de l'entité (enfant créée)
            name (str): Nom de l'entité
            tag_value (str): UUID utilisé aussi pour GLPI

        Returns:
            organisation_id: l'id de l'org créée dans la base
        """
        org = self.Saas_organisations(
            organisation_name=name,
            entity_id=str(entity_id),
            entity_name=name,
            tag_name=tag_value,
        )
        session.add(org)
        session.flush()
        org_id = org.organisation_id
        session.commit()
        return org_id

    @DatabaseHelper._sessionm
    def update_entity(self, session, entity_id, new_name):
        """
        Updates the name of the entity in the Saas_organizations table.

        Args:
            session (session):SessionSqlAlchemyOuverte
            entity_id (int | str): id glpi of the entity to update
            new_name (STR): new name

        Returns:
            Bool: True Si Maj, False otherwise
        """
        org = session.query(self.Saas_organisations).filter_by(entity_id=str(entity_id)).first()
        if not org:
            return False

        org.organisation_name = new_name
        org.entity_name = new_name
        session.commit()
        return True

    @DatabaseHelper._sessionm
    def delete_entity(self, session, entity_id):
        """
        Deletes the entity

        Args:
            entity_id: ID GLPI of the entity to be deleted
        """
        rows = (
            session.query(self.Saas_organisations)
            .filter_by(entity_id=str(entity_id))
            .delete(synchronize_session=False)
        )
        session.commit()
        return rows
    # =====================================================================
    # admin FUNCTIONS
    # =====================================================================
    # =====================================================================
    # API REST GLPI
    # =====================================================================
