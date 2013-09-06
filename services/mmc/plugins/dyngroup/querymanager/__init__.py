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
QueryManager API for dyngroup
"""

import logging

from mmc.plugins.dyngroup.database import DyngroupDatabase
from mmc.plugins.dyngroup.config import DGConfig

def activate():
    conf = DGConfig()
    conf.init("dyngroup")
    return conf.dyngroup_activate

def queryPossibilities():
    ret = {}
    ret['groupname'] = ['list', getAllGroupName]
    return ret

def queryGroups():
    # Assign criterions to categories
    ret = {}
    #
    ret['Group'] = [ ['groupname',''] ]
    #
    return ret

def extendedPossibilities():
    return ""

def query(ctx, criterion, value):
    logging.getLogger().info(ctx)
    logging.getLogger().info(criterion)
    logging.getLogger().info(value)
    machines = []
    if criterion == 'groupname':
        machines = map(lambda x: x.name, DyngroupDatabase().getMachines(ctx, {'gname':value}))
    return [machines, True]

def getAllGroupName(ctx, value = ''):
    return map(lambda x:x.name, DyngroupDatabase().getallgroups(ctx, {'filter':value}))
