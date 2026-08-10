# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

# File : mmc/plugins/mastering/__init__.py

from pulse2.version import getVersion, getRevision # pyflakes.ignore
# Au cas où on souhaite appeler des configs d'autres modules
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.mastering.config import MasteringConfig

from mmc.support.mmctools import (
    RpcProxyI,
    ContextMakerI,
    SecurityContext,
    EnhancedSecurityContext
)

from mmc.plugins.base import (
    with_xmpp_context,
    with_optional_xmpp_context
)

from mmc.plugins.xmppmaster.master.agentmaster import (
    XmppSimpleCommand,
    getXmppConfiguration,
    callXmppFunction,
    ObjectXmpp,
    callXmppPlugin,
    callInventory,
    callrestartbymaster,
    callrestartbotbymaster,
    callshutdownbymaster,
    send_message_json,
    callvncchangepermsbymaster,
    callInstallKey,
    callremotefile,
    calllocalfile,
    callremotecommandshell,
    calllistremotefileedit,
    callremotefileeditaction,
    callremoteXmppMonitoring,
)

from mmc.plugins.xmppmaster.master.lib.utils import name_random

# import pour la database
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.dyngroup.database import DyngroupDatabase
from pulse2.database.mastering import MasteringDatabase

import logging
import json

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
    config = MasteringConfig("mastering")

    if config.disable:
        logger.warning("Plugin mastering: disabled by configuration.")
        return False

    if not MasteringDatabase().activate(config):
        logger.error("Plugin mastering: an error occurred during the database initialization")
        return False
    return True


class ContextMaker(ContextMakerI):
    """
    Fabrique de contextes personnalisés pour XMPP, héritée de ContextMakerI.
    Sert à créer et initialiser un objet de type `EnhancedSecurityContext`.

    appeler sur chaque module a l'initialiasation'

    Méthodes
    --------
    getContext() :
        Crée et retourne un contexte sécurisé enrichi contenant les informations
        de l'utilisateur et de la requête courante.
    """

    def getContext(self):
        """
        Crée un contexte de type `EnhancedSecurityContext` pour l'utilisateur courant.

        Retourne
        --------
        EnhancedSecurityContext
            Contexte initialisé avec :
              - `userid` : l'identifiant de l'utilisateur courant
              - `request` : la requête associée
              - `session` : la session courante

        Effets de bord
        --------------
        - Écrit des logs de niveau `error` lors de la création du contexte.
        """
        s = EnhancedSecurityContext()
        s.userid = self.userid
        s.request = self.request
        s.session = self.session
        return s



class RpcProxy(RpcProxyI):
    # If we need user context
    pass

def get_machines_list_for_mastering(start=0, limit=-1, entity="", filter=""):
    result = Glpi().get_machines_list_for_mastering(start, limit, entity, filter)
    return result

def get_server_from_parent_entities(entities=[]):
    """
    Get the server associated to the entity. Here we assumes the entity the shape UUID11 AND IS the root entity

    Args:
        entities (list) : The parent entities uuid order by most close to farther parent.

    Return:
        str : the server jid associated with the entity
    """

    if entities == []:
        return ""

    result = MasteringDatabase().get_server_from_parent_entities(entities)
    return result

def get_server_disk(jid):
    config = MasteringConfig("mastering")

    command = f"df -h {config.master_path}"
    result = {}

    ret = callremotecommandshell(jid, command)
    ret = json.loads(ret)

    if ret["code"] != 0:
        return result

    # the result has the shape :
    # {
    #     "code": 0,
    #     "result": [
    #         "Filesystem               1K-blocks     Used Available Use% Mounted on\n",
    #         "/dev/mapper/ 513452376 48009912 439287048  10% /\n"
    #     ],
    #     "separateurline": "\n",
    #     "cmd": "df /var/lib/pulse2/imaging/masters",
    #     "timeout": 20
    # }
    # So we want to extract elements from the second line: ret["result"][1]
    # Then we split it on " ". The list is now ["/dev/mapper/", "513452376", "48009912", "439287048", " ","10%", "/\n"]
    # So what we want are element 1 to 4 from this list, the occupied size and the
    total, used, available, percent = [e for e in ret["result"][1].split(" ") if e != ""][1:5]
    result["total"] = total
    result["used"] = used
    result["available"] = available
    result["percent"] = percent

    return result


def get_masters_for_entity(entity, start=0, limit=-1, filter=""):
    result = MasteringDatabase().get_masters_for_entity(entity, start, limit, filter)
    return result

def create_action(action, gid, uuid, target, server, begin_date, end_date, config, workflow="", entity_id=-1):

    try:
        workflow = json.loads(workflow)
    except Exception as e:
        return {"status":1, "msg":"invalid incoming datas: %s"%e}
    server = server.replace(r"\/", "/")
    result = MasteringDatabase().create_action(action, gid, uuid, target, server, begin_date, end_date, config, workflow, entity_id)
    return result


def get_actions_for_entity(entity, start=0, limit=-1, _filter=""):

    if isinstance(entity, str):
        if entity.startswith("UUID"):
            entity = entity.replace("UUID", "")
        entity = int(entity)

    actions_list = MasteringDatabase().get_actions_for_entity(entity, start, limit, _filter)

    return actions_list

def get_actions_for_machine(uuid, start=0, maxperpage=-1, _filter=""):
    actions_list = MasteringDatabase().get_actions_for_machine(uuid, start, maxperpage, _filter)
    return actions_list

