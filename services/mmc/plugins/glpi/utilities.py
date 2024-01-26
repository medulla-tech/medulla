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
    loc.name = mmc.plugins.glpi.database.Glpi().decode(loc.name)
    return loc


def complete_ctx(ctx):
    """
    Set GLPI user locations and profile in current security context.
    """
    if not hasattr(ctx, "locations") or ctx.locations == None:
        logging.getLogger().debug(
            "adding locations in context for user %s" % (ctx.userid)
        )
        ctx.locations = list(
            map(
                __convert, mmc.plugins.glpi.database.Glpi().getUserLocations(ctx.userid)
            )
        )
        if isinstance(ctx.locations, list) and len(ctx.locations) > 0:
            if hasattr(ctx.locations[0], "id"):  # GLPI 0.8
                ctx.locationsid = [e.id for e in ctx.locations]
            elif hasattr(ctx.locations[0], "ID"):  # GLPI 0.7x
                ctx.locationsid = [e.ID for e in ctx.locations]
        else:
            ctx.locationsid = []
    if not hasattr(ctx, "profile"):
        logging.getLogger().debug(
            "adding profiles in context for user %s" % (ctx.userid)
        )
        ctx.profile = ComputerLocationManager().getUserProfile(ctx.userid)
