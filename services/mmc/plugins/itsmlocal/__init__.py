# file : services/mmc/plugins/itsmlocal/__init__.py

"""Plugin backend for the Medulla itsmlocal database."""

import logging

from mmc.plugins.itsmlocal.config import ItsmlocalConfig
from pulse2.database.itsmlocal import ItsmlocalDatabase

logger = logging.getLogger()
VERSION = "1.0.0"
APIVERSION = "1:0:0"


def getApiVersion():
    """Return the backend API version."""
    return APIVERSION


def getVersion():
    """Return the plugin version required by the MMC plugin loader."""
    return VERSION


def activate():
    """Activate itsmlocal when explicitly enabled in its configuration."""
    config = ItsmlocalConfig("itsmlocal")
    if config.disable:
        logger.info("Plugin itsmlocal is disabled by configuration")
        return False
    return ItsmlocalDatabase().activate(config)
