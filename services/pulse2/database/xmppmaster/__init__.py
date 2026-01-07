# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

"""
xmppmaster database handler
"""

# SqlAlchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    func,
    and_,
    desc,
    or_,
    distinct,
    not_,
    text,
)  # cast, Date, select,
from sqlalchemy.orm import sessionmaker, load_only
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import DBAPIError
from datetime import datetime, date, timedelta  # date,

# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.msc import MscDatabase

from pulse2.database.xmppmaster.schema import (
    Network,
    Machines,
    RelayServer,
    Users,
    Has_machinesusers,
    Has_relayserverrules,
    Regles,
    Has_guacamole,
    Base,
    UserLog,
    Deploy,
    Has_login_command,
    Logs,
    Organization,
    Packages_list,
    Qa_custom_command,
    Qa_relay_command,
    Qa_relay_launched,
    Qa_relay_result,
    Cluster_ars,
    Has_cluster_ars,
    Command_action,
    Command_qa,
    Syncthingsync,
    Organization_ad,
    Cluster_resources,
    Syncthing_ars_cluster,
    Syncthing_machine,
    Syncthing_deploy_group,
    Substituteconf,
    Agentsubscription,
    Subscription,
    Def_remote_deploy_status,
    Uptime_machine,
    Mon_machine,
    Mon_devices,
    Mon_device_service,
    Mon_rules,
    Mon_event,
    Mon_panels_template,
    Glpi_entity,
    Glpi_location,
    Glpi_Register_Keys,
    Up_machine_windows,
    Update_data,
    Up_black_list,
    Up_white_list,
    Up_gray_list,
    Up_history,
    Up_machine_activated,
    Mmc_module_actif,
    Users_adgroups,
)
from pulse2.utils import to_int, normalize_entity

# Imported last
import logging
import json
import time

# topology
import os
import pwd
import traceback
import sys
import re
import uuid
import random
import copy
from sqlalchemy.ext.automap import automap_base
import re

class ProcedureError(Exception):
    """Exception levée en cas d'erreur lors de l'appel d'une procédure stockée."""
    pass
Session = sessionmaker()

logger = logging.getLogger()

# sql debug mode
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class DomaineTypeDeviceError(Error):
    """
        type is not in domaine 'thermalprinter', 'nfcReader', 'opticalReader',\
        'cpu', 'memory', 'storage', 'network'
    """

    def __str__(self):
        return "{0} {1}".format(self.__doc__, Exception.__str__(self))


class DomainestatusDeviceError(Error):
    """
    status is not in domaine 'ready', 'busy', 'warning', 'error'
    """

    def __str__(self):
        return "{0} {1}".format(self.__doc__, Exception.__str__(self))


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError("Unknown type")


class XmppMasterDatabase(DatabaseHelper):
    """
    Singleton Class to query the xmppmaster database.

    """

    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "xmppmaster"
        self.configfile = "xmppmaster.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()

        if self.is_activated:
            return None
        # This is used to automatically create the mapping
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize,
            pool_timeout=self.config.dbpooltimeout,
        )
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)
        Base = automap_base()
        Base.prepare(self.db, reflect=True)
        # add table auto_base
        self.Update_machine = Base.classes.update_machine
        self.Ban_machines = Base.classes.ban_machines

        # Only federated tables (beginning by local_) are automatically mapped
        # If needed, excludes tables from this list
        exclude_table = []
        # Dynamically add attributes to the object for each mapped class
        for table_name, mapped_class in Base.classes.items():
            if table_name in exclude_table:
                continue
            if table_name.startswith("local"):
                setattr(self, table_name.capitalize(), mapped_class)

        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the xmppmaster database
        """
        # No mapping is needed, all is done on schema file
        return

    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError as e:
                logger.error(e)
            except Exception as e:
                logger.error(e)
            if ret:
                break
        if not ret:
            raise "Database connection error"
        return ret

    # ---------------------- function dict from dataset -------------------------
    def _return_dict_from_dataset_mysql(self, resultproxy):
        return [rowproxy._asdict() for rowproxy in resultproxy]

    # =====================================================================
    # xmppmaster FUNCTIONS deploy syncthing
    # =====================================================================

    # xmppmaster FUNCTIONS FOR SUBSCRIPTION

    @DatabaseHelper._sessionm
    def setagentsubscription(self, session, name):
        """
        this functions addition a log line in table log xmpp.
        """
        try:
            new_agentsubscription = Agentsubscription()
            new_agentsubscription.name = name
            session.add(new_agentsubscription)
            session.commit()
            session.flush()
            return new_agentsubscription.id
        except Exception as e:
            logger.error(str(e))
            return None

    @DatabaseHelper._sessionm
    def deAgentsubscription(self, session, name):
        """
        del organization name
        """
        session.query(Agentsubscription).filter(
            Agentsubscription.name == name).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def setupagentsubscription(self, session, name):
        """
        this functions addition ou update table in table log xmpp.
        """
        try:
            q = session.query(Agentsubscription)
            q = q.filter(Agentsubscription.name == name)
            record = q.first()
            if record:
                record.name = name
                session.commit()
                session.flush()
                return record.id
            else:
                return self.setagentsubscription(name)
        except Exception as e:
            logger.error(str(e))
            return None

    @DatabaseHelper._sessionm
    def setSubscription(self, session, macadress, idagentsubscription):
        """
        this functions addition a log line in table log xmpp.
        """
        try:
            new_subscription = Subscription()
            new_subscription.macadress = macadress
            new_subscription.idagentsubscription = idagentsubscription
            session.add(new_subscription)
            session.commit()
            session.flush()
            return new_subscription.id
        except Exception as e:
            logger.error(str(e))
            return None

    @DatabaseHelper._sessionm
    def setupSubscription(self, session, macadress, idagentsubscription):
        """
        this functions addition a log line in table log xmpp.
        """
        try:
            q = session.query(Subscription)
            q = q.filter(Subscription.macadress == macadress)
            record = q.first()
            if record:
                record.macadress = macadress
                record.idagentsubscription = idagentsubscription
                session.commit()
                session.flush()
                return record.id
            else:
                return self.setSubscription(macadress, idagentsubscription)
        except Exception as e:
            logger.error(str(e))
            return None

    @DatabaseHelper._sessionm
    def setuplistSubscription(self, session, listmacadress, agentsubscription):
        try:
            id = self.setupagentsubscription(agentsubscription)
            if id is not None:
                for macadress in listmacadress:
                    self.setupSubscription(macadress, id)
                return id
            else:
                logger.error(
                    "setup or create record for"
                    " agent subscription %s" % agentsubscription
                )
                return None
        except Exception as e:
            logger.error(str(e))
            return None

    @DatabaseHelper._sessionm
    def delSubscriptionmacadress(self, session, macadress):
        """
        this functions addition a log line in table log xmpp.
        """
        try:
            q = session.query(Subscription)
            q = q.filter(Subscription.macadress == macadress).delete()
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
            self.logger.error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def update_count_subscription(self, session, agentsubtitutename, countroster):
        logger.debug("update_count_subscription %s" % agentsubtitutename)
        try:
            result = (
                session.query(Substituteconf)
                .filter(Substituteconf.jidsubtitute == agentsubtitutename)
                .all()
            )
            first_value = True
            for t in result:
                logger.debug(
                    "countsub %s->%s ars %s"
                    % (t.countsub, t.jidsubtitute, t.relayserver_id)
                )
                if first_value:
                    first_value = False
                    t.countsub = countroster
                else:
                    t.countsub = 0
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logger.error("update_count_subscription %s" % str(e))
            return False

    @DatabaseHelper._sessionm
    def update_enable_for_agent_subscription(
        self, session, agentsubtitutename, status="0", agenttype="machine"
    ):
        try:
            sql = """
            UPDATE `xmppmaster`.`machines`
                    INNER JOIN
                `xmppmaster`.`subscription` ON `xmppmaster`.`machines`.`macaddress` = `xmppmaster`.`subscription`.`macadress`
                    INNER JOIN
                `xmppmaster`.`agent_subscription` ON `xmppmaster`.`subscription`.`idagentsubscription` = `xmppmaster`.`agent_subscription`.`id`
            SET
                `xmppmaster`.`machines`.`enabled` = '%s'
            WHERE
                `xmppmaster`.`machines`.agenttype = '%s'
                    AND `xmppmaster`.`agent_subscription`.`name` = '%s';""" % (
                status,
                agenttype,
                agentsubtitutename,
            )
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            self.logger.error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def setSyncthing_deploy_group(
        self,
        session,
        namepartage,
        directory_tmp,
        packagename,
        cmd,
        grp_parent,
        status="C",
        dateend=None,
        deltatime=60,
    ):
        try:
            idpartage = self.search_partage_for_package(packagename)
            if idpartage == -1:
                # print "add partage"
                # il faut cree le partage.
                new_Syncthing_deploy_group = Syncthing_deploy_group()
                new_Syncthing_deploy_group.namepartage = namepartage
                new_Syncthing_deploy_group.directory_tmp = directory_tmp
                new_Syncthing_deploy_group.cmd = cmd
                new_Syncthing_deploy_group.status = status
                new_Syncthing_deploy_group.package = packagename
                new_Syncthing_deploy_group.grp_parent = grp_parent
                if dateend is None:
                    dateend = datetime.now() + timedelta(minutes=deltatime)
                else:
                    new_Syncthing_deploy_group.dateend = dateend + timedelta(
                        minutes=deltatime
                    )
                session.add(new_Syncthing_deploy_group)
                session.commit()
                session.flush()
                return new_Syncthing_deploy_group.id
            else:
                return idpartage
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def incr_count_transfert_terminate(self, session, iddeploy):
        sql = """UPDATE xmppmaster.syncthing_deploy_group
                SET
                    nbtransfert = nbtransfert + 1
                WHERE
                    id = %s;""" % (
            iddeploy
        )
        # print "incr_count_transfert_terminate", sql
        result = session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def update_transfert_progress(self, session, progress, iddeploy, jidmachine):
        """this function update this level progress"""
        sql = """
                UPDATE xmppmaster.syncthing_machine
                        INNER JOIN
                    syncthing_ars_cluster
                      ON xmppmaster.syncthing_ars_cluster.id =
                             xmppmaster.syncthing_machine.fk_arscluster
                        INNER JOIN
                    xmppmaster.syncthing_deploy_group
                      ON xmppmaster.syncthing_deploy_group.id =
                      xmppmaster.syncthing_ars_cluster.fk_deploy
                SET
                    xmppmaster.syncthing_machine.progress = IF(%s>=xmppmaster.syncthing_machine.progress,%s,xmppmaster.syncthing_machine.progress)
                WHERE
                    xmppmaster.syncthing_deploy_group.id = %s
                        AND xmppmaster.syncthing_machine.jidmachine LIKE '%s';""" % (
            progress,
            progress,
            iddeploy,
            jidmachine,
        )
        # print "update_transfert_progress", sql
        result = session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def get_approve_products(self, session, identity, colonne=True):
        """
        Récupère les enregistrements de la table 'up_list_produit' pour une entité spécifique
        et renvoie les résultats sous forme de colonnes ou de lignes.
        La colonne 'entity_id' est exclue. Les valeurs NULL sont remplacées par des chaînes vides.

        Paramètres :
        - identity : identifiant de l'entité à filtrer (entity_id)
        - colonne (bool) : Si True, les résultats sont retournés sous forme de colonnes. Sinon, sous forme de lignes.

        Retourne :
        - dict/list : dictionnaire ou liste contenant les informations des produits trouvés
        """
        if identity is not None:
            try:
                resultat = self._call_procedure(session, "up_genere_list_produit_entity", [identity])
                session.commit()
            except Exception as e:
                logger.error(f"Erreur call procedure Rollback {e}")
                session.rollback()

        try:
            # Sélectionne les colonnes souhaitées, y compris 'comment'
            query = text("""
                SELECT id, name_procedure, enable, comment
                FROM xmppmaster.up_list_produit
                WHERE entity_id = :identity
                ORDER BY comment
            """)
            result = session.execute(query, {"identity": identity})
            produits = result.fetchall()

            if not produits:
                logger.info(f"No products found for entity_id={identity}.")
                if colonne:
                    return {"id": [], "name_procedure": [], "enable": [], "comment": []}
                return []

            if colonne:
                produits_info = {
                    "id": [p[0] if p[0] is not None else "" for p in produits],
                    "name_procedure": [p[1] if p[1] is not None else "" for p in produits],
                    "enable": [p[2] if p[2] is not None else "" for p in produits],
                    "comment": [p[3] if p[3] is not None else "" for p in produits],
                }
            else:
                produits_info = [
                    {
                        "id": p[0] if p[0] is not None else "",
                        "name_procedure": p[1] if p[1] is not None else "",
                        "enable": p[2] if p[2] is not None else "",
                        "comment": p[3] if p[3] is not None else "",
                    }
                    for p in produits
                ]

            return produits_info

        except Exception as e:
            logger.error(f"An error occurred while fetching products for entity_id={identity}: {str(e)}")
            return {"id": [], "name_procedure": [], "enable": [], "comment": []} if colonne else []


    @DatabaseHelper._sessionm
    def update_approve_products(self, session, updatesproduct, entity_id=None):
        """
        Met à jour la colonne 'enable' dans la table 'up_list_produit'
        pour les IDs spécifiés, en tenant compte de l'entité si précisée.

        Paramètres :
        - updatesproduct (list of tuples or lists) : Chaque élément doit contenir (id, enable).
        - entity_id (int|None) : ID de l'entité. Si None, pas de filtre par entité.

        Exemples d'utilisation :
        1. Sans filtre d'entité :
        ```python
        updatesproduct = [
            (1, 1),
            (2, 0),
        ]
        result = obj.update_approve_products(updates=updates)
        ```

        2. Avec filtre sur une entité (entity_id=5) :
        ```python
        updatesproduct = [
            [4, 0],
            [7, 1],
        ]
        result = obj.update_approve_products(updatesproduct=updatesproduct, entity_id=5)
        ```

        Retourne :
        - dict : Un dictionnaire indiquant si la mise à jour a réussi ou non.

        Exemple de retour en cas de succès :
        ```python
        {"success": True, "message": "Update successful"}
        ```

        Exemple de retour en cas d'erreur :
        ```python
        {"success": False, "message": "An error occurred during update: <details>"}
        ```
        """

        try:
            entity_id = int(entity_id)
        except (TypeError, ValueError):
            msgerror = f"Invalid entity_id value: {entity_id!r}"
            logger.error(msgerror)
            return {"success": False, "message": msgerror}

        try:
            normalized_updates = [tuple(update) if isinstance(update, list) else update for update in updatesproduct]

            for id, enable in normalized_updates:
                query = """
                    UPDATE xmppmaster.up_list_produit
                    SET enable = :enable
                    WHERE id = :id
                """
                params = {"enable": enable, "id": id}

                if entity_id is not None:
                    query += " AND entity_id = :entity_id"
                    params["entity_id"] = entity_id
                logger.error(f"Exécutant la requête: {query} avec les paramètres: {params}")
                session.execute(text(query), params)

            session.commit()
            logger.info("Mise à jour réussie des produits.")
            return {"success": True, "message": "Update successful"}

        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred during update: {str(e)}")
            return {"success": False, "message": str(e)}

    @DatabaseHelper._sessionm
    def get_auto_approve_rules(self, session, entityid=None, colonne=True ):
        """
        Récupère les enregistrements de la table 'up_auto_approve_rules' et renvoie
        les résultats sous forme de colonnes ou de lignes.
        Si entityid est spécifié, on ne prend que les enregistrements correspondants.

        Paramètres :
        - entityid (int|None) : ID de l'entité à filtrer. Si None, on prend toutes les entités.
        - colonne (bool) : Si True, retour en colonnes, sinon en lignes.

        Retourne :
        - dict/list : Résultats sous forme de colonnes (dict) ou de lignes (list).
        """
        if entityid:
            try:
                resultat = self._call_procedure(session,
                            "up_genere_list_rule_entity",
                            [entityid])
                session.commit()
            except Exception as e:
                logger.error(f"Erreur call procedure Rollback {e}")
                session.rollback()
        try:
            # Construction dynamique de la requête
            query = "SELECT id, entityid, msrcseverity, updateclassification, active_rule FROM xmppmaster.up_auto_approve_rules"
            params = {}

            if entityid is not None:
                query += " WHERE entityid = :entityid"
                params["entityid"] = entityid

            result = session.execute(text(query), params)
            rules = result.fetchall()

            if rules:
                if colonne:
                    rules_info = {
                        "id": [rule[0] or "" for rule in rules],
                        "entityid": [rule[1] or 0 for rule in rules],
                        "msrcseverity": [rule[2] or "" for rule in rules],
                        "updateclassification": [rule[3] or "" for rule in rules],
                        "active_rule": [rule[4] or 0 for rule in rules],
                    }
                else:
                    rules_info = [
                        {
                            "id": rule[0] or "",
                            "entityid": rule[1] or "",
                            "msrcseverity": rule[2] or "",
                            "updateclassification": rule[3] or "",
                            "active_rule": rule[4] or 0
                        }
                        for rule in rules
                    ]
                return rules_info
            else:
                logger.info("No rules found in the table.")
                return []

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return {}

    @DatabaseHelper._sessionm
    def update_auto_approve_rules(self, session, updates, entity_id=None):
        """
        Met à jour la colonne 'active_rule' dans la table 'up_auto_approve_rules'
        pour les IDs spécifiés. Peut être restreint à une entité via entityid.

        Paramètres :
        - updates (list of (id, active_rule))
        - entity_id (int|None) : ID de l'entité à filtrer. Si None, pas de filtre.

        Exemples d'utilisation :
        1. Avec une liste de tuples (sans filtre d'entité) :
        ```python
        updates = [
            (1, 1),  # ID 1 -> active_rule = 1
            (2, 0),  # ID 2 -> active_rule = 0
            (3, 1),  # ID 3 -> active_rule = 1
        ]
        result = obj.update_auto_approve_rules(updates=updates)
        ```

        2. Avec une liste de listes (filtré sur entityid=5) :
        ```python
        updates = [
            [4, 0],  # ID 4 -> active_rule = 0 (dans l'entité 5)
            [7, 1],  # ID 7 -> active_rule = 1 (dans l'entité 5)
        ]
        result = obj.update_auto_approve_rules(updates=updates, entity_id=5)
        ```
        Retourne :
            - dict : Un dictionnaire indiquant si la mise à jour a réussi ou non,
                avec un message correspondant.
            Exemple de retour :
                ```python
                {"success": True, "message": "Update successful"}
                ```

                En cas d'erreur :
                ```python
                {"success": False, "message": "An error occurred during update: <details>"}
                ```
        """
        try:
            entity_id = int(entity_id)
        except (TypeError, ValueError):
            msgerror = f"Invalid entity_id value: {entity_id!r}"
            logger.error(msgerror)
            return {"success": False, "message": msgerror}

        try:
            normalized_updates = [tuple(update) if isinstance(update, list) else update for update in updates]

            for id, active_rule in normalized_updates:
                query = text("""
                    UPDATE xmppmaster.up_auto_approve_rules
                    SET active_rule = :active_rule
                    WHERE id = :id AND entityid = :entityid
                """)
                params = {
                    "active_rule": int(active_rule),
                    "id": int(id),
                    "entityid": int(entity_id)
                }
                session.execute(query, params)

            session.commit()
            logger.info("Mise à jour réussie des règles d'approbation automatique.")
            return {"success": True, "message": "Update successful"}

        except Exception as e:
            session.rollback()
            logger.error(f"An error occurred during update: {str(e)}")
            return {"success": False, "message": str(e)}

    @DatabaseHelper._sessionm
    def get_ars_for_pausing_syncthing(self, session, nbtransfert=2):
        sql = """SELECT
                    xmppmaster.syncthing_deploy_group.id,
                    xmppmaster.syncthing_ars_cluster.liststrcluster,
                    xmppmaster.syncthing_deploy_group.directory_tmp,
                    xmppmaster.syncthing_deploy_group.nbtransfert,
                    xmppmaster.syncthing_ars_cluster.id
                FROM
                    xmppmaster.syncthing_deploy_group
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster
                      ON
                         xmppmaster.syncthing_deploy_group.id =
                         xmppmaster.syncthing_ars_cluster.fk_deploy
                WHERE
                    xmppmaster.syncthing_deploy_group.nbtransfert >= %s
                    and
                    xmppmaster.syncthing_ars_cluster.keypartage != "pausing";""" % (
            nbtransfert
        )
        # print "get_ars_for_pausing_syncthing"#, sql
        result = session.execute(sql)
        session.commit()
        session.flush()
        if result is None:
            return -1
        else:
            re = [y for y in [x for x in result]]
            for arssyncthing in re:
                self.update_ars_status(arssyncthing[4], "pausing")
        return re

    @DatabaseHelper._sessionm
    def update_ars_status(self, session, idars, keystatus="pausing"):
        sql = """UPDATE
                    xmppmaster.syncthing_ars_cluster
                SET
                    xmppmaster.syncthing_ars_cluster.keypartage = '%s'
                WHERE
                    xmppmaster.syncthing_ars_cluster.id = '%s';""" % (
            keystatus,
            idars,
        )
        # print "update_ars_status", sql
        result = session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def search_partage_for_package(self, session, packagename):
        result = -1
        sql = """ SELECT
                    xmppmaster.syncthing_deploy_group.id
                FROM
                    xmppmaster.syncthing_deploy_group
                WHERE
                    xmppmaster.syncthing_deploy_group.package LIKE '%s'
                        AND xmppmaster.syncthing_deploy_group.dateend > DATE_SUB(NOW(), INTERVAL 1 HOUR)
                limit 1;""" % (
            packagename
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        resultat = [x for x in result]
        if not resultat:
            return -1
        else:
            return resultat[0][0]

    @DatabaseHelper._sessionm
    def search_ars_cluster_for_package(self, session, idpartage, ars):
        result = -1
        sql = """SELECT
                xmppmaster.syncthing_ars_cluster.id
                FROM
                    xmppmaster.syncthing_ars_cluster
                where xmppmaster.syncthing_ars_cluster.fk_deploy = %s and
                xmppmaster.syncthing_ars_cluster.liststrcluster like '%s'
                LIMIT 1;""" % (
            idpartage,
            ars,
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        resultat = [x for x in result]
        if len(resultat) == 0:
            return -1
        else:
            return resultat[0][0]

    @DatabaseHelper._sessionm
    def search_ars_master_cluster_(self, session, idpartage, numcluster):
        result = -1
        sql = """SELECT DISTINCT xmppmaster.syncthing_ars_cluster.arsmastercluster
                FROM
                    xmppmaster.syncthing_ars_cluster
                where
                    xmppmaster.syncthing_ars_cluster.fk_deploy = %s
                      and
                    xmppmaster.syncthing_ars_cluster.numcluster = %s limit 1;""" % (
            idpartage,
            numcluster,
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        resultat = [x for x in result]
        countresult = len(resultat)

        if countresult == 0:
            return ""
        elif countresult == 1:
            return resultat[0][0]
        else:
            # il y a plusieurs cluster dans le deployement.
            # il faut donc choisir celui correspondant au cluster
            ljidars = [x[0] for x in resultat]
            for jidars in ljidars:
                # print jidars
                if self.ars_in_num_cluster(jidars, numcluster):
                    return jidars
        return ""

    @DatabaseHelper._sessionm
    def ars_in_num_cluster(self, session, jidars, numcluster):
        """
        test si jidars est dans le cluster number.
        """
        sql = """SELECT
                    id_ars
                FROM
                    xmppmaster.has_cluster_ars
                INNER JOIN
                    xmppmaster.relayserver
                        ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                where xmppmaster.relayserver.jid like '%s'
                  and
                  xmppmaster.has_cluster_ars.id_cluster= %s;""" % (
            jidars,
            numcluster,
        )
        # print sql

        result = session.execute(sql)
        session.commit()
        session.flush()
        resultat = [x for x in result]
        if resultat:
            return True
        else:
            return False

    @DatabaseHelper._sessionm
    def setSyncthing_ars_cluster(
        self,
        session,
        numcluster,
        namecluster,
        liststrcluster,
        arsmastercluster,
        fk_deploy,
        type_partage="",
        devivesyncthing="",
        keypartage="",
    ):
        try:
            # search ars elu if exist for partage
            arsmasterclusterexist = self.search_ars_master_cluster_(
                fk_deploy, numcluster
            )
            ars_cluster_id = self.search_ars_cluster_for_package(
                fk_deploy, liststrcluster
            )
            if ars_cluster_id == -1:
                new_Syncthing_ars_cluster = Syncthing_ars_cluster()
                new_Syncthing_ars_cluster.numcluster = numcluster
                new_Syncthing_ars_cluster.namecluster = namecluster
                new_Syncthing_ars_cluster.liststrcluster = liststrcluster
                if arsmasterclusterexist == "":
                    new_Syncthing_ars_cluster.arsmastercluster = arsmastercluster
                else:
                    new_Syncthing_ars_cluster.arsmastercluster = arsmasterclusterexist
                new_Syncthing_ars_cluster.keypartage = keypartage
                new_Syncthing_ars_cluster.fk_deploy = fk_deploy
                new_Syncthing_ars_cluster.type_partage = type_partage
                new_Syncthing_ars_cluster.devivesyncthing = devivesyncthing
                session.add(new_Syncthing_ars_cluster)
                session.commit()
                session.flush()
                return new_Syncthing_ars_cluster.id
            else:
                return ars_cluster_id
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def setSyncthing_machine(
        self,
        session,
        jidmachine,
        jid_relay,
        cluster,
        pathpackage,
        sessionid,
        start,
        startcmd,
        endcmd,
        command,
        group_uuid,
        result,
        fk_arscluster,
        syncthing=1,
        state="",
        user="",
        type_partage="",
        title="",
        inventoryuuid=None,
        login=None,
        macadress=None,
        comment="",
    ):
        try:
            new_Syncthing_machine = Syncthing_machine()
            new_Syncthing_machine.jidmachine = jidmachine
            new_Syncthing_machine.cluster = cluster
            new_Syncthing_machine.jid_relay = jid_relay
            new_Syncthing_machine.pathpackage = pathpackage
            new_Syncthing_machine.state = state
            new_Syncthing_machine.sessionid = sessionid
            new_Syncthing_machine.start = start
            new_Syncthing_machine.startcmd = startcmd
            new_Syncthing_machine.endcmd = endcmd
            new_Syncthing_machine.user = user
            new_Syncthing_machine.command = command
            new_Syncthing_machine.group_uuid = group_uuid
            new_Syncthing_machine.result = result
            new_Syncthing_machine.syncthing = syncthing
            new_Syncthing_machine.type_partage = type_partage
            new_Syncthing_machine.title = title
            new_Syncthing_machine.inventoryuuid = inventoryuuid
            new_Syncthing_machine.login = login
            new_Syncthing_machine.macadress = macadress
            new_Syncthing_machine.comment = comment
            new_Syncthing_machine.fk_arscluster = fk_arscluster
            session.add(new_Syncthing_machine)
            session.commit()
            session.flush()
            return new_Syncthing_machine.id
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def stat_syncthing_distributon(self, session, idgrp, idcmd, valuecount=[0, 100]):
        setvalues = " "
        if valuecount:
            setvalues = "AND xmppmaster.syncthing_machine.progress in (%s)" % ",".join(
                [str(x) for x in valuecount]
            )
        sql = """SELECT DISTINCT progress, COUNT(progress)
                    FROM
                        xmppmaster.syncthing_machine
                    WHERE
                        xmppmaster.syncthing_machine.group_uuid = %s
                        AND xmppmaster.syncthing_machine.command = %s
                        """ % (
            idgrp,
            idcmd,
        )
        sql = sql + setvalues + "\nGROUP BY progress ;"

        # print sql
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [(x[0], x[1]) for x in result]

    @DatabaseHelper._sessionm
    def stat_syncthing_transfert(self, session, idgrp, idcmd):
        ddistribution = self.stat_syncthing_distributon(idgrp, idcmd)
        distibution = {"nbvalue": len(
            ddistribution), "data_dist": ddistribution}

        sql = """SELECT
                    pathpackage,
                    COUNT(*) AS nb,
                    CAST((SUM(xmppmaster.syncthing_machine.progress) / COUNT(*)) AS CHAR) AS progress
                FROM
                    xmppmaster.syncthing_machine
                WHERE
                    xmppmaster.syncthing_machine.group_uuid = %s
                        AND xmppmaster.syncthing_machine.command = %s;
                        """ % (
            idgrp,
            idcmd,
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        re = [x for x in result]
        re = re[0]
        if re[0] is None:
            return {
                "package": "",
                "nbmachine": 0,
                "progresstransfert": 0,
                "distibution": distibution,
            }
        try:
            progress = int(float(re[2]))
        except BaseException:
            progress = 0

        return {
            "package": re[0],
            "nbmachine": re[1],
            "progresstransfert": progress,
            "distibution": distibution,
        }

    @DatabaseHelper._sessionm
    def getnumcluster_for_ars(self, session, jidrelay):
        sql = (
            """SELECT
                    xmppmaster.has_cluster_ars.id_cluster
                FROM
                    xmppmaster.relayserver
                        INNER JOIN
                    xmppmaster.has_cluster_ars
                      ON `has_cluster_ars`.`id_ars` = xmppmaster.relayserver.id
                WHERE
                    `relayserver`.`jid` LIKE '%s'
                LIMIT 1;"""
            % jidrelay
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result][0]

    @DatabaseHelper._sessionm
    def getCluster_deploy_syncthing(self, session, iddeploy):
        sql = (
            """SELECT
                    xmppmaster.syncthing_deploy_group.namepartage,
                    xmppmaster.syncthing_deploy_group.directory_tmp,
                    xmppmaster.syncthing_deploy_group.package,
                    xmppmaster.syncthing_ars_cluster.namecluster,
                    xmppmaster.syncthing_ars_cluster.arsmastercluster,
                    xmppmaster.syncthing_ars_cluster.numcluster,
                    xmppmaster.syncthing_machine.cluster,
                    xmppmaster.syncthing_deploy_group.grp_parent,
                    xmppmaster.syncthing_deploy_group.cmd,
                    xmppmaster.syncthing_deploy_group.id
                FROM
                    xmppmaster.syncthing_deploy_group
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster ON xmppmaster.syncthing_deploy_group.id = xmppmaster.syncthing_ars_cluster.fk_deploy
                        INNER JOIN
                    xmppmaster.syncthing_machine ON xmppmaster.syncthing_ars_cluster.id = xmppmaster.syncthing_machine.fk_arscluster
                WHERE
                    xmppmaster.syncthing_deploy_group.id = %s ;"""
            % iddeploy
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [y for y in [x for x in result]]

    @DatabaseHelper._sessionm
    def updateMachine_deploy_Syncthing(
        self, session, listidmachine, statusold=2, statusnew=3
    ):
        if isinstance(listidmachine, (int, str)):
            listidmachine = [listidmachine]
        if not listidmachine:
            return
        listidmachine = ",".join([str(x) for x in listidmachine])

        sql = """UPDATE
                    xmppmaster.syncthing_machine
                SET
                    xmppmaster.syncthing_machine.syncthing = %s
                where
                    syncthing = %s
                    and
                    id in (%s);""" % (
            statusnew,
            statusold,
            listidmachine,
        )
        # print sql
        result = session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getMachine_deploy_Syncthing(self, session, iddeploy, ars=None, status=None):
        sql = (
            """SELECT
                    xmppmaster.syncthing_machine.sessionid,
                    xmppmaster.syncthing_machine.jid_relay,
                    xmppmaster.syncthing_machine.jidmachine,
                    xmppmaster.machines.keysyncthing,
                    xmppmaster.syncthing_machine.result,
                    xmppmaster.syncthing_machine.id
                FROM
                    xmppmaster.syncthing_deploy_group
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster
                            ON xmppmaster.syncthing_deploy_group.id =
                                xmppmaster.syncthing_ars_cluster.fk_deploy
                        INNER JOIN
                    xmppmaster.syncthing_machine
                            ON xmppmaster.syncthing_ars_cluster.id =
                                xmppmaster.syncthing_machine.fk_arscluster
                        INNER JOIN
                    xmppmaster.machines
                            ON xmppmaster.machines.uuid_inventorymachine =
                                xmppmaster.syncthing_machine.inventoryuuid
                WHERE
                    xmppmaster.syncthing_deploy_group.id=%s """
            % iddeploy
        )
        if ars is not None:
            sql = (
                sql
                + """
            and
            xmppmaster.syncthing_machine.jid_relay like '%s' """
                % ars
            )
        if status is not None:
            sql = (
                sql
                + """
            and
            xmppmaster.syncthing_machine.syncthing = %s """
                % status
            )
        sql = sql + ";"
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    # =====================================================================
    # xmppmaster FUNCTIONS synch syncthing
    # =====================================================================
    @DatabaseHelper._sessionm
    def setSyncthingsync(
        self,
        session,
        uuidpackage,
        relayserver_jid,
        typesynchro="create",
        watching="yes",
    ):
        try:
            new_Syncthingsync = Syncthingsync()
            new_Syncthingsync.uuidpackage = uuidpackage
            new_Syncthingsync.typesynchro = typesynchro
            new_Syncthingsync.relayserver_jid = relayserver_jid
            new_Syncthingsync.watching = watching
            session.add(new_Syncthingsync)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))

    @DatabaseHelper._sessionm
    def get_List_jid_ServerRelay_enable(self, session, enabled=1):
        """return list enable server relay id"""
        sql = """SELECT
                    jid
                FROM
                    xmppmaster.relayserver
                WHERE
                        `relayserver`.`enabled` = %d;""" % (
            enabled
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def getRelayServerfromid(self, session, ids):
        """
        This function is used to obtain the relayservers infos
        based on the ids
        Args:
            session: The SQLAlchemy session
            ids: ids of the relayservers
        Returns:
            It returns the complete infos of the relayservers
        """
        relayserver_list = []
        if isinstance(ids, str):
            ids = ids.split(",")
        elif isinstance(ids, int):
            ids = [ids]

        try:
            relayservers = session.query(
                RelayServer).filter(RelayServer.id.in_(ids))
            relayservers = relayservers.all()
            session.commit()
            session.flush()
            for relayserver in relayservers:
                res = {
                    "id": relayserver.id,
                    "urlguacamole": relayserver.urlguacamole,
                    "subnet": relayserver.subnet,
                    "nameserver": relayserver.nameserver,
                    "ipserver": relayserver.ipserver,
                    "ipconnection": relayserver.ipconnection,
                    "port": relayserver.port,
                    "portconnection": relayserver.portconnection,
                    "mask": relayserver.mask,
                    "jid": relayserver.jid,
                    "longitude": relayserver.longitude,
                    "latitude": relayserver.latitude,
                    "enabled": relayserver.enabled,
                    "switchonoff": relayserver.switchonoff,
                    "mandatory": relayserver.mandatory,
                    "classutil": relayserver.classutil,
                    "groupdeploy": relayserver.groupdeploy,
                    "package_server_ip": relayserver.package_server_ip,
                    "package_server_port": relayserver.package_server_port,
                    "moderelayserver": relayserver.moderelayserver,
                }
                relayserver_list.append(res)
            return relayserver_list
        except Exception as e:
            logger.error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))
            return relayserver_list

    @DatabaseHelper._sessionm
    def get_Arsid_list_from_clusterid_list(self, session, idscluster):
        """
        This function returns the list of the ars from a cluster id or cluster cluster list id.
        Args:
            session: The SQLAlchemy session
            idscluster: cluster id or cluster list id
        Returns:
            It returns the list of the ARS contained in the cluster(s)
        """
        if isinstance(idscluster, str):
            idscluster = [idscluster.strip()]

        if not idscluster:
            return []
        strlistcluster = ",".join([str(x[0]) for x in idscluster])
        sql = (
            """SELECT
                    id_ars
                FROM
                    xmppmaster.has_cluster_ars
                WHERE
                    id_cluster IN (%s);"""
            % strlistcluster
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def get_List_Mutual_ARS_from_cluster_of_one_idars(self, session, idars):
        """
        This function returns the list of the ars from a cluster based
        on the id of one provided ARS.
        Args:
            session: The SQLAlchemy session
            idars: The id of the ARS
        Returns:
            It returns the list of the ARS contained in the cluster

        """
        sql = (
            """SELECT
                    id_ars
                 FROM
                     xmppmaster.has_cluster_ars
                 WHERE
                    id_cluster IN (SELECT
                            id_cluster
                        FROM
                            xmppmaster.has_cluster_ars
                        WHERE
                            id_ars = %d);"""
            % idars
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x[0] for x in result]

    @DatabaseHelper._sessionm
    def get_List_Mutual_ARS_from_cluster_of_list_idars(self, session, listidars):
        """
        This function returns the list of the ars from a cluster based
        on the list id of one provided ARS.
        Args:
            session: The SQLAlchemy session
            idars: The id of the ARS
        Returns:
            It returns the list of the ARS contained in the cluster

        """
        listin = "%s" % ",".join([str(x) for x in listidars])
        sql = (
            """SELECT
                    id_ars
                 FROM
                     xmppmaster.has_cluster_ars
                 WHERE
                    id_cluster IN (SELECT
                            id_cluster
                        FROM
                            xmppmaster.has_cluster_ars
                        WHERE
                            id_ars in  (%s));"""
            % listin
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x[0] for x in result]

    @DatabaseHelper._sessionm
    def get_stat_ars_machine(self, session, listarsjid):
        listin = ",".join(["'%s'" % x for x in listarsjid])
        sql = (
            """
            SELECT
                groupdeploy,
                SUM(CASE
                    WHEN (LOCATE('linux', platform)) THEN 1
                    ELSE 0
                END) AS nblinuxmachine,
                SUM(CASE
                    WHEN (LOCATE('windows', platform)) THEN 1
                    ELSE 0
                END) AS nbwindows,
                SUM(CASE
                    WHEN (LOCATE('darwin', platform)) THEN 1
                    ELSE 0
                END) AS nbdarwin,
                SUM(CASE
                    WHEN (enabled = '1') THEN 1
                    ELSE 0
                END) AS mach_on,
                SUM(CASE
                    WHEN (enabled = '0') THEN 1
                    ELSE 0
                END) AS mach_off,
                SUM(CASE
                    WHEN SUBSTRING(uuid_inventorymachine,1,1) = "U"
                    THEN
                    0
                    ELSE
                    1
                END) AS uninventoried,
                SUM(CASE
                    WHEN  SUBSTRING(uuid_inventorymachine,1,1) = "U"
                    THEN
                        1
                    ELSE 0
                END) AS inventoried,
                SUM(CASE
                    WHEN
                        (enabled = '1'
                            AND  SUBSTRING(uuid_inventorymachine,1,1) = "U"  )
                    THEN
                        0
                    ELSE 1
                END) AS uninventoried_online,
                SUM(CASE
                    WHEN
                        (enabled = '0'
                            AND  SUBSTRING(uuid_inventorymachine,1,1) = "U"  )
                    THEN
                        0
                    ELSE 1
                END) AS uninventoried_offline,
                SUM(CASE
                    WHEN
                        (enabled = 1
                            AND  SUBSTRING(uuid_inventorymachine,1,1) = "U"  )
                    THEN
                        1
                    ELSE 0
                END) AS inventoried_online,
                SUM(CASE
                    WHEN
                        (enabled = '0'
                            AND  SUBSTRING(uuid_inventorymachine,1,1) = "U"  )
                    THEN
                        1
                    ELSE 0
                END) AS inventoried_offline,
                SUM(CASE
                    WHEN id THEN 1
                    ELSE 0
                END) AS nbmachine,
                SUM(CASE
                    WHEN (COALESCE(uuid_serial_machine, '') != '') THEN 1
                    ELSE 0
                END) AS with_uuid_serial,
                SUM(CASE
                    WHEN (classutil = 'both') THEN 1
                    ELSE 0
                END) AS bothclass,
                SUM(CASE
                    WHEN (classutil = 'public') THEN 1
                    ELSE 0
                END) AS publicclass,
                SUM(CASE
                    WHEN (classutil = 'private') THEN 1
                    ELSE 0
                END) AS privateclass,
                SUM(CASE
                    WHEN (COALESCE(ad_ou_user, '') != '') THEN 1
                    ELSE 0
                END) AS nb_ou_user,
                SUM(CASE
                    WHEN (COALESCE(ad_ou_machine, '') != '') THEN 1
                    ELSE 0
                END) AS nb_OU_mach,
                SUM(CASE
                    WHEN (kiosk_presence = 'True') THEN 1
                    ELSE 0
                END) AS kioskon,
                SUM(CASE
                    WHEN (kiosk_presence = 'FALSE') THEN 1
                    ELSE 0
                END) AS kioskoff,
                SUM(CASE
                    WHEN need_reconf THEN 1
                    ELSE 0
                END) AS nbmachinereconf
            FROM
                machines
            WHERE
                groupdeploy IN (%s)
                    AND agenttype = 'machine'
            GROUP BY groupdeploy;"""
            % listin
        )
        # logger.error("sql\n%s"%sql)
        result = session.execute(sql)
        session.commit()
        session.flush()
        resultatout = {}
        if result:
            for row in result:
                resultatout[row[0]] = {}
                resultatout[row[0]]["nblinuxmachine"] = int(row[1])
                resultatout[row[0]]["nbwindows"] = int(row[2])
                resultatout[row[0]]["nbdarwin"] = int(row[3])
                resultatout[row[0]]["mach_on"] = int(row[4])
                resultatout[row[0]]["mach_off"] = int(row[5])
                resultatout[row[0]]["uninventoried"] = int(row[6])
                resultatout[row[0]]["inventoried"] = int(row[7])
                resultatout[row[0]]["uninventoried_online"] = int(row[8])
                resultatout[row[0]]["uninventoried_offline"] = int(row[9])
                resultatout[row[0]]["inventoried_online"] = int(row[10])
                resultatout[row[0]]["inventoried_offline"] = int(row[11])
                resultatout[row[0]]["nbmachine"] = int(row[12])
                resultatout[row[0]]["with_uuid_serial"] = int(row[13])
                resultatout[row[0]]["bothclass"] = int(row[14])
                resultatout[row[0]]["publicclass"] = int(row[15])
                resultatout[row[0]]["privateclass"] = int(row[16])
                resultatout[row[0]]["nb_ou_user"] = int(row[17])
                resultatout[row[0]]["nb_OU_mach"] = int(row[18])
                resultatout[row[0]]["kioskon"] = int(row[19])
                resultatout[row[0]]["kioskoff"] = int(row[20])
                resultatout[row[0]]["nbmachinereconf"] = int(row[21])
        return resultatout

    @DatabaseHelper._sessionm
    def get_ars_list_belongs_cluster(self, session, listidars, start, limit, filter):





        try:
            start = int(start)
        except BaseException:
            start = -1
        try:
            limit = int(limit)
        except BaseException:
            limit = -1

        resultobj = {
            "id": [],
            "hostname": [],
            "jid": [],
            "jid_from_relayserver": [],
            "cluster_name": [],
            "cluster_description": [],
            "classutil": [],
            "macaddress": [],
            "ip_xmpp": [],
            "enabled": [],
            "enabled_css": [],
            "mandatory": [],
            "switchonoff": [],
        }

        count = 0
        # filter activate
        filterars = ""
        if filter != "":
            filterars = """ AND (relayserver.subnet LIKE '%%%s%%' OR
                relayserver.nameserver LIKE '%%%s%%' OR
                relayserver.ipserver LIKE '%%%s%%' OR
                relayserver.ipconnection LIKE '%%%s%%' OR
                relayserver.port LIKE '%%%s%%' OR
                relayserver.portconnection LIKE '%%%s%%' OR
                relayserver.mask LIKE '%%%s%%' OR
                relayserver.jid LIKE '%%%s%%' OR
                relayserver.longitude LIKE '%%%s%%' OR
                relayserver.latitude LIKE '%%%s%%' OR
                relayserver.classutil LIKE '%%%s%%' OR
                relayserver.groupdeploy LIKE '%%%s%%' OR
                relayserver.package_server_ip LIKE '%%%s%%' OR
                relayserver.package_server_port LIKE '%%%s%%' OR
                relayserver.syncthing_port LIKE '%%%s%%') """ % (
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
                filter,
            )

        if listidars:
            listin = "%s" % ",".join([str(x) for x in listidars if x != ""])
            sql = """
                SELECT SQL_CALC_FOUND_ROWS
                    relayserver.id AS relayserver_id,
                    relayserver.ipserver AS relayserver_ipserver,
                    relayserver.nameserver AS relayserver_nameserver,
                    relayserver.moderelayserver AS relayserver_moderelayserver,
                    relayserver.jid AS jid_from_relayserver,
                    relayserver.classutil AS relayserver_classutil,
                    relayserver.enabled AS relayserver_enabled,
                    relayserver.switchonoff AS relayserver_switchonoff,
                    relayserver.mandatory AS relayserver_mandatory,
                    machines.jid AS machines_jid,
                    cluster_ars.name AS cluster_name,
                    cluster_ars.description AS cluster_description,
                    cluster_ars.id AS cluster_id,
                    machines.macaddress AS macaddress
                FROM
                    relayserver
                        LEFT OUTER JOIN
                    has_cluster_ars ON has_cluster_ars.id_ars = relayserver.id
                        LEFT OUTER JOIN
                    cluster_ars ON cluster_ars.id = has_cluster_ars.id_cluster
                        LEFT OUTER JOIN
                    machines ON machines.hostname = relayserver.nameserver
                WHERE
                    relayserver.moderelayserver = 'static' %s
                    AND relayserver.id in(       SELECT
                                                has_cluster_ars.id_ars
                                            FROM
                                                xmppmaster.has_cluster_ars
                                            WHERE
                                                has_cluster_ars.id_cluster IN (
                                                                                SELECT
                                                                                        id_cluster
                                                                                    FROM
                                                                                        xmppmaster.has_cluster_ars
                                                                                    WHERE
                                                                                        id_ars in  (%s))

                    )""" % (
                filterars,
                listin,
            )
            if start != -1 and limit != -1:
                sql = sql + "LIMIT %s OFFSET %s" % (limit, start)
            sql = sql + ";"
            result = session.execute(sql)

            #  Count the ARS
            sql_count = "SELECT FOUND_ROWS();"
            ret_count = session.execute(sql_count)
            count = ret_count.first()[0]

            session.commit()
            session.flush()

            if result:
                for row in result:
                    resultobj["id"].append(row[0])
                    resultobj["hostname"].append(row[2])
                    resultobj["jid"].append(row[9])
                    resultobj["jid_from_relayserver"].append(row[4])
                    resultobj["cluster_name"].append(row[10])
                    resultobj["cluster_description"].append(row[11])
                    resultobj["classutil"].append(row[3])
                    resultobj["ip_xmpp"].append(row[1])
                    resultobj["macaddress"].append(row[13])
                    resultobj["enabled"].append(row[6])
                    resultobj["enabled_css"].append(
                        "machineNamepresente"
                        if (row[6] == "1" or row[6] == 1)
                        else "machineName"
                    )
                    resultobj["mandatory"].append(row[8])
                    resultobj["switchonoff"].append(row[7])

        resultobj["count"] = count
        return resultobj

    @DatabaseHelper._sessionm
    def getRelayServer(self, session, enable=None):
        relayserver_list = []
        if enable is not None:
            relayservers = (
                session.query(RelayServer)
                .filter(and_(RelayServer.enabled == enable))
                .all()
            )
        else:
            relayservers = session.query(RelayServer).all()
        session.commit()
        session.flush()
        try:
            for relayserver in relayservers:
                res = {
                    "id": relayserver.id,
                    "urlguacamole": relayserver.urlguacamole,
                    "subnet": relayserver.subnet,
                    "nameserver": relayserver.nameserver,
                    "ipserver": relayserver.ipserver,
                    "ipconnection": relayserver.ipconnection,
                    "port": relayserver.port,
                    "portconnection": relayserver.portconnection,
                    "mask": relayserver.mask,
                    "jid": relayserver.jid,
                    "longitude": relayserver.longitude,
                    "latitude": relayserver.latitude,
                    "enabled": relayserver.enabled,
                    "switchonoff": relayserver.switchonoff,
                    "mandatory": relayserver.mandatory,
                    "classutil": relayserver.classutil,
                    "groupdeploy": relayserver.groupdeploy,
                    "package_server_ip": relayserver.package_server_ip,
                    "package_server_port": relayserver.package_server_port,
                    "moderelayserver": relayserver.moderelayserver,
                }
                relayserver_list.append(res)
            return relayserver_list
        except Exception as e:
            logger.error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))
            return relayserver_list

    @DatabaseHelper._sessionm
    def get_relayservers_no_sync_for_packageuuid(self, session, uuidpackage):
        result_list = []
        try:
            relayserversync = (
                session.query(Syncthingsync)
                .filter(and_(Syncthingsync.uuidpackage == uuidpackage))
                .all()
            )
            session.commit()
            session.flush()
            for relayserver in relayserversync:
                res = {}
                res["uuidpackage"] = relayserver.uuidpackage
                res["typesynchro"] = relayserver.typesynchro
                res["relayserver_jid"] = relayserver.relayserver_jid
                res["watching"] = relayserver.watching
                res["date"] = relayserver.date
                result_list.append(res)
            return result_list
        except Exception as e:
            logger.error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))
            return []

    @DatabaseHelper._sessionm
    def xmpp_regiter_synchro_package(self, session, uuidpackage, typesynchro):
        # list id server relay
        list_server_relay = self.get_List_jid_ServerRelay_enable(enabled=1)
        for jid in list_server_relay:
            # exclude local package server
            if jid[0].startswith("rspulse@pulse/"):
                continue
            self.setSyncthingsync(
                uuidpackage, jid[0], typesynchro, watching="yes")

    # =====================================================================
    # xmppmaster FUNCTIONS
    # =====================================================================

    @DatabaseHelper._sessionm
    def setlogxmpp(
        self,
        session,
        text,
        type="noset",
        sessionname="",
        priority=0,
        who="",
        how="",
        why="",
        module="",
        action="",
        touser="",
        fromuser="",
    ):
        """
        this functions addition a log line in table log xmpp.
        """
        try:
            new_log = Logs()
            new_log.text = text
            new_log.type = type
            new_log.sessionname = sessionname
            new_log.priority = priority
            new_log.who = who
            new_log.how = how
            new_log.why = why
            new_log.module = module
            new_log.action = action
            new_log.touser = touser
            new_log.fromuser = fromuser
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))

    @DatabaseHelper._sessionm
    def getQAforMachine(self, session, cmd_id, uuidmachine):
        try:
            command_action = session.query(Command_action).filter(
                and_(
                    Command_action.command_id == cmd_id,
                    Command_action.target == uuidmachine,
                )
            )
            # print command_action
            # print cmd_id
            # print uuidmachine
            command_action = command_action.all()
            listcommand = []
            for command in command_action:
                action = []
                action.append(command.command_id)
                action.append(str(command.date))
                action.append(command.session_id)
                action.append(command.typemessage)
                action.append(command.command_result)
                listcommand.append(action)
            return listcommand
        except Exception as e:
            logger.error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))
            return []

    @DatabaseHelper._sessionm
    def getQAforMachineByJid(self, session, cmd_id, jid):
        try:
            command_action = session.query(Command_action).filter(
                and_(
                    Command_action.command_id == cmd_id,
                    Command_action.jid_target == jid,
                )
            )
            # print command_action
            # print cmd_id
            # print uuidmachine
            command_action = command_action.all()
            listcommand = []
            for command in command_action:
                action = []
                action.append(command.command_id)
                action.append(str(command.date))
                action.append(command.session_id)
                action.append(command.typemessage)
                action.append(command.command_result)
                listcommand.append(action)
            return listcommand
        except Exception as e:
            logger.error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))
            return []

    @DatabaseHelper._sessionm
    def getCommand_action_time(
        self, session, during_the_last_seconds, start, stop, filter=None
    ):
        try:
            command_qa = session.query(
                distinct(Command_qa.id).label("id"),
                Command_qa.command_name.label("command_name"),
                Command_qa.command_login.label("command_login"),
                Command_qa.command_os.label("command_os"),
                Command_qa.command_start.label("command_start"),
                Command_qa.command_grp.label("command_grp"),
                Command_qa.command_machine.label("command_machine"),
                Command_action.target.label("target"),
                Command_qa.jid_machine.label("jid_machine"),
            ).outerjoin(Command_action, Command_qa.id == Command_action.command_id)
            # si on veut passer par les groupe avant d'aller sur les machine.
            # command_qa = command_qa.group_by(Command_qa.id)
            command_qa = command_qa.order_by(desc(Command_qa.id))
            if during_the_last_seconds:
                command_qa = command_qa.filter(
                    Command_qa.command_start
                    >= (datetime.now() - timedelta(seconds=during_the_last_seconds))
                )
            # nb = self.get_count(deploylog)
            # len_query = session.query(func.count(distinct(Deploy.title)))[0]

            nbtotal = self.get_count(command_qa)
            if start != "" and stop != "":
                command_qa = command_qa.offset(
                    int(start)).limit(int(stop) - int(start))
            command_qa = command_qa.all()
            session.commit()
            session.flush()
            # creation des list pour affichage web organiser par colone
            result_list = []
            command_id_list = []
            command_name_list = []
            command_login_list = []
            command_os_list = []
            command_start_list = []
            command_grp_list = []
            command_machine_list = []
            command_target_list = []
            jid_machine_list = []
            for command in command_qa:
                command_id_list.append(command.id)
                command_name_list.append(command.command_name)
                command_login_list.append(command.command_login)
                command_os_list.append(command.command_os)
                command_start_list.append(command.command_start)
                command_grp_list.append(command.command_grp)
                command_machine_list.append(command.command_machine)
                command_target_list.append(
                    command.target if command.target is not None else ""
                )
                jid_machine_list.append(command.jid_machine)
            result_list.append(command_id_list)
            result_list.append(command_name_list)
            result_list.append(command_login_list)
            result_list.append(command_os_list)
            result_list.append(command_start_list)
            result_list.append(command_grp_list)
            result_list.append(command_machine_list)
            result_list.append(command_target_list)
            result_list.append(jid_machine_list)
            return {"nbtotal": nbtotal, "result": result_list}
        except Exception as e:
            logger.debug("getCommand_action_time error %s->" % str(e))
            logger.error("\n%s" % (traceback.format_exc()))
            return {"nbtotal": 0, "result": result_list}

    @DatabaseHelper._sessionm
    def setCommand_qa(
        self,
        session,
        command_name,
        command_action,
        command_login,
        command_grp="",
        command_machine="",
        command_os="",
        jid="",
    ):
        try:
            new_Command_qa = Command_qa()
            new_Command_qa.command_name = command_name
            new_Command_qa.command_action = command_action
            new_Command_qa.command_login = command_login
            new_Command_qa.command_grp = command_grp
            new_Command_qa.command_machine = command_machine
            new_Command_qa.command_os = command_os
            new_Command_qa.jid_machine = jid
            session.add(new_Command_qa)
            session.commit()
            session.flush()
            return new_Command_qa.id
        except Exception as e:
            logger.error(str(e))

    @DatabaseHelper._sessionm
    def getCommand_qa_by_cmdid(self, session, cmdid):
        try:
            command_qa = session.query(
                Command_qa).filter(Command_qa.id == cmdid)
            command_qa = command_qa.first()
            session.commit()
            session.flush()
            return {
                "id": command_qa.id,
                "command_name": command_qa.command_name,
                "command_action": command_qa.command_action,
                "command_login": command_qa.command_login,
                "command_os": command_qa.command_os,
                "command_start": str(command_qa.command_start),
                "command_grp": command_qa.command_grp,
                "command_machine": command_qa.command_machine,
            }
        except Exception as e:
            logger.error("getCommand_qa_by_cmdid error %s->" % str(e))
            logger.error("\n%s" % (traceback.format_exc()))
            return {
                "id": "",
                "command_name": "",
                "command_action": "",
                "command_login": "",
                "command_os": "",
                "command_start": "",
                "command_grp": "",
                "command_machine": "",
            }

    @DatabaseHelper._sessionm
    def setCommand_action(
        self,
        session,
        target,
        command_id,
        sessionid,
        command_result="",
        typemessage="log",
        jid="",
    ):
        try:
            new_Command_action = Command_action()
            new_Command_action.session_id = sessionid
            new_Command_action.command_id = command_id
            new_Command_action.typemessage = typemessage
            new_Command_action.command_result = command_result
            new_Command_action.target = target
            new_Command_action.jid_target = jid
            session.add(new_Command_action)
            session.commit()
            session.flush()
            return new_Command_action.id
        except Exception as e:
            logger.error(str(e))

    @DatabaseHelper._sessionm
    def updateaddCommand_action(
        self, session, command_result, sessionid, typemessage="result"
    ):
        try:
            sql = """UPDATE `xmppmaster`.`command_action`
                    SET
                        `typemessage` = '%s',
                        `command_result` = CONCAT(`command_result`, ' ', '%s')
                    WHERE
                        (`session_id` = '%s');""" % (
                typemessage,
                command_result,
                sessionid,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logger.error(str(e))
            return False

    @DatabaseHelper._sessionm
    def logtext(self, session, text, sessionname="", type="noset", priority=0, who=""):
        try:
            new_log = Logs()
            new_log.text = text
            new_log.sessionname = sessionname
            new_log.type = type
            new_log.priority = priority
            new_log.who = who
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))

    @DatabaseHelper._sessionm
    def log(self, session, msg, type="info"):
        try:
            new_log = UserLog()
            new_log.msg = msg
            new_log.type = type
            session.add(new_log)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))

    #
    @DatabaseHelper._sessionm
    def getlistpackagefromorganization(
        self, session, organization_name=None, organization_id=None
    ):
        """
        return list package an organization
        eg call function example:
        XmppMasterDatabase().getlistpackagefromorganization( organization_id = 1)
        or
        XmppMasterDatabase().getlistpackagefromorganization( organization_name = "name")
        """
        # recupere id organization
        idorganization = -1
        try:
            if organization_id is not None:
                try:
                    result_organization = session.query(Organization).filter(
                        Organization.id == organization_id
                    )
                    result_organization = result_organization.one()
                    session.commit()
                    session.flush()
                    idorganization = result_organization.id

                except Exception as e:
                    logger.debug(
                        "organization id : %s does not exists" % organization_id
                    )
                    return -1
            elif organization_name is not None:
                idorganization = self.getIdOrganization(organization_name)
                if idorganization == -1:
                    return {"nb": 0, "packageslist": []}
            else:
                return {"nb": 0, "packageslist": []}
            result = (
                session.query(
                    Packages_list.id.label("id"),
                    Packages_list.packageuuid.label("packageuuid"),
                    Packages_list.organization_id.label("idorganization"),
                    Organization.name.label("name"),
                )
                .join(Organization, Packages_list.organization_id == Organization.id)
                .filter(Organization.id == idorganization)
            )
            nb = self.get_count(result)
            result = result.all()

            list_result = [
                {
                    "id": x.id,
                    "packageuuid": x.packageuuid,
                    "idorganization": x.idorganization,
                    "name": x.name,
                }
                for x in result
            ]
            return {"nb": nb, "packageslist": list_result}
        except Exception as e:
            logger.debug(
                "load packages for organization id : %s is error : %s"
                % (organization_id, str(e))
            )
            return {"nb": 0, "packageslist": []}

    #
    @DatabaseHelper._sessionm
    def getIdOrganization(self, session, name_organization):
        """
        return id organization suivant le Name
        On error return -1
        """
        try:
            result_organization = session.query(Organization).filter(
                Organization.name == name_organization
            )
            result_organization = result_organization.one()
            session.commit()
            session.flush()
            return result_organization.id
        except Exception as e:
            logger.error(str(e))
            logger.debug("organization name : %s does not exists" %
                         name_organization)
            return -1

    @DatabaseHelper._sessionm
    def addOrganization(self, session, name_organization):
        """
        creation d'une organization
        """
        id = self.getIdOrganization(name_organization)
        if id == -1:
            organization = Organization()
            organization.name = name_organization
            session.add(organization)
            session.commit()
            session.flush()
            return organization.id
        else:
            return id

    @DatabaseHelper._sessionm
    def delOrganization(self, session, name_organization):
        """
        del organization name
        """
        idorganization = self.getIdOrganization(name_organization)
        if idorganization != -1:
            session.query(Organization).filter(
                Organization.name == name_organization
            ).delete()
            session.commit()
            session.flush()
            q = session.query(Packages_list).filter(
                Packages_list.organization_id == idorganization
            )
            q.delete()
            session.commit()
            session.flush()

    # Custom Command Quick Action################################
    @DatabaseHelper._sessionm
    def create_Qa_custom_command(
        self, session, user, osname, namecmd, customcmd, description=""
    ):
        """
        create Qa_custom_command
        """
        try:
            qa_custom_command = Qa_custom_command()
            qa_custom_command.namecmd = namecmd
            qa_custom_command.user = user
            qa_custom_command.os = osname
            qa_custom_command.customcmd = customcmd
            qa_custom_command.description = description
            session.add(qa_custom_command)
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.error(str(e))
            logger.debug("qa_custom_command error")
            return -1

    @DatabaseHelper._sessionm
    def update_Glpi_entity(self, session, glpi_id, complete_name=None, name=None):
        try:
            result_entity = (
                session.query(Glpi_entity)
                .filter(Glpi_entity.glpi_id == glpi_id)
                .first()
            )
            if result_entity:
                if complete_name is not None:
                    result_entity.complete_name = complete_name
                if name is not None:
                    result_entity.name = name
                session.commit()
                session.flush()
                return result_entity.get_data()
            else:
                logger.debug("id entity no exist for update")
        except Exception:
            logger.error("update Glpi_entity ")
        return None

    @DatabaseHelper._sessionm
    def update_Glpi_location(self, session, glpi_id, complete_name=None, name=None):
        try:
            result_location = (
                session.query(Glpi_location)
                .filter(Glpi_location.glpi_id == glpi_id)
                .first()
            )
            if result_location:
                if complete_name is not None:
                    result_location.complete_name = complete_name
                if name is not None:
                    result_location.name = name
                session.commit()
                session.flush()
                return result_location.get_data()
            else:
                logger.debug("id location no exist for update")
        except Exception:
            logger.error("update Glpi_location ")
        return None

    @DatabaseHelper._sessionm
    def update_Glpi_register_key(self, session, machines_id, name, value, comment=""):
        try:
            if name is not None and name != "":
                result_register_key = (
                    session.query(Glpi_Register_Keys)
                    .filter(
                        or_(
                            Glpi_Register_Keys.machines_id == machines_id,
                            Glpi_Register_Keys.name == name,
                        )
                    )
                    .one()
                )
                session.commit()
                session.flush()
                if result_register_key:
                    return result_register_key.get_data()
                else:
                    logger.debug("id registration no exist for update")
        except Exception:
            logger.error(
                "update Glpi_Register_Keys  : %s for machine %s does not exists"
                % (name, machines_id)
            )
        return None

    @DatabaseHelper._sessionm
    def get_Glpi_entity(self, session, glpi_id):
        """
        get Glpi_entity by glpi id machine
        """
        # logger.error("get_Glpi_entity")
        try:
            result_entity = (
                session.query(Glpi_entity)
                .filter(Glpi_entity.glpi_id == glpi_id)
                .first()
            )
            session.commit()
            session.flush()
            if result_entity:
                return result_entity.get_data()
            else:
                logger.debug("Glpi_entity id : %s does not exists" % glpi_id)
        except Exception as e:
            logger.error("Glpi_entity id : %s does not exists" % glpi_id)
        return None

    @DatabaseHelper._sessionm
    def get_Glpi_location(self, session, glpi_id):
        """
        get Glpi_location by glpi id machine
        """
        # logger.error("get_Glpi_location")
        try:
            result_location = (
                session.query(Glpi_location)
                .filter(Glpi_location.glpi_id == glpi_id)
                .first()
            )
            session.commit()
            session.flush()
            if result_location:
                return result_location.get_data()
            else:
                logger.debug("Glpi_location id : %s des not exists" % glpi_id)
        except Exception as e:
            logger.error("Glpi_location id : %s does not exists" % glpi_id)
        return None

    @DatabaseHelper._sessionm
    def get_Glpi_register_key(self, session, machines_id, name):
        """
        get Glpi_register_key by glpi id machine and name key reg
        """
        # logger.error("get_Glpi_register_key %s %s" %(machines_id, name) )
        try:
            result_register_key = (
                session.query(Glpi_Register_Keys)
                .filter(
                    and_(
                        Glpi_Register_Keys.machines_id == machines_id,
                        Glpi_Register_Keys.name == name,
                    )
                )
                .one()
            )
            result_register_key = result_register_key
            session.commit()
            session.flush()
            if result_register_key:
                return result_register_key.get_data()
            else:
                logger.debug(
                    "Glpi_Register_Keys  : %s"
                    " for machine %s does not exists" % (name, machines_id)
                )
        except Exception as e:
            logger.error(
                "Glpi_Register_Keys  : %s "
                "for machine %s does not exists" % (name, machines_id)
            )
        return None

    @DatabaseHelper._sessionm
    def create_Glpi_entity(self, session, complete_name, name, glpi_id):
        """
        create Glpi_entity
        """
        if glpi_id is None or glpi_id == "":
            logger.warning("create_Glpi_entity glpi_id missing")
            return None
        ret = self.get_Glpi_entity(glpi_id)
        if ret is None:
            # Creation of this entity
            try:
                # We create it if it does not exists
                new_glpi_entity = Glpi_entity()
                new_glpi_entity.complete_name = complete_name
                new_glpi_entity.name = name
                new_glpi_entity.glpi_id = glpi_id
                session.add(new_glpi_entity)
                session.commit()
                session.flush()
                return new_glpi_entity.get_data()
            except Exception as e:
                logger.error(str(e))
                logger.error("glpi_entity error")
        else:
            if ret["name"] == name and ret["complete_name"] == complete_name:
                return ret
            else:
                # update entity
                logger.warning("update entity exist")
                return self.update_Glpi_entity(glpi_id, complete_name, name)
        return None

    @DatabaseHelper._sessionm
    def create_Glpi_location(self, session, complete_name, name, glpi_id):
        """
        create Glpi_location
        """
        if glpi_id is None or glpi_id == "":
            logger.warning("create_Glpi_location glpi_id missing")
            return None

        ret = self.get_Glpi_location(glpi_id)
        if ret is None:
            try:
                new_glpi_location = Glpi_location()
                new_glpi_location.complete_name = complete_name
                new_glpi_location.name = name
                new_glpi_location.glpi_id = glpi_id
                session.add(new_glpi_location)
                session.commit()
                session.flush()
                return new_glpi_location.get_data()
            except Exception as e:
                logger.error(str(e))
                logger.error("create_Glpi_location error")
        else:
            if ret["name"] == name and ret["complete_name"] == complete_name:
                return ret
            else:
                logger.debug("We update the location")
                return self.update_Glpi_location(glpi_id, complete_name, name)
        return None

    @DatabaseHelper._sessionm
    def create_Glpi_register_keys(
        self, session, machines_id, name, value=0, comment=""
    ):
        """
        create Glpi_Register_Keys
        """

        # logger.error("create %s = %s" %(name, value))

        if machines_id is None or machines_id == "" or name is None or name == "":
            return None
        ret = self.get_Glpi_register_key(machines_id, name)
        if ret is None:
            # creation de cette register_keys
            try:
                # creation si cette entite n'existe pas.
                new_glpi_register_keys = Glpi_Register_Keys()
                new_glpi_register_keys.name = name
                new_glpi_register_keys.value = value
                new_glpi_register_keys.machines_id = machines_id
                new_glpi_register_keys.comment = comment
                session.add(new_glpi_register_keys)
                session.commit()
                session.flush()
                return new_glpi_register_keys.get_data()
            except Exception as e:
                logger.error(str(e))
                logger.error("Glpi_register_keys error")
        else:
            if ret["name"] == name and ret["value"] == value:
                return ret
            else:
                logger.warning("We update the register_keys")
                return self.update_Glpi_register_key(machines_id, name, value, comment)
        return None

    @DatabaseHelper._sessionm
    def updateMachineGlpiInformationInventory(
        self, session, glpiinformation, idmachine, data
    ):
        retentity = self.create_Glpi_entity(
            glpiinformation["data"]["complete_entity"][0],
            glpiinformation["data"]["entity"][0],
            glpiinformation["data"]["entity_glpi_id"][0],
        )
        if retentity is None:
            entity_id_xmpp = "NULL"
        else:
            entity_id_xmpp = retentity["id"]

        retlocation = self.create_Glpi_location(
            glpiinformation["data"]["complete_location"][0],
            glpiinformation["data"]["location"][0],
            glpiinformation["data"]["location_glpi_id"][0],
        )
        if retlocation is None:
            location_id_xmpp = "NULL"
        else:
            location_id_xmpp = retlocation["id"]
        if "win" in data["information"]["info"]["platform"].lower():
            for regwindokey in glpiinformation["data"]["reg"]:
                if glpiinformation["data"]["reg"][regwindokey][0] is not None:
                    self.create_Glpi_register_keys(
                        idmachine,
                        regwindokey,
                        value=glpiinformation["data"]["reg"][regwindokey][0],
                    )
        # type au lieu de model pour etre conforme and model remplace manufactured
        # pour avoir meme information que glpi
        return self.updateGLPI_information_machine(
            idmachine,
            "UUID%s" % glpiinformation["data"]["uuidglpicomputer"][0],
            glpiinformation["data"]["description"][0],
            glpiinformation["data"]["owner_firstname"][0],
            glpiinformation["data"]["owner_realname"][0],
            glpiinformation["data"]["owner"][0],
            glpiinformation["data"]["type"][0],
            glpiinformation["data"]["model"][0],
            entity_id_xmpp,
            location_id_xmpp,
        )

    @DatabaseHelper._sessionm
    def updateGLPI_information_machine(
        self,
        session,
        id,
        uuid_inventory,
        description_machine,
        owner_firstname,
        owner_realname,
        owner,
        model,
        manufacturer,
        entity_id_xmpp,
        location_id_xmpp,
    ):
        """
        update Machine table with information retrieved from GLPI
        """
        try:
            entity_id_xmpp = None if entity_id_xmpp in [
                "NULL", ""] else entity_id_xmpp
            location_id_xmpp = (
                None if location_id_xmpp in ["NULL", ""] else location_id_xmpp
            )
            obj = {
                Machines.uuid_inventorymachine: uuid_inventory,
                Machines.glpi_description: description_machine,
                Machines.glpi_owner_firstname: owner_firstname,
                Machines.glpi_owner_realname: owner_realname,
                Machines.glpi_owner: owner,
                Machines.model: model,
                Machines.manufacturer: manufacturer,
                Machines.glpi_entity_id: entity_id_xmpp,
                Machines.glpi_location_id: location_id_xmpp,
            }
            session.query(Machines).filter(Machines.id == id).update(obj)
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.debug("updateMachines error %s->" % str(e))
            return -1

    @DatabaseHelper._sessionm
    def updateName_Qa_custom_command(
        self, session, user, osname, namecmd, customcmd, description
    ):
        """
        update updateName_Qa_custom_command
        """

        try:
            session.query(Qa_custom_command).filter(
                Qa_custom_command.namecmd == namecmd
            ).update(
                {
                    Qa_custom_command.customcmd: customcmd,
                    Qa_custom_command.description: description,
                    Qa_custom_command.os: osname,
                }
            )
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.debug("updateName_Qa_custom_command error %s->" % str(e))
            return -1

    @DatabaseHelper._sessionm
    def delQa_custom_command(self, session, user, osname, namecmd):
        """
        del Qa_custom_command
        """
        try:
            session.query(Qa_custom_command).filter(
                and_(
                    Qa_custom_command.user == user,
                    Qa_custom_command.os == osname,
                    Qa_custom_command.namecmd == namecmd,
                )
            ).delete()
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.debug("delQa_custom_command error %s ->" % str(e))
            return -1

    @DatabaseHelper._sessionm
    def get_list_of_users_for_shared_qa(self, session, namecmd):
        """Return the list of users who are owning the specified QA.
        Param:
            str: namecmd the name of the quickaction
        Returns :
            list of users"""

        query = session.query(Qa_custom_command.user).filter(
            Qa_custom_command.namecmd == namecmd
        )

        if query is not None:
            user_list = [user[0] for user in query]
            return user_list
        else:
            return []

    @DatabaseHelper._sessionm
    def getlistcommandforuserbyos(
        self, session, user, osname=None, min=None, max=None, filt=None, edit=None
    ):
        ret = {
            "len": 0,
            "nb": 0,
            "limit": 0,
            "max": 0,
            "min": 0,
            "filt": "",
            "command": [],
        }
        try:
            if edit is not None:
                # We are in the edition view
                result = session.query(Qa_custom_command).filter(
                    and_(Qa_custom_command.user == user)
                )
            elif osname is None:
                # We are displaying the list of QAs for use where OS is not
                # defined (view list of QAs)
                result = session.query(Qa_custom_command).filter(
                    or_(
                        Qa_custom_command.user == user,
                        Qa_custom_command.user == "allusers",
                    )
                )
            else:
                # We are displaying the list of QAs for use where OS is defined
                # (list QAs for specific machine)
                result = session.query(Qa_custom_command).filter(
                    and_(
                        or_(
                            Qa_custom_command.user == user,
                            Qa_custom_command.user == "allusers",
                        ),
                        Qa_custom_command.os == osname,
                    )
                )

            total = self.get_count(result)
            # todo filter
            if filt is not None:
                result = result.filter(
                    or_(
                        result.namecmd.like("%%%s%%" % (filt)),
                        result.os.like("%%%s%%" % (filt)),
                        result.description.like("%%%s%%" % (filt)),
                    )
                )

            nbfilter = self.get_count(result)

            if min is not None and max is not None:
                result = result.offset(int(min)).limit(int(max) - int(min))
                ret["limit"] = int(max) - int(min)

            if min:
                ret["min"] = min
            if max:
                ret["max"] = max
            if filt:
                ret["filt"] = filt
            result = result.all()
            session.commit()
            session.flush()
            ret["len"] = total
            ret["nb"] = nbfilter

            arraylist = []
            for t in result:
                obj = {}
                obj["user"] = t.user
                obj["os"] = t.os
                obj["namecmd"] = t.namecmd
                obj["customcmd"] = t.customcmd
                obj["description"] = t.description
                arraylist.append(obj)
            ret["command"] = arraylist
            return ret
        except Exception as e:
            logger.debug("getlistcommandforuserbyos error %s->" % str(e))
            return ret

    ################################################

    @DatabaseHelper._sessionm
    def addPackageByOrganization(
        self, session, packageuuid, organization_name=None, organization_id=None
    ):
        """
        addition reference package in packages table for organization id
            the organization input parameter is either organization name or either organization id
            return -1 if not created
        """
        # recupere id organization
        idorganization = -1
        try:
            if organization_id is not None:
                try:
                    result_organization = session.query(Organization).filter(
                        Organization.id == organization_id
                    )
                    result_organization = result_organization.one()
                    session.commit()
                    session.flush()
                    idorganization = result_organization.id
                except Exception as e:
                    logger.debug(
                        "organization id : %s does not exist" % organization_id
                    )
                    return -1
            elif organization_name is not None:
                idorganization = self.getIdOrganization(organization_name)
                if idorganization == -1:
                    return -1
            else:
                return -1

            # addition reference package in listpackages for attribut
            # organization id.
            packageslist = Packages_list()
            packageslist.organization_id = idorganization
            packageslist.packageuuid = packageuuid
            session.add(packageslist)
            session.commit()
            session.flush()
            return packageslist.id
        except Exception as e:
            logger.error(str(e))
            logger.debug(
                "add Package [%s] for Organization : %s %s does not exists"
                % (
                    packageuuid,
                    self.__returntextisNone__(organization_name),
                    self.__returntextisNone__(organization_id),
                )
            )
            return -1

    @DatabaseHelper._sessionm
    def call_procedure(self, session, name_procedure, params=None):
        """
        Appelle une procédure stockée MySQL avec une liste de paramètres.
        Args:
            session: Une session SQLAlchemy active.
            name_procedure (str): Nom de la procédure stockée à appeler.
            params (list, tuple, dict ou int): Paramètres à passer à la procédure.
        Returns:
            Le résultat de l'exécution de la procédure (si applicable).
        Raises:
            ProcedureError: Si une erreur survient lors de l'appel de la procédure.
        """
        try:
            resultat = self._call_procedure(session, name_procedure, params)
            session.commit()
            return resultat
        except Exception as e:
            logger.error(
                f"Erreur lors de l'appel de la procédure {name_procedure} avec les paramètres {params}: {e}",
                exc_info=True
            )
            session.rollback()
            raise ProcedureError(f"Erreur lors de l'appel de la procédure {name_procedure}: {e}") from e

    def _call_procedure(self, session, name_procedure, params=None):
        """
        Appelle une procédure stockée MySQL avec une liste de paramètres.
        Args:
            session: Une session SQLAlchemy active.
            name_procedure (str): Nom de la procédure stockée à appeler.
            params (list, tuple, dict ou int): Paramètres à passer à la procédure.
        Returns:
            Le résultat de l'exécution de la procédure (si applicable).
        """
        logger.debug(f"Appel de la procédure {name_procedure} avec les paramètres {params}")
        if params is None:
            params = ()
        elif not isinstance(params, (list, tuple)):
            params = (params,)
        # Créer des placeholders nommés dynamiques
        placeholders = []
        bind_params = {}
        for i, val in enumerate(params):
            key = f"p{i}"
            placeholders.append(f":{key}")
            bind_params[key] = val
        query = text(f"CALL {name_procedure}({', '.join(placeholders)})")
        resultat = session.execute(query, bind_params)
        return resultat


    def __returntextisNone__(self, para, text=""):
        if para is None:
            return text
        else:
            return para

    ########## gestion packages###############

    ################################

    @DatabaseHelper._sessionm
    def resetPresenceMachine(self, session):
        session.query(Machines).update({Machines.enabled: "0"})
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getIdMachineFromMacaddress(self, session, macaddress):
        presence = (
            session.query(Machines.id)
            .filter(Machines.macaddress.like(macaddress + "%"))
            .first()
        )
        session.commit()
        session.flush()
        return presence

    @DatabaseHelper._sessionm
    def getMachinefrommacadress(self, session, macaddress, agenttype=None):
        """information machine"""
        if agenttype is None:
            machine = (
                session.query(Machines)
                .filter(Machines.macaddress.like(macaddress))
                .first()
            )
        elif agenttype == "machine":
            machine = (
                session.query(Machines)
                .filter(
                    and_(
                        Machines.macaddress.like(macaddress),
                        Machines.agenttype.like("machine"),
                    )
                )
                .first()
            )
        elif agenttype == "relayserver":
            machine = (
                session.query(Machines)
                .filter(
                    and_(
                        Machines.macaddress.like(macaddress),
                        Machines.agenttype.like("relayserver"),
                    )
                )
                .first()
            )
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {
                "id": machine.id,
                "jid": machine.jid,
                "platform": machine.platform,
                "archi": machine.archi,
                "hostname": machine.hostname,
                "uuid_inventorymachine": machine.uuid_inventorymachine,
                "ip_xmpp": machine.ip_xmpp,
                "ippublic": machine.ippublic,
                "macaddress": machine.macaddress,
                "subnetxmpp": machine.subnetxmpp,
                "agenttype": machine.agenttype,
                "classutil": machine.classutil,
                "groupdeploy": machine.groupdeploy,
                "urlguacamole": machine.urlguacamole,
                "picklekeypublic": machine.picklekeypublic,
                "ad_ou_user": machine.ad_ou_user,
                "ad_ou_machine": machine.ad_ou_machine,
                "kiosk_presence": machine.kiosk_presence,
                "lastuser": machine.lastuser,
                "keysyncthing": machine.keysyncthing,
                "enabled": machine.enabled,
                "uuid_serial_machine": machine.uuid_serial_machine,
            }
        return result

    @DatabaseHelper._sessionm
    def getMachinefromuuidsetup(self, session, uuid_serial_machine, agenttype=None):
        """information machine"""
        if agenttype is None:
            machine = (
                session.query(Machines)
                .filter(Machines.uuid_serial_machine.like(uuid_serial_machine))
                .first()
            )
        elif agenttype == "machine":
            machine = (
                session.query(Machines)
                .filter(
                    and_(
                        Machines.uuid_serial_machine.like(uuid_serial_machine),
                        Machines.agenttype.like("machine"),
                    )
                )
                .first()
            )
        elif agenttype == "relayserver":
            machine = (
                session.query(Machines)
                .filter(
                    and_(
                        Machines.uuid_serial_machine.like(uuid_serial_machine),
                        Machines.agenttype.like("relayserver"),
                    )
                )
                .first()
            )
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {
                "id": machine.id,
                "jid": machine.jid,
                "platform": machine.platform,
                "archi": machine.archi,
                "hostname": machine.hostname,
                "uuid_inventorymachine": machine.uuid_inventorymachine,
                "ip_xmpp": machine.ip_xmpp,
                "ippublic": machine.ippublic,
                "macaddress": machine.macaddress,
                "subnetxmpp": machine.subnetxmpp,
                "agenttype": machine.agenttype,
                "classutil": machine.classutil,
                "groupdeploy": machine.groupdeploy,
                "urlguacamole": machine.urlguacamole,
                "picklekeypublic": machine.picklekeypublic,
                "ad_ou_user": machine.ad_ou_user,
                "ad_ou_machine": machine.ad_ou_machine,
                "kiosk_presence": machine.kiosk_presence,
                "lastuser": machine.lastuser,
                "keysyncthing": machine.keysyncthing,
                "enabled": machine.enabled,
                "uuid_serial_machine": machine.uuid_serial_machine,
            }
        return result

    @DatabaseHelper._sessionm
    def addPresenceMachine(
        self,
        session,
        jid,
        platform,
        hostname,
        archi,
        uuid_inventorymachine,
        ip_xmpp,
        subnetxmpp,
        macaddress,
        agenttype,
        classutil="private",
        urlguacamole="",
        groupdeploy="",
        objkeypublic=None,
        ippublic=None,
        ad_ou_user="",
        ad_ou_machine="",
        kiosk_presence="False",
        lastuser="",
        keysyncthing="",
        uuid_serial_machine="",
        glpi_description="",
        glpi_owner_firstname="",
        glpi_owner_realname="",
        glpi_owner="",
        model="",
        manufacturer="",
        json_re="",
        glpi_entity_id=1,
        glpi_location_id=None,
        glpi_regkey_id=None,
    ):
        if uuid_inventorymachine is None:
            uuid_inventorymachine = ""
        msg = "Create Machine"
        pe = -1
        if uuid_serial_machine != "":
            machineforupdate = self.getMachinefromuuidsetup(
                uuid_serial_machine, agenttype=agenttype
            )
        else:
            machineforupdate = self.getMachinefrommacadress(
                macaddress, agenttype=agenttype
            )
        if machineforupdate:
            pe = machineforupdate["id"]
        if pe != -1:
            # update
            maxlenhostname = max(
                [len(machineforupdate["hostname"]), len(hostname)])
            maxlenjid = max([len(machineforupdate["jid"]), len(jid)])
            maxmacadress = max(
                [len(machineforupdate["macaddress"]), len(macaddress)])
            maxip_xmpp = max(
                [len(machineforupdate["ip_xmpp"]),
                 len(ip_xmpp), len("ip_xmpp")]
            )
            maxsubnetxmpp = max(
                [
                    len(machineforupdate["subnetxmpp"]),
                    len(subnetxmpp),
                    len("subnetxmpp"),
                ]
            )
            maxonoff = 6
            uuidold = str(machineforupdate["uuid_inventorymachine"])
            if uuid_inventorymachine is None:
                uuidnew = "None"
            else:
                uuidnew = str(uuid_inventorymachine)
            if lastuser is None or lastuser == "":
                lastuser = str(machineforupdate["lastuser"])
            maxuuid = max([len(uuidold), len(uuidnew)])
            msg = (
                "Update Machine %8s (%s)\n"
                "|%*s|%*s|%*s|%*s|%*s|%*s|%*s|\n"
                "|%*s|%*s|%*s|%*s|%*s|%*s|%*s|\n"
                "by\n"
                "|%*s|%*s|%*s|%*s|%*s|%*s|%*s|"
                % (
                    machineforupdate["id"],
                    uuid_serial_machine,
                    maxlenhostname,
                    "hostname",
                    maxlenjid,
                    "jid",
                    maxmacadress,
                    "macaddress",
                    maxip_xmpp,
                    "ip_xmpp",
                    maxsubnetxmpp,
                    "subnetxmpp",
                    maxonoff,
                    "On/OFF",
                    maxuuid,
                    "UUID",
                    maxlenhostname,
                    machineforupdate["hostname"],
                    maxlenjid,
                    machineforupdate["jid"],
                    maxmacadress,
                    machineforupdate["macaddress"],
                    maxip_xmpp,
                    machineforupdate["ip_xmpp"],
                    maxsubnetxmpp,
                    machineforupdate["subnetxmpp"],
                    maxonoff,
                    machineforupdate["enabled"],
                    maxuuid,
                    uuidold,
                    maxlenhostname,
                    hostname,
                    maxlenjid,
                    jid,
                    maxmacadress,
                    macaddress,
                    maxip_xmpp,
                    ip_xmpp,
                    maxsubnetxmpp,
                    subnetxmpp,
                    maxonoff,
                    "1",
                    6,
                    uuidnew,
                )
            )
            self.logger.warning(msg)
            session.query(Machines).filter(Machines.id == pe).update(
                {
                    Machines.jid: jid,
                    Machines.platform: platform,
                    Machines.hostname: hostname,
                    Machines.archi: archi,
                    Machines.uuid_inventorymachine: uuid_inventorymachine,
                    Machines.ippublic: ippublic,
                    Machines.ip_xmpp: ip_xmpp,
                    Machines.subnetxmpp: subnetxmpp,
                    Machines.macaddress: macaddress,
                    Machines.agenttype: agenttype,
                    Machines.classutil: classutil,
                    Machines.urlguacamole: urlguacamole,
                    Machines.groupdeploy: groupdeploy,
                    Machines.picklekeypublic: objkeypublic,
                    Machines.ad_ou_user: ad_ou_user,
                    Machines.ad_ou_machine: ad_ou_machine,
                    Machines.kiosk_presence: kiosk_presence,
                    Machines.lastuser: lastuser,
                    Machines.keysyncthing: keysyncthing,
                    Machines.enabled: 1,
                    Machines.uuid_serial_machine: uuid_serial_machine,
                }
            )
            session.commit()
            session.flush()
            return pe, msg
        else:
            # create
            lenhostname = len(hostname)
            lenjid = len(jid)
            lenmacadress = len(macaddress)
            lenip_xmpp = len(ip_xmpp)
            lensubnetxmpp = len(subnetxmpp)
            lenonoff = 6
            msg = (
                "creat Machine (%s)\n"
                "|%*s|%*s|%*s|%*s|%*s|%*s|\n"
                "|%*s|%*s|%*s|%*s|%*s|%*s|\n"
                % (
                    uuid_serial_machine,
                    lenhostname,
                    "hostname",
                    lenjid,
                    "jid",
                    lenmacadress,
                    "macaddress",
                    lenip_xmpp,
                    "ip_xmpp",
                    lensubnetxmpp,
                    "subnetxmpp",
                    lenonoff,
                    "On/OFF",
                    lenhostname,
                    hostname,
                    lenjid,
                    jid,
                    lenmacadress,
                    macaddress,
                    lenip_xmpp,
                    ip_xmpp,
                    lensubnetxmpp,
                    subnetxmpp,
                    lenonoff,
                    "1",
                )
            )
            self.logger.debug(msg)
            try:
                new_machine = Machines()
                new_machine.jid = jid
                new_machine.platform = platform
                new_machine.hostname = hostname
                new_machine.archi = archi
                new_machine.uuid_inventorymachine = uuid_inventorymachine
                new_machine.ippublic = ippublic
                new_machine.ip_xmpp = ip_xmpp
                new_machine.subnetxmpp = subnetxmpp
                new_machine.macaddress = macaddress
                new_machine.agenttype = agenttype
                new_machine.classutil = classutil
                new_machine.urlguacamole = urlguacamole
                new_machine.groupdeploy = groupdeploy
                new_machine.picklekeypublic = objkeypublic
                new_machine.ad_ou_user = ad_ou_user
                new_machine.ad_ou_machine = ad_ou_machine
                new_machine.kiosk_presence = kiosk_presence
                new_machine.lastuser = lastuser
                new_machine.keysyncthing = keysyncthing
                new_machine.glpi_description = glpi_description
                new_machine.glpi_owner_firstname = glpi_owner_firstname
                new_machine.glpi_owner_realname = glpi_owner_realname
                new_machine.glpi_owner = glpi_owner
                new_machine.model = model
                new_machine.manufacturer = manufacturer
                new_machine.json_re = json_re
                new_machine.glpi_entity_id = glpi_entity_id
                new_machine.glpi_location_id = glpi_location_id
                new_machine.glpi_regkey_id = glpi_regkey_id
                new_machine.enabled = "1"
                new_machine.uuid_serial_machine = uuid_serial_machine
                session.add(new_machine)
                session.commit()
                session.flush()
                if agenttype == "relayserver":
                    sql = (
                        "UPDATE `xmppmaster`.`relayserver` \
                                SET `enabled`='1' \
                                WHERE `xmppmaster`.`relayserver`.`nameserver`='%s';"
                        % hostname
                    )
                    session.execute(sql)
                    session.commit()
                    session.flush()
                else:
                    sql = """DELETE FROM xmppmaster.machines
                        WHERE
                        hostname LIKE '%s' and
                            id < %s;
                            """ % (
                        hostname,
                        new_machine.id,
                    )
                    self.logger.debug(sql)
                    session.execute(sql)
                    session.commit()
                    session.flush()
            except Exception as e:
                logger.error(str(e))
                msg = str(e)
                return -1, msg
            return new_machine.id, msg

    @DatabaseHelper._sessionm
    def is_jiduser_organization_ad(self, session, jiduser):
        """if user exist return True"""
        sql = """SELECT COUNT(jiduser) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s');""" % (
            jiduser
        )
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret = [m[0] for m in req]
        if ret[0] == 0:
            return False
        return True

    def uuidtoid(self, uuid):
        if uuid.strip().lower().startswith("uuid"):
            return uuid[4:]
        else:
            return uuid

    @DatabaseHelper._sessionm
    def is_id_inventory_organization_ad(self, session, id_inventory):
        """if id_inventory exist return True"""
        sql = """SELECT COUNT(id_inventory) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s');""" % (
            self.uuidtoid(id_inventory)
        )
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret = [m[0] for m in req]
        if ret[0] == 0:
            return False
        return True

    @DatabaseHelper._sessionm
    def is_id_inventory_jiduser_organization_ad(self, session, id_inventory, jiduser):
        """if id_inventory exist return True"""
        sql = """SELECT COUNT(id_inventory) AS nb
            FROM
                 xmppmaster.organization_ad
             WHERE
              jiduser LIKE ('%s')
              and
              id_inventory LIKE ('%s')
              ;""" % (
            jiduser,
            self.uuidtoid(id_inventory),
        )
        req = session.execute(sql)
        session.commit()
        session.flush()
        ret = [m[0] for m in req]
        if ret[0] == 0:
            return False
        return True

    @DatabaseHelper._sessionm
    def getAllOUuser(self, session, ctx, filt=""):
        """
        @return: all ou defined in the xmpp database
        """
        query = session.query(Organization_ad)
        if filter != "":
            query = query.filter(Organization_ad.ouuser.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def getAllOUmachine(self, session, ctx, filt=""):
        """
        @return: all ou defined in the xmpp database
        """
        query = session.query(Organization_ad)
        if filter != "":
            query = query.filter(
                Organization_ad.oumachine.like("%" + filt + "%"))
        ret = query.all()
        session.close()
        return ret

    @DatabaseHelper._sessionm
    def replace_Organization_ad_id_inventory(
        self, session, old_id_inventory, new_id_inventory
    ):
        if old_id_inventory is None:
            logger.warning("Organization AD id inventory is not exits")
            return -1
        try:
            session.query(Organization_ad).filter(
                Organization_ad.id_inventory == self.uuidtoid(old_id_inventory)
            ).update({Organization_ad.id_inventory: self.uuidtoid(new_id_inventory)})
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updateOrganization_ad_id_inventory(
        self,
        session,
        id_inventory,
        jiduser,
        ouuser="",
        oumachine="",
        hostname="",
        username="",
    ):
        """
        update Organization_ad table in base xmppmaster
        """
        try:
            session.query(Organization_ad).filter(
                Organization_ad.id_inventory == self.uuidtoid(id_inventory)
            ).update(
                {
                    Organization_ad.jiduser: jiduser,
                    Organization_ad.id_inventory: self.uuidtoid(id_inventory),
                    Organization_ad.ouuser: ouuser,
                    Organization_ad.oumachine: oumachine,
                    Organization_ad.hostname: hostname,
                    Organization_ad.username: username,
                }
            )
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updateOrganization_ad_jiduser(
        self,
        session,
        id_inventory,
        jiduser,
        ouuser="",
        oumachine="",
        hostname="",
        username="",
    ):
        """
        update Organization_ad table in base xmppmaster
        """
        try:
            session.query(Organization_ad).filter(
                Organization_ad.jiduser == jiduser
            ).update(
                {
                    Organization_ad.jiduser: jiduser,
                    Organization_ad.id_inventory: self.uuidtoid(id_inventory),
                    Organization_ad.ouuser: ouuser,
                    Organization_ad.oumachine: oumachine,
                    Organization_ad.hostname: hostname,
                    Organization_ad.username: username,
                }
            )
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def addOrganization_ad(
        self,
        session,
        id_inventory,
        jiduser,
        ouuser="",
        oumachine="",
        hostname="",
        username="",
    ):
        id = self.uuidtoid(id_inventory)
        new_Organization = Organization_ad()
        new_Organization.id_inventory = id
        new_Organization.jiduser = jiduser
        new_Organization.ouuser = ouuser
        new_Organization.oumachine = oumachine
        new_Organization.hostname = hostname
        new_Organization.username = username
        boolexistuserjid = self.is_jiduser_organization_ad(jiduser)
        if not boolexistuserjid:
            # creation de organization for machine jiduser
            if self.is_id_inventory_organization_ad(id):
                # delete for uuid
                self.delOrganization_ad(id_inventory=id)
            try:
                session.add(new_Organization)
                session.commit()
                session.flush()
            except Exception as e:
                logger.error(
                    "creation Organisation_ad for jid user %s inventory uuid : %s"
                    % (jiduser, id)
                )
                logger.error(
                    "ouuser=%s\noumachine = %s\nhostname=%s\nusername=%s"
                    % (ouuser, oumachine, hostname, username)
                )
                logger.error(str(e))
                return -1
            return new_Organization.id_inventory
        else:
            # update fiche
            self.updateOrganization_ad_jiduser(
                id_inventory,
                jiduser,
                ouuser=ouuser,
                oumachine=oumachine,
                hostname=hostname,
                username=username,
            )
        return new_Organization.id_inventory

    @DatabaseHelper._sessionm
    def delOrganization_ad(self, session, id_inventory=None, jiduser=None):
        """
        supp organization ad
        """
        req = session.query(Organization_ad)
        if id_inventory is not None and jiduser is not None:
            req = req.filter(
                and_(
                    Organization_ad.id_inventory == id_inventory,
                    Organization_ad.jiduser == jiduser,
                )
            )
        elif id_inventory is not None and jiduser is None:
            req = req.filter(Organization_ad.id_inventory == id_inventory)
        elif jiduser is not None and id_inventory is None:
            req = req.filter(Organization_ad.jiduser == jiduser)
        else:
            return False
        try:
            req.delete()
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logger.error("delOrganization_ad : %s " % str(e))
            return False

    @DatabaseHelper._sessionm
    def loginbycommand(self, session, idcommand):
        sql = (
            """SELECT
                    login
                FROM
                    xmppmaster.has_login_command
                WHERE
                    command = %s
                    LIMIT 1 ;"""
            % idcommand
        )
        try:
            result = session.execute(sql)
            session.commit()
            session.flush()
            l = [x[0] for x in result][0]
            return l
        except Exception as e:
            logger.error(str(e))
            return ""

    @DatabaseHelper._sessionm
    def updatedeployinfo(self, session, idcommand):
        """
        this function allows to update the counter of deployments in pause
        """
        try:
            session.query(Has_login_command).filter(
                and_(Has_login_command.command == idcommand)
            ).update(
                {
                    Has_login_command.count_deploy_progress: Has_login_command.count_deploy_progress
                    + 1
                }
            )
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            return -1

    @DatabaseHelper._sessionm
    def wolbroadcastadressmacaddress(self, session, listmacaddress):
        """
        We monitor the mac addresses to check.

        Args:
            session: The SQL Alchemy session
            listmacaddress: The mac addressesses to follow

        Return:
            We return those mac addresses grouped by the broadcast address.
        """
        grp_wol_broadcast_adress = {}
        result = (
            session.query(Network.broadcast, Network.macaddress)
            .distinct(Network.macaddress)
            .filter(
                and_(
                    Network.broadcast != "",
                    Network.broadcast.isnot(None),
                    Network.macaddress.in_(listmacaddress),
                )
            )
            .all()
        )

        if not bool(result):
            logger.error(
                "An error occured while checking the broadcast address.")
            logger.error(
                "Please check that the broadcast information exists for the following mac addresses: %s"
                % listmacaddress
            )

        for t in result:
            if t.broadcast not in grp_wol_broadcast_adress:
                grp_wol_broadcast_adress[t.broadcast] = []
            grp_wol_broadcast_adress[t.broadcast].append(t.macaddress)
        return grp_wol_broadcast_adress

    def convertTimestampToSQLDateTime(self, value):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))

    def convertSQLDateTimeToTimestamp(self, value):
        return time.mktime(time.strptime(value, "%Y-%m-%d %H:%M:%S"))

    @DatabaseHelper._sessionm
    def checkstatusdeploy(self, session, idcommand):
        """
        this function is used to determine the state of the deployment when the deployemnet is scheduled and scheduler
        """
        nowtime = datetime.now()
        try:
            result = (
                session.query(Has_login_command)
                .filter(and_(Has_login_command.command == idcommand))
                .order_by(desc(Has_login_command.id))
                .limit(1)
                .one()
            )
            deployresult = (
                session.query(Deploy)
                .filter(and_(Deploy.command == idcommand))
                .order_by(desc(Deploy.id))
                .limit(1)
                .one()
            )
        except BaseException:
            # error case command supp base nunualy
            return "abandonmentdeploy"
            pass
        if not (deployresult.startcmd <= nowtime and deployresult.endcmd >= nowtime):
            # we are more in the range of deployments.
            # abandonmentdeploy
            for id in self.sessionidforidcommand(idcommand):
                self.updatedeploystate(id, "ERROR UNKNOWN ERROR")
            return "abandonmentdeploy"

        if not (
            result.start_exec_on_time is None
            or str(result.start_exec_on_time) == ""
            or str(result.start_exec_on_time) == "None"
        ):
            # time processing
            if nowtime > result.start_exec_on_time:
                return "run"
        if not (
            result.start_exec_on_nb_deploy is None
            or result.start_exec_on_nb_deploy == ""
        ):
            # nb of deploy processing
            if result.start_exec_on_nb_deploy <= result.count_deploy_progress:
                return "run"
        for id in self.sessionidforidcommand(idcommand):
            self.updatedeploystate(id, "DEPLOYMENT DELAYED")
        return "pause"

    @DatabaseHelper._sessionm
    def clean_syncthing_deploy(self, session, iddeploy, jid_relay):
        """
        analyse table deploy syncthing and search the shared folders which must be terminated.
        """
        datenow = datetime.datetime.now()
        sql = (
            """SELECT
                    xmppmaster.syncthing_machine.sessionid,
                    xmppmaster.syncthing_deploy_group.directory_tmp,
                    xmppmaster.syncthing_machine.jidmachine
                FROM
                    xmppmaster.syncthing_deploy_group
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster
                            ON xmppmaster.syncthing_deploy_group.id =
                                xmppmaster.syncthing_ars_cluster.fk_deploy
                        INNER JOIN
                    xmppmaster.syncthing_machine
                            ON xmppmaster.syncthing_ars_cluster.id =
                                xmppmaster.syncthing_machine.fk_arscluster
                        INNER JOIN
                    xmppmaster.machines
                            ON xmppmaster.machines.uuid_inventorymachine =
                                xmppmaster.syncthing_machine.inventoryuuid
                WHERE
                    xmppmaster.syncthing_deploy_group.id=%s """
            % iddeploy
        )
        if jid_relay is not None:
            sql = (
                sql
                + """
            and
            xmppmaster.syncthing_machine.jid_relay like '%s'"""
                % jid_relay
            )
        sql = sql + ";"
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def deploysyncthingxmpp(self, session):
        """
        analyse the deploy table and creates the sharing syncthing
        """
        # todo: get ARS device
        datenow = datetime.now()
        result = (
            session.query(Deploy)
            .filter(and_(Deploy.startcmd <= datenow, Deploy.syncthing == 1))
            .all()
        )
        id_deploylist = set()
        # TODO: search keysyncthing in table machine.
        session.commit()
        session.flush()
        if not result:
            return list(id_deploylist)
        list_id_ars = {}
        list_ars = set()
        list_cluster = set()
        # syncthing and set stat to 2
        self.chang_status_deploy_syncthing(datenow)
        cluster = self.clusterlistars()
        # keysyncthing  = getMachinefromjid(jid)
        cluster_pris_encharge = []
        gr_pris_en_charge = -1
        command_pris_en_charge = -1

        for t in result:
            if t.group_uuid == "":
                # machine doit faire partie d un grp
                continue
            # if command_pris_en_charge == -1:
            # on deploy qu'une commande sur 1 group a la fois en syncthing
            # command_pris_en_charge = t.command
            # gr_pris_en_charge = t.group_uuid
            # if t.command != command_pris_en_charge or \
            # t.group_uuid != gr_pris_en_charge:
            # continue
            # if t.inventoryuuid.startswith("UUID"):
            # inventoryid = int(t.inventoryuuid[4:])
            # else:
            # inventoryid = int(t.inventoryuuid)

            e = json.loads(t.result)
            package = os.path.basename(e["path"])
            # We create the share if it does not exist.
            id_deploy = self.setSyncthing_deploy_group(
                t.title,
                uuid.uuid4(),
                package,
                t.command,
                t.group_uuid,
                dateend=t.endcmd,
            )
            id_deploylist.add(id_deploy)
            clu = self.clusternum(t.jid_relay)
            ars_cluster_id = self.setSyncthing_ars_cluster(
                clu["numcluster"],
                clu["namecluster"],
                t.jid_relay,
                clu["choose"],
                id_deploy,
                type_partage="cluster",
                devivesyncthing="",
                keypartage="",
            )
            cluster = self.clusterlistars()
            clusterdata = {}
            for z in cluster:
                if t.jid_relay in cluster[z]["listarscluster"]:
                    # on trouve le cluster qui possede ars
                    clusterdata = cluster[z]
            self.setSyncthing_machine(
                t.jidmachine,
                t.jid_relay,
                json.dumps(clusterdata),
                package,
                t.sessionid,
                t.start,
                t.startcmd,
                t.endcmd,
                t.command,
                t.group_uuid,
                t.result,
                ars_cluster_id,
                syncthing=t.syncthing,
                state=t.state,
                user=t.user,
                type_partage="",
                title=t.title,
                inventoryuuid=t.inventoryuuid,
                login=t.login,
                macadress=t.macadress,
                comment="%s_%s"
                % (
                    t.command,
                    t.group_uuid,
                ),
            )

        return list(id_deploylist)

    @DatabaseHelper._sessionm
    def clusternum(self, session, jidars):
        jidars = jidars.split("/")[0]
        sql = (
            """SELECT
                    relayserver.jid,
                    xmppmaster.has_cluster_ars.id_cluster,
                    xmppmaster.cluster_ars.name
                FROM
                    xmppmaster.relayserver
                        INNER JOIN
                    xmppmaster.has_cluster_ars ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                        INNER JOIN
                    xmppmaster.cluster_ars ON xmppmaster.cluster_ars.id = xmppmaster.has_cluster_ars.id_cluster
                WHERE
                    xmppmaster.has_cluster_ars.id_cluster = (SELECT
                            has_cluster_ars.id_cluster
                        FROM
                            xmppmaster.relayserver
                                INNER JOIN
                            xmppmaster.has_cluster_ars ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                                INNER JOIN
                            xmppmaster.cluster_ars ON xmppmaster.cluster_ars.id = xmppmaster.has_cluster_ars.id_cluster
                        WHERE
                            relayserver.jid like '%s%%'
                            AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
                            LIMIT 1);"""
            % jidars
        )
        listars = session.execute(sql)
        session.commit()
        session.flush()
        cluster = {"ars": [], "numcluster": -
                   1, "namecluster": "", "choose": ""}
        n = 0
        for z in listars:
            cluster["ars"].append(z[0])
            cluster["numcluster"] = z[1]
            cluster["namecluster"] = z[2]
            n = n + 1
        if n != 0:
            nb = random.randint(0, n - 1)
            cluster["choose"] = cluster["ars"][nb]
        return cluster

    @DatabaseHelper._sessionm
    def clusterlistars(self, session, enabled=1):
        sql = """SELECT
            GROUP_CONCAT(`jid`) AS 'listarsincluster',
            cluster_ars.name AS 'namecluster',
            cluster_ars.id AS 'numcluster',
            GROUP_CONCAT(`keysyncthing`) AS 'ksync'
        FROM
            xmppmaster.relayserver
                INNER JOIN
            xmppmaster.has_cluster_ars ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                INNER JOIN
            xmppmaster.cluster_ars ON xmppmaster.cluster_ars.id = xmppmaster.has_cluster_ars.id_cluster"""

        if enabled is not None:
            sql = """%s WHERE
            `relayserver`.`enabled` = %s
            AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)           """ % (
                sql,
                enabled,
            )

        sql = sql + " GROUP BY xmppmaster.has_cluster_ars.id_cluster;"
        listars = session.execute(sql)
        session.commit()
        session.flush()
        cluster = {}
        for z in listars:
            if z[3] is None:
                za = ""
            else:
                za = z[3]
            cluster[z[2]] = {
                "listarscluster": z[0].split(","),
                "namecluster": z[1],
                "numcluster": z[2],
                "keysyncthing": za.split(","),
            }
        return cluster

    @DatabaseHelper._sessionm
    def chang_status_deploy_syncthing(self, session, datenow=None):
        if datenow is None:
            datenow = datetime.now()
        sql = (
            """ UPDATE `xmppmaster`.`deploy` SET `syncthing`='2'
                WHERE `startcmd`<= "%s" and syncthing = 1;"""
            % datenow
        )
        session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def change_end_deploy_syncthing(self, session, iddeploy, offsettime=60):
        dateend = datetime.now() + timedelta(minutes=offsettime)
        sql = """ UPDATE `xmppmaster`.`syncthing_deploy_group` SET `dateend`=%s
                WHERE `id`= "%s";""" % (
            dateend,
            iddeploy,
        )

        session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def update_status_deploy_end(self, session):
        """this function schedued by xmppmaster"""
        datenow = datetime.now()
        result = (
            session.query(Deploy)
            .filter(
                and_(Deploy.endcmd < datenow,
                     Deploy.state.like("DEPLOYMENT START%%"))
            )
            .all()
        )
        session.flush()
        session.close()
        for t in result:
            try:
                sql = (
                    """UPDATE `xmppmaster`.`deploy`
                                SET `state`='ERROR UNKNOWN ERROR'
                                WHERE `id`='%s';"""
                    % t.id
                )
                session.execute(sql)
                session.commit()
                session.flush()
            except Exception as e:
                logger.error(str(e))

    @DatabaseHelper._sessionm
    def sessionidforidcommand(self, session, idcommand):
        result = (
            session.query(Deploy.sessionid).filter(
                Deploy.command == idcommand).all()
        )
        if result:
            a = [m[0] for m in result]
            return a
        else:
            return []

    @DatabaseHelper._sessionm
    def datacmddeploy(self, session, idcommand):
        try:
            result = (
                session.query(Has_login_command)
                .filter(and_(Has_login_command.command == idcommand))
                .order_by(desc(Has_login_command.id))
                .limit(1)
                .one()
            )
            session.commit()
            session.flush()
            obj = {"countnb": 0, "exec": True}
            if result.login != "":
                obj["login"] = result.login
            obj["idcmd"] = result.command
            if not (
                result.start_exec_on_time is None
                or str(result.start_exec_on_time) == ""
                or str(result.start_exec_on_time) == "None"
            ):
                obj["exectime"] = str(result.start_exec_on_time)
                obj["exec"] = False

            if result.grpid != "":
                obj["grp"] = result.grpid
            if result.nb_machine_for_deploy != "":
                obj["nbtotal"] = result.nb_machine_for_deploy
            if not (
                result.start_exec_on_nb_deploy is None
                or result.start_exec_on_nb_deploy == ""
            ):
                obj["consignnb"] = result.start_exec_on_nb_deploy
                obj["exec"] = False
            obj["rebootrequired"] = result.rebootrequired
            obj["shutdownrequired"] = result.shutdownrequired
            obj["limit_rate_ko"] = result.bandwidth
            obj["syncthing"] = result.syncthing
            if result.params_json is not None:
                try:
                    params_json = json.loads(result.params_json)
                    if "spooling" in params_json:
                        obj["spooling"] = params_json["spooling"]
                except Exception as e:
                    logger.error(
                        "[the avanced parameters from msc] : " + str(e))

            if result.parameters_deploy is not None:
                try:
                    params = str(result.parameters_deploy)
                    if params == "":
                        return obj
                    if not params.startswith("{"):
                        params = "{" + params
                    if not params.endswith("}"):
                        params = params + "}"
                    obj["paramdeploy"] = json.loads(params)
                except Exception as e:
                    logger.error(
                        "[the avanced parameters must be"
                        " declared in a json dictionary] : " + str(e)
                    )
            return obj
        except Exception as e:
            logger.error("[ obj commandid missing] : " + str(e))
            return {}

    @DatabaseHelper._sessionm
    def adddeploy(
        self,
        session,
        idcommand,
        jidmachine,
        jidrelay,
        host,
        inventoryuuid,
        uuidpackage,
        state,
        sessionid,
        user="",
        login="",
        title="",
        group_uuid=None,
        startcmd=None,
        endcmd=None,
        macadress=None,
        result=None,
        syncthing=None,
    ):
        """
        parameters
        startcmd and endcmd  int(timestamp) either str(datetime)
        """
        createcommand = datetime.now()
        try:
            start = int(startcmd)
            end = int(endcmd)
            startcmd = datetime.fromtimestamp(
                start).strftime("%Y-%m-%d %H:%M:%S")
            endcmd = datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            # logger.error(str(e))
            pass
        # del doublon macadess
        if macadress is not None:
            adressemac = str(macadress).split("||")
            adressemac = list(set(adressemac))
            macadress = "||".join(adressemac)
        # recupere login command
        if login == "":
            login = self.loginbycommand(idcommand)[0]
        try:
            new_deploy = Deploy()
            new_deploy.group_uuid = group_uuid
            new_deploy.jidmachine = jidmachine
            new_deploy.jid_relay = jidrelay
            new_deploy.host = host
            new_deploy.inventoryuuid = inventoryuuid
            new_deploy.pathpackage = uuidpackage
            new_deploy.state = state
            new_deploy.sessionid = sessionid
            new_deploy.user = user
            new_deploy.command = idcommand
            new_deploy.login = login
            new_deploy.startcmd = startcmd
            new_deploy.endcmd = endcmd
            new_deploy.start = createcommand
            new_deploy.macadress = macadress
            new_deploy.title = title
            if result is not None:
                new_deploy.result = result
            if syncthing is not None:
                new_deploy.syncthing = syncthing
            session.add(new_deploy)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
        return new_deploy.id

    @DatabaseHelper._sessionm
    def deploy_machine_partage_exist(self, session, jidmachine, uidpackage):
        sql = """SELECT
                    *
                FROM
                    xmppmaster.syncthing_machine
                        INNER JOIN
                    xmppmaster.syncthing_ars_cluster ON xmppmaster.syncthing_ars_cluster.id = xmppmaster.syncthing_machine.fk_arscluster
                        INNER JOIN
                    xmppmaster.syncthing_deploy_group ON xmppmaster.syncthing_deploy_group.id = xmppmaster.syncthing_ars_cluster.fk_deploy
                WHERE
                    xmppmaster.syncthing_machine.jidmachine LIKE '%s'
                        AND xmppmaster.syncthing_deploy_group.package LIKE '%s'
                LIMIT 1;""" % (
            jidmachine,
            uidpackage,
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result][0]

    @DatabaseHelper._sessionm
    def addcluster_resources(
        self,
        session,
        jidmachine,
        jidrelay,
        hostname,
        sessionid,
        login="",
        startcmd=None,
        endcmd=None,
    ):
        """
        add ressource for cluster ressource
        """
        self.clean_resources(jidmachine)
        try:
            new_cluster_resources = Cluster_resources()
            new_cluster_resources.jidmachine = jidmachine
            new_cluster_resources.jidrelay = jidrelay
            new_cluster_resources.hostname = hostname
            new_cluster_resources.sessionid = sessionid
            new_cluster_resources.login = login
            new_cluster_resources.startcmd = startcmd
            new_cluster_resources.endcmd = endcmd
            session.add(new_cluster_resources)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
        return new_cluster_resources.id

    @DatabaseHelper._sessionm
    def getcluster_resources(self, session, jidmachine):
        clusterresources = (
            session.query(Cluster_resources)
            .filter(Cluster_resources.jidmachine == str(jidmachine))
            .all()
        )
        session.commit()
        session.flush()
        ret = {"len": len(clusterresources)}
        arraylist = []
        for t in clusterresources:
            obj = {}
            obj["jidmachine"] = t.jidmachine
            obj["jidrelay"] = t.jidrelay
            obj["hostname"] = t.hostname
            obj["sessionid"] = t.sessionid
            obj["login"] = t.login
            obj["startcmd"] = str(t.startcmd)
            obj["endcmd"] = str(t.endcmd)
            arraylist.append(obj)
        ret["resource"] = arraylist
        self.clean_resources(jidmachine)
        return ret

    @DatabaseHelper._sessionm
    def clean_resources(self, session, jidmachine):
        session.query(Cluster_resources).filter(
            Cluster_resources.jidmachine == str(jidmachine)
        ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def delete_resources(self, session, sessionid):
        session.query(Cluster_resources).filter(
            Cluster_resources.sessionid == str(sessionid)
        ).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def getlinelogswolcmd(self, session, idcommand, uuid):
        log = (
            session.query(Logs)
            .filter(
                and_(
                    Logs.sessionname == str(idcommand),
                    Logs.type == "wol",
                    Logs.who == uuid,
                )
            )
            .order_by(Logs.id)
        )
        log = log.all()
        session.commit()
        session.flush()
        ret = {}
        ret["len"] = len(log)
        arraylist = []
        for t in log:
            obj = {}
            obj["type"] = t.type
            obj["date"] = t.date
            obj["text"] = t.text
            obj["sessionname"] = t.sessionname
            obj["priority"] = t.priority
            obj["who"] = t.who
            arraylist.append(obj)
        ret["log"] = arraylist
        return ret

    @DatabaseHelper._sessionm
    def get_machine_stop_deploy(self, session, cmdid, inventoryuuid):
        """
        It is used  to get a list of machines with deploiements to stop.

        Args:
            session: The SQL Alchemy session
            cmdid: The id of the command ( = the deploiement )
            inventoryuuid: The id of the machine on which we are trying to deploy.

        Returns:
            For the machine with `cmdid` and `inventoryuuid`, it returns a dict with
            informations about this deploy for the machine ( title, pathpackage,pathpackage, jidmachine, etc.)

            There is two possible errors:
                1- If no machine is found ( the `cmdid` or `inventoryuuid` does not exist.
                2- If there is more than one machine answering the request.

            For this two specific cases, it returns an empty dict.
        """
        machine = {}
        try:
            query = session.query(Deploy).filter(
                and_(Deploy.inventoryuuid == inventoryuuid,
                     Deploy.command == cmdid)
            )
            query = query.one()
            session.commit()
            session.flush()

        except NoResultFound as e:
            logger.error(str(e))
            logger.error(
                "We tried to stop the deploiement for the cmd %s. We did not find the uuid %s"
                % (cmdid, inventoryuuid)
            )
            return machine

        except MultipleResultsFound as e:
            logger.error(str(e))
            logger.error(
                "When stopping the deploiement we detected several machines for the cmd %s and uuid %s "
                % (cmdid, inventoryuuid)
            )
            return machine

        machine["len"] = 0

        try:
            machine["len"] = 1
            machine["title"] = query.title
            machine["pathpackage"] = query.pathpackage
            machine["jid_relay"] = query.jid_relay
            machine["inventoryuuid"] = query.inventoryuuid
            machine["jidmachine"] = query.jidmachine
            machine["state"] = query.state
            machine["sessionid"] = query.sessionid
            machine["start"] = query.start
            machine["startcmd"] = query.startcmd
            machine["endcmd"] = query.endcmd
            machine["host"] = query.host
            machine["user"] = query.user
            machine["login"] = str(query.login)
            machine["command"] = query.command
            machine["group_uuid"] = query.group_uuid
            machine["macadress"] = query.macadress
            machine["syncthing"] = query.syncthing
        except Exception as e:
            logger.error(str(e))

        return machine

    @DatabaseHelper._sessionm
    def get_group_stop_deploy(self, session, grpid, cmdid):
        """
        this function return the machines list for 1 group id and 1 command id
        """
        machine = session.query(Deploy).filter(
            and_(
                Deploy.group_uuid == grpid,
                Deploy.command == cmdid,
                not_(Deploy.sessionid.like("missingagent%")),
            )
        )
        machine = machine.all()
        session.commit()
        session.flush()
        ret = {}
        ret["len"] = len(machine)
        arraylist = []
        for t in machine:
            obj = {}
            obj["title"] = t.title
            obj["pathpackage"] = t.pathpackage
            obj["jid_relay"] = t.jid_relay
            obj["inventoryuuid"] = t.inventoryuuid
            obj["jidmachine"] = t.jidmachine
            obj["state"] = t.state
            obj["sessionid"] = t.sessionid
            obj["start"] = t.start
            obj["startcmd"] = t.startcmd
            obj["endcmd"] = t.endcmd
            obj["host"] = t.host
            obj["user"] = t.user
            obj["login"] = str(t.login)
            obj["command"] = t.command
            obj["group_uuid"] = t.group_uuid
            obj["macadress"] = t.macadress
            obj["syncthing"] = t.syncthing
            arraylist.append(obj)
        ret["objectdeploy"] = arraylist
        return ret

    @DatabaseHelper._sessionm
    def getstatdeployfromcommandidstartdate(self, session, command_id, datestart):
        try:
            machinedeploy = (
                session.query(Deploy.state, func.count(Deploy.state))
                .filter(
                    and_(Deploy.command == command_id,
                         Deploy.startcmd == datestart)
                )
                .group_by(Deploy.state)
            )
            machinedeploy = machinedeploy.all()
            ret = {
                "totalmachinedeploy": 0,
                "deploymentsuccess": 0,
                "abortontimeout": 0,
                "abortmissingagent": 0,
                "abortinconsistentglpiinformation": 0,
                "abortrelaydown": 0,
                "abortalternativerelaysdown": 0,
                "abortinforelaymissing": 0,
                "errorunknownerror": 0,
                "abortpackageidentifiermissing": 0,
                "abortpackagenamemissing": 0,
                "abortpackageversionmissing": 0,
                "abortpackageworkflowerror": 0,
                "abortdescriptormissing": 0,
                "abortmachinedisappeared": 0,
                "abortdeploymentcancelledbyuser": 0,
                "aborttransferfailed": 0,
                "abortpackageexecutionerror": 0,
                "abortduplicatemachines": 0,
                "deploymentstart": 0,
                "wol1": 0,
                "wol2": 0,
                "wol3": 0,
                "waitingmachineonline": 0,
                "deploymentpending": 0,
                "deploymentdelayed": 0,
                "deploymentspooled": 0,
                "errorhashmissing": 0,
                "aborthashinvalid": 0,
                "otherstatus": 0,
            }
            dynamic_status_list = self.get_log_status()
            dynamic_label = []
            dynamic_status = []
            if dynamic_status_list != []:
                for status in dynamic_status_list:
                    ret[status["label"]] = 0
                    dynamic_label.append(status["label"])
                    dynamic_status.append(status["status"])

            liststatus = {x[0]: x[1] for x in machinedeploy}
            totalmachinedeploy = 0
            for t in liststatus:
                ret["totalmachinedeploy"] += liststatus[t]

                if t == "DEPLOYMENT SUCCESS":
                    ret["deploymentsuccess"] = liststatus[t]
                elif t == "ABORT ON TIMEOUT":
                    ret["abortontimeout"] = liststatus[t]
                elif t == "ABORT MISSING AGENT":
                    ret["abortmissingagent"] = liststatus[t]
                elif t == "ABORT INCONSISTENT GLPI INFORMATION":
                    ret["abortinconsistentglpiinformation"] = liststatus[t]
                elif t == "ABORT RELAY DOWN":
                    ret["abortrelaydown"] = liststatus[t]
                elif t == "ABORT ALTERNATIVE RELAYS DOWN":
                    ret["abortalternativerelaysdown"] = liststatus[t]
                elif t == "ABORT INFO RELAY MISSING":
                    ret["abortinforelaymissing"] = liststatus[t]
                elif t == "ERROR UNKNOWN ERROR":
                    ret["errorunknownerror"] = liststatus[t]
                elif t == "ABORT PACKAGE IDENTIFIER MISSING":
                    ret["abortpackageidentifiermissing"] = liststatus[t]
                elif t == "ABORT PACKAGE NAME MISSING":
                    ret["abortpackagenamemissing"] = liststatus[t]
                elif t == "ABORT PACKAGE VERSION MISSING":
                    ret["abortpackageversionmissing"] = liststatus[t]
                elif t == "ABORT PACKAGE WORKFLOW ERROR":
                    ret["abortpackageworkflowerror"] = liststatus[t]
                elif t == "ABORT DESCRIPTOR MISSING":
                    ret["abortdescriptormissing"] = liststatus[t]
                elif t == "ABORT MACHINE DISAPPEARED":
                    ret["abortmachinedisappeared"] = liststatus[t]
                elif t == "ABORT DEPLOYMENT CANCELLED BY USER":
                    ret["abortdeploymentcancelledbyuser"] = liststatus[t]
                elif t == "ABORT PACKAGE EXECUTION ERROR":
                    ret["abortpackageexecutionerror"] = liststatus[t]
                elif t == "ABORT DUPLICATE MACHINES":
                    ret["abortduplicatemachines"] = liststatus[t]
                elif t == "DEPLOYMENT START":
                    ret["deploymentstart"] = liststatus[t]
                elif t == "WOL 1":
                    ret["wol1"] = liststatus[t]
                elif t == "WOL 2":
                    ret["wol2"] = liststatus[t]
                elif t == "WOL 3":
                    ret["wol3"] = liststatus[t]
                elif t == "WAITING MACHINE ONLINE":
                    ret["waitingmachineonline"] = liststatus[t]
                elif t == "DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)":
                    ret["deploymentpending"] = liststatus[t]
                elif t == "DEPLOYMENT DELAYED":
                    ret["deploymentdelayed"] = liststatus[t]
                elif t == "ERROR HASH MISSING":
                    ret["errorhashmissing"] = liststatus[t]
                elif t == "ABORT HASH INVALID":
                    ret["aborthashinvalid"] = liststatus[t]

                elif t in dynamic_status:
                    index = dynamic_status.index(t)
                    ret[dynamic_label[index]] = liststatus[t]
                else:
                    ret["otherstatus"] = liststatus[t]
            return ret
        except Exception:
            return ret

    @DatabaseHelper._sessionm
    def getstatdeploy_from_command_id_and_title(self, session, command_id, title):
        """
        Retrieve the deploy statistics based on the command_id and name
        Args:
            session: The SQL Alchemy session
            command_id: id of the deploy
            title: The name of deploy
        Return:
            It returns the number of machines per status.
        """
        try:
            sql = """
                SELECT state, COUNT(*)
                FROM deploy
                WHERE (inventoryuuid, id) IN (
                    SELECT inventoryuuid, MAX(id)
                    FROM deploy
                    WHERE command = :command_id AND title = :title
                    GROUP BY inventoryuuid
                )
                GROUP BY state;
            """
            machinedeploy = session.execute(
                sql, {"command_id": command_id, "title": title}
            )
            machinedeploy = machinedeploy.fetchall()
            ret = {
                "totalmachinedeploy": 0,
                "deploymentsuccess": 0,
                "uninstallsuccess": 0,
                "abortontimeout": 0,
                "abortmissingagent": 0,
                "abortinconsistentglpiinformation": 0,
                "abortrelaydown": 0,
                "abortalternativerelaysdown": 0,
                "abortinforelaymissing": 0,
                "errorunknownerror": 0,
                "abortpackageidentifiermissing": 0,
                "abortpackagenamemissing": 0,
                "abortpackageversionmissing": 0,
                "abortpackageworkflowerror": 0,
                "abortdescriptormissing": 0,
                "abortmachinedisappeared": 0,
                "abortdeploymentcancelledbyuser": 0,
                "aborttransferfailed": 0,
                "abortpackageexecutionerror": 0,
                "abortduplicatemachines": 0,
                "deploymentstart": 0,
                "wol1": 0,
                "wol2": 0,
                "wol3": 0,
                "waitingmachineonline": 0,
                "deploymentpending": 0,
                "deploymentdelayed": 0,
                "deploymentspooled": 0,
                "errorhashmissing": 0,
                "aborthashinvalid": 0,
                "otherstatus": 0,
            }
            dynamic_status_list = self.get_log_status()
            dynamic_label = []
            dynamic_status = []
            if dynamic_status_list != []:
                for status in dynamic_status_list:
                    ret[status["label"]] = 0
                    dynamic_label.append(status["label"])
                    dynamic_status.append(status["status"])

            liststatus = {x[0]: x[1] for x in machinedeploy}
            totalmachinedeploy = 0
            for t in liststatus:
                ret["totalmachinedeploy"] += liststatus[t]

                if t == "DEPLOYMENT SUCCESS":
                    ret["deploymentsuccess"] = liststatus[t]
                elif t == "UNINSTALL SUCCESS":
                    ret["uninstallsuccess"] = liststatus[t]
                elif t == "ABORT ON TIMEOUT":
                    ret["abortontimeout"] = liststatus[t]
                elif t == "ABORT MISSING AGENT":
                    ret["abortmissingagent"] = liststatus[t]
                elif t == "ABORT INCONSISTENT GLPI INFORMATION":
                    ret["abortinconsistentglpiinformation"] = liststatus[t]
                elif t == "ABORT RELAY DOWN":
                    ret["abortrelaydown"] = liststatus[t]
                elif t == "ABORT ALTERNATIVE RELAYS DOWN":
                    ret["abortalternativerelaysdown"] = liststatus[t]
                elif t == "ABORT INFO RELAY MISSING":
                    ret["abortinforelaymissing"] = liststatus[t]
                elif t == "ERROR UNKNOWN ERROR":
                    ret["errorunknownerror"] = liststatus[t]
                elif t == "ABORT PACKAGE IDENTIFIER MISSING":
                    ret["abortpackageidentifiermissing"] = liststatus[t]
                elif t == "ABORT PACKAGE NAME MISSING":
                    ret["abortpackagenamemissing"] = liststatus[t]
                elif t == "ABORT PACKAGE VERSION MISSING":
                    ret["abortpackageversionmissing"] = liststatus[t]
                elif t == "ABORT PACKAGE WORKFLOW ERROR":
                    ret["abortpackageworkflowerror"] = liststatus[t]
                elif t == "ABORT DESCRIPTOR MISSING":
                    ret["abortdescriptormissing"] = liststatus[t]
                elif t == "ABORT MACHINE DISAPPEARED":
                    ret["abortmachinedisappeared"] = liststatus[t]
                elif t == "ABORT DEPLOYMENT CANCELLED BY USER":
                    ret["abortdeploymentcancelledbyuser"] = liststatus[t]
                elif t == "ABORT PACKAGE EXECUTION ERROR":
                    ret["abortpackageexecutionerror"] = liststatus[t]
                elif t == "ABORT DUPLICATE MACHINES":
                    ret["abortduplicatemachines"] = liststatus[t]
                elif t == "DEPLOYMENT START":
                    ret["deploymentstart"] = liststatus[t]
                elif t == "WOL 1":
                    ret["wol1"] = liststatus[t]
                elif t == "WOL 2":
                    ret["wol2"] = liststatus[t]
                elif t == "WOL 3":
                    ret["wol3"] = liststatus[t]
                elif t == "WAITING MACHINE ONLINE":
                    ret["waitingmachineonline"] = liststatus[t]
                elif t == "DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)":
                    ret["deploymentpending"] = liststatus[t]
                elif t == "DEPLOYMENT DELAYED":
                    ret["deploymentdelayed"] = liststatus[t]
                elif t == "ERROR HASH MISSING":
                    ret["errorhashmissing"] = liststatus[t]
                elif t == "ABORT HASH INVALID":
                    ret["aborthashinvalid"] = liststatus[t]

                elif t in dynamic_status:
                    index = dynamic_status.index(t)
                    ret[dynamic_label[index]] = liststatus[t]
                else:
                    ret["otherstatus"] = liststatus[t]
            return ret
        except Exception:
            return ret

    @DatabaseHelper._sessionm
    def getstatdeploy_from_command_id_and_title_for_convergence(self, session, command_id, title):
        """
        Stats par état pour le dernier déploiement (command_id + title LIKE),
        limitées aux machines encore présentes dans l'inventaire (xmppmaster.machines).
        """
        try:
            global_deploy = (
                session.query(Deploy)
                .filter(Deploy.command == command_id, Deploy.title.like(f"%{title}%"))
                .order_by(Deploy.start.desc())
                .first()
            )
            if not global_deploy:
                return {"totalmachinedeploy": 0}

            params = {
                "command_id": command_id,
                "group_uuid": global_deploy.group_uuid,
                "title_like": f"%{title}%",
            }

            sql = text("""
                SELECT d.state, COUNT(*) AS count
                FROM xmppmaster.deploy d
                JOIN (
                    SELECT inventoryuuid, MAX(id) AS latest_id
                    FROM xmppmaster.deploy
                    WHERE command = :command_id
                    AND group_uuid = :group_uuid
                    AND title LIKE :title_like
                    GROUP BY inventoryuuid
                ) ld ON ld.inventoryuuid = d.inventoryuuid
                AND ld.latest_id     = d.id
                JOIN xmppmaster.machines m
                ON m.uuid_inventorymachine = d.inventoryuuid
                WHERE d.command    = :command_id
                AND d.group_uuid = :group_uuid
                AND d.title      LIKE :title_like
                GROUP BY d.state
            """)

            rows = session.execute(sql, params).fetchall()

            if not rows:
                return {"totalmachinedeploy": 0}

            ret = {
                "totalmachinedeploy": 0,
                "deploymentsuccess": 0,
                "uninstallsuccess": 0,
                "abortontimeout": 0,
                "abortmissingagent": 0,
                "abortinconsistentglpiinformation": 0,
                "abortrelaydown": 0,
                "abortalternativerelaysdown": 0,
                "abortinforelaymissing": 0,
                "errorunknownerror": 0,
                "abortpackageidentifiermissing": 0,
                "abortpackagenamemissing": 0,
                "abortpackageversionmissing": 0,
                "abortpackageworkflowerror": 0,
                "abortdescriptormissing": 0,
                "abortmachinedisappeared": 0,
                "abortdeploymentcancelledbyuser": 0,
                "aborttransferfailed": 0,
                "abortpackageexecutionerror": 0,
                "abortduplicatemachines": 0,
                "deploymentstart": 0,
                "wol1": 0,
                "wol2": 0,
                "wol3": 0,
                "waitingmachineonline": 0,
                "deploymentpending": 0,
                "deploymentdelayed": 0,
                "deploymentspooled": 0,
                "errorhashmissing": 0,
                "aborthashinvalid": 0,
                "errortransferfailed": 0,
                "abortpackageexecutioncancelled": 0,
                "abortmissingdependency": 0,
                "restartdeploy": 0,
                "otherstatus": 0,
            }

            dynamic_status_list = self.get_log_status() or []
            code_to_label = {d["status"]: d["label"] for d in dynamic_status_list}
            for d in dynamic_status_list:
                ret.setdefault(d["label"], 0)

            mapping = {
                "DEPLOYMENT SUCCESS": "deploymentsuccess",
                "UNINSTALL SUCCESS": "uninstallsuccess",
                "ABORT ON TIMEOUT": "abortontimeout",
                "ABORT MISSING AGENT": "abortmissingagent",
                "ABORT INCONSISTENT GLPI INFORMATION": "abortinconsistentglpiinformation",
                "ABORT RELAY DOWN": "abortrelaydown",
                "ABORT ALTERNATIVE RELAYS DOWN": "abortalternativerelaysdown",
                "ABORT INFO RELAY MISSING": "abortinforelaymissing",
                "ERROR UNKNOWN ERROR": "errorunknownerror",
                "ABORT PACKAGE IDENTIFIER MISSING": "abortpackageidentifiermissing",
                "ABORT PACKAGE NAME MISSING": "abortpackagenamemissing",
                "ABORT PACKAGE VERSION MISSING": "abortpackageversionmissing",
                "ABORT PACKAGE WORKFLOW ERROR": "abortpackageworkflowerror",
                "ABORT DESCRIPTOR MISSING": "abortdescriptormissing",
                "ABORT MACHINE DISAPPEARED": "abortmachinedisappeared",
                "ABORT DEPLOYMENT CANCELLED BY USER": "abortdeploymentcancelledbyuser",
                "ABORT PACKAGE EXECUTION ERROR": "abortpackageexecutionerror",
                "ABORT DUPLICATE MACHINES": "abortduplicatemachines",
                "DEPLOYMENT START": "deploymentstart",
                "WOL 1": "wol1", "WOL 2": "wol2", "WOL 3": "wol3",
                "WAITING MACHINE ONLINE": "waitingmachineonline",
                "DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)": "deploymentpending",
                "DEPLOYMENT DELAYED": "deploymentdelayed",
                "DEPLOYMENT SPOOLED": "deploymentspooled",
                "ERROR HASH MISSING": "errorhashmissing",
                "ABORT HASH INVALID": "aborthashinvalid",
                "ERROR TRANSFER FAILED": "errortransferfailed",
                "ABORT PACKAGE EXECUTION CANCELLED": "abortpackageexecutioncancelled",
                "ABORT MISSING DEPENDENCY": "abortmissingdependency",
                "RESTART DEPLOY": "restartdeploy",
            }

            for state, count in rows:
                count = int(count or 0)
                ret["totalmachinedeploy"] += count
                if state in mapping:
                    ret[mapping[state]] = count
                elif state in code_to_label:
                    ret[code_to_label[state]] = count
                else:
                    ret["otherstatus"] += count

            return ret
        except Exception as e:
            logging.getLogger().error(f"ERROR: {str(e)}")
            return {"totalmachinedeploy": 0}

    @DatabaseHelper._sessionm
    def getdeployment_cmd_and_title(
        self, session, command_id, title, filter="", start=0, limit=-1
    ):
        """
        Get the list of deploys based on the command_id and title of the packages.

        Arg:
            sesion: The SQL Alchemy session
            command_id: The id the package
            title: Name of the package
            filter: Used filters in the web page
            start: Number of the first package to show.
            limit: Maximum number of deploys sent at once.
        Return:
            It returns the list of the deploys

        """
        criterion = filter["criterion"]
        filter = filter["filter"]

        start = int(start)
        limit = int(limit)

        query = session.query(Deploy).filter(
            and_(Deploy.command == command_id, Deploy.title == title)
        )
        if filter == "status" and criterion != "":
            query = query.filter(
                or_(
                    Deploy.state.contains(criterion),
                    Deploy.inventoryuuid.contains(criterion),
                )
            )

        if filter == "relays" and criterion != "":
            query = query.join(
                Machines, Machines.groupdeploy == Deploy.jid_relay)

            query = query.filter(
                and_(
                    or_(
                        Machines.groupdeploy.contains(criterion),
                        Machines.hostname.contains(criterion),
                        Machines.uuid_serial_machine.contains(criterion),
                    ),
                    Machines.agenttype == "relayserver",
                )
            )

        if filter != "infos":
            count = query.count()
            if limit != -1:
                query = query.offset(start).limit(limit)
        else:
            count = 0
        result = query.all()
        elements = {"id": [], "uuid": [], "status": []}

        for deployment in result:
            elements["id"].append(deployment.inventoryuuid.replace("UUID", ""))
            elements["uuid"].append(deployment.inventoryuuid)
            elements["status"].append(deployment.state)
        return {"total": count, "datas": elements}

    @DatabaseHelper._sessionm
    def getdeployment_cmd_and_title_for_convergence(
        self, session, command_id, title, filter="", start=0, limit=-1
    ):
        """
        Get the most recent deploys based on command_id and partial title match,
        returning a simplified data format for the convergence.

        Args:
            session: SQLAlchemy session.
            command_id: The command ID to match.
            title: Partial title for a LIKE query.
            filter: Optional filters for status or other criteria.
            start: Offset for pagination.
            limit: Maximum number of records to return.

        Returns:
            dict: Contains the most recent deployments with simplified fields.
        """
        try:
            global_deploy = (
                session.query(Deploy)
                .filter(Deploy.command == command_id, Deploy.title.like(f"%{title}%"))
                .order_by(Deploy.start.desc())
                .first()
            )

            if not global_deploy:
                return {"total": 0, "datas": {"id": [], "uuid": [], "status": []}}

            group_uuid = global_deploy.group_uuid

            subq = (
                session.query(
                    Deploy.jidmachine.label("jidmachine"),
                    func.max(Deploy.start).label("latest_start"),
                )
                .filter(
                    Deploy.command == command_id,
                    Deploy.group_uuid == group_uuid,
                    Deploy.title.like(f"%{title}%"),
                )
                .group_by(Deploy.jidmachine)
                .subquery()
            )

            query = (
                session.query(Deploy)
                .join(
                    subq,
                    and_(
                        Deploy.jidmachine == subq.c.jidmachine,
                        Deploy.start == subq.c.latest_start,
                    ),
                )
                .filter(
                    Deploy.command == command_id,
                    Deploy.group_uuid == group_uuid,
                    Deploy.title.like(f"%{title}%"),
                )
            )

            if limit != -1:
                query = query.offset(int(start)).limit(int(limit))

            result = query.all()

            elements = {
                "total": len(result),
                "datas": {
                    "id": [],
                    "uuid": [],
                    "status": [],
                },
            }

            for deploy in result:
                simplified_id = deploy.inventoryuuid.replace("UUID", "")
                elements["datas"]["id"].append(simplified_id)
                elements["datas"]["uuid"].append(deploy.inventoryuuid)
                elements["datas"]["status"].append(deploy.state)

            return elements

        except Exception as e:
            logging.getLogger().error(f"ERROR : {str(e)}")
            return {"total": 0, "datas": {"id": [], "uuid": [], "status": []}}

    @DatabaseHelper._sessionm
    def getdeployment(self, session, command_id, filter="", start=0, limit=-1):
        criterion = filter["criterion"]
        filter = filter["filter"]

        start = int(start)
        limit = int(limit)

        query = session.query(Deploy).filter(Deploy.command == command_id)
        if filter == "status" and criterion != "":
            query = query.filter(
                or_(
                    Deploy.state.contains(criterion),
                    Deploy.inventoryuuid.contains(criterion),
                )
            )

        elif filter == "relays" and criterion != "":
            query = query.filter(Deploy.jid_relay.contains(criterion))

        if filter != "infos":
            count = query.count()
            if limit != -1:
                query = query.offset(start).limit(limit)
        else:
            count = 0
        result = query.all()
        elements = {"id": [], "uuid": [], "status": []}
        for deployment in result:
            elements["id"].append(deployment.inventoryuuid.replace("UUID", ""))
            elements["uuid"].append(deployment.inventoryuuid)
            elements["status"].append(deployment.state)

        return {"total": count, "datas": elements}

    @DatabaseHelper._sessionm
    def getdeployfromcommandid(self, session, command_id, uuid):
        if uuid == "UUID_NONE":
            relayserver = session.query(Deploy).filter(
                and_(Deploy.command == command_id)
            )
            # ,Deploy.result .isnot(None)
        else:
            relayserver = session.query(Deploy).filter(
                and_(Deploy.inventoryuuid == uuid,
                     Deploy.command == command_id)
            )
            # , Deploy.result .isnot(None)
        # print relayserver
        relayserver = relayserver.all()
        session.commit()
        session.flush()
        ret = {}
        ret["len"] = len(relayserver)
        arraylist = []
        for t in relayserver:
            obj = {}
            obj["pathpackage"] = t.pathpackage
            obj["jid_relay"] = t.jid_relay
            obj["inventoryuuid"] = t.inventoryuuid
            obj["jidmachine"] = t.jidmachine
            obj["state"] = t.state
            obj["sessionid"] = t.sessionid
            obj["start"] = t.start
            if t.result is None:
                obj["result"] = ""
            else:
                obj["result"] = t.result
            obj["host"] = t.host
            obj["user"] = t.user
            obj["login"] = str(t.login)
            obj["command"] = t.command
            arraylist.append(obj)
        ret["objectdeploy"] = arraylist
        return ret

    @DatabaseHelper._sessionm
    def getdeployfromcommandid_for_convergence(self, session, command_id, uuid):
        try:
            if uuid == "UUID_NONE":
                global_deploy = (
                    session.query(Deploy)
                    .filter(
                        Deploy.command == command_id, Deploy.title.like(
                            "%Convergence%")
                    )
                    .order_by(Deploy.start.desc())
                    .first()
                )

                if not global_deploy:
                    return {"len": 0, "objectdeploy": []}

                group_uuid = global_deploy.group_uuid

                subq = (
                    session.query(
                        Deploy.jidmachine.label("jidmachine"),
                        func.max(Deploy.start).label("latest_start"),
                    )
                    .filter(
                        Deploy.command == command_id,
                        Deploy.group_uuid == group_uuid,
                        Deploy.title.like("%Convergence%"),
                    )
                    .group_by(Deploy.jidmachine)
                    .subquery()
                )

                query = (
                    session.query(Deploy)
                    .join(
                        subq,
                        and_(
                            Deploy.jidmachine == subq.c.jidmachine,
                            Deploy.start == subq.c.latest_start,
                        ),
                    )
                    .filter(
                        Deploy.command == command_id,
                        Deploy.group_uuid == group_uuid,
                        Deploy.title.like("%Convergence%"),
                    )
                )
            else:
                latest_start = (
                    session.query(func.max(Deploy.start))
                    .filter(
                        and_(Deploy.inventoryuuid == uuid,
                             Deploy.command == command_id)
                    )
                    .scalar()
                )

                if not latest_start:
                    return {"len": 0, "objectdeploy": []}

                query = session.query(Deploy).filter(
                    and_(
                        Deploy.inventoryuuid == uuid,
                        Deploy.command == command_id,
                        Deploy.start == latest_start,
                    )
                )
            relayserver = query.all()
            ret = {"len": len(relayserver), "objectdeploy": []}

            for t in relayserver:
                start_obj = {"timestamp": int(
                    t.start.timestamp())} if t.start else None

                obj = {
                    "pathpackage": t.pathpackage,
                    "jid_relay": t.jid_relay,
                    "inventoryuuid": t.inventoryuuid,
                    "jidmachine": t.jidmachine,
                    "state": t.state,
                    "sessionid": t.sessionid,
                    "start": start_obj,
                    "result": t.result if t.result else "",
                    "host": t.host,
                    "user": t.user,
                    "login": str(t.login),
                    "command": t.command,
                }
                ret["objectdeploy"].append(obj)
            return ret

        except Exception as e:
            logging.getLogger().error(f"ERROR : {str(e)}")
            return {"len": 0, "objectdeploy": []}

    @DatabaseHelper._sessionm
    def getlinelogssession(self, session, sessionnamexmpp):
        log_type = "deploy"
        if re.search("update", sessionnamexmpp) is not None:
            log_type = "update"
        log = (
            session.query(Logs)
            .filter(and_(Logs.sessionname == sessionnamexmpp, Logs.type == log_type))
            .order_by(Logs.id)
        )
        log = log.all()
        session.commit()
        session.flush()
        ret = {}
        ret["len"] = len(log)
        arraylist = []
        for t in log:
            obj = {}
            obj["type"] = t.type
            obj["date"] = t.date
            obj["text"] = t.text
            obj["sessionname"] = t.sessionname
            obj["priority"] = t.priority
            obj["who"] = t.who
            arraylist.append(obj)
        ret["log"] = arraylist
        return ret

    @DatabaseHelper._sessionm
    def addlogincommand(
        self,
        session,
        login,
        commandid,
        grpid,
        nb_machine_in_grp,
        instructions_nb_machine_for_exec,
        instructions_datetime_for_exec,
        parameterspackage,
        rebootrequired,
        shutdownrequired,
        bandwidth,
        syncthing,
        params,
    ):
        """
        Inserts a new login command into the database.If an order with the same ID already exists,
        Updates his file with the new values provided.

        Args:
            Session: Sqlalchemy session to interact with the database.
            Login (Str): The login username.
            Commandid (int): the order identifier.
            Grpid (Str): the group's identifier, if there is one.
            nb_machine_in_grp (Str): the number of machines in the group.
            instructions_nb_machine_for_exec (STR): Instructions for the number of machines to execute the command.
            instructions_datetime_for_exec (STR): Instructions for the time of execution of the order.
            ParametersPackage (STR): the deployment settings for the command.
            Reborootired (int): indicates if a restart is required (0 for False, 1 for True).
            ShutdownRequired (int): indicates if a stop is required (0 for False, 1 for True).
            Bandwidth (int): the bandwidth of the command.
            SYNCTHING (INT): Indicates if SYNCTHING is required (0 for FALSE, 1 for True).
            Params (List or Dict): additional control parameters.

        Returns:
            INT: The identifier of the inserted command or update in the database.
        """

        try:
            # Check if an entry with the same commandid already exists
            existing_logincommand = (
                session.query(Has_login_command).filter_by(
                    command=commandid).first()
            )

            if existing_logincommand:
                # Update existing values
                existing_logincommand.login = login
                existing_logincommand.count_deploy_progress = 0
                existing_logincommand.bandwidth = int(bandwidth)
                if grpid != "":
                    existing_logincommand.grpid = grpid
                if instructions_datetime_for_exec != "":
                    existing_logincommand.start_exec_on_time = (
                        instructions_datetime_for_exec
                    )
                if nb_machine_in_grp != "":
                    existing_logincommand.nb_machine_for_deploy = nb_machine_in_grp
                if instructions_nb_machine_for_exec != "":
                    existing_logincommand.start_exec_on_nb_deploy = (
                        instructions_nb_machine_for_exec
                    )
                if parameterspackage is False:
                    existing_logincommand.parameters_deploy = None
                elif parameterspackage != "":
                    existing_logincommand.parameters_deploy = parameterspackage
                existing_logincommand.rebootrequired = bool(rebootrequired)
                existing_logincommand.shutdownrequired = bool(shutdownrequired)
                existing_logincommand.syncthing = bool(syncthing)
                if isinstance(params, (list, dict)) and len(params) != 0:
                    existing_logincommand.params_json = json.dumps(params)
            else:
                # Create a new entry if a empty control field
                new_logincommand = Has_login_command(
                    login=login,
                    command=commandid,
                    count_deploy_progress=0,
                    bandwidth=int(bandwidth),
                    grpid=grpid if grpid != "" else None,
                    start_exec_on_time=(
                        instructions_datetime_for_exec
                        if instructions_datetime_for_exec != ""
                        else None
                    ),
                    nb_machine_for_deploy=(
                        nb_machine_in_grp if nb_machine_in_grp != "" else None
                    ),
                    start_exec_on_nb_deploy=(
                        instructions_nb_machine_for_exec
                        if instructions_nb_machine_for_exec != ""
                        else None
                    ),
                    parameters_deploy=(
                        parameterspackage if parameterspackage != "" else None
                    ),
                    rebootrequired=bool(rebootrequired),
                    shutdownrequired=bool(shutdownrequired),
                    syncthing=bool(syncthing),
                    params_json=(
                        json.dumps(params)
                        if isinstance(params, (list, dict)) and len(params) != 0
                        else None
                    ),
                )
                session.add(new_logincommand)

            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
        return (
            new_logincommand.id
            if existing_logincommand
            else new_logincommand.id if new_logincommand else None
        )

    @DatabaseHelper._sessionm
    def update_login_command(
        self,
        session,
        login,
        commandid,
        grpid,
        nb_machine_in_grp,
        instructions_nb_machine_for_exec,
        instructions_datetime_for_exec,
        parameterspackage,
        rebootrequired,
        shutdownrequired,
        bandwidth,
        syncthing,
        params,
    ):
        try:
            login_command = (
                session.query(Has_login_command).filter_by(
                    command=commandid).first()
            )
            if not login_command:
                logger.error(
                    f"Aucune commande trouvée pour command id {commandid}.")
                return None

            login_command.login = login
            login_command.count_deploy_progress = 0
            login_command.bandwidth = int(bandwidth)
            if grpid != "":
                login_command.grpid = grpid
            if instructions_datetime_for_exec != "":
                login_command.start_exec_on_time = instructions_datetime_for_exec
            if nb_machine_in_grp != "":
                login_command.nb_machine_for_deploy = nb_machine_in_grp
            if instructions_nb_machine_for_exec != "":
                login_command.start_exec_on_nb_deploy = instructions_nb_machine_for_exec
            if parameterspackage is False:
                login_command.parameters_deploy = None
            elif parameterspackage != "":
                login_command.parameters_deploy = parameterspackage

            login_command.rebootrequired = bool(rebootrequired)
            login_command.shutdownrequired = bool(shutdownrequired)
            login_command.syncthing = bool(syncthing)

            if isinstance(params, dict):
                if "do_reboot" in params:
                    login_command.do_reboot = params["do_reboot"]
                if "deployment_intervals" in params:
                    login_command.deployment_intervals = params["deployment_intervals"]

            if isinstance(params, (list, dict)) and len(params) != 0:
                login_command.params_json = json.dumps(params)

            session.commit()
            session.flush()
            return login_command.id
        except Exception as e:
            logger.error(f"Error when updating the login command: {e}")
            session.rollback()
            return None

    @DatabaseHelper._sessionm
    def getListPresenceRelay(self, session):
        sql = """SELECT
                    jid, agenttype, hostname
                FROM
                    xmppmaster.machines
                WHERE
                    `machines`.`enabled` = '1' and
                    `machines`.`agenttype` = 'relayserver'
                ORDER BY hostname;"""
        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = []
            for t in presencelist:
                a.append({"jid": t[0], "type": t[1], "hostname": t[2]})

            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def deploylog(self, session, nblastline):
        """return les machines en fonction du RS"""
        sql = (
            """SELECT
                    *
                FROM
                    xmppmaster.deploy
                ORDER BY id DESC
                LIMIT %s;"""
            % nblastline
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def updatemachine_kiosk_presence(self, session, idmachine, presence):
        """Modify the kiosk presence for the specified machines
        Params:
            session : sql session
            idmachine : int corresponding to the xmppmaster.machine.id
            presence : str representing the presence ("True" or "False")

        Returns:
            int : 1 value if success
            int : -1 value if failure
        """
        try:
            session.query(Machines).filter(Machines.id == idmachine).update(
                {Machines.kiosk_presence: presence}
            )
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updatedeploystate1(self, session, sessionid, state):
        try:
            if "DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)":
                sql = """UPDATE `xmppmaster`.`deploy`
                            SET
                                `state` = '%s'
                            WHERE
                                (deploy.sessionid = '%s'
                                    AND ( `state` NOT IN ('DEPLOYMENT SUCCESS' ,
                                                        'ABORT DEPLOYMENT CANCELLED BY USER',
                                                        "WOL 1",
                                                        "WOL 2",
                                                        "WOL 3",
                                                        "WAITING MACHINE ONLINE"
                                                        )
                                            OR
                                        `state` REGEXP '^(?!ERROR)^(?!SUCCESS)^(?!ABORT)'));
                        """ % (
                    state,
                    sessionid,
                )
            else:
                sql = """UPDATE `xmppmaster`.`deploy`
                        SET
                            `state` = '%s'
                        WHERE
                            (deploy.sessionid = '%s'
                                AND ( `state` NOT IN ('DEPLOYMENT SUCCESS' ,
                                                    'ABORT DEPLOYMENT CANCELLED BY USER')
                                        OR
                                    `state` REGEXP '^(?!ERROR)^(?!SUCCESS)^(?!ABORT)'));
                        """ % (
                    state,
                    sessionid,
                )
            result = session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updatemachineAD(self, session, idmachine, lastuser, ou_machine, ou_user):
        """
        update Machine table in base xmppmaster
        data AD
        """
        try:
            session.query(Machines).filter(
                and_(Machines.id == idmachine, Machines.enabled == "1")
            ).update(
                {
                    Machines.ad_ou_machine: ou_machine,
                    Machines.ad_ou_user: ou_user,
                    Machines.lastuser: lastuser,
                }
            )
            session.commit()
            session.flush()
            return 1
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def updatedeploystate(self, session, sessionid, state):
        """
        update status deploy
        """
        try:
            deploysession = (
                session.query(Deploy).filter(
                    Deploy.sessionid == sessionid).one()
            )
            if deploysession:
                # les status commençant par error, success, abort ne peuvent
                # plus être modifiés.
                regexpexlusion = re.compile(
                    "^(?!abort)^(?!success)^(?!error)", re.IGNORECASE
                )
                if regexpexlusion.match(state) is None:
                    return
                if state == "DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)":
                    if deploysession.state in [
                        "WOL 1",
                        "WOL 2",
                        "WOL 3",
                        "WAITING MACHINE ONLINE",
                    ]:
                        # STATUS NE CHANGE PAS
                        return 0
                # update status
                deploysession.state = state
                session.commit()
                session.flush()
                return 1
        except Exception:
            logger.error("sql : %s" % traceback.format_exc())
            return -1
        finally:
            session.close()

    @DatabaseHelper._sessionm
    def delNetwork_for_machines_id(self, session, machines_id):
        sql = (
            """DELETE FROM `xmppmaster`.`network`
                WHERE
                    (`machines_id` = '%s');"""
            % machines_id
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return result

    @DatabaseHelper._sessionm
    def addPresenceNetwork(
        self, session, macaddress, ipaddress, broadcast, gateway, mask, mac, id_machine
    ):
        # self.delNetwork_for_machines_id(id_machine)
        try:
            new_network = Network()
            new_network.macaddress = macaddress
            new_network.ipaddress = ipaddress
            new_network.broadcast = broadcast
            new_network.gateway = gateway
            new_network.mask = mask
            new_network.mac = mac
            new_network.machines_id = id_machine
            session.add(new_network)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
        # return new_network.toDict()

    @DatabaseHelper._sessionm
    def addServerRelay(
        self,
        session,
        urlguacamole,
        subnet,
        nameserver,
        groupdeploy,
        ipserver,
        ipconnection,
        portconnection,
        port,
        mask,
        jid,
        longitude="",
        latitude="",
        enabled=False,
        classutil="private",
        packageserverip="",
        packageserverport="",
        moderelayserver="static",
        keysyncthing="",
        syncthing_port=23000,
    ):
        sql = (
            "SELECT count(*) as nb FROM xmppmaster.relayserver where `relayserver`.`nameserver`='%s';"
            % nameserver
        )
        nb = session.execute(sql)
        session.commit()
        session.flush()
        result = [x for x in nb][0][0]
        if result == 0:
            try:
                new_relayserver = RelayServer()
                new_relayserver.urlguacamole = urlguacamole
                new_relayserver.subnet = subnet
                new_relayserver.nameserver = nameserver
                new_relayserver.groupdeploy = groupdeploy
                new_relayserver.ipserver = ipserver
                new_relayserver.port = port
                new_relayserver.mask = mask
                new_relayserver.jid = jid
                new_relayserver.ipconnection = ipconnection
                new_relayserver.portconnection = portconnection
                new_relayserver.longitude = longitude
                new_relayserver.latitude = latitude
                new_relayserver.enabled = enabled
                new_relayserver.classutil = classutil
                new_relayserver.package_server_ip = packageserverip
                new_relayserver.package_server_port = packageserverport
                new_relayserver.moderelayserver = moderelayserver
                new_relayserver.keysyncthing = keysyncthing
                new_relayserver.syncthing_port = syncthing_port
                session.add(new_relayserver)
                session.commit()
                session.flush()
            except Exception as e:
                logger.error(str(e))
        else:
            try:
                sql = (
                    "UPDATE `xmppmaster`.`relayserver`\
                        SET `enabled`=%s, `classutil`='%s'\
                      WHERE `xmppmaster`.`relayserver`.`nameserver`='%s';"
                    % (enabled, classutil, nameserver)
                )
                session.execute(sql)
                session.commit()
                session.flush()
            except Exception as e:
                logger.error(str(e))

    @DatabaseHelper._sessionm
    def getCountPresenceMachine(self, session):
        return (
            session.query(func.count(Machines.id))
            .filter(Machines.enabled == "1")
            .scalar()
        )

    @DatabaseHelper._sessionm
    def getIdUserforHostname(self, session, namesession, hostname):
        idresult = (
            session.query(Users.id)
            .filter(and_(Users.namesession == namesession, Users.hostname == hostname))
            .first()
        )
        session.commit()
        session.flush()
        return idresult

    @DatabaseHelper._sessionm
    def adduser(
        self,
        session,
        namesession,
        hostname,
        city="",
        region_name="",
        time_zone="",
        longitude="",
        latitude="",
        postal_code="",
        country_code="",
        country_name="",
        creation_user="",
        last_modif="",
    ):
        city = city.decode("iso-8859-1").encode("utf8")
        region_name = region_name.decode("iso-8859-1").encode("utf8")
        time_zone = time_zone.decode("iso-8859-1").encode("utf8")
        postal_code = postal_code.decode("iso-8859-1").encode("utf8")
        country_code = country_code.decode("iso-8859-1").encode("utf8")
        country_name = country_name.decode("iso-8859-1").encode("utf8")
        createuser = datetime.now()
        id = self.getIdUserforHostname(namesession, hostname)
        if id is None:
            try:
                new_user = Users()
                new_user.namesession = namesession
                new_user.hostname = hostname
                new_user.city = city
                new_user.region_name = region_name
                new_user.time_zone = time_zone
                new_user.longitude = longitude
                new_user.latitude = latitude
                new_user.postal_code = postal_code
                new_user.country_code = country_code
                new_user.country_name = country_name
                new_user.creation_user = createuser
                new_user.last_modif = createuser
                session.add(new_user)
                session.commit()
                session.flush()
                return new_user.id
            except Exception as e:
                logger.error(str(e))
                return -1
        else:
            try:
                session.query(Users).filter(
                    and_(Users.namesession == namesession,
                         Users.hostname == hostname)
                ).update(
                    {
                        Users.city: city,
                        Users.region_name: region_name,
                        Users.time_zone: time_zone,
                        Users.longitude: longitude,
                        Users.latitude: latitude,
                        Users.postal_code: postal_code,
                        Users.country_code: country_code,
                        Users.country_name: country_name,
                        Users.last_modif: createuser,
                    }
                )
                session.commit()
                session.flush()
                return id
            except Exception as e:
                logger.error(str(e))
        return -1

    def get_count(self, q):
        count_q = q.statement.with_only_columns([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

    def get_count1(self, q):
        return q.with_entities(func.count()).scalar()

    @DatabaseHelper._sessionm
    def getdeploybyuserlen(self, session, login=None, typedeploy="command"):
        deploybyuserlen = session.query(Deploy).filter(
            Deploy.sessionid.like("%s%%" % (typedeploy))
        )
        if login is not None:
            return self.get_count(deploybyuserlen.filter(Deploy.login == login))
        else:
            return self.get_count(deploybyuserlen)

    @DatabaseHelper._sessionm
    def syncthingmachineless(self, session, grp, cmd):
        mach = session.query(
            Syncthing_machine.jidmachine,
            Syncthing_machine.progress,
            Syncthing_machine.startcmd,
            Syncthing_machine.endcmd,
            Syncthing_machine.cluster,
        ).filter(
            and_(Syncthing_machine.group_uuid == grp,
                 Syncthing_machine.command == cmd)
        )
        result = mach.all()
        session.commit()
        session.flush()
        ret = {"data": []}

        for linemach in result:
            listchamp = []
            try:
                machime = linemach.jidmachine.split("/")[1]
            except BaseException:
                machime = linemach.jidmachine
            try:
                cluster = json.loads(linemach.cluster)
                ars = [x.split("@")[0] for x in cluster["listarscluster"]]
                # clusterlist = ",".join(cluster["listarscluster"])
                clusterlist = ",".join(ars)
                nbclustermachine = str(cluster["numcluster"])
            except BaseException:
                clusterlist = ""
                nbclustermachine = ""
            listchamp.append(clusterlist)
            listchamp.append(nbclustermachine)
            listchamp.append(machime)
            if linemach.progress is None:
                progress = "000%"
            else:
                progress = "%03d%%" % linemach.progress
            listchamp.append(progress)
            listchamp.append(str(linemach.startcmd))
            listchamp.append(str(linemach.endcmd))
            ret["data"].append(listchamp)
        return ret

    @DatabaseHelper._sessionm
    def getLogxmpp(
        self,
        session,
        start_date,
        end_date,
        typelog,
        action,
        module,
        user,
        how,
        who,
        why,
        headercolumn,
    ):
        # labelheader = [x.strip() for x in headercolumn.split("|") if x.strip() != "" and x is not "None"]
        logs = session.query(Logs)
        if headercolumn == "":
            headercolumn = "date@fromuser@who@text"

        if start_date != "":
            logs = logs.filter(Logs.date > start_date)
        if end_date != "":
            logs = logs.filter(Logs.date < end_date)
        if not (typelog == "None" or typelog == ""):
            logs = logs.filter(Logs.type == typelog)
        if not (action == "None" or action == ""):
            logs = logs.filter(Logs.action == action)
        if not (module == "None" or module == ""):
            # plusieurs criteres peuvent se trouver dans ce parametre.
            criterformodule = [
                x.strip() for x in module.split("|") if x.strip() != "" and x != "None"
            ]
            for x in criterformodule:
                stringsearchinmodule = "%" + x + "%"
                logs = logs.filter(Logs.module.like(stringsearchinmodule))
        if not (user == "None" or user == ""):
            logs = logs.filter(func.lower(
                Logs.fromuser).like(func.lower(user)))
        if not (how == "None" or how == ""):
            logs = logs.filter(Logs.how == how)
        if not (who == "None" or who == ""):
            logs = logs.filter(Logs.who == who)
        if not (why == "None" or why == ""):
            logs = logs.filter(Logs.why == why)
        logs = logs.order_by(desc(Logs.id)).limit(1000)
        result = logs.all()
        session.commit()
        session.flush()
        ret = {"data": []}
        index = 0
        for linelogs in result:
            listchamp = []
            # listchamp.append(index)
            if headercolumn != "" and "date" in headercolumn:
                listchamp.append(str(linelogs.date))
            if headercolumn != "" and "fromuser" in headercolumn:
                listchamp.append(linelogs.fromuser)
            if headercolumn != "" and "type" in headercolumn:
                listchamp.append(linelogs.type)
            if headercolumn != "" and "action" in headercolumn:
                listchamp.append(linelogs.action)
            if headercolumn != "" and "module" in headercolumn:
                listchamp.append(linelogs.module)
            if headercolumn != "" and "how" in headercolumn:
                listchamp.append(linelogs.how)
            if headercolumn != "" and "who" in headercolumn:
                listchamp.append(linelogs.who)
            if headercolumn != "" and "why" in headercolumn:
                listchamp.append(linelogs.why)
            if headercolumn != "" and "priority" in headercolumn:
                listchamp.append(linelogs.priority)
            if headercolumn != "" and "touser" in headercolumn:
                listchamp.append(linelogs.touser)
            if headercolumn != "" and "sessionname" in headercolumn:
                listchamp.append(linelogs.sessionname)
            if headercolumn != "" and "text" in headercolumn:
                listchamp.append(linelogs.text)

            # listchamp.append(linelogs.type)
            # listchamp.append(linelogs.action)
            # listchamp.append(linelogs.module)
            # listchamp.append(linelogs.how)
            # listchamp.append(linelogs.who)
            # listchamp.append(linelogs.why)
            # listchamp.append(linelogs.priority)
            # listchamp.append(linelogs.touser)
            # listchamp.append(linelogs.sessionname)
            # listchamp.append(linelogs.text)
            ret["data"].append(listchamp)
            # index = index + 1
        return ret

    @DatabaseHelper._sessionm
    def get_deploy_from_group(
        self,
        session,
        group_uuid,
        state,
        intervalsearch,
        minimum,
        maximum,
        filt,
        typedeploy="command",
    ):
        """
        This function is used to retrieve the deploy of a machine's group.

        Args:
            session: The SQL Alchemy session
            group_uuid: The login of the user
            state: The state of the deploy. (Started, Error, etc. ).
            intervalsearch: The interval on which we search the deploys.
            minimum: Minimum value ( for pagination )
            maximum: Maximum value ( for pagination )
            filt: Filter of the search
        Returns:
            It returns all the deployement of a group.
        """
        deploylog = session.query(Deploy).filter(
            Deploy.sessionid.like("%s%%" % (typedeploy))
        )

        if group_uuid:
            deploylog = deploylog.filter(Deploy.group_uuid == group_uuid)
        if intervalsearch:
            deploylog = deploylog.filter(
                Deploy.start >= (datetime.now() -
                                 timedelta(seconds=intervalsearch))
            )
        if state:
            deploylog = deploylog.filter(Deploy.state == state)

        # TODO: Add filter support
        # if filt:
        # deploylog = deploylog.filter( or_(Deploy.state.like('%%%s%%'%(filt)),
        # Deploy.pathpackage.like('%%%s%%'%(filt)),
        # Deploy.start.like('%%%s%%'%(filt)),
        # Deploy.login.like('%%%s%%'%(filt)),
        # Deploy.host.like('%%%s%%'%(filt))))
        nb = self.get_count(deploylog)
        len_query = session.query(func.count(distinct(Deploy.title)))[0]
        # deploylog = deploylog.group_by(Deploy.title)
        deploylog = deploylog.order_by(desc(Deploy.id))

        nb = self.get_count(deploylog)
        if minimum and maximum:
            deploylog = deploylog.offset(int(minimum)).limit(
                int(maximim) - int(minimum)
            )

        result = deploylog.all()
        session.commit()
        session.flush()
        ret = {
            "lentotal": 0,
            "lenquery": 0,
            "tabdeploy": {
                "len": [],
                "state": [],
                "pathpackage": [],
                "sessionid": [],
                "inventoryuuid": [],
                "command": [],
                "start": [],
                "login": [],
                "host": [],
                "macadress": [],
                "group_uuid": [],
                "startcmd": [],
                "endcmd": [],
                "jidmachine": [],
                "jid_relay": [],
                "title": [],
            },
        }
        ret["lentotal"] = len_query[0]
        ret["lenquery"] = nb
        for linedeploy in result:
            # ret['tabdeploy']['len'].append(linedeploy[1])
            ret["tabdeploy"]["state"].append(linedeploy.state)
            ret["tabdeploy"]["pathpackage"].append(
                linedeploy.pathpackage.split("/")[-1]
            )
            ret["tabdeploy"]["sessionid"].append(linedeploy.sessionid)
            ret["tabdeploy"]["start"].append(str(linedeploy.start))
            ret["tabdeploy"]["inventoryuuid"].append(linedeploy.inventoryuuid)
            ret["tabdeploy"]["command"].append(linedeploy.command)
            ret["tabdeploy"]["login"].append(linedeploy.login)
            ret["tabdeploy"]["host"].append(linedeploy.host.split("@")[0][:-4])
            ret["tabdeploy"]["macadress"].append(linedeploy.macadress)
            if linedeploy.group_uuid is None:
                linedeploy.group_uuid = ""
            ret["tabdeploy"]["group_uuid"].append(linedeploy.group_uuid)
            ret["tabdeploy"]["startcmd"].append(linedeploy.startcmd)
            ret["tabdeploy"]["endcmd"].append(linedeploy.endcmd)
            ret["tabdeploy"]["jidmachine"].append(linedeploy.jidmachine)
            ret["tabdeploy"]["jid_relay"].append(linedeploy.jid_relay)
            ret["tabdeploy"]["title"].append(linedeploy.title)
        return ret

    @DatabaseHelper._sessionm
    def get_deploy_for_machine(
        self,
        session,
        uuidinventory,
        state,
        intervalsearch,
        minimum,
        maximum,
        filt,
        typedeploy="command",
    ):
        """
        This function is used to retrieve the deploy of a user.

        Args:
            session: The SQL Alchemy session
            uuidinventory: The login of the user
            state: The state of the deploy. (Started, Error, etc. ).
            intervalsearch: The interval on which we search the deploys.
            minimum: Minimum value ( for pagination )
            maximum: Maximum value ( for pagination )
            filt: Filter of the search
        Returns:
            It returns all the deployement for a machine.
        """

        deploylog = session.query(Deploy).filter(
            Deploy.sessionid.like("%s%%" % (typedeploy))
        )
        if uuidinventory:
            deploylog = deploylog.filter(Deploy.inventoryuuid == uuidinventory)
        if intervalsearch:
            deploylog = deploylog.filter(
                Deploy.start >= (datetime.now() -
                                 timedelta(seconds=intervalsearch))
            )
        if state:
            deploylog = deploylog.filter(Deploy.state == state)

        nb = self.get_count(deploylog)

        len_query = session.query(func.count(distinct(Deploy.title)))[0]
        deploylog = deploylog.order_by(desc(Deploy.id))

        nb = self.get_count(deploylog)
        if minium and maximum:
            deploylog = deploylog.offset(int(minimum)).limit(
                int(maximum) - int(minimum)
            )
        result = deploylog.all()
        session.commit()
        session.flush()
        ret = {
            "lentotal": 0,
            "lenquery": 0,
            "tabdeploy": {
                "len": [],
                "state": [],
                "pathpackage": [],
                "sessionid": [],
                "inventoryuuid": [],
                "command": [],
                "start": [],
                "login": [],
                "host": [],
                "macadress": [],
                "group_uuid": [],
                "startcmd": [],
                "endcmd": [],
                "jidmachine": [],
                "jid_relay": [],
                "title": [],
            },
        }
        ret["lentotal"] = len_query[0]
        ret["lenquery"] = nb
        for linedeploy in result:
            ret["tabdeploy"]["state"].append(linedeploy.state)
            ret["tabdeploy"]["pathpackage"].append(
                linedeploy.pathpackage.split("/")[-1]
            )
            ret["tabdeploy"]["sessionid"].append(linedeploy.sessionid)
            ret["tabdeploy"]["start"].append(str(linedeploy.start))
            ret["tabdeploy"]["inventoryuuid"].append(linedeploy.inventoryuuid)
            ret["tabdeploy"]["command"].append(linedeploy.command)
            ret["tabdeploy"]["login"].append(linedeploy.login)
            ret["tabdeploy"]["host"].append(linedeploy.host.split("/")[-1])
            ret["tabdeploy"]["macadress"].append(linedeploy.macadress)
            ret["tabdeploy"]["group_uuid"].append(linedeploy.group_uuid)
            ret["tabdeploy"]["startcmd"].append(linedeploy.startcmd)
            ret["tabdeploy"]["endcmd"].append(linedeploy.endcmd)
            ret["tabdeploy"]["jidmachine"].append(linedeploy.jidmachine)
            ret["tabdeploy"]["jid_relay"].append(linedeploy.jid_relay)
            ret["tabdeploy"]["title"].append(linedeploy.title)
        return ret

    @DatabaseHelper._sessionm
    def delDeploybygroup(self, session, numgrp):
        """
        creation d'une organization
        """
        session.query(Deploy).filter(Deploy.group_uuid == numgrp).delete()
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def get_teammembers_from_login(self, session, login):
        """
        This function is used to retrieve the id of the users of the 'login' team.
        Args:
            session: The SQL Alchemy session
            login: The login of a user of the group we are searching.
        Returns:
            It returns a list with all the logins belonging to the group of 'login'
        """
        if login is None or login == "":
            return []

        sql = (
            """ SELECT DISTINCT
                    xmppmaster.pulse_users.login
                FROM
                    xmppmaster.pulse_users
                        INNER JOIN
                    xmppmaster.pulse_team_user ON
                        xmppmaster.pulse_team_user.id_user = xmppmaster.pulse_users.id
                WHERE
                    xmppmaster.pulse_team_user.id_team
                        IN (SELECT
                                xmppmaster.pulse_team_user.id_team
                            FROM
                                xmppmaster.pulse_users
                                    INNER JOIN
                                xmppmaster.pulse_team_user ON
                                    xmppmaster.pulse_team_user.id_user = xmppmaster.pulse_users.id
                            WHERE
                                '%s' REGEXP xmppmaster.pulse_users.login);"""
            % login
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        if result:
            return [x[0] for x in result]
        else:
            return []

    @DatabaseHelper._sessionm
    def get_team_patterns_from_login(self, session, login):
        if login is None or login == "":
            return []

        sql = text("""
            SELECT DISTINCT xmppmaster.pulse_users.login
            FROM xmppmaster.pulse_users
            INNER JOIN xmppmaster.pulse_team_user
            ON xmppmaster.pulse_team_user.id_user = xmppmaster.pulse_users.id
            WHERE :login REGEXP xmppmaster.pulse_users.login
        """)
        result = session.execute(sql, {"login": login})
        patterns = [row[0] for row in result]

        return patterns

    @DatabaseHelper._sessionm
    def get_deploy_by_team_member(
        self,
        session,
        login,
        state,
        intervalsearch,
        minimum=None,
        maximum=None,
        filt=None,
        typedeploy="command",
    ):
        """
        This function is used to retrieve the deployements of a team.
        This team is found based on the login of a member.

        Args:
            session: The SQL Alchemy session
            login: The login of the user
            state: State of the deployment (Started, Error, etc.)
            intervalsearch: The interval on which we search the deploys.
            minimum: Minimum value ( for pagination )
            maximum: Maximum value ( for pagination )
            filt: Filter of the search
        Returns:
            It returns all the deployement done by a specific team.
            It can be done by time search too.
        """
        pulse_usersid = self.get_teammembers_from_login(login)
        deploylog = session.query(Deploy).filter(
            Deploy.sessionid.like("%s%%" % typedeploy)
        )
        deploylog = deploylog.filter(and_(~Deploy.title.like("%Convergence%"), ~Deploy.title.like("%-@system@-%")) )

        if not pulse_usersid or len(pulse_usersid) == 1 and pulse_usersid[0] == "root":
            return self.get_deploy_by_user_with_interval(
                login,
                state,
                intervalsearch,
                minimum=None,
                maximum=None,
                filt=None,
                typedeploy=typedeploy,
            )

        preposition_comparaisons = [
            Deploy.login.op("regexp")(field) for field in pulse_usersid
        ]
        deploylog = deploylog.filter(or_(*preposition_comparaisons))

        preposition_comparaisons_count = [
            "login REGEXP '%s' " % field for field in pulse_usersid
        ]
        preposition_sql_string = ""
        if preposition_comparaisons_count:
            preposition_sql_string = (
                "and ("
                + " or ".join(["%s" %
                              x for x in preposition_comparaisons_count])
                + ")"
            )

        if state:
            deploylog = deploylog.filter(Deploy.state == state)

        if intervalsearch:
            deploylog = deploylog.filter(
                Deploy.start >= (datetime.now() -
                                 timedelta(seconds=intervalsearch))
            )

        if filt:
            deploylog = deploylog.filter(
                or_(
                    Deploy.state.like("%%%s%%" % filt),
                    Deploy.pathpackage.like("%%%s%%" % filt),
                    Deploy.start.like("%%%s%%" % filt),
                    Deploy.login.like("%%%s%%" % filt),
                    Deploy.host.like("%%%s%%" % filt),
                )
            )
            count = """select count(*) as nb from (
                            select count(id) as nb
                            from deploy
                            where
                                sessionid like "%s%%" AND
                                start >= DATE_SUB(NOW(),INTERVAL 24 HOUR)
                                %s
                                AND (state LIKE "%%%s%%"
                                or pathpackage LIKE "%%%s%%"
                                or start LIKE "%%%s%%"
                                or login LIKE "%%%s%%"
                                or host LIKE "%%%s%%"
                                )
                            group by title
                            ) as x;""" % (
                typedeploy,
                preposition_sql_string,
                filt,
                filt,
                filt,
                filt,
                filt,
            )
        else:
            # nb deploiement different
            count = """select count(*) as nb from (
                            select count(id) as nb
                            from deploy
                            where
                                sessionid like "%s%%" AND
                                start >= DATE_SUB(NOW(),INTERVAL 24 HOUR)
                            %s
                            group by title
                            ) as x;""" % (
                typedeploy,
                preposition_sql_string,
            )

        len_query = self.get_count(deploylog)

        result = session.execute(count)
        session.commit()
        session.flush()
        lenrequest = [x for x in result]

        deploylog = deploylog.group_by(Deploy.title).order_by(desc(Deploy.id))

        if minimum is not None and maximum is not None:
            deploylog = deploylog.offset(int(minimum)).limit(
                int(maximum) - int(minimum)
            )

        result = deploylog.all()
        session.commit()
        session.flush()
        ret = {
            "total_of_rows": 0,
            "lentotal": 0,
            "tabdeploy": {
                "state": [],
                "pathpackage": [],
                "sessionid": [],
                "start": [],
                "inventoryuuid": [],
                "command": [],
                "login": [],
                "host": [],
                "macadress": [],
                "group_uuid": [],
                "startcmd": [],
                "endcmd": [],
                "jidmachine": [],
                "jid_relay": [],
                "title": [],
            },
        }

        ret["lentotal"] = len_query
        ret["total_of_rows"] = lenrequest[0][0]
        reg = "(.*)\\.(.*)@(.*)\\/(.*)"

        for linedeploy in result:
            if re.match(reg, linedeploy.host):
                # New jid : name.salt@relay/macaddress
                hostname = linedeploy.host.split(".")[0]
            else:
                try:
                    # Old jid : macaddress@relay/name
                    hostname = linedeploy.host.split("/")[1]
                except Exception as e:
                    hostname = linedeploy.host.split(".")[0]

            ret["tabdeploy"]["state"].append(linedeploy.state)
            ret["tabdeploy"]["pathpackage"].append(
                linedeploy.pathpackage.split("/")[-1]
            )
            ret["tabdeploy"]["sessionid"].append(linedeploy.sessionid)
            ret["tabdeploy"]["start"].append(str(linedeploy.start))
            ret["tabdeploy"]["inventoryuuid"].append(linedeploy.inventoryuuid)
            ret["tabdeploy"]["command"].append(linedeploy.command)
            ret["tabdeploy"]["login"].append(linedeploy.login)
            ret["tabdeploy"]["host"].append(hostname)
            ret["tabdeploy"]["macadress"].append(linedeploy.macadress)
            ret["tabdeploy"]["group_uuid"].append(linedeploy.group_uuid)
            ret["tabdeploy"]["startcmd"].append(linedeploy.startcmd)
            ret["tabdeploy"]["endcmd"].append(linedeploy.endcmd)
            ret["tabdeploy"]["jidmachine"].append(linedeploy.jidmachine)
            ret["tabdeploy"]["jid_relay"].append(linedeploy.jid_relay)
            ret["tabdeploy"]["title"].append(linedeploy.title)
        return ret

    @DatabaseHelper._sessionm
    def get_convergence_deploys_by_user_with_interval(
        self,
        session,
        login,
        state,
        intervalsearch,
        minimum=None,
        maximum=None,
        filt=None,
        typedeploy="command",
    ):
        """
        Retrieve recent deployments for a user, filtering only those with "Convergence" in the title.
        Returns aggregated structure similar to get_deploy_convergence.

        Args:
            session: SQLAlchemy session.
            login: User login.
            state: Deployment state.
            intervalsearch: Search interval in seconds.
            minimum: Pagination start index.
            maximum: Pagination end index.
            filt: Additional filter.

        Returns:
            Dictionary with aggregated deployment details (one row per convergence).
        """
        query_base = session.query(Deploy).filter(
            and_(
                Deploy.sessionid.like(f"{typedeploy}%"),
                Deploy.title.like("%Convergence%"),
            )
        )

        if login:
            query_base = query_base.filter(Deploy.login == login)

        if intervalsearch:
            since_date = datetime.now() - timedelta(seconds=intervalsearch)
            query_base = query_base.filter(Deploy.start >= since_date)

        if state:
            query_base = query_base.filter(Deploy.state == state)

        if filt:
            like = f"%{filt}%"
            query_base = query_base.filter(
                or_(
                    Deploy.state.like(like),
                    Deploy.pathpackage.like(like),
                    Deploy.start.like(like),
                    Deploy.login.like(like),
                    Deploy.host.like(like),
                )
            )

        # Aggregate by command and group_uuid to get one row per convergence
        global_subq = (
            query_base.with_entities(
                Deploy.command,
                Deploy.group_uuid,
                func.max(Deploy.start).label("global_latest_start"),
            )
            .group_by(Deploy.command, Deploy.group_uuid)
            .subquery()
        )

        global_deploy_query = session.query(Deploy).join(
            global_subq,
            and_(
                Deploy.command == global_subq.c.command,
                Deploy.group_uuid == global_subq.c.group_uuid,
                Deploy.start == global_subq.c.global_latest_start,
            ),
        )

        global_deploy_raw = global_deploy_query.all()
        unique_global = {}
        for row in global_deploy_raw:
            key = (row.command, row.group_uuid)
            if key not in unique_global or row.start > unique_global[key].start:
                unique_global[key] = row
        global_deploy_list = list(unique_global.values())

        aggregated_list = []
        for global_deploy in global_deploy_list:
            machine_query = query_base.filter(
                Deploy.command == global_deploy.command,
                Deploy.group_uuid == global_deploy.group_uuid,
            )

            machine_subq = (
                machine_query.with_entities(
                    Deploy.inventoryuuid,
                    func.max(Deploy.start).label("machine_latest_start"),
                )
                .group_by(Deploy.inventoryuuid)
                .subquery()
            )

            deploy_per_machine_query = (
                session.query(
                    Deploy.command,
                    Deploy.group_uuid,
                    Deploy.login,
                    Deploy.host,
                    Deploy.inventoryuuid,
                    Deploy.state,
                    Deploy.jid_relay,
                    Deploy.sessionid,
                    Deploy.start,
                    Deploy.endcmd,
                )
                .join(
                    machine_subq,
                    and_(
                        Deploy.inventoryuuid == machine_subq.c.inventoryuuid,
                        Deploy.start == machine_subq.c.machine_latest_start,
                    ),
                )
                .order_by(Deploy.start.desc())
            )
            machine_results = deploy_per_machine_query.all()
            total_machine_count = len(machine_results)

            machine_details_list = []
            for row in machine_results:
                machine_details_list.append(
                    {
                        "host": row.host,
                        "state": row.state,
                        "inventoryuuid": row.inventoryuuid,
                        "jid_relay": row.jid_relay,
                        "sessionid": row.sessionid,
                        "start": (
                            row.start.strftime("%Y-%m-%d %H:%M:%S")
                            if row.start
                            else None
                        ),
                        "end": (
                            row.endcmd.strftime("%Y-%m-%d %H:%M:%S")
                            if row.endcmd
                            else None
                        ),
                    }
                )

            aggregated = {
                "command": global_deploy.command,
                "group_uuid": global_deploy.group_uuid,
                "title": global_deploy.title,
                "nb_machines": total_machine_count,
                "start": (
                    {"timestamp": int(global_deploy.start.timestamp())}
                    if global_deploy.start
                    else None
                ),
                "endcmd": (
                    {"timestamp": int(global_deploy.endcmd.timestamp())}
                    if global_deploy.endcmd
                    else None
                ),
                "machine_details_json": json.dumps(machine_details_list),
                "login": global_deploy.login,
            }
            aggregated_list.append(aggregated)

        # Sort by start date (most recent first)
        aggregated_list.sort(key=lambda x: x["start"]["timestamp"] if x["start"] else 0, reverse=True)

        if minimum is not None and maximum is not None:
            aggregated_list = aggregated_list[int(minimum): int(maximum)]
        lentotal = len(aggregated_list)

        ret = {
            "lentotal": lentotal,
            "tabdeploy": {
                "command": [a["command"] for a in aggregated_list],
                "group_uuid": [a["group_uuid"] for a in aggregated_list],
                "title": [a["title"] for a in aggregated_list],
                "nb_machines": [a["nb_machines"] for a in aggregated_list],
                "start": [a["start"] for a in aggregated_list],
                "endcmd": [a["endcmd"] for a in aggregated_list],
                "machine_details_json": [
                    a["machine_details_json"] for a in aggregated_list
                ],
                "login": [a["login"] for a in aggregated_list],
            },
        }

        session.commit()
        session.flush()
        return ret

    @DatabaseHelper._sessionm
    def get_deploy_by_team_member_for_convergence(
        self,
        session,
        login,
        state,
        intervalsearch,
        minimum=None,
        maximum=None,
        filt=None,
        typedeploy="command",
    ):
        """
        Recovers and aggregates the deployments of a team for convergence,
        In order to return only the last deployment (by order) for research.

        Args:
        Session: SQLALCHEMY session.
        Login: user login (used to find team members).
        State: state of deployment.
        Intervalsearch: Second interval for research.
        Minimum: starting index for pagination.
        Maximum: end index for pagination.
        Filt: Filter on various fields.
        Typedeploy: type of deployment (by default "command").

        Returns:
            dict: {
                "lentotal": Total number of convergences
                "tabdeploy": {
                    "command": [...],
                    "group_uuid": [...],
                    "title": [...],
                    "nb_machines": [...],
                    "start": [...],
                    "endcmd": [...],
                    "machine_details_json": [...],
                    "login": [...],
                }
            }
        """
        pulse_usersid = self.get_teammembers_from_login(login)
        if not pulse_usersid or (
            len(pulse_usersid) == 1 and pulse_usersid[0] == "root"
        ):
            return self.get_convergence_deploys_by_user_with_interval(
                login,
                state,
                intervalsearch,
                minimum=None,
                maximum=None,
                filt=None,
                typedeploy=typedeploy,
            )

        query_base = session.query(Deploy).filter(
            Deploy.sessionid.like(
                f"{typedeploy}%"), Deploy.title.like("%Convergence%")
        )
        if intervalsearch:
            since_date = datetime.now() - timedelta(seconds=intervalsearch)
            query_base = query_base.filter(Deploy.start >= since_date)
        if filt:
            query_base = query_base.filter(
                or_(
                    Deploy.state.like(f"%{filt}%"),
                    Deploy.pathpackage.like(f"%{filt}%"),
                    Deploy.start.like(f"%{filt}%"),
                    Deploy.login.like(f"%{filt}%"),
                    Deploy.host.like(f"%{filt}%"),
                )
            )

        team_filter = or_(*[Deploy.login.op("regexp")(uid)
                          for uid in pulse_usersid])
        query_base = query_base.filter(team_filter)

        if state:
            query_base = query_base.filter(Deploy.state == state)

        global_subq = (
            query_base.with_entities(
                Deploy.command,
                Deploy.group_uuid,
                func.max(Deploy.start).label("global_latest_start"),
            )
            .group_by(Deploy.command, Deploy.group_uuid)
            .subquery()
        )

        global_deploy_query = session.query(Deploy).join(
            global_subq,
            and_(
                Deploy.command == global_subq.c.command,
                Deploy.group_uuid == global_subq.c.group_uuid,
                Deploy.start == global_subq.c.global_latest_start,
            ),
        )
        global_deploy_raw = global_deploy_query.all()
        unique_global = {}
        for row in global_deploy_raw:
            key = (row.command, row.group_uuid)
            if key not in unique_global or row.start > unique_global[key].start:
                unique_global[key] = row
        global_deploy_list = list(unique_global.values())

        aggregated_list = []
        for global_deploy in global_deploy_list:
            machine_query = query_base.filter(
                Deploy.command == global_deploy.command,
                Deploy.group_uuid == global_deploy.group_uuid,
            )
            machine_subq = (
                machine_query.with_entities(
                    Deploy.inventoryuuid,
                    func.max(Deploy.start).label("machine_latest_start"),
                )
                .group_by(Deploy.inventoryuuid)
                .subquery()
            )

            deploy_per_machine_query = (
                session.query(
                    Deploy.command,
                    Deploy.group_uuid,
                    Deploy.login,
                    Deploy.host,
                    Deploy.inventoryuuid,
                    Deploy.state,
                    Deploy.jid_relay,
                    Deploy.sessionid,
                    Deploy.start,
                    Deploy.endcmd,
                )
                .join(
                    machine_subq,
                    and_(
                        Deploy.inventoryuuid == machine_subq.c.inventoryuuid,
                        Deploy.start == machine_subq.c.machine_latest_start,
                    ),
                )
                .order_by(Deploy.start.desc())
            )
            machine_results = deploy_per_machine_query.all()
            total_machine_count = len(machine_results)

            machine_details_list = []
            for row in machine_results:
                machine_details_list.append(
                    {
                        "host": row.host,
                        "state": row.state,
                        "inventoryuuid": row.inventoryuuid,
                        "jid_relay": row.jid_relay,
                        "sessionid": row.sessionid,
                        "start": (
                            row.start.strftime("%Y-%m-%d %H:%M:%S")
                            if row.start
                            else None
                        ),
                        "end": (
                            row.endcmd.strftime("%Y-%m-%d %H:%M:%S")
                            if row.endcmd
                            else None
                        ),
                    }
                )

            aggregated = {
                "command": global_deploy.command,
                "group_uuid": global_deploy.group_uuid,
                "title": global_deploy.title,
                "nb_machines": total_machine_count,
                "start": (
                    {"timestamp": int(global_deploy.start.timestamp())}
                    if global_deploy.start
                    else None
                ),
                "endcmd": (
                    {"timestamp": int(global_deploy.endcmd.timestamp())}
                    if global_deploy.endcmd
                    else None
                ),
                "machine_details_json": json.dumps(machine_details_list),
                "login": global_deploy.login,
            }
            aggregated_list.append(aggregated)

        # Sort by start date (most recent first)
        aggregated_list.sort(key=lambda x: x["start"]["timestamp"] if x["start"] else 0, reverse=True)

        if minimum is not None and maximum is not None:
            aggregated_list = aggregated_list[int(minimum): int(maximum)]
        lentotal = len(aggregated_list)

        ret = {
            "lentotal": lentotal,
            "tabdeploy": {
                "command": [a["command"] for a in aggregated_list],
                "group_uuid": [a["group_uuid"] for a in aggregated_list],
                "title": [a["title"] for a in aggregated_list],
                "nb_machines": [a["nb_machines"] for a in aggregated_list],
                "start": [a["start"] for a in aggregated_list],
                "endcmd": [a["endcmd"] for a in aggregated_list],
                "machine_details_json": [
                    a["machine_details_json"] for a in aggregated_list
                ],
                "login": [a["login"] for a in aggregated_list],
            },
        }

        session.commit()
        session.flush()
        return ret

    @DatabaseHelper._sessionm
    def get_deploy_by_user_with_interval(
        self,
        session,
        login,
        state,
        intervalsearch,
        minimum=None,
        maximum=None,
        filt=None,
        typedeploy="command",
    ):
        """
        This function is used to retrive the recent deployment done by a user.

        Args:
            session: The SQL Alchemy session
            login: The login of the user
            intervalsearch: The interval on which we search the deploys.
            minimum: Minimum value ( for pagination )
            maximum: Maximum value ( for pagination )
            filt: Filter of the search

        Returns:
            It returns all the deployment done by a user.
            If intervalsearch is not used it is by default in the last 24 hours.
        """
        try:
            window_sec = 24 * 3600 if intervalsearch is None else int(intervalsearch)
        except Exception:
            window_sec = 24 * 3600

        # Filtres communs
        filters = [
            ~Deploy.title.like("%Convergence%"),
            ~Deploy.title.like("%-@system@-%"),
            Deploy.sessionid.like(f"{typedeploy}%"),
        ]
        if window_sec > 0:
            filters.append(
                Deploy.start >= func.date_sub(func.now(), text(f"INTERVAL {window_sec} SECOND"))
            )
        if login:
            filters.append(Deploy.login == login)
        if state:
            filters.append(Deploy.state == state)
        if filt:
            like = f"%{filt}%"
            filters.append(
                or_(
                    Deploy.state.like(like),
                    Deploy.pathpackage.like(like),
                    func.date_format(Deploy.start, "%Y-%m-%d %H:%i:%s").like(like),
                    Deploy.login.like(like),
                    Deploy.host.like(like),
                )
            )

        # Clé de groupe sans cast / sans case :
        #   - si group_uuid est NULL ou "", on prend CONCAT('ID:', id) (type string)
        #   - sinon on prend group_uuid (déjà string)
        group_key = func.coalesce(
            func.nullif(Deploy.group_uuid, ""),
            func.concat("ID:", Deploy.id),
        )

        # Sous-requête: id le plus récent par (command, group_key)
        subq = (
            session.query(func.max(Deploy.id).label("max_id"))
            .filter(*filters)
            .group_by(Deploy.command, group_key)
            .subquery()
        )

        # total_rows = nombre de groupes (ou unitaires)
        total_rows = session.query(func.count()).select_from(subq).scalar()

        # Récupération des lignes représentatives
        q = (
            session.query(Deploy)
            .join(subq, Deploy.id == subq.c.max_id)
            .order_by(desc(Deploy.id))
        )

        # Pagination
        if minimum is not None and maximum is not None:
            off = int(minimum)
            lim = max(0, int(maximum) - off)
            q = q.offset(off).limit(lim)

        rows = q.all()

        # Construction du retour (identique)
        ret = {
            "total_of_rows": total_rows,
            "lentotal": total_rows,
            "tabdeploy": {
                "state": [],
                "pathpackage": [],
                "sessionid": [],
                "start": [],
                "inventoryuuid": [],
                "command": [],
                "login": [],
                "host": [],
                "macadress": [],
                "group_uuid": [],
                "startcmd": [],
                "endcmd": [],
                "jidmachine": [],
                "jid_relay": [],
                "title": [],
            },
        }

        reg = r"(.*)\.(.*)@(.*)\/(.*)"
        for d in rows:
            raw_host = d.host or ""
            if re.match(reg, raw_host):
                hostname = raw_host.split(".")[0]
            else:
                try:
                    hostname = raw_host.split("/")[1]
                except Exception:
                    hostname = raw_host.split(".")[0] if "." in raw_host else raw_host

            ret["tabdeploy"]["state"].append(d.state)
            ret["tabdeploy"]["pathpackage"].append((d.pathpackage or "").split("/")[-1])
            ret["tabdeploy"]["sessionid"].append(d.sessionid)
            ret["tabdeploy"]["start"].append(str(d.start))
            ret["tabdeploy"]["inventoryuuid"].append(d.inventoryuuid)
            ret["tabdeploy"]["command"].append(d.command)
            ret["tabdeploy"]["login"].append(d.login)
            ret["tabdeploy"]["host"].append(hostname)
            ret["tabdeploy"]["macadress"].append(d.macadress)
            ret["tabdeploy"]["group_uuid"].append(d.group_uuid)
            ret["tabdeploy"]["startcmd"].append(d.startcmd)
            ret["tabdeploy"]["endcmd"].append(d.endcmd)
            ret["tabdeploy"]["jidmachine"].append(d.jidmachine)
            ret["tabdeploy"]["jid_relay"].append(d.jid_relay)
            ret["tabdeploy"]["title"].append(d.title)

        return ret

    @DatabaseHelper._sessionm
    def get_deploy_convergence(
        self,
        session,
        login,
        intervalsearch,
        minimum=None,
        maximum=None,
        filt=None,
        typedeploy="command",
    ):
        query_base = session.query(Deploy).filter(
            and_(
                Deploy.sessionid.like(f"{typedeploy}%"),
                Deploy.title.like("%Convergence%"),
            )
        )

        if login:
            query_base = query_base.filter(Deploy.login.like(login))
        if intervalsearch:
            since_date = datetime.now() - timedelta(seconds=intervalsearch)
            query_base = query_base.filter(Deploy.start >= since_date)
        if filt:
            like = f"%{filt}%"
            query_base = query_base.filter(
                or_(
                    Deploy.state.like(like),
                    Deploy.pathpackage.like(like),
                    Deploy.start.like(like),
                    Deploy.login.like(like),
                    Deploy.host.like(like),
                )
            )

        global_subq = (
            query_base.with_entities(
                Deploy.command,
                Deploy.group_uuid,
                func.max(Deploy.start).label("global_latest_start"),
            )
            .group_by(Deploy.command, Deploy.group_uuid)
            .subquery()
        )

        global_deploy_query = session.query(Deploy).join(
            global_subq,
            and_(
                Deploy.command == global_subq.c.command,
                Deploy.group_uuid == global_subq.c.group_uuid,
                Deploy.start == global_subq.c.global_latest_start,
            ),
        )

        inv_rows = session.execute(
            text(
                "SELECT uuid_inventorymachine "
                "FROM xmppmaster.machines "
                "WHERE uuid_inventorymachine IS NOT NULL AND uuid_inventorymachine <> ''"
            )
        ).fetchall()
        inventory_uuids = {r[0] for r in inv_rows}

        global_deploy_raw = global_deploy_query.all()
        unique_global = {}
        for row in global_deploy_raw:
            key = (row.command, row.group_uuid)
            if key not in unique_global or row.start > unique_global[key].start:
                unique_global[key] = row
        global_deploy_list = list(unique_global.values())

        aggregated_list = []
        for global_deploy in global_deploy_list:
            machine_query = query_base.filter(
                Deploy.command == global_deploy.command,
                Deploy.group_uuid == global_deploy.group_uuid,
            )

            machine_subq = (
                machine_query.with_entities(
                    Deploy.inventoryuuid,
                    func.max(Deploy.start).label("machine_latest_start"),
                )
                .group_by(Deploy.inventoryuuid)
                .subquery()
            )

            deploy_per_machine_query = (
                session.query(
                    Deploy.command,
                    Deploy.group_uuid,
                    Deploy.login,
                    Deploy.host,
                    Deploy.inventoryuuid,
                    Deploy.state,
                    Deploy.jid_relay,
                    Deploy.sessionid,
                    Deploy.start,
                    Deploy.endcmd,
                )
                .join(
                    machine_subq,
                    and_(
                        Deploy.inventoryuuid == machine_subq.c.inventoryuuid,
                        Deploy.start == machine_subq.c.machine_latest_start,
                    ),
                )
                .order_by(Deploy.start.desc())
            )
            machine_results = deploy_per_machine_query.all()

            filtered_results = [
                row for row in machine_results
                if row.inventoryuuid and row.inventoryuuid in inventory_uuids
            ]
            total_machine_count = len(filtered_results)

            machine_details_list = []
            for row in filtered_results:
                machine_details_list.append(
                    {
                        "host": row.host,
                        "state": row.state,
                        "inventoryuuid": row.inventoryuuid,
                        "jid_relay": row.jid_relay,
                        "sessionid": row.sessionid,
                        "start": row.start.strftime("%Y-%m-%d %H:%M:%S") if row.start else None,
                        "end": row.endcmd.strftime("%Y-%m-%d %H:%M:%S") if row.endcmd else None,
                    }
                )

            aggregated = {
                "command": global_deploy.command,
                "group_uuid": global_deploy.group_uuid,
                "title": global_deploy.title,
                "nb_machines": total_machine_count,  # ✅ corrigé
                "start": (
                    {"timestamp": int(global_deploy.start.timestamp())}
                    if global_deploy.start else None
                ),
                "endcmd": (
                    {"timestamp": int(global_deploy.endcmd.timestamp())}
                    if global_deploy.endcmd else None
                ),
                "machine_details_json": json.dumps(machine_details_list),
                "login": global_deploy.login,
            }
            aggregated_list.append(aggregated)

        # Sort by start date (most recent first)
        aggregated_list.sort(key=lambda x: x["start"]["timestamp"] if x["start"] else 0, reverse=True)

        if minimum is not None and maximum is not None:
            aggregated_list = aggregated_list[int(minimum): int(maximum)]
        lentotal = len(aggregated_list)

        ret = {
            "lentotal": lentotal,
            "tabdeploy": {
                "command": [a["command"] for a in aggregated_list],
                "group_uuid": [a["group_uuid"] for a in aggregated_list],
                "title": [a["title"] for a in aggregated_list],
                "nb_machines": [a["nb_machines"] for a in aggregated_list],
                "start": [a["start"] for a in aggregated_list],
                "endcmd": [a["endcmd"] for a in aggregated_list],
                "machine_details_json": [a["machine_details_json"] for a in aggregated_list],
                "login": [a["login"] for a in aggregated_list],
            },
        }

        session.commit()
        session.flush()
        return ret

    @DatabaseHelper._sessionm
    def get_deploy_by_user_finished(
        self,
        session,
        login,
        intervalsearch,
        minimum=None,
        maximum=None,
        filt=None,
        typedeploy="command",
    ):
        """
        This function is used to retrieve all the deployments done by a user (or a team).

        Args:
            session: The SQL Alchemy session
            login: The login of the user
            intervalsearch: The interval on which we search the deploys (in seconds).
                            If None, defaults to the last 3 months.
            minimum: Minimum value (for pagination offset)
            maximum: Maximum value (for pagination end)
            filt: Filter of the search (applied with LIKE)
            typedeploy: Prefix filter on sessionid (default: "command")

        Returns:
            There are 3 scenarios:
                If login is empty, returns all past deploys for everyone
                If login is a string, returns all past deploys for this user
                If login is a list, returns all past deploys for the group this user belongs to.
        """

        try:
            window_sec = 90 * 24 * 3600 if intervalsearch is None else int(intervalsearch)
        except Exception:
            window_sec = 90 * 24 * 3600

        # Filtres communs
        filters = [
            ~Deploy.title.like("%Convergence%"),
            ~Deploy.title.like("%-@system@-%"),
            Deploy.sessionid.like(f"{typedeploy}%"),
            or_(
                Deploy.state == "DEPLOYMENT SUCCESS",
                Deploy.state.like("ERROR%"),
                Deploy.state.like("ABORT%"),
            ),
            Deploy.endcmd.isnot(None),
        ]

        if window_sec > 0:
            filters.append(
                Deploy.endcmd >= func.date_sub(func.now(), text(f"INTERVAL {window_sec} SECOND"))
            )

        if login:
            if isinstance(login, list):
                filters.append(Deploy.login.in_(login))
            else:
                filters.append(Deploy.login == login)

        if filt:
            like = f"%{filt}%"
            filters.append(
                or_(
                    Deploy.state.like(like),
                    Deploy.pathpackage.like(like),
                    func.date_format(Deploy.start, "%Y-%m-%d %H:%i:%s").like(like),
                    Deploy.login.like(like),
                    Deploy.host.like(like),
                )
            )

        # Clé de groupe sans cast / sans case :
        #   - si group_uuid est NULL ou "", on prend CONCAT('ID:', id) (type string)
        #   - sinon on prend group_uuid (déjà string)
        group_key = func.coalesce(
            func.nullif(Deploy.group_uuid, ""),
            func.concat("ID:", Deploy.id),
        )

        # Sous-requête: id le plus récent par (command, group_key)
        subq = (
            session.query(func.max(Deploy.id).label("max_id"))
            .filter(*filters)
            .group_by(Deploy.command, group_key)
            .subquery()
        )

        # total_rows = nombre de groupes (ou unitaires)
        total_rows = session.query(func.count()).select_from(subq).scalar()

        # Récupération des lignes représentatives
        q = (
            session.query(Deploy)
            .join(subq, Deploy.id == subq.c.max_id)
            .order_by(desc(Deploy.id))
        )

        # Pagination
        if minimum is not None and maximum is not None:
            off = int(minimum)
            lim = max(0, int(maximum) - off)
            q = q.offset(off).limit(lim)

        rows = q.all()

        ret = {
            "lentotal": total_rows,
            "tabdeploy": {
                "len": [],
                "state": [],
                "pathpackage": [],
                "sessionid": [],
                "start": [],
                "inventoryuuid": [],
                "command": [],
                "login": [],
                "host": [],
                "macadress": [],
                "group_uuid": [],
                "startcmd": [],
                "endcmd": [],
                "jidmachine": [],
                "jid_relay": [],
                "title": [],
            },
        }

        reg = r"(.*)\.(.*)@(.*)\/(.*)"
        for d in rows:
            raw_host = d.host or ""
            if re.match(reg, raw_host):
                hostname = raw_host.split(".")[0]
            else:
                try:
                    hostname = raw_host.split("/")[1]
                except Exception:
                    hostname = raw_host.split(".")[0] if "." in raw_host else raw_host

            ret["tabdeploy"]["state"].append(d.state)
            ret["tabdeploy"]["pathpackage"].append((d.pathpackage or "").split("/")[-1])
            ret["tabdeploy"]["sessionid"].append(d.sessionid)
            ret["tabdeploy"]["start"].append(str(d.start))
            ret["tabdeploy"]["inventoryuuid"].append(d.inventoryuuid)
            ret["tabdeploy"]["command"].append(d.command)
            ret["tabdeploy"]["login"].append(d.login)
            ret["tabdeploy"]["host"].append(hostname)
            ret["tabdeploy"]["macadress"].append(d.macadress)
            ret["tabdeploy"]["group_uuid"].append(d.group_uuid)
            ret["tabdeploy"]["startcmd"].append(d.startcmd)
            ret["tabdeploy"]["endcmd"].append(d.endcmd)
            ret["tabdeploy"]["jidmachine"].append(d.jidmachine)
            ret["tabdeploy"]["jid_relay"].append(d.jid_relay)
            ret["tabdeploy"]["title"].append(d.title)

        return ret


    @DatabaseHelper._sessionm
    def getdeploybyuser(
        self, session, login=None, numrow=None, offset=None, typedeploy="command"
    ):
        deploylog = session.query(Deploy).filter(
            Deploy.sessionid.like("%s%%" % (typedeploy))
        )
        if login is not None:
            deploylog = deploylog.filter(Deploy.login == login).order_by(
                desc(Deploy.id)
            )
        else:
            deploylog = deploylog.order_by(desc(Deploy.id))
        if numrow is not None:
            deploylog = deploylog.limit(numrow)
            if offset is not None:
                deploylog = deploylog.offset(offset)
        deploylog = deploylog.all()
        session.commit()
        session.flush()
        ret = {
            "len": len(deploylog),
            "tabdeploy": {
                "state": [],
                "pathpackage": [],
                "sessionid": [],
                "inventoryuuid": [],
                "command": [],
                "start": [],
                "login": [],
                "host": [],
            },
        }
        for linedeploy in deploylog:
            ret["tabdeploy"]["state"].append(linedeploy.state)
            ret["tabdeploy"]["pathpackage"].append(
                linedeploy.pathpackage.split("/")[-1]
            )
            ret["tabdeploy"]["sessionid"].append(linedeploy.sessionid)
            ret["tabdeploy"]["inventoryuuid"].append(linedeploy.inventoryuuid)
            ret["tabdeploy"]["command"].append(linedeploy.command)
            starttime_formated = str(
                linedeploy.start.strftime("%Y-%m-%d %H:%M"))
            ret["tabdeploy"]["start"].append(starttime_formated)
            ret["tabdeploy"]["login"].append(linedeploy.login)
            ret["tabdeploy"]["host"].append(linedeploy.host.split("/")[-1])
        return ret

    @DatabaseHelper._sessionm
    def showmachinegrouprelayserver(self, session):
        """return les machines en fonction du RS"""
        sql = """SELECT
                `jid`,
                `agenttype`,
                `platform`,
                `groupdeploy`,
                `hostname`,
                `uuid_inventorymachine`,
                `ip_xmpp`,
                `subnetxmpp`
            FROM
                xmppmaster.machines
            WHERE
                machines.enabled = '1'
            order BY `groupdeploy` ASC, `agenttype` DESC;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def get_qaction(self, session, namecmd, user, grp, completename):
        """
        return quick actions informations
        """
        if grp == 0:
            qa_custom_command = session.query(Qa_custom_command).filter(
                and_(
                    Qa_custom_command.namecmd == namecmd, Qa_custom_command.user == user
                )
            )
            qa_custom_command = qa_custom_command.first()
        else:
            osdetection = ""
            if completename != "":
                if completename.endswith("(windows)"):
                    osdetection = "windows"
                elif completename.endswith("(macos)"):
                    osdetection = "macos"
                elif completename.endswith("(linux)"):
                    osdetection = "linux"
            if osdetection == "":
                qa_custom_command = session.query(Qa_custom_command).filter(
                    and_(
                        Qa_custom_command.customcmd == namecmd,
                        or_(
                            Qa_custom_command.user == user,
                            Qa_custom_command.user == "allusers",
                        ),
                    )
                )
            else:
                qa_custom_command = session.query(Qa_custom_command).filter(
                    and_(
                        Qa_custom_command.customcmd == namecmd,
                        Qa_custom_command.os == osdetection,
                        or_(
                            Qa_custom_command.user == user,
                            Qa_custom_command.user == "allusers",
                        ),
                    )
                )
            qa_custom_command = qa_custom_command.first()
        if qa_custom_command:
            result = {
                "user": qa_custom_command.user,
                "os": qa_custom_command.os,
                "namecmd": qa_custom_command.namecmd,
                "customcmd": qa_custom_command.customcmd,
                "description": qa_custom_command.description,
            }
            return result
        else:
            result = {}

    @DatabaseHelper._sessionm
    def listjidRSdeploy(self, session):
        """return les RS pour le deploiement"""
        sql = """SELECT
                    groupdeploy
                FROM
                    xmppmaster.machines
                WHERE
                    machines.enabled = '1' and
                    machines.agenttype = 'relayserver';"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def listmachinesfromRSdeploy(self, session, groupdeploy):
        """return les machine suivie par un RS"""
        sql = (
            """SELECT
                    *
                FROM
                    xmppmaster.machines
                WHERE
                    machines.enabled = '1' and
                    machines.agenttype = 'machine'
                        AND machines.groupdeploy = '%s';"""
            % groupdeploy
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def listmachinesfromdeploy(self, session, groupdeploy):
        """return toutes les machines pour un deploy"""
        sql = (
            """SELECT
                        *
                    FROM
                        xmppmaster.machines
                    WHERE
                    machines.enabled = '1' and
                    machines.groupdeploy = '%s'
                    order BY  `agenttype` DESC;"""
            % groupdeploy
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def ipfromjid(self, session, jid, enable=1):
        """return ip xmpp for JID"""
        user = str(jid).split("@")[0]
        if enable is None:
            sql = (
                """SELECT
                        ip_xmpp
                    FROM
                        xmppmaster.machines
                    WHERE
                        jid LIKE ('%s%%')
                                    LIMIT 1;"""
                % user
            )
        else:
            sql = """SELECT
                        ip_xmpp
                    FROM
                        xmppmaster.machines
                    WHERE
                        enabled = '%s' and
                        jid LIKE ('%s%%')
                                    LIMIT 1;""" % (
                enable,
                user,
            )

        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def groupdeployfromjid(self, session, jid):
        """return groupdeploy xmpp for JID"""
        user = str(jid).split("@")[0]
        sql = (
            """SELECT
                    groupdeploy
                FROM
                    xmppmaster.machines
                WHERE
                    enabled = '1' and
                    jid LIKE ('%s%%')
                                LIMIT 1;"""
            % user
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def ippackageserver(self, session, jid):
        """return ip xmpp for JID"""
        user = str(jid).split("@")[0]
        sql = (
            """SELECT
                    package_server_ip
                FROM
                    xmppmaster.relayserver
                WHERE
                    jid LIKE ('%s@%%')
                                LIMIT 1;"""
            % user
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def portpackageserver(self, session, jid):
        """return ip xmpp for JID"""
        user = str(jid).split("@")[0]
        sql = (
            """SELECT
                    package_server_port
                FROM
                    xmppmaster.relayserver
                WHERE
                    jid LIKE ('%s%%')
                                LIMIT 1;"""
            % user
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def ipserverARS(self, session, jid):
        """return ip xmpp for JID"""
        user = str(jid).split("@")[0]
        sql = (
            """SELECT
                    ipserver
                FROM
                    xmppmaster.relayserver
                WHERE
                    jid LIKE ('%s%%')
                                LIMIT 1;"""
            % user
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def getUuidFromJid(self, session, jid):
        """
        This function return the UUID based on the jid

        Args:
            session:    The sqlalchemy session
            jid:        The jid of the machine we want to determine the UUID

        Returns:
            It returns the UUID based on the jid, False otherwise
        """
        uuid_inventorymachine = (
            session.query(Machines).filter_by(
                jid=jid).first().uuid_inventorymachine
        )
        if uuid_inventorymachine:
            return uuid_inventorymachine.strip("UUID")

        return False

    @DatabaseHelper._sessionm
    def algoruleadorganisedbyusers(
        self, session, userou, classutilMachine="both", rule=8, enabled=1
    ):
        """
        Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 8 by organization users
        Field "subject" is used to define the organisation by user OU eg Computers/HeadQuarter/Locations
        Field "relayserver_id" is used to define the Relayserver associe a ce name user
        enabled = 1 Only on active relayserver.
        If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """

        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (
                rule,
                userou,
                enabled,
                classutilMachine,
            )
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (
                rule,
                userou,
                enabled,
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algoruleadorganisedbymachines(
        self, session, machineou, classutilMachine="both", rule=7, enabled=1
    ):
        """
        This is used to assign an ARS to a machine based on the machine's OU of the AD.
        Args:
            session: The SQL Alchemy session
            machineou: The OU where the machine is located.
            classutilMachine: Type of ARS ( can be private, public, both )
            rule: the number of the rule to proceed
            enabled: Tell if the relayserver is enabled or not.
                     1 means the relayserver is enabled, 0 otherwise

        Returns:
            It returns the ID of the relay server matching this SQL Request.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (
                rule,
                machineou,
                enabled,
                classutilMachine,
            )
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (
                rule,
                machineou,
                enabled,
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algoruleuser(
        self, session, username, classutilMachine="both", rule=1, enabled=1
    ):
        """
        Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 1 for user name
        Field "subject" is used to define the name of the user in this rule
        Field "relayserver_id" is used to define the Relayserver associe a ce name user
        enabled = 1 Only on active relayserver.
        If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
            limit 1;""" % (
                rule,
                username,
                enabled,
                classutilMachine,
            )
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
            limit 1;""" % (
                rule,
                username,
                enabled,
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulehostname(
        self, session, hostname, classutilMachine="both", rule=2, enabled=1
    ):
        """
        Field "rule_id" : This information allows you to apply the search
                          only to the rule designated. rule_id = 2 for hostname
        Field "subject" is used to define the hostname in this rule
        enabled = 1 Only on active relayserver.
        If classutilMachine is private then the choice of relayserver will be
          in the relayservers reserved for machines where [global].agent_space
          configuration is set to private.
        # hostname regex
            #hostname matches subject of has_relayserverrules table
            #-- subject is the regex.
            #-- eg : ^machine_win_.*1$
            #-- eg : ^machine_win_.*[2-9]{1,3}$
            Tip: For cheching the regex using Mysql use
                select "hostname_for_test" REGEXP "^hostname.*";  => result  1
                select "hostname_for_test" REGEXP "^(?!hostname).*"; => result 0
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id` , `has_relayserverrules`.`subject`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            order by `has_relayserverrules`.`order`
            limit 1;""" % (
                rule,
                hostname,
                enabled,
                classutilMachine,
            )
        else:
            sql = """select `relayserver`.`id` , `has_relayserverrules`.`subject`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            order by `has_relayserverrules`.`order`
            limit 1;""" % (
                rule,
                hostname,
                enabled,
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        ret = [y for y in result]
        if ret:
            logger.debug(
                "Matched hostname rule with "
                'hostname "%s\\# by regex \\#%s"' % (hostname, ret[0].subject)
            )
        return ret

    @DatabaseHelper._sessionm
    def algoruleloadbalancer(self, session):
        sql = """
            SELECT
                COUNT(*) AS nb, `machines`.`groupdeploy`, `relayserver`.`id`
            FROM
                xmppmaster.machines
                    INNER JOIN
                xmppmaster.`relayserver` ON `relayserver`.`groupdeploy` = `machines`.`groupdeploy`
            WHERE
                enabled = '1' and
                agenttype = 'machine'
                AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            GROUP BY `machines`.`groupdeploy`
            ORDER BY nb DESC
            LIMIT 1;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulesubnet(
        self, session, subnetmachine, classutilMachine="both", enabled=1
    ):
        """
        To associate relay server that is on same networks...
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
            where
                        `relayserver`.`enabled` = %d
                    AND `relayserver`.`subnet` ='%s'
                    AND `relayserver`.`classutil` = '%s'
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (
                enabled,
                subnetmachine,
                classutilMachine,
            )
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
            where
                        `relayserver`.`enabled` = %d
                    AND `relayserver`.`subnet` ='%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (
                enabled,
                subnetmachine,
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulebynetmaskaddress(
        self, session, netmaskaddress, classutilMachine="both", rule=10, enabled=1
    ):
        """
        Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 10 by network mask
        Field "netmaskaddress" is used to define the net mask address for association
        Field "relayserver_id" is used to define the Relayserver to be assigned to the machines matching that rule
        enabled = 1 Only on active relayserver.
        If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (
                rule,
                netmaskaddress,
                enabled,
                classutilMachine,
            )
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND `has_relayserverrules`.`subject` = '%s'
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            limit 1;""" % (
                rule,
                netmaskaddress,
                enabled,
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def algorulebynetworkaddress(
        self, session, subnetmachine, classutilMachine="both", rule=9, enabled=1
    ):
        """
        Field "rule_id" : This information allows you to apply the search only to the rule pointed. rule_id = 9 by network address
        Field "subject" is used to define the subnet for association
        Field "relayserver_id" is used to define the Relayserver to be assigned to the machines matching that rule
        enabled = 1 Only on active relayserver.
        If classutilMachine is deprived then the choice of relayserver will be in the relayserver reserve to a use of the private machine.
        subnetmachine CIDR machine.
            CIDR matching with subject of table has_relayserverrules
            -- subject is the expresseion relationel.
            -- eg : ^55\\.171\\.[5-6]{1}\\.[0-9]{1,3}/24$
            -- eg : ^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}/24$ all adress mask 255.255.255.255
        """
        if classutilMachine == "private":
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND `relayserver`.`classutil` = '%s'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            order by `has_relayserverrules`.`order`
            limit 1;""" % (
                rule,
                subnetmachine,
                enabled,
                classutilMachine,
            )
        else:
            sql = """select `relayserver`.`id`
            from `relayserver`
                inner join
                    `has_relayserverrules` ON  `relayserver`.`id` = `has_relayserverrules`.`relayserver_id`
            where
                `has_relayserverrules`.`rules_id` = %d
                    AND '%s' REGEXP `has_relayserverrules`.`subject`
                    AND `relayserver`.`enabled` = %d
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`)
            order by `has_relayserverrules`.`order`
            limit 1;""" % (
                rule,
                subnetmachine,
                enabled,
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def IpAndPortConnectionFromServerRelay(self, session, id):
        """return ip et port server relay for connection"""
        sql = (
            """SELECT
                    ipconnection, port, jid, urlguacamole
                 FROM
                    xmppmaster.relayserver
                 WHERE
                    id = %s;"""
            % id
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return list([x for x in result][0])

    @DatabaseHelper._sessionm
    def jidrelayserverforip(self, session, ip):
        """return jid server relay for connection"""
        sql = (
            """SELECT
                    ipconnection, port, jid, urlguacamole
                FROM
                    xmppmaster.relayserver
                WHERE
                    ipconnection = '%s';"""
            % ip
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = list([x for x in result][0])
            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def IdlonglatServerRelay(self, session, classutilMachine="both", enabled=1):
        """return long and lat server relay"""
        if classutilMachine == "private":
            sql = """SELECT
                        id, longitude, latitude
                    FROM
                        xmppmaster.relayserver
                    WHERE
                            `relayserver`.`enabled` = %d
                        AND `relayserver`.`classutil` = '%s'
                    AND `relayserver`.`moderelayserver` = 'static'
                    AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`);""" % (
                enabled,
                classutilMachine,
            )
        else:
            sql = """SELECT
                        id,longitude,latitude
                    FROM
                        xmppmaster.relayserver
                    WHERE
                            `relayserver`.`enabled` = %d
                            AND (`relayserver`.`switchonoff` OR `relayserver`.`mandatory`);""" % (
                enabled
            )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    # @DatabaseHelper._sessionm
    # def algoruledefault(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
    # pass

    # @DatabaseHelper._sessionm
    # def algorulegeo(self, session, subnetmachine, classutilMachine = "private",  enabled=1):
    # pass

    @DatabaseHelper._sessionm
    def Orderrules(self, session):
        sql = """SELECT
                    *
                FROM
                    xmppmaster.rules
                ORDER BY level;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def hasmachineusers(self, session, machines_id, users_id):
        result = (
            session.query(Has_machinesusers.machines_id)
            .filter(
                and_(
                    Has_machinesusers.machines_id == machines_id,
                    Has_machinesusers.users_id == users_id,
                )
            )
            .first()
        )
        session.commit()
        session.flush()
        if result is None:
            new_machineuser = Has_relayserverrules()
            new_machineuser.machines_id = machines_id
            new_machineuser.users_id = users_id
            session.commit()
            session.flush()
            return True
        return False

    @DatabaseHelper._sessionm
    def addguacamoleidformachineid(self, session, machine_id, idguacamole):
        try:
            hasguacamole = Has_guacamole()
            hasguacamole.idguacamole = idguacamole
            hasguacamole.machine_id = machine_id
            session.add(hasguacamole)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))

    @DatabaseHelper._sessionm
    def addlistguacamoleidformachineid(self, session, machine_id, connection):
        # objet connection: {u'VNC': 60, u'RDP': 58, u'SSH': 59}}
        if not connection:
            # on ajoute 1 protocole inexistant pour signaler que guacamle est
            # configure.
            connection["INF"] = 0

        sql = (
            """DELETE FROM `xmppmaster`.`has_guacamole`
                    WHERE
                        `xmppmaster`.`has_guacamole`.`machine_id` = '%s';"""
            % machine_id
        )
        session.execute(sql)
        session.commit()
        session.flush()

        for idguacamole in connection:
            try:
                hasguacamole = Has_guacamole()
                hasguacamole.idguacamole = connection[idguacamole]
                hasguacamole.machine_id = machine_id
                hasguacamole.protocol = idguacamole
                session.add(hasguacamole)
                session.commit()
                session.flush()
            except Exception as e:
                # logger.error("addPresenceNetwork : %s " % new_network)
                logger.error(str(e))

    @DatabaseHelper._sessionm
    def listserverrelay(self, session, moderelayserver="static"):
        sql = (
            """SELECT
                    jid
                FROM
                    xmppmaster.relayserver
                WHERE
                    `xmppmaster`.`relayserver`.`moderelayserver` = '%s'
                    ;"""
            % moderelayserver
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def column_list_table(self, session, tablename, basename="xmppmaster"):
        """
        This function returns the list of column titles in the table,
        where the name of this table is passed as a parameter.
        """
        try:
            sql = """SELECT
                        column_name
                    FROM
                        information_schema.columns WHERE table_name = '%s'
                        AND
                        table_schema='%s';""" % (
                tablename,
                basename,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return [x[0] for x in result]
        except Exception as e:
            logger.error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def random_list_ars_relay_one_only_in_cluster(
        self, session, sessiontype_return="dict"
    ):
        """
        this function search 1 list ars.
        1 only ars by cluster.
        the ars of cluster is randomly selected

        return object is 1 list organize per row found.
            following the sessiontype_return parameter:
                - sessiontype_return is "dict"
                    the rows are expressed in the form of dictionary (column name, value column)
                - sessiontype_return is "list"
                    the rows are expressed as a list of values.
        """
        sql = """SELECT
                    *
                FROM
                    xmppmaster.relayserver
                WHERE
                    `xmppmaster`.`relayserver`.`id` IN (
                        SELECT
                            id
                        FROM
                            (SELECT
                                id
                            FROM
                                (SELECT
                                    xmppmaster.relayserver.id AS id,
                                    xmppmaster.has_cluster_ars.id_cluster AS cluster
                                FROM
                                    xmppmaster.relayserver
                                INNER JOIN xmppmaster.has_cluster_ars
                                        ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                                ORDER BY RAND()) selectrandonlistars
                            GROUP BY cluster) selectcluster);"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        a = []
        if result:
            if sessiontype_return == "dict":
                columnlist = self.column_list_table("relayserver")
                for ligneresult in [x for x in result]:
                    obj = {}
                    for index, value in enumerate(columnlist):
                        obj[value] = ligneresult[index]
                    a.append(obj)
                return a
            else:
                return [x[0] for x in result]
        else:
            return []

    @DatabaseHelper._sessionm
    def listmachines(self, session, enable="1"):
        sql = (
            """SELECT
                    jid
                FROM
                    xmppmaster.machines
                WHERE
                    xmppmaster.machines.enabled = '%s' and
                    xmppmaster.machines.agenttype="machine";"""
            % enable
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def clearMachine(self, session):
        session.execute("TRUNCATE TABLE xmppmaster.machines;")
        session.execute("TRUNCATE TABLE xmppmaster.network;")
        session.execute("TRUNCATE TABLE xmppmaster.has_machinesusers;")
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def listMacAdressforMachine(self, session, id_machine, infomac=False):
        try:
            sql = """SELECT
                        GROUP_CONCAT(DISTINCT mac ORDER BY mac ASC  SEPARATOR ',') AS listmac
                    FROM
                        xmppmaster.network
                    WHERE
                        machines_id = '%s';""" % (
                id_machine
            )
            if infomac:
                logger.debug(
                    "SQL request to get the mac addresses list "
                    "for the presence machine #%s" % id_machine
                )
            listMacAdress = session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
        result = [x for x in listMacAdress][0]
        if infomac:
            logger.debug("Result list MacAdress for Machine : %s" % result[0])
        return result

    @DatabaseHelper._sessionm
    def getjidMachinefromuuid(self, session, uuid):
        try:
            sql = (
                """SELECT
                        jid
                    FROM
                        xmppmaster.machines
                    WHERE
                        enabled = '1' and
                        uuid_inventorymachine = '%s'
                        LIMIT 1;"""
                % uuid
            )
            jidmachine = session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
            return ""
        try:
            result = [x for x in jidmachine][0]
        except BaseException:
            return ""
        return result[0]

    @DatabaseHelper._sessionm
    def updateMachineidinventory(self, session, id_machineinventory, idmachine):
        updatedb = -1
        try:
            sql = """UPDATE `machines`
                    SET
                        `uuid_inventorymachine` = '%s'
                    WHERE
                        `id` = '%s';""" % (
                id_machineinventory,
                idmachine,
            )
            updatedb = session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
        return updatedb

    def datetimetotimestamp(self, date):
        return int(time.mktime(date.timetuple()))

    def query_to_array_of_dict(
        self,
        ret,
        timestmp=False,
        list_colonne_name=True,
        bycolumn=True,
        nbelement=True,
        listexclude=[],
    ):
        """convert sql objet to list of dict"""
        result = []
        if ret is not None:
            countelt = ret.rowcount
            columns_name = list(ret.keys())
            columns_name = [x for x in columns_name if x not in listexclude]
            if not bycolumn:
                for row in ret:
                    if row is not None:
                        dictresult = {}
                        drow = row._asdict()
                        for key, value in list(drow.items()):
                            if key in listexclude:
                                continue
                            logger.warning("value type %s" % type(value))
                            if value is None:
                                dictresult[key] = ""
                            elif isinstance(value, datetime):
                                dictresult[key] = value.strftime(
                                    "%Y-%m-%d %H:%M:%S")
                                if timestmp:
                                    dictresult["%s_stmp" % key] = (
                                        self.datetimetotimestamp(value)
                                    )
                            else:
                                dictresult[key] = value
                        logger.warning("value type %s" % type(value))
                        result.append(dictresult)
            else:  # by column
                # create list by name.
                # initialisation structure result
                if ret:
                    result = {"data": {index: [] for index in columns_name}}
                    if nbelement:
                        result["count"] = countelt
                    if list_colonne_name:
                        result["data"]["columns_name"] = columns_name
                    for row in ret:
                        if row is not None:
                            drow = row._asdict()
                            for key, value in list(drow.items()):
                                if key in listexclude:
                                    continue
                                if value is None:
                                    result["data"][key].append("")
                                elif isinstance(value, datetime):
                                    result["data"][key].append(
                                        value.strftime("%Y-%m-%d %H:%M:%S")
                                    )
                                    # if timestmp:
                                    # dictresult["%s_stmp"%key] = self.datetimetotimestamp(value)
                                else:
                                    result["data"][key].append(value)
        else:
            result = [{}]
        return result

    @DatabaseHelper._sessionm
    def get_machines_list(self, session, start, end, ctx):
        def _likecriterium(field, filter):
            return " AND %s like '%%%s%%'" % (field, filter)

        # fiel for table mach
        machinefield = [
            "id",
            "jid",
            "uuid_serial_machine",
            "enabled",
            "platform",
            "archi",
            "hostname",
            "uuid_inventorymachine",
            "ippublic",
            "ip_xmpp",
            "macaddress",
            "subnetxmpp",
            "agenttype",
            "classutil",
            "groupdeploy",
            "ad_ou_machine",
            "ad_ou_user",
            "glpi_description",
            "lastuser",
            "glpi_owner_firstname",
            "glpi_owner_realname",
            "glpi_owner",
            "glpi_entity_id",
            "glpi_location_id",
            "model",
            "manufacturer",
            "need_reconf",
            "kiosk_presence",
        ]
        # fiel for table ent and alias
        entityfield = {
            "entityname": "name",
            "entitypath": "complete_name",
            "entityid": "glpi_id",
        }
        # fiel for table location and alias
        locationfield = {
            "locationname": "name",
            "locationpath": "complete_name",
            "locationid": "glpi_id",
        }
        debugfunction = 0
        recherchefild = ""
        ctx["field"] = ctx["field"].strip()
        ctx["filter"] = ctx["filter"].strip()
        if "@@@DEBUG@@@" in ctx["filter"]:
            debugfunction = 1
            ctx["filter"] = ctx["filter"].replace("@@@DEBUG@@@", "").strip()

        if "field" in ctx and ctx["field"].strip() != "":
            if "filter" in ctx and ctx["filter"].strip() != "":
                if ctx["field"] == "allchamp":
                    tabelt = []
                    for indexchamp in machinefield:
                        elt = "mach.%s" % indexchamp
                        tabelt.append("COALESCE(%s, '')" % elt)
                    for indexchamp in entityfield:
                        elt = "ent.%s" % entityfield[indexchamp]
                        tabelt.append("COALESCE(%s, '')" % elt)
                    for indexchamp in locationfield:
                        elt = "loc.%s" % locationfield[indexchamp]
                        tabelt.append("COALESCE(%s, '')" % elt)
                    tabelt = ",'~',".join(tabelt)
                    # logger.warning("tabelt %s" % tabelt)
                    recherchefild = " AND ( concat(%s) like '%%%s%%')" % (
                        tabelt,
                        ctx["filter"],
                    )
                else:
                    # traitement des boolean posssible value
                    if ctx["field"] in ["need_reconf", "kiosk_presence"]:
                        reply = str(ctx["filter"]).lower().strip()
                        if reply[0] in ["y", "o", "t", "v", "1"]:
                            ctx["filter"] = "1"
                        elif reply[0] in ["n", "f", "0"]:
                            ctx["filter"] = "0"
                    if ctx["field"] in machinefield:
                        ctx["field"] = "mach.%s" % ctx["field"]
                    elif ctx["field"] in entityfield:
                        ctx["field"] = "ent.%s" % entityfield[ctx["field"]]
                    elif ctx["field"] in locationfield:
                        ctx["field"] = "loc.%s" % locationfield[ctx["field"]]
                    if ctx["filter"].lower().strip() == "null":
                        recherchefild = " AND %s IS NULL " % ctx["field"]
                    elif ctx["field"] in [
                        "mach.id",
                        "mach.glpi_entity_id",
                        "mach.glpi_location_id",
                        "ent.glpi_id",
                        "loc.glpi_id",
                    ]:
                        recherchefild = " AND %s = '%s'" % (
                            ctx["field"], ctx["filter"])
                    else:
                        recherchefild = _likecriterium(
                            ctx["field"], ctx["filter"])
        r = re.compile(r"reg_key_.*")
        regs = list(filter(r.search, self.config.summary))
        list_reg_columns_name = [
            getattr(self.config, regkey).split("|")[0].split("\\")[-1]
            for regkey in regs
        ]
        entity = " "
        if "location" in ctx and ctx["location"] != "":
            if ctx["location"].strip() == "-1":
                logger.warning("location is %s" % ctx["location"])
                pass
            else:
                entitylist = [
                    x.strip()
                    for x in str(ctx["location"]).replace("UUID", "").split(",")
                    if x != ""
                ]
                if entitylist:
                    entitystrlist = ",".join(entitylist)
                    entity = " AND ent.glpi_id in (%s) " % entitystrlist

        ordered = ""
        if self.config.ordered == 1:
            ordered = " order by mach.hostname "

        computerpresence = ""
        if "computerpresence" in ctx:
            if ctx["computerpresence"] == "presence":
                computerpresence = " AND enabled > 0 "
            elif ctx["computerpresence"] == "no_presence":
                computerpresence = " AND enabled = 0 "
        sql = """
                SELECT SQL_CALC_FOUND_ROWS
                    mach.id,
                    mach.jid,
                    mach.uuid_serial_machine,
                    mach.need_reconf,
                    mach.enabled,
                    mach.platform,archi,
                    mach.hostname,
                    mach.uuid_inventorymachine,
                    mach.ippublic,
                    mach.ip_xmpp,
                    mach.macaddress,
                    mach.subnetxmpp,
                    mach.agenttype,
                    mach.classutil,
                    mach.groupdeploy,
                    mach.ad_ou_machine,
                    mach.ad_ou_user,
                    mach.kiosk_presence,
                    mach.lastuser,
                    mach.glpi_description,
                    mach.glpi_owner_firstname,
                    mach.glpi_owner_realname,
                    mach.glpi_owner,
                    mach.glpi_entity_id,
                    mach.glpi_location_id,
                    mach.model,
                    mach.manufacturer,
                    GROUP_CONCAT(DISTINCT CONCAT(reg.name, '|', reg.value)
                        SEPARATOR '@@@') AS regedit,
                    loc.name AS locationname,
                    loc.complete_name AS locationpath,
                    loc.glpi_id AS locationid,
                    ent.name AS entityname,
                    ent.complete_name AS entitypath,
                    ent.glpi_id AS entityid,
                    GROUP_CONCAT(DISTINCT IF( netw.ipaddress='', null,netw.ipaddress) SEPARATOR ',') AS listipadress,
                    GROUP_CONCAT(DISTINCT IF( netw.broadcast='', null,netw.broadcast) SEPARATOR ',') AS broadcast,
                    GROUP_CONCAT(DISTINCT IF( netw.gateway='', null,netw.gateway) SEPARATOR ',') AS gateway,
                    GROUP_CONCAT(DISTINCT IF( netw.mask='', null, netw.mask) SEPARATOR ',') AS mask
                FROM
                    xmppmaster.machines mach
                        INNER JOIN
                    local_glpi_filters lgf on CONCAT("UUID", lgf.id) = mach.uuid_inventorymachine
                        LEFT OUTER JOIN
                    glpi_entity ent ON lgf.entities_id = ent.glpi_id
                        LEFT OUTER JOIN
                    glpi_location loc ON loc.id = mach.glpi_location_id
                        LEFT OUTER JOIN
                    glpi_register_keys reg ON reg.machines_id = mach.id
                        LEFT OUTER JOIN
                    network netw ON  netw.machines_id = mach.id
                WHERE
                    agenttype = 'machine'%s%s%s
                GROUP BY mach.id
                %s
                limit %s, %s;""" % (
            computerpresence,
            entity,
            recherchefild,
            ordered,
            start,
            end,
        )

        if debugfunction:
            logger.info("SQL request :  %s" % sql)

        result = session.execute(sql)
        sql_count = "SELECT FOUND_ROWS();"
        ret_count = session.execute(sql_count)
        count = ret_count.first()[0]
        session.commit()
        session.flush()
        ret = self.query_to_array_of_dict(
            result,
            bycolumn=True,
            listexclude=["picklekeypublic", "urlguacamole", "keysyncthing"],
        )
        # 'keysyncthing',
        # 'glpi_location_id',
        # 'locationid',
        # 'locationpath',
        # 'locationname'
        ret["column"] = self.config.summary
        ret["list_reg_columns_name"] = list_reg_columns_name

        for columkeyreg in list_reg_columns_name:
            ret["data"][columkeyreg] = []
            for stringkeyregistre in ret["data"]["regedit"]:
                if stringkeyregistre == "":
                    ret["data"][columkeyreg].append("")
                else:
                    for strkeyvalue in stringkeyregistre.split("@@@"):
                        couplekeyvalue = strkeyvalue.split("|")
                        if len(couplekeyvalue) == 2:
                            if couplekeyvalue[0] == columkeyreg:
                                ret["data"][columkeyreg].append(
                                    couplekeyvalue[1])
        ret["total"] = count
        return ret

    @DatabaseHelper._sessionm
    def getPresenceuuidenabled(self, session, uuid, enabled=0):
        return session.query(
            exists().where(
                and_(
                    Machines.uuid_inventorymachine == uuid, Machines.enabled == enabled
                )
            )
        ).scalar()

    @DatabaseHelper._sessionm
    def getPresenceuuid(self, session, uuid):
        machinespresente = (
            session.query(Machines.uuid_inventorymachine)
            .filter(
                and_(Machines.uuid_inventorymachine ==
                     uuid, Machines.enabled == "1")
            )
            .first()
        )
        session.commit()
        session.flush()
        if machinespresente:
            return True
        return False

    @DatabaseHelper._sessionm
    def getPresenceuuids(self, session, uuids):
        if isinstance(uuids, str):
            uuids = [uuids]
        result = {}
        for uuidmachine in uuids:
            result[uuidmachine] = False
        machinespresente = (
            session.query(Machines.uuid_inventorymachine)
            .filter(
                and_(Machines.uuid_inventorymachine.in_(
                    uuids), Machines.enabled == "1")
            )
            .all()
        )
        session.commit()
        session.flush()
        for linemachine in machinespresente:
            result[linemachine.uuid_inventorymachine] = True
        return result

    @DatabaseHelper._sessionm
    def getPresenceExistuuids(self, session, uuids):
        """
        This function is used to obtain the presence and the GLPI uuid
        of machines based on the uuids.
        Args:
            session: SQLAlchemy session
            uuids: uuid of the machine we are searching
        Return: This fonction return a dictionnary:
                {'UUID_GLPI': [presence of the machine, initialised glpi uuid]}
        """
        result = {}
        if isinstance(uuids, str):
            if uuids == "":
                return {}
            uuids = [uuids]
        if uuids:
            for uuidmachine in uuids:
                result[uuidmachine] = [0, 0]
            machinespresente = (
                session.query(Machines.uuid_inventorymachine, Machines.enabled)
                .filter(Machines.uuid_inventorymachine.in_(uuids))
                .all()
            )
            session.commit()
            session.flush()
            for linemachine in machinespresente:
                out = 0
                if linemachine.enabled is True:
                    out = 1
                result[linemachine.uuid_inventorymachine] = [out, 1]
        return result

    @DatabaseHelper._sessionm
    def update_uuid_inventory(self, session, sql_id, uuid):
        """
        This function is used to update the uuid_inventorymachine value
        in the database for a specific machine.
        Args:
            session: The SQLAlchemy session
            sql_id: the id of the machine in the SQL database
            uuid: The uuid_inventorymachine of the machine
        Return:
           It returns None if it failed to update the machine uuid_inventorymachine.
        """
        try:
            sql = """UPDATE `xmppmaster`.`machines`
                    SET
                        `uuid_inventorymachine` = '%s'
                    WHERE
                        `id`  = %s;""" % (
                uuid,
                sql_id,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return result
        except Exception as e:
            logger.error("Function update_uuid_inventory")
            logger.error("We got the error: %s" % str(e))
            return None

    # topology
    @DatabaseHelper._sessionm
    def listRS(self, session):
        """return les RS pour le deploiement"""
        sql = """SELECT DISTINCT
                    groupdeploy
                FROM
                    xmppmaster.machines
                WHERE
                    xmppmaster.machines.enabled = '1' and
                    xmppmaster.machines.agenttype="relayserver";"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        listrs = [x for x in result]
        return [i[0] for i in listrs]

    # topology
    @DatabaseHelper._sessionm
    def topologypulse(self, session):
        # listrs = self.listRS()
        # select liste des RS
        # list des machines pour un relayserver

        sql = """SELECT groupdeploy,
                    GROUP_CONCAT(jid)
                FROM
                    xmppmaster.machines
                WHERE
                    xmppmaster.machines.enabled = '1' and
                    xmppmaster.machines.agenttype = 'machine'
                GROUP BY
                    groupdeploy;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        listmachinebyRS = [x for x in result]
        resulttopologie = {}
        for i in listmachinebyRS:
            listmachines = i[1].split(",")
            resulttopologie[i[0]] = listmachines
        self.write_topologyfile(resulttopologie)
        return [resulttopologie]

    # topology
    def write_topologyfile(self, topology):
        directoryjson = os.path.join(
            "/", "usr", "share", "mmc", "datatopology")
        if not os.path.isdir(directoryjson):
            # creation repertoire de json topology
            os.makedirs(directoryjson)
            os.chmod(directoryjson, 0o777)  # for example
            uid, gid = pwd.getpwnam("root").pw_uid, pwd.getpwnam("root").pw_gid
            # set user:group as root:www-data
            os.chown(directoryjson, uid, gid)
        # creation topology file.
        filename = "topology.json"
        pathfile = os.path.join(directoryjson, filename)
        builddatajson = {"name": "Pulse", "type": "AMR",
                         "parent": None, "children": []}
        for i in topology:
            listmachines = topology[i]

            ARS = {}
            ARS["name"] = i
            ARS["display_name"] = i.split("@")[0]
            ARS["type"] = "ARS"
            ARS["parent"] = "Pulse"
            ARS["children"] = []

            listmachinesstring = []
            for mach in listmachines:
                ARS["children"].append(
                    {
                        "name": mach,
                        "display_name": mach.split(".")[0],
                        "type": "AM",
                        "parent": i,
                    }
                )
            # builddatajson[i] = listmachinesstring
            # ARS['children'] = builddatajson
            # print listmachinesstring
            builddatajson["children"].append(ARS)
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(builddatajson)

        with open(pathfile, "w") as outfile:
            json.dump(builddatajson, outfile, indent=4)
        os.chmod(pathfile, 0o777)
        uid, gid = pwd.getpwnam("root").pw_uid, pwd.getpwnam("root").pw_gid
        os.chown(pathfile, uid, gid)

    @DatabaseHelper._sessionm
    def getstepdeployinsession(self, session, sessiondeploy):
        sql = """
                SELECT
            date, text
        FROM
            xmppmaster.logs
        WHERE
            type = 'deploy'
                AND sessionname = '%s'
        ORDER BY id;""" % (
            sessiondeploy
        )
        step = session.execute(sql)
        session.commit()
        session.flush()
        step
        # return [x for x in step]
        try:
            a = []
            for t in step:
                a.append({"date": t[0], "text": t[1]})
            return a
        except BaseException:
            return []

    @DatabaseHelper._sessionm
    def getlistPresenceMachineid(self, session, format=False):
        sql = """SELECT
                    uuid_inventorymachine
                 FROM
                    xmppmaster.machines
                 WHERE
                    enabled = '1' and
                    agenttype = 'machine' and (uuid_inventorymachine IS NOT NULL AND uuid_inventorymachine!='');"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = []
            for t in presencelist:
                a.append(t[0])
            return a
        except BaseException:
            return a

    @DatabaseHelper._sessionm
    def getidlistPresenceMachine(self, session, presence=None):
        """
        This function is used to retrieve the list of the machines based on the 'presence' argument.

        Args:
            session: The SQLAlchemy session
            presence: if True, it returns the list of the machine with an agent up.
                      if False, it returns the list of the machine with an agent down.
                      if None, it returns the list with all the machines.
        Returns:
            It returns the list of the machine based on the 'presence' argument.
        """
        strpresence = ""

        try:
            if presence is not None:
                if presence:
                    strpresence = " and enabled = 1"
                else:
                    strpresence = " and enabled = 0"
            sql = (
                """SELECT
                        SUBSTR(uuid_inventorymachine, 5)
                    FROM
                        xmppmaster.machines
                    WHERE
                        agenttype = 'machine'
                    and
                        uuid_inventorymachine IS NOT NULL %s;"""
                % strpresence
            )
            presencelist = session.execute(sql)
            session.commit()
            session.flush()
            return [x[0] for x in presencelist]
        except Exception as e:
            logger.error(
                "Error debug for the getidlistPresenceMachine function!")
            logger.error("The presence of the machine is:  %s" % presence)
            logger.error("The sql error is: %s" % sql)
            logger.error("the Exception catched is %s" % str(e))
            return []

    @DatabaseHelper._sessionm
    def getxmppmasterfilterforglpi(self, session, listqueryxmppmaster=None):
        listqueryxmppmaster[2] = listqueryxmppmaster[2].lower()
        Regexpression = False
        if listqueryxmppmaster[2] in ["ou user", "ou machine"]:
            if listqueryxmppmaster[3][:1] == "/" and listqueryxmppmaster[3][-1:] == "/":
                Regexpression = True
                fl = listqueryxmppmaster[3][1:-1]
        if not Regexpression:
            # SQL Wildcards
            # % : The percentage symbol represent zero, one or several wildcard caracters.
            fl = listqueryxmppmaster[3].replace("*", "%")

        if listqueryxmppmaster[2] == "ou user":
            machineid = session.query(Machines.uuid_inventorymachine).filter(
                Machines.uuid_inventorymachine.isnot(None)
            )
            if Regexpression:
                machineid = machineid.filter(
                    Machines.ad_ou_user.op("regexp")(fl))
            else:
                machineid = machineid.filter(Machines.ad_ou_user.like(fl))
        elif listqueryxmppmaster[2] == "ou machine":
            machineid = session.query(Machines.uuid_inventorymachine).filter(
                Machines.uuid_inventorymachine.isnot(None)
            )
            if Regexpression:
                machineid = machineid.filter(
                    Machines.ad_ou_machine.op("regexp")(fl))
            else:
                machineid = machineid.filter(Machines.ad_ou_machine.like(fl))

        elif listqueryxmppmaster[2] == "online computer":
            d = XmppMasterDatabase().getlistPresenceMachineid()
            listid = [x.replace("UUID", "") for x in d]
            return listid
        machineid = machineid.all()
        session.commit()
        session.flush()
        ret = [str(m.uuid_inventorymachine).replace("UUID", "")
               for m in machineid]
        return ret

    @DatabaseHelper._sessionm
    def getListPresenceMachine(self, session):
        sql = """SELECT
                    jid, agenttype, hostname, uuid_inventorymachine
                 FROM
                    xmppmaster.machines
                 WHERE
                    enabled = '1' and
                    agenttype='machine' and uuid_inventorymachine IS NOT NULL;"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = []
            for t in presencelist:
                a.append(
                    {
                        "jid": t[0],
                        "type": t[1],
                        "hostname": t[2],
                        "uuid_inventorymachine": t[3],
                    }
                )
            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def getListPresenceMachineWithKiosk(self, session):
        sql = """SELECT
                    *
                 FROM
                    xmppmaster.machines
                 WHERE
                    enabled = '1' and
                    agenttype='machine' and uuid_inventorymachine IS NOT NULL ;"""

        presencelist = session.execute(sql)
        session.commit()
        session.flush()
        try:
            a = []
            for t in presencelist:
                a.append(
                    {
                        "id": t[0],
                        "jid": t[1],
                        "platform": t[2],
                        "hostname": t[4],
                        "uuid_inventorymachine": t[5],
                        "agenttype": t[10],
                        "classutil": t[11],
                    }
                )
            return a
        except BaseException:
            return -1

    @DatabaseHelper._sessionm
    def changStatusPresenceMachine(self, session, jid, enable="0"):
        """
        update presence machine in table machine.
        """
        try:
            user = "%s%%" % str(jid).split("@")[0]
            machine = session.query(Machines).filter(
                Machines.jid.like(user)).first()
            if machine:
                machine.enabled = "%s" % enable
                session.commit()
                session.flush()
            else:
                logger.warning(
                    "xmpp signal changement status on machine no exist %s" % jid
                )
        except Exception:
            logger.warning(
                "xmpp signal changement status on machine no exist %s" % jid)

    @DatabaseHelper._sessionm
    def delMachineXmppPresence(self, session, uuidinventory):
        """
        del machine of table machine
        """
        result = ["-1"]
        typemachine = "machine"
        try:
            sql = (
                """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.uuid_inventorymachine = '%s';"""
                % uuidinventory
            )
            id = session.execute(sql)
            session.commit()
            session.flush()
            result = [x for x in id][0]
            sql = (
                """DELETE FROM `xmppmaster`.`machines`
                    WHERE
                        `xmppmaster`.`machines`.`id` = '%s';"""
                % result[0]
            )
            if result[2] == "relayserver":
                typemachine = "relayserver"
                sql2 = (
                    """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';"""
                    % result[1]
                )
                session.execute(sql2)
            session.execute(sql)
            session.commit()
            session.flush()
        except IndexError:
            logger.warning(
                "Configuration agent machine uuidglpi [%s]. no uuid in base for configuration"
                % uuidinventory
            )
            return {}
        except Exception as e:
            logger.error(str(e))
            return {}
        resulttypemachine = {"type": typemachine}
        return resulttypemachine

    @DatabaseHelper._sessionm
    def delMachineXmppPresenceHostname(self, session, hostname):
        """
        Remove the `hostname` machine from the xmppmaster database.

        Args:
            session: The SQL Alchemy session.
            hostname: The hostname of the machine we want to remove.
        """
        result = ["-1"]
        typemachine = "machine"

        try:
            list_hostname = (
                """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.hostname  like '%s';"""
                % hostname
            )

            machines_id = session.execute(list_hostname)

            session.commit()
            session.flush()

            result = [x for x in machines_id][0]

            delete_machine = (
                """DELETE FROM `xmppmaster`.`machines`
                                WHERE
                                    `xmppmaster`.`machines`.`id` = '%s';"""
                % result[0]
            )

            if result[2] == "relayserver":
                typemachine = "relayserver"
                update_status = (
                    """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';"""
                    % result[1]
                )
                session.execute(update_status)

            session.execute(delete_machine)
            session.commit()
            session.flush()
        except IndexError as index_error:
            logger.warning(
                "The machine %s has not been found in the database. We cannot delete it."
                % hostname
            )
            logger.warning("We obtained the error: %s" % index_error)
            return {}
        except Exception as e:
            logger.error(str(e))
            return {}

        resulttypemachine = {"type": typemachine}
        return resulttypemachine

    @DatabaseHelper._sessionm
    def get_machine_from_hostname(self, session, hostname):
        """
        Retrieve the machine based on `hostname`
        Args:
            session: The SQL Alchemy session
            hostname: The hostname of the machines we are searching
        Returns:
            List of dict. The dict contains all the machines found.
        """
        sql = (
            """
                    SELECT
                        *
                    FROM
                        machines
                    WHERE
                        hostname like "%s%%";"""
            % hostname
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [rowproxy._asdict() for rowproxy in result]

    def jid_to_hostname(self, jid):
        try:
            user = jid.split("@")[0].split(".")
            if len(user) > 1:
                user = user[:-1]
        except Exception:
            return None
        user = ".".join(user)
        if not user:
            return None
        return user

    @DatabaseHelper._sessionm
    def SetPresenceMachine(self, session, jid, presence=0):
        """
        Change the presence in the machine table.
        Args:
            session: The SQL Alchemy session
            jid: The jid of the machine where we want to change the presence
            presence: The new presence state/
                      0: The machine is offline
                      1: The machine is online
        """
        user = self.jid_to_hostname(jid)
        if not user:
            logger.error("SetPresenceMachine jid error : %s" % jid)
            return False
        try:
            sql = """UPDATE
                        `xmppmaster`.`machines`
                    SET
                        `xmppmaster`.`machines`.`enabled` = '%s'
                    WHERE
                        `xmppmaster`.`machines`.hostname like '%s' limit 1;""" % (
                presence,
                user,
            )
            session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception as error_presence:
            logger.error("An error occured while setting the new presence.")
            logger.error("We got the error:\n %s" % str(error_presence))
            return False

    @DatabaseHelper._sessionm
    def updatedeployresultandstate(self, session, sessionid, state, result):
        jsonresult = json.loads(result)
        jsonautre = copy.deepcopy(jsonresult)
        del jsonautre["descriptor"]
        del jsonautre["packagefile"]
        # DEPLOYMENT START
        try:
            deploysession = (
                session.query(Deploy).filter(
                    Deploy.sessionid == sessionid).one()
            )
            if deploysession:
                if (
                    deploysession.result is None
                    or ("wol" in jsonresult and jsonresult["wol"] == 1)
                    or (
                        "advanced" in jsonresult
                        and "syncthing" in jsonresult["advanced"]
                        and jsonresult["advanced"]["syncthing"] == 1
                    )
                ):
                    jsonbase = {
                        "infoslist": [jsonresult["descriptor"]["info"]],
                        "descriptorslist": [jsonresult["descriptor"]["sequence"]],
                        "otherinfos": [jsonautre],
                        "title": deploysession.title,
                        "session": deploysession.sessionid,
                        "macadress": deploysession.macadress,
                        "user": deploysession.login,
                    }
                else:
                    jsonbase = json.loads(deploysession.result)
                    jsonbase["infoslist"].append(
                        jsonresult["descriptor"]["info"])
                    jsonbase["descriptorslist"].append(
                        jsonresult["descriptor"]["sequence"]
                    )
                    jsonbase["otherinfos"].append(jsonautre)
                deploysession.result = json.dumps(jsonbase, indent=3)
                if (
                    "infoslist" in jsonbase
                    and "otherinfos" in jsonbase
                    and jsonbase["otherinfos"]
                    and "plan" in jsonbase["otherinfos"][0]
                    and len(jsonbase["infoslist"])
                    != len(jsonbase["otherinfos"][0]["plan"])
                    and state == "DEPLOYMENT SUCCESS"
                ):
                    state = "DEPLOYMENT PARTIAL SUCCESS"
                regexpexlusion = re.compile(
                    "^(?!abort)^(?!success)^(?!error)", re.IGNORECASE
                )
                if regexpexlusion.match(state) is not None:
                    deploysession.state = state
            session.commit()
            session.flush()
            session.close()
            return 1
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error("\n%s" % (traceback.format_exc()))
            return -1

    @DatabaseHelper._sessionm
    def substituteinfo(self, session, listconfsubstitute, arsname):
        """
        This function creates sorted lists of substitutes to configure machines.
        It uses the sum of every substitute and attribute the one with the less machines in. It is used for the load balancing.
        The calculation is done taking into consideration all the substitutes associated to the relay to which the machine is connected.

        Args:
            session: The SQL Alchemy session
            listconfsubstitute: The list of the substitutes in the machine configuration
            arsname: The ars where the machine is connected to.
        Returns:
        """
        incrementeiscount = []
        try:
            try:
                sql = """SELECT
                            `substituteconf`.`id` AS `id`,
                            `substituteconf`.`jidsubtitute` AS `jidsubtitute`,
                            `substituteconf`.`type` AS `type`,
                            SUM(`substituteconf`.`countsub`) AS `totsub`
                        FROM
                            `substituteconf`
                        WHERE
                            `substituteconf`.`jidsubtitute` IN (SELECT DISTINCT
                                    `substituteconf`.`jidsubtitute`
                                FROM
                                    `substituteconf`
                                WHERE
                                    `substituteconf`.`relayserver_id` IN (SELECT
                                            id
                                        FROM
                                            xmppmaster.relayserver
                                        WHERE
                                            jid LIKE ('%s')))
                        GROUP BY `substituteconf`.`jidsubtitute` , type
                        ORDER BY type , totsub;""" % (
                    arsname
                )
                resultproxy = session.execute(sql)
                session.commit()
                session.flush()
                # ret = self._return_dict_from_dataset_mysql(resultproxy)
                for listconfsubstituteitem in listconfsubstitute["conflist"]:
                    # reinitialise les lists
                    listconfsubstitute[listconfsubstituteitem] = []
                for x in resultproxy:
                    if str(x[2]).startswith("master@pulse"):
                        continue
                    if x[2] not in listconfsubstitute:
                        listconfsubstitute["conflist"].append(x[2])
                        listconfsubstitute[x[2]] = []
                    listconfsubstitute[x[2]].append(x[1])
                    incrementeiscount.append(x[0])
                self.logger.debug("listconfsubstitute %s" % listconfsubstitute)
                self.logger.debug("incrementeiscount %s" % incrementeiscount)
            except Exception as e:
                self.logger.error(
                    "An error occured while fetching the ordered list of subsitutes."
                )
                self.logger.error(
                    "We hit the backtrace: \n%s" % (traceback.format_exc())
                )

            if incrementeiscount:
                sql = """UPDATE `xmppmaster`.`substituteconf`
                    SET
                        `countsub` = `countsub` + '1'
                    WHERE
                        `id` IN (%s);""" % ",".join(
                    [str(x) for x in incrementeiscount]
                )
                result = session.execute(sql)
                session.commit()
                session.flush()
        except Exception as e:
            logger.error("substituteinfo : %s" % str(e))
            logger.debug("substitute list : %s" % listconfsubstitute)
        return listconfsubstitute

    @DatabaseHelper._sessionm
    def GetMachine(self, session, jid):
        """
        Initialize boolean presence in table machines
        """
        user = str(jid).split("@")[0]
        try:
            sql = (
                """SELECT
                        id, hostname, agenttype, need_reconf
                    FROM
                        `xmppmaster`.`machines`
                    WHERE
                        `xmppmaster`.`machines`.jid like('%s@%%')
                    LIMIT 1;"""
                % user
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return [x for x in result][0]
        except IndexError:
            return None
        except Exception as e:
            logger.error("GetMachine : %s" % str(e))
            return None

    @DatabaseHelper._sessionm
    def updateMachinereconf(self, session, jid, status=0):
        """
        update boolean need_reconf in table machines
        """
        user = self.jid_to_hostname(jid)
        if not user:
            logger.error("SetPresenceMachine jid error : %s" % jid)
            return False
        try:
            sql = """UPDATE `xmppmaster`.`machines`
                         SET `need_reconf` = '%s'
                     WHERE
                         `xmppmaster`.`machines`.hostname like '%s' limit 1;""" % (
                status,
                user,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logger.error("updateMachinereconf : %s" % str(e))
            return False

    @DatabaseHelper._sessionm
    def initialisePresenceMachine(self, session, jid, presence=0):
        """
        Initialize presence in table machines and relay
        """
        mach = self.GetMachine(jid)
        if mach is not None:
            self.SetPresenceMachine(jid, presence)
            if mach[2] != "machine":
                try:
                    sql = """UPDATE
                                `xmppmaster`.`relayserver`
                            SET
                                `xmppmaster`.`relayserver`.`enabled` = '%s'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';""" % (
                        presence,
                        mach[1],
                    )
                    session.execute(sql)
                    session.commit()
                    session.flush()
                except Exception as e:
                    logger.error("initialisePresenceMachine : %s" % str(e))
                finally:
                    return {"type": "relayserver", "reconf": mach[3]}
            else:
                return {"type": "machine", "reconf": mach[3]}
        else:
            return {}

    @DatabaseHelper._sessionm
    def update_Presence_Relay(self, session, jid, presence=0):
        """
        Update the presence in the relay and machine SQL Tables
        Args:
            session: The SQL Alchemy session
            jid: jid of the relay to update
            presence: Availability of the relay
                      0: Set the relay as offline
                      1: Set the relay as online
        """
        try:
            user = str(jid).split("@")[0]
            sql = """UPDATE
                        `xmppmaster`.`machines`
                    SET
                        `enabled` = '%s'
                    WHERE
                        `xmppmaster`.`machines`.`jid` like('%s@%%') limit 1;""" % (
                presence,
                user,
            )
            session.execute(sql)
            sql = """UPDATE
                        `xmppmaster`.`relayserver`
                    SET
                        `enabled` = '%s'
                    WHERE
                        `xmppmaster`.`relayserver`.`jid` like('%s@%%') limit 1;""" % (
                presence,
                user,
            )
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(
                "Function : update_Presence_Relay, we got the error: " % str(e)
            )
            logger.error("We encountered the backtrace: \n%s" %
                         traceback.format_exc())

    @DatabaseHelper._sessionm
    def update_reconf_mach_of_Relay_down(self, session, jid, reconf=1):
        """
        renitialise remote configuration
        """
        try:
            user = str(jid).split("@")[0]
            sql = """UPDATE
                        `xmppmaster`.`machines`
                     SET
                        `need_reconf` = '%s'
                     WHERE
                        `xmppmaster`.`machines`.`agenttype` like ("machine")
                        AND
                        `xmppmaster`.`machines`.`groupdeploy` like('%s@%%');""" % (
                reconf,
                user,
            )
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
            logger.error("\n%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def delPresenceMachine(self, session, jid):
        """
        del machine of table machines
        """
        result = ["-1"]
        typemachine = "machine"
        try:
            sql = (
                """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.jid = '%s';"""
                % jid
            )
            id = session.execute(sql)
            session.commit()
            session.flush()
            result = [x for x in id][0]
            sql = (
                """DELETE FROM `xmppmaster`.`machines`
                    WHERE
                        `xmppmaster`.`machines`.`id` = '%s';"""
                % result[0]
            )
            if result[2] == "relayserver":
                typemachine = "relayserver"
                sql2 = (
                    """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';"""
                    % result[1]
                )
                session.execute(sql2)
            session.execute(sql)
            session.commit()
            session.flush()
        except IndexError:
            logger.warning(
                "Configuration agent machine jid [%s]. no jid in base for configuration"
                % jid
            )
            return {}
        except Exception as e:
            logger.error(str(e))
            return {}
        resulttypemachine = {"type": typemachine}
        return resulttypemachine

    @DatabaseHelper._sessionm
    def getPresencejiduser(self, session, jiduser, enable="1"):
        """
        presence machine for jid user  ...@
        """
        machine = (
            session.query(Machines)
            .filter(
                and_(
                    Machines.jid.like("%s@%%" % (jiduser)),
                    Machines.enabled == "%s" % enable,
                )
            )
            .first()
        )
        session.commit()
        session.flush()
        if machine is None:
            return False
        return True

    @DatabaseHelper._sessionm
    def delPresenceMachinebyjiduser(self, session, jiduser):
        """
        del machine of table machines
        """
        result = ["-1"]
        typemachine = "machine"
        try:
            sql = (
                """SELECT
                        id, hostname, agenttype
                    FROM
                        xmppmaster.machines
                    WHERE
                        xmppmaster.machines.jid like('%s@%%');"""
                % jiduser
            )
            id = session.execute(sql)
            session.commit()
            session.flush()
            result = [x for x in id][0]
            sql = (
                """DELETE FROM `xmppmaster`.`machines`
                    WHERE
                        `xmppmaster`.`machines`.`id` = '%s';"""
                % result[0]
            )
            if result[2] == "relayserver":
                typemachine = "relayserver"
                sql2 = (
                    """UPDATE `xmppmaster`.`relayserver`
                            SET
                                `enabled` = '0'
                            WHERE
                                `xmppmaster`.`relayserver`.`nameserver` = '%s';"""
                    % result[1]
                )
                session.execute(sql2)
            session.execute(sql)
            session.commit()
            session.flush()
        except IndexError:
            logger.warning(
                "Configuration agent machine jid [%s]. no jid in base for configuration"
                % jiduser
            )
            return {}
        except Exception as e:
            logger.error(str(e))
            return {}
        resulttypemachine = {"type": typemachine}
        return resulttypemachine

    @DatabaseHelper._sessionm
    def update_status_waiting_for_machine_off_in_state_deploy_start(self, session):
        """
        Change the status of deploiements where the computer is offline.
        It change de status from DEPLOYMENT START to WAITING MACHINE ONLINE
        """
        try:
            sql = """UPDATE `xmppmaster`.`deploy`
                        SET
                            `state` = 'WAITING MACHINE ONLINE'
                        WHERE
                            deploy.sessionid IN (SELECT
                                    sessionid
                                FROM
                                    xmppmaster.deploy
                                        JOIN
                                    xmppmaster.machines ON FS_JIDUSERTRUE(machines.jid) = FS_JIDUSERTRUE(deploy.jidmachine)
                                WHERE
                                    deploy.state = 'DEPLOYMENT START'
                                        AND (NOW() BETWEEN deploy.startcmd AND deploy.endcmd)
                                        AND machines.enabled = 0);"""
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception:
            logger.error("%s" % (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def update_status_waiting_for_deploy_on_machine_restart_or_stop(self, session):
        """
        We select the machines in a stalled deploiement for more than 60 seconds in the
        WAITING MACHINE ONLINE state.
        """
        try:
            sql = """UPDATE `xmppmaster`.`deploy`
                        SET
                            `state` = 'WAITING MACHINE ONLINE'
                        WHERE
                            `deploy`.sessionid IN (SELECT DISTINCT
                                    `xmppmaster`.`deploy`.sessionid
                                FROM
                                    xmppmaster.deploy
                                        JOIN
                                    logs ON logs.sessionname = deploy.sessionid
                                WHERE
                                    deploy.state = 'DEPLOYMENT START'
                                        AND (NOW() BETWEEN deploy.startcmd AND deploy.endcmd)
                                        AND logs.text LIKE '%online. Starting deployment%'
                                        AND logs.date < DATE_ADD(NOW(), INTERVAL - 60 SECOND)
                                        AND NOT EXISTS( SELECT
                                            *
                                        FROM
                                            logs
                                        WHERE
                                            logs.text LIKE 'File transfer is enabled'
                                                AND sessionname = deploy.sessionid)
                                GROUP BY deploy.sessionid);"""
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception as stalled_error:
            logger.error(
                "We failed to find/select machines on a stalled deploiement for more than 60 seconds"
            )
            logger.error("We got the error %s" % stalled_error)
            logger.error("We hit the backtrace: \n %s" %
                         (traceback.format_exc()))

    @DatabaseHelper._sessionm
    def search_machines_from_state(self, session, state, subdep_user=None):
        dateend = datetime.now()
        sql = """SELECT
                    *
                FROM
                    xmppmaster.deploy
                WHERE
                    state LIKE '%s%%' AND
                    '%s' BETWEEN startcmd AND
                    endcmd;""" % (
            state,
            dateend,
        )
        machines = session.execute(sql)
        session.commit()
        session.flush()
        result = [x for x in machines]
        resultlist = []
        for t in result:
            listresult = {
                "id": t[0],
                "title": t[1],
                "jidmachine": t[2],
                "jid_relay": t[3],
                "pathpackage": t[4],
                "state": t[5],
                "sessionid": t[6],
                "start": str(t[7]),
                "startcmd": str(t[8]),
                "endcmd": str(t[9]),
                "inventoryuuid": t[10],
                "host": t[11],
                "user": t[12],
                "command": t[13],
                "group_uuid": t[14],
                "login": t[15],
                "macadress": t[16],
                "syncthing": t[17],
                "result": t[18],
            }
            resultlist.append(listresult)
        return resultlist

    @DatabaseHelper._sessionm
    def Timeouterrordeploy(self, session):
        """
        Args:
            session: The SqlAlchemy session
        Returns:
            It returns an Array with the list of deploys in timeout
        """
        Stateforupdateontimeout = [
            "'WOL 1'",
            "'WOL 2'",
            "'WOL 3'",
            "'WAITING MACHINE ONLINE'",
            "'DEPLOYMENT START'",
            "'WAITING REBOOT'",
            "'DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)'",
            "'Offline'",
        ]

        nowdate = datetime.now()
        set_search = ",".join(Stateforupdateontimeout)

        try:
            sql = """SELECT
                        *
                    FROM
                        xmppmaster.deploy
                    WHERE
                        state in (%s) AND
                        '%s' > endcmd;""" % (
                set_search,
                nowdate,
            )
            machines = session.execute(sql)
            session.commit()
            session.flush()
            result = [x for x in machines]
            resultlist = []
            for t in result:
                self.update_state_deploy(t[0], "ABORT ON TIMEOUT")
                listresult = {
                    "id": t[0],
                    "title": t[1],
                    "jidmachine": t[2],
                    "jid_relay": t[3],
                    "pathpackage": t[4],
                    "state": t[5],
                    "sessionid": t[6],
                    "start": str(t[7]),
                    "startcmd": str(t[8]),
                    "endcmd": str(t[9]),
                    "inventoryuuid": t[10],
                    "host": t[11],
                    "user": t[12],
                    "command": t[13],
                    "group_uuid": t[14],
                    "login": t[15],
                    "macadress": t[16],
                    "syncthing": t[17],
                    "result": t[18],
                }
                resultlist.append(listresult)
            return resultlist
        except Exception as e:
            logger.error(str(e))
            logger.error("fn Timeouterrordeploy on sql %s" % (sql))
            return resultlist

    @DatabaseHelper._sessionm
    def update_state_deploy(self, session, id, state):
        try:
            sql = """UPDATE `xmppmaster`.`deploy`
                     SET `state`='%s'
                     WHERE `id`='%s';""" % (
                state,
                id,
            )
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))

    def restart_blocked_deployments(self, nb_reload=50):
        """
        Plan with blocked deployments again
        call procedure mmc_restart_blocked_deployments
        """
        connection = self.db.raw_connection()
        results = None
        try:
            self.logger.info(
                "call procedure stockee mmc_restart_blocked_deployments(%s)" % nb_reload
            )
            cursor = connection.cursor()
            cursor.callproc("mmc_restart_blocked_deployments", [nb_reload])
            results = list(cursor.fetchall())
            cursor.close()
            connection.commit()
        finally:
            connection.close()
        self.logger.info("results (%s)" % results)
        return results

    @DatabaseHelper._sessionm
    def updatedeploytosessionid(self, session, status, sessionid):
        try:
            sql = """UPDATE `xmppmaster`.`deploy`
                     SET `state`='%s'
                     WHERE `sessionid`='%s';""" % (
                status,
                sessionid,
            )
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))

    @DatabaseHelper._sessionm
    def updatedeploytosyncthing(self, session, sessionid, syncthing=1):
        try:
            sql = """UPDATE `xmppmaster`.`deploy`
                     SET `syncthing`='%s'
                     WHERE `sessionid`='%s';""" % (
                syncthing,
                sessionid,
            )
            # print sql
            session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))

    @DatabaseHelper._sessionm
    def nbsyncthingdeploy(self, session, grp, cmd):
        try:
            sql = """SELECT
                        COUNT(*) as nb
                    FROM
                        deploy
                    WHERE
                        group_uuid = %s AND command = %s
                            AND syncthing > 1;""" % (
                grp,
                cmd,
            )
            req = session.execute(sql)
            session.commit()
            session.flush()
            ret = [elt for elt in req]
            return ret[0][0]
        except Exception as e:
            logger.error(str(e))
            return 0

    @DatabaseHelper._sessionm
    def getPresencejiduser(self, session, userjid):
        user = str(userjid).split("@")[0]
        sql = """SELECT COUNT(jid) AS nb
            FROM
                 xmppmaster.machines
             WHERE
              jid LIKE ('%s%%');""" % (
            user
        )
        presencejid = session.execute(sql)
        session.commit()
        session.flush()
        ret = [m[0] for m in presencejid]
        if ret[0] == 0:
            return False
        return True

    @DatabaseHelper._sessionm
    def getMachinedeployexistonHostname(self, session, hostname):
        """
        This function is used to find all the machines based on the hostname
        Args:
            session: The SQLAlchemy session
            hostname: The hostname we are searching

        Returns:
            It returns the list of the machines with the searched hostname
        """
        machinesexits = []
        try:
            sql = (
                """SELECT
                    machines.id AS id,
                    machines.uuid_inventorymachine AS uuid,
                    machines.uuid_serial_machine AS serial,
                    GROUP_CONCAT(network.mac) AS macs
                FROM
                    xmppmaster.machines
                        JOIN
                    xmppmaster.network ON machines.id = network.machines_id
                WHERE
                    machines.agenttype = 'machine'
                        AND machines.hostname LIKE '%s'
                GROUP BY machines.id;"""
                % hostname.strip()
            )
            machines = session.execute(sql)
        except Exception as e:
            logger.error("The hostname is: %s" % str(e))
            logger.error("We encountered the error: %s" % str(e))
            return machinesexits

        for machine in machines:
            mach = {
                "id": machine.id,
                "uuid": machine.uuid,
                "macs": machine.macs,
                "serial": machine.serial,
            }
            machinesexits.append(mach)
        return machinesexits

    @DatabaseHelper._sessionm
    def getMachineHostname(self, session, hostname):
        try:
            machine = (
                session.query(Machines.id, Machines.uuid_inventorymachine)
                .filter(Machines.hostname == hostname)
                .first()
            )
            session.commit()
            session.flush()
            if machine:
                return {
                    "id": machine.id,
                    "uuid_inventorymachine": machine.uuid_inventorymachine,
                }
        except Exception as e:
            logger.error("function getMachineHostname %s" % str(e))

        return {}

    @DatabaseHelper._sessionm
    def getAgenttype(self, session, hostname):
        """
        This function is use to define the agenttype of an agent.
        Args:
            session: The SqlAlchemy session
            hostname: The hostname of the machine where we try to define the agenttype.

        Returns:
            It returns the type of an agent.
            If two or more machines have the same hostname, we use the first one.
            Can be machine, relay or None ( if we can't detect ).

        """
        machine = (
            session.query(Machines.agenttype)
            .filter(Machines.hostname == hostname)
            .first()
        )
        if machine:
            return machine.agenttype

        return None

    @DatabaseHelper._sessionm
    def getGuacamoleRelayServerMachineHostname(
        self, session, hostname, enable=1, agenttype="machine"
    ):
        querymachine = session.query(Machines)
        agenttype = self.getAgenttype(hostname)
        if enable == None:
            querymachine = querymachine.filter(Machines.hostname == hostname)
        else:
            querymachine = querymachine.filter(
                and_(
                    Machines.hostname == hostname,
                    Machines.enabled == enable,
                    Machines.agenttype == agenttype,
                )
            )
        machine = querymachine.first()
        session.commit()
        session.flush()
        try:
            result = {
                "uuid": machine.uuid_inventorymachine,
                "jid": machine.jid,
                "groupdeploy": machine.groupdeploy,
                "urlguacamole": machine.urlguacamole,
                "subnetxmpp": machine.subnetxmpp,
                "hostname": machine.hostname,
                "platform": machine.platform,
                "macaddress": machine.macaddress,
                "archi": machine.archi,
                "uuid_inventorymachine": machine.uuid_inventorymachine,
                "ip_xmpp": machine.ip_xmpp,
                "agenttype": machine.agenttype,
                "keysyncthing": machine.keysyncthing,
                "enabled": machine.enabled,
            }
            for i in result:
                if result[i] is None:
                    result[i] = ""
        except Exception:
            result = {
                "uuid": -1,
                "jid": "",
                "groupdeploy": "",
                "urlguacamole": "",
                "subnetxmpp": "",
                "hostname": "",
                "platform": "",
                "macaddress": "",
                "archi": "",
                "uuid_inventorymachine": "",
                "ip_xmpp": "",
                "agenttype": "",
                "keysyncthing": "",
                "enabled": 0,
            }
        return result

    @DatabaseHelper._sessionm
    def get_machine_with_dupplicate_uuidinventory(self, session, uuid, enable=1):
        """
        This function is used to retrieve computers with dupplicate uuids.
        Args:
            session: The SQL Alchemy session
            uuid: The uuid we are looking for
            enable: Used to search for enabled or disabled only machines

        Returns:
            It return machines with dupplicate UUIDs.
            We can search for enabled/disabled or all machines.
        """
        try:
            querymachine = session.query(Machines)
            if enable is None:
                querymachine = querymachine.filter(
                    Machines.uuid_inventorymachine == uuid
                )
            else:
                querymachine = querymachine.filter(
                    and_(
                        Machines.uuid_inventorymachine == uuid,
                        Machines.enabled == enable,
                    )
                )
            machine = querymachine.all()
            resultdata = []
            if machine:
                for t in machine:
                    result = {
                        "uuid": uuid,
                        "jid": t.jid,
                        "groupdeploy": t.groupdeploy,
                        "urlguacamole": t.urlguacamole,
                        "subnetxmpp": t.subnetxmpp,
                        "hostname": t.hostname,
                        "platform": t.platform,
                        "macaddress": t.macaddress,
                        "archi": t.archi,
                        "uuid_inventorymachine": t.uuid_inventorymachine,
                        "ip_xmpp": t.ip_xmpp,
                        "agenttype": t.agenttype,
                        "keysyncthing": t.keysyncthing,
                        "enabled": t.enabled,
                    }
                    for i in result:
                        if result[i] is None:
                            result[i] = ""
                    resultdata.append(result)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(
                "We failed to search the computers having %s as uuid" % uuid)
            logger.error("The backtrace we trapped is: \n %s" % str(e))
        return resultdata

    @DatabaseHelper._sessionm
    def getGuacamoleRelayServerMachineUuid(self, session, uuid, enable=1):
        result = {
            "error": "noresult",
            "uuid": uuid,
            "jid": "",
            "groupdeploy": "",
            "urlguacamole": "",
            "subnetxmpp": "",
            "hostname": "",
            "platform": "",
            "macaddress": "",
            "archi": "",
            "uuid_inventorymachine": "",
            "ip_xmpp": "",
            "agenttype": "",
            "keysyncthing": "",
            "enabled": enable,
        }
        try:
            querymachine = session.query(Machines)
            if enable is None:
                querymachine = querymachine.filter(
                    Machines.uuid_inventorymachine == uuid
                )
            else:
                querymachine = querymachine.filter(
                    and_(
                        Machines.uuid_inventorymachine == uuid,
                        Machines.enabled == enable,
                    )
                )
            machine = querymachine.one()

            session.commit()
            session.flush()

            result = {
                "error": "noerror",
                "uuid": uuid,
                "jid": machine.jid,
                "groupdeploy": machine.groupdeploy,
                "urlguacamole": machine.urlguacamole,
                "subnetxmpp": machine.subnetxmpp,
                "hostname": machine.hostname,
                "platform": machine.platform,
                "macaddress": machine.macaddress,
                "archi": machine.archi,
                "uuid_inventorymachine": machine.uuid_inventorymachine,
                "ip_xmpp": machine.ip_xmpp,
                "agenttype": machine.agenttype,
                "keysyncthing": machine.keysyncthing,
                "enabled": machine.enabled,
            }
            for i in result:
                if result[i] is None:
                    result[i] = ""

        except NoResultFound as e:
            result["error"] = "NoResultFound"
            if enable is None:
                logger.error("We found no machines with the UUID %s" % uuid)
            else:
                logger.error(
                    "We found no machines with the UUID %s, and with enabled: %s"
                    % (uuid, enable)
                )

            logger.error("We encountered the following error:\n %s" % str(e))
        except MultipleResultsFound as e:
            result["error"] = "MultipleResultsFound"
            if enable is None:
                logger.error(
                    "We found multiple machines with the UUID %s" % uuid)
            else:
                logger.error(
                    "We found multiple machines with the UUID %s, and with enabled: %s"
                    % uuid,
                    enable,
                )

            logger.error("We encountered the following error:\n %s" % str(e))

        except Exception as e:
            result["error"] = str(e)
            if enable is None:
                logger.error(
                    "We were searching for machines with the UUID %s" % uuid)
            else:
                logger.error(
                    "We were searching for machines with the UUID %s, and with enabled: %s"
                    % uuid,
                    enable,
                )

            logger.error("We encountered the following error:\n %s" % str(e))

        return result

    @DatabaseHelper._sessionm
    def getGuacamoleidforUuid(self, session, uuid, existtest=None):
        """
        if existtest is None
         this function return the list of protocole for 1 machine
         if existtest is not None:
         this function return True if guacamole is configured
         or false si guacamole is not configued.
        """
        if existtest is None:
            ret = (
                session.query(Has_guacamole.idguacamole,
                              Has_guacamole.protocol)
                .filter(
                    and_(
                        Has_guacamole.idinventory == uuid.replace("UUID", ""),
                        Has_guacamole.protocol != "INF",
                    )
                )
                .all()
            )
            session.commit()
            session.flush()
            if ret:
                return [(m[1], m[0]) for m in ret]
            else:
                return []
        else:
            ret = (
                session.query(Has_guacamole.idguacamole)
                .filter(Has_guacamole.idinventory == uuid.replace("UUID", ""))
                .first()
            )
            if ret:
                return True
            return False

    @DatabaseHelper._sessionm
    def getGuacamoleIdForHostname(self, session, host, existtest=None):
        """
        if existtest is None
         this function return the list of protocole for 1 machine
         if existtest is not None:
         this function return True if guacamole is configured
         or false si guacamole is not configued.
        """
        if existtest is None:
            protocole = session.query(
                Has_guacamole.idguacamole, Has_guacamole.protocol
            ).join(Machines, Machines.id == Has_guacamole.machine_id)
            protocole = protocole.filter(
                and_(Has_guacamole.protocol != "INF", Machines.hostname == host)
            )
            protocole = protocole.all()
            session.commit()
            session.flush()
            if protocole:
                return [(m[1], m[0]) for m in protocole]
            else:
                return []
        else:
            protocole = session.query(Has_guacamole.idguacamole).join(
                Machines, Machines.id == Has_guacamole.machine_id
            )
            protocole = protocole.filter(Machines.hostname == host)

            protocole = protocole.first()
            if protocole:
                return True
            return False

    @DatabaseHelper._sessionm
    def isMachineExistPresentTFN(self, session, jid):
        """
        This function is used to determine if a machine exist and is online.

        Args:
            session:    Sqlalchemy session
            jid:        Jid of the machine we are testing

        Returns:
            It returns None if the machine does not exists in pulse machine database
            It returns True if the machines exists in pulse machine database and is online
            It returns False if the machines exists in pulse machine database and is offline
        """
        machine = session.query(Machines).filter(
            and_(Machines.jid == jid)).first()
        if machine:
            if machine.enabled == "0":
                return False

            return True

        return None

    @DatabaseHelper._sessionm
    def getPresencejid(self, session, jid, eanable=1):
        machine = (
            session.query(Machines)
            .filter(and_(Machines.jid == jid, Machines.enabled == eanable))
            .first()
        )
        session.commit()
        session.flush()
        if machine is None:
            return False
        return True

    @DatabaseHelper._sessionm
    def getMacsMachinefromjid(self, session, jidorjid):
        if isinstance(jidorjid, str) and "@" in jidorjid:
            # jid
            """information machine"""
            user = str(jidorjid).split("@")[0]

            sql = (
                """
            SELECT
                xmppmaster.network.macaddress,
                xmppmaster.network.broadcast,
                xmppmaster.machines.groupdeploy
            FROM
                xmppmaster.machines
                    INNER JOIN
                xmppmaster.network ON xmppmaster.network.machines_id = xmppmaster.machines.id
            WHERE
                xmppmaster.machines.jid LIKE '%s%%'
                    AND xmppmaster.network.ipaddress IS NOT NULL
                    AND xmppmaster.network.mask IS NOT NULL
                    AND xmppmaster.network.broadcast IS NOT NULL;"""
                % user
            )
        elif isinstance(jidorjid, list) and jidorjid:
            # uuid
            re = ",".join(["'%s'" % t for t in jidorjid])
            sql = (
                """
            SELECT
                xmppmaster.network.macaddress,
                xmppmaster.network.broadcast,
                xmppmaster.machines.groupdeploy
            FROM
                xmppmaster.machines
                    INNER JOIN
                xmppmaster.network ON xmppmaster.network.machines_id = xmppmaster.machines.id
            WHERE
                xmppmaster.machines.uuid_inventorymachine in(%s)
                    AND xmppmaster.network.ipaddress IS NOT NULL
                    AND xmppmaster.network.mask IS NOT NULL
                    AND xmppmaster.network.broadcast IS NOT NULL;"""
                % re
            )
        else:
            return None
        result = session.execute(sql)
        session.commit()
        session.flush()
        d = self._return_dict_from_dataset_mysql(result)
        return d

    @DatabaseHelper._sessionm
    def getMachinefromjid(self, session, jid):
        """information machine"""
        user = str(jid).split("@")[0]
        machine = (
            session.query(Machines).filter(
                Machines.jid.like("%s%%" % user)).first()
        )
        session.commit()
        session.flush()
        result = {}
        if machine:
            result = {
                "id": machine.id,
                "jid": machine.jid,
                "platform": machine.platform,
                "archi": machine.archi,
                "hostname": machine.hostname,
                "uuid_inventorymachine": machine.uuid_inventorymachine,
                "ip_xmpp": machine.ip_xmpp,
                "ippublic": machine.ippublic,
                "macaddress": machine.macaddress,
                "subnetxmpp": machine.subnetxmpp,
                "agenttype": machine.agenttype,
                "classutil": machine.classutil,
                "groupdeploy": machine.groupdeploy,
                "urlguacamole": machine.urlguacamole,
                "picklekeypublic": machine.picklekeypublic,
                "ad_ou_user": machine.ad_ou_user,
                "ad_ou_machine": machine.ad_ou_machine,
                "kiosk_presence": machine.kiosk_presence,
                "lastuser": machine.lastuser,
                "keysyncthing": machine.keysyncthing,
                "enabled": machine.enabled,
                "uuid_serial_machine": machine.uuid_serial_machine,
            }
        return result

    @DatabaseHelper._sessionm
    def getMachinefromuuid(self, session, uuid):
        """
        This function is used to retrieve a machine from its UUID.
        Args:
            uuid: The UUID of the machine we are looking for
        Returns:
            It returns a dictionary with the machine information.
        """
        machine = (
            session.query(Machines)
            .filter(Machines.uuid_inventorymachine == uuid)
            .first()
        )

        # Initializes everything, including the network, with an empty chain by default
        result = {
            "id": "",
            "jid": "",
            "platform": "",
            "archi": "",
            "hostname": "",
            "uuid_inventorymachine": "",
            "ip_xmpp": "",
            "ippublic": "",
            "macaddress": "",
            "subnetxmpp": "",
            "agenttype": "",
            "classutil": "",
            "groupdeploy": "",
            "urlguacamole": "",
            "picklekeypublic": "",
            "ad_ou_user": "",
            "ad_ou_machine": "",
            "kiosk_presence": "",
            "lastuser": "",
            "enabled": "",
            "uuid_serial_machine": "",
            "ipaddress": "",
            "mac": "",
            "broadcast": "",
            "gateway": "",
            "mask": ""
        }

        if machine:
            # Update machine info
            result.update({
                "id": machine.id,
                "jid": machine.jid,
                "platform": machine.platform,
                "archi": machine.archi,
                "hostname": machine.hostname,
                "uuid_inventorymachine": machine.uuid_inventorymachine,
                "ip_xmpp": machine.ip_xmpp or "",
                "ippublic": machine.ippublic or "",
                "macaddress": machine.macaddress or "",
                "subnetxmpp": machine.subnetxmpp or "",
                "agenttype": machine.agenttype or "",
                "classutil": machine.classutil or "",
                "groupdeploy": machine.groupdeploy or "",
                "urlguacamole": machine.urlguacamole or "",
                "picklekeypublic": machine.picklekeypublic or "",
                "ad_ou_user": machine.ad_ou_user or "",
                "ad_ou_machine": machine.ad_ou_machine or "",
                "kiosk_presence": str(machine.kiosk_presence),
                "lastuser": machine.lastuser or "",
                "enabled": str(machine.enabled),
                "uuid_serial_machine": machine.uuid_serial_machine or "",
            })

            # search for the "perfect" network line
            complete_net = (
                session.query(Network)
                .filter(
                    Network.machines_id == machine.id,
                    Network.ipaddress.isnot(None), Network.ipaddress != "",
                    Network.broadcast.isnot(None), Network.broadcast != "",
                    Network.gateway.isnot(None),   Network.gateway   != "",
                    Network.mask.isnot(None),      Network.mask      != ""
                )
                .first()
            )
            # Fallback on the first if no "perfect"
            if not complete_net:
                complete_net = (
                    session.query(Network)
                    .filter(Network.machines_id == machine.id)
                    .first()
                )

            # update, or leave the initial gaps
            if complete_net:
                result.update({
                    "ipaddress": complete_net.ipaddress or "",
                    "mac":       complete_net.mac         or "",
                    "broadcast": complete_net.broadcast   or "",
                    "gateway":   complete_net.gateway     or "",
                    "mask":      complete_net.mask        or "",
                })

        session.commit()
        return result

    @DatabaseHelper._sessionm
    def getRelayServerForMachineUuid(self, session, uuid):
        relayserver = (
            session.query(Machines)
            .filter(Machines.uuid_inventorymachine == uuid)
            .filter(Machines.agenttype == "machine")
            .one()
        )
        session.commit()
        session.flush()
        try:
            result = {"uuid": uuid, "jid": relayserver.groupdeploy}
            for i in result:
                if result[i] is None:
                    result[i] = ""
        except Exception:
            result = {"uuid": uuid, "jid": ""}
        return result

    @DatabaseHelper._sessionm
    def getCountOnlineMachine(self, session):
        return (
            session.query(func.count(Machines.id))
            .filter(and_(Machines.agenttype == "machine", Machines.enabled == "1"))
            .scalar()
        )

    @DatabaseHelper._sessionm
    def getRelayServerofclusterFromjidars(
        self, session, jid, moderelayserver=None, enablears=1
    ):
        # determine ARS id from jid
        relayserver = session.query(RelayServer).filter(RelayServer.jid == jid)
        relayserver = relayserver.first()
        session.commit()
        session.flush()
        if relayserver:
            # object complete
            notconfars = {
                relayserver.jid: [
                    relayserver.ipconnection,
                    relayserver.port,
                    relayserver.jid,
                    relayserver.urlguacamole,
                    0,
                    relayserver.syncthing_port,
                ]
            }
            # search for clusters where ARS is
            clustersid = session.query(Has_cluster_ars).filter(
                Has_cluster_ars.id_ars == relayserver.id
            )
            clustersid = clustersid.all()
            session.commit()
            session.flush()
            # search the ARS in the same cluster that ARS finds
            if clustersid:
                listcluster_id = [m.id_cluster for m in clustersid]
                ars = (
                    session.query(RelayServer)
                    .join(Has_cluster_ars, Has_cluster_ars.id_ars == RelayServer.id)
                    .join(Cluster_ars, Has_cluster_ars.id_cluster == Cluster_ars.id)
                )
                ars = ars.filter(
                    Has_cluster_ars.id_cluster.in_(listcluster_id))
                if moderelayserver is not None:
                    ars = ars.filter(
                        RelayServer.moderelayserver == moderelayserver)
                if enablears is not None:
                    ars = ars.filter(RelayServer.enabled == enablears)
                ars = ars.all()
                session.commit()
                session.flush()
                if ars:
                    # result1 = [(m.ipconnection,m.port,m.jid,m.urlguacamole)for m in ars]
                    try:
                        result2 = {
                            m.jid: [
                                m.ipconnection,
                                m.port,
                                m.jid,
                                m.urlguacamole,
                                0,
                                m.keysyncthing,
                                m.syncthing_port,
                            ]
                            for m in ars
                        }
                    except Exception:
                        result2 = {
                            m.jid: [
                                m.ipconnection,
                                m.port,
                                m.jid,
                                m.urlguacamole,
                                0,
                                "",
                                0,
                            ]
                            for m in ars
                        }
                    countarsclient = self.algoloadbalancerforcluster()
                    if countarsclient:
                        for i in countarsclient:
                            try:
                                if result2[i[1]]:
                                    result2[i[1]][4] = i[0]
                            except KeyError:
                                pass
                    return result2
            else:
                # there are no clusters configured for this ARS.
                logger.warning(
                    "Cluster ARS [%s] no configured" % relayserver.jid)
                return notconfars
        else:
            logger.warning("Relay server no present")
            logger.warning("ARS not known for machine")
        return {}

    @DatabaseHelper._sessionm
    def algoloadbalancerforcluster(self, session):
        sql = """
            SELECT
                COUNT(*) - 1 AS nb, `machines`.`groupdeploy`
            FROM
                xmppmaster.machines
            GROUP BY `machines`.`groupdeploy`
            HAVING nb != 0
                AND COALESCE(`machines`.`groupdeploy`, '') <> ''
            ORDER BY nb DESC;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [x for x in result]

    @DatabaseHelper._sessionm
    def get_machine_ad_infos(self, session, uuid_inventory):
        """
        Select the founded OUs of the logged machine.
        Param:
            uuid_inventory: str. This param is the uuid of the inventory of the machine received by xmpp.

        Returns:
            List of tuple. The tuple contains all the ou_machine and ou_user founded.
        """

        sql = """
        SELECT
            ad_ou_machine, ad_ou_user
        FROM
            machines
        WHERE
            enabled = '1' and
            uuid_inventorymachine = '%s';""" % (
            uuid_inventory
        )

        result = session.execute(sql)
        session.commit()
        session.flush()
        return [element for element in result]

    @DatabaseHelper._sessionm
    def get_machines_with_kiosk(self, session):
        """
        Select the machines with the kiosk installed.
        Returns:
            List of tuple. The tuple contains all the machines founded.
        """

        sql = """
        SELECT
            *
        FROM
            machines
        WHERE
            enabled = '1' and
            kiosk_presence = 'True';"""
        result = session.execute(sql)
        session.commit()
        session.flush()

        return [element for element in result]

    @DatabaseHelper._sessionm
    def get_machines_online_for_dashboard(self, session):
        ret = (
            session.query(Machines.uuid_inventorymachine, Machines.macaddress)
            .filter(and_(Machines.agenttype != "relayserver", Machines.enabled == "1"))
            .all()
        )

        if ret is None:
            ret = []
        else:
            ret = [{"uuid": machine[0], "macaddress": machine[1]}
                   for machine in ret]
        return ret

    @DatabaseHelper._sessionm
    def get_computer_count_for_dashboard(self, session, entities:list=[]):
        """
        Count the machines based on:
            - machine offline uninventoried
            - machine offline inventoried
            - machine online uninventoried
            - machine online inventoried
            - total of uninventoried machines
            - total of inventoried machines
            - total of (all) machines

        Params:
            - self XmppMasterDatabase: Object instance
            - session Sqlalchemy session: Wrapped session.

        Return dict containing the machines counts
        """

        # Convert the list of int to a list of str, to be able to join them
        entities = "(%s)"%(','.join([str(e) for e in entities]))

        # Bind the datas to the request.
        bind = {'agenttype': 'machine'}
        sql = """SELECT
          SUM(1) as total,
          SUM(CASE WHEN enabled = 0 THEN 1 ELSE 0 END) as total_offline,
          SUM(CASE WHEN enabled = 0 AND uuid_inventorymachine = "" THEN 1 ELSE 0 END) as offline_uninventoried,
          SUM(CASE WHEN enabled = 0 AND uuid_inventorymachine != "" THEN 1 ELSE 0 END) as offline_inventoried,
          SUM(CASE WHEN enabled = 1 THEN 1 ELSE 0 END) as total_online,
          SUM(CASE WHEN enabled = 1 AND uuid_inventorymachine = "" THEN 1 ELSE 0 END) as online_uninventoried,
          SUM(CASE WHEN enabled = 1 AND uuid_inventorymachine != "" THEN 1 ELSE 0 END) as online_inventoried,
          SUM(CASE WHEN uuid_inventorymachine = "" THEN 1 ELSE 0 END) as total_uninventoried,
          SUM(CASE WHEN uuid_inventorymachine != "" THEN 1 ELSE 0 END) as total_inventoried
        FROM machines
        join local_glpi_filters lgf on machines.uuid_inventorymachine = concat("UUID", lgf.id)
        where agenttype ="machine" and lgf.entities_id in %s"""%entities
        result = session.execute(sql, bind).first()
        session.commit()
        session.flush()

        # There is only one line so we can truncate
        ret = {
            "total": int(result.total) if result.total is not None else 0,
            "total_offline": int(result.total_offline) if result.total_offline is not None else 0,
            "offline_uninventoried": int(result.offline_uninventoried) if result.offline_uninventoried is not None else 0,
            "offline_inventoried": int(result.offline_inventoried) if result.offline_inventoried is not None else 0,
            "total_online": int(result.total_online) if result.total_online is not None else 0,
            "online_uninventoried": int(result.online_uninventoried) if result.online_uninventoried is not None else 0,
            "online_inventoried": int(result.online_inventoried) if result.online_inventoried is not None else 0,
            "total_uninventoried": int(result.total_uninventoried) if result.total_uninventoried is not None else 0,
            "total_inventoried": int(result.total_inventoried) if result.total_inventoried is not None else 0,
        }

        return ret

    @DatabaseHelper._sessionm
    def get_syncthing_deploy_to_clean(self, session):
        sql = """
    SELECT
        distinct xmppmaster.syncthing_deploy_group.id,
        GROUP_CONCAT(xmppmaster.syncthing_machine.jidmachine) AS jidmachines,
        GROUP_CONCAT(xmppmaster.syncthing_machine.jid_relay) AS jidrelays,
        xmppmaster.syncthing_ars_cluster.numcluster,
        syncthing_deploy_group.directory_tmp
    FROM
        xmppmaster.syncthing_deploy_group
            INNER JOIN
        xmppmaster.syncthing_ars_cluster
            ON xmppmaster.syncthing_deploy_group.id = xmppmaster.syncthing_ars_cluster.fk_deploy
            INNER JOIN
        xmppmaster.syncthing_machine
            ON xmppmaster.syncthing_ars_cluster.fk_deploy = xmppmaster.syncthing_deploy_group.id
    WHERE
        xmppmaster.syncthing_deploy_group.dateend < NOW()
    GROUP BY xmppmaster.syncthing_ars_cluster.numcluster; """
        result = session.execute(sql)
        session.commit()
        session.flush()
        ret = [
            {
                "id": x[0],
                "jidmachines": x[1],
                "jidrelays": x[2],
                "numcluster": x[3],
                "directory_tmp": x[4],
            }
            for x in result
        ]
        return ret

    @DatabaseHelper._sessionm
    def get_ensemble_ars_idem_cluster(self, session, ars_id):
        sql = (
            """SELECT
                    jid, nameserver, keysyncthing
                FROM
                    xmppmaster.has_cluster_ars
                        INNER JOIN
                    xmppmaster.relayserver ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                WHERE
                    id_cluster = (SELECT
                            id_cluster
                        FROM
                            xmppmaster.has_cluster_ars
                        WHERE
                            id_ars = %s);"""
            % ars_id
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [
            {"jid": element[0], "name": element[1], "keysyncthing": element[2]}
            for element in result
        ]

    @DatabaseHelper._sessionm
    def get_list_ars_from_cluster(self, session, cluster=0):
        sql = (
            """SELECT jid, nameserver, keysyncthing  FROM xmppmaster.has_cluster_ars
                INNER JOIN
                xmppmaster.relayserver
                    ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                WHERE id_cluster = %s;"""
            % cluster
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [
            {"jid": element[0], "name": element[1], "keysyncthing": element[2]}
            for element in result
        ]

    @DatabaseHelper._sessionm
    def refresh_syncthing_deploy_clean(self, session, iddeploy):
        sql = (
            """DELETE FROM `xmppmaster`.`syncthing_deploy_group` WHERE  id= %s;"""
            % iddeploy
        )
        result = session.execute(sql)
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def get_log_status(self, session):
        """
        get complete table
        """
        result = []
        try:
            ret = session.query(Def_remote_deploy_status).all()
            session.commit()
            session.flush()
            if ret is None:
                result = []
            else:
                result = [
                    {
                        "index": id,
                        "id": rule.id,
                        "regexplog": rule.regex_logmessage,
                        "status": rule.status,
                        "label": rule.label,
                    }
                    for id, rule in enumerate(ret)
                ]
            return result
        except Exception as e:
            logger.error("\n%s" % (traceback.format_exc()))
            return result

    @DatabaseHelper._sessionm
    def updateMachinejidGuacamoleGroupdeploy(
        self, session, jid, urlguacamole, groupdeploy, idmachine
    ):
        updatedb = -1
        try:
            sql = """UPDATE machines
                    SET
                        jid = '%s', urlguacamole = '%s', groupdeploy = '%s'
                    WHERE
                        id = '%s';""" % (
                jid,
                urlguacamole,
                groupdeploy,
                idmachine,
            )
            updatedb = session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
        return updatedb

    @DatabaseHelper._sessionm
    def get_xmppmachines_list(self, session, start, limit, filter, presence):
        try:
            start = int(start)
        except BaseException:
            start = -1
        try:
            limit = int(limit)
        except BaseException:
            limit = -1

        query = (
            session.query(
                Machines.id,
                Machines.hostname,
                Machines.enabled,
                Machines.jid,
                Machines.platform,
                Machines.archi,
                Machines.classutil,
                Machines.urlguacamole,
                Machines.kiosk_presence,
                Machines.ad_ou_user,
                Machines.ad_ou_machine,
                Machines.macaddress,
                Machines.ip_xmpp,
            )
            .add_column(Cluster_ars.name.label("cluster_name"))
            .add_column(Cluster_ars.description.label("cluster_description"))
            .join(RelayServer, RelayServer.jid == Machines.groupdeploy)
            .outerjoin(Has_cluster_ars, Has_cluster_ars.id_ars == RelayServer.id)
            .outerjoin(Cluster_ars, Cluster_ars.id == Has_cluster_ars.id_cluster)
            .filter(
                and_(
                    Machines.agenttype == "machine",
                    or_(
                        Machines.uuid_inventorymachine == "",
                        Machines.uuid_inventorymachine is None,
                    ),
                )
            )
        )

        if presence == "nopresence":
            query = query.filter(Machines.enabled != 1)
        elif presence == "presence":
            query = query.filter(Machines.enabled == 1)

        if filter != "":
            query = query.filter(
                or_(
                    Machines.hostname.contains(filter),
                    Machines.platform.contains(filter),
                    Machines.jid.contains(filter),
                    Machines.archi.contains(filter),
                    Machines.hostname.contains(filter),
                    Machines.ip_xmpp.contains(filter),
                    Machines.macaddress.contains(filter),
                    Machines.classutil.contains(filter),
                    Machines.ad_ou_machine.contains(filter),
                    Machines.ad_ou_user.contains(filter),
                    Machines.kiosk_presence.contains(filter),
                    Cluster_ars.name.contains(filter),
                    Cluster_ars.description.contains(filter),
                )
            )
        count = query.count()
        if start != -1 and limit != -1:
            query = query.offset(start).limit(limit)

        query = query.all()

        result = {
            "id": [],
            "jid": [],
            "enabled": [],
            "enabled_css": [],
            "archi": [],
            "platform": [],
            "hostname": [],
            "ip_xmpp": [],
            "macaddress": [],
            "classutil": [],
            "urlguacamole": [],
            "ad_ou_machine": [],
            "ad_ou_user": [],
            "kiosk_presence": [],
            "cluster_name": [],
            "cluster_description": [],
        }
        if query is not None:
            for machine in query:
                result["id"].append(machine.id)
                result["jid"].append(machine.jid)
                if machine.enabled == 1:
                    result["enabled"].append(True)
                    result["enabled_css"].append("machineNamepresente")
                else:
                    result["enabled"].append(False)
                    result["enabled_css"].append("machineName")
                result["archi"].append(machine.archi)
                result["platform"].append(machine.platform)
                result["hostname"].append(machine.hostname)
                result["ip_xmpp"].append(machine.ip_xmpp)
                result["macaddress"].append(machine.macaddress)
                result["classutil"].append(machine.classutil)
                result["ad_ou_machine"].append(machine.ad_ou_machine)
                result["urlguacamole"].append(machine.urlguacamole)
                result["ad_ou_user"].append(machine.ad_ou_user)
                result["kiosk_presence"].append(machine.kiosk_presence)
                if machine.cluster_name is None:
                    result["cluster_name"].append("NULL")
                else:
                    result["cluster_name"].append(machine.cluster_name)
                if machine.cluster_description is None:
                    result["cluster_description"].append("NULL")
                else:
                    result["cluster_description"].append(
                        machine.cluster_description)
        return {"total": count, "datas": result}

    @DatabaseHelper._sessionm
    def get_clusters_list(self, session, start, max, filter):
        try:
            start = int(start)
        except BaseException:
            start = -1
        try:
            max = int(max)
        except BaseException:
            max = -1

        query = session.query(Cluster_ars)

        if filter != "":
            query = query.filter(
                or_(
                    Cluster_ars.name.contains(filter),
                    Cluster_ars.description.contains(filter),
                )
            )
        count = query.count()

        if start != -1 and max != -1:
            query = query.offset(start).limit(max)

        result = {
            "id": [],
            "name": [],
            "description": [],
            "nb_ars": [],
        }

        for cluster in query:
            count_ars = (
                session.query(Has_cluster_ars.id_cluster)
                .filter(Has_cluster_ars.id_cluster == cluster.id)
                .count()
            )
            result["id"].append(cluster.id)
            result["name"].append(cluster.name)
            result["description"].append(cluster.description)
            result["nb_ars"].append(count_ars if count_ars is not None else 0)

        return {"total": count, "datas": result}


    @DatabaseHelper._sessionm
    def get_xmpprelays_list(self, session, start, limit, filter, presence):
        """
        Retourne la liste des relais XMPP avec les informations machines et des compteurs agrégés.

        Optimisation :
        - Une seule requête SQL avec agrégations et GROUP BY.
        - Initialisation dynamique des listes via dict comprehension (évite d’écrire toutes les clés à la main).

        Paramètres
        ----------
        session : sqlalchemy.orm.Session
            Session SQLAlchemy.
        start : int
            Offset pagination (ou -1 si désactivé).
        limit : int
            Limite pagination (ou -1 si désactivé).
        filter : str
            Filtre texte appliqué sur plusieurs colonnes.
        presence : str
            "presence"   → enabled = 1
            "nopresence" → enabled != 1
            "all"        → aucun filtre

        Retour
        ------
        dict :
            {
                "total": <nombre total>,
                "datas": {clé -> liste de valeurs}
            }
        """

        # Clauses WHERE
        where_clauses = ["rs.moderelayserver = 'static'", "m.agenttype = 'relayserver'"]

        if presence == "nopresence":
            where_clauses.append("rs.enabled != 1")
        elif presence == "presence":
            where_clauses.append("rs.enabled = 1")

        if filter:
            filter_like = f"'%{filter}%'"
            where_clauses.append(
                f"""(
                    rs.nameserver LIKE {filter_like}
                    OR m.jid LIKE {filter_like}
                    OR c.name LIKE {filter_like}
                    OR c.description LIKE {filter_like}
                    OR rs.classutil LIKE {filter_like}
                    OR m.macaddress LIKE {filter_like}
                    OR rs.ipserver LIKE {filter_like}
                )"""
            )

        where_sql = " AND ".join(where_clauses)

        # Requête principale
        sql = f"""
            SELECT
                rs.id,
                rs.nameserver AS hostname,
                rs.ipserver   AS ip_xmpp,
                rs.jid        AS jid_from_relayserver,
                rs.classutil,
                rs.enabled,
                rs.switchonoff,
                rs.mandatory,
                m.jid,
                m.macaddress,
                c.name        AS cluster_name,
                c.description AS cluster_description,

                -- Compteurs
                COUNT(m.id) AS total_machines,
                SUM(CASE WHEN SUBSTRING(m.uuid_inventorymachine,1,1) = 'U' THEN 1 ELSE 0 END) AS inventoried,
                SUM(CASE WHEN SUBSTRING(m.uuid_inventorymachine,1,1) != 'U' THEN 1 ELSE 0 END) AS uninventoried,
                SUM(CASE WHEN SUBSTRING(m.uuid_inventorymachine,1,1) != 'U' AND m.enabled = 0 THEN 1 ELSE 0 END) AS uninventoried_offline,
                SUM(CASE WHEN SUBSTRING(m.uuid_inventorymachine,1,1) != 'U' AND m.enabled = 1 THEN 1 ELSE 0 END) AS uninventoried_online,
                SUM(CASE WHEN SUBSTRING(m.uuid_inventorymachine,1,1) = 'U' AND m.enabled = 0 THEN 1 ELSE 0 END) AS inventoried_offline,
                SUM(CASE WHEN SUBSTRING(m.uuid_inventorymachine,1,1) = 'U' AND m.enabled = 1 THEN 1 ELSE 0 END) AS inventoried_online,
                SUM(CASE WHEN m.enabled = 1 THEN 1 ELSE 0 END) AS mach_on,
                SUM(CASE WHEN m.enabled = 0 THEN 1 ELSE 0 END) AS mach_off,
                SUM(CASE WHEN m.platform REGEXP '^linux.*' THEN 1 ELSE 0 END) AS nblinuxmachine,
                SUM(CASE WHEN m.platform REGEXP '^Microsoft.*' THEN 1 ELSE 0 END) AS nbwindows,
                SUM(CASE WHEN LOCATE('darwin', m.platform) > 0 THEN 1 ELSE 0 END) AS nbdarwin,
                SUM(CASE WHEN m.archi REGEXP '^x86_64|^AMD64' THEN 1 ELSE 0 END) AS nbAMD64,
                SUM(CASE WHEN m.archi REGEXP '^ARM64' THEN 1 ELSE 0 END) AS nbARM64,
                SUM(CASE WHEN COALESCE(m.uuid_serial_machine,'') != '' THEN 1 ELSE 0 END) AS with_uuid_serial,
                SUM(CASE WHEN rs.classutil = 'both' THEN 1 ELSE 0 END) AS bothclass,
                SUM(CASE WHEN rs.classutil = 'public' THEN 1 ELSE 0 END) AS publicclass,
                SUM(CASE WHEN rs.classutil = 'private' THEN 1 ELSE 0 END) AS privateclass,
                SUM(CASE WHEN COALESCE(m.ad_ou_user,'') != '' THEN 1 ELSE 0 END) AS nb_ou_user,
                SUM(CASE WHEN COALESCE(m.ad_ou_machine,'') != '' THEN 1 ELSE 0 END) AS nb_OU_mach,
                SUM(CASE WHEN m.kiosk_presence = 'True' THEN 1 ELSE 0 END) AS kioskon,
                SUM(CASE WHEN m.kiosk_presence = 'FALSE' THEN 1 ELSE 0 END) AS kioskoff,
                SUM(CASE WHEN m.need_reconf THEN 1 ELSE 0 END) AS nbmachinereconf
            FROM relayserver rs
            LEFT JOIN has_cluster_ars hca ON hca.id_ars = rs.id
            LEFT JOIN cluster_ars c       ON c.id = hca.id_cluster
            LEFT JOIN machines m          ON m.hostname = rs.nameserver
            WHERE {where_sql}
            GROUP BY rs.id
        """

        if start != -1 and limit != -1:
            sql += f" LIMIT {limit} OFFSET {start}"

        rows = session.execute(sql).fetchall()

        # Compter le total (sans pagination)
        sql_count = f"""
            SELECT COUNT(DISTINCT rs.id)
            FROM relayserver rs
            LEFT JOIN has_cluster_ars hca ON hca.id_ars = rs.id
            LEFT JOIN machines m ON m.hostname = rs.nameserver
            LEFT JOIN cluster_ars c ON c.id = hca.id_cluster
            WHERE {where_sql}
        """
        total = session.execute(sql_count).scalar()

        # Colonnes à exporter en listes
        columns = [
            "id", "hostname", "jid", "jid_from_relayserver", "cluster_name", "cluster_description",
            "classutil", "macaddress", "ip_xmpp", "mandatory", "switchonoff", "enabled",
            "total_machines", "inventoried", "uninventoried", "uninventoried_offline",
            "uninventoried_online", "inventoried_offline", "inventoried_online", "mach_on",
            "mach_off", "nblinuxmachine", "nbwindows", "nbdarwin", "nbAMD64", "nbARM64",
            "with_uuid_serial", "bothclass", "publicclass", "privateclass", "nb_ou_user",
            "nb_OU_mach", "kioskon", "kioskoff", "nbmachinereconf"
        ]

        # Sous-ensemble des colonnes qui sont des compteurs -> doivent être forcées en int
        counters = [
            "total_machines", "inventoried", "uninventoried", "uninventoried_offline",
            "uninventoried_online", "inventoried_offline", "inventoried_online",
            "mach_on", "mach_off", "nblinuxmachine", "nbwindows", "nbdarwin",
            "nbAMD64", "nbARM64", "with_uuid_serial", "bothclass", "publicclass",
            "privateclass", "nb_ou_user", "nb_OU_mach", "kioskon", "kioskoff",
            "nbmachinereconf"
        ]
        # Init dictionnaire vide avec listes
        result = {col: [] for col in columns}
        result["enabled_css"] = []  # calculé à part

        # Remplissage
        for r in rows:
            for col in columns:
                value = getattr(r, col)
                # Eviter None → mettre "NULL" pour cluster_xxx, ou 0 pour compteurs
                if col in ["cluster_name", "cluster_description"] and value is None:
                    result[col].append("NULL")
                elif col in counters:
                    result[col].append(int(value or 0))  # <-- force int ici
                else:
                    result[col].append(value)

            # enabled_css dépend de enabled
            result["enabled_css"].append(
                "machineNamepresente" if r.enabled == 1 else "machineName"
            )

        return {"total": total, "datas": result}

    @DatabaseHelper._sessionm
    def change_relay_switch(self, session, jid, switch, propagate):
        id_cluster = None
        if propagate is True:
            session.query(RelayServer).filter(
                and_(
                    func.substring_index(
                        RelayServer.jid, "/", 1) == jid.split("/")[0],
                    RelayServer.mandatory == 0,
                )
            ).update({RelayServer.switchonoff: switch})
            try:
                cluster = (
                    session.query(Has_cluster_ars.id_cluster)
                    .join(RelayServer, Has_cluster_ars.id_ars == RelayServer.id)
                    .join(Machines, Machines.hostname == RelayServer.nameserver)
                    .filter(Machines.jid == jid)
                    .one()
                )
                id_cluster = cluster.id_cluster
            except BaseException:
                pass

        if id_cluster is not None and propagate is True:
            sql = (
                """update
    machines
set
    need_reconf = 1
where agenttype="machine" and groupdeploy in (
    select
        relayserver.jid
    from relayserver
    inner join
        has_cluster_ars
    on has_cluster_ars.id_ars = relayserver.id
    where id_cluster = %s
);"""
                % id_cluster
            )
            session.execute(sql)
        elif id_cluster is None or propagate is False:
            session.query(Machines).filter(
                Machines.agenttype == "machine", Machines.groupdeploy == jid
            ).update({Machines.need_reconf: 1})
        session.commit()
        session.flush()

    @DatabaseHelper._sessionm
    def call_reconfiguration_machine(self, session, limit=None, typemachine="machine"):
        if typemachine in ["machine", "relay"]:
            res = session.query(Machines.id, Machines.jid).filter(
                and_(
                    Machines.need_reconf == "1",
                    Machines.enabled == "1",
                    Machines.agenttype.like(typemachine),
                )
            )
        elif typemachine is None or typemachine == "all":
            res = session.query(Machines.id, Machines.jid).filter(
                and_(Machines.need_reconf == "1", Machines.enabled == "1")
            )
        if limit is not None:
            res = res.limit(int(limit))
        res = res.all()
        listjid = []
        if res is not None:
            for machine in res:
                listjid.append([machine.id, machine.jid])
        session.commit()
        session.flush()
        return listjid

    @DatabaseHelper._sessionm
    def call_acknowledged_reconficuration(self, session, listmachine=[]):
        listjid = []
        if not listmachine:
            return listjid
        res = (
            session.query(Machines.id, Machines.need_reconf)
            .filter(and_(Machines.need_reconf == "0", Machines.id.in_(listmachine)))
            .all()
        )
        if res is not None:
            for machine in res:
                listjid.append(machine.id)
        session.commit()
        session.flush()
        return listjid

    @DatabaseHelper._sessionm
    def call_set_list_machine(self, session, listmachine=[], valueset=0):
        """
        initialise presence on list id machine
        """
        if not listmachine:
            return False
        try:
            liststr = ",".join(["'%s'" % x for x in listmachine])

            sql = """UPDATE `xmppmaster`.`machines`
                    SET
                        `enabled` = '%s'
                    WHERE
                        `id` IN (%s);""" % (
                valueset,
                liststr,
            )
            session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logger.error("call_set_list_machine: %s" % str(e))
            return False

    @DatabaseHelper._sessionm
    def is_relay_online(self, session, jid):
        """Get the enable status for a specified relay
        @param: jid str
        @returns: boolean"""
        try:
            query = (
                session.query(RelayServer.enabled)
                .filter(
                    func.substring_index(
                        RelayServer.jid, "/", 1) == jid.split("/")[0]
                )
                .one()
            )
            if query is not None:
                return query.enabled
            else:
                return False
        except BaseException:
            return False

    @DatabaseHelper._sessionm
    def get_qa_for_relays(self, session, login=""):
        """Get the list of qa for relays
        @login : user's login
        @returns : list of quick actions
        """
        if login != "":
            query = (
                session.query(Qa_relay_command)
                .filter(
                    or_(
                        Qa_relay_command.user == "allusers",
                        Qa_relay_command.user == login,
                    )
                )
                .all()
            )
        else:
            query = (
                session.query(Qa_relay_command)
                .filter(Qa_relay_command.user == "allusers")
                .all()
            )

        result = []
        tmp = {"id": 0, "user": "", "namecmd": "",
               "customcmd": "", "description": ""}
        if query is not None:
            for command in query:
                result.append(
                    {
                        "id": command.id,
                        "user": command.user,
                        "script": command.script,
                        "description": command.description,
                    }
                )
        return result

    @DatabaseHelper._sessionm
    def get_relay_qa(self, session, login, qa_relay_id):
        """Get the qa by its id and its login
        @returns : the command to be run or None
        """

        try:
            query = (
                session.query(Qa_relay_command)
                .filter(
                    and_(
                        or_(
                            Qa_relay_command.user == "allusers",
                            Qa_relay_command.user == login,
                        )
                    ),
                    Qa_relay_command.id == qa_relay_id,
                )
                .one()
            )
            return {
                "id": query.id,
                "user": query.user,
                "name": query.name,
                "script": query.script,
                "description": query.description,
            }
        except BaseException:
            return None

    @DatabaseHelper._sessionm
    def get_qa_relay_result(self, session, result_id):
        result = {
            "id": 0,
            "launched_id": 0,
            "session_id": "",
            "typemessage": "log",
            "command_result": "",
            "relay": "",
        }

        query = (
            session.query(Qa_relay_result).filter(
                Qa_relay_result.id == result_id).one()
        )
        if query is not None:
            result["id"] = query.id
            result["launched_id"] = query.launched_id
            result["session_id"] = query.session_id
            result["typemessage"] = query.typemessage
            result["command_result"] = query.command_result
            result["relay"] = query.relay

        if query.command_result == "" or query.command_result is None:
            if query.session_id != "" and os.path.isfile(
                os.path.join("/", "tmp", query.session_id)
            ):
                # Try to read the tmp file
                try:
                    with open(
                        os.path.join("/", "tmp", query.session_id), "r"
                    ) as tmp_file:
                        # If some content : read it
                        content = tmp_file.read()
                        if content != "":
                            # update the result field
                            query.command_result = content
                            session.commit()
                            result["command_result"] = content
                            os.remove(os.path.join(
                                "/", "tmp", result["session_id"]))
                            tmp_file.close()

                    # do nothing if the tmp file is not readable for any
                    # reasons

                except Exception as e:
                    result["command_result"] = ""

        return result

    @DatabaseHelper._sessionm
    def add_qa_relay_launched(self, session, qa_relay_id, login, cluster_id, jid):
        format = "%Y-%m-%d %H:%M:%S"
        execution_date = datetime.now()

        qa_launched = Qa_relay_launched()

        qa_launched.id_command = qa_relay_id
        qa_launched.user_command = login
        qa_launched.command_relay = jid
        qa_launched.command_start = execution_date

        session.add(qa_launched)
        session.commit()
        session.flush()

        if qa_launched.id is None:
            qa_launched.id = 0
        if qa_launched.id_command is None:
            qa_launched.id_command = 0
        if qa_launched.user_command is None:
            qa_launched.user_command = ""
        if qa_launched.command_start is None:
            qa_launched.command_start = ""
        if qa_launched.command_cluster is None:
            qa_launched.command_cluster = ""
        if qa_launched.command_relay is None:
            qa_launched.command_relay = ""

        return {
            "id": qa_launched.id,
            "id_command": qa_launched.id_command,
            "user_command": qa_launched.user_command,
            "command_start": qa_launched.command_start.strftime(format),
            "command_cluster": qa_launched.command_cluster,
            "command_relay": qa_launched.command_relay,
        }

    @DatabaseHelper._sessionm
    def add_qa_relay_result(
        self, session, jid, exec_date, qa_relay_id, launched_id, session_id=""
    ):
        qa_result = Qa_relay_result()
        qa_result.id_command = qa_relay_id
        qa_result.launched_id = launched_id
        qa_result.session_id = session_id  # name_random(8,"quick_")
        qa_result.typemessage = "log"
        qa_result.command_result = ""
        qa_result.relay = jid

        session.add(qa_result)
        session.commit()
        session.flush()

        if qa_result.id is None:
            qa_result.id = 0
        if qa_result.id_command is None:
            qa_result.id_command = ""
        if qa_result.launched_id is None:
            qa_result.launched_id = ""
        if qa_result.session_id is None:
            qa_result.session_id = ""
        if qa_result.typemessage is None:
            qa_result.typemessage = ""
        if qa_result.command_result is None:
            qa_result.command_result = ""
        if qa_result.relay is None:
            qa_result.relay = ""

        return {
            "id": qa_result.id,
            "id_command": qa_result.id_command,
            "launched_id": qa_result.launched_id,
            "session_id": qa_result.session_id,
            "typemessage": qa_result.typemessage,
            "command_result": qa_result.command_result,
            "relay": qa_result.relay,
        }

    @DatabaseHelper._sessionm
    def get_relay_qa_launched(self, session, jid, login, start=-1, limit=-1):
        format = "%Y-%m-%d %H:%M:%S"
        try:
            start = int(start)
        except BaseException:
            start = -1

        try:
            limit = int(limit)
        except BaseException:
            limit = -1

        total = 0

        query = (
            session.query(Qa_relay_launched)
            .add_column(Qa_relay_command.name)
            .add_column(Qa_relay_command.description)
            .add_column(Qa_relay_result.id.label("id_result"))
            .filter(Qa_relay_launched.user_command == login)
            .filter(Qa_relay_launched.command_relay == jid)
            .order_by(desc(Qa_relay_launched.command_start))
            .outerjoin(
                Qa_relay_command, Qa_relay_launched.id_command == Qa_relay_command.id
            )
            .outerjoin(
                Qa_relay_result, Qa_relay_launched.id == Qa_relay_result.launched_id
            )
        )

        total = query.count()

        if start != -1:
            query = query.offset(start)

        if limit != -1:
            query = query.limit(limit)

        query = query.all()

        result = {
            "total": total,
            "datas": {
                "id": [],
                "id_command": [],
                "name": [],
                "description": [],
                "user_command": [],
                "command_start": [],
                "command_cluster": [],
                "command_relay": [],
                "result_id": [],
            },
        }
        if query is not None:
            for launched, name, description, result_id in query:
                result["datas"]["id"].append(launched.id)
                result["datas"]["id_command"].append(launched.id_command)
                result["datas"]["command_start"].append(
                    launched.command_start.strftime(format)
                )
                if launched.command_cluster is None:
                    result["datas"]["command_cluster"].append("")
                else:
                    result["datas"]["command_cluster"].append(
                        launched.command_cluster)

                result["datas"]["command_relay"].append(launched.command_relay)
                result["datas"]["user_command"].append(launched.user_command)
                result["datas"]["name"].append(name)
                result["datas"]["description"].append(description)
                if result_id is None:
                    result["datas"]["result_id"].append("")
                else:
                    result["datas"]["result_id"].append(result_id)
        return result

    @DatabaseHelper._sessionm
    def getmachinesbyuuids(self, session, uuids):
        query = (
            session.query(Machines)
            .filter(and_(Machines.uuid_inventorymachine.in_(uuids)))
            .all()
        )

        result = {}

        for machine in query:
            result[machine.uuid_inventorymachine] = {
                "id": machine.id,
                "jid": machine.jid,
                "need_reconf": machine.need_reconf,
                "enabled": machine.enabled,
                "platform": machine.platform,
                "archi": machine.archi,
                "hostname": machine.hostname,
                "uuid_inventorymachine": machine.uuid_inventorymachine,
                "id_inventorymachine": machine.uuid_inventorymachine.replace(
                    "UUID", ""
                ),
                "ippublic": machine.ippublic,
                "ip_xmpp": machine.ip_xmpp,
                "macaddress": machine.macaddress,
                "subnetxmpp": machine.subnetxmpp,
                "classutil": machine.classutil,
                "groupdeploy": machine.groupdeploy,
                "ad_ou_machine": machine.ad_ou_machine,
                "ad_ou_user": machine.ad_ou_user,
                "kiosk_presence": machine.kiosk_presence,
                "lastuser": machine.lastuser,
                "keysyncthing": machine.keysyncthing,
                "uuid_serial_machine": machine.uuid_serial_machine,
            }
        return result

    # SUBSTITUTE UPDATE TIME
    @DatabaseHelper._sessionm
    def setUptime_machine(
        self, session, hostname, jid, status=0, updowntime=0, date=None
    ):
        """
        This function allow to know the uptime of a machine
        Args:
            session: The sqlalchemy session
            hostname: The hostname of the machine
            jid: The jid of the machine
            status: The current status of the machine
                    Can be 1 or 0
                    0: The machine is offline
                    1: The machine is online
            uptime: The current uptime of the machine
        Returns:
            It returns the id of the machine
        """
        try:
            new_Uptime_machine = Uptime_machine()
            new_Uptime_machine.hostname = hostname
            new_Uptime_machine.jid = jid
            new_Uptime_machine.status = status
            new_Uptime_machine.updowntime = updowntime
            if date is not None:
                new_Uptime_machine.date = date
            session.add(new_Uptime_machine)
            session.commit()
            session.flush()
            return new_Uptime_machine.id
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def Update_version_agent_machine_md5(self, session, hostname, md5, version):
        """
        This function updates the md5 and the version of the agent in the uptime_machine
        table.
        Args:
            session: The sqlalchemy session
            hostname: The hostname of the machine
            md5: The md5 fingerprint of the agent.
            version: The version of the agent
        """
        try:
            sql = """
                UPDATE
                    `xmppmaster`.`uptime_machine`
                SET
                    `md5agentversion` = '%s',
                    `version` = '%s'
                WHERE
                    (id = (SELECT
                            id
                        FROM
                            xmppmaster.uptime_machine
                        WHERE
                            hostname LIKE '%s' AND status = 1
                        ORDER BY id DESC
                        LIMIT 1));""" % (
                md5,
                version,
                hostname,
            )
            session.execute(sql)
            session.commit()
            session.flush()
            return True
        except Exception as e:
            logger.error(
                "We failed to update the md5 and the version of the running agent for %s"
                % hostname
            )
            logger.error("we encounterd the error: %s" % str(e))
            return False

    @DatabaseHelper._sessionm
    def last_event_presence_xmpp(self, session, jid, nb=1):
        """
        This function allow to obtain the last presence.
            Args:
                session: The sqlalchemy session
                jid: The jid of the machine
                nb: Number of evenements we look at

            Returns:
                It returns a dictionnary with:
                    id: The id of the machine
                    hostname: The hostname of the machine
                    status: The current status of the machine
                        Can be 1 or 0:
                            0: The machine is offline
                            1: The machine is online
                    updowntime:
                            The uptime if status is set to 0
                            The downtime if status is set to 1
                    date: The date we checked the informations
                    time: Unix time
        """
        try:
            sql = """SELECT
                    *,
                    UNIX_TIMESTAMP(date)
                FROM
                    xmppmaster.uptime_machine
                WHERE
                    jid LIKE '%s'
                ORDER BY id DESC
                LIMIT %s;""" % (
                jid,
                nb,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            return [
                {
                    "id": element[0],
                    "hostname": element[1],
                    "jid": element[2],
                    "status": element[3],
                    "updowntime": element[4],
                    "date": element[5].strftime("%Y/%m/%d/ %H:%M:%S"),
                    "time": element[6],
                }
                for element in result
            ]
        except Exception as e:
            logger.error(str(e))
            return []

    # TODO: Add this function for hours too.
    #      Add in QA too.
    @DatabaseHelper._sessionm
    def stat_up_down_time_by_last_day(self, session, jid, day=1):
        """
        This function is used to know how long a machine is online/offline.
        It allow to know the number of start of this machine too.

        Args:
            session: The Sqlalchemy session
            jid: The jid of the machine
            day: The number of days for the count
        Returns:
            It returns a dictonary with :
                jid: The jid of the machine
                downtime: The time the machine has been down
                uptime: The time the machine has been running the agent
                nbstart: The number of start of the agent
                totaltime: The interval (in seconds) on which we count
        """

        statdict = {}
        statdict["machine"] = jid
        statdict["downtime"] = 0
        statdict["uptime"] = 0
        statdict["nbstart"] = 0
        statdict["totaltime"] = day * 86400
        try:
            sql = """SELECT
                    id, status, updowntime, date
                FROM
                    xmppmaster.uptime_machine
                WHERE
                        jid LIKE '%s'
                    AND
                        date > CURDATE() - INTERVAL %s DAY;""" % (
                jid,
                day,
            )
            result = session.execute(sql)
            session.commit()
            session.flush()
            # We set nb to false to not use the last informations
            # This would lead to errors.
            nb = False
            if result:
                for el in result:
                    if el.status == 0:
                        if statdict["nbstart"] > 0:
                            if nb:
                                statdict["uptime"] = statdict["uptime"] + el[2]
                            else:
                                nb = True
                    else:
                        statdict["nbstart"] = statdict["nbstart"] + 1
                        if nb:
                            statdict["downtime"] = statdict["downtime"] + el[2]
                        else:
                            nb = True
            return statdict
        except Exception as e:
            self.logger.error("\n%s" % (traceback.format_exc()))
            logger.error(str(e))
            return statdict

    @DatabaseHelper._sessionm
    def setMonitoring_machine(
        self, session, machines_id, hostname, statusmsg="", date=None
    ):
        try:
            new_Monitoring_machine = Mon_machine()
            new_Monitoring_machine.machines_id = machines_id
            if date is not None:
                date = date.replace("T", " ").replace("Z", "")[:19]
                new_Monitoring_machine.date = date
            new_Monitoring_machine.hostname = hostname
            new_Monitoring_machine.statusmsg = statusmsg
            session.add(new_Monitoring_machine)
            session.commit()
            session.flush()
            return new_Monitoring_machine.id
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def setMonitoring_device(
        self,
        session,
        hostname,
        mon_machine_id,
        device_type,
        serial,
        firmware,
        status,
        alarm_msg,
        doc,
    ):
        try:
            logger.debug(
                "==================================\n" "device_type [%s]" % device_type
            )
            # if device_type not in ['thermalPrinter',
            # 'nfcReader',
            # 'opticalReader',
            # 'cpu',
            # 'memory',
            # 'storage',
            # 'network',
            # 'system']:
            # raise DomaineTypeDeviceError()
            if status not in ["ready", "busy", "warning", "error", "disable"]:
                raise DomainestatusDeviceError()
            new_Monitoring_device = Mon_devices()
            new_Monitoring_device.mon_machine_id = mon_machine_id
            new_Monitoring_device.device_type = device_type
            new_Monitoring_device.serial = serial
            new_Monitoring_device.firmware = firmware
            new_Monitoring_device.status = status
            new_Monitoring_device.alarm_msg = alarm_msg
            new_Monitoring_device.doc = doc
            session.add(new_Monitoring_device)
            session.commit()
            session.flush()
            logger.debug("==================================")
            return new_Monitoring_device.id
        except Exception as e:
            logger.error(str(e))
            self.logger.error("\n%s" % (traceback.format_exc()))
            return -1

    @DatabaseHelper._sessionm
    def setMonitoring_device_reg(
        self,
        session,
        hostname,
        xmppobject,
        msg_from,
        sessionid,
        mon_machine_id,
        device_type,
        serial,
        firmware,
        status,
        alarm_msg,
        doc,
    ):
        try:
            id_device_reg = self.setMonitoring_device(
                hostname,
                mon_machine_id,
                device_type,
                serial,
                firmware,
                status,
                alarm_msg,
                doc,
            )

            # creation event on rule
            objectlist_local_rule = self._rule_monitoring(
                hostname,
                mon_machine_id,
                device_type,
                serial,
                firmware,
                status,
                alarm_msg,
                doc,
                localrule=True,
            )
            if objectlist_local_rule:
                # A rule is defined for this device on this machine
                self._action_new_event(
                    objectlist_local_rule,
                    xmppobject,
                    msg_from,
                    sessionid,
                    mon_machine_id,
                    id_device_reg,
                    doc,
                    status_event=1,
                    hostname=hostname,
                )
            else:
                # Check if there is a general rule for this device
                objectlist_local_rule = self._rule_monitoring(
                    hostname,
                    mon_machine_id,
                    device_type,
                    serial,
                    firmware,
                    status,
                    alarm_msg,
                    doc,
                    localrule=False,
                )
                if objectlist_local_rule:
                    self._action_new_event(
                        objectlist_local_rule,
                        xmppobject,
                        msg_from,
                        sessionid,
                        mon_machine_id,
                        id_device_reg,
                        doc,
                        status_event=1,
                        hostname=hostname,
                    )
            logger.debug("==================================")
            return id_device_reg
        except Exception as e:
            logger.error(str(e))
            self.logger.error("\n%s" % (traceback.format_exc()))
            return -1

    @DatabaseHelper._sessionm
    def setMonitoring_event(
        self,
        session,
        machines_id,
        id_device,
        id_rule,
        cmd,
        type_event="log",
        status_event=1,
    ):
        try:
            new_Monitoring_event = Mon_event()
            new_Monitoring_event.machines_id = machines_id
            new_Monitoring_event.id_rule = id_rule
            new_Monitoring_event.id_device = id_device
            new_Monitoring_event.type_event = type_event
            new_Monitoring_event.cmd = cmd
            session.add(new_Monitoring_event)
            session.commit()
            session.flush()
            return new_Monitoring_event.id
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def get_info_event(self, session, id_device, outformat=None):
        def is_number_string(s):
            """Returns True is string is a number."""
            try:
                float(s)
                return True
            except ValueError:
                return False

        def is_integer_string():
            if is_number_string():
                try:
                    int(s)
                    return True
                except ValueError:
                    return False
            else:
                return False

        def is_float_string():
            if is_number_string():
                try:
                    int(s)
                    return False
                except ValueError:
                    return True
            else:
                return False

        keys = [
            "mon_event_id",
            "mon_event_status_event",
            "mon_event_type_event",
            "mon_event_cmd",
            "mon_event_id_rule",
            "mon_event_machines_id",
            "mon_event_id_device",
            "mon_event_parameter_other",
            "mon_event_ack_user",
            "mon_event_ack_date",
            "mon_rules_id",
            "mon_rules_hostname",
            "mon_rules_device_type",
            "mon_rules_binding",
            "mon_rules_succes_binding_cmd",
            "mon_rules_no_success_binding_cmd",
            "mon_rules_error_on_binding",
            "mon_rules_type_event",
            "mon_rules_user",
            "mon_rules_comment",
            "mon_machine_id",
            "mon_machine_machines_id",
            "mon_machine_date",
            "mon_machine_hostname",
            "mon_machine_statusmsg",
            "mon_devices_id",
            "mon_devices_mon_machine_id",
            "mon_devices_device_type",
            "mon_devices_serial",
            "mon_devices_firmware",
            "mon_devices_status",
            "mon_devices_alarm_msg",
            "mon_devices_doc",
        ]

        sql = """
            SELECT
            mon_event.id as mon_event_id,
            mon_event.status_event as mon_event_status_event,
            mon_event.type_event as mon_event_type_event,
            mon_event.cmd as mon_event_cmd,
            mon_event.id_rule as mon_event_id_rule ,
            mon_event.machines_id as mon_event_machines_id,
            mon_event.id_device as mon_event_id_device,
            mon_event.parameter_other as mon_event_parameter_other,
            mon_event.ack_user as mon_event_ack_user,
            mon_event.ack_date as mon_event_ack_date,
            mon_rules.id as mon_rules_id ,
            mon_rules.hostname as mon_rules_hostname,
            mon_rules.device_type as mon_rules_device_type,
            mon_rules.binding as mon_rules_binding,
            mon_rules.succes_binding_cmd as mon_rules_succes_binding_cmd,
            mon_rules.no_success_binding_cmd as mon_rules_no_success_binding_cmd,
            mon_rules.error_on_binding as mon_rules_error_on_binding,
            mon_rules.type_event as mon_rules_type_event,
            mon_rules.user as mon_rules_user,
            mon_rules.comment as mon_rules_comment,
            mon_machine.id as mon_machine_id,
            mon_machine.machines_id as mon_machine_machines_id,
            mon_machine.date as mon_machine_date,
            mon_machine.hostname as mon_machine_hostname,
            mon_machine.statusmsg as mon_devices_id,
            mon_devices.id as mon_devices_id,
            mon_devices.mon_machine_id as mon_devices_mon_machine_id ,
            mon_devices.device_type as mon_devices_device_type,
            mon_devices.serial as mon_devices_serial,
            mon_devices.firmware as mon_devices_firmware,
            mon_devices.status asmon_devices_status,
            mon_devices.alarm_msg as mon_devices_alarm_msg,
            mon_devices.doc as mon_devices_doc
            FROM
                xmppmaster.mon_event
                    JOIN
                xmppmaster.mon_rules ON xmppmaster.mon_rules.id = xmppmaster.mon_event.id_rule
                    JOIN
                xmppmaster.mon_machine ON xmppmaster.mon_machine.id = xmppmaster.mon_event.machines_id
                    JOIN
                xmppmaster.mon_devices ON xmppmaster.mon_devices.id = xmppmaster.mon_event.id_device
            WHERE
                xmppmaster.mon_event.id = %s;""" % (
            id_device
        )
        result = session.execute(sql)
        session.commit()
        session.flush()
        python_dict = {}
        tupleresult = [i for i in result]
        if tupleresult:
            for count, value in enumerate(tupleresult[0]):
                tp = type(value)
                if tp == datetime or tp == datetime.time:
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                python_dict[keys[count]] = value
        if outformat is None:
            return python_dict
        # serialization for remplace in script
        if outformat == "json_string":
            return json.dumps(python_dict)
        elif outformat == "pickle_string":
            import pickle

            return pickle.dumps(python_dict)
        elif outformat == "cgi_string":
            import urllib.request
            import urllib.parse
            import urllib.error

            return urllib.parse.urlencode(python_dict)
        elif outformat == "bash_string":
            # creation string parameter for bash script.
            return self._template_bash_string_event(python_dict)
        elif outformat == "python_string":
            # creation string parameter for bash script.
            return self._template_python_string_event(python_dict)
        elif outformat == "html_string":
            # return string html format event
            return self._template_html_event(python_dict)
        else:
            return ""

    def replace_in_file_exist_template(self, srcfile, destfile, oldvalue, newvalue):
        fin = open(srcfile, "rt")
        data = fin.read()
        data = data.replace(oldvalue, newvalue)
        fin.close()
        fin = open(srcfile, "wt")
        fin.write(data)
        fin.close()

    def replace_in_file_template(self, srcfile, destfile, oldvalue, newvalue):
        fin = open(srcfile, "rt")
        fout = open(destfile, "wt")
        # for each line in the input file
        for line in fin:
            # read replace the string and write to output file
            fout.write(line.replace(oldvalue, newvalue))
        # close input and output files
        fin.close()
        fout.close()

    def _template_bash_string_event(self, python_dict):
        bash_string = ""
        for t in python_dict:
            bash_string = bash_string + "%s=%s\n" % (t, python_dict[t])
        return bash_string

    def _template_python_string_event(self, python_dict):
        # creation string parameter for bash script.
        python_string = ""
        for t in python_dict:
            valor = python_dict[t]
            if isinstance(valor, str):
                if is_number_string(valor):
                    python_string = python_string + "%s = %s \n" % (t, valor)
                else:
                    valor = python_dict[t].replace('"', '\\"')
                    python_string = python_string + '%s = "%s" \n' % (t, valor)
            else:
                python_string = python_string + "%s = %s \n" % (t, valor)
            python_string = python_string.replace('"None"', "None")
            python_string = python_string.replace('"false"', "False")
            python_string = python_string.replace('"true"', "True")
            python_string = python_string.replace('"null"', "None")
            python_string = python_string.replace('"NULL"', "None")
        return python_string

    def _template_html_event(self, dictresult):
        templateevent = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title></title>
<style type="text/css">
table {
border:3px solid #6495ed;
border-collapse:collapse;
width:90%;
margin:auto;
}
thead, tfoot {
background-color:#D0E3FA;
background-image:url(sky.jpg);
border:1px solid #6495ed;
}
tbody {
background-color:#FFFFFF;
border:1px solid #6495ed;
}
th {
font-family:monospace;
border:1px dotted #6495ed;
padding:5px;
background-color:#EFF6FF;
width:25%;
}
td {
font-family:sans-serif;
font-size:80%;
border:1px solid #6495ed;
padding:5px;
text-align:left;
}
caption {
font-family:sans-serif;
}

</style>
</head>
<body>

<h1>ALERT @mon_devices_device_type@ : e.
</h1>
<h2>MAchine @mon_machine_hostname@</h2>

<!-- DEVICE INFORMATION -->
<!-- mon_devices_mon_machine_id = @mon_devices_mon_machine_id@ -->
<!-- mon_devices_doc = @mon_devices_doc@ -->
<!-- mon_devices_status = @mon_devices_status@ -->
<!-- mon_devices_device_type = @mon_devices_device_type@ -->
<!-- mon_devices_firmware = @mon_devices_firmware@ -->
<!-- mon_devices_alarm_msg = @mon_devices_alarm_msg@ -->
<!-- mon_devices_serial = @mon_devices_serial@ -->
<!-- mon_devices_id = @mon_devices_id@ -->
<table>
  <!-- <caption>Device information</caption> -->
   <thead>
        <tr>
            <th colspan="5">DEVICE</th>
        </tr>
    </thead>
  <tbody>
    <tr>
      <th scope="col">status</th>
      <th scope="col">firmware</th>
      <th scope="col">serial</th>
      <th scope="col">alarm_msg</th>
      <th scope="col">retour</th>
    </tr>
    <tr>
      <td>@mon_devices_status@</td>
      <td>@mon_devices_firmware@</td>
      <td>@mon_devices_serial@</td>
      <td>@mon_devices_alarm_msg@</td>
      <td><code>@mon_devices_doc@</code></td>
    </tr>
  </tbody>
</table>

<!-- MACHINES INFORMATION -->
<!-- mon_machine_hostname = @mon_machine_hostname@
mon_machine_statusmsg =@mon_machine_statusmsg@
mon_machine_date = @mon_machine_date@
mon_machine_id = @mon_machine_id@
mon_machine_machines_id = @mon_machine_machines_id@ -->

<table>
  <!-- <caption>Device information</caption> -->
   <thead>
        <tr>
            <th colspan="2">MACHINE</th>
        </tr>
    </thead>
  <tbody>
    <tr>
      <th scope="col">host</th>
      <th scope="col">date</th>
    </tr>
    <tr>

      <td>@mon_machine_hostname@</td>
      <td>@mon_machine_date@</td>
    </tr>
  </tbody>
</table>

<!-- EVENT INFORMATION -->
<!-- mon_event_type_event = @mon_event_type_event@
mon_event_id = @mon_event_id@
mon_event_cmd = @mon_event_cmd@
mon_event_status_event = @mon_event_status_event@
mon_event_machines_id = @mon_event_machines_id@
mon_event_id_device = @mon_event_id_device@
mon_event_id_rule = @mon_event_id_rule@
mon_event_ack_date = @mon_event_ack_date@
mon_event_parameter_other = @mon_event_parameter_other@
mon_event_ack_user = @mon_event_ack_user@ -->

<!-- RULES INFORMATION -->
<!-- mon_rules_user = @mon_rules_user@
mon_rules_error_on_binding = @mon_rules_error_on_binding@
mon_rules_id = @mon_rules_id@
mon_rules_hostname = @mon_rules_hostname@
mon_rules_succes_binding_cmd = @mon_rules_succes_binding_cmd@
mon_rules_comment = @mon_rules_comment@
mon_rules_binding = @mon_rules_binding@
mon_rules_type_event = @mon_rules_type_event@
mon_rules_device_type = @mon_rules_device_type@
mon_rules_no_success_binding_cmd = @mon_rules_no_success_binding_cmd@ -->

<table>
  <!-- <caption>Device information</caption> -->
   <thead>
        <tr>
            <th colspan="4">RULES</th>
        </tr>
    </thead>
  <tbody>
    <tr>
      <th scope="col">Type</th>
      <th scope="col">comments</th>
      <th scope="col">BINDING</th>
    </tr>
    <tr>
      <td>@mon_rules_type_event@</td>
      <td>@mon_rules_comment@</td>
      <td><code>@mon_rules_binding@</code></td>
    </tr>
  </tbody>
</table>

</body>
</html>"""
        for t in dictresult:
            search = "@%s@" % t
            templateevent = templateevent.replace(search, str(dictresult[t]))
        return templateevent

    def _action_new_event(
        self,
        objectlist_local_rule,
        xmppobject,
        msg_from,
        sessionid,
        id_machine,
        id_device,
        doc,
        status_event=1,
        hostname=None,
    ):
        if objectlist_local_rule:
            # apply binding to find out if an alert or event is defined
            for z in objectlist_local_rule:
                self.logger.debug(
                    "event type : %s on device %s"
                    % (str(z["type_event"]), str(z["device_type"]))
                )
                bindingcmd = ""
                msg, result = self.__binding_application_check(
                    doc, z["binding"], z["device_type"]
                )
                if result == -1:
                    if (
                        z["error_on_binding"] is None
                        or z["error_on_binding"].strip() == ""
                    ):
                        # aucun trairement sur error
                        continue
                elif result == 1:
                    # alert True
                    # create event if action associated to true
                    if (
                        z["succes_binding_cmd"] is None
                        or z["succes_binding_cmd"].strip() == ""
                    ):
                        # aucun trairement sur success binding
                        continue
                    # 1 event est a prendre en compte.
                    bindingcmd = z["succes_binding_cmd"]
                elif result == 0:
                    # alert False
                    # create event if action associated to False
                    if (
                        z["no_success_binding_cmd"] is None
                        or z["no_success_binding_cmd"].strip() == ""
                    ):
                        continue
                    bindingcmd = z["no_success_binding_cmd"]
                else:
                    # cas pas encore prevu
                    self.logger.warning(
                        "No treatment on" "missing on def binding action%s " % (
                            z)
                    )
                    continue

                idevent = self.setMonitoring_event(
                    id_machine,
                    id_device,
                    z["id"],
                    bindingcmd,
                    type_event=z["type_event"],
                    status_event=1,
                )
                # traitement event
                script_monitoring = os.path.join(
                    "/", "var", "lib", "pulse2", "script_monitoring"
                )
                if not os.path.exists(script_monitoring):
                    os.makedirs(script_monitoring)
                tmpprocessmonitoring = os.path.join(
                    "/", "var", "lib", "pulse2", "tmpprocessmonitoring"
                )
                if not os.path.exists(tmpprocessmonitoring):
                    os.makedirs(tmpprocessmonitoring)
                namescript = "%s_%s_%s_%s" % (
                    id_device,
                    z["type_event"],
                    getRandomName(
                        5, pref=datetime.now().strftime("%a_%d%b%Y_%Hh%M")),
                    bindingcmd,
                )
                dest_script = os.path.join(tmpprocessmonitoring, namescript)

                if bindingcmd != "":
                    src_script = os.path.join(script_monitoring, bindingcmd)
                    if (
                        z["type_event"] == "script_python"
                        and os.path.isfile(src_script)
                        and bindingcmd.endswith("py")
                    ):
                        # on doit executer le script python
                        # le sript python doit contenir
                        # import suivant
                        # import pickle
                        # et le texte suivant pour template.
                        # serialisationpickleevent = "@@@@@event@@@@@"
                        # variable messagefrom = "@@@@@msgfrom@@@@@"
                        # le script possede toutes les donne pour pouvoir
                        # effectier 1 traitement

                        # on copy le script dans tmpprocessmonitoring le script
                        # python pour cet event.
                        serializeinformation = self.get_info_event(
                            idevent, outformat="pickle_string"
                        )

                        self.replace_in_file_template(
                            src_script,
                            dest_script,
                            "@@@@@event@@@@@",
                            serializeinformation,
                        )
                        self.replace_in_file_exist_template(
                            dest_script, dest_script, "@@@@@msgfrom@@@@@", str(
                                msg_from)
                        )
                        self.replace_in_file_exist_template(
                            dest_script,
                            dest_script,
                            "@@@@@binding@@@@@",
                            str(bindingcmd),
                        )
                        pid = subprocess.Popen(
                            ["python", dest_script],
                            stdin=None,
                            stdout=None,
                            stderr=None,
                        ).pid
                        self.logger.debug(
                            "call script python pid %s : %s " % (
                                pid, dest_script)
                        )
                        self.update_status_event(idevent)

                    elif (
                        z["type_event"] == "email"
                        and os.path.isfile(src_script)
                        and bindingcmd.endswith("py")
                    ):
                        # on doit executer le script python
                        # le sript python doit contenir la texte suivant pour template.
                        # serialisationpickleevent = "@@@@@event@@@@@"

                        # on copy le script dans tmpprocessmonitoring le script
                        # python pour cet event.
                        serializeinformation = self.get_info_event(
                            idevent, outformat="html_string"
                        )
                        self.replace_in_file_template(
                            src_script,
                            dest_script,
                            "@@@@@event@@@@@",
                            serializeinformation,
                        )
                        self.replace_in_file_exist_template(
                            dest_script,
                            dest_script,
                            "@@@@@to_addrs_string@@@@@",
                            z["user"],
                        )
                        self.replace_in_file_exist_template(
                            dest_script, dest_script, "@@@@@msgfrom@@@@@", str(
                                msg_from)
                        )
                        self.replace_in_file_exist_template(
                            dest_script,
                            dest_script,
                            "@@@@@binding@@@@@",
                            str(bindingcmd),
                        )
                        # pid =subprocess.Popen(["python", dest_script]).pid
                        pid = subprocess.Popen(
                            ["python", dest_script],
                            stdin=None,
                            stdout=None,
                            stderr=None,
                        ).pid
                        self.logger.debug(
                            "call script pid %s  : %s " % (pid, dest_script)
                        )

                    elif z["type_event"] == "json_string" and os.path.isfile(
                        src_script
                    ):
                        serializeinformation_json = ""
                        serializeinformation_json = self.get_info_event(
                            idevent, outformat="json_string"
                        )
                        self.replace_in_file_template(
                            src_script,
                            dest_script,
                            "@@@@@event@@@@@",
                            serializeinformation_json,
                        )
                        self.replace_in_file_exist_template(
                            dest_script, dest_script, "@@@@@msgfrom@@@@@", str(
                                msg_from)
                        )
                        self.replace_in_file_exist_template(
                            dest_script,
                            dest_script,
                            "@@@@@binding@@@@@",
                            str(bindingcmd),
                        )
                        os.chmod(dest_script, stat.S_IEXEC)
                        pid = subprocess.Popen(
                            dest_script, stdin=None, stdout=None, stderr=None
                        ).pid
                        self.logger.debug(
                            "call script python pid %s : %s " % (
                                pid, dest_script)
                        )
                    elif z["type_event"] == "xmppmsg":
                        # send message user a jid reception
                        # comment le json du message a envoyer
                        destinataire = ""
                        if z["user"] != "" and "@" in z["user"]:
                            # message to user
                            destinataire = z["user"]
                        elif z["user"] == "this":
                            destinataire = xmppobject.boundjid.bare
                        else:
                            destinataire = str(msg_from)
                        if destinataire != "":
                            serializeinformation = self.get_info_event(
                                idevent, outformat="pickle_string"
                            )
                            datal = pickle.loads(serializeinformation)
                            datal["mon_rules_comment"] = ""
                            serializeinformation_json = json.dumps(
                                datal, indent=4)
                            z["comment"] = z["comment"].replace(
                                "@@@@@event@@@@@", serializeinformation_json
                            )
                            z["comment"] = z["comment"].replace(
                                "@@@@@session_id@@@@@", str(sessionid)
                            )
                            z["comment"] = z["comment"].replace(
                                "@@@@@msgfrom@@@@@", str(msg_from)
                            )
                            z["comment"] = z["comment"].replace(
                                "@@@@@binding@@@@@", bindingcmd
                            )
                            # z['comment'] json message
                            xmppobject.send_message(
                                mto=str(msg_from), mbody=z["comment"], mtype="chat"
                            )
                            self.logger.debug("msg to %s" % (str(msg_from)))

    def __binding_application_check(self, datastring, bindingstring, device_type):
        resultbinding = None
        try:
            data = json.loads(datastring)
        except Exception as e:
            msg = (
                "[binding error device rule %s] : data from message"
                " monitoring format json error %s" % (device_type, str(e))
            )
            logger.error("%s" % msg)
            return (msg, -1)
        try:
            logger.debug("compile")
            code = compile(bindingstring, "<string>", "exec")
            exec(code)
        except KeyError as e:
            msg = (
                "[binding error device rule %s] : key %s in "
                "binding:\n%s\nis missing. Check your binding on data\n%s"
                % (device_type, str(e), bindingstring, json.dumps(data, indent=4))
            )
            logger.error("%s" % msg)
            return (msg, -1)
        except Exception as e:
            msg = (
                "[binding device rule %s error %s] in binding:\n%s\\ "
                "on data\n%s"
                % (device_type, str(e), bindingstring, json.dumps(data, indent=4))
            )
            logger.error("%s" % msg)
            return (msg, -1)
        msg = "[ %s : result binding %s for binding:\n%s\\ " "on data\n%s" % (
            device_type,
            resultbinding,
            bindingstring,
            json.dumps(data, indent=4),
        )
        logger.debug("%s" % msg)
        return (msg, resultbinding)

    @DatabaseHelper._sessionm
    def remise_status_event(self, session, id_rule, status_event, hostname):
        try:
            sql = """UPDATE `xmppmaster`.`mon_event`
                        JOIN
                    xmppmaster.mon_machine ON xmppmaster.mon_machine.id = xmppmaster.mon_event.machines_id
                SET
                    `xmppmaster`.`mon_event`.`status_event` = '%s'
                WHERE
                        xmppmaster.mon_machine.hostname LIKE '%s'
                    AND
                        xmppmaster.mon_event.id_rule = %s;""" % (
                status_event,
                hostname,
                id_rule,
            )

            result = session.execute(sql)
            session.commit()
            session.flush()
        except Exception as e:
            logger.error(str(e))
            return -1

    def __binding_application(self, datastring, bindingstring, device_type):
        resultbinding = None
        try:
            data = json.loads(datastring)
        except Exception as e:
            return (
                "[binding error device rule %s] : data from message"
                " monitoring format json error %s" % (device_type, str(e))
            )

        try:
            code = compile(bindingstring, "<string>", "exec")
            exec(code)
        except KeyError as e:
            resultbinding = (
                "[binding error device rule %s] : key %s in "
                "binding:\n%s\nis missing. Check your binding on data\n%s"
                % (device_type, str(e), bindingstring, json.dumps(data, indent=4))
            )
        except Exception as e:
            resultbinding = (
                "[binding device rule %s error %s] in binding:\n%s\\ "
                "on data\n%s"
                % (device_type, str(e), bindingstring, json.dumps(data, indent=4))
            )
        return resultbinding

    @DatabaseHelper._sessionm
    def getlistMonitoring_devices_type(self, session, enable=1):
        sql = """ SELECT DISTINCT
                    LOWER(device_type)
                FROM
                    xmppmaster.mon_device_service
                WHERE
                    enable = 1;"""
        result = session.execute(sql)
        session.commit()
        session.flush()
        return [i[0].lower() for i in result]

    @DatabaseHelper._sessionm
    def _rule_monitoring(
        self,
        session,
        hostname_machine,
        hostname,
        id_machine,
        platform,
        agenttype,
        mon_machine_id,
        device_type,
        serial,
        firmware,
        status,
        alarm_msg,
        doc,
        localrule=True,
    ):
        result = None
        sql = """ SELECT
                    *
                FROM
                    xmppmaster.mon_rules
                WHERE
                    enable = 1 AND
                    ('%s' REGEXP hostname or NULLIF(hostname, "") is null) AND
                    ('%s' REGEXP os or NULLIF(os, "") is null) AND
                    (type_machine like '%s' or NULLIF(type_machine, "") is Null ) AND
                    device_type LIKE '%s';""" % (
            hostname_machine,
            platform,
            agenttype,
            device_type,
        )
        # logger.debug("sql %s"%sql)
        result = session.execute(sql)
        session.commit()
        session.flush()
        if result:
            return [
                {
                    "id": i[0],
                    "hostname": i[2],
                    "device_type": i[3],
                    "binding": i[4],
                    "succes_binding_cmd": i[5],
                    "no_success_binding_cmd": i[6],
                    "error_on_binding": i[7],
                    "type_event": i[8],
                    "user": i[9],
                    "comment": i[10],
                }
                for i in result
            ]
        else:
            return []

    @DatabaseHelper._sessionm
    def analyse_mon_rules(
        self,
        session,
        mon_machine_id,
        device_type,
        serial,
        firmware,
        status,
        alarm_msg,
        doc,
    ):
        # search rule for device and machine
        pass

    @DatabaseHelper._sessionm
    def setMonitoring_panels_template(
        self,
        session,
        name_graphe,
        template_json,
        type_graphe,
        parameters="{}",
        status=True,
        comment="",
    ):
        """
        This function allows to record panel graph template
        Args:
            session: The sqlalchemy session
            name_graphe: The name of graph
            template_json: The panel template in json format
            type_graphe: The type of graph
            parameters: The optional parameters json string  { "key":"value",...}
            status: Can be True, False or None
            comment:
        Returns:
            It returns the id of the machine
        """
        try:
            new_Monitoring_panels_template = Mon_panels_template()
            new_Monitoring_panels_template.name_graphe = name_graphe
            new_Monitoring_panels_template.template_json = template_json
            new_Monitoring_panels_template.type_graphe = type_graphe
            new_Monitoring_panels_template.parameters = parameters
            new_Monitoring_panels_template.status = status
            new_Monitoring_panels_template.comment = comment
            session.add(new_Monitoring_panels_template)
            session.commit()
            session.flush()
            return new_Monitoring_panels_template.id
        except Exception as e:
            logger.error(str(e))
            return -1

    @DatabaseHelper._sessionm
    def getMonitoring_panels_template(self, session, status=True):
        """
        This function allows to get panel graph template
        Args:
            session: The sqlalchemy session
            status: The default value is True
                    Can be 1, 0 or None
                    False : list of template panels status False
                    True : list of template panels status True
                    None: list of all template panels
        Returns:
            It returns the list of template panels
        """
        try:
            list_panels_template = []
            if status:
                result_panels_template = (
                    session.query(Mon_panels_template)
                    .filter(and_(Mon_panels_template.status == 1))
                    .all()
                )
            elif status is False:
                result_panels_template = (
                    session.query(Mon_panels_template)
                    .filter(and_(Mon_panels_template.status == 0))
                    .all()
                )
            else:
                result_panels_template = session.query(
                    Mon_panels_template).all()
            session.commit()
            session.flush()
            for graphe_template in result_panels_template:
                res = {
                    "id": graphe_template.id,
                    "name_graphe": graphe_template.name_graphe,
                    "template_json": graphe_template.template_json,
                    "type_graphe": graphe_template.type_graphe,
                    "parameters": graphe_template.parameters,
                    "status": graphe_template.status,
                    "comment": graphe_template.comment,
                }
                list_panels_template.append(res)
        except Exception as e:
            logger.error(str(e))
        return list_panels_template

    @DatabaseHelper._sessionm
    def get_mon_events(self, session, start=0, max=-1, filter="", entities=[]):
        """Get monitoring events informations

        Args:
            session (SqlAlchemy session):Managed by DatabaseHelper._sessionm decorator
            start (int, optionnal): Represents the starting offset for a sql limit clause
            max (int, optionnal): Represents the number of result returned by the function
            filter (str): if not empty this string is searched into each event
            entities (list): the list of entities the user can reach
        Returns:
            dict: All the events found for the limit and filter clause. The dict has the following shape:
            result = {
                'total': 1,
                'datas' : [
                    {dict representing the event 1},
                    {dict representing the event 2},
                    ...
                ]
            }
        """

        try:
            start = int(start)
        except ValueError:
            start = -1

        try:
            max = int(max)
        except ValueError:
            max = -1

        event_types = ["log", "ack"]
        count = 0
        query = (
            session.query(Mon_event, Mon_devices,
                          Mon_rules, Mon_machine, Machines)
            .outerjoin(Mon_devices, Mon_event.id_device == Mon_devices.id)
            .outerjoin(Mon_rules, Mon_event.id_rule == Mon_rules.id)
            .outerjoin(Mon_machine, Mon_event.machines_id == Mon_machine.id)
            .outerjoin(Machines, Mon_machine.machines_id == Machines.id)
            .join(Glpi_entity, Machines.glpi_entity_id == Glpi_entity.id)
            .filter(
                and_(Mon_event.status_event == 1,
                     Mon_event.type_event.in_(event_types),
                     Glpi_entity.glpi_id.in_(entities))
            )
        )

        if filter != "":
            query = query.filter(
                or_(
                    Machines.hostname.contains(filter),
                    Machines.jid.contains(filter),
                    Mon_machine.date.contains(filter),
                    Mon_machine.statusmsg.contains(filter),
                    Mon_devices.alarm_msg.contains(filter),
                    Mon_rules.comment.contains(filter),
                    Mon_rules.device_type.contains(filter),
                    Mon_devices.firmware.contains(filter),
                    Mon_devices.serial.contains(filter),
                    Mon_devices.status.contains(filter),
                    Mon_event.type_event.contains(filter),
                )
            )

        count = query.count()
        query = query.order_by(desc(Mon_machine.date))

        if start != -1:
            query = query.offset(start)
        if max != -1:
            query = query.limit(max)

        query = query.all()

        result = {"total": count, "datas": []}
        if query:
            for event, device, rule, mon_machine, machine in query:
                tmp = {
                    "event_id": event.id,
                    "event_status": (
                        event.status_event if event.status_event is not None else ""
                    ),
                    "event_type_event": (
                        event.type_event if event.type_event is not None else ""
                    ),
                    "event_cmd": event.cmd if event.cmd is not None else "",
                    "rule_id": rule.id,
                    "rule_hostname": rule.hostname if rule.hostname is not None else "",
                    "rule_device_type": (
                        rule.device_type if rule.device_type is not None else ""
                    ),
                    "rule_binding": rule.binding if rule.binding is not None else "",
                    "rule_succes_binding_cmd": (
                        rule.succes_binding_cmd
                        if rule.succes_binding_cmd is not None
                        else ""
                    ),
                    "rule_error_on_binding": (
                        rule.error_on_binding
                        if rule.error_on_binding is not None
                        else ""
                    ),
                    "rule_user": rule.user if rule.user is not None else "",
                    "rule_comment": rule.comment if rule.comment is not None else "",
                    "mon_machine_date": (
                        mon_machine.date.strftime("%m-%d-%Y %H:%M:%S")
                        if mon_machine.date is not None
                        else ""
                    ),
                    "machine_hostname": (
                        machine.hostname if machine.hostname is not None else ""
                    ),
                    "machine_jid": machine.jid if machine.jid is not None else "",
                    "machine_enabled": (
                        machine.enabled if machine.enabled is not None else ""
                    ),
                    "machine_uuid": (
                        machine.uuid_inventorymachine
                        if machine.uuid_inventorymachine is not None
                        else ""
                    ),
                    "mon_machine_statusmsg": (
                        mon_machine.statusmsg
                        if mon_machine.statusmsg is not None
                        else ""
                    ),
                    "device_type": (
                        device.device_type if device.device_type is not None else ""
                    ),
                    "device_serial": device.serial if device.serial is not None else "",
                    "device_firmware": (
                        device.firmware if device.firmware is not None else ""
                    ),
                    "device_status": device.status if device.status is not None else "",
                    "device_alarm_msg": (
                        device.alarm_msg if device.alarm_msg is not None else ""
                    ),
                    "device_doc": device.doc if device.doc is not None else "",
                }
                result["datas"].append(tmp)
        return result

    @DatabaseHelper._sessionm
    def get_mon_events_history(self, session, start, max, filter):
        """Get monitoring events informations
        Params:
            - sqlalchemy session: managed by DatabaseHelper._sessionm decorator
            - int start: represents the starting offset for a sql limit clause
            - int max: represents the number of result returned by the function
            - string filter: if not empty this string is searched into each event
        Returns:
            dict events: The events history found for the limit and filter clause. The
            dict has the following shape:
            result = {
                'total': 1,
                'datas' : [
                    {dict representing the event 1},
                    {dict representing the event 2},
                    ...
                ]
            }
        """

        try:
            start = int(start)
        except ValueError:
            start = -1

        try:
            max = int(max)
        except ValueError:
            max = -1

        event_types = ["log", "ack"]
        count = 0
        query = (
            session.query(Mon_event, Mon_devices,
                          Mon_rules, Mon_machine, Machines)
            .outerjoin(Mon_devices, Mon_event.id_device == Mon_devices.id)
            .outerjoin(Mon_rules, Mon_event.id_rule == Mon_rules.id)
            .outerjoin(Mon_machine, Mon_event.machines_id == Mon_machine.id)
            .outerjoin(Machines, Mon_machine.machines_id == Machines.id)
            .filter(
                and_(Mon_event.status_event == 0,
                     Mon_event.type_event.in_(event_types))
            )
        )

        if filter != "":
            query = query.filter(
                or_(
                    Machines.hostname.contains(filter),
                    Machines.jid.contains(filter),
                    Mon_machine.date.contains(filter),
                    Mon_machine.statusmsg.contains(filter),
                    Mon_devices.alarm_msg.contains(filter),
                    Mon_rules.comment.contains(filter),
                    Mon_rules.device_type.contains(filter),
                    Mon_devices.firmware.contains(filter),
                    Mon_devices.serial.contains(filter),
                    Mon_devices.status.contains(filter),
                    Mon_event.type_event.contains(filter),
                    Mon_event.ack_user.contains(filter),
                    Mon_event.ack_date.contains(filter),
                )
            )

        count = query.count()
        query = query.order_by(desc(Mon_machine.date))

        if start != -1:
            query = query.offset(start)
        if max != -1:
            query = query.limit(max)

        query = query.all()

        result = {"total": count, "datas": []}
        if query:
            for event, device, rule, mon_machine, machine in query:
                tmp = {
                    "event_id": event.id,
                    "event_status": (
                        event.status_event if event.status_event is not None else ""
                    ),
                    "event_type_event": (
                        event.type_event if event.type_event is not None else ""
                    ),
                    "event_cmd": event.cmd if event.cmd is not None else "",
                    "ack_user": event.ack_user if event.ack_user is not None else "",
                    "ack_date": (
                        event.ack_date.strftime("%m-%d-%Y %H:%M:%S")
                        if event.ack_date is not None
                        else ""
                    ),
                    "rule_id": rule.id,
                    "rule_hostname": rule.hostname if rule.hostname is not None else "",
                    "rule_device_type": (
                        rule.device_type if rule.device_type is not None else ""
                    ),
                    "rule_binding": rule.binding if rule.binding is not None else "",
                    "rule_succes_binding_cmd": (
                        rule.succes_binding_cmd
                        if rule.succes_binding_cmd is not None
                        else ""
                    ),
                    "rule_error_on_binding": (
                        rule.error_on_binding
                        if rule.error_on_binding is not None
                        else ""
                    ),
                    "rule_user": rule.user if rule.user is not None else "",
                    "rule_comment": rule.comment if rule.comment is not None else "",
                    "mon_machine_date": (
                        mon_machine.date.strftime("%m-%d-%Y %H:%M:%S")
                        if mon_machine.date is not None
                        else ""
                    ),
                    "machine_hostname": (
                        machine.hostname if machine.hostname is not None else ""
                    ),
                    "machine_jid": machine.jid if machine.jid is not None else "",
                    "machine_enabled": (
                        machine.enabled if machine.enabled is not None else ""
                    ),
                    "machine_uuid": (
                        machine.uuid_inventorymachine
                        if machine.uuid_inventorymachine is not None
                        else ""
                    ),
                    "mon_machine_statusmsg": (
                        mon_machine.statusmsg
                        if mon_machine.statusmsg is not None
                        else ""
                    ),
                    "device_type": (
                        device.device_type if device.device_type is not None else ""
                    ),
                    "device_serial": device.serial if device.serial is not None else "",
                    "device_firmware": (
                        device.firmware if device.firmware is not None else ""
                    ),
                    "device_status": device.status if device.status is not None else "",
                    "device_alarm_msg": (
                        device.alarm_msg if device.alarm_msg is not None else ""
                    ),
                    "device_doc": device.doc if device.doc is not None else "",
                }
                result["datas"].append(tmp)
        return result

    @DatabaseHelper._sessionm
    def acquit_mon_event(self, session, id, user):
        """Disables the selected event specified by its id.
        params:
            - sqlalchemy session : managed by DatabaseHelper._sessionm decorator
            - int id : monitoring event id
            - string user: user name (not used yet)
        returns:
            string "success" if the modification successed or "failure" in the other case
        """
        try:
            id = int(id)
        except BaseException:
            return "failure"
        try:
            session.query(Mon_event).filter(Mon_event.id == id).update(
                {
                    Mon_event.status_event: 0,
                    Mon_event.ack_user: user,
                    Mon_event.ack_date: datetime.now(),
                }
            )
            session.commit()
            session.flush()
            return "success"
        except BaseException:
            return "failure"

    @DatabaseHelper._sessionm
    def get_count_success_rate_for_dashboard(self, session, entities=[]):
        """
        Calculate the success rate for deployments for the six last weeks socped for specified entities

        Args:
            self (XmppMasterDatabase): Instance of the model object
            session (sqlalchemy session): The sql session
            entities (list, optionnal): The list of entities to include on the scope
        Returns:
            (list) list of float corresponding to the success ratio for the six last weeks
        """

        entities = "(%s)"%(",".join([str(e) for e in entities]))

        sql = """select
  coalesce(NULL, (w1/total_w1)*100, 0) as ratio1,
  coalesce(NULL, (w2/total_w2)*100, 0) as ratio2,
  coalesce(NULL, (w3/total_w3)*100, 0) as ratio3,
  coalesce(NULL, (w4/total_w4)*100, 0) as ratio4,
  coalesce(NULL, (w5/total_w5)*100, 0) as ratio5,
  coalesce(NULL, (w6/total_w6)*100, 0) as ratio6
from(select
    coalesce(NULL, sum(case when state = "DEPLOYMENT SUCCESS" and startcmd >= (CURRENT_DATE() - INTERVAL 1 WEEK) then 1 else 0 end), 0) as w1,
    coalesce(NULL, sum(case when startcmd >= (CURRENT_DATE() - INTERVAL 1 WEEK) then 1 else 0 end), 0) as total_w1,
    coalesce(NULL, sum(case when state = "DEPLOYMENT SUCCESS" and startcmd >= (CURRENt_DATE() - INTERVAL 2 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 1 WEEK) then 1 else 0 end), 0) as w2,
    coalesce(NULL, sum(case when startcmd >= (CURRENt_DATE() - INTERVAL 2 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 1 WEEK) then 1 else 0 end), 0) as total_w2,
    coalesce(NULL, sum(case when state = "DEPLOYMENT SUCCESS" and startcmd >= (CURRENt_DATE() - INTERVAL 3 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 2 WEEK) then 1 else 0 end), 0) as w3,
    coalesce(NULL, sum(case when startcmd >= (CURRENt_DATE() - INTERVAL 3 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 2 WEEK) then 1 else 0 end), 0) as total_w3,
    coalesce(NULL, sum(case when state = "DEPLOYMENT SUCCESS" and startcmd >= (CURRENt_DATE() - INTERVAL 4 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 3 WEEK) then 1 else 0 end), 0) as w4,
    coalesce(NULL, sum(case when startcmd >= (CURRENt_DATE() - INTERVAL 4 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 3 WEEK) then 1 else 0 end), 0) as total_w4,
    coalesce(NULL, sum(case when state = "DEPLOYMENT SUCCESS" and startcmd >= (CURRENt_DATE() - INTERVAL 5 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 4 WEEK) then 1 else 0 end), 0) as w5,
    coalesce(NULL, sum(case when startcmd >= (CURRENt_DATE() - INTERVAL 5 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 4 WEEK) then 1 else 0 end), 0) as total_w5,
    coalesce(NULL, sum(case when state = "DEPLOYMENT SUCCESS" and startcmd >= (CURRENt_DATE() - INTERVAL 5 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 4 WEEK) then 1 else 0 end), 0) as w6,
    coalesce(NULL, sum(case when startcmd >= (CURRENt_DATE() - INTERVAL 5 WEEK) and startcmd < (CURRENT_DATE() - INTERVAL 4 WEEK) then 1 else 0 end), 0) as total_w6
  from deploy d
  join machines m on m.jid = d.jidmachine
  join local_glpi_filters lgf on m.uuid_inventorymachine = concat("UUID", lgf.id)
  where lgf.entities_id in %s
) as t;"""%entities
        query = session.execute(sql).first()
        if query is None :
            return [0, 0, 0, 0, 0, 0]

        # return sorted datas order by older to newer
        result = [
            query.ratio1,
            query.ratio2,
            query.ratio3,
            query.ratio4,
            query.ratio5,
            query.ratio6,
        ]
        return result

    @DatabaseHelper._sessionm
    def get_ars_from_cluster(self, session, id, filter=""):
        result = {
            "in_cluster": [],
            "out_cluster": [],
            "in_ars_list": [],
            "out_ars_list": [],
        }

        query = (
            session.query(Has_cluster_ars.id_ars, Has_cluster_ars.id_cluster)
            .add_column(RelayServer.nameserver)
            .add_column(RelayServer.jid)
            .outerjoin(RelayServer, Has_cluster_ars.id_ars == RelayServer.id)
            .filter(Has_cluster_ars.id_cluster == id)
            .all()
        )

        if query is not None:
            for id_ars, id_cluster, name, jid in query:
                result["in_cluster"].append(
                    {
                        "id_ars": id_ars,
                        "id_cluster": id_cluster,
                        "name": name,
                        "jid": jid,
                    }
                )
                result["in_ars_list"].append(id_ars)

        query2 = (
            session.query(Has_cluster_ars.id_ars, Has_cluster_ars.id_cluster)
            .add_column(RelayServer.nameserver)
            .add_column(RelayServer.jid)
            .outerjoin(RelayServer, Has_cluster_ars.id_ars == RelayServer.id)
            .filter(not_(Has_cluster_ars.id_ars.in_(result["in_ars_list"])))
            .filter(RelayServer.id)
        )

        query2 = query2.all()

        if query2 is not None:
            for id_ars, id_cluster, name, jid in query2:
                result["out_cluster"].append(
                    {
                        "id_ars": id_ars,
                        "id_cluster": id_cluster,
                        "name": name,
                        "jid": jid,
                    }
                )
                result["out_ars_list"].append(id_ars)
        return result

    @DatabaseHelper._sessionm
    def update_cluster(self, session, id, name, description, relay_ids):
        relay_ids = relay_ids.split(",")

        try:
            id = int(id)
            if name != "":
                query = (
                    session.query(Cluster_ars)
                    .filter(Cluster_ars.id == id)
                    .update(
                        {Cluster_ars.name: name, Cluster_ars.description: description}
                    )
                )
                session.commit()
                session.flush()
            else:
                query = (
                    session.query(Cluster_ars)
                    .filter(Cluster_ars == id)
                    .update({Cluster_ars.description: description})
                )
                session.commit()
                session.flush()

            query = (
                session.query(Has_cluster_ars)
                .filter(Has_cluster_ars.id_ars.in_(relay_ids))
                .update({Has_cluster_ars.id_cluster: id}, synchronize_session="fetch")
            )
            session.commit()
            session.flush()

        except Exception as err:
            return {"state": "failure", "msg": "No cluster found"}
        return {"state": "success"}

    @DatabaseHelper._sessionm
    def delete_cluster(self, session, id):
        try:
            id = int(id)

            session.query(Has_cluster_ars).filter(Has_cluster_ars.id_cluster == id).delete(
                synchronize_session="fetch"
            )

            session.query(Cluster_ars).filter(Cluster_ars.id == id).delete()

            session.commit()
            session.flush()

        except Exception as err:
            session.rollback()
            return {"state": "failure", "msg": f"Could not delete cluster: {err}"}

        return {"state": "success"}

    @DatabaseHelper._sessionm
    def create_cluster(self, session, name, description, relay_ids):
        relay_ids = relay_ids.split(",")

        try:
            if name != "":
                cluster = Cluster_ars()
                cluster.name = name
                cluster.description = description
                session.add(cluster)
                session.commit()
                session.flush()

                query = (
                    session.query(Has_cluster_ars)
                    .filter(Has_cluster_ars.id_ars.in_(relay_ids))
                    .update(
                        {Has_cluster_ars.id_cluster: cluster.id},
                        synchronize_session="fetch",
                    )
                )
                session.commit()
                session.flush()
            else:
                return {"state": "failure", "msg": "This cluster has no name"}

        except Exception as err:
            return {"state": "failure", "msg": "No cluster found"}
        return {"state": "success"}

    @DatabaseHelper._sessionm
    def get_rules_list(self, session, start, end, filter):
        try:
            start = int(start)
        except BaseException:
            start = -1

        try:
            end = int(end)
        except BaseException:
            end = -1

        result = {
            "total": 0,
            "datas": {
                "id": [],
                "name": [],
                "description": [],
                "level": [],
                "count": [],
            },
        }

        query = session.query(Regles).order_by(Regles.level)

        if filter != "":
            query = query.filter(
                or_(
                    Regles.name.contains(filter),
                    Regles.description.contains(filter),
                    Regles.level.contains(filter),
                )
            )
        count = query.count()

        if start != -1 and end != -1:
            query = query.offset(start).limit(end)

        query = query.all()
        result["total"] = count
        if query is not None:
            for rule in query:
                count_rules = (
                    session.query(Has_relayserverrules.id)
                    .filter(Has_relayserverrules.rules_id == rule.id)
                    .count()
                )

                result["datas"]["id"].append(rule.id)
                result["datas"]["name"].append(rule.name)
                result["datas"]["description"].append(rule.description)
                result["datas"]["level"].append(rule.level)
                result["datas"]["count"].append(count_rules)
        return result

    @DatabaseHelper._sessionm
    def order_relay_rule(self, session, action, id):
        try:
            id = int(id)
        except Exception as err:
            return {"status": "error", "message": "Invalid id"}
        if action not in ["raise", "down"]:
            return {"status": "error", "message": "Unknown action"}
        else:
            selected = session.query(Regles).filter(Regles.id == id).one()
            if selected is not None:
                selected_level = selected.level
                if action == "raise":
                    query = (
                        session.query(Regles)
                        .filter(Regles.level < selected.level)
                        .order_by(desc(Regles.level))
                        .first()
                    )

                    if query is None:
                        return {"status": "success", "message": "Is top level"}
                    else:
                        new_level = query.level
                else:
                    query = (
                        session.query(Regles)
                        .filter(Regles.level > selected.level)
                        .order_by(Regles.level)
                        .first()
                    )
                    if query is None:
                        return {"status": "success", "message": "Is lowest level"}
                    else:
                        new_level = query.level

                query.level, selected.level = selected.level, query.level

                session.commit()
                session.flush()
                if action == "raise":
                    return {"status": "success", "message": "raised"}
                else:
                    return {"status": "success", "message": "downed"}
            else:
                return {"status": "error", "message": "No rule found with id # %s" % id}

    @DatabaseHelper._sessionm
    def get_relay_rules(self, session, id, start, end, filter):
        try:
            start = int(start)
        except BaseException:
            start = 0
        try:
            end = int(end)
        except BaseException:
            end = -1

        result = {
            "total": 0,
            "datas": {"id": [], "subject": [], "order": [], "name": []},
            "status": "error",
            "message": "",
        }
        try:
            id = int(id)
        except Exception as err:
            result["message"] = "Bad relay Id"
            return result

        query = (
            session.query(Has_relayserverrules)
            .filter(Has_relayserverrules.relayserver_id == id)
            .add_column(Regles.name)
            .join(Regles, Regles.id == Has_relayserverrules.rules_id)
            .order_by(Has_relayserverrules.order)
        )

        if filter != "":
            query = query.filter(
                or_(
                    Has_relayserverrules.subject.contains(filter),
                    Has_relayserverrules.order.contains(filter),
                    Regles.name.contains(filter),
                )
            )

        result["total"] = query.count()

        if end != -1:
            query = query.offset(start).limit(end)
        else:
            query = query.offset(start)

        query = query.all()
        result["status"] = "success"
        if query is not None:
            for rule, name in query:
                result["datas"]["id"].append(rule.id)
                result["datas"]["subject"].append(rule.subject)
                result["datas"]["order"].append(rule.order)
                result["datas"]["name"].append(name)
            return result
        else:
            return result

    @DatabaseHelper._sessionm
    def new_rule_order_relay(self, session, id):
        query = (
            session.query(Has_relayserverrules.order)
            .filter(Has_relayserverrules.relayserver_id == id)
            .order_by(desc(Has_relayserverrules.order))
            .first()
        )

        if query is not None:
            return int(query[0]) + 1
        else:
            return 0

    @DatabaseHelper._sessionm
    def add_rule_to_relay(self, session, relay_id, rule_id, order, subject):
        has_rule = Has_relayserverrules()

        has_rule.rules_id = rule_id
        has_rule.order = order
        has_rule.subject = subject
        has_rule.relayserver_id = relay_id
        try:
            session.add(has_rule)
            session.commit()
            session.flush()
            return {"status": "success"}
        except BaseException:
            return {"status": "error"}

    @DatabaseHelper._sessionm
    def delete_rule_relay(self, session, rule_id):
        try:
            rule_id = int(rule_id)
        except BaseException:
            return {"status": "error"}
        try:
            result = (
                session.query(Has_relayserverrules)
                .filter(Has_relayserverrules.id == rule_id)
                .delete()
            )
            session.commit()
            session.flush()
            if result == 0:
                return {"status": "error", "message": "rule doesn't exist"}
            else:
                return {"status": "success"}
        except BaseException:
            return {"status": "error"}

    @DatabaseHelper._sessionm
    def move_relay_rule(self, session, relay_id, rule_id, action):
        result = {"status": None, "message": ""}

        try:
            relay_id = int(relay_id)
        except BaseException:
            result["status"] = "error"
            result["message"] = "wrong relay id"
            return result

        try:
            rule_id = int(rule_id)
        except BaseException:
            result["status"] = "error"
            result["message"] = "wrong rule id"
            return result

        # Get the selected rule
        rule = (
            session.query(Has_relayserverrules)
            .filter(Has_relayserverrules.id == rule_id)
            .one()
        )

        if rule is not None:
            if action == "raise":
                selected = (
                    session.query(Has_relayserverrules)
                    .filter(
                        and_(
                            Has_relayserverrules.rules_id == rule.rules_id,
                            Has_relayserverrules.order < rule.order,
                        )
                    )
                    .order_by(desc(Has_relayserverrules.order))
                    .first()
                )

            elif action == "down":
                selected = (
                    session.query(Has_relayserverrules)
                    .filter(
                        and_(
                            Has_relayserverrules.rules_id == rule.rules_id,
                            Has_relayserverrules.order > rule.order,
                        )
                    )
                    .order_by(Has_relayserverrules.order)
                    .first()
                )
            else:
                result["status"] = "error"
                result["message"] = "bad action"
                return result

            if selected is not None:
                selected.order, rule.order = rule.order, selected.order
                session.commit()
                session.flush()

                result["status"] = "success"
                result["message"] = "%sed" % action
            else:
                result["status"] = "success"
                result["message"] = (
                    "reached top level" if action == "raise" else "reached last level"
                )
            return result

        else:
            result["status"] = "error"
            result["message"] = "No rule found"
            return result

    @DatabaseHelper._sessionm
    def get_relay_rule(self, session, rule_id):
        result = {"status": None, "massage": ""}
        try:
            rule_id = int(rule_id)
        except BaseException:
            result["status"] = "error"
            result["message"] = "bad rule id"
            return result

        query = (
            session.query(Has_relayserverrules)
            .filter(Has_relayserverrules.id == rule_id)
            .first()
        )

        if query is not None:
            has_rule = query
            result["datas"] = {
                "id": query.id,
                "rules_id": query.rules_id,
                "order": query.order,
                "relayserver_id": query.relayserver_id,
                "subject": query.subject,
            }
            result["status"] = "success"
            result["message"] = ""
        else:
            result["status"] = "error"
            result["message"] = "no rule found"

        return result

    @DatabaseHelper._sessionm
    def get_relays_for_rule(self, session, rule_id, start, end, filter=""):
        result = {
            "status": None,
            "massage": "",
            "total": 0,
            "datas": {
                "relay_id": [],
                "hostname": [],
                "order": [],
                "subject": [],
                "id": [],
                "rule_id": [],
                "enabled": [],
            },
        }
        try:
            rule_id = int(rule_id)
        except BaseException:
            result["status"] = "error"
            result["message"] = "bad rule id"
            return result

        try:
            start = int(start)
        except BaseException:
            result["status"] = "error"
            result["message"] = "bad start offset"
            return result
        try:
            end = int(end)
        except BaseException:
            result["status"] = "error"
            result["message"] = "bad end limit"
            return result

        query = (
            session.query(Has_relayserverrules, RelayServer)
            .filter(
                and_(
                    Has_relayserverrules.rules_id == rule_id,
                    RelayServer.moderelayserver == "static",
                )
            )
            .join(RelayServer, RelayServer.id == Has_relayserverrules.relayserver_id)
        )

        if filter != "":
            query = query.filter(
                or_(
                    RelayServer.id.contains(filter),
                    RelayServer.nameserver.contains(filter),
                    Has_relayserverrules.order.contains(filter),
                    Has_relayserverrules.subject.contains(filter),
                )
            )
        count = query.count()
        query = query.order_by(RelayServer.nameserver).offset(start).limit(end)
        query = query.all()

        result["total"] = count

        if query is not None:
            for rule, relay in query:
                result["datas"]["id"].append(rule.id)
                result["datas"]["rule_id"].append(rule.rules_id)
                result["datas"]["relay_id"].append(relay.id)
                result["datas"]["hostname"].append(relay.nameserver)
                result["datas"]["enabled"].append(relay.enabled)
                result["datas"]["order"].append(rule.order)
                result["datas"]["subject"].append(rule.subject)

            result["status"] = "success"
            result["message"] = ""
        else:
            result["status"] = "error"
            result["message"] = "no rule found"

        return result

    @DatabaseHelper._sessionm
    def edit_rule_to_relay(self, session, id, relay_id, rule_id, subject):
        result = {"status": None, "message": ""}

        try:
            id = int(id)
        except BaseException:
            result["status"] = "error"
            result["message"] = "bad id"
            return result

        try:
            relay_id = int(relay_id)
        except BaseException:
            result["status"] = "error"
            result["message"] = "bad relay id"
            return result

        try:
            rule_id = int(rule_id)
        except BaseException:
            result["status"] = "error"
            result["message"] = "bad rule_id"
            return result

        query = (
            session.query(Has_relayserverrules)
            .filter(Has_relayserverrules.id == id)
            .first()
        )

        if query is None:
            result["status"] = "error"
            result["message"] = "no rule found"
        else:
            query.rules_id = rule_id
            if subject != "":
                query.subject = subject

            query.relayserver_id = relay_id

            session.commit()
            session.flush()

            result["status"] = "success"
            result["message"] = "rule edited"

        return result

    @DatabaseHelper._sessionm
    def get_minimal_relays_list(self, session, mode):
        query = session.query(RelayServer.id, RelayServer.nameserver)
        if mode in ["static", "dynamic"]:
            query = query.filter(RelayServer.moderelayserver == mode)
        else:
            query = query.filter(RelayServer.moderelayserver == "static")
        query = query.order_by(RelayServer.nameserver)
        query = query.all()

        result = {"id": [], "hostname": []}

        if query is not None:
            for id, hostname in query:
                result["id"].append(id)
                result["hostname"].append(hostname)
        return result

    @DatabaseHelper._sessionm
    def get_count_total_deploy_for_dashboard(self, session, entities=[]):
        """Get the total of deployments for each last six months
        Params:
            self (XmppMasterDatabase) : The model object instance
            session (sqlalchemy session): The session sql
            entities (list, optionnal): The list of entities to include in the scope
        Returns: list of deployments
        """

        entities = "(%s)"%(",".join([str(e) for e in entities]))

        sql = """select
  coalesce(NULL, sum(case when startcmd >= (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 6 MONTH) and startcmd < (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 5 MONTH) then 1 else 0 end), 0) as m6,
  coalesce(NULL, sum(case when startcmd >= (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 5 MONTH) and startcmd < (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 4 MONTH) then 1 else 0 end), 0) as m5,
  coalesce(NULL, sum(case when startcmd >= (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 4 MONTH) and startcmd < (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 3 MONTH) then 1 else 0 end), 0) as m4,
  coalesce(NULL, sum(case when startcmd >= (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 3 MONTH) and startcmd < (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 2 MONTH) then 1 else 0 end), 0) as m3,
  coalesce(NULL, sum(case when startcmd >= (DATE_FORMAT(CURDATE(), "%%Y-%%m-01") - INTERVAL 2 MONTH) and startcmd < (DATE_FORMAT(CURDATE(), "%%Y-%%m-01")) then 1 else 0 end), 0) as m2,
  coalesce(NULL, sum(case when startcmd >= (DATE_FORMAT(CURDATE(), "%%Y-%%m-01")) then 1 else 0 end), 0) as m1
from deploy d
join machines m on m.jid = d.jidmachine
join local_glpi_filters lgf on concat("UUID", lgf.id) = m.uuid_inventorymachine
where lgf.entities_id in %s"""%entities

        query = session.execute(sql).first()

        if query is None:
            return [0, 0, 0, 0, 0, 0]

        result = [
            query.m6,
            query.m5,
            query.m4,
            query.m3,
            query.m2,
            query.m1,
        ]
        return result

    @DatabaseHelper._sessionm
    def get_count_agent_for_dashboard(self, session, entity=[]):
        """
        Count distincts agents in activity (enabled or disabled) for the six last months.

        Args:
            self (XmppMasterDatabase) : The instance of the model object
            session (sqlalchemy session) : The session to the database
            entity (list, optionnal) : Define the entity scope we have to count
        Returns:
            (list) List of counts for the last six months, ordered by older to newer (element[0] = month 6 and element[5] = month 1)
        """
        entities = "(%s)"%(','.join([str(e) for e in entity]))
        e0 = date.today()
        b0 = e0.replace(day=1)
        e1 = b0 - timedelta(days=1)
        b1 = e1.replace(day=1)
        e2 = b1- timedelta(days=1)
        b2 = e2.replace(day=1)
        e3 = b2 - timedelta(days=1)
        b3 = e3.replace(day=1)
        e4 = b3 - timedelta(days=1)
        b4 = e4.replace(day=1)
        e5 = b4 - timedelta(days=1)
        b5 = e5.replace(day=1)
        bind = {
            "e0" : e0,
            "b0" : b0,
            "e1" : e1,
            "b1" : b1,
            "e2" : e2,
            "b2" : b2,
            "e3" : e3,
            "b3" : b3,
            "e4" : e4,
            "b4" : b4,
            "e5" : e5,
            "b5" : b5,
        }

        sql = """SELECT
    SUM(month6) AS total_month6,
    SUM(month5) AS total_month5,
    SUM(month4) AS total_month4,
    SUM(month3) AS total_month3,
    SUM(month2) AS total_month2,
    SUM(month1) AS total_month1
FROM (
    SELECT
        um.jid,
        (case when um.date >= :b0 AND um.date <= :e0 then 1 else 0 end) AS month1,
        (case when um.date >= :b1 AND um.date <= :e1 then 1 else 0 end) AS month2,
        (case when um.date >= :b2 AND um.date <= :e2 then 1 else 0 end) AS month3,
        (case when um.date >= :b3 AND um.date <= :e3 then 1 else 0 end) AS month4,
        (case when um.date >= :b4 AND um.date <= :e4 then 1 else 0 end) AS month5,
        (case when um.date >= :b5 AND um.date <= :e5 then 1 else 0 end) AS month6
    FROM uptime_machine um
    JOIN machines m ON um.jid = m.jid
    JOIN local_glpi_machines lgm on m.uuid_inventorymachine = concat("UUID", lgm.id)
    JOIN local_glpi_entities lge on lgm.entities_id = lge.id
    WHERE    m.agenttype = 'machine'
         AND lge.id IN %s
    GROUP BY um.jid
) AS t;"""%entities

        query = session.execute(sql, bind).first()
        if query is None :
            return [0, 0, 0, 0, 0, 0]

        # return sorted datas order by older to newer
        result = [
            query.total_month6,
            query.total_month5,
            query.total_month4,
            query.total_month3,
            query.total_month2,
            query.total_month1,
        ]
        return result

    @DatabaseHelper._sessionm
    def get_ars_group_in_list_clusterid(self, session, clusterid, enabled=None):
        """
        This function is used to get the list of the ars from a cluster.

        Args:
            session: the SQLAlchemy session
            clusterid: the id of the used cluster
            enabled: Tell if we used enabled ars only
                     If None we do not use enabled in the SQL request
        Returns:
            It returns informations from the ars of a cluster
            like jid, name, classutil, enabled, etc.
        """
        setsearch = clusterid
        if isinstance(clusterid, list):
            listidcluster = [x for x in set(clusterid)]
            if listidcluster:
                setsearch = ("%s" % listidcluster)[1:-1]
            else:
                raise
        searchclusterars = "(%s)" % setsearch

        sql = """SELECT
                    relayserver.id AS ars_id,
                    relayserver.urlguacamole AS urlguacamole,
                    relayserver.subnet AS subnet,
                    relayserver.nameserver AS nameserver,
                    relayserver.ipserver AS ipserver,
                    relayserver.ipconnection AS ipconnection,
                    relayserver.port AS port,
                    relayserver.portconnection AS portconnection,
                    relayserver.mask AS mask,
                    relayserver.jid AS jid,
                    relayserver.longitude AS longitude,
                    relayserver.latitude AS latitude,
                    relayserver.enabled AS enabled,
                    relayserver.mandatory AS mandatory,
                    relayserver.switchonoff AS switchonoff,
                    relayserver.classutil AS classutil,
                    relayserver.groupdeploy AS groupdeploy,
                    relayserver.package_server_ip AS package_server_ip,
                    relayserver.package_server_port AS package_server_port,
                    relayserver.moderelayserver AS moderelayserver,
                    relayserver.keysyncthing AS keysyncthing,
                    relayserver.syncthing_port AS syncthing_port,
                    has_cluster_ars.id_cluster AS id_cluster,
                    cluster_ars.name AS name_cluster
                FROM
                    xmppmaster.relayserver
                        INNER JOIN
                    xmppmaster.has_cluster_ars ON xmppmaster.has_cluster_ars.id_ars = xmppmaster.relayserver.id
                        INNER JOIN
                    xmppmaster.cluster_ars ON xmppmaster.cluster_ars.id = xmppmaster.has_cluster_ars.id_cluster
                WHERE
                    id_cluster IN %s """ % (
            searchclusterars
        )
        if enabled is not None:
            sql += """AND `relayserver`.`enabled` = %s""" % enabled
        sql += ";"
        clusterList = session.execute(sql)
        session.commit()
        session.flush()
        arsListInfos = []
        for ars in clusterList:
            arsInfos = {
                "ars_id": ars[0],
                "urlguacamole": ars[1],
                "subnet": ars[2],
                "nameserver": ars[3],
                "ipserver": ars[4],
                "ipconnection": ars[5],
                "port": ars[6],
                "portconnection": ars[7],
                "mask": ars[8],
                "jid": ars[9],
                "longitude": ars[10],
                "latitude": ars[11],
                "enabled": ars[12],
                "mandatory": ars[13],
                "switchonoff": ars[14],
                "classutil": ars[15],
                "groupdeploy": ars[16],
                "package_server_ip": ars[17],
                "package_server_port": ars[18],
                "moderelayserver": ars[19],
                "keysyncthing": ars[20],
                "syncthing_port": ars[21],
                "id_cluster": ars[22],
                "name_cluster": ars[23],
            }
            arsListInfos.append(arsInfos)
        return arsListInfos

    @DatabaseHelper._sessionm
    def get_machines_for_ban(self, session, jid_ars, start=0, end=-1, filter=""):
        try:
            start = int(start)
        except BaseException:
            start = 0

        try:
            end = int(end)
        except BaseException:
            end = -1

        subquery = (
            session.query(self.Ban_machines.jid)
            .filter(self.Ban_machines.ars_server == jid_ars)
            .subquery()
        )

        query = session.query(Machines.jid, Machines.hostname)

        if filter != "":
            query = query.filter(
                and_(
                    Machines.agenttype == "machine",
                    Machines.groupdeploy == jid_ars,
                    Machines.hostname.contains(filter),
                    not_(Machines.jid.in_(subquery)),
                )
            )

        else:
            query = query.filter(
                and_(
                    Machines.agenttype == "machine",
                    Machines.groupdeploy == jid_ars,
                    not_(Machines.jid.in_(subquery)),
                )
            )

        count = query.count()

        query = query.offset(start)
        if end > 0:
            query = query.limit(end)

        query = query.all()

        result = {"total": count, "datas": []}

        if query is not None:
            for element in query:
                result["datas"].append(
                    {"jid": element.jid, "name": element.hostname})

        return result

    @DatabaseHelper._sessionm
    def reload_deploy(
        self,
        session,
        uuid,
        cmd_id,
        gid,
        sessionid,
        hostname,
        login,
        title,
        start,
        endcmd,
        startcmd,
        force_redeploy,
        rechedule,
    ):
        connection = self.db.raw_connection()

        if cmd_id and gid and sessionid:
            logger.info(
                "user %s reload deployement %s cmd id "
                "%s on group (%s[%s]) sessionid  %s"
                % (login, title, cmd_id, hostname, gid, sessionid)
            )
            try:
                logger.info(
                    "call procedure stockee mmc_restart_deploy_sessionid( %s,%s,%s) "
                    % (sessionid, force_redeploy, rechedule)
                )
                cursor = connection.cursor()
                cursor.callproc(
                    "mmc_restart_deploy_sessionid",
                    [sessionid, force_redeploy, rechedule],
                )
                results = list(cursor.fetchall())
                cursor.close()
                connection.commit()
            finally:
                connection.close()
            return
        try:
            if not gid:
                logger.info(
                    "user %s reload deployement %s cmd id %s on mach (%s[%s])"
                    % (login, title, cmd_id, hostname, uuid)
                )
            else:
                # groupe complet a traite
                logger.info(
                    "user %s reload deployement %s cmd id %s on complet group (%s[%s])"
                    % (login, title, cmd_id, hostname, gid)
                )

            logger.info(
                "callprocedure stockee  mmc_restart_deploy_cmdid( %s,%s,%s) "
                % (cmd_id, force_redeploy, rechedule)
            )
            cursor = connection.cursor()
            cursor.callproc(
                "mmc_restart_deploy_cmdid", [cmd_id, force_redeploy, rechedule]
            )
            results = list(cursor.fetchall())
            cursor.close()
            connection.commit()
        finally:
            connection.close()

    @DatabaseHelper._sessionm
    def get_machines_to_unban(self, session, jid_ars, start=0, end=-1, filter=""):
        try:
            start = int(start)
        except BaseException:
            start = 0

        try:
            end = int(end)
        except BaseException:
            end = -1

        subquery = (
            session.query(self.Ban_machines.jid)
            .filter(self.Ban_machines.ars_server == jid_ars)
            .subquery()
        )

        query = session.query(Machines.jid, Machines.hostname)

        if filter != "":
            query = query.filter(
                and_(
                    Machines.agenttype == "machine",
                    Machines.groupdeploy == jid_ars,
                    Machines.hostname.contains(filter),
                    Machines.jid.in_(subquery),
                )
            )

        else:
            query = query.filter(
                and_(
                    Machines.agenttype == "machine",
                    Machines.groupdeploy == jid_ars,
                    Machines.jid.in_(subquery),
                )
            )

        count = query.count()

        query = query.offset(start)
        if end > 0:
            query = query.limit(end)

        query = query.all()

        result = {"total": count, "datas": []}

        if query is not None:
            for element in query:
                result["datas"].append(
                    {"jid": element.jid, "name": element.hostname})

        return result

    @DatabaseHelper._sessionm
    def ban_machines(self, session, jid_ars, machines, dates=[], reasons=[]):
        if machines != "all" or isinstance(machines, list) and "all" not in machines:
            _list = machines

        else:
            subquery = (
                session.query(self.Ban_machines.jid)
                .filter(self.Ban_machines.ars_server == jid_ars)
                .subquery()
            )

            machines_list = (
                session.query(Machines.jid)
                .filter(
                    and_(
                        Machines.groupdeploy == jid_ars,
                        Machines.agenttype == "machine",
                        not_(Machines.jid.in_(subquery)),
                    )
                )
                .all()
            )

            _list = []
            if machines_list is not None:
                _list = [element.jid for element in machines_list]

        for machine in _list:
            new_ban = self.Ban_machines()
            new_ban.jid = machine
            new_ban.ars_server = jid_ars
            try:
                session.add(new_ban)
            except BaseException:
                continue
        try:
            session.commit()
            session.flush()
        except BaseException:
            pass

        return {"jid_ars": jid_ars, "jid_machines": _list}

    @DatabaseHelper._sessionm
    def unban_machines(self, session, jid_ars, machines, dates=[], reasons=[]):
        if machines != "all" or isinstance(machines, list) and "all" not in machines:
            _list = machines

        else:
            _list = machines
        query = session.query(self.Ban_machines).filter(
            self.Ban_machines.ars_server == jid_ars
        )

        # Before deleting, we need to select machines info to send to the relay
        machines_list = query.all()
        if machines_list is not None:
            _list = [element.jid for element in machines_list]

        try:
            query.delete()
        except BaseException:
            pass
        finally:
            session.commit()
            session.flush()

        return {"jid_ars": jid_ars, "jid_machines": _list}

    # Update machine scheduling
    def __updatemachine(self, object_update_machine):
        """
        This function create a dictionnary with the informations of the
        machine that need to be updated.

        Args:
            object_update_machine: An object with the informations of the machine.
        Returns:
            A dicth with the informations of the machine.
        """
        try:
            ret = {
                "id": object_update_machine.id,
                "jid": object_update_machine.jid,
                "ars": object_update_machine.ars,
                "status": object_update_machine.status,
                "descriptor": object_update_machine.descriptor,
                "md5": object_update_machine.md5,
                "date_creation": object_update_machine.date_creation,
            }
            return ret

        except Exception as error_creating:
            logger.error(
                "We failed to retrieve the informations of the machine to update"
            )
            logger.error("We got the error \n : %s" % str(error_creating))
            return None

    @DatabaseHelper._sessionm
    def update_update_machine(
        self,
        session,
        hostname,
        jid,
        ars="",
        status="ready",
        descriptor="",
        md5="",
        date_creation=None,
    ):
        """
        We create the informations of the machines in the update SQL table
        Args:
            session: The SQL Alchemy session
            hostname: The hostname of the machine to update
            jid: The jid of the machine to update
            ars: The ARS on which the machine is connected
            status: The status of the update (ready, updating, ... )
            descriptor: All the md5sum of files that needs to be updated.
            md5: md5 of the md5 of files ( that helps to see quickly if an update is needed )
            date_creation: Date when it has been added on the update table.
        """
        try:
            query = (
                session.query(self.Update_machine)
                .filter(self.Update_machine.jid.like(jid))
                .one()
            )

            query.hostname = hostname
            query.ars = ars
            query.status = status
            query.descriptor = descriptor
            query.md5 = md5
            session.commit()
            session.flush()
            return self.__updatemachine(query)
        except Exception as e:
            logger.error(
                "We failed to update the informations on the SQL Table")
            logger.error("We got the error %s " % str(e))
            self.logger.error("We hit the backtrace \n%s" %
                              (traceback.format_exc()))
            return None

    @DatabaseHelper._sessionm
    def setUpdate_machine(
        self,
        session,
        hostname,
        jid,
        ars="",
        status="ready",
        descriptor="",
        md5="",
        date_creation=None,
    ):
        """
        We update the informations of the machines in the update SQL table
        Args:
            session: The SQL Alchemy session
            hostname: The hostname of the machine to update
            jid: The jid of the machine to update
            ars: The ARS on which the machine is connected
            status: The status of the update (ready, updating, ... )
            descriptor: All the md5sum of files that needs to be updated.
            md5: md5 of the md5 of files ( that helps to see quickly if an update is needed )
            date_creation: Date when it has been added on the update table.
        """
        try:
            new_Update_machine = self.Update_machine()
            new_Update_machine.hostname = hostname
            new_Update_machine.jid = jid
            new_Update_machine.ars = ars
            new_Update_machine.status = status
            new_Update_machine.descriptor = descriptor
            new_Update_machine.md5 = md5
            if date_creation is not None:
                new_Update_machine.date_creation = date_creation
            session.add(new_Update_machine)
            session.commit()
            session.flush()
            return self.__updatemachine(new_Update_machine)
        except IntegrityError as e:
            reason = e.message
            # self.logger.error("\n%s" % (traceback.format_exc()))
            if "Duplicate entry" in reason:
                self.logger.info("%s already in table." % e.params[0])
                return self.update_update_machine(
                    hostname, jid, ars, status, descriptor, md5
                )
            else:
                self.logger.info("setUpdate_machine : %s" % str(e))
                return None
        except Exception as e:
            logger.error(str(e))
            self.logger.error("\n%s" % (traceback.format_exc()))
            return None

    @DatabaseHelper._sessionm
    def getUpdate_machine(self, session, status="updating", nblimiti=1000):
        """
        This function is used to retrieve the machines in the pending list
        for update.

        Args:
            session: The SQL Alchemy session
            status: The status of the machine in the database ( ready, updating, ... )
            nblimit: Number maximum of machines allowed to be updated at once.
        """

        sql = """SELECT
                    MIN(id) AS minid , MAX(id) AS maxid
                FROM
                    (SELECT id
                        FROM
                            update_machine
                        WHERE
                            status LIKE '%s'
                        LIMIT %s) AS dt;""" % (
            status,
            nblimit,
        )

        machines_jid_for_updating = []
        borne = session.execute(sql)

        result = [x for x in borne][0]
        minid = result[0]
        maxid = result[0]
        if minid is not None:
            sql = """ SELECT
                        jid, ars
                    FROM
                        update_machine
                    WHERE
                        id >= %s and id <= %s and
                            status LIKE '%s';""" % (
                minid,
                maxid,
                status,
            )
            resultquery = session.execute(sql)

            for record_updating_machine in resultquery:
                machines_jid_for_updating.append(
                    (
                        record_updating_machine.jid,
                        record_updating_machine.ars,
                    )
                )
            sql = """ delete

                    FROM
                        update_machine
                    WHERE
                        id >= %s and id <= %s and
                            status LIKE '%s';""" % (
                minid,
                maxid,
                status,
            )
            resultquery = session.execute(sql)

            session.commit()
            session.flush()
        return machines_jid_for_updating

    @DatabaseHelper._sessionm
    def get_update_by_entity(self, session):
        """
        This function returns the total number of updates to apply for each entity
        """
        sql = """SELECT
                    glpi_entity.glpi_id AS entity,
                    COUNT(DISTINCT(xmppmaster.machines.id)) AS total_machine_entity,
                    SUM(CASE
                        WHEN (COALESCE(update_id, '') != '') THEN 1
                        ELSE 0
                    END) AS update_a_mettre_a_jour
                FROM
                    xmppmaster.machines
                        JOIN
                    glpi_entity ON machines.glpi_entity_id = glpi_entity.id
                        LEFT JOIN
                    xmppmaster.up_machine_windows ON xmppmaster.machines.id = xmppmaster.up_machine_windows.id_machine
                WHERE
                    platform LIKE 'Mic%'
                GROUP BY glpi_entity.glpi_id;"""
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        result = [rowproxy._asdict() for rowproxy in resultquery]
        return result

    @DatabaseHelper._sessionm
    def get_machine_by_entity_in_grayandwhite_lists(self, session):
        """
        This function returns the machines to update in an entity considering only the updates enabled in gray list
        """
        sql = """SELECT
                    glpi_entity.glpi_id AS entity,
                    COUNT(DISTINCT(xmppmaster.machines.id)) AS machine_a_mettre_a_jour,
                    SUM(CASE
                        WHEN (COALESCE(update_id, '') != '') THEN 1
                        ELSE 0
                    END) AS update_a_mettre_a_jour
                FROM
                    xmppmaster.machines
                        JOIN
                    glpi_entity ON machines.glpi_entity_id = glpi_entity.id
                        LEFT JOIN
                    xmppmaster.up_machine_windows ON xmppmaster.machines.id = xmppmaster.up_machine_windows.id_machine
                        LEFT JOIN
                    xmppmaster.up_gray_list ON xmppmaster.up_gray_list.updateid = xmppmaster.up_machine_windows.update_id
                        LEFT JOIN
                    xmppmaster.up_white_list ON xmppmaster.up_white_list.updateid = xmppmaster.up_machine_windows.update_id
                WHERE
                    platform LIKE 'Mic%'
                        AND (xmppmaster.up_gray_list.valided = 1 or xmppmaster.up_white_list.valided = 1)
                        AND xmppmaster.up_machine_windows.curent_deploy is NULL AND xmppmaster.up_machine_windows.required_deploy is NULL
                GROUP BY glpi_entity.glpi_id;"""
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        result = [rowproxy._asdict() for rowproxy in resultquery]
        return result

    @DatabaseHelper._sessionm
    def get_conformity_update_by_entity(self, session, entities: list = [], config=None):
        """
        Récupère les statistiques de conformité des mises à jour Windows par entité (version SQL optimisée).

        Cette fonction consolide les informations de conformité des machines Windows
        au niveau de chaque entité GLPI, en ne considérant que les mises à jour
        activées dans la "gray list" (ou "white list") et validées.

        Elle repose sur une seule requête SQL optimisée qui regroupe et agrège
        les données nécessaires, au lieu d’exécuter plusieurs requêtes séparées.
        Les résultats permettent d’obtenir une vue globale de la conformité par entité.

        ────────────────────────────────────────────────────────────────
        ⚙️ PRINCIPE GÉNÉRAL
        ----------------------------------------------------------------
        Pour chaque entité GLPI spécifiée :
        - On recense le nombre total de machines Windows.
        - On identifie les machines non conformes (présentes dans la vue `up_machine_activated`).
        - On compte le nombre total de mises à jour manquantes associées à ces machines.

        Ces informations sont extraites en une seule passe SQL via des agrégations
        et jointures conditionnelles entre les tables principales :
        - `machines` : contient les informations de base sur les ordinateurs.
        - `glpi_entity` : associe chaque machine à son entité GLPI.
        - `up_machine_activated` : vue recensant les mises à jour activées
            (et validées) sur les machines.
        - `local_glpi_filters` : permet d’appliquer des filtres supplémentaires
            selon l’état ou le type des machines.

        ────────────────────────────────────────────────────────────────
        🧩 PHASES INTERNES DE TRAITEMENT
        ----------------------------------------------------------------
        1️⃣ **Préparation des filtres dynamiques**
            - Si un objet `config` est fourni avec un attribut `filter_on`,
            les filtres suivants peuvent être appliqués :
                - `"entity"` : restreint la requête à certaines entités GLPI.
                - `"state"`  : filtre selon les états des machines (via `local_glpi_filters`).
                - `"type"`   : filtre selon les types d’ordinateurs.
            - Ces filtres sont traduits en clauses SQL `AND ... IN (...)`
            et insérés dans la requête finale.

        2️⃣ **Filtrage des machines Windows**
            - Seules les machines dont `platform` commence par `'Microsoft Windows'`
            sont incluses (`m.platform LIKE 'Microsoft Windows%'`).
            - Les machines doivent également avoir `m.agenttype = 'machine'`.

        3️⃣ **Agrégation SQL unifiée**
            - La requête principale regroupe les informations par entité (`ge.glpi_id`).
            - Elle calcule :
                - `totalmach`   → nombre total de machines Windows par entité.
                - `nbmachines`  → nombre de machines non conformes (ayant des mises à jour manquantes).
                - `nbupdates`   → nombre total de mises à jour distinctes manquantes.
            - Les jointures avec `up_machine_activated` et `local_glpi_filters`
            permettent d’isoler les machines non conformes et d’appliquer les filtres optionnels.

        4️⃣ **Restitution des résultats**
            - Les données agrégées sont retournées sous forme d’une liste de dictionnaires Python :
                [
                    {
                        "entity": "<ID de l'entité>",
                        "nbmachines": <nombre de machines non conformes>,
                        "nbupdates": <nombre de mises à jour manquantes>,
                        "totalmach": <nombre total de machines Windows>,
                    },
                    ...
                ]
            - Les entités sans non-conformité retournent `0` pour `nbmachines` et `nbupdates`.

        ────────────────────────────────────────────────────────────────
        ⚙️ PARAMÈTRES
        ----------------------------------------------------------------
        Args:
            session (Session):
                Session SQLAlchemy active, fournie par le décorateur `@DatabaseHelper._sessionm`.

            entities (list[int]):
                Liste des identifiants d’entités GLPI à analyser.
                Si vide, la requête ne retournera aucun résultat.

            config (object, optionnel):
                Objet de configuration facultatif pouvant contenir un attribut `filter_on`
                sous forme de dictionnaire :
                    {
                        "entity": [id1, id2, ...],
                        "state": [id_state1, id_state2, ...],
                        "type": [id_type1, id_type2, ...]
                    }
                Ces filtres s’appliquent respectivement aux entités GLPI,
                aux états des machines et aux types d’ordinateurs.

        ────────────────────────────────────────────────────────────────
        📤 RETOUR
        ----------------------------------------------------------------
        Returns:
            list[dict]:
                Liste de dictionnaires contenant les statistiques de conformité
                pour chaque entité analysée :
                - `entity` (str) : Identifiant de l’entité GLPI.
                - `nbmachines` (int) : Nombre de machines Windows non conformes.
                - `nbupdates` (int) : Nombre total de mises à jour manquantes.
                - `totalmach` (int) : Nombre total de machines Windows enregistrées.

        ────────────────────────────────────────────────────────────────
        🧠 NOTES TECHNIQUES
        ----------------------------------------------------------------
        - Cette version réduit considérablement le nombre de requêtes SQL
        (une seule au lieu de trois) et améliore les performances globales.
        - Toutes les agrégations sont réalisées côté SQL, limitant les traitements Python.
        - Les données de non-conformité proviennent de la vue `up_machine_activated`,
        qui recense les mises à jour validées dans les listes grise et blanche.
        - Les filtres dynamiques peuvent être combinés sans modifier la logique de base.
        """

        # Construction dynamique des filtres
        filter_sql = []
        filter_noncompliant_sql = []

        if config is not None and getattr(config, "filter_on", None) is not None:
            for key, values in config.filter_on.items():
                if not values:
                    continue
                if key == "entity":
                    filter_sql.append(f"ge.glpi_id IN ({','.join(map(str, values))})")
                elif key == "state":
                    filter_noncompliant_sql.append(f"lgf.states_id IN ({','.join(map(str, values))})")
                elif key == "type":
                    filter_noncompliant_sql.append(f"lgf.computertypes_id IN ({','.join(map(str, values))})")

        # Clause WHERE commune
        where_conditions = [
            "m.agenttype = 'machine'",
            "m.platform LIKE 'Microsoft Windows%'",
        ]
        if entities:
            where_conditions.append(f"ge.glpi_id IN ({','.join(map(str, entities))})")
        if filter_sql:
            where_conditions.extend(filter_sql)

        # Clause WHERE spécifique non-conformité
        where_noncompliant = ""
        if filter_noncompliant_sql:
            where_noncompliant = " AND " + " AND ".join(filter_noncompliant_sql)

        # Requête SQL unifiée
        sql = f"""
            SELECT
                ge.glpi_id AS entity_id,
                COUNT(DISTINCT m.id) AS totalmach,
                COUNT(DISTINCT uma.id_machine) AS nbmachines,
                COUNT(DISTINCT uma.update_id) AS nbupdates
            FROM
                machines m
                JOIN glpi_entity ge ON ge.id = m.glpi_entity_id
                LEFT JOIN up_machine_activated uma
                    ON uma.id_machine = m.id
                LEFT JOIN local_glpi_filters lgf
                    ON lgf.id = uma.glpi_id
            WHERE
                {' AND '.join(where_conditions)}
                {where_noncompliant}
            GROUP BY
                ge.glpi_id
            ORDER BY
                ge.glpi_id;
        """

        logger.debug("SQL conformité Windows : %s", sql)

        result = []
        for row in session.execute(sql):
            result.append({
                "entity": str(row.entity_id),
                "nbmachines": row.nbmachines or 0,
                "nbupdates": row.nbupdates or 0,
                "totalmach": row.totalmach or 0,
            })

        return result

    # @DatabaseHelper._sessionm
    # def get_conformity_update_by_entity(self, session, entities: list = [], config=None):
    #     """
    #     Récupère les statistiques de conformité des mises à jour Windows par entité.
    #
    #     Cette fonction analyse la conformité des machines Windows gérées par entité GLPI.
    #     Elle regroupe et corrèle plusieurs ensembles de données SQL pour déterminer :
    #         - le nombre total de machines Windows par entité,
    #         - le nombre de machines non conformes (celles avec des mises à jour manquantes),
    #         - le nombre total de mises à jour manquantes,
    #     en ne considérant **que** les mises à jour activées dans la *gray list*.
    #
    #     La fonction s’appuie sur plusieurs requêtes SQL exécutées successivement :
    #
    #     ────────────────────────────────────────────────────────────────
    #     🧩 PHASE 1 — Récupération des machines Windows par entité
    #     ----------------------------------------------------------------
    #     - Interroge la table `machines` (jointure avec `glpi_entity`) pour obtenir
    #     la liste des machines actives dont le champ `platform` commence par
    #     `"Microsoft Windows"`.
    #     - Les filtres éventuels passés via `config.filter_on` sont appliqués
    #     (par entité, état ou type).
    #     - Les machines sont ensuite regroupées par identifiant d’entité
    #     dans un dictionnaire Python (`machine_by_entity`).
    #
    #     ────────────────────────────────────────────────────────────────
    #     🧩 PHASE 2 — Comptage global des machines Windows par entité
    #     ----------------------------------------------------------------
    #     - Exécute une requête d’agrégation SQL pour compter le nombre total
    #     de machines Windows par entité (`total_machines`).
    #     - Cette étape garantit que le nombre total de machines est calculé
    #     même si certaines ne figurent pas dans les listes de non-conformité.
    #
    #     ────────────────────────────────────────────────────────────────
    #     🧩 PHASE 3 — Analyse de la non-conformité
    #     ----------------------------------------------------------------
    #     - Interroge la vue `up_machine_activated`, déjà filtrée pour ne contenir
    #     que des machines Windows (via la clause `m.platform LIKE 'Microsoft Windows%'`).
    #     - Calcule, pour chaque entité, le nombre de machines distinctes non conformes
    #     (`noncompliant`) et le nombre de mises à jour distinctes manquantes (`missing`).
    #     - Les filtres `state` ou `type` provenant de `config.filter_on`
    #     sont appliqués à cette étape.
    #
    #     ────────────────────────────────────────────────────────────────
    #     🧩 PHASE 4 — Agrégation et restitution
    #     ----------------------------------------------------------------
    #     - Combine les résultats des trois étapes précédentes pour construire
    #     une liste de dictionnaires structurés contenant, pour chaque entité :
    #         {
    #             "entity": <ID de l'entité>,
    #             "nbmachines": <nombre de machines non conformes>,
    #             "nbupdates": <nombre total de mises à jour manquantes>,
    #             "totalmach": <nombre total de machines Windows>,
    #         }
    #     - Si une entité ne présente aucune non-conformité, les valeurs par défaut
    #     sont `0` pour `nbmachines` et `nbupdates`.
    #
    #     ────────────────────────────────────────────────────────────────
    #     ⚙️ PARAMÈTRES
    #     ----------------------------------------------------------------
    #     Args:
    #         session (Session):
    #             Session SQLAlchemy active, fournie par le décorateur `@DatabaseHelper._sessionm`.
    #         entities (list[int]):
    #             Liste des identifiants d’entités GLPI à analyser.
    #         config (object, optionnel):
    #             Objet de configuration optionnel pouvant contenir un attribut `filter_on`
    #             (dictionnaire de filtres supplémentaires) :
    #             - "entity" : liste des IDs d'entités à inclure
    #             - "state"  : liste des IDs d'états de machines
    #             - "type"   : liste des IDs de types d’ordinateurs
    #
    #     ────────────────────────────────────────────────────────────────
    #     📤 RETOUR
    #     ----------------------------------------------------------------
    #     Returns:
    #         list[dict]:
    #             Liste de dictionnaires contenant les statistiques de conformité
    #             par entité, avec les clés suivantes :
    #             - `entity` (str) : Identifiant de l'entité GLPI.
    #             - `nbmachines` (int) : Nombre de machines Windows non conformes.
    #             - `nbupdates` (int) : Nombre total de mises à jour manquantes.
    #             - `totalmach` (int) : Nombre total de machines Windows recensées.
    #
    #     ────────────────────────────────────────────────────────────────
    #     🧠 NOTES
    #     ----------------------------------------------------------------
    #     - Seules les machines dont `platform` commence par "Microsoft Windows"
    #     sont prises en compte dans toutes les phases.
    #     - Les données de non-conformité reposent sur la vue SQL `up_machine_activated`,
    #     déjà filtrée sur les machines Windows et les mises à jour validées
    #     (dans la *gray* ou *white list*).
    #     - L’objectif est d’obtenir une vue consolidée de la conformité des
    #     mises à jour Windows par entité, tout en respectant les filtres GLPI.
    # """
    #
    #     # Initialisation des filtres SQL
    #     filter_on = ""
    #     filter_on_noncompliant = ""
    #
    #     # Application des filtres depuis la configuration (si fournie)
    #     if config is not None and getattr(config, "filter_on", None) is not None:
    #         for key in config.filter_on:
    #             if key not in ["entity", "state", "type"]:
    #                 continue
    #
    #             if key == "entity":
    #                 column = "ge.glpi_id"
    #                 filter_on += f" AND {column} IN ({','.join(map(str, config.filter_on[key]))})"
    #             elif key == "state":
    #                 column = "lgf.states_id"
    #                 filter_on_noncompliant += f" AND {column} IN ({','.join(map(str, config.filter_on[key]))})"
    #             elif key == "type":
    #                 column = "lgf.computertypes_id"
    #                 filter_on_noncompliant += f" AND {column} IN ({','.join(map(str, config.filter_on[key]))})"
    #
    #     # ─────────────────────────────────────────────
    #     # 1️⃣ Récupération de la liste des machines Windows par entité
    #     # ─────────────────────────────────────────────
    #     sql_machine_details = f"""
    #         SELECT
    #             m.id AS machine_id,
    #             m.hostname,
    #             ge.glpi_id AS entity_id
    #         FROM
    #             machines m
    #             JOIN glpi_entity ge ON m.glpi_entity_id = ge.id
    #         WHERE
    #             m.agenttype = 'machine'
    #             AND m.platform LIKE 'Microsoft Windows%'
    #             {filter_on};
    #     """
    #     machine_details = session.execute(sql_machine_details).fetchall()
    #
    #     # Organisation des machines par entité
    #     machine_by_entity = {}
    #     for row in machine_details:
    #         entity_id = row.entity_id
    #         machine_by_entity.setdefault(entity_id, []).append({
    #             "id": row.machine_id,
    #             "hostname": row.hostname,
    #             "valid": row.machine_id != 0,
    #         })
    #     logger.debug("Machines Windows par entité [%s]" % (machine_by_entity))
    #
    #     # ─────────────────────────────────────────────
    #     # 2️⃣ Total de machines Windows par entité
    #     # ─────────────────────────────────────────────
    #     sql_total_machines = f"""
    #         SELECT
    #             ge.glpi_id AS id,
    #             COUNT(m.hostname) AS totalmach
    #         FROM
    #             machines m
    #             JOIN glpi_entity ge ON m.glpi_entity_id = ge.id
    #         WHERE
    #             m.agenttype = 'machine'
    #             AND m.platform LIKE 'Microsoft Windows%'
    #             {filter_on}
    #         GROUP BY
    #             ge.glpi_id;
    #     """
    #     total_machines = {
    #         row.id: row.totalmach for row in session.execute(sql_total_machines)
    #     }
    #     logger.debug("Total machines Windows par entité [%s]" % (total_machines))
    #
    #     # ─────────────────────────────────────────────
    #     # 3️⃣ Données de non-conformité (vue filtrée Windows)
    #     # ─────────────────────────────────────────────
    #     sql_noncompliant = f"""
    #         SELECT
    #             uma.entities_id AS id,
    #             COUNT(DISTINCT uma.id_machine) AS noncompliant,
    #             COUNT(DISTINCT uma.update_id) AS missing
    #         FROM
    #             up_machine_activated uma
    #             JOIN local_glpi_filters lgf ON lgf.id = uma.glpi_id
    #         WHERE
    #             uma.entities_id IN ({",".join(map(str, entities))})
    #             {filter_on_noncompliant}
    #         GROUP BY
    #             uma.entities_id;
    #     """
    #     noncompliant_data = {
    #         row.id: (row.noncompliant, row.missing)
    #         for row in session.execute(sql_noncompliant)
    #     }
    #
    #     # ─────────────────────────────────────────────
    #     # 4️⃣ Construction du résultat final
    #     # ─────────────────────────────────────────────
    #     result = []
    #     for entity_id in entities:
    #         entity_id = int(entity_id)
    #
    #         machines = machine_by_entity.get(entity_id, [])
    #         noncompliant, missing = noncompliant_data.get(entity_id, (0, 0))
    #         total = total_machines.get(entity_id, len(machines))
    #
    #         result.append({
    #             "entity": str(entity_id),
    #             "nbmachines": noncompliant,
    #             "nbupdates": missing,
    #             "totalmach": total,
    #         })
    #
    #     return result



    #
    # @DatabaseHelper._sessionm
    # def get_conformity_update_by_entity(self, session, entities: list = [], config=None):
    #     """
    #     Récupère les statistiques de conformité des mises à jour par entité.
    #
    #     Cette fonction calcule, pour chaque entité spécifiée, le nombre total de machines,
    #     le nombre de machines non conformes (ayant des mises à jour manquantes)
    #     et le nombre total de mises à jour concernées, en se basant uniquement sur les
    #     mises à jour activées dans la "gray list".
    #
    #     Args:
    #         session (Session): Session SQLAlchemy active.
    #         entities (list): Liste des ID d'entités à analyser.
    #         config (object, optional): Objet de configuration contenant éventuellement
    #             un attribut `filter_on`, dictionnaire de filtres possibles :
    #             - "entity" : liste des IDs d'entités à inclure
    #             - "state" : liste des IDs d'états des machines
    #             - "type" : liste des IDs de types d’ordinateurs
    #
    #     Returns:
    #         list[dict]: Liste de dictionnaires contenant pour chaque entité :
    #             - entity (str): ID de l'entité
    #             - nbmachines (int): Nombre de machines non conformes
    #             - nbupdates (int): Nombre de mises à jour manquantes
    #             - totalmach (int): Nombre total de machines dans l'entité
    #     """
    #
    #     # Initialisation des filtres SQL
    #     filter_on = ""
    #     filter_on_noncompliant = ""
    #
    #     # Application des filtres depuis la configuration (si fournie)
    #     if config is not None and getattr(config, "filter_on", None) is not None:
    #         for key in config.filter_on:
    #             if key not in ["entity", "state", "type"]:
    #                 continue
    #
    #             if key == "entity":
    #                 column = "ge.glpi_id"
    #                 filter_on += f" AND {column} IN ({','.join(map(str, config.filter_on[key]))})"
    #             elif key == "state":
    #                 column = "lgf.states_id"
    #                 filter_on_noncompliant += f" AND {column} IN ({','.join(map(str, config.filter_on[key]))})"
    #             elif key == "type":
    #                 column = "lgf.computertypes_id"
    #                 filter_on_noncompliant += f" AND {column} IN ({','.join(map(str, config.filter_on[key]))})"
    #
    #     # ─────────────────────────────────────────────
    #     # 1️⃣  Récupération de la liste des machines par entité
    #     # ─────────────────────────────────────────────
    #     sql_machine_details = f"""
    #         SELECT
    #             m.id AS machine_id,
    #             m.hostname,
    #             ge.glpi_id AS entity_id
    #         FROM
    #             machines m
    #             JOIN glpi_entity ge ON m.glpi_entity_id = ge.id
    #         WHERE
    #             m.agenttype = 'machine'
    #             {filter_on};
    #     """
    #     machine_details = session.execute(sql_machine_details).fetchall()
    #
    #     # Organisation des machines par entité
    #     machine_by_entity = {}
    #     for row in machine_details:
    #         entity_id = row.entity_id
    #         machine_by_entity.setdefault(entity_id, []).append({
    #             "id": row.machine_id,
    #             "hostname": row.hostname,
    #             "valid": row.machine_id != 0,
    #         })
    #     logger.debug("Récupération de la liste des machines par entité [%s] " % (machine_by_entity))
    #     # ─────────────────────────────────────────────
    #     # 2️⃣  Récupération du total de machines par entité
    #     # ─────────────────────────────────────────────
    #     sql_total_machines = f"""
    #         SELECT
    #             ge.glpi_id AS id,
    #             COUNT(m.hostname) AS totalmach
    #         FROM
    #             machines m
    #             JOIN glpi_entity ge ON m.glpi_entity_id = ge.id
    #         WHERE
    #             m.agenttype = 'machine'
    #             {filter_on}
    #         GROUP BY
    #             ge.glpi_id;
    #     """
    #     total_machines = {
    #         row.id: row.totalmach for row in session.execute(sql_total_machines)
    #     }
    #     logger.debug("Récupération du total de machines par entité [%s] " % (total_machines))
    #     # ─────────────────────────────────────────────
    #     # 3️⃣  Récupération des données de non-conformité
    #     # ─────────────────────────────────────────────
    #     sql_noncompliant = f"""
    #         SELECT
    #             uma.entities_id AS id,
    #             COUNT(DISTINCT uma.id_machine) AS noncompliant,
    #             COUNT(DISTINCT uma.update_id) AS missing
    #         FROM
    #             up_machine_activated uma
    #             JOIN local_glpi_filters lgf ON lgf.id = uma.glpi_id
    #         WHERE
    #             uma.entities_id IN ({",".join(map(str, entities))})
    #             {filter_on_noncompliant}
    #         GROUP BY
    #             uma.entities_id;
    #     """
    #     noncompliant_data = {
    #         row.id: (row.noncompliant, row.missing)
    #         for row in session.execute(sql_noncompliant)
    #     }
    #
    #     # ─────────────────────────────────────────────
    #     # 4️⃣  Construction du résultat final
    #     # ─────────────────────────────────────────────
    #     result = []
    #     for entity_id in entities:
    #         entity_id = int(entity_id)
    #
    #         machines = machine_by_entity.get(entity_id, [])
    #         noncompliant, missing = noncompliant_data.get(entity_id, (0, 0))
    #         total = total_machines.get(entity_id, len(machines))
    #
    #         result.append({
    #             "entity": str(entity_id),
    #             "nbmachines": noncompliant,
    #             "nbupdates": missing,
    #             "totalmach": total,
    #         })
    #
    #     return result


    @DatabaseHelper._sessionm
    def get_machines_xmppmaster(self, session, start, end, ctx):
        """
        Recovers the machines from the XMPPMaster base
        """
        location = ""
        criterion = ""
        field = ""
        contains = ""

        if "location" in ctx and ctx["location"] != "":
            location = ctx["location"].replace("UUID", "")

        if "filter" in ctx and ctx["filter"] != "":
            criterion = ctx["filter"]

        if "field" in ctx and ctx["field"] != "":
            field = ctx["field"]

        if "contains" in ctx and ctx["contains"] != "":
            contains = ctx["contains"]

        where_clauses = [
            "m.agenttype = 'machine'",
            f"m.glpi_entity_id = (SELECT id FROM glpi_entity WHERE glpi_id = {location})"
        ]
        if criterion:
            where_clauses.append(
                f"(m.hostname LIKE '%{criterion}%' OR ge.complete_name LIKE '%{criterion}%')"
            )
        where_sql = " AND ".join(where_clauses)

        count_sql = f"""
            SELECT COUNT(*) AS total
            FROM machines m
            JOIN glpi_entity ge ON m.glpi_entity_id = ge.id
            WHERE {where_sql}
        """
        total = session.execute(count_sql).scalar() or 0

        sql_query = f"""
            SELECT
                m.uuid_inventorymachine AS uuid,
                m.hostname             AS cn,
                m.platform             AS os,
                m.model                AS description,
                m.manufacturer         AS type,
                m.lastuser             AS user,
                ge.complete_name       AS entity
            FROM machines m
            JOIN glpi_entity ge ON m.glpi_entity_id = ge.id
            WHERE {where_sql}
            LIMIT {start}, {end}
        """
        result = session.execute(sql_query)
        machines = result.fetchall()

        result_data = {
            "count": total,
            "data": {
                "uuid": [],
                "cn": [],
                "os": [],
                "description": [],
                "type": [],
                "user": [],
                "entity": [],
                "presence": [],
            },
        }

        for row in machines:
            uid = row["uuid"].replace("UUID", "") if row["uuid"] else ""
            result_data["data"]["uuid"].append(uid)
            result_data["data"]["cn"].append(row["cn"] or "")
            result_data["data"]["os"].append(row["os"] or "")
            result_data["data"]["description"].append(row["description"] or "")
            result_data["data"]["type"].append(row["type"] or "")
            result_data["data"]["user"].append(row["user"] or "")
            result_data["data"]["entity"].append(row["entity"] or "")
            result_data["data"]["presence"].append(1)

        uuids = [f"UUID{u}" for u in result_data["data"]["uuid"]]
        result_data["xmppdata"] = XmppMasterDatabase().getmachinesbyuuids(uuids)

        return result_data

    @DatabaseHelper._sessionm
    def get_all_machines_grouped_by_os(self, session, start, end, ctx):
        """
        Récupère les machines du XMPPMaster, groupées par type d'OS :
        - Microsoft Windows
        - Linux (Linux, Ubuntu, RedHat, Debian, CentOS, etc.)
        - Autres

        Filtres (ctx) et pagination inclus.
        """

        # ───────────────────────────────
        # 1️⃣ Préparation des filtres
        # ───────────────────────────────
        location = ctx.get("location", "").replace("UUID", "")
        criterion = ctx.get("filter", "")
        field = ctx.get("field", "")
        contains = ctx.get("contains", "")

        where_clauses = ["m.agenttype = 'machine'"]

        if location:
            where_clauses.append(
                f"m.glpi_entity_id = (SELECT id FROM glpi_entity WHERE glpi_id = {location})"
            )

        if criterion:
            where_clauses.append(
                f"(m.hostname LIKE '%{criterion}%' OR ge.complete_name LIKE '%{criterion}%')"
            )

        if field and contains:
            where_clauses.append(f"{field} LIKE '%{contains}%'")

        where_sql = " AND ".join(where_clauses)

        # ───────────────────────────────
        # 2️⃣ Structure du résultat final
        # ───────────────────────────────
        result_data = {
            "windows": {"count": 0, "data": {k: [] for k in ["uuid", "cn", "os", "description", "type", "user", "entity", "presence"]}},
            "linux":   {"count": 0, "data": {k: [] for k in ["uuid", "cn", "os", "description", "type", "user", "entity", "presence"]}},
            "autres":  {"count": 0, "data": {k: [] for k in ["uuid", "cn", "os", "description", "type", "user", "entity", "presence"]}},
        }

        # ───────────────────────────────
        # 3️⃣ Requête SQL principale
        # ───────────────────────────────
        sql_query = f"""
            SELECT
                m.uuid_inventorymachine AS uuid,
                m.hostname              AS cn,
                m.platform              AS os,
                m.model                 AS description,
                m.manufacturer          AS type,
                m.lastuser              AS user,
                ge.complete_name        AS entity
            FROM machines m
            JOIN glpi_entity ge ON m.glpi_entity_id = ge.id
            WHERE {where_sql}
            LIMIT {start}, {end}
        """

        result = session.execute(sql_query)
        machines = result.fetchall()

        # ───────────────────────────────
        # 4️⃣ Regroupement par OS
        # ───────────────────────────────
        linux_keywords = ["linux", "ubuntu", "debian", "centos", "redhat", "fedora", "suse"]

        for row in machines:
            uid = row["uuid"].replace("UUID", "") if row["uuid"] else ""
            os_value = (row["os"] or "").lower()

            if "windows" in os_value or "mic" in os_value:
                group = "windows"
            elif any(keyword in os_value for keyword in linux_keywords):
                group = "linux"
            else:
                group = "autres"

            section = result_data[group]

            section["data"]["uuid"].append(uid)
            section["data"]["cn"].append(row["cn"] or "")
            section["data"]["os"].append(row["os"] or "")
            section["data"]["description"].append(row["description"] or "")
            section["data"]["type"].append(row["type"] or "")
            section["data"]["user"].append(row["user"] or "")
            section["data"]["entity"].append(row["entity"] or "")
            section["data"]["presence"].append(1)
            section["count"] += 1

        # ───────────────────────────────
        # 5️⃣ Ajout des données XMPP
        # ───────────────────────────────
        all_uuids = (
            result_data["windows"]["data"]["uuid"]
            + result_data["linux"]["data"]["uuid"]
            + result_data["autres"]["data"]["uuid"]
        )

        uuids = [f"UUID{u}" for u in all_uuids]
        xmppdata = XmppMasterDatabase().getmachinesbyuuids(uuids)

        result_data["xmppdata"] = xmppdata

        return result_data


    @DatabaseHelper._sessionm
    def get_machine_in_both_sources(self, session, glpi_ids):
        """
        This function checks if the machines are present in both sources XMPPMaster and GLPI
        """
        if isinstance(glpi_ids, str):
            glpi_ids = [glpi_ids]

        # No id selected: nothing to return
        if glpi_ids == []:
            return {}

        query_xmpp = session.execute(
            """
            SELECT uuid_inventorymachine
            FROM xmppmaster.machines
            WHERE uuid_inventorymachine IN :uuids
            """,
            {"uuids": tuple(glpi_ids)},
        )

        found_uuids = {row[0] for row in query_xmpp.fetchall()}

        result = {uuid: (uuid in found_uuids) for uuid in glpi_ids}

        return result

    @DatabaseHelper._sessionm
    def get_conformity_update_by_entity_in_gray_list(self, session):
        """
        This function returns the total number of machines to update in an entity considering only the updates enabled in gray list
        """
        sql = """SELECT
                    glpi_entity_id AS entity,
                    COUNT(*) AS total_machine_entity,
                    SUM(CASE
                        WHEN (COALESCE(update_id, '') != '') THEN 1
                        ELSE 0
                    END) AS a_mettre_a_jour,
                    SUM(CASE
                        WHEN (COALESCE(update_id, '') = '') THEN 1
                        ELSE 0
                    END) AS a_ne_pas_mettre_a_jour
                FROM
                    xmppmaster.machines
                        LEFT JOIN
                    xmppmaster.up_machine_windows ON xmppmaster.machines.id = xmppmaster.up_machine_windows.id_machine
                        JOIN
                    xmppmaster.up_gray_list ON xmppmaster.up_gray_list.updateid = xmppmaster.up_machine_windows.update_id
                WHERE
                    platform LIKE 'Mic%'
                        AND xmppmaster.up_gray_list.valided = 1
                GROUP BY glpi_entity_id;"""
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        result = [rowproxy._asdict() for rowproxy in resultquery]
        return result

    @DatabaseHelper._sessionm
    def get_conformity_update_by_machine(self, session, idmachine):
        """
        This function returns value for compliance rate for one machine
        Params: id of one machine
        Return : waiting updates
        """
        sql = """SELECT COUNT(*) AS update_waiting
                FROM
                    xmppmaster.up_machine_windows
                LEFT JOIN
                    xmppmaster.up_gray_list ON xmppmaster.up_gray_list.updateid = xmppmaster.up_machine_windows.update_id
                LEFT JOIN
                    xmppmaster.up_white_list ON xmppmaster.up_white_list.updateid = xmppmaster.up_machine_windows.update_id
                WHERE
                    (up_gray_list.valided = 1 OR up_white_list.valided = 1)
                AND
                    up_machine_windows.id_machine = '%s';""" % (
            idmachine
        )
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        result = [rowproxy._asdict() for rowproxy in resultquery]
        return result

    @DatabaseHelper._sessionm
    def get_machine_with_update(
        self, session, kb, updateid, uuid, start=0, limit=-1, filter="", config=None
    ):

        filter_on = ""
        if config is not None and config.filter_on is not None:
            for key in config.filter_on:
                column = ""
                if key not in ["entity", "state", "type"]:
                    continue
                if key == "entity":
                    column = "lgf.entities_id"
                elif key == "state":
                    column = "lgf.states_id"
                elif key == "type":
                    column = "lgf.computertypes_id"
                filter_on = " %s AND %s in (%s) " % (
                    filter_on,
                    column,
                    ",".join(config.filter_on[key]),
                )
        try:
            start = int(start)
        except:
            start = 0
        try:
            limit = int(limit)
        except:
            limit = -1

        filterlimit = ""
        if start != -1 and limit != -1:
            filterlimit = "LIMIT %s, %s" % (start, limit)

        sfilter = ""
        if filter != "":
            sfilter = (
                """AND (lgm.name LIKE '%%%s%%' OR m.platform LIKE '%%%s%%')"""
                % tuple(filter for x in range(0, 2))
            )

        sql = """Select SQL_CALC_FOUND_ROWS
                    lgm.id,
                    lgm.name,
                    m.platform
                from
                    up_history uh
                join
                    update_data ud on ud.updateid = uh.update_id
                join
                    deploy d on uh.id_deploy=d.id
                join
                    machines m on m.id = uh.id_machine
                join
                    local_glpi_machines lgm on concat("UUID", lgm.id) = m.uuid_inventorymachine
                join
                    local_glpi_filters lgf on lgf.id = lgm.id
                where
                    uh.update_id="%s"
                and
                    d.state="DEPLOYMENT SUCCESS"
                and
                    delete_date is not NULL and delete_date != ""
                and
                    lgm.is_deleted =0 and lgm.is_template = 0
                and lgm.entities_id = %s
                %s %s
                union
                select
                    lgm.id,
                    lgm.name,
                    m.platform
                from
                    local_glpi_machines lgm
                join
                    machines m on m.uuid_inventorymachine = concat(lgm.id)
                join
                    local_glpi_filters lgf on lgf.id = lgm.id
                join
                    local_glpi_items_softwareversions lgisv on lgisv.items_id = lgm.id and lgisv.itemtype="Computer"
                join
                    local_glpi_softwareversions lgsv on lgsv.id = lgisv.softwareversions_id
                join
                    local_glpi_softwares lgs on lgs.id = lgsv.softwares_id
                where
                    lgsv.name LIKE '%%%s%%'
                AND
                    (lgsv.comment LIKE '%%Update%%' OR COALESCE(lgsv.comment, '') = '')
                %s %s
                group by lgm.id
                order by name
                %s
                """ % (
            updateid,
            uuid.replace("UUID", ""),
            filter_on,
            sfilter,
            kb,
            filter_on,
            sfilter,
            filterlimit,
        )

        datas = session.execute(sql)
        count = session.execute("SELECT FOUND_ROWS();")
        result = {"total": 0, "datas": {"id": [], "name": [], "os": []}}
        for elem in count:
            result["total"] = elem[0]
            break

        for elem in datas:
            result["datas"]["id"].append(elem.id)
            result["datas"]["name"].append(elem.name)
            result["datas"]["os"].append(elem.platform)
        return result

    @DatabaseHelper._sessionm
    def get_idmachine_from_name(self, session, name):
        """
        This function returns id of machine searched by hostname
        """
        sql = """SELECT id AS id_machine
                FROM
                    xmppmaster.machines
                WHERE
                    hostname = '%s' LIMIT 1;""" % (
            name
        )
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        result = [rowproxy._asdict() for rowproxy in resultquery]
        return result

    @DatabaseHelper._sessionm
    def get_count_updates_enable(self, session):
        """
        This function returns the the update already done and update enable
        """
        sql = """SELECT CAST(SUM( t.enabled_updates )AS INTEGER) as nb_enabled_updates
                FROM(
                    SELECT COUNT(*) AS enabled_updates FROM xmppmaster.up_gray_list WHERE valided = 1
                    UNION ALL
                    SELECT COUNT(*) AS enabled_updates FROM xmppmaster.up_white_list WHERE valided = 1) t;"""
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        return [rowproxy._asdict() for rowproxy in resultquery]

    @DatabaseHelper._sessionm
    def get_conformity_update_for_group(self, session, uuidArray):
        """
        This function returns value for compliance rate for group
        Params: array of uuid group
        Return : waiting updates and count of machine
        """
        if uuidArray != []:
            array_GUID = " AND uuid_inventorymachine IN (%s)" % ",".join(
                ["'%s'" % str(x) for x in uuidArray]
            )
        else:
            array_GUID = " AND uuid_inventorymachine IN ('')"

        sql = """SELECT
                    COUNT(DISTINCT(xmppmaster.machines.id)) AS count_machines,
                    SUM(CASE
                        WHEN (COALESCE(update_id, '') != '') THEN 1
                        ELSE 0
                    END) AS pending_updates
                FROM
                    xmppmaster.machines
                        LEFT JOIN
                    xmppmaster.up_machine_windows ON xmppmaster.machines.id = xmppmaster.up_machine_windows.id_machine
                        LEFT JOIN
                    xmppmaster.up_gray_list ON xmppmaster.up_gray_list.updateid = xmppmaster.up_machine_windows.update_id
                        LEFT JOIN
                    xmppmaster.up_white_list ON xmppmaster.up_white_list.updateid = xmppmaster.up_machine_windows.update_id
                WHERE
                    platform LIKE 'Mic%'
                        AND (xmppmaster.up_gray_list.valided = 1 or xmppmaster.up_white_list.valided = 1)"""

        sql = sql + array_GUID + ";"
        resultquery = session.execute(sql)
        session.commit()
        session.flush()
        result = [rowproxy._asdict() for rowproxy in resultquery]
        for t in result:
            if t["pending_updates"] == None:
                t["pending_updates"] = 0
        return result

    @DatabaseHelper._sessionm
    def get_oumachine_list_from_machines(self, session):
        """Get all ous listed in machines table (in ad_ou_machine and ad_ou_user fields)
        Returns list: all unique OUs found in the table
        """
        query = (
            session.query(Machines.ad_ou_machine).group_by(
                Machines.ad_ou_machine).all()
        )
        result = []
        if query is not None:
            for ou in query:
                if ou[0] != "":
                    if ou[0] not in result:
                        result.append(ou[0].replace("@@", "/"))
        return result

    @DatabaseHelper._sessionm
    def get_ouuser_list_from_machines(self, session):
        """Get all ous listed in machines table (in ad_ou_machine and ad_ou_user fields)
        Returns list: all unique OUs found in the table
        """
        query = session.query(Machines.ad_ou_user).group_by(
            Machines.ad_ou_user).all()
        result = []
        if query is not None:
            for ou in query:
                if ou[0] != "":
                    if ou[0] not in result:
                        result.append(ou[0].replace("@@", "/"))
        return result

    @DatabaseHelper._sessionm
    def get_users_from_ou_from_machines(self, session, ou):
        """Get all users listed in machines table corresponding to ad_ou_user = ou
        Params:
            ou (str) : The location where the users are searched
        Returns list: all unique OUs found in the table
        """
        result = []
        query = (
            session.query(Machines.lastuser)
            .filter(Machines.ad_ou_user == ou)
            .group_by(Machines.lastuser)
            .all()
        )

        if query is not None:
            result = [user[0] for user in query]
        return result

    @DatabaseHelper._sessionm
    def get_ou_list_from_entity(self, session):
        result = []
        query = (
            session.query(Glpi_entity.complete_name)
            .join(Machines, Machines.glpi_entity_id == Glpi_entity.id)
            .all()
        )

        if query is not None:
            result = [user[0] for user in query]

        return result

    @DatabaseHelper._sessionm
    def get_ou_for_user_from_machines(self, session, user):
        """Get user's ous listed in machines table corresponding to lastuser = user
        Params:
            user (str) : The user searched
        Returns list: all unique OUs found in the table
        """
        result = []
        query = (
            session.query(Machines.ad_ou_user)
            .filter(Machines.lastuser == user)
            .group_by(Machines.ad_ou_user)
            .all()
        )

        if query is not None:
            result = [ou[0].replace("@@", "/") for ou in query]
        return result

    # ################################## update function ####################################

    @DatabaseHelper._sessionm
    def update_Up_machine_windows(
        self,
        session,
        id_machine,
        update_id,
        curent_deploy,
        required_deploy,
        start_date,
        end_date,
    ):
        """
        update table Up_machine_windows for deploy individuel
        id_machine integer
        update_id  uuid
        curent_deploy boolean
        required_deploy boolean,
        start_date datetime,
        end_date datetime
        """
        try:
            result = (
                session.query(Up_machine_windows)
                .filter(
                    and_(
                        Up_machine_windows.id_machine == id_machine,
                        Up_machine_windows.update_id == update_id,
                    )
                )
                .first()
            )
            if result is None:
                logger.warning(
                    "update_Up_machine_windows no update [%s] for this id machine (%s)"
                    % (update_id, id_machine)
                )
            else:
                result.curent_deploy = curent_deploy
                result.required_deploy = required_deploy
                result.start_date = start_date
                result.end_date = end_date
                logger.debug(
                    "update_Up_machine_windows\n\tid machine%s\n\tupdate_id %s"
                    "\n\tkb %s\n\tcurent_deploy %s\n\trequired_deploy %s"
                    "\n\tstart_date %s\n\tend_date %s"
                    % (
                        id_machine,
                        Up_machine_windows.update_id,
                        result.kb,
                        result.curent_deploy,
                        result.required_deploy,
                        result.start_date,
                        result.end_date,
                    )
                )

                session.commit()
                session.flush()
        except Exception as e:
            logger.error(
                "An error occured on update_Up_machine_windows function.")
            logger.error("We obtained the error: \n %s" % str(e))
            return False
        return True

    @DatabaseHelper._sessionm
    def update_all_for_machine_Up_machine_windows(
        self, session, id_machine, start_date, end_date, required_deploy=True
    ):
        """
        demande de faire toute les mise a jour d'une machine dans 1 slot de temps
        id_machine integer
        required_deploy boolean default mise a jour
        """
        try:
            result = (
                session.query(Up_machine_windows)
                .filter(Up_machine_windows.id_machine == id_machine)
                .all()
            )
            if result is None:
                logger.warning(
                    "update_Up_machine_windows no update for this id machine (%s)"
                    % (id_machine)
                )
            else:
                for t in result:
                    t.required_deploy = required_deploy
                    t.start_date = start_date
                    t.end_date = end_date
                    logger.debug(
                        "update_Up_machine_windows\n\tid machine%s\n\tupdate_id %s"
                        "\n\tkb %s\n\tcurent_deploy %s\n\trequired_deploy %s"
                        "\n\tstart_date %s\n\tend_date %s"
                        % (
                            id_machine,
                            t.update_id,
                            t.kb,
                            t.curent_deploy,
                            t.required_deploy,
                            t.start_date,
                            t.end_date,
                        )
                    )

                    session.commit()
                    session.flush()
        except Exception as e:
            logger.error(
                "An error occured on update_Up_machine_windows function.")
            logger.error("We obtained the error: \n %s" % str(e))
            return False
        return True

    @DatabaseHelper._sessionm
    def get_updates_by_entity(self, session, entity, start=0, limit=-1, filter=""):
        entity = normalize_entity(entity, defaut=-1)
        start = to_int(start, 0)
        limit = to_int(limit, -1)
        try:
            sql = f"""
                SELECT
                    umw.id_machine,
                    umw.update_id,
                    umw.kb,
                    COALESCE(umw.curent_deploy, 0) AS current_deploy,
                    COALESCE(umw.required_deploy, 0) AS required_deploy,
                    COALESCE(umw.start_date, '') AS start_date,
                    COALESCE(umw.end_date, '') AS end_date,
                    COALESCE(umw.intervals, '') AS deployment_intervals,
                    COALESCE(umw.msrcseverity, '') AS msrcseverity,
                    COALESCE(p.label, '') AS pkgs_label,
                    COALESCE(p.version, '') AS pkgs_version,
                    COALESCE(p.description, '') AS pkgs_description
                FROM up_machine_windows AS umw
                INNER JOIN machines AS m ON umw.id_machine = m.id
                INNER JOIN glpi_entity AS ge ON ge.id = m.glpi_entity_id
                LEFT JOIN up_gray_list AS g ON g.updateid = umw.update_id
                LEFT JOIN up_white_list AS w ON w.updateid = umw.update_id
                LEFT JOIN pkgs.packages AS p ON p.uuid = umw.update_id
                WHERE
                    ge.glpi_id = :entity
                    AND (g.valided = 1 OR w.valided = 1)
                    AND (umw.curent_deploy IS NULL OR umw.curent_deploy = 0)
                    AND (umw.required_deploy IS NULL OR umw.required_deploy = 0)
                    {f"AND (umw.kb LIKE :filter OR umw.update_id LIKE :filter)" if filter else ""}
                GROUP BY umw.update_id
                ORDER BY umw.update_id
                {f"LIMIT {limit} OFFSET {start}" if limit != -1 else ""}
            """

            params = {"entity": entity}
            if filter:
                params["filter"] = f"%{filter}%"

            result = session.execute(sql, params).fetchall()

            return {
                "total": len(result),
                "datas": [dict(row._mapping) for row in result],
            }

        except Exception as e:
            if DEBUG_MODE:
                logger.exception(f"[get_updates_by_entity] Erreur lors de l'exécution SQL : {e}")
            else:
                logger.error(f"[get_updates_by_entity] Erreur SQL : {e}")

            logger.error(f"[get_updates_by_entity] Erreur lors de l'exécution SQL : {e}")
            return {"total": 0, "datas": []}


    @DatabaseHelper._sessionm
    def get_updates_machines_by_entity(
        self, session, entity, pid, start, limit, filter
    ):
        entity = normalize_entity(entity, defaut=-1)
        start = to_int(start, 0)
        limit = to_int(limit, -1)

        query = (
            session.query(
                Machines.id,
                Machines.uuid_inventorymachine,
                Machines.jid,
                Machines.hostname,
            )
            .join(Glpi_entity, Glpi_entity.id == Machines.glpi_entity_id)
            .join(Up_machine_windows, Up_machine_windows.id_machine == Machines.id)
            .filter(
                and_(
                    Up_machine_windows.update_id == pid,
                    Glpi_entity.glpi_id == entity,
                    or_(
                        Up_machine_windows.curent_deploy == None,
                        Up_machine_windows.curent_deploy == 0,
                    ),
                    or_(
                        Up_machine_windows.required_deploy == None,
                        Up_machine_windows.required_deploy == 0,
                    ),
                )
            )
            .all()
        )
        result = []

        for machine in query:
            result.append(
                {
                    "id": machine.id,
                    "uuid_inventorymachine": machine.uuid_inventorymachine,
                    "jid": machine.jid,
                    "hostname": machine.hostname,
                }
            )
        return result

    @DatabaseHelper._sessionm
    def pending_entity_update_by_pid(
        self, session, entity, pid="", startdate="", enddate="", interval=""
    ):
        start_date = None
        end_date = None

        current = datetime.today()
        a_week_from_current = current + timedelta(days=7)

        if startdate != "":
            try:
                start_date = datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S")
            except:
                start_date = current

        if enddate != "":
            try:
                end_date = datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S")
            except:
                end_date = a_week_from_current

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        if end_date < current:
            end_date = a_week_from_current

        query = session.query(Up_machine_activated, self.Local_glpi_entities).join(
            self.Local_glpi_entities,
            self.Local_glpi_entities.id == Up_machine_activated.entities_id,
        )

        if pid == "":
            query = query.filter(
                and_(
                    or_(
                        Up_machine_activated.curent_deploy == None,
                        Up_machine_activated.curent_deploy == 0,
                    ),
                    or_(
                        Up_machine_activated.required_deploy == None,
                        Up_machine_activated.required_deploy == 0,
                    ),
                    Up_machine_activated.entities_id == entity.replace(
                        "UUID", ""),
                    # Up_machine_activated.id_machine.in_(sub),
                )
            )
        else:
            query = query.filter(and_(Up_machine_activated.update_id == pid))
        datas = query.all()
        kblist = []
        entity = None
        result = {
            "success": False,
            "mesg": "Nothing to update",
        }
        if query is not None:
            for element, _ in query:
                element.required_deploy = 1
                element.start_date = start_date
                element.end_date = end_date
                element.intervals = interval
                session.commit()
                session.flush()

            for upd, ent in datas:
                if "KB%s" % upd.kb not in kblist:
                    kblist.append("KB%s" % upd.kb)
                if entity is None:
                    entity = ent.name

            result["success"] = True
            result["mesg"] = "Update(s) %s have been requested for entity %s" % (
                ",".join(kblist),
                entity,
            )

        return result

    @DatabaseHelper._sessionm
    def get_updates_by_uuids(self, session, uuids, start=0, limit=-1, filter=""):
        query = (
            session.query(Up_machine_windows)
            .join(Machines, Machines.id == Up_machine_windows.id_machine)
            .outerjoin(
                Up_gray_list, Up_gray_list.updateid == Up_machine_windows.update_id
            )
            .outerjoin(
                Up_white_list, Up_white_list.updateid == Up_machine_windows.update_id
            )
            .filter(
                and_(
                    Machines.uuid_inventorymachine.in_(uuids),
                    or_(Up_gray_list.valided == 1, Up_white_list.valided == 1),
                    or_(
                        Up_machine_windows.curent_deploy == None,
                        Up_machine_windows.curent_deploy == 0,
                    ),
                    or_(
                        Up_machine_windows.required_deploy == None,
                        Up_machine_windows.required_deploy == 0,
                    ),
                )
            )
            .group_by(Up_machine_windows.update_id)
            .order_by(
                func.field(
                    Up_machine_windows.msrcseverity,
                    "Critical",
                    "Important",
                    "Corrective",
                )
            )
        )

        if filter != "":
            query = query.filter(
                or_(
                    Up_machine_windows.update_id.contains(filter),
                    Up_machine_windows.msrcseverity.contains(filter),
                    Up_gray_list.kb.contains(filter),
                    Up_white_list.kb.contains(filter),
                    Up_gray_list.title.contains(filter),
                    Up_white_list.title.contains(filter),
                    Machines.hostname.contains(filter),
                    Up_gray_list.description.contains(filter),
                    Up_white_list.description.contains(filter),
                )
            )

        count = query.count()
        query = query.offset(start)
        if limit != -1:
            query = query.limit(limit)

        query = query.all()
        pkgs_list = {}
        result = {"total": count, "datas": []}

        for element in query:
            startdate = ""
            if element.start_date is not None:
                startdate = element.start_date

            current_deploy = 0
            if element.curent_deploy is not None:
                current_deploy = element.curent_deploy

            required_deploy = 0
            if element.required_deploy is not None:
                required_deploy = element.required_deploy

            enddate = ""
            if element.end_date is not None:
                enddate = element.end_date

            result["datas"].append(
                {
                    "id_machine": element.id_machine if not None else 0,
                    "update_id": element.update_id if not None else "",
                    "kb": element.kb if not None else "",
                    "current_deploy": current_deploy,
                    "required_deploy": required_deploy,
                    "start_date": startdate,
                    "end_date": enddate,
                    "pkgs_label": "" if not None else "",
                    "pkgs_version": "",
                    "pkgs_description": "",
                    "severity": element.msrcseverity if not None else "Corrective",
                }
            )
            pkgs_list[element.update_id] = {}

        if pkgs_list != {}:
            if pkgs_list.keys() != []:
                concat = "in (%s)" % ",".join(
                    ['"%s"' % uuid for uuid in pkgs_list.keys()]
                )
            else:
                concat = '= ""'

            sql2 = (
                """SELECT pkgs.packages.uuid,
            pkgs.packages.label,
            pkgs.packages.version,
            pkgs.packages.description
            FROM pkgs.packages
            WHERE pkgs.packages.uuid %s
            """
                % concat
            )
            query2 = session.execute(sql2)

            for element in query2:
                pkgs_list[element[0]] = {
                    "label": element[1],
                    "version": element[2],
                    "description": element[3],
                }

            for element in result["datas"]:
                if element["update_id"] in pkgs_list:
                    print(pkgs_list[element["update_id"]])
                    element["pkgs_label"] = pkgs_list[element["update_id"]]["label"]
                    element["pkgs_version"] = pkgs_list[element["update_id"]]["version"]
                    element["pkgs_description"] = pkgs_list[element["update_id"]][
                        "description"
                    ]
        return result

    @DatabaseHelper._sessionm
    def get_updates_by_machineids(
        self, session, machineids, start=0, limit=-1, filter=""
    ):
        query = (
            session.query(Up_machine_activated, Update_data)
            .join(Update_data, Update_data.updateid == Up_machine_activated.update_id)
            .filter(
                and_(
                    Up_machine_activated.id_machine.in_(machineids),
                    or_(
                        Up_machine_activated.curent_deploy == None,
                        Up_machine_activated.curent_deploy == 0,
                    ),
                    or_(
                        Up_machine_activated.required_deploy == None,
                        Up_machine_activated.required_deploy == 0,
                    ),
                )
            )
            .order_by(
                func.field(
                    Up_machine_activated.msrcseverity,
                    "Critical",
                    "Important",
                    "Corrective",
                )
            )
        )

        if filter != "":
            query = query.filter(
                or_(
                    Up_machine_activated.kb.contains(filter),
                    Up_machine_activated.update_id.contains(filter),
                    Update_data.title.contains(filter),
                    Update_data.description.contains(filter),
                    Update_data.kb.contains(filter),
                    Update_data.creationdate.contains(filter),
                )
            )

        count = query.count()
        query = query.offset(start)
        if limit != -1:
            query = query.limit(limit)

        query = query.all()
        pkgs_list = {}
        result = {"total": count, "datas": []}

        for element, update_data in query:
            startdate = ""
            if element.start_date is not None:
                startdate = element.start_date

            current_deploy = 0
            if element.curent_deploy is not None:
                current_deploy = element.curent_deploy

            required_deploy = 0
            if element.required_deploy is not None:
                required_deploy = element.required_deploy

            enddate = ""
            if element.end_date is not None:
                enddate = element.end_date

            update_list = element.list
            title = update_data.title
            description = update_data.description if update_data is not None else ""
            kb = update_data.kb

            result["datas"].append(
                {
                    "id_machine": (
                        element.id_machine if element.id_machine is not None else 0
                    ),
                    "update_id": element.update_id if not None else "",
                    "title": title if title is not None else "",
                    "description": description if description is not None else "",
                    "kb": kb if kb is not None else "",
                    "current_deploy": current_deploy,
                    "required_deploy": required_deploy,
                    "start_date": startdate,
                    "end_date": enddate,
                    "deployment_intervals": (
                        element.intervals if element.intervals is not None else ""
                    ),
                    "pkgs_version": "",
                    "pkgs_description": "",
                    "severity": (
                        element.msrcseverity
                        if element.msrcseverity is not None
                        else "Corrective"
                    ),
                    "list": update_list,
                }
            )
            pkgs_list[element.update_id] = {}

        if pkgs_list != {}:
            if pkgs_list.keys() != []:
                concat = "in (%s)" % ",".join(
                    ['"%s"' % uuid for uuid in pkgs_list.keys()]
                )
            else:
                concat = '= ""'

            sql2 = (
                """SELECT pkgs.packages.uuid,
            pkgs.packages.label,
            pkgs.packages.version,
            pkgs.packages.description
            FROM pkgs.packages
            WHERE pkgs.packages.uuid %s
            """
                % concat
            )
            query2 = session.execute(sql2)

            for element in query2:
                pkgs_list[element[0]] = {
                    "label": element[1],
                    "version": element[2],
                    "description": element[3],
                }

            for element in result["datas"]:
                if element["update_id"] in pkgs_list:
                    print(pkgs_list[element["update_id"]])
                    element["pkgs_label"] = (
                        pkgs_list[element["update_id"]]["label"]
                        if "label" in pkgs_list[element["update_id"]]
                        else ""
                    )
                    element["pkgs_version"] = (
                        pkgs_list[element["update_id"]]["version"]
                        if "version" in pkgs_list[element["update_id"]]
                        else ""
                    )
                    element["pkgs_description"] = (
                        pkgs_list[element["update_id"]]["description"]
                        if "description" in pkgs_list[element["update_id"]]
                        else ""
                    )
        return result

    @DatabaseHelper._sessionm
    def get_machines_infos(
        self, session, mom_keys_for_search, data_search, exclude_keys=None
    ):
        """
        Récupère les informations des machines en fonction des critères de recherche spécifiés,
        avec la possibilité d'exclure certaines clés des résultats.

        Paramètres :
        - mom_keys_for_search (str/list) : Une clé ou une liste de clés correspondant aux colonnes de la table 'machines'.
        - data_search (list) : Une liste de valeurs correspondant aux critères de recherche pour chaque clé.
        - exclude_keys (list) : Une liste de clés à exclure des dictionnaires de résultats. Peut être vide ou None.

        Retourne :
        - list : Une liste de dictionnaires contenant les informations des machines trouvées,
                ou un message d'erreur si les paramètres sont invalides ou si aucune machine n'est trouvée.

        Exemples :
        1. Recherche par UUID d'inventaire :
        ```python
        result = get_machines_infos("uuid_inventorymachine", [5])
        print(result)
        ```
        2. Recherche par UUID d'inventaire et état d'activation, avec exclusion de certaines clés :
        ```python
        result = get_machines_infos(["uuid_inventorymachine", "enabled"], [5, 1], ["picklekeypublic", "ad_ou_machine", "ad_ou_user"])
        print(result)
        ```
        """
        # Vérifier que mom_keys_for_search et data_search ont le même nombre d'éléments
        if isinstance(mom_keys_for_search, str):
            mom_keys_for_search = [mom_keys_for_search]

        if len(mom_keys_for_search) != len(data_search):
            return {
                "error": "mom_keys_for_search and data_search must have the same number of elements."
            }

        if exclude_keys is None:
            exclude_keys = []

        try:
            # Construire la requête dynamiquement
            filters = [
                getattr(Machines, key) == value
                for key, value in zip(mom_keys_for_search, data_search)
            ]
            query = session.query(Machines).filter(and_(*filters))

            # Exécuter la requête et récupérer les résultats
            machines = query.all()

            if machines:
                # Convertir les objets en dictionnaires
                machines_info = []
                for machine in machines:
                    machine_info = {
                        "jid": machine.jid,
                        "uuid_serial_machine": machine.uuid_serial_machine,
                        "need_reconf": machine.need_reconf,
                        "enabled": machine.enabled,
                        "platform": machine.platform,
                        "hostname": machine.hostname,
                        "archi": machine.archi,
                        "uuid_inventorymachine": machine.uuid_inventorymachine,
                        "ippublic": machine.ippublic,
                        "ip_xmpp": machine.ip_xmpp,
                        "subnetxmpp": machine.subnetxmpp,
                        "macaddress": machine.macaddress,
                        "agenttype": machine.agenttype,
                        "classutil": machine.classutil,
                        "urlguacamole": machine.urlguacamole,
                        "groupdeploy": machine.groupdeploy,
                        "picklekeypublic": machine.picklekeypublic,
                        "ad_ou_machine": machine.ad_ou_machine,
                        "ad_ou_user": machine.ad_ou_user,
                        "kiosk_presence": machine.kiosk_presence,
                        "lastuser": machine.lastuser,
                        "keysyncthing": machine.keysyncthing,
                        "glpi_description": machine.glpi_description,
                        "glpi_owner_firstname": machine.glpi_owner_firstname,
                        "glpi_owner_realname": machine.glpi_owner_realname,
                        "glpi_owner": machine.glpi_owner,
                        "model": machine.model,
                        "manufacturer": machine.manufacturer,
                        "glpi_entity_id": machine.glpi_entity_id,
                        "glpi_location_id": machine.glpi_location_id,
                    }
                    # Exclure les clés spécifiées
                    for key in exclude_keys:
                        machine_info.pop(key, None)

                    machines_info.append(machine_info)
                return machines_info
            else:
                return {"error": "No machines found matching the criteria."}

        except Exception as e:
            return {"error": str(e)}

    @DatabaseHelper._sessionm
    def get_machines_infos_reg(
        self, session, mom_keys_for_search, data_search, exclude_keys=None
    ):
        """
        Récupère les informations des machines en fonction des critères de recherche spécifiés,
        avec la possibilité d'exclure certaines clés des résultats.

        Paramètres :
        - mom_keys_for_search (str/list) : Une clé ou une liste de clés correspondant aux colonnes de la table 'machines'.
        - data_search (list) : Une liste de valeurs correspondant aux critères de recherche pour chaque clé.
                            Peut contenir des expressions avec '%', des listes d'éléments, ou des expressions régulières.
        - exclude_keys (list) : Une liste de clés à exclure des dictionnaires de résultats. Peut être vide ou None.

        Retourne :
        - list : Une liste de dictionnaires contenant les informations des machines trouvées,
                ou un message d'erreur si les paramètres sont invalides ou si aucune machine n'est trouvée.

        Exemples :
        1. Recherche par UUID d'inventaire avec expression :
        ```python
        result = get_machines_infos("uuid_inventorymachine", ["%5%"])
        print(result)
        ```
        2. Recherche par UUID d'inventaire et état d'activation, avec exclusion de certaines clés :
        ```python
        result = get_machines_infos(["uuid_inventorymachine", "enabled"], [["2", "3", "4"], 1], ["picklekeypublic", "ad_ou_machine", "ad_ou_user"])
        print(result)
        ```
        """
        # Vérifier que mom_keys_for_search et data_search ont le même nombre d'éléments
        if isinstance(mom_keys_for_search, str):
            mom_keys_for_search = [mom_keys_for_search]

        if len(mom_keys_for_search) != len(data_search):
            return {
                "error": "mom_keys_for_search and data_search must have the same number of elements."
            }

        if exclude_keys is None:
            exclude_keys = []

        try:
            # Construire la requête dynamiquement
            filters = []
            for key, value in zip(mom_keys_for_search, data_search):
                column = getattr(Machines, key)
                if isinstance(value, list):
                    # Cas où la valeur est une liste d'éléments
                    filters.append(column.in_(value))
                elif isinstance(value, str) and "%" in value:
                    # Cas où la valeur contient des '%'
                    filters.append(column.like(value))
                elif isinstance(value, str) and value.startswith("regex:"):
                    # Cas où la valeur est une expression régulière
                    regex = value[len("regex:"):]
                    filters.append(column.op("REGEXP")(regex))
                else:
                    # Cas par défaut : égalité stricte
                    filters.append(column == value)

            query = session.query(Machines).filter(and_(*filters))

            # Exécuter la requête et récupérer les résultats
            machines = query.all()

            if machines:
                # Convertir les objets en dictionnaires
                machines_info = []
                for machine in machines:
                    machine_info = {
                        "jid": machine.jid,
                        "uuid_serial_machine": machine.uuid_serial_machine,
                        "need_reconf": machine.need_reconf,
                        "enabled": machine.enabled,
                        "platform": machine.platform,
                        "hostname": machine.hostname,
                        "archi": machine.archi,
                        "uuid_inventorymachine": machine.uuid_inventorymachine,
                        "ippublic": machine.ippublic,
                        "ip_xmpp": machine.ip_xmpp,
                        "subnetxmpp": machine.subnetxmpp,
                        "macaddress": machine.macaddress,
                        "agenttype": machine.agenttype,
                        "classutil": machine.classutil,
                        "urlguacamole": machine.urlguacamole,
                        "groupdeploy": machine.groupdeploy,
                        "picklekeypublic": machine.picklekeypublic,
                        "ad_ou_machine": machine.ad_ou_machine,
                        "ad_ou_user": machine.ad_ou_user,
                        "kiosk_presence": machine.kiosk_presence,
                        "lastuser": machine.lastuser,
                        "keysyncthing": machine.keysyncthing,
                        "glpi_description": machine.glpi_description,
                        "glpi_owner_firstname": machine.glpi_owner_firstname,
                        "glpi_owner_realname": machine.glpi_owner_realname,
                        "glpi_owner": machine.glpi_owner,
                        "model": machine.model,
                        "manufacturer": machine.manufacturer,
                        "glpi_entity_id": machine.glpi_entity_id,
                        "glpi_location_id": machine.glpi_location_id,
                    }
                    # Exclure les clés spécifiées
                    for key in exclude_keys:
                        machine_info.pop(key, None)

                    machines_info.append(machine_info)
                return machines_info
            else:
                return {"error": "No machines found matching the criteria."}

        except Exception as e:
            return {"error": str(e)}

    @DatabaseHelper._sessionm
    def get_machines_infos_generic(
        self,
        session,
        mom_keys_for_search,
        data_search,
        include_keys=None,
        offset=0,
        limit=-1,
        colonne=True,
    ):
        """
        Récupère les informations des machines en fonction des critères de recherche spécifiés,
        en incluant uniquement les clés spécifiées dans les résultats.

        Paramètres :
        - mom_keys_for_search (str/list) : Une clé ou une liste de clés correspondant aux colonnes de la table 'machines'.
        - data_search (list) : Une liste de valeurs correspondant aux critères de recherche pour chaque clé.
                            Peut contenir des expressions avec '%', des listes d'éléments, ou des expressions régulières.
        - include_keys (list) : Une liste de clés à inclure dans les dictionnaires de résultats. Si vide, seul l'ID est renvoyé.
        - offset (int) : Le nombre d'enregistrements à ignorer.
        - limit (int) : Le nombre maximum d'enregistrements à renvoyer.
        - colonne (bool) : Si True, les résultats sont retournés sous forme de colonnes.

        Retourne :
        - dict : Un dictionnaire contenant les informations des machines trouvées,
                ou un message d'erreur si les paramètres sont invalides ou si aucune machine n'est trouvée.

        Exemples :
        1. Recherche par UUID d'inventaire avec inclusion de certaines clés :
        ```python
        result = get_machines_infos_additif("uuid_inventorymachine", ["%5%"], ["hostname", "platform"])
        print(result)
        ```

        2. Recherche par UUID d'inventaire et état d'activation, avec inclusion de certaines clés :
        ```python
        result = get_machines_infos_additif(["uuid_inventorymachine", "enabled"], [["2", "3", "4"], 1], ["hostname", "platform"])
        print(result)
        ```

        3. Recherche avec pagination et résultats sous forme de colonnes :
        ```python
        result = get_machines_infos_additif("uuid_inventorymachine", ["%5%"], ["hostname", "platform"], offset=10, limit=5, colonne=True)
        print(result)
        ```

        4. Recherche avec pagination et résultats sous forme de dictionnaires :
        ```python
        result = get_machines_infos_additif("uuid_inventorymachine", ["%5%"], ["hostname", "platform"], offset=10, limit=5, colonne=False)
        print(result)
        ```
        """
        # Vérifier que mom_keys_for_search et data_search ont le même nombre d'éléments
        if isinstance(mom_keys_for_search, str):
            mom_keys_for_search = [mom_keys_for_search]

        if len(mom_keys_for_search) != len(data_search):
            return {
                "error": "mom_keys_for_search and data_search must have the same number of elements."
            }

        if not include_keys:
            include_keys = [
                "id",
                "hostname",
                "platform",
                "jid",
                "uuid_serial_machine",
                "uuid_inventorymachine",
                "model",
                "manufacturer",
                "enabled",
            ]

        # # Si include_keys est vide, inclure uniquement l'ID
        # if not include_keys:
        #     include_keys = ["id"]

        try:
            # Construire la requête dynamiquement
            filters = []
            for key, value in zip(mom_keys_for_search, data_search):
                column = getattr(Machines, key)
                if isinstance(value, list):
                    # Cas où la valeur est une liste d'éléments
                    filters.append(column.in_(value))
                elif isinstance(value, str) and "%" in value:
                    # Cas où la valeur contient des '%'
                    filters.append(column.like(value))
                elif isinstance(value, str) and value.startswith("regex:"):
                    # Cas où la valeur est une expression régulière
                    regex = value[len("regex:"):]
                    filters.append(column.op("REGEXP")(regex))
                else:
                    # Cas par défaut : égalité stricte
                    filters.append(column == value)

            # Optimiser la requête pour ne sélectionner que les colonnes nécessaires
            query = (
                session.query(Machines)
                .options(load_only(*include_keys))
                .filter(and_(*filters))
            )

            # Calculer le nombre total d'enregistrements sans offset et limit
            total_count = query.count()

            # Appliquer offset et limit si spécifiés
            if limit != -1:
                query = query.offset(offset).limit(limit)

            # Exécuter la requête et récupérer les résultats
            machines = query.all()

            if machines:
                # Convertir les objets en dictionnaires ou en listes de colonnes
                if colonne:
                    machines_info = {key: [] for key in include_keys}
                    for machine in machines:
                        for key in include_keys:
                            value = getattr(machine, key)
                            machines_info[key].append(
                                value if value is not None else ""
                            )
                else:
                    machines_info = []
                    for machine in machines:
                        machine_info = {
                            key: (
                                getattr(machine, key)
                                if getattr(machine, key) is not None
                                else ""
                            )
                            for key in include_keys
                        }
                        machines_info.append(machine_info)

                return {
                    "total": total_count,
                    "partielle_total": len(machines),
                    "result": machines_info,
                }
            else:
                return {"error": "No machines found matching the criteria."}

        except Exception as e:
            return {"error": str(e)}

    @DatabaseHelper._sessionm
    def get_machines_infos_additif(
        self, session, mom_keys_for_search, data_search, include_keys=None
    ):
        """
        Récupère les informations des machines en fonction des critères de recherche spécifiés,
        en incluant uniquement les clés spécifiées dans les résultats.

        Paramètres :
        - mom_keys_for_search (str/list) : Une clé ou une liste de clés correspondant aux colonnes de la table 'machines'.
        - data_search (list) : Une liste de valeurs correspondant aux critères de recherche pour chaque clé.
                            Peut contenir des expressions avec '%', des listes d'éléments, ou des expressions régulières.
        - include_keys (list) : Une liste de clés à inclure dans les dictionnaires de résultats. Si vide, seul l'ID est renvoyé.

        Retourne :
        - list : Une liste de dictionnaires contenant les informations des machines trouvées,
                ou un message d'erreur si les paramètres sont invalides ou si aucune machine n'est trouvée.

        Exemples :
        1. Recherche par UUID d'inventaire avec inclusion de certaines clés :
        ```python
        result = get_machines_infos_additif("uuid_inventorymachine", ["%5%"], ["hostname", "platform"])
        print(result)
        ```
        2. Recherche par UUID d'inventaire et état d'activation, avec inclusion de certaines clés :
        ```python
        result = get_machines_infos_additif(["uuid_inventorymachine", "enabled"], [["2", "3", "4"], 1], ["hostname", "platform"])
        print(result)
        ```
        """
        # Vérifier que mom_keys_for_search et data_search ont le même nombre d'éléments
        if isinstance(mom_keys_for_search, str):
            mom_keys_for_search = [mom_keys_for_search]

        if len(mom_keys_for_search) != len(data_search):
            return {
                "error": "mom_keys_for_search and data_search must have the same number of elements."
            }

        if include_keys is None:
            include_keys = []

        # Si include_keys est vide, inclure uniquement l'ID
        if not include_keys:
            include_keys = ["id"]

        try:
            # Construire la requête dynamiquement
            filters = []
            for key, value in zip(mom_keys_for_search, data_search):
                column = getattr(Machines, key)
                if isinstance(value, list):
                    # Cas où la valeur est une liste d'éléments
                    filters.append(column.in_(value))
                elif isinstance(value, str) and "%" in value:
                    # Cas où la valeur contient des '%'
                    filters.append(column.like(value))
                elif isinstance(value, str) and value.startswith("regex:"):
                    # Cas où la valeur est une expression régulière
                    regex = value[len("regex:"):]
                    filters.append(column.op("REGEXP")(regex))
                else:
                    # Cas par défaut : égalité stricte
                    filters.append(column == value)

            # Optimiser la requête pour ne sélectionner que les colonnes nécessaires
            query = (
                session.query(Machines)
                .options(load_only(*include_keys))
                .filter(and_(*filters))
            )

            # Exécuter la requête et récupérer les résultats
            machines = query.all()

            if machines:
                # Convertir les objets en dictionnaires
                machines_info = []
                for machine in machines:
                    machine_info = {key: getattr(machine, key)
                                    for key in include_keys}
                    machines_info.append(machine_info)
                return machines_info
            else:
                return {"error": "No machines found matching the criteria."}

        except Exception as e:
            return {"error": str(e)}

    @DatabaseHelper._sessionm
    def get_os_xmpp_update_major_stats(self, session, presence=False):
        """
        Récupère les statistiques de mise à jour majeure des systèmes d'exploitation Windows 10 et Windows 11.

        Args:
            session (sqlalchemy.orm.session.Session): La session de base de données.
            presence (bool, optional): Filtrer uniquement les machines activées si True. Par défaut, True.

        Returns:
            dict: Un dictionnaire contenant les statistiques de mise à jour des systèmes d'exploitation.
        """
        try:
            # Dictionnaire final des résultats
            cols = ["W10to10", "W10to11", "W11to11"]
            results = {"entity": {}}

            # Condition de filtre sur xma.enabled
            presence_filter = "AND xma.enabled = 1" if presence else ""

            # Requête pour le nombre total de machines par entité
            total_os_sql = f"""
                SELECT
                    xe.name AS entity_name,
                    xe.complete_name AS complete_name,
                    COUNT(*) AS count
                FROM
                    xmppmaster.machines xma
                INNER JOIN xmppmaster.glpi_entity xe ON xe.id = xma.glpi_entity_id
                WHERE
                    xma.platform LIKE '%Windows%'
                    {presence_filter}
                GROUP BY xe.id;
            """

            total_os_result = session.execute(total_os_sql).fetchall()
            for row in total_os_result:
                results["entity"].setdefault(
                    row.complete_name, {"count": int(row.count)}
                )

            # Requête pour les statistiques par entité
            entity_sql = f"""
                        SELECT
                            xe.glpi_id as entity_id,
                            xe.name AS entity_name,
                            xe.complete_name AS complete_name,
                            COUNT(*) AS nbwin,
                            CASE
                                WHEN
                                    xma.platform LIKE '%Windows 10%'
                                        AND xma.platform NOT LIKE '%[22H2]'
                                THEN
                                    'W10to10'
                                WHEN
                                    xma.platform LIKE '%Windows 10%'
                                        AND xma.platform LIKE '%[22H2]'
                                THEN
                                    'W10to11'
                                WHEN
                                    xma.platform LIKE '%Windows 11%'
                                        AND xma.platform NOT LIKE '%[24H2]'
                                THEN
                                    'W11to11'
                                WHEN
                                    xma.platform LIKE '%Windows%'
                                        AND xma.platform NOT REGEXP '\[[0-9]{2}H[0-9]\]$'
                                THEN
                                    'winVers_missing'
                                ELSE 'not_win'
                            END AS os
                        FROM
                            xmppmaster.machines xma
                                INNER JOIN
                            xmppmaster.glpi_entity xe ON xe.id = xma.glpi_entity_id
                        WHERE
                            xma.platform LIKE '%Windows%'
                            {presence_filter}
                        GROUP BY xe.id , os
                        ORDER BY xe.complete_name , os;
            """

            entity_result = session.execute(entity_sql).fetchall()
            for row in entity_result:
                # initialisation
                results["entity"].setdefault(row.complete_name, {})
                results["entity"][row.complete_name]["name"] = row.entity_name
                results["entity"][row.complete_name][row.os] = int(row.nbwin)
                results["entity"][row.complete_name]["entity_id"] = int(
                    row.entity_id)
            # Calcul de la conformité
            for entity, data in results["entity"].items():
                total = results["entity"][entity]["count"]
                non_conforme = sum(data.get(key, 0) for key in cols)
                results["entity"][entity]["conformite"] = round(
                    ((non_conforme - total) / total *
                     100) if non_conforme > 0 else 0, 2
                )

            # Copier les clés existantes avant d'itérer
            existing_entities = list(results["entity"].keys())
            for entity in existing_entities:  # Itérer sur la copie des clés
                for col in cols:
                    if col not in results["entity"][entity]:
                        results["entity"][entity][col] = 0
            return results

        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération des statistiques de mise à jour des OS : {str(e)}"
            )
            logger.error(f"Traceback : {traceback.format_exc()}")
            return {}

    @DatabaseHelper._sessionm
    def get_os_xmpp_update_major_details(
        self, session, entity_id, filter="", start=0, limit=-1, colonne=True
    ):
        """
        Récupère les détails des machines avec des systèmes d'exploitation Windows à partir de la base de données XMPPMaster.

        Cette fonction exécute une requête SQL pour récupérer des informations sur les machines
        avec des systèmes d'exploitation Windows, y compris une colonne calculée 'os' qui
        catégorise la version du système d'exploitation et indique les mises à jour majeures
        nécessaires entre la version actuelle et la prochaine mise à jour majeure. Les résultats
        peuvent être retournés soit dans un format détaillé ligne par ligne, soit dans un format
        en colonnes, selon le paramètre 'colonne'.

        Paramètres :
            session (Session) : Objet de session SQLAlchemy pour l'interaction avec la base de données.
            entity_id (int) : L'ID de l'entité pour filtrer les résultats.
            filter (str) : Critères de filtrage supplémentaires pour filtrer par nom de machine.
            start (int) : Le décalage pour commencer à retourner les lignes.
            limit (int) : Le nombre maximum de lignes à retourner. Si -1, pas de limitation.
            colonne (bool) : Si True, retourne les résultats dans un format en colonnes. La valeur par défaut est True.

        Retourne :
            dict : Un dictionnaire contenant le nombre de lignes correspondantes et soit
                   des résultats détaillés ligne par ligne, soit des résultats en colonnes,
                   selon le paramètre 'colonne'. La colonne 'update' indique les mises à jour majeures
                   nécessaires, telles que 'W10to10' pour une mise à jour entre versions de Windows 10,
                   'W10to11' pour une mise à jour de Windows 10 vers Windows 11, et 'W11to11' pour une
                   mise à jour entre versions de Windows 11.
        """

        # Base SQL query
        total_os_sql = """
            SELECT
                SQL_CALC_FOUND_ROWS
                xma.id AS id_machine,
                xma.hostname AS machine,
                xma.platform AS platform,
                -- xe.glpi_id AS entity_id,
                -- xe.name AS entity_name,
                -- xe.complete_name AS complete_name,
                CASE
                    WHEN xma.platform REGEXP '\\\\[([0-9]{2}H[0-9])\\\\]$' THEN
                        SUBSTRING_INDEX(SUBSTRING_INDEX(xma.platform, '[', -1), ']', 1)
                    ELSE NULL
                END AS version,
                CASE
                    WHEN xma.platform LIKE '%Windows 10%' AND xma.platform NOT LIKE '%[22H2]' THEN 'W10to10'
                    WHEN xma.platform LIKE '%Windows 10%' AND xma.platform LIKE '%[22H2]' THEN 'W10to11'
                    WHEN xma.platform LIKE '%Windows 11%' AND xma.platform NOT LIKE '%[24H2]' THEN 'W11to11'
                    WHEN xma.platform LIKE '%Windows%' AND xma.platform NOT REGEXP '[[0-9]{2}H[0-9]]$' THEN 'winVers_missing'
                    ELSE 'not_win'
                END AS 'update'
            FROM
                xmppmaster.machines xma
                INNER JOIN xmppmaster.glpi_entity xe ON xe.id = xma.glpi_entity_id
            WHERE
                xma.platform LIKE '%Windows%' AND xe.glpi_id = :entity_id
        """
        # Add filter condition if filter is not empty
        if filter:
            total_os_sql += " AND xma.hostname LIKE :filter"

        # Add ORDER BY and LIMIT/OFFSET if limit is not -1
        total_os_sql += " ORDER BY xma.hostname "
        if limit != -1:
            logger.error("limit %s " % limit)
            total_os_sql += " LIMIT :limit OFFSET :start"

        # Convert to text for parameter binding
        total_os_sql = text(total_os_sql)

        # Log the SQL query with parameters
        logger.debug("Executing SQL query: %s", total_os_sql)
        logger.debug(
            "With parameters: entity_id=%s, filter=%s, limit=%s, start=%s",
            entity_id,
            f"%{filter}%",
            limit,
            start,
        )

        # Execute the SQL query with parameters
        entity_result = session.execute(
            total_os_sql,
            {
                "entity_id": entity_id,
                "filter": f"%{filter}%",
                "limit": limit,
                "start": start,
            },
        ).fetchall()

        # Count the total number of matching elements using FOUND_ROWS()
        sql_count = text("SELECT FOUND_ROWS();")
        ret_count = session.execute(sql_count).scalar()

        # Extract common fields from the first row
        # common_entity_id = entity_result[0].entity_id if entity_result else ""
        # common_entity_name = entity_result[0].entity_name if entity_result else ""
        # common_complete_name = entity_result[0].complete_name if entity_result else ""

        # Prepare the result dictionary with the count of matching rows and common fields
        result = {
            "nb_machine": ret_count,
            # 'entity_id': common_entity_id,
            # 'entity_name': common_entity_name,
            # 'complete_name': common_complete_name
        }

        if colonne:
            # If colonne is True, return results in columnar format
            result.update(
                {
                    "id_machine": [
                        row.id_machine if row.id_machine is not None else ""
                        for row in entity_result
                    ],
                    "machine": [
                        row.machine if row.machine is not None else ""
                        for row in entity_result
                    ],
                    "platform": [
                        row.platform if row.platform is not None else ""
                        for row in entity_result
                    ],
                    "version": [
                        row.version if row.version is not None else ""
                        for row in entity_result
                    ],
                    "update": [
                        row.update if row.update is not None else ""
                        for row in entity_result
                    ],
                }
            )
        else:
            # If colonne is False, return detailed results in row-wise format
            result["details"] = [
                {
                    "id_machine": row.id_machine if row.id_machine is not None else "",
                    "machine": row.machine if row.machine is not None else "",
                    "platform": row.platform if row.platform is not None else "",
                    "version": row.version if row.version is not None else "",
                    "update": row.update if row.update is not None else "",
                }
                for row in entity_result
            ]

        return result

    @DatabaseHelper._sessionm
    def pending_machine_update_by_pid(
        self,
        session,
        machineid,
        inventoryid,
        pid,
        deployName,
        user,
        startdate,
        enddate,
        interval,
    ):
        try:
            machineid = int(machineid)
        except:
            machineid = 0

        start_date = None
        end_date = None

        current = datetime.today()
        a_week_from_current = current + timedelta(days=7)

        if startdate != "":
            try:
                start_date = datetime.strptime(startdate, "%Y-%m-%d %H:%M:%S")
            except:
                start_date = current

        if enddate != "":
            try:
                end_date = datetime.strptime(enddate, "%Y-%m-%d %H:%M:%S")
            except:
                end_date = a_week_from_current

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        if end_date < current:
            end_date = a_week_from_current

        query, machine, update_data = (
            session.query(Up_machine_windows, Machines, Update_data)
            .join(Machines, Machines.id == Up_machine_windows.id_machine)
            .join(Update_data, Update_data.updateid == Up_machine_windows.update_id)
            .filter(
                and_(
                    Up_machine_windows.id_machine == machineid,
                    Up_machine_windows.update_id == pid,
                    or_(
                        Up_machine_windows.curent_deploy == None,
                        Up_machine_windows.curent_deploy == 0,
                    ),
                    or_(
                        Up_machine_windows.required_deploy == None,
                        Up_machine_windows.required_deploy == 0,
                    ),
                )
            )
            .first()
        )
        result = {}
        if query is not None:
            deployName = "%s -@upd@- %s" % (update_data.title, start_date)
            history = Up_history()
            history.update_id = query.update_id
            history.id_machine = query.id_machine
            history.jid = machine.jid
            history.update_list = "gray"
            history.required_date = datetime.strftime(
                start_date, "%Y-%m-%d %H:%M:%S")
            history.deploy_title = deployName
            session.add(history)

            query.start_date = start_date
            query.end_date = end_date
            query.required_deploy = 1
            query.intervals = interval
            session.commit()
            session.flush()

            result["success"] = True
            result["mesg"] = "Update %s required to deploy on machine %s" % (
                query.update_id,
                query.id_machine,
            )
        else:
            result["success"] = False
            result["mesg"] = "No update to install"

        return result

    @DatabaseHelper._sessionm
    def get_tagged_updates_by_machine(
        self, session, machineid, start=0, end=-1, filter=""
    ):
        start = to_int(start, 0)
        machineid = to_int(machineid, 0)
        end = to_int(end, -1)

        query = (
            session.query(Up_machine_windows, Update_data)
            .filter(
                and_(
                    Up_machine_windows.id_machine == machineid,
                    or_(
                        Up_machine_windows.curent_deploy == 1,
                        Up_machine_windows.required_deploy == 1,
                    ),
                )
            )
            .join(Update_data, Update_data.updateid == Up_machine_windows.update_id)
        )
        if filter != "":
            query = query.filter(
                or_(
                    Update_data.title.contains(filter),
                    Update_data.kb.contains(filter),
                    Update_data.updateid.contains(filter),
                    Update_data.revisionid.contains(filter),
                    Update_data.payloadfiles.contains(filter),
                    Update_data.description.contains(filter),
                    Up_machine_windows.start_date.contains(filter),
                    Up_machine_windows.end_date.contains(filter),
                )
            )

        count = query.count()

        if start != -1:
            query = query.offset(start)
        if end != 0:
            query = query.limit(end)

        query = query.all()

        result = {"count": count, "datas": []}

        for update, data in query:
            tmp = {
                "title": data.title,
                "description": data.description if data.description is not None else "",
                "update_id": update.update_id if update.update_id is not None else "",
                "package_id": update.update_id if update.update_id is not None else "",
                "kb": update.kb if update.kb is not None else "",
                "start_date": (
                    datetime_handler(update.start_date)
                    if update.start_date is not None
                    else ""
                ),
                "end_date": (
                    datetime_handler(update.end_date)
                    if update.end_date is not None
                    else ""
                ),
                "current_deploy": (
                    update.curent_deploy if update.curent_deploy is not None else 0
                ),
                "required_deploy": (
                    update.required_deploy if update.required_deploy is not None else 0
                ),
            }

            result["datas"].append(tmp)

        return result

    @DatabaseHelper._sessionm
    def get_audit_summary_updates_by_machine(
        self, session, machineid, start, end, filter
    ):
        start = to_int(start, 0)
        machineid = to_int(machineid, 0)
        end = to_int(end, -1)

        query = (
            session.query(Deploy)
            .join(Machines, Machines.jid == Deploy.jidmachine)
            .filter(and_(Deploy.sessionid.contains("update"), Machines.id == machineid))
            .order_by(desc(Deploy.start))
        )

        if filter != "":
            query = query.filter(
                or_(
                    Deploy.title.contains(filter),
                    Deploy.state.contains(filter),
                    Deploy.start.contains(filter),
                    Deploy.startcmd.contains(filter),
                    Deploy.endcmd.contains(filter),
                )
            )
        if start != 0:
            query = query.offset(start)
        if end != -1:
            query = query.limit(end)

        count = query.count()
        query = query.all()

        result = {"count": count, "datas": []}

        for deploy in query:
            tmp = {
                "id": deploy.id,
                "title": deploy.title,
                "jidmachine": deploy.jidmachine,
                "jid_relay": deploy.jid_relay,
                "pathpackage": deploy.pathpackage,
                "state": deploy.state,
                "sessionid": deploy.sessionid,
                "start": datetime_handler(deploy.start),
                "startcmd": datetime_handler(deploy.startcmd),
                "endcmd": datetime_handler(deploy.endcmd),
                "uuid": deploy.inventoryuuid,
                "hostname": deploy.host,
                "user": deploy.user,
                "cmd_id": deploy.command,
                "grp_id": deploy.group_uuid,
                "login": deploy.login,
                "macadress": deploy.macadress,
                "syncthing": deploy.syncthing,
            }
            result["datas"].append(tmp)
        return result

    @DatabaseHelper._sessionm
    def get_count_missing_updates_by_machines(self, session, ids):
        result = {}
        if not ids:
            return result

        ids = "(%s)" % ",".join([str(id) for id in ids])

        sql = f"""
                SELECT
                    uma.id_machine AS id,
                    uma.hostname,
                    CONCAT("UUID", uma.glpi_id) AS uuid,
                    COUNT(DISTINCT CASE WHEN uma.curent_deploy IS NULL OR uma.curent_deploy = 0 THEN uma.update_id END) AS missing,
                    COUNT(DISTINCT CASE WHEN uma.curent_deploy = 1 THEN uma.update_id END) AS inprogress
                FROM up_machine_activated uma
                WHERE uma.id_machine IN {ids}
                GROUP BY uma.id_machine;
        """

        datas = session.execute(sql)

        for element in datas:
            result[element.uuid] = {
                "id": element.id,
                "uuid": element.uuid,
                "hostname": element.hostname,
                "missing": element.missing or 0,
                "inprogress": element.inprogress or 0,
            }

        return result

    @DatabaseHelper._sessionm
    def get_update_kb(self, session, updateid):
        try:
            query = session.query(Update_data).filter(
                Update_data.updateid == updateid)

            result = query.first()
            if query is not None:
                return result.kb
        except Exception as e:
            pass
        return ""

    @DatabaseHelper._sessionm
    def initialisation_module_list_mmc(self, session, listmodules):
        """
        Initialise la table 'mmc_module_actif' en tronquant d'abord son contenu, puis insère de nouveaux modules.

        Args:
            session (sqlalchemy.orm.Session): La session SQLAlchemy active.
            listmodules (list): Une liste de noms de modules à insérer.

        Note:
            Cette méthode va tronquer la table 'mmc_module_actif', supprimant tous les enregistrements.
            Ensuite, elle insérera de nouveaux enregistrements avec 'enable' à 1 et 'informations' à une chaîne vide.

        Example:
            Pour initialiser avec une liste de modules ['module1', 'module2']:

            >>> mmc_module = Mmc_module_actif()
            >>> mmc_module.initialisation_module_list_mmc(session, ['module1', 'module2'])

        """

        session.execute("TRUNCATE TABLE mmc_module_actif")

        if listmodules:
            # Pour chaque nom de module dans la liste, insérer avec enable à 1 et informations à null
            for module in listmodules:
                new_module = Mmc_module_actif(
                    name_module=module, enable=True, informations=""
                )
                session.add(new_module)
            # Commit pour valider les changements
        session.commit()

    @DatabaseHelper._sessionm
    def get_module_list_mmc(self, session, enable=1):
        """
        Renvoie une liste de 'name_module' depuis la table 'mmc_module_actif' selon la valeur de 'enable'.

        Args:
            session (sqlalchemy.orm.Session): La session SQLAlchemy active.
            enable (int, optional): La valeur de 'enable' à considérer (par défaut à 1).

        Returns:
            list: Une liste de 'name_module' correspondant aux critères spécifiés.

        Example:
            Pour obtenir la liste de 'name_module' avec 'enable' à 1:

            >>> mmc_module = Mmc_module_actif()
            >>> modules_actifs = mmc_module.get_module_list_mmc(session)

            Pour obtenir la liste de 'name_module' avec 'enable' à 0:

            >>> modules_inactifs = mmc_module.get_module_list_mmc(session, enable=0)

        """
        if enable not in (0, 1):
            raise ValueError("La valeur de 'enable' doit être soit 0 ou 1.")

        modules = (
            session.query(Mmc_module_actif.name_module)
            .filter(Mmc_module_actif.enable == enable)
            .all()
        )
        return [module[0] for module in modules]

    @DatabaseHelper._sessionm
    def cancel_update(self, session, machineid, updateid):
        machineid = to_int(machineid, 0)
        try:
            update = (
                session.query(Up_machine_windows)
                .filter(
                    and_(
                        Up_machine_windows.id_machine == machineid,
                        Up_machine_windows.update_id == updateid,
                        Up_machine_windows.required_deploy == 1,
                    )
                )
                .first()
            )

            update.required_deploy = None
            update.start_date = None
            update.end_date = None

            history = (
                session.query(Up_history)
                .filter(and_(Up_history.id_machine == machineid, Up_history.update_id))
                .delete()
            )

            session.commit()
            session.flush()
        except Exception as e:
            logging.getLogger().error(e)
            return False

        return True

    @DatabaseHelper._sessionm
    def get_update_history_by_machines(self, session, idmachines):
        if idmachines == []:
            return {}

        query = (
            session.query(Up_history)
            .add_column(Update_data.kb)
            .add_column(Machines.uuid_inventorymachine)
            .filter(
                and_(
                    Up_history.id_machine.in_(idmachines),
                    Deploy.state == "DEPLOYMENT SUCCESS",
                    or_(Up_history.delete_date != None,
                        Up_history.delete_date != 0),
                )
            )
            .join(Update_data, Up_history.update_id == Update_data.updateid)
            .join(Machines, Up_history.id_machine == Machines.id)
            .outerjoin(Deploy, Up_history.id_deploy == Deploy.id)
        )
        query = query.all()
        result = {}
        for element, kb, uuid in query:
            if uuid not in result:
                result[uuid] = [
                    {
                        "updateid": element.update_id,
                        "id_machine": element.id_machine,
                        "kb": kb,
                    }
                ]
            else:
                result[uuid].append(
                    {
                        "updateid": element.update_id,
                        "id_machine": element.id_machine,
                        "kb": kb,
                    }
                )

        return result

    @DatabaseHelper._sessionm
    def get_history_by_update(self, session, updateid):
        query = (
            session.query(Up_history, Update_data, Machines, Glpi_entity)
            .join(Update_data, Update_data.updateid == Up_history.update_id)
            .join(Machines, Up_history.id_machine == Machines.id)
            .join(Glpi_entity, Machines.glpi_entity_id == Glpi_entity.id)
            .filter(Up_history.delete_date is not None)
            .all()
        )

        result = {}

        for hist, data, mach, entity in query:
            result[mach.uuid_inventorymachine] = {
                "id": (
                    int(mach.uuid_inventorymachine.replace("UUID", ""))
                    if mach.uuid_inventorymachine and mach.uuid_inventorymachine.strip()
                    else ""
                ),
                "hostname": mach.hostname,
                "eid": entity.glpi_id if entity.glpi_id is not None else 0,
                "entity": (
                    entity.complete_name if entity.complete_name is not None else ""
                ),
                "kb": "Update(KB%s)" % data.kb,
                "numkb": data.kb,
            }

        return result

    @DatabaseHelper._sessionm
    def get_ad_group_for_lastuser(self, session, login):
        query = (
            session.query(Users_adgroups).filter(
                Users_adgroups.lastuser == login).all()
        )

        result = [element.adname for element in query] if query != None else []
        return result

    @DatabaseHelper._sessionm
    def get_all_ad_groups(self, session):
        query = session.query(Users_adgroups).group_by(
            Users_adgroups.adname).all()

        result = [element.adname for element in query] if query != None else []
        return result

    @DatabaseHelper._sessionm
    def get_all_ad_groups_team(self, session, logins):
        query = (
            session.query(Users_adgroups)
            .filter(Users_adgroups.lastuser.in_(logins))
            .group_by(Users_adgroups.adname)
            .all()
        )

        result = [element.adname for element in query] if query != None else []
        return result

    @DatabaseHelper._sessionm
    def getmachineentityfromjid(self, session, jid):
        """
        Retrieves the machine entity from the specified jid identifier.

        Args:
            session: An active SQLAlchemy session to interact with the database.
            jid (str): The jid identifier of the machine.

        Returns:
            Glpi_entity: The machine entity corresponding to the specified jid identifier, or None if no entity is found.

        Raises:
            None
        """
        query = (
            session.query(Glpi_entity)
            .join(Machines, Glpi_entity.id == Machines.glpi_entity_id)
            .filter(Machines.jid == jid)
            .first()
        )
        return query

    @DatabaseHelper._sessionm
    def get_os_xmpp_update_major_stats(self, session, presence=False):
        """
        Récupère les statistiques de mise à jour majeure des systèmes d'exploitation Windows 10 et Windows 11.

        Args:
            session (sqlalchemy.orm.session.Session): La session de base de données.
            presence (bool, optional): Filtrer uniquement les machines activées si True. Par défaut, True.

        Returns:
            dict: Un dictionnaire contenant les statistiques de mise à jour des systèmes d'exploitation.
        """
        try:
            # Dictionnaire final des résultats
            cols = ["W10to10", "W10to11", "W11to11"]
            results = {"entity": {}}

            # Condition de filtre sur xma.enabled
            presence_filter = "AND xma.enabled = 1" if presence else ""

            # Requête pour le nombre total de machines par entité
            total_os_sql = f"""
                SELECT
                    xe.name AS entity_name,
                    xe.complete_name AS complete_name,
                    COUNT(*) AS count
                FROM
                    xmppmaster.machines xma
                INNER JOIN xmppmaster.glpi_entity xe ON xe.id = xma.glpi_entity_id
                WHERE
                    xma.platform LIKE '%Windows%'
                    {presence_filter}
                GROUP BY xe.id;
            """

            total_os_result = session.execute(total_os_sql).fetchall()
            for row in total_os_result:
                results["entity"].setdefault(
                    row.complete_name, {"count": int(row.count)}
                )

            # Requête pour les statistiques par entité
            entity_sql = f"""
                        SELECT
                            xe.glpi_id as entity_id,
                            xe.name AS entity_name,
                            xe.complete_name AS complete_name,
                            COUNT(*) AS nbwin,
                            CASE
                                WHEN
                                    xma.platform LIKE '%Windows 10%'
                                        AND xma.platform NOT LIKE '%[22H2]'
                                THEN
                                    'W10to10'
                                WHEN
                                    xma.platform LIKE '%Windows 10%'
                                        AND xma.platform LIKE '%[22H2]'
                                THEN
                                    'W10to11'
                                WHEN
                                    xma.platform LIKE '%Windows 11%'
                                        AND xma.platform NOT LIKE '%[24H2]'
                                THEN
                                    'W11to11'
                                WHEN
                                    xma.platform LIKE '%Windows%'
                                        AND xma.platform NOT REGEXP '\[[0-9]{2}H[0-9]\]$'
                                THEN
                                    'winVers_missing'
                                ELSE 'not_win'
                            END AS os
                        FROM
                            xmppmaster.machines xma
                                INNER JOIN
                            xmppmaster.glpi_entity xe ON xe.id = xma.glpi_entity_id
                        WHERE
                            xma.platform LIKE '%Windows%'
                            {presence_filter}
                        GROUP BY xe.id , os
                        ORDER BY xe.complete_name , os;
            """

            entity_result = session.execute(entity_sql).fetchall()
            for row in entity_result:
                # initialisation
                results["entity"].setdefault(row.complete_name, {})
                results["entity"][row.complete_name]["name"] = row.entity_name
                results["entity"][row.complete_name][row.os] = int(row.nbwin)
                results["entity"][row.complete_name]['entity_id'] = int(
                    row.entity_id)
              # Calcul de la conformité
            for entity, data in results["entity"].items():
                total = results["entity"][entity]["count"]
                non_conforme = sum(data.get(key, 0) for key in cols)
                results["entity"][entity]["conformite"] = round(
                    ((non_conforme - total) / total *
                     100) if non_conforme > 0 else 0, 2
                )

            # Copier les clés existantes avant d'itérer
            existing_entities = list(results["entity"].keys())
            for entity in existing_entities:  # Itérer sur la copie des clés
                for col in cols:
                    if col not in results["entity"][entity]:
                        results["entity"][entity][col] = 0
            return results

        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération des statistiques de mise à jour des OS : {str(e)}"
            )
            logger.error(f"Traceback : {traceback.format_exc()}")
            return {}

    @DatabaseHelper._sessionm
    def get_os_update_major_stats_win(self, session, entitylist=None, presence=False):
        """
        Statistiques de mise à jour Windows 10 / 11 (client uniquement).
        Args:
            session: session SQLAlchemy.
            presence: si True, filtre uniquement les machines activées.
        Returns:
            dict: statistiques par entité.
        """
        try:
            results = {"entity": {}}
            presence_filter = "AND mw.enabled = 1" if presence else ""

            # Requête pour récupérer les données brutes
            query = f"""
                SELECT
                    mw.ent_id,
                    e.complete_name,
                    mw.old_version,
                    mw.new_version,
                    mw.oldcode,
                    mw.is_active
                FROM xmppmaster.up_major_win mw
                INNER JOIN xmppmaster.glpi_entity e ON e.glpi_id = mw.ent_id
                WHERE mw.target_name LIKE 'Win%' AND mw.target_name NOT LIKE '%Server%'
                {presence_filter}
            """
            rows = session.execute(query).fetchall()

            # Initialisation des catégories
            categories = ["W10to10", "W10to11", "W11to11", "UPDATED", "non_conforme", "autre_cas"]

            # Traitement des résultats bruts en Python
            for row in rows:
                ent_id = row.ent_id
                ent_name = row.complete_name
                old_version = row.old_version
                new_version = row.new_version
                oldcode = row.oldcode
                is_active = row.is_active
                logger.error(f"old_version{old_version}  new_version{new_version} oldcode {oldcode}")
                # Détermination de la catégorie
                if old_version == "10" and new_version == "10" and not oldcode.startswith('22H2'):
                    category = "W10to10"
                elif old_version == "10" and new_version == "11":

                    if is_active == "False":
                        category = "non_conforme"
                    else:
                        category = "W10to11"

                elif old_version == "11" and not oldcode.startswith('24H2'):
                    category = "W11to11"

                elif old_version == 11 and oldcode.startswith('24H2'):

                    category = "UPDATED"
                else:
                    category = "autre_cas"


                # Mise à jour des résultats
                if ent_name not in results["entity"]:
                    results["entity"][ent_name] = {
                        "entity_id": ent_id,
                        "name": ent_name,
                        "count": 0,
                        "W10to10": 0,
                        "W10to11": 0,
                        "W11to11": 0,
                        "UPDATED": 0,
                        "non_conforme": 0,
                        "autre_cas" : 0,
                        "non_inventorie" : 0
                    }

                results["entity"][ent_name][category] += 1

            # Récupération du nombre total de machines Windows par entité
            total_query = f"""
                            SELECT
                                e.complete_name, COUNT(*) AS count
                            FROM
                                xmppmaster.machines m
                                    inner JOIN
                                xmppmaster.glpi_entity e ON e.id = m.glpi_entity_id
                            WHERE
                                m.platform LIKE 'Microsoft Windows%'
                                AND m.platform NOT LIKE '%Server%' {presence_filter}
                            GROUP BY e.complete_name;
            """
            for row in session.execute(total_query).fetchall():
                ent_name = row.complete_name
                if ent_name in results["entity"]:
                    results["entity"][ent_name]["count"] = row.count

            # Calcul de la conformité et de la complétude
            for ent_data in results["entity"].values():
                total = int(ent_data["count"])

                definie = sum(ent_data[c] for c in ["W10to10",
                                                    "W10to11",
                                                    "W11to11",
                                                    "UPDATED",
                                                    "non_conforme",
                                                    "autre_cas"])

                ent_data["conformite"] = round(((ent_data['UPDATED']) / definie * 100), 2) if definie else 0.0
                ent_data["non_inventorie"] = total - sum(ent_data[c] for c in [ "W10to10",
                                                                                "W10to11",
                                                                                "W11to11",
                                                                                "UPDATED",
                                                                                "non_conforme",
                                                                                "autre_cas"])

            return results

        except Exception as e:
            logger.error(f"Erreur stats Windows : {e}")
            logger.error(traceback.format_exc())
            return {}


    @DatabaseHelper._sessionm
    def get_os_update_major_stats_win_serv(self, session, entitylist=None, presence=False):
        """
        Statistiques de mise à jour Windows 10 / 11 (client uniquement).
        Args:
            session: session SQLAlchemy.
            presence: si True, filtre uniquement les machines activées.
        Returns:
            dict: statistiques par entité.
        """
        try:
            results = {"entity": {}}
            presence_filter = "AND mw.enabled = 1" if presence else ""

            # Requête pour récupérer les données brutes
            query = f"""
                SELECT
                    mw.ent_id,
                    e.complete_name,
                    mw.old_version,
                    mw.new_version,
                    mw.oldcode,
                    mw.is_active
                FROM xmppmaster.up_major_win mw
                INNER JOIN xmppmaster.glpi_entity e ON e.glpi_id = mw.ent_id
                WHERE mw.platform LIKE 'Microsoft Windows Server%'
                {presence_filter}
            """
            rows = session.execute(query).fetchall()

            # Initialisation des catégories
            categories = ["MS25toMS25", "MS19toMS25", "MS16toMS25","MS12toMS25" "UPDATED", "non_conforme", "autre_cas"]
            # Traitement des résultats bruts en Python
            for row in rows:
                ent_id = row.ent_id
                ent_name = row.complete_name
                old_version = row.old_version
                new_version = row.new_version
                oldcode = row.oldcode
                is_active = row.is_active
                logger.error(f"old_version{old_version}  new_version{new_version} oldcode {oldcode}")
                # Détermination de la catégorie
                if old_version == "MSO12" :
                    if is_active == "False":
                        category = "non_conforme"
                    else:
                        category = "MS12toMS25"

                if old_version == "MSO16" :
                    if is_active == "False":
                        category = "non_conforme"
                    else:
                        category = "MS16toMS25"

                elif old_version == "MSO19":
                    if is_active == "False":
                        category = "non_conforme"
                    else:
                        category = "MS19toMS25"

                elif old_version == "MSO25" and not oldcode.startswith('24H2'):
                    category = "MS25toMS25"

                elif old_version == "MSO25" and oldcode.startswith('24H2'):
                    category = "UPDATED"
                else:
                    category = "autre_cas"


                # Mise à jour des résultats
                if ent_name not in results["entity"]:
                    results["entity"][ent_name] = {
                        "entity_id": ent_id,
                        "name": ent_name,
                        "count": 0,
                        "MS12toMS25": 0,
                        "MS16toMS25": 0,
                        "MS19toMS25": 0,
                        "MS25toMS25": 0,
                        "UPDATED": 0,
                        "non_conforme": 0,
                        "autre_cas" : 0,
                        "non_inventorie" : 0
                    }

                results["entity"][ent_name][category] += 1

            # Récupération du nombre total de machines Windows par entité
            total_query = f"""
                            SELECT
                                e.complete_name, COUNT(*) AS count
                            FROM
                                xmppmaster.machines m
                                    inner JOIN
                                xmppmaster.glpi_entity e ON e.id = m.glpi_entity_id
                            WHERE
                                m.platform LIKE 'Microsoft Windows Server%' {presence_filter}
                            GROUP BY e.complete_name;
            """
            for row in session.execute(total_query).fetchall():
                ent_name = row.complete_name
                if ent_name in results["entity"]:
                    results["entity"][ent_name]["count"] = row.count

            # Calcul de la conformité et de la complétude
            for ent_data in results["entity"].values():
                total = int(ent_data["count"])

                definie = sum(ent_data[c] for c in ["MS12toMS25",
                                                    "MS16toMS25",
                                                    "MS19toMS25",
                                                    "MS25toMS25",
                                                    "UPDATED",
                                                    "non_conforme",
                                                    "autre_cas"])

                ent_data["conformite"] = round(((ent_data['UPDATED']) / definie * 100), 2) if definie else 0.0
                ent_data["non_inventorie"] = total - sum(ent_data[c] for c in [ "MS12toMS25",
                                                                                "MS16toMS25",
                                                                                "MS19toMS25",
                                                                                "MS25toMS25",
                                                                                "UPDATED",
                                                                                "non_conforme",
                                                                                "autre_cas"])

            return results

        except Exception as e:
            logger.error(f"Erreur stats Windows : {e}")
            logger.error(traceback.format_exc())
            return {}

    @DatabaseHelper._sessionm
    def get_os_update_major_stats(self, session, presence=False):
        """
        Récupère les statistiques de mise à jour des systèmes d'exploitation Windows 10 et Windows 11,
        en excluant les Windows Server.

        Args:
            session (sqlalchemy.orm.session.Session): La session de base de données.
            presence (bool, optional): Si True, filtre uniquement les machines activées. Par défaut False.

        Returns:
            dict: Un dictionnaire contenant les statistiques par entité.
        """
        try:
            results = {"entity": {}}
            cols = ["W10to10", "W10to11", "W11to11", "UPDATED", "undefined"]

            # Filtre de présence
            presence_filter = "AND xma.enabled = 1" if presence else ""

            # =========================
            # 1 Total des machines Windows non Server
            # =========================
            total_os_sql = f"""
                SELECT
                    xe.id AS entity_id,
                    xe.name AS entity_name,
                    xe.complete_name AS complete_name,
                    COUNT(*) AS count
                FROM
                    xmppmaster.machines AS xma
                INNER JOIN xmppmaster.glpi_entity AS xe
                    ON xe.id = xma.glpi_entity_id
                WHERE
                    xma.platform LIKE '%Windows%'
                    AND xma.platform NOT LIKE '%Server%'
                    {presence_filter}
                GROUP BY xe.id, xe.name, xe.complete_name;
            """

            for row in session.execute(total_os_sql):
                results["entity"][row.complete_name] = {
                    "entity_id": int(row.entity_id),
                    "name": row.entity_name,
                    "count": int(row.count)
                }

            # =========================
            # 2 Statistiques de mise à jour par entité
            # =========================
            entity_sql = f"""
                SELECT
                    ent_id,
                    entity AS entity_name,
                    entity AS complete_name,
                    COUNT(*) AS nbwin,
                    CASE
                        WHEN old_version = 10 AND new_version = 10 AND oldcode NOT LIKE '22H2' THEN 'W10to10'
                        WHEN old_version = 10 AND new_version = 11 THEN 'W10to11'
                        WHEN old_version = 11 AND oldcode NOT LIKE '24H2' THEN 'W11to11'
                        WHEN old_version = new_version AND oldcode = newcode THEN 'UPDATED'
                        ELSE 'undefined'
                    END AS os
                FROM
                    xmppmaster.up_machine_major_windows
                WHERE
                    old_version IS NOT NULL
                    AND new_version IS NOT NULL
                    {presence_filter}
                GROUP BY ent_id, entity, os
                ORDER BY complete_name, os;
            """

            for row in session.execute(entity_sql):
                entity_data = results["entity"].setdefault(
                    row.complete_name,
                    {"entity_id": int(row.ent_id), "name": row.entity_name, "count": 0}
                )
                entity_data[row.os] = int(row.nbwin)

            # =========================
            # 3 Calcul des conformités et complétude
            # =========================
            for entity_name, data in results["entity"].items():
                total = data.get("count", 0)

                definie = sum(data.get(c, 0) for c in cols if c != "undefined")
                non_conforme = sum(data.get(c, 0) for c in ["W10to10", "W10to11", "W11to11"])
                undefined = max(total - definie, 0)

                data["definie"] = definie
                data["undefined"] = undefined
                data["conformite"] = (
                    round(((definie - non_conforme) / definie * 100), 2)
                    if definie > 0 else 0.0
                )

                # Ajouter les clés manquantes pour cohérence
                for col in cols:
                    data.setdefault(col, 0)

            logger.info(f"OS update stats calculées pour {len(results['entity'])} entités.")
            return results

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques OS : {e}")
            logger.error(f"Traceback : {traceback.format_exc()}")
            return {}


    @DatabaseHelper._sessionm
    def get_os_update_major_stats2(self, session, presence=False):
        """
        Statistiques de mise à jour Windows 10 / 11 (client uniquement).

        Args:
            session (sqlalchemy.orm.session.Session): session SQLAlchemy.
            presence (bool): si True, filtre uniquement les machines activées.

        Returns:
            dict: statistiques par entité.
        """
        try:
            results = {"entity": {}}
            presence_filter = "AND mw.enabled = 1" if presence else ""

            # Catégories Windows
            categories = ["W10to10", "W10to11", "W11to11", "UPDATED", "undefined"]

            # Requête principale avec toutes les catégories
            categories_cte = " UNION ALL ".join([f"SELECT '{c}' AS category" for c in categories])
            entity_sql = f"""
                WITH categories AS ({categories_cte}),
                data AS (
                    SELECT
                        mw.ent_id,
                        e.complete_name,
                        CASE
                            WHEN mw.old_version = 10 AND mw.new_version = 10 AND mw.oldcode NOT LIKE '22H2' THEN 'W10to10'
                            WHEN mw.old_version = 10 AND mw.new_version = 11 AND mw.is_active != 'False' THEN 'W10to11'
                            WHEN mw.old_version = 10 AND mw.new_version = 11 AND mw.is_active = 'False' THEN 'W10to11'
                            WHEN mw.old_version = 11 AND mw.oldcode NOT LIKE '24H2' THEN 'W11to11'
                            WHEN mw.old_version = 11 AND mw.oldcode LIKE '24H2' THEN 'UPDATED'
                            ELSE 'undefined'
                        END AS category
                    FROM xmppmaster.up_major_win mw
                    INNER JOIN xmppmaster.glpi_entity e ON e.glpi_id = mw.ent_id
                    WHERE mw.target_name LIKE 'Win%' AND mw.target_name NOT LIKE '%Server%'
                    {presence_filter}
                )
                SELECT
                    COALESCE(d.complete_name, e.complete_name) AS complete_name,
                    COALESCE(d.ent_id, e.glpi_id) AS ent_id,
                    c.category,
                    COUNT(d.category) AS nb
                FROM categories c
                LEFT JOIN data d ON d.category = c.category
                LEFT JOIN xmppmaster.glpi_entity e ON e.glpi_id = COALESCE(d.ent_id, e.glpi_id)
                GROUP BY COALESCE(d.ent_id, e.glpi_id), COALESCE(d.complete_name, e.complete_name), c.category
                ORDER BY complete_name, category;
            """

            # Exécution de la requête
            rows = session.execute(entity_sql).fetchall()

            # Initialisation du dictionnaire
            for row in rows:
                ent = row.complete_name
                results["entity"].setdefault(ent, {"count": 0})
                results["entity"][ent].setdefault("entity_id", int(row.ent_id))
                results["entity"][ent].setdefault("name", ent)
                results["entity"][ent][row.category] = int(row.nb)

            # Récupérer le nombre total de machines Windows par entité
            total_sql = f"""
                SELECT
                    e.complete_name,
                    COUNT(*) AS count
                FROM xmppmaster.machines m
                INNER JOIN xmppmaster.glpi_entity e ON e.glpi_id = m.glpi_entity_id
                WHERE m.platform LIKE '%Windows%' {presence_filter}
                GROUP BY e.complete_name;
            """
            for row in session.execute(total_sql).fetchall():
                ent = row.complete_name
                results["entity"].setdefault(ent, {})
                results["entity"][ent]["count"] = int(row.count)

            # Calcul conformité et complétude
            for ent, data in results["entity"].items():
                total = data.get("count", 0)
                definie = sum(data.get(c, 0) for c in categories if c != "undefined")
                undefined = max(total - definie, 0)
                non_conforme = sum(data.get(c, 0) for c in ["W10to10", "W10to11", "W11to11"])
                data["definie"] = definie
                data["undefined"] = undefined
                data["conformite"] = round(((definie - non_conforme) / definie * 100), 2) if definie else 0.0

                # Assurer que toutes les catégories existent
                for c in categories:
                    data.setdefault(c, 0)

            return results

        except Exception as e:
            logger.error(f"Erreur stats Windows : {e}")
            logger.error(traceback.format_exc())
            return {}


    @DatabaseHelper._sessionm
    def get_os_xmpp_update_major_stats3(self, session, presence=False):
        """
        Récupère les statistiques de mise à jour majeure des systèmes d'exploitation Windows 10 et Windows 11.

        Args:
            session (sqlalchemy.orm.session.Session): La session de base de données.
            presence (bool, optional): Filtrer uniquement les machines activées si True. Par défaut, True.

        Returns:
            dict: Un dictionnaire contenant les statistiques de mise à jour des systèmes d'exploitation.
        """
        try:
            # Dictionnaire final des résultats
            cols = ["W10to10", "W10to11", "W11to11"]
            results = {"entity": {}}

            # Condition de filtre sur xma.enabled
            presence_filter = "AND xma.enabled = 1" if presence else ""

            # Requête pour le nombre total de machines par entité
            total_os_sql = f"""
                SELECT
                    xe.name AS entity_name,
                    xe.complete_name AS complete_name,
                    COUNT(*) AS count
                FROM
                    xmppmaster.machines xma
                INNER JOIN xmppmaster.glpi_entity xe ON xe.id = xma.glpi_entity_id
                WHERE
                    xma.platform LIKE '%Windows%'
                    {presence_filter}
                GROUP BY xe.id;
            """

            total_os_result = session.execute(total_os_sql).fetchall()
            for row in total_os_result:
                results["entity"].setdefault(
                    row.complete_name, {"count": int(row.count)}
                )

            # Requête pour les statistiques par entité
            entity_sql = f"""
                        SELECT
                            xe.glpi_id as entity_id,
                            xe.name AS entity_name,
                            xe.complete_name AS complete_name,
                            COUNT(*) AS nbwin,
                            CASE
                                WHEN
                                    xma.platform LIKE '%Windows 10%'
                                        AND xma.platform NOT LIKE '%[22H2]'
                                THEN
                                    'W10to10'
                                WHEN
                                    xma.platform LIKE '%Windows 10%'
                                        AND xma.platform LIKE '%[22H2]'
                                THEN
                                    'W10to11'
                                WHEN
                                    xma.platform LIKE '%Windows 11%'
                                        AND xma.platform NOT LIKE '%[24H2]'
                                THEN
                                    'W11to11'
                                WHEN
                                    xma.platform LIKE '%Windows%'
                                        AND xma.platform NOT REGEXP '\[[0-9]{2}H[0-9]\]$'
                                THEN
                                    'winVers_missing'
                                ELSE 'not_win'
                            END AS os
                        FROM
                            xmppmaster.machines xma
                                INNER JOIN
                            xmppmaster.glpi_entity xe ON xe.id = xma.glpi_entity_id
                        WHERE
                            xma.platform LIKE '%Windows%'
                            {presence_filter}
                        GROUP BY xe.id , os
                        ORDER BY xe.complete_name , os;
            """

            entity_result = session.execute(entity_sql).fetchall()
            for row in entity_result:
                # initialisation
                results["entity"].setdefault(row.complete_name, {})
                results["entity"][row.complete_name]["name"] = row.entity_name
                results["entity"][row.complete_name][row.os] = int(row.nbwin)
                results["entity"][row.complete_name]['entity_id'] = int(
                    row.entity_id)
            # Calcul de la conformité
            for entity, data in results["entity"].items():
                total = results["entity"][entity]["count"]
                non_conforme = sum(data.get(key, 0) for key in cols)
                results["entity"][entity]["conformite"] = round(
                    ((non_conforme - total) / total *
                     100) if non_conforme > 0 else 0, 2
                )

            # Copier les clés existantes avant d'itérer
            existing_entities = list(results["entity"].keys())
            for entity in existing_entities:  # Itérer sur la copie des clés
                for col in cols:
                    if col not in results["entity"][entity]:
                        results["entity"][entity][col] = 0
            return results

        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération des statistiques de mise à jour des OS : {str(e)}"
            )
            logger.error(f"Traceback : {traceback.format_exc()}")
            return {}


    @DatabaseHelper._sessionm
    def get_os_update_major_stats1(self, session, typeos="win", presence=False):
        """
        Récupère les statistiques de mise à jour des OS Windows (client) ou Windows Server.
        Affiche toutes les catégories même si aucune machine ne correspond (nb = 0).
        Calcule également le nombre total de machines par entité pour évaluer la complétude.

        Args:
            session (sqlalchemy.orm.session.Session): session SQLAlchemy.
            typeos (str): "win" pour Windows client, "MSO" pour Windows Server.
            presence (bool): si True, filtre les machines activées (enabled = 1).
        """
        try:
            results = {"entity": {}}
            presence_filter = "AND xma.enabled = 1" if presence else ""

            # =========================
            # 1️⃣ Sélection du filtre OS
            # =========================
            if typeos == "win":
                platform_filter = "xma.platform LIKE '%Windows%' AND xma.platform NOT LIKE '%Server%'"
                os_filter = "mw.target_name LIKE 'Win%' AND mw.target_name NOT LIKE '%Server%'"
                categories = ["W10to10", "W10to11", "W10to11_BLOCKED", "W11to11", "UPDATED", "undefined"]
                case_stmt = """
                    CASE
                        WHEN mw.old_version = 10 AND mw.new_version = 10 AND mw.oldcode NOT LIKE '22H2' THEN 'W10to10'
                        WHEN mw.old_version = 10 AND mw.new_version = 11 AND mw.is_active != 'False' THEN 'W10to11'
                        WHEN mw.old_version = 10 AND mw.new_version = 11 AND mw.is_active = 'False' THEN 'W10to11_BLOCKED'
                        WHEN mw.old_version = 11 AND mw.oldcode NOT LIKE '24H2' THEN 'W11to11'
                        WHEN mw.old_version = 11 AND mw.oldcode LIKE '24H2' THEN 'UPDATED'
                        ELSE 'undefined'
                    END AS category
                """
            elif typeos == "MSO":
                platform_filter = "xma.platform LIKE '%Server%'"
                os_filter = "mw.target_name LIKE '%Win_Server%'"
                categories = ["S12to25", "S16to25", "S19to25", "S22to25", "S25to25", "S_UPDATED", "undefined"]
                case_stmt = """
                    CASE
                        WHEN mw.old_version = 'MOS12' AND mw.new_version LIKE 'MOS25' AND mw.is_active != 'False' THEN 'S12to25'
                        WHEN mw.old_version = 'MOS16' AND mw.new_version LIKE 'MOS25' AND mw.is_active != 'False' THEN 'S16to25'
                        WHEN mw.old_version = 'MOS19' AND mw.new_version LIKE 'MOS25' AND mw.is_active != 'False' THEN 'S19to25'
                        WHEN mw.old_version = 'MOS22' AND mw.new_version LIKE 'MOS25' AND mw.is_active != 'False' THEN 'S22to25'
                        WHEN mw.old_version = 'MOS25' AND mw.new_version LIKE 'MOS25' AND mw.oldcode NOT LIKE '24H2' THEN 'S25to25'
                        WHEN mw.old_version = 'MOS25' AND mw.new_version LIKE 'MOS25' AND mw.oldcode LIKE '24H2' THEN 'S_UPDATED'
                        ELSE 'undefined'
                    END AS category
                """
            else:
                raise ValueError(f"typeos inconnu : {typeos}")

            # =========================
            # 2️⃣ Total des machines par entité
            # =========================
            total_os_sql = f"""
                SELECT
                    xe.id AS entity_id,
                    xe.name AS entity_name,
                    xe.complete_name AS complete_name,
                    COUNT(*) AS count
                FROM xmppmaster.machines AS xma
                INNER JOIN xmppmaster.glpi_entity AS xe
                    ON xe.glpi_id = xma.glpi_entity_id
                WHERE {platform_filter} {presence_filter}
                GROUP BY xe.id, xe.name, xe.complete_name;
            """
            for row in session.execute(total_os_sql):
                results["entity"][row.complete_name] = {
                    "entity_id": int(row.entity_id),
                    "name": row.entity_name,
                    "count": int(row.count),
                }

            # =========================
            # 3️⃣ Statistiques avec toutes les catégories
            # =========================
            categories_cte = " UNION ALL ".join([f"SELECT '{c}' AS category" for c in categories])
            entity_sql = f"""
                WITH categories AS ({categories_cte}),
                data AS (
                    SELECT
                        mw.ent_id,
                        e.complete_name,
                        {case_stmt}
                    FROM xmppmaster.up_major_win mw
                    INNER JOIN xmppmaster.glpi_entity e ON e.glpi_id = mw.ent_id
                    WHERE {os_filter}
                )
                SELECT
                    COALESCE(d.ent_id, 0) AS ent_id,
                    COALESCE(d.complete_name, 'UNKNOWN') AS complete_name,
                    c.category,
                    COUNT(d.category) AS nb
                FROM categories c
                LEFT JOIN data d ON d.category = c.category
                GROUP BY d.ent_id, d.complete_name, c.category
                ORDER BY d.complete_name, c.category;
            """
            logger.debug(f"Requête SQL exécutée : {entity_sql}")

            for row in session.execute(entity_sql):
                entity_data = results["entity"].setdefault(
                    row.complete_name,
                    {"entity_id": int(row.ent_id), "name": row.complete_name, "count": 0},
                )
                entity_data[row.category] = int(row.nb)

            # =========================
            # 4️⃣ Calcul conformité et complétude
            # =========================
            for name, data in results["entity"].items():
                total = data.get("count", 0)
                definie = sum(v for k, v in data.items() if k not in ("entity_id", "name", "count"))
                undefined = max(total - definie, 0)
                non_conforme = sum(
                    v for k, v in data.items()
                    if any(tag in k for tag in categories if tag not in ["UPDATED", "S_UPDATED", "undefined"])
                )
                data["definie"] = definie
                data["undefined"] = undefined
                data["conformite"] = round(((definie - non_conforme) / definie * 100), 2) if definie else 0.0
                data["completeness_rate"] = round(((total - undefined) / total * 100), 2) if total else 0.0

            return results

        except Exception as e:
            logger.error(f"Erreur stats OS ({typeos}) : {e}")
            logger.error(traceback.format_exc())
            return {}

    @DatabaseHelper._sessionm
    def get_os_update_major_statsbon(self, session, presence=False):
        """
        Récupère les statistiques de mise à jour des systèmes d'exploitation Windows 10 et Windows 11,
        en excluant les Windows Server.

        Args:
            session (sqlalchemy.orm.session.Session): La session de base de données.
            presence (bool, optional): Si True, filtre uniquement les machines activées. Par défaut False.

        Returns:
            dict: Un dictionnaire contenant les statistiques par entité.
        """
        try:
            results = {"entity": {}}
            cols = ["W10to10", "W10to11", "W11to11", "UPDATED", "undefined"]

            # Filtre de présence
            presence_filter = "AND xma.enabled = 1" if presence else ""

            # =========================
            # 1 Total des machines Windows non Server
            # =========================
            total_os_sql = f"""
                SELECT
                    xe.id AS entity_id,
                    xe.name AS entity_name,
                    xe.complete_name AS complete_name,
                    COUNT(*) AS count
                FROM
                    xmppmaster.machines AS xma
                INNER JOIN xmppmaster.glpi_entity AS xe
                    ON xe.id = xma.glpi_entity_id
                WHERE
                    xma.platform LIKE '%Windows%'
                    AND xma.platform NOT LIKE '%Server%'
                    {presence_filter}
                GROUP BY xe.id, xe.name, xe.complete_name;
            """

            for row in session.execute(total_os_sql):
                results["entity"][row.complete_name] = {
                    "entity_id": int(row.entity_id),
                    "name": row.entity_name,
                    "count": int(row.count)
                }

            # =========================
            # 2 Statistiques de mise à jour par entité
            # =========================
            entity_sql = f"""
                SELECT
                    ent_id,
                    entity AS entity_name,
                    entity AS complete_name,
                    COUNT(*) AS nbwin,
                    CASE
                        WHEN old_version = 10 AND new_version = 10 AND oldcode NOT LIKE '22H2' THEN 'W10to10'
                        WHEN old_version = 10 AND new_version = 11 THEN 'W10to11'
                        WHEN old_version = 11 AND oldcode NOT LIKE '24H2' THEN 'W11to11'
                        WHEN old_version = new_version AND oldcode = newcode THEN 'UPDATED'
                        ELSE 'undefined'
                    END AS os
                FROM
                    xmppmaster.up_machine_major_windows
                WHERE
                    old_version IS NOT NULL
                    AND new_version IS NOT NULL
                    {presence_filter}
                GROUP BY ent_id, entity, os
                ORDER BY complete_name, os;
            """

            for row in session.execute(entity_sql):
                entity_data = results["entity"].setdefault(
                    row.complete_name,
                    {"entity_id": int(row.ent_id), "name": row.entity_name, "count": 0}
                )
                entity_data[row.os] = int(row.nbwin)

            # =========================
            # 3 Calcul des conformités et complétude
            # =========================
            for entity_name, data in results["entity"].items():
                total = data.get("count", 0)

                definie = sum(data.get(c, 0) for c in cols if c != "undefined")
                non_conforme = sum(data.get(c, 0) for c in ["W10to10", "W10to11", "W11to11"])
                undefined = max(total - definie, 0)

                data["definie"] = definie
                data["undefined"] = undefined
                data["conformite"] = (
                    round(((definie - non_conforme) / definie * 100), 2)
                    if definie > 0 else 0.0
                )

                # Ajouter les clés manquantes pour cohérence
                for col in cols:
                    data.setdefault(col, 0)

            logger.info(f"OS update stats calculées pour {len(results['entity'])} entités.")
            return results

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques OS : {e}")
            logger.error(f"Traceback : {traceback.format_exc()}")
            return {}


    @DatabaseHelper._sessionm
    def get_os_xmpp_update_major_details(self,
                                         session,
                                         entity_id,
                                         filter="",
                                         start=0,
                                         limit=-1,
                                         colonne=True):
        """
        Récupère les détails des machines avec des systèmes d'exploitation Windows à partir de la base de données XMPPMaster.

        Cette fonction exécute une requête SQL pour récupérer des informations sur les machines
        avec des systèmes d'exploitation Windows, y compris une colonne calculée 'os' qui
        catégorise la version du système d'exploitation et indique les mises à jour majeures
        nécessaires entre la version actuelle et la prochaine mise à jour majeure. Les résultats
        peuvent être retournés soit dans un format détaillé ligne par ligne, soit dans un format
        en colonnes, selon le paramètre 'colonne'.

        Paramètres :
            session (Session) : Objet de session SQLAlchemy pour l'interaction avec la base de données.
            entity_id (int) : L'ID de l'entité pour filtrer les résultats.
            filter (str) : Critères de filtrage supplémentaires pour filtrer par nom de machine.
            start (int) : Le décalage pour commencer à retourner les lignes.
            limit (int) : Le nombre maximum de lignes à retourner. Si -1, pas de limitation.
            colonne (bool) : Si True, retourne les résultats dans un format en colonnes. La valeur par défaut est True.

        Retourne :
            dict : Un dictionnaire contenant le nombre de lignes correspondantes et soit
                   des résultats détaillés ligne par ligne, soit des résultats en colonnes,
                   selon le paramètre 'colonne'. La colonne 'update' indique les mises à jour majeures
                   nécessaires, telles que 'W10to10' pour une mise à jour entre versions de Windows 10,
                   'W10to11' pour une mise à jour de Windows 10 vers Windows 11, et 'W11to11' pour une
                   mise à jour entre versions de Windows 11.
        """

        # Base SQL query
        total_os_sql = '''
            SELECT
                SQL_CALC_FOUND_ROWS
                xma.id AS id_machine,
                xma.hostname AS machine,
                xma.platform AS platform,
                -- xe.glpi_id AS entity_id,
                -- xe.name AS entity_name,
                -- xe.complete_name AS complete_name,
                CASE
                    WHEN xma.platform REGEXP '\\\\[([0-9]{2}H[0-9])\\\\]$' THEN
                        SUBSTRING_INDEX(SUBSTRING_INDEX(xma.platform, '[', -1), ']', 1)
                    ELSE NULL
                END AS version,
                CASE
                    WHEN xma.platform LIKE '%Windows 10%' AND xma.platform NOT LIKE '%[22H2]' THEN 'W10to10'
                    WHEN xma.platform LIKE '%Windows 10%' AND xma.platform LIKE '%[22H2]' THEN 'W10to11'
                    WHEN xma.platform LIKE '%Windows 11%' AND xma.platform NOT LIKE '%[24H2]' THEN 'W11to11'
                    WHEN xma.platform LIKE '%Windows%' AND xma.platform NOT REGEXP '[[0-9]{2}H[0-9]]$' THEN 'winVers_missing'
                    ELSE 'not_win'
                END AS 'update'
            FROM
                xmppmaster.machines xma
                INNER JOIN xmppmaster.glpi_entity xe ON xe.id = xma.glpi_entity_id
            WHERE
                xma.platform LIKE '%Windows%' AND xe.glpi_id = :entity_id
        '''
        # Add filter condition if filter is not empty
        if filter:
            total_os_sql += " AND xma.hostname LIKE :filter"

        # Add ORDER BY and LIMIT/OFFSET if limit is not -1
        total_os_sql += " ORDER BY xma.hostname "
        if limit != -1:
            logger.error("limit %s " % limit)
            total_os_sql += " LIMIT :limit OFFSET :start"

        # Convert to text for parameter binding
        total_os_sql = text(total_os_sql)

        # Log the SQL query with parameters
        logger.debug("Executing SQL query: %s", total_os_sql)
        logger.debug("With parameters: entity_id=%s, filter=%s, limit=%s, start=%s",
                     entity_id, f"%{filter}%", limit, start)

        # Execute the SQL query with parameters
        entity_result = session.execute(total_os_sql, {
            'entity_id': entity_id,
            'filter': f"%{filter}%",
            'limit': limit,
            'start': start
        }).fetchall()

        # Count the total number of matching elements using FOUND_ROWS()
        sql_count = text("SELECT FOUND_ROWS();")
        ret_count = session.execute(sql_count).scalar()

        # Extract common fields from the first row
        # common_entity_id = entity_result[0].entity_id if entity_result else ""
        # common_entity_name = entity_result[0].entity_name if entity_result else ""
        # common_complete_name = entity_result[0].complete_name if entity_result else ""

        # Prepare the result dictionary with the count of matching rows and common fields
        result = {
            'nb_machine': ret_count,
            # 'entity_id': common_entity_id,
            # 'entity_name': common_entity_name,
            # 'complete_name': common_complete_name
        }

        if colonne:
            # If colonne is True, return results in columnar format
            result.update({
                'id_machine': [row.id_machine if row.id_machine is not None else "" for row in entity_result],
                'machine': [row.machine if row.machine is not None else "" for row in entity_result],
                'platform': [row.platform if row.platform is not None else "" for row in entity_result],
                'version': [row.version if row.version is not None else "" for row in entity_result],
                'update': [row.update if row.update is not None else "" for row in entity_result]
            })
        else:
            # If colonne is False, return detailed results in row-wise format
            result['details'] = [
                {
                    'id_machine': row.id_machine if row.id_machine is not None else "",
                    'machine': row.machine if row.machine is not None else "",
                    'platform': row.platform if row.platform is not None else "",
                    'version':  row.version if row.version is not None else "",
                    'update': row.update if row.update is not None else ""
                }
                for row in entity_result
            ]

        return result

    @DatabaseHelper._sessionm
    def get_outdated_major_os_updates_by_entity(self,
                                                session,
                                                entity_id,
                                                typeaction="windows",
                                                start=0,
                                                limit=-1,
                                                filter="",
                                                colonne=True):
        """
        Récupère les informations des machines dont les mises à jour majeures du système d'exploitation sont obsolètes ou déconseillées,
        avec la possibilité de filtrer par entité, type de plateforme (Windows ou Windows Server), et nom d'hôte, ainsi que de paginer les résultats.

        Cette fonction exécute une requête SQL pour identifier les machines nécessitant une mise à jour majeure de leur système d'exploitation,
        en tenant compte du type de plateforme (Windows standard ou Windows Server) selon le paramètre `typeaction`.
        Les résultats peuvent être retournés soit dans un format détaillé ligne par ligne, soit dans un format en colonnes.

        Paramètres :
            session (Session) : Objet de session SQLAlchemy pour l'interaction avec la base de données.
            entity_id (int) : ID de l'entité pour filtrer les résultats. Si None ou -1, toutes les entités sont incluses.
            typeaction (str) : Type de machines à filtrer :
                - "windows" : Exclut les machines dont la plateforme (mx.platform) contient "Microsoft Windows Server".
                - "serverwin" : Inclut uniquement les machines dont la plateforme (mx.platform) contient "Microsoft Windows Server".
            start (int) : Index de départ pour la pagination.
            limit (int) : Nombre maximum de lignes à retourner. Si -1, aucune limite n'est appliquée.
            filter (str) : Filtre optionnel sur le nom d'hôte (hostname).
            colonne (bool) : Si True, retourne les données par colonne. Sinon, retourne les données par ligne.

        Retourne :
            dict : Un dictionnaire contenant :
                - 'nb_total_element' : Nombre total de machines correspondantes (avant pagination).
                - 'nb_element' : Nombre de machines retournées dans cette requête.
                - Si 'colonne' est True : Un dictionnaire où chaque clé est un nom de colonne et chaque valeur est une liste des valeurs de cette colonne.
                - Si 'colonne' est False : Une liste de dictionnaires, chaque dictionnaire représentant une ligne de résultats avec les clés suivantes :
                    'xmpp_id', 'glpi_id', 'ent_id', 'hostname', 'enabled', 'jid', 'serial', 'platform', 'name', 'comment', 'entity', 'lang_code', 'iso_filename', 'package_uuid', 'old_version', 'new_version', 'oldcode', 'newcode', 'isolang'.
        """
        sql = '''
            SELECT SQL_CALC_FOUND_ROWS
                mx.id AS xmpp_id,
                m.id AS glpi_id,
                e.id AS ent_id,
                mx.hostname,
                mx.enabled,
                mx.jid,
                mx.uuid_serial_machine AS serial,
                mx.platform AS platform,
                s.name,
                s.comment,
                e.completename AS entity,
                lc.lang_code,
                lc.iso_filename,
                lc.package_uuid,
                SUBSTRING(s.name, LOCATE('_', s.name) + 1, LOCATE('@', s.name) - LOCATE('_', s.name) - 1) AS old_version,
                SUBSTRING_INDEX(s.name, '-', -1) AS new_version,
                SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1) AS oldcode,
                SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 5), '@', -1), '_', 2), '_', -1) AS newcode,
                SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 3), '@', -1) AS isolang
            FROM xmppmaster.local_glpi_items_softwareversions si
            JOIN xmppmaster.local_glpi_softwareversions sv ON si.softwareversions_id = sv.id
            JOIN xmppmaster.local_glpi_machines m ON si.items_id = m.id
            JOIN xmppmaster.local_glpi_softwares s ON sv.softwares_id = s.id
            JOIN xmppmaster.local_glpi_entities e ON e.id = m.entities_id
            JOIN xmppmaster.machines mx ON NULLIF(REPLACE(mx.uuid_inventorymachine, 'UUID', ''),'') = si.items_id
            JOIN xmppmaster.up_packages_major_Lang_code lc
                ON lc.lang_code = SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 3), '@', -1)
                AND lc.major = SUBSTRING(s.name, LENGTH(s.name) - LOCATE('-', REVERSE(s.name)) + 2)
            WHERE
                SUBSTRING_INDEX(s.name, '-', -1) > 10
                AND (:entity_id IS NULL OR :entity_id = -1 OR e.id = :entity_id)
                AND s.name LIKE 'Medulla\_%'
                AND (
                    SUBSTRING(s.name, LOCATE('_', s.name) + 1, LOCATE('@', s.name) - LOCATE('_', s.name) - 1) != SUBSTRING_INDEX(s.name, '@', -1)
                    OR SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1) != SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 5), '@', -1), '_', 2), '_', -1)
                )
                AND (
                    s.name NOT LIKE '%False%'
                    OR NOT SUBSTRING_INDEX(s.name, '-', -1) != '11'
                )
        '''

        # Ajouter la condition sur typeaction
        if typeaction == "windows":
            sql += " AND mx.platform NOT LIKE '%Microsoft Windows Server%'"
        elif typeaction == "serverwin":
            sql += " AND mx.platform LIKE '%Microsoft Windows Server%'"

        # Ajouter le filtre sur le nom d'hôte si nécessaire
        if filter:
            sql += " AND mx.hostname LIKE :filter"

        # Ajouter la clause ORDER BY
        sql += " ORDER BY mx.hostname"

        # Ajouter la pagination
        if limit != -1:
            sql += " LIMIT :limit OFFSET :start"

        sql_text = text(sql)
        params = {
            'entity_id': entity_id if entity_id is not None else -1,
            'filter': f"%{filter}%" if filter else "%",
            'limit': int(limit) if limit != -1 else 18446744073709551615,
            'start': int(start)
        }

        logger.debug("Executing SQL query for outdated major OS updates: %s", sql)
        logger.debug("Parameters: %s", params)

        rows = session.execute(sql_text, params).fetchall()
        count_sql = text("SELECT FOUND_ROWS();")
        total = session.execute(count_sql).scalar()

        result = {
            'nb_total_element': total,
            'nb_element': len(rows)
        }

        if colonne:
            if rows:
                result.update({key: [row[key] if row[key] is not None else "" for row in rows] for key in rows[0].keys()})
            else:
                result.update({})
        else:
            result['details'] = [dict(row._mapping) for row in rows]

        return result

    # @DatabaseHelper._sessionm
    # def get_outdated_major_os_updates_by_entity(self,
    #                                             session,
    #                                             entity_id,
    #                                             typeaction,
    #                                             start=0,
    #                                             limit=-1,
    #                                             filter="",
    #                                             # colonne=True):
    #     """
    #     Récupère les informations des machines dont les mises à jour majeures du système d'exploitation sont obsolètes ou déconseillées,
    #     avec la possibilité de filtrer par entité ou nom d'hôte, et de paginer les résultats.
    #
    #     :param session: session SQLAlchemy (injectée automatiquement par le décorateur)
    #     :param entity_id: ID de l'entité, ou None/-1 pour toutes les entités
    #     :param filter: filtre sur le hostname (optionnel)
    #     :param start: index de départ pour la pagination
    #     :param limit: nombre de lignes à retourner (-1 = pas de limite)
    #     :param colonne: si True, retourne les données par colonne, sinon par ligne
    #     :return: dict contenant les résultats, avec nb_total_element, nb_element et les données
    #     """
    #     sql = '''
    #         SELECT SQL_CALC_FOUND_ROWS
    #             mx.id AS xmpp_id,
    #             m.id AS glpi_id,
    #             e.id AS ent_id,
    #             mx.hostname,
    #             mx.enabled,
    #             mx.jid,
    #             mx.uuid_serial_machine AS serial,
    #             mx.platform AS platform,
    #             s.name,
    #             s.comment,
    #             e.completename AS entity,
    #             lc.lang_code,
    #             lc.iso_filename,
    #             lc.package_uuid,
    #             SUBSTRING(s.name, LOCATE('_', s.name) + 1, LOCATE('@', s.name) - LOCATE('_', s.name) - 1) AS old_version,
    #             SUBSTRING_INDEX(s.name, '-', -1) AS new_version,
    #             SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1) AS oldcode,
    #             SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 5), '@', -1), '_', 2), '_', -1) AS newcode,
    #             SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 3), '@', -1) AS isolang
    #         FROM xmppmaster.local_glpi_items_softwareversions si
    #         JOIN xmppmaster.local_glpi_softwareversions sv ON si.softwareversions_id = sv.id
    #         JOIN xmppmaster.local_glpi_machines m ON si.items_id = m.id
    #         JOIN xmppmaster.local_glpi_softwares s ON sv.softwares_id = s.id
    #         JOIN xmppmaster.local_glpi_entities e ON e.id = m.entities_id
    #         JOIN xmppmaster.machines mx ON NULLIF(REPLACE(mx.uuid_inventorymachine, 'UUID', ''),'') = si.items_id
    #         JOIN xmppmaster.up_packages_major_Lang_code lc
    #             ON lc.lang_code = SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 3), '@', -1)
    #             AND lc.major = SUBSTRING(s.name, LENGTH(s.name) - LOCATE('-', REVERSE(s.name)) + 2)
    #         WHERE
    #             SUBSTRING_INDEX(s.name, '-', -1) > 10
    #             AND (:entity_id IS NULL OR :entity_id = -1 OR e.id = :entity_id)
    #             AND s.name LIKE 'Medulla\_%'
    #             AND (
    #                 SUBSTRING(s.name, LOCATE('_', s.name) + 1, LOCATE('@', s.name) - LOCATE('_', s.name) - 1) != SUBSTRING_INDEX(s.name, '@', -1)
    #                 OR SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1) != SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 5), '@', -1), '_', 2), '_', -1)
    #             )
    #             AND (
    #                 s.name NOT LIKE '%False%'
    #                 OR NOT SUBSTRING_INDEX(s.name, '-', -1) != '11'
    #             )
    #         ORDER BY mx.hostname
    #     '''
    #
    #     if limit != -1:
    #         sql += " LIMIT :limit OFFSET :start"
    #
    #     sql_text = text(sql)
    #     params = {
    #         'entity_id': entity_id if entity_id is not None else -1,
    #         'filter': f"%{filter}%",
    #         'limit': int(limit),
    #         'start': int(start)
    #     }
    #
    #     logger.debug(
    #         "Executing SQL query for outdated major OS updates: %s", sql)
    #     logger.debug("Parameters: %s", params)
    #
    #     rows = session.execute(sql_text, params).fetchall()
    #
    #     count_sql = text("SELECT FOUND_ROWS();")
    #     total = session.execute(count_sql).scalar()
    #
    #     result = {
    #         'nb_total_element': total,
    #         'nb_element': len(rows)
    #     }
    #
    #     if colonne:
    #         result.update({key: [row[key] if row[key] is not None else "" for row in rows]
    #                       for key in rows[0].keys()} if rows else {})
    #     else:
    #         result['details'] = [dict(row._mapping) for row in rows]
    #
    #     return result

    @DatabaseHelper._sessionm
    def get_os_update_major_details(self,
                                    session,
                                    entity_id,
                                    typeaction,
                                    filter="",
                                    start=0,
                                    limit=-1,
                                    colonne=True):
        """
            Récupère les détails des machines avec des systèmes d'exploitation Windows ou Windows Server à partir de la base de données XMPPMaster.

            Cette fonction exécute une requête SQL pour récupérer des informations sur les machines Windows,
            y compris une colonne calculée 'update' qui catégorise les mises à jour majeures nécessaires entre la version actuelle et la prochaine.
            Les résultats peuvent être retournés soit dans un format détaillé ligne par ligne, soit dans un format en colonnes, selon le paramètre 'colonne'.

            Paramètres :
                session (Session) : Objet de session SQLAlchemy pour l'interaction avec la base de données.
                entity_id (int) : L'ID de l'entité pour filtrer les résultats.
                typeaction (str) : Type de machines à filtrer :
                    - "windows" : Exclut les machines dont la plateforme contient "Microsoft Windows Server".
                    - "serverwin" : Inclut uniquement les machines dont la plateforme contient "Microsoft Windows Server".
                filter (str) : Critères de filtrage supplémentaires pour filtrer par nom de machine.
                start (int) : Le décalage pour commencer à retourner les lignes.
                limit (int) : Le nombre maximum de lignes à retourner. Si -1, pas de limitation.
                colonne (bool) : Si True, retourne les résultats dans un format en colonnes. La valeur par défaut est True.

            Retourne :
                dict : Un dictionnaire contenant :
                    - 'nb_machine' : Le nombre total de machines correspondantes.
                    - Si 'colonne' est True : Un dictionnaire de listes, où chaque clé est un nom de colonne et chaque valeur est une liste des valeurs de cette colonne.
                    - Si 'colonne' est False : Une liste de dictionnaires, chaque dictionnaire représentant une ligne de résultats avec les clés suivantes :
                        - 'id_machine', 'uuid_inventorymachine', 'entity', 'entity_id', 'machine', 'platform', 'package_id', 'installeur', 'version', 'update'.
                La colonne 'update' indique les mises à jour majeures nécessaires :
                    - 'W10to10' : Mise à jour entre versions de Windows 10.
                    - 'W10to11' : Mise à jour de Windows 10 vers Windows 11.
                    - 'W11to11' : Mise à jour entre versions de Windows 11.
                    - 'not update' : Aucune mise à jour majeure nécessaire.
        """
        # Base de la requête SQL
        total_os_sql = '''
            SELECT
                SQL_CALC_FOUND_ROWS
                up_mach.id_machine AS id_machine,
                up_mach.glpi_id AS uuid_inventorymachine,
                up_mach.hostname AS machine,
                up_mach.update_id AS package_id,
                up_mach.platform AS platform,
                up_mach.entity AS entity,
                up_mach.ent_id AS entity_id,
                up_mach.kb AS installeur,
                up_mach.oldcode AS version,
                CASE
                    WHEN old_version = 10 AND new_version = 10 THEN 'W10to10'
                    WHEN old_version = 10 AND new_version = 11 THEN 'W10to11'
                    WHEN old_version = 11 AND oldcode NOT LIKE '24H2' THEN 'W11to11'
                    ELSE 'not update'
                END AS 'update'
            FROM
                xmppmaster.up_machine_major_windows up_mach
            WHERE
                ent_id = :entity_id
        '''

        # Ajouter la condition selon typeaction
        if typeaction == "windows":
            total_os_sql += " AND up_mach.platform NOT LIKE '%Microsoft Windows Server%'"
        elif typeaction == "serverwin":
            total_os_sql += " AND up_mach.platform LIKE '%Microsoft Windows Server%'"

        # Ajouter le filtre sur le nom de la machine si nécessaire
        if filter:
            total_os_sql += " AND up_mach.hostname LIKE :filter"

        # Ajouter ORDER BY et LIMIT/OFFSET si nécessaire
        total_os_sql += " ORDER BY up_mach.hostname "
        if limit != -1:
            total_os_sql += " LIMIT :limit OFFSET :start"

        # Convertir en texte pour la liaison des paramètres
        total_os_sql = text(total_os_sql)

        # Journaliser la requête SQL avec les paramètres
        logger.debug("Executing SQL query: %s", total_os_sql)
        logger.debug("With parameters: entity_id=%s, filter=%s, limit=%s, start=%s, typeaction=%s",
                    entity_id, f"%{filter}%", limit, start, typeaction)

        # Exécuter la requête SQL avec les paramètres
        entity_result = session.execute(total_os_sql, {
            'entity_id': entity_id,
            'filter': f"%{filter}%",
            'limit': limit,
            'start': start
        }).fetchall()

        # Compter le nombre total d'éléments correspondants
        sql_count = text("SELECT FOUND_ROWS();")
        ret_count = session.execute(sql_count).scalar()

        # Préparer le dictionnaire de résultats
        result = {
            'nb_machine': ret_count,
        }

        if colonne:
            # Format colonne
            result.update({
                'id_machine': [row.id_machine if row.id_machine is not None else "" for row in entity_result],
                'uuid_inventorymachine': [row.uuid_inventorymachine if row.uuid_inventorymachine is not None else "" for row in entity_result],
                'entity': [row.entity if row.entity is not None else "" for row in entity_result],
                'entity_id': [row.entity_id if row.entity_id is not None else "" for row in entity_result],
                'machine': [row.machine if row.machine is not None else "" for row in entity_result],
                'platform': [row.platform if row.platform is not None else "" for row in entity_result],
                'package_id': [row.package_id if row.package_id is not None else "" for row in entity_result],
                'installeur': [row.installeur if row.installeur is not None else "" for row in entity_result],
                'version': [row.version if row.version is not None else "" for row in entity_result],
                'update': [row.update if row.update is not None else "" for row in entity_result]
            })
        else:
            # Format ligne
            result['details'] = [
                {
                    'id_machine': row.id_machine if row.id_machine is not None else "",
                    'entity': row.entity if row.entity is not None else "",
                    'entity_id': row.entity_id if row.entity_id is not None else "",
                    'uuid_inventorymachine': row.uuid_inventorymachine if row.uuid_inventorymachine is not None else "",
                    'machine': row.machine if row.machine is not None else "",
                    'platform': row.platform if row.platform is not None else "",
                    'package_id': row.package_id if row.package_id is not None else "",
                    'installeur': row.installeur if row.installeur is not None else "",
                    'version': row.version if row.version is not None else "",
                    'update': row.update if row.update is not None else ""
                }
                for row in entity_result
            ]

        return result


#     @DatabaseHelper._sessionm
#     def get_os_update_major_details(self,
#                                     session,
#                                     entity_id,
#                                     typeaction,
#                                     filter="",
#                                     start=0,
#                                     limit=-1,
#                                     colonne=True):
#         """
#
#         ""Microsoft Windows Server
#         Récupère les détails des machines avec des systèmes d'exploitation Windows à partir de la base de données XMPPMaster.
#
#         Cette fonction exécute une requête SQL pour récupérer des informations sur les machines
#         avec des systèmes d'exploitation Windows, y compris une colonne calculée 'os' qui
#         catégorise la version du système d'exploitation et indique les mises à jour majeures
#         nécessaires entre la version actuelle et la prochaine mise à jour majeure. Les résultats
#         peuvent être retournés soit dans un format détaillé ligne par ligne, soit dans un format
#         en colonnes, selon le paramètre 'colonne'.
#
#         Paramètres :
#             session (Session) : Objet de session SQLAlchemy pour l'interaction avec la base de données.
#             entity_id (int) : L'ID de l'entité pour filtrer les résultats.
#             filter (str) : Critères de filtrage supplémentaires pour filtrer par nom de machine.
#             start (int) : Le décalage pour commencer à retourner les lignes.
#             limit (int) : Le nombre maximum de lignes à retourner. Si -1, pas de limitation.
#             colonne (bool) : Si True, retourne les résultats dans un format en colonnes. La valeur par défaut est True.
#
#         Retourne :
#             dict : Un dictionnaire contenant le nombre de lignes correspondantes et soit
#                 des résultats détaillés ligne par ligne, soit des résultats en colonnes,
#                 selon le paramètre 'colonne'. La colonne 'update' indique les mises à jour majeures
#                 nécessaires, telles que 'W10to10' pour une mise à jour entre versions de Windows 10,
#                 'W10to11' pour une mise à jour de Windows 10 vers Windows 11, et 'W11to11' pour une
#                 mise à jour entre versions de Windows 11.
#         """
#         # Nouvelle requête SQL
#         total_os_sql = '''
#             SELECT
#                 SQL_CALC_FOUND_ROWS
#                 up_mach.id_machine AS id_machine,
#                 up_mach.glpi_id AS uuid_inventorymachine,
#                 up_mach.hostname AS machine,
#                 up_mach.update_id AS package_id,
#                 up_mach.platform AS platform,
#                 up_mach.entity AS entity,
#                 up_mach.ent_id AS entity_id,
#                 up_mach.kb AS installeur,
#                 up_mach.oldcode AS version,
#                 CASE
#                     WHEN old_version = 10 AND new_version = 10 THEN 'W10to10'
#                     WHEN old_version = 10 AND new_version = 11 THEN 'W10to11'
#                     WHEN old_version = 11 AND oldcode NOT LIKE '24H2' THEN 'W11to11'
#                     ELSE 'not update'
#                 END AS 'update'
#             FROM
#                 xmppmaster.up_machine_major_windows up_mach
#             WHERE
#                 ent_id = :entity_id
#
#         '''
#
#         # Ajouter la condition de filtre si le filtre n'est pas vide
#         if filter:
#             total_os_sql += " AND up_mach.hostname LIKE :filter"
#
#         # Ajouter ORDER BY et LIMIT/OFFSET si limit n'est pas -1
#         total_os_sql += " ORDER BY up_mach.hostname "
#         if limit != -1:
#             logger.error("limit %s ", limit)
#             total_os_sql += " LIMIT :limit OFFSET :start"
#
#         # Convertir en texte pour la liaison des paramètres
#         total_os_sql = text(total_os_sql)
#
#         # Journaliser la requête SQL avec les paramètres
#         logger.debug("Executing SQL query: %s", total_os_sql)
#         logger.debug("With parameters: entity_id=%s, filter=%s, limit=%s, start=%s",
#                      entity_id, f"%{filter}%", limit, start)
#
#         # Exécuter la requête SQL avec les paramètres
#         entity_result = session.execute(total_os_sql, {
#             'entity_id': entity_id,
#             'filter': f"%{filter}%",
#             'limit': limit,
#             'start': start
#         }).fetchall()
#
#         # Compter le nombre total d'éléments correspondants en utilisant FOUND_ROWS()
#         sql_count = text("SELECT FOUND_ROWS();")
#         ret_count = session.execute(sql_count).scalar()
#         # Préparer le dictionnaire de résultats avec le nombre de lignes correspondantes
#         result = {
#             'nb_machine': ret_count,
#         }
#
#         if colonne:
#             # Si colonne est True, retourner les résultats au format colonne
#             result.update({
#                 'id_machine': [row.id_machine if row.id_machine is not None else "" for row in entity_result],
#                 'uuid_inventorymachine': [row.uuid_inventorymachine if row.uuid_inventorymachine is not None else "" for row in entity_result],
#                 'entity': [row.entity if row.entity is not None else "" for row in entity_result],
#                 'entity_id': [row.entity_id if row.entity_id is not None else "" for row in entity_result],
#
#                 'machine': [row.machine if row.machine is not None else "" for row in entity_result],
#                 'platform': [row.platform if row.platform is not None else "" for row in entity_result],
#                 'package_id': [row.package_id if row.package_id is not None else "" for row in entity_result],
#                 'installeur': [row.installeur if row.installeur is not None else "" for row in entity_result],
#                 'version': [row.version if row.version is not None else "" for row in entity_result],
#                 'update': [row.update if row.update is not None else "" for row in entity_result]
#             })
#         else:
#             # Si colonne est False, retourner les résultats détaillés au format ligne
#             result['details'] = [
#                 {
#                     'id_machine': row.id_machine if row.id_machine is not None else "",
#                     'entity': row.entity if row.entity is not None else "",
#                     'entity_id': row.entity_id if row.entity_id is not None else "",
#                     'uuid_inventorymachine': row.uuid_inventorymachine if row.uuid_inventorymachine is not None else "",
#                     'machine': row.machine if row.machine is not None else "",
#                     'platform': row.platform if row.platform is not None else "",
#                     'package_id': row.package_id if row.package_id is not None else "",
#                     'installeur': row.installeur if row.installeur is not None else "",
#                     'version': row.version if row.version is not None else "",
#                     'update': row.update if row.update is not None else ""
#                 }
#                 for row in entity_result
#             ]
#
#         return result

    @DatabaseHelper._sessionm
    def getAlldistinctvaluetable(self, session, ctx, key: str, value: str) -> list:
        pass

    @DatabaseHelper._sessionm
    def getMachinesByCriteria(self, session, key: str, value: str) -> list:
        """
        Retrieve a list of hostnames based on the provided key and pattern.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            key (str): The column name to search in (e.g., 'oldcode', 'oldversion').
            value (str): The pattern to match.

        Returns:
            list: A list of hostnames that match the pattern.
                  Returns an empty list if an error occurs.
        """
        try:
            # Construct the SQL query
            sql = f"""
                SELECT distinct hostname AS name
                FROM xmppmaster.up_major_win
                WHERE {key} REGEXP :pattern
            """

            # Log the SQL query for debugging
            logger.error(f"Executing SQL query: {sql} with pattern: {value}")

            # Execute the query with the provided value
            result = session.execute(sql, {'pattern': value})

            # Fetch all matching hostnames
            hostnames = [row['name'] for row in result.fetchall()]
            return hostnames

        except Exception as e:
            # Log the exception (optional)
            print(f"An error occurred: {e}")
            # Return an empty list in case of an error
            return []

    @DatabaseHelper._sessionm
    def getAllMachineByVersion(self, session, ctx, value: str) -> list:
        """
        Retrieve a list of hostnames based on the provided version pattern.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            value (str): The version pattern to match (e.g., '24H2', '21H2').

        Returns:
            list: A list of hostnames that match the version pattern.
                Returns an empty list if an error occurs.
        """
        try:
            # Construct the SQL query
            sql = """
                SELECT distinct oldcode AS oldcode
                FROM xmppmaster.up_major_win
                WHERE oldcode REGEXP :pattern
            """

            # Log the SQL query for debugging
            logger.error(f"Executing SQL query: {sql} with pattern: {value}")

            # Execute the query with the provided value
            result = session.execute(sql, {'pattern': value})

            # Fetch all matching hostnames
            hostnames = [row['oldcode'] for row in result.fetchall()]
            return hostnames

        except Exception as e:
            # Log the exception as an error
            logger.error(f"An error occurred: {e}")
            # Return an empty list in case of an error
            return []

    @DatabaseHelper._sessionm
    def getMachineByversion(self, session, ctx, value: str) -> list:
        """
        Retrieve a list of hostnames based on the provided version pattern.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            value (str): The version pattern to match (e.g., '24H2', '21H2').

        Returns:
            list: A list of hostnames that match the version pattern.
                  Returns an empty list if an error occurs.
        """
        try:
            # Construct the SQL query
            sql = """
                SELECT hostname AS name
                FROM xmppmaster.up_major_win
                WHERE oldcode REGEXP :pattern
            """
            # Execute the query with the provided value
            result = session.execute(sql, {'pattern': value})

            # Fetch all matching hostnames
            hostnames = [row['name'] for row in result.fetchall()]
            return hostnames

        except Exception as e:
            # Log the exception (optional)
            logger.error(f"An error occurred: {e}")
            # Return an empty list in case of an error
            return []

    @DatabaseHelper._sessionm
    def getAllMachineByOsType(self, session, ctx, value: str) -> list:
        """
        Retrieve a list of hostnames based on the provided OS type pattern.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            value (str): The OS type pattern to match (e.g., 'W10', 'W11').

        Returns:
            list: A list of hostnames that match the OS type pattern.
                Returns an empty list if an error occurs.
        """
        try:
            # Construct the SQL query
            sql = """
                SELECT distinct oldversion
                FROM xmppmaster.up_major_win
                WHERE oldversion REGEXP :pattern
            """
            # Execute the query with the provided value
            result = session.execute(sql, {'pattern': value})

            # Fetch all matching hostnames
            hostnames = [row['oldversion'] for row in result.fetchall()]
            return hostnames

        except Exception as e:
            # Log the exception (optional)
            logger.error(f"An error occurred: {e}")
            # Return an empty list in case of an error
            return []

    @DatabaseHelper._sessionm
    def getMachineByOsType(self, session, ctx, value: str) -> list:
        """
        Retrieve a list of hostnames based on the provided OS type pattern.

        Args:
            session (Session): The SQLAlchemy session to use for the query.
            value (str): The OS type pattern to match (e.g., 'W10', 'W11').

        Returns:
            list: A list of hostnames that match the OS type pattern.
                Returns an empty list if an error occurs.
        """
        try:
            # Construct the SQL query
            sql = """
                SELECT hostname AS name
                FROM xmppmaster.up_major_win
                WHERE oldversion REGEXP :pattern
            """
            # Execute the query with the provided value
            result = session.execute(sql, {'pattern': value})

            # Fetch all matching hostnames
            hostnames = [row['name'] for row in result.fetchall()]
            return hostnames

        except Exception as e:
            # Log the exception (optional)
            logger.error(f"An error occurred: {e}")
            # Return an empty list in case of an error
            return []

    @DatabaseHelper._sessionm
    def test_update_major_deployment_in_progress(self,
                                                 session,
                                                 title):
        """
        Test if there are any major deployments in progress that match the specified title,
        are in the 'DEPLOYMENT START' state, and have an endcmd time before the current time.
        Returns True if a deployment in progress is found, otherwise returns False.
        """
        # Define the SQL query to check for existence
        sql_query = text("""
        SELECT EXISTS (
            SELECT 1
            FROM xmppmaster.deploy
            WHERE title LIKE :title
                AND state = 'DEPLOYMENT START'
                AND endcmd < NOW()
        ) AS deployment_exists;
        """)
        # Execute the query using the session
        result = session.execute(sql_query, {'title': f'{title}%'})
        # Fetch the result
        deployment_exists = result.fetchone()[0]
        # Return True if deployment exists, otherwise False
        return deployment_exists

    @DatabaseHelper._sessionm
    def get_audit_summary_updates_by_entity(self, session, entity_uuid, start, limit, filter):
        entity_uuid = normalize_entity(entity_uuid, defaut=-1)
        start = to_int(start, 0)
        limit = to_int(limit, -1)
        query = (
            session.query(Deploy)
            .join(Machines, Machines.jid == Deploy.jidmachine)
            .join(Glpi_entity, Glpi_entity.id == Machines.glpi_entity_id)
            .filter(
                and_(
                    Deploy.sessionid.contains("update"),
                    Glpi_entity.glpi_id == entity_uuid
                )
            )
            .order_by(desc(Deploy.start))
        )

        if filter != "":
            query = query.filter(
                or_(
                    Deploy.title.contains(filter),
                    Deploy.state.contains(filter),
                    Deploy.start.contains(filter),
                    Deploy.startcmd.contains(filter),
                    Deploy.endcmd.contains(filter),
                )
            )
        if start != 0:
            query = query.offset(start)
        if limit != -1:
            query = query.limit(limit)

        count = query.count()
        query = query.all()

        result = {"count": count, "datas": []}

        for deploy in query:
            tmp = {
                "id": deploy.id,
                "title": deploy.title,
                "jidmachine": deploy.jidmachine,
                "jid_relay": deploy.jid_relay,
                "pathpackage": deploy.pathpackage,
                "state": deploy.state,
                "sessionid": deploy.sessionid,
                "start": datetime_handler(deploy.start),
                "startcmd": datetime_handler(deploy.startcmd),
                "endcmd": datetime_handler(deploy.endcmd),
                "uuid": deploy.inventoryuuid,
                "hostname": deploy.host,
                "user": deploy.user,
                "cmd_id": deploy.command,
                "grp_id": deploy.group_uuid,
                "login": deploy.login,
                "macadress": deploy.macadress,
                "syncthing": deploy.syncthing,
            }
            result["datas"].append(tmp)
        return result

    @DatabaseHelper._sessionm
    def get_audit_summary_updates_by_update(self, session, updateid, start, limit, filter):
        start = to_int(start, 0)
        limit = to_int(limit, -1)
        query = (
            session.query(Deploy)
            .join(Machines, Machines.jid == Deploy.jidmachine)
            .filter(
                and_(
                    Deploy.sessionid.contains("update"),
                    func.json_extract(Deploy.result, "$.infoslist[0].packageUuid") == f'{updateid}',
                )
            )
            .order_by(desc(Deploy.start))
        )

        if filter != "":
            query = query.filter(
                or_(
                    Deploy.title.contains(filter),
                    Deploy.state.contains(filter),
                    Deploy.start.contains(filter),
                    Deploy.startcmd.contains(filter),
                    Deploy.endcmd.contains(filter),
                )
            )
        if start != 0:
            query = query.offset(start)
        if limit != -1:
            query = query.limit(limit)

        count = query.count()
        query = query.all()

        result = {"count": count, "datas": []}

        for deploy in query:
            tmp = {
                "id": deploy.id,
                "title": deploy.title,
                "jidmachine": deploy.jidmachine,
                "jid_relay": deploy.jid_relay,
                "pathpackage": deploy.pathpackage,
                "state": deploy.state,
                "sessionid": deploy.sessionid,
                "start": datetime_handler(deploy.start),
                "startcmd": datetime_handler(deploy.startcmd),
                "endcmd": datetime_handler(deploy.endcmd),
                "uuid": deploy.inventoryuuid,
                "hostname": deploy.host,
                "user": deploy.user,
                "cmd_id": deploy.command,
                "grp_id": deploy.group_uuid,
                "login": deploy.login,
                "macadress": deploy.macadress,
                "syncthing": deploy.syncthing,
            }
            result["datas"].append(tmp)
        return result

class WhereClauseGenerator:
    def __init__(self, data, correspondance):
        self.data = data
        # Convertir les clés en minuscules
        self.correspondance = {k.lower(): v for k, v in correspondance.items()}
        # logger.error(f"WhereClauseGenerator data : {data['query']}")
        # logger.error(f"WhereClauseGenerator correspondance: {correspondance}")

    def generate(self):
        if 'query' in self.data:
            return self._parse_condition(self.data['query'])
        else:
            return ""

    def _parse_condition(self, condition):
        if not isinstance(condition, list) or len(condition) < 2:
            return ""

        operator = condition[0]
        clauses = condition[1]

        if operator == 'AND':
            joiner = ' AND '
        elif operator == 'OR':
            joiner = ' OR '
        elif operator == 'NOT':
            if isinstance(clauses, list) and len(clauses) == 4:
                _, source, key, value = clauses
                return f"NOT ({self._format_condition(key, value)})"
            return f"NOT ({self._parse_condition(clauses)})"
        else:
            return ""

        parsed_clauses = set()  # Utiliser un ensemble pour éliminer les doublons

        for clause in clauses:
            if isinstance(clause, list) and len(clause) == 4:
                _, source, key, value = clause
                parsed_clauses.add(self._format_condition(key, value))
            elif isinstance(clause, list):
                parsed_clauses.add(f"({self._parse_condition(clause)})")

        return f"({joiner.join(sorted(parsed_clauses))})"

    def _format_condition(self, key, value):
        if isinstance(value, list) and len(value) > 0:
            # Prendre uniquement le premier élément pour cette version
            value = value[0]

        match = re.match(r'^(=|>|<|<>)\s*(.*)$', value)
        if match:
            operator, clean_value = match.groups()
        else:
            operator, clean_value = 'REGEXP', value

        # Appliquer la correspondance insensible à la casse juste avant le retour
        key_lower = key.lower()
        if key_lower in self.correspondance:
            key = self.correspondance[key_lower]

        return f"{key} {operator} '{clean_value}'"
