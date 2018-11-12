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
xmppmaster querymanager
give informations to the dyngroup plugin to be able to build dyngroups
on glpi and xmppmaster informations
"""

import logging
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.config import GlpiQueryManagerConfig

from pulse2.utils import unique


from pulse2.database.xmppmaster import XmppMasterDatabase

#from mmc.plugins.xmppmaster.config import xmppMasterConfig


def activate():
    conf = GlpiQueryManagerConfig("glpi")
    return conf.activate


def queryPossibilities():
    ret = {}
    ret['OU user'] = ['list', getAllOuuser]
    ret['OU Machine'] = ['list', getAllOumachine]
    logging.getLogger().info('queryPossibilities %s' %
                             (str(ret)))
    return ret


def queryGroups():
    # jfkjfk
    # Assign criterions to categories
    ret = []
    # Identification cat
    ret.append(['ActifDirectory',
                [['OU user', 'ex OU User'],
                 ['OU Machine', 'ex OU Machine']
                 ]])
    return ret


def extendedPossibilities():
    """
    xmpp plugin has no extended possibilities
    """
    return {}


def query(ctx, criterion, value):
    logging.getLogger().info(ctx)
    logging.getLogger().info(criterion)
    logging.getLogger().info(value)
    machines = []

    if criterion == 'OU user':
        machines = [x.name for x in Glpi().getMachineByHostname(ctx, value)]
    elif criterion == 'OU Machine':
        machines = [x.name for x in Glpi().getMachineByContact(ctx, value)]
    return [machines, True]


def getAllOuuser(ctx, value=''):
    return unique([x.ouuser for x in XmppMasterDatabase().getAllOUuser(ctx, value)])


def getAllOumachine(ctx, value=''):
    return unique([x.oumachine for x in XmppMasterDatabase().getAllOUmachine(ctx, value)])
