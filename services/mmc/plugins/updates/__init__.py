# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
# file : services/mmc/plugins/updates/__init__.py

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

from mmc.support.mmctools import (
    xmlrpcCleanup,
    RpcProxyI,
    ContextMakerI,
    SecurityContext,
    EnhancedSecurityContext
)
from mmc.plugins.base import (with_xmpp_context,
                              with_optional_xmpp_context,
                              Contexte_XmlRpc_surcharge_info_Glpi)

# Au cas où on souhaite appeler des configs d'autres modules
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.updates.config import UpdatesConfig

# import pour la database
from pulse2.database.updates import UpdatesDatabase

from pulse2.database.xmppmaster import XmppMasterDatabase

from pulse2.database.pkgs import PkgsDatabase
from pulse2.database.msc import MscDatabase

from mmc.plugins.glpi.database import Glpi

from .kb_package import KBUninstallPackage

import logging
import traceback

VERSION = "1.0.0"
APIVERSION = "1:0:0"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################


def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = UpdatesConfig("updates")

    if config.disable:
        logger.warning("Plugin updates: disabled by configuration.")
        return False

    if not UpdatesDatabase().activate(config):
        logger.error(
            "Plugin updates: an error occurred during the database initialization"
        )
        return False
    return True


class ContextMaker(ContextMakerI):
    """
    Fabrique de contextes personnalisés pour XMPP, héritée de ContextMakerI.
    Sert à créer et initialiser un objet de type `EnhancedSecurityContext`.

    appeler sur chaque module a l'initialiasation'

    Méthodes
    --------
    getContext() :
        Crée et retourne un contexte sécurisé enrichi contenant les informations
        de l'utilisateur et de la requête courante.
    """

    def getContext(self):
        """
        Crée un contexte de type `EnhancedSecurityContext` pour l'utilisateur courant.

        Retourne
        --------
        EnhancedSecurityContext
            Contexte initialisé avec :
              - `userid` : l'identifiant de l'utilisateur courant
              - `request` : la requête associée
              - `session` : la session courante

        Effets de bord
        --------------
        - Écrit des logs de niveau `error` lors de la création du contexte.
        """
        s = EnhancedSecurityContext()
        s.userid = self.userid
        s.request = self.request
        s.session = self.session
        return s


