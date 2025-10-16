# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText:2007-2014 Mandriva, http://www.mandriva.com
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This module just give access to small functions needed by both 0.7 and 0.8 backend
"""

from pulse2.utils import grepv
import logging


def encode_utf8(self, s):
    return s


def encode_latin1(self, s):
    try:
        return s.decode("utf8")
    except exceptions.UnicodeEncodeError:
        return s
    except AttributeError:
        # under python 2.3, unicode object dont have any decode method
        # but in the case it's already a unicode, we dont really need to decode
        # so just return the string
        return s


def decode_utf8(self, s):
    return s


def decode_latin1(self, s):
    try:
        return s.decode("latin-1")
    except exceptions.UnicodeEncodeError:
        return s


class DbTOA(object):
    def to_a(self):
        a = grepv("^_", dir(self))
        ret = []
        for i in a:
            j = getattr(self, i)
            if type(j) in (str, int, str):
                ret.append([i, j])
        return ret

#
# def fromUUID(uuid):
#     return int(uuid.replace("UUID", ""))
def fromUUID(uuid):
    """
    Convertit un UUID (chaîne, dictionnaire ou liste) en entier en utilisant `normalize_entity`.
    Renvoie un entier ou lève une exception si la conversion échoue.

    Args:
        uuid (str/dict/list): UUID à convertir.

    Returns:
        int: UUID converti en entier.

    Raises:
        ValueError: Si la conversion échoue ou si l'UUID est invalide.
    """
    normalized_uuid = normalize_entity(uuid)
    if normalized_uuid is None:
        raise ValueError(f"UUID invalide : {uuid}")
    return normalized_uuid

def toUUID(uuid):
    return "UUID%s" % (str(uuid))


def setUUID(obj):
    if hasattr(obj, "id"):
        setattr(obj, "uuid", toUUID(obj.id))
    elif hasattr(obj, "ID"):
        setattr(obj, "uuid", toUUID(obj.ID))
    else:
        logging.getLogger().error("Can't get id for %s => no UUID" % (str(obj)))
    return obj


def to_int(value, default=None):
    """Convertit value en int, ou renvoie default si conversion impossible."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def normalize_entity(entity, default=0):
    """
    Nettoie et convertit une valeur d'entité en entier.
    - Si entity est une liste, prend le premier élément.
    - Si entity est un dictionnaire, extrait la valeur de "id" ou "uuid".
    - Si c'est une chaîne commençant par "UUID", retire le préfixe.
    - Renvoie un entier ou default si échec.
    """
    if isinstance(entity, list):
        if not entity:  # Liste vide
            return default
        entity = entity[0]  # Prend le premier élément

    if isinstance(entity, dict):
        for key in ["id", "uuid"]:
            if key in entity:
                entity = entity[key]
                break
        else:
            return default

    if isinstance(entity, str) and entity.startswith("UUID"):
        entity = entity.replace("UUID", "")

    return to_int(entity, default)


def normalize_entity_list(entities, default=0):
    """
    Normalise une liste d'entités (chaînes, dictionnaires, ou mélangé).
    Renvoie une liste d'entiers normalisés.
    """
    if isinstance(entities, list):
        return [normalize_entity(entity, default) for entity in entities]
    return [normalize_entity(entities, default)]
