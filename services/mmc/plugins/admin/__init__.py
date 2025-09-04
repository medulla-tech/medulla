# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.version import getVersion, getRevision

from mmc.plugins.admin.config import AdminConfig

# Import for Database
from pulse2.database.admin import AdminDatabase
from mmc.plugins.glpi import get_entities_with_counts, get_entities_with_counts_root, set_user_api_token, get_user_profile_email

import traceback
import requests
import logging
import base64
import random
import string
import json
import uuid
import re

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
    - ## change_user_profile todo delete et recreate profile pour user voir delete_profile_from_user et add_profile_to_user
    - create_entity_under_custom_parent(self, parent_entity_id, name): Creates an entity under a specified parent.
    - create_user(self, name_user, pwd, entities_id=None, realname=None, firstname=None): Creates a new user.
    - update_entity(self, entity_id, item_name, new_value): Updates an entity with new values.
    - update_user(self, user_id, item_name, new_value): Updates a user with new values.
    - add_profile_to_user(self, user_id, profile_id, entities_id, is_recursive=0, is_dynamic=0, is_default=0): Adds a profile to a user.
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

    def __clean_none_values(self, obj):
        """
        Remplace récursivement toutes les occurrences de None/null par une chaîne vide ("")
        dans un objet JSON de type dict ou list.

        Args:
            obj (dict | list | any): L'objet JSON ou une valeur à traiter.

        Returns:
            dict | list | str | any: L'objet avec tous les None remplacés par "".
        """
        # Si c'est un dictionnaire, on applique la fonction à chaque valeur
        if isinstance(obj, dict):
            return {k: self.__clean_none_values(v) for k, v in obj.items()}
        # Si c'est une liste, on applique la fonction à chaque élément
        elif isinstance(obj, list):
            return [self.__clean_none_values(v) for v in obj]
        # Si la valeur est None, on la remplace par une chaîne vide
        elif obj is None:
            return ""
        # Sinon, on retourne la valeur telle quelle
        else:
            return obj

    def generate_token(self, length=40):
        """
        Génère un jeton (token) aléatoire composé de lettres et de chiffres.

        Le jeton est généré en utilisant un ensemble de caractères alphanumériques
        (lettres majuscules, lettres minuscules et chiffres). La longueur par défaut
        du jeton est de 32 caractères, mais elle peut être personnalisée.

        Args:
            length (int, optional): Longueur souhaitée pour le jeton généré. Par défaut, 32.

        Returns:
            str: Une chaîne de caractères alphanumériques aléatoires de la longueur spécifiée.

        Example:
            >>> token = generate_token()
            >>> print(token)  # Exemple de sortie : "aB3x9KpL2qR7vY4zW1sT5uV8nM6"
            >>> custom_token = generate_token(16)
            >>> print(custom_token)  # Exemple de sortie : "fG7hJ9kL2mN4"
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


    def kill_session(self):
        """
        Termine la session courante en envoyant une requête au serveur pour invalider le jeton de session.

        Cette méthode envoie une requête GET à l'endpoint `/killSession` de l'API,
        en utilisant les jetons d'application et de session pour authentification.
        Si la requête réussit (code HTTP 200), le jeton de session est réinitialisé à `None`.

        Raises:
            requests.exceptions.HTTPError: Si la requête échoue (code HTTP différent de 200),
                une exception est levée avec les détails de l'erreur.

        Notes:
            - Si aucun jeton de session (`SESSION_TOKEN`) n'est défini, un avertissement est logged
            et la méthode retourne immédiatement.
            - En cas de succès, un message de confirmation est logged, ainsi que la réponse JSON
            du serveur (en mode debug).
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

    def _headers(self):
        if not self.APP_TOKEN:
            raise Exception("App-Token manquant.")
        if not self.SESSION_TOKEN:
            raise Exception("Session non initialisée (connecte le client avant).")
        return {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN,
            "Content-Type": "application/json",
        }

    @staticmethod
    def extract_glpi_error_message(text: str) -> str | None:
        """
        Retourne uniquement le message lisible GLPI
        (ex: Ajout impossible. L'utilisateur existe déjà.)
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

    # 1) Création "nue" de l'utilisateur (pas d’upsert de lien ici)
    def create_user_basic(self, name_user, pwd, entities_id,
                        realname=None, firstname=None, email=None):
        headers = self._headers()

        if not name_user or not pwd:
            raise ValueError("name_user et pwd requis")

        payload = {
            "input": {
                "name": name_user,
                "password": pwd,
                "password2": pwd,
                "realname": realname,
                "firstname": firstname,
                "language": "fr_FR",
                "is_active": 1,
                "entities_id": int(entities_id)
            }
        }
        if email:
            payload["input"]["email"] = email

        r = requests.post(f"{self.URL_BASE}/User", headers=headers, json=payload, timeout=15)
        if r.status_code >= 300:
            self._raise_glpi("Create User", r)

        data = r.json() if "application/json" in (r.headers.get("Content-Type") or "") else {}
        user_id = int(data.get("id") or 0)
        if user_id <= 0:
            raise RuntimeError(f"Create User failed: HTTP {r.status_code} — réponse inattendue: {data}")
        return user_id

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

    def set_user_email(self, user_id, email):
        if not email:
            return
        headers = self._headers()

        requests.put(f"{self.URL_BASE}/User/{int(user_id)}",
                    headers=headers,
                    json={"input": {"id": int(user_id), "email": email}},
                    timeout=10).raise_for_status()

        gr = requests.get(f"{self.URL_BASE}/User/{int(user_id)}/UserEmail",
                        headers=headers, timeout=10)
        gr.raise_for_status()
        erows = gr.json()
        erows = [erows] if isinstance(erows, dict) else (erows or [])

        same = None
        for e in erows:
            if (e.get("email") or "").lower() == email.lower():
                same = e
                break

        if same:
            uid = int(same.get("id") or 0)
            if uid:
                requests.put(f"{self.URL_BASE}/UserEmail/{uid}",
                            headers=headers,
                            json={"input": {"id": uid, "is_default": 1}},
                            timeout=10).raise_for_status()
        else:
            requests.post(f"{self.URL_BASE}/UserEmail",
                        headers=headers,
                        json={"input": {"users_id": int(user_id),
                                        "email": email,
                                        "is_default": 1}},
                        timeout=10).raise_for_status()

        gr = requests.get(f"{self.URL_BASE}/User/{int(user_id)}/UserEmail",
                        headers=headers, timeout=10)
        gr.raise_for_status()
        for e in (gr.json() or []):
            try:
                eid = int(e.get("id") or 0)
                if eid and (e.get("email") or "").lower() != email.lower() and int(e.get("is_default") or 0) == 1:
                    requests.put(f"{self.URL_BASE}/UserEmail/{eid}",
                                headers=headers,
                                json={"input": {"id": eid, "is_default": 0}},
                                timeout=10).raise_for_status()
            except Exception:
                pass

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

    def create_user(self,
                    name_user,
                    pwd,
                    entities_id,
                    profiles_id,
                    realname=None,
                    firstname=None,
                    email=None,
                    is_recursive=False,
                    is_default=True,
                    unique_entity=True,
                    do_rollback_on_error=True) -> int:
        user_id = None
        try:
            user_id = self.create_user_basic(
                name_user, pwd, entities_id,
                realname=realname, firstname=firstname, email=email
            )
            self.add_profile_to_user(
                user_id=user_id,
                profile_id=profiles_id,
                entities_id=entities_id,
                is_recursive=1 if is_recursive else 0,
                is_dynamic=0,
                is_default=1 if is_default else 0
            )
            if email:
                self.set_user_email(user_id, email)
            return user_id
        except Exception as e:
            if do_rollback_on_error and user_id:
                self.delete_and_purge_user(user_id)
            raise RuntimeError(f"Echec création utilisateur GLPI: {e}") from e


    def get_list(self, type: str, is_recursive: bool = False):
        """
        Récupère une liste d'objets GLPI (utilisateurs, profils ou entités).

        Cette méthode interroge l'API GLPI en fonction du `type` demandé et retourne
        la liste correspondante. Pour les entités, il est possible d'activer
        la récupération récursive via `is_recursive`.

        Paramètres
        ----------
        type : str
            Le type de liste à récupérer. Valeurs permises :
            - "users"      : liste des utilisateurs
            - "profiles"   : liste des profils
            - "entities"   : liste des entités
            - "myentities" : liste des entités accessibles à l'utilisateur courant
                            (respecte `is_recursive`)
        is_recursive : bool, optionnel (défaut = False)
            Indique si les entités doivent être récupérées de manière récursive
            (applicable uniquement si `type="myentities"`).

        Retour
        ------
        list :
            - Si `type="users"`, retourne une liste d'utilisateurs.
            - Si `type="profiles"`, retourne une liste de profils (et met à jour self.profiles).
            - Si `type="entities"`, retourne une liste d'entités.
            - Si `type="myentities"`, retourne une liste d'entités accessibles via la clé `myentities`.

        Exceptions
        ----------
        Exception
            Levée si la session n'est pas initialisée (`SESSION_TOKEN` absent).
        ValueError
            Levée si le paramètre `type` est invalide (non inclus dans la liste des valeurs permises).

        Notes
        -----
        - La méthode supprime automatiquement les valeurs `None` dans la réponse JSON.
        - En cas d'erreur HTTP (code != 200), une exception `requests.HTTPError` est levée.
        """

        if not self.SESSION_TOKEN:
            logger.error("Session non initialisée. Veuillez initialiser la session.")
            raise Exception("Session non initialisée. Veuillez initialiser la session.")

        # Vérification stricte des valeurs permises
        allowed_types = {"users", "profiles", "entities", "myentities"}
        if type not in allowed_types:
            logger.error("Type invalide fourni : %s", type)
            raise ValueError(f"Type invalide '{type}'. Valeurs permises : {allowed_types}")

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }

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
        Récupère la liste des utilisateurs GLPI avec leurs informations principales.

        La fonction s'appuie sur `get_list('users', True)` pour extraire
        l'ensemble des utilisateurs, puis formate les résultats dans une
        structure simplifiée contenant uniquement les champs pertinents.

        ⚠️ Remarque :
        -------------
        - Les informations retournées dépendent des privilèges associés au token utilisé
        lors de l'initialisation du client GLPI (root ou utilisateur).
        - Certains champs peuvent être vides ou non présents selon la configuration GLPI.

        Retour :
        --------
        list[dict] :
            Liste d'utilisateurs, chaque élément contient :
            {
                "id": int,                # ID de l'utilisateur
                "name": str,              # Identifiant (login) de l'utilisateur
                "lastname": str,          # Nom réel (realname)
                "is_active": int | bool,  # Statut actif/inactif
                "profiles_id": int,       # ID du profil principal
                "last_login": str,        # Date de dernière connexion
                "date_mod": str,          # Date de dernière modification
                "date_creation": str,     # Date de création du compte
                "entities_id": int,       # ID de l'entité associée
                "locations_id": int,      # ID de la localisation associée
                "groups_id": int          # ID du groupe associé
            }
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
        Récupère la liste des entités disponibles et les organise dans un dictionnaire.

        Cette méthode appelle `get_list` pour obtenir la liste complète des entités,
        puis reformate les résultats en un dictionnaire où chaque clé est l'identifiant
        de l'entité et la valeur est un dictionnaire contenant les informations principales
        de l'entité (nom, nom complet, date de modification et niveau).

        Returns:
            dict: Un dictionnaire associant les identifiants des entités à leurs informations.
                Chaque entrée du dictionnaire a la structure suivante :
                {
                    'name': (str) Nom court de l'entité,
                    'completename': (str) Nom complet de l'entité,
                    'date_mod': (str) Date de dernière modification,
                    'level': (int) Niveau de l'entité
                }

        Example:
            >>> entities = client.get_list_entities()
            >>> print(entities)
            {
                '1': {
                    'name': 'Root Entity',
                    'completename': 'Root Entity',
                    'date_mod': '2025-08-22 12:00:00',
                    'level': 0
                },
                '2': {
                    'name': 'Sub Entity',
                    'completename': 'Root Entity > Sub Entity',
                    'date_mod': '2025-08-21 10:30:00',
                    'level': 1
                }
            }
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

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }

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

    def delete_entity(self, entity_id):
        """
        Supprime une entité par son ID.

        Args:
            entity_id (int): L'ID de l'entité à supprimer.

        Returns:
            dict: { "success": bool, "message": str }
        """
        if not self.SESSION_TOKEN:
            msg = "Session non initialisée. Veuillez initialiser la session."
            logger.error(msg)
            return {"success": False, "message": msg}

        if not entity_id:
            msg = "[!] Usage: delete_entity <entity_id>"
            logger.error(msg)
            return {"success": False, "message": msg}

        headers = {
            "App-Token": self.APP_TOKEN,
            "Session-Token": self.SESSION_TOKEN
        }

        response = requests.delete(
            f"{self.URL_BASE}/Entity/{entity_id}",
            headers=headers
        )

        if response.status_code >= 300:
            try:
                error_data = response.json()
                if isinstance(error_data, list) and len(error_data) >= 2:
                    return {"success": False, "message": error_data[1]}
                else:
                    return {"success": False, "message": response.text}
            except ValueError:
                return {"success": False, "message": response.text}

        logger.info(f"[+] Entité {entity_id} supprimée avec succès")
        return {"success": True, "message": f"Entité {entity_id} supprimée avec succès"}

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

    def switch_user_profile(self,
                            user_id,
                            new_profile_id,
                            entities_id,
                            is_recursive=0,
                            is_dynamic=0,
                            is_default=1,
                            tokenuser=None):
        """
        Changes the active profile of a GLPI user by deleting the old profiles,
        By adding the new one, then updating the active profile in the user sheet.

        Args:
            user_id (int): User ID
            new_profile_id (int): ID of the new profile
            entities_id (int): ID of the entity
            is_recursive (int): Apply to sub-entities (0/1)
            is_dynamic (int): Dynamic profile (0/1)
            is_default (int): Default profile (0/1)

        Returns:
            dict: Operation result
        """
        client = get_glpi_client(tokenuser=tokenuser)

        client.init_session()

        headers = {
            "App-Token": client.APP_TOKEN,
            "Session-Token": client.SESSION_TOKEN
        }

        resp = requests.get(f"{client.URL_BASE}/User/{user_id}/Profile_User/", headers=headers)
        if resp.status_code == 200:
            profiles_list = resp.json()
            for prof in profiles_list:
                prof_id = prof.get('id')
                if prof_id:
                    requests.delete(f"{client.URL_BASE}/User/{user_id}/Profile_User/{prof_id}", headers=headers)

        payload = {
            "input": {
                "users_id": user_id,
                "profiles_id": new_profile_id,
                "entities_id": entities_id,
                "is_recursive": is_recursive,
                "is_dynamic": is_dynamic,
                "is_default": is_default
            }
        }

        requests.post(f"{client.URL_BASE}/User/{user_id}/Profile_User/", headers=headers, json=payload)

        payload_update = {
            "input": {
                "id": user_id,
                "profiles_id": new_profile_id
            }
        }

        requests.put(f"{client.URL_BASE}/User/{user_id}", headers=headers, json=payload_update)

        client.kill_session()

        return {"success": True, "message": "Profil changé et mis à jour avec succès"}


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

def get_CONNECT_API(tokenuser=None):
    """
    Initialise une connexion à l'API GLPI et récupère des informations
    sur l'utilisateur et ses profils.

    Args:
        tokenuser (str, optional): Jeton utilisateur GLPI.
                                   Si None (par défaut), le token root sera utilisé.

    Returns:
        dict:
            {
                "get_user_info": <infos utilisateur>,
                "get_list_profiles": [ { "id": <id>, "name": <nom> }, ... ]
            }
            Retourne {} si la récupération échoue.
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

