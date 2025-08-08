# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

from mmc.plugins.admin.config import AdminConfig

# import pour la database
from pulse2.database.admin import AdminDatabase
from mmc.plugins.updates import get_machine_count_by_entity
import logging
import requests
import json
import traceback
import base64
import random
import string
import uuid

VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


class GLPIClient:
    """
    A client class to interact with the GLPI API.

    This class provides methods to initialize a session, manage users, profiles, and entities,
    and perform various operations such as creating, updating, and deleting entities and users.

    Functions:
    - __init__(self, app_token, url_base, user_token): Initializes the GLPI client with tokens and base URL.
    - init_session(self): Initializes a session with the GLPI API.
    - kill_session(self): Terminates the current session.
    - get_list(self, type, is_recursive=False): Retrieves a list of users, profiles, or entities.
    - get_user_info(self): Retrieves information about the active user profile.
    - ## change_user_profile todo delete et recreate profile pour user voir delete_profile_from_user et add_profile_to_user
    - create_entity_under_custom_parent(self, parent_entity_id, name): Creates an entity under a specified parent.
    - create_user(self, name_user, pwd, entities_id=None, realname=None, firstname=None): Creates a new user.
    - update_entity(self, entity_id, item_name, new_value): Updates an entity with new values.
    - update_user(self, user_id, item_name, new_value): Updates a user with new values.
    - add_profile_to_user(self, user_id, profile_id, entities_id, is_recursive=0, is_dynamic=0, is_default_profile=0): Adds a profile to a user.
    - delete_profile_from_user(self, user_id, profile_id): Deletes a profile from a user.
    """

    def __init__(self, url_base, app_token, user_token=None, login=None, password=None):
        """
        Initializes the GLPI client with the necessary tokens and base URL.

        Args:
            url_base (str): The base URL for the GLPI API.
            app_token (str): The application token for API authentication.
            user_token (str, optional): The user token for API authentication.
            login (str, optional): The login for basic authentication.
            password (str, optional): The password for basic authentication.
        """
        self.URL_BASE = url_base
        self.APP_TOKEN = app_token
        self.USER_TOKEN = user_token
        self.LOGIN = login
        self.PASSWORD = password
        self.SESSION_TOKEN = None

        if user_token:
            self.auth_method = "user_token"
        elif login and password:
            self.auth_method = "basic"
        else:
            raise Exception("No valid authentication method provided.")

    def init_session(self):
        """
        Initializes a session with the GLPI API.

        Raises:
            Exception: If session initialization fails.
        """
        headers = {
            "App-Token": self.APP_TOKEN,
        }

        if self.auth_method == "user_token":
            headers["Authorization"] = f"user_token {self.USER_TOKEN}"
        elif self.auth_method == "basic":
            credentials = f"{self.LOGIN}:{self.PASSWORD}"
            encoded_credentials = base64.b64encode(
                credentials.encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {encoded_credentials}"

        response = requests.get(
            f"{self.URL_BASE}/initSession", headers=headers)

        if response.status_code == 200:
            data = response.json()
            self.SESSION_TOKEN = data.get('session_token')
            if not self.SESSION_TOKEN:
                raise Exception("Session initialization failed.")
            print(f"Session initialized (token: {self.SESSION_TOKEN})")
            print(json.dumps(data, indent=4))
        else:
            response.raise_for_status()

    def generate_token(self, length=32):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    # def __init__(self, app_token, url_base, user_token):
    #     """
    #     Initializes the GLPI client with the necessary tokens and base URL.
    #
    #     Args:
    #         app_token (str): The application token for API authentication.
    #         url_base (str): The base URL for the GLPI API.
    #         user_token (str): The user token for API authentication.
    #     """
    #     self.APP_TOKEN = app_token
    #     self.URL_BASE = url_base
    #     self.USER_TOKEN = user_token
    #     self.SESSION_TOKEN = None
    #     self.users = []
    #     self.profiles = []
    #     self.entities = []
    #
    # def init_session(self):
    #     """
    #     Initializes a session with the GLPI API.
    #
    #     Raises:
    #         Exception: If session initialization fails.
    #     """
    #     logger.info("[*] Initialisation de la session...")
    #     headers = {
    #         "App-Token": self.APP_TOKEN,
    #         "Authorization": f"user_token {self.USER_TOKEN}"
    #     }
    #     response = requests.get(f"{self.URL_BASE}/initSession", headers=headers)
    #
    #     if response.status_code == 200:
    #         data = response.json()
    #         self.SESSION_TOKEN = data.get('session_token')
    #         if not self.SESSION_TOKEN:
    #             logger.error("[!] Échec de l'initialisation de la session")
    #             raise Exception("[!] Échec de l'initialisation de la session")
    #         logger.info(f"[+] Session initialisée (token : {self.SESSION_TOKEN})")
    #         logger.debug(json.dumps(data, indent=4))
    #     else:
    #         response.raise_for_status()

    def kill_session(self):
        """
        Terminates the current session.
        """
        if not self.SESSION_TOKEN:
            logger.warning("Aucune session active à terminer.")
            return

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }
        response = requests.get(
            f"{self.URL_BASE}/killSession", headers=headers)

        if response.status_code == 200:
            logger.info("[*] Session terminée")
            self.SESSION_TOKEN = None
            logger.debug(json.dumps(response.json(), indent=4))
        else:
            response.raise_for_status()

    def get_list(self, type, is_recursive=False):
        """
        Retrieves a list of users, profiles, or entities.

        Args:
            type (str): The type of list to retrieve ('users', 'profiles', or 'entities').
            is_recursive (bool): Whether to retrieve entities recursively.

        Returns:
            list: The list of items retrieved.

        Raises:
            ValueError: If the type is invalid.
            Exception: If the session is not initialized.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            raise Exception(
                "Session non initialisée. Veuillez initialiser la session.")

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }

        if type == "users":
            endpoint = "User"
        elif type == "profiles":
            endpoint = "Profile"
        elif type == "entities":
            endpoint = f"getMyEntities?is_recursive={str(is_recursive).lower()}"
        else:
            logger.error(
                "Type invalide. Utilisez 'users', 'profiles', ou 'entities'.")
            raise ValueError(
                "Type invalide. Utilisez 'users', 'profiles', ou 'entities'.")

        response = requests.get(f"{self.URL_BASE}/{endpoint}", headers=headers)

        if response.status_code == 200:
            data = response.json()
            if type == "users":
                users_list = data if isinstance(data, list) else data.get('users', [])
                filtered = []
                for user in users_list:
                    name = user.get("name", "")
                    if (
                        name == "glpi-system"
                        or name.startswith("Plugin_")
                    ):
                        continue

                    entity_info = self.get_entity_info(user.get("entities_id"))
                    entity_name = entity_info.get("name", "") if entity_info and isinstance(entity_info, dict) else ""
                    filtered.append({
                        "id": user.get("id"),
                        "name": user.get("name") or "",
                        "realname": user.get("realname") or "",
                        "is_active": user.get("is_active"),
                        "profiles_id": user.get("profiles_id"),
                        "last_login": user.get("last_login") or "",
                        "date_mod": user.get("date_mod") or "",
                        "date_creation": user.get("date_creation") or "",
                        "entities_id": user.get("entities_id"),
                        "entities_name": entity_name
                    })
                return filtered
            elif type == "profiles":
                self.profiles = data
                return data
            elif type == "entities":
                return data.get('myentities', [])
        else:
            response.raise_for_status()

    def get_user_info(self, user_id=None):
        """
        Retrieves information about the active user profile or a specific user if user_id is provided.

        Args:
            user_id (int, optional): The ID of the user to retrieve information for. If not provided,
                                information about the active profile is retrieved.

        Returns:
            dict: Information about the active profile or the specified user.

        Raises:
            Exception: If the session is not initialized.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            raise Exception(
                "Session non initialisée. Veuillez initialiser la session.")

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }

        if user_id is not None:
            # If user_id is provided, retrieve information for that specific user
            response = requests.get(
                f"{self.URL_BASE}/User/{user_id}", headers=headers)
        else:
            # Otherwise, retrieve information about the active profile
            response = requests.get(
                f"{self.URL_BASE}/getActiveProfile", headers=headers)

        if response.status_code == 200:
            data = response.json()
            if user_id is not None:
                if isinstance(data, list):
                    data = data[0] if data else {}
                # Extract user-specific information
                user_name = data.get('name', '')
                user_id = data.get('id', '')
                user_entity_name = data.get('entities', [{}])[0].get('name', '') if data.get('entities') else ''
                user_entity_id = data.get('entities', [{}])[0].get('id', '') if data.get('entities') else ''
                user_entity_recursif = data.get('entities', [{}])[0].get('is_recursive', False) if data.get('entities') else False

                # logger.info("******************************************************")
                # logger.info(type(data))a
                # logger.debug(json.dumps(data, indent=4))
                # logger.info(type(data))
                # logger.info("******************************************************")

                return {
                    "user_id": data.get('id') or '',
                    "name": data.get('name') or '',
                    "realname": data.get('realname') or '',
                    "firstname": data.get('firstname') or '',
                    "email": data.get('email') or '',
                    "is_active": data.get('is_active') if data.get('is_active') is not None else '',
                    "profiles_id": data.get('profiles_id') if data.get('profiles_id') is not None else '',
                    "last_login": data.get('last_login') or '',
                    "date_mod": data.get('date_mod') or '',
                    "date_creation": data.get('date_creation') or '',
                    "phone": data.get('phone') or '',
                    "entities": data.get('entities') if data.get('entities') is not None else [],
                }
            else:
                # Extract active profile information
                profil_name = data['active_profile']['name']
                profil_id = data['active_profile']['id']
                profil_entity_name = data['active_profile']['entities'][0]['name']
                profil_entity_id = data['active_profile']['entities'][0]['id']
                profil_entity_recursif = data['active_profile']['entities'][0]['is_recursive']

                logger.info(
                    "******************************************************")
                logger.debug(json.dumps(data, indent=4))
                logger.info(
                    "******************************************************")

                return {
                    "profil_name": profil_name,
                    "profil_id": profil_id,
                    "profil_entity_name": profil_entity_name,
                    "profil_entity_id": profil_entity_id,
                    "profil_entity_recursif": profil_entity_recursif
                }
        else:
            response.raise_for_status()

    def get_users_count_by_entity(self, entity_id):
        """
        Retourne uniquement les id et noms des utilisateurs d'une entité (hors glpi-system et Plugin_).
        """
        if not self.SESSION_TOKEN:
            logger.error("Session non initialisée. Veuillez initialiser la session.")
            raise Exception("Session non initialisée. Veuillez initialiser la session.")

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }

        params = {
            'criteria[0][field]': 80,
            'criteria[0][searchtype]': 'equals',
            'criteria[0][value]': entity_id,
            'range': '0-999',
            'forcedisplay[0]': '2',
            'forcedisplay[1]': '1'
        }

        response = requests.get(
            f"{self.URL_BASE}/search/User",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        users = response.json().get('data', [])

        result = []
        for user in users:
            name = user.get('1', '')
            if not name or name == 'glpi-system' or name.startswith('Plugin_'):
                continue
            result.append({
                'id': user.get('2', ''),
                'name': name
            })
        return result

    def get_entity_info(self, entity_id):
        """
        Recovers the info from a GLPI entity by his ID.

        Args:
            Entity_ID (int | str): the ID of the entity.

        Returns:
            Dict: Info of the entity (name, parent, etc.) or {} if not found.
        """
        if not self.SESSION_TOKEN:
            logger.error("Session non initialisée.")
            raise Exception("Session non initialisée. Veuillez initialiser la session.")

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }
        response = requests.get(f"{self.URL_BASE}/Entity/{entity_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Entité {entity_id} introuvable.")
            return {}
        else:
            response.raise_for_status()

    # def get_user_info(self):
    #     """
    #     Retrieves information about the active user profile.
    #
    #     Returns:
    #         dict: Information about the active profile.
    #
    #     Raises:
    #         Exception: If the session is not initialized.
    #     """
    #     if not self.SESSION_TOKEN:
    #         logger.error("Session non initialisée. Veuillez initialiser la session.")
    #         raise Exception("Session non initialisée. Veuillez initialiser la session.")
    #
    #     headers = {
    #         "App-Token": self.APP_TOKEN,
    #         "Session-Token": self.SESSION_TOKEN
    #     }
    #
    #     response = requests.get(f"{self.URL_BASE}/getActiveProfile", headers=headers)
    #
    #     if response.status_code == 200:
    #         data = response.json()
    #         profil_name = data['active_profile']['name']
    #         profil_id = data['active_profile']['id']
    #         profil_entity_name = data['active_profile']['entities'][0]['name']
    #         profil_entity_id = data['active_profile']['entities'][0]['id']
    #         profil_entity_recursif = data['active_profile']['entities'][0]['is_recursive']
    #
    #         logger.info("******************************************************")
    #         logger.debug(json.dumps(data, indent=4))
    #         logger.info("******************************************************")
    #
    #         return {
    #             "profil_name": profil_name,
    #             "profil_id": profil_id,
    #             "profil_entity_name": profil_entity_name,
    #             "profil_entity_id": profil_entity_id,
    #             "profil_entity_recursif": profil_entity_recursif
    #         }
    #     else:
    #         response.raise_for_status()
    def get_profile_name(self, profile_id):
        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }
        response = requests.get(
            f"{self.URL_BASE}/Profile/{profile_id}", headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("name", "")

    def create_entity_under_custom_parent(self, parent_entity_id, name, tagvalue=None):
        """
        Creates an entity under a specified parent.

        Args:
            parent_entity_id (int): The ID of the parent entity.
            name (str): The name of the new entity.

        Returns:
            int: The ID of the newly created entity.

        Raises:
            Exception: If the session is not initialized or if creation fails.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            raise Exception(
                "Session non initialisée. Veuillez initialiser la session.")

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN,
            "Content-Type": "application/json"
        }

        data = {
            "input": {
                "name": name,
                "entities_id": parent_entity_id

            }
        }
        if tagvalue:
            data['input']['tag'] = tagvalue

        response = requests.post(
            f"{self.URL_BASE}/Entity",
            headers=headers,
            data=json.dumps(data)
        )

        if response.status_code > 300:
            logger.error(f"error{response.status_code} creation entity'{response.text}'")
            response.raise_for_status()

        new_id = response.json().get('id')
        if new_id is None:
            logger.error(
                "[!] Échec de la création — droits insuffisants ou autre erreur ?")
            raise Exception(
                "[!] Échec de la création — droits insuffisants ou autre erreur ?")

        logger.info(
            f"[+] Entité '{name}' créée avec ID : {new_id} sous parent ID {parent_entity_id}")
        return new_id

    def create_user(self,
                    name_user,
                    pwd,
                    entities_id=None,
                    realname=None,
                    firstname=None,
                    profiles_id=None):
        """
        Creates a new user.

        Args:
            name_user (str): The username.
            pwd (str): The password.
            entities_id (int, optional): The ID of the entity.
            realname (str, optional): The real name of the user.
            firstname (str, optional): The first name of the user.

        Returns:
            int: The ID of the newly created user.

        Raises:
            Exception: If the session is not initialized or if creation fails.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            raise Exception(
                "Session non initialisée. Veuillez initialiser la session.")

        logger.info("Veuillez confirmer les informations suivantes :")
        logger.info(f"Nom d'utilisateur : {name_user}")
        logger.info("Mot de passe : ******")
        logger.info(f"Nom réel : {realname}")
        logger.info(f"Prénom : {firstname}")
        logger.info(f"ID de l'entité : {entities_id}")

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN,
            "Content-Type": "application/json"
        }

        data = {
            "input": {
                "name": name_user,
                "password": pwd,
                "password2": pwd,
                "realname": realname,
                "firstname": firstname,
                "language": "fr_FR",
                "is_active": 1,
                "entities_id": entities_id,
                "reset_personal_token": True,
                "reset_api_token": True,
            }
        }

        if profiles_id:
            data['input']['profiles_id'] = profiles_id

        response = requests.post(
            f"{self.URL_BASE}/User",
            headers=headers,
            data=json.dumps(data)
        )

        if response.status_code > 300 or "ERROR_GLPI_ADD" in response.text:
            logger.error(f"error{response.status_code} creation '{response.text}'")
            response.raise_for_status()
            logger.error("[!] Échec de la création de l'utilisateur")
            raise Exception("[!] Échec de la création de l'utilisateur")

        user_id = response.json().get('id')
        logger.info(
            f"[+] Utilisateur créé avec succès. ID de l'utilisateur : {user_id}")

        #
        #
        # # Réinitialisation du token personnel
        # response_token = requests.post(
        #     f"{self.URL_BASE}/User/{user_id}/_reset_personal_token/1",
        #     headers=headers
        # )
        # if response_token.status_code >= 300:
        #     logger.warning("[!] Échec de la réinitialisation du token personnel.")
        #
        # # Réinitialisation du token API
        # response_api = requests.post(
        #     f"{self.URL_BASE}/User/{user_id}/_reset_api_token/1",
        #     headers=headers
        # )
        # if response_api.status_code >= 300:
        #     logger.warning("[!] Échec de la réinitialisation du token API.")

        return user_id

    def update_entity(self, entity_id, item_name, new_value, parent_id):
        """
        Updates an entity with new values.

        Args:
            entity_id (int): The ID of the entity.
            item_name (str): The name of the item to update.
            new_value: The new value for the item.

        Returns:
            int: 1 if the update was successful, 0 otherwise.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            return 0

        if not entity_id or not item_name or not new_value:
            logger.error(
                "[!] Usage: update_entity <entity_id> <item_name> <new_value>")
            return 0

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN,
            "Content-Type": "application/json"
        }

        data = {
            "input": {
                item_name: new_value,
                "id": entity_id,
                "entities_id": parent_id
            }
        }

        response = requests.put(
            f"{self.URL_BASE}/Entity/{entity_id}",
            headers=headers,
            data=json.dumps(data)
        )

        if response.status_code >= 300:
            logger.error(f"error{response.status_code} update_profile_user '{response.text}'")

        logger.debug(json.dumps(response.json(), indent=4))

        if "ERROR" in response.text:
            logger.error("[!] Échec de la mise à jour de l'entité")
            return 0
        else:
            logger.info("[+] Entité mise à jour avec succès")
            return 1

    def update_user(self, user_id, item_name, new_value):
        """
        Updates a user with new values.

        Args:
            user_id (int): The ID of the user.
            item_name (str): The name of the item to update.
            new_value: The new value for the item.

        Returns:
            int: 1 if the update was successful, 0 otherwise.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            return 0

        if not user_id or not item_name or new_value is None:
            logger.error(
                "[!] Usage: update_user <user_id> <item_name> <new_value>")
            return 0

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN,
            "Content-Type": "application/json"
        }

        data = {
            "input": {
                item_name: new_value,
                "id": user_id
            }
        }

        response = requests.put(
            f"{self.URL_BASE}/User/{user_id}",
            headers=headers,
            data=json.dumps(data)
        )
        logger.debug(response.text)
        if not response.ok or "ERROR" in response.text:
            logger.error(f"[!] Échec de la mise à jour de l'utilisateur {user_id} (HTTP {response.status_code})")
            try:
                logger.debug(json.dumps(response.json(), indent=4))
            except Exception:
                logger.debug(response.text)
            return 0
        else:
            logger.info(f"[+] Utilisateur {user_id} mis à jour avec succès")
            return 1

    def add_profile_to_user(self, user_id, profile_id, entities_id, is_recursive=0, is_dynamic=0, is_default_profile=0):
        """
        Adds a profile to a user.

        Args:
            user_id (int): The ID of the user.
            profile_id (int): The ID of the profile.
            entities_id (int): The ID of the entity.
            is_recursive (int, optional): Whether the profile is recursive.
            is_dynamic (int, optional): Whether the profile is dynamic.
            is_default_profile (int, optional): Whether the profile is the default profile.

        Returns:
            dict: The response from the API.

        Raises:
            Exception: If the session is not initialized or if adding the profile fails.
        """
        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN,
            "Content-Type": "application/json"
        }

        data = {
            "input": {
                "users_id": user_id,
                "profiles_id": profile_id,
                "entities_id": entities_id,
                "is_recursive": is_recursive,
                "is_dynamic": is_dynamic,
                "is_default_profile": is_default_profile,
                "_reset_personal_token": True,
            }
        }

        response = requests.post(
            f"{self.URL_BASE}/User/{user_id}/Profile_User/",
            headers=headers,
            data=json.dumps(data)
        )

        if response.status_code > 300:
            logger.error(f"Error {response.status_code}: {response.text}")
            response.raise_for_status()
            logger.error("[!] Échec de l'ajout du profil à l'utilisateur")
            raise Exception("[!] Échec de l'ajout du profil à l'utilisateur")

        logger.info(
            f"[+] Profil ajouté avec succès à l'utilisateur ID : {user_id}")
        return response.json()

    def delete_profile_from_user(self, user_id, profile_id):
        """
        Deletes a profile from a user.

        Args:
            user_id (int): The ID of the user.
            profile_id (int): The ID of the profile.

        Returns:
            dict: The response from the API.

        Raises:
            Exception: If the session is not initialized or if deleting the profile fails.
        """
        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN,
            "Content-Type": "application/json"
        }

        data = {
            "input": {
                "id": profile_id
            }
        }

        response = requests.delete(
            f"{self.URL_BASE}/User/{user_id}/Profile_User/",
            headers=headers,
            data=json.dumps(data)
        )

        if response.status_code > 300:
            logger.error(f"Error {response.status_code}: {response.text}")
            response.raise_for_status()
            logger.error(
                "[!] Échec de la suppression du profil de l'utilisateur")
            raise Exception(
                "[!] Échec de la suppression du profil de l'utilisateur")

        logger.info(
            f"[+] Profil supprimé avec succès de l'utilisateur ID : {user_id}")
        return response.json()


