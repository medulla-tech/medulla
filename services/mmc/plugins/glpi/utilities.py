# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Glpi utilities
"""

from pulse2.managers.location import ComputerLocationManager
import mmc.plugins.glpi.database
import logging


# ################# display sql literal from sqlalchemy ############################

from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.sql.sqltypes import String, DateTime, NullType

# python2/3 compatible.
is_python3 = str is not bytes
text_type = str if is_python3 else str
int_type = int if is_python3 else (int, int)
str_type = str if is_python3 else (str, str)


class StringLiteral(String):
    """Teach SA how to literalize various things."""

    def literal_processor(self, dialect):
        super_processor = super(StringLiteral, self).literal_processor(dialect)

        def process(value):
            if isinstance(value, int_type):
                return text_type(value)
            if not isinstance(value, str_type):
                value = text_type(value)
            result = super_processor(value)
            if isinstance(result, bytes):
                result = result.decode(dialect.encoding)
            return result

        return process


class LiteralDialect(DefaultDialect):
    colspecs = {
        # prevent various encoding explosions
        String: StringLiteral,
        # teach SA about how to literalize a datetime
        DateTime: StringLiteral,
        # don't format py2 long integers to NULL
        NullType: StringLiteral,
    }


def literalquery(statement):
    """NOTE: This is entirely insecure. DO NOT execute the resulting strings."""
    import sqlalchemy.orm

    if isinstance(statement, sqlalchemy.orm.Query):
        statement = statement.statement
    return statement.compile(
        dialect=LiteralDialect(),
        compile_kwargs={"literal_binds": True},
    ).string


# ################# display sql literal from sqlalchemy ############################

def __convert(loc):
    """
    Convertit le nom d'une localisation en utilisant le décodage GLPI.

    Args:
        loc (object): Un objet représentant une localisation, avec au moins un attribut `name`.

    Returns:
        object: L'objet `loc` modifié, avec `loc.name` décodé selon la méthode GLPI.
    """
    # Décode le nom de la localisation via l'API GLPI
    loc.name = mmc.plugins.glpi.database.Glpi().decode(loc.name)
    return loc


def log_object_attributes(obj):
    """
    Affiche les attributs d'un objet sous forme de dictionnaire.

    Args:
        obj (object): L'objet dont on veut inspecter les attributs.

    Returns:
        dict or str: Un dictionnaire des attributs de l'objet si possible, sinon une chaîne indiquant l'absence d'attributs.
    """
    try:
        # Utilise vars() pour récupérer les attributs de l'objet sous forme de dictionnaire
        attributes = vars(obj)
        return attributes
    except TypeError:
        # Si l'objet n'a pas de __dict__ (ex: objet natif Python), retourne un message par défaut
        return "No attributes"


def complete_ctx(ctx):
    """
    Complète le contexte utilisateur avec les localisations GLPI et le profil utilisateur.

    Cette fonction ajoute deux informations au contexte (`ctx`) :
    - `locations`: Liste des localisations GLPI associées à l'utilisateur.
    - `profile`: Profil utilisateur récupéré via `ComputerLocationManager`.

    Args:
        ctx (object): Le contexte utilisateur actuel, doit avoir un attribut `userid` et éventuellement `locations` et `profile`.

    Side Effects:
        - Ajoute ou met à jour `ctx.locations` et `ctx.locationsid` si nécessaire.
        - Ajoute ou met à jour `ctx.profile` si nécessaire.
    """
    # Ajoute les localisations GLPI au contexte si elles ne sont pas déjà présentes
    if not hasattr(ctx, "locations") or ctx.locations is None:
        logging.getLogger().debug(
            "Ajout des localisations au contexte pour l'utilisateur %s" % (ctx.userid)
        )
        # Récupère les localisations de l'utilisateur et les convertit via __convert
        ctx.locations = list(
            map(
                __convert, mmc.plugins.glpi.database.Glpi().getUserLocations(ctx.userid)
            )
        )

        # Si des localisations sont trouvées, extrait les IDs selon la version de GLPI
        if isinstance(ctx.locations, list) and len(ctx.locations) > 0:
            if hasattr(ctx.locations[0], "id"):  # Cas GLPI 0.8+
                ctx.locationsid = [e.id for e in ctx.locations]
            elif hasattr(ctx.locations[0], "ID"):  # Cas GLPI 0.7x
                ctx.locationsid = [e.ID for e in ctx.locations]
            else:
                ctx.locationsid = []  # Aucun ID trouvé
        else:
            ctx.locationsid = []  # Aucune localisation trouvée

    # Ajoute le profil utilisateur au contexte s'il n'est pas déjà présent
    if not hasattr(ctx, "profile"):
        logging.getLogger().debug(
            "Ajout du profil au contexte pour l'utilisateur %s" % (ctx.userid)
        )
        ctx.profile = ComputerLocationManager().getUserProfile(ctx.userid)
