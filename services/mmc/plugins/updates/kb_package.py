#!/usr/bin/env python3
"""Utilitaires de generation de packages Medulla pour la desinstallation de KB Windows."""

import argparse
import os
import json
import uuid
import random
import string
import shutil
from datetime import datetime

# exemple utilisation
# from kb_package import KBUninstallPackage

# base_winupdates = os.path.join("/", "var", "lib", "pulse2", "packages", "sharing", "winupdates")
# # Créer ou recréer le package KB
# pkg = KBUninstallPackage("KB5030211", base_path="./packages", recreate=True)
# pkg.create_package()
#
# # Supprimer le package
# # pkg.delete_package()


class KBUninstallPackage:
    """Construit sur disque un package Medulla pour desinstaller une KB Windows.

    La classe genere un repertoire de package avec un nom compatible Medulla,
    un script PowerShell de desinstallation ainsi que les metadonnees JSON
    attendues par la plateforme de deploiement.
    """

    def __init__(self, kb, base_path=".", create_if_missing=True, recreate=False):
        """Initialise le contexte de generation du package de desinstallation.

        Args:
            kb: Identifiant KB a traiter, avec ou sans prefixe ``KB``.
            base_path: Repertoire racine dans lequel creer le package.
            create_if_missing: Autorise la creation du repertoire cible.
            recreate: Supprime puis recree le package si le dossier existe deja.
        """
        self.kb = str(kb).upper().replace("KB", "")
        self.base_path = os.path.abspath(base_path)
        self.create_if_missing = create_if_missing
        self.recreate = recreate
        self.dir_name = self.generate_directory_name(self.kb)
        self.full_path = os.path.join(self.base_path, self.dir_name)

        # Préparer le répertoire
        self.prepare_directory()

    # -------------------------
    # Gestion répertoire
    # -------------------------
    def prepare_directory(self):
        """Prepare le repertoire du package avant generation des fichiers.

        Si le dossier existe deja, il peut etre recree selon ``self.recreate``.
        Sinon il est cree sous ``self.base_path``.
        """
        if os.path.exists(self.full_path):
            if self.recreate:
                shutil.rmtree(self.full_path)
                os.makedirs(self.full_path)
            else:
                if not self.create_if_missing:
                    raise FileExistsError(f"{self.full_path} existe déjà")
        else:
            os.makedirs(self.full_path)

    # -------------------------
    # Génération noms / fichiers
    # -------------------------
    def generate_directory_name(self, kb):
        """Genere un nom de dossier de longueur fixe pour le package.

        Le nom combine un prefixe pseudo-UUID et une base lisible issue du KB,
        puis ajuste la longueur finale a 36 caracteres.
        """
        uuid_part = str(uuid.uuid4()).split('-')[0]
        base_name = f"uninstallKB{kb}forx64bas"
        dir_name = f"{uuid_part}-{base_name}"
        if len(dir_name) > 36:
            dir_name = dir_name[:36]
        elif len(dir_name) < 36:
            needed = 36 - len(dir_name)
            random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=needed))
            dir_name = f"{dir_name}{random_part}"
        return dir_name

    def generate_powershell_script(self):
        """Construit le script PowerShell charge de desinstaller la KB.

        Returns:
            Le contenu du script au format texte avec fins de ligne Windows.
        """
        kb_array = f'"{self.kb}"'
        script = f"""$KBs = @({kb_array})
Write-Output "===== Début traitement ====="
foreach ($KB in $KBs) {{
    $kbFull = "KB$KB"
    Write-Output "Traitement $kbFull..."
    $installed = Get-HotFix -Id $kbFull -ErrorAction SilentlyContinue
    if ($installed) {{
        Write-Output "$kbFull détectée → désinstallation"
        $process = Start-Process "wusa.exe" `
            -ArgumentList "/uninstall /kb:$KB /quiet /norestart" `
            -Wait -PassThru
        if ($process.ExitCode -eq 0) {{
            Write-Output "Succès désinstallation $kbFull"
        }} else {{
            Write-Output "Erreur désinstallation $kbFull (code $($process.ExitCode))"
        }}
    }} else {{
        Write-Output "$kbFull absente → rien à faire"
    }}
}}
Write-Output "===== Fin ====="
"""
        return script.replace("\n", "\r\n")

    def generate_conf_json(self):
        """Construit le contenu du fichier ``conf.json`` du package.

        Returns:
            Un dictionnaire conforme au format de configuration Medulla.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "sub_packages": [],
            "description": "A security or compatibility issue has been identified with a Microsoft software update installed on your system To maintain system stability and proper functionality this update will be removed",
            "entity_id": "0",
            "creator": "automate_medulla",
            "edition": "automate_medulla",
            "id": self.dir_name,
            "localisation_server": "winupdates",
            "previous_localisation_server": "winupdates",
            "creation_date": now,
            "editor": "root",
            "edition_date": now,
            "commands": {
                "postCommandSuccess": {"command": "", "name": ""},
                "installInit": {"command": "", "name": ""},
                "postCommandFailure": {"command": "", "name": ""},
                "command": {"command": "", "name": ""},
                "preCommand": {"command": "", "name": ""}
            },
            "name": f"uninstall KB{self.kb} for x64-based",
            "targetos": "win",
            "reboot": 0,
            "version": "0.1",
            "metagenerator": "manual",
            "inventory": {
                "associateinventory": "0",
                "licenses": "1.0",
                "queries": {
                    "Qversion": "",
                    "Qvendor": "",
                    "Qsoftware": "",
                    "boolcnd": ""
                }
            }
        }

    def generate_xmppdeploy_json(self):
        """Construit le contenu du fichier ``xmppdeploy.json`` du package.

        Returns:
            Un dictionnaire de deploiement utilise par l'agent XMPP.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "info": {
                "Dependency": [],
                "editor": "automate_medulla",
                "edition_date": now,
                "creator": "automate_medulla",
                "creation_date": now,
                "previous_localisation_server": "winupdates",
                "localisation_server": "winupdates",
                "name": f"uninstall KB{self.kb} for x64-based",
                "version": "0.1",
                "description": "A security or compatibility issue has been identified with a Microsoft software update installed on your system To maintain system stability and proper functionality this update will be removed",
                "metagenerator": "manual",
                "transferfile": True,
                "methodetransfert": "pushrsync",
                "licenses": "1.0",
                "packageUuid": self.dir_name,
                "software": f"uninstall KB{self.kb} for x64-based"
            },
            "win": {
                "sequence": [
                    {
                        "action": "actionprocessscriptfile",
                        "step": 0,
                        "typescript": "Batch",
                        "script": "cG93ZXJzaGVsbC5leGUgLUV4ZWN1dGlvblBvbGljeSBCeXBhc3MgLUZpbGUgdW5pbnN0YWxsX2tiLnBzMQ==",
                        "gotoreturncode@!=0": "END_ERROR"
                    },
                    {"step": 1, "action": "actionsuccescompletedend", "actionlabel": "END_SUCCESS", "clear": True},
                    {"step": 2, "action": "actionerrorcompletedend", "actionlabel": "END_ERROR"}
                ]
            },
            "metaparameter": {"os": ["win"], "uuid": self.dir_name}
        }

    # -------------------------
    # Créer tous les fichiers
    # -------------------------
    def create_package(self):
        """Genere tous les fichiers du package sur disque.

        Cree successivement le script PowerShell, ``conf.json`` et
        ``xmppdeploy.json`` dans le repertoire du package.

        Returns:
            Le chemin complet du package genere.
        """
        # PowerShell
        ps_path = os.path.join(self.full_path, "uninstall_kb.ps1")
        with open(ps_path, "w", encoding="utf-8") as f:
            f.write(self.generate_powershell_script())

        # conf.json
        conf_path = os.path.join(self.full_path, "conf.json")
        with open(conf_path, "w", encoding="utf-8") as f:
            json.dump(self.generate_conf_json(), f, indent=4)

        # xmppdeploy.json
        xmpp_path = os.path.join(self.full_path, "xmppdeploy.json")
        with open(xmpp_path, "w", encoding="utf-8") as f:
            json.dump(self.generate_xmppdeploy_json(), f, indent=4)

        print(f"✅ Package créé : {self.full_path}")
        return self.full_path

    # -------------------------
    # Supprimer package
    # -------------------------
    def delete_package(self):
        """Supprime le repertoire du package s'il existe deja."""
        if os.path.exists(self.full_path):
            shutil.rmtree(self.full_path)
            print(f"🗑️ Package supprimé : {self.full_path}")
        else:
            print(f"⚠️ Le package n'existe pas : {self.full_path}")


def build_argument_parser():
    """Construit le parseur d'arguments de l'utilitaire en ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Genere ou supprime un package Medulla de desinstallation de KB."
    )
    parser.add_argument("action", choices=["create", "delete"], help="Action a executer")
    parser.add_argument("kb", help="Identifiant KB a traiter, avec ou sans prefixe KB")
    parser.add_argument(
        "--base-path",
        default=".",
        help="Repertoire racine dans lequel creer ou rechercher le package",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Supprime puis recree le package s'il existe deja",
    )
    parser.add_argument(
        "--no-create-if-missing",
        action="store_true",
        help="Echoue si le repertoire du package n'existe pas deja",
    )
    return parser


def main():
    """Execute l'utilitaire en ligne de commande."""
    parser = build_argument_parser()
    args = parser.parse_args()

    package = KBUninstallPackage(
        args.kb,
        base_path=args.base_path,
        create_if_missing=not args.no_create_if_missing,
        recreate=args.recreate,
    )

    if args.action == "create":
        package.create_package()
        return 0

    package.delete_package()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
