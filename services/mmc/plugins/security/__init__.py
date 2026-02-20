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
    """Get summary for dashboard display, filtered by entity and policies"""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    return SecurityDatabase().get_dashboard_summary(
        location=location,
        min_cvss=cfg.display_min_cvss,
        min_severity=cfg.display_min_severity,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )


# =============================================================================
# CVE List
# =============================================================================
def get_cves(start=0, limit=50, filter_str='', severity=None, location='',
             sort_by='cvss_score', sort_order='desc'):
    """Get paginated list of CVEs, filtered by entity and local policies"""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    # Use min_severity from config if no explicit severity filter requested
    effective_severity = severity if severity else cfg.display_min_severity

    result = SecurityDatabase().get_cves(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        severity=effective_severity,
        location=location,
        sort_by=sort_by,
        sort_order=sort_order,
        min_cvss=cfg.display_min_cvss,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )

    # Apply local policies filtering (for exclusions, etc.)
    if result.get('data'):
        filtered_data = [cve for cve in result['data'] if cfg.should_display_cve(cve)]
        result['data'] = filtered_data

    return result


def get_cve_details(cve_id, location=''):
    """Get details of a CVE including affected machines, filtered by entity"""
    return SecurityDatabase().get_cve_details(cve_id, location=location)


# =============================================================================
# Machine-centric view
# =============================================================================
def get_machines_summary(start=0, limit=50, filter_str='', location=''):
    """Get list of machines with CVE counts, filtered by entity and policies"""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    return SecurityDatabase().get_machines_summary(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        location=location,
        min_cvss=cfg.display_min_cvss,
        min_severity=cfg.display_min_severity,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )


def get_machine_cves(id_glpi, start=0, limit=50, filter_str='', severity=None):
    """Get all CVEs affecting a specific machine with pagination and filtering."""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    result = SecurityDatabase().get_machine_cves(
        int(id_glpi),
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        severity=severity,
        min_cvss=cfg.display_min_cvss,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )

    # Apply local policies filtering
    if result.get('data'):
        filtered_data = [cve for cve in result['data'] if cfg.should_display_cve(cve)]
        result['data'] = filtered_data

    return result


def get_machine_softwares_summary(id_glpi, start=0, limit=50, filter_str=''):
    """Get vulnerable software summary for a machine, grouped by software."""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    return SecurityDatabase().get_machine_softwares_summary(
        int(id_glpi),
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        min_cvss=cfg.display_min_cvss,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )


def scan_machine(id_glpi):
    """Scan a specific machine (triggers full scan)"""
    from mmc.plugins.security.scanner import scan_single_machine
    # Get machine hostname for logging
    try:
        from sqlalchemy import text
        from mmc.plugins.security.scanner import get_glpi_db_url, create_engine
        engine = create_engine(get_glpi_db_url())
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM glpi_computers WHERE id = :id"), {'id': int(id_glpi)})
            row = result.fetchone()
            hostname = row[0] if row else f"ID:{id_glpi}"
    except Exception:
        hostname = f"ID:{id_glpi}"
    logger.info(f"Starting CVE scan for machine '{hostname}' (id_glpi={id_glpi})")
    result = scan_single_machine(int(id_glpi))
    if result.get('success'):
        logger.info(f"CVE scan completed for '{hostname}': {result.get('vulnerabilities_found', 0)} vulnerabilities found")
    else:
        logger.error(f"CVE scan failed for '{hostname}': {result.get('error', 'Unknown error')}")
    return result


# =============================================================================
# Scans
# =============================================================================
def get_scans(start=0, limit=20):
    """Get scan history"""
    return SecurityDatabase().get_scans(int(start), int(limit))


def create_scan():
    """Create a new scan and start it asynchronously"""
    from mmc.plugins.security.scanner import run_scan_async
    logger.info("Starting global CVE scan (all machines)")
    scan_id = run_scan_async()
    logger.info(f"Global CVE scan started with ID: {scan_id}")
    return scan_id


