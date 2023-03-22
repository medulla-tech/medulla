# SPDX-FileCopyrightText: 2008 Mandriva
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

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