class RpcProxy(RpcProxyI):
    ##
    # machines
    ##

    @with_optional_xmpp_context
    def get_os_update_major_stats_win(self, ctx=None):
        infos = ctx.get_session_info()['mondict']
        return XmppMasterDatabase().get_os_update_major_stats_win(entitylist=infos['liste_entities_user'])

    @with_optional_xmpp_context
    def get_os_update_major_stats_win_serv(self, ctx=None):
        infos = ctx.get_session_info()['mondict']
        return XmppMasterDatabase().get_os_update_major_stats_win_serv(infos['liste_entities_user'])


    @with_optional_xmpp_context
    def get_conformity_update_by_entity(self, entities=[], source="xmppmaster",ctx=None):
        """Get the conformity for specified entities"""

        # init resultarray with default datas
        # init entitiesarray with entities ids, this will be used in the "in" sql clause
        logger.debug(f"Parametres entities {entities}")
        logger.debug(f"Parametres source {source}")

        resultarray = {}
        for entity in entities:
            eid = entity["uuid"].replace("UUID", "")
            resultarray[entity["uuid"]] = {
                "entity": eid,
                "nbmachines": 0,
                "nbupdate": 0,
                "totalmach": 0,
                "conformite": 0,
            }

        config = Glpi().config if source == "glpi" else None

        if source == "xmppmaster":
            result = XmppMasterDatabase().get_conformity_update_by_entity(
                entities=[entity["uuid"].replace("UUID", "")
                        for entity in entities],
                config=config,
            )

            for counters in result:
                euid = f"UUID{counters['entity']}"
                if euid in resultarray:
                    resultarray[euid]["totalmach"] = counters.get("totalmach", 0)
                    resultarray[euid]["nbmachines"] = counters.get("nbmachines", 0)
                    resultarray[euid]["nbupdate"] = counters.get("nbupdates", 0)

                    if resultarray[euid]["totalmach"] > 0:
                        resultarray[euid]["conformite"] = int(
                            (1 - (resultarray[euid]["nbmachines"] /
                            resultarray[euid]["totalmach"])) * 100
                        )
                    else:
                        resultarray[euid]["conformite"] = 100

        elif source == "glpi":
            # Recover the machines from GLPI for each entity
            glpi_results = []
            for entity in entities:
                params = {
                    "location": entity["uuid"],
                    "filter": "",
                    "field": "",
                    "contains": "",
                    "start": 0,
                    "end": 20,
                    "maxperpage": 20,
                }
                glpi_data = Glpi().get_machines_list1(0, 20, params)
                glpi_uuids = glpi_data["data"].get("uuid", [])
                glpi_results.append({
                    "entity": entity["uuid"].replace("UUID", ""),
                    "machines": [{"uuid": f"UUID{uuid}"} for uuid in glpi_uuids],
                    "totalmach": len(glpi_uuids),
                })

            # Identify the machines common to GLPI and XMPPMaster
            all_glpi_machines = [machine["uuid"]
                                for result in glpi_results for machine in result["machines"]]
            machines_in_both = XmppMasterDatabase().get_machine_in_both_sources(all_glpi_machines)

            result = []
            for glpi_result in glpi_results:
                entity_id = glpi_result["entity"]
                total_machines_glpi = glpi_result["totalmach"]
                glpi_machine_ids = [machine["uuid"]
                                    for machine in glpi_result["machines"]]

                machines_common = [
                    uuid for uuid in glpi_machine_ids if machines_in_both.get(uuid, False)]

                conformity_data = XmppMasterDatabase().get_conformity_update_by_entity(
                    entities=[entity_id],
                    config=config,
                )

                if conformity_data:
                    total_non_conform = conformity_data[0].get("nbmachines", 0)
                else:
                    total_non_conform = 0

                total_updates = sum(item.get("nbupdates", 0)
                                    for item in conformity_data)

                result.append({
                    "entity": entity_id,
                    "totalmach": total_machines_glpi,
                    "nbmachines": total_non_conform,
                    "nbupdates": total_updates,
                    "common_machines_count": len(machines_common),
                })

            for counters in result:
                euid = f"UUID{counters['entity']}"
                if euid in resultarray:
                    resultarray[euid]["totalmach"] = counters.get("totalmach", 0)
                    resultarray[euid]["nbmachines"] = counters.get("nbmachines", 0)
                    resultarray[euid]["nbupdate"] = counters.get("nbupdates", 0)

                    # Calculation based solely on common machines
                    common_count = counters.get("common_machines_count", 0)
                    if common_count > 0:
                        resultarray[euid]["conformite"] = int(
                            (1 - (resultarray[euid]
                            ["nbmachines"] / common_count)) * 100
                        )
                    else:
                        resultarray[euid]["conformite"] = 100

        else:
            raise ValueError(f"Source inconnue : {source}")

        return resultarray

    @with_optional_xmpp_context
    def get_machines_update_grp(self,
                                entity_id,
                                type="windows",
                                colonne="hardware_requirements",
                                ctx=None):
        return UpdatesDatabase().get_machines_update_grp( entity_id,
                                                          type=type,
                                                          colonne=colonne )

    @with_optional_xmpp_context
    def get_linux_major_deployment_history_by_entity(self,
                                                     distributor_id,
                                                     entity_id,
                                                     start=0,
                                                     limit=-1,
                                                     filter="",
                                                     ctx=None):
        return XmppMasterDatabase().get_linux_major_deployment_history_by_entity(
            distributor_id,
            entity_id,
            start,
            limit,
            filter,
        )



    @with_optional_xmpp_context
    def update_machine_compliance_by_action(self,
                                            action,
                                            onoff,
                                            date_start=None,
                                            date_stop=None,
                                            interval=None,
                                            harduuids=None,
                                            entity_ids=None,
                                            distributor_ids=None,
                                            ctx=None):
        """
        Met à jour la conformité des machines via une action XML-RPC, en gérant les dates de début et de fin,
        les identifiants de machines, les entités et les distributeurs.

        Comportement spécifique pour les dates :
        - Si `date_start` est `None` ou une chaîne vide, il est défini à la date et l'heure actuelles.
        - Si `date_stop` est `None` ou une chaîne vide, il est défini à `date_start + 2 heures`.
        - Si `date_stop` est antérieur à `date_start`, un warning est logué et les dates sont réinitialisées :
        - `date_start` devient la date et l'heure actuelles.
        - `date_stop` devient `date_start + 2 heures`.

        Args:
            action (str): Type d'action à effectuer. Doit être dans la liste des actions autorisées.
                Exemples : "require_kernel", "current_security", etc.
            onoff (int): 0 pour désactiver, 1 pour activer.
            date_start (str|datetime|None): Date de début au format "YYYY-MM-DD HH:MM:SS" ou objet datetime.
                Si `None` ou chaîne vide, utilise la date et l'heure actuelles.
            date_stop (str|datetime|None): Date de fin au format "YYYY-MM-DD HH:MM:SS" ou objet datetime.
                Si `None` ou chaîne vide, utilise `date_start + 2 heures`.
            interval (str|None): Intervalle de temps (ex: "2h"). Peut être `None` ou une chaîne vide.
            harduuids (str|list|None): UUID(s) des machines concernées. Peut être une chaîne, une liste ou `None`.
            entity_ids (int|list|None): ID(s) des entités concernées. Peut être un entier, une liste ou `None`.
            distributor_ids (list|None): Liste des distributeurs (ex: ["debian", "redhat"]). Peut être `None`.
            ctx (object|None): Contexte XMPP pour récupérer les informations de session.

        Returns:
            tuple: (bool, str) ou (bool, dict)
                - En cas de succès : (True, résultat de la mise à jour).
                - En cas d'erreur : (False, "Message d'erreur").
        """
        # Récupérer les infos de session
        infos = ctx.get_session_info()['mondict'] if ctx else {}

        # Remplacer les chaînes vides par None pour tous les paramètres
        if harduuids == '':
            harduuids = None
        if entity_ids == '':
            entity_ids = None
        if distributor_ids == '':
            distributor_ids = None
        if date_start == '':
            date_start = None
        if date_stop == '':
            date_stop = None
        if interval == '':
            interval = None

        # Vérification de l'action
        valid_actions = [
            "require_kernel", "require_security", "require_other",
            "current_kernel", "current_security", "current_other",
            "require_all", "current_all"
        ]
        if action not in valid_actions:
            return False, f"Erreur : Action invalide. Actions autorisées : {', '.join(valid_actions)}"

        # Vérification de onoff (doit être 0 ou 1)
        if onoff not in [0, 1]:
            return False, "Erreur : 'onoff' doit être 0 ou 1."

        # Gestion de date_start
        if date_start is None:
            date_start = datetime.now()

        # Gestion de date_stop
        if date_stop is None:
            date_stop = date_start + timedelta(hours=2)

        # Vérification de la cohérence des dates
        if date_stop < date_start:
            logger.warning("date_stop est avant date_start. Réinitialisation des dates.")
            date_start = datetime.now()
            date_stop = date_start + timedelta(hours=2)

        # Vérification de entity_ids
        if entity_ids is not None:
            # Cas où entity_ids est un entier
            if isinstance(entity_ids, int):
                if entity_ids == -1:
                    entity_ids = None
                elif entity_ids not in infos.get('liste_entities_user', []):
                    msgerror = f"Erreur : Privileges insuffisants pour l'utilisateur {infos.get('user_name', 'inconnu')} sur l'entité {infos.get('complet_entity_name_', 'inconnu')}"
                    logger.error(msgerror)
                    return False, msgerror
            # Cas où entity_ids est une liste
            elif isinstance(entity_ids, list):
                # Filtrer les entités non autorisées
                valid_entities = infos.get('liste_entities_user', [])
                entity_ids = [eid for eid in entity_ids if eid in valid_entities]
                if not entity_ids:
                    msgerror = f"Erreur : Aucune entité valide pour l'utilisateur {infos.get('user_name', 'inconnu')}"
                    logger.error(msgerror)
                    return False, msgerror
            else:
                return False, "Erreur : 'entity_ids' doit être un entier, une liste d'entiers ou None."

        # Vérification de harduuids (optionnel, mais doit être une liste ou None)
        if harduuids is not None:
            if not isinstance(harduuids, (list, str)):
                return False, "Erreur : 'harduuids' doit être une liste, une chaîne ou None."
            # Si harduuids est une chaîne vide, le remplacer par None
            if isinstance(harduuids, str) and harduuids == '':
                harduuids = None

        # Vérification de distributor_ids (optionnel, mais doit être une liste ou None)
        if distributor_ids is not None:
            if not isinstance(distributor_ids, list):
                return False, "Erreur : 'distributor_ids' doit être une liste ou None."
            # Si distributor_ids est une liste vide, le remplacer par None
            if not distributor_ids:
                distributor_ids = None

        # Vérification de l'intervalle (optionnel, mais doit être une chaîne non vide ou None)
        if interval is not None and interval != "":
            if not isinstance(interval, str) or not interval.strip():
                return False, "Erreur : 'interval' doit être une chaîne non vide ou None."

        # Appel de la fonction de base
        try:
            result = XmppMasterDatabase().update_machine_compliance_by_action(
                action, onoff, date_start, date_stop, interval, harduuids, entity_ids, distributor_ids
            )
            return result
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la conformité : {str(e)}")
            return False, f"Erreur interne : {str(e)}"

