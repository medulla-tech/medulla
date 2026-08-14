# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2022-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import base64
import json
import uuid
import configparser

from pulse2.version import getVersion, getRevision  # pyflakes.ignore
from pulse2.database.urbackup import UrbackupDatabase
from pulse2.database.urbackup import UrbackupSettingsDb
from pulse2.database.urbackup import UrbackupDb

from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.urbackup.config import UrbackupConfig
from mmc.plugins.xmppmaster.master.agentmaster import callremotecommandshell
from mmc.plugins.xmppmaster.master.agentmaster import send_message_json
from mmc.plugins.xmppmaster.master.lib.utils import name_random
from mmc.plugins.urbackup.urwrapper import UrApiWrapper

from mmc.support.mmctools import (
    xmlrpcCleanup,
    RpcProxyI,
    ContextMakerI,
    SecurityContext,
    EnhancedSecurityContext
)
from mmc.plugins.base import (with_xmpp_context,
                              with_optional_xmpp_context,
                              Contexte_XmlRpc_surcharge_info_Glpi)

VERSION = "1.0.0"
APIVERSION = "1:0:0"

logger = logging.getLogger()

# PLUGIN GENERAL FUNCTIONS


def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = UrbackupConfig("urbackup")

    if config.disable:
        logger.warning("Plugin urbackup: disabled by configuration.")
        return False

    if not UrbackupDatabase().activate(config):
        logger.error(
            "Plugin urbackup: an error occurred during the database initialization"
        )
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

def tests():
    return UrbackupDatabase().tests()


def login():
    """
    Create a connection with urbackup.

    Returns:
       It returns a session value
       If it failed to connect it returns False.
    """
    api = UrApiWrapper()
    logged = api.login()
    # logged = api.response(logged)

    if "content" in logged and "session" in logged["content"]:
        return logged["content"]["session"]

    return False


class RpcProxy(RpcProxyI):
    # groups
    @with_optional_xmpp_context
    def getAllLogs(self, ctx=None):
        """
        Get all logs from urbackup database

        Args:
            None

        Returns:
            Dict Logs in database
        """
        return UrbackupDatabase().getAllLogs()

def enable_client(jidmachine, clientid, authkey):
    """
    Write backup_enabled to 1 on updatebackupclient.ini file to enable backup for windows client

    Args:
        JID Machine, client id and authkey of client

    Returns:
        1 or 0, state of function execution
    """
    conf_file = "/var/lib/pulse2/clients/config/updatebackupclient.ini"

    urbackup_conf = configparser.ConfigParser()
    urbackup_conf.read(conf_file)

    urbackup_server = urbackup_conf.get("parameters", "backup_server")
    urbackup_port = urbackup_conf.get("parameters", "backup_port")

    enable_client_database(clientid)

    command = (
        "(echo [parameters] & echo backup_enabled = 1 & echo client_id = "
        + str(clientid)
        + " & echo authkey = "
        + str(authkey)
        + " & echo backup_server = "
        + "urbackup://"
        + str(urbackup_server)
        + " & echo backup_port = "
        + str(urbackup_port)
        + ") > C:\\progra~1\\Medulla\\etc\\updatebackupclient.ini"
    )

    callremotecommandshell(jidmachine, command)
    sessionid = name_random(8, "update_")
    msg = {
        "action": "restartbot",
        "sessionid": sessionid,
        "data": {},
        "ret": 0,
        "base64": False,
    }
    send_message_json(jidmachine, msg)


def remove_client(jidmachine, clientid):
    """
    Write backup_enabled to 0 on updatebackupclient.ini file to disable backup for windows client

    Args:
        JID Machine and client id

    Returns:
        1 or 0, state of function execution
    """
    disable_client_database(clientid)

    command = "(echo [parameters] & echo backup_enabled = 0) > C:\\progra~1\\Medulla\\etc\\updatebackupclient.ini"

    callremotecommandshell(jidmachine, command)
    sessionid = name_random(8, "update_")
    msg = {
        "action": "restartbot",
        "sessionid": sessionid,
        "data": {},
        "ret": 0,
        "base64": False,
    }
    send_message_json(jidmachine, msg)


