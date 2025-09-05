# -*- coding: utf-8; -*-
from pulse2.version import getVersion, getRevision
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.mobile.config import MobileConfig
from pulse2.database.mobile import MobileDatabase
import logging
import requests
import hashlib
import json


VERSION = "1.0.0"
APIVERSION = "1:0:0"
logger = logging.getLogger()
db = MobileDatabase()

def getApiVersion():
    return APIVERSION

def activate():
    
    config = MobileConfig("mobile")
    if config.disable:
        logger.warning("Plugin %s: disabled by configuration." % "mobile")
        return False
 
    if not MobileDatabase().activate(config):
        logger.warning(
            "Plugin %s: an error occurred during the database initialization" % "mobile")
        return False
    return True

# def tests():
#     return db.tests()

def nano_devices():
    return db.devices()

def to_back(name, desc):
    logging.getLogger().error(f"111 - Voila ma variable name quand je suis dans plugins {name}")
    logging.getLogger().error(f"222 - Voila ma variable quand je suis dans plugins desc {desc}")

    return MobileDatabase().givenNameDesc(name, desc)

def getDevice():
    
    return db.getDevices()







