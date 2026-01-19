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

def addHmdmDevice(name, configuration_id, description="", groups=None, imei="", phone="", device_id=None):
    return MobileDatabase().addHmdmDevice(name, configuration_id, description, groups, imei, phone, device_id)

def getHmdmDevices():
    return MobileDatabase().getHmdmDevices()

def getHmdmConfigurationById(id):
    return MobileDatabase().getHmdmConfigurationById(id)

def updateHmdmConfiguration(config_data):
    return MobileDatabase().updateHmdmConfiguration(config_data)

def deleteHmdmDeviceById(id):
    return MobileDatabase().deleteHmdmDeviceById(id)

def getHmdmApplications():
    return MobileDatabase().getHmdmApplications()

def getHmdmConfigurationApplications(id):
    return MobileDatabase().getHmdmConfigurationApplications(id)

def getHmdmIcons():
    return MobileDatabase().getHmdmIcons()

def addHmdmIcon(icon_data):
    return MobileDatabase().addHmdmIcon(icon_data)

def deleteHmdmIconsById(id):
    return MobileDatabase().deleteHmdmIconsById(id)

def deleteIconById(id):
    return MobileDatabase().deleteIconById(id)

def addHmdmApplication(app_data):
    return MobileDatabase().addHmdmApplication(app_data)

def deleteApplicationById(id):
    return MobileDatabase().deleteApplicationById(id)

def getApplicationVersions(app_id):
    return MobileDatabase().getApplicationVersions(app_id)

def getConfigurationNames():
    return MobileDatabase().getConfigurationNames()

def updateApplicationConfigurations(app_id, configuration_id, configuration_name=None):
    return MobileDatabase().updateApplicationConfigurations(app_id, configuration_id, configuration_name)

def getConfigurationNames():
    return MobileDatabase().getConfigurationNames()

def getHmdmConfigurations():
    return MobileDatabase().getHmdmConfigurations()

def getHmdmFiles():
    return MobileDatabase().getHmdmFiles()

def addHmdmFile(uploaded_file_path=None, uploaded_file_name=None, external_url=None, file_name=None, path_on_device=None, description=None, variable_content=None, configuration_ids=None):
    return MobileDatabase().addHmdmFile(uploaded_file_path, uploaded_file_name, external_url, file_name, path_on_device, description, variable_content, configuration_ids)

def updateHmdmFile(file_data):
    return MobileDatabase().updateHmdmFile(file_data)

def deleteFileById(file_data=None, file_id=None, filePath=None):
    return MobileDatabase().deleteFileById(file_data=file_data, file_id=file_id, filePath=filePath)

def assignFileToConfigurations(file_id, configuration_ids):
    return MobileDatabase().assignFileToConfigurations(file_id, configuration_ids)

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

def getHmdmGroups():
    return MobileDatabase().getHmdmGroups()

def addHmdmGroup(name, group_id=None, customer_id=None, common=None):
    return MobileDatabase().addHmdmGroup(name, group_id, customer_id, common)

def deleteHmdmGroupById(id):
    return MobileDatabase().deleteHmdmGroupById(id)

def sendHmdmMessage(scope, device_number="", group_id="", configuration_id="", message=""):
    return MobileDatabase().sendHmdmMessage(scope, device_number, group_id, configuration_id, message)

def sendHmdmPushMessage(scope, message_type="", payload="", device_number="", group_id="", configuration_id=""):
    return MobileDatabase().sendHmdmPushMessage(scope, message_type, payload, device_number, group_id, configuration_id)

def getHmdmDeviceLogs(device_number="", package_id="", severity="-1", page_size=50, page_num=1):
    return MobileDatabase().getHmdmDeviceLogs(device_number, package_id, severity, page_size, page_num)

def exportHmdmDeviceLogs(device_number="", app="", severity="-1"):
    return MobileDatabase().exportHmdmDeviceLogs(device_number, app, severity)

def searchHmdmAppPackages(filter_text=""):
    return MobileDatabase().searchHmdmAppPackages(filter_text)

def uploadWebUiFiles(uploaded_file_path=None, uploaded_file_name=None, mime_type=None):
    return MobileDatabase().uploadWebUiFiles(uploaded_file_path, uploaded_file_name, mime_type)