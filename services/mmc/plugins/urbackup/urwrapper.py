# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
import json
import requests
from requests.structures import CaseInsensitiveDict
from mmc.plugins.urbackup import config

try:
    from urllib import urlencode
except BaseException:
    from urllib.parse import urlencode


class UrApiWrapper:
    """
    Wrapper for UrBackup API.

    Attributes:
        url (str): UrBackup server URL.
        user_login (str): UrBackup server username.
        password (str): UrBackup server password.
        ses (str): Session ID.
        headers (dict): HTTP headers for requests.
        verify (bool): SSL certificate verification.
        allow_redirects (bool): Allow redirects in HTTP requests.

    Methods:
        set_header(self, key, value): Set a custom header.
        request(self, action, params, method="POST"): Make a request to the UrBackup API.
        login(self, lang="en"): Log in to the UrBackup server.
        get_session(self): Get the current session ID.
        response(resp): Parse and return a standardized response.
        get_logs(self, clientid=0): Get live logs for a client.
        add_client(self, clientname): Add a new client to UrBackup.
        get_stats(self): Get server usage statistics.
        add_group(self, groupname): Add a new group to UrBackup.
        remove_group(self, groupid): Remove a group from UrBackup.
        get_settings_general(self): Get general settings.
        save_settings(self, clientid, name_data, value_data): Save client settings.
        get_settings_clientsettings(self, id_client): Get client-specific settings.
        get_settings_clients(self): Get a list of clients.
        get_backups(self, client_id): Get a list of backups for a client.
        delete_backup(self, client_id, backup_id): Delete a specific backup.
        get_backup_files(self, client_id, backup_id, path): Get files from a backup.
        client_download_backup_file(self, client_id, backup_id, path, filter_path): Download a specific file from a backup.
        client_download_backup_file_shahash(self, client_id, backup_id, path, shahash): Download a file by SHA hash from a backup.
        get_progress(self): Get the progress of ongoing operations.
        get_status(self): Get the status of the UrBackup server.
        create_backup(self, type_backup, client_id): Start a new backup operation.
    """
    url = ""
    user_login = ""
    password = ""
    ses = ""
    headers = {}
    verify = False
    allow_redirects = True

    def __init__(self):
        """
        Initialize UrApiWrapper with configuration from UrbackupConfig.
        """
        _config = config.UrbackupConfig()
        self.url = _config.urbackup_url
        self.user_login = _config.urbackup_username
        self.password = _config.urbackup_password
        self.ses = ""  # sessionid

        self.headers = CaseInsensitiveDict()
        self.headers["Accept"] = "application/json"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"
        self.verify = False
        self.allow_redirects = True

    def set_header(self, key, value):
        """
        Set a custom header for the HTTP request.

        Args:
            key (str): Header key.
            value (str): Header value.
        """
        self.headers[key] = value

    def request(self, action, params, method="POST"):
        """
        Make a request to the UrBackup API.

        Args:
            action (str): API action to perform.
            params (dict): Parameters for the API action.
            method (str): HTTP method (default is "POST").

        Returns:
            Response: HTTP response object.
        """
        url = self.url + "?" + urlencode({"a": action})

        if method == "GET":
            response = requests.get(
                url,
                headers=self.headers,
                data=params,
                verify=self.verify,
                allow_redirects=self.allow_redirects,
            )
        if method == "POST":
            response = requests.post(
                url,
                headers=self.headers,
                data=params,
                verify=self.verify,
                allow_redirects=self.allow_redirects,
            )

        return response

    def login(self, lang="en"):
        """
        Log in to the UrBackup server.

        Args:
            lang (str): Language for the login (default is "en").

        Returns:
            Response: HTTP response object.
        """
        params = {
            "username": self.user_login,
            "password": self.password,
            "plainpw": 1,
            "lang": lang,
        }
        response = self.request("login", params)

        try:
            result = json.loads(response.text)
            if "session" in result:
                self.ses = result["session"]
        except BaseException:
            pass

        return response

    def get_session(self):
        """
        Get the current session ID.

        Returns:
            str: Session ID.
        """
        self.login()
        session = self.ses
        return session

    @staticmethod
    def response(resp):
        """
        Parse and return a standardized response.

        Args:
            resp (Response): HTTP response object.

        Returns:
            dict: Standardized response containing status code, headers, and content.
        """
        try:
            resp_json = json.loads(resp.text)
        except BaseException:
            resp_json = resp.text

        return {
            "status_code": resp.status_code,
            "headers": resp.headers,
            "content": resp_json,
        }

    def get_logs(self, clientid=0):
        """
        Get live logs for a client.

        Args:
            clientid (int): Client ID (default is 0).

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"clientid": clientid, "lastid": 0, "ses": self.ses}
        response = self.request("livelog", params)

        return response

    def add_client(self, clientname):
        """
        Add a new client to UrBackup.

        Args:
            clientname (str): Name of the new client.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"clientname": clientname, "ses": self.ses}
        response = self.request("add_client", params)

        return response

    def get_stats(self):
        """
        Get server usage statistics.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"ses": self.ses}
        response = self.request("usage", params)

        return response

    def add_group(self, groupname):
        """
        Add a new group to UrBackup.

        Args:
            groupname (str): Name of the new group.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"sa": "groupadd", "name": groupname, "ses": self.ses}
        response = self.request("settings", params)

        return response

    def remove_group(self, groupid):
        """
        Remove a group from UrBackup.

        Args:
            groupid (str): ID of the group to be removed.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"sa": "groupremove", "id": groupid, "ses": self.ses}
        response = self.request("settings", params)

        return response

    def get_settings_general(self):
        """
        Get general settings.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"sa": "general", "ses": self.ses}
        response = self.request("settings", params)

        return response

    def save_settings(self, clientid, name_data, value_data):
        """
        Save client settings.

        Args:
            clientid (str): ID of the client.
            name_data (str): Name of the setting.
            value_data: Value of the setting.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {
            "sa": "clientsettings_save",
            "t_clientid": clientid,
            "overwrite": "true",
            name_data: value_data,
            "ses": self.ses,
        }
        response = self.request("settings", params)

        return response

    def get_settings_clientsettings(self, id_client):
        """
        Get client-specific settings.

        Args:
            id_client (str): ID of the client.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"sa": "clientsettings", "t_clientid": id_client, "ses": self.ses}
        response = self.request("settings", params)

        return response

    def get_settings_clients(self):
        """
        Get a list of clients.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"sa": "listusers", "ses": self.ses}
        response = self.request("settings", params)

        return response
    
    def get_settings_client(self, id_client):
        """
        Get settings for one client with id client

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"sa": "clientsettings", "t_clientid": id_client, "ses": self.ses}
        response = self.request("settings", params)

        return response

    def get_backups(self, client_id):
        """
        Get a list of backups for a client.

        Args:
            client_id (str): ID of the client.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"clientid": client_id, "ses": self.ses}
        response = self.request("backups", params)

        return response

    def delete_backup(self, client_id, backup_id):
        """
        Delete a specific backup.

        Args:
            client_id (str): ID of the client.
            backup_id (str): ID of the backup to be deleted.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {
            "sa": "backups",
            "clientid": client_id,
            "delete_now": backup_id,
            "ses": self.ses,
        }
        response = self.request("backups", params)

        return response

    def get_backup_files(self, client_id, backup_id, path):
        """
        Get files from a backup.

        Args:
            client_id (str): ID of the client.
            backup_id (str): ID of the backup.
            path (str): Path to the files in the backup.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {
            "sa": "files",
            "clientid": client_id,
            "backupid": backup_id,
            "path": path,
            "ses": self.ses,
        }
        response = self.request("backups", params)

        return response

    def client_download_backup_file(self, client_id, backup_id, path, filter_path):
        """
        Download a specific file from a backup.

        Args:
            client_id (str): ID of the client.
            backup_id (str): ID of the backup.
            path (str): Path to the file in the backup.
            filter_path (str): Filter path.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {
            "sa": "clientdl",
            "clientid": client_id,
            "backupid": backup_id,
            "path": path,
            "filter": filter_path,
            "ses": self.ses,
        }
        response = self.request("backups", params)

        return response

    def client_download_backup_file_shahash(self, client_id, backup_id, path, shahash):
        """
        Download a file by SHA hash from a backup.

        Args:
            client_id (str): ID of the client.
            backup_id (str): ID of the backup.
            path (str): Path to the file in the backup.
            shahash (str): SHA hash of the file.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {
            "sa": "clientdl",
            "clientid": client_id,
            "backupid": backup_id,
            "path": path,
            "ses": self.ses,
            "shahash": shahash,
        }
        response = self.request("backups", params)

        return response

    def get_progress(self):
        """
        Get the progress of ongoing operations.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"ses": self.ses}
        response = self.request("progress", params)

        return response

    def get_status(self):
        """
        Get the status of the UrBackup server.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"ses": self.ses}
        response = self.request("status", params)

        return response

    def create_backup(self, type_backup, client_id):
        """
        Start a new backup operation.

        Args:
            type_backup (str): Type of backup operation.
            client_id (str): ID of the client.

        Returns:
            Response: HTTP response object.
        """
        self.login()
        params = {"start_type": type_backup, "start_client": client_id, "ses": self.ses}
        response = self.request("start_backup", params)

        return response
