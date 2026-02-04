# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

import traceback
import os

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, Table, select, func, text, inspect
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.ext.automap import automap_base


# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper

# Imported last
from typing import List, Dict, Any
import logging
import json
import re

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
        include_table = ['providers', 'magic_link']

        # Dynamically add attributes to the object for each mapped class
        for table_name, mapped_class in Base.classes.items():
            if table_name in exclude_table:
                continue
            if table_name.startswith("saas_"):
                logger.debug(f"Mapping table by automap: {table_name.capitalize()}")
                # Set the mapped class as an attribute of this instance
                setattr(self, table_name.capitalize(), mapped_class)
            if table_name.endswith("_conf"):
                logger.debug(f"Mapping config table by automap: {table_name.capitalize()}")
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
    def create_entity_under_custom_parent(self, session, entity_id, name, tag_value, stripe_tag=None):
        """
        Inserts a new entity into the saas_organisations table
        after creation in GLPI, using the UUID/tag generated on the Python side.

        Args:
            session (Session): open SQLAlchemy session
            entity_id (int|str): GLPI ID of the entity (created child)
            name (str): Entity name
            tag_value (str): UUID also used for GLPI
            stripe_tag (str|None): Value to store in saas_organisations.stripe_tag (NULL if absent)

        Returns:
            organisation_id: the id of the org created in the database
        """
        org = self.Saas_organisations(
            organisation_name=name,
            entity_id=str(entity_id),
            entity_name=name,
            tag_name=tag_value,
            stripe_tag=stripe_tag,
        )
        session.add(org)
        session.flush()
        org_id = org.organisation_id
        session.commit()
        return org_id

    @DatabaseHelper._sessionm
    def get_dl_tag(self, session, tag: str) -> str | None:
        t = (tag or "").strip()
        if not t:
            return None

        row = (
            session.query(self.Saas_organisations.dl_tag)
            .filter(self.Saas_organisations.tag_name == t)
            .first()
        )
        return row[0] if row else None

    @DatabaseHelper._sessionm
    def get_id_entity(self, session, stripe_tag):
        stripe_tag = (stripe_tag or "").strip()
        if not stripe_tag:
            return None

        row = (
            session.query(self.Saas_organisations.entity_id)
            .filter(self.Saas_organisations.stripe_tag == stripe_tag)
            .first()
        )
        return row[0] if row else None

    @DatabaseHelper._sessionm
    def update_entity(self, session, entity_id, new_name):
        """
        Updates the name of the entity in the Saas_organizations table.

        Args:
            session (session): open SQLAlchemy session
            entity_id (int | str): GLPI id of the entity to update
            new_name (str): new name

        Returns:
            Bool: True if updated, False otherwise
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
            entity_id: GLPI ID of the entity to be deleted
        """
        rows = (
            session.query(self.Saas_organisations)
            .filter_by(entity_id=str(entity_id))
            .delete(synchronize_session=False)
        )
        session.commit()
        return rows

    # ---- PROVIDER MANAGEMENT ----
    # READ
    @DatabaseHelper._sessionm
    def get_providers_all(self, session) -> List[Dict[str, Any]]:
        stmt = select(
            self.Providers.id,
            self.Providers.client_name,
            self.Providers.name,
            self.Providers.logo_url,
            self.Providers.url_provider,
            self.Providers.client_id,
            self.Providers.client_secret,
            self.Providers.lmc_acl,
            self.Providers.ldap_uid,
            self.Providers.ldap_givenName,
            self.Providers.ldap_sn,
            self.Providers.ldap_mail,
            self.Providers.profiles_order,
            self.Providers.acls_json,
            self.Providers.proxy_url,
        ).order_by(self.Providers.client_name, self.Providers.name)

        rows = session.execute(stmt).mappings().all()
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append({
                "id":             int(r["id"] or 0),
                "client_name":    r["client_name"]    or "",
                "name":           r["name"]           or "",
                "logo_url":       r["logo_url"]       or "",
                "url_provider":   r["url_provider"]   or "",
                "client_id":      r["client_id"]      or "",
                "client_secret":  r["client_secret"]  or "",
                "lmc_acl":        r["lmc_acl"]        or "",
                "ldap_uid":       r["ldap_uid"]       or "",
                "ldap_givenName": r["ldap_givenName"] or "",
                "ldap_sn":        r["ldap_sn"]        or "",
                "ldap_mail":      r["ldap_mail"]      or "",
                "profiles_order": r["profiles_order"] or "",
                "acls_json":      r["acls_json"]      or "",
                "proxy_url":      r["proxy_url"]      or "",
            })
        return out

    @DatabaseHelper._sessionm
    def get_providers_by_client(self, session, client_name: str) -> List[Dict[str, Any]]:
        client = (client_name or "MMC").strip()
        stmt = select(
            self.Providers.id,
            self.Providers.client_name,
            self.Providers.name,
            self.Providers.logo_url,
            self.Providers.url_provider,
            self.Providers.client_id,
            self.Providers.client_secret,
            self.Providers.lmc_acl,
            self.Providers.ldap_uid,
            self.Providers.ldap_givenName,
            self.Providers.ldap_sn,
            self.Providers.ldap_mail,
            self.Providers.profiles_order,
            self.Providers.acls_json,
            self.Providers.proxy_url,
        ).where(self.Providers.client_name == client
        ).order_by(self.Providers.name)

        rows = session.execute(stmt).mappings().all()
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append({
                "id":             int(r["id"] or 0),
                "client_name":    r["client_name"]    or "",
                "name":           r["name"]           or "",
                "logo_url":       r["logo_url"]       or "",
                "url_provider":   r["url_provider"]   or "",
                "client_id":      r["client_id"]      or "",
                "client_secret":  r["client_secret"]  or "",
                "lmc_acl":        r["lmc_acl"]        or "",
                "ldap_uid":       r["ldap_uid"]       or "",
                "ldap_givenName": r["ldap_givenName"] or "",
                "ldap_sn":        r["ldap_sn"]        or "",
                "ldap_mail":      r["ldap_mail"]      or "",
                "profiles_order": r["profiles_order"] or "",
                "acls_json":      r["acls_json"]      or "",
                "proxy_url":      r["proxy_url"]      or "",
            })
        return out

    # CREATE
    @DatabaseHelper._sessionm
    def create_provider(self, session, payload: dict) -> dict:
        norm = lambda s: (s or "").strip()

        client_name   = norm(payload.get("client_name"))
        name          = norm(payload.get("name"))
        url_provider  = norm(payload.get("url_provider"))
        client_id     = norm(payload.get("client_id"))
        client_secret = payload.get("client_secret")

        if not all([client_name, name, url_provider, client_id, client_secret]):
            return {"ok": False, "error": "Missing required fields (client_name, name, url_provider, client_id, client_secret)."}

        exists = session.execute(
            select(self.Providers.id).where(
                (self.Providers.client_name == client_name) &
                (self.Providers.name == name)
            ).limit(1)
        ).first()
        if exists:
            return {"ok": False, "error": f"Provider '{name}' already exists for client '{client_name}'."}

        # Flexible acls_json
        acls_json = payload.get("acls_json")
        if isinstance(acls_json, dict):
            acls_json = json.dumps(acls_json, ensure_ascii=False)
        elif isinstance(acls_json, str) and acls_json.strip():
            try:
                json.loads(acls_json)
            except Exception as e:
                return {"ok": False, "error": f"Invalid acls_json: {e}"}
        else:
            acls_json = None

        # We don't set lmc_acl here to let the default SQL value play if there is nothing
        data = {
            "client_name":   client_name,
            "name":          name,
            "logo_url":      norm(payload.get("logo_url")) or None,
            "url_provider":  url_provider,
            "client_id":     client_id,
            "client_secret": str(client_secret),
            "profiles_order": norm(payload.get("profiles_order")) or None,
            "acls_json":     acls_json,
        }

        v_acl = norm(payload.get("lmc_acl"))
        if v_acl != "":
            data["lmc_acl"] = v_acl

        # ldap_*: add only if provided (otherwise default SQL)
        for k in ("ldap_uid", "ldap_givenName", "ldap_sn", "ldap_mail", "proxy_url"):
            v = norm(payload.get(k))
            if v:
                data[k] = v

        row = self.Providers(**data)
        session.add(row)
        session.flush()
        new_id = int(row.id)
        session.commit()
        return {"ok": True, "id": new_id}

    # UPDATE
    @DatabaseHelper._sessionm
    def update_provider(self, session, payload: dict) -> dict:
        norm = lambda s: (s or "").strip()

        pid = int(payload.get("id") or 0)
        if pid <= 0:
            return {"ok": False, "error": "Missing or invalid id"}

        row = session.get(self.Providers, pid)
        if not row:
            return {"ok": False, "error": "Provider not found"}

        if "client_name" in payload:
            new_cn = norm(payload["client_name"])
            if new_cn:  # if provided and not empty, process it
                if len(new_cn) > 64 or not re.match(r'^[A-Za-z0-9._\- ]+$', new_cn):
                    return {"ok": False, "error": "Invalid client_name"}
                # uniqueness (client_name, name)
                conflict = session.execute(
                    select(self.Providers.id).where(
                        (self.Providers.client_name == new_cn) &
                        (self.Providers.name == row.name) &
                        (self.Providers.id != row.id)
                    ).limit(1)
                ).first()
                if conflict:
                    return {"ok": False, "error": "(client_name, name) already exists"}
                row.client_name = new_cn

        if "name" in payload:
            payload.pop("name", None)

        nullable = {"logo_url", "lmc_acl", "ldap_uid", "ldap_givenName",
                    "ldap_sn", "ldap_mail", "profiles_order", "proxy_url"}

        for key in list(nullable):
            if key in payload:
                v = norm(payload[key])
                setattr(row, key, None if v == "" else v)

        for key in ("url_provider", "client_id", "client_secret"):
            if key in payload:
                v = norm(payload[key])
                if v != "":
                    setattr(row, key, v)

        if "acls_json" in payload:
            aj = payload["acls_json"]
            if aj is None or (isinstance(aj, str) and aj.strip() == ""):
                row.acls_json = None
            elif isinstance(aj, dict):
                row.acls_json = json.dumps(aj, ensure_ascii=False)
            elif isinstance(aj, str):
                try:
                    json.loads(aj)
                except Exception as e:
                    return {"ok": False, "error": f"Invalid acls_json: {e}"}
                row.acls_json = aj
            else:
                return {"ok": False, "error": "Invalid acls_json type"}

        session.flush()
        session.commit()
        return {"ok": True, "id": pid}

    # DELETE
    @DatabaseHelper._sessionm
    def delete_provider(self, session, provider_id: int) -> Dict[str, object]:
        """
        Delete a provider by ID
        """
        pid = int(provider_id or 0)
        if pid <= 0:
            return {"ok": False, "deleted": 0, "id": 0, "error": "invalid id"}

        row = session.get(self.Providers, pid)
        if not row:
            return {"ok": False, "deleted": 0, "id": pid, "error": "not found"}

        try:
            session.delete(row)
            session.flush()
            session.commit()
            return {"ok": True, "deleted": 1, "id": pid, "error": ""}
        except SQLAlchemyError as e:
            session.rollback()
            return {"ok": False, "deleted": 0, "id": pid, "error": str(e)}

    @DatabaseHelper._sessionm
    def get_root_token(self, session):
        token = (session.query(self.Saas_application.setting_value)
            .filter(self.Saas_application.setting_name == 'glpi_root_user_token')
            .scalar())

        return token

    @DatabaseHelper._sessionm
    def validateToken(self, session, uid: str, token: str) -> bool:
        uid = (uid or "").strip()
        token = (token or "").strip()

        if not uid or not token:
            return False

        ML = getattr(self, "Magic_link", None)
        if ML is None:
            return False

        try:
            row = (
                session.query(ML)
                .with_for_update()
                .filter(ML.login == uid)
                .filter(ML.token == token)
                .filter(ML.used_at.is_(None))
                .filter(ML.expires_at > func.now())
                .first()
            )
            if not row:
                session.rollback()
                return False

            # Consume the link (single use)
            row.used_at = func.now()
            session.flush()
            session.commit()
            return True

        except SQLAlchemyError:
            session.rollback()
            return False

    ############### CONFIG #########################

    @DatabaseHelper._sessionm
    def get_config_tables (self, session) -> List[str]:
        """Get all *_conf tables in the admin databse"""
        try:
            inspector = inspect(self.db)
            tables = inspector.get_table_names()
            conf_tables = [t for t in tables if t.endswith("_conf")]
            return conf_tables
        except SQLAlchemyError as e:
            logger.error(f"[ConfigDB] Error reading config tables: {e}")
            return []

    @DatabaseHelper._sessionm
    def get_config_value(self, session, table_name: str, section: str, option: str):
        """Get a configuration value from a *_conf table."""
        try:
            cls_name = table_name.capitalize()
            Conf = getattr(self, cls_name)
            row = (
                session.query(Conf.valeur, Conf.valeur_defaut)
                .filter(
                    Conf.section == section,
                    Conf.nom == option,
                    Conf.activer == 1,
                )
                .first()
            )
            if row:
                return row[0] if row[0] is not None else row[1]
            return None
        except SQLAlchemyError as e:
            logger.error(f"[ConfigDB] Error reading: {e}")
            return None

    @DatabaseHelper._sessionm
    def has_config_section(self, session, table_name: str, section: str) -> bool:
        """Check if a section exists in a *_conf table."""
        try:
            cls_name = table_name.capitalize()
            Conf = getattr(self, cls_name)
            count = (
                session.query(func.count(Conf.id))
                .filter(
                    Conf.section == section,
                    Conf.activer == 1,
                )
                .scalar()
            )
            return count > 0
        except SQLAlchemyError as e:
            logger.error(f"[ConfigDB] Error checking section: {e}")
            return False

    @DatabaseHelper._sessionm
    def get_config_data(self, session, table_name: str):
        """Get all configuration data from a *_conf table."""
        try:
            cls_name = table_name.capitalize()
            Conf = getattr(self, cls_name)
            rows = (
                session.query(
                    Conf.section,
                    Conf.nom,
                    Conf.valeur,
                    Conf.valeur_defaut,
                    Conf.description,
                    Conf.activer,
                )
                .filter(Conf.activer == 1)
                .all()
            )
            # Convert SQLAlchemy Row objects to native Python dicts for XML-RPC serialization
            return [
                {
                    "section": row[0] or "",
                    "nom": row[1] or "",
                    "valeur": row[2],
                    "valeur_defaut": row[3],
                    "description": row[4] or "",
                    "activer": int(row[5] or 0),
                }
                for row in rows
            ]
        except SQLAlchemyError as e:
            logger.error(f"[ConfigDB] Error reading data: {e}")
            return []
        
    @DatabaseHelper._sessionm
    def update_config_data(self, session, table_name: str, data: dict) -> bool:
        """Update a configuration in a *_conf table."""
        try:
            cls_name = table_name.capitalize()
            Conf = getattr(self, cls_name)
            row = None
            section = (data.get("section") or "").strip()
            nom = (data.get("nom") or "").strip()
            if section and nom:
                row = (
                    session.query(Conf)
                    .filter(
                        Conf.section == section,
                        Conf.nom == nom,
                    )
                    .first()
                )
            else:
                logger.warning("[ConfigDB] update_config_data: missing keys table=%s data=%s", table_name, data)
            if not row:
                logger.warning("[ConfigDB] update_config_data: row not found for table=%s data=%s", table_name, data)
                return False

            if "valeur" in data:
                row.valeur = data["valeur"]
            if "valeur_defaut" in data:
                row.valeur_defaut = data["valeur_defaut"]
            if "description" in data:
                row.description = data["description"]
            if "activer" in data:
                row.activer = int(data["activer"])
            session.flush()
            session.commit()
            logger.info("[ConfigDB] update_config_data: updated table=%s id=%s", table_name, getattr(row, "id", None))
            return True
        except SQLAlchemyError as e:
            logger.error(f"[ConfigDB] Error updating data: {e}")
            return False