def get_glpi_client(tokenuser=None, app_token=None, url_base=None):
    """
    Initialise et retourne un client GLPI avec une session active.

    Cette fonction permet de créer un client GLPI de manière flexible :
    - Si `tokenuser`, `app_token` ou `url_base` sont fournis, ils seront utilisés
      pour initialiser le client.
    - Sinon, les valeurs par défaut sont chargées depuis la base de données
      (via `AdminDatabase().get_CONNECT_API()`).

    Args:
        tokenuser (str, optional): Jeton d'accès de l'utilisateur GLPI.
                                   Si None, le token root configuré sera utilisé.
        app_token (str, optional): Jeton d'application GLPI.
                                   Si None, la valeur configurée en base sera utilisée.
        url_base (str, optional): URL de l'API GLPI.
                                  Si None, la valeur configurée en base sera utilisée.

    Returns:
        GLPIClient | None:
            - Une instance de `GLPIClient` initialisée et authentifiée si la session est valide.
            - None si l'initialisation ou l'ouverture de session échoue.
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

def get_list(type, is_recursive=False, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)

    results = client.get_list(type, is_recursive)

    return results

def create_user(name_user, pwd, entities_id=None, profiles_id=None,
                realname=None, firstname=None, email=None,
                is_recursive=False, is_default=True,
                tokenuser=None, return_token=True):
    try:
        client = get_glpi_client(tokenuser=tokenuser)
        user_id = client.create_user(
            name_user=name_user, pwd=pwd, entities_id=entities_id, profiles_id=profiles_id,
            realname=realname, firstname=firstname, email=email,
            is_recursive=is_recursive, is_default=is_default
        )

        api_token = client.generate_token()
        set_user_api_token(int(user_id), api_token)
        return {"ok": True, "id": int(user_id), "api_token": api_token}

    except Exception as e:
        raw = str(e)
        nice = client.extract_glpi_error_message(raw) or raw
        return {"ok": False, "error": nice}

def delete_and_purge_user(user_id):
    try:
        client = get_glpi_client()
        result = client.delete_and_purge_user(user_id)
        return result
    except Exception as e:
        raw = str(e)
        nice = client.extract_glpi_error_message(raw) or raw
        return {"ok": False, "error": nice}

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

def get_user_info(id_user=None, id_profile=None):
    user_list = get_user_profile_email(id_user, id_profile)
    return user_list

def get_users_count_by_entity(entity_id, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)

    result = client.get_users_count_by_entity(entity_id)

    return result

def get_counts_by_entity(entities):
    """
    Retourne pour chaque entité le nombre de machines et d'utilisateurs.
    Args:
        entities (list): peut être une liste d'entiers [1, 2] ou une liste de dicts [{'id': 1}, {'id': 2}]
    Returns:
        dict: { "<entity_id>": {"machines": int, "users": int}, ... }
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