def _create_targeted_scan(target_type, target_id):
    """Internal helper for creating scoped scans (entity or group).

    Args:
        target_type: 'entity' or 'group'
        target_id: ID of the entity or group to scan

    Returns:
        scan_id: The ID of the created scan
    """
    from mmc.plugins.security.scanner import run_cve_scan, get_glpi_db_url
    from pulse2.database.security import SecurityDatabase
    from threading import Thread
    from sqlalchemy import text, create_engine

    target_id = int(target_id)

    # Get target name for logging
    queries = {
        'entity': "SELECT name FROM glpi_entities WHERE id = :id",
        'group': "SELECT name FROM dyngroup.Groups WHERE id = :id"
    }
    try:
        engine = create_engine(get_glpi_db_url())
        with engine.connect() as conn:
            result = conn.execute(text(queries[target_type]), {'id': target_id})
            row = result.fetchone()
            target_name = row[0] if row else f"ID:{target_id}"
    except Exception:
        target_name = f"ID:{target_id}"

    # Start scan in background thread
    scan_id = SecurityDatabase().create_scan()
    entity_id = target_id if target_type == 'entity' else None
    group_id = target_id if target_type == 'group' else None
    thread = Thread(target=run_cve_scan, args=(scan_id, entity_id, group_id), daemon=True)
    thread.start()

    logger.info(f"Started CVE scan for {target_type} '{target_name}' ({target_type}_id={target_id}) with scan ID: {scan_id}")
    return scan_id


def create_scan_entity(entity_id):
    """Create a new scan for a specific entity and start it asynchronously"""
    return _create_targeted_scan('entity', entity_id)


def create_scan_group(group_id):
    """Create a new scan for a specific group and start it asynchronously"""
    return _create_targeted_scan('group', group_id)


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


def get_policies():
    """Get current policies (merged from DB + ini files).

    Returns effective policies after DB overrides are applied.
    Always reloads from DB to get fresh values.
    """
    from mmc.plugins.security.config import SecurityConfig
    config = SecurityConfig("security")

    # Force reload from DB to get fresh values
    config._db_policies_loaded = False
    config._ensure_db_policies_loaded()

    return {
        'display': config.get_display_policies(),
        'exclusions': config.get_exclusion_policies()
    }


def get_policies_raw():
    """Get raw policies from database only (for editing UI).

    Returns only values stored in DB, not merged with ini defaults.
    """
    return SecurityDatabase().get_all_policies()


def set_policies(policies, user=None):
    """Set policies in database.

    Args:
        policies: dict like {
            'display': {'min_cvss': 4.0, 'min_severity': 'High'},
            'exclusions': {'cve_ids': ['CVE-2024-1234']}
        }
        user: username making the change

    Returns:
        bool: True on success
    """
    result = SecurityDatabase().set_policies_bulk(policies, user)
    if result:
        # Reload config to reflect new policies
        from mmc.plugins.security.config import SecurityConfig
        SecurityConfig("security").reload_policies()
    return result


def set_policies_json(policies_json, user=None):
    """Set policies in database from JSON string.

    This function is used by PHP XMLRPC to avoid nested array issues.

    Args:
        policies_json: JSON string of policies dict
        user: username making the change

    Returns:
        bool: True on success
    """
    import json
    try:
        policies = json.loads(policies_json)
        logger.debug(f"set_policies_json received: {policies}")
        result = SecurityDatabase().set_policies_bulk(policies, user)
        if result:
            # Reload config to reflect new policies
            from mmc.plugins.security.config import SecurityConfig
            SecurityConfig("security").reload_policies()
        return result
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in set_policies_json: {e}")
        return False


def set_policy(category, key, value, user=None):
    """Set a single policy value.

    Args:
        category: 'display' or 'exclusions'
        key: policy key (e.g., 'min_cvss', 'vendors')
        value: the value to set
        user: username making the change

    Returns:
        bool: True on success
    """
    result = SecurityDatabase().set_policy(category, key, value, user)
    if result:
        # Reload config to reflect new policies
        from mmc.plugins.security.config import SecurityConfig
        SecurityConfig("security").reload_policies()
    return result


def reset_policies(user=None):
    """Reset all policies to default values.

    Deletes all existing policies and reinserts the default values
    matching schema-001.sql.

    Args:
        user: username making the change (optional)

    Returns:
        bool: True on success
    """
    result = SecurityDatabase().reset_all_policies(user=user)
    if result:
        # Reload config to reflect new policies
        from mmc.plugins.security.config import SecurityConfig
        SecurityConfig("security").reload_policies()
    return result


