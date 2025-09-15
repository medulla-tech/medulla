# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
XML-RPC server implementation of the MMC agent.
"""

from resource import RLIMIT_NOFILE, RLIM_INFINITY, getrlimit
import signal
import multiprocessing as mp
from inspect import getfullargspec, currentframe, getframeinfo
import base64
import zlib
import string
import yaml
from collections import OrderedDict
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import xmltodict

import twisted.internet.error
import twisted.copyright
from twisted.web import xmlrpc, server
from twisted.web.xmlrpc import XMLRPC, Handler
from twisted.internet import reactor, defer
from twisted.python import failure
import json

try:
    from twisted.web import http
except ImportError:
    from twisted.protocols import http  # pyflakes.ignore

from mmc.site import localstatedir
from mmc.ssl import makeSSLContext
from mmc.support.mmctools import Singleton
from mmc.core.version import scmRevision
from mmc.core.audit import AuditFactory
from mmc.core.log import ColoredFormatter

# from mmc.plugins.xmppmaster.master.lib import convert

from decimal import Decimal
import importlib
import logging
import logging.config
import xmlrpc.client
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import configparser
import glob
import time
import pwd
import grp
import threading
import re
import zipfile
import traceback
import time
import sys

import random

# import posix_ipc
import socket
import ssl
import gzip

from pulse2.database.xmppmaster import XmppMasterDatabase
from datetime import datetime, timedelta

logger = logging.getLogger()

sys.path.append("plugins")

Fault = xmlrpc.client.Fault
ctx = None
VERSION = "5.3.0"

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

    def listfileindir(self, path_abs_current=None):
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
        list_files_current = (
            os.walk(pathabs).next()[2]
            if PYTHON_VERSION == 2
            else next(os.walk(pathabs))[2]
        )
        ff = []
        for t in list_files_current:
            fii = os.path.join(pathabs, t)
            ff.append((t, os.path.getsize(fii)))
        # TODO: Remove MIGRATION3
        self.dirinfos = {
            "path_abs_current": pathabs,
            "list_dirs_current": (
                os.walk(pathabs).next()[1]
                if PYTHON_VERSION == 2
                else next(os.walk(pathabs))[1]
            ),
            "list_files_current": ff,
            "parentdir": os.path.abspath(os.path.join(pathabs, os.pardir)),
            "rootfilesystem": self.rootfilesystem,
            "defaultdir": self.defaultdir,
        }
        return self.dirinfos


# decorateur mesure temps d'une fonction
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Temps d'exécution de {func.__name__}: {execution_time} secondes")
        return result

    return wrapper


def log_params(func):
    def wrapper(*args, **kwargs):
        print(f"Paramètres positionnels : {args}")
        print(f"Paramètres nommés : {kwargs}")
        result = func(*args, **kwargs)
        return result

    return wrapper


def log_details(func):
    def wrapper(*args, **kwargs):
        frame = currentframe().f_back
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno
        function_name = func.__name__
        print(f"Nom de la fonction : {function_name}")
        print(f"Fichier : {filename}, ligne : {line_number}")
        print(f"Paramètres positionnels : {args}")
        print(f"Paramètres nommés : {kwargs}")
        result = func(*args, **kwargs)
        return result

    return wrapper


def log_details_debug_info(func):
    def wrapper(*args, **kwargs):
        frame = currentframe().f_back
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno
        function_name = func.__name__
        # Configuration du logger
        logger = logging.getLogger(function_name)
        logger.setLevel(logging.INFO)
        # Configuration du format de log
        log_format = f"{function_name} - Ligne {line_number} - %(message)s"
        formatter = logging.Formatter(log_format)
        # Configuration du handler de log vers la console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        # Log des paramètres passés à la fonction
        logger.info(f"Paramètres positionnels : {args}")
        logger.info(f"Paramètres nommés : {kwargs}")
        result = func(*args, **kwargs)
        return result

    return wrapper


def generate_log_line(message):
    frame = currentframe().f_back
    file_name = getframeinfo(frame).filename
    line_number = frame.f_lineno
    log_line = f"[{file_name}:{line_number}] - {message}"
    return log_line


def display_message(message):
    frame = currentframe().f_back
    file_name = getframeinfo(frame).filename
    line_number = frame.f_lineno
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.INFO)
    # Configuration du handler de stream (affichage console)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    log_line = generate_log_line(message)
    logger.info(log_line)


def generer_mot_de_passe(taille):
    """
    Cette fonction permet de generer 1 mot de passe aléatoire
    le parametre taille precise le nombre de caractere du mot de passe
    renvoi le mot de passe

    eg : mot_de_passe = generer_mot_de_passe(32)
    """
    caracteres = string.ascii_letters + string.digits + string.punctuation
    mot_de_passe = "".join(random.choice(caracteres) for _ in range(taille))
    return mot_de_passe


class MotDePasse:
    def __init__(
        self,
        taille,
        temps_validation=60,
        caracteres_interdits=""""()[],%:|`.{}'><\\/^""",
    ):
        self.taille = taille
        self.caracteres_interdits = [x for x in caracteres_interdits]
        self.temps_validation = temps_validation
        self.mot_de_passe = self.generer_mot_de_passe()
        self.date_expiration = self.calculer_date_expiration()

    def generer_mot_de_passe(self):
        caracteres = string.ascii_letters + string.digits + string.punctuation
        for caractere_interdit in self.caracteres_interdits:
            caracteres = caracteres.replace(caractere_interdit, "")
        mot_de_passe = "".join(random.choice(caracteres) for _ in range(self.taille))
        return mot_de_passe

    def calculer_date_expiration(self):
        return datetime.now() + timedelta(seconds=self.temps_validation)

    def verifier_validite(self):
        temps_restant = (self.date_expiration - datetime.now()).total_seconds()
        return temps_restant

    def est_valide(self):
        return datetime.now() < self.date_expiration

    # def generer_qr_code(self, nom_fichier):
    # qr = qrcode.QRCode(version=1, box_size=10, border=4)
    # qr.add_data(self.mot_de_passe)
    # qr.make(fit=True)
    # qr_img = qr.make_image(fill="black", back_color="white")
    # qr_img.save(nom_fichier)
    # print(f"QR code généré et sauvegardé dans {nom_fichier}.")


