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
from threading import Event
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


def get_dyngroup_db_url():
    """Read dyngroup database configuration and return SQLAlchemy URL"""
    config = configparser.ConfigParser()
    config.read(['/etc/mmc/plugins/dyngroup.ini', '/etc/mmc/plugins/dyngroup.ini.local'])

    dbhost = config.get('database', 'dbhost', fallback='localhost')
    dbport = config.get('database', 'dbport', fallback='3306')
    dbname = config.get('database', 'dbname', fallback='dyngroup')
    dbuser = config.get('database', 'dbuser', fallback='mmc')
    dbpasswd = config.get('database', 'dbpasswd', fallback='mmc')

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

        if machine_id is not None:
            where_clause += " AND c.id = :machine_id"
            params['machine_id'] = machine_id

        if entity_id is not None:
            where_clause += " AND c.entities_id = :entity_id"
            params['entity_id'] = entity_id

        if group_id is not None:
            # Get machine IDs from dyngroup database (separate connection)
            try:
                dyngroup_engine = create_engine(get_dyngroup_db_url())
                with dyngroup_engine.connect() as dg_conn:
                    dg_result = dg_conn.execute(text("""
                        SELECT DISTINCT dm.uuid
                        FROM Results r
                        JOIN Machines dm ON dm.id = r.FK_machines
                        WHERE r.FK_groups = :group_id
                    """), {'group_id': group_id})
                    machine_ids = []
                    for row in dg_result:
                        uuid_val = row[0]
                        if uuid_val and uuid_val.startswith('UUID'):
                            machine_ids.append(int(uuid_val[4:]))
                dyngroup_engine.dispose()
                if machine_ids:
                    ids_str = ','.join(str(mid) for mid in machine_ids)
                    where_clause += f" AND c.id IN ({ids_str})"
                else:
                    logger.warning(f"No machines found in group {group_id}")
                    return []
            except Exception as e:
                logger.error(f"Error getting machines from dyngroup for group {group_id}: {e}")
                return []

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

    def test_connection(self) -> bool:
        """Test connection to CVE Central API via health check."""
        try:
            url = f"{self.base_url}/up"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200 and response.json().get('success', False):
                return True
            logger.warning(f"CVE Central health check failed: HTTP {response.status_code}")
            return False
        except Exception as e:
            logger.warning(f"CVE Central unreachable: {e}")
            return False

    def scan(self, softwares: List[Dict],
             on_progress: Callable = None,
             on_cves: Callable = None,
             timeout: int = 7200) -> Dict:
        """
        Run CVE scan via WebSocket with real-time progress.

        CVE Central stocke toutes les CVEs sans filtre.
        Le filtrage se fait cote client a l'affichage.

        Args:
            softwares: List of software dicts with name/version/vendor
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
                'softwares': softwares
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
                 group_id: Optional[int] = None, machine_id: Optional[int] = None,
                 target_name: Optional[str] = None) -> Dict[str, Any]:
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
    if machine_id is not None:
        name_part = f" '{target_name}'" if target_name else ""
        filter_info = f" (machine{name_part} id={machine_id})"
    elif entity_id is not None:
        name_part = f" '{target_name}'" if target_name else ""
        filter_info = f" (entity{name_part} id={entity_id})"
    elif group_id is not None:
        name_part = f" '{target_name}'" if target_name else ""
        filter_info = f" (group{name_part} id={group_id})"
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

        # Pas de filtre au scan - CVE Central stocke tout
        # Le filtrage se fait a l'affichage via should_display_cve()

        # CVE storage tracking
        cves_added = set()
        severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'N/A': 0}
        new_critical_cves = []

        def store_cve(cve_entry):
            """Store a single CVE entry to database"""
            nonlocal cves_added, severity_counts, new_critical_cves

            cve_id_str = cve_entry.get('cve_id')
            if not cve_id_str or cve_id_str in cves_added:
                return False

            try:
                cvss_raw = cve_entry.get('cvss_score')
                cvss_score = float(cvss_raw) if cvss_raw is not None else None
                severity = cve_entry.get('severity', 'N/A')

                cve_db_id = security_db.add_cve(
                    cve_id=cve_id_str,
                    cvss_score=cvss_score,
                    severity=severity,
                    description=cve_entry.get('description', ''),
                    published_at=cve_entry.get('published_at'),
                    last_modified=cve_entry.get('last_modified'),
                    sources=cve_entry.get('sources', []),
                    source_urls=cve_entry.get('source_urls', {})
                )

                software_name = cve_entry.get('software_name', '')
                if software_name:
                    security_db.link_software_cve(
                        software_name=software_name,
                        software_version=cve_entry.get('software_version', ''),
                        cve_db_id=cve_db_id,
                        glpi_software_name=cve_entry.get('glpi_software_name') or None,
                        target_platform=cve_entry.get('target_platform')
                    )

                sev = severity if severity in severity_counts else 'N/A'
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                if severity == 'Critical':
                    new_critical_cves.append(cve_id_str)

                cves_added.add(cve_id_str)
                return True
            except Exception as e:
                logger.error(f"Error storing CVE {cve_id_str}: {e}")
                return False

        # WebSocket scan (seul mode supporté)
        if not WEBSOCKET_AVAILABLE:
            raise Exception("python-socketio not installed. Install it: pip install python-socketio websocket-client")

        def on_ws_progress(data):
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

        def on_ws_cves(cves_list):
            new_count = sum(1 for cve in cves_list if store_cve(cve))
            if new_count > 0:
                logger.debug(f"{new_count} new CVEs stored (total: {len(cves_added)})")

        ws_result = cve_client.scan(
            softwares=softwares,
            on_progress=on_ws_progress,
            on_cves=on_ws_cves,
            timeout=3600
        )

        if ws_result.get('success'):
            duration = ws_result.get('duration_display', '')
            duration_info = f" in {duration}" if duration else ""
            logger.info(f"Scan completed: {ws_result.get('softwares_scanned', 0)} scanned, {len(cves_added)} CVEs stored{duration_info}")
        else:
            error = ws_result.get('error', 'Unknown WebSocket error')
            raise Exception(f"WebSocket scan failed: {error}")

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