def restart_urbackup_service(jidmachine):
    """
    Restart Urbackup service on client

    Args:
        JID Machine

    Returns:
        1 or 0, state of function execution
    """

    command = 'powershell.exe -command "Restart-Service -Name UrBackupClientBackend"'

    callremotecommandshell(jidmachine, command)
    sessionid = name_random(8, "update_")
    msg = {
        "action": "restartbot",
        "sessionid": sessionid,
        "data": {},
        "ret": 0,
        "base64": False,
    }
    send_message_json(jidmachine, msg)


def get_client_status(client_id):
    """
    Get client status if enable or not from the database

    Args:
        Client id

    Returns:
        1 or 0, backup_enabled value
    """
    return UrbackupDatabase().getClientStatus(client_id)




def insertNewClient(client_id, machine_jid, authkey):
    """
    Insert new client in database

    Args:
        client id and auth key of client

    Returns:
        True or False
    """
    return UrbackupDatabase().insertNewClient(client_id, machine_jid, authkey)


def enable_client_database(client_id):
    """
    Get client status if enable or not from the database

    Args:
        Client id

    Returns:
        1 or 0, backup_enabled value
    """
    return UrbackupDatabase().editClientState("1", client_id)


def disable_client_database(client_id):
    """
    Get client status if enable or not from the database

    Args:
        Client id

    Returns:
        1 or 0, backup_enabled value
    """
    return UrbackupDatabase().editClientState("0", client_id)


def getComputersEnableValue(jid):
    """
    Get enable status from xmppmaster.machines table

    Args:
        JID Machine

    Returns:
        id, jid and enabled from database xmppmaster.machines
    """
    return UrbackupDatabase().getComputersEnableValue(jid)


def get_ses():
    """
    Get value of session

    Returns:
        Session key
    """
    api = UrApiWrapper()
    session = api.get_session()

    if session == "":
        return "No DATA in session"

    return session


def get_logs_for_entity(entity, start=0, limit=-1, filter=""):
    """
    Get the logs of the server

    Returns:
        It returns the server logs.
        If no logs are available, it returns the "No DATA" string.
    """
    entity = _entity
    if isinstance(entity, str):
        _entity = entity.replace("UUID", "")

    try:
        _entity = int(_entity)
    except:
        pass

    client_ids = UrbackupDatabase().get_client_ids_from_entity(_entity)

    # Update all logs for found clients
    api = UrApiWrapper()
    for client_id in client_ids:
        _logs = api.get_logs(client_id)
        logs = _logs["content"] if "content" in _logs else []

        if "logdata" in logs:
            UrbackupDatabase().update_logs(client_id, logs["logdata"])


    result = UrbackupDatabase().get_logs_for_entity(_entity, start, limit, filter)
    return result


def add_client(client_name):
    """
    Create client with new id and authkey

    Args:
        Client id

    Returns:
        Server,
        Port,
        Authkey,
        Client ID,
        Client Name
    """
    api = UrApiWrapper()
    newclient = api.add_client(client_name)
    # newclient = api.response(newclient)
    if "content" in newclient:
        return newclient["content"]

    return "No DATA in newclient"


def get_stats():
    """
    Return all stats by client, size of file, size of image and clientname

    Returns:
        Image size,
        File size
    """
    api = UrApiWrapper()
    stats = api.get_stats()
    # stats = api.response(stats)
    if "content" in stats:
        return stats["content"]

    return "No DATA in stats"


def add_group(groupname):
    """
    Create groupe

    Args:
        New groupe name

    Returns:
        All Settings of server
    """
    api = UrApiWrapper()
    newgroup = api.add_group(groupname)
    # newgroup = api.response(newgroup)
    if "content" in newgroup and newgroup["content"].get("add_ok"):
        content = newgroup["content"]
        return {
            "add_ok": content["add_ok"],
            "groupname": content.get("added_group", {}).get("name", "")
        }
    return {"add_ok": False, "groupname": ""}


