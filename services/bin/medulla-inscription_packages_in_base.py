#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour inscrire ou mettre à jour les packages existants dans la base MySQL.

Chaque package est un dossier UUID (36 caractères) dans /var/lib/pulse2/packages.
Le script lit les fichiers conf.json, calcule la taille et ajoute ou met à jour la table packages.
Les packages peuvent être liés à un partage (pkgs_share_id).
"""

import os
import sys
import json
import logging
import argparse
import subprocess
import traceback
import getpass
import MySQLdb

# ----------------------
# Configuration logging
# ----------------------
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ----------------------
# Fonctions utilitaires
# ----------------------
def simplecommand(cmd):
    """
    Exécute une commande shell et renvoie le code et la sortie en str.
    """
    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,   # str au lieu de bytes
        check=False,
    )
    return {"code": result.returncode, "result": result.stdout.splitlines()}


def find_packages(packagedir):
    """
    Parcours récursif de packagedir pour trouver tous les packages (dossiers UUID de 36 caractères).
    Les liens symboliques sont ignorés.

    Returns:
        list[str]: liste des chemins complets des packages
    """
    packages = []
    for root, dirs, files in os.walk(packagedir, followlinks=False):
        # Éviter de descendre dans les liens symboliques
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
        for d in dirs:
            if len(d) == 36 and os.path.isdir(os.path.join(root, d)):
                packages.append(os.path.join(root, d))
    return packages


def loadjsonfile(filename):
    """
    Lit un fichier JSON et retourne son contenu.
    Retourne None en cas d'erreur avec log.
    """
    if not os.path.isfile(filename):
        logger.error("Fichier JSON manquant : %s", filename)
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error("JSON invalide (%s) : %s", filename, e)
    except Exception as e:
        logger.error("Erreur lecture %s : %s", filename, e)
    return None


def get_nested(d, *keys, default=""):
    """
    Récupère une valeur dans un dictionnaire imbriqué.
    Retourne default si une clé est manquante.

    Exemple:
        get_nested(conf, "commands", "preCommand", "name")
    """
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d


# ----------------------
# Fonction principale
# ----------------------
def main():
    # Arguments CLI
    parser = argparse.ArgumentParser(description="Register existing packages into MySQL database")
    parser.add_argument("-H", "--hostname", default="localhost", help="Hostname MySQL")
    parser.add_argument("-P", "--port", default=3306, type=int, help="Port MySQL")
    parser.add_argument("-u", "--user", default="root", help="Utilisateur MySQL")
    parser.add_argument("-p", "--password", default="", help="Mot de passe MySQL")
    parser.add_argument("-g", "--regeneratetable", action="store_true", help="Supprime tous les packages avant insertion")
    parser.add_argument(
        "-D", "--debug",
        action="store_true",
        help="Active le mode debug"
    )
    args = parser.parse_args()
    # Configuration du logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s"
    )
    dbname = "pkgs"
    password = args.password or getpass.getpass(f"Password for mysql://{args.user}@{args.hostname}:{args.port}/{dbname}: ")

    # Répertoire des packages
    packagedir = "/var/lib/pulse2/packages"
    list_package = find_packages(packagedir)
    logger.info("Packages trouvés : %d", len(list_package))
    # supprimer uniquement les liens symboliques dans
    # /var/lib/pulse2/packages
    for entry in os.listdir(packagedir):
        path = os.path.join(packagedir, entry)

        try:
            if os.path.islink(path):
                os.remove(path)
                logger.info("Lien symbolique supprimé : %s", path)
        except OSError as e:
            logger.error(
                "Erreur lors de la suppression du lien symbolique %s : %s",
                path, e
            )

    # Connexion MySQL
    try:
        db = MySQLdb.connect(
            host=args.hostname,
            user=args.user,
            passwd=password,
            port=args.port,
            db=dbname,
            charset="utf8mb4"
        )
        cursor = db.cursor()

        # Optionnel : réinitialisation de la table
        if args.regeneratetable:
            logger.info("Réinitialisation de la table packages...")
            cursor.execute("DELETE FROM packages")
            db.commit()

        # Requête d'insertion avec ON DUPLICATE KEY UPDATE pour gérer les packages existants
        insert_sql = """
            INSERT INTO packages (
                label, description, uuid, version, os, metagenerator,
                entity_id, sub_packages, reboot,
                inventory_associateinventory, inventory_licenses,
                Qversion, Qvendor, Qsoftware, boolcnd,
                postCommandSuccess_command, postCommandSuccess_name,
                installInit_command, installInit_name,
                postCommandFailure_command, postCommandFailure_name,
                command_command, command_name,
                preCommand_command, preCommand_name,
                pkgs_share_id, edition_status, conf_json, size
            ) VALUES (
                %(label)s, %(description)s, %(uuid)s, %(version)s, %(os)s,
                %(metagenerator)s, %(entity_id)s, %(sub_packages)s, %(reboot)s,
                %(inventory_associateinventory)s, %(inventory_licenses)s,
                %(Qversion)s, %(Qvendor)s, %(Qsoftware)s, %(boolcnd)s,
                %(postCommandSuccess_command)s, %(postCommandSuccess_name)s,
                %(installInit_command)s, %(installInit_name)s,
                %(postCommandFailure_command)s, %(postCommandFailure_name)s,
                %(command_command)s, %(command_name)s,
                %(preCommand_command)s, %(preCommand_name)s,
                %(pkgs_share_id)s, 1, %(conf_json)s, %(size)s
            )
            ON DUPLICATE KEY UPDATE
                label=VALUES(label),
                description=VALUES(description),
                version=VALUES(version),
                os=VALUES(os),
                metagenerator=VALUES(metagenerator),
                entity_id=VALUES(entity_id),
                sub_packages=VALUES(sub_packages),
                reboot=VALUES(reboot),
                inventory_associateinventory=VALUES(inventory_associateinventory),
                inventory_licenses=VALUES(inventory_licenses),
                Qversion=VALUES(Qversion),
                Qvendor=VALUES(Qvendor),
                Qsoftware=VALUES(Qsoftware),
                boolcnd=VALUES(boolcnd),
                postCommandSuccess_command=VALUES(postCommandSuccess_command),
                postCommandSuccess_name=VALUES(postCommandSuccess_name),
                installInit_command=VALUES(installInit_command),
                installInit_name=VALUES(installInit_name),
                postCommandFailure_command=VALUES(postCommandFailure_command),
                postCommandFailure_name=VALUES(postCommandFailure_name),
                command_command=VALUES(command_command),
                command_name=VALUES(command_name),
                preCommand_command=VALUES(preCommand_command),
                preCommand_name=VALUES(preCommand_name),
                pkgs_share_id=VALUES(pkgs_share_id),
                conf_json=VALUES(conf_json),
                size=VALUES(size);
        """

        # Parcours des packages
        for package in list_package:
            try:
                pkg_name = os.path.basename(package)
                share_name = os.path.basename(os.path.dirname(package))
                logger.debug("Install package %s (partage: %s)", pkg_name, share_name)

                conf_path = os.path.join(package, "conf.json")
                conf = loadjsonfile(conf_path)
                if not conf:
                    logger.error("Package ignoré (conf.json invalide) : %s", package)
                    continue

                # Taille du package
                du = simplecommand(f"du -b {package}")
                size = int(du["result"][0].split()[0]) if du["result"] else 0

                # Déterminer le nom du partage
                parts = os.path.normpath(package).split(os.sep)
                pkgs_share_name = ""
                if "sharing" in parts:
                    idx = parts.index("sharing")
                    if len(parts) > idx + 1:
                        pkgs_share_name = parts[idx + 1]

                # Récupérer pkgs_share_id
                pkgs_share_id = None
                if pkgs_share_name:
                    os.symlink(package, os.path.join(packagedir, os.path.basename(package)))
                    cursor.execute("SELECT id FROM pkgs.pkgs_shares WHERE name = %s", (pkgs_share_name,))
                    res = cursor.fetchone()
                    if res:
                        pkgs_share_id = res[0]
                    else:
                        logger.warning("Pas de partage trouvé pour %s, pkgs_share_id = NULL", pkgs_share_name)

                # Préparer les données pour insertion
                data = {
                    "label": get_nested(conf, "name"),
                    "description": get_nested(conf, "description"),
                    "uuid": get_nested(conf, "id"),
                    "version": get_nested(conf, "version"),
                    "os": get_nested(conf, "targetos"),
                    "metagenerator": get_nested(conf, "metagenerator"),
                    "entity_id": get_nested(conf, "entity_id"),
                    "sub_packages": json.dumps(get_nested(conf, "sub_packages", default=[])),
                    "reboot": get_nested(conf, "reboot"),
                    "inventory_associateinventory": get_nested(conf, "inventory", "associateinventory"),
                    "inventory_licenses": get_nested(conf, "inventory", "licenses"),
                    "Qversion": get_nested(conf, "inventory", "queries", "Qversion"),
                    "Qvendor": get_nested(conf, "inventory", "queries", "Qvendor"),
                    "Qsoftware": get_nested(conf, "inventory", "queries", "Qsoftware"),
                    "boolcnd": get_nested(conf, "inventory", "queries", "boolcnd"),
                    "postCommandSuccess_command": get_nested(conf, "commands", "postCommandSuccess", "command"),
                    "postCommandSuccess_name": get_nested(conf, "commands", "postCommandSuccess", "name"),
                    "installInit_command": get_nested(conf, "commands", "installInit", "command"),
                    "installInit_name": get_nested(conf, "commands", "installInit", "name"),
                    "postCommandFailure_command": get_nested(conf, "commands", "postCommandFailure", "command"),
                    "postCommandFailure_name": get_nested(conf, "commands", "postCommandFailure", "name"),
                    "command_command": get_nested(conf, "commands", "command", "command"),
                    "command_name": get_nested(conf, "commands", "command", "name"),
                    "preCommand_command": get_nested(conf, "commands", "preCommand", "command"),
                    "preCommand_name": get_nested(conf, "commands", "preCommand", "name"),
                    "conf_json": json.dumps(conf),
                    "size": size,
                    "pkgs_share_id": pkgs_share_id
                }

                cursor.execute(insert_sql, data)
                db.commit()
                logger.info("Package ajouté/mis à jour : %s (share: %s)", get_nested(conf, "name"), pkgs_share_name)

            except Exception as e:
                logger.error("Erreur package %s : %s", package, e)
                logger.debug(traceback.format_exc())

    except Exception as e:
        logger.error("Erreur générale : %s", e)
        logger.debug(traceback.format_exc())
        sys.exit(1)
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    main()