def get_counts_by_entity_root( filter, start, end,  entities=None):
    """
    Récupère les statistiques des entités GLPI (nombre de machines,
    nombre d'utilisateurs et IDs des utilisateurs), avec options
    de filtrage, pagination et restriction sur une liste d'entités.

    Cette fonction est un raccourci simplifié de `get_entities_with_counts_root`,
    qui utilise la configuration par défaut et ne nécessite pas de session SQLAlchemy
    ni le paramètre `colonne`.

    Paramètres :
    -----------
    filter : str
        Chaîne de filtrage appliquée sur `completename` (LIKE %filter%).
        Si None ou "", pas de filtre.
    start : int
        Index de départ (OFFSET). Si -1, pas de pagination.
    end : int
        Index de fin (inclus). Si -1, pas de pagination.
    entities : list[int], optionnel
        Liste d’IDs d’entités à filtrer. Si None, toutes.

    Retour :
    -------
    dict :
        {
        "total_count": int,     # Nombre total d'entités
        "filtered_count": int,  # Nombre d'entités après filtrage
        "data": ...             # Données des entités avec leurs compteurs
        }
    """
    result  = get_entities_with_counts_root( filter=filter, start=start, end=end,  entities=entities)
    return result


def get_list_user_token(tokenuser=None):
    """
    Récupère la liste des IDs des entités accessibles par un utilisateur via l'API GLPI.

    Args:
        token (str, optional):
            Le token d'authentification de l'utilisateur GLPI.
            Si None (par défaut), le token root sera utilisé.

    Returns:
        list: Une liste d'IDs d'entités accessibles par l'utilisateur.
              Retourne une liste vide si aucune entité n'est trouvée ou en cas d'erreur.
    """
    logger.debug("Début de la récupération des entités pour l'utilisateur")

    client = get_glpi_client(tokenuser=tokenuser)
    if not client:
        return []

    try:
        # Récupère la liste des entités accessibles par l'utilisateur
        listid = client.get_list("myentities", True)

        # Vérifie que la réponse n'est pas vide
        if not listid:
            logger.warning("Aucune entité trouvée pour cet utilisateur")
            return []

        # Extrait les IDs des entités
        result = [x['id'] for x in listid if 'id' in x]
        logger.debug(f"IDs des entités récupérées : {result}")
        return result

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des entités : {e}")
        return []