def reset_display_policies(user=None):
    """Reset only display policies to default values, keeping exclusions intact.

    Args:
        user: username making the change (optional)

    Returns:
        bool: True on success
    """
    result = SecurityDatabase().reset_display_policies(user=user)
    if result:
        # Reload config to reflect new policies
        from mmc.plugins.security.config import SecurityConfig
        SecurityConfig("security").reload_policies()
    return result


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
    """Get list of softwares with CVE counts, filtered by entity and policies"""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    return SecurityDatabase().get_softwares_summary(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        location=location,
        min_cvss=cfg.display_min_cvss,
        min_severity=cfg.display_min_severity,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )


def get_software_cves(software_name, software_version, start=0, limit=50,
                      filter_str='', severity=None):
    """Get all CVEs affecting a specific software version"""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    result = SecurityDatabase().get_software_cves(
        software_name=software_name,
        software_version=software_version,
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        severity=severity,
        min_cvss=cfg.display_min_cvss
    )

    # Apply local policies filtering
    if result.get('data'):
        filtered_data = [cve for cve in result['data'] if cfg.should_display_cve(cve)]
        result['data'] = filtered_data

    return result


# =============================================================================
# Entity-centric view
# =============================================================================
def get_entities_summary(start=0, limit=50, filter_str='', user_entities=''):
    """Get list of entities with CVE counts, filtered by user's accessible entities"""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    return SecurityDatabase().get_entities_summary(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        user_entities=user_entities,
        min_cvss=cfg.display_min_cvss,
        min_severity=cfg.display_min_severity,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )


# =============================================================================
# Group-centric view
# =============================================================================
def get_groups_summary(start=0, limit=50, filter_str='', user_login=''):
    """Get list of groups with CVE counts, filtered by ShareGroup for this user"""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    return SecurityDatabase().get_groups_summary(
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        user_login=user_login,
        min_cvss=cfg.display_min_cvss,
        min_severity=cfg.display_min_severity,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )


def get_group_machines(group_id, start=0, limit=50, filter_str=''):
    """Get machines in a group with CVE counts"""
    from mmc.plugins.security.config import SecurityConfig
    cfg = SecurityConfig("security")

    return SecurityDatabase().get_group_machines(
        group_id=int(group_id),
        start=int(start),
        limit=int(limit),
        filter_str=filter_str,
        min_cvss=cfg.display_min_cvss,
        min_severity=cfg.display_min_severity,
        excluded_vendors=cfg.excluded_vendors,
        excluded_names=cfg.excluded_names,
        excluded_cve_ids=cfg.excluded_cve_ids,
        excluded_machines_ids=cfg.excluded_machines_ids,
        excluded_groups_ids=cfg.excluded_groups_ids
    )


# =============================================================================
# Group creation helpers
# =============================================================================
def get_machines_by_severity(severity, location=''):
    """Get list of machine UUIDs affected by CVEs of a given severity.

    Args:
        severity: CVE severity level (Critical, High, Medium, Low)
        location: Entity filter (optional)

    Returns:
        List of machine UUIDs in format 'UUID<id>'
    """
    return SecurityDatabase().get_machines_by_severity(severity, location)


# =============================================================================
# Store integration - Deploy updates for vulnerable software
# =============================================================================
def get_store_software_info(software_name):
    """Get store information for a specific software.

    Args:
        software_name: Name of the software (e.g., "Python")

    Returns:
        dict with store info or None if not found
    """
    return SecurityDatabase().get_store_software_info(software_name)


def get_machines_for_vulnerable_software(software_name, software_version,
                                          location='', start=0, limit=100, filter_str=''):
    """Get machines that have a specific vulnerable software installed.

    Args:
        software_name: Normalized software name (e.g., "Python")
        software_version: Vulnerable version (e.g., "3.11.9")
        location: Entity filter (comma-separated entity IDs)
        start: Pagination offset
        limit: Pagination limit
        filter_str: Search filter on hostname

    Returns:
        dict with 'total' count and 'data' list of machines
    """
    return SecurityDatabase().get_machines_for_vulnerable_software(
        software_name=software_name,
        software_version=software_version,
        location=location,
        start=int(start),
        limit=int(limit),
        filter_str=filter_str
    )