def has_update_data():
    return UpdatesDatabase().has_update_data()

def tests():
    return UpdatesDatabase().tests()


def test_xmppmaster():
    return UpdatesDatabase().test_xmppmaster()


def get_grey_list(start, end, filter="", entityid=None):
    return UpdatesDatabase().get_grey_list(start, end, filter, entityid = entityid)


def get_white_list(start, end, filter="", entityid=None):
    return UpdatesDatabase().get_white_list(start, end, filter, entityid = entityid )


def get_black_list(start, end, filter="", entityid=None):
    return UpdatesDatabase().get_black_list(start, end, filter, entityid = entityid)


def get_enabled_updates_list(entity, upd_list="gray", start=0, end=-1, filter=""):
    if upd_list not in ["gray", "white", "gray|white"]:
        upd_list = "gray"
    # The glpi config is sent to updatedatabase to get the filter_on param
    datas = UpdatesDatabase().get_enabled_updates_list(
        entity, upd_list, start, end, filter, Glpi().config
    )
    count_glpi = Glpi().get_machines_list1(0, 0, {"location": entity})
    datas["total"] = count_glpi["count"]
    return datas


def get_family_list(start, end, filter="", entityid=-1):
    return UpdatesDatabase().get_family_list(start, end, filter, entityid)


