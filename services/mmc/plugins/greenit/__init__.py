# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# file mmc/plugins/greenit/__init__.py

"""
Plugin to manage the interface with Greenit
"""
import logging
import uuid
import os
import base64
import re

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

from mmc.support.config import PluginConfigFactory
from mmc.plugins.greenit.config import GreenitConfig


# Database
from pulse2.database.greenit import GreenitDatabase
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
from distutils.version import LooseVersion, StrictVersion

VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################


def getApiVersion():
    return APIVERSION


def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    logger = logging.getLogger()
    config = GreenitConfig("greenit")

    if config.disable:
        logger.warning("Plugin greenit: disabled by configuration.")
        return False

    if not GreenitDatabase().activate(config):
        logger.warning(
            "Plugin greenit: an error occurred during the database initialization"
        )
        return False
    return True


# #############################################################
# GREENIT DATABASE FUNCTIONS
# #############################################################

def getTests():
    return GreenitDatabase().getTests()


def getDatasyear( annee=None):
    return GreenitDatabase().getDatasyear(annee=annee)

