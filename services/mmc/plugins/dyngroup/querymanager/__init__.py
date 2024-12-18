# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

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
    ret["groupname"] = ["list", getAllGroupName]
    return ret


def queryGroups():
    # Assign criterions to categories
    ret = []
    #
    ret.append(["Group", [["groupname", ""]]])
    #
    return ret


def extendedPossibilities():
    return {}


def query(ctx, criterion, value):
    logging.getLogger().info(ctx)
    logging.getLogger().info(criterion)
    logging.getLogger().info(value)
    machines = []
    if criterion == "groupname":
        machines = [
            x.name for x in DyngroupDatabase().getMachines(ctx, {"gname": value})
        ]
    return [machines, True]


def getAllGroupName(ctx, value=""):
    return [x.name for x in DyngroupDatabase().getallgroups(ctx, {"filter": value})]
