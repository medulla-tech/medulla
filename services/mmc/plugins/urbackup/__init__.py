# -*- coding: utf-8; -*-
#
# (c) 2022 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import logging
import base64
import json
import configparser

from pulse2.version import getVersion, getRevision  # pyflakes.ignore
from pulse2.database.urbackup import UrbackupDatabase

from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.urbackup.config import UrbackupConfig
from mmc.plugins.xmppmaster.master.agentmaster import callremotecommandshell
from mmc.plugins.xmppmaster.master.agentmaster import send_message_json
from mmc.plugins.xmppmaster.master.lib.utils import name_random
from mmc.plugins.urbackup.urwrapper import UrApiWrapper

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
        logger.warning(
            "Plugin urbackup: an error occurred during the database initialization"
        )
        return False
    return True

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
    logged = api.response(logged)

    if "content" in logged and "session" in logged["content"]:
        return logged["content"]["session"]

    return False

def check_client(jidmachine, clientid, authkey):
    conf_file = "/var/lib/pulse2/clients/config/updatebackupclient.ini"

    urbackup_conf = configparser.ConfigParser()
    urbackup_conf.read(conf_file)

    urbackup_server = urbackup_conf.get('parameters', 'backup_server')
    urbackup_port = urbackup_conf.get('parameters', 'backup_port')

    command = "(echo [parameters] & echo backup_enabled = 1 & echo client_id = "+str(clientid)+" & echo authkey = "+str(authkey)+" & echo backup_server = "+str(urbackup_server)+" & echo backup_port = "+str(urbackup_port)+") > C:\progra~1\pulse\etc\updatebackupclient.ini"

    callremotecommandshell(jidmachine, command)
    sessionid = name_random(8, "update_")
    msg = {
    "action": "restartbot",
    "sessionid": sessionid,
    "data": {},
    "ret": 0,
    "base64": False
    }
    send_message_json(jidmachine, msg)

def remove_client(jidmachine):
    command = "(echo [parameters] & echo backup_enabled = 0 ) > C:\progra~1\pulse\etc\updatebackupclient.ini"

    callremotecommandshell(jidmachine, command)
    sessionid = name_random(8, "update_")
    msg = {
    "action": "restartbot",
    "sessionid": sessionid,
    "data": {},
    "ret": 0,
    "base64": False
    }
    send_message_json(jidmachine, msg)

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

def get_logs():
    """
    Get the logs of the server

    Returns:
        It returns the server logs.
        If no logs are available, it returns the "No DATA" string.
    """
    api = UrApiWrapper()
    _logs = api.get_logs()
    logs = api.response(_logs)
    if "content" in logs:
        return logs["content"]

    return "No DATA in logs"

def add_client(client_name):
    """
    Create client with new id and authkey

    Returns:
        Server,
        Port,
        Authkey,
        Client ID,
        Client Name
    """
    api = UrApiWrapper()
    newclient = api.add_client(client_name)
    newclient = api.response(newclient)
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
    stats = api.response(stats)
    if "content" in stats:
        return stats["content"]

    return "No DATA in stats"

def add_group(groupname):
    """
    Create groupe

    Returns:
        Settings
    """
    api = UrApiWrapper()
    newgroup = api.add_group(groupname)
    newgroup = api.response(newgroup)
    if "content" in newgroup:
        return newgroup["content"]

    return "No DATA in newclient"

def remove_group(groupid):
    """
    Remove groupe

    Returns:
        Settings
    """
    api = UrApiWrapper()
    removegroup = api.remove_group(groupid)
    removegroup = api.response(removegroup)
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
    settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA in global settings"


def save_settings(clientid, name_data, value_data):
    """
    Save settings for client of group

    Returns:
        Settings saved for group
    """
    api = UrApiWrapper()
    settings = api.save_settings(clientid, name_data, value_data)
    settings = api.response(settings)
    if "content" in settings:
        return settings["content"]

    return "No DATA settings saved"


def get_settings_clientsettings(id_client):
    """
    Get multiples settings for one client

    Returns:
        Array of client settings
    """
    api = UrApiWrapper()
    settings = api.get_settings_clientsettings(id_client)
    settings = api.response(settings)
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
    list_clients = api.response(list_clients)
    if "content" in list_clients:
        return list_clients["content"]

    return "No DATA listusers"


def get_backups_all_client():
    """
    Get every backups for each client

    Returns:
        Array of every backup for each client
    """
    api = UrApiWrapper()
    backups = api.get_backups("0")
    backups = api.response(backups)
    if "content" in backups:
        return backups["content"]

    return "No DATA backups"


def get_backup_files(client_id, backup_id, path):
    """
    Get every files on backup

    Returns:
        Array of info from backup
    """
    api = UrApiWrapper()
    files = api.get_backup_files(client_id, backup_id, path)
    files = api.response(files)
    if "content" in files:
        return files["content"]


    return "No DATA file"

def delete_backup(client_id, backup_id):
    """
    Delete backup

    Returns:
        Array of info from backup deleted
    """
    api = UrApiWrapper()
    delete = api.delete_backup(client_id, backup_id)
    delete = api.response(delete)
    if "content" in delete:
        return delete["content"]

    return "No DATA file"


def client_download_backup_file(clientid, backupid, path, filter_path):
    """ """
    api = UrApiWrapper()
    download = api.client_download_backup_file(clientid, backupid, path, filter_path)
    download = api.response(download)
    if "content" in download:
        return download["content"]

    return "No DATA file"


def client_download_backup_file_shahash(clientid, backupid, path, shahash):
    """ """
    api = UrApiWrapper()
    download = api.client_download_backup_file_shahash(
        clientid, backupid, path, shahash
    )
    download = api.response(download)
    if "content" in download:
        return download["content"]

    return "No DATA file"


def get_status():
    """
    Get server and all client status

    Returns:
        Array of server and all client status
    """
    api = UrApiWrapper()
    status = api.get_status()
    status = api.response(status)
    if "content" in status:
        return status["content"]

    return "No DATA status"


def get_progress():
    """
    Get progress for every backups

    Returns:
        Array of progress review for backups
    """
    api = UrApiWrapper()
    progress = api.get_progress()
    progress = api.response(progress)
    if "content" in progress:
        return progress["content"]

    return "No DATA progress"


def get_status_client(clientname):
    """
    Get status for one client

    Args:
        Clientname

    Returns:
        Array status for one client
    """
    api = UrApiWrapper()
    status = api.get_status()
    status = api.response(status)

    for client in status["status"]:
        if client["name"] == clientname:
            return client

        return "No DATA client"


def create_backup_incremental_file(client_id):
    """ """
    api = UrApiWrapper()
    backup = api.create_backup("incr_file", client_id)
    backup = api.response(backup)

    if "content" in backup:
        return backup["content"]

    return "No DATA incremental backup file"


def create_backup_full_file(client_id):
    """ """
    api = UrApiWrapper()
    backup = api.create_backup("full_file", client_id)
    backup = api.response(backup)

    if "content" in backup:
        return backup["content"]

    return "No DATA full backup file"
