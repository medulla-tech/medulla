# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.version import getVersion, getRevision

from mmc.plugins.admin.config import AdminConfig

# Import for Database
from pulse2.database.admin import AdminDatabase
from pulse2.database.pkgs import PkgsDatabase
from mmc.plugins.glpi import get_entities_with_counts, get_entities_with_counts_root, set_user_api_token, get_user_profile_email, get_complete_name

from configparser import ConfigParser
import traceback
import requests
import logging
import base64
import random
import shutil
import string
import json
import uuid
import os
import re

VERSION = "1.0.0"
APIVERSION = "4:1:3"

logger = logging.getLogger()

class GLPIClient:
    """
    REST customer for the GLPI API.

    Manages authentication (User Token or Basic), the opening/closing of
    session and exposes methods to read, create, update, assign and
    Remove resources (users, profiles, entities).

    Main attributes
    ------------------
    Url_base, app_token, user_token, login, password, session_token, author_method

    Methods
    --------
    # Session
    - INIT_SISSION (): Open a session (recovers session_token).
    - Kill_session (): Closes the current session.

    # Reading / Getting
    - Get_list (Type, is_recursive = False): USERS/PROFILES/ENTITIES/MYENTITITIES.
    - Get_list_users (): User list (useful fields).
    - Get_list_entities (): List of entities (Dict by ID).
    - Get_users_count_by_entity (Entity_ID): users of an entity (with profile).
    - Get_entity_info (entity_id): details of an entity.
    - Get_Profile_Name (profile_id): name of a profile.

    # Creation
    - Create_user_basic (name_user, pwd, realname = none, firstname = none)
    - Create_user (Name_user, Pwd, Entities_id, Profiles_id, ..., email = none, ...)
    - Create_entity_under_custom_Parent (parent_entity_id, name, tagvalue = none)

    # Update / assignment
    - Update_user (user_id, item_name, new_value): User fields.
    - set_user_email (user_id, email, exclusive = true): sync user.email + usemail
    (Exclusive = True => keep only one address).
    - Update_entity (entity_id, item_name, new_value, parent_id): Màj entity.
    - Switch_user_entity (User_id, new_entity_id): Change the default entity.
    - Switch_user_profile (User_id, New_Profile_ID, Entities_id, ...)
    - add_profile_to_user (user_id, profile_id, entities_id, ...)

    # Deletion
    - delete_entity (entity_id)
    - delete_and_purge_user (user_id)
    - delete_profile_from_user (user_id, profile_id)

    # Utilities
    - Generate_Token (Length = 40): generates an alphanumeric token.
    - Extract_GLPI_ERROR_Message (text) (staticmethod): Extract a readable error message.
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

    def kill_session(self):
        """
        Complete the current session by sending a request to the server to invalidate the session token.

        This method sends a request Get to the endpoint `/Killsession 'of the API,
        Using the application and session tokens for authentication.
        If the request succeeds (HTTP 200 code), the session token is reset to `none '.

        Raises:
        Requistes. Exceptions.httperror: If the request fails (HTTP code different from 200),
        An exception is lifted with the details of the error.

        Notes:
        - If no session token (`session_token`) is defined, a warning is logged
        And the method returns immediately.
        - If successful, a confirmation message is logged, as well as the JSON response
        server (in debug mode).
        """
        if not self.SESSION_TOKEN:
            logger.warning("No active session to finish.")
            return
        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }
        response = requests.get(
            f"{self.URL_BASE}/killSession", headers=headers)
        if response.status_code == 200:
            logger.info("[*] Completed session")
            self.SESSION_TOKEN = None
            logger.debug(json.dumps(response.json(), indent=4))
        else:
            response.raise_for_status()

    def _headers(self):
        if not self.APP_TOKEN:
            raise Exception("App-Token manquant.")
        if not self.SESSION_TOKEN:
            raise Exception("Uninitialized session (connects the client before).")
        return {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN,
            "Content-Type": "application/json",
        }

    @staticmethod
    def extract_glpi_error_message(text: str) -> str | None:
        """
        Return only the readable GLPI message
        (ex: addition impossible. The user already exists.)
        """
        if not text:
            return None

        m = re.search(r'(\[\s*"ERROR_[A-Z_]+"[^]]*\])', text)
        if m:
            try:
                arr = json.loads(m.group(1))
                if isinstance(arr, list) and len(arr) >= 2 and isinstance(arr[1], str):
                    return arr[1].replace("\\'", "'").strip()
            except Exception:
                pass

        for sep in [" — ", " - "]:
            if sep in text:
                tail = text.split(sep, 1)[1].strip()
                return tail.strip("'").strip('"')

        for needle in [
            "L'utilisateur existe déjà",
            "n'avez pas les droits requis",
            "Ajout impossible",
        ]:
            i = text.find(needle)
            if i != -1:
                return text[i:].replace("\\'", "'").strip()

        return None

    def _raise_glpi(self, action: str, resp) -> None:
        """
        Lève RuntimeError: "{action} failed: HTTP {code} — {message lisible}"
        """
        try:
            body = resp.json()
        except Exception:
            body = resp.text

        msg = None
        if isinstance(body, list) and len(body) >= 2 and isinstance(body[1], str):
            msg = body[1]
        if not msg:
            msg = self.extract_glpi_error_message(resp.text) or str(body)

        raise RuntimeError(f"{action} failed: HTTP {resp.status_code} — {msg}")

    def __clean_none_values(self, obj):
        """
        Replaces recursively all the occurrences of None/Null with an empty chain ("")
        In a Dict or List JSON object.

        Args:
            obj (dict | list | any): The JSON object or a value to be treated.

        Returns:
            dict | list | str | any: The object with all the none replaced by "".
        """
        # Si c'est un dictionnaire, on applique la fonction à chaque valeur
        if isinstance(obj, dict):
            return {k: self.__clean_none_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.__clean_none_values(v) for v in obj]
        elif obj is None:
            return ""

        else:
            return obj

    def generate_token(self, length=40):
        """
        Generates a random token (token) made up of letters and numbers.

        The token is generated using a set of alphanumeric characters
        (capital letters, tiny letters and numbers).The default length
        of the token is 32 characters, but it can be personalized.

        Args:
        Length (int, optional): desired length for the generated token.By default, 32.

        Returns:
        STR: A random alphanumeric character string of the specified length.

        Example:
        >>> Token = generate_token ()
        >>> Print (token) # Exit example: "AB3x9kpl2qr7vy4Zw1st5uv8nm6"
        >>> Custom_token = generate_token (16)
        >>> Print (Custom_Token) # Exit example: "FG7HJ9KL2MN4"
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    # READ
    def get_list(self, type: str, is_recursive: bool = False):
        """
        Recovers a list of GLPI objects (users, profiles or entities).
        [...]
        """
        if not self.SESSION_TOKEN:
            logger.error("Session non initialisée. Veuillez initialiser la session.")
            raise Exception("Session non initialisée. Veuillez initialiser la session.")

        # Vérification stricte des valeurs permises
        allowed_types = {"users", "profiles", "entities", "myentities"}
        if type not in allowed_types:
            logger.error("Type invalide fourni : %s", type)
            raise ValueError(f"Type invalide '{type}'. Valeurs permises : {allowed_types}")

        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return 0

        if type == "users":
            endpoint = "User"
        elif type == "profiles":
            endpoint = "Profile"
        elif type == "entities":
            endpoint = "Entity"
        elif type == "myentities":
            endpoint = f"getMyEntities?is_recursive={str(is_recursive).lower()}"

        response = requests.get(f"{self.URL_BASE}/{endpoint}", headers=headers)

        if response.status_code != 200:
            response.raise_for_status()

        data = self.__clean_none_values(response.json())

        if type == "users":
            return data
        elif type == "profiles":
            self.profiles = data
            return data
        elif type == "entities":
            return data
        elif type == "myentities":
            return data.get("myentities", [])

    def get_list_users(self):
        """
        Recovers the list of GLPI users with their main information.
        """
        results = self.get_list('users', True)
        users_data = []
        for t in results:
            users_data.append({
                "id": t.get("id"),
                "name": t.get("name") or "",
                "lastname": t.get("realname") or "",
                "is_active": t.get("is_active"),
                "profiles_id": t.get("profiles_id"),
                "last_login": t.get("last_login") or "",
                "date_mod": t.get("date_mod") or "",
                "date_creation": t.get("date_creation") or "",
                "entities_id": t.get("entities_id"),
                "locations_id":t.get("locations_id"),
                "groups_id":t.get("groups_id"),
            })
        return users_data

    def get_list_entities(self):
        """
        Recovers the list of available entities and organizes them in a dictionary.
        """
        results = self.get_list('entities', True)
        entity_data = {}
        for t in results:
            entity_id = t['id']
            entity_data[entity_id] = {
                'name': t['name'],
                'completename': t['completename'],
                'date_mod': t['date_mod'],
                'level': t['level']
            }
        return entity_data

    def get_users_count_by_entity(self, entity_id):
        if not self.SESSION_TOKEN:
            raise Exception("Session non initialisée. Veuillez initialiser la session.")

        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return 0

        params = {
            "criteria[0][field]": 80,
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": entity_id,
            "range": "0-999",
            "forcedisplay[0]": "2",  # id
            "forcedisplay[1]": "1",  # name
        }
        r = requests.get(f"{self.URL_BASE}/search/User", headers=headers, params=params, timeout=15)
        r.raise_for_status()
        users = (r.json() or {}).get("data", []) or []

        out = []
        for row in users:
            name = row.get("1", "") or ""
            if not name or name in ("root", "glpi-system") or name.startswith("Plugin_"):
                continue

            uid = str(row.get("2", "")).strip()
            if not uid:
                continue

            profile_id = ""
            try:
                pr = requests.get(f"{self.URL_BASE}/User/{uid}/Profile_User", headers=headers, timeout=10)
                pr.raise_for_status()
                links = pr.json()
                if isinstance(links, dict):
                    links = [links]
                links = links or []

                eid_str = str(entity_id)
                candidates = [l for l in links if str(l.get("entities_id")) == eid_str]

                chosen = None
                for l in candidates:
                    is_def = str(l.get("is_default") or "0").lower()
                    if is_def in ("1", "true", "yes", "on"):
                        chosen = l
                        break
                if not chosen and candidates:
                    chosen = candidates[0]

                if chosen:
                    profile_id = str(chosen.get("profiles_id") or "").strip()
                else:

                    ur = requests.get(f"{self.URL_BASE}/User/{uid}", headers=headers, timeout=10)
                    ur.raise_for_status()
                    u = ur.json() or {}
                    if str(u.get("entities_id")) == eid_str:
                        profile_id = str(u.get("profiles_id") or "").strip()
            except Exception:
                logger.debug(f"Erreur récupération profil user {uid} / entity {entity_id}: {traceback.format_exc()}")

            out.append({
                "id": uid,
                "name": name,
                "entity_id": int(entity_id),
                "profile_id": profile_id
            })

        return out

    def get_entity_info(self, entity_id):
        """
        Recovers the info from a GLPI entity by his ID.
        """
        if not self.SESSION_TOKEN:
            logger.error("Session non initialisée.")
            raise Exception("Session non initialisée. Veuillez initialiser la session.")

        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return 0

        response = requests.get(f"{self.URL_BASE}/Entity/{entity_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Entité {entity_id} introuvable.")
            return {}
        else:
            response.raise_for_status()

    def get_profile_name(self, profile_id):
        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return 0

        response = requests.get(
            f"{self.URL_BASE}/Profile/{profile_id}", headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("name", "")

    # CREATE
    def create_user_basic(
        self,
        identifier: str,               # login (email)
        password: str,
        lastname: str | None = None,   # GLPI: realname
        firstname: str | None = None,
        phone: str | None = None,
        language: str = "fr_FR",
        active: bool = True,
    ) -> int:
        """
        Create a basic GLPI user (without managing profile/entity).
        - `Identify` => User.Name
        - `Password` => User.Password/Password2
        - Return an exception in case of error
        """
        headers = self._headers()

        payload = {
            "input": {
                "name": identifier,
                "password": password,
                "password2": password,
                "language": language,
                "is_active": 1 if active else 0,
            }
        }
        if lastname is not None:
            payload["input"]["realname"] = lastname
        if firstname is not None:
            payload["input"]["firstname"] = firstname
        if phone is not None:
            payload["input"]["phone"] = phone

        r = requests.post(f"{self.URL_BASE}/User", headers=headers, json=payload, timeout=15)
        if r.status_code >= 300:
            self._raise_glpi("Create User", r)

        data = r.json() if "application/json" in (r.headers.get("Content-Type") or "") else {}
        user_id = int((data or {}).get("id") or 0)
        if user_id <= 0:
            raise RuntimeError(f"Create User failed: HTTP {r.status_code} — unexpected response: {data}")
        return user_id

    def create_user(
        self,
        identifier: str,
        lastname: str | None = None,
        firstname: str | None = None,
        password: str | None = None,
        phone: str | None = None,
        id_entity: int | None = None,
        id_profile: int | None = None,
        is_recursive: bool = False,
        do_rollback_on_error: bool = True,
    ) -> int:
        """
        Create the user and then apply the strict switch:
        - 1 only link (profile, entity), defect posed
        - purge of other links
        """
        user_id = None
        try:
            user_id = self.create_user_basic(
                identifier=identifier,
                password=password,
                lastname=lastname,
                firstname=firstname,
                phone=phone,
            )

            self.switch_user_profile(
                user_id=user_id,
                new_profile_id=int(id_profile),
                entities_id=int(id_entity),
                is_recursive=1 if is_recursive else 0,
            )

            return user_id

        except Exception as e:
            if do_rollback_on_error and user_id:
                try:
                    self.delete_and_purge_user(user_id)
                except Exception:
                    pass
            raise RuntimeError(f"Echec création utilisateur GLPI: {e}") from e

    def create_entity_under_custom_parent(self, parent_entity_id, name, tagvalue=None):
        """
        Creates an entity under a specified parent.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            raise Exception(
                "Session non initialisée. Veuillez initialiser la session.")

        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return 0

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

    # UPDATE
    def update_user(self, user_id, item_name, new_value):
        """
        Updates a user with new values.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            return 0

        if not user_id or not item_name or new_value is None:
            logger.error(
                "[!] Usage: update_user <user_id> <item_name> <new_value>")
            return 0

        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return 0

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

    def set_user_email(self, user_id, email, exclusive=True):
        if not email:
            return 1

        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return 0

        uid = int(user_id)
        email = email.strip()

        # 1) Sync User.email
        requests.put(
            f"{self.URL_BASE}/User/{uid}",
            headers=headers,
            json={"input": {"id": uid, "email": email}},
            timeout=10
        ).raise_for_status()

        # 2) Lire UserEmail
        r = requests.get(f"{self.URL_BASE}/User/{uid}/UserEmail", headers=headers, timeout=10)
        r.raise_for_status()
        rows = r.json()
        rows = [rows] if isinstance(rows, dict) else (rows or [])

        def_row = next((e for e in rows if int(e.get("is_default") or 0) == 1), None)
        same    = next((e for e in rows if (e.get("email") or "").lower() == email.lower()), None)

        if def_row:
            # Mettre à jour l’email de la ligne par défaut
            did = {"input": {"id": int(def_row["id"]), "email": email, "is_default": 1}}
            requests.put(f"{self.URL_BASE}/UserEmail/{int(def_row['id'])}", headers=headers, json=did, timeout=10).raise_for_status()
            # S'il existe une autre ligne avec la même adresse, on la supprime pour éviter les doublons
            if same and int(same.get("id") or 0) != int(def_row["id"]):
                requests.delete(f"{self.URL_BASE}/UserEmail/{int(same['id'])}", headers=headers, timeout=10).raise_for_status()
        elif same:
            # Aucune par défaut, mais une ligne identique existe -> la passer en défaut
            requests.put(
                f"{self.URL_BASE}/UserEmail/{int(same['id'])}",
                headers=headers,
                json={"input": {"id": int(same["id"]), "is_default": 1}},
                timeout=10
            ).raise_for_status()
        else:
            # Rien d’existant -> créer une ligne par défaut
            requests.post(
                f"{self.URL_BASE}/UserEmail",
                headers=headers,
                json={"input": {"users_id": uid, "email": email, "is_default": 1}},
                timeout=10
            ).raise_for_status()

        if exclusive:
            # 3) Supprimer toutes les lignes NON défaut (on ne garde qu’une seule adresse)
            r = requests.get(f"{self.URL_BASE}/User/{uid}/UserEmail", headers=headers, timeout=10)
            r.raise_for_status()
            for e in (r.json() or []):
                if int(e.get("is_default") or 0) != 1:
                    try:
                        requests.delete(f"{self.URL_BASE}/UserEmail/{int(e['id'])}", headers=headers, timeout=10).raise_for_status()
                    except Exception:
                        pass
        return 1

    def update_entity(self, entity_id, item_name, new_value, parent_id):
        """
        Updates an entity with new values.
        """
        if not self.SESSION_TOKEN:
            logger.error(
                "Session non initialisée. Veuillez initialiser la session.")
            return 0

        if not entity_id or not item_name or not new_value:
            logger.error(
                "[!] Usage: update_entity <entity_id> <item_name> <new_value>")
            return 0

        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return 0

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

    def switch_user_entity(self, user_id: int, new_entity_id: int, tokenuser=None) -> dict:
        """
        Change l'entité par défaut d'un utilisateur GLPI.
        """
        try:
            headers = self._headers()
            uid = int(user_id)
            eid = int(new_entity_id)

            r = requests.put(
                f"{self.URL_BASE}/User/{uid}",
                headers=headers,
                json={"input": {"id": uid, "entities_id": eid}},
                timeout=10
            )
            r.raise_for_status()
            return {"success": True, "code": 0, "user_id": uid, "entities_id": eid}

        except requests.HTTPError as e:
            return {
                "success": False,
                "code": getattr(e.response, "status_code", None) or -1,
                "error": str(e),
                "body": getattr(e.response, "text", "")
            }
        except Exception as e:
            return {"success": False, "code": -1, "error": str(e)}

    def switch_user_profile(
        self,
        user_id: int,
        new_profile_id: int,
        entities_id: int,
        is_recursive: int = 0,
    ) -> dict:
        """
        1 only profile_user link for the user.
        - Create/up the link (profile, entity)
        - Updates is_recursive if necessary
        - Deletes all other links
        - Position the defect (is_default = 1) on the target
        - purge afterwards any dynamic self-service possibly reinjected by GLPI
        """
        headers = self._headers()
        uid = int(user_id); pid = int(new_profile_id); eid = int(entities_id)
        want_rec = 1 if int(is_recursive) == 1 else 0

        def _list_links():
            r = requests.get(f"{self.URL_BASE}/User/{uid}/Profile_User", headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json() or []
            return [data] if isinstance(data, dict) else data

        _ss_cache: dict[int, bool] = {}

        def _is_self_service_profile_id(prof_id: int) -> bool:
            prof_id = int(prof_id or 0)
            if prof_id in _ss_cache:
                return _ss_cache[prof_id]
            try:
                r = requests.get(f"{self.URL_BASE}/Profile/{prof_id}", headers=headers, timeout=10)
                r.raise_for_status()
                name = str((r.json() or {}).get("name", "")).strip().lower()
                is_ss = (name == "self-service")
                _ss_cache[prof_id] = is_ss
                return is_ss
            except Exception:
                _ss_cache[prof_id] = False
                return False

        try:
            rows = _list_links()
            target = next((lk for lk in rows
                        if int(lk.get("profiles_id", 0)) == pid and int(lk.get("entities_id", 0)) == eid), None)

            if not target:
                self.add_profile_to_user(
                    user_id=uid, profile_id=pid, entities_id=eid,
                    is_recursive=want_rec, is_dynamic=0, is_default=1
                )
                rows = _list_links()
                target = next((lk for lk in rows
                            if int(lk.get("profiles_id", 0)) == pid and int(lk.get("entities_id", 0)) == eid), None)

            if not target:
                return {"success": False, "code": 500, "error": "target link not found after creation"}

            tlid = int(target.get("id", 0) or 0)
            cur_rec = int(target.get("is_recursive", 0) or 0)
            if tlid and cur_rec != want_rec:
                requests.put(
                    f"{self.URL_BASE}/Profile_User/{tlid}",
                    headers=headers,
                    json={"input": {"id": tlid, "is_recursive": want_rec}},
                    timeout=10
                ).raise_for_status()

            # Purge of all other links
            rows = _list_links()
            for lk in rows:
                lid = int(lk.get("id", 0) or 0)
                if not lid or lid == tlid:
                    continue
                try:
                    requests.delete(f"{self.URL_BASE}/Profile_User/{lid}", headers=headers, timeout=10).raise_for_status()
                except requests.HTTPError as e:
                    if getattr(e.response, "status_code", None) != 404:
                        logger.warning(f"Failed to delete link {lid}: {e}")

            # Place the defect on the target
            requests.put(
                f"{self.URL_BASE}/User/{uid}",
                headers=headers,
                json={"input": {"id": uid, "entities_id": eid, "profiles_id": pid}},
                timeout=10
            ).raise_for_status()

            rows2 = _list_links()
            for lk in rows2:
                lid = int(lk.get("id", 0) or 0)
                if not lid or lid == tlid:
                    continue
                if int(lk.get("is_dynamic", 0) or 0) == 1:
                    lpid = int(lk.get("profiles_id", 0) or 0)
                    if _is_self_service_profile_id(lpid):
                        try:
                            requests.delete(f"{self.URL_BASE}/Profile_User/{lid}", headers=headers, timeout=10).raise_for_status()
                        except requests.HTTPError as e:
                            if getattr(e.response, "status_code", None) != 404:
                                logger.warning(f"Failed to delete dynamic Self-Service link {lid}: {e}")

            return {"success": True, "code": 0, "user_id": uid, "entities_id": eid, "profiles_id": pid}

        except requests.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            body = getattr(e.response, "text", "")
            logger.error(f"HTTP Error: {status} - {body}")
            return {"success": False, "code": status or -1, "error": str(e), "body": body}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "code": -1, "error": str(e)}


    def add_profile_to_user(
        self,
        user_id: int,
        profile_id: int,
        entities_id: int,
        is_recursive: int = 0,
        is_dynamic: int = 0,
        is_default: int = 0) -> dict:

        h = self._headers()
        payload = {
            "input": {
                "users_id": int(user_id),
                "profiles_id": int(profile_id),
                "entities_id": int(entities_id),
                "is_recursive": int(bool(is_recursive)),
                "is_dynamic": int(bool(is_dynamic)),
                "is_default": int(bool(is_default))
            }
        }

        r1 = requests.post(f"{self.URL_BASE}/User/{int(user_id)}/Profile_User",
                        headers=h, json=payload, timeout=15)
        if r1.status_code < 300:
            return {"ok": True, "source": "nested"}

        r2 = requests.post(f"{self.URL_BASE}/Profile_User",
                        headers=h, json=payload, timeout=15)
        if r2.status_code < 300:
            return {"ok": True, "source": "flat"}

        self._raise_glpi("Add Profile_User", r1 if r1.status_code >= 300 else r2)

    # DELETE
    def _find_selfservice_profile_id(self) -> int | None:
        try:
            profs = self.get_list("profiles", False) or []
            def norm(s): return (s or "").lower().replace(" ", "").replace("-", "")
            for p in profs:
                if norm(p.get("name")) in ("selfservice", "self_service"):
                    return int(p["id"])
        except Exception:
            pass
        return None

    def delete_entity(self, entity_id):
        """
        Supprime une entité puis assigne Self-Service sur l’entité parente
        aux utilisateurs qui y ont été migrés par GLPI.
        """
        if not self.SESSION_TOKEN:
            msg = "Session non initialisée. Veuillez initialiser la session."
            logger.error(msg)
            return {"success": False, "message": msg}
        if not entity_id:
            msg = "[!] Usage: delete_entity <entity_id>"
            logger.error(msg)
            return {"success": False, "message": msg}

        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Session/headers error: {e}")
            return {"success": False, "message": str(e)}

        eid = int(entity_id)

        parent_id = 0
        try:
            info = self.get_entity_info(eid) or {}
            parent_id = int(info.get("entities_id") or 0)
        except Exception:
            pass

        try:
            users_rows = self.get_users_count_by_entity(eid) or []
            user_ids = [int(u.get("id") or 0) for u in users_rows if u.get("id")]
        except Exception:
            user_ids = []

        # delete entity
        response = requests.delete(f"{self.URL_BASE}/Entity/{eid}", headers=headers)
        if response.status_code >= 300:
            try:
                error_data = response.json()
                if isinstance(error_data, list) and len(error_data) >= 2:
                    return {"success": False, "message": error_data[1]}
                else:
                    return {"success": False, "message": response.text}
            except ValueError:
                return {"success": False, "message": response.text}

        # poser Self-Service sur le parent
        ss_pid = self._find_selfservice_profile_id()
        if ss_pid and parent_id and user_ids:
            for uid in user_ids:
                try:
                    payload = {"input": {
                        "users_id": uid, "profiles_id": ss_pid, "entities_id": parent_id,
                        "is_recursive": 0, "is_dynamic": 0, "is_default": 1
                    }}
                    r1 = requests.post(f"{self.URL_BASE}/User/{uid}/Profile_User",
                                    headers=headers, json=payload, timeout=15)
                    if r1.status_code >= 300:
                        r2 = requests.post(f"{self.URL_BASE}/Profile_User",
                                        headers=headers, json=payload, timeout=15)
                        if r2.status_code >= 300:
                            if "already" not in (r2.text or "").lower():
                                logger.warning(f"Profile_User add failed for user {uid}: {r2.text}")

                    requests.put(
                        f"{self.URL_BASE}/User/{uid}",
                        headers=headers,
                        json={"input": {"id": uid, "profiles_id": ss_pid}},
                        timeout=10
                    ).raise_for_status()

                except Exception as e:
                    logger.warning(f"Self-Service assign failed for user {uid} on parent {parent_id}: {e}")

        logger.info(f"[+] Entité {eid} supprimée avec succès")
        return {"success": True, "message": f"Entité {eid} supprimée avec succès"}

    def delete_and_purge_user(self, user_id: int) -> dict:
        h = self._headers()
        uid = int(user_id)

        def _ok(r): return r.status_code in (200, 204, 404)
        def _json(r):
            try: return r.json()
            except: return r.text

        r = requests.delete(f"{self.URL_BASE}/User/{uid}",
                            headers=h, params={"force_purge": "true"}, timeout=10)
        if _ok(r):
            return {"ok": True, "id": uid,
                    "message": "purged" if r.status_code != 404 else "already absent"}

        s = requests.put(f"{self.URL_BASE}/User/{uid}",
                        headers=h, json={"input": {"id": uid, "is_deleted": 1}},
                        timeout=10)
        if s.status_code >= 300:
            return {"ok": False, "error": "USER_SOFT_DELETE_FAILED",
                    "http": s.status_code, "details": _json(s)}

        r2 = requests.delete(f"{self.URL_BASE}/User/{uid}",
                            headers=h, params={"force_purge": "true"}, timeout=10)
        if _ok(r2):
            return {"ok": True, "id": uid, "message": "purged after soft delete"}

        return {"ok": False, "error": "USER_PURGE_FAILED",
                "http": r2.status_code, "details": _json(r2)}


    def delete_user_profile_on_entity(self, user_id, profile_id, entities_id):
        """
        Delete precise authorization (user, profile, entity).
        True if success, false if not.
        """
        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Erreur session/headers: {e}")
            return False

        # Recover all user authorizations
        search_url = f"{self.URL_BASE}/Profile_User/"
        params = {'users_id': user_id}
        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            results = response.json()
            if not results:
                logger.error("Aucune habilitation trouvée pour cet utilisateur.")
                return False

            # Filter manually to find the right line
            profile_user_id = None
            for item in results:
                if (str(item['users_id']) == user_id and
                    str(item['profiles_id']) == profile_id and
                    str(item['entities_id']) == entities_id):
                    profile_user_id = item['id']
                    break

            if not profile_user_id:
                logger.error(f"Aucune habilitation trouvée pour user_id={user_id}, profile_id={profile_id}, entities_id={entities_id}")
                return False

        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'habilitation: {e}")
            return False

        # Remove the line found
        delete_url = f"{self.URL_BASE}/Profile_User/{profile_user_id}"
        try:
            response = requests.delete(delete_url, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"[+] Habilitation supprimée avec succès (user_id={user_id}, profile_id={profile_id}, entities_id={entities_id})")
            return True
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP lors de la suppression: {e}")
            logger.error(f"Réponse: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la suppression: {e}")
            return False

    def toggle_user_active(self, user_id):
        """
        Switch on the active/inactive state of a GLPI user.
        Returns True if the user becomes active, false if it becomes inactive, none in case of failure.
        """
        try:
            headers = self._headers()
        except Exception as e:
            logger.error(f"Erreur session/headers: {e}")
            return None

        # Read the current state
        get_url = f"{self.URL_BASE}/User/{user_id}"
        try:
            r = requests.get(get_url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json() or {}
            current_active = bool(int(str(data.get("is_active", 1))))
        except Exception as e:
            logger.error(f"Erreur lecture user {user_id}: {e}")
            return None

        # Reverse and push the update
        new_is_active = 0 if current_active else 1
        put_url = f"{self.URL_BASE}/User/{user_id}"
        payload = {"input": {"id": int(user_id), "is_active": new_is_active}}

        try:
            r = requests.put(put_url, headers=headers, json=payload, timeout=10)
            r.raise_for_status()
            logger.info(f"[+] User {user_id} {'activé' if new_is_active == 1 else 'désactivé'}")
            return True if new_is_active == 1 else False
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP lors de l'update user {user_id}: {e}")
            logger.error(f"Réponse: {getattr(r, 'text', '')}")
            return None
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'update user {user_id}: {e}")
            return None

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

def get_glpi_client(tokenuser=None, app_token=None, url_base=None):
    """
    Initializes and returns a GLPI customer with an active session.
    """
    initparametre = AdminDatabase().get_CONNECT_API()
    verifier_parametres(initparametre, [
        "glpi_mmc_app_token", "glpi_url_base_api", "glpi_root_user_token"
    ])

    # Choix des paramètres : valeurs fournies > valeurs en base
    app_token = app_token if app_token else initparametre["glpi_mmc_app_token"]
    url_base = url_base if url_base else initparametre["glpi_url_base_api"]
    user_token = tokenuser if tokenuser else initparametre["glpi_root_user_token"]

    client = GLPIClient(
        app_token=app_token,
        url_base=url_base,
        user_token=user_token,
    )
    client.init_session()

    # Vérifie que le client est bien initialisé et qu'une session est active
    if not client or not hasattr(client, 'SESSION_TOKEN') or not client.SESSION_TOKEN:
        logger.error("Session GLPI non initialisée : impossible d'obtenir un client valide")
        return None

    return client

def get_CONNECT_API(tokenuser=None):
    """
    Initialise une connexion à l'API GLPI et récupère des informations
    sur l'utilisateur et ses profils.
    """
    out_result = {"get_user_info": {}, "get_list_profiles": {}}

    try:
        client = get_glpi_client(tokenuser=tokenuser)
        if not client:
            logger.error("Impossible d'initialiser le client GLPI.")
            return {}

        # Récupération des informations utilisateur
        get_user_info = client.get_user_info()
        logger.info("Informations utilisateur récupérées avec succès.")

        # Récupération de la liste des profils
        get_profiles_info = client.get_list("profiles", is_recursive=True)
        profilslist = [{"id": x["id"], "name": x["name"]}
                       for x in get_profiles_info]
        logger.info("Liste des profils récupérée avec succès.")

        # Mise à jour du résultat
        out_result = {
            "get_user_info": get_user_info,
            "get_list_profiles": profilslist
        }

        # Fermeture propre de la session
        client.kill_session()

    except Exception as e:
        logger.error("Erreur lors de la récupération des informations : %s", traceback.format_exc())

    return out_result

def create_share_dir(tag: str, mode: int = 0o755) -> tuple[str, bool]:
    """
    Crée le dossier /var/lib/pulse2/packages/sharing/<tag>.
    """
    BASE_SHARE = "/var/lib/pulse2/packages/sharing"

    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", tag):
        raise ValueError("tag invalide")

    target = os.path.realpath(os.path.join(BASE_SHARE, tag))
    base_real = os.path.realpath(BASE_SHARE)

    if not target.startswith(base_real + os.sep):
        raise ValueError("Path is not authorized")

    existed = os.path.isdir(target)
    os.makedirs(target, mode=mode, exist_ok=True)
    os.chmod(target, mode)

    return target, not existed

def delete_share_dir(tag: str) -> tuple[str, bool]:
    """Supprime récursivement /var/lib/pulse2/packages/sharing/<tag>."""
    if not tag:                    # <-- garde anti-None pour éviter le TypeError
        return None, False
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", tag):
        raise ValueError("tag invalide")

    target = os.path.realpath(os.path.join(BASE_SHARE, tag))
    base_real = os.path.realpath(BASE_SHARE)
    if not target.startswith(base_real + os.sep):
        raise ValueError("Path is not authorized")
    if not os.path.exists(target):
        return target, False

    shutil.rmtree(target)
    return target, True

# READ
def get_list(type, is_recursive=False, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)
    results = client.get_list(type, is_recursive)
    return results

def get_list_entity_users(tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)
    users=[]
    users = client.get_list_users()
    entity_data = client.get_list_entities()

    for user in users:
        entity_id = user.get("entities_id")
        if entity_id is not None:
            user.update({
                "entity_name": entity_data[entity_id].get("name"),
                "entity_completename": entity_data[entity_id].get("completename"),
                "entity_date_mod": entity_data[entity_id].get("date_mod"),
                "entity_level": entity_data[entity_id].get("level")
            })

    return users

def get_user_info(id_user=None, id_profile=None, id_entity=None):
    """
    Récupère TOUTES les infos d'un utilisateur (même désactivé).
    Retourne un dictionnaire avec is_active et is_disabled.
    """
    user_list = get_user_profile_email(id_user, id_profile, id_entity)
    if not user_list:
        return {}
    return user_list

def get_users_count_by_entity(entity_id, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)
    result = client.get_users_count_by_entity(entity_id)
    return result

def get_list_user_token(tokenuser=None):
    """
    Récupère la liste des IDs des entités accessibles par un utilisateur via l'API GLPI.
    """
    logger.debug("Début de la récupération des entités pour l'utilisateur")

    client = get_glpi_client(tokenuser=tokenuser)
    if not client:
        return []

    try:
        listid = client.get_list("myentities", True)
        if not listid:
            logger.warning("Aucune entité trouvée pour cet utilisateur")
            return []
        result = [x['id'] for x in listid if 'id' in x]
        logger.debug(f"IDs des entités récupérées : {result}")
        return result

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des entités : {e}")
        return []

def get_entity_info(entity_id, tokenuser=None):
    """
    Récupère les informations d'une entité GLPI par son ID.
    """
    client = get_glpi_client(tokenuser=tokenuser)
    entity_info = client.get_entity_info(entity_id)

    entity = entity_info if isinstance(entity_info, dict) else entity_info[0]
    return {
        "id": entity.get("id"),
        "name": entity.get("name"),
        "entities_id": entity.get("entities_id"),
        "completename": entity.get("completename")
    }

def get_profile_name(profile_id, tokenuser=None):
    """
    Récupère le nom d'un profil GLPI par son ID.
    """
    client = get_glpi_client(tokenuser=tokenuser)
    profil_name = client.get_profile_name(profile_id)
    return profil_name

def get_dl_tag(tag):
    dl_tag = AdminDatabase().get_dl_tag(tag)

    return dl_tag

def get_dl_tag_by_entity_id(entity_id):
    """
    Retourne le dl_tag associé à une entité GLPI via son ID.
    """
    meta = get_complete_name(entity_id)
    tag = meta.get("tag")
    dl_tag = AdminDatabase().get_dl_tag(tag)

    return dl_tag

def get_profiles_in_conf(profil_user, tokenuser):
    """
    Lit l'ordre des profils (ini + .local), mappe vers les IDs GLPI,
    puis filtre selon le profil appelant :
      - Super-Admin : voit tout
      - Admin       : ne voit pas Super-Admin
    """
    cfg = ConfigParser(interpolation=None)
    cfg.read([p for p in ('/etc/mmc/plugins/glpi.ini','/etc/mmc/plugins/glpi.ini.local') if os.path.isfile(p)], encoding='utf-8')
    if not cfg.has_section('provisioning_glpi'):
        return []

    raw = cfg.get('provisioning_glpi', 'profiles_order',
                  fallback=cfg.get('provisioning_glpi', 'profiles_oder', fallback=''))
    if not raw:
        return []

    profils = [s.strip("'\" ") for s in re.split(r'[,\s;]+', raw) if s.strip()]

    client = get_glpi_client(tokenuser=tokenuser)
    try:
        glpi = client.get_list('profiles', False) or []
    except Exception:
        glpi = []

    norm = lambda s: re.sub(r'[\s_-]+', '', s or '').lower()
    index = {norm(p.get('name','')): p.get('id') for p in glpi}

    result = [{'name': n, 'id': index.get(norm(n))} for n in profils]

    # --- Filtrage selon le profil appelant ---
    caller = norm(profil_user) if profil_user else ''
    if caller == 'admin':
        result = [r for r in result if norm(r['name']) not in ('superadmin',)]

    missing = [d['name'] for d in result if d['id'] is None]
    if missing:
        logging.getLogger().warning("Profils absents côté GLPI: %s", missing)

    return result

def get_root_token():
    db = AdminDatabase()
    token = db.get_root_token()
    return token

# CREATE
def create_user(
        identifier,     # login (email)
        lastname        = None,
        firstname       = None,
        password        = None,
        phone           = None,
        id_entity       = None,
        id_profile      = None,
        is_recursive    = False,
        caller_profile  = None,
        tokenuser       = None
    ):
    try:
        caller = (caller_profile or "").lower()
        if caller == "admin":
            token_to_use = get_root_token()
            if not token_to_use:
                return {"success": False, "code": -1, "error": "root token unavailable"}
        else:
            token_to_use = tokenuser
            if not token_to_use:
                return {"success": False, "code": -1, "error": "no user token provided"}

        client = get_glpi_client(tokenuser=token_to_use)
        id_user = client.create_user(
            identifier      = identifier,
            lastname        = lastname,
            firstname       = firstname,
            password        = password,
            phone           = phone,
            id_entity       = id_entity,
            id_profile      = id_profile,
            is_recursive    = is_recursive
        )

        api_token = client.generate_token()
        set_user_api_token(int(id_user), api_token)
        return {"ok": True, "id": int(id_user), "api_token": api_token}

    except Exception as e:
        raw = str(e)
        nice = client.extract_glpi_error_message(raw) or raw
        return {"ok": False, "error": nice}

def create_entity_under_custom_parent(parent_entity_id, display_name, user, tokenuser=None):
    """
    Crée l’entité GLPI, le dossier /sharing/<dl_tag>, puis pkgs_shares + règles.
    Retourne l'id GLPI créé.
    """
    try:
        client = get_glpi_client(tokenuser=tokenuser)

        # Création de l’entité GLPI
        tag_uuid = str(uuid.uuid4())
        entity_id = client.create_entity_under_custom_parent(parent_entity_id, display_name, tag_uuid)

        # Création dans saas_organisations
        AdminDatabase().create_entity_under_custom_parent(entity_id, display_name, tag_uuid)

        # Récup méta (nom + nom complet + tag GLPI) et dl_tag interne
        meta = get_complete_name(entity_id) or {}
        name          = meta.get("name", display_name)
        complete_name = meta.get("completename", display_name)
        tag           = meta.get("tag")
        dl_tag        = AdminDatabase().get_dl_tag(tag)

        # Création du dossier /sharing/<dl_tag>
        share_path, _ = create_share_dir(dl_tag)

        # Insert pkgs_shares + règles locales
        pkdb = PkgsDatabase()
        share_id = pkdb.add_pkgs_shares(name, complete_name, dl_tag)
        if user and user != "root":
            pkdb.add_pkgs_rules_local(user, share_id)
        pkdb.add_pkgs_rules_local("root", share_id)

        logger.debug(f"Creation Successful: entity_id={entity_id} share_id={share_id} path={share_path}")

        return entity_id
    except Exception as e:
        logger.error(f"Failed to create Entity : {e}")
        return False

def create_organization(parent_entity_id,
                        name_new_entity,
                        name_user,
                        pwd,
                        profiles_id,
                        tag_value,
                        realname="",
                        firstname="",
                        tokenuser=None):
    """
    Crée une nouvelle organisation (entité GLPI) sous un parent donné,
    ainsi qu'un utilisateur associé avec un profil défini.
    """
    client = get_glpi_client(tokenuser=tokenuser)
    if not client:
        logger.error("Impossible d'initialiser le client GLPI.")
        return []

    try:
        logger.debug(f"CREATION ENTITY : {name_new_entity}")
        id_create_new_entity = client.create_entity_under_custom_parent(
            parent_entity_id, name_new_entity, tag_value
        )
        logger.debug(f"Nouvelle entité créée avec l'ID : {id_create_new_entity}")

        logger.debug(f"CREATION UTILISATEUR : {name_user}")
        id_new_user = client.create_user(
            name_user,
            pwd,
            entities_id=id_create_new_entity,
            realname=realname,
            firstname=firstname,
            profiles_id=profiles_id
        )
        logger.info(f"Nouvel utilisateur créé avec l'ID : {id_new_user}")

        # Attribution d’un profil à l’utilisateur
        logger.debug(f"AFFECTATION PROFIL {profiles_id} à l’utilisateur {id_new_user}")
        client.add_profile_to_user(id_new_user, 3, id_create_new_entity)

        # Réinitialisation des tokens de l’utilisateur
        result = client.update_user(id_new_user, "_reset_api_token", True)
        logger.debug(f"Reset API token : {result}")

        result = client.update_user(id_new_user, "_reset_personal_token", True)
        logger.debug(f"Reset personal token : {result}")

        return [id_create_new_entity, id_new_user, profiles_id, result]

    except Exception as e:
        logger.error("Erreur lors de la création de l'organisation : %s", traceback.format_exc())
        return []
    finally:
        if client:
            client.kill_session()

# UPDATE
def update_user(user_id, item_name, new_value, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)
    result = client.update_user(user_id, item_name, new_value)
    return result

def set_user_email(user_id, email, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)
    return client.set_user_email(user_id, email)

def update_entity(entity_id, field_name, new_name, parent_id, tokenuser=None):
    """
    Met à jour l'entité GLPI, puis synchronise AdminDB et pkgs_shares (name/comments)
    en ciblant pkgs_shares via le dl_tag.
    """
    client = get_glpi_client(tokenuser=tokenuser)

    try:
        # Récupération du dl_tag
        dl_tag = get_dl_tag_by_entity_id(entity_id)

        # Màj GLPI
        ok = client.update_entity(entity_id, field_name, new_name, parent_id)
        if not ok:
            return ok

        # MàJ AdminDB
        AdminDatabase().update_entity(entity_id, new_name)

        # Comments = completename à jour
        meta = get_complete_name(entity_id) or {}
        complete_name = meta.get("completename") or new_name

        # Màj pkgs_shares via dl_tag
        if dl_tag:
            PkgsDatabase().update_pkgs_shares_names_by_dl_tag(dl_tag, new_name, complete_name)
        else:
            logger.debug(f"Skipped pkgs_shares update: no dl_tag for entity_id={entity_id}")

        logger.debug(f"Update Successful: entity_id={entity_id} new_name={new_name}")
        return ok

    except Exception as e:
        logger.error(f"Failed to update Entity: {e!r}")
        return False

def switch_user_profile(
    user_id: int,
    new_profile_id: int,
    entities_id: int,
    is_recursive: int = 0,
    caller_profile: str | None = None,
    tokenuser: str | None = None,
) -> dict:
    caller = (caller_profile or "").lower()
    if caller == "admin":
        token_to_use = get_root_token()
        if not token_to_use:
            return {"success": False, "code": -1, "error": "root token unavailable"}
    else:
        token_to_use = tokenuser
        if not token_to_use:
            return {"success": False, "code": -1, "error": "no user token provided"}

    client = get_glpi_client(tokenuser=token_to_use)

    return client.switch_user_profile(
        user_id=int(user_id),
        new_profile_id=int(new_profile_id),
        entities_id=int(entities_id),
        is_recursive=int(is_recursive),
    )

def switch_user_entity(user_id: int, new_entity_id: int, tokenuser=None) -> dict:
    client = get_glpi_client(tokenuser=tokenuser)
    return client.switch_user_entity(user_id=int(user_id), new_entity_id=int(new_entity_id), tokenuser=tokenuser)

# DELETE
def delete_and_purge_user(user_id):
    try:
        client = get_glpi_client()
        result = client.delete_and_purge_user(user_id)
        return result
    except Exception as e:
        raw = str(e)
        nice = client.extract_glpi_error_message(raw) or raw
        return {"ok": False, "error": nice}

def delete_entity(entity_id: int, tokenuser=None):
    """
    Supprime le dossier /sharing/<dl_tag>, les lignes pkgs_* liées,
    puis l'entité GLPI et l'entrée AdminDB. Logs courts.
    """
    client = get_glpi_client(tokenuser=tokenuser)

    try:
        # Récupération du dl_tag
        dl_tag = get_dl_tag_by_entity_id(entity_id)

        # Suppression du repertoire /sharing/<dl_tag>
        if dl_tag:
            delete_share_dir(dl_tag)
        else:
            logger.debug(f"Skipped FS delete: no dl_tag for entity_id={entity_id}")

        # Suppression pkgs_shares + rules_local via dl_tag
        if dl_tag:
            share_id = PkgsDatabase().get_pkgs_share_id_by_dl_tag(dl_tag) if hasattr(PkgsDatabase, "get_pkgs_share_id_by_dl_tag") else None
            if share_id is None:
                meta = get_complete_name(entity_id) or {}
                share = PkgsDatabase().find_share_by_entity_names(meta.get("name",""), meta.get("completename",""))
                share_id = share["id"] if share else None

            if share_id is not None:
                PkgsDatabase().delete_rules_by_share_ids([share_id])
                PkgsDatabase().delete_shares_by_ids([share_id])

        # Suprression GLPI + AdminDB
        result = client.delete_entity(entity_id)
        if result.get("success"):
            AdminDatabase().delete_entity(entity_id)

        logger.debug(f"Delete Successful: entity_id={entity_id} dl_tag={dl_tag}")
        return result

    except Exception as e:
        logger.error(f"Failed to delete Entity: {e!r}")
        return {"success": False, "message": str(e)}

def delete_user_profile_on_entity(user_id, profile_id, entities_id, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)
    result = client.delete_user_profile_on_entity(user_id, profile_id, entities_id)
    return result

def toggle_user_active(user_id, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)
    result = client.toggle_user_active(user_id)
    return result

# STATS
def get_counts_by_entity(entities):
    """
    Retourne pour chaque entité le nombre de machines et d'utilisateurs.
    """
    logger.error(f"get_counts_by_entity {entities}")

    listid = []
    for t in entities:
        if isinstance(t, dict):
            listid.append(t['id'])
        else:
            listid.append(t)

    result = get_entities_with_counts(entities=listid)
    return result

def get_counts_by_entity_root(filter, start, end, entities=None):
    """
    Récupère les statistiques des entités GLPI (machines, utilisateurs, IDs).
    """
    result  = get_entities_with_counts_root(filter=filter, start=start, end=end, entities=entities)
    return result


# ---- PROVIDER MANAGEMENT ----
# READ
def get_providers(login: str, client: str | None = None) -> list[dict]:
    try:
        db = AdminDatabase()
        return db.get_providers_all() if (login or "").strip() == "root" else db.get_providers_by_client((client or "MMC").strip())
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des fournisseurs : {e}")
        return []

# CREATE
def create_provider(data: dict) -> dict:
    try:
        db = AdminDatabase()
        return db.create_provider(data)
    except Exception as e:
        logger.error(f"Erreur lors de la création du fournisseur : {e}")
        return {"ok": False, "error": str(e)}

# UPDATE
def update_provider(data: dict) -> dict:
    try:
        db = AdminDatabase()
        return db.update_provider(data)
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du fournisseur : {e}")
        return {"ok": False, "error": str(e)}

# DELETE
def delete_provider(provider_id: int) -> dict:
    try:
        pid = int(provider_id or 0)
        if pid <= 0:
            return {"ok": False, "deleted": 0, "id": 0, "error": "invalid id"}
        db = AdminDatabase()
        return db.delete_provider(pid)
    except Exception as e:
        return {"ok": False, "deleted": 0, "id": 0, "error": str(e)}