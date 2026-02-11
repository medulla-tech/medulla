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
from typing import Optional, Dict, List, Any, Callable
from threading import Thread, Event
from sqlalchemy import create_engine, text
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
import base64
import os

# Optional: WebSocket support (python-socketio)
try:
    import socketio
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    socketio = None

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
                                   excluded_vendors=None, excluded_names=None):
    """
    Get unique software list from GLPI (optionally filtered by entity, group or machine)

    Args:
        entity_id: Filter by entity ID (optional)
        group_id: Filter by group ID (optional)
        machine_id: Filter by machine GLPI ID (optional)
        excluded_vendors: List of vendors to exclude (exact match, case-insensitive)
        excluded_names: List of exact names to exclude (case-sensitive)

    Returns:
        List of unique software dicts with name, version, vendor
    """
    # Use empty lists if not provided (exclusions come from config)
    if excluded_vendors is None:
        excluded_vendors = []
    if excluded_names is None:
        excluded_names = []

    # Prepare lowercase vendors for comparison
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
        # Supprimer les logs verbeux urllib3/requests
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)

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

    def get_queue_status(self) -> Dict:
        """Get current queue status from CVE Central"""
        try:
            url = f"{self.base_url}/api/queue/status"
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting queue status from CVE Central: {e}")
            return {'queue': {'pending': 0}, 'error': str(e)}

    def queue_submit(self, software_ids: List[int], force_rescan: bool = False) -> Dict:
        """Submit software IDs to the scan queue

        Args:
            software_ids: List of software IDs to queue for scanning
            force_rescan: If True, queue even if recently scanned

        Returns:
            Dict with queued/skipped/already_pending counts
        """
        try:
            url = f"{self.base_url}/api/queue/submit"
            response = self.session.post(
                url,
                headers=self._get_headers(),
                json={'software_ids': software_ids, 'force_rescan': force_rescan},
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error submitting to queue: {e}")
            return {'success': False, 'error': str(e)}

    def queue_process(self, batch_size: int = 100) -> Dict:
        """Trigger queue processing on CVE Central

        Args:
            batch_size: Number of jobs to process per batch

        Returns:
            Dict with processing status
        """
        try:
            url = f"{self.base_url}/api/queue/process"
            response = self.session.post(
                url,
                headers=self._get_headers(),
                params={'batch_size': batch_size},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error triggering queue processing: {e}")
            return {'success': False, 'error': str(e)}

    def wait_for_queue_completion(self, poll_interval: int = 10, max_wait: int = 3600,
                                     on_progress: callable = None) -> Dict:
        """Wait for queue processing to complete with polling

        Args:
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait before timeout
            on_progress: Optional callback(status_dict) called on each poll iteration
                        Can be used to fetch CVEs progressively

        Returns:
            Final queue status dict
        """
        start_time = time.time()
        last_done = 0

        while True:
            status = self.get_queue_status()
            queue = status.get('queue', {})
            scan = status.get('scan', {})

            pending = queue.get('pending', 0)
            processing = queue.get('processing', 0)
            done = queue.get('done', 0)
            failed = queue.get('failed', 0)

            # Call progress callback if provided and new jobs completed
            if on_progress and done > last_done:
                try:
                    on_progress(status)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")
                last_done = done

            # Queue is complete when no pending/processing jobs
            if pending == 0 and processing == 0 and not scan.get('running', False):
                # Final callback
                if on_progress:
                    try:
                        on_progress(status)
                    except Exception as e:
                        logger.warning(f"Final progress callback error: {e}")
                return status

            elapsed = time.time() - start_time
            if elapsed >= max_wait:
                logger.warning(f"Queue wait timeout after {elapsed:.0f}s")
                return {'error': 'Timeout waiting for queue completion', 'partial': True, **status}

            cves_found = scan.get('cves_found', 0)
            logger.info(f"Queue processing: {pending} pending, {processing} processing, {done} done, {failed} failed, {cves_found} CVEs found...")

            time.sleep(poll_interval)

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

    def scan_via_websocket(self, softwares: List[Dict], max_age_days: int = 365,
                           min_published_year: int = 2020,
                           on_progress: Callable = None,
                           on_cves: Callable = None,
                           timeout: int = 3600) -> Dict:
        """
        Run CVE scan via WebSocket with real-time progress.

        Args:
            softwares: List of software dicts with name/version/vendor
            max_age_days: CVE age filter
            min_published_year: Ignore CVEs before this year
            on_progress: Callback(progress_dict) for progress updates
            on_cves: Callback(cves_list) when CVEs are found
            timeout: Maximum seconds to wait

        Returns:
            Dict with scan results
        """
        if not WEBSOCKET_AVAILABLE:
            logger.warning("WebSocket not available (python-socketio not installed), falling back to polling")
            return {'success': False, 'error': 'WebSocket not available', 'fallback': True}

        results = {
            'success': False,
            'cves': [],
            'softwares_scanned': 0,
            'cves_found': 0,
            'error': None
        }
        completed = Event()

        # Create SocketIO client
        sio = socketio.Client(ssl_verify=False)

        @sio.on('connect')
        def on_connect():
            logger.debug("WebSocket connected to CVE Central")

        @sio.on('disconnect')
        def on_disconnect():
            logger.debug("WebSocket disconnected from CVE Central")
            completed.set()

        @sio.on('authenticated')
        def on_authenticated(data):
            logger.debug(f"WebSocket authenticated: {data}")

        @sio.on('auth_error')
        def on_auth_error(data):
            logger.error(f"WebSocket auth error: {data}")
            results['error'] = data.get('error', 'Authentication failed')
            completed.set()

        @sio.on('scan_started')
        def on_scan_started(data):
            logger.debug(f"WebSocket scan_started event: {data}")
            if on_progress:
                on_progress({'phase': 'started', 'percent': 0, **data})

        @sio.on('progress')
        def on_progress_event(data):
            logger.debug(f"WebSocket progress: {data}")
            if on_progress:
                on_progress(data)

        @sio.on('cves_found')
        def on_cves_found(data):
            cves = data.get('cves', [])
            logger.debug(f"CVEs received for {data.get('software')}: {len(cves)}")
            results['cves'].extend(cves)
            if on_cves:
                on_cves(cves)

        @sio.on('scan_completed')
        def on_scan_completed(data):
            logger.debug(f"WebSocket scan_completed event: {data}")
            results['success'] = data.get('success', True)
            results['softwares_scanned'] = data.get('softwares_scanned', 0)
            results['cves_found'] = data.get('cves_found', 0)
            results['duration_seconds'] = data.get('duration_seconds', 0)
            results['duration_display'] = data.get('duration_display', '')
            completed.set()

        @sio.on('scan_error')
        def on_scan_error(data):
            logger.error(f"WebSocket scan error: {data}")
            results['error'] = data.get('error', 'Unknown error')
            completed.set()

        try:
            # Connect to CVE Central WebSocket
            ws_url = self.base_url.replace('https://', 'wss://').replace('http://', 'ws://')
            logger.debug(f"Connecting to WebSocket: {ws_url}")
            sio.connect(ws_url, transports=['websocket'])

            # Generate auth data
            timestamp = str(int(time.time()))
            signature = self._generate_auth_token()

            # Start scan
            sio.emit('start_scan', {
                'server_id': self.server_id,
                'signature': signature,
                'timestamp': timestamp,
                'softwares': softwares,
                'max_age_days': max_age_days,
                'min_published_year': min_published_year
            })

            # Wait for completion
            if not completed.wait(timeout=timeout):
                results['error'] = 'WebSocket scan timeout'
                logger.warning(f"WebSocket scan timeout after {timeout}s")

        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            results['error'] = str(e)
        finally:
            try:
                sio.disconnect()
            except:
                pass

        return results


def run_cve_scan(scan_id: Optional[int] = None, entity_id: Optional[int] = None,
                 group_id: Optional[int] = None, machine_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Run a full CVE scan:
    1. Get unique software from GLPI (optionally filtered by entity, group or machine)
    2. Submit to CVE Central
    3. Trigger CVE scan on CVE Central
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
        filter_info = f" (machine {machine_id})"
    elif entity_id:
        filter_info = f" (entity {entity_id})"
    elif group_id:
        filter_info = f" (group {group_id})"
    logger.debug(f"CVE scan config: log_level={config.log_level}, url={config.cve_central_url}")

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
            excluded_vendors=config.excluded_vendors,
            excluded_names=config.excluded_names
        )
        stats['softwares_sent'] = len(softwares)

        if not softwares:
            logger.warning("No software found in GLPI")
            security_db.complete_scan(scan_id, 0, 0, 0, "No software in GLPI")
            return {'scan_id': scan_id, 'status': 'completed', **stats}

        logger.info(f"CVE scan: {len(softwares)} software{filter_info}")

        # Step 2: Submit software to CVE Central
        submit_result = cve_client.submit_softwares(softwares)
        logger.debug(f"Submit result: {submit_result}")
        if not submit_result.get('success', False):
            logger.warning(f"Software submission failed: {submit_result.get('error')}")

        # Step 3: Run CVE scan (WebSocket preferred, fallback to polling)
        max_age_days = getattr(config, 'display_max_age_days', 0)
        min_published_year = getattr(config, 'display_min_published_year', 2000)
        logger.debug(f"Starting CVE scan (max_age_days={max_age_days}, min_published_year={min_published_year})")

        # Prepare CVE storage tracking
        cves_added = set()
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'N/A': 0}
        new_critical_cves = []

        def store_cve(cve_entry):
            """Store a single CVE entry to database"""
            nonlocal cves_added, severity_counts, new_critical_cves

            cve_id_str = cve_entry.get('cve_id')
            if not cve_id_str or cve_id_str in cves_added:
                return False  # Skip if no ID or already processed

            # Handle NULL cvss_score
            cvss_raw = cve_entry.get('cvss_score')
            cvss_score = float(cvss_raw) if cvss_raw is not None else None
            severity = cve_entry.get('severity', 'N/A')
            description = cve_entry.get('description', '')
            published_at = cve_entry.get('published_at')
            last_modified = cve_entry.get('last_modified')
            software_name = cve_entry.get('software_name', '')
            software_version = cve_entry.get('software_version', '')
            glpi_software_name = cve_entry.get('glpi_software_name', '')
            target_platform = cve_entry.get('target_platform')
            sources = cve_entry.get('sources', [])
            source_urls = cve_entry.get('source_urls', {})

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

            # Link software to CVE
            if software_name:
                security_db.link_software_cve(
                    software_name=software_name,
                    software_version=software_version,
                    cve_db_id=cve_db_id,
                    glpi_software_name=glpi_software_name or None,
                    target_platform=target_platform
                )

            # Count by severity
            sev = severity if severity in severity_counts else 'N/A'
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            if severity == 'Critical':
                new_critical_cves.append(cve_id_str)

            cves_added.add(cve_id_str)
            return True

        def store_cves_from_central():
            """Fetch and store CVEs from CVE Central (called during polling)"""
            cve_result = cve_client.get_cves(softwares)
            if not cve_result.get('success', False):
                logger.warning(f"Failed to get CVEs: {cve_result.get('error')}")
                return 0

            new_cves = 0
            for cve_entry in cve_result.get('cves', []):
                if store_cve(cve_entry):
                    new_cves += 1

            if new_cves > 0:
                logger.info(f"Progressive fetch: {new_cves} new CVEs stored (total: {len(cves_added)})")
            return new_cves

        def on_polling_progress(status):
            """Callback for progressive CVE fetching during queue polling"""
            store_cves_from_central()

        # Try WebSocket first (real-time, more efficient)
        use_websocket = WEBSOCKET_AVAILABLE and getattr(config, 'use_websocket', True)
        ws_success = False

        if use_websocket:
            logger.debug("Using WebSocket for CVE scan")

            def on_ws_progress(data):
                """WebSocket progress callback"""
                phase = data.get('phase', '')
                if phase == 'started':
                    eta = data.get('eta_display', '')
                    count = data.get('softwares_count', 0)
                    if eta:
                        logger.info(f"Scan started: {count} softwares, ETA {eta}")
                elif phase == 'scanning':
                    current = data.get('current', 0)
                    total = data.get('total', 0)
                    cves = data.get('cves_found', 0)
                    eta = data.get('eta_display', '')
                    elapsed = data.get('elapsed_seconds', 0)
                    elapsed_display = f"{elapsed // 60}m{elapsed % 60:02d}s" if elapsed >= 60 else f"{elapsed}s"
                    logger.info(f"Scan progress: {current}/{total} - {cves} CVEs - {elapsed_display} elapsed, ETA {eta}")
                else:
                    logger.debug(f"Scan phase: {phase}")

            def on_ws_cves(cves_list):
                """WebSocket CVE callback - store CVEs as they arrive"""
                new_count = 0
                for cve_entry in cves_list:
                    if store_cve(cve_entry):
                        new_count += 1
                if new_count > 0:
                    logger.debug(f"{new_count} new CVEs stored (total: {len(cves_added)})")

            ws_result = cve_client.scan_via_websocket(
                softwares=softwares,
                max_age_days=max_age_days,
                min_published_year=min_published_year,
                on_progress=on_ws_progress,
                on_cves=on_ws_cves,
                timeout=3600
            )

            if ws_result.get('success'):
                duration = ws_result.get('duration_display', '')
                duration_info = f" in {duration}" if duration else ""
                logger.info(f"Scan completed: {ws_result.get('softwares_scanned', 0)} scanned, {len(cves_added)} CVEs stored{duration_info}")
                ws_success = True
            elif ws_result.get('fallback'):
                # WebSocket not available, fall through to polling
                logger.info("WebSocket unavailable, falling back to polling")
            else:
                # WebSocket failed, try polling as fallback
                logger.warning(f"WebSocket scan failed: {ws_result.get('error')}, falling back to polling")

        # Polling fallback (or primary if WebSocket disabled/failed)
        if not ws_success:
            logger.info("Using polling for CVE scan")

            # Trigger scan - CVE Central 1.1+ uses queue internally for multi-server deduplication
            scan_result = cve_client.trigger_scan(background=True, max_age_days=max_age_days, min_published_year=min_published_year)

            if scan_result.get('success'):
                softwares_to_scan = scan_result.get('softwares_to_scan', 0) or scan_result.get('queued', 0)
                if softwares_to_scan > 0:
                    logger.debug(f"CVE Central scanning {softwares_to_scan} software...")

                    # Check if CVE Central 1.1+ (has queue status)
                    queue_status = cve_client.get_queue_status()
                    if 'queue' in queue_status and 'error' not in queue_status:
                        # Use queue polling with progressive CVE fetching
                        logger.debug("Using queue-based polling with progressive CVE fetching (CVE Central 1.1+)")
                        final_status = cve_client.wait_for_queue_completion(
                            poll_interval=10, max_wait=3600, on_progress=on_polling_progress
                        )
                    else:
                        # Fallback to legacy scan status polling (no progressive fetch)
                        final_status = cve_client.wait_for_scan_completion(poll_interval=10, max_wait=3600)
                        # Fetch all CVEs at the end for legacy mode
                        store_cves_from_central()

                    if final_status.get('error'):
                        logger.warning(f"CVE Central scan warning: {final_status.get('error')}")
                else:
                    logger.debug("No software needs scanning (all recently scanned)")
                    # Still fetch existing CVEs from cache
                    store_cves_from_central()
            else:
                logger.warning(f"CVE Central scan failed: {scan_result.get('error', 'Unknown')}")
                # Try to get cached CVEs anyway
                store_cves_from_central()

            # Final fetch to ensure we have all CVEs (in case some were missed)
            store_cves_from_central()

        # CVEs are already stored by store_cves_from_central() during polling
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
