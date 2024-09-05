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


def get_enabled_updates_list(entity, upd_list="gray", start=0, end=-1, filter=""):
    if upd_list not in ["gray", "white"]:
        upd_list = "gray"
    # The glpi config is sent to updatedatabase to get the filter_on param
    datas = UpdatesDatabase().get_enabled_updates_list(entity, upd_list, start, end, filter, Glpi().config)
    count_glpi = Glpi().get_machines_list1(0, 0, {"location":entity})
    datas["total"] = count_glpi["count"]
    return datas

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


def get_machine_with_update(kb, updateid):
    glpi = Glpi().get_machine_with_update(kb)
    history = []
    if updateid != "":
        history = XmppMasterDatabase().get_history_by_update(updateid)

    for machine in glpi:
        if machine != []:
            uuid = "UUID%s" % machine[0]
            if uuid in history:
                del history[uuid]

    for uuid in history:
        glpi.append(history[uuid]["id"])
        glpi.append(history[uuid]["hostname"])
        glpi.append(history[uuid]["entity"])
        glpi.append(history[uuid]["kb"])
        glpi.append(history[uuid]["numkb"])
    return glpi


def get_count_machine_with_update(kb, uuid, list):
    return Glpi().get_count_machine_with_update(kb, uuid, list)


def get_machines_needing_update(updateid, entity, start=0, limit=-1, filter=""):
    return UpdatesDatabase().get_machines_needing_update(updateid, entity, Glpi().config, start, limit, filter)


def get_conformity_update_by_entity(entities=[]):
    """Get the conformity for specified entities"""

    # init resultarray with default datas
    # init entitiesarray with entities ids, this will be used in the "in" sql clause
    resultarray = {}
    entitieslist = []
    for entity in entities:
        eid=entity["uuid"].replace("UUID", "")
        entitieslist.append(eid)
        total = Glpi().get_machines_list1(0, 0, {"location":entity["uuid"]})

        rtmp = {
            "entity": eid,
            "nbmachines": 0,
            "nbupdate": 0,
            "totalmach": total['count'],
            "conformite": 100,
        }
        resultarray[entity["uuid"]] = rtmp
    result = XmppMasterDatabase().get_conformity_update_by_entity(entitieslist, Glpi().config)

    for counters in result:
        euid = "UUID%s"%counters['entity']
        resultarray[euid]["nbmachines"] = counters["nbmachines"] #count machines with missing updates
        resultarray[euid]["nbupdate"] = counters["nbupdates"] # count updates for this entity
        if resultarray[euid]["totalmach"] > 0 and int(counters["nbmachines"]) > 0:
            resultarray[euid]["conformite"] = int(((resultarray[euid]["totalmach"] - counters["nbmachines"]) / resultarray[euid]["totalmach"]) * 100)
    return resultarray


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

    history = XmppMasterDatabase().get_update_history_by_machines(ids["ids"])
    if ids["uuids"] == "" or ids["uuids"] == []:
        installed = {}
    else:
        installed = Glpi().get_count_installed_updates_by_machines(ids["uuids"])

    if ids["ids"] == "" or ids["ids"] == []:
        missing = {}
    else:
        missing = XmppMasterDatabase().get_count_missing_updates_by_machines(ids["ids"])

    result = {}
    for uuid in installed:
        _missing = missing[uuid]["missing"] if uuid in missing else 0
        count_historic = 0
        try:
            count_historic = len(history[uuid])
        except:
            pass
        count_installed = installed[uuid]["installed"] + count_historic
        count_total = count_installed + _missing
        try:
            # in python3 the result of a division (even of int values) is float
            compliance = (count_installed / float(count_total)) * 100
        except:
            compliance = 100
        result[uuid] = {
            "uuid": uuid,
            "id": merged[uuid],
            "missing": _missing,
            "hostname": installed[uuid]["cn"],
            "installed": count_installed,
            "total": count_total,
            "compliance": compliance,
        }

    return result
