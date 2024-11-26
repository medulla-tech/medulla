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
    datas = UpdatesDatabase().get_enabled_updates_list(
        entity, upd_list, start, end, filter, Glpi().config
    )
    count_glpi = Glpi().get_machines_list1(0, 0, {"location": entity})
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


def get_machine_with_update(kb, updateid, uuid, start=0, limit=-1, filter=""):
    result = XmppMasterDatabase().get_machine_with_update(
        kb, updateid, uuid, start, limit, filter, Glpi().config
    )
    return result


def get_count_machine_with_update(kb, uuid, list):
    return Glpi().get_count_machine_with_update(kb, uuid, list)


def get_machines_needing_update(updateid, entity, start=0, limit=-1, filter=""):
    return UpdatesDatabase().get_machines_needing_update(
        updateid, entity, Glpi().config, start, limit, filter
    )


def get_conformity_update_by_entity(entities=[], source="xmppmaster"):
    """Get the conformity for specified entities"""

    # init resultarray with default datas
    # init entitiesarray with entities ids, this will be used in the "in" sql clause
    resultarray = {}
    for entity in entities:
        eid = entity["uuid"].replace("UUID", "")
        resultarray[entity["uuid"]] = {
            "entity": eid,
            "nbmachines": 0,
            "nbupdate": 0,
            "totalmach": 0,
            "conformite": 0,
        }

    config = Glpi().config if source == "glpi" else None

    if source == "xmppmaster":
        result = XmppMasterDatabase().get_conformity_update_by_entity(
            entities=[entity["uuid"].replace("UUID", "") for entity in entities],
            config=config,
        )

        for counters in result:
            euid = f"UUID{counters['entity']}"
            if euid in resultarray:
                resultarray[euid]["totalmach"] = counters.get("totalmach", 0)
                resultarray[euid]["nbmachines"] = counters.get("nbmachines", 0)
                resultarray[euid]["nbupdate"] = counters.get("nbupdates", 0)

                if resultarray[euid]["totalmach"] > 0:
                    resultarray[euid]["conformite"] = int(
                        (1 - (resultarray[euid]["nbmachines"] / resultarray[euid]["totalmach"])) * 100
                    )
                else:
                    resultarray[euid]["conformite"] = 100

    elif source == "glpi":
        # Recover the machines from GLPI for each entity
        glpi_results = []
        for entity in entities:
            params = {
                "location": entity["uuid"],
                "filter": "",
                "field": "",
                "contains": "",
                "start": 0,
                "end": 20,
                "maxperpage": 20,
            }
            glpi_data = Glpi().get_machines_list1(0, 20, params)
            glpi_uuids = glpi_data["data"].get("uuid", [])
            glpi_results.append({
                "entity": entity["uuid"].replace("UUID", ""),
                "machines": [{"uuid": f"UUID{uuid}"} for uuid in glpi_uuids],
                "totalmach": len(glpi_uuids),
            })

        # Identify the machines common to GLPI and XMPPMaster
        all_glpi_machines = [machine["uuid"] for result in glpi_results for machine in result["machines"]]
        machines_in_both = XmppMasterDatabase().get_machine_in_both_sources(all_glpi_machines)

        result = []
        for glpi_result in glpi_results:
            entity_id = glpi_result["entity"]
            total_machines_glpi = glpi_result["totalmach"]
            glpi_machine_ids = [machine["uuid"] for machine in glpi_result["machines"]]

            machines_common = [uuid for uuid in glpi_machine_ids if machines_in_both.get(uuid, False)]

            conformity_data = XmppMasterDatabase().get_conformity_update_by_entity(
                entities=[entity_id],
                config=config,
            )

            if conformity_data:
                total_non_conform = conformity_data[0].get("nbmachines", 0)
            else:
                total_non_conform = 0

            total_updates = sum(item.get("nbupdates", 0) for item in conformity_data)

            result.append({
                "entity": entity_id,
                "totalmach": total_machines_glpi,
                "nbmachines": total_non_conform,
                "nbupdates": total_updates,
                "common_machines_count": len(machines_common),
            })

        for counters in result:
            euid = f"UUID{counters['entity']}"
            if euid in resultarray:
                resultarray[euid]["totalmach"] = counters.get("totalmach", 0)
                resultarray[euid]["nbmachines"] = counters.get("nbmachines", 0)
                resultarray[euid]["nbupdate"] = counters.get("nbupdates", 0)

                # Calculation based solely on common machines
                common_count = counters.get("common_machines_count", 0)
                if common_count > 0:
                    resultarray[euid]["conformite"] = int(
                        (1 - (resultarray[euid]["nbmachines"] / common_count)) * 100
                    )
                else:
                    resultarray[euid]["conformite"] = 100

    else:
        raise ValueError(f"Source inconnue : {source}")

    return resultarray

def get_machines_xmppmaster(start, end, filter=""):
    return XmppMasterDatabase().get_machines_xmppmaster(start, end, filter)

def get_machine_in_both_sources(glpi_ids):
    return XmppMasterDatabase().get_machine_in_both_sources(glpi_ids)

def get_conformity_update_by_machines(ids=[]):
    """ids is formated as :
    {
        "uuids": ["UUID4", "UUID3"], // glpi inventory uuids
        "ids": [4,3]
    }
    """

    result = {}
    for uuid in ids["uuids"]:
        result[uuid] = {
            "uuid": "",
            "id": "",
            "missing": 0,
            "inprogress": 0,  # Ajout du champ inprogress
            "hostname": "",
            "installed": 0,
            "total": 0,
            "compliance": 100.0,
        }
    range = len(ids["uuids"])
    count = 0
    while count < range:
        result[ids["uuids"][count]]["id"] = ids["ids"][count]
        count += 1


    if ids["uuids"] == "" or ids["uuids"] == []:
        installed = {}
    else:
        installed = Glpi().get_count_installed_updates_by_machines(ids["uuids"])

    if ids["ids"] == "" or ids["ids"] == []:
        missing = {}
    else:
        missing = XmppMasterDatabase().get_count_missing_updates_by_machines(ids["ids"])


    for uuid in installed:
        result[uuid]["installed"] = installed[uuid]["installed"]

    for uuid in missing:
        result[uuid]["missing"] = missing[uuid]["missing"]
        result[uuid]["inprogress"] = missing[uuid]["inprogress"]

    for uuid in result:
        result[uuid]["total"] = result[uuid]["installed"] + result[uuid]["missing"] + result[uuid]["inprogress"]
        result[uuid]["compliance"] = (
            (result[uuid]["installed"] / result[uuid]["total"]) * 100
            if result[uuid]["total"] > 0
            else 100
        )

    return result
