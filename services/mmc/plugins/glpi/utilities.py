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

def __convert(loc):
    loc.name = mmc.plugins.glpi.database.Glpi().decode(loc.name)
    return loc

def complete_ctx(ctx):
    """
    Set GLPI user locations and profile in current security context.
    """
    if not hasattr(ctx, "locations") or ctx.locations == None:
        logging.getLogger().debug("adding locations in context for user %s" % (ctx.userid))
        ctx.locations = map(__convert, mmc.plugins.glpi.database.Glpi().getUserLocations(ctx.userid))
        if type(ctx.locations) == list:
            if hasattr(ctx.locations[0], 'id'): # GLPI 0.8
                ctx.locationsid = map(lambda e: e.id, ctx.locations)
            elif hasattr(ctx.locations[0], 'ID'): # GLPI 0.7x
                ctx.locationsid = map(lambda e: e.ID, ctx.locations)
    if not hasattr(ctx, "profile"):
        logging.getLogger().debug("adding profiles in context for user %s" % (ctx.userid))
        ctx.profile = ComputerLocationManager().getUserProfile(ctx.userid)
