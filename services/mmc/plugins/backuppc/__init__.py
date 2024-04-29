# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Plugin to manage the interface with BackupPC
"""
import logging

from mmc.plugins.backuppc.config import BackuppcConfig
from mmc.plugins.backuppc import bpc
from medulla.version import getVersion, getRevision  # pyflakes.ignore
from mmc.plugins.base import ComputerI
from mmc.plugins.base.computers import ComputerManager

# Database
from medulla.database.backuppc import BackuppcDatabase


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

    # Registering BackupComputers in ComputerManager
    ComputerManager().register("backuppc", BackupComputers)

    if config.disable:
        logger.warning("Plugin backuppc: disabled by configuration.")
        return False
    if not BackuppcDatabase().activate(config):
        logger.warning(
            "Plugin backuppc: an error occurred during the database initialization"
        )
        return False
    return True


# #############################################################
# BACKUPPC MAIN FUNCTIONS [HTTP INTERFACE]
# #############################################################


def get_host_list(pattern):
    return bpc.get_host_list(pattern)


def get_backup_list(host):
    return bpc.get_backup_list(host)


def get_share_names(host, backup_num):
    return bpc.get_share_names(host, backup_num)


def list_files(host, backup_num, share_name, dir, filter):
    return bpc.list_files(host, backup_num, share_name, dir, filter)


def get_file_versions(host, share_name, filepath):
    return bpc.get_file_versions(host, share_name, filepath)


def get_download_status():
    return bpc.get_download_status()


def restore_file(host, backup_num, share_name, restore_path):
    return bpc.restore_file(host, backup_num, share_name, restore_path)


def restore_files_to_host(
    host, backup_num, share_name, files, hostDest, shareDest, pathHdr
):
    return bpc.restore_files_to_host(
        host, backup_num, share_name, files, hostDest, shareDest, pathHdr
    )


def get_host_config(host):
    return bpc.get_host_config(host)


def set_host_config(host, config):
    return bpc.set_host_config(host, config)


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


def edit_backup_profile(id, override):
    return BackuppcDatabase().edit_backup_profile(id, override)


def get_host_backup_profile(uuid):
    return BackuppcDatabase().get_host_backup_profile(uuid)


def get_host_backup_reverse_port(uuid):
    return BackuppcDatabase().get_host_backup_reverse_port(uuid)


def set_host_backup_profile(uuid, newprofile):
    return bpc.set_host_backup_profile(uuid, newprofile)


def get_host_rsync_path(uuid):
    return bpc.get_host_rsync_path(uuid)


def get_all_hosts():
    """Return all the machines which are hosted in backuppc"""
    return BackuppcDatabase().get_all_hosts()


def get_count_of_backuped_hosts():
    """Return the number of machines which are hosted in backuppc"""
    return BackuppcDatabase().get_count_of_backuped_hosts()


# PERIOD PROFILES


def get_period_profiles():
    return BackuppcDatabase().get_period_profiles()


def add_period_profile(profile):
    return BackuppcDatabase().add_period_profile(profile)


def delete_period_profile(id):
    return BackuppcDatabase().delete_period_profile(id)


def edit_period_profile(id, override):
    return BackuppcDatabase().edit_period_profile(id, override)


def get_host_period_profile(uuid):
    return BackuppcDatabase().get_host_period_profile(uuid)


def set_host_period_profile(uuid, newprofile):
    return bpc.set_host_period_profile(uuid, newprofile)


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


def stop_backup(host, backoff):
    return bpc.stop_backup(host, backoff)


# Host status


def get_host_status(host):
    return bpc.get_host_status(host)


def set_backup_for_host(uuid):
    return bpc.set_backup_for_host(uuid)


def unset_backup_for_host(uuid):
    return bpc.unset_backup_for_host(uuid)


def get_xfer_log(host, backupnum):
    return bpc.get_xfer_log(host, backupnum)


def get_host_log(host):
    return bpc.get_host_log(host)


def get_backupservers_list():
    return BackuppcDatabase().get_backupservers_list()


def add_backupserver(entityuuid, serverURL):
    return BackuppcDatabase().add_backupserver(entityuuid, serverURL)


# Global status


def get_global_status(entity_uuid):
    return bpc.get_global_status(entity_uuid)


def get_backupserver_for_computer(uuid):
    return bpc.getBackupServerByUUID(uuid)


def host_exists(uuid):
    return BackuppcDatabase().host_exists(uuid)


def build_fileindex(host):
    return bpc.build_fileindex(host)


def file_search(
    host,
    backupnum_0,
    sharename_0,
    filename_0,
    filesize_min=-1,
    filesize_max=-1,
    type_0=" ",
):
    return bpc.file_search(
        host, backupnum_0, sharename_0, filename_0, filesize_min, filesize_max, type_0
    )


def calldb(func, *args, **kw):
    return getattr(BackuppcDatabase(), func).__call__(*args, **kw)


# Pre and post backup scripts


def get_host_pre_backup_script(uuid):
    return BackuppcDatabase().get_host_pre_backup_script(uuid)


def set_host_pre_backup_script(uuid, script):
    return BackuppcDatabase().set_host_pre_backup_script(uuid, script)


def get_host_post_backup_script(uuid):
    return BackuppcDatabase().get_host_post_backup_script(uuid)


def set_host_post_backup_script(uuid, script):
    return BackuppcDatabase().set_host_post_backup_script(uuid, script)


def get_host_pre_restore_script(uuid):
    return BackuppcDatabase().get_host_pre_restore_script(uuid)


def set_host_pre_restore_script(uuid, script):
    return BackuppcDatabase().set_host_pre_restore_script(uuid, script)


def get_host_post_restore_script(uuid):
    return BackuppcDatabase().get_host_post_restore_script(uuid)


def set_host_post_restore_script(uuid, script):
    return BackuppcDatabase().set_host_post_restore_script(uuid, script)


######################


class BackupComputers(ComputerI):
    def __init__(self, conffile=None):
        self.logger = logging.getLogger()

    def canDelComputer(self):
        return True

    def delComputer(self, ctx, uuid, backup):
        return bpc.unset_backup_for_host(uuid)