def approve_update(updateid, entityid):
    return UpdatesDatabase().approve_update(updateid, entityid)


def grey_update(updateid, entityid, enabled=0):
    return UpdatesDatabase().grey_update(updateid, entityid, enabled)


def exclude_update(updateid, entityid):
    # ajouter la creation du package de d"installation du package.
    # base_winupdates = os.path.join("/", "var", "lib", "pulse2", "packages", "sharing", "winupdates")
    # Créer ou recréer le package KB
    # pkg = KBUninstallPackage("KB5030211", base_path="./packages", recreate=True)
    return UpdatesDatabase().exclude_update(updateid, entityid)


def get_count_machine_as_not_upd(updateid, entityid=-1):
    return UpdatesDatabase().get_count_machine_as_not_upd(updateid, entityid )


def delete_rule(id, entityid):
    return UpdatesDatabase().delete_rule(id, entityid)


def white_unlist_update(updateid, entityid):
    return UpdatesDatabase().white_unlist_update(updateid, entityid)


def get_machine_with_update(kb, updateid, uuid, start=0, limit=-1, filter=""):
    result = XmppMasterDatabase().get_machine_with_update(
        kb, updateid, uuid, start, limit, filter, Glpi().config
    )
    return result


def get_count_machine_with_update(kb, uuid, list):
    return Glpi().get_count_machine_with_update(kb, uuid, list)


