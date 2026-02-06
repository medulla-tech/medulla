# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.version import getVersion, getRevision

from mmc.plugins.admin.config import AdminConfig

# Import for Database
from pulse2.database.admin import AdminDatabase
from pulse2.database.pkgs import PkgsDatabase

from mmc.plugins.glpi import get_entities_with_counts, get_entities_with_counts_root, set_user_api_token, get_user_profile_email, get_complete_name, get_user_identifier, list_entity_ids_subtree, list_user_ids_in_subtree, list_computer_ids_in_subtree
from mmc.support.apirest.glpi import GLPIClient
from mmc.support.apirest.glpi import verifier_parametres
from configparser import ConfigParser
import subprocess
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
#
# def verifier_parametres(dictctrl, cles_requises):
#     # Vérifier chaque clé
#     for cle in cles_requises:
#         if cle not in dictctrl or dictctrl[cle] is None:
#             # Lever une exception si une clé est manquante ou None
#             raise ValueError(
#                 f"La clé '{cle}' est manquante ou None dans le dictionnaire initparametre.")


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
    BASE_SHARE = "/var/lib/pulse2/packages/sharing"
    if not tag:
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

def delete_agent_dir(tag: str) -> tuple[str, bool]:
    """Supprime le repertoire de l'agent /var/lib/pulse2/medulla_agent/<dl_tag>."""
    BASE_AGENT = "/var/lib/pulse2/medulla_agent"
    if not tag:
        return None, False
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", tag):
        raise ValueError("tag invalide")

    target = os.path.realpath(os.path.join(BASE_AGENT, tag))
    base_real = os.path.realpath(BASE_AGENT)
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

def get_user_info(id_user=None, id_profile=None, id_entity=None, filters=None):
    """
    Récupère TOUTES les infos d'un utilisateur (même désactivé).
    'filters' est un dict optionnel pour filtrer
    Retourne un dictionnaire avec is_active et is_disabled.
    """
    user = get_user_profile_email(
        id_user=id_user,
        id_profile=id_profile,
        id_entity=id_entity,
        filters=filters or {}
    )
    if not user:
        return {}
    return user

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

def run_generate_medulla_agent_async(tag):
    """
    Lance le script avec le tag
    Retourne le PID si démarré, sinon None.
    """
    script_path = "/usr/sbin/generate_medulla_agent.sh"
    if not tag or not re.match(r'^[A-Za-z0-9._:-]+$', tag):
        return None
    if not (os.path.exists(script_path) and os.access(script_path, os.X_OK)):
        return None

    try:
        proc = subprocess.Popen(
            [script_path, tag],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
            env=os.environ.copy(),
        )
        return proc.pid
    except Exception:
        return None
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

        # Creation of the sharing rule for the user who has just been created
        final_entity_id = int(id_entity) if id_entity not in (None, '', 0) else 0

        entity_info = get_entity_info(final_entity_id)
        entity_name             = entity_info.get('name')
        entity_completename     = entity_info.get('completename')

        pkdb = PkgsDatabase()

        if final_entity_id == 0:
            share_row = pkdb.find_global_share()
        else:
            entity_info = get_entity_info(final_entity_id) or {}
            entity_name = entity_info.get('name')
            entity_completename = entity_info.get('completename')
            share_row = pkdb.find_share_by_entity_names(entity_name, entity_completename)

        id_shares = share_row.get('id') if share_row else None

        if id_shares:
            pkdb.add_pkgs_rules_local(identifier, id_shares)

        return {"ok": True, "id": int(id_user), "api_token": api_token}

    except Exception as e:
        raw = str(e)
        nice = client.extract_glpi_error_message(raw) or raw
        return {"ok": False, "error": nice}

def create_entity_under_custom_parent(parent_entity_id, display_name, user, stripe_tag=None, tokenuser=None):
    """
    Crée l’entité GLPI, le dossier /sharing/<dl_tag>, puis pkgs_shares + règles.
    Si `stripe_tag` est fourni, il est stocké dans saas_organisations.stripe_tag.
    Retourne l'id GLPI créé.
    """
    try:
        client = get_glpi_client(tokenuser=tokenuser)

        # Création de l’entité GLPI
        tag_uuid = str(uuid.uuid4())
        entity_id = client.create_entity_under_custom_parent(parent_entity_id, display_name, tag_uuid)

        # Création dans saas_organisations
        AdminDatabase().create_entity_under_custom_parent(
            entity_id=entity_id,
            name=display_name,
            tag_value=tag_uuid,
            stripe_tag=stripe_tag,
        )

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

        # Generation Agent
        agent = run_generate_medulla_agent_async(tag)

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

    # Update of sharing ID for this user
    identifier = get_user_identifier(user_id)
    entity_info = get_entity_info(entities_id) or {}
    entity_name             = entity_info.get('name')
    entity_completename     = entity_info.get('completename')

    pkdb = PkgsDatabase()

    if int(entities_id) == 0:
        share_row = pkdb.find_global_share()
    else:
        share_row = pkdb.find_share_by_entity_names(entity_name, entity_completename)

    id_shares = share_row.get('id') if share_row else None

    if id_shares:
        pkgs_rules = pkdb.update_pkgs_rules_local(identifier, id_shares)

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
        # Deletion of sharing for this user
        identifier = get_user_identifier(user_id)

        pkdb = PkgsDatabase()
        pkgs_rules_delete = pkdb.delete_pkgs_rules_local_by_name(identifier)

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

        # Suppression Agent
        del_agent = delete_agent_dir(dl_tag)

        logger.debug(f"Delete Successful: entity_id={entity_id} dl_tag={dl_tag}")
        return result

    except Exception as e:
        logger.error(f"Failed to delete Entity: {e!r}")
        return {"success": False, "message": str(e)}

