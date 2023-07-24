# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

from mmc.plugins.admin.config import AdminConfig

# import pour la database
from pulse2.database.admin import AdminDatabase
import logging

VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################


def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = AdminConfig("admin")

    if config.disable:
        logger.warning("Plugin admin: disabled by configuration.")
        return False

    if not AdminDatabase().activate(config):
        logger.warning(
            "Plugin admin: an error occurred during the database initialization"
        )
        return False
    return True