#
# def get_os_update_major_stats():
#     return XmppMasterDatabase().get_os_update_major_stats()


def get_os_xmpp_update_major_stats():
    return XmppMasterDatabase().get_os_xmpp_update_major_stats()


def get_outdated_major_os_updates_by_entity(entity_id,
                                            typeaction,
                                            start=0,
                                            limit=-1,
                                            filter="",
                                            colonne=True):
    return XmppMasterDatabase().get_outdated_major_os_updates_by_entity(entity_id,
                                                                        typeaction,
                                                                        start,
                                                                        limit,
                                                                        filter,
                                                                        colonne)


def get_os_update_major_details(entity_id,
                                typeaction="windows",
                                filter="",
                                start=0,
                                limit=-1,
                                colonne=True):
    return XmppMasterDatabase().get_os_update_major_details(entity_id,
                                                            typeaction,
                                                            filter,
                                                            start,
                                                            limit,
                                                            colonne)


def get_linux_upgrade_info(distributor_id, release_version):
    """
    Retourne les métadonnées d'upgrade Linux pour une version source donnée.

    Exemple:
        get_linux_upgrade_info("debian", "12")
    """
    # Forward XML-RPC vers la couche base xmppmaster.
    return XmppMasterDatabase().get_linux_upgrade_info(distributor_id, release_version)


def get_linux_upgrade_info_before_target(distributor_id, target_version):
    """
    Retourne les métadonnées d'upgrade de la version immédiatement inférieure à la cible.

    Exemple:
        get_linux_upgrade_info_before_target("debian", "13")
    """
    # Forward XML-RPC vers la couche base xmppmaster.
    return XmppMasterDatabase().get_linux_upgrade_info_before_target(distributor_id, target_version)


def get_linux_upgrade_candidates(distributor_id, entity_id, target_version=None):
    """
    Liste les machines candidates à un upgrade majeur Linux pour une entité.

    Exemple:
        get_linux_upgrade_candidates("debian", 42, "13")
        get_linux_upgrade_candidates("debian", 42)
    """
    # Forward XML-RPC vers la couche base xmppmaster.
    return XmppMasterDatabase().get_linux_upgrade_candidates(distributor_id, entity_id, target_version)


def get_linux_major_deployment_history_by_entity(distributor_id,
                                                 entity_id,
                                                 start=0,
                                                 limit=-1,
                                                 filter=""):
    """
    Retourne l'historique des déploiements Linux major d'une entité.

    La fenêtre temporelle est limitée au dernier mois.
    """
    return XmppMasterDatabase().get_linux_major_deployment_history_by_entity(
        distributor_id,
        entity_id,
        start,
        limit,
        filter,
    )