def remove_group(groupid):
    """
    Remove groupe

    Args:
        Group id

    Returns:
        All Settings of server
    """
    api = UrApiWrapper()
    removegroup = api.remove_group(groupid)
    # removegroup = api.response(removegroup)
    if "content" in removegroup:
        return removegroup["content"]

    return "No DATA in newclient"


def get_settings_general():
    """
    Get multiples settings value of server

    Returns:
        Array of every settings value of server
    """
    api = UrApiWrapper()
    settings = api.get_settings_general()
    # settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA in global settings"


def save_settings(clientid, name_data, value_data):
    """
    Save settings for client of group

    Args:
        Client id, settings name to change and new value for this settings

    Returns:
        Settings saved for group
    """
    api = UrApiWrapper()
    settings = api.save_settings(clientid, name_data, value_data)
    # settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA settings saved"


def get_settings_clientsettings(id_client):
    """
    Get multiples settings for one client

    Args:
        Client id

    Returns:
        Array of client settings
    """
    api = UrApiWrapper()
    settings = api.get_settings_clientsettings(id_client)
    # settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA client settings"


def get_settings_clients():
    """
    Get clients groups and user on urbackup

    Returns:
        Array of every client informations
    """
    api = UrApiWrapper()
    list_clients = api.get_settings_clients()
    # list_clients = api.response(list_clients)

    if "content" in list_clients:
        return list_clients["content"]

    return "No DATA listusers"


def get_auth_client(clientid):
    """
    Get auth key for one client

    Returns:
        Array of internet_authkey informations
    """
    api = UrApiWrapper()
    setting_client = api.get_settings_client(clientid)
    # setting_client = api.response(setting_client)
    if "content" in setting_client:
        return setting_client["content"]["settings"]["internet_authkey"]

    return "No DATA listusers"


def get_backups_all_client():
    """
    Get every backups for each client

    Returns:
        Array of every backup for each client
    """
    api = UrApiWrapper()
    backups = api.get_backups("0")
    # backups = api.response(backups)
    if "content" in backups:
        return backups["content"]

    return "No DATA backups"


def get_backup_files(client_id, backup_id, path):
    """
    Get every files on backup

    Args:
        Client id, backup id and path of file

    Returns:
        Array of info from backup
    """
    api = UrApiWrapper()
    files = api.get_backup_files(client_id, backup_id, path)
    # files = api.response(files)
    if "content" in files:
        return files["content"]

    return "No DATA file"


def delete_backup(client_id, backup_id):
    """
    Delete backup

    Args:
        Client id and backup id

    Returns:
        Array of info from backup deleted
    """
    api = UrApiWrapper()
    delete = api.delete_backup(client_id, backup_id)
    # delete = api.response(delete)
    if "content" in delete:
        return delete["content"]

    return "No DATA file"


def client_download_backup_file(clientid, backupid, path, filter_path):
    """
    Restore directory for one client

    Args:
        Client id, backup id, path of directory, filter

    Returns:
        State of restoration
    """
    api = UrApiWrapper()
    download = api.client_download_backup_file(clientid, backupid, path, filter_path)
    # download = api.response(download)
    if "content" in download:
        return download["content"]

    return "No DATA file"


def client_download_backup_file_shahash(clientid, backupid, path, shahash, filter_path):
    """
    Restore file for one client

    Args:
        Client id, backup id, path of directory, shahash of file

    Returns:
        State of restoration
    """
    api = UrApiWrapper()
    download = api.client_download_backup_file_shahash(
        clientid, backupid, path, shahash, filter_path
    )
    # download = api.response(download)
    if "content" in download:
        return download["content"]

    return "No DATA file"


def get_status():
    """
    Get server and all client status

    Returns:
        Array of server and all client status and parameters
    """
    api = UrApiWrapper()
    status = api.get_status()
    # status = api.response(status)
    if "content" in status:
        return status["content"]

    return "No DATA status"



