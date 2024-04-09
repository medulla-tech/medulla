# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys

PYTHON_VERSION = sys.version_info.major


class xmppbrowsing:
    """ """

    def __init__(self, defaultdir=None, rootfilesystem=None):
        """
        :param type: Uses this parameter to give a path abs
        :type defaultdir: string
        :type rootfilesystem :string
        :return: Function init has no return
        """
        self.defaultdir = None
        self.rootfilesystem = None
        self.dirinfos = {}

        if defaultdir is not None:
            self.defaultdir = defaultdir
        if rootfilesystem is not None:
            self.rootfilesystem = rootfilesystem
        self.listfileindir()

    def listfileindir1(self, path_abs_current=None):
        if path_abs_current is None or path_abs_current == "":
            if self.defaultdir is None:
                pathabs = os.getcwd()
            else:
                pathabs = self.defaultdir
        else:
            if self.rootfilesystem in path_abs_current:
                pathabs = os.path.abspath(path_abs_current)
            else:
                pathabs = self.rootfilesystem
        # TODO: Remove MIGRATION3
        self.dirinfos = {
            "path_abs_current": pathabs,
            "list_dirs_current": (
                os.walk(pathabs).next()[1]
                if PYTHON_VERSION == 2
                else next(os.walk(pathabs))[1]
            ),
            "list_files_current": (
                os.walk(pathabs).next()[2]
                if PYTHON_VERSION == 2
                else next(os.walk(pathabs))[2]
            ),
            "parentdir": os.path.abspath(os.path.join(pathabs, os.pardir)),
            "rootfilesystem": self.rootfilesystem,
            "defaultdir": self.defaultdir,
        }
        return self.dirinfos

    # def listfileindir(self, path_abs_current=None):
    # if path_abs_current is None or path_abs_current == "":
    # if self.defaultdir is None:
    # pathabs = os.getcwd()
    # else:
    # pathabs = self.defaultdir
    # else:
    # if self.rootfilesystem in path_abs_current:
    # pathabs = os.path.abspath(path_abs_current)
    # else:
    # pathabs = self.rootfilesystem
    ## TODO: Remove MIGRATION3
    # list_files_current = (
    # os.walk(pathabs).next()[2]
    # if PYTHON_VERSION == 2
    # else next(os.walk(pathabs))[2]
    # )
    # ff = []
    # for t in list_files_current:
    # fii = os.path.join(pathabs, t)
    # ff.append((t, os.path.getsize(fii)))
    ## TODO: Remove MIGRATION3
    # self.dirinfos = {
    # "path_abs_current": pathabs,
    # "list_dirs_current": os.walk(pathabs).next()[1]
    # if PYTHON_VERSION == 2
    # else next(os.walk(pathabs))[1],
    # "list_files_current": ff,
    # "parentdir": os.path.abspath(os.path.join(pathabs, os.pardir)),
    # "rootfilesystem": self.rootfilesystem,
    # "defaultdir": self.defaultdir,
    # }
    # return self.dirinfos

    def listfileindir(self, path_abs_current=None):
        """
        Liste les fichiers et dossiers dans le répertoire spécifié.

        Si aucun chemin n'est fourni, utilise le répertoire par défaut.

        Args:
            path_abs_current (str, optional): Le chemin absolu du répertoire à lister.
                Si non spécifié, utilise le répertoire par défaut.

        Returns:
            dict: Un dictionnaire contenant les informations suivantes :
                - 'path_abs_current' : Chemin absolu du répertoire actuel.
                - 'list_dirs_current' : Liste des noms de dossiers dans le répertoire.
                - 'list_files_current' : Liste des tuples (nom de fichier, taille)
                pour les fichiers dans le répertoire.
                - 'parentdir' : Chemin absolu du répertoire parent.
                - 'rootfilesystem' : Racine du système de fichiers.
                - 'defaultdir' : Répertoire par défaut.

        Raises:
            OSError: Si le chemin spécifié n'existe pas.

        Example:
            Pour lister le contenu du répertoire '/chemin/vers/repertoire' :
            >>> dir_info = listfileindir('/chemin/vers/repertoire')
        """
        if path_abs_current is None or path_abs_current == "":
            if self.defaultdir is None:
                pathabs = os.getcwd()
            else:
                pathabs = self.defaultdir
        else:
            if self.rootfilesystem in path_abs_current:
                pathabs = os.path.abspath(path_abs_current)
            else:
                pathabs = self.rootfilesystem

        # Utilisation de `os.walk()` pour obtenir les listes de dossiers et de fichiers
        _, list_dirs_current, list_files_current = next(os.walk(pathabs))

        # Création de la liste des fichiers avec leurs tailles
        ff = [
            (t, os.path.getsize(os.path.join(pathabs, t))) for t in list_files_current
        ]

        self.dirinfos = {
            "path_abs_current": pathabs,
            "list_dirs_current": list_dirs_current,
            "list_files_current": ff,
            "parentdir": os.path.abspath(os.path.join(pathabs, os.pardir)),
            "rootfilesystem": self.rootfilesystem,
            "defaultdir": self.defaultdir,
        }
        return self.dirinfos


# dirname(path): retourne le répertoire associé au path ;
# basename(path): retourne le nom simple du fichier (extension comprise) ;
# split(path): retourne le couple (répertoire, nom du fichier) ;
# splitdrive(path): retourne le couple (lecteur, chemin du fichier sans le lecteur) ;
# splitext(path): retourne le couple (chemin du fichier sans l'extension, extension) ;
# splitunc(path): retourne le couple (unc, rest) où unc est du type \\h
