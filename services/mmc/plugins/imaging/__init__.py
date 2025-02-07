# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Class to manage imaging mmc-agent api
imaging plugin
"""

import logging

from mmc.agent import PluginManager
from mmc.support.mmctools import ContextMakerI, SecurityContext
from mmc.plugins.imaging.config import ImagingConfig
from mmc.plugins.imaging.profile import ImagingProfile
from mmc.plugins.imaging.computer import InventoryComputers
from mmc.plugins.imaging.imaging import ComputerImagingImaging
from mmc.plugins.imaging.pulse import ImagingPulse2Manager
from mmc.plugins.imaging.functions import ImagingRpcProxy, computersUnregister
from mmc.core.tasks import TaskManager
from pulse2.managers.profile import ComputerProfileManager
from mmc.plugins.base.computers import ComputerManager
from pulse2.managers.imaging import ComputerImagingManager
from pulse2.managers.pulse import Pulse2Manager
from pulse2.database.imaging import ImagingDatabase

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

APIVERSION = "0:0:0"

NOAUTHNEEDED = [
    "computerRegister",
    "imagingServerRegister",
    "getGeneratedMenu",
    "isImagingServerRegistered",
    "getComputerByMac",
    "getMachineByUuidSetup",
    "imageRegister",
    "imageUpdate",
    "logClientAction",
    "injectInventory",
    "injectInventoryUuid",
    "getDefaultMenuForRegistering",
    "getPXEParams",
    "linkImagingServerToLocation",
    "computerChangeDefaultMenuItem",
    "synchroComputer",
    "getDefaultMenuItem",
    "getClonezillaParamsForTarget",
    "getPostInstalls"
]


def getApiVersion():
    return APIVERSION


def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    logger = logging.getLogger()
    config = ImagingConfig("imaging")

    if config.disabled:
        logger.warning("Plugin imaging: disabled by configuration.")
        return False

    # Initialize imaging database
    if not ImagingDatabase().activate(config):
        logger.warning(
            "Plugin imaging: an error occurred during the database initialization"
        )
        return False

    # register ImagingProfile in ComputerProfileManager but only as a client
    ComputerProfileManager().register("imaging", ImagingProfile)

    ComputerImagingManager().register("imaging", ComputerImagingImaging)

    Pulse2Manager().register("imaging", ImagingPulse2Manager)

    ComputerManager().register("imaging", InventoryComputers)

    TaskManager().addTask(
        "imaging.purge_removed_computers",
        (purge_removed_computers,),
        cron_expression=config.purge_interval,
    )

    return True


def activate_2():
    """
    Check that the MMC pulse2 plugin is enabled
    """
    if not PluginManager().isEnabled("medulla_server"):
        ret = False
        logging.getLogger().error(
            "Plugin imaging: plugin is disabled because the pulse2 plugin is not available"
        )
    else:
        ret = True
    return ret


def purge_removed_computers():
    from mmc.plugins.base.computers import ComputerManager
    from mmc.plugins.base import LdapUserGroupControl

    # Get all imaging targets
    targets = ImagingDatabase().getAllRegisteredComputers()

    # Creating root context to query ComputerManager
    ctx = SecurityContext()
    ctx.userid = "root"
    ctx.userdn = LdapUserGroupControl().searchUserDN(ctx.userid)

    # Init to_delete computer list
    to_delete = []

    for uuid in targets:
        if ComputerManager().getComputerCount(ctx, {"uuid": uuid}) == 0:
            # If the target computer is not in ComputerManager database anymore
            # we unregister it from imaging
            to_delete.append(uuid)

    # Unregistering orphan targets without backup
    if to_delete:
        logging.getLogger().info("Orphan imaging computer(s) found")
        logging.getLogger().info("Going to purge %s" % " ".join(to_delete))
        computersUnregister(to_delete, False)

    return True


class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s


class RpcProxy(ImagingRpcProxy):
    pass