def get_entity_info(entity_id, tokenuser=None):
    """
    Récupère les informations d'une entité GLPI par son ID.

    ⚠️ Remarque :
    -------------
    - Si `tokenuser` est None, les informations sont récupérées avec le token root
      (accès complet).
    - Si `tokenuser` est défini, seules les informations accessibles à cet utilisateur
      seront retournées, selon ses privilèges et droits sur l'entité.

    Paramètres :
    ------------
    entity_id : int
        ID de l'entité à récupérer.
    tokenuser : str, optionnel
        Jeton utilisateur GLPI.
        Si None (par défaut), le token root sera utilisé.

    Retour :
    --------
    dict :
        {
            "id": <ID de l'entité>,
            "name": <Nom de l'entité>,
            "entities_id": <ID de l'entité parente>,
            "completename": <Nom complet hiérarchique>
        }
        Le contenu peut varier selon les privilèges de l'utilisateur.
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

    ⚠️ Remarque :
    -------------
    - Si `tokenuser` est None, la récupération se fait avec le token root
      (accès complet).
    - Si `tokenuser` est défini, l'accès dépend des privilèges de l'utilisateur.

    Paramètres :
    ------------
    profile_id : int
        ID du profil à récupérer.
    tokenuser : str, optionnel
        Jeton utilisateur GLPI.
        Si None (par défaut), le token root sera utilisé.

    Retour :
    --------
    str :
        Nom du profil associé à l'ID.
    """
    client = get_glpi_client(tokenuser=tokenuser)

    profil_name = client.get_profile_name(profile_id)
    return profil_name

