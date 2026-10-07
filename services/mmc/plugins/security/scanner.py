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
from typing import Optional, Dict, List, Any, Callable
from collections import Counter
from threading import Condition, Event
from sqlalchemy import bindparam, create_engine, text
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
import base64
import os
from pulse2.database.security import OS_BUILD, OS_JOINS, OS_LABEL

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


def _group_machine_ids(group_id):
    engine = create_engine(get_dyngroup_db_url())
    try:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT DISTINCT dm.uuid
                FROM Results r
                JOIN Machines dm ON dm.id = r.FK_machines
                WHERE r.FK_groups = :group_id
            """), {'group_id': group_id})
            return [int(uuid[4:]) for (uuid,) in rows if uuid and uuid.startswith('UUID') and uuid[4:].isdigit()]
    finally:
        engine.dispose()


def get_unique_software_from_glpi(entity_id=None, group_id=None, machine_id=None,
                                  excluded_vendors=None, excluded_names=None):
    """Unique (name, version, os) software and Windows builds of the targeted machines.

    Raises on database error so that the scan is reported as failed.
    """
    excluded_vendors = {v.lower() for v in excluded_vendors or [] if v}
    excluded_names = set(excluded_names or [])

    where = ["c.is_deleted = 0", "c.is_template = 0"]
    params = {'ext': '%Extension Navigateur%', 'addon': '%Categorie: %'}
    if machine_id is not None:
        where.append("c.id = :machine_id")
        params['machine_id'] = machine_id
    if entity_id is not None:
        where.append("c.entities_id = :entity_id")
        params['entity_id'] = entity_id
    if group_id is not None:
        machine_ids = _group_machine_ids(group_id)
        if not machine_ids:
            logger.warning(f"No machines found in group {group_id}")
            return []
        where.append("c.id IN :machine_ids")
        params['machine_ids'] = machine_ids
    where = ' AND '.join(where)

    # Le script d'inventaire des extensions note « Categorie: … » en commentaire : extension
    # de navigateur, ou autre composant (complément Office, thème, pack de langue…).
    query = text(f"""
        SELECT s.name, sv.name, m.name,
               CASE WHEN s.comment LIKE :ext THEN 'browser extension'
                    WHEN s.comment LIKE :addon THEN 'add-on' ELSE '' END, {OS_LABEL}
        FROM glpi_items_softwareversions isv
        JOIN glpi_softwareversions sv ON sv.id = isv.softwareversions_id
        JOIN glpi_softwares s ON s.id = sv.softwares_id
        LEFT JOIN glpi_manufacturers m ON m.id = s.manufacturers_id
        JOIN glpi_computers c ON c.id = isv.items_id {OS_JOINS}
        WHERE isv.itemtype = 'Computer' AND isv.is_deleted = 0 AND {where}
        UNION
        SELECT os.name, {OS_BUILD}, 'Microsoft', 'os', {OS_LABEL}
        FROM glpi_computers c {OS_JOINS}
        WHERE {OS_BUILD} IS NOT NULL AND {where}
    """)
    if 'machine_ids' in params:
        query = query.bindparams(bindparam('machine_ids', expanding=True))

    engine = create_engine(get_glpi_db_url())
    try:
        with engine.connect() as conn:
            rows = conn.execute(query, params).fetchall()
    finally:
        engine.dispose()

    softwares = {}
    excluded = 0
    for name, version, vendor, category, os_name in rows:
        if not name:
            continue
        if (vendor and vendor.lower() in excluded_vendors) or name in excluded_names:
            excluded += 1
            continue
        key = (name, version or '', os_name or '')
        softwares.setdefault(key, {'name': key[0], 'version': key[1], 'vendor': vendor or '',
                                   'category': category, 'os': key[2]})

    logger.debug(f"GLPI inventory: {len(softwares)} software, {excluded} excluded by config")
    return list(softwares.values())


class CVECentralClient:
    """Client for the CVE Central API"""

    def __init__(self, base_url: str, server_id: str, aes_key: str, ssl_verify: bool = True):
        self.base_url = base_url.rstrip('/')
        self.server_id = server_id
        self.aes_key = aes_key.encode('utf-8')
        if len(self.aes_key) != 32:
            raise ValueError("[cve_central] keyAES32 must be 32 characters")
        self.ssl_verify = ssl_verify
        self.session = requests.Session()
        self.session.verify = ssl_verify
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

    def get_access_status(self) -> Dict[str, Any]:
        """Check runtime access against CVE Central access endpoint."""
        try:
            timestamp = str(int(time.time()))
            signature = self._generate_auth_token()
            url = f"{self.base_url}/access/status"
            response = self.session.post(url, json={
                'server_id': self.server_id,
                'signature': signature,
                'timestamp': timestamp
            }, timeout=10)

            if response.status_code == 200:
                payload = response.json() if response.content else {}
                return {
                    'reachable': True,
                    'authorized': True,
                    'reason': payload.get('status', 'active')
                }

            if response.status_code == 403:
                payload = response.json() if response.content else {}
                return {
                    'reachable': True,
                    'authorized': False,
                    'reason': payload.get('reason', 'access_denied')
                }

            if response.status_code == 404:
                return {
                    'reachable': True,
                    'authorized': False,
                    'reason': 'endpoint_unavailable'
                }

            return {
                'reachable': True,
                'authorized': False,
                'reason': f'http_{response.status_code}'
            }
        except Exception as e:
            logger.warning(f"CVE Central access status check failed: {e}")
            return {
                'reachable': False,
                'authorized': False,
                'reason': 'service_unreachable'
            }

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
        """Run a CVE scan over WebSocket; CVEs are streamed to on_cves(list)."""
        results = {'success': False, 'softwares_scanned': 0, 'error': None}
        completed = Event()
        # python-socketio runs each message in its own thread: store them one at a time
        # and wait for the last ones before reporting the end of the scan.
        stored = Condition()
        received = {'cves': 0, 'expected': None}
        sio = socketio.Client(ssl_verify=self.ssl_verify)

        def fail(data, default):
            logger.error(f"CVE Central: {default}: {data}")
            results['error'] = (data or {}).get('error') or default
            completed.set()

        @sio.on('disconnect')
        def on_disconnect():
            logger.debug("WebSocket disconnected from CVE Central")
            completed.set()

        @sio.on('auth_error')
        def on_auth_error(data):
            fail(data, 'Authentication failed')

        @sio.on('scan_error')
        def on_scan_error(data):
            fail(data, 'Scan error')

        @sio.on('progress')
        def on_progress_event(data):
            if on_progress:
                on_progress(data)

        @sio.on('cves_found')
        def on_cves_found(data):
            cves = data.get('cves', [])
            logger.debug(f"CVEs received for {data.get('software')}: {len(cves)}")
            with stored:
                if on_cves:
                    on_cves(cves)
                received['cves'] += len(cves)
                stored.notify_all()

        @sio.on('scan_completed')
        def on_scan_completed(data):
            results['success'] = data.get('success', True)
            results['softwares_scanned'] = data.get('softwares_scanned', 0)
            results['duration_display'] = data.get('duration_display', '')
            received['expected'] = data.get('cves_found')
            if not results['success']:
                results['error'] = data.get('error') or 'Scan reported as failed by CVE Central'
            completed.set()

        try:
            ws_url = self.base_url.replace('https://', 'wss://').replace('http://', 'ws://')
            logger.debug(f"Connecting to WebSocket: {ws_url}")
            sio.connect(ws_url, transports=['websocket'])
            sio.emit('start_scan', {
                'server_id': self.server_id,
                'signature': self._generate_auth_token(),
                'timestamp': str(int(time.time())),
                'softwares': softwares
            })
            if not completed.wait(timeout=timeout):
                results['error'] = f'No answer from CVE Central after {timeout}s'
            elif results['success'] and received['expected'] is not None:
                with stored:
                    if not stored.wait_for(lambda: received['cves'] >= received['expected'], timeout=300):
                        results['success'] = False
                        results['error'] = (f"Incomplete results: {received['cves']}/"
                                            f"{received['expected']} CVEs received")
        except Exception as e:
            results['error'] = f'WebSocket error: {e}'
        finally:
            try:
                sio.disconnect()
            except Exception:
                pass

        if not results['success'] and not results['error']:
            results['error'] = 'Connection closed by CVE Central before the end of the scan'
        return results


def run_cve_scan(scan_id: Optional[int] = None, entity_id: Optional[int] = None,
                 group_id: Optional[int] = None, machine_id: Optional[int] = None,
                 target_name: Optional[str] = None) -> Dict[str, Any]:
    """Scan the GLPI software of the target with CVE Central and store the results."""
    from pulse2.database.security import SecurityDatabase
    from mmc.plugins.security.config import SecurityConfig

    config = SecurityConfig("security")
    setup_logger(config.log_level)

    target = ""
    for kind, value in (('machine', machine_id), ('entity', entity_id), ('group', group_id)):
        if value is not None:
            name = f" '{target_name}'" if target_name else ""
            target = f" ({kind}{name} id={value})"
            break

    security_db = SecurityDatabase()
    if not SecurityDatabase.is_activated:
        security_db.activate(config)
    if not scan_id:
        scan_id = security_db.create_scan()

    stats = {'softwares_sent': 0, 'cves_received': 0}
    try:
        if not all([config.cve_central_url, config.cve_central_server_id, config.cve_central_keyAES32]):
            raise Exception("CVE Central API not configured. Check [cve_central] section in "
                            "/etc/mmc/plugins/security.ini.local")
        if not WEBSOCKET_AVAILABLE:
            raise Exception("python-socketio not installed. Install it: pip install python-socketio websocket-client")

        client = CVECentralClient(config.cve_central_url, config.cve_central_server_id,
                                  config.cve_central_keyAES32, config.cve_central_ssl_verify)
        if not client.test_connection():
            raise Exception("Cannot connect to CVE Central API")

        exclusions = config.get_exclusion_policies()  # relues en base : le relais vit longtemps
        softwares = get_unique_software_from_glpi(
            entity_id=entity_id,
            group_id=group_id,
            machine_id=machine_id,
            excluded_vendors=exclusions['vendors'],
            excluded_names=exclusions['names']
        )
        stats['softwares_sent'] = len(softwares)
        if not softwares:
            logger.warning(f"CVE scan #{scan_id}: no software in GLPI{target}")
            security_db.complete_scan(scan_id, 0, 0)
            return {'scan_id': scan_id, 'status': 'completed', **stats}

        logger.info(f"CVE scan: {len(softwares)} software{target}")

        # Links are pruned at the end, only for the (name, version) sent in this scan.
        scanned = {(sw['name'], sw['version']) for sw in softwares}
        confirmed = {}
        cve_pks = {}
        severities = Counter()

        def store(entry):
            cve_id = entry.get('cve_id')
            name = entry.get('software_name') or ''
            glpi_name = entry.get('glpi_software_name') or name
            version = entry.get('software_version') or ''
            if not cve_id or not glpi_name:
                return
            confirmed.setdefault((glpi_name, version), set()).add(cve_id)
            try:
                pk = cve_pks.get(cve_id)
                if pk is None:
                    cvss = entry.get('cvss_score')
                    severity = entry.get('severity') or 'N/A'
                    pk = security_db.add_cve(
                        cve_id=cve_id,
                        cvss_score=float(cvss) if cvss is not None else None,
                        severity=severity,
                        description=entry.get('description', ''),
                        published_at=entry.get('published_at'),
                        last_modified=entry.get('last_modified'),
                        exploited_since=entry.get('exploited_since') or None,
                        euvd_id=entry.get('euvd_id') or None,
                        sources=entry.get('sources', []),
                        source_urls=entry.get('source_urls', {})
                    )
                    if pk is None:
                        raise Exception("CVE not saved")
                    cve_pks[cve_id] = pk
                    severities[severity] += 1
                security_db.link_software_cve(
                    software_name=name or glpi_name,
                    software_version=version,
                    cve_db_id=pk,
                    glpi_software_name=glpi_name,
                    target_platform=entry.get('target_platform'),
                    fix_available=entry.get('fix_available'),
                    source_package=entry.get('source_package') or None
                )
            except Exception as e:
                logger.error(f"Error storing {cve_id} for {glpi_name} {version}: {e}")

        logged = {'step': -1}

        def on_progress(data):
            step = data.get('percent', 0) // 10
            if data.get('phase') == 'scanning' and step > logged['step']:
                logged['step'] = step
                logger.info(f"Scan progress: {data.get('percent', 0)}% ({data.get('elapsed_seconds', 0)}s)")

        def on_cves(cves):
            for cve in cves:
                store(cve)

        result = client.scan(softwares=softwares, on_progress=on_progress, on_cves=on_cves, timeout=3600)
        if not result['success']:
            raise Exception(f"CVE Central scan failed: {result['error']}")

        stats['cves_received'] = len(cve_pks)
        pruned = security_db.prune_stale_cves(scanned, confirmed)
        if pruned:
            logger.info(f"Pruned {pruned} stale CVE links after scan")

        security_db.complete_scan(scan_id, stats['softwares_sent'], stats['cves_received'])
        duration = result.get('duration_display')
        logger.info(f"Scan #{scan_id} completed{target}: {stats['softwares_sent']} software -> "
                    f"{stats['cves_received']} CVEs ({severities['Critical']}C/{severities['High']}H/"
                    f"{severities['Medium']}M/{severities['Low']}L)" + (f" in {duration}" if duration else ""))
        return {'scan_id': scan_id, 'status': 'completed', **stats}

    except Exception as e:
        logger.error(f"CVE scan #{scan_id} failed{target}: {e}")
        try:
            security_db.complete_scan(scan_id, stats['softwares_sent'], stats['cves_received'], error_message=str(e))
        except Exception as db_error:
            logger.error(f"Cannot mark scan #{scan_id} as failed: {db_error}")
        return {'scan_id': scan_id, 'status': 'failed', 'error': str(e), **stats}
