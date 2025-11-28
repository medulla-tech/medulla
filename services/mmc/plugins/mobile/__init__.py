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

def getHmdmDevices():
    return MobileDatabase().getHmdmDevices()

def getHmdmConfigurationById(id):
    return MobileDatabase().getHmdmConfigurationById(id)

def deleteHmdmDeviceById(id):
    return MobileDatabase().deleteHmdmDeviceById(id)

def getHmdmApplications():
    return MobileDatabase().getHmdmApplications()

def deleteApplicationById(id):
    return MobileDatabase().deleteApplicationById(id)

def getHmdmConfigurations():
    return MobileDatabase().getHmdmConfigurations()

def getHmdmFiles():
    return MobileDatabase().getHmdmFiles()

def deleteFileById(id=None, filePath=None):
    return MobileDatabase().deleteFileById(file_id=id, filePath=filePath)

def deleteConfigurationById(id):
    return MobileDatabase().deleteConfigurationById(id)

def getHmdmAuditLogs(page_size=50, page_num=1, message_filter="", user_filter=""):
    return MobileDatabase().getHmdmAuditLogs(page_size, page_num, message_filter, user_filter)

def getHmdmDetailedInfo(device_number):
    return MobileDatabase().getHmdmDetailedInfo(device_number)

def searchHmdmDevices(filter_text=""):
    return MobileDatabase().searchHmdmDevices(filter_text)

def getHmdmMessages(device_number="", message_filter="", status_filter="",
                date_from_millis=None, date_to_millis=None, page_size=50, page_num=1):
    return MobileDatabase().getHmdmMessages(device_number, message_filter, status_filter,
                                        date_from_millis, date_to_millis, page_size, page_num)

def getHmdmPushMessages(device_number="", message_filter="", status_filter="",
                date_from_millis=None, date_to_millis=None, page_size=50, page_num=1):
    return MobileDatabase().getHmdmPushMessages(device_number, message_filter, status_filter,
                                        date_from_millis, date_to_millis, page_size, page_num)