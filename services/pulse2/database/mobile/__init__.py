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

    def addHmdmDevice(self, name, configuration_id, description="", groups=None, imei="", phone="", device_id=None):
        """
        Create or update a device in HMDM.
        
        :param name: Device number/name (required)
        :param configuration_id: Configuration ID (required)
        :param description: Device description (optional)
        :param groups: List of group IDs (optional)
        :param imei: Device IMEI (optional)
        :param phone: Device phone number (optional)
        :param device_id: Device ID for updates (optional)
        :return: Response from HMDM or None on error
        """
        # Log all received parameters
        logging.getLogger().info(f"=== addHmdmDevice called ===")
        logging.getLogger().info(f"  name: {repr(name)}")
        logging.getLogger().info(f"  configuration_id: {repr(configuration_id)}")
        logging.getLogger().info(f"  description: {repr(description)}")
        logging.getLogger().info(f"  groups: {repr(groups)}")
        logging.getLogger().info(f"  imei: {repr(imei)}")
        logging.getLogger().info(f"  phone: {repr(phone)}")
        logging.getLogger().info(f"  device_id: {repr(device_id)}")
        
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour créer un appareil.")
            return None

        url = f"{self.BASE_URL}/private/devices"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        device_data = {
            "number": name,
            "configurationId": int(configuration_id)
        }
        logging.getLogger().info(f"Initial device_data: {device_data}")

        if device_id is not None and str(device_id).strip():
            device_data["id"] = int(device_id)
            logging.getLogger().info(f"Added device_id to payload: {device_id}")

        if description:
            device_data["description"] = description
            logging.getLogger().info(f"Added description to payload: {description}")
        
        if groups and isinstance(groups, list):
            device_data["groups"] = [{"id": int(g)} for g in groups if g]
            logging.getLogger().info(f"Added groups to payload: {device_data['groups']}")
        
        if imei:
            device_data["imei"] = imei
            logging.getLogger().info(f"Added imei to payload: {imei}")
        
        if phone:
            device_data["phone"] = phone
            logging.getLogger().info(f"Added phone to payload: {phone}")

        logging.getLogger().info(f"=== FINAL PAYLOAD ===")
        logging.getLogger().info(f"{json.dumps(device_data, indent=2)}")
        logging.getLogger().info(f"=== END PAYLOAD ===")

        try:
            resp = requests.put(url, json=device_data, headers=headers)
            logging.getLogger().info(f"HMDM device creation HTTP status: {resp.status_code}")
            logging.getLogger().info(f"HMDM device creation response: {resp.text}")
            resp.raise_for_status()
            
            resp_json = resp.json()
            resp_json["message"] = resp_json.get("message") or ""
            resp_json["data"] = resp_json.get("data") or {}
            
            logging.getLogger().info(f"Device '{name}' created successfully in HMDM.")
            return resp_json
        except Exception as e:
            logging.getLogger().error(f"Error creating device '{name}': {e}")
            return None
    
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
        
    def getHmdmConfigurationApplications(self, config_id: int):
        """
        Fetch applications linked to a specific configuration.

        :param config_id: Configuration ID
        :return: List of application dicts or [] on error
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer les applications de la configuration.")
            return []

        url = f"{self.BASE_URL}/private/configurations/applications/{config_id}"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            logging.getLogger().info(f"Applications for configuration {config_id} fetched successfully {resp.json()}")
            data = resp.json() or {}
            payload = data.get("data", data)
            # Some responses may nest under 'applications'
            if isinstance(payload, dict) and "applications" in payload:
                payload = payload.get("applications", [])
            return payload if isinstance(payload, list) else []
        except Exception as e:
            logging.getLogger().error(f"Error fetching applications for configuration {config_id}: {e}")
            return []    

    def getHmdmIcons(self):
        """
        Fetch the list of icons from HMDM.
        Returns a list of icon dicts.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Failed to authenticate when fetching icons.")
            return []

        url = f"{self.BASE_URL}/private/icons/search"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers, json={})
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "OK":
                logging.getLogger().info(f"Icons fetched successfully.")
                return data.get("data", [])
            else:
                logging.getLogger().error(f"Failed to fetch icons: {data}")
                return []
        except Exception as e:
            logging.getLogger().error(f"Failed to fetch icons: {e}")
            return []

    def addHmdmIcon(self, icon_data: dict):
        """
        Create an icon in HMDM.
        
        :param icon_data: Dict with 'name' (required), 'fileId' (required), and optionally 'fileName'
        :return: Response from HMDM or None on error
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Failed to authenticate when creating icon.")
            return None

        url = f"{self.BASE_URL}/private/icons"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        # Build base payload
        payload = {
            "name": icon_data.get("name", ""),
            "fileId": int(icon_data.get("fileId", 0)),
            "fileName": icon_data.get("fileName", "")
        }

        # If an id is provided, treat this as an update operation
        icon_id = icon_data.get("id") if isinstance(icon_data, dict) else None
        is_update = False
        try:
            if icon_id is not None and str(icon_id).strip() != "":
                payload["id"] = int(icon_id)
                is_update = True
        except Exception:
            # ignore invalid id, proceed as create
            is_update = False

        logging.getLogger().info(f"[mobile] addHmdmIcon payload (update={is_update}): {json.dumps(payload)}")

        try:
            # PUT is used for both create and update in HMDM API
            resp = requests.put(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            logging.getLogger().info(f"[mobile] addHmdmIcon response: {json.dumps(data)}")
            if data.get("status") == "OK":
                if is_update:
                    logging.getLogger().info(f"Icon (id={payload.get('id')}) updated successfully.")
                else:
                    logging.getLogger().info(f"Icon created successfully.")
                return data.get("data")
            else:
                action = "update" if is_update else "create"
                logging.getLogger().error(f"Failed to {action} icon: {data}")
                return None
        except Exception as e:
            action = "update" if is_update else "create"
            logging.getLogger().error(f"Failed to {action} icon: {e}")
            return None

    def deleteHmdmIconsById(self, id):
        """
        Delete an icon in HMDM by its ID.
        
        :param id: Icon ID to delete
        :return: True if deletion was successful, False otherwise
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Failed to authenticate when deleting icon.")
            return False

        url = f"{self.BASE_URL}/private/icons/{id}"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.delete(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            logging.getLogger().info(f"[mobile] deleteHmdmIconsById response: {json.dumps(data)}")
            if data.get("status") == "OK":
                logging.getLogger().info(f"Icon (id={id}) deleted successfully.")
                return True
            else:
                logging.getLogger().error(f"Failed to delete icon (id={id}): {data}")
                return False
        except Exception as e:
            logging.getLogger().error(f"Failed to delete icon (id={id}): {e}")
            return False

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

    def uploadFileToHmdm(self, file_path: str, file_name: str, mime_type: str = "application/octet-stream") -> dict:
        """
        Upload an APK/XAPK (or any file) to HMDM via /private/web-ui-files.

        Returns the file metadata (id, url, fileDetails…) sanitized for XML-RPC,
        or None on error.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logger.error("Unable to authenticate for file upload.")
            return None

        url = f"{self.BASE_URL}/private/web-ui-files"
        headers = {"Authorization": f"Bearer {hmtoken}"}

        try:
            with open(file_path, "rb") as fh:
                files = {"file": (file_name, fh, mime_type)}
                resp = requests.post(url, headers=headers, files=files)
            logger.info(f"Upload response status: {resp.status_code}")
            logger.info(f"Upload response body: {resp.text}")
            resp.raise_for_status()

            data = resp.json() if resp.text else {}
            if data.get("status") == "OK":
                payload = self._sanitize_for_xmlrpc(data.get("data", {}))
                return payload
            logger.error(f"HMDM returned error during upload: {data.get('message', 'Unknown error')}")
            return None
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error uploading file to HMDM: {e}", exc_info=True)
            return None
    
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
                    "id": d.get("id", ""),
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
                    "androidVersion": d.get("androidVersion", ""),
                    "groups": d.get("groups", [])
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

    def _strip_file_last_update(self, config_data: dict):
        """Remove large millisecond timestamps from files entries to avoid XML-RPC overflow."""
        try:
            files = config_data.get('files', []) if isinstance(config_data, dict) else []
            if isinstance(files, list):
                for file_item in files:
                    if isinstance(file_item, dict) and 'lastUpdate' in file_item:
                        del file_item['lastUpdate']
        except Exception:
            pass

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
            config_data = raw.get('data', {})

            # Remove fields with large integers that exceed XML-RPC limits
            self._strip_file_last_update(config_data)
            
            # Log the configuration for debugging
            logging.getLogger().info(f"Retrieved configuration {config_id}: {json.dumps(config_data, indent=2)}")
            return config_data
        except Exception as e:
            logging.getLogger().error(f"Error fetching configuration {config_id}: {e}")
            return None

    def updateHmdmConfiguration(self, config_data: dict):
        """
        Update an existing HMDM configuration by merging changes into the existing config.
        """
        if not isinstance(config_data, dict):
            logging.getLogger().error("config_data must be a dict")
            return None

        config_id = config_data.get("id") or config_data.get("configurationId")
        if not config_id:
            logging.getLogger().error("Configuration ID is required to update configuration.")
            return None

        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour mettre à jour la configuration.")
            return None

        # First, GET the existing configuration
        existing = self.getHmdmConfigurationById(config_id)
        if not existing:
            logging.getLogger().error(f"Could not fetch existing configuration {config_id}")
            return None

        # Merge user changes into existing config
        existing.update(config_data)

        # Ensure outgoing payload does not contain large integers in files
        self._strip_file_last_update(existing)

        url = f"{self.BASE_URL}/private/configurations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hmtoken}"
        }

        try:
            logging.getLogger().info(f"Updating HMDM configuration {config_id} with merged payload: {json.dumps(existing, indent=2)}")
            resp = requests.put(url, headers=headers, json=existing)
            resp.raise_for_status()
            data = resp.json()
            cleaned = data.get('data', data) or {}
            self._strip_file_last_update(cleaned)
            logging.getLogger().info(f"Configuration {config_id} updated successfully: {json.dumps(cleaned, indent=2)}")
            return cleaned
        except Exception as e:
            logging.getLogger().error(f"Error updating configuration {config_id}: {e}")
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
        :return: Dict { error: bool, message: str }
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour supprimer l'application.")
            return {"error": True, "message": "auth_failed"}

        url = f"{self.BASE_URL}/private/applications/{app_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hmtoken}"
        }

        try:
            resp = requests.delete(url, headers=headers)

            # Parse JSON body if present
            body = None
            try:
                if resp.headers.get("Content-Type", "").startswith("application/json"):
                    body = resp.json()
            except Exception:
                body = None

            # If HMDM returns an explicit error status
            if isinstance(body, dict):
                status_val = str(body.get("status", "")).upper()
                if status_val in ("ERROR", "FAIL", "FAILED") or body.get("error") is True:
                    msg = body.get("message") or body.get("error") or "error"
                    logging.getLogger().error(f"HMDM error deleting app {app_id}: {body}")
                    return {"error": True, "message": msg}

            # HTTP status check
            if resp.status_code not in (200, 204):
                logging.getLogger().warning(
                    f"Unexpected status deleting application {app_id}: {resp.status_code}"
                )
                return {"error": True, "message": f"http_{resp.status_code}"}

            # Verify that app is really gone
            try:
                apps = self.getHmdmApplications() or []
                for app in apps:
                    try:
                        if int(app.get("id")) == int(app_id):
                            logging.getLogger().warning(
                                f"Application {app_id} still present after delete; treating as failure."
                            )
                            return {"error": True, "message": "delete_verification_failed"}
                    except Exception:
                        continue
            except Exception as ve:
                logging.getLogger().warning(
                    f"Could not verify deletion of application {app_id}: {ve}"
                )

            logging.getLogger().info(f"Application {app_id} deleted successfully.")
            return {"error": False, "message": ""}
        except Exception as e:
            logging.getLogger().error(f"Error deleting application {app_id}: {e}")
            return {"error": True, "message": str(e)}

    def getApplicationVersions(self, app_id: int):
        """
        Get the list of versions for a specified application.
        
        :param app_id: Application ID
        :return: List of version dicts or empty list on error
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Unable to authenticate to retrieve application versions.")
            return []

        url = f"{self.BASE_URL}/private/applications/{app_id}/versions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            logging.getLogger().info(f"Application versions fetched successfully for app {app_id}")
            
            versions = data.get("data", [])
            return versions
        except Exception as e:
            logging.getLogger().error(f"Error fetching application versions for app {app_id}: {e}")
            return []

    def getConfigurationNames(self):
        """
        Get the list of available configuration names.

        :return: List of dicts with keys id and name
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Unable to authenticate to retrieve configuration names.")
            return []

        url = f"{self.BASE_URL}/private/configurations/list"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            raw_items = data if isinstance(data, list) else data.get("data") or data.get("configurations") or []

            configs = []
            for item in raw_items:
                if isinstance(item, dict):
                    cid = item.get("id") or item.get("configurationId")
                    cname = item.get("name") or item.get("title") or item.get("configurationName")
                    configs.append({"id": cid, "name": cname})
                else:
                    configs.append({"id": None, "name": str(item)})

            logging.getLogger().info("Configuration names fetched successfully")
            return configs
        except Exception as e:
            logging.getLogger().error(f"Error fetching configuration names: {e}")
            return []

    def updateApplicationConfigurations(self, app_id: int, configuration_id: int, configuration_name: str = None):
        """
        Attach a configuration to an application.

        :param app_id: Application ID
        :param configuration_id: Configuration ID to attach
        :param configuration_name: Optional configuration name
        :return: dict result from HMDM
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Unable to authenticate to update application configurations.")
            return {"status": "ERROR", "message": "auth_failed"}

        url = f"{self.BASE_URL}/private/applications/configurations"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        config_entry = {
            "applicationId": app_id,
            "configurationId": configuration_id,
            "action": 0,
        }
        if configuration_name:
            config_entry["configurationName"] = configuration_name

        payload = {
            "applicationId": app_id,
            "configurations": [config_entry],
        }

        try:
            resp = requests.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            logging.getLogger().info(
                f"Configuration {configuration_id} attached to application {app_id}"
            )
            return data if isinstance(data, dict) else {"status": "OK"}
        except Exception as e:
            logging.getLogger().error(
                f"Error updating configurations for application {app_id} with configuration {configuration_id}: {e}"
            )
            return {"status": "ERROR", "message": str(e)}

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

    def addHmdmGroup(self, name, group_id=None, customer_id=None, common=None):
        """
        Create or update a group in HMDM.
        
        :param name: Group name (required)
        :param group_id: Group ID for updates (optional)
        :param customer_id: Customer ID (optional)
        :param common: Common flag (optional)
        :return: Response from HMDM or None on error
        """
        logging.getLogger().info(
            f"addHmdmGroup called with name={name!r}, group_id={group_id}, customer_id={customer_id}, common={common}"
        )
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible to authenticate to create/update group.")
            return None

        url = f"{self.BASE_URL}/private/groups"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {hmtoken}"}

        # Build payload - HMDM API expects id/name and may include customer/common
        group_data = {
            "name": name
        }
        
        if group_id is not None and str(group_id).strip():
            group_data["id"] = int(group_id)

        if customer_id is not None and str(customer_id).strip():
            group_data["customerId"] = int(customer_id)

        if common is not None:
            common_value = common
            if isinstance(common_value, str):
                common_value = common_value.lower() not in ("false", "0", "")
            group_data["common"] = bool(common_value)

        try:
            action = "Updating" if group_id else "Creating"
            logging.getLogger().info(f"{action} group in HMDM: {json.dumps(group_data, indent=2)}")
            resp = requests.put(url, json=group_data, headers=headers)
            logging.getLogger().info(f"HMDM group {action.lower()} HTTP status: {resp.status_code}")
            logging.getLogger().info(f"HMDM group {action.lower()} response: {resp.text}")
            resp.raise_for_status()
            
            resp_json = resp.json()
            resp_json["message"] = resp_json.get("message") or ""
            resp_json["data"] = resp_json.get("data") or {}
            
            logging.getLogger().info(f"Group '{name}' {action.lower()}d successfully in HMDM.")
            return resp_json
        except Exception as e:
            action = "updating" if group_id else "creating"
            logging.getLogger().error(f"Error {action} group '{name}': {e} {group_data}")
            return None

    def deleteHmdmGroupById(self, group_id):
        """
        Delete a group from HMDM by its ID.

        :param group_id: The group ID to delete.
        :return: True if deleted, False otherwise.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible to authenticate to delete group.")
            return False

        url = f"{self.BASE_URL}/private/groups/{group_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hmtoken}"
        }

        try:
            resp = requests.delete(url, headers=headers)
            resp.raise_for_status()

            logging.getLogger().info(f"Group {group_id} deleted successfully.")
            return True

        except Exception as e:
            logging.getLogger().error(f"Error deleting group {group_id}: {e}")
            return False

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

    def addHmdmApplication(self, app_data: dict):
        """
        Create or update an application in HMDM, with icon upload support.

        If app_data contains 'icon_upload_path' and 'icon_upload_name', upload the icon
        to HMDM and set the icon filename in the payload.
        """
        hmtoken = self.authenticate()
        if hmtoken is None:
            logging.getLogger().error("Impossible d'authentifier pour ajouter/modifier l'application.")
            return None

        # Icon uploads are no longer handled server-side. If callers still provide
        # icon_upload_* fields they will be ignored. Use `iconText` or `showIcon`
        # flags in the payload instead.

        # Build payload strictly per type, only relevant fields
        app_type = app_data.get("type", "")
        payload = {
            "type": app_type,
            "name": app_data.get("name", ""),
        }

        # If ID is provided, include it for update operation
        if app_data.get("id"):
            payload["id"] = app_data["id"]

        if app_type == "app":
            if app_data.get("pkg"):
                payload["pkg"] = app_data["pkg"]
            if app_data.get("version"):
                payload["version"] = app_data["version"]
            # System flag: only send if provided
            if app_data.get("system"):
                payload["system"] = True
            
            if app_data.get("arch"):
                payload["arch"] = app_data["arch"]
            
            if app_data.get("url"):
                payload["url"] = app_data["url"]

            # Include filePath key when provided by caller (even if None)
            # Some HMDM endpoints expect the key to exist (can be null).
            if "filePath" in app_data:
                payload["filePath"] = app_data.get("filePath")
            
            # Run options
            if app_data.get("runAfterInstall"):
                payload["runAfterInstall"] = True
            if app_data.get("runAtBoot"):
                payload["runAtBoot"] = True
            # Optional versionCode from APK metadata
            if app_data.get("versionCode"):
                payload["versionCode"] = app_data["versionCode"]
            # If provided, include usedVersionId to keep HMDM version tracking consistent
            # Preserve usedVersionId and mirror it to latestVersion to match HMDM UI payload
            if app_data.get("usedVersionId") is not None:
                try:
                    uvid = int(app_data.get("usedVersionId"))
                    payload["usedVersionId"] = uvid
                    payload["latestVersion"] = uvid
                except Exception:
                    payload["usedVersionId"] = app_data.get("usedVersionId")
                    payload["latestVersion"] = app_data.get("usedVersionId")

        elif app_type == "web":
            if app_data.get("url"):
                payload["url"] = app_data["url"]
            if app_data.get("useKiosk"):
                payload["useKiosk"] = True

        elif app_type == "intent":
            if app_data.get("action"):
                payload["intent"] = app_data["action"]

        # Common optional icon fields
        if app_data.get("iconText"):
            payload["iconText"] = app_data["iconText"]
        if app_data.get("showIcon"):
            payload["showIcon"] = True
        icon_id = app_data.get("iconId")
        if icon_id:
            payload["iconId"] = icon_id

        # Select endpoint based on app type
        endpoint = "web" if app_type == "web" else "android"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hmtoken}",
        }

        # For Android apps, validate package first (required by HMDM)
        if app_type == "app" and app_data.get("pkg"):
            validate_url = f"{self.BASE_URL}/private/applications/validatePkg"
            try:
                logging.getLogger().info(f"Validating package with full payload")
                validate_resp = requests.put(validate_url, json=payload, headers=headers)
                logging.getLogger().info(f"Validation HTTP status: {validate_resp.status_code}")
                logging.getLogger().info(f"Validation response: {validate_resp.text}")
                if validate_resp.status_code != 200:
                    logging.getLogger().error(f"Package validation failed: {validate_resp.text}")
                    return None
            except Exception as e:
                logging.getLogger().error(f"Error validating package: {e}")
                return None

        url = f"{self.BASE_URL}/private/applications/{endpoint}"

        try:
            logging.getLogger().info(f"Sending application payload to HMDM: {json.dumps(payload)}")
            resp = requests.put(url, json=payload, headers=headers)
            logging.getLogger().info(f"HMDM HTTP status: {resp.status_code}")
            logging.getLogger().info(f"HMDM raw response: {resp.text}")
            resp.raise_for_status()
            try:
                resp_json = resp.json()
            except Exception:
                logging.getLogger().error("Failed to decode HMDM response as JSON")
                return None

            logging.getLogger().info(f"HMDM response: {json.dumps(resp_json)}")
            if resp_json.get("status") == "OK":
                resp_json["message"] = resp_json.get("message") or ""
                resp_json["data"] = resp_json.get("data") or {}
                logging.getLogger().info("Application added/updated successfully in HMDM.")
                return resp_json
            else:
                logging.getLogger().error(f"HMDM returned error: {resp_json.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            logging.getLogger().error(f"Error adding/updating application: {e}")
            return None   

    def _sanitize_for_xmlrpc(self, obj):
        """Recursively cast big ints to strings to avoid XML-RPC overflow."""
        limit = 2**31 - 1
        if isinstance(obj, dict):
            return {k: self._sanitize_for_xmlrpc(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._sanitize_for_xmlrpc(v) for v in obj]
        if isinstance(obj, int) and (obj > limit or obj < -limit):
            return str(obj)
        return obj

    def uploadWebUiFiles(self, file_path: str, file_name: str, mime_type: str = "application/octet-stream"):
        """
        Upload a file to HMDM via /private/web-ui-files.
        
        Returns sanitized HMDM response dict containing serverPath, fileDetails, etc., or error dict.
        """
        logger.info(f"[uploadWebUiFiles] === START ===")
        logger.info(f"[uploadWebUiFiles] file_path: {file_path}")
        logger.info(f"[uploadWebUiFiles] file_name: {file_name}")
        logger.info(f"[uploadWebUiFiles] mime_type: {mime_type}")
        
        hmtoken = self.authenticate()
        if hmtoken is None:
            logger.error("[uploadWebUiFiles] Unable to authenticate.")
            return {"status": "error", "message": "Authentication failed"}
        
        logger.info("[uploadWebUiFiles] Authentication successful")

        url = f"{self.BASE_URL}/private/web-ui-files"
        headers = {"Authorization": f"Bearer {hmtoken}"}
        logger.info(f"[uploadWebUiFiles] Target URL: {url}")

        try:
            logger.info(f"[uploadWebUiFiles] Sending multipart request with file")
            with open(file_path, "rb") as fh:
                files = {"file": (file_name, fh, mime_type)}
                logger.info(f"[uploadWebUiFiles] File opened: {file_name} (MIME: {mime_type})")
                resp = requests.post(url, headers=headers, files=files)

            logger.info(f"[uploadWebUiFiles] HTTP status code: {resp.status_code}")
            logger.info(f"[uploadWebUiFiles] Response headers: {dict(resp.headers)}")
            logger.info(f"[uploadWebUiFiles] Response body: {resp.text}")
            
            resp.raise_for_status()
            logger.info(f"[uploadWebUiFiles] HTTP request successful")

            resp_json = resp.json() if resp.text else {"status": "OK", "data": {}}
            logger.info(f"[uploadWebUiFiles] Response JSON before sanitization: {json.dumps(resp_json, indent=2)}")
            
            resp_json = self._sanitize_for_xmlrpc(resp_json)
            logger.info(f"[uploadWebUiFiles] Response JSON after sanitization: {json.dumps(resp_json, indent=2)}")

            if resp_json.get("status") == "OK":
                logger.info(f"[uploadWebUiFiles] === SUCCESS === File uploaded")
                return resp_json
            
            logger.error(f"[uploadWebUiFiles] Status is not OK: {resp_json.get('status')}, message: {resp_json.get('message')}")
            return {"status": "error", "message": resp_json.get("message", "Unknown error"), "raw": resp_json}

        except FileNotFoundError:
            logger.error(f"[uploadWebUiFiles] File not found: {file_path}")
            return {"status": "error", "message": "File not found"}
        except Exception as e:
            logger.error(f"[uploadWebUiFiles] Exception occurred: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