def verifier_parametres(dictctrl, cles_requises):
    # Vérifier chaque clé
    for cle in cles_requises:
        if cle not in dictctrl or dictctrl[cle] is None:
            # Lever une exception si une clé est manquante ou None
            raise ValueError(
                f"La clé '{cle}' est manquante ou None dans le dictionnaire initparametre.")


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################
def getApiVersion():
    return APIVERSION

def activate():
    logger = logging.getLogger()
    config = AdminConfig("admin")

    if config.disable:
        logger.warning("Plugin admin: disabled by configuration.")
        return False

    if not AdminDatabase().activate(config):
        logger.warning(
            "Plugin admin: an error occurred during the database initialization"
        )
        return False
    return True

def get_CONNECT_API():
    out_result = {"get_user_info": {}, "get_list_profiles": {}}
    client = None

    # Récupération des paramètres de connexion à l'API
    initparametre = AdminDatabase().get_CONNECT_API()
    logger.info(f"Paramètres de connexion à l'API : {initparametre}")

    # Vérification de la présence et de la validité du type d'API dans les paramètres
    if "type_api" in initparametre and initparametre["type_api"] is not None:
        # Vérification des paramètres nécessaires pour l'API REST GLPI
        try:
            verifier_parametres(initparametre, ["glpi_mmc_app_token",
                                                "glpi_url_base_api",
                                                "glpi_root_user_token"])
        except Exception as e:
            logger.error("Paramètres manquants ou invalides : %s",
                         traceback.format_exc())
            return []

        # Traitement spécifique pour l'API REST GLPI
        if initparametre["type_api"] == "glpi_rest":
            try:
                # Initialisation du client GLPI avec les tokens et l'URL de base
                client = GLPIClient(
                    app_token=initparametre["glpi_mmc_app_token"],
                    url_base=initparametre["glpi_url_base_api"],
                    user_token=initparametre["glpi_root_user_token"])

                # Initialisation de la session du client
                client.init_session()

                # Vérification de l'initialisation de la session
                if client and client.SESSION_TOKEN:
                    logger.info("Session GLPI initialisée avec succès.")
                    # Récupération des informations utilisateur
                    get_user_info = client.get_user_info()
                    logger.info(
                        "Informations utilisateur récupérées avec succès.")

                    # Récupération de la liste des profils
                    get_profiles_info = client.get_list(
                        "profiles", is_recursive=True)
                    profilslist = [{"id": x["id"], "name": x["name"]}
                                   for x in get_profiles_info]
                    logger.info("Liste des profils récupérée avec succès.")

                    # Mise à jour du résultat avec les informations récupérées
                    out_result = {"get_user_info": get_user_info,
                                  "get_list_profiles": profilslist}

                    client.kill_session()
                    return out_result
                else:
                    logger.error(
                        "Échec de l'initialisation de la session GLPI.")
                    return []
            except Exception as e:
                logger.error(
                    "Erreur lors de la récupération des informations : %s", traceback.format_exc())
                return []
    else:
        # Gestion d'autres types d'API (non implémenté)
        logger.info(
            "Type d'API non supporté ou non spécifié. Cette section peut être étendue pour d'autres types d'API.")
        return []