def deploy_update_major(package_id,
                        uuid_inventorymachine,
                        hostname,
                        title_deployement=None,
                        start_date=None,
                        end_date=None,
                        deployment_intervals="",
                        userconnect="root",
                        usercreator="root",
                        list_file="fileslistpackage",
                        upgrade_parameters=None):
    """
    Lance un déploiement de mise à jour majeure sur une machine.
    
    Cette fonction crée une commande de déploiement MSC pour une mise à jour
    majeure du système d'exploitation (Windows ou Linux).
    
    Processus :
    -----------
    1. Valide le format du titre de déploiement (convention de nommage)
    2. Vérifie qu'aucun déploiement identique n'existe déjà en MSC
    3. Vérifie qu'aucun déploiement majeur n'est déjà en cours sur cette machine
    4. Valide que le package de déploiement existe dans la base
    5. Crée la commande MSC avec les paramètres de planification
    6. Enregistre la commande dans le journal de session XMPP
    
    Paramètres
    ----------
    package_id : str
        UUID du package à déployer (ex: 'dfd3b8dc-linuxupdategenericcommand_p')
    uuid_inventorymachine : str
        UUID GLPI de la machine cible (commence par 'UUID')
    hostname : str
        Nom d'hôte de la machine (ex: 'machine01')
    title_deployement : str, optionnel
        Titre du déploiement (convention: "hostname--@upd@--distributor_login_timestamp")
    start_date : str, optionnel
        Date de début du déploiement (format: "YYYY-MM-DD HH:MM:SS")
    end_date : str, optionnel
        Date de fin du déploiement (format: "YYYY-MM-DD HH:MM:SS")
    deployment_intervals : str, optionnel
        Crénaux horaires de déploiement (ex: "12-14,20-24,0-8" en format 24h)
    userconnect : str, optionnel
        Utilisateur qui exécute la commande (défaut: "root")
    usercreator : str, optionnel
        Utilisateur qui crée la commande (défaut: "root")
    list_file : str, optionnel
        Liste des fichiers à traiter (défaut: "fileslistpackage")
    upgrade_parameters : dict, optionnel
        Paramètres supplémentaires pour Linux (target_version, target_codename, repo_profile, etc.)
    
    Retour
    ------
    dict : Dictionnaire de résultat avec les clés :
        - success (bool) : True si le déploiement a été créé avec succès
        - commandid (str) : ID de la commande MSC créée (ou "-1" en cas d'erreur)
        - msg (str) : Message de statut ou description de l'erreur
    
    Exemples d'erreur
    -----------------
    - Titre de déploiement ne respectant pas la convention de nommage
    - Déploiement identique déjà planifié en MSC
    - Déploiement majeur déjà en cours sur la machine
    - Package introuvable dans la base (label vide)
    - Exceptions lors de la création de la commande MSC
    """

    logger.info(
        "deploy_update_major inputs: package_id=%r, uuid_inventorymachine=%r, hostname=%r, title_deployement=%r, start_date=%r, end_date=%r, deployment_intervals=%r, userconnect=%r, usercreator=%r, list_file=%r, upgrade_parameters=%r",
        package_id,
        uuid_inventorymachine,
        hostname,
        title_deployement,
        start_date,
        end_date,
        deployment_intervals,
        userconnect,
        usercreator,
        list_file,
        upgrade_parameters,
    )

    # Structure de retour par défaut (déploiement déjà existant)
    result = {"success": False,
              "commandid": "-1",
              "msg": f"Déploiement non relancé : {package_id} est déjà planifié pour {hostname}"}

    # === ÉTAPE 1 : Validation du titre de déploiement ===
    # Extraction du titre sans le timestamp final (supprime le dernier segment séparé par _)
    try:
        title_deployementnew = title_deployement[:-
                                                 (len(title_deployement.split("_")[-1]))]
    except:
        # Le titre ne respecte pas la convention attendue
        result["msg"] = f"Convention de nommage invalide pour {package_id} sur {hostname}"
        result["success"] = False
        return result

    # === ÉTAPE 2 : Vérification des déploiements existants en MSC ===
    # Évite de créer un doublon si un déploiement identique est déjà planifié
    if MscDatabase().test_msc_process(title_deployementnew):
        logger.warning(f"Déploiement non relancé : {package_id} est déjà planifié pour {hostname}")
        result["msg"] = f"Déploiement non relancé : {package_id} est déjà planifié pour {hostname}"
        result["success"] = False
        return result

    # === ÉTAPE 3 : Vérification des déploiements majeurs en cours ===
    # Évite de relancer un déploiement si une mise à jour majeure est déjà en cours
    if XmppMasterDatabase().test_update_major_deployment_in_progress(title_deployementnew):
        logger.warning(f"Déploiement non relancé : {package_id} est déjà en cours sur {hostname}")
        result["msg"] = f"Déploiement non relancé : {package_id} est déjà en cours sur {hostname}"
        result["success"] = False
        return result

    try:
        # === ÉTAPE 4 : Validation du package ===
        # Vérifie que le package existe et possède un label valide
        if title_deployement:
            pkgsinfos = PkgsDatabase().pkgs_get_infos_details(package_id)
            if not pkgsinfos or pkgsinfos.get('label') == "":
                logger.error(f"Déploiement non relancé : package {package_id} introuvable pour {hostname}")
                result["msg"] = f"Déploiement non relancé : package {package_id} introuvable pour {hostname}"
                result["success"] = False
                return result

        # === ÉTAPE 5 : Création de la commande MSC ===
        # Lance la création réelle du déploiement avec les paramètres de planification
        result = MscDatabase().deploy_package_msc(package_id,
                                                  uuid_inventorymachine,
                                                  hostname,
                                                  title_deployement=title_deployement,
                                                  start_date=start_date,
                                                  end_date=end_date,
                                                  deployment_intervals=deployment_intervals,
                                                  userconnect=userconnect,
                                                  usercreator=usercreator,
                                                  list_file=list_file,
                                                  upgrade_parameters=upgrade_parameters)
        
        # === ÉTAPE 6 : Enregistrement du succès ===
        # Si la création MSC a réussi, enregistre la commande dans le journal XMPP
        if result["success"]:
            # Ajoute un enregistrement de connexion pour tracer la création de la commande
            # avec le login de l'utilisateur qui a créé le déploiement
            XmppMasterDatabase().addlogincommand(usercreator,
                                                 result["commandid"],
                                                 "", "", "", "", "",
                                                 0, 0, 0, 0, {})
            logger.info(f"Déploiement créé avec succès : commande {result['commandid']} pour {hostname} par {usercreator}")

    except Exception as e:
        # === GESTION DES ERREURS ===
        # Capture et enregistre toute exception lors du traitement
        logger.error("\n%s" % (traceback.format_exc()))
        result["msg"] = str(e)
        result["success"] = False
        result["commandid"] = "-1"
    
    return result


