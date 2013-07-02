# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
Plugin to manage the interface with BackupPC
"""
import logging

from mmc.plugins.backuppc.config import BackuppcConfig
from mmc.plugins.backuppc import bpc
#from mmc.agent import PluginManager
#from mmc.support.mmctools import ContextMakerI, SecurityContext
from pulse2.version import getVersion, getRevision # pyflakes.ignore

# Database
from pulse2.database.backuppc import BackuppcDatabase


VERSION = "2.0.0"
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
    config = BackuppcConfig("backuppc")
    if config.disable:
        logger.warning("Plugin backuppc: disabled by configuration.")
        return False
    if not BackuppcDatabase().activate(config):
        logger.warning("Plugin backuppc: an error occurred during the database initialization")
        return False
    return True


# #############################################################
# BACKUPPC MAIN FUNCTIONS [HTTP INTERFACE]
# #############################################################

def get_host_list(pattern):
    return bpc.get_host_list(pattern)

def get_backup_list(host):
    return bpc.get_backup_list(host)

def get_share_names(host,backup_num):
    return bpc.get_share_names(host,backup_num)

def list_files(host,backup_num,share_name,dir,filter):
    return bpc.list_files(host,backup_num,share_name,dir,filter)

def get_file_versions(host,share_name,filepath):
    return bpc.get_file_versions(host,share_name,filepath)

def get_download_status():
    return bpc.get_download_status()
    
def restore_file(host,backup_num,share_name,restore_path):
    return bpc.restore_file(host,backup_num,share_name,restore_path)

def restore_files_to_host(host,backup_num,share_name,files,hostDest,shareDest,pathHdr):
    return bpc.restore_files_to_host(host,backup_num,share_name,files,hostDest,shareDest,pathHdr)

def get_host_config(host):
    return bpc.get_host_config(host)

def set_host_config(host,config):
    return bpc.set_host_config(host,config)


# #############################################################
# DATABASE QUERY FUNCTIONS
# #############################################################

# BACKUP PROFILES

def get_backup_profiles():
    return BackuppcDatabase().get_backup_profiles()
    
def add_backup_profile(profile):
    return BackuppcDatabase().add_backup_profile(profile)
    
def delete_backup_profile(id):
    return BackuppcDatabase().delete_backup_profile(id)
    
def edit_backup_profile(id,override):
    return BackuppcDatabase().edit_backup_profile(id,override)
    
def get_host_backup_profile(uuid):
    return BackuppcDatabase().get_host_backup_profile(uuid)
    
def set_host_backup_profile(uuid,newprofile):
    return BackuppcDatabase().set_host_backup_profile(uuid,newprofile)


# PERIOD PROFILES

def get_period_profiles():
    return BackuppcDatabase().get_period_profiles()
    
def add_period_profile(profile):
    return BackuppcDatabase().add_period_profile(profile)
    
def delete_period_profile(id):
    return BackuppcDatabase().delete_period_profile(id)
    
def edit_period_profile(id,override):
    return BackuppcDatabase().edit_period_profile(id,override)
    
def get_host_period_profile(uuid):
    return BackuppcDatabase().get_host_period_profile(uuid)
    
def set_host_period_profile(uuid,newprofile):
    return BackuppcDatabase().set_host_period_profile(uuid,newprofile)

# Apply profiles to hosts

def apply_backup_profile(profileid):
    return bpc.apply_backup_profile(profileid)

def apply_period_profile(profileid):
    return bpc.apply_period_profile(profileid)


# Backup commands functions

def start_full_backup(host):
    return bpc.start_full_backup(host)

def start_incr_backup(host):
    return bpc.start_incr_backup(host)

def stop_backup(host,backoff):
    return bpc.stop_backup(host,backoff)

# Host status

def get_host_status(host):
    return bpc.get_host_status(host)


def set_backup_for_host(uuid):
    return bpc.set_backup_for_host(uuid)

def get_xfer_log(host,backupnum):
    return bpc.get_xfer_log(host,backupnum)

# Function to associate entities to backup servers
# To be used by external script
# TODO : remove this

def get_backupservers_list():
    return BackuppcDatabase().get_backupservers_list()

def add_backupserver(entityuuid,serverURL):
    return BackuppcDatabase().add_backupserver(entityuuid,serverURL)

# Global status

def get_global_status(entity_uuid):
    return bpc.get_global_status(entity_uuid)

def host_exists(uuid):
    return BackuppcDatabase().host_exists(uuid)