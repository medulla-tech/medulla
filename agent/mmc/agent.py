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
VERSION = "5.0.0"


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
    les packages suivant son obligatoire.
    python3-xmltodict python3-dicttoxml python3-yaml json2xml
    pip3 install dict2xml
    Cette class presente des methodes pour convertir simplement des objects.
    elle expose les fonction suivante
        convert_dict_to_yaml(input_dict)
        convert_yaml_to_dict(yaml_data)
        yaml_string_to_dict(yaml_string)
        check_yaml_conformance(yaml_data)
        compare_yaml(yaml_string1, yaml_string2)
        convert_dict_to_json(input_dict_json, indent=None, sort_keys=False)
        check_json_conformance(json_data)
        convert_json_to_dict(json_str)
        xml_to_dict(xml_string)
        compare_xml(xml_file1, xml_file2)
        convert_xml_to_dict(xml_str)
        convert_json_to_xml(input_json)
        convert_xml_to_json(input_xml)
        convert_dict_to_xml(data_dict)
        convert_bytes_datetime_to_string(data)
        compare_dicts(dict1, dict2)
        compare_json(json1, json2)
        convert_to_bytes(input_data)
        compress_and_encode(string)
        decompress_and_encode(string)
        convert_datetime_to_string(input_date)
        encode_to_string_base64(input_data)
        decode_base64_to_string_(input_data)
        check_base64_encoding(input_string)
        taille_string_in_base64(string)
        string_to_int(s)
        int_to_string(n)
        string_to_float(s)
        float_to_string(f)
        list_to_string(lst, separator=', ')
        string_to_list(s, separator=', ')
        list_to_set(lst)
        set_to_list(s)
        dict_to_list(d)
        list_to_dict(lst)
        char_to_ascii(c)
        ascii_to_char(n)
        convert_rows_to_columns(data)
        convert_columns_to_rows(data)
        convert_to_ordered_dict(dictionary)
        generate_random_text(num_words)
        capitalize_words(text)
        compress_data_to_bytes(data)
        decompress_data_to_bytes(data_bytes_compress
        compress_dict_to_dictbytes(dict_data)
        decompress_dictbytes_to_dict(data_bytes_compress)
        unserialized_compressdictbytes_to_dict(serialized_dict_bytes_compress)
        is_multiple_of(s, multiple=4)
        is_base64(s)
        header_body(xml_string)
        format_xml(xml_string)
        check_keys_in( dictdata, array_keys)
    """

    # YAML
    @staticmethod
    def convert_dict_to_yaml(input_dict):
        """
        la fonction suivante Python convertit 1 dict python en json.
        """
        if isinstance(input_dict, dict):
            return yaml.dump(convert.convert_bytes_datetime_to_string(input_dict))
        else:
            raise TypeError("L'entrée doit être de type dict.")

    @staticmethod
    def convert_yaml_to_dict(yaml_string):
        return convert.yaml_string_to_dict(yaml_string)

    @staticmethod
    def yaml_string_to_dict(yaml_string):
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
        try:
            # Chargement du YAML pour vérifier la conformité
            yaml.safe_load(convert.convert_bytes_datetime_to_string(yaml_data))
            return True
        except yaml.YAMLError:
            return False

    @staticmethod
    def compare_yaml(yaml_string1, yaml_string2):
        """
        Dans cette fonction compare_yaml, nous appelons la fonction yaml_string_to_dict pour convertir chaque chaîne YAML en dictionnaire.
        Si une exception ValueError est levée lors de la conversion, nous affichons l'erreur et retournons False.
        nous utilisons la fonction compare_dicts pour comparer les dictionnaires obtenus.
        Si les dictionnaires sont égaux, la fonction compare_yaml retourne True, sinon elle retourne False.
        """
        try:
            dict1 = convert.yaml_string_to_dict(yaml_string1)
            dict2 = convert.yaml_string_to_dict(yaml_string2)
            return convert.compare_dicts(dict1, dict2)
        except ValueError as e:
            print(f"Erreur: {str(e)}")
            return False

    # JSON
    @staticmethod
    def convert_dict_to_json(input_dict_json, indent=None, sort_keys=False):
        """
        la fonction suivante Python convertit 1 dict python en json.
        """
        if isinstance(input_dict_json, dict):
            return json.dumps(
                convert.convert_bytes_datetime_to_string(input_dict_json), indent=indent
            )
        else:
            raise TypeError("L'entrée doit être de type dict.")

    @staticmethod
    def check_json_conformance(json_data):
        try:
            json.loads(json_data)
            return True
        except json.JSONDecodeError:
            return False

    # json_bytes = json.dumps(dict_data, indent = 4, cls=DateTimebytesEncoderjson).encode('utf-8')

    @staticmethod
    def convert_json_to_dict(json_str):
        if isinstance(json_str, (dict)):
            return json_str
        stringdata = convert.convert_bytes_datetime_to_string(json_str)
        if isinstance(stringdata, (str)):
            try:
                return json.loads(stringdata)
            except json.decoder.JSONDecodeError as e:
                raise
            except Exception as e:
                # Code de gestion d'autres types d'exceptions
                logger.error("convert_json_to_dict %s" % (e))
                raise

    @staticmethod
    def xml_to_dict(xml_string):
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
        try:
            dict1 = convert.xml_to_dict(xml_file1)
            dict2 = convert.xml_to_dict(xml_file2)
            return convert.compare_dicts(dict1, dict2)
        except ValueError as e:
            print(f"Erreur: {str(e)}")
            return False

    @staticmethod
    def convert_xml_to_dict(xml_string):
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

    # xml
    @staticmethod
    def convert_xml_to_json(input_xml):
        return json.dumps(xmltodict.parse(input_xml), indent=4)

    @staticmethod
    def convert_dict_to_xml(data_dict):
        xml_str = xmltodict.unparse({"root": data_dict}, pretty=True)
        return xml_str

    @staticmethod
    def convert_bytes_datetime_to_string(data):
        """
        la fonction suivante Python parcourt récursivement un dictionnaire,
        convertit les types bytes en str,
        les objets datetime en chaînes de caractères au format "année-mois-jour heure:minute:seconde"
        si les clés sont de type bytes elles sont convertit en str :
        encodage ('utf-8') est utilise pour le decode des bytes.
        Si 1 chaine est utilisée pour definir FALSE ou True alors c'est convertit en boolean True/false
        Si 1 valeur est None, elle est convertit a ""
        Si key ou valeur ne peut pas etre convertit en str alors 1 exception est leve
        renvoi le dictionnaire serializable
        """
        if isinstance(data, (str)):
            compa = data.lower
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
                convert.convert_bytes_datetime_to_string(
                    key
                ): convert.convert_bytes_datetime_to_string(value)
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
                raise ValueError(
                    "Type %s impossible de convertir en string " % type(data)
                )
        return data

    @staticmethod
    def compare_dicts(dict1, dict2):
        """
        Dans cette fonction, nous commençons par comparer les ensembles des clés des deux dictionnaires (dict1.keys() et dict2.keys()). Si les ensembles des clés sont différents, nous retournons False immédiatement car les dictionnaires ne peuvent pas être égaux.

        Ensuite, nous itérons sur les clés du premier dictionnaire (dict1.keys()) et comparons les valeurs correspondantes dans les deux dictionnaires (value1 et value2).

        Si une valeur est un autre dictionnaire, nous effectuons un appel récursif à la fonction compare_dicts pour comparer les sous-dictionnaires. Si le résultat de l'appel récursif est False, nous retournons False immédiatement.

        Si les valeurs ne sont pas égales et ne sont pas des dictionnaires, nous retournons également False.

        Si toutes les clés et les valeurs correspondent dans les deux dictionnaires, nous retournons True à la fin de la fonction.
        """
        if dict1.keys() != dict2.keys():
            return False

        for key in dict1.keys():
            value1 = dict1[key]
            value2 = dict2[key]

            if isinstance(value1, dict) and isinstance(value2, dict):
                # Si la valeur est un dictionnaire, appel récursif
                if not convert.compare_dicts(value1, value2):
                    return False
            elif value1 != value2:
                # Si les valeurs ne sont pas égales, retourne False
                return False
        return True

    @staticmethod
    def compare_json(json1, json2):
        try:
            dict1 = json.loads(json1)
            dict2 = json.loads(json2)
        except json.JSONDecodeError:
            raise ValueError("Erreur lors de la conversion JSON en dictionnaire.")
        return convert.compare_dicts(dict1, dict2)

    @staticmethod
    def convert_to_bytes(input_data):
        if isinstance(input_data, bytes):
            return input_data
        elif isinstance(input_data, str):
            return input_data.encode("utf-8")
        else:
            raise TypeError("L'entrée doit être de type bytes ou string.")

    # COMPRESS
    @staticmethod
    def compress_and_encode(string):
        # Convert string to bytes
        data = convert.convert_to_bytes(string)
        # Compress the data using zlib
        compressed_data = zlib.compress(data, 9)
        # Encode the compressed data in base64
        encoded_data = base64.b64encode(compressed_data)
        return encoded_data.decode("utf-8")

    @staticmethod
    def decompress_and_encode(string):
        # Convert string to bytes
        data = convert.convert_to_bytes(string)
        decoded_data = base64.b64decode(data)
        # Decompress the data using zlib
        decompressed_data = zlib.decompress(decoded_data)
        # Encode the decompressed data in base64
        return decompressed_data.decode("utf-8")

    # datetime
    @staticmethod
    def convert_datetime_to_string(input_date: datetime):
        if isinstance(input_date, datetime):
            return input_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            raise TypeError("L'entrée doit être de type datetime.")

    # base64
    @staticmethod
    def encode_to_string_base64(input_data):
        if isinstance(input_data, str):
            input_data_bytes = input_data.encode("utf-8")
        elif isinstance(input_data, bytes):
            input_data_bytes = input_data
        else:
            raise TypeError("L'entrée doit être une chaîne ou un objet bytes.")
        encoded_bytes = base64.b64encode(input_data_bytes)
        encoded_string = encoded_bytes.decode("utf-8")
        return encoded_string

    @staticmethod
    def decode_base64_to_string_(input_data):
        try:
            decoded_bytes = base64.b64decode(input_data)
            decoded_string = decoded_bytes.decode("utf-8")
            return decoded_string
        except base64.binascii.Error:
            raise ValueError("L'entrée n'est pas encodée en base64 valide.")

    @staticmethod
    def check_base64_encoding(input_string):
        try:
            # Décode la chaîne en base64 et vérifie si cela génère une erreur
            base64.b64decode(input_string)
            return True
        except base64.binascii.Error:
            return False

    @staticmethod
    def taille_string_in_base64(string):
        """
        renvoie la taille que prend 1 string en encode en base64.
        """
        taille = len(string)
        return (taille + 2 - ((taille + 2) % 3)) * 4 / 3

    @staticmethod
    def string_to_int(s):
        """
        Conversion de chaînes en entiers
        """
        try:
            return int(s)
        except ValueError:
            return None

    @staticmethod
    def int_to_string(n):
        """
        Conversion d'entiers en chaînes
        """
        return str(n)

    @staticmethod
    def string_to_float(s):
        """
        Conversion de chaînes en nombres à virgule flottante
        """
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def float_to_string(f):
        """
        Conversion de nombres à virgule flottante en chaînes
        """
        return str(f)

    @staticmethod
    def list_to_string(lst, separator=", "):
        """
        Conversion d'une liste de chaînes en une seule chaîne avec un séparateur
        """
        return separator.join(lst)

    @staticmethod
    def string_to_list(s, separator=", "):
        """
        Conversion d'une chaîne en une liste en utilisant un séparateur
        """
        return s.split(separator)

    @staticmethod
    def list_to_set(lst):
        """
        Conversion d'une liste en un ensemble (élimine les doublons)
        """
        return set(lst)

    @staticmethod
    def set_to_list(s):
        """
        Conversion d'un ensemble en une liste en conservant l'ordre
        """
        return [item for item in s]

    @staticmethod
    def dict_to_list(d):
        """
        Conversion d'un dictionnaire en une liste de tuples clé-valeur
        """
        return list(d.items())

    @staticmethod
    def list_to_dict(lst):
        """
        Conversion d'une liste de tuples clé-valeur en un dictionnaire
        """
        return dict(lst)

    @staticmethod
    def char_to_ascii(c):
        """
        Conversion de caractères en code ASCII
        """
        return ord(c)

    @staticmethod
    def ascii_to_char(n):
        """
        Conversion de code ASCII en caractère :
        """
        return chr(n)

    @staticmethod
    def convert_rows_to_columns(data):
        """
        cette fonction fait la convertion depuis 1 list de dict representant des lignes
        en
        1 list de colonne

        data = [{"id": 1, "name": "dede", "age": 30},
                {"id": 2, "name": "dada", "age": 25}]
        to
        [{'age': [30, 25]}, {'name': ['dede', 'dada']}, {'id': [1, 2]}]
        """
        # Obtenez les noms de colonnes
        column_names = set()
        for row in data:
            column_names.update(row.keys())
        # Créez un dictionnaire vide pour chaque colonne
        columns = {name: [] for name in column_names}
        # Remplissez les colonnes avec les valeurs correspondantes
        for row in data:
            for column, value in row.items():
                columns[column].append(value)
        # Convertissez les dictionnaires de colonnes en une liste de colonnes
        columns_list = [{name: values} for name, values in columns.items()]
        return columns_list

    @staticmethod
    def convert_columns_to_rows(data):
        """
        Cette fonction fait l'inverse de la conversion réalisée par la fonction convert_rows_to_columns.

        data = [{'age': [30, 25]}, {'name': ['dede', 'dada']}, {'id': [1, 2]}]
        to
        [{"id": 1, "name": "dede", "age": 30},
        {"id": 2, "name": "dada", "age": 25}]
        """
        # Obtenez tous les noms de colonnes
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
        ordered_dict = OrderedDict()
        for key, value in dictionary.items():
            ordered_dict[key] = value
        return ordered_dict

    @staticmethod
    def generate_random_text(num_words):
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
        renvoi la chaine avec chaque mot commencant par une majuscule et les autres lettres sont en minuscules
        """
        words = text.split()
        capitalized_words = [word.capitalize() for word in words]
        capitalized_text = " ".join(capitalized_words)
        return capitalized_text

    # Fonction de compression gzip
    @staticmethod
    def compress_data_to_bytes(data_string_or_bytes):
        return gzip.compress(convert.convert_to_bytes(data_string_or_bytes))

    # Fonction de décompression gzip
    @staticmethod
    def decompress_data_to_bytes(data_bytes_compress):
        return convert.convert_to_bytes(gzip.decompress(data_bytes_compress))

    @staticmethod
    def serialized_dict_to_compressdictbytes(dict_data):
        json_bytes = json.dumps(
            dict_data, indent=4, cls=DateTimebytesEncoderjson
        ).encode("utf-8")
        return convert.compress_data_to_bytes(json_bytes)

    @staticmethod
    def unserialized_compressdictbytes_to_dict(serialized_dict_bytes_compress):
        json_bytes = gzip.decompress(
            convert.convert_to_bytes(serialized_dict_bytes_compress)
        )
        return json.loads(json_bytes)

    @staticmethod
    def is_multiple_of(s, multiple=4):
        return len(s) % multiple == 0

    @staticmethod
    def is_base64(s):
        if not convert.is_multiple_of(s, multiple=4):
            return False
        decoded = None
        try:
            # Tente de décoder la chaîne en base64
            decoded = base64.b64decode(s)
            # Vérifie si la chaîne d'origine est égale à la chaîne encodée puis décodée
            if base64.b64encode(decoded) == s.encode():
                return decoded
            else:
                return False
        except:
            return False

    @staticmethod
    def header_body(xml_string):
        """
        on supprime l'entete xml
        """
        body = header = ""
        index = xml_string.find("?>")
        if index != -1:
            # Supprimer l'en-tête XML
            body = xml_string[index + 2 :]
            header = xml_string[: index + 2]
        return header, body

    @staticmethod
    def format_xml(xml_string):
        dom = parseString(xml_string)
        formatted_xml = dom.toprettyxml(indent="  ")
        return formatted_xml

    @staticmethod
    def check_keys_in(dictdata, array_keys):
        if all(key in dictdata for key in array_keys):
            return True
        return False


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

    def __init__(self, config):
        # Lit configuration du fichier
        self.config = config
        self.message_type = "json"
        self.config_bool_done = False

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
            if self.config.submaster_ip_format == "ipv6":
                client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Activation de l'option pour réutiliser l'adresse
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = self.config.submaster_check_hostname
            context.verify_mode = ssl.CERT_NONE

            # test json
            client.connect((self.config.submaster_host, self.config.submaster_port))
            ssock = context.wrap_socket(
                client, server_hostname=self.config.submaster_host
            )
            response = None
            try:
                message = self.config.submaster_allowed_token + msg
                ssock.sendall(convert.compress_data_to_bytes(message))
                response = convert.decompress_data_to_bytes(ssock.recv(2097152))
                response = convert.convert_bytes_datetime_to_string(response)
            finally:
                # Fermeture de la connexion SSL
                # Fermeture du socket principal
                ssock.close()
                if self.config.submaster_allowed_token:
                    longueur = len(self.config.submaster_allowed_token)
                    if longueur > 0 and len(response) > longueur:
                        return response[longueur:]
                return response
        except ConnectionRefusedError as e:
            logger.error(
                "Erreur connection verify substitut master %s:%s"
                % (self.config.submaster_host, self.config.submaster_port)
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
            self.init_master_substitut()
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
    Extended version of TimedRotatingFileHandler that compress logs on rollover.
    the rotation file is compress in zip
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
        super(TimedCompressedRotatingFileHandler, self).__init__(
            filename, when, interval, backupCount, encoding, delay, utc
        )
        self.backupCountlocal = backupCount

    def get_files_by_date(self):
        dir_name, base_name = os.path.split(self.baseFilename)
        file_names = os.listdir(dir_name)
        result = []
        result1 = []
        prefix = "{}".format(base_name)
        for file_name in file_names:
            if file_name.startswith(prefix) and not file_name.endswith(".zip"):
                f = os.path.join(dir_name, file_name)
                result.append((os.stat(f).st_ctime, f))
            if file_name.startswith(prefix) and file_name.endswith(".zip"):
                f = os.path.join(dir_name, file_name)
                result1.append((os.stat(f).st_ctime, f))
        result1.sort()
        result.sort()
        while result1 and len(result1) >= self.backupCountlocal:
            el = result1.pop(0)
            if os.path.exists(el[1]):
                os.remove(el[1])
        return result[1][1]

    def doRollover(self):
        super(TimedCompressedRotatingFileHandler, self).doRollover()
        try:
            dfn = self.get_files_by_date()
        except:
            return
        dfn_zipped = "{}.zip".format(dfn)
        if os.path.exists(dfn_zipped):
            os.remove(dfn_zipped)
        with zipfile.ZipFile(dfn_zipped, "w") as f:
            f.write(dfn, dfn_zipped, zipfile.ZIP_DEFLATED)
        os.remove(dfn)


logger = logging.getLogger()

sys.path.append("plugins")

Fault = xmlrpc.client.Fault
ctx = None
VERSION = "5.0.0"


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
    MMC Server implemented as a XML-RPC server.

    config file : @sysconfdir@/agent/config.ini

    Create a twisted XMLRPC server, load plugins in
    "plugins/" directory
    """

    # Attribute to keep traces of all running sessions
    sessions = set()

    def __init__(self, modules, config):
        XMLRPC.__init__(self)
        self.modules = modules
        self.config = config

    def _splitFunctionPath(self, functionPath):
        if "." in functionPath:
            mod, func = functionPath.split(".", 1)
        else:
            mod = None
            func = functionPath
        return mod, func

    def _getFunction(self, functionPath, request=""):
        """Overrided to use functions from our plugins"""
        mod, func = self._splitFunctionPath(functionPath)

        try:
            if mod and mod != "system":
                try:
                    ret = getattr(self.modules[mod], func)
                except AttributeError:
                    rpcProxy = getattr(self.modules[mod], "RpcProxy")
                    ret = rpcProxy(request, mod).getFunction(func)
            else:
                ret = getattr(self, func)
        except AttributeError:
            logger.error(functionPath + " not found")
            raise Fault("NO_SUCH_FUNCTION", "No such function " + functionPath)
        return ret

    def _needAuth(self, functionPath):
        """
        @returns: True if the specified function requires a user authentication
        @rtype: boolean
        """
        mod, func = self._splitFunctionPath(functionPath)
        # Special case: reload mehod
        if (mod, func) == ("system", "reloadModulesConfiguration"):
            return False
        ret = True
        if mod:
            try:
                nanl = self.modules[mod].NOAUTHNEEDED
                ret = func not in nanl
            except (KeyError, AttributeError):
                pass
        return ret

    def render_OPTIONS(self, request):
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
        override method of xmlrpc python twisted framework

        @param request: raw request xmlrpc
        @type request: xml str

        @return: interpreted request
        """
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
        requestxml = request.content.read()
        args, functionPath = xmlrpc.client.loads(requestxml)
        s = request.getSession()
        try:
            s.loggedin
        except AttributeError:
            s.loggedin = False
            # Set session expire timeout
            s.sessionTimeout = self.config.sessiontimeout

        # Check authorization using HTTP Basic
        cleartext_token = self.config.login + ":" + self.config.password
        user = str(request.getUser(), "utf-8")
        password = str(request.getPassword(), "utf-8")

        token = user + ":" + password
        if token != cleartext_token:
            logger.error("Invalid login / password for HTTP basic authentication")
            request.setResponseCode(http.UNAUTHORIZED)
            self._cbRender(
                Fault(
                    http.UNAUTHORIZED,
                    "Unauthorized: invalid credentials to connect to the MMC agent, basic HTTP authentication is required",
                ),
                request,
            )
            return server.NOT_DONE_YET

        if not s.loggedin:
            logger.debug(
                "RPC method call from unauthenticated user: %s" % functionPath
                + str(args)
            )
            # Save the first sent HTTP headers, as they contain some
            # informations
            s.http_headers = request.requestHeaders.copy()
        else:
            logger.debug(
                "RPC method call from user %s: %s"
                % (s.userid, functionPath + str(args))
            )
        try:
            if not s.loggedin and self._needAuth(functionPath):
                msg = "Authentication needed: %s" % functionPath
                logger.error(msg)
                raise Fault(8003, msg)
            else:
                if not s.loggedin and not self._needAuth(functionPath):
                    # Provide a security context when a method which doesn't
                    # require a user authentication is called
                    s = request.getSession()
                    s.userid = "root"
                    try:
                        self._associateContext(request, s, s.userid)
                    except Exception as e:
                        s.loggedin = False
                        logger.exception(e)
                        f = Fault(8004, "MMC agent can't provide a security context")
                        self._cbRender(f, request)
                        return server.NOT_DONE_YET
                function = self._getFunction(functionPath, request)
        except Fault as f:
            self._cbRender(f, request)
        else:
            if self.config.multithreading:
                oldargs = args
                args = (
                    function,
                    s,
                ) + args
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
        Very similar to deferToThread, but also handles function that results
        to a Deferred object.
        """

        def _printExecutionTime(start):
            logger.debug("Execution time: %f" % (time.time() - start))

        def _cbSuccess(result, deferred, start):
            _printExecutionTime(start)
            reactor.callFromThread(deferred.callback, result)

        def _cbFailure(failure, deferred, start):
            _printExecutionTime(start)
            reactor.callFromThread(deferred.errback, failure)

        def _putResult(deferred, f, session, args, kwargs):
            logger.debug(
                "Using thread #%s for %s"
                % (threading.currentThread().getName().split("-")[2], f.__name__)
            )
            # Attach current user session to the thread
            threading.currentThread().session = session
            start = time.time()
            try:
                result = f(*args, **kwargs)
            except:
                f = failure.Failure()
                reactor.callFromThread(deferred.errback, f)
            else:
                if isinstance(result, defer.Deferred):
                    # If the result is a Deferred object, attach callback and
                    # errback (we are not allowed to result to a Deferred)
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
        s = request.getSession()
        auth_funcs = ["base.ldapAuth", "base.tokenAuthenticate", "base.authenticate"]
        if functionPath in auth_funcs and not isinstance(result, Fault):
            # if we are logging on and there was no error
            if result:
                s = request.getSession()
                s.loggedin = True
                s.userid = args[0]
                try:
                    self._associateContext(request, s, s.userid)
                except Exception as e:
                    s.loggedin = False
                    logger.exception(e)
                    f = Fault(
                        8004,
                        "MMC agent can't provide a security context for this account",
                    )
                    self._cbRender(f, request)
                    return
        if result is None:
            result = 0
        if isinstance(result, Handler):
            result = result.result

        if not isinstance(result, xmlrpc.client.Fault):
            result = (result,)
        try:
            if type(result[0]) == dict:
                # FIXME
                # Evil hack ! We need this to transport some data as binary instead of string
                if "jpegPhoto" in result[0]:
                    result[0]["jpegPhoto"] = [
                        xmlrpc.client.Binary(result[0]["jpegPhoto"][0])
                    ]
        except IndexError:
            pass
        except Exception:
            pass
        try:
            if s.loggedin:
                logger.debug(
                    "Result for "
                    + s.userid
                    + ", "
                    + str(functionPath)
                    + ": "
                    + str(result)
                )
            else:
                logger.debug(
                    "Result for unauthenticated user, "
                    + str(functionPath)
                    + ": "
                    + str(result)
                )
            s = xmlrpc.client.dumps(result, methodresponse=1)
        except Exception as e:
            f = Fault(self.FAILURE, "can't serialize output: " + str(e))
            s = xmlrpc.client.dumps(f, methodresponse=1)
        s = bytes(s, encoding="utf-8")
        request.setHeader("content-length", str(len(s)))
        request.setHeader("content-type", "application/xml")
        request.write(s)
        request.finish()

    def _ebRender(self, failure, functionPath, args, request):
        logger.error(
            "Error during render " + functionPath + ": " + failure.getTraceback()
        )
        # Prepare a Fault result to return
        result = {}
        result["faultString"] = functionPath + " " + str(args)
        result["faultCode"] = str(failure.type) + ": " + str(failure.value) + " "
        result["faultTraceback"] = failure.getTraceback()
        return result

    def _associateContext(self, request, session, userid):
        """
        Ask to each activated Python plugin a context to attach to the user
        session.

        @param request: the current XML-RPC request
        @param session: the current session object
        @param userid: the user login
        """
        session.contexts = {}
        for mod in self.modules:
            try:
                contextMaker = getattr(self.modules[mod], "ContextMaker")
            except AttributeError:
                # No context provided
                continue
            cm = contextMaker(request, session, userid)
            context = cm.getContext()
            if context:
                logger.debug("Attaching module '%s' context to user session" % mod)
                session.contexts[mod] = context

        # Add associated context session to sessions set
        if session not in self.sessions:
            self.sessions.add(session)

    # ======== Reload method ================

    def reloadModulesConfiguration(self):
        import gc
        from mmc.support.config import PluginConfig

        for obj in gc.get_objects():
            if isinstance(obj, PluginConfig):
                try:
                    # Reloading configuration file
                    fid = open(obj.conffile, "r")
                    obj.readfp(fid, obj.conffile)
                    if os.path.isfile(obj.conffile + ".local"):
                        fid = open(obj.conffile + ".local", "r")
                        obj.readfp(fid, obj.conffile + ".local")
                    # Refresh config attributes
                    obj.readConf()
                except Exception as e:
                    logger.error(
                        "Error while reloading configuration file %s", obj.conffile
                    )
                    logger.error(str(e))
                    return "Failed"

        # Manually expiring all logged sessions
        for session in self.sessions:
            session.expire()
        self.sessions = set()
        return "Done"

    # ======== XMLRPC Standard Introspection methods ================

    def listMethods(self):
        method_list = []

        for mod in self.modules:
            instance = self.modules[mod]
            # Fetching module root methods
            for m in dir(instance):
                r = getattr(instance, m)
                # If attr is callable, we add it to method_list
                if hasattr(r, "__call__"):
                    method_list.append(mod + "." + m)
            # Doing same thing for module.RPCProxy if exists
            if hasattr(instance, "RpcProxy"):
                for m in dir(instance.RpcProxy):
                    r = getattr(instance.RpcProxy, m)
                    # If attr is callable, we add it to method_list
                    if hasattr(r, "__call__"):
                        method_list.append(mod + "." + m)

        return method_list

    def __getClassMethod(self, name):
        mod, func = self._splitFunctionPath(name)

        if not mod in self.modules:
            return None

        instance = self.modules[mod]
        if hasattr(instance, "RpcProxy"):
            if hasattr(instance.RpcProxy, func):
                return getattr(instance.RpcProxy, func)
            elif hasattr(instance, func):
                return getattr(instance, func)
            else:
                return None
        else:
            return None

    def methodSignature(self, name):
        method = self.__getClassMethod(name)

        if method is None:
            return []
        else:
            return getfullargspec(method)[0]

    def methodHelp(self, name):
        method = self.__getClassMethod(name)

        if method is None:
            return ""
        else:
            return method.__doc__

    # ===============================================================

    def getRevision(self):
        return scmRevision("$Rev$")

    def getVersion(self):
        return VERSION

    def log(self, fileprefix, content):
        """
        @param fileprefix: Write log file in @localstatedir@/log/mmc/mmc-fileprefix.log
        @param content: string to record in log file
        """
        f = open(localstatedir + "/log/mmc/mmc-" + fileprefix + ".log", "a")
        f.write(time.asctime() + ": " + content + "\n")
        f.close()


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
            # create file  message
            PluginManager().getEnabledPlugins()[
                "xmppmaster"
            ].messagefilexmpp = messagefilexmpp(self.config)
            self.modulexmppmaster = (
                PluginManager().getEnabledPlugins()["xmppmaster"].messagefilexmpp
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
        if (
            not PluginManager()
            .getEnabledPlugins()["xmppmaster"]
            .messagefilexmpp.config_bool_done
        ):
            # important ici sont reunit en exemple mcanisme d'utilisation du serveur substiitut master.
            logger.info("Start/restart MMC send module On on MMC")
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

            PluginManager().getEnabledPlugins()[
                "xmppmaster"
            ].messagefilexmpp.config_bool_done = True

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