def get_glpi_client():
    initparametre = AdminDatabase().get_CONNECT_API()
    verifier_parametres(initparametre, [
        "glpi_mmc_app_token", "glpi_url_base_api", "glpi_root_user_token"
    ])
    client = GLPIClient(
        app_token=initparametre["glpi_mmc_app_token"],
        url_base=initparametre["glpi_url_base_api"],
        user_token=initparametre["glpi_root_user_token"],
    )
    client.init_session()
    return client

def get_list(type, is_recursive=False):
    client = get_glpi_client()

    results = client.get_list(type, is_recursive)

    return results

def get_user_info(user_id=None):
    client = get_glpi_client()

    user_info = client.get_user_info(user_id)

    return user_info

def get_users_count_by_entity(entity_id):
    client = get_glpi_client()

    result = client.get_users_count_by_entity(entity_id)

    return result

def get_counts_by_entity(entities):
    """
    Retourne pour chaque entité le nombre de machines et d'utilisateurs.
    Args:
        entities (list[dict]): chaque dict contient au moins 'id'
    Returns:
        dict: { "<entity_id>": {"machines": int, "users": int}, ... }
    """
    result = {}
    # Compte machines : on réutilise ta logique existante
    machines_by_entity = get_machine_count_by_entity(entities)  # { "id": count }

    client = get_glpi_client()
    try:
        for e in entities:
            eid = str(e["id"])
            # Si tu as une méthode dédiée "count only", utilise-la.
            # Sinon on réutilise ta fonction existante et on prend la longueur.
            try:
                users_list = client.get_users_count_by_entity(eid)
                users_count = len(users_list)
            except Exception:
                logger.exception("Failed to get users for entity %s", eid)
                users_count = 0

            machines_count = int(machines_by_entity.get(eid) or machines_by_entity.get(e["id"], 0))

            result[eid] = {
                "users": users_count,
                "machines": machines_count,
            }
    finally:
        try:
            client.kill_session()
        except Exception:
            logger.warning("Failed to kill GLPI session", exc_info=True)

    return result