class DateTimebytesEncoderjson(json.JSONEncoder):
    """
    Used to handle datetime in json files.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.isoformat()
        elif isinstance(obj, bytes):
            encoded_object = obj.decode("utf-8")
        else:
            encoded_object = json.JSONEncoder.default(self, obj)
        return encoded_object


class convert:
    """
        Cette classe fournit des méthodes utilitaires pour convertir et manipuler des objets entre différents formats :
        YAML, JSON, XML, dictionnaires, listes, chaînes de caractères, etc.
        Elle inclut également des fonctions pour la compression, l'encodage, la validation et la comparaison de données.

        ---
        ### Catalogue des fonctions disponibles :

        #### 1. YAML
        - `convert_dict_to_yaml(input_dict)` : Convertit un dictionnaire en chaîne YAML.
        - `convert_yaml_to_dict(yaml_string)` : Convertit une chaîne YAML en dictionnaire.
        - `yaml_string_to_dict(yaml_string)` : Convertit une chaîne YAML en dictionnaire (version détaillée).
        - `check_yaml_conformance(yaml_data)` : Vérifie si une chaîne YAML est valide.
        - `compare_yaml(yaml_string1, yaml_string2)` : Compare deux chaînes YAML pour vérifier leur équivalence.

        #### 2. JSON
        - `convert_dict_to_json(input_dict_json, indent=None, sort_keys=False)` : Convertit un dictionnaire en chaîne JSON.
        - `check_json_conformance(json_data)` : Vérifie si une chaîne JSON est valide.
        - `convert_json_to_dict(json_str)` : Convertit une chaîne JSON en dictionnaire.
        - `compare_json(json1, json2)` : Compare deux chaînes JSON pour vérifier leur équivalence.

        #### 3. XML
        - `xml_to_dict(xml_string)` : Convertit une chaîne XML en dictionnaire.
        - `compare_xml(xml_file1, xml_file2)` : Compare deux chaînes XML pour vérifier leur équivalence.
        - `convert_xml_to_dict(xml_string)` : Convertit une chaîne XML en dictionnaire (version alternative).
        - `convert_json_to_xml(json_data, root_name="root")` : Convertit une chaîne JSON en chaîne XML.
        - `convert_xml_to_json(input_xml)` : Convertit une chaîne XML en chaîne JSON.
        - `convert_dict_to_xml(data_dict)` : Convertit un dictionnaire en chaîne XML.
        - `header_body(xml_string)` : Sépare l'en-tête et le corps d'une chaîne XML.
        - `format_xml(xml_string)` : Formate une chaîne XML pour une meilleure lisibilité.

        #### 4. Conversions de types et structures
        - `convert_bytes_datetime_to_string(data)` : Convertit récursivement les objets `bytes` et `datetime` en chaînes.
        - `compare_dicts(dict1, dict2)` : Compare deux dictionnaires récursivement.
        - `convert_to_bytes(input_data)` : Convertit une chaîne ou des `bytes` en `bytes`.
        - `string_to_int(s)` : Convertit une chaîne en entier.
        - `int_to_string(n)` : Convertit un entier en chaîne.
        - `string_to_float(s)` : Convertit une chaîne en nombre flottant.
        - `float_to_string(f)` : Convertit un nombre flottant en chaîne.
        - `list_to_string(lst, separator=", ")` : Convertit une liste en chaîne avec un séparateur.
        - `string_to_list(s, separator=", ")` : Convertit une chaîne en liste avec un séparateur.
        - `list_to_set(lst)` : Convertit une liste en ensemble (élimine les doublons).
        - `set_to_list(s)` : Convertit un ensemble en liste.
        - `dict_to_list(d)` : Convertit un dictionnaire en liste de tuples `(clé, valeur)`.
        - `list_to_dict(lst)` : Convertit une liste de tuples `(clé, valeur)` en dictionnaire.
        - `char_to_ascii(c)` : Convertit un caractère en code ASCII.
        - `ascii_to_char(n)` : Convertit un code ASCII en caractère.
        - `convert_rows_to_columns(data)` : Convertit une liste de dictionnaires (lignes) en liste de dictionnaires (colonnes).
        - `convert_columns_to_rows(data)` : Convertit une liste de dictionnaires (colonnes) en liste de dictionnaires (lignes).
        - `convert_to_ordered_dict(dictionary)` : Convertit un dictionnaire en `OrderedDict`.

        #### 5. Compression et encodage
        - `compress_and_encode(string)` : Compresse une chaîne et l'encode en base64.
        - `decompress_and_encode(string)` : Décompresse une chaîne encodée en base64.
        - `compress_data_to_bytes(data_string_or_bytes)` : Compresse une chaîne ou des `bytes` avec gzip.
        - `decompress_data_to_bytes(data_bytes_compress)` : Décompresse des `bytes` avec gzip.
        - `serialized_dict_to_compressdictbytes(dict_data)` : Sérialise un dictionnaire en `bytes` compressés.
        - `unserialized_compressdictbytes_to_dict(serialized_dict_bytes_compress)` : Désérialise des `bytes` compressés en dictionnaire.

        #### 6. Base64
        - `encode_to_string_base64(input_data)` : Encode une chaîne ou des `bytes` en base64.
        - `decode_base64_to_string_(input_data)` : Décode une chaîne base64 en chaîne de caractères.
        - `check_base64_encoding(input_string)` : Vérifie si une chaîne est encodée en base64 valide.
        - `taille_string_in_base64(string)` : Calcule la taille d'une chaîne une fois encodée en base64.
        - `is_base64(s)` : Vérifie si une chaîne est un base64 valide (version avancée).

        #### 7. Datetime
        - `convert_datetime_to_string(input_date)` : Convertit un objet `datetime` en chaîne de caractères.

        #### 8. Utilitaires divers
        - `generate_random_text(num_words)` : Génère un texte aléatoire de `num_words` mots.
        - `capitalize_words(text)` : Met en majuscule la première lettre de chaque mot dans une chaîne.
        - `is_multiple_of(s, multiple=4)` : Vérifie si la longueur d'une chaîne est un multiple de `multiple`.
        - `check_keys_in(dictdata, array_keys)` : Vérifie si toutes les clés d'un tableau sont présentes dans un dictionnaire.

        ---
        ### Remarques :
        - Toutes les fonctions sont **statiques** : utilisez-les directement via `convert.nom_de_la_fonction()`.
        - Certaines fonctions nécessitent des **packages externes** (ex: `yaml`, `xmltodict`, `base64`, etc.).
        - Pour les conversions entre formats (YAML/JSON/XML), les fonctions gèrent les **types complexes** (dates, bytes, etc.).
    """

    # ======================
    # YAML
    # ======================

    @staticmethod
    def convert_dict_to_yaml(input_dict):
        """
        Convertit un dictionnaire Python en chaîne YAML.

        Args:
            input_dict (dict): Dictionnaire à convertir.

        Returns:
            str: Chaîne YAML représentant le dictionnaire.

        Raises:
            TypeError: Si l'entrée n'est pas un dictionnaire.

        Exemple:
            >>> data = {"name": "Alice", "age": 30}
            >>> yaml_str = convert.convert_dict_to_yaml(data)
            >>> print(yaml_str)
            name: Alice
            age: 30
        """
        if isinstance(input_dict, dict):
            return yaml.dump(convert.convert_bytes_datetime_to_string(input_dict))
        else:
            raise TypeError("L'entrée doit être de type dict.")

    @staticmethod
    def convert_yaml_to_dict(yaml_string):
        """
        Convertit une chaîne YAML en dictionnaire Python.
        Utilise `yaml_string_to_dict` pour la conversion.

        Args:
            yaml_string (str): Chaîne YAML à convertir.

        Returns:
            dict: Dictionnaire résultant.

        Exemple:
            >>> yaml_str = "name: Alice\nage: 30"
            >>> data = convert.convert_yaml_to_dict(yaml_str)
            >>> print(data)
            {'name': 'Alice', 'age': 30}
        """
        return convert.yaml_string_to_dict(yaml_string)

    @staticmethod
    def yaml_string_to_dict(yaml_string):
        """
        Convertit une chaîne YAML en dictionnaire Python.

        Args:
            yaml_string (str): Chaîne YAML à convertir.

        Returns:
            dict: Dictionnaire résultant.

        Raises:
            ValueError: Si la conversion échoue.

        Exemple:
            >>> yaml_str = "name: Alice\nage: 30"
            >>> data = convert.yaml_string_to_dict(yaml_str)
            >>> print(data)
            {'name': 'Alice', 'age': 30}
        """
        try:
            yaml_data = yaml.safe_load(
                convert.convert_bytes_datetime_to_string(yaml_string)
            )
            if isinstance(yaml_data, (dict, list)):
                return yaml_data
            else:
                raise yaml.YAMLError(
                    "Erreur lors de la conversion de la chaîne YAML en dictionnaire."
                )
        except yaml.YAMLError as e:
            raise ValueError(
                "Erreur lors de la conversion de la chaîne YAML en dictionnaire."
            )

    @staticmethod
    def check_yaml_conformance(yaml_data):
        """
        Vérifie si une chaîne YAML est valide.

        Args:
            yaml_data (str): Chaîne YAML à vérifier.

        Returns:
            bool: True si la chaîne est valide, False sinon.

        Exemple:
            >>> yaml_str = "name: Alice\nage: 30"
            >>> is_valid = convert.check_yaml_conformance(yaml_str)
            >>> print(is_valid)
            True
        """
        try:
            yaml.safe_load(convert.convert_bytes_datetime_to_string(yaml_data))
            return True
        except yaml.YAMLError:
            return False

    @staticmethod
    def compare_yaml(yaml_string1, yaml_string2):
        """
        Compare deux chaînes YAML pour vérifier si elles sont équivalentes.

        Args:
            yaml_string1 (str): Première chaîne YAML.
            yaml_string2 (str): Deuxième chaîne YAML.

        Returns:
            bool: True si les chaînes sont équivalentes, False sinon.

        Exemple:
            >>> yaml1 = "name: Alice\nage: 30"
            >>> yaml2 = "name: Alice\nage: 30"
            >>> is_equal = convert.compare_yaml(yaml1, yaml2)
            >>> print(is_equal)
            True
        """
        try:
            dict1 = convert.yaml_string_to_dict(yaml_string1)
            dict2 = convert.yaml_string_to_dict(yaml_string2)
            return convert.compare_dicts(dict1, dict2)
        except ValueError as e:
            print(f"Erreur: {str(e)}")
            return False

    # ======================
    # JSON
    # ======================

    @staticmethod
    def convert_dict_to_json(input_dict_json, indent=None, sort_keys=False):
        """
        Convertit un dictionnaire Python en chaîne JSON.

        Args:
            input_dict_json (dict): Dictionnaire à convertir.
            indent (int, optional): Indentation pour le JSON. Par défaut None.
            sort_keys (bool, optional): Trier les clés. Par défaut False.

        Returns:
            str: Chaîne JSON représentant le dictionnaire.

        Raises:
            TypeError: Si l'entrée n'est pas un dictionnaire.

        Exemple:
            >>> data = {"name": "Alice", "age": 30}
            >>> json_str = convert.convert_dict_to_json(data, indent=2)
            >>> print(json_str)
            {
              "name": "Alice",
              "age": 30
            }
        """
        if isinstance(input_dict_json, dict):
            return json.dumps(
                convert.convert_bytes_datetime_to_string(input_dict_json), indent=indent
            )
        else:
            raise TypeError("L'entrée doit être de type dict.")

    @staticmethod
    def check_json_conformance(json_data):
        """
        Vérifie si une chaîne JSON est valide.

        Args:
            json_data (str): Chaîne JSON à vérifier.

        Returns:
            bool: True si la chaîne est valide, False sinon.

        Exemple:
            >>> json_str = '{"name": "Alice", "age": 30}'
            >>> is_valid = convert.check_json_conformance(json_str)
            >>> print(is_valid)
            True
        """
        try:
            json.loads(json_data)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def convert_json_to_dict(json_str):
        """
        Convertit une chaîne JSON en dictionnaire Python.

        Args:
            json_str (str): Chaîne JSON à convertir.

        Returns:
            dict: Dictionnaire résultant.

        Raises:
            json.JSONDecodeError: Si la conversion échoue.

        Exemple:
            >>> json_str = '{"name": "Alice", "age": 30}'
            >>> data = convert.convert_json_to_dict(json_str)
            >>> print(data)
            {'name': 'Alice', 'age': 30}
        """
        if isinstance(json_str, (dict)):
            return json_str
        stringdata = convert.convert_bytes_datetime_to_string(json_str)
        if isinstance(stringdata, (str)):
            try:
                return json.loads(stringdata)
            except json.decoder.JSONDecodeError as e:
                raise
            except Exception as e:
                raise

    # ======================
    # XML
    # ======================

    @staticmethod
    def xml_to_dict(xml_string):
        """
        Convertit une chaîne XML en dictionnaire Python.

        Args:
            xml_string (str): Chaîne XML à convertir.

        Returns:
            dict: Dictionnaire résultant.

        Raises:
            ValueError: Si la conversion échoue.

        Exemple:
            >>> xml_str = "<root><name>Alice</name><age>30</age></root>"
            >>> data = convert.xml_to_dict(xml_str)
            >>> print(data)
            {'name': 'Alice', 'age': '30'}
        """
        def xml_element_to_dict(element):
            if len(element) == 0:
                return element.text
            result = {}
            for child in element:
                child_dict = xml_element_to_dict(child)
                if child.tag in result:
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = child_dict
            return result
        try:
            tree = ET.ElementTree(
                ET.fromstring(convert.convert_bytes_datetime_to_string(xml_string))
            )
            root = tree.getroot()
            return xml_element_to_dict(root)
        except ET.ParseError:
            raise ValueError("Erreur lors de la conversion XML en dictionnaire.")

    @staticmethod
    def compare_xml(xml_file1, xml_file2):
        """
        Compare deux chaînes XML pour vérifier si elles sont équivalentes.

        Args:
            xml_file1 (str): Première chaîne XML.
            xml_file2 (str): Deuxième chaîne XML.

        Returns:
            bool: True si les chaînes sont équivalentes, False sinon.

        Exemple:
            >>> xml1 = "<root><name>Alice</name><age>30</age></root>"
            >>> xml2 = "<root><name>Alice</name><age>30</age></root>"
            >>> is_equal = convert.compare_xml(xml1, xml2)
            >>> print(is_equal)
            True
        """
        try:
            dict1 = convert.xml_to_dict(xml_file1)
            dict2 = convert.xml_to_dict(xml_file2)
            return convert.compare_dicts(dict1, dict2)
        except ValueError as e:
            print(f"Erreur: {str(e)}")
            return False

    @staticmethod
    def convert_xml_to_dict(xml_string):
        """
        Convertit une chaîne XML en dictionnaire Python (version alternative).

        Args:
            xml_string (str): Chaîne XML à convertir.

        Returns:
            dict: Dictionnaire résultant.

        Exemple:
            >>> xml_str = "<root><name>Alice</name><age>30</age></root>"
            >>> data = convert.convert_xml_to_dict(xml_str)
            >>> print(data)
            {'root': {'name': ['Alice'], 'age': ['30']}}
        """
        def _element_to_dict(element):
            result = {}
            for child in element:
                if child.tag not in result:
                    result[child.tag] = []
                result[child.tag].append(_element_to_dict(child))
            if not result:
                return element.text
            return result
        root = ET.fromstring(convert.convert_bytes_datetime_to_string(xml_string))
        return _element_to_dict(root)

    @staticmethod
    def convert_json_to_xml(json_data, root_name="root"):
        """
        Convertit une chaîne JSON en chaîne XML.

        Args:
            json_data (str): Chaîne JSON à convertir.
            root_name (str, optional): Nom de la racine XML. Par défaut "root".

        Returns:
            str: Chaîne XML résultante.

        Exemple:
            >>> json_str = '{"name": "Alice", "age": 30}'
            >>> xml_str = convert.convert_json_to_xml(json_str)
            >>> print(xml_str)
            <root><name>Alice</name><age>30</age></root>
        """
        def _convert(element, parent):
            if isinstance(element, dict):
                for key, value in element.items():
                    if isinstance(value, (dict, list)):
                        sub_element = ET.SubElement(parent, key)
                        _convert(value, sub_element)
                    else:
                        child = ET.SubElement(parent, key)
                        child.text = str(value)
            elif isinstance(element, list):
                for item in element:
                    sub_element = ET.SubElement(parent, parent.tag[:-1])
                    _convert(item, sub_element)
        root = ET.Element(root_name)
        _convert(json.loads(json_data), root)
        xml_data = ET.tostring(root, encoding="unicode", method="xml")
        return xml_data

    @staticmethod
    def convert_xml_to_json(input_xml):
        """
        Convertit une chaîne XML en chaîne JSON.

        Args:
            input_xml (str): Chaîne XML à convertir.

        Returns:
            str: Chaîne JSON résultante.

        Exemple:
            >>> xml_str = "<root><name>Alice</name><age>30</age></root>"
            >>> json_str = convert.convert_xml_to_json(xml_str)
            >>> print(json_str)
            {
                "root": {
                    "name": "Alice",
                    "age": "30"
                }
            }
        """
        return json.dumps(xmltodict.parse(input_xml), indent=4)

    @staticmethod
    def convert_dict_to_xml(data_dict):
        """
        Convertit un dictionnaire Python en chaîne XML.

        Args:
            data_dict (dict): Dictionnaire à convertir.

        Returns:
            str: Chaîne XML résultante.

        Exemple:
            >>> data = {"name": "Alice", "age": 30}
            >>> xml_str = convert.convert_dict_to_xml(data)
            >>> print(xml_str)
            <?xml version="1.0" ?>
            <root>
                <name>Alice</name>
                <age>30</age>
            </root>
        """
        xml_str = xmltodict.unparse({"root": data_dict}, pretty=True)
        return xml_str

    # ======================
    # Utilitaires de conversion
    # ======================

    @staticmethod
    def convert_bytes_datetime_to_string(data):
        """
        Convertit récursivement les objets bytes et datetime en chaînes de caractères.
        Gère aussi les booléens et les valeurs None.

        Args:
            data: Donnée à convertir (dict, list, bytes, datetime, etc.).

        Returns:
            Donnée convertie en chaînes si nécessaire.

        Exemple:
            >>> data = {"name": b"Alice", "date": datetime(2023, 1, 1)}
            >>> clean_data = convert.convert_bytes_datetime_to_string(data)
            >>> print(clean_data)
            {'name': 'Alice', 'date': '2023-01-01 00:00:00'}
        """
        if isinstance(data, (str)):
            compa = data.lower()
            if compa == "true":
                return True
            elif compa == "false":
                return False
            elif compa == "none":
                return ""
            return data
        if isinstance(data, (int, float, bool)):
            return data
        elif isinstance(data, dict):
            return {
                convert.convert_bytes_datetime_to_string(key): convert.convert_bytes_datetime_to_string(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [convert.convert_bytes_datetime_to_string(item) for item in data]
        elif isinstance(data, bytes):
            return data.decode("utf-8")
        elif isinstance(data, datetime):
            return data.strftime("%Y-%m-%d %H:%M:%S")
        elif data is None:
            return ""
        else:
            try:
                str(data)
                return data
            except Exception as e:
                raise ValueError(f"Type {type(data)} impossible de convertir en string")

    @staticmethod
    def compare_dicts(dict1, dict2):
        """
        Compare deux dictionnaires récursivement.

        Args:
            dict1 (dict): Premier dictionnaire.
            dict2 (dict): Deuxième dictionnaire.

        Returns:
            bool: True si les dictionnaires sont égaux, False sinon.

        Exemple:
            >>> d1 = {"name": "Alice", "age": 30}
            >>> d2 = {"name": "Alice", "age": 30}
            >>> is_equal = convert.compare_dicts(d1, d2)
            >>> print(is_equal)
            True
        """
        if dict1.keys() != dict2.keys():
            return False
        for key in dict1.keys():
            value1 = dict1[key]
            value2 = dict2[key]
            if isinstance(value1, dict) and isinstance(value2, dict):
                if not convert.compare_dicts(value1, value2):
                    return False
            elif value1 != value2:
                return False
        return True

    @staticmethod
    def compare_json(json1, json2):
        """
        Compare deux chaînes JSON pour vérifier si elles sont équivalentes.

        Args:
            json1 (str): Première chaîne JSON.
            json2 (str): Deuxième chaîne JSON.

        Returns:
            bool: True si les chaînes sont équivalentes, False sinon.

        Raises:
            ValueError: Si la conversion JSON échoue.

        Exemple:
            >>> j1 = '{"name": "Alice", "age": 30}'
            >>> j2 = '{"name": "Alice", "age": 30}'
            >>> is_equal = convert.compare_json(j1, j2)
            >>> print(is_equal)
            True
        """
        try:
            dict1 = json.loads(json1)
            dict2 = json.loads(json2)
        except json.JSONDecodeError:
            raise ValueError("Erreur lors de la conversion JSON en dictionnaire.")
        return convert.compare_dicts(dict1, dict2)

    # ======================
    # Compression et encodage
    # ======================

    @staticmethod
    def compress_and_encode(string):
        """
        Compresse une chaîne en base64.

        Args:
            string (str): Chaîne à compresser.

        Returns:
            str: Chaîne compressée et encodée en base64.

        Exemple:
            >>> s = "Hello, world!"
            >>> encoded = convert.compress_and_encode(s)
            >>> print(encoded)
            eJwLKkksSizJL0pJT8lMyUxOLMnMS0zJT8lQSgGAAJmBwk=
        """
        data = convert.convert_to_bytes(string)
        compressed_data = zlib.compress(data, 9)
        encoded_data = base64.b64encode(compressed_data)
        return encoded_data.decode("utf-8")

    @staticmethod
    def decompress_and_encode(string):
        """
        Décompresse une chaîne encodée en base64.

        Args:
            string (str): Chaîne compressée et encodée en base64.

        Returns:
            str: Chaîne décompressée.

        Exemple:
            >>> encoded = "eJwLKkksSizJL0pJT8lMyUxOLMnMS0zJT8lQSgGAAJmBwk="
            >>> decoded = convert.decompress_and_encode(encoded)
            >>> print(decoded)
            Hello, world!
        """
        data = convert.convert_to_bytes(string)
        decoded_data = base64.b64decode(data)
        decompressed_data = zlib.decompress(decoded_data)
        return decompressed_data.decode("utf-8")

    # ======================
    # Datetime
    # ======================

    @staticmethod
    def convert_datetime_to_string(input_date: datetime):
        """
        Convertit un objet datetime en chaîne de caractères.

        Args:
            input_date (datetime): Objet datetime à convertir.

        Returns:
            str: Chaîne au format "YYYY-MM-DD HH:MM:SS".

        Raises:
            TypeError: Si l'entrée n'est pas un datetime.

        Exemple:
            >>> dt = datetime(2023, 1, 1, 12, 0, 0)
            >>> s = convert.convert_datetime_to_string(dt)
            >>> print(s)
            2023-01-01 12:00:00
        """
        if isinstance(input_date, datetime):
            return input_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            raise TypeError("L'entrée doit être de type datetime.")

    # ======================
    # Base64
    # ======================

    @staticmethod
    def encode_to_string_base64(input_data):
        """
        Encode une chaîne ou des bytes en base64.

        Args:
            input_data (str/bytes): Donnée à encoder.

        Returns:
            str: Chaîne encodée en base64.

        Raises:
            TypeError: Si l'entrée n'est ni une chaîne ni des bytes.

        Exemple:
            >>> s = "Hello, world!"
            >>> encoded = convert.encode_to_string_base64(s)
            >>> print(encoded)
            SGVsbG8sIHdvcmxkIQ==
        """
        if isinstance(input_data, str):
            input_data_bytes = input_data.encode("utf-8")
        elif isinstance(input_data, bytes):
            input_data_bytes = input_data
        else:
            raise TypeError("L'entrée doit être une chaîne ou un objet bytes.")
        encoded_bytes = base64.b64encode(input_data_bytes)
        return encoded_bytes.decode("utf-8")

    @staticmethod
    def decode_base64_to_string_(input_data):
        """
        Décode une chaîne base64 en chaîne de caractères.

        Args:
            input_data (str): Chaîne base64 à décoder.

        Returns:
            str: Chaîne décodée.

        Raises:
            ValueError: Si l'entrée n'est pas un base64 valide.

        Exemple:
            >>> encoded = "SGVsbG8sIHdvcmxkIQ=="
            >>> decoded = convert.decode_base64_to_string_(encoded)
            >>> print(decoded)
            Hello, world!
        """
        try:
            decoded_bytes = base64.b64decode(input_data)
            return decoded_bytes.decode("utf-8")
        except base64.binascii.Error:
            raise ValueError("L'entrée n'est pas encodée en base64 valide.")

    @staticmethod
    def check_base64_encoding(input_string):
        """
        Vérifie si une chaîne est encodée en base64 valide.

        Args:
            input_string (str): Chaîne à vérifier.

        Returns:
            bool: True si la chaîne est un base64 valide, False sinon.

        Exemple:
            >>> s = "SGVsbG8sIHdvcmxkIQ=="
            >>> is_valid = convert.check_base64_encoding(s)
            >>> print(is_valid)
            True
        """
        try:
            base64.b64decode(input_string)
            return True
        except base64.binascii.Error:
            return False

    @staticmethod
    def taille_string_in_base64(string):
        """
        Calcule la taille d'une chaîne une fois encodée en base64.

        Args:
            string (str): Chaîne dont on veut calculer la taille.

        Returns:
            float: Taille estimée en base64.

        Exemple:
            >>> s = "Hello, world!"
            >>> size = convert.taille_string_in_base64(s)
            >>> print(size)
            20.0
        """
        taille = len(string)
        return (taille + 2 - ((taille + 2) % 3)) * 4 / 3

    # ======================
    # Conversions de types
    # ======================

    @staticmethod
    def string_to_int(s):
        """
        Convertit une chaîne en entier.

        Args:
            s (str): Chaîne à convertir.

        Returns:
            int: Entier résultant, ou None si la conversion échoue.

        Exemple:
            >>> s = "42"
            >>> i = convert.string_to_int(s)
            >>> print(i)
            42
        """
        try:
            return int(s)
        except ValueError:
            return None

    @staticmethod
    def int_to_string(n):
        """
        Convertit un entier en chaîne.

        Args:
            n (int): Entier à convertir.

        Returns:
            str: Chaîne résultante.

        Exemple:
            >>> i = 42
            >>> s = convert.int_to_string(i)
            >>> print(s)
            '42'
        """
        return str(n)

    @staticmethod
    def string_to_float(s):
        """
        Convertit une chaîne en nombre à virgule flottante.

        Args:
            s (str): Chaîne à convertir.

        Returns:
            float: Nombre flottant résultant, ou None si la conversion échoue.

        Exemple:
            >>> s = "3.14"
            >>> f = convert.string_to_float(s)
            >>> print(f)
            3.14
        """
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def float_to_string(f):
        """
        Convertit un nombre à virgule flottante en chaîne.

        Args:
            f (float): Nombre flottant à convertir.

        Returns:
            str: Chaîne résultante.

        Exemple:
            >>> f = 3.14
            >>> s = convert.float_to_string(f)
            >>> print(s)
            '3.14'
        """
        return str(f)

    @staticmethod
    def list_to_string(lst, separator=", "):
        """
        Convertit une liste en chaîne avec un séparateur.

        Args:
            lst (list): Liste à convertir.
            separator (str, optional): Séparateur. Par défaut ", ".

        Returns:
            str: Chaîne résultante.

        Exemple:
            >>> lst = ["Alice", "Bob", "Charlie"]
            >>> s = convert.list_to_string(lst)
            >>> print(s)
            'Alice, Bob, Charlie'
        """
        return separator.join(lst)

    @staticmethod
    def string_to_list(s, separator=", "):
        """
        Convertit une chaîne en liste avec un séparateur.

        Args:
            s (str): Chaîne à convertir.
            separator (str, optional): Séparateur. Par défaut ", ".

        Returns:
            list: Liste résultante.

        Exemple:
            >>> s = "Alice, Bob, Charlie"
            >>> lst = convert.string_to_list(s)
            >>> print(lst)
            ['Alice', 'Bob', 'Charlie']
        """
        return s.split(separator)

    @staticmethod
    def list_to_set(lst):
        """
        Convertit une liste en ensemble (élimine les doublons).

        Args:
            lst (list): Liste à convertir.

        Returns:
            set: Ensemble résultant.

        Exemple:
            >>> lst = [1, 2, 2, 3]
            >>> s = convert.list_to_set(lst)
            >>> print(s)
            {1, 2, 3}
        """
        return set(lst)

    @staticmethod
    def set_to_list(s):
        """
        Convertit un ensemble en liste.

        Args:
            s (set): Ensemble à convertir.

        Returns:
            list: Liste résultante.

        Exemple:
            >>> s = {1, 2, 3}
            >>> lst = convert.set_to_list(s)
            >>> print(lst)
            [1, 2, 3]
        """
        return [item for item in s]

    @staticmethod
    def dict_to_list(d):
        """
        Convertit un dictionnaire en liste de tuples (clé, valeur).

        Args:
            d (dict): Dictionnaire à convertir.

        Returns:
            list: Liste de tuples résultante.

        Exemple:
            >>> d = {"name": "Alice", "age": 30}
            >>> lst = convert.dict_to_list(d)
            >>> print(lst)
            [('name', 'Alice'), ('age', 30)]
        """
        return list(d.items())

    @staticmethod
    def list_to_dict(lst):
        """
        Convertit une liste de tuples (clé, valeur) en dictionnaire.

        Args:
            lst (list): Liste de tuples à convertir.

        Returns:
            dict: Dictionnaire résultant.

        Exemple:
            >>> lst = [('name', 'Alice'), ('age', 30)]
            >>> d = convert.list_to_dict(lst)
            >>> print(d)
            {'name': 'Alice', 'age': 30}
        """
        return dict(lst)

    @staticmethod
    def char_to_ascii(c):
        """
        Convertit un caractère en code ASCII.

        Args:
            c (str): Caractère à convertir.

        Returns:
            int: Code ASCII résultant.

        Exemple:
            >>> c = 'A'
            >>> code = convert.char_to_ascii(c)
            >>> print(code)
            65
        """
        return ord(c)

    @staticmethod
    def ascii_to_char(n):
        """
        Convertit un code ASCII en caractère.

        Args:
            n (int): Code ASCII à convertir.

        Returns:
            str: Caractère résultant.

        Exemple:
            >>> n = 65
            >>> c = convert.ascii_to_char(n)
            >>> print(c)
            'A'
        """
        return chr(n)

    # ======================
    # Conversions de structures
    # ======================

    @staticmethod
    def convert_rows_to_columns(data):
        """
        Convertit une liste de dictionnaires (lignes) en une liste de dictionnaires (colonnes).

        Args:
            data (list): Liste de dictionnaires représentant des lignes.

        Returns:
            list: Liste de dictionnaires représentant des colonnes.

        Exemple:
            >>> data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
            >>> columns = convert.convert_rows_to_columns(data)
            >>> print(columns)
            [{'id': [1, 2]}, {'name': ['Alice', 'Bob']}]
        """
        column_names = set()
        for row in data:
            column_names.update(row.keys())
        columns = {name: [] for name in column_names}
        for row in data:
            for column, value in row.items():
                columns[column].append(value)
        return [{name: values} for name, values in columns.items()]

    @staticmethod
    def convert_columns_to_rows(data):
        """
        Convertit une liste de dictionnaires (colonnes) en une liste de dictionnaires (lignes).

        Args:
            data (list): Liste de dictionnaires représentant des colonnes.

        Returns:
            list: Liste de dictionnaires représentant des lignes.

        Exemple:
            >>> data = [{'id': [1, 2]}, {'name': ['Alice', 'Bob']}]
            >>> rows = convert.convert_columns_to_rows(data)
            >>> print(rows)
            [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        """
        rows = []
        s = [list(x.keys())[0] for x in data]
        nbligne = len(data[0][s[0]])
        for t in range(nbligne):
            result = {}
            for z in range(len(s)):
                result[s[z]] = data[z][s[z]][t]
            rows.append(result)
        return rows

    @staticmethod
    def convert_to_ordered_dict(dictionary):
        """
        Convertit un dictionnaire en OrderedDict.

        Args:
            dictionary (dict): Dictionnaire à convertir.

        Returns:
            OrderedDict: OrderedDict résultant.

        Exemple:
            >>> d = {"name": "Alice", "age": 30}
            >>> od = convert.convert_to_ordered_dict(d)
            >>> print(od)
            OrderedDict([('name', 'Alice'), ('age', 30)])
        """
        return OrderedDict(dictionary.items())

    # ======================
    # Génération aléatoire
    # ======================

    @staticmethod
    def generate_random_text(num_words):
        """
        Génère un texte aléatoire de `num_words` mots.

        Args:
            num_words (int): Nombre de mots à générer.

        Returns:
            str: Texte aléatoire généré.

        Exemple:
            >>> text = convert.generate_random_text(5)
            >>> print(text)
            "abcde fghij klmno pqrst uvwxy"
        """
        words = []
        for _ in range(num_words):
            word = "".join(
                random.choice(string.ascii_letters) for _ in range(random.randint(3, 8))
            )
            words.append(word)
        return " ".join(words)

    @staticmethod
    def capitalize_words(text):
        """
        Met en majuscule la première lettre de chaque mot dans une chaîne.

        Args:
            text (str): Chaîne à transformer.

        Returns:
            str: Chaîne transformée.

        Exemple:
            >>> text = "hello world"
            >>> capitalized = convert.capitalize_words(text)
            >>> print(capitalized)
            "Hello World"
        """
        words = text.split()
        return " ".join(word.capitalize() for word in words)

    # ======================
    # Compression Gzip
    # ======================

    @staticmethod
    def compress_data_to_bytes(data_string_or_bytes):
        """
        Compresse une chaîne ou des bytes avec gzip.

        Args:
            data_string_or_bytes (str/bytes): Donnée à compresser.

        Returns:
            bytes: Donnée compressée.

        Exemple:
            >>> s = "Hello, world!"
            >>> compressed = convert.compress_data_to_bytes(s)
            >>> print(compressed)
            b'\x1f\x8b\x08\x00...'
        """
        return gzip.compress(convert.convert_to_bytes(data_string_or_bytes))

    @staticmethod
    def decompress_data_to_bytes(data_bytes_compress):
        """
        Décompresse des bytes avec gzip.

        Args:
            data_bytes_compress (bytes): Donnée compressée.

        Returns:
            bytes: Donnée décompressée.

        Exemple:
            >>> compressed = b'\x1f\x8b\x08\x00...'
            >>> decompressed = convert.decompress_data_to_bytes(compressed)
            >>> print(decompressed)
            b'Hello, world!'
        """
        return convert.convert_to_bytes(gzip.decompress(data_bytes_compress))

    # ======================
    # Sérialisation avancée
    # ======================

    @staticmethod
    def serialized_dict_to_compressdictbytes(dict_data):
        """
        Sérialise un dictionnaire en bytes compressés.

        Args:
            dict_data (dict): Dictionnaire à sérialiser.

        Returns:
            bytes: Bytes compressés.

        Exemple:
            >>> d = {"name": "Alice", "age": 30}
            >>> compressed = convert.serialized_dict_to_compressdictbytes(d)
            >>> print(compressed)
            b'\x1f\x8b\x08\x00...'
        """
        json_bytes = json.dumps(dict_data, indent=4).encode("utf-8")
        return convert.compress_data_to_bytes(json_bytes)

    @staticmethod
    def unserialized_compressdictbytes_to_dict(serialized_dict_bytes_compress):
        """
        Désérialise des bytes compressés en dictionnaire.

        Args:
            serialized_dict_bytes_compress (bytes): Bytes compressés.

        Returns:
            dict: Dictionnaire résultant.

        Exemple:
            >>> compressed = b'\x1f\x8b\x08\x00...'
            >>> d = convert.unserialized_compressdictbytes_to_dict(compressed)
            >>> print(d)
            {'name': 'Alice', 'age': 30}
        """
        json_bytes = gzip.decompress(
            convert.convert_to_bytes(serialized_dict_bytes_compress)
        )
        return json.loads(json_bytes)

    # ======================
    # Utilitaires divers
    # ======================

    @staticmethod
    def is_multiple_of(s, multiple=4):
        """
        Vérifie si la longueur d'une chaîne est un multiple de `multiple`.

        Args:
            s (str): Chaîne à vérifier.
            multiple (int, optional): Multiple à vérifier. Par défaut 4.

        Returns:
            bool: True si la longueur est un multiple, False sinon.

        Exemple:
            >>> s = "abcd"
            >>> is_multiple = convert.is_multiple_of(s)
            >>> print(is_multiple)
            True
        """
        return len(s) % multiple == 0

    @staticmethod
    def is_base64(s):
        """
        Vérifie si une chaîne est encodée en base64 valide.

        Args:
            s (str): Chaîne à vérifier.

        Returns:
            bool: True si la chaîne est un base64 valide, False sinon.

        Exemple:
            >>> s = "SGVsbG8="
            >>> is_valid = convert.is_base64(s)
            >>> print(is_valid)
            True
        """
        if not convert.is_multiple_of(s, multiple=4):
            return False
        try:
            decoded = base64.b64decode(s)
            return base64.b64encode(decoded) == s.encode()
        except:
            return False

    @staticmethod
    def header_body(xml_string):
        """
        Sépare l'en-tête et le corps d'une chaîne XML.

        Args:
            xml_string (str): Chaîne XML à séparer.

        Returns:
            tuple: (header, body)

        Exemple:
            >>> xml_str = '<?xml version="1.0"?><root>...</root>'
            >>> header, body = convert.header_body(xml_str)
            >>> print(header)
            '<?xml version="1.0"?>'
        """
        body = header = ""
        index = xml_string.find("?>")
        if index != -1:
            header = xml_string[: index + 2]
            body = xml_string[index + 2 :]
        return header, body

    @staticmethod
    def format_xml(xml_string):
        """
        Formate une chaîne XML pour une meilleure lisibilité.

        Args:
            xml_string (str): Chaîne XML à formater.

        Returns:
            str: Chaîne XML formatée.

        Exemple:
            >>> xml_str = "<root><name>Alice</name></root>"
            >>> formatted = convert.format_xml(xml_str)
            >>> print(formatted)
            <?xml version="1.0" ?>
            <root>
                <name>Alice</name>
            </root>
        """
        dom = parseString(xml_string)
        return dom.toprettyxml(indent="  ")

    @staticmethod
    def check_keys_in(dictdata, array_keys):
        """
        Vérifie si toutes les clés d'un tableau sont présentes dans un dictionnaire.

        Args:
            dictdata (dict): Dictionnaire à vérifier.
            array_keys (list): Liste de clés à vérifier.

        Returns:
            bool: True si toutes les clés sont présentes, False sinon.

        Exemple:
            >>> d = {"name": "Alice", "age": 30}
            >>> keys = ["name", "age"]
            >>> has_keys = convert.check_keys_in(d, keys)
            >>> print(has_keys)
            True
        """
        return all(key in dictdata for key in array_keys)

    @staticmethod
    def auto_convert(data: str):
        """
        Détecte automatiquement le format (JSON, YAML, XML) d'une chaîne
        et la convertit en dict/list Python.

        :param data: chaîne en entrée
        :return: dict ou list
        :raises ValueError: si le format est inconnu
        """
        import yaml

        # Essai JSON
        try:
            return Convert.json_to_dict(data)
        except Exception:
            pass

        # Essai YAML
        try:
            return Convert.yaml_to_dict(data)
        except Exception:
            pass

        # Essai XML
        try:
            return Convert.xml_to_dict(data)
        except Exception:
            pass

        raise ValueError("Format non reconnu (ni JSON, ni YAML, ni XML)")

    @staticmethod
    def dict_diff(d1: dict, d2: dict) -> dict:
        """
        Compare deux dictionnaires et retourne les différences.

        :param d1: premier dict
        :param d2: second dict
        :return: dict avec "added", "removed", "changed"
        """
        diff = {"added": {}, "removed": {}, "changed": {}}

        # Clés ajoutées
        for key in d2.keys() - d1.keys():
            diff["added"][key] = d2[key]

        # Clés supprimées
        for key in d1.keys() - d2.keys():
            diff["removed"][key] = d1[key]

        # Clés modifiées
        for key in d1.keys() & d2.keys():
            if d1[key] != d2[key]:
                # Si sous-dict → comparaison récursive
                if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    sub_diff = Convert.dict_diff(d1[key], d2[key])
                    if any(sub_diff.values()):
                        diff["changed"][key] = sub_diff
                else:
                    diff["changed"][key] = {"old": d1[key], "new": d2[key]}

        return diff

class messagefilexmpp:
    """
    Cette class est charge de communique avec le substitut master.
    elle permet d'envoyer des messages et iq sur xmpp
    """

    # priority : 1 send message remote to
    # dataform jsonstring ({to,action,ret,base64,data,sessionid}

    # priority : 2 send message remote iq
    # dataform

    # priority 4 call plugin master
    # (dataform : json string { "action" : plugin, "ret": 0, "sessionid": sessionid, "data": data

    # priority 9 notification
    # (dataform : string )

    def name_random(self, nb, pref=""):
        a = "abcdefghijklnmopqrstuvwxyz0123456789"
        d = pref
        for t in range(nb):
            d = d + a[random.randint(0, 35)]
        return d

    def __init__(self, objmmc, config_mcc_agent, config_xmpp):
        # Lit configuration du fichier
        self.config_mcc_agent = config_mcc_agent
        self.config_xmpp = config_xmpp
        # self.config = config
        self.message_type = "json"
        self.config_bool_done = False
        self.objmmc = objmmc
        self.xmppbrowsingpath = xmppbrowsing(
            defaultdir=self.config_xmpp.defaultdir,
            rootfilesystem=self.config_xmpp.rootfilesystem,
        )

    def sendstr(self, msg, timeout=0, priority=9):
        """
        fonction de bas niveaux qui envoi 1 chaine au substitut master
        """
        # logger.error("sendstr %s" % msg)
        try:
            try:
                msg = convert.convert_bytes_datetime_to_string(msg)
            except ValueError as e:
                logger.error("messagefilexmpp send error: %s" % str(e))
                return None
            if self.config_mcc_agent.submaster_ip_format == "ipv6":
                client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Activation de l'option pour réutiliser l'adresse
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = self.config_mcc_agent.submaster_check_hostname
            context.verify_mode = ssl.CERT_NONE

            # test json
            client.connect(
                (
                    self.config_mcc_agent.submaster_host,
                    self.config_mcc_agent.submaster_port,
                )
            )
            ssock = context.wrap_socket(
                client, server_hostname=self.config_mcc_agent.submaster_host
            )
            response = None
            try:
                message = self.config_mcc_agent.submaster_allowed_token + msg
                ssock.sendall(convert.compress_data_to_bytes(message))
                response = convert.decompress_data_to_bytes(ssock.recv(2097152))
                response = convert.convert_bytes_datetime_to_string(response)
            finally:
                # Fermeture de la connexion SSL
                # Fermeture du socket principal
                ssock.close()
                if self.config_mcc_agent.submaster_allowed_token:
                    longueur = len(self.config_mcc_agent.submaster_allowed_token)
                    if longueur > 0 and len(response) > longueur:
                        return response[longueur:]
                return response
        except ConnectionRefusedError as e:
            self.config_bool_done = False
            logger.error(
                "Erreur connection verify substitut master %s:%s"
                % (
                    self.config_mcc_agent.submaster_host,
                    self.config_mcc_agent.submaster_port,
                )
            )
            logger.warning("Restart Substitut master")
        except Exception as e:
            logger.error("client mmc to submast : %s " % str(e))
            logger.error("%s" % (traceback.format_exc()))
            return None

    def send_message(self, mto, msg):
        logger.debug("---------------------------------------------------------")
        logger.debug("------------------- SEND MESSAGE-------------------------")
        logger.debug("---------------------------------------------------------")
        if not self.config_bool_done:
            if not self.objmmc.init_master_substitut():
                return None
        try:
            msg = convert.convert_json_to_dict(msg)
            logger.debug("send_message msg format json")
        except json.decoder.JSONDecodeError as e:
            # type n est pas 1 json.
            logger.debug("msg pas 1 json ")
            try:
                msg = convert.yaml_string_to_dict(msg)
                logger.debug("send_message msg format yam")
            except:
                logger.debug("msg pas 1 yam ")
                try:
                    msg = convert.xml_to_dict(msg)
                    logger.debug("send_message msg format xml")
                except:
                    logger.debug("msg pas 1 xml")
        if isinstance(msg, (dict)):
            # verification message format
            # verification keys minimuns
            if not convert.check_keys_in(msg, ["action", "data"]):
                # il manque des keys obligatoire dans le message
                return None
            if "sessionid" not in msg:
                msg["sessionid"] = self.name_random(10, pref="mmc_message")
            sessionid = msg["sessionid"]
            if "base64" not in msg:
                msg["base64"] = False
            if "ret" not in msg:
                msg["ret"] = 0
            if not isinstance(msg["data"], (list)):
                if not isinstance(msg["data"], (dict)):
                    if convert.is_base64(msg["data"]):
                        msg["base64"] = True
                    elif isinstance(msg["data"], (str)):
                        logger.warning(
                            "Message sessionid %s data est 1 simple string"
                            % msg["sessionid"]
                        )
                    else:
                        logger.error(
                            "Message data type error : type %s" % type(msg["data"])
                        )
                        return None

            # addition des metadatas de message.
            msg["metadatas"] = {"type": "msg", "to": mto, "timeout": 0}
            messagesend = json.dumps(msg, indent=4)
            self.sendstr(messagesend)
            return sessionid

        elif isinstance(msg, (str)):
            logger.error("Message does not have a valid format")
            return None
        else:
            logger.error("type msg pas compatible %s" % type(msg))
            return None

    def iqsendpulse(self, mto, msg, timeout):
        return self.send_iq(mto, msg, timeout)

    def send_iq(self, mto, msg, timeout):
        logger.debug("---------------------------------------------------------")
        logger.debug("----------------------- SEND IQ -------------------------")
        logger.debug("---------------------------------------------------------")
        if not self.config_bool_done:
            if not self.objmmc.init_master_substitut():
                return None
        try:
            msg = convert.convert_json_to_dict(msg)
            logger.debug("msg est 1 json")
        except json.decoder.JSONDecodeError as e:
            # type n est pas 1 json.
            logger.debug("msg pas 1 json ")
            try:
                msg = convert.yaml_string_to_dict(msg)
                logger.debug("msg est 1 yam")
            except:
                logger.debug("msg pas 1 yam ")
                try:
                    msg = convert.xml_to_dict(msg)
                    logger.debug("msg est 1 xml")
                except:
                    logger.debug("msg pas 1 xml")

        if isinstance(msg, (dict)):
            # verification message format
            # verification keys minimuns
            if not convert.check_keys_in(msg, ["action", "data"]):
                # il manque des keys obligatoire dans le message
                return None
            if "sessionid" not in msg:
                msg["sessionid"] = self.name_random(10, pref="mmc_message")
            sessionid = msg["sessionid"]
            if "base64" not in msg:
                msg["base64"] = False
            if "ret" not in msg:
                msg["ret"] = 0

            if not isinstance(msg["data"], (list)):
                if not isinstance(msg["data"], (dict)):
                    if convert.is_base64(msg["data"]):
                        msg["base64"] = True
                    elif isinstance(msg["data"], (str)):
                        logger.warning(
                            "Message sessionid %s data est 1 simple string"
                            % msg["sessionid"]
                        )
                    else:
                        logger.error(
                            "Message data type error : type %s" % type(msg["data"])
                        )
                        return None
            # addition des metadatas de message.
            msg["metadatas"] = {"type": "iq", "to": mto, "timeout": timeout}
            messagesend = json.dumps(msg, indent=4)
            return self.sendstr(messagesend, timeout)
            # return sessionid

        elif isinstance(msg, (str)):
            logger.error("Message does not have a valid format")
            return None
        else:
            logger.error("type msg pas compatible %s" % type(msg))
            return None

    def send_call_plugin(self, msg):
        logger.debug("---------------------------------------------------------")
        logger.debug("--------------------- CALL PLUGINS ----------------------")
        logger.debug("---------------------------------------------------------")
        if not isinstance(msg, (dict)):
            try:
                msg = convert.convert_json_to_dict(msg)
                logger.debug("msg est 1 json")
            except json.decoder.JSONDecodeError as e:
                # type n est pas 1 json.
                logger.debug("msg pas 1 json ")
                try:
                    msg = convert.yaml_string_to_dict(msg)
                    logger.debug("msg est 1 yam")
                except:
                    logger.debug("msg pas 1 yam ")
                    try:
                        msg = convert.xml_to_dict(msg)
                        logger.debug("msg est 1 xml")
                    except:
                        logger.debug("msg pas 1 xml")

        if isinstance(msg, (dict)):
            # verification message format
            # verification keys minimuns
            if not convert.check_keys_in(msg, ["action", "data"]):
                # il manque des keys obligatoire dans le message
                return None, None

            if "sessionid" not in msg:
                msg["sessionid"] = self.name_random(10, pref="mmc_message")
            sessionid = msg["sessionid"]
            if "base64" not in msg:
                msg["base64"] = False
            if "ret" not in msg:
                msg["ret"] = 0
            if not isinstance(msg["data"], (list)):
                if not isinstance(msg["data"], (dict)):
                    if convert.is_base64(msg["data"]):
                        msg["base64"] = True
                    elif isinstance(msg["data"], (str)):
                        logger.warning(
                            "Message sessionid %s data est 1 simple string"
                            % msg["sessionid"]
                        )
                    else:
                        logger.error(
                            "Message data type error : type %s" % type(msg["data"])
                        )
                        return None, None
            # addition des metadatas de message.
            msg["metadatas"] = {
                "type": "plugin",
                "to": "master@pulse/MASTER",
                "timeout": 0,
            }
            messagesend = json.dumps(msg, indent=4)
            res = self.sendstr(messagesend)
            if res != None:
                logger.debug("Plugin call executed %s on master " % msg["action"])
                return sessionid, res
            return None, "Error connection"

        elif isinstance(msg, (str)):
            logger.error("Message does not have a valid format")
            return None, None
        else:
            logger.error("type msg pas compatible %s" % type(msg))
            return None, None

    def callpluginmasterfrommmc(self, plugin, data, sessionid=None):
        if sessionid is None:
            sessionid = self.name_random(5, plugin)
        msg = {"action": plugin, "ret": 0, "sessionid": sessionid, "data": data}
        self.send_call_plugin(msg)

    def _call_remote_action(self, to, nameaction, sessionname):
        msg = {
            "action": nameaction,
            "sessionid": self.name_random(5, sessionname),
            "data": [],
            "ret": 255,
            "base64": False,
        }
        self.send_message(to, msg)

    def send_message_json(self, to, jsonstring):
        return self.send_message(to, jsonstring)
        # jsonstring["to"] = to
        # return self.sendstr(json.dumps(jsonstring), priority=1)

    def callrestartbymaster(self, to):
        return self._call_remote_action(to, "restarfrommaster", "restart")

    def callInstallKey(self, jidAM, jidARS):
        """
        Envoie une requête pour installer une clé SSH d'un ars sur 1 machine
        cette fonction est 1 client qui envoi le message XMPP en utilisant le serveur substitut master.
        substitut master fait la requette xmpp

        Cette méthode crée un message de requête pour l'installation d'une clé SSH,
        ARS qui recoit se message install sa clef sur la machine jidAM.

        Args:
            jidAM (str): L'adresse JID de l'agent de messagerie (jidAM) pour lequel
                        la clé SSH doit être installée.
            jidARS (str): L'adresse JID du destinataire (jidARS) du message XMPP
                        demandant l'installation de la clé SSH.

        Raises:
            Exception: Si l'envoi du message échoue pour une raison quelconque.

        """
        msg = {
            "action": "installkey",
            "sessionid": self.name_random(5, "installkey"),
            "data": {"jidAM": jidAM},
            "ret": 0,
            "base64": False,
        }
        self.send_message(jidARS, msg)

    def callinventory(self, to):
        return self._call_remote_action(to, "inventory", "inventory")

    def callrestartbotbymaster(self, to):
        return self._call_remote_action(to, "restartbot", "restartbot")

    def callshutdownbymaster(self, to, time=0, msg=""):
        shutdownmachine = {
            "action": "shutdownfrommaster",
            "sessionid": self.name_random(5, "shutdown"),
            "data": {"time": time, "msg": msg},
            "ret": 0,
            "base64": False,
        }
        return self.send_message(to, shutdownmachine)
        # self.sendstr(json.dumps(shutdownmachine), priority=1)
        # return True

    def callvncchangepermsbymaster(self, to, askpermission=1):
        vncchangepermsonmachine = {
            "action": "vncchangepermsfrommaster",
            "sessionid": self.name_random(5, "vncchangeperms"),
            "data": {"askpermission": askpermission},
            "ret": 0,
            "base64": False,
        }
        return self.send_message(to, vncchangepermsonmachine)
        # self.sendstr(json.dumps(vncchangepermsonmachine), priority=1)
        # return True


class TimedCompressedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Extended version of TimedRotatingFileHandler that compresses logs on rollover.

    This handler rotates logs based on a time interval and compresses the rotated
    log files into ZIP format. It manages the number of backup files to keep.

    Attributes:
        backupCountlocal (int): The number of backup files to keep.
    """

    def __init__(
        self,
        filename,
        when="h",
        interval=1,
        backupCount=0,
        encoding=None,
        delay=False,
        utc=False,
        compress="zip",
    ):
        """
        Initializes the TimedCompressedRotatingFileHandler with the specified parameters.

        Args:
            filename (str): The base filename for the log files.
            when (str): The time interval for rotation (default: "h" for hours).
            interval (int): The number of units for the rotation interval (default: 1).
            backupCount (int): The maximum number of backup files to keep (default: 0).
            encoding (str): The encoding used for the log files (default: None).
            delay (bool): If True, the log file will not be opened until the first write (default: False).
            utc (bool): If True, uses UTC time for rotations (default: False).
            compress (str): The compression format (default: "zip").
        """
        # Call the superclass initializer for basic log file handling
        super(TimedCompressedRotatingFileHandler, self).__init__(
            filename, when, interval, backupCount, encoding, delay, utc
        )
        self.backupCountlocal = backupCount  # Store the backup count locally

    def get_files_by_date(self):
        """
        Retrieves log files and their creation timestamps, sorting them into
        compressed and uncompressed lists. Deletes old compressed files
        beyond the backup count limit.

        Returns:
            str: The filename of the log file to keep after rotation.
        """
        dir_name, base_name = os.path.split(self.baseFilename)  # Split the path to get directory and base name
        file_names = os.listdir(dir_name)  # List all files in the directory
        result = []  # To hold uncompressed files
        result1 = []  # To hold compressed files
        prefix = "{}".format(base_name)  # Create a prefix based on the base name

        # Loop through files to categorize them as compressed or uncompressed
        for file_name in file_names:
            if file_name.startswith(prefix) and not file_name.endswith(".zip"):
                f = os.path.join(dir_name, file_name)
                result.append((os.stat(f).st_ctime, f))  # Store creation time and file path
            if file_name.startswith(prefix) and file_name.endswith(".zip"):
                f = os.path.join(dir_name, file_name)
                result1.append((os.stat(f).st_ctime, f))  # Store creation time and compressed file path

        result1.sort()  # Sort compressed files by creation time
        result.sort()  # Sort uncompressed files by creation time

        # Remove old compressed files beyond the defined backup count
        while result1 and len(result1) >= self.backupCountlocal:
            el = result1.pop(0)  # Get the oldest compressed file
            if os.path.exists(el[1]):
                os.remove(el[1])  # Remove it from the filesystem

        # Return the most recent uncompressed log file to keep
        return result[1][1]

    def doRollover(self):
        """
        Handles the log file rollover by calling the superclass's rollover method
        and compressing the old log file into a ZIP format.
        """
        super(TimedCompressedRotatingFileHandler, self).doRollover()  # Perform regular rollover
        try:
            dfn = self.get_files_by_date()  # Get the most recent log file to work with
        except:
            return  # If an error occurs, simply return

        # Prepare the name for the compressed ZIP file
        dfn_zipped = "{}.zip".format(dfn)
        if os.path.exists(dfn_zipped):
            os.remove(dfn_zipped)  # Remove the ZIP file if it exists

        # Create a new ZIP file and add the uncompressed log file to it
        with zipfile.ZipFile(dfn_zipped, "w") as f:
            f.write(dfn, os.path.basename(dfn), zipfile.ZIP_DEFLATED)

        os.remove(dfn)  # Remove the uncompressed log file after compression


logger = logging.getLogger()

sys.path.append("plugins")

Fault = xmlrpc.client.Fault
ctx = None
VERSION = "5.3.0"


class IncludeStartsWithFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter include ONLY the logs which starts by the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is found (= print the record)
            or
            False if the criterion is not found (= don't print the record)
        """
        return record.getMessage().startswith(self.criterion)


# include log containing the criterions
class IncludeContainsFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter include ONLY the logs which contains the specified criterions"""

    def __init__(self, criterion=[]):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: list of the searched criterions"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is found (= print the record)
            or
            False if the criterion is not found (= don't print the record)
        """
        # if criterion == [] the filter let pass all messages
        flag = False
        for criterion in self.criterion:
            if re.search(criterion, record.getMessage(), re.I):
                flag = True
        return flag


# include log ending by the criterion
class IncludeEndsWithFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter include ONLY the logs which ends by the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is found (= print the record)
            or
            False if the criterion is not found (= don't print the record)
        """
        return record.getMessage().endswith(self.criterion)


# exclude all log starting by criterion
class ExcludeStartsWithFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter excludes ALL the logs which starts by the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is not found (= print the record)
            or
            False if the criterion is found (= don't print the record)
        """
        # if criterion == "" the filter exclude all messages
        return not record.getMessage().startswith(self.criterion)


# include log containing the criterion
class ExcludeContainsFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter excludes ALL the logs which contains the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is not found (= print the record)
            or
            False if the criterion is found (= don't print the record)
        """
        if re.search(self.criterion, record.getMessage(), re.I):
            return False
        else:
            return True


# include log ending by the criterion
class ExcludeEndsWithFilter(logging.Filter):
    """This class create a specialized filter for logging.getLogger.
    This filter excludes ALL the logs which ends by the specified criterion"""

    def __init__(self, criterion=""):
        """At the creation of the filter, the search criterion is given.
        Param:
            criterion: str of the searched criterion"""
        super(logging.Filter, self).__init__()
        self.criterion = criterion

    def filter(self, record):
        """The filter method say "print" or "not print" the recorded message to the logger
        Param:
            record: corresponding to the log entry.
        Returns:
            True if the criterion is not found (= print the record)
            or
            False if the criterion is found (= don't print the record)
        """
        return not record.getMessage().endswith(self.criterion)

class MmcServer(XMLRPC, object):
    """
    Serveur MMC implémenté comme un serveur XML-RPC avec Twisted.
    Ce serveur permet de :
    - Charger des plugins depuis le répertoire "plugins/"
    - Gérer l'authentification des utilisateurs via HTTP Basic Auth
    - Gérer les sessions utilisateur (avec expiration)
    - Supporter l'exécution multithread des requêtes
    - Fournir des méthodes d'introspection XML-RPC standard
    - Permettre le rechargement des configurations des plugins
    Fichier de configuration : @sysconfdir@/agent/config.ini
    """

    # Ensemble pour suivre toutes les sessions actives
    sessions = set()

    def __init__(self, modules, config):
        """
        Initialise le serveur MMC.

        Args:
            modules (dict): Modules de plugins chargés.
            config (object): Objet de configuration du serveur.
        """
        XMLRPC.__init__(self)
        self.modules = modules
        self.config = config

    def _splitFunctionPath(self, functionPath):
        """
        Sépare un chemin de fonction en module et nom de fonction.

        Args:
            functionPath (str): Chemin de la fonction, par exemple "module.fonction".

        Returns:
            tuple: (module, function_name) ou (None, function_name) si pas de module.
        """
        if "." in functionPath:
            mod, func = functionPath.split(".", 1)
        else:
            mod = None
            func = functionPath
        return mod, func

    def _getFunction(self, functionPath, request=""):
        """
        Résout un chemin de fonction en un objet appelable.

        Args:
            functionPath (str): Chemin de la fonction, par exemple "module.fonction".
            request (Request): Objet de requête actuel.

        Returns:
            callable: Fonction à exécuter.

        Raises:
            Fault: Si la fonction n'existe pas.
        """
        mod, func = self._splitFunctionPath(functionPath)
        try:
            if mod and mod != "system":
                try:
                    # Récupère directement la fonction depuis le module
                    ret = getattr(self.modules[mod], func)
                except AttributeError:
                    # Si la fonction n'est pas trouvée, essaie le wrapper RpcProxy
                    rpcProxy = getattr(self.modules[mod], "RpcProxy")
                    ret = rpcProxy(request, mod).getFunction(func)
            else:
                # Fonctions appartenant au serveur lui-même
                ret = getattr(self, func)
        except AttributeError:
            logger.error(f"{functionPath} non trouvé")
            raise Fault("NO_SUCH_FUNCTION", f"No such function {functionPath}")
        return ret

    def _needAuth(self, functionPath):
        """
        Vérifie si une fonction nécessite une authentification.

        Args:
            functionPath (str): Chemin de la fonction.

        Returns:
            bool: True si une authentification est nécessaire.
        """
        mod, func = self._splitFunctionPath(functionPath)
        # Cas spécial : la fonction de rechargement ne nécessite pas d'authentification
        if (mod, func) == ("system", "reloadModulesConfiguration"):
            return False
        ret = True
        if mod:
            try:
                # Liste NOAUTHNEEDED est définie par le plugin
                nanl = self.modules[mod].NOAUTHNEEDED
                ret = func not in nanl
            except (KeyError, AttributeError):
                pass
        return ret

    def render_OPTIONS(self, request):
        """
        Gère les requêtes CORS preflight OPTIONS.
        """
        request.setHeader(
            "Access-Control-Allow-Origin",
            request.requestHeaders.getRawHeaders("Origin"),
        )
        request.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS")
        request.setHeader("Access-Control-Allow-Credentials", "true")
        request.setHeader("Access-Control-Allow-Headers", "content-type, authorization")
        request.setHeader("Access-Control-Max-Age", "1728000")
        request.setHeader("Content-Type", "text/plain")
        return ""

    def render_POST(self, request):
        """
        Surcharge de la méthode POST du framework XML-RPC Twisted.
        Gère l'authentification, les sessions, et l'exécution des fonctions RPC.

        Args:
            request: Requête XML-RPC brute.

        Returns:
            server.NOT_DONE_YET: Indique que la réponse sera envoyée plus tard.
        """
        # Gestion des headers CORS
        if request.requestHeaders.hasHeader("Origin"):
            request.setHeader(
                "Access-Control-Allow-Origin",
                request.requestHeaders.getRawHeaders("Origin"),
            )
        request.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS")
        request.setHeader("Access-Control-Allow-Credentials", "true")
        request.setHeader("Access-Control-Allow-Headers", "content-type,authorization")
        request.setHeader("Access-Control-Expose-Headers", "content-type,cookie")
        request.setHeader("Access-Control-Max-Age", "1728000")

        # Lecture de la requête XML
        requestxml = request.content.read()
        args, functionPath = xmlrpc.client.loads(requestxml)
        s = request.getSession()

        # Initialisation des attributs de session si absents
        if not hasattr(s, "loggedin"):
            s.loggedin = False
        if not hasattr(s, "lastModified"):
            s.lastModified = reactor.seconds()
        if not hasattr(s, "sessionTimeout"):
            s.sessionTimeout = self.config.sessiontimeout

        # Vérification de l'expiration de la session
        try:
            current_time = reactor.seconds()
            if (
                self.config.sessiontimeout
                and (current_time - s.lastModified) > self.config.sessiontimeout
            ):
                logger.debug("Session expirée !")
                s.loggedin = False
                request.setResponseCode(http.UNAUTHORIZED)
                request.setHeader(b"content-type", b"text/html")
                request.setHeader(b"content-length", b"0")
                request.finish()
                return server.NOT_DONE_YET
            s.lastModified = current_time
        except AttributeError as e:
            logger.error(f"Erreur d'attribut : {e}")
            s.loggedin = False
            s.sessionTimeout = self.config.sessiontimeout
            return server.NOT_DONE_YET

        # Authentification HTTP Basic
        cleartext_token = f"{self.config.login}:{self.config.password}"
        user = str(request.getUser(), "utf-8")
        password = str(request.getPassword(), "utf-8")
        token = f"{user}:{password}"
        if token != cleartext_token:
            logger.error("Identifiants invalides pour l'authentification HTTP Basic")
            request.setResponseCode(http.UNAUTHORIZED)
            self._cbRender(
                Fault(
                    http.UNAUTHORIZED,
                    "Non autorisé : identifiants invalides pour se connecter à l'agent MMC, authentification HTTP Basic requise",
                ),
                request,
            )
            return server.NOT_DONE_YET

        # Log des appels RPC
        if not s.loggedin:
            logger.debug(f"Appel RPC depuis un utilisateur non authentifié : {functionPath}{str(args)}")
            s.http_headers = request.requestHeaders.copy()
        else:
            logger.debug(f"Appel RPC depuis l'utilisateur {s.userid} : {functionPath}{str(args)}")

        # Vérification de l'authentification et exécution de la fonction
        try:
            if not s.loggedin and self._needAuth(functionPath):
                msg = f"Authentification nécessaire : {functionPath}"
                logger.error(msg)
                raise Fault(8003, msg)
            else:
                if not s.loggedin and not self._needAuth(functionPath):
                    s.userid = "root"
                    try:
                        self._associateContext(request, s, s.userid)
                    except Exception as e:
                        s.loggedin = False
                        logger.exception(e)
                        f = Fault(8004, "L'agent MMC ne peut pas fournir de contexte de sécurité")
                        self._cbRender(f, request)
                        return server.NOT_DONE_YET
                function = self._getFunction(functionPath, request)
        except Fault as f:
            self._cbRender(f, request)
        else:
            if self.config.multithreading:
                oldargs = args
                args = (function, s,) + args
                defer.maybeDeferred(self._runInThread, *args).addErrback(
                    self._ebRender, functionPath, oldargs, request
                ).addCallback(self._cbRender, request, functionPath, oldargs)
            else:
                defer.maybeDeferred(function, *args).addErrback(
                    self._ebRender, functionPath, args, request
                ).addCallback(self._cbRender, request, functionPath, args)
        return server.NOT_DONE_YET

    def _runInThread(self, *args, **kwargs):
        """
        Exécute une fonction dans un thread séparé, en gérant les Deferred.
        Permet de ne pas bloquer le réacteur Twisted.
        """
        def _printExecutionTime(start):
            logger.debug(f"Temps d'exécution : {time.time() - start}")

        def _cbSuccess(result, deferred, start):
            _printExecutionTime(start)
            reactor.callFromThread(deferred.callback, result)

        def _cbFailure(failure, deferred, start):
            _printExecutionTime(start)
            reactor.callFromThread(deferred.errback, failure)

        def _putResult(deferred, f, session, args, kwargs):
            logger.debug(
                f"Utilisation du thread #{threading.currentThread().getName().split('-')[2]} pour {f.__name__}"
            )
            threading.currentThread().session = session
            start = time.time()
            try:
                result = f(*args, **kwargs)
            except:
                f = failure.Failure()
                reactor.callFromThread(deferred.errback, f)
            else:
                if isinstance(result, defer.Deferred):
                    result.addCallback(_cbSuccess, deferred, start)
                    result.addErrback(_cbFailure, deferred, start)
                else:
                    _printExecutionTime(start)
                    reactor.callFromThread(deferred.callback, result)

        function = args[0]
        context = args[1]
        args = args[2:]
        d = defer.Deferred()
        reactor.callInThread(_putResult, d, function, context, args, kwargs)
        return d


    def _cbRender(self, result, request, functionPath=None, args=None):
        """
        Callback pour rendre le résultat d'une requête XML-RPC.

        - Appelée automatiquement par Twisted après l'exécution d'une méthode
        XML-RPC exposée.
        - Sérialise le résultat Python en XML-RPC et écrit la réponse HTTP.

        🔹 Transformations appliquées avant sérialisation :
        -----------------------------------------------
        1. `result = sanitize_for_xmlrpc(result)` :
        - Remplace `None` par '' pour compatibilité maximale.
        - Convertit `decimal.Decimal` en `float`.
        - Transforme récursivement les dicts et listes.
        - Possibilité d'ajouter d'autres types exotiques (datetime, UUID, etc.).
        2. `xmlrpc.client.dumps((result,), methodresponse=True, allow_none=True)` :
        - Enveloppe le résultat dans un tuple comme l'exige xmlrpc.client.
        - `allow_none=True` permet de générer `<nil/>` pour les valeurs `None`.

        ⚠️ Points importants :
        ----------------------
        - XML-RPC standard ne supporte pas `None`. Sans `allow_none=True`, une
        exception "cannot marshal objects" est levée.
        - Les clients XML-RPC doivent accepter `<nil/>` pour que cela fonctionne
        correctement. Exemple en PHP : `$GLOBALS['xmlrpc_null_extension'] = true;`
        avec phpxmlrpc.
        - Tout type Python non supporté par XML-RPC (Decimal, datetime, UUID, etc.)
        doit être transformé avant le dump pour éviter une exception.

        Avantages :
        ----------
        - Permet d'envoyer des résultats contenant des `None` et d'autres types
        Python non-XML-RPC sans planter le serveur.

        Inconvénients :
        --------------
        - `<nil/>` n'est pas standard XML-RPC : certains clients stricts peuvent
        ne pas savoir le décoder. Dans ce cas, il faudra prévoir un fallback
        (ex : remplacer `None` par '').

        Parameters
        ----------
        result : any
            Résultat de la méthode XML-RPC (dict, list, etc.)
        request : twisted.web.http.Request
            Objet HTTP Twisted pour la réponse
        functionPath : str, optional
            Nom de la méthode appelée
        args : tuple, optional
            Arguments passés à la méthode
        """
        s = request.getSession()
        auth_funcs = ["base.ldapAuth", "base.tokenAuthenticate", "base.authenticate"]

        if functionPath in auth_funcs and not isinstance(result, Fault):
            if result:
                s.loggedin = True
                s.userid = args[0]
                try:
                    self._associateContext(request, s, s.userid)
                except Exception as e:
                    s.loggedin = False
                    logger.exception(e)
                    f = Fault(8004, "L'agent MMC ne peut pas fournir de contexte de sécurité pour ce compte")
                    self._cbRender(f, request)
                    return

        try:
            # 🔹 Fix: autoriser la sérialisation de None via <nil/>
            # Toujours envelopper le résultat dans un tuple
            result = sanitize_for_xmlrpc(result)
            # Log du résultat
            if s.loggedin:
                logger.debug(f"Résultat pour {s.userid}, {functionPath}: {result}")
            else:
                logger.debug(f"Résultat pour utilisateur non authentifié, {functionPath}: {result}")

            xml = xmlrpc.client.dumps((result,), methodresponse=True, allow_none=True)
        except Exception as e:
            logger.exception("Erreur de sérialisation XML-RPC: %s", e)
            fault = Fault(8005, f"Impossible de sérialiser la sortie : {e}")
            xml = xmlrpc.client.dumps((fault,), methodresponse=True, allow_none=True)
        request.setHeader(b"content-type", b"text/xml")
        request.write(xml.encode("utf-8"))
        request.finish()
    #
    # a supprimer apres test
    # def _cbRender(self, result, request, functionPath=None, args=None):
    #     """
    #     Callback pour rendre le résultat d'une requête RPC.
    #     Gère la sérialisation XML, les logs et les headers HTTP.
    #     """
    #     s = request.getSession()
    #     auth_funcs = ["base.ldapAuth", "base.tokenAuthenticate", "base.authenticate"]
    #     if functionPath in auth_funcs and not isinstance(result, Fault):
    #         if result:
    #             s = request.getSession()
    #             s.loggedin = True
    #             s.userid = args[0]
    #             try:
    #                 self._associateContext(request, s, s.userid)
    #             except Exception as e:
    #                 s.loggedin = False
    #                 logger.exception(e)
    #                 f = Fault(8004, "L'agent MMC ne peut pas fournir de contexte de sécurité pour ce compte")
    #                 self._cbRender(f, request)
    #                 return
    #
    #     if result is None:
    #         result = 0
    #     if isinstance(result, Handler):
    #         result = result.result
    #     if not isinstance(result, xmlrpc.client.Fault):
    #         result = (result,)
    #
    #     # Hack pour gérer les données binaires (ex: jpegPhoto)
    #     try:
    #         if isinstance(result[0], dict) and "jpegPhoto" in result[0]:
    #             result[0]["jpegPhoto"] = [xmlrpc.client.Binary(result[0]["jpegPhoto"][0])]
    #     except (IndexError, Exception):
    #         pass
    #
    #     # Log du résultat
    #     try:
    #         if s.loggedin:
    #             logger.debug(f"Résultat pour {s.userid}, {functionPath}: {result}")
    #         else:
    #             logger.debug(f"Résultat pour utilisateur non authentifié, {functionPath}: {result}")
    #         s = xmlrpc.client.dumps(result, methodresponse=1)
    #     except Exception as e:
    #         f = Fault(self.FAILURE, f"Impossible de sérialiser la sortie : {e}")
    #         s = xmlrpc.client.dumps(f, methodresponse=1)
    #
    #     s = bytes(s, encoding="utf-8")
    #     request.setHeader("content-length", str(len(s)))
    #     request.setHeader("content-type", "application/xml")
    #     request.write(s)
    #     request.finish()

    def _ebRender(self, failure, functionPath, args, request):
        """
        Callback en cas d'erreur lors du rendu d'une requête RPC.
        """
        logger.error(f"Erreur lors du rendu {functionPath} : {failure.getTraceback()}")
        result = {
            "faultString": f"{functionPath} {str(args)}",
            "faultCode": f"{failure.type}: {failure.value}",
            "faultTraceback": failure.getTraceback(),
        }
        return result

    def _associateContext(self, request, session, userid):
        """
        Demande à chaque plugin Python activé un contexte à attacher à la session utilisateur.

        Args:
            request: Requête XML-RPC actuelle.
            session: Objet de session actuel.
            userid: Identifiant de l'utilisateur.
        """
        session.contexts = {}
        for mod in self.modules:
            try:
                contextMaker = getattr(self.modules[mod], "ContextMaker")
            except AttributeError:
                continue
            cm = contextMaker(request, session, userid)
            context = cm.getContext()
            if context:
                logger.debug(f"Attachement du contexte du module '{mod}' à la session utilisateur")
                session.contexts[mod] = context
        if session not in self.sessions:
            self.sessions.add(session)

    # ===== Méthode de rechargement =====
    def reloadModulesConfiguration(self):
        """
        Recharge la configuration de tous les plugins.
        Expire toutes les sessions actives.
        """
        import gc
        from mmc.support.config import PluginConfig
        for obj in gc.get_objects():
            if isinstance(obj, PluginConfig):
                try:
                    with open(obj.conffile, "r") as fid:
                        obj.readfp(fid, obj.conffile)
                    if os.path.isfile(obj.conffile + ".local"):
                        with open(obj.conffile + ".local", "r") as fid:
                            obj.readfp(fid, obj.conffile + ".local")
                    obj.readConf()
                except Exception as e:
                    logger.error(f"Erreur lors du rechargement du fichier {obj.conffile}")
                    logger.error(str(e))
                    return "Failed"
        for session in self.sessions:
            session.expire()
        self.sessions = set()
        return "Done"

    # ===== Méthodes d'introspection XML-RPC standard =====
    def listMethods(self):
        """
        Liste toutes les méthodes RPC disponibles.
        """
        method_list = []
        for mod in self.modules:
            instance = self.modules[mod]
            for m in dir(instance):
                r = getattr(instance, m)
                if hasattr(r, "__call__"):
                    method_list.append(f"{mod}.{m}")
            if hasattr(instance, "RpcProxy"):
                for m in dir(instance.RpcProxy):
                    r = getattr(instance.RpcProxy, m)
                    if hasattr(r, "__call__"):
                        method_list.append(f"{mod}.{m}")
        return method_list

    def __getClassMethod(self, name):
        """
        Récupère une méthode de classe à partir de son nom.

        Args:
            name (str): Nom de la méthode.

        Returns:
            callable: Méthode ou None si non trouvée.
        """
        mod, func = self._splitFunctionPath(name)
        if mod not in self.modules:
            return None
        instance = self.modules[mod]
        if hasattr(instance, "RpcProxy"):
            if hasattr(instance.RpcProxy, func):
                return getattr(instance.RpcProxy, func)
            elif hasattr(instance, func):
                return getattr(instance, func)
        return None

    def methodSignature(self, name):
        """
        Retourne la signature d'une méthode RPC.

        Args:
            name (str): Nom de la méthode.

        Returns:
            list: Liste des arguments de la méthode.
        """
        method = self.__getClassMethod(name)
        if method is None:
            return []
        return getfullargspec(method)[0]

    def methodHelp(self, name):
        """
        Retourne la documentation d'une méthode RPC.

        Args:
            name (str): Nom de la méthode.

        Returns:
            str: Documentation de la méthode.
        """
        method = self.__getClassMethod(name)
        if method is None:
            return ""
        return method.__doc__

    # ===== Méthodes utilitaires =====
    def getRevision(self):
        """Retourne la révision SCM du serveur."""
        return scmRevision("$Rev$")

    def getVersion(self):
        """Retourne la version du serveur."""
        return VERSION

    def log(self, fileprefix, content):
        """
        Écrit un message dans un fichier de log.

        Args:
            fileprefix (str): Préfixe du fichier de log.
            content (str): Contenu à enregistrer.
        """
        with open(f"{localstatedir}/log/mmc/mmc-{fileprefix}.log", "a") as f:
            f.write(f"{time.asctime()}: {content}\n")


















class MMCApp(object):
    """Represent the MMCApp"""

    def __init__(self, config, options):
        self.config = readConfig(config)
        self.conffile = options.inifile
        self.daemon = options.daemonize
        self.daemonlog = options.daemonizenolog

        if hasattr(options, "exclude") and options.exclude is not None:
            self.exclude = options.exclude.split(",")

            for filter in self.exclude:
                logger.addFilter(ExcludeContainsFilter(filter))
                logging.getLogger("slixmpp.xmlstream.xmlstream").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.clientxmpp").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.plugins.base").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger(
                    "slixmpp.features.feature_starttls.starttls"
                ).addFilter(ExcludeContainsFilter(filter))
                logging.getLogger("slixmpp.thirdparty.statemachine").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger(
                    "slixmpp.features.feature_rosterver.rosterver"
                ).addFilter(ExcludeContainsFilter(filter))
                logging.getLogger("slixmpp.plugins.xep_0045").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.plugins.xep_0078.legacyauth").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.features.feature_bind.bind").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.features.feature_session.session").addFilter(
                    ExcludeContainsFilter(filter)
                )
                logging.getLogger("slixmpp.xmlstream.scheduler").addFilter(
                    ExcludeContainsFilter(filter)
                )

        if hasattr(options, "include") and options.include is not None:
            self.include = options.include.split(",")
            logger.addFilter(IncludeContainsFilter(self.include))
            logging.getLogger("slixmpp.xmlstream.xmlstream").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.clientxmpp").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.plugins.base").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.features.feature_starttls.starttls").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.thirdparty.statemachine").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.features.feature_rosterver.rosterver").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.plugins.xep_0045").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.plugins.xep_0078.legacyauth").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.features.feature_bind.bind").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.features.feature_session.session").addFilter(
                IncludeContainsFilter(self.include)
            )
            logging.getLogger("slixmpp.xmlstream.scheduler").addFilter(
                IncludeContainsFilter(self.include)
            )

        if not self.daemonlog:
            self.daemon = False
        # Shared return state, so that father can know if children goes wrong
        if self.daemon:
            self._shared_state = mp.Value("i", 0)

        if self.daemon:
            self.lock = mp.Lock()

    def getState(self):
        if self.daemon:
            return self._shared_state.value

    def setState(self, s):
        if self.daemon:
            self._shared_state.value = s

    state = property(getState, setState)

    def daemonize(self):
        # Test if mmcagent has been already launched in daemon mode
        if os.path.isfile(self.config.pidfile):
            print(
                "%s already exist. Maybe mmc-agent is already running\n"
                % self.config.pidfile
            )
            sys.exit(0)

        # do the UNIX double-fork magic, see Stevens' "Advanced
        # Programming in the UNIX Environment" for details (ISBN 0201563177)
        try:
            pid = os.fork()
            if pid > 0:
                # Wait for initialization before exiting
                self.lock.acquire()
                # exit first parent and return
                sys.exit(self.state)
        except OSError as e:
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            self.state = 1
            self.lock.release()
            sys.exit(1)

        maxfd = getrlimit(RLIMIT_NOFILE)[1]
        if maxfd == RLIM_INFINITY:
            maxfd = 1024

        for fd in range(0, maxfd):
            # Don't close twisted FDs
            # TODO: make a clean code to be sure nothing is opened before this function
            # ie: daemonize very early, then after import all stuff...
            if fd not in (3, 4, 5, 6, 7, 8):
                try:
                    os.close(fd)
                except OSError:
                    pass

        if hasattr(os, "devnull"):
            REDIRECT_TO = os.devnull
        else:
            REDIRECT_TO = "/dev/null"

        os.open(REDIRECT_TO, os.O_RDWR)
        os.dup2(0, 1)
        os.dup2(0, 2)

        # write pidfile
        self.writePid()

    def kill(self):
        pid = self.readPid()
        if pid is None:
            print("Can not find a running mmc-agent.")
            return 1

        try:
            os.kill(pid, signal.SIGTERM)
        except Exception as e:
            print("Can not terminate running mmc-agent: %s" % e)
            return 1

        return 0

    def reload(self):
        if self.config.enablessl:
            protocol = "https"
        else:
            protocol = "http"

        client = xmlrpc.client.ServerProxy(
            "%s://%s:%s@%s:%s/"
            % (
                protocol,
                self.config.login,
                self.config.password,
                self.config.host,
                self.config.port,
            )
        )
        try:
            client.system.reloadModulesConfiguration()
            return 0
        except Exception as e:
            print("Unable to reload configuration: %s" % str(e))
            return 1

    def readPid(self):
        """Try to read pid of running mmc-agent in pidfile
        Return the pid or None in case of failure
        """
        try:
            if os.path.exists(self.config.pidfile):
                f = open(self.config.pidfile, "r")
                try:
                    line = f.readline()
                    return int(line.strip())
                finally:
                    f.close()
        except:
            return None

    def writePid(self):
        pid = os.getpid()
        f = open(self.config.pidfile, "w")
        try:
            f.write("%s\n" % pid)
        finally:
            f.close()

    def cleanPid(self):
        if os.path.exists(self.config.pidfile):
            os.unlink(self.config.pidfile)

    def run(self):
        # If umask = 0077, created files will be rw for effective user only
        # If umask = 0007, they will be rw for effective user and group only
        os.umask(self.config.umask)
        os.setegid(self.config.egid)
        os.seteuid(self.config.euid)

        # Daemonize early
        if self.daemon:
            self.lock.acquire()
            self.daemonize()

        # Do all kind of initialization
        try:
            ret = self.initialize()
        finally:
            # Tell the father how to return, and let him return (release)
            if self.daemon:
                self.state = ret
                self.lock.release()

        if ret:
            return ret

        reactor.run()

    def initialize(self):
        # Initialize logging object
        print("Initialisation of the XMLRPC Server")
        try:
            logging.handlers.TimedCompressedRotatingFileHandler = (
                TimedCompressedRotatingFileHandler
            )
            logging.config.fileConfig(self.conffile)

            # In foreground mode, log to stderr
            if not self.daemon:
                if self.daemonlog:
                    hdlr2 = logging.StreamHandler()
                    hdlr2.setFormatter(ColoredFormatter("%(levelname)-18s %(message)s"))
                    logger.addHandler(hdlr2)

            # Create log dir if it doesn't exist
            try:
                os.mkdir(localstatedir + "/log/mmc")
            except OSError as xxx_todo_changeme:
                # Raise exception if error is not "File exists"
                (errno, strerror) = xxx_todo_changeme.args
                # Raise exception if error is not "File exists"
                if errno != 17:
                    raise
                else:
                    pass

            # Changing path to probe and load plugins
            os.chdir(os.path.dirname(globals()["__file__"]))

            logger.info("mmc-agent %s starting..." % VERSION)
            logger.info("Using Python %s" % sys.version.split("\n")[0])
            logger.info("Using Python Twisted %s" % twisted.copyright.version)

            logger.debug(
                "Running as euid = %d, egid = %d" % (os.geteuid(), os.getegid())
            )
            if self.config.multithreading:
                logger.info(
                    "Multi-threading enabled, max threads pool size is %d"
                    % self.config.maxthreads
                )
                reactor.suggestThreadPoolSize(self.config.maxthreads)

            # Export the MMC-AGENT variable in the environement so that
            # child process can know they were spawned by mmc-agent
            os.environ["MMC_AGENT"] = VERSION

            # Start audit system
            l = AuditFactory().log("MMC-AGENT", "MMC_AGENT_SERVICE_START")

            # Ask PluginManager to load MMC plugins
            pm = PluginManager()
            code = pm.loadPlugins()
            if code:
                logger.debug(
                    "The initialisation of the XMLRPC Server returned the code: %s "
                    % code
                )
                return code

            try:
                self.startService(pm.plugins)
            except Exception as e:
                # This is a catch all for all the exception that can happened
                logger.exception("Program exception: " + str(e))
                logger.debug("The initialisation of the XMLRPC Server returned 1")
                return 1

            l.commit()
        except Exception:
            logger.error("%s" % (traceback.format_exc()))
        logger.debug("The initialisation of the XMLRPC Server returned 0")
        return 0

    def startService(self, mod):
        # Starting XMLRPC server
        r = MmcServer(mod, self.config)
        if self.config.enablessl:
            sslContext = makeSSLContext(
                self.config.verifypeer, self.config.cacert, self.config.localcert
            )
            reactor.listenSSL(
                self.config.port,
                MMCSite(r),
                interface=self.config.host,
                contextFactory=sslContext,
            )
        else:
            logger.warning("SSL is disabled by configuration.")
            reactor.listenTCP(
                self.config.port, server.Site(r), interface=self.config.host
            )

        # Add event handler before shutdown
        reactor.addSystemEventTrigger("before", "shutdown", self.cleanUp)
        logger.info(
            "Listening to XML-RPC requests on %s:%s"
            % (self.config.host, self.config.port)
        )
        # Start client XMPP if module xmppmaster enable
        if PluginManager().isEnabled("xmppmaster"):
            configxmppmaster = XmppMasterDatabase().config
            # create file  message
            PluginManager().getEnabledPlugins()["xmppmaster"].modulemessagefilexmpp = (
                messagefilexmpp(self, self.config, configxmppmaster)
            )
            self.modulexmppmaster = (
                PluginManager().getEnabledPlugins()["xmppmaster"].modulemessagefilexmpp
            )
            # on a besoin de savoir les modules de mmc initialise
            XmppMasterDatabase().initialisation_module_list_mmc(
                PluginManager().getEnabledPluginNames()
            )
            # MASTER now is a substitute.
            self.config_bool_done = False
            logger.info("Start/restart MMC presence client substitut master")
            result = self.modulexmppmaster.sendstr("Start/restart MMC")
            if result is None:
                logger.info("INITIALISATION MMC (xmppmaster) ERREUR")
                logger.info("VERIFY SUBSTITUT MASTER START")
                logger.info("VERIFY PARAMETERS CONNECTION TO SUBSTITUT MASTER")
                logger.info("Restart SUBSTITUT MASTER")
                return
            self.init_master_substitut()

    def init_master_substitut(self):
        logger.debug("INITIALISATION SUBSTITUT")
        ree = None
        if (
            not PluginManager()
            .getEnabledPlugins()["xmppmaster"]
            .modulemessagefilexmpp.config_bool_done
        ):
            # important ici sont reunit en exemple mcanisme d'utilisation du serveur substiitut master.
            logger.info("initialise la liste des module MMC dans substitut master")
            # list_mmc_module est appeler au lancement de la mmc.
            # list_mmc_module n'est pas 1 plugin cet appel est traité dans le plugin
            # serveur /pluginsmastersubstitute/plugin___server_mmc_master.py
            # cette list permet de renseigner le substitut master des module active dans mmc.
            # remarque si mmc est lancer avant le substitut master. celui ci ne recevra pas cette list.
            result = {
                "action": "list_mmc_module",
                "data": PluginManager().getEnabledPluginNames(),
            }
            logger.info(
                "Start/restart MMC send module On on %s  MMC"
                % PluginManager().getEnabledPluginNames()
            )

            ree = self.modulexmppmaster.send_call_plugin(result)
            logger.info(
                "call plugin %s on master directement tcp/ip : sessionid  %s => %s"
                % (result["action"], ree[0], ree[1])
            )
            if ree[0] is None and ree[0] == "Error connection":
                PluginManager().getEnabledPlugins()[
                    "xmppmaster"
                ].modulemessagefilexmpp.config_bool_done = False
                return False

            PluginManager().getEnabledPlugins()[
                "xmppmaster"
            ].modulemessagefilexmpp.config_bool_done = True
            return True
            # appel plugin directement sur substitut master.
            # Cela remplace les plugins master. qui seront transferer sur le substitut master.
            # remarque on prefixera les plugin par mmc_ quand ceux ci seront uniquement appelable par mmc
            # exemple appel pluging mmc directement sur substitut master test_plugin_master
            # remarque on pas de parametre to c'est 1 plugin mmc type
            # la connection mmc substitut est client/serveur/ mmc est client du substitut.
            # celui -ci est en mesure de renvoyer 1 resultat ici ree
            # -----------------------------------------------------------------------------------
            # --------------------------------- call plugin mmc ---------------------------------
            # logger.info("MMC start plugin test_plugin_master on substitut master : sessionid  %s => %s" % ( ree[0],ree[1]))
            # ree = self.modulexmppmaster.send_call_plugin({"action": "test_plugin_master",
            # "data": { "text" : "message" }} )
            # logger.info("call plugin test_plugin_master on master : sessionid  %s => %s" % ( ree[0],ree[1]))
            # -----------------------------------------------------------------------------------
            # -----------------------------------------------------------------------------------

            # --------------------------------------------------------------------------------------------------
            # --------------------------------- call plugin sur 1 acteur en xmpp -------------------------------
            # test envoi mesage to  machine  dev-deb12-2.zb0@pulse/525400944ac7
            # logger.info("Start/restart MMC creation canal commande xmpp3")

            # ree = self.modulexmppmaster.send_message('dev-deb12-2.zb0@pulse/525400944ac7',
            # {"action": "ping",
            # "data": { "text" : "message" }} )
            # --------------------------------------------------------------------------------------------------
            # --------------------------------------------------------------------------------------------------

            # --------------------------------------------------------------------------------------------------
            # --------------------------------- call iq synchrone sur sur 1 acteur en xmpp -------------------------------
            # test de machinessend_iq(mto, msg, timeout):
            # ree= self.modulexmppmaster.send_iq('dev-deb12-2.zb0@pulse/525400944ac7',
            # { "action": "test",
            # "data": {
            # "listinformation": ["get_ars_key_id_rsa", "keypub"],
            # "param": {},
            # },
            # }, 30)
            # logger.debug("RESULTAT is %s" % ree)

    def cleanUp(self):
        """
        function call before shutdown of reactor
        """
        if PluginManager().isEnabled("xmppmaster"):
            # self.modulexmppmaster
            if self.modulexmppmaster.isAlive():
                logger.info("mmc-agent xmppmaster stop...")
                self.modulexmppmaster.stop()
        logger.info("mmc-agent shutting down, cleaning up...")
        l = AuditFactory().log("MMC-AGENT", "MMC_AGENT_SERVICE_STOP")
        l.commit()

        self.cleanPid()