def delete_user_profile_on_entity(user_id, profile_id, entities_id, tokenuser=None):
    client = get_glpi_client(tokenuser=tokenuser)
    result = client.delete_user_profile_on_entity(user_id, profile_id, entities_id)
    return result

def toggle_user_active(user_id, caller, tokenuser=None):
    if caller.lower() == "admin":
        token_to_use = get_root_token()
        if not token_to_use:
            return {"success": False, "code": -1, "error": "root token unavailable"}
    else:
        token_to_use = tokenuser
        if not token_to_use:
            return {"success": False, "code": -1, "error": "no user token provided"}

    client = get_glpi_client(tokenuser=token_to_use)
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

def restart_medulla_services():
    try:
        script_path = '/usr/sbin/restart-pulse-services'

        proc = subprocess.Popen(
            [script_path],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
            env=os.environ.copy(),
        )
        return proc.pid
    except Exception:
        return None

def regenerate_agent():
    try:
        cmd = (
            "/var/lib/pulse2/clients/generate-pulse-agent.sh"
        )
        proc = subprocess.Popen(
            ["/bin/bash", "-lc", cmd],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
            env=os.environ,
        )
        return True
    except Exception:
        logging.exception("regenerate_agent failed")
        return None

def validateToken(uid, token):
    db = AdminDatabase()
    return db.validateToken(uid, token)

# CRM
def get_id_entity(stripe_tag):
    id_entity = AdminDatabase().get_id_entity(stripe_tag)

    return id_entity

def check_subscribe(id_entity: int) -> dict:
    ents = list_entity_ids_subtree(id_entity)
    if isinstance(ents, dict):
        entity_ids = ents.get("entity_ids", []) or []
        total_entities = int(ents.get("total_entities", len(entity_ids)))
    else:
        entity_ids = list(ents or [])
        total_entities = len(entity_ids)

    users = list_user_ids_in_subtree(entity_ids)
    if isinstance(users, dict):
        user_ids = users.get("user_ids", []) or []
        total_users = int(users.get("total_users", len(user_ids)))
    else:
        user_ids = list(users or [])
        total_users = len(user_ids)

    comps = list_computer_ids_in_subtree(entity_ids)
    if isinstance(comps, dict):
        computer_ids = comps.get("computer_ids", []) or []
        total_computers = int(comps.get("total_computers", len(computer_ids)))
    else:
        computer_ids = list(comps or [])
        total_computers = len(computer_ids)

    return {
        "root_entity_id": int(id_entity),
        "entities":  {"ids": entity_ids, "total": total_entities},
        "users":     {"ids": user_ids,   "total": total_users},
        "computers": {"ids": computer_ids, "total": total_computers},
    }

def deactivate_users_if_needed(user_ids: list[int], tokenuser=None) -> dict:
    out = {"changed": [], "already": [], "errors": []}
    client = get_glpi_client(tokenuser=tokenuser)

    for uid in user_ids:
        res = client.ensure_user_inactive(uid)
        if res is True:
            out["changed"].append(uid)
        elif res is False:
            out["already"].append(uid)
        else:
            out["errors"].append(uid)
    return out

def activate_users_if_needed(user_ids: list[int], tokenuser=None) -> dict:
    """
    Réactive les utilisateurs GLPI si besoin.
    Retourne:
    - changed: ceux qu'on vient de réactiver
    - already: ceux déjà actifs
    - errors : ceux en erreur (HTTP/404/exception)
    """
    out = {"changed": [], "already": [], "errors": []}
    client = get_glpi_client(tokenuser=tokenuser)

    for uid in user_ids:
        res = client.ensure_user_active(uid)
        if res is True:
            out["changed"].append(uid)
        elif res is False:
            out["already"].append(uid)
        else:
            out["errors"].append(uid)
    return out

def get_config_tables():
    db = AdminDatabase()
    tables = db.get_config_tables()
    return tables

def get_config_data(table: str):
    db = AdminDatabase()
    data = db.get_config_data(table)
    return data

def update_config_data(table: str, data: dict) -> bool:
    try:
        logger.info("update_config_data: table=%s data=%s", table, data)
        db = AdminDatabase()
        return db.update_config_data(table, data)
    except Exception as e:
        logger.error("update_config_data failed: %s", e)
        return False

def add_config_data(table: str, data: dict) -> bool:
    try:
        logger.info("add_config_data: table=%s data=%s", table, data)
        db = AdminDatabase()
        return db.add_config_data(table, data)
    except Exception as e:
        logger.error("add_config_data failed: %s", e)
        return False

def delete_config_data(table: str, data: dict) -> bool:
    try:
        logger.info("delete_config_data: table=%s data=%s", table, data)
        db = AdminDatabase()
        return db.delete_config_data(table, data)
    except Exception as e:
        logger.error("delete_config_data failed: %s", e)
        return False

def restore_config_version(table: str, table_version: str) -> bool:
    try:
        logger.info("restore_config_version: table=%s version=%s", table, table_version)
        db = AdminDatabase()
        return db.restore_config_version(table, table_version)
    except Exception as e:
        logger.error("restore_config_version failed: %s", e)
        return False
