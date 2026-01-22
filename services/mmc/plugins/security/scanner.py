# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
"""
CVE Scanner Module

This module scans software inventory from GLPI and uses the CVE Central API
to find CVE vulnerabilities. CVEs are stored locally and linked to software.
"""

import logging
from logging.handlers import RotatingFileHandler
import requests
import time
import configparser
from datetime import datetime
from typing import Optional, Dict, List, Any
from threading import Thread
from sqlalchemy import create_engine, text
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
import base64
import os

# Configure dedicated logger for CVE scanner
LOG_FILE = '/var/log/mmc/medulla-cve.log'
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 5

logger = logging.getLogger('medulla-cve')

def setup_logger(log_level='INFO'):
    """Configure the CVE scanner logger with the specified log level."""
    # Map string level to logging constant
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'WARN': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    level = level_map.get(log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Add handler if not already configured
    if not logger.handlers:
        try:
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=LOG_MAX_SIZE,
                backupCount=LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            logger.addHandler(file_handler)
        except (IOError, OSError) as e:
            # Fallback to default logger if file is not writable
            logging.getLogger().warning(f"Cannot create CVE log file {LOG_FILE}: {e}")

    # Update handler level if already exists
    for handler in logger.handlers:
        handler.setLevel(level)

# Initialize with default level (will be reconfigured when config is loaded)
setup_logger('INFO')


def get_glpi_db_url():
    """Read GLPI database configuration and return SQLAlchemy URL

    Reads /etc/mmc/plugins/glpi.ini first, then overrides with
    /etc/mmc/plugins/glpi.ini.local if it exists.
    """
    config = configparser.ConfigParser()
    # Read base config, then local overrides (local values take precedence)
    config.read(['/etc/mmc/plugins/glpi.ini', '/etc/mmc/plugins/glpi.ini.local'])

    dbhost = config.get('main', 'dbhost', fallback='localhost')
    dbport = config.get('main', 'dbport', fallback='3306')
    dbname = config.get('main', 'dbname', fallback='glpi')
    dbuser = config.get('main', 'dbuser', fallback='mmc')
    dbpasswd = config.get('main', 'dbpasswd', fallback='')

    return f"mysql+pymysql://{dbuser}:{dbpasswd}@{dbhost}:{dbport}/{dbname}"


def get_unique_software_from_glpi(entity_id=None, group_id=None, machine_id=None,
                                   excluded_patterns=None, excluded_vendors=None, excluded_names=None):
    """
    Get unique software list from GLPI (optionally filtered by entity, group or machine)

    Args:
        entity_id: Filter by entity ID (optional)
        group_id: Filter by group ID (optional)
        machine_id: Filter by machine GLPI ID (optional)
        excluded_patterns: List of patterns to exclude (substring match, case-insensitive)
        excluded_vendors: List of vendors to exclude (exact match, case-insensitive)
        excluded_names: List of exact names to exclude (case-sensitive)

    Returns:
        List of unique software dicts with name, version, vendor
    """
    # Use empty lists if not provided (exclusions come from config)
    if excluded_patterns is None:
        excluded_patterns = []
    if excluded_vendors is None:
        excluded_vendors = []
    if excluded_names is None:
        excluded_names = []

    # Prepare lowercase patterns and vendors for comparison
    excluded_patterns_lower = [p.lower() for p in excluded_patterns if p]
    excluded_vendors_lower = [v.lower() for v in excluded_vendors if v]
    try:
        engine = create_engine(get_glpi_db_url())

        # Build WHERE clause based on filters
        where_clause = "WHERE isv.itemtype = 'Computer'"
        params = {}

        if machine_id:
            where_clause += " AND c.id = :machine_id"
            params['machine_id'] = machine_id

        if entity_id:
            where_clause += " AND c.entities_id = :entity_id"
            params['entity_id'] = entity_id

        if group_id:
            # Join with dyngroup tables to filter by group
            where_clause += """ AND c.id IN (
                SELECT CAST(SUBSTRING(dm.uuid, 5) AS UNSIGNED)
                FROM dyngroup.Results r
                JOIN dyngroup.Machines dm ON dm.id = r.FK_machines
                WHERE r.FK_groups = :group_id
            )"""
            params['group_id'] = group_id

        query = text(f"""
            SELECT DISTINCT
                s.name as software_name,
                sv.name as version,
                m.name as manufacturer
            FROM glpi_items_softwareversions isv
            JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
            JOIN glpi_softwares s ON s.id = sv.softwares_id
            LEFT JOIN glpi_manufacturers m ON m.id = s.manufacturers_id
            JOIN glpi_computers c ON c.id = isv.items_id
            {where_clause}
            ORDER BY s.name, sv.name
        """)

        softwares = []
        excluded_count = 0
        with engine.connect() as conn:
            result = conn.execute(query, params)
            for row in result:
                sw_name = row[0]
                sw_version = row[1]
                sw_vendor = row[2]

                if not sw_name:
                    continue

                # Check exclusion patterns (substring match, case-insensitive)
                sw_name_lower = sw_name.lower()
                if any(pattern in sw_name_lower for pattern in excluded_patterns_lower):
                    excluded_count += 1
                    logger.debug(f"Excluded by pattern: {sw_name}")
                    continue

                # Check exclusion vendors (exact match, case-insensitive)
                if sw_vendor and sw_vendor.lower() in excluded_vendors_lower:
                    excluded_count += 1
                    logger.debug(f"Excluded by vendor: {sw_name} ({sw_vendor})")
                    continue

                # Check exclusion names (exact match, case-sensitive)
                if sw_name in excluded_names:
                    excluded_count += 1
                    logger.debug(f"Excluded by name: {sw_name}")
                    continue

                softwares.append({
                    'name': sw_name,
                    'version': sw_version or '',
                    'vendor': sw_vendor or ''
                })

        if excluded_count > 0:
            logger.debug(f"Excluded {excluded_count} software by config rules")

        logger.debug(f"GLPI query returned {len(softwares)} software packages")
        return softwares

    except Exception as e:
        logger.error(f"Error getting software from GLPI: {e}")
        return []


class CVECentralClient:
    """Client for the CVE Central API"""

    def __init__(self, base_url: str, server_id: str, aes_key: str):
        self.base_url = base_url.rstrip('/')
        self.server_id = server_id
        self.aes_key = aes_key.encode('utf-8')
        self.session = requests.Session()
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _generate_auth_token(self) -> str:
        """Generate AES-encrypted authentication token"""
        timestamp = int(time.time())
        plaintext = f"{self.server_id}:{timestamp}"
        iv = os.urandom(16)
        cipher = AES.new(self.aes_key, AES.MODE_CBC, iv)
        padded = pad(plaintext.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded)
        return base64.b64encode(iv + encrypted).decode('utf-8')

    def _get_headers(self) -> Dict[str, str]:
        return {
            'X-Server-ID': self.server_id,
            'X-Auth': self._generate_auth_token(),
            'Content-Type': 'application/json'
        }

    def submit_softwares(self, software_list: List[Dict], batch_size: int = 4000) -> Dict:
        """Submit software list to central API in batches

        Args:
            software_list: List of software dicts with name/version
            batch_size: Max items per request (CVE Central limit is 5000)
        """
        total_added = 0
        total_received = 0

        try:
            url = f"{self.base_url}/api/softwares"

            # Split into batches
            for i in range(0, len(software_list), batch_size):
                batch = software_list[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(software_list) + batch_size - 1) // batch_size

                logger.debug(f"Submitting batch {batch_num}/{total_batches} ({len(batch)} softwares)")

                response = self.session.post(
                    url,
                    headers=self._get_headers(),
                    json={'softwares': batch},
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()

                total_added += result.get('added', 0)
                total_received += result.get('received', 0)

            return {
                'success': True,
                'added': total_added,
                'received': total_received
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error submitting software to CVE Central: {e}")
            return {'success': False, 'error': str(e)}

    def trigger_scan(self, background: bool = True, max_age_days: int = 365, min_published_year: int = 2015) -> Dict:
        """Trigger a CVE scan on the central server

        Args:
            background: Run scan in background (non-blocking)
            max_age_days: Only fetch CVEs modified in the last N days
            min_published_year: Ignore CVEs published before this year
        """
        try:
            url = f"{self.base_url}/api/scan"
            params = {
                'background': 'true' if background else 'false',
                'max_age_days': max_age_days,
                'min_published_year': min_published_year
            }
            response = self.session.post(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=600 if not background else 30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error triggering CVE scan: {e}")
            return {'success': False, 'error': str(e)}

    def get_cves(self, software_list: List[Dict], batch_size: int = 4000) -> Dict:
        """Get CVEs for a list of software in batches.

        Filtering (min_cvss, max_age_days) is managed server-side by CVE Central.

        Args:
            software_list: List of software dicts with name/version
            batch_size: Max items per request (CVE Central limit is 5000)
        """
        all_cves = []
        seen_cve_ids = set()

        try:
            url = f"{self.base_url}/api/cves"

            # Split into batches
            for i in range(0, len(software_list), batch_size):
                batch = software_list[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (len(software_list) + batch_size - 1) // batch_size

                logger.debug(f"Getting CVEs batch {batch_num}/{total_batches} ({len(batch)} softwares)")

                response = self.session.post(
                    url,
                    headers=self._get_headers(),
                    json={'softwares': batch},
                    timeout=120
                )
                response.raise_for_status()
                result = response.json()

                # Deduplicate CVEs across batches
                for cve in result.get('cves', []):
                    cve_id = cve.get('cve_id')
                    if cve_id and cve_id not in seen_cve_ids:
                        seen_cve_ids.add(cve_id)
                        all_cves.append(cve)

            return {
                'success': True,
                'cves': all_cves,
                'count': len(all_cves)
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting CVEs from CVE Central: {e}")
            return {'success': False, 'error': str(e)}

    def get_stats(self) -> Dict:
        """Get statistics from CVE Central"""
        try:
            url = f"{self.base_url}/api/stats"
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting stats from CVE Central: {e}")
            return {'success': False, 'error': str(e)}

    def test_connection(self) -> bool:
        """Test connection to CVE Central API"""
        try:
            result = self.get_stats()
            return 'error' not in result and 'softwares_tracked' in result
        except:
            return False

    def get_scan_status(self) -> Dict:
        """Get current scan status from CVE Central"""
        try:
            url = f"{self.base_url}/api/scan/status"
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting scan status from CVE Central: {e}")
            return {'running': False, 'error': str(e)}

    def wait_for_scan_completion(self, poll_interval: int = 10, max_wait: int = 3600) -> Dict:
        """Wait for background scan to complete with polling

        Args:
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait before timeout

        Returns:
            Final scan status dict
        """
        start_time = time.time()
        while True:
            status = self.get_scan_status()

            if not status.get('running', False):
                # Scan finished (or never started)
                return status

            elapsed = time.time() - start_time
            if elapsed >= max_wait:
                logger.warning(f"Scan wait timeout after {elapsed:.0f}s")
                return {'running': False, 'error': 'Timeout waiting for scan completion', 'partial': True}

            progress = status.get('progress', 0)
            total = status.get('total', 0)
            cves_found = status.get('cves_found', 0)
            logger.info(f"Scan in progress: {progress}/{total} software scanned, {cves_found} CVEs found...")

            time.sleep(poll_interval)


def run_cve_scan(scan_id: Optional[int] = None, entity_id: Optional[int] = None,
                 group_id: Optional[int] = None, machine_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Run a full CVE scan:
    1. Get unique software from GLPI (optionally filtered by entity, group or machine)
    2. Submit to CVE Central
    3. Trigger NVD scan on CVE Central
    4. Get CVEs for our software
    5. Store CVEs locally and link to software

    Args:
        scan_id: Existing scan ID (optional, will create one if not provided)
        entity_id: Filter by entity ID (optional)
        group_id: Filter by group ID (optional)
        machine_id: Filter by machine GLPI ID (optional)
    """
    from pulse2.database.security import SecurityDatabase
    from mmc.plugins.security.config import SecurityConfig

    # Get configuration from ini file
    config = SecurityConfig("security")

    # Configure logger with level from config
    setup_logger(config.log_level)

    filter_info = ""
    if machine_id:
        filter_info = f" for machine {machine_id}"
    elif entity_id:
        filter_info = f" for entity {entity_id}"
    elif group_id:
        filter_info = f" for group {group_id}"
    logger.info(f"Starting CVE scan{filter_info}...")
    logger.debug(f"Config: log_level={config.log_level}, url={config.cve_central_url}")

    # Ensure database is activated
    security_db = SecurityDatabase()
    if not SecurityDatabase.is_activated:
        security_db.activate(config)

    # Create scan record if not provided
    if not scan_id:
        scan_id = security_db.create_scan()
    cve_central_url = config.cve_central_url
    cve_central_server_id = config.cve_central_server_id
    cve_central_keyAES32 = config.cve_central_keyAES32

    stats = {
        'softwares_sent': 0,
        'cves_received': 0,
        'machines_affected': 0,
        'errors': []
    }

    # Check configuration
    if not all([cve_central_url, cve_central_server_id, cve_central_keyAES32]):
        error_msg = "CVE Central API not configured. Check [cve_central] section in /etc/mmc/plugins/security.ini.local"
        logger.error(error_msg)
        security_db.complete_scan(scan_id, 0, 0, 0, error_msg)
        return {'scan_id': scan_id, 'status': 'failed', 'error': error_msg}

    # Initialize client
    logger.debug(f"Initializing CVE Central client for {cve_central_url}")
    cve_client = CVECentralClient(cve_central_url, cve_central_server_id, cve_central_keyAES32)

    try:
        # Test connection
        logger.debug("Testing connection to CVE Central...")
        if not cve_client.test_connection():
            raise Exception("Cannot connect to CVE Central API")
        logger.debug("Connection successful")

        # Step 1: Get unique software from GLPI (with optional filters and exclusions)
        logger.debug(f"Querying GLPI for software (machine_id={machine_id}, entity_id={entity_id}, group_id={group_id})")
        softwares = get_unique_software_from_glpi(
            entity_id=entity_id,
            group_id=group_id,
            machine_id=machine_id,
            excluded_patterns=config.excluded_patterns,
            excluded_vendors=config.excluded_vendors,
            excluded_names=config.excluded_names
        )
        stats['softwares_sent'] = len(softwares)

        if not softwares:
            logger.warning("No software found in GLPI")
            security_db.complete_scan(scan_id, 0, 0, 0, "No software in GLPI")
            return {'scan_id': scan_id, 'status': 'completed', **stats}

        logger.debug(f"First 5 software: {softwares[:5]}")

        # Step 2: Submit software to CVE Central
        submit_result = cve_client.submit_softwares(softwares)
        logger.debug(f"Submit result: {submit_result}")
        if not submit_result.get('success', False):
            logger.warning(f"Software submission failed: {submit_result.get('error')}")

        # Step 3: Trigger NVD scan on CVE Central (background mode with polling)
        max_age_days = getattr(config, 'max_age_days', 365)
        min_published_year = getattr(config, 'min_published_year', 2015)
        logger.debug(f"Triggering CVE Central scan (max_age_days={max_age_days}, min_published_year={min_published_year})")

        # Use background=True to avoid Gunicorn worker timeout, then poll for completion
        scan_result = cve_client.trigger_scan(background=True, max_age_days=max_age_days, min_published_year=min_published_year)

        if scan_result.get('success'):
            softwares_to_scan = scan_result.get('softwares_to_scan', 0)
            if softwares_to_scan > 0:
                logger.debug(f"CVE Central scanning {softwares_to_scan} software...")
                # Wait for scan to complete with polling (max 1 hour)
                final_status = cve_client.wait_for_scan_completion(poll_interval=10, max_wait=3600)
                if final_status.get('error'):
                    logger.warning(f"CVE Central scan warning: {final_status.get('error')}")
        else:
            logger.warning(f"CVE Central scan failed: {scan_result.get('error', 'Unknown')}")

        # Step 4: Get CVEs for our software (filtering is done server-side by CVE Central)
        cve_result = cve_client.get_cves(softwares)

        if not cve_result.get('success', False):
            raise Exception(f"Failed to get CVEs: {cve_result.get('error')}")

        cves_data = cve_result.get('cves', [])

        # Step 5: Store CVEs locally and count by severity
        cves_added = set()
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'N/A': 0}
        new_critical_cves = []

        for cve_entry in cves_data:
            cve_id_str = cve_entry.get('cve_id')
            if not cve_id_str:
                continue

            # Handle NULL cvss_score (CVEs not yet evaluated by NVD)
            cvss_raw = cve_entry.get('cvss_score')
            cvss_score = float(cvss_raw) if cvss_raw is not None else None
            severity = cve_entry.get('severity', 'N/A')
            description = cve_entry.get('description', '')
            published_at = cve_entry.get('published_at')
            last_modified = cve_entry.get('last_modified')
            software_name = cve_entry.get('software_name', '')  # Nom normalisé
            software_version = cve_entry.get('software_version', '')  # Version normalisée
            glpi_software_name = cve_entry.get('glpi_software_name', '')  # Nom GLPI original
            target_platform = cve_entry.get('target_platform')  # Platform cible (android, macos, ios, etc.)
            sources = cve_entry.get('sources', [])  # Sources ayant cette CVE (circl, nvd, euvd)
            source_urls = cve_entry.get('source_urls', {})  # URLs des sources

            # Add CVE to local cache
            cve_db_id = security_db.add_cve(
                cve_id=cve_id_str,
                cvss_score=cvss_score,
                severity=severity,
                description=description,
                published_at=published_at,
                last_modified=last_modified,
                sources=sources,
                source_urls=source_urls
            )

            # Link software to CVE with target platform
            if software_name:
                security_db.link_software_cve(
                    software_name=software_name,
                    software_version=software_version,
                    cve_db_id=cve_db_id,
                    glpi_software_name=glpi_software_name or None,
                    target_platform=target_platform
                )

            # Count by severity (only once per CVE)
            if cve_id_str not in cves_added:
                sev = severity if severity in severity_counts else 'N/A'
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                # Track new critical CVEs for alerting
                if severity == 'Critical':
                    new_critical_cves.append(cve_id_str)

            cves_added.add(cve_id_str)

        stats['cves_received'] = len(cves_added)

        # Complete scan (machines_affected is computed globally, not per-entity)
        security_db.complete_scan(
            scan_id=scan_id,
            softwares_sent=stats['softwares_sent'],
            cves_received=stats['cves_received'],
            machines_affected=0
        )

        # Log final summary with severity breakdown
        severity_summary = f"{severity_counts['Critical']}C/{severity_counts['High']}H/{severity_counts['Medium']}M/{severity_counts['Low']}L"
        logger.info(f"Scan #{scan_id} completed: {stats['softwares_sent']} software -> {stats['cves_received']} CVEs ({severity_summary})")

        return {'scan_id': scan_id, 'status': 'completed', **stats}

    except Exception as e:
        logger.error(f"CVE scan failed: {e}")
        stats['errors'].append(str(e))

        try:
            security_db.complete_scan(
                scan_id=scan_id,
                softwares_sent=stats['softwares_sent'],
                cves_received=stats['cves_received'],
                machines_affected=0,
                error_message=str(e)
            )
        except:
            pass

        return {'scan_id': scan_id, 'status': 'failed', 'error': str(e), **stats}


def run_scan_async():
    """Run CVE scan in a background thread"""
    from pulse2.database.security import SecurityDatabase
    from mmc.plugins.security.config import SecurityConfig

    # Ensure database is activated
    security_db = SecurityDatabase()
    if not SecurityDatabase.is_activated:
        config = SecurityConfig("security")
        security_db.activate(config)

    scan_id = security_db.create_scan()
    thread = Thread(target=run_cve_scan, args=(scan_id,), daemon=True)
    thread.start()

    logger.info(f"Started async CVE scan with ID: {scan_id}")
    return scan_id


def scan_single_machine(id_glpi: int) -> Dict[str, Any]:
    """
    Scan a single machine - scans only software installed on this machine.

    Args:
        id_glpi: GLPI computer ID

    Returns:
        dict with success status, vulnerabilities found, and any errors
    """
    result = run_cve_scan(machine_id=id_glpi)
    return {
        'success': result.get('status') == 'completed',
        'vulnerabilities_found': result.get('cves_received', 0),
        'error': result.get('error')
    }