def get_action_results(_id, uuid, entity, start=0, end=-1, _filter=""):

    # normalize the entity id
    if isinstance(entity, str):
        if entity.startswith("UUID"):
            entity = entity.replace("UUID", "")
        entity = int(entity)

    result = MasteringDatabase().get_action_results(_id, uuid, entity, start, end, _filter)
    return result

def get_machines_action_results(_id, start=0, end=-1, _filter=""):
    result = MasteringDatabase().get_machines_action_results(_id, start, end, _filter)
    return result


def delete_master(server, entity, masterId):
    if is_master_used(masterId):
        return {"status": 1, "msg": "Master is currently used in an action and cannot be deleted."}
    result = MasteringDatabase().delete_master(server, entity, masterId)
    return result

def edit_master_infos(uuid, name, description=""):
    result = MasteringDatabase().edit_master_infos(uuid, name, description)
    return result

def delete_action(_id):
    return MasteringDatabase().delete_action(_id)

def delete_script(_id):
    if is_script_used(_id):
        return {"status": 1, "msg": "Script is currently used in an action and cannot be deleted."}
    else:
        return MasteringDatabase().delete_script(_id)

def is_script_used(_id:int)->bool:
    """Check if a mastering script is used in any action. If it is used, it cannot be deleted."""
    result = MasteringDatabase().is_script_used(_id)
    return result

def is_master_used(_id):
    """Check if a mastering script is used in any action. If it is used, it cannot be deleted."""
    result = MasteringDatabase().is_master_used(_id)
    return result

def get_action_status(_id):
    # TODO
    pass

def get_mastering_scripts_list(server, entity, start=0, end=-1, _filter=""):
    """
    Get the scripts (the postinstall script in the former imaging plugin) associated to the entity.

    Args:
        server (str): the server jid associated to the entity
        entity (str or int): the entity id, can be a string starting with "UUID" or an integer
        start (int): the index of the first mastering script to retrieve (for pagination)
        end (int): the index of the last mastering script to retrieve (for pagination)
        _filter (str): a filter string to apply to the mastering scripts (e.g., to search for specific scripts)

    Returns:
        list: a list of mastering scripts associated to the entity, each script is represented as a dictionary with its details (e.g., id, name, content, etc.)
    """

    # Normalize the entity id:
    if isinstance(entity, str):
        if entity.startswith("UUID"):
            entity = entity.replace("UUID", "")
        entity = int(entity)

    scripts_list = MasteringDatabase().get_mastering_scripts_list(server, entity, start, end, _filter)
    for script in scripts_list["data"]:
        try:
            script["used"] = is_script_used(script["id"])
        except:
            script["used"] = False
    return scripts_list

def get_script_from_payload(payload={}):
    """
    Get the script content from the payload. The payload is a dictionary that may contain the script content.

    Args:
        payload (dict): a dictionary containing the script content, typically with a key "content" that holds the script as a string

    Returns:
        str: the script content extracted from the payload, or an empty string if not found
    """
    if isinstance(payload, dict) and "type" in payload:
        _type = payload["type"]
        if "get_%s_script_from_payload"%_type in globals():
            fnc = globals()["get_%s_script_from_payload"%_type]

            return fnc(payload)
    return ""

def get_bash_script_from_payload(payload={}):
    """
    Get the bash script content from the payload. The payload is a dictionary that may contain the bash script content.

    Args:
        payload (dict): a dictionary containing the bash script content, typically with a key "bash_script" that holds the script as a string

    Returns:
        str: the bash script content extracted from the payload, or an empty string if not found
    """
    if isinstance(payload, dict) and "bash_script" in payload:
        return payload["bash_script"]
    return ""

def get_sysprep_script_from_payload(payload={}):
    """
    Get the sysprep script content from the payload. The payload is a dictionary that may contain the sysprep script content.

    Args:
        payload (dict): a dictionary containing the sysprep script content, typically with a key "sysprep_script" that holds the script as a string

    Returns:
        str: the sysprep script content extracted from the payload, or an empty string if not found
    """
    if isinstance(payload, dict) and "sysprep_script" in payload:
        return payload["sysprep_script"]
    return ""


def add_mastering_script(server, entity, name, description, content, _type="bash", payload={}):
    # Normalize entity
    if isinstance(entity, str):
        if entity.startswith("UUID"):
            entity = entity.replace("UUID", "")
        entity = int(entity)

    return MasteringDatabase().add_mastering_script(server, entity, name, description, content, _type, payload)


def edit_mastering_script(server, entity, _id, name, description, content, _type="bash", payload={}):
    # Normalize entity
    if isinstance(entity, str):
        if entity.startswith("UUID"):
            entity = entity.replace("UUID", "")
        entity = int(entity)

    return MasteringDatabase().edit_mastering_script(server, entity, _id, name, description, content, _type, payload)


def get_summary_scripts_list(entity):
    # Normalize entity
    if isinstance(entity, str):
        if entity.startswith("UUID"):
            entity = entity.replace("UUID", "")
        entity = int(entity)

    return MasteringDatabase().get_summary_scripts_list(entity)

def get_mastering_script(entity, _id):
    # Normalize entity
    if isinstance(entity, str):
        if entity.startswith("UUID"):
            entity = entity.replace("UUID", "")
        entity = int(entity)

    try:
        _id = int(_id)
    except:
        _id=0

    return MasteringDatabase().get_mastering_script(entity, _id)
