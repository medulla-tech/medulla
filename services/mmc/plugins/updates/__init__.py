# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

# Au cas où on souhaite appeler des configs d'autres modules
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.updates.config import UpdatesConfig

# import pour la database
from pulse2.database.updates import UpdatesDatabase

from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
import logging

VERSION = "1.0.0"
APIVERSION = "1:0:0"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################


def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = UpdatesConfig("updates")

    if config.disable:
        logger.warning("Plugin updates: disabled by configuration.")
        return False

    if not UpdatesDatabase().activate(config):
        logger.warning(
            "Plugin updates: an error occurred during the database initialization"
        )
        return False
    return True


def tests():
    return UpdatesDatabase().tests()


def test_xmppmaster():
    return UpdatesDatabase().test_xmppmaster()


def get_grey_list(start, end, filter=""):
    return UpdatesDatabase().get_grey_list(start, end, filter)


def get_white_list(start, end, filter=""):
    return UpdatesDatabase().get_white_list(start, end, filter)


def get_black_list(start, end, filter=""):
    return UpdatesDatabase().get_black_list(start, end, filter)


def get_enabled_updates_list(start, end, filter=""):
    return UpdatesDatabase().get_enabled_updates_list(start, end, filter)


def get_family_list(start, end, filter=""):
    return UpdatesDatabase().get_family_list(start, end, filter)


def approve_update(updateid):
    return UpdatesDatabase().approve_update(updateid)


def grey_update(updateid, enabled=0):
    return UpdatesDatabase().grey_update(updateid, enabled)


def exclude_update(updateid):
    return UpdatesDatabase().exclude_update(updateid)


def get_count_machine_as_not_upd(updateid):
    return UpdatesDatabase().get_count_machine_as_not_upd(updateid)


def delete_rule(id):
    return UpdatesDatabase().delete_rule(id)


def white_unlist_update(updateid):
    return UpdatesDatabase().white_unlist_update(updateid)


def get_machine_with_update(kb):
    return Glpi().get_machine_with_update(kb)


def get_count_machine_with_update(kb):
    return Glpi().get_count_machine_with_update(kb)


def get_machines_needing_update(updateid):
    return UpdatesDatabase().get_machines_needing_update(updateid)


def get_conformity_update_by_machines(ids=[]):
    """ids is formated as :
    {
        "uuids": ["UUID4", "UUID3"], // glpi inventory uuids
        "ids": [4,3]
    }
    """
    merged = {}
    range = len(ids["uuids"])
    count = 0
    while count < range:
        merged[ids["uuids"][count]] = ids["ids"][count]
        count += 1

    installed = Glpi().get_count_installed_updates_by_machines(ids["uuids"])
    missing = XmppMasterDatabase().get_count_missing_updates_by_machines(ids["ids"])

    result = []
    for uuid in installed:
        _missing = missing[uuid]["missing"] if uuid in missing else 0
        result.append(
            {
                "uuid": uuid,
                "id": merged[uuid],
                "missing": _missing,
                "hostname": installed[uuid]["cn"],
                "installed": installed[uuid]["installed"],
                "total": installed[uuid]["installed"] + _missing,
                "compliance": 100
                - (100 * _missing / (installed[uuid]["installed"] + _missing)),
            }
        )

    return result
