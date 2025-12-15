# -*- coding: utf-8; -*-
from sqlalchemy import create_engine, MetaData, select, func, and_, desc, or_, distinct, Table, DateTime, Text
from sqlalchemy.orm import create_session, mapper, relation
from sqlalchemy.exc import DBAPIError
from sqlalchemy import update



from sqlalchemy.ext.automap import automap_base


from datetime import date, datetime, timedelta
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.mobile.schema import Tests, Base
import logging
import json
import time
import requests
import hashlib



logger = logging.getLogger()

# Main class

class MobileDatabase(DatabaseHelper):
    is_activated = False
    session = None
    # Headwind REST API base (TO DO: consider moving to config)
    BASE_URL = "http://localhost/hmdm/rest"
    login = "admin"
    password = "admin"


    def db_check(self):
        self.my_name = "mobile"
        self.configfile = "mobile.ini"
        return DatabaseHelper.db_check(self)

    # Activate DB connection and automap tables
    def activate(self, config):
        """
        Activate the database connection and prepare the metadata and mappers.

        Args:
            config: Configuration object containing database settings.

        Returns:
            bool: True if activation is successful, False otherwise.
        """
        if self.is_activated:
            return None

        self.config = config

        try:
            # Create a database engine using the provided configuration
            self.db = create_engine(
                self.makeConnectionPath(),
                pool_recycle=self.config.dbpoolrecycle,
                pool_size=self.config.dbpoolsize,
            )
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            return False

        if not self.db_check():
            logger.error("Database check failed.")
            return False

        try:
            # Prepare metadata and automap base for SQLAlchemy
            self.metadata = MetaData(self.db)
            automap = automap_base(metadata=self.metadata)
            automap.prepare(self.db, reflect=True)
            logger.info(f"Tables mappées automatiquement : {list(automap.classes.keys())}")
        except Exception as e:
            logger.error(f"Failed to prepare automap base: {e}")
            return False

        # Lists to exclude or include specific tables for mapping
        exclude_table = []
        include_table = []

        # Dynamically add attributes to the object for each mapped class
        for table_name, mapped_class in automap.classes.items():
            if table_name in exclude_table:
                continue
            setattr(self, table_name.capitalize(), mapped_class)
        # self.Devices = Devices

        if not self.initMappersCatchException():
            self.session = None
            return False

        # Create all tables defined in metadata
        Base.metadata.create_all(bind=self.db)
        self.is_activated = True

        # Execute a sample query to check the database connection
        result = self.db.execute("SELECT * FROM mobile.version LIMIT 1;")
        re = [element.Number for element in result]
        return True

    def initMappers(self):
        """
        Initialize mappers. This method can be overridden to provide specific mapper initialization.
        """
        return

    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError as e:
                logging.getLogger().error(e)
            except Exception as e:
                logging.getLogger().error(e)
            if ret: break
        if not ret:
            raise Exception(f"Database mobile connection error")
        return ret

    @DatabaseHelper._sessionm
    def tests(self, session):
        ret = session.query(Tests).all()
        lines = []
        for row in ret:
            lines.append(row.toDict())
        return lines
    # Alternate DB-based phone retrieval (we use Headwind REST API instead)
    @DatabaseHelper._sessionm
    # function acces to database retravillé les injections plustard 
    def devices(self, session):
        ret = session.query(
            self.Devices.id,
            self.Devices.serial_number,
            self.Devices.token_update_at,
            self.Devices.created_at,
            self.Devices.updated_at,
            self.Devices.authenticate_at,
            self.Devices.bootstrap_token_at,
            self.Devices.unlock_token_at
        ).all()

        devices_nano = []
        for row in ret:
            device_dict = {
                "id": row.id,
                "serial_number": row.serial_number,
                "token_update_at": row.token_update_at.isoformat() if row.token_update_at else "",
                "created_at": row.created_at.isoformat() if row.created_at else "",
                "updated_at": row.updated_at.isoformat() if row.updated_at else "",
                "authenticate_at": row.authenticate_at.isoformat() if row.authenticate_at else "",
                "bootstrap_token_at": row.bootstrap_token_at.isoformat() if row.bootstrap_token_at else "",
                "unlock_token_at": row.unlock_token_at.isoformat() if row.unlock_token_at else ""
            }

            devices_nano.append(device_dict)

        return devices_nano


    # Headwind MDM device handling
    def to_back(self, name, desc):
        try:
                
            logger.error(f"111 - Voila ma variable name et desc avant d entrée en base {name} , {desc}")

            
            device_data = {
                    "id": 0,
                    "number": name,
                    "description": desc,
                    "configurationId": 1
                }
            return device_data
        except Exception as e:
                logging.getLogger().error(f"Erreur dans to_back: {e}")
                raise
    
    # HMDM API authentication
    def hash_password(self, password: str)-> str:
        """
        Hasher le mots de passe en md5 
        """
        hashed_pwd = hashlib.md5(password.encode()).hexdigest().upper()
        return hashed_pwd

    def authenticate(self, login: str = None, password: str = None) -> str:
        """
        Authentifie l'utilisateur auprès du service MDM en utilisant le mot de passe hashé en MD5.
        Renvoie le hmdmtoken JWT si succès, None sinon.
        """
        if login is None:
            login = self.login
        if password is None:
            password = self.password

        hashed_pwd = self.hash_password(password)

        url = f"{self.BASE_URL}/public/jwt/login"
        headers = {"Content-Type": "application/json"}
        data = {
            "login": login,
            "password": hashed_pwd
        }

        try:
            resp = requests.post(url, json=data, headers=headers)
            resp.raise_for_status()
            hmtoken = resp.json().get("id_token")

            if not hmtoken:
                raise Exception("Le hmdmtoken JWT est manquant dans la réponse.")

            logging.getLogger().info(f"Authentification réussie ")
            return hmtoken

        except Exception as e:
            logging.getLogger().error(f"Erreur lors de l'authentification : {e}")
            return None
    
    def getHmdmDevices(self):
        auth = self.authenticate()
        if auth is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer la liste des appareils.")
            return []
        return self.getList(auth)

    def getHmdmAuditLogs(self, page_size=50, page_num=1, message_filter="", user_filter=""):
        """
        Fetch audit logs from HMDM and return a normalized list.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer les logs d'audit.")
            return []

        url = f"{self.BASE_URL}/plugins/audit/private/log/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        payload = {
            "pageSize": page_size,
            "pageNum": page_num
        }

        if message_filter:
            payload["messageFilter"] = message_filter
        if user_filter:
            payload["userFilter"] = user_filter

        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()

            raw_data = resp.json()
            if raw_data is None:
                logging.getLogger().error("The audit logs were not retrieved")
                return []

            logging.getLogger().info("Audit logs retrieved successfully")

            #  Extract audit items
            audit_items = raw_data.get("data", {}).get("items", [])

            audit_list = []

            for item in audit_items:
                ts = item.get("createTime")  

                # Convert ms epoch -> formatted date
                if ts:
                    dt = datetime.fromtimestamp(ts / 1000)
                    date_str = dt.strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
                else:
                    date_str = ""

                action_code = item.get("action", "")
                readable_action = self._convert_action(action_code)

                audit_entry = {
                    "id": item.get("id"),
                    "date": date_str,
                    "login": item.get("login", ""),
                    "ip": item.get("ipAddress", ""),
                    "action": readable_action,
                    "raw_action": action_code,
                    "message": item.get("message", "")
                }

                audit_list.append(audit_entry)

            return audit_list

        except Exception as e:
            logging.getLogger().error(f"Error fetching audit logs: {e}")
            return []


    def _convert_action(self, action):
        """
        Convert HMDM audit action code into readable text.
        """
        mapping = {
            "plugin.audit.action.jwt.login": "API client login",
            "plugin.audit.action.user.login": "User login",
            "plugin.audit.action.user.logout": "User logout",
            "plugin.audit.action.update.configuration": "Configuration updated",
            "plugin.audit.action.copy.configuration": "Configuration copied",
            "plugin.audit.action.remove.configuration": "Configuration removed",
            "plugin.audit.action.update.device": "Device updated",
            "plugin.audit.action.remove.device": "Device removed",
            "plugin.audit.action.device.enroll": "Device enrollment",
            "plugin.audit.action.device.unenroll": "Device unenrollment",
            "plugin.audit.action.update.application": "Application updated",
            "plugin.audit.action.update.webapp": "Web application updated",
            "plugin.audit.action.remove.application": "Application removed",
            "plugin.audit.action.update.version": "Application version updated",
            "plugin.audit.action.remove.version": "Application version deleted",
            "plugin.audit.action.update.file": "File updated",
            "plugin.audit.action.remove.file": "File deleted",
            "plugin.audit.action.update.app.config": "Application configurations changed",
            "plugin.audit.action.version.config": "Version configurations changed",
            "plugin.audit.action.update.design": "Design settings updated",
            "plugin.audit.action.update.user.roles": "User role settings updated",
            "plugin.audit.action.update.language": "Language settings updated",
            "plugin.audit.action.update.plugins": "Plugin settings updated",
            "plugin.audit.action.update.user": "User updated",
            "plugin.audit.action.remove.user": "User removed",
            "plugin.audit.action.update.group": "Group updated",
            "plugin.audit.action.remove.group": "Group removed",
            "plugin.audit.action.password.changed": "User password changed",
            "plugin.audit.action.password.reset": "Device password reset",
            "plugin.audit.action.device.reset": "Device factory reset",
            "plugin.audit.action.device.lock": "Device locked"
        }

        return mapping.get(action, action)


    def getHmdmApplications(self):
        """
        Fetch the list of applications from HMDM.
        Returns a list of application dicts adapted for the frontend.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer la liste des applications.")
            return []

        url = f"{self.BASE_URL}/private/applications/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            logging.getLogger().info(f"Applications fetched successfully.")
            return resp.json().get("data")
        except Exception as e:
            logging.getLogger().error(f"Error fetching applications: {e}")
            return None

    def searchHmdmDevices(self, filter_text=""):
        """
        Search for devices by name for autocomplete.
        
        :param filter_text: Search filter text
        :return: List of device dicts with id, name
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour la recherche de devices.")
            return []

        url = f"{self.BASE_URL}/private/devices/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}
        
        payload = {
            "value": filter_text,
            "fastSearch": False,
            "pageSize": 5,
            "pageNum": 1
        }

        try:
            resp = requests.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            try:
                data = resp.json()
            except Exception:
                txt = resp.text.strip()
                return [txt] if txt else []
            logging.getLogger().info(f"Device search completed with filter: {filter_text}")
            devices = data.get("data", {}).get("devices", {}).get("items", [])
            result = [{"id": d["id"], "name": d["number"]} for d in devices]
            return result
        except Exception as e:
            logging.getLogger().error(f"Error searching devices: {e}")
            return []

    def getHmdmDetailedInfo(self, device_number):
        """
        Fetch detailed information for a specific device.
        
        :param device_number: Device number/identifier
        :return: Device information dict or empty dict on error
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer les infos détaillées.")
            return {}

        url = f"{self.BASE_URL}/plugins/deviceinfo/deviceinfo/private/{device_number}"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            logging.getLogger().info(f"Device detailed info fetched successfully for {device_number}.")
            return data.get("data", {}) if isinstance(data, dict) else data
        except Exception as e:
            logging.getLogger().error(f"Error fetching device detailed info: {e}")
            return {}
        
    def getHmdmMessages(self, device_number="", message_filter="", status_filter="",
                    date_from_millis=None, date_to_millis=None,
                    page_size=50, page_num=1):
        """
        Fetch messaging records from HMDM.
        
        :param device_number: Device number filter
        :param message_filter: Message content filter
        :param status_filter: Status filter (all messages, or numeric status 0-4)
        :param date_from_millis: Start date in milliseconds
        :param date_to_millis: End date in milliseconds
        :param page_size: Records per page
        :param page_num: Page number
        :return: List of message records or empty list
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer les messages.")
            return []

        url = f"{self.BASE_URL}/plugins/messaging/private/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}
        
        payload = {
            "pageSize": page_size,
            "pageNum": page_num,
            "status": -1  # Default to all messages
        }

        STATUS_MAP = {
            0: "Sent",
            1: "Delivered",
            2: "Read",
            3: "Failed",
            4: "Pending",
        }
        
        if device_number:
            payload["deviceFilter"] = device_number
        if message_filter:
            payload["messageFilter"] = message_filter
        if status_filter and status_filter != "all messages":
            try:
                payload["status"] = int(status_filter)
            except (ValueError, TypeError):
                payload["status"] = -1
        if date_from_millis:
            payload["dateFrom"] = date_from_millis
        if date_to_millis:
            payload["dateTo"] = date_to_millis

        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            messages = data.get("data", {}).get("items", [])
            result = [{"name": m["deviceNumber"], "time": m["ts"]//1000, "message": m["message"], "status": STATUS_MAP.get(m["status"], "Unknown")} for m in messages]

            logging.getLogger().info(f"Messages fetched successfully.")
            return result
        except Exception as e:
            logging.getLogger().error(f"Error fetching messages: {e}")
            return []

    def getHmdmPushMessages(self, device_number="", message_filter="", status_filter="",
                    date_from_millis=None, date_to_millis=None,
                    page_size=50, page_num=1):
        """
        Fetch push messages from HMDM.
        
        :param device_number: Device number filter
        :param message_filter: Message content filter
        :param status_filter: Status filter (all messages, sent, delivered, read)
        :param date_from_millis: Start date in milliseconds
        :param date_to_millis: End date in milliseconds
        :param page_size: Records per page
        :param page_num: Page number
        :return: List of push message records or empty list
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer les messages.")
            return []

        url = f"{self.BASE_URL}/plugins/push/private/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}
        
        payload = {
            "pageSize": page_size,
            "pageNum": page_num
        }

        STATUS_MAP = {
            0: "Sent",
            1: "Delivered",
            2: "Read",
            3: "Failed",
            4: "Pending",
        }
        
        if device_number:
            payload["deviceNumber"] = device_number
        if message_filter:
            payload["filter"] = message_filter
        if status_filter and status_filter != "all messages":
            payload["status"] = status_filter
        if date_from_millis:
            payload["dateFromMillis"] = date_from_millis
        if date_to_millis:
            payload["dateToMillis"] = date_to_millis

        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            logging.getLogger().info(f"Push messages: {data}")


            messages = data.get("data", {}).get("items", [])
            result = [{"name": m["deviceNumber"], "time": m["ts"]//1000, "type": m["messageType"], "payload": m.get("payload", "")} for m in messages]

            logging.getLogger().info(f"Push messages fetched successfully.")
            return result
        except Exception as e:
            logging.getLogger().error(f"Error fetching push messages: {e}")
            return []

    def getHmdmConfigurations(self):
        """
        Fetch the list of configurations from HMDM.
        Returns a list of configuration dicts with keys: id, name, description.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer la liste des configurations.")
            return []

        url = f"{self.BASE_URL}/private/configurations/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            raw = resp.json()
            if raw is None:
                return []

            # Depending on API shape, items may be top-level or under 'data'
            items = raw if isinstance(raw, list) else raw.get('data') or raw.get('configurations') or []
            configs = []
            for c in items:
                cfg = {
                    'id': c.get('id') or c.get('configurationId'),
                    'name': c.get('name') or c.get('title'),
                    'description': c.get('description') or ''
                }
                configs.append(cfg)
            return configs
        except Exception as e:
            logging.getLogger().error(f"Erreur lors de la récupération des configurations HMDM: {e}")
            return []

    def getHmdmFiles(self):
        """
        Fetch the list of files from HMDM and normalize fields for frontend.
        Returns list of dicts with keys: id, filePath, description, size, uploadTime (seconds), devicePath, external, replaceVariables
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer la liste des fichiers.")
            return []

        url = f"{self.BASE_URL}/private/web-ui-files/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            raw = resp.json()
            if raw is None:
                return []

            items = raw if isinstance(raw, list) else raw.get('data') or raw.get('files') or []
            files = []
            for f in items:
                # Protect against huge integers: convert ms -> seconds to avoid XML-RPC 32-bit overflow
                upload_ms = f.get('uploadTime') or f.get('upload_time') or f.get('upload')
                upload_sec = None
                if isinstance(upload_ms, (int, float)):
                    try:
                        upload_sec = int(upload_ms) // 1000
                    except Exception:
                        upload_sec = None
                raw_size = f.get('size')
                size_mb = None
                if isinstance(raw_size, (int, float)):
                    size_mb = round(raw_size / (1024 * 1024), 1)

                file_entry = {
                    'id': f.get('id'),
                    'filePath': f.get('filePath') or f.get('path') or f.get('url') or '',
                    'description': f.get('description') or '',
                    'size': size_mb,
                    'uploadTime': upload_sec,
                    'devicePath': f.get('devicePath') or f.get('device_path') or '',
                    'external': bool(f.get('external')),
                    'replaceVariables': bool(f.get('replaceVariables'))
                }
                files.append(file_entry)
            return files
        except Exception as e:
            logging.getLogger().error(f"Error fetching files: {e}")
            return []
        
    def hmdmRawFile(self, uploaded_file_path, uploaded_file_name, token):
        """
        Upload raw file via multipart to HMDM.
        Returns dict with serverPath, name, raw response or error.
        """
        upload_url = f"{self.BASE_URL}/private/web-ui-files/raw"
        headers = {"Authorization": f"Bearer {token}"}
        resp = None
        try:
            with open(uploaded_file_path, "rb") as fh:
                files = {"file": (uploaded_file_name, fh)}
                resp = requests.post(upload_url, headers=headers, files=files)
                logger.info(f"Raw upload response status: {resp.status_code}")
                logger.info(f"Raw upload response body: {resp.text}")
                resp.raise_for_status()
                upload_resp = resp.json() if resp.text else {}
                upload_data = upload_resp.get("data") or {}
                server_path = upload_data.get("serverPath") or upload_resp.get("serverPath")
                name = upload_data.get("name") or upload_resp.get("name")
                return {"serverPath": server_path, "name": name, "raw": upload_resp}
        except Exception as e:
            logger.error(f"Error in raw upload: {e}", exc_info=True)
            return {"error": True, "message": str(e), "raw_text": resp.text if resp else None}

    def hmdmUploadFile(self, body, token):
        """
        Commit uploaded/external file to HMDM (update endpoint).
        Returns dict with raw response or error.
        Note: Server may return 500 even if file is successfully uploaded.
        """
        update_url = f"{self.BASE_URL}/private/web-ui-files/update"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        resp = None
        try:
            resp = requests.post(update_url, headers=headers, json=body)
            logger.info(f"Update response status: {resp.status_code}")
            logger.info(f"Update response body: {resp.text}")
            if resp.status_code == 500:
                # Server returns 500 but file may already be on server from raw upload
                logger.warning(f"Update endpoint returned 500, but file may be uploaded. Continuing...")
                # Return a basic response based on the body we sent
                return {"raw": {"filePath": body.get("filePath"), "tmpPath": body.get("tmpPath")}}
            resp.raise_for_status()
            return {"raw": resp.json() if resp.text else {}}
        except Exception as e:
            logger.error(f"Error in update/commit: {e}", exc_info=True)
            return {"error": True, "message": str(e), "raw_text": resp.text if resp else None}

    def hmdmFileConfiguration(self, file_id, config_ids, token):
        """
        Link file to configurations in HMDM.
        Returns dict with raw response or error.
        """
        resp_cfg = None
        try:
            if not file_id:
                return {"error": True, "message": "file_id missing"}
            config_url = f"{self.BASE_URL}/private/web-ui-files/configurations"
            configs_payload = []
            for cid in (config_ids if isinstance(config_ids, list) else [config_ids]):
                configs_payload.append({"configurationId": int(cid), "upload": True})
            cfg_body = {"fileId": int(file_id), "configurations": configs_payload}
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            logger.info(f"Linking file {file_id} to configurations: {json.dumps(cfg_body)}")
            resp_cfg = requests.post(config_url, headers=headers, json=cfg_body)
            logger.info(f"Configurations response status: {resp_cfg.status_code}")
            logger.info(f"Configurations response body: {resp_cfg.text}")
            resp_cfg.raise_for_status()
            return {"raw": resp_cfg.json() if resp_cfg.text else {}}
        except Exception as e:
            logger.error(f"Failed to link configurations: {e}", exc_info=True)
            return {"error": True, "message": str(e), "raw_text": resp_cfg.text if resp_cfg else None}

    def addHmdmFile(self, uploaded_file_path=None, uploaded_file_name=None, external_url=None, file_name=None, path_on_device=None, description=None, variable_content=None, configuration_ids=None):
        """
        Add a file to HMDM.

        All arguments are optional:
        - uploaded_file_path: local file path to upload
        - uploaded_file_name: original name of the uploaded file
        - external_url: URL of an external file
        - file_name: name to give the file in HMDM
        - path_on_device: path where the file should be placed on the device
        - description: optional description of the file
        - variable_content: whether the file content should replace variables
        - configuration_ids: list of configuration IDs to link this file to (optional)

        Returns the added file info dict with keys: id, filePath, description, size, uploadTime (seconds),
        devicePath, external, replaceVariables
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logger.error("Impossible d'authentifier pour ajouter le fichier.")
            return {"error": True, "message": "Authentication failed"}

        # Main flow: raw upload (if file), then commit, then optional configuration linking
        raw_commit = None
        if uploaded_file_path and uploaded_file_name:
            logger.info(f"Starting file upload: {uploaded_file_name}")
            raw = self.hmdmRawFile(uploaded_file_path, uploaded_file_name, hmtoken)
            if raw.get("error"):
                return {"error": True, "message": f"Raw upload failed: {raw.get('message')}", "raw_text": raw.get("raw_text")}
            tmp_path = raw.get("serverPath")
            chosen_file_path = file_name or raw.get("name") or uploaded_file_name
            # Build body matching web app format
            body = {
                "tmpPath": tmp_path,
                "filePath": chosen_file_path,
                "devicePath": path_on_device or "",
                "description": description or "",
                "replaceVariables": bool(variable_content),
            }
            logger.info(f"Committing file with body: {json.dumps(body, indent=2)}")
            commit = self.hmdmUploadFile(body, hmtoken)
            if commit.get("error"):
                return {"error": True, "message": f"Commit failed: {commit.get('message')}", "raw_text": commit.get("raw_text")}
            raw_commit = commit.get("raw")

        elif external_url:
            logger.info(f"Adding external file from URL: {external_url}")
            chosen_file_path = file_name or (external_url.split('/')[-1] if external_url else None)
            # Build body for external URL matching web app format
            body = {
                "externalUrl": external_url,
                "filePath": chosen_file_path,
                "devicePath": path_on_device or "",
                "description": description or "",
                "replaceVariables": bool(variable_content),
                "external": True,
            }
            logger.info(f"External file body: {json.dumps(body, indent=2)}")
            commit = self.hmdmUploadFile(body, hmtoken)
            if commit.get("error"):
                return {"error": True, "message": f"External commit failed: {commit.get('message')}", "raw_text": commit.get("raw_text")}
            raw_commit = commit.get("raw")

        else:
            return {"error": True, "message": "Either a file or external URL must be provided"}

        if not raw_commit:
            return {"error": True, "message": "Empty response from server after commit"}

        f = raw_commit if isinstance(raw_commit, dict) else (raw_commit[0] if isinstance(raw_commit, list) and len(raw_commit) > 0 else {})
        upload_ms = f.get("uploadTime") or f.get("upload_time") or f.get("upload")
        upload_sec = None
        if isinstance(upload_ms, (int, float)):
            try:
                upload_sec = int(upload_ms) // 1000
            except Exception:
                upload_sec = None
        raw_size = f.get("size") or f.get("fileDetails", {}).get("size")
        size_mb = None
        if isinstance(raw_size, (int, float)):
            size_mb = round(raw_size / (1024 * 1024), 1)

        # Link configurations if requested
        try:
            file_id = f.get('id') or f.get('fileId') or (f.get('data', {}).get('id') if isinstance(f, dict) else None)
            if file_id and configuration_ids:
                cfg_res = self.hmdmFileConfiguration(file_id, configuration_ids, hmtoken)
                if cfg_res.get("error"):
                    logger.error(f"Configuration linking failed: {cfg_res}")
        except Exception as e:
            logger.error(f"Error while attempting to link configurations: {e}", exc_info=True)

        return {
            "id": f.get("id"),
            "filePath": f.get("filePath") or f.get("path") or f.get("url") or f.get("serverPath") or "",
            "description": f.get("description") or "",
            "size": size_mb,
            "uploadTime": upload_sec,
            "devicePath": f.get("devicePath") or f.get("device_path") or "",
            "external": bool(f.get("external")),
            "replaceVariables": bool(f.get("replaceVariables")),
        }

    def deleteFileById(self, file_id: int = None, filePath: str = None):
        """
        Delete a file in HMDM by id or filePath. Returns True on success.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour supprimer le fichier.")
            return False

        url = f"{self.BASE_URL}/private/web-ui-files/remove"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        body = {}
        if file_id is not None:
            body['id'] = file_id
        if filePath is not None:
            body['filePath'] = filePath
        if not body:
            logging.getLogger().error("No file id or filePath provided for deletion.")
            return False

        try:
            resp = requests.post(url, headers=headers, json=body)
            resp.raise_for_status()
            return True
        except Exception as e:
            logging.getLogger().error(f"Error deleting file: {e}")
            return False

    def deleteConfigurationById(self, config_id: int):
        """
        Delete a configuration in HMDM by its ID.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour supprimer la configuration.")
            return False

        url = f"{self.BASE_URL}/private/configurations/{config_id}"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}
        try:
            resp = requests.delete(url, headers=headers)
            resp.raise_for_status()
            logging.getLogger().info(f"Configuration {config_id} deleted successfully.")
            return True
        except Exception as e:
            logging.getLogger().error(f"Error deleting configuration {config_id}: {e}")
            return False

    def getList(self,hmtoken: str):
        url = f"{self.BASE_URL}/private/devices/search"
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}
        payload = {
            "limit": 100,
            "offset": 0
        }

        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            logging.getLogger().info(f"Liste of device is Ok: {resp.status_code}")

            raw_data = resp.json()
            
            if raw_data is None:
                logging.getLogger().error("La liste n'a pas été récupérée.")
                return None
            
            devices_items = raw_data.get("data", {}).get("devices", {}).get("items", [])

            deviceList = []
            for d in devices_items:
                device_data = {
                    "number": d.get("number", ""),
                    "description": d.get("description", ""),
                    "statusCode": d.get("statusCode", ""),
                    "configurationId": d.get("configurationId", ""),
                    "custom1": d.get("statusCode", ""),
                    "custom2": d.get("custom2", ""),
                    "custom3": d.get("custom3", ""),
                    "publicIp": d.get("publicIp", ""),
                    "imei": d.get("imei", ""),
                    "phone": d.get("phone", ""),
                    "serial": d.get("serial", ""),
                    "launcherVersion": d.get("launcherVersion", ""),
                    "mdmMode": d.get("mdmMode", ""),
                    "kioskMode": d.get("kioskMode", ""),
                    "androidVersion": d.get("androidVersion", "")
                }
                deviceList.append(device_data)

            return deviceList

        except Exception as e:
            logging.getLogger().error(f"une erreur s'est produite {e}")
            return []
            
    def givenNameDesc(self, name, desc):

        device_data = {
        # "id": 0,
        "number": name,
        "description": desc,
        "configurationId": 1  
        }
        
        form = self.createDevice(device_data)
        logging.getLogger().info(f"createDevice response: {form}")
        return form

    # Creating device on hmdm from ower front app
    def createDevice(self, device_data: dict):
        """ Create or update device using put requests in headwind mdmd"""
        
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour créer ou mettre à jour un appareil.")
            return None
        url =  f"{self.BASE_URL}/private/devices"
        

        headers = {"Content-Type": "application/json", "Authorization":f"Bearer {hmtoken}"}

        try:
            logging.getLogger().info(f"Payload sent to Headwind: {json.dumps(device_data, indent=2)}")
            resp = requests.put(url, json=device_data, headers=headers)
            resp.raise_for_status()
            logging.getLogger().info(f"The device has been created successfully")
            resp = resp.json()
            resp["message"] = resp.get("message") or ""
            resp["data"] = resp.get("data") or {}
            return resp
        except Exception as e:
            logging.getLogger().error(f"There is an error: device was not created: {e} ")


    def getHmdmConfigurationById(self, config_id: int, base_url: str = None):
        """
        Fetch full configuration data for a given configuration ID (requires auth).

        :param config_id: Configuration ID
        :param base_url: Optional base URL if HMDM is hosted elsewhere
        :return: Configuration JSON or None
        """

        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error(
                "Impossible d'authentifier pour récupérer la configuration."
            )
            return None

        url = f"{self.BASE_URL}/private/configurations/{config_id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hmtoken}"
        }
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            raw = resp.json()
            return raw.get('data', {}).get('qrCodeKey')
        except Exception as e:
            logging.getLogger().error(f"Error fetching configuration {config_id}: {e}")
            return None

    def deleteHmdmDeviceById(self, device_id: int):
        """
        Delete a device from HMDM by its ID.

        :param device_id: The device ID to delete.
        :return: True if deleted, False otherwise.
        """

        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error(
                "Impossible d'authentifier pour supprimer un appareil."
            )
            return False

        url = f"{self.BASE_URL}/private/devices/{device_id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hmtoken}"
        }

        try:
            resp = requests.delete(url, headers=headers)
            resp.raise_for_status()

            logging.getLogger().info(f"Device {device_id} deleted successfully.")
            return True

        except Exception as e:
            logging.getLogger().error(f"Error deleting device {device_id}: {e}")
            return False

    def deleteApplicationById(self, app_id: int):
        """
        Delete an application in HMDM by its ID.

        :param app_id: The application ID to delete.
        :return: True if deleted, False otherwise.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error(
                "Impossible d'authentifier pour supprimer l'application."
            )
            return False

        url = f"{self.BASE_URL}/private/applications/{app_id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hmtoken}"
        }

        try:
            resp = requests.delete(url, headers=headers)

            if resp.status_code not in (200, 204):
                logging.getLogger().warning(
                    f"Unexpected status deleting application {app_id}: {resp.status_code}"
                )

            try:
                if resp.headers.get("Content-Type", "").startswith("application/json"):
                    body = resp.json()
                    if isinstance(body, dict):
                        if str(body.get("status", "")).upper() in ("ERROR", "FAIL", "FAILED"):
                            logging.getLogger().error(
                                f"HMDM reported error deleting app {app_id}: {body}"
                            )
                            return False
                        if body.get("error") is True:
                            logging.getLogger().error(
                                f"HMDM reported error deleting app {app_id}: {body}"
                            )
                            return False
            except Exception:
                # Ignore JSON parsing errors
                pass
            try:
                apps = self.getHmdmApplications() or []
                still_exists = False
                for app in apps:
                    try:
                        if int(app.get("id")) == int(app_id):
                            still_exists = True
                            break
                    except Exception:
                        continue
                if still_exists:
                    logging.getLogger().warning(
                        f"Application {app_id} still present after delete; treating as failure."
                    )
                    return False
            except Exception as ve:
                logging.getLogger().warning(
                    f"Could not verify deletion of application {app_id}: {ve}"
                )

            logging.getLogger().info(f"Application {app_id} deleted successfully.")
            return True
        except Exception as e:
            logging.getLogger().error(f"Error deleting application {app_id}: {e}")
            return False

    def getHmdmGroups(self):
        """
        Fetch all groups from HMDM.
        
        :return: List of group objects with id and name
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible to authenticate to retrieve groups.")
            return []

        url = f"{self.BASE_URL}/private/groups/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            logging.getLogger().info(f"Groups fetched successfully")
            
            groups = data.get("data", [])
            return groups
        except Exception as e:
            logging.getLogger().error(f"Error fetching groups: {e}")
            return []

    def sendHmdmMessage(self, scope, device_number="", group_id="", configuration_id="", message=""):
        """
        Send a message to devices, groups, configurations, or all devices via HMDM.
        
        :param scope: One of: 'device', 'group', 'configuration', 'all_devices'
        :param device_number: Device number (for device scope)
        :param group_id: Group ID (for group scope)
        :param configuration_id: Configuration ID (for configuration scope)
        :param message: Message text to send
        :return: Response from HMDM or error dict
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible to authenticate to send message.")
            return {"status": "error", "message": "Authentication failed"}

        url = f"{self.BASE_URL}/plugins/messaging/private/send"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        # Build payload based on scope
        payload = {"message": message}

        if scope == "device":
            payload["scope"] = "DEVICE"
            payload["deviceNumber"] = device_number
        elif scope == "group":
            payload["scope"] = "GROUP"
            payload["groupId"] = int(group_id)
        elif scope == "configuration":
            payload["scope"] = "CONFIGURATION"
            payload["configurationId"] = int(configuration_id)
        elif scope == "all_devices":
            payload["scope"] = "ALL"
        else:
            return {"status": "error", "message": "Invalid scope"}

        try:
            logging.getLogger().info(f"Sending message via HMDM: {json.dumps(payload)}")
            resp = requests.post(url, json=payload, headers=headers)
            logging.getLogger().info(f"HMDM send message HTTP status: {resp.status_code}")
            logging.getLogger().info(f"HMDM send message raw response: {resp.text}")
            
            resp.raise_for_status()
            resp_json = resp.json()
            logging.getLogger().info(f"Message sent successfully: {json.dumps(resp_json)}")
            return resp_json
        except Exception as e:
            logging.getLogger().error(f"Error sending message: {e}")
            return {"status": "error", "message": str(e)}
        
    def sendHmdmPushMessage(self, scope, message_type="", payload="", device_number="", group_id="", configuration_id=""):
        """
        Send a push message to devices, groups, configurations, or all devices via HMDM.
        
        :param scope: One of: 'device', 'group', 'configuration', 'all_devices'
        :param message_type: Type of push message (e.g., configUpdated, runApp, etc.)
        :param payload: Payload/content of the push message
        :param device_number: Device number (for device scope)
        :param group_id: Group ID (for group scope)
        :param configuration_id: Configuration ID (for configuration scope)
        :return: Response from HMDM or error dict
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible to authenticate to send push message.")
            return {"status": "error", "message": "Authentication failed"}

        url = f"{self.BASE_URL}/plugins/push/private/send"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        # Build payload based on scope
        api_payload = {
            "messageType": message_type,
            "payload": payload
        }

        if scope == "device":
            api_payload["scope"] = "DEVICE"
            api_payload["deviceNumber"] = device_number
        elif scope == "group":
            api_payload["scope"] = "GROUP"
            api_payload["groupId"] = int(group_id)
        elif scope == "configuration":
            api_payload["scope"] = "CONFIGURATION"
            api_payload["configurationId"] = int(configuration_id)
        elif scope == "all_devices":
            api_payload["scope"] = "ALL"
        else:
            return {"status": "error", "message": "Invalid scope"}

        try:
            logging.getLogger().info(f"Sending push message via HMDM: {json.dumps(api_payload)}")
            resp = requests.post(url, json=api_payload, headers=headers)
            logging.getLogger().info(f"HMDM send push message HTTP status: {resp.status_code}")
            logging.getLogger().info(f"HMDM send push message raw response: {resp.text}")
            
            resp.raise_for_status()
            resp_json = resp.json()
            logging.getLogger().info(f"Push message sent successfully: {json.dumps(resp_json)}")
            return resp_json
        except Exception as e:
            logging.getLogger().error(f"Error sending push message: {e}")
            return {"status": "error", "message": str(e)}
    def getHmdmDeviceLogs(self, device_number="", package_id="", severity="-1", page_size=50, page_num=1):
        """
        Search device logs via HMDM.
        Endpoint: /plugins/devicelog/log/private/search
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Unable to authenticate for device logs search.")
            return []

        url = f"{self.BASE_URL}/plugins/devicelog/log/private/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        payload = {
            "pageSize": page_size,
            "pageNum": page_num
        }
        if device_number:
            payload["deviceFilter"] = device_number
        if package_id:
            payload["applicationFilter"] = package_id
        try:
            sev = int(severity)
        except Exception:
            sev = -1
        payload["severity"] = sev

        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data", {}).get("items", [])
            result = []
            for m in items:
                result.append({
                    "device": m.get("deviceNumber") or m.get("device"),
                    "time": (m.get("ts") or m.get("time") or 0) // 1000,
                    "package": m.get("package") or m.get("packageName") or "",
                    "severity": m.get("severity"),
                    "message": m.get("message") or m.get("text") or "",
                })
            return result
        except Exception as e:
            logging.getLogger().error(f"Error fetching device logs: {e}")
            return []

    def exportHmdmDeviceLogs(self, device_number="", app_id="", severity="-1"):
        """
        Export device logs via HMDM.
        Endpoint: /plugins/devicelog/log/private/search/export
        Returns dict with 'content' (binary) or error.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Unable to authenticate for device logs export.")
            return {"status": "error", "message": "Authentication failed"}

        url = f"{self.BASE_URL}/plugins/devicelog/log/private/search/export"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            sev = int(severity)
        except Exception:
            sev = -1

        payload = {
            "pageNum": 1,
            "pageSize": 50,
            "deviceFilter": device_number or "",
            "applicationFilter": app_id,
            "severity": sev,
            "messageFilter": "",
            "dateFrom": None,
            "dateTo": None,
            "sortValue": "createTime"
        }

        try:
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return {"status": "OK", "content": resp.content}
        except Exception as e:
            logging.getLogger().error(f"Error exporting device logs: {e}")
            return {"status": "error", "message": str(e)}

    def searchHmdmAppPackages(self, filter_text=""):
        """Autocomplete for app package names using /private/applications/autocomplete (POST body = filter string).
        Response: { 'status': 'OK', 'data': [ { 'id': int, 'name': str }, ... ] }
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Unable to authenticate for app package search.")
            return []

        url = f"{self.BASE_URL}/private/applications/autocomplete"
        headers = {"Content-Type": "text/plain", "Authorization": f"Bearer {hmtoken}"}
        body = filter_text or ""
        
        try:
            resp = requests.post(url, data=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            
            # Extract data array from response
            items = data.get("data", []) if isinstance(data, dict) else []
            
            packages = []
            f = (filter_text or "").lower()
            for item in items:
                if isinstance(item, dict):
                    pkg = item.get("name", "")
                    if pkg and f in pkg.lower():
                        packages.append({
                            "id": item.get("id"),
                            "name": pkg
                        })
                        if len(packages) >= 7:
                            break
            
            return packages
        except Exception as e:
            logging.getLogger().error(f"Error searching app packages: {e}")
            return []