#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

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
text_type = str if is_python3 else unicode
int_type = int if is_python3 else (int, long)
str_type = str if is_python3 else (str, unicode)


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
        if type(ctx.locations) == list:
            if hasattr(ctx.locations[0], "id"):  # GLPI 0.8
                ctx.locationsid = [e.id for e in ctx.locations]
            elif hasattr(ctx.locations[0], "ID"):  # GLPI 0.7x
                ctx.locationsid = [e.ID for e in ctx.locations]
    if not hasattr(ctx, "profile"):
        logging.getLogger().debug(
            "adding profiles in context for user %s" % (ctx.userid)
        )
        ctx.profile = ComputerLocationManager().getUserProfile(ctx.userid)