def recursive_str_to_int(data):
    if isinstance(data, int):
        data = str(data)
        return data

    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = recursive_str_to_int(value)
    elif isinstance(data, list):
        for index, item in enumerate(data):
            data[index] = recursive_str_to_int(item)

    return data



def get_progress():
    """
    Get progress for every backups

    Returns:
        Array of progress review for backups
    """
    api = UrApiWrapper()
    progress = api.get_progress()
    # progress = api.response(progress)

    if "content" in progress:
        return recursive_str_to_int(progress["content"])

    return "No DATA progress"


def get_status_client(clientname):
    """
    Get status for one client

    Args:
        Client name

    Returns:
        Array status, and parameters for one client
    """
    api = UrApiWrapper()
    status = api.get_status()
    # status = api.response(status)

    for client in status["status"]:
        if client["name"] == clientname:
            return client

        return "No DATA client"


def create_backup_incremental_file(client_id):
    """
    Run incremental backup for one client

    Args:
        Client id

    Returns:
        State of this backup, ok or failed
    """
    api = UrApiWrapper()
    backup = api.create_backup("incr_file", client_id)
    # backup = api.response(backup)

    if "content" in backup:
        return backup["content"]

    return "No DATA incremental backup file"


def create_backup_full_file(client_id):
    """
    Run full backup for one client

    Args:
        Client id

    Returns:
        State of this backup, ok or failed
    """
    api = UrApiWrapper()
    backup = api.create_backup("full_file", client_id)
    # backup = api.response(backup)

    if "content" in backup:
        return backup["content"]

    return "No DATA full backup file"


