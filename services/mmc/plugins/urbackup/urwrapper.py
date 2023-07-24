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
    url = ""
    user_login = ""
    password = ""
    ses = ""
    headers = {}
    verify = False
    allow_redirects = True

    def __init__(self):
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
        self.headers[key] = value

    def request(self, action, params, method="POST"):
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
        self.login()
        session = self.ses
        return session

    @staticmethod
    def response(resp):
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
        self.login()
        params = {"clientid": clientid, "lastid": 0, "ses": self.ses}
        response = self.request("livelog", params)

        return response

    def add_client(self, clientname):
        self.login()
        params = {"clientname": clientname, "ses": self.ses}
        response = self.request("add_client", params)

        return response

    def get_stats(self):
        self.login()
        params = {"ses": self.ses}
        response = self.request("usage", params)

        return response

    def add_group(self, groupname):
        self.login()
        params = {"sa": "groupadd", "name": groupname, "ses": self.ses}
        response = self.request("settings", params)

        return response

    def remove_group(self, groupid):
        self.login()
        params = {"sa": "groupremove", "id": groupid, "ses": self.ses}
        response = self.request("settings", params)

        return response

    def get_settings_general(self):
        self.login()
        params = {"sa": "general", "ses": self.ses}
        response = self.request("settings", params)

        return response

    def save_settings(self, clientid, name_data, value_data):
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
        self.login()
        params = {"sa": "clientsettings", "t_clientid": id_client, "ses": self.ses}
        response = self.request("settings", params)

        return response

    def get_settings_clients(self):
        self.login()
        params = {"sa": "listusers", "ses": self.ses}
        response = self.request("settings", params)

        return response

    def get_backups(self, client_id):
        self.login()
        params = {"clientid": client_id, "ses": self.ses}
        response = self.request("backups", params)

        return response

    def delete_backup(self, client_id, backup_id):
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
        self.login()
        params = {"ses": self.ses}
        response = self.request("progress", params)

        return response

    def get_status(self):
        self.login()
        params = {"ses": self.ses}
        response = self.request("status", params)

        return response

    def create_backup(self, type_backup, client_id):
        self.login()
        params = {"start_type": type_backup, "start_client": client_id, "ses": self.ses}
        response = self.request("start_backup", params)

        return response