def get_os_xmpp_update_major_details(entity_id,
                                     filter="",
                                     start=0,
                                     limit=-1,
                                     colonne=True):
    return XmppMasterDatabase().get_os_xmpp_update_major_details(entity_id,
                                                                 filter,
                                                                 start,
                                                                 limit,
                                                                 colonne)


def get_os_update_major_stats():
    return XmppMasterDatabase().get_os_update_major_stats()


def get_machines_needing_update(updateid, entity, start=0, limit=-1, filter=""):
    return UpdatesDatabase().get_machines_needing_update(
        updateid, entity, Glpi().config, start, limit, filter
    )


def get_machine_count_by_entity(entities):
    """
    Returns the total number of machines per entity from the GLPI base.

    Args:
        ENTITIES (List): List of dictates with at least the 'ID' key.

    Returns:
        Dict: {entity_id: number_de_machines}
    """
    result = {}
    glpi = Glpi()
    for entity in entities:
        params = {
            "location": str(entity["id"]),
            "filter": "",
            "field": "",
            "contains": "",
            "start": 0,
            "end": 1,
            "maxperpage": 1,
        }
        glpi_data = glpi.get_machines_list1(0, 1, params)
        result[str(entity["id"])] = glpi_data.get("count", 0)
    return result


def get_machines_xmppmaster(start, end, filter=""):
    return XmppMasterDatabase().get_machines_xmppmaster(start, end, filter)


