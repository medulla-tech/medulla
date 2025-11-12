# -*- coding:Utf-8; -*
# SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

# File : mmc/plugins/mastering/__init__.py

from pulse2.version import getVersion, getRevision # pyflakes.ignore
# Au cas où on souhaite appeler des configs d'autres modules
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.mastering.config import MasteringConfig

# import pour la database
from pulse2.database.mastering import MasteringDatabase
import logging

VERSION = "1.0.0"
APIVERSION = "1:0:0"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################

def getApiVersion():
    return APIVERSION


def activate():
    logger = logging.getLogger()
    config = MasteringConfig("mastering")

    if config.disable:
        logger.warning("Plugin mastering: disabled by configuration.")
        return False

    if not MasteringDatabase().activate(config):
        logger.warning("Plugin mastering: an error occurred during the database initialization")
        return False
    return True