def create_entity_under_custom_parent(parent_entity_id, name, tokenuser=None):

    """
    Crée une nouvelle entité GLPI sous un parent personnalisé,
    et l'enregistre également dans la base interne.

    ⚠️ Remarque :
    -------------
    - Si `tokenuser` est None, la création se fait avec le token root
      (accès complet).
    - Si `tokenuser` est défini, l'utilisateur doit disposer des droits
      suffisants pour créer une entité sous le parent spécifié.

    Paramètres :
    ------------
    parent_entity_id : int
        ID de l'entité parente sous laquelle créer la nouvelle entité.
    name : str
        Nom de la nouvelle entité à créer.
    tokenuser : str, optionnel
        Jeton utilisateur GLPI.
        Si None (par défaut), le token root sera utilisé.

    Retour :
    --------
    int :
        ID de la nouvelle entité créée dans GLPI.
    """

    client = get_glpi_client(tokenuser=tokenuser)

    tag_value = str(uuid.uuid4())
    create_entities_in_glpi = client.create_entity_under_custom_parent(parent_entity_id, name, tag_value)

    AdminDatabase().create_entity_under_custom_parent(create_entities_in_glpi, name, tag_value)

    return create_entities_in_glpi

def update_entity(entity_id, item_name, new_entity_name, parent_id, tokenuser=None):
    """
    Met à jour une entité GLPI et synchronise la mise à jour
    dans la base interne.

    ⚠️ Remarque :
    -------------
    - Si `tokenuser` est None, la mise à jour se fait avec le token root
      (accès complet).
    - Si `tokenuser` est défini, l'utilisateur doit avoir les privilèges
      nécessaires pour modifier cette entité.

    Paramètres :
    ------------
    entity_id : int
        ID de l'entité à mettre à jour.
    item_name : str
        Champ de l'entité à modifier (par ex. "name").
    new_entity_name : str
        Nouvelle valeur pour le champ.
    parent_id : int
        ID de l'entité parente.
    tokenuser : str, optionnel
        Jeton utilisateur GLPI.
        Si None (par défaut), le token root sera utilisé.

    Retour :
    --------
    dict | bool :
        Résultat de l'opération renvoyé par l'API GLPI.
        False en cas d'échec ou si l'utilisateur n'a pas les droits.
    """

    client = get_glpi_client(tokenuser=tokenuser)

    result = client.update_entity(entity_id, item_name, new_entity_name, parent_id)

    if result:
        AdminDatabase().update_entity(entity_id, new_entity_name)

    return result