class MMCHTTPChannel(http.HTTPChannel):
    """
    We inherit from http.HTTPChannel to log incoming connections when the MMC
    agent is in DEBUG mode, and to log connection errors.
    """

    def connectionMade(self):
        http.HTTPChannel.connectionMade(self)

    def connectionLost(self, reason):
        if not reason.check(twisted.internet.error.ConnectionDone):
            logger.debug(reason)
        http.HTTPChannel.connectionLost(self, reason)


class MMCSite(server.Site):
    protocol = MMCHTTPChannel


def readConfig(config):
    """
    Read and check the MMC agent configuration file

    @param config: a MMCConfigParser object reading the agent conf file
    @type config: MMCConfigParser

    @return: MMCConfigParser object with extra attributes set
    @rtype: MMCConfigParser
    """
    # TCP/IP stuff
    try:
        config.host = config.get("main", "host")
        config.port = config.getint("main", "port")
    except Exception as e:
        logger.error(e)
        return 1

    if config.has_section("daemon"):
        config.euid = pwd.getpwnam(config.get("daemon", "user"))[2]
        config.egid = grp.getgrnam(config.get("daemon", "group"))[2]
        config.umask = int(config.get("daemon", "umask"), 8)
    else:
        config.euid = 0
        config.egid = 0
        config.umask = 0o077

    # HTTP authentication login/password
    config.login = config.get("main", "login")
    config.password = config.getpassword("main", "password")

    # RPC session timeout
    try:
        config.sessiontimeout = config.getint("main", "sessiontimeout")
    except (configparser.NoSectionError, configparser.NoOptionError):
        # Use default session timeout
        config.sessiontimeout = server.Session.sessionTimeout

    # SSL stuff
    try:
        config.enablessl = config.getboolean("main", "enablessl")
    except (configparser.NoSectionError, configparser.NoOptionError):
        config.enablessl = False
    try:
        config.verifypeer = config.getboolean("main", "verifypeer")
    except (configparser.NoSectionError, configparser.NoOptionError):
        config.verifypeer = False

    if config.enablessl:
        # For old version compatibility, we try to get the old options name
        try:
            config.localcert = config.get("main", "localcert")
        except (configparser.NoSectionError, configparser.NoOptionError):
            config.localcert = config.get("main", "privkey")
        try:
            config.cacert = config.get("main", "cacert")
        except (configparser.NoSectionError, configparser.NoOptionError):
            config.cacert = config.get("main", "certfile")

    try:
        config.pidfile = config.get("daemon", "pidfile")
    except (configparser.NoSectionError, configparser.NoOptionError):
        # For compatibility with old version
        config.pidfile = config.get("log", "pidfile")

    # Multi-threading support
    config.multithreading = True
    config.maxthreads = 20
    try:
        config.multithreading = config.getboolean("main", "multithreading")
        config.maxthreads = config.getint("main", "maxthreads")
    except configparser.NoOptionError:
        pass

    # parametre client submaster
    config.submaster_host = "::1"
    config.submaster_check_hostname = False
    config.submaster_allowed_token = "4O&vHYKG3Cqq3RCUJu!vnQu+dBGwDkpZ"
    config.submaster_ip_format = "ipv6"
    config.submaster_port = "57041"

    if config.has_option("submaster", "host"):
        config.submaster_host = config.get("submaster", "host")

    if config.has_option("submaster", "port"):
        config.submaster_port = config.getint("submaster", "port")

    if config.has_option("submaster", "ip_format"):
        config.submaster_ip_format = config.get("submaster", "ip_format")

    if config.has_option("submaster", "allowed_token"):
        config.submaster_allowed_token = config.get("submaster", "allowed_token")

    # if config.has_option("submaster", "check_hostname"):
    # config.submaster_check_hostname = config.getboolean("submaster", "check_hostname")

    return config


