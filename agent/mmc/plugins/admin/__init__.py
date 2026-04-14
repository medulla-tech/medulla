# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
from mmc.plugins.admin.config import AdminConfig
from pulse2.database.admin import AdminDatabase
from pulse2.version import getVersion, getRevision

VERSION = "5.5.1"
APIVERSION = "0:0:0"
REVISION = ""

def getApiVersion():
    return APIVERSION

def activate():
    logger = logging.getLogger()
    config = AdminConfig("admin")

    if config.disable:
        logger.warning("Plugin admin: disabled by configuration.")
        return False

    if not AdminDatabase().activate(config):
        logger.error(
            "Plugin admin: an error occurred during the database initialization"
        )
        return False
    return True


# --- Configuration management RPC wrappers (exposed to XML-RPC) ---
def get_config_tables():
    """Return a list of available *_conf tables (wrapper over AdminDatabase)."""
    try:
        db = AdminDatabase()
        return db.get_config_tables()
    except Exception as e:
        logging.getLogger().exception("get_config_tables failed: %s", e)
        return []


def get_config_data(table: str):
    try:
        db = AdminDatabase()
        return db.get_config_data(table)
    except Exception as e:
        logging.getLogger().exception("get_config_data failed: %s", e)
        return []


def add_config_data(table: str, data: dict) -> bool:
    try:
        logging.getLogger().info("add_config_data: table=%s data=%s", table, data)
        db = AdminDatabase()
        return db.add_config_data(table, data)
    except Exception as e:
        logging.getLogger().exception("add_config_data failed: %s", e)
        return False


def update_config_data(table: str, data: dict) -> bool:
    try:
        logging.getLogger().info("update_config_data: table=%s data=%s", table, data)
        db = AdminDatabase()
        return db.update_config_data(table, data)
    except Exception as e:
        logging.getLogger().exception("update_config_data failed: %s", e)
        return False


def delete_config_data(table: str, data: dict) -> bool:
    try:
        logging.getLogger().info("delete_config_data: table=%s data=%s", table, data)
        db = AdminDatabase()
        return db.delete_config_data(table, data)
    except Exception as e:
        logging.getLogger().exception("delete_config_data failed: %s", e)
        return False


def restore_config_version(table: str, table_version: str) -> bool:
    try:
        logging.getLogger().info("restore_config_version: table=%s version=%s", table, table_version)
        db = AdminDatabase()
        return db.restore_config_version(table, table_version)
    except Exception as e:
        logging.getLogger().exception("restore_config_version failed: %s", e)
        return False


def get_config_sections(table: str = None):
    """Return config sections for a given table. If table is None, try best-effort.
    """
    try:
        db = AdminDatabase()
        if table:
            return db.get_config_sections(table)
        # Best-effort: if AdminDatabase exposes a no-arg helper, call it; else return []
        try:
            return db.get_config_sections()
        except TypeError:
            return []
    except Exception as e:
        logging.getLogger().exception("get_config_sections failed: %s", e)
        return []