def get_all_machines_grouped_by_os(start, end, filter="", os_filter=""):
    return XmppMasterDatabase().get_all_machines_grouped_by_os(start, end, filter, os_filter)


def get_machine_in_both_sources(glpi_ids):
    return XmppMasterDatabase().get_machine_in_both_sources(glpi_ids)


def get_conformity_update_by_machines(ids=[]):
    """ids is formated as :
    {
        "uuids": ["UUID4", "UUID3"], // glpi inventory uuids
        "ids": [4,3]
    }
    """

    result = {}
    for uuid in ids["uuids"]:
        result[uuid] = {
            "uuid":  uuid.replace("UUID", ""),
            "id": "",
            "missing": 0,
            "inprogress": 0,  # Ajout du champ inprogress
            "hostname": "",
            "installed": 0,
            "total": 0,
            "compliance": 100.0,
        }
    range = len(ids["uuids"])
    count = 0
    while count < range:
        result[ids["uuids"][count]]["id"] = ids["ids"][count]
        count += 1

    if ids["uuids"] == "" or ids["uuids"] == []:
        installed = {}
    else:
        installed = Glpi().get_count_installed_updates_by_machines(
            ids["uuids"])

    if ids["ids"] == "" or ids["ids"] == []:
        missing = {}
    else:
        missing = XmppMasterDatabase(
        ).get_count_missing_updates_by_machines(ids["ids"])

    for uuid in installed:
        result[uuid]["installed"] = installed[uuid]["installed"]
        result[uuid]["hostname"] = installed[uuid]["cn"]

    for uuid in missing:
        result[uuid]["missing"] = missing[uuid]["missing"]
        result[uuid]["inprogress"] = missing[uuid]["inprogress"]

    for uuid in result:
        result[uuid]["total"] = result[uuid]["installed"] + \
            result[uuid]["missing"] + result[uuid]["inprogress"]
        result[uuid]["compliance"] = (
            (result[uuid]["installed"] / result[uuid]["total"]) * 100
            if result[uuid]["total"] > 0
            else 100
        )

    return result


def analyze_machine_compliance_distribution_linux(  entity_id,
                                                    filter,  # filtre sur distributor_id
                                                    start,
                                                    limit,
                                                    colonne):
    # Initialiser les valeurs par défaut de start et limit à -1 si elles sont None ou des chaînes vides
    if start is None or str(start).strip() == "":
        startint = -1

    if limit is None or str(limit).strip() == "":
        limitint = -1


    try:
        startint =  int(start)
    except (ValueError, TypeError):
        startint = -1

    try:
        limitint =  int(limit)
    except (ValueError, TypeError):
        limitint = -1

    return XmppMasterDatabase().analyze_machine_compliance_distribution_linux( entity_id,
                                                                               filter,
                                                                               startint,
                                                                               limitint,
                                                                               colonne)


def get_machines_by_update_type( entity_id,
                                 updatetype,
                                 filter_str,
                                 start,
                                 limit,
                                 colonne):
    try:
        start = int(start)
        limit = int(limit)
    except (TypeError, ValueError):
        start = -1
        limit = -1

    return XmppMasterDatabase().get_machines_by_update_type( entity_id,
                                                             updatetype,
                                                             filter_str,
                                                             start,
                                                             limit,
                                                             colonne)


def analyze_machine_compliance_linux( entity_id,
                                      filter,
                                      start,
                                      limit,
                                      colonne):
    return XmppMasterDatabase().analyze_machine_compliance_linux(entity_id,
                                                                 filter,
                                                                 start,
                                                                 limit,
                                                                 colonne)