class PluginManager(Singleton):
    """
    This singleton class imports available MMC plugins, activates them, and
    keeps track of all enabled plugins.
    """

    pluginDirectory = "plugins/"
    # Will contains the enabled plugins name and corresponding python
    # module objects
    plugins = {}

    def __init__(self):
        Singleton.__init__(self)

    def isEnabled(self, plugin):
        """
        @rtype: bool
        @return: Return True if the plugin has been enabled
        """
        return plugin in self.plugins

    def getEnabledPlugins(self):
        """
        @rtype: dict
        @return: the enabled plugins as a dict, key is the plugin name, value
                 is the python module object
        """
        return self.plugins

    def getEnabledPluginNames(self):
        """
        @rtype: list
        @return: the names of the enabled plugins
        """
        return list(self.getEnabledPlugins().keys())

    def getAvailablePlugins(self):
        """
        Fetch all available MMC plugin

        @return: list of all mmc plugins names
        @rtype: list
        """
        plugins = []
        for path in glob.glob(os.path.join(self.pluginDirectory, "*", "__init__.py*")):
            plugin = path.split("/")[1]
            if not plugin in plugins:
                plugins.append(plugin)
        return plugins

    def loadPlugin(self, name, force=False):
        """
        Load a plugin with the given name.

        To start one single module after the agent startup, use startPlugin()
        instead

        @returns: 4 on fatal error (mmc agent should not start without that
        plugin), 0 on non-fatal failure, and the module itself if
        the load was successful
        """
        sys.path.append(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins")
        )
        try:
            logger.debug("Trying to load module %s" % name)
            spec = importlib.util.find_spec(name)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            logger.debug("Module %s loaded" % name)
        except Exception as e:
            logger.exception(e)
            logger.error(
                "Module " + name + " raise an exception.\n" + name + " not loaded."
            )
            return 0

        # If module has no activate function
        try:
            # if not force:
            #     func = getattr(plugin, "activate")
            # else:
            # logger.debug('Forcing plugin startup')
            # try:
            # func = getattr(plugin, "activateForced")
            # except AttributeError:
            # logger.debug('Trying to force startup of plugin %s but no "activateForced" method found\nFalling back to the normale activate method' % (name,))

            version = "version: " + str(getattr(plugin, "getVersion")())
            logger.info("Plugin %s loaded, %s" % (name, version))

            func = getattr(plugin, "activate")

        except AttributeError as error:
            logger.error("%s is not a MMC plugin." % name)
            logger.error("We obtained the error \n %s." % error)
            plugin = None
            return 0

        # If is active
        try:
            if func():
                version = "version: " + str(getattr(plugin, "getVersion")())
                logger.info("Plugin %s loaded, %s" % (name, version))
            else:
                # If we can't activate it
                logger.warning("Plugin %s not loaded." % name)
                plugin = None
        except Exception as e:
            logger.error("Error while trying to load plugin " + name)
            logger.exception(e)
            plugin = None
            # We do no exit but go on when another plugin than base fail

        # Check that "base" plugin was loaded
        if name == "base" and not plugin:
            logger.error("MMC agent can't run without the base plugin. Exiting.")
            return 4
        return plugin

    def startPlugin(self, name):
        """
        Force a plugin load.
        Even if the configuration indicates the plugin is disabled,
        we load it and add it to the loaded list.

        Use it to start a plugin after the mmc agent startup, dynamically.

        This tries to call the activateForced method of the plugin (for example to
        ignore the disable = 1 configuration option)
        """
        if name in self.getEnabledPluginNames() or name in self.plugins:
            logger.warning("Trying to start an already loaded plugin: %s" % (name,))
            return 0
        res = self.loadPlugin(name, force=True)
        if res == 0:
            return 0
        elif res is not None and not isinstance(res, int):
            self.plugins[name] = res
            getattr(self.plugins["base"], "setModList")(
                [name for name in list(self.plugins.keys())]
            )
        elif res == 4:
            return 4
        return res

    def loadPlugins(self):
        """
        Find and load available MMC plugins

        @rtype: int
        @returns: exit code > 0 on error
        """
        # Find available plugins
        mod = {}
        sys.path.append("plugins")
        # self.modList = []
        plugins = self.getAvailablePlugins()
        if not "base" in plugins:
            logger.error("Plugin 'base' is not available. Please install it.")
            return 1
        else:
            # Set base plugin as the first plugin to load
            plugins.remove("base")
            plugins.insert(0, "base")

        # Put pulse2 plugins as the last to be imported, else we may get a mix
        # up with pulse2 module available in the main python path
        if "pulse2" in plugins:
            plugins.remove("pulse2")
            plugins.append("pulse2")

        # Load plugins
        logger.info("Importing available MMC plugins")
        for plugin in plugins:
            res = self.loadPlugin(plugin)
            if res == 0:
                continue
            elif res is not None and not isinstance(res, int):
                mod[plugin] = res
            elif res == 4:
                return 4

        # store enabled plugins
        self.plugins = mod

        logger.info("MMC plugins activation stage 2")
        for plugin in plugins:
            if self.isEnabled(plugin):
                try:
                    func = getattr(mod[plugin], "activate_2")
                except AttributeError:
                    func = None
                if func:
                    if not func():
                        logger.error(
                            "Error in activation stage 2 for plugin '%s'" % plugin
                        )
                        logger.error(
                            "Please check your MMC agent configuration and log"
                        )
                        return 4

        # Set module list
        getattr(self.plugins["base"], "setModList")(
            [name for name in list(self.plugins.keys())]
        )
        return 0

    def stopPlugin(self, name):
        """
        Stops a plugin.

        @rtype: boolean
        returns: True on success, False if the module is not loaded.
        """
        if not name in self.plugins:
            return False
        plugin = self.plugins[name]
        try:
            deactivate = getattr(plugin, "deactivate")
        except AttributeError:
            logger.info("Plugin %s has no deactivate function" % (name,))
        else:
            logger.info("Deactivating plugin %s" % (name,))
            deactivate()
        del self.plugins[name]
        getattr(self.plugins["base"], "setModList")(
            [name for name in list(self.plugins.keys())]
        )
        return True