def delete_entity(entity_id, tokenuser=None):
    """
    Supprime une entité GLPI et la supprime également de la base interne.

    ⚠️ Remarque :
    -------------
    - Si `tokenuser` est None, la suppression se fait avec le token root
      (accès complet).
    - Si `tokenuser` est défini, l'utilisateur doit disposer des droits
      nécessaires pour supprimer l'entité.

    Paramètres :
    ------------
    entity_id : int
        ID de l'entité à supprimer.
    tokenuser : str, optionnel
        Jeton utilisateur GLPI.
        Si None (par défaut), le token root sera utilisé.

    Retour :
    --------
    dict :
        Réponse de l'API GLPI contenant au minimum une clé "success".
        Exemple : {"success": True}
    """
    client = get_glpi_client(tokenuser=tokenuser)

    result = client.delete_entity(entity_id)

    if result["success"]:
        AdminDatabase().delete_entity(entity_id)

    return result

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

    Étapes effectuées :
    -------------------
    1. Connexion à l'API GLPI (via `get_glpi_client` avec le token root par défaut
       ou le `tokenuser` fourni).
    2. Création d'une nouvelle entité sous l'entité parente spécifiée.
    3. Création d'un utilisateur rattaché à cette nouvelle entité.
    4. Attribution d'un profil à l'utilisateur.
    5. Réinitialisation des tokens API et personnel de l'utilisateur.

    Paramètres :
    ------------
    parent_entity_id : int
        ID de l'entité parente sous laquelle créer la nouvelle entité.
    name_new_entity : str
        Nom de la nouvelle entité à créer.
    name_user : str
        Nom du nouvel utilisateur à créer.
    pwd : str
        Mot de passe du nouvel utilisateur.
    profiles_id : int
        ID du profil à assigner à l'utilisateur.
    tag_value : str
        Valeur du tag à appliquer à l'entité.
    realname : str, optionnel
        Nom de famille de l'utilisateur.
    firstname : str, optionnel
        Prénom de l'utilisateur.
    tokenuser : str, optionnel
        Jeton utilisateur GLPI.
        Si None (par défaut), le token root sera utilisé.

    Retour :
    --------
    list :
        [ id_create_new_entity, id_new_user, profiles_id, result_update_user ]
        - id_create_new_entity : ID de l'entité créée
        - id_new_user : ID du nouvel utilisateur
        - profiles_id : Profil attribué
        - result_update_user : Résultat de la mise à jour de l'utilisateur (reset tokens)

        Retourne [] en cas d'erreur.
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