def update_profile_machine(entityId, entityName, computerJid, computerName):
    """
    Update the profile and machine association in the database and urbackup server.
    Consolidates the profile and machine information, ensuring that the machine is correctly associated with the specified profile.

    args:
        entityId (str): The unique identifier for the profile entity.
        entityName (str): The name of the profile entity.
        computerJid (str): The JID (Jabber ID) of the computer/machine to be associated with the profile.
        computerName (str): The name of the computer/machine to be associated with the profile.

    Returns:
        dict: Status of the update operation, including success or failure message.
    """


    #
    # profile exists in db ?
    #
    #   yes : nothing to do
    #   no : create profile in db
    #   finally: get the profile info
    #
    # Check if the entity is stored in profiles table
    profile_db = UrbackupDatabase().get_profile(entityId)

    # Need to create a profile
    if profile_db == {}:
        # Ensure unique uuid for the profile
        # urbackup.profiles.profile_uuid. This uuid will be used as profile name on urbackup api
        entity_id = entityId
        profile_uuid = f"{entityName}{uuid.uuid4()}"
        profile_name = entityName
        profile_db = UrbackupDatabase().add_profile(entity_id, profile_uuid, profile_name)

    # Here it's not normal to have an empty profile,
    # Something went wrong here.
    if profile_db == {}:
        return {"status": 1, "msg": "Impossible to create profile %s"%profile_name}

    #
    # machine associated to any profile ?
    #   yes : get the association info
    #       machine associated to the right profile ?
    #           yes : nothing to do
    #           no : update the machine profile association in db
    #   no : nothing to do
    #   finally : get the association info
    #
    # Now we need to add the machine tho this profile
    # Check if the machine is in the profile
    profile_id = profile_db["id"]
    machine_jid = computerJid
    association_machine_profile = UrbackupDatabase().get_machine_profile(machine_jid)

    if association_machine_profile != {}:
        if association_machine_profile["profile_id"] != profile_id:
            # The machine is associated to another profile, we need to update the association in the database
            # First we need to remove the association in the database
            if UrbackupDatabase().update_association_machine_profile(association_machine_profile["id"], profile_id) is True:
                association_machine_profile = UrbackupDatabase().get_machine_profile(machine_jid)
            else:
                return {"status": 1, "msg": "Impossible to update machine %s to profile %s"%(computerName, entityName)}
    else:
        # The machine is not associated to any profile, we need to add the association in the database
        association_machine_profile = UrbackupDatabase().add_machine_to_profile(profile_id, machine_jid)

        if association_machine_profile == {}:
            return {"status": 1, "msg": "Impossible to add machine %s to profile %s"%(computerName, entityName)}


    #
    # profile exists in urbackup ?
    #   yes : nothing to do
    #   no : create profile in urbackup
    #   finally : get the profile info
    #

    group = UrbackupSettingsDb().get_group_by_name(profile_db["profile_uuid"])
    if group == {}:
        group_added = add_group(profile_db["profile_uuid"])

    # Second try: if this time the group is still not in urbackup, we have a problem with the urbackup api
    group = UrbackupSettingsDb().get_group_by_name(profile_db["profile_uuid"])
    if group == {}:
        return {"status":1, "msg":"Impossible to add urbackup-api group %s"%(profile_db["profile_name"])}

    #
    # machine exists in urbackup ?
    #   yes : nothing to do
    #   no : add the machine in urbackup
    #   finally : get the machine info
    #
    client = UrbackupDb().get_client_by_name(computerName)
    if client == {}:
        add_client(computerName)

    client = UrbackupDb().get_client_by_name(computerName)
    if client == {}:
        return {"status":1, "msg":"Impossible to add urbackup-api client %s"%(computerName)}


    #
    # machine associated to the right profile in urbackup ?
    #   yes : nothing to do
    #   no : update the machine profile association in urbackup
    #
    UrbackupDb().update_client_group(client["id"], group["id"])
    ret = UrbackupSettingsDb().update_client_group(client["id"], group["id"])
    if ret is False:
        return {"status":1, "msg":"Impossible to update urbackup-api client %s to group %s"%(computerName, profile_db["profile_name"])}

    # Get client authkey
    auth = UrbackupSettingsDb().get_setting("internet_authkey", client["id"])

    state = UrbackupDatabase().update_client_state(client["id"], machine_jid, auth, state=1)
    if state == {}:
        return {"status":1, "msg":"Impossible to update client %s state"%(computerName)}

    return {"status":0, "msg":"", "data": {
        "clientid":client["id"],
        "authkey":auth,
        "profile_id":profile_id,
        "profile_name":profile_db["profile_name"],
        "profile_uuid":profile_db["profile_uuid"],
        }
    }


def get_backup_state_for_client(clientid):
    """
    Get backups for one client

    Args:
        Client id
    Returns:
        Array of backups for one client
    """
    result = {
        "backup": {},
        "state": {},
    }

    api = UrApiWrapper()
    response = api.get_backups(clientid)

    if "content" not in response or "clients" not in response["content"]:
        return {}

    backups = response["content"]["clients"]
    # if {'clients': [{'id': 1, 'lastbackup': 1785846086, 'name': 'kno-w11-1'}]}

    if len(backups) > 0:
        backups[0]["lastbackup"] = str(backups[0]["lastbackup"])
        result["backup"] = backups[0]

    state = UrbackupDatabase().get_client_state(clientid)
    result["state"] = state
    return result

def get_backups_for_client(clientid, start, end, filter=""):
    """
    Get backups for one client

    Args:
        Client id,
        start : begin offset,
        end : end offset,
        filter : filter criteria
    Returns:
        Array of backups for one client
    """
    return UrbackupDb().get_backups_for_client(clientid, start, end, filter)


def get_group_info(entityid):
    if entityid is None or entityid == "":
        return {}

    if isinstance(entityid, str):
        try:
            entityid = int(entityid.replace("UUID", ""))
        except:
            return {}

    groupdb = UrbackupDatabase().get_group_info(entityid)
    if groupdb != {}:
        api = UrbackupSettingsDb().get_group_by_name(groupdb["profile_uuid"])

        if api != {}:
            groupdb["api_id"] = api["id"]


    return groupdb
