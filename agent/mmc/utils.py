# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# # tous les object incluts ici sont directement importable directement dans
# # exemple from mmc import convert
# # la class convert et importe.
from datetime import datetime
import base64
import zlib
import string
import yaml
from collections import OrderedDict
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import xmltodict
import json
import random

import re
import zipfile
import gzip

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
        # attention
        def convert_xml_to_dict → si tu veux toujours des listes, pratique pour un traitement uniforme.
        def xml_to_dict → si tu veux un dict naturel, proche de JSON classique, et gérer les erreurs.

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
        # attention
        def convert_xml_to_dict → si tu veux toujours des listes, pratique pour un traitement uniforme.
        def xml_to_dict → si tu veux un dict naturel, proche de JSON classique, et gérer les erreur

        xml_to_dict → cohérence avec JSON/YAML, plus simple à utiliser partout.
        convert_xml_to_dict → utile si tu veux forcer la structure en listes systématiques.

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
    def convert_to_bytes(input_data):
        if isinstance(input_data, bytes):
            return input_data
        elif isinstance(input_data, str):
            return input_data.encode("utf-8")
        else:
            raise TypeError("L'entrée doit être de type bytes ou string.")

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
            return convert.convert_json_to_dict(data)
        except Exception:
            pass

        # Essai YAML
        try:
            return convert.convert_yaml_to_dict(data)
        except Exception:
            pass

        # Essai XML
        try:
            return convert.xml_to_dict(data)
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
                    sub_diff = convert.dict_diff(d1[key], d2[key])
                    if any(sub_diff.values()):
                        diff["changed"][key] = sub_diff
                else:
                    diff["changed"][key] = {"old": d1[key], "new": d2[key]}

        return diff
