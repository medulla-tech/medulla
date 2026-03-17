#!/usr/bin/python3
# -*- coding:utf-8 -*-
# SPDX-FileCopyrightText: 2022-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# This script is used to generate update packages in /var/lib/pulse2/packages

from datetime import datetime
import re
import requests
import subprocess
import sys, os
import signal
import logging
import traceback
import MySQLdb
import base64
import getpass
import json
from optparse import OptionParser
import shutil

# from  MySQLdb import IntegrityError
# Global Variables

logger = logging.getLogger()


class synch_packages:
    def __init__(self, db, opts):
        self.db = db
        self.param = opts
        # logger.info("File parmetre %s" % self.param)
        self.update_file_windows = {}
        self.path_base = os.path.join(
            "/", "var", "lib", "pulse2", "base_update_package"
        )
        if not os.path.exists(self.path_base):
            try:
                os.makedirs(self.path_base)
            except OSError as e:
                logger.error(f"{str(e)} create directory share'{self.path_base}'")

        self.sharing = os.path.join("/", "var", "lib", "pulse2", "packages", "sharing")
        self.dirpartageupdate = os.path.join(self.sharing, self.param["partage"])
        self.path_in_partage = os.path.join(
            self.dirpartageupdate, self.param["uidpackage"]
        )
        self.path_in_base = os.path.join(self.path_base, self.param["uidpackage"])
        self.packagelist = self.search_list_package()
        package_install = self.param["uidpackage"] in self.packagelist
        if self.param["forcedelpackage"]:
            logger.info(f'completely remove the package {self.param["uidpackage"]}')
            self.uninstall_full_package()

        elif self.param["delpackage"]:
            logger.info(
                f"""uninstall package {self.param["uidpackage"]} but don't remove it"""
            )
            self.mv_partage_to_base()
            # supprime le package de la base
            self.del_package_pkgs()
            return
        elif self.param["forcecreatepackage"]:
            logger.info(
                f'create or completely create the package and install it {self.param["uidpackage"]}'
            )
            self.uninstall_full_package()
            self.install_full_package()
        elif self.param["createpackage"]:
            logger.info(f'install package if not install {self.param["uidpackage"]}')
            self.install_full_package()

    def install_full_package(self):
        if self.create_package_file():
            self.mv_base_to_partage()
            self.install_package()
        self.verify_packages_install()

    def uninstall_full_package(self):
        # supprime de la base fichier
        self.del_package()
        # suprime le lien symbolique
        # self.mv_partage_to_base()
        # supprime le package de la base
        self.del_package_pkgs()
        self.verify_packages_uninstall()

    def create_directory_in_partage(self):
        if not os.path.exists(self.path_in_partage):
            try:
                os.makedirs(self.path_in_partage)
            except OSError as e:
                logger.error(f"{str(e)} : create_directory '{self.path_in_partage}'")

    def create_directory_in_base(self):
        if not os.path.exists(self.path_in_base):
            try:
                os.makedirs(self.path_in_base)
            except OSError as e:
                logger.error(f"{str(e)} : create_directory '{self.path_in_base}'")

    def mv_base_to_partage(self):
        # mv base vers partages
        if os.path.isdir(self.path_in_base):
            logger.debug(
                f"function make transfert {self.path_in_base} to {self.path_in_partage}"
            )
            file_names = os.listdir(self.path_in_base)
            self.create_directory_in_partage()
            for file_name in file_names:
                shutil.move(
                    os.path.join(self.path_in_base, file_name), self.path_in_partage
                )
                logger.debug(
                    f"move {os.path.join(self.path_in_base, file_name)} to {self.path_in_partage}"
                )
            logger.debug(f"del  {self.path_in_base}")
            shutil.rmtree(self.path_in_base)

    def mv_partage_to_base(self):
        # mv de partages vers base
        # mv_partage_to_base
        if os.path.isdir(self.path_in_partage):
            logger.debug(
                f"function make transfert {self.path_in_partage} to {self.path_in_base}"
            )
            file_names = os.listdir(self.path_in_partage)
            self.create_directory_in_base()
            for file_name in file_names:
                try:
                    shutil.move(
                        os.path.join(self.path_in_partage, file_name), self.path_in_base
                    )
                except Exception as e:
                    pass
            shutil.rmtree(self.path_in_partage)

    def del_package(self):
        """
        supprime completement les fichiers du package de la base fichier
        """
        if os.path.isdir(self.path_in_base):
            try:
                shutil.rmtree(self.path_in_base)
                logger.debug(f"delete directory '{self.path_in_base}'")
            except Exception as e:
                logger.error(f"{str(e)} : del_package '{self.path_in_base}'")
        else:
            logger.debug(f"directory '{self.path_in_base}' is not exit")

        if os.path.isdir(self.path_in_partage):
            try:
                shutil.rmtree(self.path_in_partage)
                logger.debug(f"delete directory '{self.path_in_partage}'")
            except Exception as e:
                logger.error(f"{str(e)} : del_package '{self.path_in_partage}'")
        else:
            logger.debug(f"directory '{self.path_in_partage}' is not exit")

    def del_package_pkgs(self):
        """
        Supprime l'enregistrement d'un package dans la base de données `pkgs`.

        Cette fonction exécute une requête SQL DELETE dans la table
        `pkgs.packages` en utilisant l'identifiant unique du package
        (`uidpackage`). Si le package existe, il est supprimé de la base.

        Étapes :
            1. Construction de la requête SQL DELETE.
            2. Exécution de la requête sur la base de données.
            3. Validation de la transaction (commit).
            4. Journalisation du résultat de l'opération.

        Attributs utilisés :
            self.param["uidpackage"] : identifiant unique du package.
            self.db                  : connexion active à la base de données.

        Effets de bord :
            - Suppression d'une entrée dans la table `pkgs.packages`.
            - Écriture dans les logs (debug / error).

        Gestion des erreurs :
            Toute exception est capturée et enregistrée dans les logs.
        """
        try:
            sql = (
                """DELETE
                        FROM `pkgs`.`packages`
                    WHERE
                        (`uuid` = '%s');"""
                % self.param["uidpackage"]
            )
            logger.debug(f"sql {sql}")
            cursor = self.db.cursor()
            result = cursor.execute(sql)
            self.db.commit()
            if result:
                logger.debug(f'the package [{self.param["uidpackage"]}] is uninstalled')
            else:
                logger.debug(
                    f'the package [{self.param["uidpackage"]}] is not installed'
                )
        except Exception as e:
            logger.error(
                f"""{str(e)} : del_package_pkgs '{self.param["uidpackage"]}'"""
            )

    def verify_packages_install(self):
        """
        Vérifie que l'installation du package est correcte.

        Cette fonction valide deux éléments :
            1. La présence des fichiers du package dans le répertoire partagé.
            2. L'enregistrement du package dans la base de données `pkgs`.

        Critères de validation :
            - Le répertoire du package existe dans `path_in_partage`.
            - Le répertoire contient au moins trois fichiers
            (généralement le fichier téléchargé et les fichiers JSON).
            - Le package est présent dans la base via `check_in_base()`.

        Retour :
            bool
                True  : le package est correctement installé.
                False : le package est absent ou incomplet.

        Attributs utilisés :
            self.param["uidpackage"] : identifiant unique du package.
            self.path_in_partage     : chemin vers le répertoire partagé du package.

        Effets de bord :
            - Écriture d'informations dans les logs pour le suivi du statut
            de l'installation.
        """
        logger.debug(f"verify packages install {self.path_in_partage}")
        if os.path.isdir(self.path_in_partage):
            ff = os.listdir(self.path_in_partage)
            if len(ff) >= 3:
                logger.debug(
                    f'the package {self.param["uidpackage"]} was successfully created'
                )
            else:
                logger.error(
                    f'package {self.param["uidpackage"]} exists but is incomplete'
                )
                return False
        else:
            logger.error(f'package file {self.param["uidpackage"]} does not exist')
            return False

        if self.check_in_base():
            logger.debug(f'package {self.param["uidpackage"]} is installed in pkgs')
        else:
            logger.error(
                f'the package {self.param["uidpackage"]} is not installed in pkgs'
            )
            return False
        logger.info(f'package {self.param["uidpackage"]} is successfully installed')
        return True

    def verify_packages_uninstall(self):
        """
        Vérifie que la désinstallation d'un package est complète.

        La vérification porte sur deux points :
            1. Les fichiers du package ne doivent plus exister sur le système
            de fichiers (répertoire supprimé).
            2. L'entrée correspondante ne doit plus exister dans la base
            de données `pkgs`.

        Étapes :
            - Vérification de l'absence du répertoire du package.
            - Vérification que le package n'est plus présent en base
            via `check_in_base()`.

        Retour :
            bool
                True  : la désinstallation est correcte et complète.
                False : des fichiers ou une entrée en base existent encore.

        Attributs utilisés :
            self.param["uidpackage"] : identifiant unique du package.
            self.path_in_base        : chemin du répertoire local du package.

        Effets de bord :
            - Écriture dans les logs pour indiquer l'état de la désinstallation.
        """
        logger.debug(f"verify packages uninstall {self.path_in_partage}")
        if os.path.isdir(self.path_in_base):
            logger.error(f'the {self.param["uidpackage"]} package files still exist')
            return False
        else:
            logger.debug(f'package {self.param["uidpackage"]} no longer exists')

        if os.path.isdir(self.path_in_base):
            logger.error(f'the {self.param["uidpackage"]} package files still exist')
            return False
        else:
            logger.debug(f'package {self.param["uidpackage"]} no longer exists')
        if self.check_in_base():
            logger.debug(
                f'package {self.param["uidpackage"]} is still installed in pkgs'
            )
            return False
        else:
            logger.debug(f'uninstalled package {self.param["uidpackage"]} in pkgs')
        logger.info(f'correct uninstalled package {self.param["uidpackage"]}')
        return True

    # dans /var/lib/pulse2/packages/sharing/winupdates
    # ln -s /var/lib/pulse2/base_update_package/fcc60465-497b-4395-b714-4699cef797ca fcc60465-497b-4395-b714-4699cef797ca

    def search_list_package(self):
        """
        list tout les packages in le partages
        """
        return [f for f in os.listdir(self.dirpartageupdate) if uuid_validate(f)]

    def search_file_update(self):
        """
        Recherche l'URL de téléchargement (payloadfiles) la plus pertinente
        pour une mise à jour Windows.

        Étapes :
        1. Recherche la mise à jour correspondant à l'UID du package.
        2. Si trouvée, recherche les payloads associés via le champ `supersededby`.
        3. Si plusieurs payloads existent, sélectionne celui ayant le numéro KB
        le plus élevé (donc le plus récent) extrait depuis l'URL `payloadfiles`.

        Retourne :
            dict contenant les informations de la mise à jour et du payload trouvé.
            Si rien n'est trouvé, retourne un dictionnaire vide.
        """

        # dictionnaire contenant les informations finales
        self.update_file_windows = {}

        # -------------------------------------------------------------
        # 1. Recherche des informations de base de la mise à jour
        # -------------------------------------------------------------
        sql = """SELECT
                    updateid,
                    kb,
                    revisionid,
                    title,
                    description
                FROM
                    xmppmaster.%s
                WHERE
                    updateid = '%s'
                LIMIT 1;""" % (
            self.param["nametable"],
            self.param["uidpackage"],
        )

        logger.debug(f"sql {sql}")

        cursor = self.db.cursor()
        cursor.execute(sql)

        for row in cursor.fetchall():
            self.update_file_windows["updateid"] = row[0]
            self.update_file_windows["kb"] = row[1]
            self.update_file_windows["revisionid"] = row[2]
            self.update_file_windows["title"] = row[3]
            self.update_file_windows["description"] = row[4]

        # -------------------------------------------------------------
        # 2. Recherche du payload associé
        # -------------------------------------------------------------
        # On sélectionne le payload le plus récent :
        # - extraction du numéro KB depuis l'URL payloadfiles
        # - tri par numéro KB décroissant
        # - LIMIT 1 pour récupérer le plus récent
        # -------------------------------------------------------------
        if self.update_file_windows:

            sql = """SELECT
                        updateid,
                        payloadfiles,
                        supersededby,
                        creationdate,
                        title_short
                    FROM
                        xmppmaster.%s
                    WHERE
                        payloadfiles <> ''
                        AND supersededby LIKE "%s"
                    ORDER BY
                        CAST(
                            REPLACE(
                                REGEXP_SUBSTR(payloadfiles, 'kb[0-9]+'),
                                'kb',
                                ''
                            ) AS UNSIGNED
                        ) DESC
                    LIMIT 1;""" % (
                self.param["nametable"],
                self.update_file_windows["revisionid"],
            )

            logger.debug(f"sql {sql}")

            cursor.execute(sql)

            for row in cursor.fetchall():
                self.update_file_windows["updateid_payloadfiles"] = row[0]
                self.update_file_windows["payloadfiles"] = row[1]
                self.update_file_windows["supersededby"] = row[2]
                self.update_file_windows["creationdate"] = row[3]
                self.update_file_windows["title_short"] = row[4]

            logger.debug(
                f"update_file_windows complet {self.update_file_windows}"
            )

        return self.update_file_windows

    def create_package_file(self):
        """
        Télécharge le fichier d'une mise à jour Windows et construit le package associé.

        Fonctionnement :
        1. Vérifie si le package existe déjà dans les répertoires locaux (`path_in_base`
        ou `path_in_partage`). Si plusieurs fichiers sont déjà présents (>=3),
        la création du package est ignorée.
        2. Recherche les informations de la mise à jour via `search_file_update()`,
        notamment l'URL `payloadfiles` du fichier à télécharger.
        3. Si une URL valide est trouvée :
        - création du répertoire du package si nécessaire
        - téléchargement du fichier depuis Windows Update
        - tentative avec proxy si le téléchargement direct échoue
        4. Enregistre le fichier téléchargé dans le répertoire du package.
        5. Génère les fichiers de configuration nécessaires au déploiement :
        - `conf.json`
        - `xmppdeploy.json`

        Retour :
            bool
                True  : package existant ou création réussie
                False : aucune URL de mise à jour trouvée ou erreur bloquante

        Attributs utilisés :
            self.param["uidpackage"] : identifiant du package
            self.path_in_base        : répertoire principal du package
            self.path_in_partage     : répertoire partagé éventuel
            self.update_file_windows : dictionnaire contenant les métadonnées
                                    de la mise à jour (URL, KB, titre, etc.)

        Effets de bord :
            - Téléchargement d'un fichier CAB/MSU depuis Windows Update
            - Création de fichiers dans le système de fichiers
            - Génération de fichiers JSON de configuration pour le déploiement
        """
        if os.path.isdir(self.path_in_base):
            ff = os.listdir(self.path_in_base)
            if len(ff) >= 3:
                logger.debug(f'package exists {self.param["uidpackage"]} already')
                return True
        elif os.path.isdir(self.path_in_partage):
            ff = os.listdir(self.path_in_partage)
            if len(ff) >= 3:
                logger.debug(f'package exists {self.param["uidpackage"]} already')
                return True
        # logger.debug("download %s" % urlpath)
        # start = datetime.now()
        # search url file update
        if not self.search_file_update():
            logger.error(
                f'not find update file to download for {self.param["uidpackage"]}'
            )
            return False

        # test si url exist
        if (
            self.update_file_windows
            and "payloadfiles" in self.update_file_windows
            and self.update_file_windows["payloadfiles"] != ""
        ):
            # 1 url trouver on fabrique le package
            logger.debug(
                f'url update file windows package {self.param["uidpackage"]} is {self.update_file_windows["payloadfiles"]}'
            )
            namefile = self.update_file_windows["payloadfiles"].split("/")[-1]
            path_file_download = os.path.join(self.path_in_base, namefile)
            # creation repertoire du package si non exist
            self.create_directory_in_base()
            try:
                data = requests.get(
                    self.update_file_windows["payloadfiles"], stream=True
                )
            except Exception as e:
                logger.error(
                    "Error trying to download %s: %s"
                    % (self.update_file_windows["payloadfiles"], e)
                )
                try:
                    # Try with proxy parameters as defined on the system
                    proxy_url = (
                        os.environ.get("HTTP_PROXY")
                        or os.environ.get("HTTPS_PROXY")
                        or os.environ.get("http_proxy")
                        or os.environ.get("https_proxy")
                    )
                    if proxy_url:
                        proxies = {"http": proxy_url, "https": proxy_url}
                        data = requests.get(
                            self.update_file_windows["payloadfiles"],
                            stream=True,
                            proxies=proxies,
                        )
                    else:
                        logger.error("No proxies defined")
                except Exception as e:
                    logger.error("Error downloading update file: %s" % str(e))
            with open(path_file_download, "wb") as f:
                for chunk in data.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            typename = os.path.splitext(path_file_download)[1][1:]
            file_conf_json = os.path.join(self.path_in_base, "conf.json")
            file_xmppdeploy_json = os.path.join(self.path_in_base, "xmppdeploy.json")
            nameexecution = os.path.basename(path_file_download)

            with open(file_conf_json, "w") as outfile:
                outfile.write(
                    self.generate_conf_json(
                        self.update_file_windows["title"],
                        self.update_file_windows["updateid"],
                        self.update_file_windows["description"],
                        self.update_file_windows["payloadfiles"],
                    )
                )

            with open(file_xmppdeploy_json, "w") as outfile:
                outfile.write(
                    self.generate_xmppdeploy_json(
                        self.update_file_windows["title"],
                        self.update_file_windows["updateid"],
                        self.update_file_windows["description"],
                        typename,
                        nameexecution,
                        self.update_file_windows["payloadfiles"],
                        self.update_file_windows["kb"],
                        self.update_file_windows["creationdate"],
                    )
                )
        else:
            # terminer avec erreur
            logger.error(f'create package {self.param["uidpackage"]}')
        # end = datetime.now()
        # total_elapsed_time = end - start
        return True

    def loadjsonfile(self, filename):
        """
        This function is used to load a json file
        Args:
            filename: The filename of the json file to load
        Returns:
            It returns the content of the JSON file
        """

        if os.path.isfile(filename):
            try:
                with open(filename, "r") as info:
                    outputJSONFile = json.load(info)
                return outputJSONFile
            except Exception as e:
                logger.error(f"We failed to decode the file {filename}")
                logger.error(f"we encountered the error: {str(e)}")
                errorstr = f"{traceback.format_exc()}"
                logger.error("\n%s" % (errorstr))
        return None

    def generate_xmppdeploy_json(
        self,
        name,
        id,
        description,
        typename,
        namefile,
        urlpath,
        kb,
        date_edition_windows_update,
    ):
        """
        Génère le fichier JSON `xmppdeploy.json` utilisé par Medulla/Pulse
        pour déployer une mise à jour Windows.

        Cette fonction construit dynamiquement la structure JSON décrivant
        les métadonnées du package et la séquence d'exécution côté Windows.

        Fonctionnement :
            1. Détermine la commande d'installation selon le type du fichier :
            - `.cab` : installation via DISM.
            - outil MRT (`kb890830`) : copie dans System32.
            - autres fichiers : exécution classique avec `Start /wait`.
            2. Encode la commande en Base64 pour l'intégrer dans le script.
            3. Génère le template JSON contenant :
            - les métadonnées du package
            - la séquence d'exécution
            - les actions de gestion du reboot
            - les paramètres de déploiement.

        Paramètres :
            name (str)  : nom du package.
            id (str)    : identifiant unique du package (UUID).
            description (str) : description du package.
            typename (str) : type du fichier téléchargé (cab, msu, exe…).
            namefile (str) : nom du fichier à exécuter.
            urlpath (str) : URL d'origine du fichier Windows Update.
            kb (str) : numéro KB de la mise à jour.
            date_edition_windows_update (str) : date de publication de la mise à jour.

        Retour :
            str : contenu JSON complet du fichier `xmppdeploy.json`.

        Effets de bord :
            Aucun. La fonction retourne uniquement une chaîne JSON.
        """
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        if typename == "cab":
            cmd = (
                """dism /Online /Add-Package /PackagePath:"@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" /NoRestart"""
                % (namefile)
            )
        elif "kb890830" in namefile:
            cmd = (
                """copy /y "@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" C:\Windows\System32\MRT.exe"""
                % (namefile)
            )
        else:
            cmd = """Start /wait "@@@PACKAGE_DIRECTORY_ABS_MACHINE@@@\\%s" """ % (
                namefile
            )
        cmd64 = base64.b64encode(bytes(cmd, "utf-8"))
        template = """{
        "info": {
            "meta_update_kb" : "%s",
            "meta_update_date_edition_windows_update" : "%s",
            "urlpath" : "%s",
            "creator": "automate_medulla",
            "edition": "automate_medulla",
            "creation_date": "%s",
            "licenses": "1.0",
            "gotoreturncode": "3010",
            "gotolabel": "REBOOTREQUIRED",
            "packageUuid": "%s",
            "spooling": "ordinary",
            "limit_rate_ko": "",
            "version": "0.1",
            "editor": "automate_medulla",
            "metagenerator": "expert",
            "targetrestart": "MA",
            "inventory": "noforced",
            "localisation_server": "%s",
            "typescript": "Batch",
            "description": "%s",
            "previous_localisation_server": "%s",
            "Dependency": [],
            "name": "%s",
            "url": "",
            "edition_date": "%s",
            "transferfile": true,
            "methodetransfert": "pushrsync",
            "software": "templated",
            "type_section" : "update"
        },
        "win": {
            "sequence": [
                {
                    "action": "action_section_update",
                    "step": 0,
                    "actionlabel": "upd_70a70cc9"
                },
                {
                    "typescript": "Batch",
                    "script": "%s",
                    "30@lastlines": "30@lastlines",
                    "actionlabel": "02d57e96",
                    "codereturn": "",
                    "step": 1,
                    "error": 6,
                    "action": "actionprocessscriptfile",
                    "timeout": "3600",
                    "gotoreturncode@3010": "REBOOTREQUIRED"
                },
                {
                    "action": "actionwaitandgoto",
                    "step": 2,
                    "codereturn": "",
                    "actionlabel": "wait_cc66c870",
                    "waiting": "1",
                    "goto": "END_SUCCESS"
                },
                {
                    "step": 3,
                    "action": "action_comment",
                    "actionlabel": "REBOOTREQUIRED",
                    "comment": "The update has been installed but a reboot is required to apply it."
                },
                {
                    "action": "action_notification",
                    "step": 4,
                    "codereturn": "",
                    "actionlabel": "notif_ee9943f2",
                    "titlemessage": "V2luZG93cyBVcGRhdGUgLSBSZWJvb3Q=",
                    "sizeheader": "15",
                    "message": "QW4gdXBkYXRlIGhhcyBiZWVuIGluc3RhbGxlZCBvbiB5b3VyIGNvbXB1dGVyIGJ5IE1lZHVsbGEuIFBsZWFzZSByZWJvb3Qgd2hlbiBwb3NzaWJsZSB0byBhcHBseSB0aGUgdXBkYXRlLg0KDQpVbmUgbWlzZSDDoCBqb3VyIGEgw6l0w6kgaW5zdGFsbMOpZSBzdXIgdm90cmUgb3JkaW5hdGV1ciBwYXIgTWVkdWxsYS4gUGVuc2V6IMOgIHJlZMOpbWFycmVyIHF1YW5kIGMnZXN0IHBvc3NpYmxlIGFmaW4gcXVlIGxhIG1pc2Ugw6Agam91ciBzb2l0IGFwcGxpcXXDqWUu",
                    "sizemessage": "10",
                    "textbuttonyes": "OK",
                    "timeout": "800"
                },
                {
                    "action": "actionsuccescompletedend",
                    "step": 5,
                    "actionlabel": "END_SUCCESS",
                    "clear": "False",
                    "inventory": "noforced"
                },
                {
                    "action": "actionerrorcompletedend",
                    "step": 6,
                    "actionlabel": "END_ERROR"
                }
            ]
        },
        "metaparameter": {
            "win": {
                "label": {
                    "upd_70a70cc9": 0,
                    "02d57e96": 1,
                    "wait_cc66c870": 2,
                    "REBOOTREQUIRED": 3,
                    "notif_ee9943f2": 4,
                    "END_SUCCESS": 5,
                    "END_ERROR": 6
                }
            },
            "os": [
                "win"
            ]
        }
    }""" % (
            kb,
            date_edition_windows_update,
            urlpath,
            dt_string,
            id,
            self.param["partage"],
            description,
            self.param["partage"],
            name,
            dt_string,
            cmd64.decode("utf-8"),
        )
        return template

    def id_partage(self):
        """
        Récupère ou crée l'identifiant du partage utilisé pour les packages.

        Cette fonction recherche dans la table `pkgs.pkgs_shares`
        le partage correspondant au nom défini dans `self.param["partage"]`.

        Fonctionnement :
            1. Recherche du partage existant dans la base.
            2. Si trouvé, retourne son identifiant.
            3. Sinon, crée un nouveau partage avec les paramètres par défaut.
            4. Enregistre le nouvel identifiant dans `self.partage_id`.

        Attributs utilisés :
            self.param["partage"] : nom du partage.
            self.dirpartageupdate : chemin du partage sur le serveur.
            self.db               : connexion à la base de données.

        Retour :
            int | None
                ID du partage si trouvé ou créé,
                None en cas d'erreur.

        Effets de bord :
            - Peut créer une entrée dans `pkgs.pkgs_shares`.
            - Met à jour `self.partage_id`.
        """
        self.partage_id = None
        sql = (
            """SELECT
                id
            FROM
                pkgs.pkgs_shares
            WHERE
                name = '%s' limit 1;"""
            % self.param["partage"]
        )
        logger.debug(f"sql {sql}")
        cursor = self.db.cursor()
        record = cursor.execute(sql)
        for i in cursor.fetchall():
            self.partage_id = i[0]
        if self.partage_id:
            logger.debug(f"ID partage is  {self.partage_id}")
            return self.partage_id
        else:
            # creation partage
            sql = """INSERT INTO `pkgs`.`pkgs_shares` (`name`, `comments`,
                                                    `enabled`, `type`,
                                                    `uri`, `ars_name`,
                                                    `ars_id`, `share_path`,
                                                    `usedquotas`, `quotas`) VALUES ('%s', 'partage update', '1', 'update', 'pulse', 'pulse', '1', '%s', '0', '0');""" % (
                self.param["partage"],
                self.dirpartageupdate,
            )
            logger.debug(f"sql {sql}")
            try:
                logger.debug("creation partage %s %s" % self.param["partage"])
                cursor = self.db.cursor()
                cursor.execute(sql)
                self.partage_id = cursor.lastrowid
                self.db.commit()
                logger.debug(f"ID partage is  {self.partage_id}")
                return self.partage_id
            except MySQLdb.Error as e:
                errorstr = f"{traceback.format_exc()}"
                logger.error("\n%s" % (errorstr))
                logger.error("%s : id_partage '%s'" % (str(e)))
                self.partage_id = None
            except Exception as e:
                errorstr = f"{traceback.format_exc()}"
                logger.error("\n%s" % (errorstr))
                self.partage_id = None
            finally:
                cursor.close()
        return None

    def check_in_base(self):
        """
        Vérifie si un package est déjà enregistré dans la base de données.

        La fonction recherche l'identifiant unique (`uuid`) du package
        dans la table `pkgs.packages`.

        Attributs utilisés :
            self.param["uidpackage"] : identifiant unique du package.

        Retour :
            bool
                True  : le package existe déjà en base.
                False : le package n'est pas présent.

        Effets de bord :
            - Écriture d'informations dans les logs pour faciliter le debug.
        """
        sql = (
            """SELECT
                id
            FROM
                pkgs.packages
            WHERE
                uuid = '%s' limit 1;"""
            % self.param["uidpackage"]
        )
        logger.debug(f"sql {sql}")
        cursor = self.db.cursor()
        record = cursor.execute(sql)
        for _ in cursor.fetchall():
            logger.debug("check_in_base TRUE")
            return True
        logger.debug("package non installer in pkgs")
        return False

    def install_package(self):
        """
        Installe un package dans la base de données `pkgs`.

        Cette fonction lit le fichier `conf.json` du package généré
        et insère ses informations dans la table `pkgs.packages`.

        Fonctionnement :
            1. Vérifie si le package existe déjà via `check_in_base()`.
            2. Récupère ou crée l'identifiant du partage avec `id_partage()`.
            3. Détermine le répertoire contenant le package.
            4. Charge et valide le fichier `conf.json`.
            5. Complète les champs manquants (dates, metagenerator…).
            6. Calcule la taille du dossier du package.
            7. Construit la structure de données (`fiche`) contenant
            toutes les informations nécessaires à l'installation.
            8. Insère les données dans la table `pkgs.packages`.

        Attributs utilisés :
            self.param["uidpackage"] : identifiant unique du package.
            self.param["partage"]    : nom du partage.
            self.path_in_base        : répertoire local du package.
            self.path_in_partage     : répertoire partagé du package.
            self.db                  : connexion à la base de données.

        Retour :
            bool | None
                False en cas d'erreur critique (ex : JSON invalide),
                sinon la fonction termine sans retour explicite.

        Effets de bord :
            - Lecture de fichiers JSON du package.
            - Calcul de la taille du dossier.
            - Insertion d'une entrée dans la table `pkgs.packages`.
            - Écriture dans les logs pour suivi et diagnostic.

        Gestion des erreurs :
            Toutes les exceptions sont capturées et enregistrées
            dans les logs avec la trace complète.
        """
        try:
            # search id_partage winupdates
            if self.check_in_base():
                return
            self.id_partage()
            if not self.partage_id:
                return
            if os.path.isdir(self.path_in_base):
                dirpackage = self.path_in_base
            else:
                dirpackage = self.path_in_partage

            logger.debug("1")
            file_xmppdeploy_json = os.path.join(dirpackage, "conf.json")
            contenuedejson = self.loadjsonfile(file_xmppdeploy_json)
            logger.debug("3")
            if contenuedejson is None:
                # erreur d'installation package
                logger.error("decodage json conf.json erreur")
                return False
            logger.debug("4")
            if (
                "localisation_server" not in contenuedejson
                or contenuedejson["localisation_server"] == ""
            ):
                contenuedejson["localisation_server"] = self.param["partage"]
                contenuedejson["previous_localisation_server"] = self.param["partage"]

            # if not ("creator" in contenuedejson and contenuedejson['creator'] != "") :
            # contenuedejson['creator'] = "root"

            # if not ("edition" in contenuedejson  and contenuedejson['edition'] != "") :
            # contenuedejson['edition'] = "root"

            if (
                "creation_date" not in contenuedejson
                or contenuedejson["creation_date"] == ""
            ):
                contenuedejson["creation_date"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            if (
                "edition_date" not in contenuedejson
                or contenuedejson["edition_date"] == ""
            ):
                contenuedejson["edition_date"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            if "metagenerator" not in contenuedejson:
                contenuedejson["metagenerator"] = "expert"

            edition_status = 0 if contenuedejson["metagenerator"] == "manual" else 1
            ### print json.dumps(contenuedejson, indent=4)
            # du = simplecommand("du -Lsb")

            result = simplecommand(f"du -b {dirpackage}")
            taillebytefolder = int(result["result"][0].split()[0])

            fiche = {
                "size": f"{taillebytefolder}",
                "label": contenuedejson["name"],
                "description": contenuedejson["description"],
                "version": contenuedejson["version"],
                "os": contenuedejson["targetos"],
                "metagenerator": contenuedejson["metagenerator"],
                "uuid": contenuedejson["id"],
                "entity_id": contenuedejson["entity_id"],
                "sub_packages": json.dumps(contenuedejson["sub_packages"]),
                "reboot": contenuedejson["reboot"],
                "inventory_associateinventory": contenuedejson["inventory"][
                    "associateinventory"
                ],
                "inventory_licenses": contenuedejson["inventory"]["licenses"],
                "Qversion": contenuedejson["inventory"]["queries"]["Qversion"],
                "Qvendor": contenuedejson["inventory"]["queries"]["Qvendor"],
                "Qsoftware": contenuedejson["inventory"]["queries"]["Qsoftware"],
                "boolcnd": contenuedejson["inventory"]["queries"]["boolcnd"],
                "postCommandSuccess_command": contenuedejson["commands"][
                    "postCommandSuccess"
                ]["command"],
                "postCommandSuccess_name": contenuedejson["commands"][
                    "postCommandSuccess"
                ]["name"],
                "installInit_command": contenuedejson["commands"]["installInit"][
                    "command"
                ],
                "installInit_name": contenuedejson["commands"]["installInit"]["name"],
                "postCommandFailure_command": contenuedejson["commands"][
                    "postCommandFailure"
                ]["command"],
                "postCommandFailure_name": contenuedejson["commands"][
                    "postCommandFailure"
                ]["name"],
                "command_command": contenuedejson["commands"]["command"]["command"],
                "command_name": contenuedejson["commands"]["command"]["name"],
                "preCommand_command": contenuedejson["commands"]["preCommand"][
                    "command"
                ],
                "preCommand_name": contenuedejson["commands"]["preCommand"]["name"],
                "pkgs_share_id": self.partage_id,
                "edition_status": 1,
                "conf_json": json.dumps(contenuedejson),
            }
            for p in fiche:
                # logger.debug("p %s" % p)
                if p in ["name", "description", "conf_json"]:
                    fiche[p] = MySQLdb.escape_string(str(fiche[p])).decode("utf-8")

            sql = """INSERT IGNORE INTO `pkgs`.`packages` (
                                            `label`,
                                            `description`,
                                            `uuid`,
                                            `version`,
                                            `os`,
                                            `metagenerator`,
                                            `entity_id`,
                                            `sub_packages`,
                                            `reboot`,
                                            `inventory_associateinventory`,
                                            `inventory_licenses`,
                                            `Qversion`,
                                            `Qvendor`,
                                            `Qsoftware`,
                                            `boolcnd`,
                                            `postCommandSuccess_command`,
                                            `postCommandSuccess_name`,
                                            `installInit_command`,
                                            `installInit_name`,
                                            `postCommandFailure_command`,
                                            `postCommandFailure_name`,
                                            `command_command`,
                                            `command_name`,
                                            `preCommand_command`,
                                            `preCommand_name`,
                                            `pkgs_share_id`,
                                            `edition_status`,
                                            `conf_json`,
                                            `size`)
                                            VALUES ("%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s","%s",
                                                    "%s","%s","%s","%s");""" % (
                fiche["label"],
                fiche["description"],
                fiche["uuid"],
                fiche["version"],
                fiche["os"],
                fiche["metagenerator"],
                fiche["entity_id"],
                fiche["sub_packages"],
                fiche["reboot"],
                fiche["inventory_associateinventory"],
                fiche["inventory_licenses"],
                fiche["Qversion"],
                fiche["Qvendor"],
                fiche["Qsoftware"],
                fiche["boolcnd"],
                fiche["postCommandSuccess_command"],
                fiche["postCommandSuccess_name"],
                fiche["installInit_command"],
                fiche["installInit_name"],
                fiche["postCommandFailure_command"],
                fiche["postCommandFailure_name"],
                fiche["command_command"],
                fiche["command_name"],
                fiche["preCommand_command"],
                fiche["preCommand_name"],
                fiche["pkgs_share_id"],
                fiche["edition_status"],
                fiche["conf_json"],
                fiche["size"],
            )
            logger.debug(f"sql {sql}")
            try:
                cursor = self.db.cursor()
                cursor.execute(sql)
                self.db.commit()
            except MySQLdb.Error as e:
                errorstr = f"{traceback.format_exc()}"
                logger.error("\n%s" % (errorstr))
            except Exception as e:
                errorstr = f"{traceback.format_exc()}"
                logger.error("\n%s" % (errorstr))
            finally:
                cursor.close()
        except Exception as e:
            errorstr = f"{traceback.format_exc()}"
            logger.error("\n%s" % (errorstr))

    def generate_conf_json(self, name, id, description, urlpath):
        """
        Génère le fichier JSON `conf.json` pour un package Windows.

        Cette fonction crée un template JSON minimal contenant :
            - l'URL du fichier à télécharger (`urlpath`)
            - les informations de localisation et de partage
            - les métadonnées du package (nom, ID, description, dates)
            - la configuration d'inventaire et des commandes
            - les informations de version et de reboot

        Paramètres :
            name (str)        : nom du package
            id (str)          : identifiant unique (UUID) du package
            description (str) : description du package
            urlpath (str)     : URL du fichier de mise à jour Windows

        Retour :
            str : contenu JSON complet sous forme de chaîne

        Effets de bord :
            Aucun, ne fait que retourner une chaîne JSON.
        """
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        return """{
            "urlpath" : "%s",
            "localisation_server": "%s",
            "sub_packages": [],
            "metagenerator": "manual",
            "description": "%s",
            "creator": "automate_medulla",
            "edition": "automate_medulla",
            "edition_date": "%s",
            "previous_localisation_server": "%s",
            "entity_id": "0",
            "creation_date": "%s",
            "inventory": {
                "associateinventory": "0",
                "licenses": "",
                "queries": {
                    "Qsoftware": "",
                    "Qvendor": "",
                    "boolcnd": "",
                    "Qversion": ""
                }
            },
            "version": "0.1",
            "reboot": 0,
            "editor": "",
            "targetos": "win",
            "commands": {
                "postCommandSuccess": {
                    "command": "",
                    "name": ""
                },
                "command": {
                    "command": "",
                    "name": ""
                },
                "postCommandFailure": {
                    "command": "",
                    "name": ""
                },
                "installInit": {
                    "command": "",
                    "name": ""
                },
                "preCommand": {
                    "command": "",
                    "name": ""
                }
            },
            "id": "%s",
            "name": "%s"
        }""" % (
            urlpath,
            self.param["partage"],
            description,
            dt_string,
            self.param["partage"],
            dt_string,
            id,
            name,
        )


def simplecommand(cmd):
    """
    Exécute une commande système en shell et récupère la sortie sous forme de liste de lignes.

    Paramètres :
        cmd (str) : commande shell à exécuter

    Retour :
        dict : dictionnaire contenant
            - "code"   : code de retour du processus (0 = succès)
            - "result" : liste des lignes de sortie (stdout + stderr)

    Effets de bord :
        - Exécute la commande dans le shell.
        - Les erreurs sont capturées dans `result` via stderr redirigé.
    """
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    obj = {"code": p.wait()}
    obj["result"] = result
    return obj


def simplecommandstr(cmd):
    """
    Exécute une commande système en shell et récupère la sortie sous forme de chaîne.

    Paramètres :
    cmd (str) : commande shell à exécuter

    Retour :
    dict : dictionnaire contenant
        - "code"   : code de retour du processus (0 = succès)
        - "result" : sortie complète combinée stdout + stderr sous forme de chaîne

    Effets de bord :
    - Exécute la commande dans le shell.
    - Les erreurs sont incluses dans `result`.
    """
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    result = p.stdout.readlines()
    obj = {"code": p.wait()}
    obj["result"] = "\n".join(result)
    return obj


def uuid_validate(uuid):
    """
    Vérifie si une chaîne donnée est un UUID valide au format standard.

    Le format attendu est : xxxxxxxx-xxxx-Mxxx-Nxxx-xxxxxxxxxxxx
    où M = version (0-5), N = variante (8,9,a,b)

    Paramètres :
    uuid (str) : chaîne à valider

    Retour :
    bool : True si la chaîne est un UUID valide, False sinon

    Exemples :
    uuid_validate("550e8400-e29b-41d4-a716-446655440000") -> True
    uuid_validate("invalid-uuid") -> False
    """
    if len(uuid) != 36:
        return False
    uuid_pattern = (
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    result = re.match(uuid_pattern, uuid)
    return result is not None


## Extract number from a string
# uuid_extract_pattern = "[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}"
# re.findall(uuid_extract_pattern, 'The UUID 123e4567-e89b-12d3-a456-426614174000 for node Node 01 is not unique.') # returns ['123e4567-e89b-12d3-a456-426614174000']


if __name__ == "__main__":
    # Quit the process if we don't want to continue
    signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

    parser = OptionParser()
    parser.add_option(
        "-H", "--host", dest="hostname", default="localhost", help="hostname SGBD"
    )

    parser.add_option("-P", "--port", dest="port", default=3306, help="port SGBD")

    parser.add_option("-u", "--user", dest="user", default="root", help="user account")

    parser.add_option(
        "-B", "--base", dest="base", default="xmppmaster", help="base sql name"
    )

    parser.add_option(
        "-p", "--password", dest="password", default="", help="password connection"
    )

    parser.add_option(
        "-t",
        "--testconnect",
        action="store_true",
        dest="testconnect",
        default=False,
        help="test connection and quit",
    )

    parser.add_option(
        "-T",
        "--nametable",
        dest="nametable",
        default="update_data",
        help="name table update",
    )

    parser.add_option(
        "-U",
        "--uidpackage",
        dest="uidpackage",
        default="",
        help="name uid package windows",
    )

    parser.add_option(
        "-C",
        "--forcecreatepackage",
        action="store_true",
        dest="forcecreatepackage",
        default=False,
        help="installation du package avec creation ou recreation",
    )

    parser.add_option(
        "-c",
        "--createpackage",
        action="store_true",
        dest="createpackage",
        default=False,
        help="installation du package avec creation si necessaire",
    )

    parser.add_option(
        "-S",
        "--forcedelpackage",
        action="store_true",
        dest="forcedelpackage",
        default=False,
        help="deinstallation du package et suppression complete",
    )

    parser.add_option(
        "-s",
        "--delpackage",
        action="store_true",
        dest="delpackage",
        default=False,
        help="deinstallation du package mais conserve package",
    )

    parser.add_option(
        "-o",
        "--outputdir",
        dest="outputdir",
        default="/var/lib/pulse2/base_update_package",
        help="path base directory generation package",
    )

    parser.add_option(
        "-M",
        "--share_dir_medulla ",
        dest="partage",
        default="winupdates",
        help="partage name",
    )

    parser.add_option(
        "-l",
        "--logfile",
        dest="logfile",
        default="/var/log/mmc/medulla-mariadb-synchro-update-package.log",
        help="file de configuration",
    )

    parser.add_option(
        "-d",
        "--debug",
        dest="debugmode",
        action="store_true",
        default=False,
        help="ecrit reference in code",
    )

    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        default=True,
        help="don't print status messages to stdout",
    )

    parser.add_option(
        "-i",
        "--info_parametre",
        action="store_true",
        dest="show_parametre",
        default=False,
        help="display tout les parametres and quit",
    )

    (opts, args) = parser.parse_args()

    try:
        if not os.path.exists(opts.logfile):
            if not os.path.isdir(os.path.dirname(opts.logfile)):
                os.makedirs(os.path.abspath(os.path.dirname(opts.logfile)))
            open(opts.logfile, "w").close()
    except Exception as e:
        errorstr = f"{traceback.format_exc()}"
        print("\n%s" % (errorstr))
        sys.exit(1)

    file_handler = logging.FileHandler(filename=opts.logfile)

    if opts.verbose:
        handlers = [file_handler]
    else:
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]
    level = logging.INFO
    format = "%(asctime)s - %(levelname)s - %(message)s"
    if opts.debugmode:
        # format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
        # format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
        format = "[%(asctime)s] {%(lineno)d} %(levelname)s - %(message)s"
        level = logging.DEBUG

    logging.basicConfig(level=level, format=format, handlers=handlers)

    logger = logging.getLogger()
    commandline = " ".join(sys.argv)
    logger.debug(f"comand line {commandline}")
    print(f'comand line {" ".join(sys.argv)}')

    parametre_display = vars(opts).copy()
    parametre_display["password"] = "xxxxx"
    parametre_dis = json.dumps(parametre_display, indent=4)
    if opts.debugmode:
        logger.debug(parametre_dis)
    if opts.show_parametre:
        print(
            "*************************************************************************************************************************"
        )
        print(
            "*********************************************** utility usage information ***********************************************"
        )
        print(
            "*************************************************************************************************************************"
        )
        print(f"your command line : {commandline}")
        print("Current or default option")
        print(parametre_dis)
        print("exemples")
        print("command information\n")
        print("\t1) affiche cette info option -i")
        print("\t\tpython3 ./%s -i\n" % os.path.basename(sys.argv[0]))
        print("\n\t2) test connection option -t")
        print(
            "\t\tpython3 ./%s -t -uroot -P 3306 -Hlocalhost -p siveo\n"
            % os.path.basename(sys.argv[0])
        )
        print("\tPARAMETRE CONNECION CORRECT: CONNECT SUCCESS")
        print("\ttest connection format debug")
        print(
            "\t\tpython3 ./%s -t -uroot -P 3306 -Hlocalhost -p siveo -d"
            % os.path.basename(sys.argv[0])
        )
        print(
            "try Connecting with parameters\n"
            "\thost: localhost\n"
            "\tuser: root\n"
            "\tport: 3306\n"
            "\tdb: 3306\n"
        )
        print("PARAMETRE CONNECION CORRECT: CONNECT SUCCESS\n")
        print(
            "\n\t3) forces the complete creation of an update package and installs it in pkgs option -C"
        )
        print(
            "\t\tpython3 ./%s -uroot -P 3306 -Hlocalhost -p siveo -U c9240667-c3d9-4ba0-8a4e-e258473f7b73 -C"
            % os.path.basename(sys.argv[0])
        )
        print("\t\tIf the package exists it is completely recreated")
        print("\t\tIf the package is installed it reinstalls it")
        print(
            "package c9240667-c3d9-4ba0-8a4e-e258473f7b73 is successfully installed\n"
        )

        print(
            "SELECT uuid FROM pkgs.packages where uuid='c9240667-c3d9-4ba0-8a4e-e258473f7b73';"
        )
        print("+--------------------------------------+")
        print("| uuid                                 |")
        print("+--------------------------------------+")
        print("| c9240667-c3d9-4ba0-8a4e-e258473f7b73 |    <<--- package installer  ")
        print("+--------------------------------------+")
        print("ls -al  /var/lib/pulse2/packages/sharing/winupdates/")
        print("c9240667-c3d9-4ba0-8a4e-e258473f7b73")

        print(
            "\n\t4 creation if no exist package and installs it in pkgs if is not installed option -c"
        )
        print(
            "\t\tpython3 ./%s -uroot -P 3306 -Hlocalhost -p siveo -U c9240667-c3d9-4ba0-8a4e-e258473f7b73 -c "
            % os.path.basename(sys.argv[0])
        )
        print("\t\tpackage exists c9240667-c3d9-4ba0-8a4e-e258473f7b73 already")
        print("\t\tpackage c9240667-c3d9-4ba0-8a4e-e258473f7b73 is installed in pkgs")

        print("\n\t5 uninstall package option -s")
        print(
            "\t\tpython3 ./%s -uroot -P 3306 -Hlocalhost -p siveo -U c9240667-c3d9-4ba0-8a4e-e258473f7b73 -s "
            % os.path.basename(sys.argv[0])
        )
        print("\t\tpackage move to base update : the package still exists")
        print("ls /var/lib/pulse2/base_update_package")
        print("c9240667-c3d9-4ba0-8a4e-e258473f7b73     <---the package still exists")
        print("ls  /var/lib/pulse2/packages/sharing/winupdates/    uninstall")
        print("uninstall pkgs")
        print(
            "SELECT * FROM pkgs.packages where uuid='c9240667-c3d9-4ba0-8a4e-e258473f7b73';"
        )
        print("Empty set (0.000 sec)  package uninstall in pkgs")

        print("\n\t6 complete uninstall package option -S")
        print(
            "\t\tpython3 ./%s -uroot -P 3306 -Hlocalhost -p siveo -U c9240667-c3d9-4ba0-8a4e-e258473f7b73 -S "
            % os.path.basename(sys.argv[0])
        )
        print("\t\tRemove package")
        print("\t\tthe package no longer exists")
        print(
            "ls /var/lib/pulse2/base_update_package    <---  the package no longer exists"
        )
        print(
            "ls  /var/lib/pulse2/packages/sharing/winupdates/    <---  the package no longer exists"
        )
        print("uninstall pkgs")
        print(
            "MariaDB [pkgs]> SELECT * FROM pkgs.packages where uuid='c9240667-c3d9-4ba0-8a4e-e258473f7b73';"
        )
        print("Empty set (0.000 sec)  package uninstall in pkgs")
        print(
            "*************************************************************************************************************************"
        )
        sys.exit(1)

    if opts.partage == "":
        print("name partage missing")
    path_partage = os.path.join("/var/lib/pulse2/packages/sharing/", opts.partage)

    # if opts.outputdir == "/var/lib/pulse2/packages/base_update_package":
    # opts.outputdir=os.path.join(opts.outputdir, opts.table_name)

    # print ( "path_partage %s " % path_partage)

    Passwordbase = ""
    if opts.password != "":
        Passwordbase = opts.password
    else:
        print("key password input ????")
        Passwordbase = getpass.getpass(
            prompt=f"Password for mysql://{opts.user}:<password>@{opts.hostname}:{opts.port}/{opts.base}",
            stream=None,
        )
    if Passwordbase == "":
        print("Connecting parameters password missing")
        sys.exit(1)
    if opts.testconnect:
        print(
            "try Connecting with parameters\n"
            "\thost: %s\n"
            "\tuser: %s\n"
            "\tport: %s\n"
            "\tdb: %s\n" % (opts.hostname, opts.user, int(opts.port), opts.base)
        )
        try:
            db = MySQLdb.connect(
                host=opts.hostname,
                user=opts.user,
                passwd=Passwordbase,
                port=int(opts.port),
                db=opts.base,
            )
            print("CORRECT CONNECTION PARAMETER: CONNECT SUCCESS")
            logger.debug("CONECTION SUCCES : TEST TERMINER OK")
        except Exception as e:
            errorstr = f"{traceback.format_exc()}"
            print("\n%s" % (errorstr))
        finally:
            db.close()
            sys.exit(1)

    nbtrue = len(
        [
            x
            for x in [
                opts.forcecreatepackage,
                opts.createpackage,
                opts.forcedelpackage,
                opts.delpackage,
            ]
            if x
        ]
    )
    valquit = 0
    if nbtrue != 1:
        print(
            "at least 1 of the following options is required (sScC) -s or -S or -c or -C"
        )
        valquit = 1

    if opts.uidpackage == "":
        print("you must have the -U option to specify the update uuid")
        logger.debug("you must have the -U option to specify the update uuid")
        sys.exit(1)

    if len(opts.uidpackage) != 36 or uuid_validate(opts.uidpackage) is None:
        print("uuid de l'option U n'est pas conforme")
        # obligatoirement ce parametre avec 1 uuid valable pour option -u")
        print(uuid_validate(opts.uidpackage))
        valquit = 1

    if opts.nametable == "":
        print("l'option -T 'table produit' ne peut pas etre vide")
        valquit = 1

    if valquit:
        print(
            "at least 1 of the following options is required (sScC) -s or -S or -c or -C"
        )

        sys.exit(1)
    try:
        # db = MySQLdb.connect(host=opts.hostname,
        # user=opts.user,
        # passwd=Passwordbase,
        # port = int(opts.port),
        # db=opts.base)
        db = MySQLdb.connect(
            host=opts.hostname, user=opts.user, passwd=Passwordbase, port=int(opts.port)
        )
        logger.debug("CONNECT SUCCESS")

        logger.debug("Generate the packages")

        # if opts.forcecreatepackage or opts.createpackage or opts.forcedelpackage or opts.delpackage:
        # il y a au moin 1 demande
        # verification qu'il y ai 1 seule demande

        generateur = synch_packages(db, vars(opts))
        # generateur = synch_packages(db, opts ).search_file_update()

    except Exception as e:
        errorstr = f"{traceback.format_exc()}"
        print("ERROR CONNECTION")
        print("\n%s" % (errorstr))
        logger.error("\n%s" % (errorstr))
        sys.exit(1)
    finally:
        db.close()
