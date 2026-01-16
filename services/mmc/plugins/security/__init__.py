# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from pulse2.version import getVersion, getRevision
from mmc.support.config import PluginConfig, PluginConfigFactory
from mmc.plugins.security.config import SecurityConfig
from pulse2.database.security import SecurityDatabase
import logging

VERSION = "1.0.0"
APIVERSION = "1:0:0"
logger = logging.getLogger()

# Global config instance (initialized in activate())
config = None


def getApiVersion():
    return APIVERSION


def activate():
    global config
    logger = logging.getLogger()
    config = SecurityConfig("security")
    if config.disable:
        logger.warning("Plugin security: disabled by configuration.")
        return False
    if not SecurityDatabase().activate(config):
        logger.warning(
            "Plugin security: an error occurred during the database initialization")
        return False
    logger.info("Plugin security: activated successfully")
    return True


# =============================================================================
# Legacy test function
# =============================================================================
def tests():
    return SecurityDatabase().tests()


# =============================================================================
# Dashboard
# =============================================================================
def get_dashboard_summary(location=''):
    """Get summary for dashboard display, filtered by entity"""
    return SecurityDatabase().get_dashboard_summary(location=location)


# =============================================================================
# CVE List
# =============================================================================
def get_cves(start=0, limit=50, filter_str='', severity=None, location='',
             sort_by='cvss_score', sort_order='desc'):
    """Get paginated list of CVEs, filtered by entity"""
    return SecurityDatabase().get_cves(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        severity=severity,
        location=location,
        sort_by=sort_by,
        sort_order=sort_order
    )


def get_cve_details(cve_id, location=''):
    """Get details of a CVE including affected machines, filtered by entity"""
    return SecurityDatabase().get_cve_details(cve_id, location=location)


# =============================================================================
# Machine-centric view
# =============================================================================
def get_machines_summary(start=0, limit=50, filter_str='', location=''):
    """Get list of machines with CVE counts, filtered by entity"""
    return SecurityDatabase().get_machines_summary(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        location=location
    )


def get_machine_cves(id_glpi, start=0, limit=50, filter_str='', severity=None):
    """Get all CVEs affecting a specific machine with pagination and filtering."""
    return SecurityDatabase().get_machine_cves(
        int(id_glpi),
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        severity=severity
    )


def scan_machine(id_glpi):
    """Scan a specific machine (triggers full scan)"""
    from mmc.plugins.security.scanner import scan_single_machine
    return scan_single_machine(int(id_glpi))


# =============================================================================
# Scans
# =============================================================================
def get_scans(start=0, limit=20):
    """Get scan history"""
    return SecurityDatabase().get_scans(int(start), int(limit))


def create_scan():
    """Create a new scan and start it asynchronously"""
    from mmc.plugins.security.scanner import run_scan_async
    return run_scan_async()


def create_scan_entity(entity_id):
    """Create a new scan for a specific entity and start it asynchronously"""
    from mmc.plugins.security.scanner import run_cve_scan
    from pulse2.database.security import SecurityDatabase
    from threading import Thread

    scan_id = SecurityDatabase().create_scan()
    thread = Thread(target=run_cve_scan, args=(scan_id, int(entity_id), None), daemon=True)
    thread.start()

    logger.info(f"Started async CVE scan for entity {entity_id} with ID: {scan_id}")
    return scan_id


def create_scan_group(group_id):
    """Create a new scan for a specific group and start it asynchronously"""
    from mmc.plugins.security.scanner import run_cve_scan
    from pulse2.database.security import SecurityDatabase
    from threading import Thread

    scan_id = SecurityDatabase().create_scan()
    thread = Thread(target=run_cve_scan, args=(scan_id, None, int(group_id)), daemon=True)
    thread.start()

    logger.info(f"Started async CVE scan for group {group_id} with ID: {scan_id}")
    return scan_id


def run_scan_sync():
    """Run a CVE scan synchronously (blocking)"""
    from mmc.plugins.security.scanner import run_cve_scan
    return run_cve_scan()


# =============================================================================
# Configuration
# =============================================================================
def get_config(key=None):
    """Get scanner configuration from ini file"""
    from mmc.plugins.security.config import SecurityConfig
    config = SecurityConfig("security")

    config_dict = {
        'cve_central_url': config.cve_central_url,
        'cve_central_server_id': config.cve_central_server_id,
        'cve_central_configured': config.is_cve_central_configured(),
    }

    if key:
        return config_dict.get(key, '')
    return config_dict


def set_config(key, value):
    """
    Configuration is read-only from ini file.
    To change configuration, edit /etc/mmc/plugins/security.ini.local
    """
    logger.warning(f"set_config called for {key} but config is read-only from ini file")
    return False


# =============================================================================
# Exclusions
# =============================================================================
def get_exclusions():
    """Get list of excluded CVEs"""
    return SecurityDatabase().get_exclusions()


def add_exclusion(cve_id, reason, user, expires_at=None):
    """Add a CVE to exclusion list"""
    return SecurityDatabase().add_exclusion(cve_id, reason, user, expires_at)


def remove_exclusion(cve_id):
    """Remove a CVE from exclusion list"""
    return SecurityDatabase().remove_exclusion(cve_id)


def is_excluded(cve_id):
    """Check if a CVE is excluded"""
    return SecurityDatabase().is_excluded(cve_id)


# =============================================================================
# Software-centric view
# =============================================================================
def get_softwares_summary(start=0, limit=50, filter_str='', location=''):
    """Get list of softwares with CVE counts, filtered by entity"""
    return SecurityDatabase().get_softwares_summary(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        location=location
    )


def get_software_cves(software_name, software_version, start=0, limit=50,
                      filter_str='', severity=None):
    """Get all CVEs affecting a specific software version"""
    return SecurityDatabase().get_software_cves(
        software_name=software_name,
        software_version=software_version,
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        severity=severity
    )


# =============================================================================
# Entity-centric view
# =============================================================================
def get_entities_summary(start=0, limit=50, filter_str='', user_entities=''):
    """Get list of entities with CVE counts, filtered by user's accessible entities"""
    return SecurityDatabase().get_entities_summary(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        user_entities=user_entities
    )


# =============================================================================
# Group-centric view
# =============================================================================
def get_groups_summary(start=0, limit=50, filter_str='', user_login=''):
    """Get list of groups with CVE counts, filtered by ShareGroup for this user"""
    return SecurityDatabase().get_groups_summary(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        user_login=user_login
    )


def get_group_machines(group_id, start=0, limit=50, filter_str=''):
    """Get machines in a group with CVE counts"""
    return SecurityDatabase().get_group_machines(
        group_id=int(group_id),
        start=int(start),
        limit=int(limit),
        filter_str=filter_str
    )
