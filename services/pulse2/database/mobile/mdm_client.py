# headwinn_api

import requests
import hashlib
import json
import logging


logger = logging.getLogger(__name__)

class HmdmApi:
    def __init__(self, base_url: str, login: str, password: str):
        
        """  
        initalizes the API object
        :param base_url: Base URL of the headwind MDM API
        :param login: Username for authentification
        :param password: Password for authentification will be hashed
        """
        self.base_url = base_url
        self.login = login
        self.password = password
        
        
    def hash_password(self, password: str) -> str:
            
            """" 
            Hash the password using md5 required by the hmdm api
            :param password: Plaintext password
            :return uppercase md5 hash string           
            """
            return hashlib.md5(password.encode()).hexdigest().upper()
            
    def authenticate(self) -> str:
        
        """ 
        Authentificate the user and return the JWT token if succcessful
        :return: JWT token as a string or None if authentification fails
        """   
        hashed_pwd = self.hash_password(self.password)
        url = f"{self.base_url}/public/jwt/login"
        auth_headers = {"Content-Type": "application/json"}
        data = {"login": self.login, "password": hashed_pwd}
        
        try:
            resp = requests.post(url, json=data, headers=auth_headers)
            resp.raise_for_status()
            return resp.json().get("id_token")
        except Exception as e:
            logger.error(f"[Hmdm] Auth Auth failed: {e}")
            return None

    def get_devices_from_hmdm(self) -> list:
        
        """ 
        Retrives the list of devices via the hmdm Api
        :return: list of device dict
        """
        
        token= self.authenticate()
        if not token:
            logger.error("[HMDM] No token recived after authentification")
            return []
        
        url = f"{self.base_url}/private/devices/search"
        
        request_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        payload = {"limit": 100, "offset":0}
        
        try:
            resp = requests.post(url, json=payload, headers=request_headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("devices", {}).get("items", [])
        except Exception as e:
            logger.error(f"[Hmdm] Failed to get devices: {e}")
        
      
    def create_hmdm_device_payload(self, name: str, desc:str)->dict:
        logger.error(f"[HMDM] Building payload for {name},{desc} ")
        
        return {
            "id": 0,
            "number": name,
            "description":desc,
            "configurationId": 1
        }
        
    def create_devices_on_hmdm(self, device_data: dict):
        
        """ 
        Creates or updates d device using the Hmdm api
        
        :param device_data: dict with device informatoin
        :return api respinse as dic or None if failed
        """ 
            
        token = self.authenticate()
        
        if not token:
            logger.error("Token not retrieved from authentication")
            return None 
        
        request_headers= {"Content-Type":"application/json", "Authorization":f"Bearer {token}"}
        url = f"{self.base_url}/private/devices"
        
        try:
            resp= requests.put(url, json=device_data, headers=request_headers)
            resp.raise_for_status()
            resp_json= resp.json()
            resp_json["message"]= resp_json.get("message", "")
            resp_json["data"]=resp_json.get("data",{})
            return resp_json
        except Exception as e :
            logger.error(f"[HMDM] Device creation failed: {e}")
            
            

            
         
