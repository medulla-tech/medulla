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
    config = MasteringConfig("mastering", None, "database")

    if config.disable:
        logger.warning("Plugin mastering: disabled by configuration.")
        return False

    if not MasteringDatabase().activate(config):
        logger.warning("Plugin mastering: an error occurred during the database initialization")
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
    
    sessionid = name_random(8, "diskmastering_")
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