def get_entity_info(entity_id):
    client = get_glpi_client()

    entity_info = client.get_entity_info(entity_id)

    entity = entity_info if isinstance(entity_info, dict) else entity_info[0]
    return {
        "id": entity.get("id"),
        "name": entity.get("name"),
        "entities_id": entity.get("entities_id"),
        "completename": entity.get("completename")
    }

def get_profile_name(profile_id):
    client = get_glpi_client()

    profil_name = client.get_profile_name(profile_id)
    return profil_name

def create_entity_under_custom_parent(parent_entity_id, name):
    client = get_glpi_client()

    tag_value = str(uuid.uuid4())
    create_entities_in_glpi = client.create_entity_under_custom_parent(parent_entity_id, name, tag_value)

    AdminDatabase().create_entity_under_custom_parent(create_entities_in_glpi, name, tag_value)

    return create_entities_in_glpi

def update_entity(entity_id, item_name, new_entity_name, parent_id):
    client = get_glpi_client()

    update_entity = client.update_entity(entity_id, item_name, new_entity_name, parent_id)

    AdminDatabase().update_entity(entity_id, item_name, new_entity_name)

    return update_entity

def create_organization(parent_entity_id,
                        name_new_entity,
                        name_user,
                        pwd,
                        profiles_id,
                        tag_value,
                        realname="",
                        firstname=""):
    # Initialisation des variables
    client = None
    id_create_entity = None

    logger.debug(f"Paramètres dparent_entity_id: {parent_entity_id}")
    logger.debug(f"Paramètres name_new_entity : {name_new_entity}")
    logger.debug(f"Paramètres name_user : {name_user}")
    logger.debug("Paramètres  pwd: *******")
    logger.debug(f"Paramètres  profiles_id: {profiles_id}")
    logger.debug(f"Paramètres  tag_value: {tag_value}")
    logger.debug(f"Paramètres  realname: {realname}")
    logger.debug(f"Paramètres  firstname: {firstname}")

    # Récupération des paramètres de connexion à l'API
    initparametre = AdminDatabase().get_CONNECT_API()
    logger.debug(f"Paramètres de connexion à l'API : {initparametre}")

    # Vérification de la présence et de la validité du type d'API dans les paramètres
    if "type_api" in initparametre and initparametre["type_api"] is not None:
        # Vérification des paramètres nécessaires pour l'API REST GLPI
        try:
            verifier_parametres(initparametre, ["glpi_mmc_app_token",
                                                "glpi_url_base_api",
                                                "glpi_root_user_token"])
        except Exception as e:
            logger.error("Paramètres manquants ou invalides : %s",
                         traceback.format_exc())
            return []

        # Traitement spécifique pour l'API REST GLPI
        if initparametre["type_api"] == "glpi_rest":
            try:
                # Initialisation du client GLPI avec les tokens et l'URL de base
                client = GLPIClient(
                    app_token=initparametre["glpi_mmc_app_token"],
                    url_base=initparametre["glpi_url_base_api"],
                    user_token=initparametre["glpi_root_user_token"])

                # Initialisation de la session du client
                client.init_session()

                # Vérification de l'initialisation de la session
                if client and client.SESSION_TOKEN:
                    logger.debug("Session GLPI initialisée avec succès.")
                    logger.debug(f"CREATION ENTITY  {name_new_entity}")
                    # Création d'une nouvelle entité sous un parent personnalisé
                    id_create_new_entity = client.create_entity_under_custom_parent(
                        parent_entity_id, name_new_entity, tag_value)
                    logger.debug(f"Nouvelle entité créée avec l'ID : {id_create_new_entity}")
                    logger.debug(f"{name_user}, {pwd}, {id_create_new_entity}, {realname}, {firstname}")
                    # Création d'un nouvel utilisateur

                    logger.debug(f"CREATION UTILISATEUR : {name_user}")
                    id_new_user = client.create_user(name_user,
                                                     pwd,
                                                     entities_id=id_create_new_entity,
                                                     realname=realname,
                                                     firstname=firstname,
                                                     profiles_id=profiles_id)

                    logger.info(
                        f"Nouvel utilisateur créé avec l'ID : {id_new_user}")

                    # # Changement du profil de l'utilisateur
                    # client.change_user_profile(id_new_user, profiles_id, id_create_new_entity)
                    # logger.info(f"Profil de l'utilisateur {id_new_user} changé avec succès.")
                    #

                    logger.debug(f"CREATION PROFIL USER {name_user} :id  {profiles_id}")
                    client.add_profile_to_user(
                        id_new_user, 3, id_create_new_entity)

                    zzz = client.get_user_info(id_new_user)
                    logger.debug(f"$$$$$$$$$$$$$$$$$$$$$$ zzz {zzz} ")
                    # client.update_profile_user( id_new_user, "profiles_id", profiles_id)

                    # logger.error(f"profiles_id id. {profiles_id}")
                    result = client.update_user(
                        id_new_user, "_reset_api_token", True)
                    logger.debug(
                        f"$$$$$$$$$$$$$$$$$$$$$$ _reset_api_token {result} ")

                    #
                    # logger.error(f"profiles_id id. {profiles_id}")
                    result = client.update_user(
                        id_new_user, "_reset_personal_token", True)
                    logger.debug(
                        f"$$$$$$$$$$$$$$$$$$$$$$ _reset_personal_token {result} ")
                    # logger.info(f"APPLIQUE TAG ENTITY  {name_new_entity} :tag {tag_value}")
                    # result = client.update_entity(id_create_new_entity, "tag", tag_value)

                    # Retourne les identifiants de la nouvelle entité, de l'utilisateur et le profil
                    return [id_create_new_entity, id_new_user, profiles_id, result]
                else:
                    logger.error(
                        "Échec de l'initialisation de la session GLPI.")
                    return []
            except Exception as e:
                client.kill_session()
                logger.error(
                    "Erreur lors de la création de l'organisation : %s", traceback.format_exc())
                return []
    else:
        # Gestion d'autres types d'API (non implémenté)
        logger.info(
            "Type d'API non supporté ou non spécifié. Cette section peut être étendue pour d'autres types d'API.")
        return []
