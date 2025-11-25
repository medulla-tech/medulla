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
    # Headwind REST API base (consider moving to config)
    BASE_URL = "http://hba.medulla-tech.io/hmdm/rest"
    login = "admin"
    password = "HbaHmdm!"


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
#
#     def activate(self, config):
#         if self.is_activated:
#             return None
#         self.config = config
#         self.db = create_engine(self.makeConnectionPath(
#         ), pool_recycle=self.config.dbpoolrecycle, pool_size=self.config.dbpoolsize)
#         print(self.makeConnectionPath())
#         if not self.db_check():
#             return False
#         self.metadata = MetaData(self.db)
#         if not self.initMappersCatchException():
#             self.session = None
#             return False
#         self.metadata.create_all()
#         self.is_activated = True
#         result = self.db.execute(
#             "SELECT * FROM mobile.version limit 1;")
#         re = [element.Number for element in result]
#         return True
#
#     def initMappers(self):
#         return

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

        # Convert incoming name/description to backend payload

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
    
    # récupération de laliste des devices from hmdm 
    def getHmdmDevices(self):
        auth = self.authenticate()
        if auth is None:
            logging.getLogger().error("Impossible d'authentifier pour récupérer la liste des appareils.")
            return []
        return self.getList(auth)

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
            resp.raise_for_status()
            logging.getLogger().info(f"Application {app_id} deleted successfully.")
            return True
        except Exception as e:
            logging.getLogger().error(f"Error deleting application {app_id}: {e}")
            return False
